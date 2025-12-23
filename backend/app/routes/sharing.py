
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import secrets

from app.database import get_session
from app.models import (
    AccessLink, AccessType, User, RelativeConnection, AuditAction
)
from app.deps import get_current_user
from app.services.audit import create_audit_log
from pydantic import BaseModel

router = APIRouter()

class AccessLinkCreate(BaseModel):
    access_type: AccessType
    label: Optional[str] = None
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = None

class AccessLinkResponse(BaseModel):
    id: int
    token: str
    access_type: AccessType
    label: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_revoked: bool
    created_at: datetime
    use_count: int

@router.post("/", response_model=AccessLinkResponse)
async def create_access_link(
    link_in: AccessLinkCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Only owner can create links for now (or relatives with permission in future)
    # Generate secure token
    token = secrets.token_urlsafe(32)

    link = AccessLink(
        owner_id=current_user.id,
        created_by_id=current_user.id,
        token=token,
        access_type=link_in.access_type,
        label=link_in.label,
        expires_at=link_in.expires_at,
        max_uses=link_in.max_uses if link_in.access_type == AccessType.ONE_TIME_PUBLIC else None
    )

    # Defaults for one-time public
    if link.access_type == AccessType.ONE_TIME_PUBLIC:
        if not link.max_uses:
            link.max_uses = 1
        if not link.expires_at:
             # Default 24h for public links
            link.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    session.add(link)
    session.commit()
    session.refresh(link)

    create_audit_log(
        session,
        AuditAction.ACCESS_LINK_CREATED,
        user_id=current_user.id,
        resource_id=link.id,
        resource_type="AccessLink"
    )

    return link

@router.get("/", response_model=List[AccessLinkResponse])
async def list_my_links(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    links = session.exec(
        select(AccessLink)
        .where(AccessLink.owner_id == current_user.id)
        .where(AccessLink.is_revoked == False)
    ).all()
    return links

@router.delete("/{link_id}")
async def revoke_link(
    link_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    link = session.get(AccessLink, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    link.is_revoked = True
    session.add(link)
    session.commit()

    create_audit_log(
        session,
        AuditAction.ACCESS_LINK_REVOKED,
        user_id=current_user.id,
        resource_id=link.id,
        resource_type="AccessLink"
    )
    return {"message": "Link revoked"}

@router.get("/access/{token}")
async def access_timeline_via_link(
    token: str,
    session: Session = Depends(get_session)
):
    # This endpoint checks the token and returns basic info or data
    # For MVP, we'll return validity status.
    # Frontend will use this to determine if it should show the timeline or ask for login.

    link = session.exec(select(AccessLink).where(AccessLink.token == token)).first()

    if not link:
        raise HTTPException(status_code=404, detail="Invalid link")

    if link.is_revoked:
        raise HTTPException(status_code=410, detail="Link revoked")

    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Link expired")

    if link.max_uses and link.use_count >= link.max_uses:
        raise HTTPException(status_code=410, detail="Link used")

    # If Authenticated type, we just return "requires_auth" meta
    if link.access_type == AccessType.AUTHENTICATED:
        return {
            "valid": True,
            "type": "authenticated",
            "owner_id": link.owner_id,
            "requires_login": True
        }

    # If One-Time Public, we increment use count and return data (or token to fetch data)
    link.use_count += 1
    link.last_accessed_at = datetime.now(timezone.utc)
    session.add(link)

    create_audit_log(
        session,
        AuditAction.TIMELINE_ACCESSED,
        resource_id=link.id,
        resource_type="AccessLink",
        metadata={"token": token}
    )
    session.commit()

    return {
        "valid": True,
        "type": "one_time_public",
        "owner_id": link.owner_id,
        "requires_login": False
    }
