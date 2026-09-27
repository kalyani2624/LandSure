import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    preprocessed_path = Column(String, nullable=True)
    doc_type = Column(String, default="Other")  # Survey Record, Mutation Record, Registration Record, Pattadar/Land Ownership Record, Cadastral Map, Other
    language = Column(String, default="English")  # English, Telugu, Hindi
    format_type = Column(String, default="Printed")  # Printed, Handwritten, Mixed
    status = Column(String, default="Processing")  # Processing, Pending Review, Low Confidence, Verified, Error, Area Mismatch, Owner Conflict, Duplicate
    confidence_score = Column(Float, default=0.0)  # Overall confidence score (0 to 100)
    processing_stage = Column(String, default="UPLOADED")  # UPLOADED, PREPROCESSING, CLASSIFYING, OCR_PROCESSING, EXTRACTING, VALIDATING, COMPLETED, NEEDS_REVIEW, FAILED
    ocr_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
