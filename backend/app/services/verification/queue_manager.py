import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def evaluate_verification_routing(
    overall_confidence: float,
    anomalies: List[Dict[str, Any]],
    is_handwritten: bool = False
) -> Dict[str, Any]:
    """
    Determines whether a document should be auto-verified or routed to human review.
    """
    has_blocking_anomalies = any(a.get("severity") == "High" for a in anomalies)
    has_warnings = len(anomalies) > 0
    
    if has_blocking_anomalies:
        status = "Pending Review"
        stage = "NEEDS_REVIEW"
        reason = "High-severity statutory anomalies flagged"
    elif has_warnings:
        status = "Pending Review"
        stage = "NEEDS_REVIEW"
        reason = "Logical discrepancies or missing mandatory fields detected"
    elif overall_confidence < 75.0:
        status = "Low Confidence"
        stage = "NEEDS_REVIEW"
        reason = f"Overall confidence ({overall_confidence}%) is below verification threshold"
    else:
        status = "Verified"
        stage = "COMPLETED"
        reason = "Passed all statutory validation checks with high confidence"

    return {
        "status": status,
        "processing_stage": stage,
        "routing_reason": reason,
        "requires_human_review": status != "Verified"
    }
