#!/usr/bin/env python3
"""
Complete setup and run script for Tigu B2B FastAPI application
"""

import os
import sys
import subprocess
import secrets

def generate_secret_key():
    """Generate a secure SECRET_KEY"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file_path = '.env'
    
    if os.path.exists(env_file_path):
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    
    secret_key = generate_secret_key()
    
    env_content = f"""# Database Configuration
DATABASE_URL=mysql+pymysql://tigu:T1gu125443!@sql.wetigu.com:3306/tigu_db

# Security Configuration
SECRET_KEY={secret_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
PROJECT_NAME=Tigu B2B Building Materials Marketplace
API_V1_STR=/api/v1
DEBUG=True

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "https://tigu.com", "https://www.tigu.com"]

# Email Configuration (for future use)
SMTP_TLS=True
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=
SMTP_PASSWORD=

# File Upload Configuration
MAX_FILE_SIZE=10485760
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png,gif,webp
ALLOWED_VIDEO_EXTENSIONS=mp4,webm,avi,mov

# Redis Configuration (for future caching)
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=development
"""
    
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        print(f"✅ .env file created successfully!")
        print(f"🔑 Generated SECRET_KEY: {secret_key}")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    dependencies = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "pymysql==1.1.0",
        "cryptography==41.0.7",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-multipart==0.0.6",
        "pydantic[email]==2.5.0",
        "python-dotenv==1.0.0"
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Could not install {dep}: {e}")
    
    print("✅ Dependencies installation completed")

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        from tigu_backend_fastapi.app.core.config import settings
        from tigu_backend_fastapi.app.db.base import engine
        
        print(f"Database URL: {settings.DATABASE_URL}")
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute("SELECT 1 as test")
            test_value = result.fetchone()[0]
            print(f"✅ Database connection successful! Test query returned: {test_value}")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please check your database configuration and network connectivity.")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Tigu B2B FastAPI Server...")
    print("=" * 50)
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/api/v1/health")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Add current directory to Python path
        current_dir = os.getcwd()
        env = os.environ.copy()
        env['PYTHONPATH'] = current_dir
        
        # Start uvicorn server
        cmd = [
            sys.executable, "-m", "uvicorn",
            "tigu_backend_fastapi.app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ]
        
        subprocess.run(cmd, env=env, cwd=current_dir)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check that all dependencies are installed")
        print("2. Verify database connection")
        print("3. Ensure port 8000 is not in use")

def main():
    """Main setup and run function"""
    print("=" * 60)
    print("🏗️  Tigu B2B FastAPI Application Setup")
    print("=" * 60)
    print(f"Current directory: {os.getcwd()}")
    print()
    
    # Step 1: Create .env file
    if not create_env_file():
        print("❌ Setup failed: Could not create .env file")
        return
    
    print()
    
    # Step 2: Install dependencies
    install_dependencies()
    print()
    
    # Step 3: Test database connection
    if not test_database_connection():
        print("⚠️  Database connection failed, but continuing with server startup...")
    
    print()
    
    # Step 4: Start server
    start_server()

if __name__ == "__main__":
    main() 