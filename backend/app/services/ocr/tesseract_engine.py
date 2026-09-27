import os
import pytesseract
from PIL import Image
import logging
from typing import Dict, Any, List
from app.services.ocr.base_ocr import BaseOCREngine

logger = logging.getLogger(__name__)

LANGUAGE_CODE_MAP = {
    "English": "eng",
    "Telugu": "tel+eng",
    "Hindi": "hin+eng",
    "Tamil": "tam+eng",
    "Kannada": "kan+eng",
    "Malayalam": "mal+eng",
    "Marathi": "mar+eng",
    "Bengali": "ben+eng",
    "Gujarati": "guj+eng",
    "Odia": "ori+eng",
    "Punjabi": "pan+eng",
    "Auto": "eng"
}

class TesseractOCREngine(BaseOCREngine):
    def extract_text(self, file_path: str, language: str = "English") -> Dict[str, Any]:
        lang_code = LANGUAGE_CODE_MAP.get(language, "eng")
        lines_list: List[Dict[str, Any]] = []
        confidences = []
        
        try:
            img = Image.open(file_path)
            ocr_text = pytesseract.image_to_string(img, lang=lang_code)
            
            try:
                data = pytesseract.image_to_data(img, lang=lang_code, output_type=pytesseract.Output.DICT)
                n_boxes = len(data.get('text', []))
                
                current_line_num = -1
                current_line_words = []
                
                for i in range(n_boxes):
                    text_word = data['text'][i].strip()
                    conf_val = int(data['conf'][i])
                    if conf_val != -1:
                        confidences.append(conf_val)
                        
                    if text_word:
                        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                        line_num = data['line_num'][i]
                        
                        word_obj = {
                            "text": text_word,
                            "bbox": [x, y, w, h],
                            "confidence": float(max(conf_val, 0))
                        }
                        
                        if line_num != current_line_num:
                            if current_line_words:
                                line_text = " ".join(w["text"] for w in current_line_words)
                                min_x = min(w["bbox"][0] for w in current_line_words)
                                min_y = min(w["bbox"][1] for w in current_line_words)
                                max_x = max(w["bbox"][0] + w["bbox"][2] for w in current_line_words)
                                max_y = max(w["bbox"][1] + w["bbox"][3] for w in current_line_words)
                                lines_list.append({
                                    "line_text": line_text,
                                    "bbox": [min_x, min_y, max_x - min_x, max_y - min_y],
                                    "words": current_line_words
                                })
                            current_line_num = line_num
                            current_line_words = [word_obj]
                        else:
                            current_line_words.append(word_obj)
                            
                if current_line_words:
                    line_text = " ".join(w["text"] for w in current_line_words)
                    min_x = min(w["bbox"][0] for w in current_line_words)
                    min_y = min(w["bbox"][1] for w in current_line_words)
                    max_x = max(w["bbox"][0] + w["bbox"][2] for w in current_line_words)
                    max_y = max(w["bbox"][1] + w["bbox"][3] for w in current_line_words)
                    lines_list.append({
                        "line_text": line_text,
                        "bbox": [min_x, min_y, max_x - min_x, max_y - min_y],
                        "words": current_line_words
                    })
            except Exception as e:
                logger.warning(f"Failed to extract tesseract bounding boxes: {str(e)}")

            avg_conf = sum(confidences) / len(confidences) if confidences else 85.0

            return {
                "text": ocr_text.strip(),
                "confidence": round(float(avg_conf), 1),
                "engine": f"Tesseract-OCR ({lang_code})",
                "lines": lines_list
            }
        except Exception as err:
            logger.warning(f"Tesseract OCR not available or failed on {file_path}: {err}")
            return {
                "text": "",
                "confidence": 0.0,
                "engine": f"Tesseract-OCR ({lang_code})",
                "lines": []
            }
