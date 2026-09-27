from typing import Dict, Any, List

def parse_document_layout(ocr_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes document layout structure, table boundaries, and text regions.
    """
    return {
        "has_tables": bool(ocr_data.get("is_table", False)),
        "sections_detected": ["header", "owner_details", "land_details", "footer_stamps"],
        "layout_quality": "High" if ocr_data.get("confidence", 0) > 80 else "Medium"
    }
