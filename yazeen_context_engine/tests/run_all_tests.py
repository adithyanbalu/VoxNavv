"""
Standalone Zero-Dependency Test Runner.
Discovers and executes all test suites without requiring pytest.
Usage:
    python tests/run_all_tests.py
"""

import sys
import os
import time
import inspect
import tempfile
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from tests import (
    test_synthetic_data,
    test_policy_boundaries,
    test_core_actions,
    test_edge_cases,
    test_sufficiency_anomalies,
    test_privacy_invariants,
    test_personalization,
    test_latency_sla,
)
from context_engine.processor import ContextProcessor
from context_engine.synthetic_data_loader import SyntheticDataLoader


def run_tests():
    modules = [
        ("Synthetic Data Suite", test_synthetic_data),
        ("Policy & Boundaries Suite", test_policy_boundaries),
        ("Core Action Flows Suite", test_core_actions),
        ("Edge Cases Suite", test_edge_cases),
        ("Sufficiency & Anomalies Suite", test_sufficiency_anomalies),
        ("Privacy Invariants Suite", test_privacy_invariants),
        ("Personalization Suite", test_personalization),
        ("Latency SLA Suite", test_latency_sla),
    ]

    total_run = 0
    total_passed = 0
    total_failed = 0
    failures = []

    print("=" * 70)
    print("VOXNAV YAZEEN CONTEXT ENGINE: EXHAUSTIVE TEST SUITE")
    print("=" * 70)

    start_all = time.perf_counter()

    for suite_name, mod in modules:
        print(f"\n▶ Running: {suite_name}")
        for attr_name in dir(mod):
            if attr_name.startswith("test_") and callable(getattr(mod, attr_name)):
                fn = getattr(mod, attr_name)
                total_run += 1
                sig = inspect.signature(fn)
                kwargs = {}
                tmp_dir_obj = None

                # Provide fixture arguments
                if "processor" in sig.parameters:
                    kwargs["processor"] = ContextProcessor()
                if "loader" in sig.parameters:
                    kwargs["loader"] = SyntheticDataLoader()
                if "tmp_path" in sig.parameters:
                    tmp_dir_obj = tempfile.TemporaryDirectory()
                    kwargs["tmp_path"] = Path(tmp_dir_obj.name)

                t0 = time.perf_counter()
                try:
                    fn(**kwargs)
                    elapsed_ms = (time.perf_counter() - t0) * 1000
                    print(f"  ✓ {attr_name:<45} ({elapsed_ms:>6.2f} ms) [PASS]")
                    total_passed += 1
                except Exception as e:
                    elapsed_ms = (time.perf_counter() - t0) * 1000
                    print(f"  ✗ {attr_name:<45} ({elapsed_ms:>6.2f} ms) [FAIL]")
                    print(f"    Error: {e}")
                    failures.append((suite_name, attr_name, str(e)))
                    total_failed += 1
                finally:
                    if tmp_dir_obj:
                        tmp_dir_obj.cleanup()

    total_time = (time.perf_counter() - start_all) * 1000
    print("\n" + "=" * 70)
    print(f"TEST SUMMARY: {total_passed}/{total_run} PASSED in {total_time:.2f} ms")
    if total_failed == 0:
        print("ALL TESTS PASSED! Subsystem is 100% stable and ready for PR merge.")
        print("=" * 70)
        return 0
    else:
        print(f"FAILED TESTS ({total_failed}):")
        for s, fn, err in failures:
            print(f"  - [{s}] {fn}: {err}")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
