
import abc
import shutil
from pathlib import Path
from fastapi import UploadFile
from .config import settings, StorageType
import boto3
from botocore.exceptions import NoCredentialsError

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

class S3StorageService(StorageService):
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.AWS_BUCKET_NAME

    async def upload(self, file: UploadFile, filename: str) -> str:
        try:
            # UploadFile.file is a SpooledTemporaryFile
            # We need to seek to 0 just in case
            file.file.seek(0)
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket,
                filename,
                ExtraArgs={'ContentType': file.content_type or 'application/octet-stream'}
            )
            return self.get_url(filename)
        except NoCredentialsError:
            raise Exception("AWS Credentials not available")

    def get_url(self, filename: str) -> str:
        return f"https://{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{filename}"

def get_storage_service() -> StorageService:
    if settings.STORAGE_TYPE == StorageType.LOCAL:
        return LocalStorageService(settings.MEDIA_DIR)
    elif settings.STORAGE_TYPE == StorageType.S3:
        return S3StorageService()
    else:
        raise ValueError(f"Unsupported storage type: {settings.STORAGE_TYPE}")
