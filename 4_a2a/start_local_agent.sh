#!/bin/bash

# Local ADK Agent Startup Script
# This script runs the local agent that connects to the A2A remote agent

set -e  # Exit on error

PROJECT_ROOT="/Users/suphakorn_p/Documents/AREAS/POCs/adk-mcp-a2a-linebot-mcp-server"
A2A_DIR="${PROJECT_ROOT}/4_a2a"
VENV_DIR="${PROJECT_ROOT}/.venv"

echo "🚀 Starting Local ADK Agent..."

# Navigate to the 4_a2a directory
cd "${A2A_DIR}"

# Create virtual environment if it doesn't exist
if [ ! -d "${VENV_DIR}" ]; then
    echo "📦 Creating virtual environment at project root..."
    cd "${PROJECT_ROOT}"
    python3 -m venv .venv
    cd "${A2A_DIR}"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "${VENV_DIR}/bin/activate"

# Install dependencies if needed
if [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
    echo "📚 Installing dependencies..."
    pip install -q -r "${PROJECT_ROOT}/requirements.txt"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting ADK web interface..."
echo "📍 Make sure the A2A server is running on port 8001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start ADK web - specify the agent file explicitly to avoid loading remote_agent directory
adk web --agent-file agent.py
