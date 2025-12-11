
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from enum import Enum

class ItemType(str, Enum):
    STATUS = "status"
    IMAGE = "image"
    REPORT = "report"

class TimelineItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: ItemType
    text: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # User relationship would go here
    # user_id: int = Field(foreign_key="user.id")

class TimelineItemCreate(SQLModel):
    type: ItemType
    text: Optional[str] = None

class TimelineItemResponse(TimelineItem):
    pass
