import cv2
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from PIL import Image

logger = logging.getLogger(__name__)

def classify_document_format(
    image_path: str,
    ocr_lines: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Scientific, content-based document format classifier (PRINTED | HANDWRITTEN | MIXED | UNKNOWN).
    Analyzes visual stroke morphology, aspect ratio distributions, horizontal projection
    profiles, and OCR token confidence variance without relying on filenames or metadata.
    """
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            pil_img = Image.open(image_path).convert('L')
            img = np.array(pil_img)

        h, w = img.shape
        if h < 50 or w < 50:
            return {
                "format_type": "UNKNOWN",
                "confidence": 0.0,
                "method": "insufficient_resolution",
                "needs_human_review": True
            }

        # 1. Binarize for stroke and contour analysis
        _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Use RETR_LIST to capture all character glyphs (not just external border frames)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        char_aspect_ratios = []
        char_heights = []
        solidities = []

        for c in contours:
            area = cv2.contourArea(c)
            if 15 < area < (h * w * 0.05):
                bx, by, bw, bh = cv2.boundingRect(c)
                if 5 < bh < (h * 0.2) and 3 < bw < (w * 0.5):
                    char_aspect_ratios.append(bw / float(bh))
                    char_heights.append(bh)
                    hull = cv2.convexHull(c)
                    hull_area = cv2.contourArea(hull)
                    if hull_area > 0:
                        solidities.append(area / float(hull_area))

        # Check for empty or unreadable images
        if len(char_aspect_ratios) < 10:
            return {
                "format_type": "UNKNOWN",
                "confidence": 35.0,
                "method": "insufficient_glyph_contours",
                "needs_human_review": True
            }

        # 2. Statistical Morphology Metrics
        ar_std = float(np.std(char_aspect_ratios))
        height_cv = float(np.std(char_heights) / (np.mean(char_heights) + 1e-5))
        solidity_std = float(np.std(solidities))

        # 3. Horizontal Projection Profile (Line Regularity & Periodicity)
        proj_profile = np.sum(thresh, axis=1) / 255.0
        line_peaks = (proj_profile > np.mean(proj_profile)).astype(int)
        line_transitions = np.sum(np.abs(np.diff(line_peaks))) // 2

        # 4. Multimodal OCR Confidence Signal
        ocr_conf_mean = 85.0
        ocr_conf_std = 8.0
        if ocr_lines and len(ocr_lines) > 0:
            confs = [float(l.get("confidence", 75.0)) for l in ocr_lines if "confidence" in l]
            if confs:
                ocr_conf_mean = float(np.mean(confs))
                ocr_conf_std = float(np.std(confs))

        # 5. Evidence-Based Scoring Calculation
        # Printed text has high OCR confidence (> 80%), regular line transitions, and low contour stroke variance
        score_printed = 0.0
        score_handwritten = 0.0

        if ocr_conf_mean >= 80.0:
            score_printed += 45.0
        elif ocr_conf_mean < 60.0:
            score_handwritten += 45.0
        else:
            score_printed += 20.0
            score_handwritten += 20.0

        if ocr_conf_std < 15.0:
            score_printed += 25.0
        elif ocr_conf_std > 25.0:
            score_handwritten += 25.0
        else:
            score_printed += 12.0
            score_handwritten += 12.0

        if line_transitions >= 4:
            score_printed += 20.0
        else:
            score_handwritten += 20.0

        if solidity_std < 0.18:
            score_printed += 10.0
        else:
            score_handwritten += 10.0

        total = score_printed + score_handwritten
        p_prob = score_printed / max(total, 1.0)
        h_prob = score_handwritten / max(total, 1.0)
        margin = abs(p_prob - h_prob)

        if margin < 0.18:
            format_type = "MIXED"
            conf = round(65.0 + (margin * 100.0), 1)
            needs_review = True
        elif p_prob > h_prob:
            format_type = "PRINTED"
            conf = round(min(70.0 + (p_prob * 28.0), 98.0), 1)
            needs_review = conf < 75.0
        else:
            format_type = "HANDWRITTEN"
            conf = round(min(70.0 + (h_prob * 28.0), 98.0), 1)
            needs_review = conf < 75.0

        return {
            "format_type": format_type,
            "confidence": conf,
            "method": "morphological_stroke_and_projection_analysis",
            "needs_human_review": needs_review,
            "metrics": {
                "aspect_ratio_std": round(ar_std, 3),
                "height_cv": round(height_cv, 3),
                "solidity_std": round(solidity_std, 3),
                "line_transitions": int(line_transitions),
                "ocr_confidence_mean": round(ocr_conf_mean, 1),
                "ocr_confidence_std": round(ocr_conf_std, 1)
            }
        }

    except Exception as e:
        logger.error(f"Format classification error: {e}")
        return {
            "format_type": "UNKNOWN",
            "confidence": 0.0,
            "method": f"error: {str(e)}",
            "needs_human_review": True
        }

assess_handwriting_and_quality = classify_document_format
