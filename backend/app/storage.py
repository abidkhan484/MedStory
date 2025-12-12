
import abc
import shutil
from pathlib import Path
from fastapi import UploadFile
from .config import settings, StorageType

class StorageService(abc.ABC):
    @abc.abstractmethod
    async def upload(self, file: UploadFile, filename: str) -> str:
        """Uploads a file and returns the URL or path"""
        pass

    @abc.abstractmethod
    def get_url(self, filename: str) -> str:
        """Returns the access URL for the file"""
        pass

class LocalStorageService(StorageService):
    def __init__(self, media_dir: Path):
        self.media_dir = media_dir

    async def upload(self, file: UploadFile, filename: str) -> str:
        file_path = self.media_dir / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return str(file_path)

    def get_url(self, filename: str) -> str:
        # Return relative URL
        return f"/media/{filename}"

def get_storage_service() -> StorageService:
    if settings.STORAGE_TYPE == StorageType.LOCAL:
        return LocalStorageService(settings.MEDIA_DIR)
    else:
        raise ValueError(f"Unsupported storage type: {settings.STORAGE_TYPE}")
