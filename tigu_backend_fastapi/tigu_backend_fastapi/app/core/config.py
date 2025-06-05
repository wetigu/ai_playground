import os
from pydantic_settings import BaseSettings
from typing import List, Union
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Tigu B2B Building Materials Marketplace")
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Database - Live MySQL Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://tigu:T1gu125443!@sql.wetigu.com:3306/tigu_db")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production-tigu-b2b-2024")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = os.getenv("BACKEND_CORS_ORIGINS", "*")

    # Email Configuration (for future use)
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "True").lower() == "true"
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

    # File Upload Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_IMAGE_EXTENSIONS: str = os.getenv("ALLOWED_IMAGE_EXTENSIONS", "jpg,jpeg,png,gif,webp")
    ALLOWED_VIDEO_EXTENSIONS: str = os.getenv("ALLOWED_VIDEO_EXTENSIONS", "mp4,webm,avi,mov")

    # Redis Configuration (for future caching)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        case_sensitive = True

settings = Settings()
