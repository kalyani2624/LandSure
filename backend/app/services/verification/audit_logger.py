import datetime
import json
import logging
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

logger = logging.getLogger(__name__)

def log_verification_action(
    db: Session,
    land_record_id: int,
    officer_id: int,
    action: str,
    previous_values: dict = None,
    new_values: dict = None,
    comments: str = ""
):
    """
    Creates immutable audit log entries for human verification decisions.
    """
    try:
        # Log action/status
        entry = AuditLog(
            land_record_id=land_record_id,
            changed_by_user_id=officer_id,
            field_name="verification_status",
            old_value=str(previous_values.get("verification_status") if previous_values else "Pending"),
            new_value=action,
            timestamp=datetime.datetime.utcnow()
        )
        db.add(entry)

        # Log any changed fields
        if previous_values and new_values:
            for k, new_v in new_values.items():
                old_v = previous_values.get(k)
                if str(old_v) != str(new_v):
                    db.add(AuditLog(
                        land_record_id=land_record_id,
                        changed_by_user_id=officer_id,
                        field_name=k,
                        old_value=str(old_v),
                        new_value=str(new_v),
                        timestamp=datetime.datetime.utcnow()
                    ))

        db.commit()
    except Exception as e:
        logger.error(f"Audit log writing failed for record #{land_record_id}: {e}")
