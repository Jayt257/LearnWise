"""
backend/app/core/config.py
Pydantic Settings class that reads all configuration from backend/.env file.
Provides a singleton `settings` object imported throughout the app.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "LearnWise"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Groq
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama3-8b-8192"

    # Whisper
    WHISPER_MODEL: str = "base"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    # Admin seed
    ADMIN_EMAIL: str = "admin@learnwise.app"
    ADMIN_PASSWORD: str = "Admin@LearnWise2026"
    ADMIN_USERNAME: str = "admin"

    # Data path (relative to backend/)
    DATA_DIR: str = "data"

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    @property
    def data_path(self) -> str:
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(backend_dir, self.DATA_DIR)

    model_config = {
        "env_file": os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            ".env"
        ),
        "extra": "ignore",
    }


settings = Settings()
