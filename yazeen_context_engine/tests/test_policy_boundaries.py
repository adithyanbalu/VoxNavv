"""
Tests for Policy Enforcement and Privacy Boundaries.
Ensures permitted sources are strictly honored and unpermitted sources are 100% blocked.
"""

import pytest
from context_engine.synthetic_data_loader import SyntheticDataLoader
from context_engine.retriever import ContextRetriever
from context_engine.models import PolicyInput
from context_engine.processor import ContextProcessor


@pytest.fixture
def processor():
    return ContextProcessor()


def test_messages_only_policy(processor):
    policy = {
        "requiredContext": ["recipient"],
        "allowedSources": ["messages"],
        "maxContextItems": 3,
    }
    target = {"recipient": "Dr. Smith", "document_id": "Medical_Report.pdf"}
    result = processor.process("SEND_DOCUMENT", target, policy)

    audit = result["audit_summary"]
    assert audit["allowed_sources_queried"] == ["messages"]
    assert set(audit["blocked_sources"]) == {"calendar", "files", "contacts"}

    # Used items must ONLY be from messages or target echo
    for used in result["privacy_log"]["used"]:
        if used.startswith("Target"):
            continue
        assert used.startswith("Messages:"), f"Expected only messages, got: {used}"


def test_files_only_policy(processor):
    policy = {
        "requiredContext": ["file"],
        "allowedSources": ["files"],
        "maxContextItems": 2,
    }
    target = {"document_id": "Henderson_Project_Notes.txt"}
    result = processor.process("DELETE_FILE", target, policy)

    audit = result["audit_summary"]
    assert audit["allowed_sources_queried"] == ["files"]
    assert "messages" in audit["blocked_sources"]

    for used in result["privacy_log"]["used"]:
        if used.startswith("Target"):
            continue
        assert used.startswith("Files:"), f"Expected only files, got: {used}"


def test_calendar_only_policy(processor):
    policy = {
        "requiredContext": ["appointment_time"],
        "allowedSources": ["calendar"],
        "maxContextItems": 2,
    }
    target = {"recipient": "Dr. Smith"}
    result = processor.process("CANCEL_APPT", target, policy)

    audit = result["audit_summary"]
    assert audit["allowed_sources_queried"] == ["calendar"]
    assert "messages" in audit["blocked_sources"]

    for used in result["privacy_log"]["used"]:
        if used.startswith("Target"):
            continue
        assert used.startswith("Calendar:"), f"Expected only calendar, got: {used}"


def test_empty_allowed_sources_blocks_all(processor):
    policy = {
        "requiredContext": [],
        "allowedSources": [],
        "maxContextItems": 3,
    }
    target = {"recipient": "Alice", "amount": 100}
    result = processor.process("TRANSFER", target, policy)

    audit = result["audit_summary"]
    assert audit["items_used_count"] == 0
    assert audit["items_shielded_count"] == audit["total_vault_items"]
    assert audit["privacy_shield_percentage"] == "100.0%"


def test_max_context_items_cap(processor):
    policy = {
        "requiredContext": ["general"],
        "allowedSources": ["messages", "calendar", "files", "contacts"],
        "maxContextItems": 1,
    }
    target = {"recipient": "Dr. Smith"}
    result = processor.process("CANCEL_APPT", target, policy)

    # Exactly 1 context item extracted (plus target metadata echoes)
    context_facts_used = [u for u in result["privacy_log"]["used"] if not u.startswith("Target")]
    assert len(context_facts_used) <= 1
