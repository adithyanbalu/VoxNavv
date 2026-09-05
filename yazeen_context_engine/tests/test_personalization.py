"""
Tests for Lightweight On-Device Personalization Engine.
Validates decision logging, trust weight updates, and isolated local storage.
"""

import os
import json
import pytest
from context_engine.personalization import PersonalizationEngine


def test_personalization_isolated_lifecycle(tmp_path):
    pref_path = str(tmp_path / "custom_prefs.json")
    engine = PersonalizationEngine(pref_file=pref_path)

    # Initial state
    assert engine.get_recipient_trust_bias("Alice") == 0.0

    # Record confirmations
    engine.record_user_decision("TRANSFER", "Alice", "continue")
    assert engine.get_recipient_trust_bias("Alice") == 0.05

    # More confirmations
    for _ in range(4):
        engine.record_user_decision("TRANSFER", "Alice", "continue")

    assert engine.get_recipient_trust_bias("Alice") == 0.15

    # Cancellations lower the trust
    engine.record_user_decision("TRANSFER", "Alice", "cancel")
    assert engine.get_recipient_trust_bias("Alice") == 0.0

    # Persistence verification
    engine2 = PersonalizationEngine(pref_file=pref_path)
    assert len(engine2.preferences["feedback_history"]) == 6


def test_corrupt_file_graceful_recovery(tmp_path):
    corrupt_file = str(tmp_path / "corrupt.json")
    with open(corrupt_file, "w") as f:
        f.write("{invalid-json-content")

    # Should not throw exception
    engine = PersonalizationEngine(pref_file=corrupt_file)
    assert engine.preferences is not None
