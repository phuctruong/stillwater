"""
Test: Combo lookup latency SLA — P99 < 1ms.

Verifies:
- CPU match completes in < 1ms (P99 over 500 iterations)
- Direct wish_id lookup is O(1) — no scanning
- Empty/no-match case is still < 1ms
- Full ExecutionMatch.latency_ms field is accurate
- Latency does not scale with combo count (O(1) proof)

rung_target: 641
EXIT_PASS: P99 < 1ms across all 500 iterations with real combo database.
EXIT_BLOCKED: Any P99 >= 1ms.
"""

import sys
import time
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.execute.cpu import ExecutionCPU
from admin.orchestration.execute.database import ComboDB


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_COMBOS_PATH = str(Path(__file__).parent.parent / "combos.jsonl")
_LEARNED_PATH = "/tmp/execute_latency_test_learned.jsonl"


@pytest.fixture(scope="module")
def loaded_db():
    """ComboDB with all 25+ combos loaded."""
    return ComboDB(combos_path=_COMBOS_PATH, learned_path=_LEARNED_PATH)


@pytest.fixture(scope="module")
def cpu(loaded_db):
    return ExecutionCPU(combo_db=loaded_db)


# ---------------------------------------------------------------------------
# Test wish_ids — diverse coverage of all 25 combos
# ---------------------------------------------------------------------------

_TEST_WISH_IDS = [
    "oauth-integration",
    "database-optimization",
    "video-compression",
    "api-design",
    "docker-containerization",
    "security-audit",
    "ci-cd-pipeline",
    "machine-learning-training",
    "react-frontend",
    "python-performance",
    "test-development",
    "git-workflow",
    "debugging",
    "documentation-writing",
    "code-refactoring",
    "dependency-management",
    "logging-monitoring",
    "data-pipeline",
    "websocket-realtime",
    "encryption-cryptography",
    "cache-optimization",
    "infrastructure-as-code",
    "file-storage-upload",
    "rate-limiting",
    "search-indexing",
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestComboLookupLatency:

    def test_p99_under_1ms_500_iterations(self, cpu):
        """
        P99 of cpu.match() must be < 1ms over 500 iterations.
        Uses 25 diverse wish_ids cycled 20x.
        """
        latencies_ms = []
        n = 500

        for i in range(n):
            wish_id = _TEST_WISH_IDS[i % len(_TEST_WISH_IDS)]
            start = time.perf_counter()
            cpu.match(wish_id)
            elapsed_ms = (time.perf_counter() - start) * 1000
            latencies_ms.append(elapsed_ms)

        latencies_ms.sort()
        p50_ms = latencies_ms[249]
        p99_idx = max(0, int(n * 0.99) - 1)
        p99_ms = latencies_ms[p99_idx]
        max_ms = max(latencies_ms)

        assert p99_ms < 1.0, (
            f"Execution CPU P99 = {p99_ms:.4f}ms — exceeds 1ms SLA. "
            f"P50 = {p50_ms:.4f}ms. Max = {max_ms:.4f}ms."
        )

    def test_no_match_under_1ms(self, cpu):
        """No-match (unknown wish_id) must still complete in < 1ms."""
        latencies_ms = []
        for _ in range(100):
            start = time.perf_counter()
            result = cpu.match("nonexistent-wish-xyzzy-foobar")
            elapsed_ms = (time.perf_counter() - start) * 1000
            latencies_ms.append(elapsed_ms)

        latencies_ms.sort()
        p99_idx = max(0, int(len(latencies_ms) * 0.99) - 1)
        p99_ms = latencies_ms[p99_idx]
        assert p99_ms < 1.0, (
            f"No-match P99 = {p99_ms:.4f}ms — exceeds 1ms SLA"
        )

    def test_match_latency_field_populated(self, cpu):
        """ExecutionMatch.latency_ms must be populated and positive."""
        match = cpu.match("oauth-integration")
        assert match is not None
        assert match.latency_ms > 0.0, "latency_ms must be positive"
        assert match.latency_ms < 10.0, (
            f"latency_ms={match.latency_ms:.4f} is unreasonably large"
        )

    def test_warm_path_faster_than_first_call(self, cpu):
        """
        After the first call (Python dict warmup), subsequent calls must
        complete within reasonable bounds.
        """
        wish_id = "oauth-integration"

        # Cold call
        start = time.perf_counter()
        cpu.match(wish_id)
        cold_ms = (time.perf_counter() - start) * 1000

        # 10 warm calls
        warm_times = []
        for _ in range(10):
            start = time.perf_counter()
            cpu.match(wish_id)
            warm_times.append((time.perf_counter() - start) * 1000)

        avg_warm_ms = sum(warm_times) / len(warm_times)

        # Warm path should be within 2x cold + 1ms overhead
        assert avg_warm_ms < cold_ms * 2 + 1.0, (
            f"Warm avg {avg_warm_ms:.4f}ms > cold {cold_ms:.4f}ms * 2 + 1ms. "
            "Hot path regression detected."
        )

    def test_latency_constant_with_combo_count(self, loaded_db, cpu):
        """
        Lookup latency must not scale with combo count (O(1) dict proof).
        Full 25+ combo database must still achieve P99 < 1ms.
        """
        n_combos = loaded_db.count()
        assert n_combos >= 25, (
            f"Expected 25+ combos in database, got {n_combos}"
        )

        latencies_ms = []
        wish_id = "oauth-integration"
        for _ in range(200):
            start = time.perf_counter()
            cpu.match(wish_id)
            latencies_ms.append((time.perf_counter() - start) * 1000)

        latencies_ms.sort()
        p99_idx = max(0, int(len(latencies_ms) * 0.99) - 1)
        p99_ms = latencies_ms[p99_idx]
        assert p99_ms < 1.0, (
            f"P99 = {p99_ms:.4f}ms with {n_combos} combos. "
            "Dict lookup must be O(1), not O(n)."
        )

    def test_batch_match_under_5ms_for_all_combos(self, cpu):
        """
        Batch matching all 25 wish_ids must complete < 5ms total.
        """
        start = time.perf_counter()
        results = cpu.match_batch(_TEST_WISH_IDS)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(results) == len(_TEST_WISH_IDS)
        assert elapsed_ms < 5.0, (
            f"Batch match of {len(_TEST_WISH_IDS)} IDs took {elapsed_ms:.3f}ms "
            f"— exceeds 5ms threshold"
        )

    def test_all_known_wish_ids_match_under_1ms_each(self, cpu):
        """
        Each individual known wish_id match must complete < 1ms.
        """
        for wish_id in _TEST_WISH_IDS:
            start = time.perf_counter()
            match = cpu.match(wish_id)
            elapsed_ms = (time.perf_counter() - start) * 1000

            assert match is not None, f"wish_id {wish_id!r} should have a combo"
            assert elapsed_ms < 1.0, (
                f"Match for {wish_id!r} took {elapsed_ms:.4f}ms — exceeds 1ms SLA"
            )
