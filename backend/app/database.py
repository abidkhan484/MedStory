
from sqlmodel import create_engine, Session
from .config import settings

# If using sqlite, check_same_thread=False is needed for FastAPI
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session
