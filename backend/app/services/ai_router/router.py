import logging
from typing import Dict, Any, List, Optional
from app.services.handwriting.format_classifier import classify_document_format
from app.services.language_detection.script_detector import detect_language
from app.services.ocr.rapidocr_engine import RapidOCREngine
from app.services.ocr.tesseract_engine import TesseractOCREngine

logger = logging.getLogger(__name__)

class AIModelRouter:
    """
    Intelligent perception router that selects the optimal OCR/HTR/VLM processing
    strategy based on content format classification and script detection.
    """

    def __init__(self):
        self.rapid_ocr = RapidOCREngine()
        self.tesseract_ocr = TesseractOCREngine()

    def route_and_process(
        self,
        image_path: str,
        hint_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes routing workflow:
        1. Fast preliminary scan for format assessment (PRINTED, HANDWRITTEN, MIXED, UNKNOWN).
        2. Routes to appropriate perception engine(s).
        3. Returns unified contract retaining full spatial bounding boxes and token confidences.
        """
        # Step 1: Preliminary OCR pass with RapidOCR to obtain text & confidence distribution
        prelim_ocr = self.rapid_ocr.extract_text(image_path, language=hint_language or "English")
        lines = prelim_ocr.get("lines", [])
        raw_text = prelim_ocr.get("text", "")

        # Step 2: Content-Based Format Classification (ZERO filename dependency)
        format_assessment = classify_document_format(image_path, ocr_lines=lines)
        format_type = format_assessment.get("format_type", "UNKNOWN")
        format_conf = format_assessment.get("confidence", 0.0)
        needs_review = format_assessment.get("needs_human_review", False)

        # Step 3: Script & Language Identification from recognized tokens
        detected_lang = detect_language(raw_text)

        # Step 4: Routing Execution
        unified_lines: List[Dict[str, Any]] = list(lines)
        unified_tokens: List[Dict[str, Any]] = []
        for l in unified_lines:
            for w in l.get("words", []):
                unified_tokens.append(w)

        chosen_engine = "RapidOCR-Neural"
        overall_conf = float(prelim_ocr.get("confidence", 85.0))

        if format_type == "PRINTED":
            # Standard high-speed neural OCR pipeline
            chosen_engine = "RapidOCR-ONNX-Printed"

        elif format_type == "HANDWRITTEN":
            # Real HTR model is not yet installed locally; route strictly to Human Review
            chosen_engine = "HTR_UNAVAILABLE_REVIEW_REQUIRED"
            needs_review = True

        elif format_type == "MIXED":
            # Dual-pass hybrid: OCR for printed headers + Human Review for handwritten fills
            chosen_engine = "Hybrid-PrintedOCR_HandwrittenReview"
            needs_review = True

        else: # UNKNOWN
            chosen_engine = "UNKNOWN_FORMAT_REVIEW_REQUIRED"
            needs_review = True

        # Extract overall document bounding box
        doc_bbox = [0, 0, 0, 0]
        if unified_lines:
            all_x = [l.get("bbox", [0, 0, 0, 0])[0] for l in unified_lines]
            all_y = [l.get("bbox", [0, 0, 0, 0])[1] for l in unified_lines]
            all_r = [l.get("bbox", [0, 0, 0, 0])[0] + l.get("bbox", [0, 0, 0, 0])[2] for l in unified_lines]
            all_b = [l.get("bbox", [0, 0, 0, 0])[1] + l.get("bbox", [0, 0, 0, 0])[3] for l in unified_lines]
            doc_bbox = [min(all_x), min(all_y), max(all_r) - min(all_x), max(all_b) - min(all_y)]

        return {
            "text": raw_text,
            "language": detected_lang,
            "script": detected_lang,
            "lines": unified_lines,
            "tokens": unified_tokens,
            "bbox": doc_bbox,
            "confidence": round(overall_conf, 1),
            "engine": chosen_engine,
            "format_type": format_type,
            "format_confidence": format_conf,
            "needs_human_review": needs_review,
            "routing_metadata": {
                "format_method": format_assessment.get("method"),
                "total_lines": len(unified_lines),
                "total_tokens": len(unified_tokens)
            }
        }
