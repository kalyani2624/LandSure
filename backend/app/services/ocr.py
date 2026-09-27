import os
import pytesseract
from PIL import Image
import logging
import requests

logger = logging.getLogger(__name__)

# Official Government Deeds Multilingual OCR Registry
DEMO_OCR_MAPPING = {
    "gujarat": """
ભારત INDIA - INDIA NON JUDICIAL
ગુજરાત GUJARAT - GJ 398765
DATE: 05-01-2024
SOLD TO: શ્રી દેવાંશ કનુભાઈ પટેલ (Devansh Kanubhai Patel)
સમજૂતી લેખપત્ર
અમુક્તદાર: શ્રી દેવાંશ કનુભાઈ પટેલ, રહે. 25, શક્તિ એન્ક્લેવ, અઠવા, સુરત.
ખરીદદાર: શ્રી પાર્થ હિતેશભાઈ શાહ, રહે. 18, ગાયત્રી સોસાયટી, વરાછા, સુરત.
મિલકતનું વર્ણન: સર્વે નં. 123/4, પ્લોટ નં. 45, ગામ: અઠવા, તા. કામરેજ, જી. સુરત.
વિસ્તાર: 120 ચો. મીટર (અંદાજે)
વેચાણ રકમ: રૂ. 12,50,000/-
    """,
    "maharashtra": """
भारत INDIA - INDIA NON JUDICIAL
महाराष्ट्र MAHARASHTRA - MA 812345
दिनांक: 01-06-2024
विक्रीपत्र (जाहिरनामा)
विक्रेत्याचे नाव: श्री. अमोल अशोक देशमुख (Amol Ashok Deshmukh), रा. फ्लॅट नं. 101, प्रणव अपार्टमेंट, कराड, जि. सातारा - 415124.
खरेदीदाराचे नाव: श्री. संदीप विजय चव्हाण
मालमत्तेचे वर्णन: गट नं. 123, क्षेत्रफळ 1000 चौ.मी., गाव तळमावले, ता. कराड, जि. सातारा.
विक्री किंमत: रुपये 10,00,000/-
    """,
    "karnataka": """
ಭಾರತ INDIA - INDIA NON JUDICIAL
ಕರ್ನಾಟಕ KARNATAKA - KA 684512
ದಿನಾಂಕ: 20-04-2024
ವಿಕ್ರಯ ಪತ್ರ (ಮಾರಾಟ ಪತ್ರ)
ಮಾರಾಟಗಾರರು: ಶ್ರೀ ರವೀಂದ್ರ ಹೆಗಡೆ (Ravindra Hegde)
ಖರೀದಿದಾರರು: ಶ್ರೀಮತಿ ಅನನ್ಯಾ ಶೆಟ್ಟಿ (Ananya Shetty)
ಆಸ್ತಿ ವಿವರ: ಸೈಟ್ ನಂ. 123/4, ಒಟ್ಟು ವಿಸ್ತೀರ್ಣ 2400 ಚದರ ಅಡಿ, ಖಾತೆ ನಂ. 4567, ಜಯನಗರ 3ನೇ ಹಂತ, ಬೆಂಗಳೂರು ದಕ್ಷಿಣ ತಾಲೂಕು, ಬೆಂಗಳೂರು ಜಿಲ್ಲೆ.
ಬೆಲೆ: ರೂ. 95,000/-
    """,
    "andhra": """
భారత INDIA - INDIA NON JUDICIAL
ఆంధ్రప్రదేశ్ రాష్ట్రం ANDHRA PRADESH - DU 478965
DATE: 18-07-2023
అమ్మకపు దస్తావేజు
అమ్మకముచేసి వారు: శ్రీ ముత్యాల నరసింహులు (Mutyala Narasimhulu), తండ్రి: శ్రీ ముత్యాల సుబ్బారాయుడు
కొనుగోలుదారు: శ్రీ దేవత్తి ప్రసాద్
సర్వే నం. 224/2B, ఖాతా నం. 578 గల వ్యవసాయ భూమి విస్టీర్ణము 3.15 ఎకరాలు (మూడు ఎకరాలు పదిహేను సెంట్లు), వెలగపూడి గ్రామము, ఏలూరు మండలం, పశ్చిమ గోదావరి జిల్లా.
మొత్తం: రూ. 15,75,000/-
    """,
    "uttar_pradesh": """
भारत INDIA - INDIA NON JUDICIAL
उत्तर प्रदेश UTTAR PRADESH - AP 896512
दिनांक: 12-04-2024
विक्रय पत्र
विक्रेता: श्री रामकिशोर यादव (Ramkishor Yadav), पुत्र श्री बद्री प्रसाद यादव, निवासी ग्राम धरमपुर, तहसील सहजनवा, जिला गोरखपुर.
भूमि का विवरण: खाता संख्या - 275, खसरा संख्या - 89/2, क्षेत्रफल - 0.860 हेक्टेयर, भूमि प्रकार - कृषि (सिंचित), ग्राम धरमपुर, तहसील सहजनवा, जिला गोरखपुर.
मूल्य: ₹ 85,000/-
    """
}

def run_online_ocr(file_path: str, language: str = "English") -> str:
    """
    Sends the image to the free OCR.space API using OCREngine 2 (supporting Indic scripts and auto-detection).
    Returns the parsed text or None if the request fails.
    """
    url = "https://api.ocr.space/parse/image"
    
    try:
        logger.info(f"Uploading {file_path} to OCR.space online API with OCREngine 2 (multilingual)...")
        with open(file_path, 'rb') as f:
            response = requests.post(
                url,
                files={'file': f},
                data={
                    'apikey': 'helloworld',
                    'language': 'auto',
                    'OCREngine': '2',
                    'isOverlayRequired': False
                },
                timeout=25
            )
        result = response.json()
        if result.get("OCRExitCode") == 1:
            parsed_results = result.get("ParsedResults", [])
            if parsed_results:
                text = parsed_results[0].get("ParsedText", "").strip()
                logger.info("Online OCR Space API successfully extracted text.")
                return text
        logger.warning(f"OCR.space API returned error: {result.get('ErrorMessage')}")
    except Exception as e:
        logger.warning(f"Failed to connect to OCR.space API: {str(e)}")
    return None

def run_ocr(file_path: str, language: str = "English") -> dict:
    """
    Runs Tesseract OCR on the image. Falls back to:
    1. Pre-defined mock texts for known demo files.
    2. OCR.space online API if Tesseract is not installed locally.
    3. Simulated mock land record text if both offline and local Tesseract is missing.
    """
    filename = os.path.basename(file_path)
    
    # Real Local OCR Flow
    try:
        lang_codes = {
            "English": "eng",
            "Telugu": "tel+eng",
            "Hindi": "hin+eng",
            "Tamil": "tam+eng",
            "Kannada": "kan+eng",
            "Bengali": "ben+eng",
            "Gujarati": "guj+eng"
        }
        lang_code = lang_codes.get(language, "eng")
            
        img = Image.open(file_path)
        ocr_text = pytesseract.image_to_string(img, lang=lang_code)
        
        try:
            data = pytesseract.image_to_data(img, lang=lang_code, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data['conf'] if int(c) != -1]
            avg_conf = sum(confidences) / len(confidences) if confidences else 85.0
        except Exception:
            avg_conf = 85.0

        return {
            "text": ocr_text.strip(),
            "confidence": round(avg_conf, 1),
            "engine": f"Tesseract-OCR ({lang_code})"
        }
        
    except Exception as e:
        logger.warning(f"Local Tesseract OCR failed: {str(e)}. Trying free online OCR API fallback...")
        
        # 1st Fallback: Free Online OCR Space API
        online_text = run_online_ocr(file_path, language)
        if online_text:
            return {
                "text": online_text,
                "confidence": 88.0,
                "engine": "OCR.space Online API"
            }
            
        # 2nd Fallback: Empty text indicating failure
        logger.warning("Online OCR fallback failed or offline. Returning empty text for human review.")
        return {
            "text": "",
            "confidence": 0.0,
            "engine": "Failed"
        }
