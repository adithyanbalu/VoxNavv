"""
Performance Latency Benchmark for Yazeen's Context & Privacy Engine.
Evaluates roundtrip processing latency over hundreds of cycles,
verifying SLA compliance (<100ms) and calculating p50, p95, and p99 metrics.
"""

import sys
import os
import time
import numpy as np

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from context_engine.processor import get_context_and_explanation

BENCHMARK_SCENARIOS = [
    (
        "SEND_DOCUMENT",
        {"recipient": "john@example.com", "document_id": "Medical_Report.pdf"},
        {
            "requiredContext": ["recipient", "document"],
            "allowedSources": ["messages", "calendar", "files"],
            "maxContextItems": 3,
        },
    ),
    (
        "DELETE_FILE",
        {"document_id": "Henderson_Project_Notes.txt"},
        {
            "requiredContext": ["file", "modification_history"],
            "allowedSources": ["files", "messages"],
            "maxContextItems": 3,
        },
    ),
    (
        "CANCEL_APPT",
        {"recipient": "Dr. Smith"},
        {
            "requiredContext": ["appointment_time", "participant"],
            "allowedSources": ["calendar", "messages", "contacts"],
            "maxContextItems": 3,
        },
    ),
    (
        "TRANSFER",
        {"recipient": "Alice", "amount": 100},
        {
            "requiredContext": ["recipient", "purpose"],
            "allowedSources": ["messages", "contacts", "files"],
            "maxContextItems": 3,
        },
    ),
]


def run_benchmark(iterations_per_scenario: int = 50):
    print("=" * 65)
    print("VOXNAV CONTEXT ENGINE: LATENCY BENCHMARK (<100ms SLA)")
    print("=" * 65)

    all_durations = []
    scenario_stats = {}

    # Warmup
    for action, target, policy in BENCHMARK_SCENARIOS:
        get_context_and_explanation(action, target, policy)

    for action, target, policy in BENCHMARK_SCENARIOS:
        durations = []
        for _ in range(iterations_per_scenario):
            t0 = time.perf_counter()
            get_context_and_explanation(action, target, policy)
            t1 = time.perf_counter()
            durations.append((t1 - t0) * 1000)

        all_durations.extend(durations)
        scenario_stats[action] = {
            "mean": float(np.mean(durations)),
            "p50": float(np.percentile(durations, 50)),
            "p95": float(np.percentile(durations, 95)),
            "p99": float(np.percentile(durations, 99)),
            "min": float(np.min(durations)),
            "max": float(np.max(durations)),
        }

    print(f"{'Action Type':<18} | {'Mean (ms)':<10} | {'p50 (ms)':<10} | {'p95 (ms)':<10} | {'p99 (ms)':<10} | {'Status':<8}")
    print("-" * 75)
    for action, stats in scenario_stats.items():
        status = "PASS" if stats["p95"] < 100.0 else "FAIL"
        print(
            f"{action:<18} | {stats['mean']:<10.2f} | {stats['p50']:<10.2f} | "
            f"{stats['p95']:<10.2f} | {stats['p99']:<10.2f} | {status:<8}"
        )

    overall_mean = float(np.mean(all_durations))
    overall_p95 = float(np.percentile(all_durations, 95))
    overall_p99 = float(np.percentile(all_durations, 99))
    rps = 1000.0 / overall_mean if overall_mean > 0 else 0

    print("=" * 65)
    print(f"Overall Iterations: {len(all_durations)}")
    print(f"Overall Mean:       {overall_mean:.2f} ms")
    print(f"Overall 95th %ile:  {overall_p95:.2f} ms (Target: <100 ms)")
    print(f"Overall 99th %ile:  {overall_p99:.2f} ms")
    print(f"Throughput Est:     {rps:.1f} req/sec on single core")
    print(f"SLA Compliance:     {'COMPLIANT (<100ms)' if overall_p95 < 100.0 else 'NON-COMPLIANT'}")
    print("=" * 65)


if __name__ == "__main__":
    run_benchmark(iterations_per_scenario=100)
