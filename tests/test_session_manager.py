#!/usr/bin/env python3
"""
Stillwater Session Manager — Test Suite
Version: 1.0.0 | Rung: 641 | Persona: Skeptic Auditor

Skeptic mandate: Assume the implementation is wrong until proven correct.
Challenge every contract claim: expiry semantics, thread isolation,
null safety, type gates, idempotency, sort stability, and counter
accuracy. No prose confidence — every claim backed by assertion.

Run:
    cd /home/phuc/projects/stillwater
    python -m pytest tests/test_session_manager.py -v --tb=short
"""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Import path setup — must resolve before any stillwater imports
# ---------------------------------------------------------------------------

CLI_SRC = Path(__file__).resolve().parent.parent / "cli" / "src"
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))

from stillwater.session_manager import Session, SessionManager  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DEFAULT_SKILLS = ["prime-safety", "prime-coder"]
_NOW = 1_700_000_000  # Fixed epoch for deterministic tests


def _make_session(
    *,
    session_id: str = "test-uuid-1234",
    skill_pack: list[str] | None = None,
    active_task: str | None = None,
    evidence_dir: str | None = None,
    created_at: int = _NOW,
    expires_at: int = _NOW + 86400,
    closed: bool = False,
) -> Session:
    """Factory for hand-built Session objects."""
    return Session(
        session_id=session_id,
        skill_pack=skill_pack if skill_pack is not None else list(_DEFAULT_SKILLS),
        active_task=active_task,
        evidence_dir=evidence_dir,
        created_at=created_at,
        expires_at=expires_at,
        closed=closed,
    )


# ===========================================================================
# Group 1: Session dataclass — field contracts
# Skeptic perspective: Verify every field is stored as declared; default
# values must not silently coerce types; UUID must be a non-empty string.
# ===========================================================================


class TestSessionFields:
    """Skeptic: Are all fields stored exactly as provided? No coercion."""

    def test_all_fields_stored(self):
        s = _make_session(
            session_id="abc-123",
            skill_pack=["prime-safety"],
            active_task="write tests",
            evidence_dir="/tmp/evidence",
            created_at=_NOW,
            expires_at=_NOW + 3600,
            closed=False,
        )
        assert s.session_id == "abc-123"
        assert s.skill_pack == ["prime-safety"]
        assert s.active_task == "write tests"
        assert s.evidence_dir == "/tmp/evidence"
        assert s.created_at == _NOW
        assert s.expires_at == _NOW + 3600
        assert s.closed is False

    def test_closed_defaults_to_false(self):
        s = Session(
            session_id="x",
            skill_pack=[],
            active_task=None,
            evidence_dir=None,
            created_at=_NOW,
            expires_at=_NOW + 1,
        )
        assert s.closed is False

    def test_optional_fields_accept_none(self):
        s = _make_session(active_task=None, evidence_dir=None)
        assert s.active_task is None
        assert s.evidence_dir is None

    def test_skill_pack_is_independent_copy(self):
        # Skeptic: mutation of the original list must not affect the session.
        original = ["prime-safety"]
        mgr = SessionManager()
        session = mgr.create_session(skill_pack=original)
        original.append("injected-skill")
        assert "injected-skill" not in session.skill_pack

    def test_timestamps_are_int(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        assert isinstance(s.created_at, int), "created_at must be int, not float"
        assert isinstance(s.expires_at, int), "expires_at must be int, not float"


# ===========================================================================
# Group 2: Session.is_expired() and Session.is_active()
# Skeptic perspective: Expiry boundary is now >= expires_at, not now > expires_at.
# closed flag must trump time check — a freshly closed session must appear
# expired even with a far-future expires_at.
# ===========================================================================


class TestSessionExpiry:
    """Skeptic: Is expiry edge-exact? Does closed override time?"""

    def test_not_expired_when_future(self):
        future = int(time.time()) + 9999
        s = _make_session(expires_at=future)
        assert s.is_expired() is False
        assert s.is_active() is True

    def test_expired_when_past(self):
        past = int(time.time()) - 1
        s = _make_session(expires_at=past)
        assert s.is_expired() is True
        assert s.is_active() is False

    def test_closed_session_is_always_expired(self):
        # Closed with far-future TTL still counts as expired.
        s = _make_session(expires_at=int(time.time()) + 99999, closed=True)
        assert s.is_expired() is True
        assert s.is_active() is False

    def test_expiry_via_short_ttl_and_sleep(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS, ttl_seconds=1)
        assert s.is_active() is True
        time.sleep(1.1)
        assert s.is_expired() is True

    def test_is_active_is_inverse_of_is_expired(self):
        future = int(time.time()) + 9999
        s = _make_session(expires_at=future)
        assert s.is_active() == (not s.is_expired())

    def test_at_exact_expiry_boundary_is_expired(self):
        # now >= expires_at → expired. Pin time.time() to expires_at exactly.
        fixed_now = _NOW + 3600
        s = _make_session(expires_at=fixed_now)
        with patch("stillwater.session_manager.time.time", return_value=float(fixed_now)):
            assert s.is_expired() is True


# ===========================================================================
# Group 3: Session.ttl_remaining_seconds()
# Skeptic perspective: Must return 0 — not negative — when already expired.
# Must return an int, not a float.
# ===========================================================================


class TestTTLRemaining:
    """Skeptic: Does TTL clamp to 0? Is the return type int?"""

    def test_positive_ttl_when_active(self):
        future = int(time.time()) + 3600
        s = _make_session(expires_at=future)
        remaining = s.ttl_remaining_seconds()
        assert remaining > 0
        assert isinstance(remaining, int)

    def test_zero_when_expired(self):
        past = int(time.time()) - 10
        s = _make_session(expires_at=past)
        assert s.ttl_remaining_seconds() == 0

    def test_zero_when_closed(self):
        # Closed session: closed flag makes is_expired() True, but
        # ttl_remaining_seconds() uses raw time math — must still be >= 0.
        future = int(time.time()) + 9999
        s = _make_session(expires_at=future, closed=True)
        assert s.ttl_remaining_seconds() >= 0

    def test_never_returns_negative(self):
        # Far past — must clamp to 0, never negative.
        ancient = int(time.time()) - 100_000
        s = _make_session(expires_at=ancient)
        assert s.ttl_remaining_seconds() == 0


# ===========================================================================
# Group 4: Session.to_dict() / Session.from_dict() round-trip
# Skeptic perspective: Serialization must be lossless. from_dict must
# survive missing optional keys (null-safety). Required key absence must
# raise KeyError, not produce a silent None.
# ===========================================================================


class TestSerialisation:
    """Skeptic: Is the round-trip byte-for-byte identical? Are missing keys handled?"""

    def test_to_dict_contains_all_keys(self):
        s = _make_session()
        d = s.to_dict()
        expected_keys = {
            "session_id", "skill_pack", "active_task",
            "evidence_dir", "created_at", "expires_at", "closed",
        }
        assert set(d.keys()) == expected_keys

    def test_round_trip_full(self):
        s = _make_session(
            session_id="rt-001",
            skill_pack=["prime-safety", "prime-coder"],
            active_task="round-trip test",
            evidence_dir="/tmp/rt",
            created_at=_NOW,
            expires_at=_NOW + 7200,
            closed=False,
        )
        restored = Session.from_dict(s.to_dict())
        assert restored.session_id == s.session_id
        assert restored.skill_pack == s.skill_pack
        assert restored.active_task == s.active_task
        assert restored.evidence_dir == s.evidence_dir
        assert restored.created_at == s.created_at
        assert restored.expires_at == s.expires_at
        assert restored.closed == s.closed

    def test_from_dict_missing_optional_fields_default_to_none(self):
        minimal = {
            "session_id": "min-001",
            "created_at": _NOW,
            "expires_at": _NOW + 3600,
        }
        s = Session.from_dict(minimal)
        assert s.active_task is None
        assert s.evidence_dir is None
        assert s.skill_pack == []
        assert s.closed is False

    def test_from_dict_closed_defaults_false_when_missing(self):
        d = {
            "session_id": "c-001",
            "created_at": _NOW,
            "expires_at": _NOW + 3600,
        }
        s = Session.from_dict(d)
        assert s.closed is False

    def test_to_dict_skill_pack_is_copy(self):
        s = _make_session(skill_pack=["prime-safety"])
        d = s.to_dict()
        d["skill_pack"].append("injected")
        assert "injected" not in s.skill_pack

    def test_from_dict_timestamps_coerced_to_int(self):
        # Stored as float (e.g. from JSON parsing with imprecision) must
        # be coerced to int on reconstruction.
        d = {
            "session_id": "ts-float",
            "created_at": float(_NOW),
            "expires_at": float(_NOW + 3600),
        }
        s = Session.from_dict(d)
        assert isinstance(s.created_at, int)
        assert isinstance(s.expires_at, int)


# ===========================================================================
# Group 5: SessionManager.__init__ — constructor validation
# Skeptic perspective: Zero and negative TTLs must be rejected loudly.
# Positive TTL must be stored verbatim.
# ===========================================================================


class TestSessionManagerInit:
    """Skeptic: Does the constructor enforce the positive-TTL invariant?"""

    def test_default_ttl_is_86400(self):
        mgr = SessionManager()
        assert mgr._ttl_seconds == 86400

    def test_custom_positive_ttl_accepted(self):
        mgr = SessionManager(default_ttl_seconds=3600)
        assert mgr._ttl_seconds == 3600

    def test_zero_ttl_raises_value_error(self):
        with pytest.raises(ValueError):
            SessionManager(default_ttl_seconds=0)

    def test_negative_ttl_raises_value_error(self):
        with pytest.raises(ValueError):
            SessionManager(default_ttl_seconds=-1)

    def test_minimum_valid_ttl_is_1(self):
        mgr = SessionManager(default_ttl_seconds=1)
        assert mgr._ttl_seconds == 1


# ===========================================================================
# Group 6: SessionManager.create_session()
# Skeptic perspective: Session IDs must be unique across concurrent calls.
# skill_pack must be validated as list. Per-session TTL override must be
# respected over the manager default.
# ===========================================================================


class TestCreateSession:
    """Skeptic: Are IDs unique? Are type gates enforced? Does custom TTL win?"""

    def test_returns_session_with_uuid(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        assert isinstance(s.session_id, str)
        assert len(s.session_id) == 36  # UUID4 canonical form

    def test_session_ids_are_unique(self):
        mgr = SessionManager()
        ids = {mgr.create_session(skill_pack=[]).session_id for _ in range(100)}
        assert len(ids) == 100, "ID collision detected in 100 sessions"

    def test_custom_ttl_overrides_default(self):
        mgr = SessionManager(default_ttl_seconds=86400)
        now_before = int(time.time())
        s = mgr.create_session(skill_pack=[], ttl_seconds=300)
        now_after = int(time.time())
        assert now_before + 300 <= s.expires_at <= now_after + 300

    def test_default_ttl_used_when_none(self):
        mgr = SessionManager(default_ttl_seconds=7200)
        now_before = int(time.time())
        s = mgr.create_session(skill_pack=[])
        now_after = int(time.time())
        assert now_before + 7200 <= s.expires_at <= now_after + 7200

    def test_non_list_skill_pack_raises_value_error(self):
        mgr = SessionManager()
        with pytest.raises(ValueError):
            mgr.create_session(skill_pack="prime-safety")  # type: ignore[arg-type]

    def test_tuple_skill_pack_raises_value_error(self):
        mgr = SessionManager()
        with pytest.raises(ValueError):
            mgr.create_session(skill_pack=("prime-safety",))  # type: ignore[arg-type]

    def test_none_skill_pack_raises_value_error(self):
        mgr = SessionManager()
        with pytest.raises(ValueError):
            mgr.create_session(skill_pack=None)  # type: ignore[arg-type]

    def test_empty_skill_pack_is_valid(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        assert s.skill_pack == []

    def test_optional_fields_stored(self):
        mgr = SessionManager()
        s = mgr.create_session(
            skill_pack=_DEFAULT_SKILLS,
            active_task="test task",
            evidence_dir="/tmp/ev",
        )
        assert s.active_task == "test task"
        assert s.evidence_dir == "/tmp/ev"

    def test_created_session_registered_in_manager(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        assert mgr.get_session(s.session_id) is s


# ===========================================================================
# Group 7: SessionManager.get_session()
# Skeptic perspective: Unknown ID must return None — not raise. Expired
# session must return None even if present in memory. Active session must
# return the exact same object.
# ===========================================================================


class TestGetSession:
    """Skeptic: Does get_session silently hide expired sessions? No surprise raises?"""

    def test_returns_none_for_unknown_id(self):
        mgr = SessionManager()
        assert mgr.get_session("no-such-id") is None

    def test_returns_session_when_active(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        found = mgr.get_session(s.session_id)
        assert found is s

    def test_returns_none_after_expiry(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS, ttl_seconds=1)
        time.sleep(1.1)
        assert mgr.get_session(s.session_id) is None

    def test_returns_none_after_close(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        mgr.close_session(s.session_id)
        assert mgr.get_session(s.session_id) is None


# ===========================================================================
# Group 8: SessionManager.close_session()
# Skeptic perspective: Idempotency must hold — double-close and close of
# unknown ID must be no-ops, not exceptions.
# ===========================================================================


class TestCloseSession:
    """Skeptic: Is close truly idempotent? Does it mark closed correctly?"""

    def test_close_marks_session_closed(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        mgr.close_session(s.session_id)
        assert s.closed is True

    def test_close_idempotent_on_already_closed(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        mgr.close_session(s.session_id)
        mgr.close_session(s.session_id)  # second call must not raise
        assert s.closed is True

    def test_close_idempotent_on_unknown_id(self):
        mgr = SessionManager()
        mgr.close_session("ghost-session-id")  # must not raise

    def test_closed_session_absent_from_active_list(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        mgr.close_session(s.session_id)
        assert s not in mgr.list_active()


# ===========================================================================
# Group 9: SessionManager.list_active() and list_all()
# Skeptic perspective: list_active must exclude expired AND closed sessions.
# list_all must include everything regardless of state. Both must sort by
# created_at ascending — not insertion order, not alphabetical.
# ===========================================================================


class TestListing:
    """Skeptic: Do active/all listings have correct membership and ordering?"""

    def test_list_active_excludes_expired(self):
        mgr = SessionManager()
        active = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        expired = mgr.create_session(skill_pack=_DEFAULT_SKILLS, ttl_seconds=1)
        time.sleep(1.1)
        result = mgr.list_active()
        assert active in result
        assert expired not in result

    def test_list_active_excludes_closed(self):
        mgr = SessionManager()
        live = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        closed = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        mgr.close_session(closed.session_id)
        result = mgr.list_active()
        assert live in result
        assert closed not in result

    def test_list_active_empty_initially(self):
        mgr = SessionManager()
        assert mgr.list_active() == []

    def test_list_all_includes_closed(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        mgr.close_session(s.session_id)
        assert s in mgr.list_all()

    def test_list_all_includes_expired(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS, ttl_seconds=1)
        time.sleep(1.1)
        assert s in mgr.list_all()

    def test_list_active_sorted_by_created_at(self):
        mgr = SessionManager()
        s1 = mgr.create_session(skill_pack=[])
        time.sleep(0.01)
        s2 = mgr.create_session(skill_pack=[])
        time.sleep(0.01)
        s3 = mgr.create_session(skill_pack=[])
        result = mgr.list_active()
        created_ats = [s.created_at for s in result]
        assert created_ats == sorted(created_ats), "list_active not sorted by created_at"

    def test_list_all_sorted_by_created_at(self):
        mgr = SessionManager()
        s1 = mgr.create_session(skill_pack=[])
        mgr.close_session(s1.session_id)
        s2 = mgr.create_session(skill_pack=[])
        result = mgr.list_all()
        assert result[0].created_at <= result[-1].created_at


# ===========================================================================
# Group 10: SessionManager.purge_expired()
# Skeptic perspective: purge must remove EXACTLY the expired/closed set.
# Return value must be the count of removed sessions. Active sessions
# must survive a purge. A second purge on a clean manager must return 0.
# ===========================================================================


class TestPurgeExpired:
    """Skeptic: Does purge count correctly? Does it spare active sessions?"""

    def test_purge_removes_expired_sessions(self):
        mgr = SessionManager()
        mgr.create_session(skill_pack=_DEFAULT_SKILLS, ttl_seconds=1)
        mgr.create_session(skill_pack=_DEFAULT_SKILLS, ttl_seconds=1)
        live = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        time.sleep(1.1)
        removed = mgr.purge_expired()
        assert removed == 2
        assert mgr.session_count() == 1
        assert mgr.get_session(live.session_id) is live

    def test_purge_removes_closed_sessions(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        mgr.close_session(s.session_id)
        removed = mgr.purge_expired()
        assert removed == 1
        assert mgr.session_count() == 0

    def test_purge_returns_zero_when_nothing_to_remove(self):
        mgr = SessionManager()
        mgr.create_session(skill_pack=_DEFAULT_SKILLS)
        removed = mgr.purge_expired()
        assert removed == 0

    def test_purge_on_empty_manager_returns_zero(self):
        mgr = SessionManager()
        assert mgr.purge_expired() == 0

    def test_second_purge_returns_zero(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=_DEFAULT_SKILLS, ttl_seconds=1)
        time.sleep(1.1)
        mgr.purge_expired()
        assert mgr.purge_expired() == 0


# ===========================================================================
# Group 11: SessionManager.session_count()
# Skeptic perspective: Count must track every session including expired and
# closed ones until purged. Must not silently drop or double-count.
# ===========================================================================


class TestSessionCount:
    """Skeptic: Is the counter accurate across create/close/purge operations?"""

    def test_count_zero_on_new_manager(self):
        mgr = SessionManager()
        assert mgr.session_count() == 0

    def test_count_increments_on_create(self):
        mgr = SessionManager()
        mgr.create_session(skill_pack=[])
        assert mgr.session_count() == 1
        mgr.create_session(skill_pack=[])
        assert mgr.session_count() == 2

    def test_close_does_not_decrement_count(self):
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        mgr.close_session(s.session_id)
        assert mgr.session_count() == 1

    def test_purge_decrements_count(self):
        mgr = SessionManager()
        mgr.create_session(skill_pack=[], ttl_seconds=1)
        time.sleep(1.1)
        mgr.purge_expired()
        assert mgr.session_count() == 0


# ===========================================================================
# Group 12: Thread safety
# Skeptic perspective: Concurrent create_session calls must not produce
# duplicate IDs or corrupt internal state. Concurrent close/get must not
# raise or return a partially-mutated session.
# ===========================================================================


class TestThreadSafety:
    """Skeptic: Does the lock actually prevent races? Prove it under load."""

    def test_concurrent_create_produces_unique_ids(self):
        mgr = SessionManager()
        results: list[str] = []
        lock = threading.Lock()

        def worker():
            s = mgr.create_session(skill_pack=[])
            with lock:
                results.append(s.session_id)

        threads = [threading.Thread(target=worker) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 50
        assert len(set(results)) == 50, "Thread-concurrent IDs collided"

    def test_concurrent_create_and_close_no_exception(self):
        mgr = SessionManager()
        sessions: list[Session] = []
        errors: list[Exception] = []
        lock = threading.Lock()

        def creator():
            try:
                s = mgr.create_session(skill_pack=[])
                with lock:
                    sessions.append(s)
            except Exception as e:
                with lock:
                    errors.append(e)

        def closer():
            with lock:
                snap = list(sessions)
            for s in snap:
                try:
                    mgr.close_session(s.session_id)
                except Exception as e:
                    with lock:
                        errors.append(e)

        threads = [threading.Thread(target=creator) for _ in range(30)]
        threads += [threading.Thread(target=closer) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Exceptions during concurrent operations: {errors}"

    def test_concurrent_count_consistent(self):
        mgr = SessionManager()
        n = 40

        def creator():
            mgr.create_session(skill_pack=[])

        threads = [threading.Thread(target=creator) for _ in range(n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert mgr.session_count() == n
