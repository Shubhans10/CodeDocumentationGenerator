import os
from pydantic import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Intelligent Code Documentation Generator"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Database
    CHROMA_DB_DIR: str = os.getenv("CHROMA_DB_DIR", "./chroma_db")

    # Repository
    REPO_STORAGE_DIR: str = os.getenv("REPO_STORAGE_DIR", "./repositories")

    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    class Config:
        case_sensitive = True

settings = Settings()
