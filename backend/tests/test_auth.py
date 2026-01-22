
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.database import get_session
from app.models import User, OTPVerification
from app.security import get_password_hash
from datetime import datetime, timezone, timedelta
import secrets

# Setup test DB
sqlite_file_name = "test.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="session")
def session_fixture():
    create_db_and_tables()
    with Session(engine) as session:
        yield session
    drop_db_and_tables()

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_register_user(client: TestClient, session: Session):
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "Password123!", "full_name": "Test User"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_verified"] is False

    # Check if user in DB
    user = session.query(User).filter(User.email == "test@example.com").first()
    assert user is not None

def test_verify_email(client: TestClient, session: Session):
    # Register first
    client.post(
        "/api/auth/register",
        json={"email": "verify@example.com", "password": "Password123!", "full_name": "Verify User"}
    )

    # Get OTP from DB manually (since email is simulated)
    user = session.query(User).filter(User.email == "verify@example.com").first()
    otp_record = session.query(OTPVerification).filter(OTPVerification.user_id == user.id).first()

    response = client.post(
        "/api/auth/verify-email",
        json={"email": "verify@example.com", "otp": otp_record.otp_code}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Email verified successfully"

    # Check verified status
    session.refresh(user)
    assert user.is_verified is True

def test_login(client: TestClient, session: Session):
    # Setup verified user
    password = "Password123!"
    hashed = get_password_hash(password)
    user = User(email="login@example.com", password_hash=hashed, full_name="Login User", is_verified=True)
    session.add(user)
    session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": "login@example.com", "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
