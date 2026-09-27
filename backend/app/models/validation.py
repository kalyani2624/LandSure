import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.database import Base

class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    rule_name = Column(String, nullable=False)  # Area Mismatch, Owner Conflict, Duplicate, Format Error, Missing Field
    severity = Column(String, default="Warning")  # Warning, Error
    description = Column(String, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
