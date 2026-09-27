import os
import json
import logging
import requests
from typing import Dict, Any, Optional, Tuple
from app.services.field_extraction.multilingual_extractor import MultilingualFieldExtractor
from app.services.normalization.date_normalizer import normalize_date
from app.services.normalization.area_normalizer import normalize_area

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """You are an expert AI Indian Land Revenue Officer and Cadastral Document Parser.
Your task is to analyze the provided OCR text from an Indian land record (e.g., Form I-B / ROR, Grama Adangal, Pahani, Khata Khatauni, Patta Chitta, 7/12 Extract, Mutation Record, or Sale Deed) and extract the key cadastral attributes into a strictly formatted JSON object.

Extract the following fields (return null for any field that is NOT present in the document):
- owner_name: Name of the landowner/pattadar/khatedar. Exclude label headers like 'Owner Name', 'Pattadar', etc.
- father_name: Father's or husband's name of the owner if mentioned.
- survey_number: The land survey or sub-division number (e.g. 145/3A, 124/2, 12-15).
- khasra_number: The khasra / dag number if distinct from survey number.
- khata_number: The khata / patta / account number (e.g. 412, 356).
- plot_number: The site / plot / door number if mentioned.
- area: The numeric land extent (e.g. 2.50, 1.25).
- area_unit: The unit of measurement ('Acres', 'Hectares', 'Guntas', 'Bighas', 'Cents', 'Sq Yards').
- village: The revenue village name (transliterated to English if in regional script).
- tehsil_mandal: The Tehsil, Mandal, or Taluk name.
- district: The District name.
- land_classification: Type of land (e.g. 'Dry - Agricultural', 'Wet', 'Inam', 'Government', 'Non-Agricultural').
- registration_number: Application or registration deed number (e.g. 2401/2024, 217/2022).
- registration_date: Registration or issuance date in YYYY-MM-DD format.

Rules:
1. Return ONLY valid JSON matching this schema with no conversational text or markdown fences.
2. If a field cannot be confidently identified, set its value to null. Do NOT invent data.
3. Standardize dates to YYYY-MM-DD format.
"""

class AILandExtractionAgent:
    """
    Ensemble AI Land Record Extraction Agent combining deep-learning layout perception,
    local/cloud Vision-Language LLMs, and deterministic spatial heuristics.
    """

    def __init__(self, ollama_url: str = "http://127.0.0.1:11434", model_name: str = "qwen2.5:3b"):
        self.ollama_url = os.getenv("OLLAMA_URL", ollama_url)
        self.model_name = os.getenv("LLM_MODEL_NAME", model_name)
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.rule_extractor = MultilingualFieldExtractor()

    def extract_with_ensemble(
        self,
        ocr_result: Dict[str, Any],
        doc_confidence: float = 85.0,
        language: str = "English",
        doc_type: str = "Other"
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Executes ensemble extraction:
        1. Runs fast deterministic spatial extraction.
        2. Queries the AI Reasoning Agent if available.
        3. Cross-verifies and merges results with boosted confidence scores.
        """
        structured_fields, staging_record = self.rule_extractor.extract_all(ocr_result, doc_confidence)
        agent_data = self._query_ai_agent(ocr_result.get("text", ""), language, doc_type)

        if not agent_data:
            return structured_fields, staging_record

        merged_staging = dict(staging_record)

        for field, agent_val in agent_data.items():
            if field not in structured_fields:
                continue
            
            rule_val = staging_record.get(field)
            
            if rule_val is not None and agent_val is not None and str(rule_val).strip().lower() == str(agent_val).strip().lower():
                structured_fields[field]["confidence"] = min(structured_fields[field]["confidence"] + 10.0, 99.0)
            
            elif rule_val is None and agent_val is not None:
                cleaned_agent_val = agent_val
                if field == "registration_date":
                    norm_d = normalize_date(str(agent_val))
                    cleaned_agent_val = norm_d["normalized"] if norm_d else str(agent_val)
                elif field == "area":
                    norm_a = normalize_area(None, source_text=str(agent_val))
                    cleaned_agent_val = norm_a["value"] if norm_a else agent_val

                merged_staging[field] = cleaned_agent_val
                structured_fields[field]["value"] = cleaned_agent_val
                structured_fields[field]["original_value"] = str(agent_val)
                structured_fields[field]["confidence"] = 88.0
                structured_fields[field]["source_text"] = f"AI Agent Contextual Resolution: {agent_val}"

        return structured_fields, merged_staging

    def _query_ai_agent(self, ocr_text: str, language: str, doc_type: str) -> Optional[Dict[str, Any]]:
        """Queries local Ollama or configured Cloud API."""
        if not ocr_text or len(ocr_text.strip()) < 20:
            return None

        # 1. Try Local Ollama (100% Offline Edge Inference)
        try:
            prompt = f"""Document Language: {language}
Document Classification: {doc_type}

OCR Recognized Text:
\"\"\"{ocr_text}\"\"\"

Extract all land record fields according to the schema in JSON format:"""

            payload = {
                "model": self.model_name,
                "system": EXTRACTION_SYSTEM_PROMPT,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1, "num_predict": 512}
            }
            
            resp = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=2.5)
            if resp.status_code == 200:
                resp_json = resp.json()
                raw_response = resp_json.get("response", "{}")
                return json.loads(raw_response)
        except Exception as e:
            logger.debug(f"Local Ollama agent not active: {e}")

        # 2. Try Gemini API if key is present
        if self.gemini_api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
                gemini_payload = {
                    "contents": [{
                        "parts": [
                            {"text": EXTRACTION_SYSTEM_PROMPT},
                            {"text": f"Document Language: {language}\nDoc Type: {doc_type}\nText:\n{ocr_text}"}
                        ]
                    }],
                    "generationConfig": {"response_mime_type": "application/json", "temperature": 0.1}
                }
                g_resp = requests.post(url, json=gemini_payload, timeout=5.0)
                if g_resp.status_code == 200:
                    text_content = g_resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text_content)
            except Exception as e:
                logger.warning(f"Gemini API query error: {e}")

        return None
