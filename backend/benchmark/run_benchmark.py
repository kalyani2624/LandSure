import os
import sys
import time
import json
import psutil
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')

from app.services.ocr import run_ocr
from app.services.handwriting.format_classifier import classify_document_format
from app.services.language_detection.script_detector import detect_language
from app.services.ai_router.vlm_understanding import VLMDocumentUnderstandingAdapter, CANONICAL_19_FIELDS

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def calculate_cer_wer(reference: str, hypothesis: str) -> tuple:
    """Computes Character Error Rate and Word Error Rate."""
    ref_chars = list(reference.replace(" ", ""))
    hyp_chars = list(hypothesis.replace(" ", ""))
    if not ref_chars:
        return 0.0, 0.0
    char_dist = levenshtein_distance("".join(ref_chars), "".join(hyp_chars))
    cer = min(char_dist / max(len(ref_chars), 1), 1.0)

    ref_words = reference.split()
    hyp_words = hypothesis.split()
    if not ref_words:
        return cer, 0.0
    word_dist = levenshtein_distance(" ".join(ref_words), " ".join(hyp_words))
    wer = min(word_dist / max(len(ref_words), 1), 1.0)
    return round(cer * 100.0, 2), round(wer * 100.0, 2)

GROUND_TRUTH = {
    "english_survey_sample.png": {
        "language": "English",
        "doc_type": "Survey Record",
        "format_type": "PRINTED",
        "fields": {
            "owner_name": "Kondru Ramu",
            "survey_number": "145/3A",
            "khasra_number": "KH/99201",
            "khata_number": "412",
            "plot_number": "12",
            "area": 2.50,
            "area_unit": "Acres",
            "village": "Krishnapuram",
            "tehsil_mandal": "Pedapadu",
            "district": "West Godavari",
            "land_classification": "Dry - Agricultural",
            "registration_number": "2401/2024",
            "registration_date": "2024-04-12"
        },
        "reference_text": "GOVERNMENT LAND REVENUE DEPARTMENT FORM I-B RECORD OF RIGHTS District West Godavari Tehsil Mandal Pedapadu Village Krishnapuram Survey Number 145/3A Khasra Number KH/99201 Khata Number 412 Plot Number 12 Area Extent 2.50 Acres Land Classification Dry - Agricultural Ownership Type Pattadar Owner Name Kondru Ramu Registration Number 2401/2024 Registration Date 12-04-2024"
    },
    "telugu_adangal_sample.jpg": {
        "language": "Telugu",
        "doc_type": "Pattadar/Land Ownership Record",
        "format_type": "PRINTED",
        "fields": {
            "owner_name": "Kondru Ramu",
            "survey_number": "145/3A",
            "khata_number": "412",
            "area": 2.50,
            "area_unit": "Acres",
            "village": "Krishnapuram",
            "tehsil_mandal": "Pedapadu",
            "district": "West Godavari",
            "registration_number": "2401/2024",
            "registration_date": "2024-04-12"
        },
        "reference_text": "GOVERNMENT LAND REVENUE DEPARTMENT GRAMA ADANGAL District West Godavari Mandal Pedapadu Village Krishnapuram Khata No 412 Owner Kondru Ramu Survey No 145/3A Area 2.50 Acres Dry-Agricultural Pattadar 2401/2024 12-04-2024"
    },
    "hindi_khasra_sample.png": {
        "language": "Hindi",
        "doc_type": "Pattadar/Land Ownership Record",
        "format_type": "PRINTED",
        "fields": {
            "owner_name": "Ramesh Singh",
            "survey_number": "145/3A",
            "khata_number": "882",
            "area": 2.50,
            "area_unit": "Acres",
            "tehsil_mandal": "Hapur",
            "district": "Meerut",
            "registration_number": "4012/2024",
            "registration_date": "2024-04-12"
        },
        "reference_text": "GOVERNMENT LAND REVENUE DEPARTMENT FORM I-B RECORD OF RIGHTS District Meerut Tehsil Mandal Hapur Village Hapur Survey Number 145/3A Khata Number 882 Area Extent 2.50 Acres Land Classification Dry - Agricultural Owner Name Ramesh Singh Registration Number 4012/2024 Registration Date 12-04-2024"
    },
    "tamil_patta_sample.jpg": {
        "language": "Tamil",
        "doc_type": "Pattadar/Land Ownership Record",
        "format_type": "PRINTED",
        "fields": {
            "owner_name": "Krishnamurthy",
            "survey_number": "145/3A",
            "khata_number": "412",
            "area": 2.50,
            "area_unit": "Acres",
            "village": "Sholavandan",
            "tehsil_mandal": "Sholavandan",
            "district": "Madurai",
            "registration_number": "9122/2023",
            "registration_date": "2023-09-10"
        },
        "reference_text": "GOVERNMENT LAND REVENUE DEPARTMENT FORM I-B RECORD OF RIGHTS District Madurai Tehsil Mandal Sholavandan Village Sholavandan Survey Number 145/3A Patta Number 412 Area Extent 2.50 Acres Land Classification Dry - Agricultural Owner Name Krishnamurthy Registration Number 9122/2023 Registration Date 10-09-2023"
    }
}

ALL_INDIAN_LANGUAGES = [
    "English", "Telugu", "Hindi", "Tamil",
    "Kannada", "Malayalam", "Marathi", "Bengali",
    "Gujarati", "Odia", "Punjabi"
]

def run_scientific_benchmark():
    print("=" * 80)
    print("SIH 2026 SCIENTIFIC AI LAND DIGITIZATION BENCHMARK REPORT")
    print("=" * 80)

    adapter = VLMDocumentUnderstandingAdapter()
    
    total_docs = 0
    total_latency_ms = 0.0
    total_cer = 0.0
    total_wer = 0.0
    total_tp = 0
    total_fp = 0
    total_fn = 0
    exact_matches = 0
    total_gt_fields = 0
    human_reviews_triggered = 0

    doc_metrics = []

    for fn, gt in GROUND_TRUTH.items():
        sample_path = os.path.join("sample_documents", fn)
        if not os.path.exists(sample_path):
            continue

        t0 = time.time()
        start_mem = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)

        ocr_res = run_ocr(sample_path)
        format_res = classify_document_format(sample_path, ocr_res.get("lines", []))
        
        doc_understanding = adapter.process_document(
            image_path=sample_path,
            ocr_result=ocr_res,
            language=gt["language"],
            doc_type=gt["doc_type"],
            format_type=format_res["format_type"]
        )

        latency_ms = (time.time() - t0) * 1000.0
        end_mem = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)

        hyp_text = ocr_res.get("text", "")
        ref_text = gt.get("reference_text", "")
        cer, wer = calculate_cer_wer(ref_text, hyp_text)

        extracted = doc_understanding.get("staging", {})
        gt_fields = gt.get("fields", {})

        tp, fp, fn_count, exact_m = 0, 0, 0, 0
        for k, gt_val in gt_fields.items():
            ext_val = extracted.get(k)
            if ext_val is not None:
                if str(ext_val).strip().lower() == str(gt_val).strip().lower():
                    tp += 1
                    exact_m += 1
                else:
                    fp += 1
            else:
                fn_count += 1

        precision = (tp / max(tp + fp, 1)) * 100.0
        recall = (tp / max(tp + fn_count, 1)) * 100.0
        f1 = (2 * precision * recall / max(precision + recall, 1e-5))

        needs_review = format_res["needs_human_review"] or (doc_understanding["document_confidence"] < 75.0)

        total_docs += 1
        total_latency_ms += latency_ms
        total_cer += cer
        total_wer += wer
        total_tp += tp
        total_fp += fp
        total_fn += fn_count
        exact_matches += exact_m
        total_gt_fields += len(gt_fields)
        if needs_review:
            human_reviews_triggered += 1

        doc_metrics.append({
            "document": fn,
            "language": gt["language"],
            "format_detected": format_res["format_type"],
            "format_confidence": format_res["confidence"],
            "ocr_cer_pct": cer,
            "ocr_wer_pct": wer,
            "field_precision_pct": round(precision, 1),
            "field_recall_pct": round(recall, 1),
            "field_f1_pct": round(f1, 1),
            "document_confidence": doc_understanding["document_confidence"],
            "latency_ms": round(latency_ms, 1),
            "memory_mb": round(end_mem, 1),
            "human_review_required": needs_review
        })

        print(f"\n[DOCUMENT] {fn}")
        print(f"  Language:           {gt['language']} (Detected Script: {detect_language(hyp_text)})")
        print(f"  Format Classified:  {format_res['format_type']} (Confidence: {format_res['confidence']}%)")
        print(f"  OCR CER:            {cer}% | WER: {wer}%")
        print(f"  Field Precision:    {precision:.1f}% | Recall: {recall:.1f}% | F1: {f1:.1f}%")
        print(f"  Doc Confidence:     {doc_understanding['document_confidence']}%")
        print(f"  Latency:            {latency_ms:.1f}ms | Memory: {end_mem:.1f}MB")

    avg_cer = total_cer / max(total_docs, 1)
    avg_wer = total_wer / max(total_docs, 1)
    overall_prec = (total_tp / max(total_tp + total_fp, 1)) * 100.0
    overall_rec = (total_tp / max(total_tp + total_fn, 1)) * 100.0
    overall_f1 = (2 * overall_prec * overall_rec / max(overall_prec + overall_rec, 1e-5))
    exact_match_rate = (exact_matches / max(total_gt_fields, 1)) * 100.0
    avg_lat = total_latency_ms / max(total_docs, 1)
    hr_rate = (human_reviews_triggered / max(total_docs, 1)) * 100.0

    print("\n" + "=" * 80)
    print("LANGUAGE TEST MATRIX")
    print("=" * 80)
    tested_langs = set(gt["language"] for gt in GROUND_TRUTH.values())
    for lang in ALL_INDIAN_LANGUAGES:
        status = "TESTED (Active Ground Truth Benchmark)" if lang in tested_langs else "NOT TESTED (Ground Truth Samples Pending)"
        print(f"  {lang:15} : {status}")

    print("\n" + "=" * 80)
    print("OVERALL SUMMARY METRICS")
    print("=" * 80)
    print(f"  Total Evaluated Documents:   {total_docs}")
    print(f"  Average OCR CER:             {avg_cer:.2f}%")
    print(f"  Average OCR WER:             {avg_wer:.2f}%")
    print(f"  Field Extraction Precision:  {overall_prec:.1f}%")
    print(f"  Field Extraction Recall:     {overall_rec:.1f}%")
    print(f"  Field Extraction F1 Score:   {overall_f1:.1f}%")
    print(f"  Exact Match Accuracy:        {exact_match_rate:.1f}%")
    print(f"  Average Processing Latency:  {avg_lat:.1f}ms per document")
    print(f"  Human Review Trigger Rate:   {hr_rate:.1f}%")

    benchmark_summary = {
        "documents": doc_metrics,
        "aggregate": {
            "total_documents": total_docs,
            "average_cer": round(avg_cer, 2),
            "average_wer": round(avg_wer, 2),
            "field_precision": round(overall_prec, 1),
            "field_recall": round(overall_rec, 1),
            "field_f1": round(overall_f1, 1),
            "exact_match_rate": round(exact_match_rate, 1),
            "average_latency_ms": round(avg_lat, 1),
            "human_review_rate": round(hr_rate, 1)
        },
        "language_matrix": {
            lang: ("TESTED" if lang in tested_langs else "NOT TESTED")
            for lang in ALL_INDIAN_LANGUAGES
        }
    }

    with open("benchmark/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(benchmark_summary, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_scientific_benchmark()
