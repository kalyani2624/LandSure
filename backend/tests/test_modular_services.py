import pytest
import os
from app.services.preprocessing import enhance_document_image, detect_skew, rotate_image
from app.services.handwriting import assess_handwriting_and_quality
from app.services.language_detection import detect_language
from app.services.document_classification import classify_document_type
from app.services.layout_analysis import find_spatial_neighbors, parse_tabular_layout
from app.services.field_extraction import MultilingualFieldExtractor, clean_value_text
from app.services.normalization import normalize_date, normalize_area
from app.services.confidence import calculate_document_confidence
from app.services.verification import evaluate_verification_routing

def test_language_detection_multiscript():
    """Verify Unicode block detection across Indic scripts."""
    assert detect_language("ఆంధ్రప్రదేశ్ ప్రభుత్వం పట్టాదారు") == "Telugu"
    assert detect_language("उत्तर प्रदेश भू-अभिलेख खतौनी") == "Hindi"
    assert detect_language("தமிழ்நாடு நில உரிமை ஆவணம்") == "Tamil"
    assert detect_language("ಕರ್ನಾಟಕ ಕಂದಾಯ ಇಲಾಖೆ ಪಹಣಿ") == "Kannada"
    assert detect_language("കേരള ഭൂരേഖ പട്ടയം") == "Malayalam"
    assert detect_language("পশ্চিমবঙ্গ সরকার জমির খতিয়ান") == "Bengali"
    assert detect_language("ગુજરાત મહેસૂલ વિભાગ ગામ નમૂનો") == "Gujarati"
    assert detect_language("ପଞ୍ଜାବ ଓଡ଼ିଶା ଭୂ-ଅଭିଲେଖ") == "Odia"
    assert detect_language("ਪੰਜਾਬ ਸਰਕਾਰ ਜਮ੍ਹਾਂਬੰਦੀ") == "Punjabi"
    assert detect_language("Government Land Revenue Department Form I-B") == "English"

def test_document_classification():
    """Verify statutory revenue document classification."""
    res_ror = classify_document_type("FORM I-B RECORD OF RIGHTS PATTADAR PASSBOOK", "ror_sample.png")
    assert res_ror["doc_type"] == "Pattadar/Land Ownership Record"

    res_mut = classify_document_type("REGISTER OF MUTATION ENTRY 2024", "mutation_doc.png")
    assert res_mut["doc_type"] == "Mutation Record"

    res_reg = classify_document_type("SALE DEED REGISTRATION AGREEMENT", "deed_2022.pdf")
    assert res_reg["doc_type"] == "Registration Record"

def test_layout_and_spatial_neighbor_matching():
    """Verify 2D spatial bounding box association."""
    label_box = [100, 100, 80, 20]
    right_val = {"text": "145/3A", "bbox": [190, 98, 60, 22]}
    far_box = {"text": "District", "bbox": [600, 500, 80, 20]}

    neighbors = find_spatial_neighbors(label_box, [right_val, far_box], direction="right")
    assert len(neighbors) == 1
    assert neighbors[0]["text"] == "145/3A"

def test_tabular_layout_clustering():
    """Verify line clustering into geometric rows."""
    lines = [
        {"line_text": "Col1", "bbox": [10, 50, 40, 20]},
        {"line_text": "Col2", "bbox": [80, 52, 40, 20]},
        {"line_text": "Row2_A", "bbox": [10, 90, 40, 20]},
        {"line_text": "Row2_B", "bbox": [80, 91, 40, 20]}
    ]
    parsed = parse_tabular_layout(lines)
    assert parsed["row_count"] == 2
    assert len(parsed["rows"][0]) == 2
    assert len(parsed["rows"][1]) == 2

def test_handwriting_assessment():
    """Verify HTR quality and format type estimation."""
    res = assess_handwriting_and_quality("sample_documents/telugu_adangal_sample.jpg")
    assert res["format_type"] in ["Printed", "Mixed", "Handwritten"]
    assert "quality_score" in res
    assert "handwritten_probability" in res

def test_verification_routing():
    """Verify confidence and anomaly based queue routing."""
    # High confidence, no anomalies -> Auto-verified
    r1 = evaluate_verification_routing(overall_confidence=92.0, anomalies=[])
    assert r1["status"] == "Verified"
    assert not r1["requires_human_review"]

    # High severity anomaly -> Pending review
    r2 = evaluate_verification_routing(
        overall_confidence=90.0,
        anomalies=[{"rule_name": "OWNER_CONFLICT", "severity": "High"}]
    )
    assert r2["status"] == "Pending Review"
    assert r2["requires_human_review"]

    # Low confidence -> Low Confidence review queue
    r3 = evaluate_verification_routing(overall_confidence=60.0, anomalies=[])
    assert r3["status"] == "Low Confidence"
    assert r3["requires_human_review"]
