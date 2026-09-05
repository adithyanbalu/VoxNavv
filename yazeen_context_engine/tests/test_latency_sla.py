"""
Tests for Latency SLA Compliance (<100ms requirement).
"""

import time
import numpy as np
import pytest
from context_engine.processor import ContextProcessor


@pytest.fixture
def processor():
    return ContextProcessor()


def test_latency_sla_all_actions(processor):
    test_cases = [
        ("SEND_DOCUMENT", {"recipient": "john@example.com", "document_id": "Medical_Report.pdf"}),
        ("DELETE_FILE", {"document_id": "Henderson_Project_Notes.txt"}),
        ("CANCEL_APPT", {"recipient": "Dr. Smith"}),
        ("TRANSFER", {"recipient": "Alice", "amount": 100}),
    ]

    all_latencies = []
    for action, target in test_cases:
        durations = []
        for _ in range(25):
            t0 = time.perf_counter()
            processor.process(action, target)
            t1 = time.perf_counter()
            durations.append((t1 - t0) * 1000)

        all_latencies.extend(durations)
        action_mean = float(np.mean(durations))
        action_p95 = float(np.percentile(durations, 95))
        assert action_mean < 5.0, f"Mean latency {action_mean}ms exceeded 5ms for {action}"
        assert action_p95 < 50.0, f"p95 latency {action_p95}ms exceeded 50ms for {action}"

    overall_max = max(all_latencies)
    assert overall_max < 100.0, f"Max latency {overall_max}ms violated <100ms SLA"
