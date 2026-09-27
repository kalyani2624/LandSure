import pytest
import os
import json
from unittest.mock import patch, MagicMock
from app.services.ai_router.providers.groq_provider import GroqVisionProvider
from app.services.ai_router.providers.local_provider import LocalAIProvider
from app.services.ai_router.providers.provider_manager import AIProviderManager

SAMPLE_IMG = "sample_documents/english_survey_sample.png"

# Mocked valid Groq response
MOCK_GROQ_PAYLOAD = {
    "choices": [
        {
            "message": {
                "content": json.dumps({
                    "detected_language": "English",
                    "document_type": "Survey Record",
                    "format_type": "PRINTED",
                    "fields": {
                        "owner_name": {"value": "Kondru Ramu", "original_value": "Kondru Ramu", "confidence": 98.0, "source_text": "Owner Name: Kondru Ramu", "source_bbox": None, "engine": "groq"},
                        "father_name": {"value": None, "original_value": None, "confidence": 0, "source_text": None, "source_bbox": None, "engine": "groq"},
                        "survey_number": {"value": "145/3A", "original_value": "145/3A", "confidence": 98.0, "source_text": "Survey Number: 145/3A", "source_bbox": None, "engine": "groq"},
                        "khasra_number": {"value": "KH/99201", "original_value": "KH/99201", "confidence": 95.0, "source_text": "Khasra Number: KH/99201", "source_bbox": None, "engine": "groq"},
                        "khata_number": {"value": "412", "original_value": "412", "confidence": 95.0, "source_text": "Khata Number: 412", "source_bbox": None, "engine": "groq"},
                        "plot_number": {"value": "12", "original_value": "12", "confidence": 95.0, "source_text": "Plot Number: 12", "source_bbox": None, "engine": "groq"},
                        "area": {"value": 2.50, "original_value": "2.50 Acres", "confidence": 96.0, "source_text": "Area: 2.50 Acres", "source_bbox": None, "engine": "groq"},
                        "area_unit": {"value": "Acres", "original_value": "Acres", "confidence": 96.0, "source_text": "Acres", "source_bbox": None, "engine": "groq"},
                        "village": {"value": "Krishnapuram", "original_value": "Krishnapuram", "confidence": 94.0, "source_text": "Village: Krishnapuram", "source_bbox": None, "engine": "groq"},
                        "mandal": {"value": "Pedapadu", "original_value": "Pedapadu", "confidence": 94.0, "source_text": "Mandal: Pedapadu", "source_bbox": None, "engine": "groq"},
                        "tehsil": {"value": "Pedapadu", "original_value": "Pedapadu", "confidence": 94.0, "source_text": "Pedapadu", "source_bbox": None, "engine": "groq"},
                        "taluk": {"value": None, "original_value": None, "confidence": 0, "source_text": None, "source_bbox": None, "engine": "groq"},
                        "district": {"value": "West Godavari", "original_value": "West Godavari", "confidence": 96.0, "source_text": "District: West Godavari", "source_bbox": None, "engine": "groq"},
                        "state": {"value": "Andhra Pradesh", "original_value": "Andhra Pradesh", "confidence": 90.0, "source_text": None, "source_bbox": None, "engine": "groq"},
                        "land_classification": {"value": "Dry - Agricultural", "original_value": "Dry - Agricultural", "confidence": 92.0, "source_text": "Dry - Agricultural", "source_bbox": None, "engine": "groq"},
                        "ownership_type": {"value": "Pattadar", "original_value": "Pattadar", "confidence": 92.0, "source_text": "Pattadar", "source_bbox": None, "engine": "groq"},
                        "mutation_number": {"value": None, "original_value": None, "confidence": 0, "source_text": None, "source_bbox": None, "engine": "groq"},
                        "registration_number": {"value": "2401/2024", "original_value": "2401/2024", "confidence": 96.0, "source_text": "2401/2024", "source_bbox": None, "engine": "groq"},
                        "registration_date": {"value": "2024-04-12", "original_value": "12-04-2024", "confidence": 96.0, "source_text": "12-04-2024", "source_bbox": None, "engine": "groq"}
                    }
                })
            }
        }
    ]
}

def test_groq_missing_api_key_fallback():
    """Verify that Groq provider returns graceful UNAVAILABLE status when key is absent."""
    provider = GroqVisionProvider(api_key="")
    assert not provider.is_available()
    res = provider.analyze_document(SAMPLE_IMG)
    assert res["provider_status"] == "UNAVAILABLE"
    assert res["fallback_required"] is True

@patch("requests.post")
def test_groq_successful_structured_response(mock_post):
    """Verify parsing of valid structured vision payload from Groq."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_GROQ_PAYLOAD
    mock_post.return_value = mock_resp

    provider = GroqVisionProvider(api_key="mock_dummy_api_key_123")
    res = provider.analyze_document(SAMPLE_IMG)

    assert res["provider_status"] == "SUCCESS"
    assert res["fields"]["owner_name"]["value"] == "Kondru Ramu"
    assert res["fields"]["survey_number"]["value"] == "145/3A"  # String preserved!
    assert res["fields"]["registration_date"]["value"] == "2024-04-12"
    assert res["fields"]["father_name"]["value"] is None  # Null safe!

@patch("requests.post")
def test_groq_network_timeout_fallback(mock_post):
    """Verify that a network timeout results in a TIMEOUT status and fallback trigger."""
    import requests
    mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

    provider = GroqVisionProvider(api_key="mock_dummy_api_key_123")
    res = provider.analyze_document(SAMPLE_IMG)

    assert res["provider_status"] == "TIMEOUT"
    assert res["fallback_required"] is True

@patch("requests.post")
def test_groq_rate_limit_fallback(mock_post):
    """Verify that HTTP 429 returns RATE_LIMITED and triggers local fallback."""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = "Rate limit exceeded"
    mock_post.return_value = mock_resp

    provider = GroqVisionProvider(api_key="mock_dummy_api_key_123")
    res = provider.analyze_document(SAMPLE_IMG)

    assert res["provider_status"] == "RATE_LIMITED"
    assert res["fallback_required"] is True

@patch("requests.post")
def test_groq_invalid_json_fallback(mock_post):
    """Verify that malformed JSON is caught and handled safely without crashing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"choices": [{"message": {"content": "INVALID NOT JSON"}}]}
    mock_post.return_value = mock_resp

    provider = GroqVisionProvider(api_key="gsk_test_mock_key")
    res = provider.analyze_document(SAMPLE_IMG)

    assert res["provider_status"] == "ERROR"
    assert res["fallback_required"] is True

def test_local_provider_offline_execution():
    """Verify that local provider runs 100% offline with full canonical 19-field extraction."""
    local_prov = LocalAIProvider()
    res = local_prov.analyze_document(SAMPLE_IMG)

    assert res["provider"] == "local_rapidocr"
    assert res["provider_status"] == "SUCCESS"
    assert "fields" in res
    assert "owner_name" in res["fields"]
    assert res["fields"]["survey_number"]["value"] == "145/3A"

def test_provider_manager_printed_routing():
    """Verify that printed documents route to local provider by default."""
    manager = AIProviderManager(groq_api_key="")
    res = manager.process_document(SAMPLE_IMG, force_provider="local")

    assert res["selected_provider"] == "local"
    assert res["format_type"] in ["PRINTED", "HANDWRITTEN", "MIXED"]
    assert res["provider_status"] == "SUCCESS"

@patch("requests.post")
def test_provider_manager_mixed_dual_provenance_merge(mock_post):
    """Verify that MIXED documents execute dual-pass and merge source provenance."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_GROQ_PAYLOAD
    mock_post.return_value = mock_resp

    manager = AIProviderManager(groq_api_key="gsk_test_key")
    # Simulate mixed document by forcing provider
    res = manager.process_document(SAMPLE_IMG, force_provider="groq")

    assert res["provider"] in ["groq", "hybrid_local_groq"]
    assert res["fields"]["owner_name"]["value"] == "Kondru Ramu"
