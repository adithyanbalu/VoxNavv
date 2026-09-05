"""
Exhaustive Edge Cases Test Suite for Context Engine.
Validates behavior under extreme inputs, malformed types, missing fields,
Unicode strings, negative amounts, path traversal attempts, and empty policies.
"""

import pytest
from context_engine.processor import ContextProcessor, get_context_and_explanation


@pytest.fixture
def processor():
    return ContextProcessor()


def test_empty_target_dict(processor):
    result = processor.process("SEND_DOCUMENT", {}, {})
    assert "explanation" in result
    assert "privacy_log" in result
    assert result["sufficiency"]["is_sufficient"] is False


def test_none_target(processor):
    result = processor.process("SEND_DOCUMENT", None, None)
    assert isinstance(result["explanation"], str)
    assert len(result["explanation"]) > 0
    assert "used" in result["privacy_log"]
    assert "not_used" in result["privacy_log"]


def test_none_action_type(processor):
    result = processor.process(None, {"recipient": "Alice"}, {})
    assert isinstance(result["explanation"], str)


def test_unknown_action_type(processor):
    result = processor.process("UNKNOWN_ACTION_XYZ", {"recipient": "Alice"}, {})
    assert "Before you proceed:" in result["explanation"]


def test_unicode_and_accented_recipient(processor):
    target = {"recipient": "Dr. Müller-Smith", "document_id": "Medical_Report.pdf"}
    result = processor.process("SEND_DOCUMENT", target, {"allowedSources": ["messages", "files"]})
    assert isinstance(result["explanation"], str)
    assert not result["explanation"].startswith("Error")


def test_recipient_with_subaddressing(processor):
    # alice+receipts@family.com
    target = {"recipient": "alice+receipts@family.com", "amount": 100}
    result = processor.process("TRANSFER", target, {"allowedSources": ["messages"]})
    assert result["sufficiency"]["is_sufficient"] is True
    assert "Alice" in result["explanation"]


def test_string_amount_with_dollar_and_commas(processor):
    target = {"recipient": "Alice", "amount": "$100.00"}
    result = processor.process("TRANSFER", target, {"allowedSources": ["messages"]})
    assert result["sufficiency"]["is_sufficient"] is True
    assert "Alice" in result["explanation"]


def test_negative_amount(processor):
    target = {"recipient": "Alice", "amount": -50}
    result = processor.process("TRANSFER", target, {"allowedSources": ["messages"]})
    assert isinstance(result["explanation"], str)


def test_zero_amount(processor):
    target = {"recipient": "Alice", "amount": 0}
    result = processor.process("TRANSFER", target, {"allowedSources": ["messages"]})
    assert isinstance(result["explanation"], str)


def test_huge_amount(processor):
    target = {"recipient": "Alice", "amount": 10000000}
    result = processor.process("TRANSFER", target, {"allowedSources": ["messages"]})
    assert isinstance(result["explanation"], str)


def test_path_traversal_document_id(processor):
    target = {"recipient": "john@example.com", "document_id": "../../../../Medical_Report.pdf"}
    result = processor.process("SEND_DOCUMENT", target, {"allowedSources": ["messages", "files"]})
    # Should still resolve the base filename Medical_Report.pdf
    assert "Medical_Report.pdf" in result["explanation"] or "Dr. John Smith" in result["explanation"]


def test_negative_max_context_items(processor):
    policy = {"maxContextItems": -5, "allowedSources": ["messages"]}
    result = processor.process("SEND_DOCUMENT", {"recipient": "john@example.com"}, policy)
    # Capped safely to at least 1
    assert result["audit_summary"]["items_used_count"] <= 1


def test_huge_max_context_items(processor):
    policy = {"maxContextItems": 9999, "allowedSources": ["messages"]}
    result = processor.process("SEND_DOCUMENT", {"recipient": "john@example.com"}, policy)
    # Clamped safely to at most 20
    assert result["audit_summary"]["items_used_count"] <= 20


def test_unknown_allowed_sources(processor):
    policy = {"allowedSources": ["crypto_chain", "satellite_feed"]}
    result = processor.process("TRANSFER", {"recipient": "Alice", "amount": 100}, policy)
    assert result["audit_summary"]["items_used_count"] == 0
    assert result["audit_summary"]["privacy_shield_percentage"] == "100.0%"


def test_very_long_input_strings(processor):
    giant_name = "Alice " * 1000
    target = {"recipient": giant_name, "amount": 100}
    result = processor.process("TRANSFER", target, {"allowedSources": ["messages"]})
    assert isinstance(result["explanation"], str)


def test_standalone_function_call():
    # Verify get_context_and_explanation top-level API works with primitive arguments
    res = get_context_and_explanation("CANCEL_APPT", {"recipient": "Dr. Smith"}, None)
    assert isinstance(res, dict)
    assert "explanation" in res
    assert "privacy_log" in res
