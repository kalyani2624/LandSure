from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user
from app.models.documents import Document
from app.models.land_records import LandRecord
from app.models.validation import ValidationResult
from app.models.audit import AuditLog
from app.schemas.land_records import LandRecordUpdate, LandRecordResponse
from app.schemas.audit import AuditLogResponse
from app.services.verification import log_verification_action

router = APIRouter(prefix="/verification", tags=["Human Verification Queue"])

@router.get("/list")
def get_verification_queue(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Returns all digitized revenue documents in the verification queue.
    Provides complete flattened attributes and nested objects for frontend compatibility.
    """
    docs = db.query(Document).order_by(Document.created_at.desc()).all()

    results = []
    for doc in docs:
        rec = db.query(LandRecord).filter(LandRecord.document_id == doc.id).first()
        validations = db.query(ValidationResult).filter(ValidationResult.document_id == doc.id).all()
        unresolved_anomalies = [v for v in validations if not v.is_resolved]

        results.append({
            "document_id": doc.id,
            "id": doc.id,
            "original_filename": doc.original_filename,
            "doc_type": doc.doc_type or "Land Record",
            "language": doc.language or "Telugu",
            "format_type": doc.format_type or "HANDWRITTEN",
            "status": doc.status or "Processing",
            "confidence_score": doc.confidence_score or 0.0,
            "processing_stage": doc.processing_stage or "COMPLETED",
            "created_at": doc.created_at.isoformat() if hasattr(doc.created_at, "isoformat") else str(doc.created_at),
            "anomalies_count": len(unresolved_anomalies),
            "land_record": {
                "id": rec.id if rec else None,
                "owner_name": rec.owner_name if rec else None,
                "father_name": getattr(rec, "father_name", None) if rec else None,
                "survey_number": rec.survey_number if rec else None,
                "khasra_number": rec.khasra_number if rec else None,
                "khata_number": rec.khata_number if rec else None,
                "area": rec.area if rec else None,
                "area_unit": rec.area_unit if rec else None,
                "village": rec.village if rec else None,
                "tehsil_mandal": rec.tehsil_mandal if rec else None,
                "district": rec.district if rec else None,
                "verification_status": rec.verification_status if rec else "Pending Review"
            } if rec else None,
            "document": doc,
            "record": rec,
            "validation_results": validations
        })
    return results

@router.put("/{document_id}/verify", response_model=LandRecordResponse)
def verify_or_edit_record(
    document_id: int,
    record_in: LandRecordUpdate,
    approved: bool = Query(True),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    rec = db.query(LandRecord).filter(LandRecord.document_id == document_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Land record not found for this document")

    previous_state = {
        "owner_name": rec.owner_name,
        "survey_number": rec.survey_number,
        "area": rec.area,
        "village": rec.village,
        "verification_status": rec.verification_status
    }

    # Update modified fields
    update_data = record_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(rec, key) and value is not None:
            setattr(rec, key, value)

    rec.verification_status = "Verified" if approved else "Rejected"
    doc.status = "Verified" if approved else "Rejected"
    doc.processing_stage = "COMPLETED"

    # Mark validation anomalies as resolved
    db.query(ValidationResult).filter(ValidationResult.document_id == document_id).update({"is_resolved": True})

    # Log audit entry
    log_verification_action(
        db=db,
        land_record_id=rec.id,
        officer_id=current_user.id,
        action="APPROVED" if approved else "REJECTED",
        previous_values=previous_state,
        new_values=update_data,
        comments=f"Reviewed and verified by officer @{current_user.username}"
    )

    db.commit()
    db.refresh(rec)
    return rec

@router.get("/{record_id}/audits", response_model=List[AuditLogResponse])
def get_audit_trail(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    return db.query(AuditLog).filter(AuditLog.land_record_id == record_id).order_by(AuditLog.timestamp.desc()).all()
