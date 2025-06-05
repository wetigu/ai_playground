#!/bin/bash

# Tigu Backend FastAPI Server Restart Script for Ubuntu/Linux
# This script cleans Python cache and starts the server with fresh environment

set -e  # Exit on any error

echo "🔄 Restarting Tigu Backend FastAPI Server"
echo "=========================================="

# Function to clean Python cache
clean_cache() {
    echo "🧹 Cleaning Python cache..."
    
    # Remove __pycache__ directories
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # Remove .pyc files
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Remove .pyo files
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    echo "✅ Cache cleaned successfully!"
}

# Function to kill existing server processes
kill_existing_servers() {
    echo "🛑 Stopping any existing server processes..."
    
    # Kill uvicorn processes
    pkill -f "uvicorn.*tigu_backend_fastapi" 2>/dev/null || true
    
    # Kill any process using port 8000
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    
    # Wait a moment for processes to stop
    sleep 2
    
    echo "✅ Existing processes stopped!"
}

# Function to check Python environment
check_environment() {
    echo "🔍 Checking environment..."
    
    # Check if we're in the right directory
    if [[ ! -f "pyproject.toml" ]]; then
        echo "❌ Error: pyproject.toml not found. Are you in the right directory?"
        exit 1
    fi
    
    # Check if poetry is installed
    if ! command -v poetry &> /dev/null; then
        echo "❌ Error: Poetry is not installed. Please install poetry first."
        exit 1
    fi
    
    # Check if virtual environment exists
    if ! poetry env info &> /dev/null; then
        echo "🔧 Creating virtual environment..."
        poetry install
    fi
    
    echo "✅ Environment ready!"
}

# Function to start the server
start_server() {
    echo "🚀 Starting server..."
    echo "📍 Server will be available at: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo "🔄 ReDoc Documentation: http://localhost:8000/redoc"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Set PYTHONPATH to ensure proper module resolution
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    
    # Start the server with proper module path
    poetry run uvicorn tigu_backend_fastapi.app.main:app \
        --reload \
        --host 0.0.0.0 \
        --port 8000 \
        --reload-dir tigu_backend_fastapi \
        --log-level info
}

# Function to handle script interruption
cleanup() {
    echo ""
    echo "🛑 Shutting down server..."
    kill_existing_servers
    echo "👋 Server stopped. Goodbye!"
    exit 0
}

# Trap Ctrl+C and call cleanup function
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    echo "🏁 Starting Tigu Backend FastAPI Server"
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Execute startup sequence
    check_environment
    clean_cache
    kill_existing_servers
    
    echo ""
    echo "🎉 Ready to start server!"
    echo ""
    
    # Start the server (this will run until interrupted)
    start_server
}

# Help function
show_help() {
    echo "Tigu Backend FastAPI Server Restart Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -c, --clean    Only clean cache and exit"
    echo "  -k, --kill     Only kill existing servers and exit"
    echo "  -t, --test     Test environment and exit"
    echo ""
    echo "Examples:"
    echo "  $0              # Start server with cache cleanup"
    echo "  $0 --clean     # Only clean cache"
    echo "  $0 --kill      # Only stop existing servers"
    echo ""
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -c|--clean)
        clean_cache
        exit 0
        ;;
    -k|--kill)
        kill_existing_servers
        exit 0
        ;;
    -t|--test)
        check_environment
        echo "✅ Environment test passed!"
        exit 0
        ;;
    "")
        # No arguments, run main function
        main
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac 