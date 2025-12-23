
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from pathlib import Path

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

    model_config = SettingsConfigDict(env_file=".env")

    def get_cors_origins(self) -> list[str]:
        """Parse CORS_ORIGINS into a list"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

settings = Settings()

# Ensure media directory exists if using local storage
if settings.STORAGE_TYPE == StorageType.LOCAL:
    settings.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
