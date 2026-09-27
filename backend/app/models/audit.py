import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    land_record_id = Column(Integer, ForeignKey("land_records.id", ondelete="CASCADE"), nullable=False)
    changed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    field_name = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
