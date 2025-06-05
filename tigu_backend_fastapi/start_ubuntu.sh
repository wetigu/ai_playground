#!/bin/bash

# Simple Ubuntu server start script
echo "🚀 Starting Tigu Backend FastAPI Server..."

# Clean cache
echo "🧹 Cleaning cache..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Kill existing servers
echo "🛑 Stopping existing servers..."
pkill -f "uvicorn.*tigu_backend_fastapi" 2>/dev/null || true
sleep 1

# Start server
echo "📍 Server: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo ""

export PYTHONPATH="$(pwd):$PYTHONPATH"
poetry run uvicorn tigu_backend_fastapi.app.main:app --reload --host 0.0.0.0 --port 8000 