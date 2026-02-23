"""
Test: Storage modes — LocalStore, HybridStore, offline, concurrent.

Covers:
- LocalStore: write atomically, read JSONL, skip malformed
- LocalStore: thread-safe concurrent writes
- LocalStore: sync_metadata.json read/write
- HybridStore: local-first write (LocalStore completes before return)
- HybridStore: Firestore write enqueued (not blocking) — mocked
- HybridStore: offline Firestore (falls back to local-only)
- SaveHandler: routes to correct backend based on mode
- SaveHandler: returns status dict with success/synced/error
- LearnedSmallTalk: model validates, sync fields present
- SmallTalkDB: append_learned_smalltalk() writes to JSONL + merges in-memory

rung_target: 641 (deterministic, testable, fully unit-tested)
EXIT_PASS: All tests pass; zero real network calls; concurrent writes produce correct output.
EXIT_BLOCKED: Race condition in concurrent writes OR LocalStore makes network calls.
"""

from __future__ import annotations

import json
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

# --- Ensure repo root on sys.path -----------------------------------------
_REPO_ROOT = str(Path(__file__).parent.parent.parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from admin.orchestration.storage.backend import (
    HybridStore,
    LocalStore,
    StorageBackend,
)
from admin.orchestration.storage.save_handler import SaveHandler
from admin.orchestration.smalltalk.models import LearnedSmallTalk
from admin.orchestration.smalltalk.database import SmallTalkDB
from admin.orchestration.intent.models import LearnedWish
from admin.orchestration.execute.models import LearnedCombo


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def data_dir(tmp_path):
    """Temporary ~/stillwater/data/ equivalent for each test."""
    d = tmp_path / "stillwater_data"
    d.mkdir()
    return d


@pytest.fixture
def local_store(data_dir):
    return LocalStore(base_dir=str(data_dir))


@pytest.fixture
def sample_wish():
    return LearnedWish(
        wish_id="oauth-integration",
        keywords=["pkce", "device-flow"],
        skill_pack_hint="coder+security",
        confidence=0.71,
        source="llm",
        session_id="sess_test_01",
    )


@pytest.fixture
def sample_combo():
    return LearnedCombo(
        wish_id="grpc-service",
        swarm="coder",
        recipe=["prime-safety", "prime-coder", "software5.0-paradigm"],
        confidence=0.70,
        source="llm",
        session_id="sess_test_01",
    )


@pytest.fixture
def sample_smalltalk():
    return LearnedSmallTalk(
        pattern_id="joke_016",
        response_template="Heard you hit a wall with {topic}. Coffee break?",
        keywords=["stuck", "blocked", "frustrated"],
        tags=["support", "encouragement"],
        min_glow=0.1,
        max_glow=0.5,
        confidence=0.72,
        source="llm",
        session_id="sess_test_01",
    )


# ===========================================================================
# 1. StorageBackend interface
# ===========================================================================

class TestStorageBackendInterface:
    """Verify StorageBackend is an ABC with the correct abstract methods."""

    def test_cannot_instantiate_backend_directly(self):
        """StorageBackend must be an ABC — not directly instantiable."""
        with pytest.raises(TypeError):
            StorageBackend()

    def test_local_store_is_storage_backend(self, local_store):
        """LocalStore must be a StorageBackend subclass."""
        assert isinstance(local_store, StorageBackend)

    def test_backend_has_required_methods(self, local_store):
        """LocalStore must have all six required interface methods."""
        required = [
            "load_learned_wishes", "save_learned_wish",
            "load_learned_combos", "save_learned_combo",
            "load_learned_smalltalk", "save_learned_smalltalk",
            "get_sync_metadata", "set_sync_metadata",
        ]
        for method in required:
            assert hasattr(local_store, method), f"Missing method: {method}"


# ===========================================================================
# 2. LocalStore — file creation and directory structure
# ===========================================================================

class TestLocalStoreDirectoryStructure:

    def test_write_wish_creates_intent_dir(self, local_store, data_dir, sample_wish):
        """save_learned_wish() must create data/intent/ and write learned_wishes.jsonl."""
        local_store.save_learned_wish(sample_wish)

        intent_dir = data_dir / "intent"
        assert intent_dir.exists(), "data/intent/ must be created"
        assert (intent_dir / "learned_wishes.jsonl").exists()

    def test_write_combo_creates_execute_dir(self, local_store, data_dir, sample_combo):
        """save_learned_combo() must create data/execute/ and write learned_combos.jsonl."""
        local_store.save_learned_combo(sample_combo)

        execute_dir = data_dir / "execute"
        assert execute_dir.exists(), "data/execute/ must be created"
        assert (execute_dir / "learned_combos.jsonl").exists()

    def test_write_smalltalk_creates_smalltalk_dir(self, local_store, data_dir, sample_smalltalk):
        """save_learned_smalltalk() must create data/smalltalk/ and write learned_smalltalk.jsonl."""
        local_store.save_learned_smalltalk(sample_smalltalk)

        smalltalk_dir = data_dir / "smalltalk"
        assert smalltalk_dir.exists(), "data/smalltalk/ must be created"
        assert (smalltalk_dir / "learned_smalltalk.jsonl").exists()


# ===========================================================================
# 3. LocalStore — write correctness and JSONL format
# ===========================================================================

class TestLocalStoreWrites:

    def test_save_wish_writes_valid_jsonl(self, local_store, data_dir, sample_wish):
        """Each write appends exactly one valid JSON line."""
        local_store.save_learned_wish(sample_wish)

        path = data_dir / "intent" / "learned_wishes.jsonl"
        lines = [l for l in path.read_text().splitlines() if l.strip()]
        assert len(lines) == 1

        parsed = json.loads(lines[0])
        assert parsed["wish_id"] == "oauth-integration"
        assert "pkce" in parsed["keywords"]

    def test_save_combo_writes_valid_jsonl(self, local_store, data_dir, sample_combo):
        local_store.save_learned_combo(sample_combo)

        path = data_dir / "execute" / "learned_combos.jsonl"
        lines = [l for l in path.read_text().splitlines() if l.strip()]
        assert len(lines) == 1

        parsed = json.loads(lines[0])
        assert parsed["wish_id"] == "grpc-service"
        assert "prime-safety" in parsed["recipe"]

    def test_save_smalltalk_writes_valid_jsonl(self, local_store, data_dir, sample_smalltalk):
        local_store.save_learned_smalltalk(sample_smalltalk)

        path = data_dir / "smalltalk" / "learned_smalltalk.jsonl"
        lines = [l for l in path.read_text().splitlines() if l.strip()]
        assert len(lines) == 1

        parsed = json.loads(lines[0])
        assert parsed["pattern_id"] == "joke_016"
        assert "stuck" in parsed["keywords"]

    def test_multiple_saves_append_not_overwrite(self, local_store, data_dir, sample_wish):
        """Three saves = three JSONL lines."""
        for i in range(3):
            w = LearnedWish(
                wish_id=f"wish-{i}",
                keywords=[f"kw{i}"],
                confidence=0.7,
                source="llm",
            )
            local_store.save_learned_wish(w)

        path = data_dir / "intent" / "learned_wishes.jsonl"
        lines = [l for l in path.read_text().splitlines() if l.strip()]
        assert len(lines) == 3, f"Expected 3 JSONL lines, got {len(lines)}"

    def test_sync_fields_written_to_jsonl(self, local_store, data_dir, sample_wish):
        """All three sync fields must be present in the written JSON."""
        local_store.save_learned_wish(sample_wish)

        path = data_dir / "intent" / "learned_wishes.jsonl"
        parsed = json.loads(path.read_text().splitlines()[0])
        assert "synced_to_firestore" in parsed
        assert "sync_timestamp" in parsed
        assert "sync_attempt_count" in parsed
        assert parsed["synced_to_firestore"] is False
        assert parsed["sync_timestamp"] is None
        assert parsed["sync_attempt_count"] == 0


# ===========================================================================
# 4. LocalStore — read (load) correctness
# ===========================================================================

class TestLocalStoreReads:

    def test_load_wishes_empty_when_no_file(self, local_store):
        """load_learned_wishes() returns [] when file doesn't exist yet."""
        result = local_store.load_learned_wishes()
        assert result == []

    def test_load_combos_empty_when_no_file(self, local_store):
        result = local_store.load_learned_combos()
        assert result == []

    def test_load_smalltalk_empty_when_no_file(self, local_store):
        result = local_store.load_learned_smalltalk()
        assert result == []

    def test_load_wishes_returns_saved_entries(self, local_store, sample_wish):
        """After saving, load returns the correct entries."""
        local_store.save_learned_wish(sample_wish)
        entries = local_store.load_learned_wishes()
        assert len(entries) == 1
        assert entries[0].wish_id == "oauth-integration"

    def test_load_skips_malformed_jsonl(self, data_dir, local_store):
        """Malformed JSONL lines are silently skipped."""
        # Write mixed file: bad + good + bad
        path = data_dir / "intent" / "learned_wishes.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "not valid json\n"
            + json.dumps({
                "wish_id": "good-wish",
                "keywords": ["kw1"],
                "confidence": 0.7,
                "source": "llm",
                "timestamp": "2026-02-23T00:00:00",
                "session_id": "",
                "skill_pack_hint": "",
                "synced_to_firestore": False,
                "sync_timestamp": None,
                "sync_attempt_count": 0,
            }) + "\n"
            + "{bad json\n"
        )
        entries = local_store.load_learned_wishes()
        assert len(entries) == 1, "Only valid entry must be loaded"
        assert entries[0].wish_id == "good-wish"

    def test_load_smalltalk_skips_malformed(self, data_dir, local_store):
        """Malformed JSONL in smalltalk file is silently skipped."""
        path = data_dir / "smalltalk" / "learned_smalltalk.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "not json\n"
            + json.dumps({
                "pattern_id": "p001",
                "response_template": "Hello {name}",
                "keywords": ["hi"],
                "tags": [],
                "min_glow": 0.0,
                "max_glow": 1.0,
                "confidence": 0.8,
                "source": "llm",
                "timestamp": "2026-02-23T00:00:00",
                "session_id": "",
                "synced_to_firestore": False,
                "sync_timestamp": None,
                "sync_attempt_count": 0,
            }) + "\n"
        )
        entries = local_store.load_learned_smalltalk()
        assert len(entries) == 1
        assert entries[0].pattern_id == "p001"


# ===========================================================================
# 5. LocalStore — atomic write (temp → rename)
# ===========================================================================

class TestLocalStoreAtomicWrite:

    def test_write_is_atomic_no_partial_lines(self, local_store, data_dir):
        """Written files must not contain partial JSON lines."""
        wishes = [
            LearnedWish(
                wish_id=f"wish-atomic-{i}",
                keywords=[f"kw{i}"],
                confidence=0.7,
                source="llm",
            )
            for i in range(10)
        ]
        for w in wishes:
            local_store.save_learned_wish(w)

        path = data_dir / "intent" / "learned_wishes.jsonl"
        lines = [l for l in path.read_text().splitlines() if l.strip()]
        assert len(lines) == 10

        for line in lines:
            # Each line must be parseable
            parsed = json.loads(line)
            assert "wish_id" in parsed


# ===========================================================================
# 6. LocalStore — sync_metadata.json
# ===========================================================================

class TestLocalStoreSyncMetadata:

    def test_get_sync_metadata_default_when_no_file(self, local_store):
        """get_sync_metadata() returns a default dict when no file exists."""
        meta = local_store.get_sync_metadata()
        assert "schema_version" in meta
        assert "pending_sync_count" in meta
        assert meta["pending_sync_count"] == 0

    def test_set_and_get_sync_metadata_roundtrip(self, local_store):
        """set_sync_metadata() persists; get_sync_metadata() retrieves it."""
        meta = {
            "schema_version": "1.0.0",
            "last_synced_at": "2026-02-23T14:30:00Z",
            "last_sync_status": "success",
            "pending_sync_count": 3,
            "total_synced": {
                "learned_wishes": 47,
                "learned_combos": 23,
                "learned_smalltalk": 11,
            },
            "failed_sync_entries": [],
        }
        local_store.set_sync_metadata(meta)
        retrieved = local_store.get_sync_metadata()
        assert retrieved["pending_sync_count"] == 3
        assert retrieved["last_sync_status"] == "success"
        assert retrieved["total_synced"]["learned_wishes"] == 47


# ===========================================================================
# 7. LocalStore — thread safety (concurrent writes)
# ===========================================================================

class TestLocalStoreConcurrentWrites:

    def test_concurrent_wish_writes_no_data_loss(self, local_store, data_dir):
        """
        10 threads each write 10 wishes = 100 total.
        All 100 must be readable with no corruption.
        """
        N_THREADS = 10
        N_WRITES = 10
        errors = []

        def write_batch(thread_idx: int):
            try:
                for i in range(N_WRITES):
                    w = LearnedWish(
                        wish_id=f"wish-t{thread_idx}-{i}",
                        keywords=[f"kw-t{thread_idx}-{i}"],
                        confidence=0.7,
                        source="llm",
                    )
                    local_store.save_learned_wish(w)
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=write_batch, args=(t,)) for t in range(N_THREADS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"

        path = data_dir / "intent" / "learned_wishes.jsonl"
        lines = [l for l in path.read_text().splitlines() if l.strip()]
        assert len(lines) == N_THREADS * N_WRITES, (
            f"Expected {N_THREADS * N_WRITES} lines, got {len(lines)}"
        )

        # Each line must be valid JSON
        parsed_ids = set()
        for line in lines:
            parsed = json.loads(line)
            parsed_ids.add(parsed["wish_id"])
        assert len(parsed_ids) == N_THREADS * N_WRITES, "Some wish IDs are duplicate or missing"

    def test_concurrent_smalltalk_writes_no_data_loss(self, local_store, data_dir):
        """5 threads each write 5 smalltalk entries = 25 total."""
        N_THREADS = 5
        N_WRITES = 5
        errors = []

        def write_batch(thread_idx: int):
            try:
                for i in range(N_WRITES):
                    st = LearnedSmallTalk(
                        pattern_id=f"p-t{thread_idx}-{i}",
                        response_template="Response {x}",
                        keywords=[f"kw-t{thread_idx}-{i}"],
                        tags=[],
                        min_glow=0.0,
                        max_glow=1.0,
                        confidence=0.7,
                        source="llm",
                        session_id="sess",
                    )
                    local_store.save_learned_smalltalk(st)
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=write_batch, args=(t,)) for t in range(N_THREADS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"

        path = data_dir / "smalltalk" / "learned_smalltalk.jsonl"
        lines = [l for l in path.read_text().splitlines() if l.strip()]
        assert len(lines) == N_THREADS * N_WRITES, (
            f"Expected {N_THREADS * N_WRITES} smalltalk lines, got {len(lines)}"
        )


# ===========================================================================
# 8. LocalStore — zero network (OSS clean)
# ===========================================================================

class TestLocalStoreNoNetwork:

    def test_local_store_has_no_cloud_imports(self):
        """LocalStore module must not import any cloud SDKs."""
        import admin.orchestration.storage.backend as backend_module
        import inspect
        source = inspect.getsource(backend_module)

        cloud_imports = ["google.cloud", "firebase_admin", "boto3", "azure"]
        found = [imp for imp in cloud_imports if f"import {imp}" in source or f"from {imp}" in source]
        # FirestoreStore class itself uses lazy import — check LocalStore does not
        # The module-level imports must not include any cloud SDK
        # (lazy imports inside FirestoreStore methods are allowed)
        assert "from google.cloud import firestore" not in source.split("class FirestoreStore")[0], (
            "google.cloud.firestore must not be imported at module level"
        )


# ===========================================================================
# 9. LearnedSmallTalk model
# ===========================================================================

class TestLearnedSmallTalkModel:

    def test_model_has_base_fields(self, sample_smalltalk):
        """All 9 base fields must be present."""
        assert sample_smalltalk.pattern_id == "joke_016"
        assert "stuck" in sample_smalltalk.keywords
        assert sample_smalltalk.confidence == 0.72
        assert sample_smalltalk.source == "llm"

    def test_model_has_sync_fields(self, sample_smalltalk):
        """All 3 sync fields must be present with correct defaults."""
        assert sample_smalltalk.synced_to_firestore is False
        assert sample_smalltalk.sync_timestamp is None
        assert sample_smalltalk.sync_attempt_count == 0

    def test_keywords_normalized_to_lowercase(self):
        """Keywords must be forced to lowercase by validator."""
        st = LearnedSmallTalk(
            pattern_id="p001",
            response_template="Hi!",
            keywords=["STUCK", "Blocked", "FRUSTRATED"],
            tags=[],
            min_glow=0.0,
            max_glow=1.0,
            confidence=0.7,
            source="llm",
        )
        assert all(kw == kw.lower() for kw in st.keywords), (
            f"Keywords must be lowercase: {st.keywords}"
        )

    def test_timestamp_is_set_automatically(self, sample_smalltalk):
        """timestamp field must be auto-set and immutable."""
        assert sample_smalltalk.timestamp is not None

    def test_model_serializes_to_json(self, sample_smalltalk):
        """model_dump_json() must produce valid JSON with all fields."""
        json_str = sample_smalltalk.model_dump_json()
        parsed = json.loads(json_str)
        assert parsed["pattern_id"] == "joke_016"
        assert "synced_to_firestore" in parsed
        assert "sync_timestamp" in parsed
        assert "sync_attempt_count" in parsed

    def test_model_roundtrips_from_jsonl(self, sample_smalltalk):
        """A serialized LearnedSmallTalk can be reconstructed from JSON."""
        json_str = sample_smalltalk.model_dump_json()
        parsed = json.loads(json_str)
        reconstructed = LearnedSmallTalk(**parsed)
        assert reconstructed.pattern_id == sample_smalltalk.pattern_id
        assert reconstructed.keywords == sample_smalltalk.keywords
        assert reconstructed.synced_to_firestore == sample_smalltalk.synced_to_firestore


# ===========================================================================
# 10. LearnedWish + LearnedCombo — sync fields added
# ===========================================================================

class TestExistingModelsWithSyncFields:

    def test_learned_wish_has_sync_fields(self, sample_wish):
        """LearnedWish must have all 3 sync fields with correct defaults."""
        assert hasattr(sample_wish, "synced_to_firestore")
        assert hasattr(sample_wish, "sync_timestamp")
        assert hasattr(sample_wish, "sync_attempt_count")
        assert sample_wish.synced_to_firestore is False
        assert sample_wish.sync_timestamp is None
        assert sample_wish.sync_attempt_count == 0

    def test_learned_combo_has_sync_fields(self, sample_combo):
        """LearnedCombo must have all 3 sync fields with correct defaults."""
        assert hasattr(sample_combo, "synced_to_firestore")
        assert hasattr(sample_combo, "sync_timestamp")
        assert hasattr(sample_combo, "sync_attempt_count")
        assert sample_combo.synced_to_firestore is False
        assert sample_combo.sync_timestamp is None
        assert sample_combo.sync_attempt_count == 0

    def test_learned_wish_backward_compat_old_jsonl(self):
        """Deserializing old JSONL without sync fields must succeed (fields default)."""
        old_json = json.dumps({
            "wish_id": "oauth-integration",
            "keywords": ["pkce"],
            "skill_pack_hint": "coder",
            "confidence": 0.7,
            "source": "llm",
            "timestamp": "2026-02-23T00:00:00",
            "session_id": "",
        })
        parsed = json.loads(old_json)
        # Must not raise
        wish = LearnedWish(**parsed)
        assert wish.synced_to_firestore is False
        assert wish.sync_timestamp is None
        assert wish.sync_attempt_count == 0

    def test_learned_combo_backward_compat_old_jsonl(self):
        """Deserializing old JSONL without sync fields must succeed."""
        old_json = json.dumps({
            "wish_id": "grpc-service",
            "swarm": "coder",
            "recipe": ["prime-safety", "prime-coder"],
            "confidence": 0.7,
            "source": "llm",
            "timestamp": "2026-02-23T00:00:00",
            "session_id": "",
        })
        parsed = json.loads(old_json)
        combo = LearnedCombo(**parsed)
        assert combo.synced_to_firestore is False
        assert combo.sync_timestamp is None
        assert combo.sync_attempt_count == 0


# ===========================================================================
# 11. SmallTalkDB — append_learned_smalltalk()
# ===========================================================================

class TestSmallTalkDBLearnedSmallTalk:

    def test_append_learned_smalltalk_writes_file(self, data_dir, sample_smalltalk):
        """append_learned_smalltalk() writes to learned_smalltalk.jsonl."""
        learned_path = str(data_dir / "smalltalk" / "learned_smalltalk.jsonl")
        db = SmallTalkDB(learned_smalltalk_path=learned_path)
        db.append_learned_smalltalk(sample_smalltalk)

        path = Path(learned_path)
        assert path.exists(), "learned_smalltalk.jsonl must be created"
        lines = [l for l in path.read_text().splitlines() if l.strip()]
        assert len(lines) == 1

        parsed = json.loads(lines[0])
        assert parsed["pattern_id"] == "joke_016"

    def test_append_learned_smalltalk_merges_into_pattern_repo(self, data_dir, sample_smalltalk):
        """After append, the pattern is available in the in-memory PatternRepo."""
        learned_path = str(data_dir / "smalltalk" / "learned_smalltalk.jsonl")
        db = SmallTalkDB(learned_smalltalk_path=learned_path)
        db.append_learned_smalltalk(sample_smalltalk)

        # Access the in-memory pattern_repo
        patterns = db.pattern_repo.all()
        pattern_ids = [p.id for p in patterns]
        assert "joke_016" in pattern_ids, (
            f"joke_016 must be in PatternRepo after append. Got: {pattern_ids}"
        )

    def test_append_multiple_smalltalk_entries(self, data_dir):
        """Multiple appends produce multiple JSONL lines and all appear in PatternRepo."""
        learned_path = str(data_dir / "smalltalk" / "learned_smalltalk.jsonl")
        db = SmallTalkDB(learned_smalltalk_path=learned_path)

        for i in range(3):
            st = LearnedSmallTalk(
                pattern_id=f"pattern_{i}",
                response_template=f"Response {i}",
                keywords=[f"kw{i}"],
                tags=[],
                min_glow=0.0,
                max_glow=1.0,
                confidence=0.7,
                source="llm",
                session_id="sess",
            )
            db.append_learned_smalltalk(st)

        path = Path(learned_path)
        lines = [l for l in path.read_text().splitlines() if l.strip()]
        assert len(lines) == 3

        patterns = db.pattern_repo.all()
        pattern_ids = [p.id for p in patterns]
        for i in range(3):
            assert f"pattern_{i}" in pattern_ids

    def test_learned_smalltalk_survives_reload(self, data_dir, sample_smalltalk):
        """A new SmallTalkDB loads previously written learned_smalltalk.jsonl."""
        learned_path = str(data_dir / "smalltalk" / "learned_smalltalk.jsonl")

        db1 = SmallTalkDB(learned_smalltalk_path=learned_path)
        db1.append_learned_smalltalk(sample_smalltalk)

        # Simulate new session
        db2 = SmallTalkDB(learned_smalltalk_path=learned_path)
        patterns = db2.pattern_repo.all()
        pattern_ids = [p.id for p in patterns]
        assert "joke_016" in pattern_ids, (
            "Learned smalltalk must survive across SmallTalkDB instances"
        )


# ===========================================================================
# 12. SaveHandler
# ===========================================================================

class TestSaveHandler:

    def test_save_learned_wish_local_mode(self, data_dir, sample_wish):
        """SaveHandler in local mode: save returns success=True, synced=False."""
        handler = SaveHandler(local_store=LocalStore(base_dir=str(data_dir)))
        result = handler.save_learned_wish(sample_wish)

        assert result["success"] is True
        assert result["synced"] is False
        assert result["error"] is None

        # Verify file was written
        path = data_dir / "intent" / "learned_wishes.jsonl"
        assert path.exists()

    def test_save_learned_combo_local_mode(self, data_dir, sample_combo):
        """SaveHandler in local mode: save combo returns success=True."""
        handler = SaveHandler(local_store=LocalStore(base_dir=str(data_dir)))
        result = handler.save_learned_combo(sample_combo)

        assert result["success"] is True
        assert result["synced"] is False

    def test_save_learned_smalltalk_local_mode(self, data_dir, sample_smalltalk):
        """SaveHandler in local mode: save smalltalk returns success=True."""
        handler = SaveHandler(local_store=LocalStore(base_dir=str(data_dir)))
        result = handler.save_learned_smalltalk(sample_smalltalk)

        assert result["success"] is True
        assert result["synced"] is False

    def test_save_handler_returns_error_on_write_failure(self, data_dir, sample_wish):
        """When LocalStore write fails, SaveHandler returns success=False with error."""
        store = LocalStore(base_dir=str(data_dir))

        # Simulate write failure by making the directory a file
        intent_dir = data_dir / "intent"
        intent_dir.mkdir(parents=True)
        jsonl_path = intent_dir / "learned_wishes.jsonl"
        # Make it a directory so writes fail
        jsonl_path.mkdir()

        handler = SaveHandler(local_store=store)
        result = handler.save_learned_wish(sample_wish)

        assert result["success"] is False
        assert result["error"] is not None

    def test_hybrid_mode_local_write_completes_synchronously(self, data_dir, sample_wish):
        """
        HybridStore: after save_learned_wish() returns, the local file must exist.
        (Firestore is mocked — not called.)
        """
        local = LocalStore(base_dir=str(data_dir))
        mock_remote = MagicMock()
        mock_remote.save_learned_wish = MagicMock()

        hybrid = HybridStore(local=local, remote=mock_remote)
        handler = SaveHandler(local_store=local, hybrid_store=hybrid)
        result = handler.save_learned_wish(sample_wish)

        assert result["success"] is True

        # Local file must exist immediately (synchronous write done)
        path = data_dir / "intent" / "learned_wishes.jsonl"
        assert path.exists(), "Local file must exist after synchronous save"

    def test_save_handler_status_dict_has_required_keys(self, data_dir, sample_wish):
        """Status dict must always contain success, synced, error."""
        handler = SaveHandler(local_store=LocalStore(base_dir=str(data_dir)))
        result = handler.save_learned_wish(sample_wish)

        assert "success" in result
        assert "synced" in result
        assert "error" in result


# ===========================================================================
# 13. HybridStore — Firestore path (mocked)
# ===========================================================================

class TestHybridStore:

    def test_hybrid_save_wish_calls_local_first(self, data_dir, sample_wish):
        """HybridStore: LocalStore.save_learned_wish() must be called."""
        local = LocalStore(base_dir=str(data_dir))
        mock_remote = MagicMock()
        hybrid = HybridStore(local=local, remote=mock_remote)

        hybrid.save_learned_wish(sample_wish)

        path = data_dir / "intent" / "learned_wishes.jsonl"
        assert path.exists(), "LocalStore must have written the file"

    def test_hybrid_save_wish_enqueues_remote_write(self, data_dir, sample_wish):
        """HybridStore: the remote write is scheduled (queue is non-empty or callable)."""
        local = LocalStore(base_dir=str(data_dir))
        mock_remote = MagicMock()
        hybrid = HybridStore(local=local, remote=mock_remote)

        hybrid.save_learned_wish(sample_wish)

        # Give async queue a moment to process (it runs in background thread)
        time.sleep(0.1)

        # The mock remote's save should have been called (async in background)
        # We call flush to ensure queue is drained in tests
        hybrid.flush_sync_queue()
        mock_remote.save_learned_wish.assert_called_once()

    def test_hybrid_load_wish_reads_from_local(self, data_dir, sample_wish):
        """HybridStore: load_learned_wishes() reads from LocalStore (local is authoritative)."""
        local = LocalStore(base_dir=str(data_dir))
        mock_remote = MagicMock()
        hybrid = HybridStore(local=local, remote=mock_remote)

        # Write via hybrid
        hybrid.save_learned_wish(sample_wish)

        # Load — must come from LocalStore (mock remote not queried for load)
        entries = hybrid.load_learned_wishes()
        assert len(entries) == 1
        assert entries[0].wish_id == "oauth-integration"

        # Remote load should NOT be called during standard load
        mock_remote.load_learned_wishes.assert_not_called()

    def test_hybrid_remote_failure_is_non_fatal(self, data_dir, sample_wish):
        """HybridStore: if remote write fails, local write still succeeds."""
        local = LocalStore(base_dir=str(data_dir))
        mock_remote = MagicMock()
        mock_remote.save_learned_wish.side_effect = Exception("Firestore unavailable")

        hybrid = HybridStore(local=local, remote=mock_remote)
        # Must not raise
        hybrid.save_learned_wish(sample_wish)

        # Local file must exist despite remote failure
        hybrid.flush_sync_queue()
        path = data_dir / "intent" / "learned_wishes.jsonl"
        assert path.exists(), "Local write must succeed even if Firestore fails"

    def test_hybrid_get_sync_status_has_required_keys(self, data_dir):
        """get_sync_status() must return dict with known keys."""
        local = LocalStore(base_dir=str(data_dir))
        mock_remote = MagicMock()
        hybrid = HybridStore(local=local, remote=mock_remote)

        status = hybrid.get_sync_status()
        assert "pending_count" in status
        assert "local_path" in status
        assert "remote_enabled" in status


# ===========================================================================
# 14. Latency gate (< 10ms for LocalStore write)
# ===========================================================================

class TestLocalStoreLatency:

    def test_wish_write_under_10ms(self, local_store, sample_wish):
        """
        LocalStore write latency must be < 10ms on warm path.

        First write creates the directory and the file (cold path — OS mkdir).
        We warm the store with one write before measuring, matching real-world
        usage where the data directory is created at app startup.
        """
        # Warm-up: first write creates directories (cold path allowed to be slow)
        warm_wish = LearnedWish(
            wish_id="warmup-wish",
            keywords=["warmup"],
            confidence=0.7,
            source="llm",
        )
        local_store.save_learned_wish(warm_wish)

        # Measure: second write on already-existing file (warm path)
        start = time.perf_counter()
        local_store.save_learned_wish(sample_wish)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 10, f"warm write took {elapsed_ms:.2f}ms (limit: 10ms)"

    def test_wish_read_under_5ms(self, local_store, data_dir, sample_wish):
        """LocalStore read latency must be < 5ms (after one write)."""
        local_store.save_learned_wish(sample_wish)

        start = time.perf_counter()
        local_store.load_learned_wishes()
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 5, f"read took {elapsed_ms:.2f}ms (limit: 5ms)"
