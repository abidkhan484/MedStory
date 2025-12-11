
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from backend.app.main import app
from backend.app.database import get_session
from backend.app.config import settings, StorageType
from backend.app.storage import get_storage_service, LocalStorageService
import os
import shutil

# Use in-memory SQLite for tests
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", 
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_read_timeline_empty(client: TestClient):
    response = client.get("/api/timeline/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_status_update(client: TestClient):
    response = client.post(
        "/api/timeline/",
        data={"type": "status", "text": "Feeling good today!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "status"
    assert data["text"] == "Feeling good today!"
    assert data["id"] is not None

def test_create_image_upload(client: TestClient, tmp_path):
    # Setup temporary media dir
    settings.MEDIA_DIR = tmp_path / "media"
    settings.MEDIA_DIR.mkdir()
    settings.STORAGE_TYPE = StorageType.LOCAL
    
    # We need to override the storage dependency because the app creates it at startup/request time
    # but we want it to point to our temp dir.
    # However, since LocalStorageService takes media_dir in constructor, 
    # and get_storage_service uses global settings, modifying settings might work 
    # if get_storage_service is called per request. It is.
    
    # Create a dummy image file
    file_content = b"fake image content"
    files = {"file": ("test.jpg", file_content, "image/jpeg")}
    
    response = client.post(
        "/api/timeline/",
        data={"type": "image", "text": "My prescription"},
        files=files
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "image"
    assert data["text"] == "My prescription"
    assert data["image_url"] is not None
    
    # Verify file exists
    filename = data["image_url"].split("/")[-1]
    assert (settings.MEDIA_DIR / filename).exists()

def test_upload_missing_file_for_image_type(client: TestClient):
    response = client.post(
        "/api/timeline/",
        data={"type": "image", "text": "No file"}
    )
    assert response.status_code == 400
