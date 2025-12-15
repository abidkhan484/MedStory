
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .config import settings, StorageType
from .routes import timeline

app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(), 
    allow_credentials=False, # Changed to False to allow wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount media directory for local storage
if settings.STORAGE_TYPE == StorageType.LOCAL:
    app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

@app.get("/")
def read_root():
    return {"message": "Welcome to MedStory API"}

app.include_router(timeline.router, prefix="/api/timeline", tags=["timeline"])
