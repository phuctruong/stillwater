"""
Test: Queue persistence across sessions.

Verifies:
- Entries written to a file-backed DB survive process restart simulation
- mark_used() persists to disk
- update_feedback() persists to disk
- In-memory DB correctly isolates between test instances
- Schema migration: DB created fresh when file doesn't exist

rung_target: 641
EXIT_PASS: All persistence operations survive close/reopen cycles
EXIT_BLOCKED: Data lost after close+reopen
"""

import json
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.smalltalk.database import BanterQueueDB
from admin.orchestration.smalltalk.models import BanterQueueEntry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_db_path(tmp_path):
    """Return a path to a temp SQLite file (not yet created)."""
    return str(tmp_path / "banter_test.db")


@pytest.fixture
def alice_entry():
    return BanterQueueEntry(
        id="persist_001",
        user_id="user_alice",
        session_id="sess_persist_01",
        banter="Persisted banter message for Alice.",
        source="job",
        source_id="job_001",
        tags=["oauth", "celebration"],
        confidence=0.92,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPersistence:

    def test_entry_survives_close_reopen(self, tmp_db_path, alice_entry):
        """Entry written to file DB is readable after close+reopen."""
        # Write
        db1 = BanterQueueDB(tmp_db_path)
        db1.insert(alice_entry)
        db1.close()

        # Reopen (simulating process restart)
        db2 = BanterQueueDB(tmp_db_path)
        result = db2.get_next(user_id="user_alice")
        db2.close()

        assert result is not None, "Entry must survive close+reopen"
        assert result.id == alice_entry.id
        assert result.banter == alice_entry.banter
        assert result.tags == alice_entry.tags

    def test_mark_used_persists(self, tmp_db_path, alice_entry):
        """mark_used() persists to disk."""
        db1 = BanterQueueDB(tmp_db_path)
        db1.insert(alice_entry)
        db1.mark_used(alice_entry.id)
        db1.close()

        db2 = BanterQueueDB(tmp_db_path)
        # Should not be returned by get_next() since used=True
        result = db2.get_next(user_id="user_alice")
        db2.close()

        assert result is None, "Used entry must not be returned after close+reopen"

    def test_feedback_persists(self, tmp_db_path, alice_entry):
        """feedback_score update persists to disk."""
        db1 = BanterQueueDB(tmp_db_path)
        db1.insert(alice_entry)
        db1.mark_used(alice_entry.id)
        db1.update_feedback(alice_entry.id, score=5)
        db1.close()

        db2 = BanterQueueDB(tmp_db_path)
        all_entries = db2.list_all(user_id="user_alice")
        db2.close()

        assert len(all_entries) == 1
        assert all_entries[0].feedback_score == 5, (
            f"Expected feedback_score=5, got {all_entries[0].feedback_score}"
        )

    def test_multiple_users_same_db(self, tmp_db_path):
        """Multiple users' data coexists in same DB without cross-contamination."""
        db = BanterQueueDB(tmp_db_path)

        users = ["alice", "bob", "charlie"]
        for uid in users:
            for i in range(3):
                db.insert(BanterQueueEntry(
                    user_id=uid,
                    session_id=f"sess_{uid}",
                    banter=f"Banter for {uid} #{i}",
                    source="queue",
                    tags=[uid],
                    confidence=0.8,
                ))
        db.close()

        db2 = BanterQueueDB(tmp_db_path)
        for uid in users:
            count = db2.count_available(uid)
            assert count == 3, (
                f"Expected 3 entries for {uid}, got {count}"
            )
        db2.close()

    def test_expired_entry_not_returned(self, tmp_db_path):
        """Entries past expires_at are not returned by get_next()."""
        db = BanterQueueDB(tmp_db_path)
        expired = BanterQueueEntry(
            id="exp_001",
            user_id="user_x",
            session_id="sess_x",
            banter="This has expired.",
            source="queue",
            tags=[],
            confidence=0.9,
            expires_at=datetime.utcnow() - timedelta(hours=1),  # in the past
        )
        db.insert(expired)
        db.close()

        db2 = BanterQueueDB(tmp_db_path)
        result = db2.get_next(user_id="user_x")
        db2.close()

        assert result is None, "Expired entry must not be returned"

    def test_count_available_excludes_used_and_expired(self, tmp_db_path):
        """count_available() correctly excludes used and expired entries."""
        db = BanterQueueDB(tmp_db_path)

        # Fresh entry
        e1 = BanterQueueEntry(
            id="count_e1",
            user_id="count_user",
            session_id="s",
            banter="Fresh.",
            source="queue",
            tags=[],
            confidence=0.9,
        )
        # Expired
        e2 = BanterQueueEntry(
            id="count_e2",
            user_id="count_user",
            session_id="s",
            banter="Expired.",
            source="queue",
            tags=[],
            confidence=0.9,
            expires_at=datetime.utcnow() - timedelta(hours=1),
        )
        # Used
        e3 = BanterQueueEntry(
            id="count_e3",
            user_id="count_user",
            session_id="s",
            banter="Used.",
            source="queue",
            tags=[],
            confidence=0.9,
            used=True,
        )
        db.insert(e1)
        db.insert(e2)
        db.insert(e3)
        db.close()

        db2 = BanterQueueDB(tmp_db_path)
        count = db2.count_available("count_user")
        db2.close()

        assert count == 1, (
            f"Expected exactly 1 available entry, got {count}"
        )

    def test_in_memory_db_isolated(self):
        """Two :memory: DBs are completely independent."""
        db_a = BanterQueueDB(":memory:")
        db_b = BanterQueueDB(":memory:")

        db_a.insert(BanterQueueEntry(
            user_id="user_shared",
            session_id="s",
            banter="Only in A.",
            source="queue",
            tags=[],
            confidence=0.9,
        ))

        # B should be empty
        result = db_b.get_next(user_id="user_shared")
        assert result is None, "In-memory DBs must be isolated"

    def test_schema_auto_created(self, tmp_db_path):
        """DB file and schema are auto-created on first open."""
        path = Path(tmp_db_path)
        assert not path.exists(), "Precondition: file must not exist yet"

        db = BanterQueueDB(tmp_db_path)
        assert path.exists(), "DB file must be auto-created"

        # Must be usable immediately
        db.insert(BanterQueueEntry(
            user_id="schema_user",
            session_id="s",
            banter="Schema test.",
            source="queue",
            tags=[],
            confidence=0.9,
        ))
        result = db.get_next(user_id="schema_user")
        assert result is not None
        db.close()

    def test_tags_serialize_deserialize(self, tmp_db_path):
        """Tags list is correctly serialized to JSON and deserialized."""
        original_tags = ["oauth", "security", "celebration", "job"]
        db = BanterQueueDB(tmp_db_path)
        db.insert(BanterQueueEntry(
            id="tag_test",
            user_id="tag_user",
            session_id="s",
            banter="Tag test banter.",
            source="job",
            tags=original_tags,
            confidence=0.9,
        ))
        db.close()

        db2 = BanterQueueDB(tmp_db_path)
        result = db2.get_next(user_id="tag_user")
        db2.close()

        assert result is not None
        assert result.tags == original_tags, (
            f"Tags mismatch: expected {original_tags}, got {result.tags}"
        )

    def test_feedback_score_validation(self, tmp_db_path):
        """update_feedback rejects scores outside 1-5."""
        db = BanterQueueDB(tmp_db_path)
        db.insert(BanterQueueEntry(
            id="feedback_val",
            user_id="fv_user",
            session_id="s",
            banter="Feedback test.",
            source="queue",
            tags=[],
            confidence=0.9,
        ))
        db.mark_used("feedback_val")

        with pytest.raises(ValueError):
            db.update_feedback("feedback_val", score=0)

        with pytest.raises(ValueError):
            db.update_feedback("feedback_val", score=6)

        db.close()
