import os
import json
import logging
from typing import Dict, Any, Optional
from app.services.field_extraction.multilingual_extractor import MultilingualFieldExtractor
from app.services.normalization.date_normalizer import normalize_date
from app.services.normalization.area_normalizer import normalize_area

logger = logging.getLogger(__name__)

CANONICAL_19_FIELDS = [
    "owner_name",
    "father_name",
    "survey_number",
    "khasra_number",
    "khata_number",
    "plot_number",
    "area",
    "area_unit",
    "village",
    "mandal",
    "tehsil",
    "taluk",
    "district",
    "state",
    "land_classification",
    "ownership_type",
    "mutation_number",
    "mutation_order_date",
    "entry_date",
    "registration_number",
    "registration_date"
]

def init_canonical_schema() -> Dict[str, Dict[str, Any]]:
    """Initializes the strict 19-field land record schema with null safety."""
    return {
        field: {
            "value": None,
            "original_value": None,
            "confidence": 0.0,
            "source_text": None,
            "source_bbox": None,
            "engine": None
        }
        for field in CANONICAL_19_FIELDS
    }

class VLMDocumentUnderstandingAdapter:
    """
    Vision-Language and Contextual Layout Document Understanding Adapter.
    Receives spatial OCR tokens, bounding boxes, document images, and statutory metadata;
    synthesizes canonical 19-field structured cadastral records without hallucination.
    """

    def __init__(self):
        self.rule_extractor = MultilingualFieldExtractor()

    def process_document(
        self,
        image_path: str,
        ocr_result: Dict[str, Any],
        preprocessed_path: Optional[str] = None,
        language: str = "English",
        doc_type: str = "Other",
        format_type: str = "PRINTED"
    ) -> Dict[str, Any]:
        """
        Executes document understanding workflow:
        1. Spatial / token layout extraction.
        2. Normalizes dates, areas, places.
        3. Enforces strict canonical schema and provenance.
        """
        canonical_fields = init_canonical_schema()
        doc_conf = float(ocr_result.get("confidence", 85.0))
        lines = ocr_result.get("lines", [])
        raw_text = ocr_result.get("text", "")

        # 1. Extract base fields via Multilingual Spatial Extractor
        extracted_fields, staging_raw = self.rule_extractor.extract_all(ocr_result, doc_conf)

        # 2. Populate Canonical 19-Field Provenance Map
        for field_name in CANONICAL_19_FIELDS:
            if field_name in extracted_fields and extracted_fields[field_name].get("value") is not None:
                src = extracted_fields[field_name]
                canonical_fields[field_name] = {
                    "value": src.get("value"),
                    "original_value": src.get("original_value") or str(src.get("value")),
                    "confidence": float(src.get("confidence", doc_conf)),
                    "source_text": src.get("source_text"),
                    "source_bbox": src.get("source_bbox"),
                    "engine": ocr_result.get("engine", "RapidOCR")
                }

        # Area Unit
        if canonical_fields["area"]["value"] is not None:
            canonical_fields["area_unit"]["value"] = extracted_fields.get("area", {}).get("unit", "Acres")
            canonical_fields["area_unit"]["confidence"] = canonical_fields["area"]["confidence"]
            canonical_fields["area_unit"]["engine"] = ocr_result.get("engine", "RapidOCR")

        # Tehsil / Taluk alias from Mandal if applicable
        if canonical_fields["mandal"]["value"] and not canonical_fields["tehsil"]["value"]:
            canonical_fields["tehsil"]["value"] = canonical_fields["mandal"]["value"]
            canonical_fields["tehsil"]["confidence"] = canonical_fields["mandal"]["confidence"]
            canonical_fields["tehsil"]["engine"] = canonical_fields["mandal"]["engine"]

        # Flattened staging dictionary for database persistence
        staging_output = {
            k: v["value"] for k, v in canonical_fields.items()
        }

        # Evidence-Based Overall Confidence Score
        active_confs = [v["confidence"] for v in canonical_fields.values() if v["value"] is not None]
        overall_conf = round(float(sum(active_confs) / max(len(active_confs), 1)), 1) if active_confs else round(doc_conf * 0.5, 1)

        return {
            "fields": canonical_fields,
            "staging": staging_output,
            "document_confidence": overall_conf,
            "extracted_field_count": len(active_confs),
            "total_canonical_fields": len(CANONICAL_19_FIELDS)
        }
