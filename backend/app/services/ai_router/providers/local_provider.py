import logging
from typing import Dict, Any, Optional
from app.services.ai_router.providers.base_provider import BaseAIProvider
from app.services.ocr.rapidocr_engine import RapidOCREngine
from app.services.handwriting.format_classifier import classify_document_format
from app.services.language_detection.script_detector import detect_language
from app.services.document_classification.classifier import classify_document_type
from app.services.ai_router.vlm_understanding import VLMDocumentUnderstandingAdapter, CANONICAL_19_FIELDS, init_canonical_schema

logger = logging.getLogger(__name__)

class LocalAIProvider(BaseAIProvider):
    """
    100% Offline Edge Perception Provider.
    Powered by local RapidOCR ONNX models and spatial layout understanding.
    """

    def __init__(self):
        self.ocr_engine = RapidOCREngine()
        self.understanding_adapter = VLMDocumentUnderstandingAdapter()

    def analyze_document(
        self,
        image_path: str,
        ocr_context: Optional[Dict[str, Any]] = None,
        hint_language: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. OCR execution if not already provided
        ocr_result = ocr_context if ocr_context else self.ocr_engine.extract_text(image_path, language=hint_language or "English")
        lines = ocr_result.get("lines", [])
        raw_text = ocr_result.get("text", "")

        # 2. Content-based format classification (zero filename dependency)
        format_assessment = classify_document_format(image_path, ocr_lines=lines)
        format_type = format_assessment.get("format_type", "UNKNOWN")

        # 3. Script & document classification
        detected_lang = detect_language(raw_text)
        doc_class = classify_document_type(raw_text)
        doc_type = doc_class.get("doc_type", "Other")

        # 4. Canonical 19-field extraction
        understanding = self.understanding_adapter.process_document(
            image_path=image_path,
            ocr_result=ocr_result,
            language=detected_lang,
            doc_type=doc_type,
            format_type=format_type
        )

        return {
            "provider": "local_rapidocr",
            "provider_status": "SUCCESS",
            "format_type": format_type,
            "format_confidence": format_assessment.get("confidence", 0.0),
            "language": detected_lang,
            "script": detected_lang,
            "doc_type": doc_type,
            "ocr": ocr_result,
            "fields": understanding["fields"],
            "staging": understanding["staging"],
            "confidence": understanding["document_confidence"],
            "needs_human_review": format_assessment.get("needs_human_review", False) or (understanding["document_confidence"] < 75.0)
        }

    def extract_land_fields(
        self,
        image_path: str,
        ocr_context: Optional[Dict[str, Any]] = None,
        language: str = "English",
        doc_type: str = "Other"
    ) -> Dict[str, Any]:
        ocr_res = ocr_context if ocr_context else self.ocr_engine.extract_text(image_path, language=language)
        return self.understanding_adapter.process_document(
            image_path=image_path,
            ocr_result=ocr_res,
            language=language,
            doc_type=doc_type
        )

    def recognize_handwriting(
        self,
        image_path: str,
        ocr_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Offline local fallback: run OCR and flag for human review
        res = self.analyze_document(image_path, ocr_context=ocr_context)
        res["needs_human_review"] = True
        res["handwriting_note"] = "Local HTR offline fallback applied; manual verification recommended."
        return res
