"""
FastAPI SSE POC for A2A Agent Streaming
This app demonstrates how to interact with the A2A agent using Server-Sent Events (SSE)
"""

import asyncio
import uuid
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from a2a.client.client import ClientConfig as A2AClientConfig
from a2a.client.client_factory import ClientFactory as A2AClientFactory
from a2a.types import TransportProtocol as A2ATransport
from google.genai import types as genai_types

# Initialize FastAPI app
app = FastAPI(title="A2A Agent SSE POC", description="POC for streaming A2A agent responses via SSE")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable streaming for A2A client
a2a_client_config = A2AClientConfig(
    streaming=True,
    polling=False,
    supported_transports=[A2ATransport.jsonrpc],
)
a2a_client_factory = A2AClientFactory(config=a2a_client_config)

# Create the RemoteA2aAgent
root_agent = RemoteA2aAgent(
    name="travel_agent",
    description="คุณคือผู้ช่วยการท่องเที่ยวที่เชี่ยวชาญด้านการวางแผนการเดินทางและที่พัก Airbnb",
    agent_card=f"http://localhost:8001/{AGENT_CARD_WELL_KNOWN_PATH}",
    a2a_client_factory=a2a_client_factory,
)

# Create session service and runner
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="travel_agent_app",
    session_service=session_service,
)


class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    session_id: str | None = None


async def generate_sse_events(
    message: str, user_id: str, session_id: str
) -> AsyncGenerator[str, None]:
    """Generate SSE events from the agent response stream.
    
    This follows the A2A protocol streaming specification:
    - TaskStatusUpdateEvent: status changes (working, input-required, completed)
    - TaskArtifactUpdateEvent: artifact chunks with append/lastChunk
    - Task: final task state
    
    Events are streamed as they arrive from the A2A server via SSE.
    """
    import json
    
    # Create new message content
    new_message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=message)]
    )
    
    # Track seen text to avoid duplicates (A2A may send cumulative updates)
    seen_text = set()
    last_text = ""
    
    try:
        # Stream events from the agent (A2A streaming via RemoteA2aAgent)
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message,
        ):
            # Send status update event
            if event.author:
                # Check for A2A metadata to determine event type
                a2a_response = event.custom_metadata.get("a2a_response", {}) if event.custom_metadata else {}
                task_status = a2a_response.get("status", {}).get("state", "working")
                
                # Handle timestamp - it might be a float (unix timestamp) or datetime
                timestamp_val = None
                if hasattr(event, 'timestamp') and event.timestamp:
                    if hasattr(event.timestamp, 'isoformat'):
                        timestamp_val = event.timestamp.isoformat()
                    elif isinstance(event.timestamp, (int, float)):
                        from datetime import datetime
                        timestamp_val = datetime.fromtimestamp(event.timestamp).isoformat()
                
                status_data = json.dumps({
                    "type": "status",
                    "author": event.author,
                    "state": task_status,
                    "timestamp": timestamp_val
                })
                yield f"event: status\ndata: {status_data}\n\n"
            
            # Extract and stream text content
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        current_text = part.text
                        
                        # Check if this is new text (not a duplicate)
                        if current_text not in seen_text:
                            seen_text.add(current_text)
                            
                            # For incremental streaming, send only new content
                            # A2A may send cumulative text, so we diff it
                            if current_text.startswith(last_text) and len(current_text) > len(last_text):
                                # This is an incremental update
                                new_content = current_text[len(last_text):]
                                text_data = json.dumps({
                                    "type": "text",
                                    "content": new_content,
                                    "incremental": True
                                })
                            else:
                                # This is a new/different text block
                                text_data = json.dumps({
                                    "type": "text", 
                                    "content": current_text,
                                    "incremental": False
                                })
                            
                            last_text = current_text
                            yield f"event: text\ndata: {text_data}\n\n"
            
            # Check for function calls (tool usage)
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        func_data = json.dumps({
                            "type": "function_call",
                            "name": part.function_call.name if hasattr(part.function_call, 'name') else "unknown",
                            "status": "executing"
                        })
                        yield f"event: function\ndata: {func_data}\n\n"
                
    except Exception as e:
        error_data = json.dumps({"type": "error", "message": str(e)})
        yield f"event: error\ndata: {error_data}\n\n"
    
    # Send done event (A2A: final: true in TaskStatusUpdateEvent)
    done_data = json.dumps({"type": "done", "status": "completed"})
    yield f"event: done\ndata: {done_data}\n\n"


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat responses via SSE."""
    
    # Generate session_id if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Ensure session exists
    session = await session_service.get_session(
        app_name="travel_agent_app",
        user_id=request.user_id,
        session_id=session_id,
    )
    if not session:
        session = await session_service.create_session(
            app_name="travel_agent_app",
            user_id=request.user_id,
            session_id=session_id,
        )
    
    return StreamingResponse(
        generate_sse_events(request.message, request.user_id, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Session-Id": session_id,
        },
    )


@app.get("/", response_class=HTMLResponse)
async def index():
    """Simple HTML page to test SSE streaming with ChatGPT-like typewriter effect."""
    return """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A2A Agent SSE POC</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #333; text-align: center; }
        .chat-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        #messages {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            background: #fafafa;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 8px;
            max-width: 85%;
            line-height: 1.5;
            white-space: pre-wrap;
        }
        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .agent-message {
            background: #e9ecef;
            color: #333;
        }
        .streaming {
            border-left: 3px solid #28a745;
        }
        /* Thinking indicator */
        .thinking {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #666;
            font-style: italic;
        }
        .thinking-dots {
            display: flex;
            gap: 4px;
        }
        .thinking-dots span {
            width: 8px;
            height: 8px;
            background: #007bff;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .thinking-dots span:nth-child(1) { animation-delay: -0.32s; }
        .thinking-dots span:nth-child(2) { animation-delay: -0.16s; }
        .thinking-dots span:nth-child(3) { animation-delay: 0s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        /* Cursor blink effect */
        .cursor {
            display: inline-block;
            width: 2px;
            height: 1em;
            background: #333;
            margin-left: 2px;
            animation: blink 1s infinite;
            vertical-align: text-bottom;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        button {
            padding: 12px 25px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #0056b3; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .status { 
            text-align: center; 
            color: #666; 
            font-size: 14px; 
            margin-top: 10px;
            min-height: 20px;
        }
        .status-icon {
            display: inline-block;
            margin-right: 6px;
        }
        /* Function call indicator */
        .function-badge {
            display: inline-block;
            background: #e3f2fd;
            color: #1976d2;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <h1>🌴 A2A Travel Agent - SSE POC</h1>
    <div class="chat-container">
        <div id="messages"></div>
        <div class="input-group">
            <input type="text" id="userInput" placeholder="พิมพ์ข้อความของคุณ..." onkeypress="if(event.key==='Enter')sendMessage()">
            <button onclick="sendMessage()" id="sendBtn">ส่ง</button>
        </div>
        <div class="status" id="status">พร้อมใช้งาน</div>
    </div>

    <script>
        let sessionId = null;
        const userId = 'web_user_' + Math.random().toString(36).substr(2, 9);
        
        // Typewriter configuration
        const TYPING_SPEED = 15; // ms per character (lower = faster)
        let typewriterQueue = [];
        let isTyping = false;
        let currentAgentDiv = null;
        let displayedText = '';
        let targetText = '';
        
        function addMessage(text, isUser) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user-message' : 'agent-message');
            if (!isUser) {
                div.innerHTML = '<span class="text-content"></span>';
            } else {
                div.textContent = text;
            }
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
            return div;
        }
        
        function showThinking(div) {
            const textContent = div.querySelector('.text-content');
            if (textContent) {
                textContent.innerHTML = '<div class="thinking"><div class="thinking-dots"><span></span><span></span><span></span></div><span>กำลังคิด...</span></div>';
            }
        }
        
        function addCursor(div) {
            const textContent = div.querySelector('.text-content');
            if (textContent && !textContent.querySelector('.cursor')) {
                const cursor = document.createElement('span');
                cursor.className = 'cursor';
                textContent.appendChild(cursor);
            }
        }
        
        function removeCursor(div) {
            const cursor = div.querySelector('.cursor');
            if (cursor) cursor.remove();
        }
        
        // Typewriter effect - types text character by character
        async function typeText(div, newText) {
            const textContent = div.querySelector('.text-content');
            if (!textContent) return;
            
            // Remove thinking indicator if present
            const thinking = textContent.querySelector('.thinking');
            if (thinking) {
                textContent.innerHTML = '';
            }
            
            // Add new text to target
            if (newText !== targetText) {
                if (newText.startsWith(targetText)) {
                    // Incremental update - just add new characters
                    targetText = newText;
                } else {
                    // New text block
                    targetText = newText;
                    displayedText = '';
                }
            }
            
            // Start typing if not already
            if (!isTyping) {
                isTyping = true;
                await typeNextCharacter(textContent);
            }
        }
        
        async function typeNextCharacter(textContent) {
            while (displayedText.length < targetText.length) {
                displayedText += targetText[displayedText.length];
                textContent.innerHTML = displayedText + '<span class="cursor"></span>';
                
                // Scroll to bottom
                const messages = document.getElementById('messages');
                messages.scrollTop = messages.scrollHeight;
                
                // Wait before next character
                await new Promise(resolve => setTimeout(resolve, TYPING_SPEED));
            }
            isTyping = false;
        }
        
        function updateStatus(text, icon = '') {
            const status = document.getElementById('status');
            status.innerHTML = icon ? '<span class="status-icon">' + icon + '</span>' + text : text;
        }
        
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message) return;
            
            input.value = '';
            document.getElementById('sendBtn').disabled = true;
            updateStatus('กำลังส่งข้อความ...', '📤');
            
            // Reset typewriter state
            displayedText = '';
            targetText = '';
            isTyping = false;
            
            addMessage(message, true);
            const agentDiv = addMessage('', false);
            agentDiv.classList.add('streaming');
            currentAgentDiv = agentDiv;
            
            // Show thinking indicator
            showThinking(agentDiv);
            updateStatus('กำลังคิด...', '🤔');
            
            try {
                const response = await fetch('/chat/stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        user_id: userId,
                        session_id: sessionId
                    })
                });
                
                sessionId = response.headers.get('X-Session-Id') || sessionId;
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                let hasReceivedText = false;
                
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\\n');
                    buffer = lines.pop() || '';
                    
                    for (const line of lines) {
                        if (line.startsWith('event: ')) continue;
                        
                        if (line.startsWith('data: ')) {
                            const dataStr = line.substring(6);
                            try {
                                const data = JSON.parse(dataStr);
                                
                                if (data.type === 'text') {
                                    hasReceivedText = true;
                                    updateStatus('กำลังพิมพ์...', '✍️');
                                    
                                    let newText;
                                    if (data.incremental) {
                                        newText = targetText + data.content;
                                    } else {
                                        newText = data.content;
                                    }
                                    
                                    // Trigger typewriter effect
                                    await typeText(agentDiv, newText);
                                    
                                } else if (data.type === 'status') {
                                    if (!hasReceivedText) {
                                        const stateInfo = {
                                            'working': { text: 'กำลังประมวลผล...', icon: '⚙️' },
                                            'input-required': { text: 'รอข้อมูลเพิ่มเติม', icon: '❓' },
                                            'completed': { text: 'เสร็จสิ้น', icon: '✅' }
                                        };
                                        const info = stateInfo[data.state] || { text: data.state, icon: '' };
                                        updateStatus(info.text, info.icon);
                                    }
                                } else if (data.type === 'function') {
                                    updateStatus('กำลังค้นหา: ' + data.name, '🔍');
                                    
                                    // Show function badge in message
                                    const textContent = agentDiv.querySelector('.text-content');
                                    const thinking = textContent.querySelector('.thinking');
                                    if (thinking) {
                                        thinking.innerHTML = '<div class="function-badge">🔧 ' + data.name + '</div><div class="thinking-dots"><span></span><span></span><span></span></div>';
                                    }
                                } else if (data.type === 'done') {
                                    // Wait for typewriter to finish
                                    while (isTyping) {
                                        await new Promise(resolve => setTimeout(resolve, 50));
                                    }
                                    removeCursor(agentDiv);
                                    agentDiv.classList.remove('streaming');
                                    updateStatus('พร้อมใช้งาน', '✅');
                                } else if (data.type === 'error') {
                                    const textContent = agentDiv.querySelector('.text-content');
                                    if (textContent) {
                                        textContent.textContent = 'เกิดข้อผิดพลาด: ' + data.message;
                                    }
                                    agentDiv.classList.remove('streaming');
                                    updateStatus('เกิดข้อผิดพลาด', '❌');
                                }
                            } catch (e) {
                                // Fallback for non-JSON data
                                if (dataStr && !dataStr.startsWith('{')) {
                                    await typeText(agentDiv, targetText + dataStr);
                                }
                            }
                        }
                    }
                }
                
                // Ensure typing completes
                while (isTyping) {
                    await new Promise(resolve => setTimeout(resolve, 50));
                }
                
                removeCursor(agentDiv);
                agentDiv.classList.remove('streaming');
                
                if (!targetText) {
                    const textContent = agentDiv.querySelector('.text-content');
                    if (textContent) textContent.textContent = '(ไม่มีการตอบกลับ)';
                }
                
            } catch (error) {
                const textContent = agentDiv.querySelector('.text-content');
                if (textContent) textContent.textContent = 'เกิดข้อผิดพลาด: ' + error.message;
                agentDiv.classList.remove('streaming');
                updateStatus('เกิดข้อผิดพลาด', '❌');
            }
            
            document.getElementById('sendBtn').disabled = false;
            updateStatus('พร้อมใช้งาน', '');
        }
    </script>
</body>
</html>
"""


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "agent": "travel_agent"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
