import re
from datetime import datetime
from typing import Optional, Dict, Any

MONTH_NAME_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12
}

def normalize_date(raw_date: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Normalizes diverse Indian date representations into ISO-8601 YYYY-MM-DD while preserving original.
    Supports:
    - 15/06/2022 -> 2022-06-15
    - 15-06-2022 -> 2022-06-15
    - 15.06.2022 -> 2022-06-15
    - 2022-06-15 -> 2022-06-15
    - 15 June 2022 -> 2022-06-15
    """
    if not raw_date:
        return None
        
    s = str(raw_date).strip()
    s = re.sub(r'[^\d\w\s/\-\.]', '', s).strip()
    
    # 1. Standard numeric formats (DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY)
    dmy_match = re.match(r'^(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})$', s)
    if dmy_match:
        day, month, year = int(dmy_match.group(1)), int(dmy_match.group(2)), int(dmy_match.group(3))
        if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2099:
            return {
                "original": s,
                "normalized": f"{year:04d}-{month:02d}-{day:02d}"
            }

    # 2. ISO format YYYY-MM-DD
    iso_match = re.match(r'^(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})$', s)
    if iso_match:
        year, month, day = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
        if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2099:
            return {
                "original": s,
                "normalized": f"{year:04d}-{month:02d}-{day:02d}"
            }

    # 3. Compact 8-digit string e.g. 15062022
    compact_match = re.match(r'^(\d{2})(\d{2})(\d{4})$', s)
    if compact_match:
        day, month, year = int(compact_match.group(1)), int(compact_match.group(2)), int(compact_match.group(3))
        if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2099:
            return {
                "original": s,
                "normalized": f"{year:04d}-{month:02d}-{day:02d}"
            }

    # 4. Textual month format e.g. 15 June 2022 or 15-Jun-2022
    text_match = re.match(r'^(\d{1,2})[\s\-\.]*([A-Za-z]+)[\s\-\.]*(\d{4})$', s)
    if text_match:
        day = int(text_match.group(1))
        m_str = text_match.group(2).lower()
        year = int(text_match.group(3))
        if m_str in MONTH_NAME_MAP and 1 <= day <= 31 and 1900 <= year <= 2099:
            month = MONTH_NAME_MAP[m_str]
            return {
                "original": s,
                "normalized": f"{year:04d}-{month:02d}-{day:02d}"
            }

    return {
        "original": s,
        "normalized": s
    }
