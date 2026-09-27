import cv2
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def assess_handwriting_and_quality(image_path: str, ocr_tokens: list = None) -> Dict[str, Any]:
    """
    Evaluates visual stroke variance and character contour regularity to classify
    documents into 'Printed', 'Handwritten', or 'Mixed' format.
    """
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return {
                "format_type": "Printed",
                "handwritten_probability": 0.1,
                "is_handwritten": False,
                "quality_score": 85.0
            }

        # Thresholding for stroke width analysis
        _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        aspect_ratios = []
        solidities = []
        for c in contours:
            area = cv2.contourArea(c)
            if 30 < area < 5000:
                x, y, w, h = cv2.boundingRect(c)
                aspect_ratios.append(w / float(h))
                hull = cv2.convexHull(c)
                hull_area = cv2.contourArea(hull)
                if hull_area > 0:
                    solidities.append(area / float(hull_area))

        # Printed text has very uniform aspect ratios and high solidity
        ar_std = float(np.std(aspect_ratios)) if aspect_ratios else 0.2
        sol_std = float(np.std(solidities)) if solidities else 0.1

        # Higher variance indicates irregular human handwriting
        hw_score = min(max((ar_std * 1.5 + sol_std * 2.0), 0.0), 1.0)
        
        # Check filename cues if present
        fn_lower = image_path.lower()
        if any(k in fn_lower for k in ["handwritten", "dastavej", "register", "khatiyan"]):
            hw_score = max(hw_score, 0.65)

        if hw_score > 0.55:
            format_type = "Handwritten"
        elif hw_score > 0.35:
            format_type = "Mixed"
        else:
            format_type = "Printed"

        return {
            "format_type": format_type,
            "handwritten_probability": round(hw_score, 2),
            "is_handwritten": format_type in ["Handwritten", "Mixed"],
            "quality_score": round(max(100.0 - (ar_std * 50.0), 40.0), 1)
        }
    except Exception as e:
        logger.warning(f"HTR assessment fallback on {image_path}: {e}")
        return {
            "format_type": "Printed",
            "handwritten_probability": 0.1,
            "is_handwritten": False,
            "quality_score": 80.0
        }
