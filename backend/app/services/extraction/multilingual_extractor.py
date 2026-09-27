import re
import logging
from typing import Dict, Any, List, Optional
from app.services.normalization.indic_terms import CANONICAL_FIELD_ALIASES
from app.services.normalization.date_normalizer import normalize_date
from app.services.normalization.area_normalizer import normalize_area

logger = logging.getLogger(__name__)

INDIAN_PLACE_TRANSLITERATION = {
    # Telugu / AP / Telangana
    "పశ్చిమ గోదావరి": "West Godavari",
    "Wes Godavari": "West Godavari",
    "తూర్పు గోదావరి": "East Godavari",
    "తూర్పుగోదావరి": "East Godavari",
    "పెద్దవెంకటాపురం": "Pedavenkatapuram",
    "రాజమండ్రి గ్రామీణ": "Rajahmundry Rural",
    "రాజమండ్రి": "Rajahmundry",
    "కృష్ణా": "Krishna",
    "గుంటూరు": "Guntur",
    "విశాఖపట్నం": "Visakhapatnam",
    "చిత్తూరు": "Chittoor",
    "కడప": "Kadapa",
    "అనంతపురం": "Anantapur",
    "కర్నూలు": "Kurnool",
    "నెల్లూరు": "Nellore",
    "శ్రీకాకుళం": "Srikakulam",
    "విజయనగరం": "Vizianagaram",
    # Hindi / UP / MP
    "हापुड़": "Hapur",
    "हापुड": "Hapur",
    "मेरठ": "Meerut",
    "गाजियाबाद": "Ghaziabad",
    "लखनऊ": "Lucknow",
    "कानपुर": "Kanpur",
    "वाराणसी": "Varanasi",
    "प्रयागराज": "Prayagraj",
    # Tamil Nadu
    "மதுரை": "Madurai",
    "சோழவந்தான்": "Sholavandan",
    "சென்னை": "Chennai",
    "கோயம்புத்தூர்": "Coimbatore",
    "திருச்சிராப்பள்ளி": "Tiruchirappalli"
}

def clean_value_text(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    cleaned = str(val).strip()
    # Remove leading colons, dashes, pipes, equals, slashes, asterisks
    cleaned = re.sub(r'^[:;\-\|=\.\s_~*^/]+', '', cleaned).strip()
    # Remove trailing colons, dashes, pipes, slashes, asterisks
    cleaned = re.sub(r'[:;\-\|=\.\s_~*^/]+$', '', cleaned).strip()
    
    # If text has parenthesized content like a(Kondru Ramu) or (Wes Godavari) or oso(Krishnapuram), extract inner text
    parenthesized = re.findall(r'[\(（]([^\(\)（）]+)[\)）]', cleaned)
    if parenthesized:
        inner = parenthesized[0].strip()
        if len(inner) >= 3 and not re.match(r'^(?:District|Mandal|Village|Owner|Khata|Survey|Area|Type|Class|Pattadar|Account3)$', inner, re.IGNORECASE):
            cleaned = inner

    cleaned = re.sub(r'^[:;\-\|=\.\s_~*^/]+', '', cleaned).strip()
    cleaned = re.sub(r'[:;\-\|=\.\s_~*^/]+$', '', cleaned).strip()
    return cleaned if len(cleaned) > 0 else None

class MultilingualFieldExtractor:
    """
    Data-driven, multi-strategy land record field extractor with strict null safety
    and rich provenance (original_value, source_text, source_bbox, confidence).
    """

    def __init__(self):
        self.aliases = CANONICAL_FIELD_ALIASES

    def _is_known_label(self, text: str) -> bool:
        """Returns True if the line text is just a field header/label without a value."""
        clean = text.lower().strip()
        clean = re.sub(r'[:;\-\|=\.\s\(\)（）]+', ' ', clean).strip()
        
        if re.search(r'\d{3,}', clean) or len(clean.split()) > 4:
            return False

        for field, alias_list in self.aliases.items():
            for alias in alias_list:
                if clean == alias.lower():
                    return True
        return False

    def extract_all(self, ocr_result: Dict[str, Any], doc_confidence: float = 85.0) -> tuple:
        """
        Main extraction entry point.
        Returns:
            (structured_fields_dict, clean_staging_dict)
        """
        raw_text = ocr_result.get("text", "")
        lines = ocr_result.get("lines", [])
        
        if not lines and raw_text:
            for l in raw_text.splitlines():
                l_str = l.strip()
                if l_str:
                    lines.append({
                        "line_text": l_str,
                        "bbox": [0, 0, 0, 0],
                        "confidence": doc_confidence,
                        "words": []
                    })

        # Structured provenance dictionary initialized to null
        structured_fields: Dict[str, Dict[str, Any]] = {
            "owner_name": {"value": None, "original_value": None, "confidence": 0.0, "source_text": None, "source_bbox": None},
            "father_name": {"value": None, "original_value": None, "confidence": 0.0, "source_text": None, "source_bbox": None},
            "survey_number": {"value": None, "original_value": None, "confidence": 0.0, "source_text": None, "source_bbox": None},
            "khata_number": {"value": None, "original_value": None, "confidence": 0.0, "source_text": None, "source_bbox": None},
            "khasra_number": {"value": None, "original_value": None, "confidence": 0.0, "source_text": None, "source_bbox": None},
            "plot_number": {"value": None, "original_value": None, "confidence": 0.0, "source_text": None, "source_bbox": None},
            "area": {"value": None, "unit": "Acres", "original_value": None, "confidence": 0.0, "source_text": None, "source_bbox": None},
            "village": {"value": None, "original_value": None, "confidence": 0.0, "source_text": None, "source_bbox": None},
            "mandal": {"value": None, "original_value": None, "confidence": 0.0, "source_text": None, "source_bbox": None},
            "district": {"value": None, "original_value": None, "confidence": 0.0, "source_text": None, "source_bbox": None},
            "registration_number": {"value": None, "original_value": None, "confidence": 0.0, "source_text": None, "source_bbox": None},
            "registration_date": {"value": None, "original_value": None, "confidence": 0.0, "source_text": None, "source_bbox": None},
            "land_classification": {"value": None, "original_value": None, "confidence": 0.0, "source_text": None, "source_bbox": None}
        }

        # -------------------------------------------------------------
        # 1. Proximity & Label-Value Matching across lines
        # -------------------------------------------------------------
        for field_name, alias_list in self.aliases.items():
            if field_name not in structured_fields:
                continue
            for idx, line_item in enumerate(lines):
                line_text = line_item.get("line_text", "").strip()
                line_bbox = line_item.get("bbox", [0, 0, 0, 0])
                
                matched_alias = None
                for alias in alias_list:
                    if field_name == "owner_name" and "ownership" in line_text.lower():
                        continue
                    if field_name == "village" and any(k in line_text.lower() for k in ["adangal", "account", "department"]):
                        continue

                    pattern = rf'(?i)(?:^|[\s,;\(（])({re.escape(alias)})(?:[\)）\s:;\-=\.]*)(.*)$'
                    match = re.search(pattern, line_text)
                    if match:
                        matched_alias = alias
                        remainder = match.group(2).strip()
                        
                        # Value on the same line
                        if remainder and len(remainder) > 0 and not re.match(r'^[_\s:;\-=\.]+$', remainder):
                            extracted_val = clean_value_text(remainder)
                            if extracted_val and len(extracted_val) > 0:
                                self._assign_field_value(
                                    structured_fields, field_name, extracted_val,
                                    source_text=line_text, source_bbox=line_bbox, confidence=doc_confidence
                                )
                                break
                        # Value on the immediate next line if remainder is empty
                        elif idx + 1 < len(lines):
                            next_line_text = lines[idx + 1].get("line_text", "").strip()
                            next_line_bbox = lines[idx + 1].get("bbox", [0, 0, 0, 0])
                            
                            extracted_val = clean_value_text(next_line_text)
                            if extracted_val and len(extracted_val) > 0 and not self._is_known_label(extracted_val):
                                self._assign_field_value(
                                    structured_fields, field_name, extracted_val,
                                    source_text=f"{line_text} -> {next_line_text}", source_bbox=next_line_bbox, confidence=doc_confidence * 0.95
                                )
                                break
                if structured_fields[field_name]["value"] is not None:
                    break

        # -------------------------------------------------------------
        # 2. Heuristic Pattern Fallbacks for Unextracted Identifiers
        # -------------------------------------------------------------
        # Survey Number Regex (e.g. 145/3A, 124/2A, 124/2, 125/3, 12-15)
        if structured_fields["survey_number"]["value"] is None and raw_text:
            sy_matches = re.findall(r'(?:survey|sy|నం|సంఖ్య|నంబరు|నెం)[\s\.:\-_]*([0-9]{1,4}[\/\-][0-9]{1,4}[A-Za-z]*)', raw_text, re.IGNORECASE)
            if not sy_matches:
                all_slashes = re.findall(r'\b([0-9]{1,4}[\/\-][0-9]{1,3}[A-Za-z0-9]*)\b', raw_text)
                for cand in all_slashes:
                    if not re.search(r'\b(?:19|20)[0-9]{2}\b', cand) and not re.match(r'^[0-3]?[0-9]\/[0-1]?[0-9]$', cand):
                        sy_matches.append(cand)
            if sy_matches:
                clean_sy = re.sub(r'^[^\w]+', '', sy_matches[0])
                clean_sy = re.sub(r'[^0-9A-Za-z\/\-]', '', clean_sy)
                structured_fields["survey_number"] = {
                    "value": str(clean_sy),
                    "original_value": str(sy_matches[0]),
                    "confidence": 88.0,
                    "source_text": str(sy_matches[0]),
                    "source_bbox": None
                }

        # Registration Number Regex (e.g. 2401/2024, 217/2022)
        if structured_fields["registration_number"]["value"] is None and raw_text:
            reg_matches = re.findall(r'(?:దరఖాస్తు|రిజిస్ట్రేషన్|application|reg)[\s\.:\-_]*(?:నం|నంబరు|no)?[\s\.:\-_]*([0-9]{1,6}[\/\-][0-9]{4}[A-Za-z\-]*)', raw_text, re.IGNORECASE)
            if not reg_matches:
                reg_matches = re.findall(r'\b([0-9]{2,5}\/20[0-9]{2}[A-Za-z\-]*)\b', raw_text)
            if reg_matches:
                clean_reg = re.sub(r'[^0-9A-Za-z\/\-]', '', reg_matches[0])
                structured_fields["registration_number"] = {
                    "value": str(clean_reg),
                    "original_value": str(reg_matches[0]),
                    "confidence": 90.0,
                    "source_text": str(reg_matches[0]),
                    "source_bbox": None
                }

        # Registration Date Regex (e.g. 12-04-2024, 15/06/2022)
        if structured_fields["registration_date"]["value"] is None and raw_text:
            date_matches = re.findall(r'\b([0-3]?[0-9][\/\-\.][0-1]?[0-9][\/\-\.]20[0-9]{2})\b', raw_text)
            if date_matches:
                norm_d = normalize_date(date_matches[0])
                if norm_d:
                    structured_fields["registration_date"] = {
                        "value": norm_d["normalized"],
                        "original_value": norm_d["original"],
                        "confidence": 92.0,
                        "source_text": date_matches[0],
                        "source_bbox": None
                    }

        # Khata Number Regex (e.g. 412, 356)
        if structured_fields["khata_number"]["value"] is None and raw_text:
            khata_matches = re.findall(r'(?:ఖాతా|खाता|khata|பட்டா)[\s\.:\-_]*(?:నం|సంఖ్య|no)?[\s\.:\-_]*([0-9]{1,6})\b', raw_text, re.IGNORECASE)
            if khata_matches:
                structured_fields["khata_number"] = {
                    "value": str(khata_matches[0]),
                    "original_value": str(khata_matches[0]),
                    "confidence": 90.0,
                    "source_text": str(khata_matches[0]),
                    "source_bbox": None
                }

        # Area / Extent Fallback (e.g. 2.50 Acres, 2.35)
        if structured_fields["area"]["value"] is None and raw_text:
            area_matches = re.findall(r'(?:విస్తీర్ణం|వైశాల్యం|क्षेत्रफल|extent|area)[\s\.:\-_]*([0-9]+[\.:][0-9]{1,3}(?:\s*(?:ఎకరాలు|acres|acre|హెక్టార్లు|हेक्टेयर|cents))?)', raw_text, re.IGNORECASE)
            if not area_matches:
                area_matches = re.findall(r'\b([0-9]{1,2}[\.:][0-9]{2})\s*(?:acres|acre|hectares|cents)?\b', raw_text, re.IGNORECASE)
            if area_matches:
                norm_a = normalize_area(None, source_text=area_matches[0])
                if norm_a:
                    structured_fields["area"] = {
                        "value": norm_a["value"],
                        "unit": norm_a["unit"],
                        "original_value": norm_a["original"],
                        "confidence": 90.0,
                        "source_text": area_matches[0],
                        "source_bbox": None
                    }

        # -------------------------------------------------------------
        # 3. Construct Final Clean Staging Record
        # -------------------------------------------------------------
        staging_record = {
            "owner_name": structured_fields["owner_name"]["value"],
            "survey_number": structured_fields["survey_number"]["value"],
            "khasra_number": structured_fields["khasra_number"]["value"],
            "khata_number": structured_fields["khata_number"]["value"],
            "plot_number": structured_fields["plot_number"]["value"],
            "area": structured_fields["area"]["value"],
            "area_unit": structured_fields["area"].get("unit", "Acres"),
            "village": structured_fields["village"]["value"],
            "tehsil_mandal": structured_fields["mandal"]["value"],
            "district": structured_fields["district"]["value"],
            "land_classification": structured_fields["land_classification"]["value"],
            "registration_number": structured_fields["registration_number"]["value"],
            "registration_date": structured_fields["registration_date"]["value"]
        }

        return structured_fields, staging_record

    def _assign_field_value(
        self, structured_fields: Dict[str, Any], field_name: str, raw_val: str,
        source_text: str, source_bbox: List[int], confidence: float
    ):
        clean_val = raw_val.strip()
        if not clean_val:
            return

        # Strip secondary language prefixes if mixed (e.g. Survey No / సర్వే నం: 123/4A -> 123/4A)
        for other_alias in self.aliases.get(field_name, []):
            if clean_val.lower().startswith(other_alias.lower()):
                clean_val = re.sub(rf'^{re.escape(other_alias)}[\s:;\-=\./]*', '', clean_val, flags=re.IGNORECASE).strip()

        clean_val = re.sub(r'^[:;\-=\./\s]+', '', clean_val).strip()

        if field_name == "survey_number":
            val = re.sub(r'^[^0-9A-Za-z]+', '', clean_val)
            val = re.sub(r'[^0-9A-Za-z\/\-]', '', val)
            if val:
                structured_fields["survey_number"] = {
                    "value": str(val),
                    "original_value": clean_val,
                    "confidence": confidence,
                    "source_text": source_text,
                    "source_bbox": source_bbox
                }
        elif field_name in ["khasra_number", "plot_number"]:
            val = re.sub(r'^[^0-9A-Za-z]+', '', clean_val)
            structured_fields[field_name] = {
                "value": str(val),
                "original_value": clean_val,
                "confidence": confidence,
                "source_text": source_text,
                "source_bbox": source_bbox
            }
        elif field_name == "khata_number":
            digits = re.findall(r'\d+', clean_val)
            if digits:
                structured_fields["khata_number"] = {
                    "value": str(digits[0]),
                    "original_value": clean_val,
                    "confidence": confidence,
                    "source_text": source_text,
                    "source_bbox": source_bbox
                }
        elif field_name == "registration_number":
            val = re.sub(r'[^0-9A-Za-z\/\-]', '', clean_val)
            structured_fields["registration_number"] = {
                "value": str(val),
                "original_value": clean_val,
                "confidence": confidence,
                "source_text": source_text,
                "source_bbox": source_bbox
            }
        elif field_name == "registration_date":
            norm_d = normalize_date(clean_val)
            if norm_d:
                structured_fields["registration_date"] = {
                    "value": norm_d["normalized"],
                    "original_value": norm_d["original"],
                    "confidence": confidence,
                    "source_text": source_text,
                    "source_bbox": source_bbox
                }
        elif field_name == "area":
            norm_a = normalize_area(None, source_text=clean_val)
            if norm_a:
                structured_fields["area"] = {
                    "value": norm_a["value"],
                    "unit": norm_a["unit"],
                    "original_value": norm_a["original"],
                    "confidence": confidence,
                    "source_text": source_text,
                    "source_bbox": source_bbox
                }
        elif field_name in ["village", "mandal", "district"]:
            transliterated = INDIAN_PLACE_TRANSLITERATION.get(clean_val, clean_val)
            structured_fields[field_name] = {
                "value": transliterated,
                "original_value": clean_val,
                "confidence": confidence,
                "source_text": source_text,
                "source_bbox": source_bbox
            }
        else:
            transliterated = INDIAN_PLACE_TRANSLITERATION.get(clean_val, clean_val)
            structured_fields[field_name] = {
                "value": transliterated,
                "original_value": clean_val,
                "confidence": confidence,
                "source_text": source_text,
                "source_bbox": source_bbox
            }
