import os
from typing import Optional, Dict, Any
from app.services.preprocessing.image_enhancer import (
    enhance_document_image,
    detect_skew,
    rotate_image,
    denoise_photocopy,
    preprocess_image
)
from app.services.preprocessing.pdf_processor import (
    extract_pdf_pages_or_text,
    process_pdf_document
)

def clean_and_deskew_image(input_path: str, output_path: Optional[str] = None) -> str:
    """Convenience helper returning enhanced image path."""
    res = enhance_document_image(input_path, output_path)
    return res.get("output_path", input_path)

__all__ = [
    "enhance_document_image",
    "clean_and_deskew_image",
    "preprocess_image",
    "detect_skew",
    "rotate_image",
    "denoise_photocopy",
    "extract_pdf_pages_or_text",
    "process_pdf_document"
]
