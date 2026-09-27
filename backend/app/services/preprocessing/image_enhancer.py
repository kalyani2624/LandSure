import os
import cv2
import numpy as np
from PIL import Image
import time
import logging
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)

def detect_skew(image: np.ndarray) -> float:
    """Detect skew angle of the image using Hough Lines with NumPy 2.x safety."""
    try:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
        
        angles = []
        if lines is not None:
            for line in lines:
                l = line[0] if len(line.shape) > 1 else line
                if len(l) >= 4:
                    x1, y1, x2, y2 = int(l[0]), int(l[1]), int(l[2]), int(l[3])
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    if -45 < angle < 45:
                        angles.append(angle)
                    
        return float(np.median(angles)) if angles else 0.0
    except Exception as e:
        logger.warning(f"Skew detection error: {str(e)}")
        return 0.0

def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """Rotate image by a specific angle."""
    if abs(angle) < 0.1:
        return image
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def denoise_photocopy(gray: np.ndarray) -> np.ndarray:
    """Removes salt-and-pepper photocopy speckles while preserving text characters."""
    return cv2.medianBlur(gray, 3)

def enhance_document_image(input_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    High-fidelity image enhancement pipeline for deep-learning OCR models:
    1. Skew angle detection and rotation
    2. High-resolution Grayscale conversion
    3. Photocopy noise filtration
    4. CLAHE contrast enhancement (preserves anti-aliased gradient edges)
    """
    start_time = time.time()
    
    if output_path is None:
        os.makedirs("preprocessed", exist_ok=True)
        base_name = os.path.basename(input_path)
        output_path = os.path.join("preprocessed", f"clean_{base_name}")

    try:
        img = cv2.imread(input_path)
        if img is None:
            pil_img = Image.open(input_path)
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # 1. Skew correction & Deskewing
        skew_angle = detect_skew(img)
        deskewed = rotate_image(img, skew_angle)

        # 2. High-resolution Grayscale conversion
        gray = cv2.cvtColor(deskewed, cv2.COLOR_BGR2GRAY)

        # 3. Background Illumination Normalization & Whitening
        # Removes yellowed background, shadows, and aging paper stains
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        bg = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        norm = cv2.divide(gray, bg, scale=255.0)
        norm = np.clip(norm, 0, 255).astype(np.uint8)

        # 4. Adaptive Contrast Enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        contrast_enhanced = clahe.apply(norm)

        # 5. Denoise photocopy speckles & artifacts while preserving text stroke edges
        denoised = cv2.medianBlur(contrast_enhanced, 3)

        # 6. Unsharp Masking for ultra-crisp, bold, high-contrast text legibility
        gaussian = cv2.GaussianBlur(denoised, (0, 0), 2.0)
        enhanced = cv2.addWeighted(denoised, 1.5, gaussian, -0.5, 0)

        cv2.imwrite(output_path, enhanced)

        return {
            "success": True,
            "output_path": output_path,
            "skew_angle": round(float(skew_angle), 2),
            "noise_removed": True,
            "contrast_enhanced": True,
            "processing_time_ms": int((time.time() - start_time) * 1000)
        }
    except Exception as e:
        logger.warning(f"Image enhancement fallback triggered on {input_path}: {e}")
        try:
            pil_img = Image.open(input_path)
            pil_img.save(output_path)
            return {
                "success": True,
                "output_path": output_path,
                "skew_angle": 0.0,
                "noise_removed": False,
                "contrast_enhanced": False,
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
        except Exception as err:
            return {"success": False, "error": f"Failed preprocessing: {str(err)}"}

preprocess_image = enhance_document_image
