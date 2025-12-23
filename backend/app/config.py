
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from pathlib import Path
from typing import List, Optional

class StorageType(str, Enum):
    LOCAL = "local"

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./medstory.db"
    STORAGE_TYPE: StorageType = StorageType.LOCAL
    MEDIA_DIR: Path = Path("media")
    CORS_ORIGINS: str = "*"

    # External APIs
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-pro"

    # Security
    JWT_SECRET_KEY: str = "change_this_to_a_secure_random_string_for_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True

    # Email (SMTP)
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "noreply@medstory.app"
    SMTP_PASSWORD: str = "password"
    EMAIL_FROM: str = "MedStory <noreply@medstory.app>"

    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")

    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS into a list"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

settings = Settings()

# Ensure media directory exists if using local storage
if settings.STORAGE_TYPE == StorageType.LOCAL:
    settings.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
