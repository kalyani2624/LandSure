from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseOCREngine(ABC):
    @abstractmethod
    def extract_text(self, file_path: str, language: str = "English") -> Dict[str, Any]:
        """
        Executes OCR and returns:
        {
            "text": str,
            "confidence": float,
            "engine": str,
            "lines": [
                {
                    "line_text": str,
                    "bbox": [int, int, int, int], # [x, y, w, h]
                    "words": [
                        {
                            "text": str,
                            "bbox": [int, int, int, int],
                            "confidence": float
                        }
                    ]
                }
            ]
        }
        """
        pass
