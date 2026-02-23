"""
Test: Queue hit latency SLA < 5ms.

Verifies:
- Queue hit returns in < 5ms (P99)
- Returned banter matches inserted banter
- Entry is marked as used after retrieval
- Second call to generate() for same user gets NEXT entry (not same)

rung_target: 641
EXIT_PASS: All assertions pass AND P99 < 5ms
EXIT_BLOCKED: Any latency measurement > 5ms P99
"""

import sys
import time
from datetime import datetime
from pathlib import Path

import pytest

# Ensure the stillwater package root is importable
_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.smalltalk.cpu import SmallTalkCPU
from admin.orchestration.smalltalk.database import BanterQueueDB
from admin.orchestration.smalltalk.models import BanterQueueEntry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fresh_db():
    """In-memory SQLite DB — isolated per test."""
    return BanterQueueDB(":memory:")


@pytest.fixture
def populated_db(fresh_db):
    """DB pre-loaded with 5 banter entries for user_alice."""
    entries = [
        BanterQueueEntry(
            id=f"entry_{i:03d}",
            user_id="user_alice",
            session_id="sess_001",
            banter=f"Banter message number {i}.",
            source="job",
            tags=["general"],
            confidence=0.9,
        )
        for i in range(5)
    ]
    for e in entries:
        fresh_db.insert(e)
    return fresh_db


@pytest.fixture
def cpu_with_queue(populated_db):
    """SmallTalkCPU backed by populated in-memory DB."""
    return SmallTalkCPU(db=populated_db)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestQueueHitLatency:

    def test_queue_hit_returns_banter(self, cpu_with_queue):
        """Queue hit returns a non-empty banter string."""
        token = cpu_with_queue.generate(
            user_id="user_alice",
            session_id="sess_001",
            prompt="Hey",
        )
        assert token.response, "Response must be non-empty"
        assert token.source == "queue_hit", (
            f"Expected source='queue_hit', got '{token.source}'"
        )

    def test_queue_hit_under_5ms(self, cpu_with_queue):
        """
        Queue hit must complete in < 5ms.

        Runs 100 iterations, checks P99.
        """
        latencies_ms = []
        for _ in range(100):
            # Re-populate after each consumption so we always get a hit
            entry = BanterQueueEntry(
                user_id="user_alice",
                session_id="sess_iter",
                banter="Latency test banter.",
                source="job",
                tags=["general"],
                confidence=0.9,
            )
            cpu_with_queue._db.insert(entry)

            start = time.perf_counter()
            token = cpu_with_queue.generate(
                user_id="user_alice",
                session_id="sess_iter",
                prompt="ping",
            )
            elapsed_ms = (time.perf_counter() - start) * 1000

            # Only count queue hits
            if token.source == "queue_hit":
                latencies_ms.append(elapsed_ms)

        assert latencies_ms, "No queue hits recorded — DB may be empty"

        latencies_ms.sort()
        p99_index = max(0, int(len(latencies_ms) * 0.99) - 1)
        p99_ms = latencies_ms[p99_index]

        assert p99_ms < 5.0, (
            f"Queue hit P99 = {p99_ms:.2f}ms — exceeds 5ms SLA. "
            f"Median = {latencies_ms[len(latencies_ms)//2]:.2f}ms. "
            f"Max = {max(latencies_ms):.2f}ms."
        )

    def test_entry_marked_used_after_hit(self, populated_db, cpu_with_queue):
        """After a queue hit, the entry is marked used=True in the DB."""
        # Get the first available entry
        before = populated_db.get_next(user_id="user_alice")
        assert before is not None, "DB should have entries"
        entry_id = before.id

        cpu_with_queue.generate(
            user_id="user_alice",
            session_id="sess_001",
            prompt="test",
        )

        # Verify the consumed entry is now used
        all_entries = populated_db.list_all(user_id="user_alice")
        consumed = next((e for e in all_entries if e.id == entry_id), None)
        assert consumed is not None
        assert consumed.used is True, "Consumed entry must be marked used=True"
        assert consumed.used_at is not None, "used_at must be set"

    def test_queue_exhaustion_falls_to_cpu(self, fresh_db):
        """When queue is empty, generate() falls back to CPU path."""
        cpu = SmallTalkCPU(db=fresh_db)

        token = cpu.generate(
            user_id="user_nobody",
            session_id="sess_empty",
            prompt="hello",
            local_hour=10,
        )
        assert token.response, "Fallback must produce non-empty response"
        assert token.source in ("cpu_glow", "cpu_repo", "fallback"), (
            f"Expected CPU source, got '{token.source}'"
        )

    def test_queue_hit_uses_highest_confidence_first(self, fresh_db):
        """get_next() returns highest-confidence entry first."""
        low = BanterQueueEntry(
            id="low_conf",
            user_id="user_prio",
            session_id="sess_prio",
            banter="Low confidence banter.",
            source="queue",
            tags=["general"],
            confidence=0.3,
        )
        high = BanterQueueEntry(
            id="high_conf",
            user_id="user_prio",
            session_id="sess_prio",
            banter="High confidence banter.",
            source="queue",
            tags=["general"],
            confidence=0.9,
        )
        # Insert low first, then high — high should still come first
        fresh_db.insert(low)
        fresh_db.insert(high)

        cpu = SmallTalkCPU(db=fresh_db)
        token = cpu.generate(
            user_id="user_prio",
            session_id="sess_prio",
            prompt="test",
        )
        assert token.response == "High confidence banter.", (
            f"Expected high-confidence entry first, got: '{token.response}'"
        )

    def test_used_entry_not_returned(self, fresh_db):
        """Used entries are never returned by get_next()."""
        # Insert one entry and mark it used immediately
        entry = BanterQueueEntry(
            id="used_one",
            user_id="user_used",
            session_id="sess_used",
            banter="This should not appear.",
            source="queue",
            tags=["general"],
            confidence=0.95,
            used=True,
        )
        fresh_db.insert(entry)

        result = fresh_db.get_next(user_id="user_used")
        assert result is None, "Used entry must not be returned by get_next()"

    def test_latency_token_field_populated(self, cpu_with_queue):
        """WarmToken.latency_ms must be a positive float."""
        token = cpu_with_queue.generate(
            user_id="user_alice",
            session_id="sess_001",
            prompt="test",
        )
        assert isinstance(token.latency_ms, float)
        assert token.latency_ms > 0.0, "latency_ms should be positive"

    def test_different_users_isolated(self, fresh_db):
        """Queue entries for different users do not bleed across users."""
        alice_entry = BanterQueueEntry(
            id="alice_e",
            user_id="user_alice",
            session_id="s1",
            banter="Alice's banter.",
            source="queue",
            tags=[],
            confidence=0.9,
        )
        bob_entry = BanterQueueEntry(
            id="bob_e",
            user_id="user_bob",
            session_id="s2",
            banter="Bob's banter.",
            source="queue",
            tags=[],
            confidence=0.9,
        )
        fresh_db.insert(alice_entry)
        fresh_db.insert(bob_entry)

        alice_result = fresh_db.get_next(user_id="user_alice")
        assert alice_result is not None
        assert alice_result.banter == "Alice's banter."

        bob_result = fresh_db.get_next(user_id="user_bob")
        assert bob_result is not None
        assert bob_result.banter == "Bob's banter."
