#!/bin/bash

# Create the main project directory
MAIN_DIR="tigu_backend_fastapi"

mkdir -p "$MAIN_DIR"
cd "$MAIN_DIR" || exit

echo "Creating project structure in $(pwd)"

# Create subdirectories
mkdir -p migrations/versions
mkdir -p scripts
mkdir -p app/core
mkdir -p app/api/v1/routers
mkdir -p app/models
mkdir -p app/schemas
mkdir -p app/crud
mkdir -p app/services
mkdir -p app/db
mkdir -p app/utils
mkdir -p tests

# Create root level files

cat << 'EOF_README' > README.md
# tigu_backend_fastapi

FastAPI backend for the Tigu platform.

## Project Structure

- `app/`: Main application code.
  - `api/`: API endpoints (routers).
  - `core/`: Core settings, security, logging.
  - `crud/`: Create, Read, Update, Delete operations.
  - `db/`: Database session and base models.
  - `models/`: SQLAlchemy ORM models.
  - `schemas/`: Pydantic schemas for data validation.
  - `services/`: Business logic services.
  - `utils/`: Utility functions.
- `migrations/`: Alembic database migration scripts.
- `scripts/`: Helper scripts (e.g., for starting the app, initializing DB).
- `tests/`: Test suite.
- `.env.example`: Example environment variables.
- `pyproject.toml`: Project metadata and dependencies (Poetry).
- `Dockerfile`: For containerizing the application.
- `alembic.ini`: Alembic configuration.

## Setup

1.  Clone the repository.
2.  Create a virtual environment and install dependencies:
    ```bash
    poetry install
    ```
3.  Copy `.env.example` to `.env` and update the variables.
4.  Run database migrations:
    ```bash
    alembic upgrade head
    ```
5.  Start the application:
    ```bash
    poetry run uvicorn app.main:app --reload
    ```
EOF_README

cat << 'EOF_ENV' > .env.example
# FastAPI
PROJECT_NAME=tigu_backend_fastapi
DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tigu_db

# Security
SECRET_KEY=your_very_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS - Comma separated list of origins
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF_ENV

cat << 'EOF_POETRY' > pyproject.toml
[tool.poetry]
name = "tigu-backend-fastapi"
version = "0.1.0"
description = "FastAPI backend for Tigu platform"
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.9"
fastapi = "^0.100.0" # Or your preferred version
uvicorn = {extras = ["standard"], version = "^0.23.2"}
sqlalchemy = "^2.0.0"
pydantic = {extras = ["email"], version = "^2.0.0"}
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
alembic = "^1.11.1"
psycopg2-binary = "^2.9.6" # Or asyncpg for async
python-dotenv = "^1.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
httpx = "^0.24.1" # For testing FastAPI async clients

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF_POETRY

touch poetry.lock
echo "# Add project specific libraries here, or manage with pyproject.toml and poetry.lock" > requirements.txt

cat << 'EOF_DOCKER' > Dockerfile
# Start with a Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for psycopg2 and other potential needs
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.5.1 # Pin Poetry version for stable builds

# Copy only the files necessary for poetry to install dependencies
COPY pyproject.toml poetry.lock ./

# Install project dependencies
# --no-root: Do not install the project itself as editable, install from definition
# --no-dev: Do not install development dependencies (like pytest) in production image
RUN poetry config virtualenvs.create false && poetry install --no-root --no-dev

# Copy the rest of the application code into the container
COPY ./app ./app
COPY ./migrations ./migrations
COPY ./alembic.ini ./

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Uvicorn
# It will look for an 'app' variable in 'app/main.py'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF_DOCKER

cat << 'EOF_ALEMBIC' > alembic.ini
# A generic Alembic configuration file.

[alembic]
# path to migration scripts
script_location = migrations

# Comma-separated list of supported database dialects
# dialects = postgresql, mysql, sqlite, oracle, mssql

# Template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# Revision ID generation function
# revision_environment = false

# timezone for generated timestamps
# timezone = UTC

# System V style locks file for online migrations
# sourceless = false

# True to write revision files to standard out
# output_encoding = utf-8

sqlalchemy.url = postgresql://user:pass@localhost/dbname

[post_write_hooks]
# format using "black"
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 migrations


# Logging configuration

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF_ALEMBIC

# Create files in scripts/
touch scripts/start.sh
chmod +x scripts/start.sh
cat << 'EOF_START_SH' > scripts/start.sh
#!/bin/bash
# Run migrations
alembic upgrade head

# Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
EOF_START_SH

touch scripts/init_db.sh
chmod +x scripts/init_db.sh
cat << 'EOF_INIT_DB_SH' > scripts/init_db.sh
#!/bin/bash
# This is a placeholder for database initialization logic.
# You might use this to create an initial superuser or seed data.
echo "Initializing database (placeholder)..."
# Example: poetry run python app/initial_data.py
EOF_INIT_DB_SH

# Create files in app/
touch app/main.py
cat << 'EOF_APP_MAIN' > app/main.py
from fastapi import FastAPI
from app.core.config import settings
# from app.api.v1.api import api_router # Assuming you create this aggregator

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Placeholder for root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# Include your API routers here
# app.include_router(api_router, prefix=settings.API_V1_STR)

# Example: Add a simple health check endpoint
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
EOF_APP_MAIN

# Create files in app/core/
touch app/core/config.py
cat << 'EOF_APP_CORE_CONFIG' > app/core/config.py
import os
from pydantic_settings import BaseSettings
from typing import List, Union
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "FastAPI Application")
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db") # Default to SQLite for easy start

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key_please_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = os.getenv("BACKEND_CORS_ORIGINS", "*")

    class Config:
        case_sensitive = True

settings = Settings()
EOF_APP_CORE_CONFIG

touch app/core/security.py
echo "# Authentication and authorization logic (e.g., JWT handling)" > app/core/security.py

touch app/core/logging.py
echo "# Logging configuration for the application" > app/core/logging.py

# Create files in app/api/
touch app/api/deps.py
echo "# Dependencies for API endpoints (e.g., get_db_session, get_current_user)" > app/api/deps.py

# Create files in app/api/v1/routers/
touch app/api/v1/routers/orders.py
echo "# API Endpoints for orders" > app/api/v1/routers/orders.py

touch app/api/v1/routers/products.py
echo "# API Endpoints for products" > app/api/v1/routers/products.py

# Create files in app/models/
touch app/models/order.py
echo "# SQLAlchemy model for Order" > app/models/order.py

touch app/models/product.py
echo "# SQLAlchemy model for Product" > app/models/product.py

touch app/models/user.py
echo "# SQLAlchemy model for User" > app/models/user.py

# Create files in app/schemas/
touch app/schemas/order.py
echo "# Pydantic schema for Order (request/response)" > app/schemas/order.py

touch app/schemas/product.py
echo "# Pydantic schema for Product (request/response)" > app/schemas/product.py

touch app/schemas/user.py
echo "# Pydantic schema for User (request/response)" > app/schemas/user.py

# Create files in app/crud/
touch app/crud/order.py
echo "# CRUD operations for Order model" > app/crud/order.py

touch app/crud/product.py
echo "# CRUD operations for Product model" > app/crud/product.py

# Create files in app/services/
touch app/services/payment_gateway.py
echo "# Service for interacting with payment gateways" > app/services/payment_gateway.py

touch app/services/notification.py
echo "# Service for sending notifications (email, SMS, etc.)" > app/services/notification.py

# Create files in app/db/
touch app/db/base.py
cat << 'EOF_APP_DB_BASE' > app/db/base.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF_APP_DB_BASE

# Create files in app/utils/
touch app/utils/pagination.py
echo "# Utility functions for pagination" > app/utils/pagination.py

touch app/utils/exceptions.py
echo "# Custom exception handlers and classes" > app/utils/exceptions.py

# Create __init__.py files to make directories Python packages
touch app/__init__.py
touch app/core/__init__.py
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/api/v1/routers/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/crud/__init__.py
touch app/services/__init__.py
touch app/db/__init__.py
touch app/utils/__init__.py

# Create files in tests/
touch tests/conftest.py
echo "# Pytest configuration and fixtures" > tests/conftest.py

touch tests/test_products.py
echo "# Test cases for product-related functionality" > tests/test_products.py

cd ..
echo "Backend project '$MAIN_DIR' structure created successfully in $(pwd)/$MAIN_DIR"
echo "Remember to 'cd $MAIN_DIR' to start working on the project."
