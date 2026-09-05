"""
Tests for Core Action Flows.
Verifies SEND_DOCUMENT, DELETE_FILE, CANCEL_APPT, and TRANSFER.
"""

import pytest
from context_engine.processor import ContextProcessor


@pytest.fixture
def processor():
    return ContextProcessor()


def test_send_document_flow(processor):
    policy = {
        "requiredContext": ["recipient", "document", "previous_request"],
        "allowedSources": ["messages", "calendar", "files"],
        "maxContextItems": 3,
    }
    target = {"recipient": "john@example.com", "document_id": "Medical_Report.pdf"}
    result = processor.process("SEND_DOCUMENT", target, policy)

    assert "Before you send:" in result["explanation"]
    assert "John Smith" in result["explanation"] or "August 28" in result["explanation"]
    assert result["sufficiency"]["is_sufficient"] is True
    assert result["sufficiency"]["anomaly_detected"] is False
    assert len(result["privacy_log"]["used"]) >= 2
    assert len(result["privacy_log"]["not_used"]) == 4


def test_delete_file_project_flow(processor):
    policy = {
        "requiredContext": ["file", "modification_history"],
        "allowedSources": ["files", "messages"],
        "maxContextItems": 3,
    }
    target = {"document_id": "Henderson_Project_Notes.txt"}
    result = processor.process("DELETE_FILE", target, policy)

    assert "Before you delete:" in result["explanation"]
    assert "July 15" in result["explanation"] or "Henderson" in result["explanation"]
    assert result["sufficiency"]["is_sufficient"] is True
    assert len(result["privacy_log"]["used"]) >= 2


def test_delete_file_temp_flow(processor):
    policy = {
        "requiredContext": ["file", "modification_history"],
        "allowedSources": ["files", "messages"],
        "maxContextItems": 3,
    }
    target = {"document_id": "temp_file.txt"}
    result = processor.process("DELETE_FILE", target, policy)

    assert "Before you delete:" in result["explanation"]
    assert "temporary" in result["explanation"].lower() or "scratch" in result["explanation"].lower()
    assert result["sufficiency"]["is_sufficient"] is True


def test_cancel_appointment_flow(processor):
    policy = {
        "requiredContext": ["appointment_time", "participant"],
        "allowedSources": ["calendar", "messages", "contacts"],
        "maxContextItems": 3,
    }
    target = {"recipient": "Dr. Smith"}
    result = processor.process("CANCEL_APPT", target, policy)

    assert "Before you cancel:" in result["explanation"]
    assert "Dr. Smith" in result["explanation"]
    assert "September" in result["explanation"] or "2:00 PM" in result["explanation"]
    assert result["sufficiency"]["is_sufficient"] is True


def test_transfer_money_flow(processor):
    policy = {
        "requiredContext": ["recipient", "purpose"],
        "allowedSources": ["messages", "contacts", "files"],
        "maxContextItems": 3,
    }
    target = {"recipient": "Alice", "amount": 100}
    result = processor.process("TRANSFER", target, policy)

    assert "Before you transfer:" in result["explanation"]
    assert "Alice" in result["explanation"]
    assert "$100" in result["explanation"]
    assert "August 20" in result["explanation"]
    assert result["sufficiency"]["is_sufficient"] is True
