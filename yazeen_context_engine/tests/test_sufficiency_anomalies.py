"""
Tests for Section 14 Context Sufficiency & Anomaly Detection.
Verifies safety guards against misdirected documents, unfamiliar recipients,
unverified bank transfers, and phantom appointment cancellations.
"""

import pytest
from context_engine.processor import ContextProcessor


@pytest.fixture
def processor():
    return ContextProcessor()


def test_anomaly_send_doc_to_stranger(processor):
    policy = {
        "requiredContext": ["recipient", "document"],
        "allowedSources": ["messages", "calendar", "files"],
        "maxContextItems": 3,
    }
    target = {
        "recipient": "eve@unverified-external.org",
        "document_id": "Medical_Report.pdf",
    }
    result = processor.process("SEND_DOCUMENT", target, policy)

    assert result["sufficiency"]["is_sufficient"] is False
    assert result["sufficiency"]["anomaly_detected"] is True
    assert "eve@unverified-external.org" in result["explanation"]
    assert "double-check" in result["explanation"].lower() or "verify" in result["explanation"].lower()


def test_anomaly_transfer_to_stranger(processor):
    policy = {
        "requiredContext": ["recipient", "purpose"],
        "allowedSources": ["messages", "contacts", "files"],
        "maxContextItems": 3,
    }
    target = {
        "recipient": "Random Stranger",
        "amount": 5000,
    }
    result = processor.process("TRANSFER", target, policy)

    assert result["sufficiency"]["is_sufficient"] is False
    assert result["sufficiency"]["anomaly_detected"] is True
    assert "Random Stranger" in result["explanation"]
    assert "verify" in result["explanation"].lower()


def test_anomaly_cancel_nonexistent_appointment(processor):
    policy = {
        "requiredContext": ["appointment_time", "participant"],
        "allowedSources": ["calendar", "messages", "contacts"],
        "maxContextItems": 3,
    }
    target = {
        "recipient": "Dr. Frankenstein",
    }
    result = processor.process("CANCEL_APPT", target, policy)

    assert result["sufficiency"]["is_sufficient"] is False
    assert result["sufficiency"]["anomaly_detected"] is True
    assert "Dr. Frankenstein" in result["explanation"]


def test_anomaly_delete_nonexistent_file(processor):
    policy = {
        "requiredContext": ["file", "modification_history"],
        "allowedSources": ["files", "messages"],
        "maxContextItems": 3,
    }
    target = {
        "document_id": "completely_unknown_file_xyz.dat",
    }
    result = processor.process("DELETE_FILE", target, policy)

    assert result["sufficiency"]["is_sufficient"] is False
    assert result["sufficiency"]["anomaly_detected"] is True
    assert "completely_unknown_file_xyz.dat" in result["explanation"]
