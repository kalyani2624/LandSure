import re
from typing import Optional, Dict, Any, Tuple

AREA_UNIT_SYNONYMS = {
    "acres": "Acres",
    "acre": "Acres",
    "ac": "Acres",
    "ఎకరాలు": "Acres",
    "ఎకరములు": "Acres",
    "ఎకర": "Acres",
    "एकड़": "Acres",
    "ಎಕರೆ": "Acres",
    "ഏക്കർ": "Acres",
    "একর": "Acres",
    "એકર": "Acres",
    "ଏକର": "Acres",
    "ਏਕੜ": "Acres",
    
    "guntas": "Guntas",
    "gunta": "Guntas",
    "guntha": "Guntas",
    "గుంటలు": "Guntas",
    "గుంట": "Guntas",
    "ಗುಂಟೆ": "Guntas",
    
    "hectares": "Hectares",
    "hectare": "Hectares",
    "ha": "Hectares",
    "హెక్టార్లు": "Hectares",
    "हेक्टेयर": "Hectares",
    "ஹெக்டேர்": "Hectares",
    "ಹೆಕ್ಟೇರ್": "Hectares",
    
    "cents": "Cents",
    "cent": "Cents",
    "సెంట్లు": "Cents",
    "சென்ட்": "Cents",
    
    "sq yards": "Sq Yards",
    "sq yard": "Sq Yards",
    "గజములు": "Sq Yards",
    "గజాలు": "Sq Yards",
    "वर्ग गज": "Sq Yards"
}

def normalize_area(raw_value: Any, raw_unit: Optional[str] = None, source_text: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Parses and normalizes Indian area/extent representations:
    - 2.35 acres -> {"value": 2.35, "unit": "Acres", "original": "2.35 acres"}
    - 2:35 -> {"value": 2.35, "unit": "Acres", "original": "2:35"}
    - 2.35 ఎకరాలు -> {"value": 2.35, "unit": "Acres", "original": "2.35 ఎకరాలు"}
    """
    if raw_value is None and not source_text:
        return None
        
    s = str(source_text or raw_value or "").strip()
    
    # 1. Parse numeric value from colon or decimal separator
    num_match = re.search(r'([0-9]+[\.:][0-9]{1,3})|([0-9]+(?:\.[0-9]+)?)', s)
    if not num_match:
        return None
        
    raw_num_str = num_match.group(1) or num_match.group(2)
    clean_num_str = raw_num_str.replace(':', '.')
    
    try:
        val = float(clean_num_str)
        if val <= 0:
            return None
    except ValueError:
        return None

    # 2. Determine Unit
    unit = "Acres"
    matched_unit = None
    if raw_unit:
        unit_key = str(raw_unit).lower().strip()
        matched_unit = AREA_UNIT_SYNONYMS.get(unit_key)
        
    if not matched_unit:
        for syn, canonical in AREA_UNIT_SYNONYMS.items():
            if syn in s.lower():
                matched_unit = canonical
                break
                
    unit = matched_unit or "Acres"

    return {
        "value": val,
        "unit": unit,
        "original": s
    }
