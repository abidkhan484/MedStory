
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timezone

from app.database import get_session
from app.models import (
    User, RelativeConnection, AuditAction
)
from app.deps import get_current_user
from app.services.audit import create_audit_log
from pydantic import BaseModel, EmailStr

router = APIRouter()

class InviteRelativeRequest(BaseModel):
    email: EmailStr
    relationship_type: str # e.g. "Daughter"

class RelativeResponse(BaseModel):
    id: int
    relative: User
    status: str
    relationship_type: str

@router.post("/invite")
async def invite_relative(
    invite_in: InviteRelativeRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Invite a registered user to become a relative (connection).
    """
    # Check if user exists
    relative_user = session.exec(select(User).where(User.email == invite_in.email)).first()
    if not relative_user:
        raise HTTPException(status_code=404, detail="User not found. They must register first.")

    if relative_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot invite yourself")

    # Check existing connection
    existing = session.exec(
        select(RelativeConnection)
        .where(RelativeConnection.user_id == current_user.id)
        .where(RelativeConnection.relative_id == relative_user.id)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail=f"Connection already exists (Status: {existing.status})")

    connection = RelativeConnection(
        user_id=current_user.id,
        relative_id=relative_user.id,
        relationship_type=invite_in.relationship_type,
        status="pending"
    )
    session.add(connection)
    session.commit()

    create_audit_log(
        session,
        AuditAction.RELATIVE_CONNECTED,
        user_id=current_user.id,
        resource_id=connection.id,
        resource_type="RelativeConnection"
    )

    return {"message": "Invitation sent"}

@router.get("/", response_model=List[RelativeConnection])
async def list_relatives(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List all relative connections for the current user.
    """
    connections = session.exec(
        select(RelativeConnection)
        .where(RelativeConnection.user_id == current_user.id)
    ).all()
    return connections

@router.post("/{connection_id}/accept")
async def accept_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Accept an incoming relative invitation.
    """
    # Note: Logic here is tricky.
    # Usually the Recipient (Relative) accepts the invitation from the Sender (User).
    # But my model `RelativeConnection` is directional `user_id` -> `relative_id`.
    # So if User A invites User B. A connection is created: user_id=A, relative_id=B, status=pending.
    # User B should accept it.

    connection = session.exec(
        select(RelativeConnection)
        .where(RelativeConnection.id == connection_id)
        .where(RelativeConnection.relative_id == current_user.id)
    ).first()

    if not connection:
        raise HTTPException(status_code=404, detail="Invitation not found")

    if connection.status != "pending":
         raise HTTPException(status_code=400, detail="Invitation already processed")

    connection.status = "accepted"
    session.add(connection)
    session.commit()

    return {"message": "Invitation accepted"}
