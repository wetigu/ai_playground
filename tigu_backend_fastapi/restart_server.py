#!/usr/bin/env python3
"""
Clean cache and restart server script
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def clean_pycache():
    """Remove all __pycache__ directories"""
    print("🧹 Cleaning Python cache...")
    for root, dirs, files in os.walk("."):
        for dir_name in dirs[:]:  # Use slice to avoid modifying during iteration
            if dir_name == "__pycache__":
                cache_path = os.path.join(root, dir_name)
                print(f"  Removing: {cache_path}")
                shutil.rmtree(cache_path)
                dirs.remove(dir_name)  # Remove from dirs list

def clean_pyc_files():
    """Remove all .pyc files"""
    print("🧹 Cleaning .pyc files...")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                print(f"  Removing: {pyc_path}")
                os.remove(pyc_path)

def restart_server():
    """Restart the FastAPI server"""
    print("🚀 Starting server...")
    try:
        # Kill any existing uvicorn processes first
        try:
            subprocess.run(["pkill", "-f", "uvicorn"], check=False)
        except:
            pass
        
        # Start the server
        cmd = [
            "poetry", "run", "uvicorn", 
            "tigu_backend_fastapi.app.main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
        return False
    
    return True

if __name__ == "__main__":
    print("🔄 Restarting Tigu Backend FastAPI Server")
    print("=" * 50)
    
    clean_pycache()
    clean_pyc_files()
    
    print("\n✅ Cache cleaned successfully!")
    print("🚀 Starting server with fresh cache...")
    
    success = restart_server()
    
    if success:
        print("✅ Server started successfully!")
    else:
        print("❌ Failed to start server")
        sys.exit(1) 