import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./inventory.db"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API
    API_V1_STR: str = "/api"

    # CORS
    backend_cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]

    # Project Info
    PROJECT_NAME: str = "ERP进销存管理系统"
    VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"

settings = Settings()