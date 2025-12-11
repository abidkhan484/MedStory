
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from pathlib import Path

class StorageType(str, Enum):
    LOCAL = "local"
    S3 = "s3"

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./medstory.db"
    STORAGE_TYPE: StorageType = StorageType.LOCAL
    MEDIA_DIR: Path = Path("media")
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_BUCKET_NAME: str | None = None
    AWS_REGION: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

# Ensure media directory exists if using local storage
if settings.STORAGE_TYPE == StorageType.LOCAL:
    settings.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
