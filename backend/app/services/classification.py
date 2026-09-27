import re

def classify_document(ocr_text: str, filename: str) -> dict:
    """
    Classifies a document based on text content and filename heuristics.
    Supports English, Telugu, Hindi, Tamil, Kannada, Bengali, and Gujarati.
    Returns:
        {
            "doc_type": str,
            "language": str,
            "format_type": str,
            "confidence_score": float
        }
    """
    text = (ocr_text or "").strip()
    fn = filename.lower()
    
    # 1. Detect Language using Unicode character ranges
    telugu_chars = len(re.findall(r'[\u0c00-\u0c7f]', text))
    hindi_chars = len(re.findall(r'[\u0900-\u097f]', text))
    tamil_chars = len(re.findall(r'[\u0b80-\u0bff]', text))
    kannada_chars = len(re.findall(r'[\u0c80-\u0cff]', text))
    bengali_chars = len(re.findall(r'[\u0980-\u09ff]', text))
    gujarati_chars = len(re.findall(r'[\u0a80-\u0aff]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    total_regional_chars = telugu_chars + hindi_chars + tamil_chars + kannada_chars + bengali_chars + gujarati_chars
    total_chars = total_regional_chars + english_chars
    
    if total_chars > 10:
        counts = {
            "Telugu": telugu_chars,
            "Hindi": hindi_chars,
            "Tamil": tamil_chars,
            "Kannada": kannada_chars,
            "Bengali": bengali_chars,
            "Gujarati": gujarati_chars
        }
        max_lang = max(counts, key=counts.get)
        
        # If at least 15% of parsed text belongs to a regional script, classify as that language
        if counts[max_lang] > 0 and (counts[max_lang] / total_chars) > 0.15:
            language = max_lang
        else:
            language = "English"
    else:
        # Fallback to filename keywords
        if "telugu" in fn or "adangal" in fn or "tel" in fn:
            language = "Telugu"
        elif "hindi" in fn or "khasra" in fn or "hin" in fn:
            language = "Hindi"
        elif "tamil" in fn or "patta" in fn or "tam" in fn:
            language = "Tamil"
        elif "kannada" in fn or "rtc" in fn or "kan" in fn:
            language = "Kannada"
        else:
            language = "English"

    # 2. Detect Document Type
    doc_type = "Other"
    type_confidence = 80.0
    lower_text = text.lower()
    
    mutation_keywords = ["mutation", "register", "change of hand", "మ్యుటేషన్", "మార్పిడి", "नामांतरण", "दाखिल खारिज", "உரிமாற்றம்"]
    survey_keywords = ["survey", "fmb", "boundaries", "సర్వే", "కొలత", "నక్షా", "सीमांकन", "புல எண்"]
    registration_keywords = ["registration", "deed", "sale deed", "stamp", "రిజిస్ట్రేషన్", "దరఖాస్తు", "పंजीకరణ", "बैनामा", "பதிவு"]
    pattadar_keywords = ["pattadar", "adangal", "pahani", "ror", "khata", "భూమి హక్కు", "హక్కు పత్రం", "యజమాని", "పట్టాదారు", "అడంగల్", "ఖాతా", "విస్తీర్ణం", "खतौनी", "खातेदार", "பட்டா"]
    cadastral_keywords = ["cadastral", "map", "parcel", "plot boundary", "మ్యాప్", "నక్షా", "படம்"]
    
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

    # 3. Detect Printed vs Handwritten
    format_type = "Printed"
    if any(k in fn for k in ["handwritten", "hand", "legacy", "register", "old", "Telugu_Handwritten"]):
        format_type = "Handwritten"
    elif "mixed" in fn:
        format_type = "Mixed"
    elif len(text) > 0 and len(re.findall(r'[0-9]', text)) / len(text) < 0.05:
        format_type = "Handwritten"

    return {
        "doc_type": doc_type,
        "language": language,
        "format_type": format_type,
        "confidence": type_confidence
    }
