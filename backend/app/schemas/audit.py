from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AuditLogResponse(BaseModel):
    id: int
    land_record_id: int
    changed_by_user_id: Optional[int] = None
    changed_by_username: Optional[str] = None # Added for easier UI display
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
        
class AuditLogCreate(BaseModel):
    land_record_id: int
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
