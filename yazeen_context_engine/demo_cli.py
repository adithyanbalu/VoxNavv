"""
Interactive CLI Demonstration of Context Before Consequence.
Simulates digital actions, displays the extracted context, Section 14 anomaly guards,
and the judge-proof privacy audit ledger.
Usage:
    python demo_cli.py
"""

import sys
import os
import json

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from context_engine.processor import get_context_and_explanation
from context_engine.personalization import PersonalizationEngine

SCENARIOS = {
    "1": (
        "Send Document (Dr. John Smith - Normal)",
        "SEND_DOCUMENT",
        {"recipient": "john@example.com", "document_id": "Medical_Report.pdf"},
        {"allowedSources": ["messages", "calendar", "files"], "maxContextItems": 3},
    ),
    "2": (
        "Send Document (Eve - Anomaly / Mismatched Recipient)",
        "SEND_DOCUMENT",
        {"recipient": "eve@unverified-external.org", "document_id": "Medical_Report.pdf"},
        {"allowedSources": ["messages", "calendar", "files"], "maxContextItems": 3},
    ),
    "3": (
        "Delete File (Henderson Project Notes - Sensitive)",
        "DELETE_FILE",
        {"document_id": "Henderson_Project_Notes.txt"},
        {"allowedSources": ["files", "messages"], "maxContextItems": 3},
    ),
    "4": (
        "Delete File (temp_file.txt - Temporary Cache)",
        "DELETE_FILE",
        {"document_id": "temp_file.txt"},
        {"allowedSources": ["files", "messages"], "maxContextItems": 3},
    ),
    "5": (
        "Cancel Appointment (Dr. Smith Consultation)",
        "CANCEL_APPT",
        {"recipient": "Dr. Smith"},
        {"allowedSources": ["calendar", "messages", "contacts"], "maxContextItems": 3},
    ),
    "6": (
        "Transfer Money ($100 to Alice Vance)",
        "TRANSFER",
        {"recipient": "Alice", "amount": 100},
        {"allowedSources": ["messages", "contacts", "files"], "maxContextItems": 3},
    ),
}


def run_scenario(key: str):
    title, action, target, policy = SCENARIOS[key]
    print("\n" + "=" * 65)
    print(f"ACTION TRIGGERED: {title}")
    print(f"Action Type:      {action}")
    print(f"Target Details:   {json.dumps(target)}")
    print(f"Allowed Sources:  {policy['allowedSources']}")
    print("=" * 65)

    res = get_context_and_explanation(action, target, policy)

    print("\n💬 [EXPLANATION TO USER]:")
    print(f"  👉 \"{res['explanation']}\"\n")

    suff = res.get("sufficiency", {})
    if suff:
        status_str = "SUFFICIENT (Confident Context Found)" if suff.get("is_sufficient") else "INSUFFICIENT / ANOMALY"
        print(f"🔎 Section 14 Assessment: {status_str}")
        print(f"   Reason: {suff.get('reason')}")
        if suff.get("suggested_verification"):
            print(f"   Recommendation: {suff.get('suggested_verification')}")

    audit = res.get("audit_summary", {})
    if audit:
        print("\n🛡️ [JUDGE PRIVACY PROOF LEDGER]:")
        print(f"   Total Vault Size:    {audit.get('total_vault_items')} items")
        print(f"   Items Evaluated:     {audit.get('items_used_count')} items")
        print(f"   Items Shielded:      {audit.get('items_shielded_count')} items")
        print(f"   Shield Ratio:        {audit.get('privacy_shield_percentage')} protected")
        print(f"   Zero Raw Exposure:   {audit.get('zero_raw_data_exposure')}")
        print(f"   Processing Latency:  {res.get('latency_ms')} ms")

    print("\n📋 Data Used (Minimum Necessary Facts):")
    for u in res["privacy_log"]["used"]:
        print(f"   • {u}")

    print("\n🔒 Data Deliberately NOT Used (Shielded from AI):")
    for nu in res["privacy_log"]["not_used"]:
        print(f"   • {nu}")

    print("=" * 65)


def main():
    print("=" * 65)
    print("  CONTEXT BEFORE CONSEQUENCE - INTERACTIVE CLI DEMO")
    print("  Inclusive Innovation Guardrail (>.hack();_'26)")
    print("=" * 65)

    if len(sys.argv) > 1 and sys.argv[1] in SCENARIOS:
        run_scenario(sys.argv[1])
        return

    while True:
        print("\nSelect an action scenario to test:")
        for k, v in SCENARIOS.items():
            print(f"  [{k}] {v[0]}")
        print("  [A] Run All Scenarios")
        print("  [Q] Quit")

        choice = input("\nEnter choice [1-6, A, Q]: ").strip().upper()
        if choice == "Q":
            print("Exiting demo. Goodbye!")
            break
        elif choice == "A":
            for k in sorted(SCENARIOS.keys()):
                run_scenario(k)
        elif choice in SCENARIOS:
            run_scenario(choice)
        else:
            print("Invalid selection. Please try again.")


if __name__ == "__main__":
    main()
