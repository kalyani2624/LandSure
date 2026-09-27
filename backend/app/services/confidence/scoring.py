from typing import Dict, Any, List

def calculate_field_confidences(extracted_fields: Dict[str, Any], base_ocr_confidence: float) -> Dict[str, float]:
    confidences: Dict[str, float] = {}
    for field, val in extracted_fields.items():
        if val is None or val == "":
            confidences[field] = 0.0
        else:
            score = float(base_ocr_confidence)
            if field in ["survey_number", "registration_number", "khata_number"] and len(str(val)) >= 3:
                score = min(score + 2.0, 99.0)
            confidences[field] = round(score, 1)
    return confidences

def calculate_overall_confidence(confidences: Dict[str, float]) -> float:
    valid_scores = [v for k, v in confidences.items() if v > 0.0 and k != "area_unit"]
    if not valid_scores:
        return 50.0
    return round(float(sum(valid_scores) / len(valid_scores)), 1)

def calculate_document_confidence(confidences: Dict[str, float], base_ocr_conf: float = 85.0, anomaly_count: int = 0) -> float:
    avg_field = calculate_overall_confidence(confidences)
    penalty = anomaly_count * 5.0
    combined = (avg_field * 0.7) + (base_ocr_conf * 0.3) - penalty
    return round(max(min(combined, 99.0), 20.0), 1)
