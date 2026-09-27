import os
import shutil
from PIL import Image, ImageDraw, ImageFont

def draw_document(filename, title, details, bg_color=(250, 245, 235), text_color=(30, 41, 59), language="English"):
    """
    Draw a mock government land record document with borders, headers, seals, and table grids.
    """
    # Standard letter size proportions
    img = Image.new('RGB', (800, 1050), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # 1. Outer Border
    draw.rectangle([(20, 20), (780, 1030)], outline=text_color, width=3)
    draw.rectangle([(25, 25), (775, 1025)], outline=text_color, width=1)
    
    # 2. Header Emblem Seal drawing (simple shape representation)
    draw.ellipse([(360, 40), (440, 120)], outline=text_color, width=2)
    draw.polygon([(380, 90), (420, 90), (400, 60)], outline=text_color, fill=text_color)
    draw.line([(360, 130), (440, 130)], fill=text_color, width=1)
    
    # 3. Write Headers
    y = 150
    # Use default font since custom TTF might not exist
    try:
      font_title = ImageFont.load_default()
    except Exception:
      font_title = None

    # Drawn representations
    draw.text((400, y), "GOVERNMENT LAND REVENUE DEPARTMENT", fill=text_color, anchor="ms")
    y += 24
    draw.text((400, y), title.upper(), fill=text_color, anchor="ms")
    y += 30
    
    # Divider line
    draw.line([(50, y), (750, y)], fill=text_color, width=2)
    y += 30
    
    # 4. Draw Details as a tabular grid
    for idx, (label, val) in enumerate(details):
        # Draw row box
        row_y = y + (idx * 45)
        draw.rectangle([(50, row_y), (750, row_y + 40)], outline=(203, 213, 225), width=1)
        # Vertical divider
        draw.line([(280, row_y), (280, row_y + 40)], fill=(203, 213, 225), width=1)
        
        # Text positioning
        draw.text((65, row_y + 20), label, fill=text_color, anchor="lm")
        draw.text((295, row_y + 20), val, fill=text_color, anchor="lm")
        
    # Draw Footer
    draw.line([(50, 950), (750, 950)], fill=text_color, width=1)
    draw.text((400, 980), "This is an official digitization sample for SIH 2026 Evaluation.", fill=(100, 116, 139), anchor="ms")
    draw.text((400, 1000), f"Document ID: {filename.split('.')[0].upper()}", fill=(100, 116, 139), anchor="ms")
    
    # Save Image
    os.makedirs("sample_documents", exist_ok=True)
    target_path = os.path.join("sample_documents", filename)
    img.save(target_path)
    print(f"Generated sample: {target_path}")
    
    # Also save to uploads and preprocessed directories for direct database matching
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("preprocessed", exist_ok=True)
    
    shutil.copy(target_path, os.path.join("uploads", filename))
    
    # Create preprocessed version (grayscale/binarized copy)
    gray_img = img.convert('L')
    binarized_img = gray_img.point(lambda x: 0 if x < 200 else 255, '1')
    binarized_img.save(os.path.join("preprocessed", f"preprocessed_{filename.split('.')[0]}.png"))

def main():
    print("Generating demo land record documents...")
    
    # 1. English Survey Record
    draw_document(
        filename="english_survey_sample.png",
        title="Form I-B - Record of Rights",
        details=[
            ("District", "West Godavari"),
            ("Tehsil / Mandal", "Pedapadu"),
            ("Village", "Krishnapuram"),
            ("Survey Number", "145/3A"),
            ("Khasra Number", "KH/99201"),
            ("Khata Number", "412"),
            ("Plot Number", "12"),
            ("Area / Extent", "2.50 Acres"),
            ("Land Classification", "Dry - Agricultural"),
            ("Ownership Type", "Pattadar"),
            ("Owner Name", "Kondru Ramu"),
            ("Registration Number", "2401/2024"),
            ("Registration Date", "12-04-2024")
        ]
    )

    # 2. Telugu Adangal
    draw_document(
        filename="telugu_adangal_sample.jpg",
        title="Grama Adangal (Village Account 3)",
        details=[
            ("జిల్లా (District)", "పశ్చిమ గోదావరి (West Godavari)"),
            ("మండలం (Mandal)", "పెదపాడు (Pedapadu)"),
            ("గ్రామం (Village)", "కృష్ణపురం (Krishnapuram)"),
            ("ఖాతా నంబరు (Khata No)", "412"),
            ("పట్టాదారు పేరు (Owner)", "కొండ్రు రాము (Kondru Ramu)"),
            ("సర్వే నంబరు (Survey No)", "145/3A"),
            ("విస్తీర్ణం (Area)", "2.50 ఎకరాలు (Acres)"),
            ("భూమి వర్గీకరణ (Class)", "మెట్ట (Dry - Agricultural)"),
            ("పట్టా రకం (Type)", "పట్టాదారు (Pattadar)"),
            ("రిజిస్ట్రేషన్ సంఖ్య", "2401/2024"),
            ("రిజిస్ట్రేషన్ తేదీ", "12-04-2024")
        ],
        bg_color=(255, 252, 240)
    )

    # 3. Mutation Record
    draw_document(
        filename="mutation_record_sample.png",
        title="Form VIII - Mutation Register",
        details=[
            ("Mandal Office", "Pedapadu"),
            ("Village Locality", "Krishnapuram"),
            ("Mutation Number", "MUT/2025/892"),
            ("Survey Number", "145/3A"),
            ("Khata Number", "412"),
            ("Area Affected", "2.50 Acres"),
            ("Transferor (Old)", "Kondru Ramu"),
            ("Transferee (New)", "Kondru Suresh"),
            ("Reason for Mutation", "Registered Sale Deed"),
            ("Registration Number", "4821/2025"),
            ("Registration Date", "15-08-2025"),
            ("Mutation Order Date", "20-08-2025")
        ]
    )

    # 4. Conflict Owner Record
    draw_document(
        filename="conflict_owner_sample.png",
        title="Form I-B - Record of Rights (Pattadar Book)",
        details=[
            ("District Name", "West Godavari"),
            ("Mandal Name", "Pedapadu"),
            ("Village Name", "Krishnapuram"),
            ("Survey Number", "145/3A"),
            ("Khata Number", "412"),
            ("Plot Number", "12"),
            ("Registered Area", "2.50 Acres"),
            ("Land Classification", "Dry - Agricultural"),
            ("Ownership Type", "Pattadar"),
            ("Owner Name", "Bandi Ramesh"), # Conflict
            ("Registration Number", "9912/2023"),
            ("Registration Date", "10-09-2023")
        ]
    )

    # 5. Area Mismatch Record
    draw_document(
        filename="area_mismatch_sample.png",
        title="Survey Boundary Measurement Sheet",
        details=[
            ("Survey Office", "Pedapadu Mandal"),
            ("Village Sector", "Krishnapuram Block 4"),
            ("Survey Number", "145/3A"),
            ("Total Measured Area", "3.10 Acres"), # Mismatch
            ("Owner Name", "Kondru Ramu"),
            ("Measurement Date", "18-09-2025"),
            ("Inspecting Surveyor", "R. Prabhakar Rao")
        ]
    )

    # 6. Telugu Handwritten Register (simulated visually with slightly distinct layout)
    draw_document(
        filename="Telugu_Handwritten_Register.png",
        title="Village Account No. 3 - Adangal (Handwritten Register)",
        details=[
            ("Village", "Krishnapuram"),
            ("Mandal", "Pedapadu"),
            ("District", "West Godavari"),
            ("Survey No", "145/3A"),
            ("Pattadar Owner", "కాండ్రు రాము (Kondru Ramu)"),
            ("Extent / Area", "2.50 Acres"),
            ("Assessed Tax", "Rs. 15.00"),
            ("Remarks", "Written in legacy register. Text legibility is low.")
        ],
        bg_color=(245, 235, 220), # parchment style
        text_color=(10, 15, 30)
    )

    # 7. Hindi Khasra
    draw_document(
        filename="hindi_khasra_sample.png",
        title="Form - Khata Khatauni / Record of Rights",
        details=[
            ("ग्राम (Village)", "रामपुर (Rampur)"),
            ("तहसील (Tehsil)", "हापुड़ (Hapur)"),
            ("जनपद (District)", "मेरठ (Meerut)"),
            ("खाता संख्या (Khata No)", "882"),
            ("खसरा संख्या (Survey No)", "145/3A"),
            ("खातेदार का नाम (Owner)", "रामेश सिंह (Ramesh Singh)"),
            ("पिता का नाम (Father Name)", "हरि सिंह"),
            ("क्षेत्रफल (Area)", "2.50 एकड़ (Acres)"),
            ("भूमि वर्गीकरण (Class)", "कृषि भूमि (Agricultural Land)"),
            ("स्वामित्व प्रकार (Type)", "खुदकाश्त (Self-Cultivated)"),
            ("पंजीकरण संख्या", "4012/2024"),
            ("पंजीकरण दिनांक", "12-04-2024")
        ],
        bg_color=(254, 250, 230),
        text_color=(15, 23, 42)
    )

    # 8. Tamil Patta
    draw_document(
        filename="tamil_patta_sample.jpg",
        title="Patta Chitta Copy",
        details=[
            ("மாவட்டம் (District)", "மதுரை (Madurai)"),
            ("வட்டம் (Taluk)", "சோழவந்தான் (Sholavandan)"),
            ("கிராமம் (Village)", "சோழவந்தான் (Sholavandan)"),
            ("பட்டா எண் (Patta No)", "412"),
            ("உரிமையாளர் பெயர் (Owner)", "கிருஷ்ணமூர்த்தி (Krishnamurthy)"),
            ("புல எண் (Survey No)", "145/3A"),
            ("பரப்பளவு (Area)", "2.50 ஹெக்டேர் (Hectares)"),
            ("நில வகைப்பாடு (Class)", "நஞ்சை (Wet Land)"),
            ("பதிவு எண்", "9122/2023"),
            ("பதிவு தேதி", "10-09-2023")
        ],
        bg_color=(250, 252, 245),
        text_color=(20, 30, 10)
    )

    print("All sample documents successfully drawn!")

if __name__ == "__main__":
    main()
