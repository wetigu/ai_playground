#!/bin/bash

# Quick development server script
# Usage: ./dev.sh [clean|test|kill|auth-test]

case "${1:-start}" in
    clean)
        echo "🧹 Cleaning cache..."
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true
        echo "✅ Cache cleaned!"
        ;;
    kill)
        echo "🛑 Killing servers..."
        pkill -f "uvicorn.*tigu_backend_fastapi" 2>/dev/null || true
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        echo "✅ Servers stopped!"
        ;;
    test)
        echo "🧪 Testing server health..."
        curl -s http://localhost:8000/api/v1/health | jq '.' 2>/dev/null || echo "Server not responding or jq not installed"
        ;;
    auth-test)
        echo "🔐 Running authentication tests..."
        chmod +x test_auth.sh
        ./test_auth.sh
        ;;
    debug)
        echo "🐛 Starting server in debug mode..."
        export PYTHONPATH="$(pwd):$PYTHONPATH"
        poetry run python -m pdb -c continue -m uvicorn tigu_backend_fastapi.app.main:app --reload --port 8000
        ;;
    start|*)
        echo "🚀 Starting development server..."
        # Clean cache first
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true
        
        # Kill existing servers
        pkill -f "uvicorn.*tigu_backend_fastapi" 2>/dev/null || true
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
        
        # Set environment and start
        export PYTHONPATH="$(pwd):$PYTHONPATH"
        echo "📍 Server: http://localhost:8000"
        echo "📚 Docs: http://localhost:8000/docs"
        echo "🧪 Test: ./dev.sh auth-test"
        poetry run uvicorn tigu_backend_fastapi.app.main:app --reload --host 0.0.0.0 --port 8000
        ;;
esac 