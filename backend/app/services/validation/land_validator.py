import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.land_records import LandRecord

def validate_record(db: Session, record_data: Dict[str, Any], document_id: int) -> List[Dict[str, Any]]:
    """
    Validates a post-normalized land record against statutory revenue rules & database cross-checks.
    Distinguishes clearly between:
    - Missing Field
    - Format Error
    - Low Confidence
    - Area Mismatch
    - Owner Conflict
    - Duplicate
    """
    anomalies: List[Dict[str, Any]] = []

    # 1. Missing Required Fields Check
    required_fields = [
        ("owner_name", "Owner Name"),
        ("survey_number", "Survey Number"),
        ("area", "Area/Extent"),
        ("village", "Village"),
        ("tehsil_mandal", "Tehsil/Mandal"),
        ("district", "District")
    ]

    for field_key, field_label in required_fields:
        if field_key == "tehsil_mandal":
            val = record_data.get("tehsil_mandal") or record_data.get("mandal") or record_data.get("tehsil")
        else:
            val = record_data.get(field_key)
            
        if val is None or (isinstance(val, str) and not val.strip()):
            anomalies.append({
                "document_id": document_id,
                "rule_name": "Missing Field",
                "severity": "Warning",
                "description": f"Required field '{field_label}' was not detected in the uploaded document. Routed to review queue for officer verification."
            })

    # 2. Format Validations on Normalized Data
    area_val = record_data.get("area")
    if area_val is not None:
        try:
            float_area = float(area_val)
            if float_area <= 0:
                anomalies.append({
                    "document_id": document_id,
                    "rule_name": "Format Error",
                    "severity": "Error",
                    "description": f"Area measurement must be a positive number. Received: {area_val}"
                })
        except (ValueError, TypeError):
            anomalies.append({
                "document_id": document_id,
                "rule_name": "Format Error",
                "severity": "Error",
                "description": f"Invalid numeric area value: {area_val}"
            })

    reg_date = record_data.get("registration_date")
    if reg_date:
        # Check standard ISO format YYYY-MM-DD or standard DD/MM/YYYY
        is_valid_date = bool(re.match(r'^\d{4}-\d{2}-\d{2}$', str(reg_date)) or re.match(r'^\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4}$', str(reg_date)))
        if not is_valid_date:
            anomalies.append({
                "document_id": document_id,
                "rule_name": "Format Error",
                "severity": "Warning",
                "description": f"Date value '{reg_date}' could not be parsed into a standard calendar date."
            })

    # 3. Cross-Check with Database for Existing Verified Records
    survey_no = record_data.get("survey_number")
    village_name = record_data.get("village")

    if survey_no and village_name:
        existing_records = db.query(LandRecord).filter(
            LandRecord.survey_number == str(survey_no),
            LandRecord.village.ilike(f"%{village_name}%"),
            LandRecord.verification_status == "Verified"
        ).all()

        for rec in existing_records:
            # Check Owner Conflict
            extracted_owner = record_data.get("owner_name")
            if extracted_owner and rec.owner_name:
                ext_owner_clean = extracted_owner.lower().strip()
                db_owner_clean = rec.owner_name.lower().strip()
                if ext_owner_clean != db_owner_clean and record_data.get("doc_type") != "Mutation Order":
                    anomalies.append({
                        "document_id": document_id,
                        "rule_name": "Owner Conflict",
                        "severity": "Critical",
                        "description": f"Survey No. {survey_no} in village {village_name} is already verified under owner '{rec.owner_name}', but uploaded record lists '{extracted_owner}'."
                    })

            # Check Area Mismatch
            if area_val is not None and rec.area is not None:
                try:
                    ext_a = float(area_val)
                    db_a = float(rec.area)
                    if abs(ext_a - db_a) > 0.05:
                        anomalies.append({
                            "document_id": document_id,
                            "rule_name": "Area Mismatch",
                            "severity": "Warning",
                            "description": f"Area discrepancy detected for Survey No. {survey_no}: Uploaded document lists {ext_a} {record_data.get('area_unit', 'Acres')}, while verified registry lists {db_a} {rec.area_unit}."
                        })
                except (ValueError, TypeError):
                    pass

            # Check Potential Exact Duplicate
            if extracted_owner and rec.owner_name and (extracted_owner.lower().strip() == rec.owner_name.lower().strip()):
                anomalies.append({
                    "document_id": document_id,
                    "rule_name": "Duplicate",
                    "severity": "Warning",
                    "description": f"A verified land record with identical owner '{rec.owner_name}' and Survey No. {survey_no} already exists (Record #{rec.id})."
                })

    return anomalies
