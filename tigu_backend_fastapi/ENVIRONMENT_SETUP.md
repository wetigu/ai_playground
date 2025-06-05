# Environment Setup for Tigu B2B Backend

## Database Configuration

The application is now configured to connect to the live MySQL database with the following settings:

- **Host**: sql.wetigu.com
- **Port**: 3306
- **Database**: tigu_db
- **Username**: tigu
- **Password**: database password

## Generate SECRET_KEY

Before setting up the environment, generate a secure SECRET_KEY:

```bash
cd tigu_backend_fastapi
python generate_secret_key.py
```

Copy one of the generated SECRET_KEY values for use in your `.env` file.

## Environment Variables

Create a `.env` file in the project root with the following configuration:

```bash
# Database Configuration
DATABASE_URL=mysql+pymysql://tigu:password_here@sql.wetigu.com:3306/tigu_db

# Security Configuration (replace with generated key)
SECRET_KEY=your-generated-secret-key-here
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
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png,gif,webp
ALLOWED_VIDEO_EXTENSIONS=mp4,webm,avi,mov

# Redis Configuration (for future caching)
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=development
```

## Quick Setup

1. **Generate SECRET_KEY:**
   ```bash
   cd tigu_backend_fastapi
   python generate_secret_key.py
   ```

2. **Create `.env` file** in the project root directory with the configuration above (use your generated SECRET_KEY).

3. **Install dependencies:**
   ```bash
   cd tigu_backend_fastapi
   pip install -r requirements.txt
   ```

4. **Test database connection:**
   ```bash
   cd tigu_backend_fastapi
   python test_db_connection.py
   ```

5. **Run the application:**
   ```bash
   cd tigu_backend_fastapi/tigu_backend_fastapi
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/v1/health

## Alternative Startup Methods

If the above doesn't work, try these alternatives:

**Method 1 - From project root:**
```bash
cd tigu_backend_fastapi
python -m uvicorn tigu_backend_fastapi.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Method 2 - Using Python path:**
```bash
cd tigu_backend_fastapi
PYTHONPATH=. uvicorn tigu_backend_fastapi.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Method 3 - Direct Python execution:**
```bash
cd tigu_backend_fastapi/tigu_backend_fastapi
python -c "import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)"
```

## Database Connection

The application will automatically connect to the live MySQL database using the configuration above. The database connection includes:

- **Connection pooling** for better performance
- **Automatic reconnection** on connection loss
- **SQL query logging** in debug mode
- **Migration support** through Alembic

## Security Notes

- Generate a unique SECRET_KEY for each environment (development, staging, production)
- Never commit the `.env` file to version control
- The SECRET_KEY should be at least 32 characters long
- In production, consider using environment-specific configurations
- Enable SSL/TLS for database connections in production

## Troubleshooting

### Server Startup Issues:
1. **ModuleNotFoundError**: Make sure you're in the correct directory
2. **Import errors**: Check that all dependencies are installed
3. **Port conflicts**: Use a different port if 8000 is occupied

### Database Connection Issues:
1. **Check network connectivity** to sql.wetigu.com:3306
2. **Verify database credentials** are correct
3. **Ensure the database exists** and is accessible
4. **Check firewall settings** that might block the connection
5. **Review application logs** for detailed error messages

## Database Schema

The application will automatically create the required database tables on startup. The schema includes:

- User and authentication tables
- Company and user association tables
- Product catalog with categories and media
- Order and quotation management
- Video content and analytics
- Audit logs and business operations

For detailed schema information, refer to `tigusql.sql` and the database design documentation. 