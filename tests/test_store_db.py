"""
tests/test_store_db.py — Unit tests for src/store/db.py (_Store, get_store).

Coverage:
  - reset(): clears all data
  - create_api_key(): returns valid APIKey, stores correctly
  - get_api_key_by_id(): finds key or returns None
  - get_api_key_by_hash(): finds key or returns None
  - update_api_key(): mutates stored fields, raises KeyError for unknown
  - list_api_keys(): returns all stored keys
  - create_skill(): stores ReviewRecord
  - get_skill(): finds record or returns None
  - get_skill_by_name(): finds by skill_name
  - update_skill(): mutates stored fields, raises KeyError for unknown
  - list_skills(): no filter, status filter, pagination, sort order
  - count_recent_submissions(): counts within window, returns 0 for unknown key
  - save/load(): round-trip persists and restores data
  - load(): creates data_dir if missing

Rung target: 641 (in-process, no HTTP, no external dependencies)
Network: OFF — no real HTTP calls
Persona: Dragon Rider (Phuc's digital twin) — pragmatic founder testing.
  Focus: data integrity, persistence round-trips, every CRUD edge case.
  Philosophy: "If the store is wrong, everything built on top of it is wrong."
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# Ensure store package is importable from project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from store.db import _Store, get_store  # noqa: E402
from store.models import APIKey, ContentType, ReviewRecord, SkillStatus  # noqa: E402


# ===========================================================================
# Helpers
# ===========================================================================

def _make_api_key(
    store: _Store,
    key_id: str = "acct_test01",
    key_hash: str = "hash_test01",
    name: str = "Test User",
    account_type: str = "human",
    description: str = "A test account",
) -> APIKey:
    """Helper: create an APIKey in the store with sensible defaults."""
    return store.create_api_key(
        key_id=key_id,
        key_hash=key_hash,
        name=name,
        account_type=account_type,
        description=description,
    )


def _make_review_record(
    skill_id: str = "skill-001",
    skill_name: str = "test-skill",
    key_id: str = "acct_test01",
    status: SkillStatus = SkillStatus.pending,
    submitted_at: datetime | None = None,
) -> ReviewRecord:
    """Helper: build a ReviewRecord with sensible defaults."""
    if submitted_at is None:
        submitted_at = datetime.now(timezone.utc)
    return ReviewRecord(
        skill_id=skill_id,
        skill_name=skill_name,
        content_type=ContentType.skill,
        author="dragon-rider",
        key_id=key_id,
        rung_claimed=641,
        skill_content="# Test skill content\nThis is valid content.",
        submitted_at=submitted_at,
        status=status,
    )


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def store() -> _Store:
    """
    Dragon Rider fixture: always start with a clean slate.
    Never reuse the module-level singleton — create a fresh _Store() instance
    and reset() it to guarantee zero state bleed between tests.
    """
    s = _Store()
    s.reset()
    return s


# ===========================================================================
# CHECKPOINT 1: Lifecycle — reset, singleton
# ===========================================================================

class TestLifecycle:
    """
    Dragon Rider perspective: the store must be perfectly clean between
    operations. State bleed = silent data corruption = trust-destroying bugs.
    reset() is the foundation of every test in this file.
    """

    def test_reset_clears_api_keys(self, store: _Store) -> None:
        """reset() removes all API keys created before the call."""
        _make_api_key(store, key_id="acct_aaa", key_hash="hash_aaa")
        _make_api_key(store, key_id="acct_bbb", key_hash="hash_bbb")
        assert len(store.list_api_keys()) == 2

        store.reset()

        assert store.list_api_keys() == []

    def test_reset_clears_skills(self, store: _Store) -> None:
        """reset() removes all skills created before the call."""
        store.create_skill(_make_review_record(skill_id="s1", skill_name="alpha-skill"))
        store.create_skill(_make_review_record(skill_id="s2", skill_name="beta-skill"))
        records, total = store.list_skills()
        assert total == 2

        store.reset()

        records_after, total_after = store.list_skills()
        assert total_after == 0
        assert records_after == []

    def test_reset_clears_both_collections_atomically(self, store: _Store) -> None:
        """reset() leaves both api_keys and skills empty in the same call."""
        _make_api_key(store)
        store.create_skill(_make_review_record())

        store.reset()

        assert store.list_api_keys() == []
        _, skill_count = store.list_skills()
        assert skill_count == 0

    def test_get_store_returns_same_singleton(self) -> None:
        """get_store() must always return the same module-level _Store instance."""
        s1 = get_store()
        s2 = get_store()
        assert s1 is s2, "get_store() must return the same singleton object"

    def test_fresh_store_is_empty(self) -> None:
        """A freshly constructed _Store() (no load) starts with no data."""
        fresh = _Store()
        fresh.reset()
        assert fresh.list_api_keys() == []
        _, total = fresh.list_skills()
        assert total == 0


# ===========================================================================
# CHECKPOINT 2: API Key CRUD
# ===========================================================================

class TestAPIKeyCRUD:
    """
    Dragon Rider perspective: API keys are the authentication backbone.
    Every field must round-trip exactly. Wrong hash lookup = auth bypass.
    KeyError on missing update = fail-closed (never silently succeed).
    """

    def test_create_api_key_returns_apikey_instance(self, store: _Store) -> None:
        """create_api_key() must return an APIKey Pydantic model, not a raw dict."""
        key = _make_api_key(store)
        assert isinstance(key, APIKey)

    def test_create_api_key_fields_match_input(self, store: _Store) -> None:
        """The returned APIKey must carry exactly the fields passed in."""
        key = store.create_api_key(
            key_id="acct_precise",
            key_hash="hash_precise_abc123",
            name="Precise Tester",
            account_type="bot",
            description="Precision account",
        )
        assert key.key_id == "acct_precise"
        assert key.key_hash == "hash_precise_abc123"
        assert key.name == "Precise Tester"
        assert key.account_type == "bot"
        assert key.description == "Precision account"

    def test_create_api_key_default_account_type_is_human(self, store: _Store) -> None:
        """Omitting account_type must default to 'human'."""
        key = store.create_api_key(
            key_id="acct_default", key_hash="hash_default", name="Default User"
        )
        assert key.account_type == "human"

    def test_get_api_key_by_id_finds_created_key(self, store: _Store) -> None:
        """get_api_key_by_id() must return the key that was just created."""
        _make_api_key(store, key_id="acct_find_me", key_hash="hash_find_me")
        result = store.get_api_key_by_id("acct_find_me")
        assert result is not None
        assert result.key_id == "acct_find_me"

    def test_get_api_key_by_id_returns_none_for_unknown(self, store: _Store) -> None:
        """get_api_key_by_id() must return None for a key_id that was never created."""
        result = store.get_api_key_by_id("acct_ghost")
        assert result is None

    def test_get_api_key_by_hash_finds_created_key(self, store: _Store) -> None:
        """get_api_key_by_hash() must return the key matching that exact hash."""
        _make_api_key(store, key_id="acct_byhash", key_hash="unique_hash_xyz999")
        result = store.get_api_key_by_hash("unique_hash_xyz999")
        assert result is not None
        assert result.key_hash == "unique_hash_xyz999"
        assert result.key_id == "acct_byhash"

    def test_get_api_key_by_hash_returns_none_for_unknown(self, store: _Store) -> None:
        """get_api_key_by_hash() must return None if no key has that hash."""
        result = store.get_api_key_by_hash("no_such_hash_ever")
        assert result is None

    def test_get_api_key_by_hash_does_not_match_partial(self, store: _Store) -> None:
        """get_api_key_by_hash() must not match a prefix/substring of the stored hash."""
        _make_api_key(store, key_id="acct_partial", key_hash="full_hash_abcdef1234")
        # Query with only the first 9 chars — must NOT match
        result = store.get_api_key_by_hash("full_hash")
        assert result is None

    def test_update_api_key_updates_fields(self, store: _Store) -> None:
        """update_api_key() must apply the given dict updates to the stored record."""
        _make_api_key(store, key_id="acct_upd")
        store.update_api_key("acct_upd", {"reputation": 1.5, "submission_count": 3})
        updated = store.get_api_key_by_id("acct_upd")
        assert updated is not None
        assert updated.reputation == 1.5
        assert updated.submission_count == 3

    def test_update_api_key_raises_keyerror_for_unknown(self, store: _Store) -> None:
        """update_api_key() must raise KeyError if key_id does not exist."""
        with pytest.raises(KeyError, match="acct_ghost"):
            store.update_api_key("acct_ghost", {"reputation": 1.0})

    def test_list_api_keys_returns_all_created(self, store: _Store) -> None:
        """list_api_keys() must return exactly as many keys as were created."""
        _make_api_key(store, key_id="acct_01", key_hash="hash_01")
        _make_api_key(store, key_id="acct_02", key_hash="hash_02")
        _make_api_key(store, key_id="acct_03", key_hash="hash_03")
        keys = store.list_api_keys()
        assert len(keys) == 3
        ids = {k.key_id for k in keys}
        assert ids == {"acct_01", "acct_02", "acct_03"}

    def test_list_api_keys_empty_on_fresh_store(self, store: _Store) -> None:
        """list_api_keys() on a fresh/reset store returns an empty list."""
        assert store.list_api_keys() == []


# ===========================================================================
# CHECKPOINT 3: Skill / ReviewRecord CRUD
# ===========================================================================

class TestSkillCRUD:
    """
    Dragon Rider perspective: skills are the product. Every submission must
    be stored verbatim and retrieved without corruption. The review pipeline
    (pending -> accepted/rejected) depends on exact field semantics.
    """

    def test_create_skill_returns_review_record_instance(self, store: _Store) -> None:
        """create_skill() must return the same ReviewRecord that was passed in."""
        record = _make_review_record()
        result = store.create_skill(record)
        assert isinstance(result, ReviewRecord)

    def test_create_skill_stored_correctly(self, store: _Store) -> None:
        """create_skill() must persist the record so get_skill() can retrieve it."""
        record = _make_review_record(skill_id="persist-001", skill_name="my-stored-skill")
        store.create_skill(record)
        fetched = store.get_skill("persist-001")
        assert fetched is not None
        assert fetched.skill_id == "persist-001"
        assert fetched.skill_name == "my-stored-skill"

    def test_get_skill_finds_created_record(self, store: _Store) -> None:
        """get_skill(skill_id) returns the record matching that skill_id."""
        record = _make_review_record(skill_id="uid-abc-123")
        store.create_skill(record)
        result = store.get_skill("uid-abc-123")
        assert result is not None
        assert result.skill_id == "uid-abc-123"

    def test_get_skill_returns_none_for_unknown(self, store: _Store) -> None:
        """get_skill() must return None if the skill_id was never created."""
        result = store.get_skill("nonexistent-id-xyz")
        assert result is None

    def test_get_skill_by_name_finds_by_name(self, store: _Store) -> None:
        """get_skill_by_name() must find the record matching that exact skill_name."""
        record = _make_review_record(skill_id="name-match-1", skill_name="prime-finder")
        store.create_skill(record)
        result = store.get_skill_by_name("prime-finder")
        assert result is not None
        assert result.skill_name == "prime-finder"
        assert result.skill_id == "name-match-1"

    def test_get_skill_by_name_returns_none_for_unknown(self, store: _Store) -> None:
        """get_skill_by_name() must return None if no skill has that name."""
        result = store.get_skill_by_name("ghost-skill-never-created")
        assert result is None

    def test_update_skill_updates_fields(self, store: _Store) -> None:
        """update_skill() must mutate the stored fields for the given skill_id."""
        record = _make_review_record(skill_id="upd-001", skill_name="update-target")
        store.create_skill(record)
        store.update_skill("upd-001", {"status": "accepted", "review_notes": "LGTM"})
        updated = store.get_skill("upd-001")
        assert updated is not None
        assert updated.status == "accepted"
        assert updated.review_notes == "LGTM"

    def test_update_skill_raises_keyerror_for_unknown(self, store: _Store) -> None:
        """update_skill() must raise KeyError if skill_id does not exist in the store."""
        with pytest.raises(KeyError, match="ghost-skill-id"):
            store.update_skill("ghost-skill-id", {"status": "accepted"})


# ===========================================================================
# CHECKPOINT 4: list_skills — filtering, pagination, ordering
# ===========================================================================

class TestListSkills:
    """
    Dragon Rider perspective: the public skill listing is what users browse.
    Pagination correctness, status filtering, and sort order are UX-critical.
    A wrong page offset = users never find skills = zero retention.
    """

    def test_list_skills_no_filter_returns_all(self, store: _Store) -> None:
        """list_skills() with no filter returns every stored skill and the correct total."""
        store.create_skill(_make_review_record(skill_id="f1", skill_name="alpha-skill"))
        store.create_skill(_make_review_record(skill_id="f2", skill_name="beta-skill"))
        store.create_skill(_make_review_record(skill_id="f3", skill_name="gamma-skill"))
        records, total = store.list_skills()
        assert total == 3
        assert len(records) == 3

    def test_list_skills_filters_by_status_pending(self, store: _Store) -> None:
        """list_skills(status=pending) must return only pending skills."""
        store.create_skill(
            _make_review_record(skill_id="p1", skill_name="pending-one", status=SkillStatus.pending)
        )
        store.create_skill(
            _make_review_record(skill_id="a1", skill_name="accepted-one", status=SkillStatus.accepted)
        )
        store.create_skill(
            _make_review_record(skill_id="r1", skill_name="rejected-one", status=SkillStatus.rejected)
        )

        records, total = store.list_skills(status=SkillStatus.pending)
        assert total == 1
        assert records[0].skill_id == "p1"

    def test_list_skills_filters_by_status_accepted(self, store: _Store) -> None:
        """list_skills(status=accepted) must return only accepted skills."""
        store.create_skill(
            _make_review_record(skill_id="p2", skill_name="pending-two", status=SkillStatus.pending)
        )
        store.create_skill(
            _make_review_record(skill_id="a2", skill_name="accepted-two", status=SkillStatus.accepted)
        )
        store.create_skill(
            _make_review_record(skill_id="a3", skill_name="accepted-three", status=SkillStatus.accepted)
        )

        records, total = store.list_skills(status=SkillStatus.accepted)
        assert total == 2
        ids = {r.skill_id for r in records}
        assert ids == {"a2", "a3"}

    def test_list_skills_filters_by_status_rejected(self, store: _Store) -> None:
        """list_skills(status=rejected) must return only rejected skills."""
        store.create_skill(
            _make_review_record(skill_id="r2", skill_name="rejected-two", status=SkillStatus.rejected)
        )
        store.create_skill(
            _make_review_record(skill_id="r3", skill_name="rejected-three", status=SkillStatus.rejected)
        )
        store.create_skill(
            _make_review_record(skill_id="a4", skill_name="accepted-four", status=SkillStatus.accepted)
        )

        records, total = store.list_skills(status=SkillStatus.rejected)
        assert total == 2

    def test_list_skills_status_filter_returns_zero_for_empty_match(self, store: _Store) -> None:
        """list_skills(status=accepted) on a store with only pending skills returns ([], 0)."""
        store.create_skill(
            _make_review_record(skill_id="p3", skill_name="pending-three", status=SkillStatus.pending)
        )
        records, total = store.list_skills(status=SkillStatus.accepted)
        assert total == 0
        assert records == []

    def test_list_skills_pagination_page1(self, store: _Store) -> None:
        """list_skills(page=1, per_page=2) must return at most 2 records."""
        for i in range(5):
            ts = datetime.now(timezone.utc) - timedelta(seconds=i)
            store.create_skill(
                _make_review_record(skill_id=f"pg-{i:02d}", skill_name=f"paged-skill-{i:02d}", submitted_at=ts)
            )
        records, total = store.list_skills(page=1, per_page=2)
        assert total == 5
        assert len(records) == 2

    def test_list_skills_pagination_page2(self, store: _Store) -> None:
        """list_skills(page=2, per_page=2) must return the second batch of records."""
        for i in range(5):
            ts = datetime.now(timezone.utc) - timedelta(seconds=i)
            store.create_skill(
                _make_review_record(skill_id=f"pg2-{i:02d}", skill_name=f"paged2-skill-{i:02d}", submitted_at=ts)
            )
        records_p1, _ = store.list_skills(page=1, per_page=2)
        records_p2, _ = store.list_skills(page=2, per_page=2)
        ids_p1 = {r.skill_id for r in records_p1}
        ids_p2 = {r.skill_id for r in records_p2}
        # Pages must not overlap
        assert ids_p1.isdisjoint(ids_p2), "page=1 and page=2 results must not overlap"

    def test_list_skills_pagination_last_page_may_have_fewer(self, store: _Store) -> None:
        """list_skills on the last page returns fewer records than per_page when total is not divisible."""
        for i in range(3):
            ts = datetime.now(timezone.utc) - timedelta(seconds=i)
            store.create_skill(
                _make_review_record(skill_id=f"lp-{i:02d}", skill_name=f"lastpage-skill-{i:02d}", submitted_at=ts)
            )
        # page=2, per_page=2: only 1 record should be on page 2
        records, total = store.list_skills(page=2, per_page=2)
        assert total == 3
        assert len(records) == 1

    def test_list_skills_pagination_beyond_last_page_returns_empty(self, store: _Store) -> None:
        """list_skills on a page well beyond the total returns an empty list."""
        for i in range(2):
            ts = datetime.now(timezone.utc) - timedelta(seconds=i)
            store.create_skill(
                _make_review_record(skill_id=f"bp-{i:02d}", skill_name=f"beyondpage-skill-{i:02d}", submitted_at=ts)
            )
        records, total = store.list_skills(page=99, per_page=20)
        assert total == 2
        assert records == []

    def test_list_skills_sorted_by_submitted_at_descending(self, store: _Store) -> None:
        """list_skills() must return newest records first (descending submitted_at)."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        # Create 3 skills submitted 10 minutes apart (oldest first)
        store.create_skill(
            _make_review_record(
                skill_id="sort-old", skill_name="sort-oldest",
                submitted_at=base,
            )
        )
        store.create_skill(
            _make_review_record(
                skill_id="sort-mid", skill_name="sort-middle",
                submitted_at=base + timedelta(minutes=10),
            )
        )
        store.create_skill(
            _make_review_record(
                skill_id="sort-new", skill_name="sort-newest",
                submitted_at=base + timedelta(minutes=20),
            )
        )

        records, _ = store.list_skills()
        assert len(records) == 3
        assert records[0].skill_id == "sort-new", "First record should be newest"
        assert records[1].skill_id == "sort-mid"
        assert records[2].skill_id == "sort-old", "Last record should be oldest"


# ===========================================================================
# CHECKPOINT 5: count_recent_submissions
# ===========================================================================

class TestCountRecentSubmissions:
    """
    Dragon Rider perspective: rate-limiting is the anti-spam gate.
    If count_recent_submissions is wrong, the store can be flooded.
    Off-by-one on the time window = silent rate-limit bypass.
    """

    def test_count_recent_submissions_counts_only_recent_entries(self, store: _Store) -> None:
        """Only submissions within window_seconds are counted."""
        now = datetime.now(timezone.utc)
        # One submission just now (within 1h window)
        store.create_skill(
            _make_review_record(
                skill_id="recent-1",
                skill_name="recent-skill-1",
                key_id="acct_rl",
                submitted_at=now - timedelta(minutes=30),
            )
        )
        # One submission 2h ago (outside 1h window)
        store.create_skill(
            _make_review_record(
                skill_id="old-1",
                skill_name="old-skill-1",
                key_id="acct_rl",
                submitted_at=now - timedelta(hours=2),
            )
        )

        count = store.count_recent_submissions("acct_rl", window_seconds=3600)
        assert count == 1

    def test_count_recent_submissions_returns_zero_for_unknown_key(self, store: _Store) -> None:
        """count_recent_submissions() must return 0 for a key_id with no submissions."""
        count = store.count_recent_submissions("acct_never_submitted", window_seconds=86400)
        assert count == 0

    def test_count_recent_submissions_counts_multiple_recent(self, store: _Store) -> None:
        """All submissions within the window are included in the count."""
        now = datetime.now(timezone.utc)
        for i in range(4):
            store.create_skill(
                _make_review_record(
                    skill_id=f"multi-recent-{i}",
                    skill_name=f"multi-recent-skill-{i}",
                    key_id="acct_multi",
                    submitted_at=now - timedelta(minutes=i * 5),
                )
            )
        # All 4 submissions are within 1h
        count = store.count_recent_submissions("acct_multi", window_seconds=3600)
        assert count == 4

    def test_count_recent_submissions_does_not_cross_key_ids(self, store: _Store) -> None:
        """count_recent_submissions() for key A must not count submissions by key B."""
        now = datetime.now(timezone.utc)
        store.create_skill(
            _make_review_record(
                skill_id="keyA-sub-1",
                skill_name="keya-skill-1",
                key_id="acct_A",
                submitted_at=now - timedelta(minutes=5),
            )
        )
        store.create_skill(
            _make_review_record(
                skill_id="keyB-sub-1",
                skill_name="keyb-skill-1",
                key_id="acct_B",
                submitted_at=now - timedelta(minutes=10),
            )
        )

        count_a = store.count_recent_submissions("acct_A", window_seconds=3600)
        count_b = store.count_recent_submissions("acct_B", window_seconds=3600)
        assert count_a == 1
        assert count_b == 1

    def test_count_recent_submissions_excludes_exactly_at_cutoff_boundary(
        self, store: _Store
    ) -> None:
        """A submission submitted before the cutoff must NOT be counted."""
        now = datetime.now(timezone.utc)
        # Submitted 2 seconds beyond the 1h window
        store.create_skill(
            _make_review_record(
                skill_id="boundary-old",
                skill_name="boundary-old-skill",
                key_id="acct_boundary",
                submitted_at=now - timedelta(seconds=3602),
            )
        )
        count = store.count_recent_submissions("acct_boundary", window_seconds=3600)
        assert count == 0


# ===========================================================================
# CHECKPOINT 6: Persistence — save/load round-trips
# ===========================================================================

class TestPersistence:
    """
    Dragon Rider perspective: if the data does not survive a process restart,
    the store is useless as a backing store. Every round-trip must be lossless.
    This is the 'does my business survive a reboot?' gate.
    """

    def test_save_load_round_trip_preserves_api_keys(self, tmp_path: Path) -> None:
        """Saving then loading in a fresh store reproduces all API key fields."""
        data_dir = tmp_path / "db"

        writer = _Store()
        writer.reset()
        writer.create_api_key(
            key_id="acct_persist",
            key_hash="hash_persist_xyz",
            name="Persistent User",
            account_type="human",
            description="Round-trip test",
        )
        writer.save(data_dir=data_dir)

        reader = _Store()
        reader.load(data_dir=data_dir)
        key = reader.get_api_key_by_id("acct_persist")

        assert key is not None
        assert key.key_id == "acct_persist"
        assert key.key_hash == "hash_persist_xyz"
        assert key.name == "Persistent User"
        assert key.description == "Round-trip test"

    def test_save_load_round_trip_preserves_skills(self, tmp_path: Path) -> None:
        """Saving then loading in a fresh store reproduces all ReviewRecord fields."""
        data_dir = tmp_path / "db_skills"

        ts = datetime(2025, 6, 15, 10, 30, 0, tzinfo=timezone.utc)
        record = ReviewRecord(
            skill_id="round-trip-skill-01",
            skill_name="round-trip-prime",
            content_type=ContentType.skill,
            author="dragon-rider",
            key_id="acct_persist",
            rung_claimed=641,
            skill_content="# Persisted skill\nFull content here.",
            submitted_at=ts,
            status=SkillStatus.accepted,
            review_notes="Auto-accepted in test",
        )

        writer = _Store()
        writer.reset()
        writer.create_skill(record)
        writer.save(data_dir=data_dir)

        reader = _Store()
        reader.load(data_dir=data_dir)
        fetched = reader.get_skill("round-trip-skill-01")

        assert fetched is not None
        assert fetched.skill_id == "round-trip-skill-01"
        assert fetched.skill_name == "round-trip-prime"
        assert fetched.author == "dragon-rider"
        assert fetched.status == SkillStatus.accepted
        assert fetched.review_notes == "Auto-accepted in test"
        assert fetched.skill_content == "# Persisted skill\nFull content here."

    def test_save_load_preserves_multiple_records(self, tmp_path: Path) -> None:
        """All records (keys + skills) are preserved exactly after a save/load cycle."""
        data_dir = tmp_path / "db_multi"

        writer = _Store()
        writer.reset()
        for i in range(3):
            writer.create_api_key(
                key_id=f"acct_{i:03d}",
                key_hash=f"hash_{i:03d}",
                name=f"User {i}",
            )
            ts = datetime(2025, 1, i + 1, 0, 0, 0, tzinfo=timezone.utc)
            writer.create_skill(
                _make_review_record(
                    skill_id=f"multi-skill-{i:03d}",
                    skill_name=f"multi-skill-{i:03d}",
                    submitted_at=ts,
                )
            )
        writer.save(data_dir=data_dir)

        reader = _Store()
        reader.load(data_dir=data_dir)

        assert len(reader.list_api_keys()) == 3
        _, total = reader.list_skills()
        assert total == 3

    def test_load_creates_data_dir_if_missing(self, tmp_path: Path) -> None:
        """load() must create the data directory when it does not yet exist."""
        data_dir = tmp_path / "nonexistent" / "nested" / "dir"
        assert not data_dir.exists(), "Pre-condition: directory must not exist yet"

        s = _Store()
        s.load(data_dir=data_dir)  # must not raise

        assert data_dir.exists(), "load() must create the data directory"

    def test_save_creates_data_dir_if_missing(self, tmp_path: Path) -> None:
        """save() must create the data directory when it does not yet exist."""
        data_dir = tmp_path / "auto_created_dir"
        assert not data_dir.exists()

        s = _Store()
        s.reset()
        s.save(data_dir=data_dir)  # must not raise

        assert data_dir.exists()
        assert (data_dir / "api_keys.json").exists()
        assert (data_dir / "skills.json").exists()

    def test_load_from_empty_dir_leaves_store_empty(self, tmp_path: Path) -> None:
        """load() on an existing but empty directory must not raise and leaves store empty."""
        data_dir = tmp_path / "empty_db"
        data_dir.mkdir()

        s = _Store()
        s.load(data_dir=data_dir)

        assert s.list_api_keys() == []
        _, total = s.list_skills()
        assert total == 0

    def test_save_load_idempotent_on_reload(self, tmp_path: Path) -> None:
        """Calling load() a second time on the same directory must not duplicate data."""
        data_dir = tmp_path / "db_idempotent"

        writer = _Store()
        writer.reset()
        writer.create_api_key(key_id="acct_idem", key_hash="hash_idem", name="Idem User")
        writer.save(data_dir=data_dir)

        reader = _Store()
        reader.load(data_dir=data_dir)
        reader.load(data_dir=data_dir)  # second load — must not duplicate

        keys = reader.list_api_keys()
        ids = [k.key_id for k in keys]
        assert ids.count("acct_idem") == 1, "Double load must not duplicate records"
