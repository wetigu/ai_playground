# Tigu Backend FastAPI - Ubuntu Setup Guide

## 🚀 Quick Start

### 1. Make Scripts Executable
```bash
chmod +x restart_ubuntu.sh
chmod +x dev.sh
```

### 2. Start the Server
```bash
# Full restart with environment check
./restart_ubuntu.sh

# Quick development start
./dev.sh
```

## 📋 Prerequisites

### Install Required Tools
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Poetry (Python dependency manager)
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (add to ~/.bashrc)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Install additional tools
sudo apt install curl jq lsof -y
```

### Verify Installation
```bash
python3 --version    # Should be 3.8+
poetry --version     # Should show poetry version
```

## 🔧 Project Setup

### 1. Install Dependencies
```bash
cd tigu_backend_fastapi
poetry install
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit database configuration
nano .env
```

### 3. Database Configuration
Ensure your `.env` file has:
```env
DATABASE_URL=mysql+pymysql://username:password@host:port/database
SECRET_KEY=your-secret-key-here
```

## 🎮 Available Scripts

### Main Scripts

#### `./restart_ubuntu.sh` - Full Production Restart
- ✅ Environment validation
- 🧹 Cache cleanup
- 🛑 Kill existing processes
- 🚀 Start server with full logging

Options:
```bash
./restart_ubuntu.sh --help     # Show help
./restart_ubuntu.sh --clean    # Only clean cache
./restart_ubuntu.sh --kill     # Only kill servers
./restart_ubuntu.sh --test     # Test environment
```

#### `./dev.sh` - Quick Development
- 🚀 Fast server start
- 🧹 Auto cache cleanup
- 🧪 Built-in testing

Options:
```bash
./dev.sh start    # Start server (default)
./dev.sh clean    # Clean cache only
./dev.sh kill     # Kill servers only
./dev.sh test     # Test registration endpoint
./dev.sh debug    # Start with Python debugger
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Module Import Error
```
ModuleNotFoundError: No module named 'tigu_backend_fastapi.app'
```

**Solution:**
```bash
# Ensure you're in the right directory
cd tigu_backend_fastapi

# Clean cache and restart
./dev.sh clean
./dev.sh start
```

#### 2. Port Already in Use
```
Error: Port 8000 is already in use
```

**Solution:**
```bash
# Kill existing processes
./dev.sh kill

# Or manually:
sudo lsof -ti:8000 | xargs kill -9
```

#### 3. Database ID Generation Error
```
Field 'id' doesn't have a default value
```

**This is FIXED in our updated code:**
- ✅ Models use `autoincrement=False`
- ✅ Manual ID generation with `generate_id()`
- ✅ All INSERT statements include ID values

#### 4. Poetry Virtual Environment Issues
```bash
# Reset virtual environment
poetry env remove python
poetry install

# Or create manually
poetry env use python3
poetry install
```

## 🧪 Testing the Fix

### 1. Start Server
```bash
./dev.sh start
```

### 2. Test Registration Endpoint
```bash
# Using the built-in test
./dev.sh test

# Or manually:
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com", 
    "password": "Test123456!",
    "full_name": "Test User",
    "phone": "1234567890",
    "company_name": "Test Company",
    "company_type": "buyer",
    "business_license": "TEST123",
    "tax_number": "TAX123"
  }'
```

### 3. Expected Success Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1734567890123456,
    "email": "test@example.com",
    "full_name": "Test User",
    "default_company_id": 1734567890789012
  }
}
```

## 📚 API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 🔒 Security Notes

### Production Deployment
1. **Change default secrets**:
   ```bash
   # Generate new secret key
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update database credentials**
3. **Configure CORS origins**
4. **Enable HTTPS**
5. **Set up reverse proxy (nginx)**

### Environment Variables
```env
# Required
DATABASE_URL=mysql+pymysql://user:pass@host:port/db
SECRET_KEY=your-super-secret-key-change-this

# Optional
DEBUG=False
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 🆘 Getting Help

### Check Logs
```bash
# Server logs are displayed in terminal
# For background running:
nohup ./dev.sh start > server.log 2>&1 &
tail -f server.log
```

### Debug Mode
```bash
# Start with Python debugger
./dev.sh debug

# Or add breakpoints in code:
import pdb; pdb.set_trace()
```

### Common Commands
```bash
# Check server status
curl http://localhost:8000/api/v1/health

# View running processes
ps aux | grep uvicorn

# Check port usage
sudo netstat -tlnp | grep :8000
```

## ✅ Verification Checklist

- [ ] Poetry installed and working
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Database connection configured
- [ ] Scripts made executable
- [ ] Server starts without errors
- [ ] Registration endpoint works
- [ ] API documentation accessible
- [ ] No ID generation errors

---

**Need help?** Check the error logs and try the troubleshooting steps above.
**Still stuck?** The ID generation issue should be completely resolved with our updated models and explicit ID assignment. 