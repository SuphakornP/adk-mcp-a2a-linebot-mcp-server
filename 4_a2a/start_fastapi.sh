#!/bin/bash

# FastAPI SSE App Startup Script
# This script sets up and runs the FastAPI app that connects to the assistant agent

set -e  # Exit on error

PROJECT_ROOT="/Users/suphakorn_p/Documents/AREAS/POCs/adk-mcp-a2a-linebot-mcp-server"
A2A_DIR="${PROJECT_ROOT}/4_a2a"
VENV_DIR="${PROJECT_ROOT}/.venv"

echo "🚀 Starting FastAPI Assistant App Setup..."

# Navigate to the 4_a2a directory
cd "${A2A_DIR}"

# Check if .env file exists in project root
if [ ! -f "${PROJECT_ROOT}/.env" ]; then
    echo "⚠️  Warning: .env file not found in project root!"
    echo "📝 Please create .env file with your GOOGLE_API_KEY"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "${VENV_DIR}" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "${VENV_DIR}"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "${VENV_DIR}/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📚 Installing dependencies..."
pip install fastapi uvicorn google-adk a2a-sdk --quiet

echo ""
echo "✅ Setup complete!"
echo ""
echo "⚠️  Make sure the A2A Travel Manager server is running on port 8001"
echo "   Run: ./start_a2a.sh"
echo ""
echo "🌐 Starting FastAPI server on port 8002..."
echo "📍 Chat UI available at: http://localhost:8002"
echo "📍 API endpoint: POST http://localhost:8002/chat/stream"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
uvicorn fastapi_app:app --host 0.0.0.0 --port 8002 --reload --env-file "${PROJECT_ROOT}/.env"
