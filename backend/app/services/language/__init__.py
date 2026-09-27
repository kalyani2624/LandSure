from app.services.language.detector import detect_language, classify_document, INDIC_SCRIPT_RANGES

classify_document_type = classify_document

__all__ = ["detect_language", "classify_document", "classify_document_type", "INDIC_SCRIPT_RANGES"]
