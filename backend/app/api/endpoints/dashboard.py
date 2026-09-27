from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.dependencies import get_db, get_current_active_user
from app.models.documents import Document
from app.models.land_records import LandRecord
from app.models.validation import ValidationResult

router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    total_docs = db.query(Document).count()
    verified_records = db.query(LandRecord).filter(LandRecord.verification_status == "Verified").count()
    pending_review = db.query(Document).filter(
        (Document.status.in_(["Pending Review", "Low Confidence", "Owner Conflict", "Area Mismatch", "Duplicate", "Pending"])) |
        (Document.processing_stage == "NEEDS_REVIEW")
    ).count()
    active_anomalies = db.query(ValidationResult).filter(ValidationResult.is_resolved == False).count()

    total_area_result = db.query(func.sum(LandRecord.area)).filter(LandRecord.verification_status == "Verified").scalar()
    total_area_digitized = round(float(total_area_result or 0.0), 2)

    # Status distribution
    status_counts = db.query(Document.status, func.count(Document.id)).group_by(Document.status).all()
    status_dist = {s or "Pending Review": count for s, count in status_counts}
    for default_status in ["Verified", "Pending Review", "Low Confidence", "Owner Conflict", "Area Mismatch", "Duplicate"]:
        if default_status not in status_dist:
            status_dist[default_status] = 0

    # Document type distribution
    doc_types = db.query(Document.doc_type, func.count(Document.id)).group_by(Document.doc_type).all()
    doc_type_dist = {dtype or "Other": count for dtype, count in doc_types}

    # Language distribution
    languages = db.query(Document.language, func.count(Document.id)).group_by(Document.language).all()
    lang_dist = {lang or "Unknown": count for lang, count in languages}

    # Recent activity
    recent_docs = db.query(Document).order_by(Document.created_at.desc()).limit(6).all()
    recent_docs_list = []
    for d in recent_docs:
        score = float(d.confidence_score or 0.0)
        # Convert to 0-100 percentage
        score_pct = round(score * 100 if score <= 1.0 else score, 1)
        recent_docs_list.append({
            "id": d.id,
            "filename": d.original_filename,
            "original_filename": d.original_filename,
            "doc_type": d.doc_type,
            "language": d.language,
            "status": d.status or "Pending Review",
            "confidence_score": score_pct,
            "processing_stage": d.processing_stage,
            "created_at": d.created_at.isoformat() if d.created_at else None
        })

    recent_records = db.query(LandRecord).order_by(LandRecord.updated_at.desc()).limit(6).all()
    recent_records_list = [
        {
            "id": r.id,
            "document_id": r.document_id,
            "owner_name": r.owner_name,
            "survey_number": r.survey_number or r.khasra_number,
            "village": r.village,
            "district": r.district,
            "verification_status": r.verification_status,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in recent_records
    ]

    return {
        "kpis": {
            "total_documents": total_docs,
            "digitized_records": verified_records,
            "pending_review": pending_review,
            "detected_anomalies": active_anomalies,
            "total_area_acres": total_area_digitized
        },
        "status_distribution": status_dist,
        "recent_activity": recent_docs_list,
        "document_type_distribution": doc_type_dist,
        "language_distribution": lang_dist,
        "recent_records": recent_records_list
    }
