from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseAIProvider(ABC):
    """
    Abstract Base Class for Document Perception and Understanding Providers.
    Decouples the core digitization pipeline from specific local or cloud AI backends.
    """

    @abstractmethod
    def analyze_document(
        self,
        image_path: str,
        ocr_context: Optional[Dict[str, Any]] = None,
        hint_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes full document analysis returning format classification,
        raw text, structured fields, confidence, and validation signals.
        """
        pass

    @abstractmethod
    def extract_land_fields(
        self,
        image_path: str,
        ocr_context: Optional[Dict[str, Any]] = None,
        language: str = "English",
        doc_type: str = "Other"
    ) -> Dict[str, Any]:
        """
        Extracts the canonical 19 land record attributes with provenance.
        """
        pass

    @abstractmethod
    def recognize_handwriting(
        self,
        image_path: str,
        ocr_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Performs handwriting recognition / transcription on handwritten or mixed documents.
        """
        pass
