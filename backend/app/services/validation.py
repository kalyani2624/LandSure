from sqlalchemy.orm import Session
from app.models.land_records import LandRecord
from app.models.validation import ValidationResult
import re

def validate_record(db: Session, record_data: dict, document_id: int) -> list:
    """
    Validates a land record against rules and existing database records.
    Returns a list of dictionaries, each representing a ValidationResult to be saved.
    """
    anomalies = []
    
    owner_name = record_data.get("owner_name")
    survey_number = record_data.get("survey_number")
    area = record_data.get("area")
    area_unit = record_data.get("area_unit", "Acres")
    village = record_data.get("village")
    tehsil_mandal = record_data.get("tehsil_mandal")
    district = record_data.get("district")
    reg_date = record_data.get("registration_date")
    khata_number = record_data.get("khata_number")
    doc_type = record_data.get("doc_type", "Other")

    # 1. Format and Missing Field Checks
    required_fields = {
        "owner_name": "Owner Name",
        "survey_number": "Survey Number",
        "area": "Area/Extent",
        "village": "Village",
        "tehsil_mandal": "Tehsil/Mandal",
        "district": "District"
    }

    for field, label in required_fields.items():
        if not record_data.get(field):
            # For Mutation Records, owner_name might be split or represent transfer, handle gracefully
            if doc_type == "Mutation Record" and field == "owner_name":
                continue
            anomalies.append({
                "rule_name": "Missing Field",
                "severity": "Warning",
                "description": f"Required field '{label}' is missing from the record."
            })

    # Validate Area format
    if area is not None:
        try:
            val = float(area)
            if val <= 0:
                anomalies.append({
                    "rule_name": "Format Error",
                    "severity": "Error",
                    "description": f"Invalid Area value ({area}). Area must be a positive number."
                })
        except ValueError:
            anomalies.append({
                "rule_name": "Format Error",
                "severity": "Error",
                "description": f"Invalid Area format ({area}). Must be a decimal number."
            })

    # Validate Registration Date format (DD-MM-YYYY or YYYY-MM-DD)
    if reg_date:
        date_pattern = r'^\d{2}-\d{2}-\d{4}$'
        if not re.match(date_pattern, str(reg_date)):
            anomalies.append({
                "rule_name": "Format Error",
                "severity": "Warning",
                "description": f"Date '{reg_date}' does not match standard DD-MM-YYYY format."
            })

    # 2. Cross-Document / Database Check (for duplicate, area mismatch, owner conflict)
    # We only match against verified records (or records that are not this current record's document)
    if survey_number and village and tehsil_mandal:
        # Search for existing records of the same land plot (Survey + Village + Mandal)
        query = db.query(LandRecord).filter(
            LandRecord.survey_number == survey_number,
            LandRecord.village == village,
            LandRecord.tehsil_mandal == tehsil_mandal,
            LandRecord.verification_status == "Verified"
        )
        
        # If this is an edit verification, don't compare against itself
        if document_id:
            query = query.filter(LandRecord.document_id != document_id)
            
        existing_records = query.all()
        
        for existing in existing_records:
            # Duplicate check
            # Same Owner, Same Area, Same Khata
            if (owner_name == existing.owner_name and 
                abs((area or 0.0) - (existing.area or 0.0)) < 0.01 and 
                khata_number == existing.khata_number):
                anomalies.append({
                    "rule_name": "Duplicate",
                    "severity": "Warning",
                    "description": f"Possible duplicate: An identical verified record already exists in database (Record ID: {existing.id})."
                })
                continue # Skip other checks if it's a duplicate

            # Area Mismatch check
            if area is not None and existing.area is not None:
                if abs(float(area) - float(existing.area)) >= 0.01:
                    anomalies.append({
                        "rule_name": "Area Mismatch",
                        "severity": "Error",
                        "description": f"Area mismatch detected: This document lists {area} {area_unit}, but existing record (ID: {existing.id}) lists {existing.area} {existing.area_unit} for Survey {survey_number}."
                    })

            # Owner Conflict / Unrecorded Mutation check
            # If names differ and this is not explicitly a Mutation Record that justifies the change
            if owner_name and existing.owner_name:
                if owner_name.lower().strip() != existing.owner_name.lower().strip():
                    if doc_type != "Mutation Record":
                        anomalies.append({
                            "rule_name": "Owner Conflict",
                            "severity": "Error",
                            "description": f"Ownership conflict: Document names owner as '{owner_name}', but database lists '{existing.owner_name}' for Survey {survey_number}. A mutation record may be required."
                        })
                    else:
                        # For a mutation record, an owner difference is expected, so we can log it as an audit note rather than a blocking error
                        pass

    # Save to db
    validation_objects = []
    for anomaly in anomalies:
        validation_objects.append(ValidationResult(
            document_id=document_id,
            rule_name=anomaly["rule_name"],
            severity=anomaly["severity"],
            description=anomaly["description"],
            is_resolved=False
        ))
        
    return validation_objects
