#!/bin/bash

# FastAPI SSE POC Startup Script
# This script starts the FastAPI app that streams A2A agent responses via SSE

set -e

PROJECT_ROOT="/Users/suphakorn_p/Documents/AREAS/POCs/adk-mcp-a2a-linebot-mcp-server"
A2A_DIR="${PROJECT_ROOT}/4_a2a"
VENV_DIR="${PROJECT_ROOT}/.venv"

echo "🚀 Starting FastAPI SSE POC..."

cd "${A2A_DIR}"

# Activate virtual environment
if [ -d "${VENV_DIR}" ]; then
    echo "🔧 Activating virtual environment..."
    source "${VENV_DIR}/bin/activate"
else
    echo "❌ Virtual environment not found at ${VENV_DIR}"
    echo "   Please run ./start_a2a.sh first to set up the environment"
    exit 1
fi

# Check if A2A server is running
echo "🔍 Checking if A2A server is running on port 8001..."
if ! curl -s http://localhost:8001/.well-known/agent.json > /dev/null 2>&1; then
    echo "⚠️  Warning: A2A server does not appear to be running on port 8001"
    echo "   Please start it first with: ./start_a2a.sh"
    echo ""
fi

echo ""
echo "✅ Starting FastAPI SSE app on port 8002..."
echo "📍 Web UI: http://localhost:8002"
echo "📍 API Endpoint: POST http://localhost:8002/chat/stream"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI app
uvicorn fastapi_sse_app:app --host 0.0.0.0 --port 8002 --reload
