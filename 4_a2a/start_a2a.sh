#!/bin/bash

# A2A Server Startup Script
# This script sets up and runs the A2A Travel Manager agent

set -e  # Exit on error

PROJECT_ROOT="/Users/suphakorn_p/Documents/AREAS/POCs/adk-mcp-a2a-linebot-mcp-server"
A2A_DIR="${PROJECT_ROOT}/4_a2a/remote_agent/travel_manager"
VENV_DIR="${A2A_DIR}/.venv"

echo "🚀 Starting A2A Travel Manager Setup..."

# Navigate to the A2A directory
cd "${A2A_DIR}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please create .env file from .env.example and add your GEMINI_API_KEY"
    echo "   Example: cp .env.example .env"
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
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "📦 Installing uvicorn..."
    pip install uvicorn
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting A2A server on port 8001..."
echo "📍 Agent Card will be available at: http://localhost:8001/.well-known/agent.json"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the A2A server
uvicorn agent:a2a_app --port 8001 --reload --env-file .env
