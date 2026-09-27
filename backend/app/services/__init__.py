from app.services.preprocessing import enhance_document_image, clean_and_deskew_image, extract_pdf_pages_or_text
from app.services.ocr import run_ocr, RapidOCREngine, TesseractOCREngine, OnlineOCREngine
from app.services.handwriting import assess_handwriting_and_quality
from app.services.language_detection import detect_language, detect_script
from app.services.document_classification import classify_document, classify_document_type
from app.services.layout_analysis import find_spatial_neighbors, parse_tabular_layout
from app.services.field_extraction import MultilingualFieldExtractor, clean_value_text
from app.services.normalization import normalize_date, normalize_area, CANONICAL_FIELD_ALIASES
from app.services.validation import validate_record
from app.services.confidence import calculate_document_confidence
from app.services.verification import evaluate_verification_routing, log_verification_action

# Backward compatibility alias
from app.services.field_extraction.multilingual_extractor import MultilingualFieldExtractor as RegexFieldExtractor
extract_fields = None
extract_area_value = None

__all__ = [
    "enhance_document_image",
    "clean_and_deskew_image",
    "extract_pdf_pages_or_text",
    "run_ocr",
    "RapidOCREngine",
    "TesseractOCREngine",
    "OnlineOCREngine",
    "assess_handwriting_and_quality",
    "detect_language",
    "detect_script",
    "classify_document",
    "classify_document_type",
    "find_spatial_neighbors",
    "parse_tabular_layout",
    "MultilingualFieldExtractor",
    "clean_value_text",
    "normalize_date",
    "normalize_area",
    "CANONICAL_FIELD_ALIASES",
    "validate_record",
    "calculate_document_confidence",
    "evaluate_verification_routing",
    "log_verification_action"
]
