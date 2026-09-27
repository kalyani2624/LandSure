import re
from typing import Dict, Any, Tuple, Optional
from app.services.extraction.multilingual_extractor import MultilingualFieldExtractor
from app.services.normalization.area_normalizer import normalize_area

_extractor = MultilingualFieldExtractor()

def extract_area_value(text: str) -> Tuple[Optional[float], Optional[str]]:
    norm = normalize_area(None, source_text=text)
    if norm:
        return norm["value"], norm["unit"]
    return None, None

def clean_extracted_value(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    cleaned = str(val).strip()
    cleaned = re.sub(r'^[:;\-\|=\.\s]+', '', cleaned).strip()
    cleaned = re.sub(r'[:;\-\|=\.\s]+$', '', cleaned).strip()
    return cleaned if len(cleaned) > 0 else None

def extract_fields(ocr_text: str, doc_confidence: float = 85.0) -> Tuple[Dict[str, Any], Dict[str, float]]:
    raw_ocr_data = {"text": ocr_text, "lines": []}
    structured_fields, staging_record = _extractor.extract_all(raw_ocr_data, doc_confidence)
    confidences = {k: v["confidence"] for k, v in structured_fields.items()}
    return staging_record, confidences

def extract_structured_fields(raw_ocr_data: Dict[str, Any], doc_confidence: float = 85.0) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    return _extractor.extract_all(raw_ocr_data, doc_confidence)
