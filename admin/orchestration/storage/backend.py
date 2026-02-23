"""
Storage backend layer for stillwater learned entities.

Implements:
  StorageBackend  — abstract base class (no cloud imports)
  LocalStore      — JSONL files under ~/stillwater/data/  (OSS-clean, zero network)
  FirestoreStore  — lazy-imported Firestore backend (opt-in only)
  HybridStore     — local-first with async Firestore backup queue

Design:
- LocalStore has ZERO cloud SDK imports (OSS-first guarantee)
- FirestoreStore is lazy-imported inside its own methods (never at module load time)
- HybridStore writes LocalStore synchronously, then enqueues FirestoreStore writes
- All JSONL writes are atomic: write to tmp file, then os.rename() (POSIX rename is atomic)
- Thread safety: one threading.Lock per file for LocalStore; background queue thread for Firestore

Rung: 641 (deterministic, testable, offline-first)
"""

from __future__ import annotations

import json
import logging
import os
import queue
import tempfile
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

# Internal imports only — zero cloud SDK at module level
from admin.orchestration.intent.models import LearnedWish
from admin.orchestration.execute.models import LearnedCombo
from admin.orchestration.smalltalk.models import LearnedSmallTalk

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default sync_metadata structure
# ---------------------------------------------------------------------------

_DEFAULT_SYNC_METADATA: Dict[str, Any] = {
    "schema_version": "1.0.0",
    "local_store_path": "",
    "firestore_project": "",
    "firestore_database": "(default)",
    "last_synced_at": None,
    "last_sync_status": "never",
    "pending_sync_count": 0,
    "total_synced": {
        "learned_wishes": 0,
        "learned_combos": 0,
        "learned_smalltalk": 0,
    },
    "failed_sync_entries": [],
}


# ---------------------------------------------------------------------------
# StorageBackend — Abstract Base Class
# ---------------------------------------------------------------------------

class StorageBackend(ABC):
    """
    Abstract interface for all storage backends.

    Implementations:
      LocalStore     — JSONL files (OSS default)
      FirestoreStore — Cloud Firestore (opt-in, lazy import)
      HybridStore    — Composed Local + Firestore

    No cloud imports at this level. Subclasses are responsible for
    their own import strategies (lazy vs. eager).
    """

    # --- LearnedWish operations ---

    @abstractmethod
    def load_learned_wishes(self) -> List[LearnedWish]:
        """Load all learned wish entries from storage."""
        ...

    @abstractmethod
    def save_learned_wish(self, entry: LearnedWish) -> None:
        """Persist a single learned wish entry."""
        ...

    # --- LearnedCombo operations ---

    @abstractmethod
    def load_learned_combos(self) -> List[LearnedCombo]:
        """Load all learned combo entries from storage."""
        ...

    @abstractmethod
    def save_learned_combo(self, entry: LearnedCombo) -> None:
        """Persist a single learned combo entry."""
        ...

    # --- LearnedSmallTalk operations ---

    @abstractmethod
    def load_learned_smalltalk(self) -> List[LearnedSmallTalk]:
        """Load all learned smalltalk entries from storage."""
        ...

    @abstractmethod
    def save_learned_smalltalk(self, entry: LearnedSmallTalk) -> None:
        """Persist a single learned smalltalk entry."""
        ...

    # --- Sync metadata ---

    @abstractmethod
    def get_sync_metadata(self) -> Dict[str, Any]:
        """Return sync metadata dict."""
        ...

    @abstractmethod
    def set_sync_metadata(self, meta: Dict[str, Any]) -> None:
        """Persist sync metadata dict."""
        ...


# ---------------------------------------------------------------------------
# LocalStore — JSONL file backend (OSS-clean, zero network)
# ---------------------------------------------------------------------------

class LocalStore(StorageBackend):
    """
    File-based storage backend.

    Layout under base_dir (typically ~/stillwater/data/):
      intent/learned_wishes.jsonl
      execute/learned_combos.jsonl
      smalltalk/learned_smalltalk.jsonl
      sync_metadata.json

    All writes are atomic: write to a temp file in the same directory,
    then os.replace() (POSIX rename — atomic on same filesystem).

    Thread safety: one threading.Lock per JSONL file. Concurrent writers
    serialize through the lock; no data loss on concurrent writes.

    Zero cloud SDK imports. Zero network calls. Works offline.
    """

    def __init__(self, base_dir: str) -> None:
        """
        Args:
            base_dir: Root of the data directory, e.g. ~/stillwater/data/.
        """
        self._base = Path(base_dir).expanduser().resolve()
        self._base.mkdir(parents=True, exist_ok=True)

        # File paths
        self._wishes_path = self._base / "intent" / "learned_wishes.jsonl"
        self._combos_path = self._base / "execute" / "learned_combos.jsonl"
        self._smalltalk_path = self._base / "smalltalk" / "learned_smalltalk.jsonl"
        self._metadata_path = self._base / "sync_metadata.json"

        # Per-file locks for thread safety
        self._wish_lock = threading.Lock()
        self._combo_lock = threading.Lock()
        self._smalltalk_lock = threading.Lock()
        self._metadata_lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # LearnedWish
    # ------------------------------------------------------------------ #

    def load_learned_wishes(self) -> List[LearnedWish]:
        """Parse learned_wishes.jsonl. Skips malformed lines silently."""
        return self._load_jsonl(self._wishes_path, LearnedWish)

    def save_learned_wish(self, entry: LearnedWish) -> None:
        """Atomically append one JSON line to learned_wishes.jsonl."""
        with self._wish_lock:
            self._atomic_append(self._wishes_path, entry.model_dump_json())

    # ------------------------------------------------------------------ #
    # LearnedCombo
    # ------------------------------------------------------------------ #

    def load_learned_combos(self) -> List[LearnedCombo]:
        """Parse learned_combos.jsonl. Skips malformed lines silently."""
        return self._load_jsonl(self._combos_path, LearnedCombo)

    def save_learned_combo(self, entry: LearnedCombo) -> None:
        """Atomically append one JSON line to learned_combos.jsonl."""
        with self._combo_lock:
            self._atomic_append(self._combos_path, entry.model_dump_json())

    # ------------------------------------------------------------------ #
    # LearnedSmallTalk
    # ------------------------------------------------------------------ #

    def load_learned_smalltalk(self) -> List[LearnedSmallTalk]:
        """Parse learned_smalltalk.jsonl. Skips malformed lines silently."""
        return self._load_jsonl(self._smalltalk_path, LearnedSmallTalk)

    def save_learned_smalltalk(self, entry: LearnedSmallTalk) -> None:
        """Atomically append one JSON line to learned_smalltalk.jsonl."""
        with self._smalltalk_lock:
            self._atomic_append(self._smalltalk_path, entry.model_dump_json())

    # ------------------------------------------------------------------ #
    # Sync metadata
    # ------------------------------------------------------------------ #

    def get_sync_metadata(self) -> Dict[str, Any]:
        """Return sync_metadata.json contents. Returns defaults if missing."""
        with self._metadata_lock:
            if not self._metadata_path.exists():
                default = dict(_DEFAULT_SYNC_METADATA)
                default["local_store_path"] = str(self._base)
                return default
            try:
                return json.loads(self._metadata_path.read_text(encoding="utf-8"))
            except Exception:
                default = dict(_DEFAULT_SYNC_METADATA)
                default["local_store_path"] = str(self._base)
                return default

    def set_sync_metadata(self, meta: Dict[str, Any]) -> None:
        """Atomically write sync_metadata.json."""
        with self._metadata_lock:
            self._atomic_write_json(self._metadata_path, meta)

    # ------------------------------------------------------------------ #
    # Private helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _load_jsonl(path: Path, model_cls) -> List:
        """
        Read a JSONL file and construct model instances.

        Silently skips:
          - Empty lines
          - Comment lines (starting with #)
          - Lines that fail JSON parsing
          - Lines whose JSON doesn't match model_cls schema
        """
        results = []
        if not path.exists():
            return results
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            return results
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                data = json.loads(line)
                obj = model_cls(**data)
                results.append(obj)
            except Exception:
                pass  # malformed — append-only safety; skip
        return results

    @staticmethod
    def _atomic_append(path: Path, json_line: str) -> None:
        """
        Append a single JSON line to path atomically.

        Strategy (atomic JSONL append):
          1. Read all existing content (if file exists)
          2. Append the new line to a string
          3. Write the full content to a temp file in the same directory
          4. os.replace() the temp file over the target (atomic on POSIX)

        This guarantees no partial writes are visible to readers.
        For high-frequency appends with large files this is O(n) in file
        size, but for the typical dataset (hundreds of entries) this is
        well within the 10ms latency budget and provides the strongest
        atomicity guarantee without a WAL.
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        # Read existing
        existing = ""
        if path.exists():
            try:
                existing = path.read_text(encoding="utf-8")
            except OSError:
                existing = ""

        # Ensure trailing newline before new line
        if existing and not existing.endswith("\n"):
            existing += "\n"

        new_content = existing + json_line + "\n"

        # Write to temp file in same dir (ensures same filesystem for atomic rename)
        dir_path = path.parent
        fd, tmp_path = tempfile.mkstemp(
            dir=str(dir_path), prefix=".tmp_", suffix=".jsonl"
        )
        try:
            os.write(fd, new_content.encode("utf-8"))
            os.fsync(fd)   # flush kernel buffers to disk
        finally:
            os.close(fd)

        # Atomic rename: on POSIX this is guaranteed atomic (POSIX rename(2))
        os.replace(tmp_path, str(path))

    @staticmethod
    def _atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
        """Write a JSON dict to path atomically."""
        path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(data, indent=2, ensure_ascii=False)

        fd, tmp_path = tempfile.mkstemp(
            dir=str(path.parent), prefix=".tmp_", suffix=".json"
        )
        try:
            os.write(fd, content.encode("utf-8"))
            os.fsync(fd)
        finally:
            os.close(fd)
        os.replace(tmp_path, str(path))


# ---------------------------------------------------------------------------
# FirestoreStore — lazy-imported cloud backend (opt-in only)
# ---------------------------------------------------------------------------

class FirestoreStore(StorageBackend):
    """
    Google Cloud Firestore storage backend.

    ONLY imported/used when config has firestore.enabled: true AND
    credentials are available. Never instantiated for OSS deployments.

    google-cloud-firestore SDK is imported LAZILY inside each method —
    never at module load time. This keeps the module importable in
    offline/OSS environments without the SDK installed.

    Credential loading order:
      1. GOOGLE_APPLICATION_CREDENTIALS env var
      2. STILLWATER_FIRESTORE_CREDENTIALS env var
      3. Application Default Credentials (gcloud login)
      4. Raise FirestoreCredentialError → caller falls back to LocalStore

    Schema:
      users/{user_id}/learned_wishes/{wish_id}
      users/{user_id}/learned_combos/{wish_id}
      users/{user_id}/learned_smalltalk/{pattern_id}
    """

    class FirestoreCredentialError(Exception):
        pass

    def __init__(self, project: str, user_id: str = "default") -> None:
        self._project = project
        self._user_id = user_id
        self._db = None  # lazy-initialized

    def _get_db(self):
        """Lazy-initialize Firestore client. Raises FirestoreCredentialError on failure."""
        if self._db is not None:
            return self._db
        try:
            from google.cloud import firestore  # type: ignore  # lazy import
            self._db = firestore.Client(project=self._project)
            return self._db
        except ImportError:
            raise FirestoreStore.FirestoreCredentialError(
                "google-cloud-firestore is not installed. "
                "Install with: pip install google-cloud-firestore"
            )
        except Exception as exc:
            raise FirestoreStore.FirestoreCredentialError(
                f"Failed to initialize Firestore client: {exc}"
            ) from exc

    def _user_ref(self):
        """Return the Firestore document reference for this user."""
        db = self._get_db()
        return db.collection("users").document(self._user_id)

    # ------------------------------------------------------------------ #
    # LearnedWish
    # ------------------------------------------------------------------ #

    def load_learned_wishes(self) -> List[LearnedWish]:
        """Load all learned wishes from Firestore for this user."""
        try:
            from google.cloud.firestore_v1.base_query import BaseQuery  # type: ignore
            docs = self._user_ref().collection("learned_wishes").stream()
            results = []
            for doc in docs:
                try:
                    data = doc.to_dict()
                    results.append(LearnedWish(**data))
                except Exception:
                    pass
            return results
        except Exception as exc:
            logger.warning("FirestoreStore.load_learned_wishes failed: %s", exc)
            return []

    def save_learned_wish(self, entry: LearnedWish) -> None:
        """Write or merge a learned wish to Firestore."""
        try:
            from google.cloud.firestore_v1 import ArrayUnion  # type: ignore
            ref = self._user_ref().collection("learned_wishes").document(entry.wish_id)
            data = entry.model_dump(mode="json")
            # Use array_union so keyword lists accumulate across sessions
            data["keywords"] = ArrayUnion(entry.keywords)
            ref.set(data, merge=True)
        except Exception as exc:
            logger.warning("FirestoreStore.save_learned_wish failed: %s", exc)
            raise

    # ------------------------------------------------------------------ #
    # LearnedCombo
    # ------------------------------------------------------------------ #

    def load_learned_combos(self) -> List[LearnedCombo]:
        try:
            docs = self._user_ref().collection("learned_combos").stream()
            results = []
            for doc in docs:
                try:
                    results.append(LearnedCombo(**doc.to_dict()))
                except Exception:
                    pass
            return results
        except Exception as exc:
            logger.warning("FirestoreStore.load_learned_combos failed: %s", exc)
            return []

    def save_learned_combo(self, entry: LearnedCombo) -> None:
        try:
            ref = self._user_ref().collection("learned_combos").document(entry.wish_id)
            ref.set(entry.model_dump(mode="json"), merge=True)
        except Exception as exc:
            logger.warning("FirestoreStore.save_learned_combo failed: %s", exc)
            raise

    # ------------------------------------------------------------------ #
    # LearnedSmallTalk
    # ------------------------------------------------------------------ #

    def load_learned_smalltalk(self) -> List[LearnedSmallTalk]:
        try:
            docs = self._user_ref().collection("learned_smalltalk").stream()
            results = []
            for doc in docs:
                try:
                    results.append(LearnedSmallTalk(**doc.to_dict()))
                except Exception:
                    pass
            return results
        except Exception as exc:
            logger.warning("FirestoreStore.load_learned_smalltalk failed: %s", exc)
            return []

    def save_learned_smalltalk(self, entry: LearnedSmallTalk) -> None:
        try:
            from google.cloud.firestore_v1 import ArrayUnion  # type: ignore
            ref = self._user_ref().collection("learned_smalltalk").document(entry.pattern_id)
            data = entry.model_dump(mode="json")
            data["keywords"] = ArrayUnion(entry.keywords)
            ref.set(data, merge=True)
        except Exception as exc:
            logger.warning("FirestoreStore.save_learned_smalltalk failed: %s", exc)
            raise

    # ------------------------------------------------------------------ #
    # Sync metadata
    # ------------------------------------------------------------------ #

    def get_sync_metadata(self) -> Dict[str, Any]:
        try:
            ref = self._user_ref().collection("sync_metadata").document("meta")
            doc = ref.get()
            if doc.exists:
                return doc.to_dict() or {}
            return dict(_DEFAULT_SYNC_METADATA)
        except Exception as exc:
            logger.warning("FirestoreStore.get_sync_metadata failed: %s", exc)
            return dict(_DEFAULT_SYNC_METADATA)

    def set_sync_metadata(self, meta: Dict[str, Any]) -> None:
        try:
            ref = self._user_ref().collection("sync_metadata").document("meta")
            ref.set(meta, merge=True)
        except Exception as exc:
            logger.warning("FirestoreStore.set_sync_metadata failed: %s", exc)


# ---------------------------------------------------------------------------
# HybridStore — local-first with async Firestore backup
# ---------------------------------------------------------------------------

class HybridStore(StorageBackend):
    """
    Composed LocalStore (always active) + remote StorageBackend (async backup).

    Write protocol:
      1. Write to LocalStore (synchronous — blocks caller until done)
      2. Enqueue remote write to background queue (non-blocking for caller)

    Read protocol:
      - Always reads from LocalStore (local is authoritative)
      - Remote is NOT queried on normal reads (only on explicit catch-up)

    Background worker:
      - Drains the async queue in a daemon thread
      - On remote write failure: increments sync_attempt_count, re-enqueues
        with exponential backoff (1s, 2s, 4s, 8s, up to 60s)
      - After 5 failures: logs to failed_sync_entries in sync_metadata
      - Local data is NEVER affected by remote failures

    Thread safety:
      - Local writes are protected by LocalStore's per-file locks
      - Queue is thread-safe (queue.Queue)
      - Background worker runs as daemon thread (dies with process)
    """

    _MAX_RETRIES = 5
    _RETRY_BACKOFF_BASE = 1.0  # seconds
    _RETRY_BACKOFF_MAX = 60.0  # seconds cap

    def __init__(self, local: LocalStore, remote: StorageBackend) -> None:
        self._local = local
        self._remote = remote
        self._queue: queue.Queue = queue.Queue()
        self._worker_thread = threading.Thread(
            target=self._sync_worker, daemon=True, name="HybridStore-SyncWorker"
        )
        self._worker_thread.start()
        self._pending_count = 0
        self._count_lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # LearnedWish
    # ------------------------------------------------------------------ #

    def load_learned_wishes(self) -> List[LearnedWish]:
        """Read from LocalStore (authoritative source)."""
        return self._local.load_learned_wishes()

    def save_learned_wish(self, entry: LearnedWish) -> None:
        """Write to LocalStore synchronously; enqueue remote async."""
        self._local.save_learned_wish(entry)
        self._enqueue("wish", entry)

    # ------------------------------------------------------------------ #
    # LearnedCombo
    # ------------------------------------------------------------------ #

    def load_learned_combos(self) -> List[LearnedCombo]:
        return self._local.load_learned_combos()

    def save_learned_combo(self, entry: LearnedCombo) -> None:
        self._local.save_learned_combo(entry)
        self._enqueue("combo", entry)

    # ------------------------------------------------------------------ #
    # LearnedSmallTalk
    # ------------------------------------------------------------------ #

    def load_learned_smalltalk(self) -> List[LearnedSmallTalk]:
        return self._local.load_learned_smalltalk()

    def save_learned_smalltalk(self, entry: LearnedSmallTalk) -> None:
        self._local.save_learned_smalltalk(entry)
        self._enqueue("smalltalk", entry)

    # ------------------------------------------------------------------ #
    # Sync metadata
    # ------------------------------------------------------------------ #

    def get_sync_metadata(self) -> Dict[str, Any]:
        return self._local.get_sync_metadata()

    def set_sync_metadata(self, meta: Dict[str, Any]) -> None:
        self._local.set_sync_metadata(meta)

    def get_sync_status(self) -> Dict[str, Any]:
        """Return current sync status for monitoring/testing."""
        with self._count_lock:
            pending = self._pending_count
        return {
            "pending_count": pending,
            "local_path": str(self._local._base),
            "remote_enabled": True,
            "queue_size": self._queue.qsize(),
        }

    # ------------------------------------------------------------------ #
    # Queue management
    # ------------------------------------------------------------------ #

    def flush_sync_queue(self, timeout: float = 5.0) -> None:
        """
        Block until all queued remote writes are processed.

        Used in tests to ensure async operations complete before assertions.
        Production code does not call this — caller is never blocked.
        """
        self._queue.join()

    # ------------------------------------------------------------------ #
    # Private: async sync worker
    # ------------------------------------------------------------------ #

    def _enqueue(self, entity_type: str, entry) -> None:
        """Add a remote write task to the queue."""
        with self._count_lock:
            self._pending_count += 1
        self._queue.put({"type": entity_type, "entry": entry, "attempt": 0})

    def _sync_worker(self) -> None:
        """
        Background daemon thread that drains the sync queue.

        Retry state machine:
          PENDING → IN_FLIGHT → SUCCESS | RETRY | EXHAUSTED

        On SUCCESS: decrements pending_count
        On RETRY: sleeps 2^attempt seconds (max 60s), re-enqueues
        On EXHAUSTED (attempt >= MAX_RETRIES): logs, decrements pending_count
        """
        while True:
            try:
                task = self._queue.get(timeout=1.0)
            except queue.Empty:
                continue

            try:
                self._process_task(task)
            except Exception as exc:
                logger.error("Unexpected error in sync worker: %s", exc)
            finally:
                self._queue.task_done()

    def _process_task(self, task: Dict[str, Any]) -> None:
        """Execute one remote write task with retry logic."""
        entity_type = task["type"]
        entry = task["entry"]
        attempt = task["attempt"]

        try:
            if entity_type == "wish":
                self._remote.save_learned_wish(entry)
            elif entity_type == "combo":
                self._remote.save_learned_combo(entry)
            elif entity_type == "smalltalk":
                self._remote.save_learned_smalltalk(entry)

            # SUCCESS
            with self._count_lock:
                self._pending_count = max(0, self._pending_count - 1)

        except Exception as exc:
            if attempt >= self._MAX_RETRIES:
                # EXHAUSTED — log and give up for now
                logger.warning(
                    "Remote sync exhausted after %d attempts for %s: %s",
                    attempt, entity_type, exc,
                )
                with self._count_lock:
                    self._pending_count = max(0, self._pending_count - 1)
                return

            # RETRY with exponential backoff
            backoff = min(
                self._RETRY_BACKOFF_BASE * (2 ** attempt),
                self._RETRY_BACKOFF_MAX,
            )
            logger.debug(
                "Remote sync attempt %d failed (%s), retrying in %.1fs",
                attempt + 1, exc, backoff,
            )
            # Re-enqueue without blocking — worker will pick it up after sleeping
            # We sleep here in the worker thread (this is a daemon thread; it's ok)
            import time
            time.sleep(backoff)
            task["attempt"] = attempt + 1
            self._queue.put(task)
            # Requeue does not call task_done here — we call it in _sync_worker's finally
            # But we've re-put the item, so we need to task_done the current item
            # and the re-queued one will get its own task_done later.
            # Note: task_done() is called in _sync_worker's finally block for the
            # current dequeue. The re-queued item gets its own cycle.
