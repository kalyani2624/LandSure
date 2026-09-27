import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from app.database import Base

class LandRecord(Base):
    __tablename__ = "land_records"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
    
    # Core Land Record Fields
    owner_name = Column(String, nullable=True)
    father_name = Column(String, nullable=True)
    survey_number = Column(String, nullable=True)
    khasra_number = Column(String, nullable=True)
    khata_number = Column(String, nullable=True)
    plot_number = Column(String, nullable=True)
    area = Column(Float, nullable=True)
    area_unit = Column(String, default="Acres") # Acres, Guntas, Hectares, Sq Yards
    
    # Location Hierarchy
    village = Column(String, nullable=True)
    tehsil_mandal = Column(String, nullable=True)
    district = Column(String, nullable=True)
    
    # Classifications & Types
    land_classification = Column(String, nullable=True) # Dry, Wet, Agricultural, Forest, Govt
    ownership_type = Column(String, nullable=True) # Pattadar, Tenant, Leasehold, Joint
    
    # Mutation & Registration info
    mutation_number = Column(String, nullable=True)
    mutation_order_date = Column(String, nullable=True)
    entry_date = Column(String, nullable=True)
    registration_number = Column(String, nullable=True)
    registration_date = Column(String, nullable=True)
    
    # Metadata for verification & trust
    confidence_scores = Column(JSON, nullable=True)  # Dict mapping field_name to score (0-100)
    verification_status = Column(String, default="Pending")  # Pending, Verified, Rejected
    regional_values = Column(JSON, nullable=True)  # Dict storing original script attributes for bilingual support
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
