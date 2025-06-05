#!/usr/bin/env python3
"""
Create .env file with proper configuration for Tigu B2B application
"""

import secrets
import os

def generate_secret_key():
    """Generate a secure SECRET_KEY"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """Create .env file with proper configuration"""
    
    # Generate a secure SECRET_KEY
    secret_key = generate_secret_key()
    
    # .env file content
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
    
    # Get the current directory (should be the project root)
    current_dir = os.getcwd()
    env_file_path = os.path.join(current_dir, '.env')
    
    print("=" * 60)
    print("Creating .env file for Tigu B2B Application")
    print("=" * 60)
    print(f"Current directory: {current_dir}")
    print(f"Creating .env file at: {env_file_path}")
    print()
    
    # Check if .env file already exists
    if os.path.exists(env_file_path):
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Cancelled. .env file not created.")
            return
    
    try:
        # Write the .env file
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created successfully!")
        print(f"📍 Location: {env_file_path}")
        print(f"🔑 Generated SECRET_KEY: {secret_key}")
        print()
        print("🎉 Your application is now configured!")
        print()
        print("Next steps:")
        print("1. Test database connection: python test_db_connection.py")
        print("2. Start the server: python start_server.py")
        print("3. Access API docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        print()
        print("Manual steps:")
        print("1. Create a file named '.env' in this directory")
        print("2. Copy the content shown above into the file")
        print("3. Save the file")

if __name__ == "__main__":
    create_env_file() 