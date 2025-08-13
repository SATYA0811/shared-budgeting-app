"""Application configuration."""
import os
from typing import List, Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "sqlite:///./budgeting.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"]
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["pdf", "csv", "xlsx", "xls"]
    upload_directory: str = "./uploads"
    
    # Rate Limiting
    rate_limit_storage: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    # Email (for notifications)
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Redis (for caching and background tasks)
    redis_url: Optional[str] = None
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Validate critical settings in production
if settings.environment == "production":
    if settings.secret_key == "your-secret-key-change-in-production":
        raise ValueError("SECRET_KEY must be changed in production")
    
    if settings.database_url.startswith("sqlite"):
        raise ValueError("SQLite is not recommended for production. Use PostgreSQL.")
    
    settings.debug = False