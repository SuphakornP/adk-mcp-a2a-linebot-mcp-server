"""
FastAPI SSE App for ADK Agent

Simple POC to stream responses from the assistant_agent via Server-Sent Events.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

import json
import uuid
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agent import root_agent

app = FastAPI(title="ADK Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session service for managing conversations
session_service = InMemorySessionService()

# Create runner for the agent
runner = Runner(
    agent=root_agent,
    app_name="assistant_app",
    session_service=session_service,
)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


async def stream_agent_response(
    user_id: str,
    session_id: str,
    message: str,
) -> AsyncGenerator[str, None]:
    """Stream agent response as SSE events."""
    
    try:
        # Ensure session exists
        session = await session_service.get_session(
            app_name="assistant_app",
            user_id=user_id,
            session_id=session_id,
        )
        if not session:
            await session_service.create_session(
                app_name="assistant_app",
                user_id=user_id,
                session_id=session_id,
            )
        
        # Create user message
        user_content = genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=message)],
        )
        
        # Stream events from the agent with SSE streaming mode for token-level output
        run_config = RunConfig(streaming_mode=StreamingMode.SSE)
        
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_content,
            run_config=run_config,
        ):
            # Build event data with all available information
            event_data = {
                "id": event.id,
                "author": event.author,
                "invocation_id": event.invocation_id,
                "partial": getattr(event, 'partial', None),
                "turn_complete": getattr(event, 'turn_complete', None),
                "finish_reason": str(event.finish_reason) if event.finish_reason else None,
                "error_code": event.error_code,
                "error_message": event.error_message,
                "interrupted": event.interrupted,
            }
            
            # Check for actions (transfer_to_agent, escalate, state changes)
            if event.actions:
                actions_data = {}
                if event.actions.transfer_to_agent:
                    actions_data["transfer_to_agent"] = event.actions.transfer_to_agent
                if event.actions.escalate:
                    actions_data["escalate"] = event.actions.escalate
                if event.actions.state_delta:
                    actions_data["state_delta"] = {k: str(v) for k, v in event.actions.state_delta.items()}
                if event.actions.artifact_delta:
                    actions_data["artifact_delta"] = event.actions.artifact_delta
                if actions_data:
                    event_data["actions"] = actions_data
            
            # Process content parts
            if event.content and event.content.parts:
                parts_data = []
                for part in event.content.parts:
                    part_info = {}
                    
                    # Text content
                    if hasattr(part, 'text') and part.text:
                        part_info["type"] = "text"
                        part_info["text"] = part.text
                    
                    # Function call (tool use)
                    if hasattr(part, 'function_call') and part.function_call:
                        part_info["type"] = "function_call"
                        part_info["function_name"] = part.function_call.name
                        part_info["function_args"] = part.function_call.args
                        part_info["function_id"] = part.function_call.id
                    
                    # Function response (tool result)
                    if hasattr(part, 'function_response') and part.function_response:
                        part_info["type"] = "function_response"
                        part_info["function_name"] = part.function_response.name
                        part_info["function_id"] = part.function_response.id
                        # Truncate response if too long
                        response_str = str(part.function_response.response)
                        part_info["response_preview"] = response_str[:500] + "..." if len(response_str) > 500 else response_str
                    
                    if part_info:
                        parts_data.append(part_info)
                
                event_data["parts"] = parts_data
            
            # Send the event
            yield f"data: {json.dumps(event_data, ensure_ascii=False, default=str)}\n\n"
        
        # Send done event
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        print(f"[ERROR] Stream error: {e}")
        import traceback
        traceback.print_exc()
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat response via SSE."""
    user_id = "default_user"
    session_id = request.session_id or str(uuid.uuid4())
    
    return StreamingResponse(
        stream_agent_response(user_id, session_id, request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Session-Id": session_id,
        },
    )


@app.get("/", response_class=HTMLResponse)
async def index():
    """Simple chat UI for testing."""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>ADK Assistant Chat</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; height: 100vh; display: flex; flex-direction: column; }
        h1 { text-align: center; color: #333; margin-bottom: 20px; }
        .chat-box { flex: 1; background: white; border-radius: 12px; padding: 20px; overflow-y: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .message { margin-bottom: 16px; padding: 12px 16px; border-radius: 12px; max-width: 80%; }
        .user { background: #007bff; color: white; margin-left: auto; }
        .assistant { background: #e9ecef; color: #333; }
        .input-area { display: flex; gap: 10px; margin-top: 20px; }
        input { flex: 1; padding: 14px 18px; border: 2px solid #ddd; border-radius: 25px; font-size: 16px; outline: none; }
        input:focus { border-color: #007bff; }
        button { padding: 14px 28px; background: #007bff; color: white; border: none; border-radius: 25px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .streaming { opacity: 0.7; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 ADK Assistant</h1>
        <div class="chat-box" id="chatBox"></div>
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="พิมพ์ข้อความ..." onkeypress="if(event.key==='Enter')sendMessage()">
            <button id="sendBtn" onclick="sendMessage()">ส่ง</button>
        </div>
    </div>
    <script>
        let sessionId = null;
        const chatBox = document.getElementById('chatBox');
        const input = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');

        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user' : 'assistant');
            div.textContent = text;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
            return div;
        }

        async function sendMessage() {
            const message = input.value.trim();
            if (!message) return;
            
            input.value = '';
            sendBtn.disabled = true;
            
            addMessage(message, true);
            const assistantDiv = addMessage('', false);
            assistantDiv.classList.add('streaming');
            
            try {
                const response = await fetch('/chat/stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, session_id: sessionId })
                });
                
                sessionId = response.headers.get('X-Session-Id') || sessionId;
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let fullText = '';
                
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                if (data.type === 'done') continue;
                                
                                // Handle new event structure with parts array
                                if (data.author === 'assistant_agent' && data.parts) {
                                    for (const part of data.parts) {
                                        if (part.type === 'text' && part.text) {
                                            if (data.partial) {
                                                fullText += part.text;
                                            } else {
                                                fullText = part.text;
                                            }
                                            assistantDiv.textContent = fullText;
                                            chatBox.scrollTop = chatBox.scrollHeight;
                                        }
                                    }
                                }
                            } catch (e) {}
                        }
                    }
                }
            } catch (error) {
                assistantDiv.textContent = 'Error: ' + error.message;
            }
            
            assistantDiv.classList.remove('streaming');
            sendBtn.disabled = false;
            input.focus();
        }
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
