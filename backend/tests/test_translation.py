from app.services.translation import translate_to_english

def test_telugu_translation():
    """Verify that Telugu land terms are translated to English."""
    telugu_text = "పట్టాదారు పేరు: కొండ్రు రాము\nసర్వే నంబరు: 145/3A\nవిస్తీర్ణం: 2.50 ఎకరాలు"
    translated = translate_to_english(telugu_text, "Telugu")
    
    assert "Owner Name" in translated
    assert "Kondru Ramu" in translated
    assert "Survey Number" in translated
    assert "Area" in translated
    assert "Acres" in translated

def test_hindi_translation():
    """Verify that Hindi/Devanagari land terms are translated to English."""
    hindi_text = "खातेदार का नाम: रामेश सिंह\nखसरा संख्या: 145/3A\nक्षेत्रफल: 2.50 एकड़"
    translated = translate_to_english(hindi_text, "Hindi")
    
    assert "Owner Name" in translated
    assert "Ramesh Singh" in translated
    assert "Khasra Number" in translated
    assert "Area" in translated
    assert "Acres" in translated

def test_tamil_translation():
    """Verify that Tamil land terms are translated to English."""
    tamil_text = "உரிமையாளர் பெயர்: கிருஷ்ணமூர்த்தி\nபுல எண்: 145/3A\nபரப்பளவு: 2.50 ஹெக்டேர்"
    translated = translate_to_english(tamil_text, "Tamil")
    
    assert "Owner Name" in translated
    assert "Krishnamurthy" in translated
    assert "Survey Number" in translated
    assert "Area" in translated
    assert "Hectares" in translated

def test_english_remains_unchanged():
    """Verify that English text passes through the translation layer unmodified."""
    english_text = "Owner Name: Kondru Ramu\nSurvey Number: 145/3A"
    translated = translate_to_english(english_text, "English")
    
    assert translated == english_text
