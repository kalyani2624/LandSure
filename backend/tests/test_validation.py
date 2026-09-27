import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.users import User
from app.models.documents import Document
from app.models.land_records import LandRecord
from app.models.validation import ValidationResult
from app.models.audit import AuditLog
from app.services.validation import validate_record

# Set up in-memory database for testing
@pytest.fixture(name="db_session")
def fixture_db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_missing_fields_validation(db_session):
    """Test that missing required fields are correctly flagged."""
    record_data = {
        "owner_name": "", # Missing owner
        "survey_number": "145/3A",
        "area": 2.50,
        "village": "Krishnapuram",
        "tehsil_mandal": "Pedapadu",
        "district": "West Godavari"
    }
    
    anomalies = validate_record(db_session, record_data, document_id=1)
    
    assert len(anomalies) > 0
    missing_fields_anomalies = [a for a in anomalies if a["rule_name"] == "Missing Field"]
    assert len(missing_fields_anomalies) == 1
    assert "Owner Name" in missing_fields_anomalies[0]["description"]

def test_invalid_area_format_validation(db_session):
    """Test that negative or invalid area values trigger format errors."""
    record_data = {
        "owner_name": "Kondru Ramu",
        "survey_number": "145/3A",
        "area": -1.5, # Invalid negative area
        "village": "Krishnapuram",
        "tehsil_mandal": "Pedapadu",
        "district": "West Godavari"
    }
    
    anomalies = validate_record(db_session, record_data, document_id=1)
    format_errors = [a for a in anomalies if a["rule_name"] == "Format Error"]
    assert len(format_errors) == 1
    assert "positive" in format_errors[0]["description"]

def test_area_mismatch_cross_check(db_session):
    """Test that a discrepancy in area measurements against a verified record triggers an Area Mismatch anomaly."""
    # Seed a verified record
    verified_record = LandRecord(
        document_id=2,
        owner_name="Kondru Ramu",
        survey_number="100/1",
        village="Kona",
        tehsil_mandal="Mandal1",
        district="Dist1",
        area=5.0, # 5 Acres verified
        verification_status="Verified"
    )
    db_session.add(verified_record)
    db_session.commit()
    
    # New staged record with a different area
    record_data = {
        "owner_name": "Kondru Ramu",
        "survey_number": "100/1",
        "area": 5.8, # Different area!
        "village": "Kona",
        "tehsil_mandal": "Mandal1",
        "district": "Dist1"
    }
    
    anomalies = validate_record(db_session, record_data, document_id=3)
    area_mismatches = [a for a in anomalies if a["rule_name"] == "Area Mismatch"]
    assert len(area_mismatches) == 1
    assert "discrepancy" in area_mismatches[0]["description"].lower()

def test_owner_conflict_cross_check(db_session):
    """Test that a mismatch in owner name triggers an Owner Conflict warning."""
    # Seed verified record
    verified_record = LandRecord(
        document_id=5,
        owner_name="Kondru Ramu", # Registered Owner
        survey_number="200/B",
        village="Kona",
        tehsil_mandal="Mandal1",
        district="Dist1",
        area=1.0,
        verification_status="Verified"
    )
    db_session.add(verified_record)
    db_session.commit()
    
    # New staged record listing a different owner for the same land survey
    record_data = {
        "owner_name": "Suresh Kumar", # Different Owner!
        "survey_number": "200/B",
        "area": 1.0,
        "village": "Kona",
        "tehsil_mandal": "Mandal1",
        "district": "Dist1",
        "doc_type": "Pattadar Record"
    }
    
    anomalies = validate_record(db_session, record_data, document_id=6)
    owner_conflicts = [a for a in anomalies if a["rule_name"] == "Owner Conflict"]
    assert len(owner_conflicts) == 1
    assert "Suresh Kumar" in owner_conflicts[0]["description"]
