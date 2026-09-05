"""
Tests for Privacy Accounting Invariants.
Validates the mathematical guarantee:
Total Vault Items = Items Used + Items Deliberately Shielded.
"""

import pytest
from context_engine.processor import ContextProcessor


@pytest.fixture
def processor():
    return ContextProcessor()


def test_mathematical_sum_invariant_across_actions(processor):
    test_cases = [
        ("SEND_DOCUMENT", {"recipient": "john@example.com", "document_id": "Medical_Report.pdf"}),
        ("DELETE_FILE", {"document_id": "Henderson_Project_Notes.txt"}),
        ("DELETE_FILE", {"document_id": "temp_file.txt"}),
        ("CANCEL_APPT", {"recipient": "Dr. Smith"}),
        ("TRANSFER", {"recipient": "Alice", "amount": 100}),
        ("SEND_DOCUMENT", {"recipient": "eve@unverified-external.org", "document_id": "Medical_Report.pdf"}),
        ("TRANSFER", {"recipient": "Unknown", "amount": 500}),
    ]

    for action, target in test_cases:
        res = processor.process(action, target)
        audit = res["audit_summary"]

        total = audit["total_vault_items"]
        used = audit["items_used_count"]
        shielded = audit["items_shielded_count"]

        # Strict invariant
        assert total == used + shielded, f"Accounting broken for {action}: {total} != {used} + {shielded}"
        assert total >= 100
        assert used <= 5

        # Shield percentage check
        shield_pct = float(audit["privacy_shield_percentage"].replace("%", ""))
        assert shield_pct >= 95.0, f"Shield percentage too low for {action}: {shield_pct}%"
        assert audit["zero_raw_data_exposure"] is True


def test_no_raw_message_bodies_in_used_log(processor):
    res = processor.process("SEND_DOCUMENT", {"recipient": "john@example.com", "document_id": "Medical_Report.pdf"})
    for u in res["privacy_log"]["used"]:
        # Ensure full raw email text like "Dear Robert, please send over..." is not dumped verbatim
        assert "Dear Robert, please send over" not in u
        # Only compressed micro-facts allowed
        assert len(u) < 300
