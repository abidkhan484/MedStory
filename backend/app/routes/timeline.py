
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from ..database import get_session
from ..models import TimelineItem, ItemType, TimelineItemResponse
from ..storage import get_storage_service, StorageService
from datetime import datetime, timezone
import uuid
import os

router = APIRouter()

@router.get("/", response_model=List[TimelineItemResponse])
def read_timeline(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    items = session.exec(select(TimelineItem).order_by(TimelineItem.created_at.desc()).offset(skip).limit(limit)).all()
    return items

@router.post("/", response_model=TimelineItemResponse)
async def create_timeline_item(
    text: Optional[str] = Form(None),
    type: ItemType = Form(...),
    file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    storage: StorageService = Depends(get_storage_service)
):
    image_url = None

    if type in [ItemType.IMAGE, ItemType.REPORT]:
        if not file:
             raise HTTPException(status_code=400, detail="File is required for this item type")

        # Generate a unique filename
        # Safer extension extraction
        _, ext = os.path.splitext(file.filename or "")
        if not ext:
            ext = ".jpg" # Default if unknown? Or maybe error out.
                         # But let's keep it simple.

        filename = f"{uuid.uuid4()}{ext}"

        await storage.upload(file, filename)
        image_url = storage.get_url(filename)

    item = TimelineItem(
        type=type,
        text=text,
        image_url=image_url,
        created_at=datetime.now(timezone.utc)
    )

    session.add(item)
    session.commit()
    session.refresh(item)
    return item
