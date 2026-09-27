import logging
from typing import Dict, Any
from app.services.ocr.base_ocr import BaseOCREngine
from app.services.ocr.rapidocr_engine import RapidOCREngine
from app.services.ocr.tesseract_engine import TesseractOCREngine, LANGUAGE_CODE_MAP
from app.services.ocr.online_ocr_engine import OnlineOCREngine

logger = logging.getLogger(__name__)

rapid_engine = RapidOCREngine()
online_engine = OnlineOCREngine()
tesseract_engine = TesseractOCREngine()

def run_online_ocr(file_path: str, language: str = "English") -> str:
    res = online_engine.extract_text(file_path, language)
    return res.get("text", "")

def run_ocr(file_path: str, language: str = "English") -> Dict[str, Any]:
    """
    Standard Robust Multi-Engine OCR entry point:
    1. Primary: RapidOCR local deep-learning ONNX neural model (fast, multi-script, offline).
    2. Fallback: Online OCR.space Engine 2.
    3. Fallback: Tesseract OCR (with multilingual models).
    """
    # 1. Try RapidOCR
    res = rapid_engine.extract_text(file_path, language)
    if res.get("text") and len(res["text"].strip()) >= 10:
        return res

    # 2. Try Online OCR if RapidOCR did not catch sufficient text
    try:
        online_res = online_engine.extract_text(file_path, language)
        if online_res.get("text") and len(online_res["text"].strip()) >= 10:
            return online_res
    except Exception as e:
        logger.warning(f"Online OCR API error: {e}")

    # 3. Try Tesseract
    try:
        tess_res = tesseract_engine.extract_text(file_path, language)
        if tess_res.get("text") and len(tess_res["text"].strip()) >= 5:
            return tess_res
    except Exception as e:
        logger.warning(f"Tesseract OCR error: {e}")

    return res

__all__ = [
    "BaseOCREngine",
    "RapidOCREngine",
    "TesseractOCREngine",
    "OnlineOCREngine",
    "LANGUAGE_CODE_MAP",
    "run_ocr",
    "run_online_ocr"
]
