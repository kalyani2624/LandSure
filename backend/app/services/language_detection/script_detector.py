import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

UNICODE_SCRIPT_RANGES = {
    "Telugu": (0x0C00, 0x0C7F),
    "Hindi": (0x0900, 0x097F),      # Devanagari (Hindi, Marathi)
    "Tamil": (0x0B80, 0x0BFF),
    "Kannada": (0x0C80, 0x0CFF),
    "Malayalam": (0x0D00, 0x0D7F),
    "Bengali": (0x0980, 0x09FF),
    "Gujarati": (0x0A80, 0x0AFF),
    "Odia": (0x0B00, 0x0B7F),
    "Punjabi": (0x0A00, 0x0A7F),     # Gurmukhi
}

def detect_language(ocr_text: str, filename: str = "") -> str:
    """
    Identifies the language/script across 11 official Indian languages.
    Uses character frequency distributions across Unicode script blocks.
    """
    text = (ocr_text or "").strip()
    if not text:
        fn = filename.lower()
        for lang in UNICODE_SCRIPT_RANGES.keys():
            if lang.lower() in fn:
                return lang
        return "English"

    counts = {lang: 0 for lang in UNICODE_SCRIPT_RANGES.keys()}
    latin_count = 0

    for char in text:
        code = ord(char)
        if 0x0041 <= code <= 0x005A or 0x0061 <= code <= 0x007A:
            latin_count += 1
            continue

        for lang, (start, end) in UNICODE_SCRIPT_RANGES.items():
            if start <= code <= end:
                counts[lang] += 1
                break

    # Find dominant Indic script
    max_lang, max_count = max(counts.items(), key=lambda x: x[1])

    # If Indic characters represent > 8% of alphabet characters, classify as that Indic language
    if max_count > 3 and max_count >= (latin_count * 0.08):
        # Distinguish Marathi from Hindi in Devanagari if specific Marathi words appear
        if max_lang == "Hindi":
            marathi_keywords = ["नाव", "क्षेत्र", "गावाचे", "क्रमांक", "जमीन", "सातबारा"]
            if any(k in text for k in marathi_keywords):
                return "Marathi"
        return max_lang

    # Check for regional cadastral keywords in mixed text
    text_lower = text.lower()
    telugu_cadastral_markers = [
        "rajahmundry", "godavari", "andhra", "adangal", "pahani", "pattadar", "krishnapuram",
        "pedavenkatapuram", "pedapadu", "e.g.dt", "w.g.dt"
    ]
    if any(k in text_lower for k in telugu_cadastral_markers):
        return "Telugu"

    return "English"

detect_script = detect_language
