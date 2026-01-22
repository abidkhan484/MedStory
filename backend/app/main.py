
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings, StorageType
from .routes import timeline, auth, sharing, relatives

# Rate Limiter
limiter = Limiter(key_func=get_remote_address, enabled=settings.RATE_LIMIT_ENABLED)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(), 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount media directory for local storage
if settings.STORAGE_TYPE == StorageType.LOCAL:
    app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

@app.get("/")
def read_root():
    return {"message": "Welcome to MedStory API"}

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(timeline.router, prefix="/api/timeline", tags=["timeline"])
app.include_router(sharing.router, prefix="/api/sharing", tags=["sharing"])
app.include_router(relatives.router, prefix="/api/relatives", tags=["relatives"])
