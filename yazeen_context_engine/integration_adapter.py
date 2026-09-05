"""
Integration Adapter for Merging Yazeen's Subsystem into the Main Project.
Provides a 1-line drop-in shim and contract validator for GSK's backend.
"""

import sys
import os
from typing import Dict, Any

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from context_engine.processor import get_context_and_explanation


def evaluate_action_context(action_type: str, target: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    """
    Contract-compliant hook matching INTERFACES.md:
    Input:
        action_type: "SEND_DOCUMENT" | "DELETE_FILE" | "CANCEL_APPT" | "TRANSFER"
        target: { "recipient": str, "document_id": str, "amount": float }
        policy: { "requiredContext": list, "allowedSources": list, "maxContextItems": int }
    Output:
        {
          "explanation": str,
          "privacy_log": {
            "used": list[str],
            "not_used": list[str]
          },
          "sufficiency": dict,
          "audit_summary": dict,
          "latency_ms": float
        }
    """
    return get_context_and_explanation(action_type, target, policy)


if __name__ == "__main__":
    print("Testing Integration Adapter...")
    sample_policy = {
        "requiredContext": ["recipient", "document"],
        "allowedSources": ["messages", "calendar", "files"],
        "maxContextItems": 3,
    }
    sample_target = {"recipient": "john@example.com", "document_id": "Medical_Report.pdf"}
    result = evaluate_action_context("SEND_DOCUMENT", sample_target, sample_policy)
    assert "explanation" in result
    assert "privacy_log" in result
    assert "used" in result["privacy_log"]
    assert "not_used" in result["privacy_log"]
    print("Integration Adapter Verified Successfully! Ready to plug into backend/main.py.")
