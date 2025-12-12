
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from pathlib import Path

class StorageType(str, Enum):
    LOCAL = "local"

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/medstory.db"
    STORAGE_TYPE: StorageType = StorageType.LOCAL
    MEDIA_DIR: Path = Path("/app/media")
    CORS_ORIGINS: str = "*"

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
