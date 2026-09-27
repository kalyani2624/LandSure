import os
import base64
import json
import logging
import requests
from typing import Dict, Any, Optional
from PIL import Image
import io

from app.core.config import settings
from app.services.ai_router.providers.base_provider import BaseAIProvider
from app.services.ai_router.vlm_understanding import CANONICAL_19_FIELDS, init_canonical_schema
from app.services.normalization.date_normalizer import normalize_date
from app.services.normalization.area_normalizer import normalize_area

from app.services.translation import transliterate_indic_text

logger = logging.getLogger(__name__)

GROQ_SYSTEM_PROMPT = """You are an Indian land-record document extraction system.

Inspect ONLY the supplied document image.

Extract only information that is visibly present in the image.

Do not guess.
Do not infer missing fields.
Do not copy values from examples.
Do not use filenames.
Do not use information from previous documents.

The document may be in any Indian language or script (Telugu, Tamil, Hindi, Kannada, Marathi, Gujarati, Odia, Malayalam, English), printed or handwritten.

Understand the source language first.

For Indic/regional language values:
- preserve the original source native script text in "original_value"
- provide an English transliteration or standard English name as the final "value"

Field identity MUST come from the document label, spatial tables, and its spatial relationship to the value.

Return ONLY valid JSON.

Schema:
{
  "detected_language": "Telugu|Tamil|Hindi|Kannada|Marathi|Gujarati|Odia|Malayalam|English",
  "document_type": "Land Record|Mutation Record|Sale Deed|Other",
  "format_type": "HANDWRITTEN|PRINTED|MIXED",
  "fields": {
    "district": {"value": null, "original_value": null, "confidence": 0},
    "mandal_or_tehsil": {"value": null, "original_value": null, "confidence": 0},
    "village": {"value": null, "original_value": null, "confidence": 0},
    "owner_name": {"value": null, "original_value": null, "confidence": 0},
    "father_name": {"value": null, "original_value": null, "confidence": 0},
    "survey_number": {"value": null, "original_value": null, "confidence": 0},
    "khasra_number": {"value": null, "original_value": null, "confidence": 0},
    "khata_number": {"value": null, "original_value": null, "confidence": 0},
    "area": {"value": null, "original_value": null, "confidence": 0},
    "area_unit": {"value": "Acres", "original_value": null, "confidence": 0},
    "registration_number": {"value": null, "original_value": null, "confidence": 0},
    "registration_date": {"value": null, "original_value": null, "confidence": 0},
    "mutation_number": {"value": null, "original_value": null, "confidence": 0}
  },
  "confidence": 85.0,
  "needs_human_review": false
}

Rules:
- Never map a Khasra number to survey_number.
- Never map a mutation number to registration_number.
- Never map mutation order date to registration_date.
- Never map father_name to owner_name.
- Never invent a missing value.
- Preserve survey/khasra/khata/mutation/registration identifiers as strings.
- Normalize dates to YYYY-MM-DD only when the date is clearly readable.
- Normalize area to a numeric value while preserving the unit.
- If a field cannot be confidently read, return null.
- If uncertain, mark needs_human_review=true.
"""

class GroqVisionProvider(BaseAIProvider):
    """
    Multimodal Cloud AI Provider utilizing Groq's low-latency Vision-Language models.
    Supports optical handwriting transcription and zero-shot cadastral document parsing.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        raw_key = api_key if api_key is not None else (os.getenv("GROQ_API_KEY") or getattr(settings, "GROQ_API_KEY", ""))
        self.api_key = str(raw_key).strip("\"' \t\r\n") if raw_key else ""
        self.model = (model or os.getenv("GROQ_MODEL") or getattr(settings, "GROQ_MODEL", "qwen/qwen3.8-27b")).strip("\"' \t\r\n")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def is_available(self) -> bool:
        """Returns True if a valid API key is configured."""
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def _encode_image_to_base64_uri(self, image_path: str) -> str:
        """Encodes local image to base64 data URI string with resizing to optimize token payload."""
        with Image.open(image_path) as img:
            # Resize if dimensions exceed 1024 to conserve tokens (~1,100 tokens) and prevent rate limiting
            if max(img.size) > 1024:
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            rgb_img = img.convert("RGB")
            buffer = io.BytesIO()
            rgb_img.save(buffer, format="JPEG", quality=85)
            encoded_bytes = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded_bytes}"

    def analyze_document(
        self,
        image_path: str,
        ocr_context: Optional[Dict[str, Any]] = None,
        hint_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submits image + supporting OCR tokens to Groq Vision model.
        Supports multi-model fallback across available vision architectures.
        """
        if not self.is_available():
            return {
                "provider": "groq",
                "provider_status": "UNAVAILABLE",
                "error": "GROQ_API_KEY is not configured in environment.",
                "fallback_required": True
            }

        candidate_models = [self.model]
        for fallback_m in ["qwen/qwen3.8-27b", "qwen/qwen3.6-27b"]:
            if fallback_m not in candidate_models:
                candidate_models.append(fallback_m)

        image_data_uri = self._encode_image_to_base64_uri(image_path)
        
        # Construct OCR supporting context prompt with token guard
        ocr_text = (ocr_context.get("text", "") or "")[:300] if ocr_context else ""
        supporting_evidence = ""
        if ocr_text:
            supporting_evidence = f"\n\nSupporting OCR Context:\n\"\"\"{ocr_text}\"\"\""

        user_prompt = f"Analyze this Indian land record image and extract all cadastral fields strictly in the JSON schema.{supporting_evidence}"

        last_error = None
        for current_model in candidate_models:
            try:
                payload = {
                    "model": current_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": GROQ_SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image_data_uri}
                                }
                            ]
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2500
                }

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                resp = requests.post(self.api_url, json=payload, headers=headers, timeout=35.0)
                
                if resp.status_code == 200:
                    resp_data = resp.json()
                    raw_content = resp_data["choices"][0]["message"]["content"]
                    active_model = current_model
                    break
                elif resp.status_code == 429:
                    logger.warning(f"Groq model {current_model} rate limited (HTTP 429). Attempting fallback model...")
                    last_error = f"Rate limited on {current_model}"
                    continue
                else:
                    logger.warning(f"Groq model {current_model} returned HTTP {resp.status_code}: {resp.text}")
                    last_error = f"HTTP {resp.status_code}: {resp.text}"
                    continue
            except requests.exceptions.Timeout as e:
                logger.warning(f"Groq model {current_model} timed out: {e}")
                last_error = "TIMEOUT: Request timed out"
                continue
            except Exception as e:
                logger.warning(f"Groq model {current_model} invocation error: {e}")
                last_error = str(e)
                continue
        else:
            # All candidate models failed or rate limited
            is_timeout = "timeout" in str(last_error).lower()
            is_ratelimit = "rate limited" in str(last_error).lower() or "429" in str(last_error)
            return {
                "provider": "groq",
                "provider_status": "TIMEOUT" if is_timeout else ("RATE_LIMITED" if is_ratelimit else "API_ERROR"),
                "error": last_error or "All Groq Vision models failed.",
                "fallback_required": True
            }

        try:
                
                # Robust extraction of JSON object from reasoning output
                import re
                clean = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
                if "<think>" in clean:
                    clean = re.sub(r'<think>.*', '', clean, flags=re.DOTALL).strip()

                clean = re.sub(r'^```(?:json)?\s*', '', clean, flags=re.IGNORECASE).strip()
                clean = re.sub(r'\s*```$', '', clean).strip()

                parsed_json = None
                if clean.startswith("{") and clean.endswith("}"):
                    try:
                        parsed_json = json.loads(clean)
                    except Exception:
                        pass

                if parsed_json is None:
                    # Regex search for outermost JSON structure in raw content
                    m = re.search(r'\{[\s\S]*\}', raw_content)
                    if m:
                        json_str = m.group(0)
                        json_str = re.sub(r'<think>.*?</think>', '', json_str, flags=re.DOTALL).strip()
                        try:
                            parsed_json = json.loads(json_str)
                        except Exception:
                            # Resilient key-value extraction fallback if JSON has missing commas
                            resilient_dict = {}
                            for f in CANONICAL_19_FIELDS:
                                pat = rf'"{f}"\s*:\s*(?:"([^"]*)"|([0-9\.]+)|(null)|(true)|(false))'
                                km = re.search(pat, json_str, re.IGNORECASE)
                                if km:
                                    if km.group(1) is not None:
                                        val = km.group(1).strip()
                                        resilient_dict[f] = val if val and val.lower() != "null" else None
                                    elif km.group(2) is not None:
                                        try:
                                            resilient_dict[f] = float(km.group(2)) if "." in km.group(2) else int(km.group(2))
                                        except Exception:
                                            resilient_dict[f] = km.group(2)
                                    else:
                                        resilient_dict[f] = None
                            if any(v is not None for v in resilient_dict.values()):
                                parsed_json = resilient_dict

                def _sanitize_val(v):
                    if v is None:
                        return None
                    cleaned = str(v).strip()
                    cleaned = re.sub(r'[\*\#\`"\'\(\)]+', '', cleaned).strip()
                    meta_phrases = [
                        "the label is", "the label says", "the label", "label", "not present",
                        "not found", "not readable", "not clearly", "cannot be", "obscured",
                        "unclear", "none", "null", "n/a", "no value", "blank", "is empty",
                        "not mentioned", "not available"
                    ]
                    if any(p in cleaned.lower() for p in meta_phrases):
                        return None
                    return cleaned if len(cleaned) > 0 else None

                if parsed_json is None:
                    # Secondary fallback: Extract fields directly from reasoning/thinking trace if JSON was truncated
                    think_extracted = {}
                    think_patterns = {
                        "village": [
                            r'(?:గ్రామము|గ్రామం|Village)[^-\n:]*(?:->|:)\s*([^\n\r\(\)]+)',
                            r'(?:Village|గ్రామము|గ్రామం).*?(?:name is|is|:)\s*["\']?([^"\']+)["\']?'
                        ],
                        "mandal": [
                            r'(?:మండలము|మండలం|Mandal)[^-\n:]*(?:->|:)\s*([^\n\r\(\)]+)',
                            r'(?:Mandal|మండలము|మండలం).*?(?:name is|is|:)\s*["\']?([^"\']+)["\']?'
                        ],
                        "district": [
                            r'(?:జిల్లా|District)[^-\n:]*(?:->|:)\s*([^\n\r\(\)]+)',
                            r'(?:District|జిల్లా).*?(?:value is|is|:)\s*["\']?([^"\']+)["\']?'
                        ],
                        "owner_name": [
                            r'(?:సభ్యుల పేరు|యజమాని|Owner Name|Owner)[^-\n:]*(?:->|:)\s*([^\n\r\(\)]+)',
                            r'(?:Owner Name|యజమాని).*?(?:name is|is|:)\s*["\']?([^"\']+)["\']?'
                        ],
                        "father_name": [
                            r'(?:తండ్రి పేరు|Father Name|Father)[^-\n:]*(?:->|:)\s*([^\n\r\(\)]+)',
                            r'(?:Father Name|తండ్రి).*?(?:name is|is|:)\s*["\']?([^"\']+)["\']?'
                        ],
                        "survey_number": [
                            r'(?:సర్వే నం|సర్వే సంఖ్య|Survey No|Survey Number)[^-\n:]*(?:->|:)\s*([0-9\/A-Za-z]+)',
                            r'(?:Survey Number|సర్వే నం).*?(?:value is|is|:)\s*["\']?([0-9\/A-Za-z]+)["\']?'
                        ],
                        "khata_number": [
                            r'(?:ఖాతా నం|ఖాతా సంఖ్య|Khata No|Khata Number)[^-\n:]*(?:->|:)\s*([0-9]+)',
                            r'(?:Khata Number|ఖాతా నం).*?(?:value is|is|:)\s*["\']?([0-9]+)["\']?'
                        ],
                        "area": [
                            r'(?:వైశాల్యం|విస్తీర్ణం|Area)[^-\n:]*(?:->|:)\s*([0-9\.]+)',
                            r'(?:Area|విస్తీర్ణం).*?(?:value is|is|:)\s*["\']?([0-9\.]+)["\']?'
                        ],
                        "registration_number": [
                            r'(?:దరఖాస్తు నం|Application No|Registration No)[^-\n:]*(?:->|:)\s*([0-9\/A-Za-z]+)',
                            r'(?:Registration Number|దరఖాస్తు నం).*?(?:value is|is|:)\s*["\']?([0-9\/A-Za-z]+)["\']?'
                        ],
                        "registration_date": [
                            r'(?:తేదీ|Date)[^-\n:]*(?:->|:)\s*([0-9\/\-\.]+)',
                            r'(?:Registration Date|తేదీ).*?(?:value is|is|:)\s*["\']?([0-9\/\-\.]+)["\']?'
                        ]
                    }
                    for fname, pat_list in think_patterns.items():
                        for pat in pat_list:
                            pm = re.search(pat, raw_content, re.IGNORECASE)
                            if pm:
                                val = pm.group(1).strip()
                                sanitized_think_val = _sanitize_val(val)
                                if sanitized_think_val:
                                    think_extracted[fname] = sanitized_think_val
                                    break
                    if think_extracted:
                        parsed_json = think_extracted

                if parsed_json is None:
                    raise ValueError(f"No valid JSON or reasoning structure found in Groq response: {raw_content[:200]}")

                # Format and sanitize fields
                canonical_fields = init_canonical_schema()
                model_fields = parsed_json.get("fields", parsed_json)

                if "mandal_or_tehsil" in model_fields and model_fields["mandal_or_tehsil"] is not None:
                    m_obj = model_fields["mandal_or_tehsil"]
                    if "mandal" not in model_fields or model_fields["mandal"] is None:
                        model_fields["mandal"] = m_obj
                    if "tehsil" not in model_fields or model_fields["tehsil"] is None:
                        model_fields["tehsil"] = m_obj

                for field_name in CANONICAL_19_FIELDS:
                    if field_name in model_fields and model_fields[field_name] is not None:
                        f_obj = model_fields[field_name]
                        if isinstance(f_obj, dict):
                            raw_val = f_obj.get("value")
                            orig_val = f_obj.get("original_value")
                            
                            san_val = _sanitize_val(raw_val)
                            san_orig = _sanitize_val(orig_val)
                            
                            chosen_orig = san_orig or san_val
                            if chosen_orig is not None:
                                # Determine English value
                                if san_val and not any(0x0C00 <= ord(c) <= 0x0D7F or 0x0900 <= ord(c) <= 0x097F for c in str(san_val)):
                                    final_val = str(san_val)
                                else:
                                    final_val = transliterate_indic_text(str(chosen_orig))
                                    
                                canonical_fields[field_name] = {
                                    "value": str(final_val) if field_name in ["survey_number", "khasra_number", "khata_number", "registration_number", "plot_number"] else final_val,
                                    "original_value": str(chosen_orig),
                                    "confidence": float(f_obj.get("confidence", 92.0)),
                                    "source_text": f_obj.get("source_text"),
                                    "source_bbox": f_obj.get("source_bbox"),
                                    "engine": self.model
                                }
                        else:
                            # Scalar fallback
                            sanitized = _sanitize_val(f_obj)
                            if sanitized is not None:
                                final_val = transliterate_indic_text(str(sanitized))
                                canonical_fields[field_name] = {
                                    "value": str(final_val) if field_name in ["survey_number", "khasra_number", "khata_number", "registration_number", "plot_number"] else final_val,
                                    "original_value": str(sanitized),
                                    "confidence": 92.0,
                                    "source_text": None,
                                    "source_bbox": None,
                                    "engine": self.model
                                }

                # Normalize dates & areas
                if canonical_fields["registration_date"]["value"]:
                    norm_d = normalize_date(str(canonical_fields["registration_date"]["value"]))
                    if norm_d:
                        canonical_fields["registration_date"]["value"] = norm_d["normalized"]

                if canonical_fields["area"]["value"]:
                    norm_a = normalize_area(None, source_text=str(canonical_fields["area"]["value"]))
                    if norm_a:
                        canonical_fields["area"]["value"] = norm_a["value"]
                        canonical_fields["area_unit"]["value"] = norm_a["unit"]

                staging = {k: v["value"] for k, v in canonical_fields.items()}
                
                # Prototype 13 core field confidence calculation
                core_keys = ["district", "mandal", "village", "owner_name", "father_name", "survey_number", "khasra_number", "khata_number", "area", "registration_number", "registration_date", "mutation_number"]
                active_confs = [canonical_fields[k]["confidence"] for k in core_keys if canonical_fields[k]["value"] is not None]
                
                model_reported_conf = float(parsed_json.get("confidence", 0)) if isinstance(parsed_json.get("confidence"), (int, float)) else 0.0
                if model_reported_conf > 0:
                    overall_conf = round(model_reported_conf, 1)
                elif active_confs:
                    overall_conf = round(float(sum(active_confs) / len(active_confs)), 1)
                else:
                    overall_conf = 65.0

                needs_review = bool(parsed_json.get("needs_human_review", overall_conf < 85.0))

                return {
                    "provider": "groq",
                    "provider_status": "SUCCESS",
                    "model": self.model,
                    "format_type": parsed_json.get("format_type", "HANDWRITTEN" if "Handwritten" in parsed_json.get("format_type", "") else "PRINTED"),
                    "format_confidence": 92.0,
                    "language": parsed_json.get("detected_language", "Telugu"),
                    "script": parsed_json.get("detected_language", "Telugu"),
                    "doc_type": parsed_json.get("document_type", "Land Record"),
                    "ocr": ocr_context or {"text": "", "confidence": overall_conf, "lines": []},
                    "fields": canonical_fields,
                    "staging": staging,
                    "confidence": overall_conf,
                    "needs_human_review": needs_review,
                    "fallback_required": False
                }

        except requests.exceptions.Timeout:
            logger.warning("Groq API request timed out (>12s).")
            return {
                "provider": "groq",
                "provider_status": "TIMEOUT",
                "error": "Groq API timed out.",
                "fallback_required": True
            }
        except Exception as e:
            logger.error(f"Groq provider unexpected error: {str(e)}")
            return {
                "provider": "groq",
                "provider_status": "ERROR",
                "error": str(e),
                "fallback_required": True
            }

    def extract_land_fields(
        self,
        image_path: str,
        ocr_context: Optional[Dict[str, Any]] = None,
        language: str = "English",
        doc_type: str = "Other"
    ) -> Dict[str, Any]:
        return self.analyze_document(image_path, ocr_context=ocr_context, hint_language=language)

    def recognize_handwriting(
        self,
        image_path: str,
        ocr_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return self.analyze_document(image_path, ocr_context=ocr_context)
