# A2A Setup and Testing Guide

## Quick Start

This project uses `.venv` virtual environments for dependency isolation.

### Option 1: Using Shell Scripts (Recommended)

#### 1. Start the A2A Remote Server
```bash
cd /Users/suphakorn_p/Documents/AREAS/POCs/adk-mcp-a2a-linebot-mcp-server/4_a2a
./start_a2a.sh
```

This will:
- Create a virtual environment at `4_a2a/remote_agent/travel_manager/.venv`
- Install all dependencies
- Start the A2A server on port 8001

#### 2. Start the Local ADK Agent (in a new terminal)
```bash
cd /Users/suphakorn_p/Documents/AREAS/POCs/adk-mcp-a2a-linebot-mcp-server/4_a2a
./start_local_agent.sh
```

This will:
- Use the project root `.venv`
- Start the ADK web interface

### Option 2: Manual Setup

#### 1. Setup and Start A2A Remote Server
```bash
cd /Users/suphakorn_p/Documents/AREAS/POCs/adk-mcp-a2a-linebot-mcp-server/4_a2a/remote_agent/travel_manager

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn agent:a2a_app --port 8001 --reload --env-file .env
```

#### 2. Setup and Start Local Agent (in a new terminal)
```bash
cd /Users/suphakorn_p/Documents/AREAS/POCs/adk-mcp-a2a-linebot-mcp-server

# Create virtual environment at project root
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Navigate to 4_a2a and start ADK (specify agent file to avoid loading remote_agent directory)
cd 4_a2a
adk web --agent-file agent.py
```

## Important Notes

### Environment Variables
Make sure you have a `.env` file in `4_a2a/remote_agent/travel_manager/` with:
```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GEMINI_API_KEY=your_api_key_here
```

### Testing the A2A Connection

1. **Check Agent Card**: Visit http://localhost:8001/.well-known/agent.json
2. **Test the Agent**: Use the ADK web interface to interact with the travel manager agent

### Architecture

- **Remote A2A Server** (port 8001): Travel Manager agent with Airbnb MCP toolset
- **Local ADK Agent**: Connects to the remote agent via A2A protocol

## FastAPI SSE POC

A simple FastAPI app that demonstrates streaming A2A agent responses via Server-Sent Events (SSE).

### Running the FastAPI SSE App

**Terminal 3 - Start FastAPI SSE app (after A2A server is running):**
```bash
cd /Users/suphakorn_p/Documents/AREAS/POCs/adk-mcp-a2a-linebot-mcp-server/4_a2a
./start_fastapi_sse.sh
```

This will:
- Start a FastAPI server on port 8002
- Provide a web UI at http://localhost:8002
- Expose a streaming endpoint at `POST /chat/stream`

### API Usage

```bash
curl -X POST http://localhost:8002/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "หาที่พักในเชียงใหม่", "user_id": "test_user"}'
```

### Troubleshooting

- **Error: "No root_agent found for 'remote_agent'"**: Use `adk web --agent-file agent.py` to explicitly specify the local agent file
- If port 8001 is already in use, change the port in both `agent.py` files
- Make sure Node.js is installed (required for the Airbnb MCP server)
- Ensure your GEMINI_API_KEY is valid in the `.env` file
