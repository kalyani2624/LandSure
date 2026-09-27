from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, Any
from app.schemas.land_records import LandRecordResponse
from app.schemas.validation import ValidationResultResponse

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    file_path: str
    preprocessed_path: Optional[str] = None
    doc_type: str
    language: str
    format_type: str
    status: str
    confidence_score: float
    processing_stage: Optional[str] = "UPLOADED"
    ocr_text: Optional[str] = None
    created_at: datetime

class DocumentUpdate(BaseModel):
    doc_type: Optional[str] = None
    language: Optional[str] = None
    format_type: Optional[str] = None
    status: Optional[str] = None
    confidence_score: Optional[float] = None

class DocumentDetailResponse(BaseModel):
    document: DocumentResponse
    land_record: Optional[LandRecordResponse] = None
    validation_results: List[ValidationResultResponse] = []
    has_govt_database_match: bool = False
    matched_registry_id: Optional[int] = None
    matched_registry_details: Optional[dict] = None
