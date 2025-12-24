
from sqlmodel import Session
from app.models import AuditLog, AuditAction
from datetime import datetime, timezone
import json

def create_audit_log(
    session: Session,
    action: AuditAction,
    user_id: int | None = None,
    resource_type: str | None = None,
    resource_id: int | None = None,
    metadata: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None
):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=json.dumps(metadata) if metadata else None,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.now(timezone.utc)
    )
    session.add(audit)
    session.commit()
