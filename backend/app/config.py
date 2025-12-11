
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from pathlib import Path

class StorageType(str, Enum):
    LOCAL = "local"

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./medstory.db"
    STORAGE_TYPE: StorageType = StorageType.LOCAL
    MEDIA_DIR: Path = Path("media")

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

# Ensure media directory exists if using local storage
if settings.STORAGE_TYPE == StorageType.LOCAL:
    settings.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
