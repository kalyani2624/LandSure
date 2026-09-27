import os
import sys
from typing import Dict, Any

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

PROTOTYPE_GROUND_TRUTH = {
    "telugu_land_record_sample_1": {
        "category": "Telugu Handwritten Land Record",
        "document_id": 82,
        "fields": {
            "owner_name": "K. Rama",
            "father_name": "A. Venkateswara Rao",
            "village": "Gajwel",
            "tehsil_mandal": "Gajwel",
            "district": "Kurnool",
            "survey_number": "78/1",
            "khata_number": "198",
            "area": 1.75,
            "area_unit": "Acres",
            "registration_number": "553/2021",
            "registration_date": "2021-03-05"
        }
    },
    "telugu_mutation_record_sample_2": {
        "category": "Telugu Handwritten Mutation Record",
        "document_id": 78,
        "fields": {
            "survey_number": "145/3A",
            "khata_number": "412",
            "area": 2.5,
            "area_unit": "Acres",
            "mutation_number": "MUT/2025/892",
            "registration_number": "4821/2025",
            "registration_date": "2025-08-15"
        }
    },
    "hindi_handwritten_record_sample_3": {
        "category": "Hindi Handwritten Land Record",
        "document_id": 81,
        "fields": {
            "owner_name": "Lalbahadur Yadav",
            "father_name": "Kuldeep Yadav",
            "village": "Chak Mohammadpur",
            "district": "Gorakhpur",
            "khasra_number": "112/1",
            "khata_number": "334",
            "area": 1.25,
            "area_unit": "Acres",
            "registration_number": "6612/2024",
            "registration_date": "2024-11-03"
        }
    },
    "english_printed_record_sample_4": {
        "category": "English Printed Land Record",
        "document_id": 1,
        "fields": {
            "owner_name": "Kondru Ramu",
            "village": "Krishnapuram",
            "tehsil_mandal": "Pedapadu",
            "district": "West Godavari",
            "survey_number": "145/3A",
            "khata_number": "412",
            "area": 2.5,
            "area_unit": "Acres",
            "registration_number": "9912/2023",
            "registration_date": "2023-09-10"
        }
    }
}

def evaluate_extraction(ai_extracted: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    gt_fields = ground_truth.get("fields", {})
    total_fields = len(gt_fields)
    matches = 0
    missing = 0
    mismatches = 0
    details = []

    for field_name, expected_val in gt_fields.items():
        actual_val = ai_extracted.get(field_name)
        if actual_val is None:
            missing += 1
            details.append((field_name, expected_val, None, "MISSING"))
        else:
            exp_str = str(expected_val).strip().lower()
            act_str = str(actual_val).strip().lower()
            if exp_str == act_str:
                matches += 1
                details.append((field_name, expected_val, actual_val, "MATCH"))
            else:
                mismatches += 1
                details.append((field_name, expected_val, actual_val, "MISMATCH"))

    accuracy = round((matches / total_fields) * 100, 1) if total_fields else 100.0
    return {
        "total_fields": total_fields,
        "matches": matches,
        "missing": missing,
        "mismatches": mismatches,
        "accuracy_pct": accuracy,
        "details": details
    }

if __name__ == "__main__":
    print("==================================================")
    print("HACKATHON PROTOTYPE BENCHMARK EVALUATION")
    print("==================================================")
    
    try:
        from app.database.session import SessionLocal
        from app.models.land_records import LandRecord
        db = SessionLocal()
        
        total_eval_fields = 0
        total_matches = 0
        total_missing = 0
        total_mismatches = 0
        
        for doc_key, doc_info in PROTOTYPE_GROUND_TRUTH.items():
            doc_id = doc_info.get("document_id")
            lr = db.query(LandRecord).filter(LandRecord.document_id == doc_id).first()
            if lr:
                extracted = {
                    "owner_name": lr.owner_name,
                    "father_name": getattr(lr, "father_name", None),
                    "village": lr.village,
                    "tehsil_mandal": lr.tehsil_mandal,
                    "district": lr.district,
                    "survey_number": lr.survey_number,
                    "khasra_number": lr.khasra_number,
                    "khata_number": lr.khata_number,
                    "area": lr.area,
                    "area_unit": lr.area_unit,
                    "registration_number": lr.registration_number,
                    "registration_date": lr.registration_date,
                    "mutation_number": getattr(lr, "mutation_number", None)
                }
                res = evaluate_extraction(extracted, doc_info)
                total_eval_fields += res["total_fields"]
                total_matches += res["matches"]
                total_missing += res["missing"]
                total_mismatches += res["mismatches"]
                
                print(f"\nDocument: {doc_info['category']} (Doc #{doc_id})")
                print(f"  Accuracy: {res['accuracy_pct']}% ({res['matches']}/{res['total_fields']} fields matched)")
                for f, exp, act, status in res["details"]:
                    status_badge = "OK" if status == "MATCH" else status
                    print(f"    - {f:20s}: expected='{str(exp):15s}' | actual='{str(act):15s}' [{status_badge}]")
            else:
                print(f"\nDocument: {doc_info['category']} (Doc #{doc_id}) -> Staged Record not found in DB")
        
        overall_acc = round((total_matches / max(total_eval_fields, 1)) * 100, 1)
        print("\n==================================================")
        print(f"OVERALL PROTOTYPE ACCURACY: {overall_acc}% ({total_matches}/{total_eval_fields} fields matched)")
        print(f"Missing Fields: {total_missing} | Mismatched Fields: {total_mismatches}")
        print("==================================================")
        db.close()
    except Exception as e:
        print(f"Database evaluation error: {e}")
