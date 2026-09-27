import re
import logging
from typing import Dict, Any
from app.services.language_detection.script_detector import detect_language

logger = logging.getLogger(__name__)

DOC_TYPE_KEYWORDS = {
    "Mutation Record": [
        "mutation", "register of mutation", "change of hand", "నకలు", "మ్యుటేషన్", "మార్పిడి",
        "नामांतरण", "दाखिल खारिज", "उपनिवेश", "உரிமாற்றம்", "ಮ್ಯುಟೇಶನ್", "নামজারি", "ફેરફાર નોંધ"
    ],
    "Survey Record": [
        "survey", "fmb", "boundaries", "field measurement", "సర్వే", "కొలత", "నక్షా",
        "सीमांकन", "புல எண்", "ನಕ್ಷೆ", "নকশা", "સર્વે નંબર"
    ],
    "Registration Record": [
        "registration", "deed", "sale deed", "stamp", "conveyance", "రిజిస్ట్రేషన్",
        "దరఖాస్తు", "పత్రం", "पंजीकरण", "बैनामा", "दस्तावेज़", "பதிவு", "நோந்தணி", "দলিল"
    ],
    "Pattadar/Land Ownership Record": [
        "pattadar", "adangal", "pahani", "ror", "khata", "form i-b", "account 3",
        "భూమి హక్కు", "హక్కు పత్రం", "యజమాని", "పట్టాదారు", "అడంగల్", "ఖాతా", "విస్తీర్ణం",
        "खतौनी", "खातेदार", "जमाबंदी", "सातबारा", "பட்டா", "பஹானி", "ಖಾತೆ", "পাহানি", "খতিয়ান", "સાતબાર"
    ],
    "Cadastral Map": [
        "cadastral", "map", "parcel map", "village map", "boundary map", "మ్యాప్", "పటం", "नक्शा", "படம்", "ನಕ್ಷೆ"
    ]
}

def classify_document(ocr_text: str, filename: str = "") -> Dict[str, Any]:
    """
    Classifies a land record into statutory revenue categories with format and language attributes.
    """
    text = (ocr_text or "").strip()
    fn = filename.lower()
    lower_text = text.lower()
    
    language = detect_language(text, filename)
    doc_type = "Other"
    type_confidence = 75.0

    # 1. High-confidence filename cue
    for dt, keywords in DOC_TYPE_KEYWORDS.items():
        if any(k in fn for k in keywords):
            doc_type = dt
            type_confidence = 90.0
            break

    # 2. Text keyword matching
    if doc_type == "Other":
        max_matches = 0
        for dt, keywords in DOC_TYPE_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw.lower() in lower_text)
            if matches > max_matches:
                max_matches = matches
                doc_type = dt
                type_confidence = min(70.0 + (matches * 6.0), 95.0)

    # Distinguish format type (printed vs handwritten)
    format_type = "Handwritten" if any(k in fn for k in ["handwritten", "dastavej"]) else "Printed"

    return {
        "doc_type": doc_type,
        "language": language,
        "format_type": format_type,
        "classification_confidence": round(type_confidence, 1)
    }

classify_document_type = classify_document
