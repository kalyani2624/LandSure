from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ValidationResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    rule_name: str
    severity: str
    description: str
    is_resolved: bool
    created_at: datetime
