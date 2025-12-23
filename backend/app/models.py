
from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship, Column, JSON
from enum import Enum

# --- Enums ---

class ItemType(str, Enum):
    STATUS = "status"
    IMAGE = "image"
    REPORT = "report"

class AccessType(str, Enum):
    AUTHENTICATED = "authenticated"
    ONE_TIME_PUBLIC = "one_time_public"

class AuditAction(str, Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    ACCESS_LINK_CREATED = "access_link_created"
    ACCESS_LINK_REVOKED = "access_link_revoked"
    TIMELINE_ACCESSED = "timeline_accessed"
    RELATIVE_CONNECTED = "relative_connected"
    RELATIVE_REMOVED = "relative_removed"
    REGISTER = "register"
    VERIFY_EMAIL = "verify_email"

# --- User & Auth Models ---

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: Optional[str] = None  # Nullable for OAuth users
    full_name: str = Field(max_length=100)

    # Verification & Status
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)

    # MFA
    mfa_enabled: bool = Field(default=False)
    mfa_secret: Optional[str] = None

    # OAuth
    oauth_provider: Optional[str] = None  # 'google'
    oauth_id: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = None

    # Relationships
    timeline_items: List["TimelineItem"] = Relationship(back_populates="user")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
    audit_logs: List["AuditLog"] = Relationship(back_populates="user")
    # Relative relationships are more complex (self-referential), defined below if needed or handled via query

class RefreshToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token: str = Field(unique=True, index=True)
    expires_at: datetime
    is_revoked: bool = Field(default=False)
    device_info: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User = Relationship(back_populates="refresh_tokens")

class OTPVerification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    otp_code: str
    purpose: str # "email_verification", "password_reset"
    expires_at: datetime
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Timeline ---

class TimelineItemBase(SQLModel):
    type: ItemType
    text: Optional[str] = None
    image_url: Optional[str] = None

class TimelineItem(TimelineItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User = Relationship(back_populates="timeline_items")

class TimelineItemCreate(TimelineItemBase):
    pass

class TimelineItemResponse(TimelineItemBase):
    id: int
    user_id: int
    created_at: datetime

# --- Sharing & Relatives ---

class AccessLink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", index=True)  # Timeline owner
    created_by_id: int = Field(foreign_key="user.id")  # Creator (owner or relative)
    token: str = Field(unique=True, index=True)

    access_type: AccessType
    max_uses: Optional[int] = None
    use_count: int = Field(default=0)
    expires_at: Optional[datetime] = None
    is_revoked: bool = Field(default=False)

    label: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed_at: Optional[datetime] = None

class RelativeConnection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True) # Timeline owner
    relative_id: int = Field(foreign_key="user.id", index=True) # Connected relative
    relationship_type: Optional[str] = None # e.g. "Daughter", "Doctor"
    status: str = Field(default="pending") # pending/accepted/rejected
    can_create_links: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Audit ---

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(foreign_key="user.id", default=None)
    action: AuditAction
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata_json: Optional[str] = None # Storing JSON as string for SQLite compatibility
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional[User] = Relationship(back_populates="audit_logs")
