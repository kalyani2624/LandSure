import logging
from typing import Dict, Any, List, Optional
import numpy as np
from PIL import Image
from app.services.ocr.base_ocr import BaseOCREngine

logger = logging.getLogger(__name__)

class RapidOCREngine(BaseOCREngine):
    """
    High-accuracy local Deep Learning OCR Engine powered by ONNX neural models.
    Supports text detection, angle classification, and recognition across all platforms
    without requiring external system binaries.
    """
    def __init__(self):
        try:
            from rapidocr_onnxruntime import RapidOCR
            self.engine = RapidOCR()
            self.available = True
        except Exception as e:
            logger.warning(f"RapidOCR engine initialization warning: {e}")
            self.engine = None
            self.available = False

    def extract_text(self, image_path: str, language: Optional[str] = 'English') -> Dict[str, Any]:
        if not self.available or self.engine is None:
            return {
                "text": "",
                "confidence": 0.0,
                "engine": "rapidocr",
                "lines": []
            }

        try:
            result, elapse = self.engine(image_path)
            if not result:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "engine": "rapidocr",
                    "lines": []
                }

            lines = []
            all_texts = []
            confidences = []

            for box, text, score in result:
                clean_text = text.strip()
                if clean_text:
                    all_texts.append(clean_text)
                    conf_pct = round(float(score) * 100.0, 2)
                    confidences.append(conf_pct)
                    
                    # Convert 4-point polygon [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] to [x, y, w, h]
                    xs = [pt[0] for pt in box]
                    ys = [pt[1] for pt in box]
                    min_x, max_x = min(xs), max(xs)
                    min_y, max_y = min(ys), max(ys)
                    bbox = [int(min_x), int(min_y), int(max_x - min_x), int(max_y - min_y)]

                    lines.append({
                        "line_text": clean_text,
                        "bbox": bbox,
                        "confidence": conf_pct,
                        "words": [{
                            "text": clean_text,
                            "bbox": bbox,
                            "confidence": conf_pct
                        }]
                    })

            full_text = "\n".join(all_texts)
            avg_conf = round(float(np.mean(confidences)), 2) if confidences else 85.0

            return {
                "text": full_text,
                "confidence": avg_conf,
                "engine": "rapidocr",
                "lines": lines
            }
        except Exception as e:
            logger.error(f"RapidOCR extraction error on {image_path}: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "engine": "rapidocr",
                "lines": []
            }
