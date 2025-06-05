#!/usr/bin/env python3
"""
Startup script for Tigu B2B FastAPI server
"""

import sys
import os
import uvicorn

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def start_server():
    """Start the FastAPI server with proper configuration"""
    print("=" * 50)
    print("Starting Tigu B2B FastAPI Server")
    print("=" * 50)
    print(f"Project root: {project_root}")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/api/v1/health")
    print("=" * 50)
    print()
    
    try:
        # Import the app to test if everything is working
        from tigu_backend_fastapi.app.main import app
        print("✅ Application imported successfully")
        
        # Start the server
        uvicorn.run(
            "tigu_backend_fastapi.app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=[project_root],
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the tigu_backend_fastapi directory")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check that all Python files are in the correct locations")
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check database connection")
        print("2. Verify .env file configuration")
        print("3. Ensure port 8000 is not in use")

if __name__ == "__main__":
    start_server() 