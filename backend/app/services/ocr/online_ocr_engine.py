import os
import requests
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.services.ocr.base_ocr import BaseOCREngine

logger = logging.getLogger(__name__)

class OnlineOCREngine(BaseOCREngine):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OCR_SPACE_API_KEY or "helloworld"
        self.url = "https://api.ocr.space/parse/image"

    def extract_text(self, file_path: str, language: str = "auto") -> Dict[str, Any]:
        """
        Sends image to OCR.space Engine 2 with full word & line bounding box preservation.
        """
        try:
            logger.info(f"Connecting to OCR.space online engine for {os.path.basename(file_path)}...")
            with open(file_path, 'rb') as f:
                response = requests.post(
                    self.url,
                    files={'file': f},
                    data={
                        'apikey': self.api_key,
                        'language': 'auto',
                        'OCREngine': '2',
                        'scale': True,
                        'isTable': True,
                        'isOverlayRequired': True
                    },
                    timeout=25
                )
            result = response.json()
            if result.get("OCRExitCode") == 1:
                parsed_results = result.get("ParsedResults", [])
                if parsed_results:
                    main_parsed = parsed_results[0]
                    text = main_parsed.get("ParsedText", "").strip()
                    
                    # Extract lines and word bounding boxes
                    lines_list: List[Dict[str, Any]] = []
                    overlay = main_parsed.get("TextOverlay", {})
                    overlay_lines = overlay.get("Lines", []) if isinstance(overlay, dict) else []
                    
                    for l in overlay_lines:
                        line_text = l.get("LineText", "")
                        words_data = l.get("Words", [])
                        words_list = []
                        for w in words_data:
                            words_list.append({
                                "text": w.get("WordText", ""),
                                "bbox": [
                                    int(w.get("Left", 0)),
                                    int(w.get("Top", 0)),
                                    int(w.get("Width", 0)),
                                    int(w.get("Height", 0))
                                ],
                                "confidence": 88.0
                            })
                            
                        min_top = int(l.get("MinTop", 0))
                        max_h = int(l.get("MaxHeight", 0))
                        lines_list.append({
                            "line_text": line_text,
                            "bbox": [0, min_top, 0, max_h],
                            "words": words_list
                        })
                        
                    logger.info("Online OCR extracted text & overlay bounding boxes successfully.")
                    return {
                        "text": text,
                        "confidence": 88.0,
                        "engine": "OCR.space Online API (Engine 2)",
                        "lines": lines_list
                    }
            logger.warning(f"OCR.space API message: {result.get('ErrorMessage')}")
        except Exception as e:
            logger.warning(f"Online OCR request failed: {str(e)}")
            
        return {
            "text": "",
            "confidence": 0.0,
            "engine": "Failed",
            "lines": []
        }
