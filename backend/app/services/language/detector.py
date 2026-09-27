import re

INDIC_SCRIPT_RANGES = {
    "Telugu": r'[\u0c00-\u0c7f]',
    "Hindi": r'[\u0900-\u097f]',
    "Tamil": r'[\u0b80-\u0bff]',
    "Kannada": r'[\u0c80-\u0cff]',
    "Malayalam": r'[\u0d00-\u0d7f]',
    "Bengali": r'[\u0980-\u09ff]',
    "Gujarati": r'[\u0a80-\u0aff]',
    "Odia": r'[\u0b00-\u0b7f]',
    "Punjabi": r'[\u0a00-\u0a7f]',
}

def detect_language(text: str, filename: str = "") -> str:
    """
    Detects language using Unicode script frequencies across all 11 supported Indian languages.
    """
    raw_text = (text or "").strip()
    fn = (filename or "").lower()
    
    char_counts = {}
    total_indic = 0
    for lang, pattern in INDIC_SCRIPT_RANGES.items():
        count = len(re.findall(pattern, raw_text))
        char_counts[lang] = count
        total_indic += count
        
    english_chars = len(re.findall(r'[a-zA-Z]', raw_text))
    total_chars = total_indic + english_chars
    
    if total_chars > 10:
        max_lang = max(char_counts, key=char_counts.get)
        # If at least 15% of parsed characters match a regional script -> classify as that language
        if char_counts[max_lang] > 0 and (char_counts[max_lang] / total_chars) >= 0.15:
            return max_lang
        return "English"
    
    # Fallback to filename keywords if OCR text is empty
    if any(k in fn for k in ["telugu", "adangal", "tel"]):
        return "Telugu"
    elif any(k in fn for k in ["hindi", "khasra", "hin"]):
        return "Hindi"
    elif any(k in fn for k in ["tamil", "patta", "tam"]):
        return "Tamil"
    elif any(k in fn for k in ["kannada", "rtc", "kan"]):
        return "Kannada"
    elif any(k in fn for k in ["malayalam", "mal"]):
        return "Malayalam"
    elif any(k in fn for k in ["marathi", "mar"]):
        return "Marathi"
    elif any(k in fn for k in ["bengali", "ben"]):
        return "Bengali"
    elif any(k in fn for k in ["gujarati", "guj"]):
        return "Gujarati"
    elif any(k in fn for k in ["odia", "ori"]):
        return "Odia"
    elif any(k in fn for k in ["punjabi", "pan"]):
        return "Punjabi"
        
    return "English"

def classify_document(ocr_text: str, filename: str) -> dict:
    """
    Classifies a document by type, language, format, and confidence score.
    """
    text = (ocr_text or "").strip()
    fn = filename.lower()
    
    language = detect_language(text, filename)
    
    # Classify Document Type
    doc_type = "Other"
    type_confidence = 80.0
    lower_text = text.lower()
    
    mutation_keywords = [
        "mutation", "register", "change of hand", "మ్యుటేషన్", "మార్పిడి",
        "नामांतरण", "दाखिल खारिज", "உரிமாற்றம்", "ಮ್ಯುಟೇಶನ್", "নামজারি"
    ]
    survey_keywords = [
        "survey", "fmb", "boundaries", "సర్వే", "కొలత", "నక్షా",
        "सीमांकन", "புல எண்", "ನಕ್ಷೆ", "নকশা"
    ]
    registration_keywords = [
        "registration", "deed", "sale deed", "stamp", "రిజిస్ట్రేషన్",
        "దరఖాస్తు", "पंजीकरण", "बैनामा", "பதிவு", "ನೋಂದಣಿ"
    ]
    pattadar_keywords = [
        "pattadar", "adangal", "pahani", "ror", "khata", "భూమి హక్కు",
        "హక్కు పత్రం", "యజమాని", "పట్టాదారు", "అడంగల్", "ఖాతా", "విస్తీర్ణం",
        "खतौनी", "खातेदार", "பட்டா", "ಪಹಣಿ", "খতিয়ান"
    ]
    cadastral_keywords = [
        "cadastral", "map", "parcel", "plot boundary", "మ్యాప్", "పటం", "नक्शा", "படம்"
    ]
    
    # Check filename first for high confidence classifications
    if any(k in fn for k in ["mutation", "muta", "namantaran"]):
        doc_type = "Mutation Record"
        type_confidence = 95.0
    elif any(k in fn for k in ["survey", "fmb", "measurement"]):
        doc_type = "Survey Record"
        type_confidence = 95.0
    elif any(k in fn for k in ["registration", "deed", "sale", "registry"]):
        doc_type = "Registration Record"
        type_confidence = 95.0
    elif any(k in fn for k in ["adangal", "pahani", "ror", "pattadar", "khasra", "khatauni", "patta"]):
        doc_type = "Pattadar/Land Ownership Record"
        type_confidence = 95.0
    elif any(k in fn for k in ["cadastral", "map", "layout"]):
        doc_type = "Cadastral Map"
        type_confidence = 95.0
    # Search in OCR text
    elif any(k in lower_text for k in mutation_keywords):
        doc_type = "Mutation Record"
        type_confidence = 85.0
    elif any(k in lower_text for k in pattadar_keywords):
        doc_type = "Pattadar/Land Ownership Record"
        type_confidence = 85.0
    elif any(k in lower_text for k in survey_keywords):
        doc_type = "Survey Record"
        type_confidence = 85.0
    elif any(k in lower_text for k in registration_keywords):
        doc_type = "Registration Record"
        type_confidence = 85.0
    elif any(k in lower_text for k in cadastral_keywords):
        doc_type = "Cadastral Map"
        type_confidence = 85.0

    return {
        "doc_type": doc_type,
        "language": language,
        "format_type": "Printed",
        "classification_confidence": type_confidence
    }
