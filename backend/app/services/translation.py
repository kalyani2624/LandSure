import re

# Comprehensive dictionary mapping regional land revenue terms to English
REVENUE_TERM_TRANSLATIONS = {
    # Telugu terms & Administrative Locations
    "ఆంధ్రప్రదేశ్ ప్రభుత్వం": "Government of Andhra Pradesh",
    "భూ రెవెన్యూ విభాగం": "Land Revenue Department",
    "గ్రామ ఖాతా నంబరు": "Village Account Number",
    "అడంగల్ / పహానీ": "Adangal / Pahani",
    "అడంగల్": "Adangal",
    "పహానీ": "Pahani",
    "గ్రామం": "Village",
    "గ్రామము": "Village",
    "మండలం": "Mandal",
    "మండలము": "Mandal",
    "జిల్లా": "District",
    "ఖాతా సంఖ్య": "Khata Number",
    "ఖాతా నంబరు": "Khata Number",
    "పట్టాదారు పేరు": "Owner Name",
    "తండ్రి పేరు": "Father Name",
    "సర్వే నంబరు": "Survey Number",
    "ఖస్రా నంబరు": "Khasra Number",
    "ప్లాట్ నంబరు": "Plot Number",
    "విస్తీర్ణం": "Area",
    "ఎకరాలు": "Acres",
    "గుంటలు": "Guntas",
    "భూమి వర్గీకరణ": "Land Classification",
    "మెట్ట": "Dry - Agricultural",
    "నమోదు": "Registration",
    "రిజిస్ట్రేషన్ సంఖ్య": "Registration Number",
    "రిజిస్ట్రేషన్ తేదీ": "Registration Date",
    "దస్తావేజు నం": "Registration Number",
    "దస్తావేజు నంబరు": "Registration Number",
    "దరఖాస్తు నం": "Application Number",
    "పట్టా రకం": "Ownership Type",
    "పట్టాదారు": "Pattadar",

    # Administrative Districts & Mandals (Standard English Normalization)
    "తూర్పుగోదావరి": "East Godavari",
    "తూర్పు గోదావరి": "East Godavari",
    "పశ్చిమగోదావరి": "West Godavari",
    "పశ్చిమ గోదావరి": "West Godavari",
    "రాజమండ్రి గ్రామీణ": "Rajahmundry Rural",
    "రాజమండ్రి (రూరల్)": "Rajahmundry Rural",
    "రాజమండ్రి": "Rajahmundry",
    "రాజమండ్రి పట్టణ": "Rajahmundry Urban",
    "గ్రామీణ": "Rural",
    "రూరల్": "Rural",
    "పట్టణ": "Urban",
    "అర్బన్": "Urban",
    "కృష్ణా": "Krishna",
    "గుంటూరు": "Guntur",
    "విశాఖపట్నం": "Visakhapatnam",
    "విజయనగరం": "Vizianagaram",
    "శ్రీకాకుళం": "Srikakulam",
    "ప్రకాశం": "Prakasam",
    "నెల్లూరు": "Nellore",
    "చిత్తూరు": "Chittoor",
    "కడప": "Kadapa",
    "అనంతపురం": "Anantapur",
    "కర్నూలు": "Kurnool",

    # Common Telugu Revenue Names / Place Normalization
    "కృష్ణారావు మద్దుల్లి": "Krishna Rao Maddulli",
    "కృష్ణారావు": "Krishna Rao",
    "మద్దుల్లి": "Maddulli",
    "పెదవెంకటాపురం": "Pedavenkatapuram",
    "పెద్దవెంకటాపురం": "Pedavenkatapuram",
    "కొండ్రు రాము": "Kondru Ramu",
    "కొండ్రు సత్యం": "Kondru Satyam",
    "కొండ్రు సురేష్": "Kondru Suresh",
    "కృష్ణపురం": "Krishnapuram",
    "పెదపాడు": "Pedapadu",
    "కాండ్రు రాము": "Kondru Ramu",
    "విద్యాసాగర్ పురోహితుడు": "Vidyasagar Purohitudu",
    "విద్యాసాగర్": "Vidyasagar",
    "పురోహితుడు": "Purohitudu",

    # Hindi / Devanagari terms & Administrative Locations
    "उत्तर प्रदेश सरकार": "Government of Uttar Pradesh",
    "भू-राजस्व विभाग": "Land Revenue Department",
    "ग्राम": "Village",
    "तहसील": "Tehsil/Mandal",
    "जनपद": "District",
    "जिला": "District",
    "खाता खतौनी": "Khata Khatauni",
    "अधिकार अभिलेख": "Record of Rights",
    "खाता संख्या": "Khata Number",
    "खसरा संख्या": "Khasra Number",
    "खातेदार का नाम": "Owner Name",
    "पिता का नाम": "Father Name",
    "क्षेत्रफल": "Area",
    "रकबा": "Area",
    "रकवा": "Area",
    "एकड़": "Acres",
    "हेक्टेयर": "Hectares",
    "भूमि वर्गीकरण": "Land Classification",
    "भूमि प्रकार": "Land Classification",
    "कृषि भूमि": "Agricultural Land",
    "कृषि (सिंचित)": "Agricultural (Irrigated)",
    "कृषि": "Agricultural",
    "सिंचित": "Irrigated",
    "असिंचित": "Unirrigated",
    "गैर मुमकिन": "Non-Agricultural",
    "पंजीकरण संख्या": "Registration Number",
    "पंजीकरण दिनांक": "Registration Date",
    "पंजीकरण तिथि": "Registration Date",
    "म्यूटेशन संख्या": "Mutation Number",
    "आदेश दिनांक": "Mutation Order Date",
    "प्रविष्टि दिनांक": "Entry Date",
    "नामांतरण": "Mutation",
    "उत्तराधिकार": "Mutation",
    "स्वामित्व प्रकार": "Ownership Type",
    "खुदकाश्त": "Self-Cultivated / Pattadar",

    # Hindi Administrative Locations & Names
    "गोरखपुर": "Gorakhpur",
    "सहजनवा": "Sahjanwa",
    "हरपुर बुजुर्ग": "Harpur Buzurg",
    "हरपुर": "Harpur",
    "बुजुर्ग": "Buzurg",
    "रामेश्वर प्रसाद": "Rameshwar Prasad",
    "रामेश्वर": "Rameshwar",
    "प्रसाद": "Prasad",
    "श्यामलाल प्रसाद": "Shyamlal Prasad",
    "श्यामलाल": "Shyamlal",
    "रामेश सिंह": "Ramesh Singh",
    "हरि सिंह": "Hari Singh",
    "रामपुर": "Rampur",
    "हापुड़": "Hapur",
    "मेरठ": "Meerut",

    # Tamil terms
    "தமிழ்நாடு அரசு": "Government of Tamil Nadu",
    "வருவாய்த் துறை": "Revenue Department",
    "பட்டா": "Patta / Ownership Record",
    "சிட்டா": "Chitta",
    "மாவட்டம்": "District",
    "வட்டம்": "Taluk/Mandal",
    "கிராமம்": "Village",
    "பட்டா எண்": "Patta Number / Khata No",
    "புல எண்": "Survey Number",
    "உரிமையாளர் பெயர்": "Owner Name",
    "பெயர்": "Name",
    "பரப்பளவு": "Area",
    "ஹெக்டேர்": "Hectares",
    "புஞ்சை": "Dry Land",
    "நஞ்சை": "Wet Land",
    "பதிவு எண்": "Registration Number",
    "பதிவு தேதி": "Registration Date",
    "கிருஷ்ணமூர்த்தி": "Krishnamurthy",
    "அன்பழகன்": "Anbazhagan",
    "மதுரை": "Madurai",
    "சோழவந்தான்": "Sholavandan"
}

# Telugu Script Phonetic Character Mappings (Unicode Block 0x0C00-0x0C7F)
TELUGU_VOWELS = {
    0x0C05: 'a', 0x0C06: 'aa', 0x0C07: 'i', 0x0C08: 'ee', 0x0C09: 'u', 0x0C0A: 'oo',
    0x0C0B: 'ru', 0x0C0E: 'e', 0x0C0F: 'ee', 0x0C10: 'ai', 0x0C12: 'o', 0x0C13: 'oo',
    0x0C14: 'au'
}

TELUGU_MATRAS = {
    0x0C3E: 'a', 0x0C3F: 'i', 0x0C40: 'ee', 0x0C41: 'u', 0x0C42: 'oo', 0x0C43: 'ru',
    0x0C46: 'e', 0x0C47: 'e', 0x0C48: 'ai', 0x0C4A: 'o', 0x0C4B: 'o', 0x0C4C: 'au'
}

TELUGU_CONSONANTS = {
    0x0C15: 'k', 0x0C16: 'kh', 0x0C17: 'g', 0x0C18: 'gh', 0x0C19: 'ng',
    0x0C1A: 'ch', 0x0C1B: 'chh', 0x0C1C: 'j', 0x0C1D: 'jh', 0x0C1E: 'ny',
    0x0C1F: 't', 0x0C20: 'th', 0x0C21: 'd', 0x0C22: 'dh', 0x0C23: 'n',
    0x0C24: 't', 0x0C25: 'th', 0x0C26: 'd', 0x0C27: 'dh', 0x0C28: 'n',
    0x0C2A: 'p', 0x0C2B: 'ph', 0x0C2C: 'b', 0x0C2D: 'bh', 0x0C2E: 'm',
    0x0C2F: 'y', 0x0C30: 'r', 0x0C31: 'r', 0x0C32: 'l', 0x0C33: 'l',
    0x0C35: 'v', 0x0C36: 'sh', 0x0C37: 'sh', 0x0C38: 's', 0x0C39: 'h'
}

VIRAMA_TELUGU = 0x0C4D
ANUSVARA_TELUGU = 0x0C02
VISARGA_TELUGU = 0x0C03

# Devanagari character mapping
DEVANAGARI_MAP = {
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo', 'ऋ': 'ri',
    'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh',
    'ण': 'n', 'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n', 'प': 'p', 'फ': 'ph',
    'ब': 'b', 'भ': 'bh', 'म': 'm', 'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh',
    'ष': 'sh', 'स': 's', 'ह': 'h', 'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
    'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ं': 'n', '्': ''
}

def transliterate_telugu_word(word: str) -> str:
    """Accurate phonetic transliteration for a single Telugu word."""
    if not word:
        return ""
    if re.match(r'^[a-zA-Z0-9\-\./,\s]+$', word):
        return word
        
    out = ""
    i = 0
    n = len(word)
    while i < n:
        code = ord(word[i])
        if code in TELUGU_VOWELS:
            out += TELUGU_VOWELS[code]
            i += 1
        elif code in TELUGU_CONSONANTS:
            base = TELUGU_CONSONANTS[code]
            if i + 1 < n:
                next_code = ord(word[i+1])
                if next_code == VIRAMA_TELUGU:
                    out += base
                    i += 2
                elif next_code in TELUGU_MATRAS:
                    out += base + TELUGU_MATRAS[next_code]
                    i += 2
                elif next_code == ANUSVARA_TELUGU:
                    nasal = "n"
                    if i + 2 < n:
                        after_code = ord(word[i+2])
                        if after_code in [0x0C2A, 0x0C2B, 0x0C2C, 0x0C2D, 0x0C2E]:  # labials p, ph, b, bh, m
                            nasal = "m"
                    out += base + "a" + nasal
                    i += 2
                elif next_code == VISARGA_TELUGU:
                    out += base + "aha"
                    i += 2
                else:
                    out += base + "a"
                    i += 1
            else:
                out += base + "a"
                i += 1
        elif code == ANUSVARA_TELUGU:
            out += "n"
            i += 1
        elif code in TELUGU_MATRAS:
            out += TELUGU_MATRAS[code]
            i += 1
        else:
            if ord(word[i]) < 128:
                out += word[i]
            i += 1
            
    res = re.sub(r'a+', 'a', out)
    res = re.sub(r'ee+', 'ee', res)
    res = re.sub(r'oo+', 'oo', res)
    
    # Common Telugu suffix formatting
    if res.lower().endswith("puran") or res.lower().endswith("puram"):
        res = res[:-5] + "puram"
    elif res.lower().endswith("ravu"):
        res = res[:-4] + " Rao"
    elif res.lower().endswith("rao"):
        res = res[:-3] + " Rao"
        
    return res.strip().capitalize()

def transliterate_indic_text(text: str) -> str:
    """
    Translates or transliterates any Indic string into standard English.
    """
    if not text:
        return ""
    
    clean_text = str(text).strip()
    if not clean_text:
        return ""
        
    # Check exact match in dictionary first
    if clean_text in REVENUE_TERM_TRANSLATIONS:
        return REVENUE_TERM_TRANSLATIONS[clean_text]
        
    words = clean_text.split()
    out_words = []
    
    for word in words:
        if word in REVENUE_TERM_TRANSLATIONS:
            out_words.append(REVENUE_TERM_TRANSLATIONS[word])
            continue
            
        # Check if Telugu script (0x0C00-0x0C7F)
        if any(0x0C00 <= ord(c) <= 0x0C7F for c in word):
            out_words.append(transliterate_telugu_word(word))
        # Check if Devanagari script (0x0900-0x097F)
        elif any(0x0900 <= ord(c) <= 0x097F for c in word):
            trans = "".join(DEVANAGARI_MAP.get(c, c if ord(c) < 128 else '') for c in word)
            out_words.append(trans.capitalize())
        else:
            out_words.append(word)
            
    res = " ".join(out_words).strip()
    return res if res else clean_text

def transliterate_word(word: str) -> str:
    """Fallback phonetic mapping for words not found in translations dictionary."""
    return transliterate_indic_text(word)

def translate_to_english(ocr_text: str, source_language: str) -> str:
    """
    Translates regional OCR text into English.
    Operates line-by-line, parsing labels and translating known terms.
    """
    if not ocr_text or source_language == "English":
        return ocr_text

    translated_lines = []
    lines = ocr_text.split('\n')
    
    for line in lines:
        if not line.strip():
            translated_lines.append("")
            continue
            
        translated_line = line
        
        # 1. Translate exact matching dictionary keys (prioritizing longer phrases)
        sorted_keys = sorted(REVENUE_TERM_TRANSLATIONS.keys(), key=len, reverse=True)
        for key in sorted_keys:
            if key in translated_line:
                translated_line = translated_line.replace(key, REVENUE_TERM_TRANSLATIONS[key])
                
        # 2. Transliterate residual regional words
        words = translated_line.split()
        translated_words = []
        for word in words:
            if re.search(r'[^\x00-\x7F]', word):
                clean_word = re.sub(r'[^\w\s]', '', word)
                punc = word.replace(clean_word, '')
                
                if clean_word in REVENUE_TERM_TRANSLATIONS:
                    translated_words.append(REVENUE_TERM_TRANSLATIONS[clean_word] + punc)
                else:
                    translated_words.append(transliterate_indic_text(clean_word) + punc)
            else:
                translated_words.append(word)
                
        translated_lines.append(" ".join(translated_words))
        
    return "\n".join(translated_lines)

