from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from typing import Dict, Any, Optional

def log_verification_action(
    db: Session,
    land_record_id: int,
    officer_id: int,
    action: str,
    previous_data: Optional[Dict[str, Any]] = None,
    new_data: Optional[Dict[str, Any]] = None,
    notes: Optional[str] = None
) -> AuditLog:
    """
    Creates an immutable audit log entry for human verification decisions.
    """
    audit = AuditLog(
        land_record_id=land_record_id,
        officer_id=officer_id,
        action=action,
        previous_data=previous_data,
        new_data=new_data,
        notes=notes
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit
