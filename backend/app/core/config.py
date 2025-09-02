from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres123@localhost:5432/5g_ticketing"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_UPLOADS: str = "uploads"
    MINIO_BUCKET_EXPORTS: str = "exports"
    
    # OCR Service
    OCR_SERVICE_URL: str = "http://localhost:8001"
    
    # JWT
    JWT_SECRET: str = "your-super-secret-jwt-key-change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # File Upload
    MAX_IMAGES_PER_TICKET: int = 8
    MAX_FILE_SIZE_MB: int = 10
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"


settings = Settings()