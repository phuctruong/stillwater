"""Benchmark 5: Verification Correctness.

Pure CPU benchmark -- proves the verification ladder infrastructure itself.
No LLM needed. Runs the full verification ladder and checks all rungs pass.
"""

from __future__ import annotations

import time

from stillwater.bench import BenchResult
from stillwater.harness.verify import (
    run_274177_stress_tests,
    run_641_edge_tests,
    run_65537_god_test,
    run_oauth_checks,
)
from stillwater.llm import LLMClient


def run(client: LLMClient) -> BenchResult:
    """Run verification correctness benchmark (pure CPU, client unused)."""
    details: list[dict] = []
    passed = 0
    total = 5
    t0 = time.perf_counter()

    # Test 1: OAuth checks all pass
    oauth = run_oauth_checks()
    oauth_ok = all(r.passed for r in oauth) and len(oauth) == 3
    if oauth_ok:
        passed += 1
    details.append({"test": "oauth_3_checks", "passed": oauth_ok})

    # Test 2: 641 edge tests all pass
    edge = run_641_edge_tests()
    edge_ok = all(r.passed for r in edge) and len(edge) >= 5
    if edge_ok:
        passed += 1
    details.append({"test": "641_edge_tests", "passed": edge_ok})

    # Test 3: 274177 stress tests all pass
    stress = run_274177_stress_tests()
    stress_ok = all(r.passed for r in stress)
    if stress_ok:
        passed += 1
    details.append({"test": "274177_stress", "passed": stress_ok})

    # Test 4: God test passes when all prior pass
    god = run_65537_god_test(oauth, edge, stress)
    if god.passed:
        passed += 1
    details.append({"test": "65537_god_approval", "passed": god.passed})

    # Test 5: Determinism -- run twice, same results
    oauth2 = run_oauth_checks()
    edge2 = run_641_edge_tests()
    stress2 = run_274177_stress_tests()
    god2 = run_65537_god_test(oauth2, edge2, stress2)
    deterministic = god.passed == god2.passed
    if deterministic:
        passed += 1
    details.append({"test": "ladder_determinism", "passed": deterministic})

    elapsed = (time.perf_counter() - t0) * 1000
    return BenchResult(
        name="Verification Correctness",
        passed=passed,
        total=total,
        elapsed_ms=elapsed,
        details=details,
    )
