"""
Database layer for the Queue-First Small Talk Twin.

Uses SQLite for the banter queue (persistent across sessions).
Uses in-memory dicts for pattern/joke/fact repos (loaded at startup, no hot-path I/O).

All operations are offline-safe. No network. No external dependencies beyond stdlib + pydantic.

Queue operations:
  insert(entry)          — add new banter to queue
  get_next(user_id)      — fetch oldest unused, non-expired entry
  mark_used(entry_id)    — mark entry as consumed
  update_feedback(id, score) — store 1-5 user rating

rung_target: 641 (deterministic, testable, no ML, offline-first)
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from .models import BanterQueueEntry, JokeEntry, LearnedSmallTalk, SmallTalkPattern, TechFactEntry

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_DB_PATH = ":memory:"
_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS banter_queue (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL,
    session_id  TEXT NOT NULL,
    banter      TEXT NOT NULL,
    source      TEXT NOT NULL DEFAULT 'queue',
    source_id   TEXT,
    tags        TEXT NOT NULL DEFAULT '[]',
    confidence  REAL NOT NULL DEFAULT 0.8,
    created_at  TEXT NOT NULL,
    expires_at  TEXT,
    used        INTEGER NOT NULL DEFAULT 0,
    used_at     TEXT,
    feedback_score INTEGER
);

CREATE INDEX IF NOT EXISTS idx_queue_lookup
    ON banter_queue (user_id, used, expires_at);
"""


# ---------------------------------------------------------------------------
# BanterQueueDB — SQLite-backed queue
# ---------------------------------------------------------------------------

class BanterQueueDB:
    """
    Thread-safe SQLite wrapper for the banter queue.

    One instance per process. Thread safety via threading.Lock (SQLite
    is not safe for concurrent writes without it).

    Designed for test isolation: pass db_path=":memory:" for in-process DBs.
    """

    def __init__(self, db_path: str = _DEFAULT_DB_PATH) -> None:
        self._db_path = db_path
        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        self._connect()

    def _connect(self) -> None:
        """Open connection and create schema."""
        if self._db_path == ":memory:":
            self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            path = Path(self._db_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.executescript(_SCHEMA_SQL)
            self._conn.commit()

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def insert(self, entry: BanterQueueEntry) -> None:
        """Insert a new banter entry into the queue."""
        sql = """
            INSERT INTO banter_queue
                (id, user_id, session_id, banter, source, source_id,
                 tags, confidence, created_at, expires_at, used, used_at, feedback_score)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            entry.id,
            entry.user_id,
            entry.session_id,
            entry.banter,
            entry.source,
            entry.source_id,
            json.dumps(entry.tags),
            entry.confidence,
            entry.created_at.isoformat(),
            entry.expires_at.isoformat() if entry.expires_at else None,
            1 if entry.used else 0,
            entry.used_at.isoformat() if entry.used_at else None,
            entry.feedback_score,
        )
        with self._lock:
            self._conn.execute(sql, params)
            self._conn.commit()

    def mark_used(self, entry_id: str) -> bool:
        """
        Mark a banter entry as consumed.

        Returns True if the entry was found and updated, False otherwise.
        """
        now = datetime.utcnow().isoformat()
        sql = """
            UPDATE banter_queue
               SET used = 1, used_at = ?
             WHERE id = ? AND used = 0
        """
        with self._lock:
            cursor = self._conn.execute(sql, (now, entry_id))
            self._conn.commit()
            return cursor.rowcount > 0

    def update_feedback(self, entry_id: str, score: int) -> bool:
        """
        Store user feedback score (1-5) for a consumed banter entry.

        Returns True if updated successfully.
        """
        if not (1 <= score <= 5):
            raise ValueError(f"Feedback score must be 1-5, got {score}")
        sql = "UPDATE banter_queue SET feedback_score = ? WHERE id = ?"
        with self._lock:
            cursor = self._conn.execute(sql, (score, entry_id))
            self._conn.commit()
            return cursor.rowcount > 0

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_next(
        self,
        user_id: str,
        tags: Optional[List[str]] = None,
    ) -> Optional[BanterQueueEntry]:
        """
        Fetch the next available (unused, non-expired) banter for this user.

        Ordering:
          1. Highest confidence first
          2. Oldest created_at first (FIFO within same confidence tier)

        Tag filtering is applied in Python (not SQL) to keep the query
        deterministic and avoid JSON_CONTAINS portability issues.
        """
        now = datetime.utcnow().isoformat()
        sql = """
            SELECT *
              FROM banter_queue
             WHERE user_id = ?
               AND used = 0
               AND (expires_at IS NULL OR expires_at > ?)
             ORDER BY confidence DESC, created_at ASC
             LIMIT 50
        """
        with self._lock:
            rows = self._conn.execute(sql, (user_id, now)).fetchall()

        if not rows:
            return None

        # Apply tag filter in Python (deterministic, no SQL JSON ops)
        for row in rows:
            entry = self._row_to_entry(row)
            if tags:
                if not set(entry.tags) & set(tags):
                    continue
            return entry

        # No tag match — return highest-confidence entry without tag filter
        if tags:
            return self._row_to_entry(rows[0])

        return None

    def count_available(self, user_id: str) -> int:
        """Return number of unused, non-expired entries for this user."""
        now = datetime.utcnow().isoformat()
        sql = """
            SELECT COUNT(*) FROM banter_queue
             WHERE user_id = ?
               AND used = 0
               AND (expires_at IS NULL OR expires_at > ?)
        """
        with self._lock:
            row = self._conn.execute(sql, (user_id, now)).fetchone()
        return row[0] if row else 0

    def list_all(self, user_id: Optional[str] = None) -> List[BanterQueueEntry]:
        """Return all entries (for testing/inspection)."""
        if user_id:
            sql = "SELECT * FROM banter_queue WHERE user_id = ? ORDER BY created_at ASC"
            with self._lock:
                rows = self._conn.execute(sql, (user_id,)).fetchall()
        else:
            sql = "SELECT * FROM banter_queue ORDER BY created_at ASC"
            with self._lock:
                rows = self._conn.execute(sql).fetchall()
        return [self._row_to_entry(r) for r in rows]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> BanterQueueEntry:
        """Convert a DB row to a BanterQueueEntry Pydantic model."""
        return BanterQueueEntry(
            id=row["id"],
            user_id=row["user_id"],
            session_id=row["session_id"],
            banter=row["banter"],
            source=row["source"],
            source_id=row["source_id"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            confidence=row["confidence"],
            created_at=datetime.fromisoformat(row["created_at"]),
            expires_at=(
                datetime.fromisoformat(row["expires_at"])
                if row["expires_at"]
                else None
            ),
            used=bool(row["used"]),
            used_at=(
                datetime.fromisoformat(row["used_at"])
                if row["used_at"]
                else None
            ),
            feedback_score=row["feedback_score"],
        )

    def close(self) -> None:
        """Close the DB connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


# ---------------------------------------------------------------------------
# PatternRepo — in-memory store loaded from JSONL at startup
# ---------------------------------------------------------------------------

class PatternRepo:
    """
    In-memory pattern repository loaded from a JSONL file.

    NO disk I/O on hot path. Load once at startup, query forever.
    """

    def __init__(self) -> None:
        self._patterns: Dict[str, SmallTalkPattern] = {}

    def load_jsonl(self, path: str) -> int:
        """
        Load patterns from a JSONL file.

        Returns number of patterns loaded.
        Silently skips malformed lines (append-only safety).
        """
        loaded = 0
        p = Path(path)
        if not p.exists():
            return 0
        with p.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    data = json.loads(line)
                    pattern = SmallTalkPattern(**data)
                    self._patterns[pattern.id] = pattern
                    loaded += 1
                except Exception:
                    pass  # malformed line — skip
        return loaded

    def load_dict(self, data: dict) -> None:
        """Load a single pattern from a dict (for tests)."""
        pattern = SmallTalkPattern(**data)
        self._patterns[pattern.id] = pattern

    def all(self) -> List[SmallTalkPattern]:
        return list(self._patterns.values())

    def count(self) -> int:
        return len(self._patterns)


# ---------------------------------------------------------------------------
# JokeRepo — in-memory jokes loaded from jokes.jsonl
# ---------------------------------------------------------------------------

class JokeRepo:
    """In-memory joke repository."""

    def __init__(self) -> None:
        self._jokes: List[JokeEntry] = []

    def load_jsonl(self, path: str) -> int:
        loaded = 0
        p = Path(path)
        if not p.exists():
            return 0
        with p.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    data = json.loads(line)
                    self._jokes.append(JokeEntry(**data))
                    loaded += 1
                except Exception:
                    pass
        return loaded

    def find(self, tags: List[str], glow: float) -> Optional[JokeEntry]:
        """
        Find best-matching joke by tags + GLOW score.

        Deterministic: returns the FIRST match in file order
        after filtering by glow range and tag intersection.
        No randomness.
        """
        # Tag-matched pass
        if tags:
            for joke in self._jokes:
                if joke.matches_glow(glow) and joke.matches_tags(tags):
                    return joke
        # Fallback: any joke matching glow
        for joke in self._jokes:
            if joke.matches_glow(glow):
                return joke
        return None

    def count(self) -> int:
        return len(self._jokes)

    def all(self) -> List[JokeEntry]:
        return list(self._jokes)


# ---------------------------------------------------------------------------
# TechFactRepo — in-memory facts loaded from tech_facts.jsonl
# ---------------------------------------------------------------------------

class TechFactRepo:
    """In-memory tech fact repository."""

    def __init__(self) -> None:
        self._facts: List[TechFactEntry] = []

    def load_jsonl(self, path: str) -> int:
        loaded = 0
        p = Path(path)
        if not p.exists():
            return 0
        with p.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    data = json.loads(line)
                    self._facts.append(TechFactEntry(**data))
                    loaded += 1
                except Exception:
                    pass
        return loaded

    def find(self, tags: List[str]) -> Optional[TechFactEntry]:
        """
        Find first tag-matching fact. Deterministic (file order).
        No randomness.
        """
        if tags:
            for fact in self._facts:
                if fact.matches_tags(tags):
                    return fact
        return self._facts[0] if self._facts else None

    def count(self) -> int:
        return len(self._facts)

    def all(self) -> List[TechFactEntry]:
        return list(self._facts)


# ---------------------------------------------------------------------------
# SmallTalkDB — facade combining BanterQueueDB + PatternRepo + learned persistence
# ---------------------------------------------------------------------------

class SmallTalkDB:
    """
    Main database class for the Small Talk Twin.

    Mirrors the structure of WishDB (intent/database.py) and ComboDB (execute/database.py).

    Startup sequence:
      1. Load canonical patterns from patterns_path (if supplied)
      2. Load learned_smalltalk.jsonl from learned_smalltalk_path and merge into PatternRepo
      3. Hot path: in-memory only (no disk I/O)

    append_learned_smalltalk():
      - Persists entry to learned_smalltalk.jsonl (atomic append)
      - Immediately merges into live PatternRepo (keyword union for existing pattern_id)
      - Thread-safe via threading.Lock

    Backward compatibility:
      - learned_smalltalk_path is optional; if absent, learned persistence is skipped
      - Existing tests that create SmallTalkDB without learned_smalltalk_path are unaffected
    """

    def __init__(
        self,
        patterns_path: Optional[str] = None,
        learned_smalltalk_path: Optional[str] = None,
        db_path: str = _DEFAULT_DB_PATH,
    ) -> None:
        """
        Args:
            patterns_path:          Path to canonical patterns JSONL (optional).
            learned_smalltalk_path: Path to learned_smalltalk.jsonl (optional).
            db_path:                SQLite path for BanterQueueDB (default: :memory:).
        """
        self._learned_path = (
            Path(learned_smalltalk_path) if learned_smalltalk_path else None
        )
        self._lock = threading.Lock()

        # In-memory repos
        self.pattern_repo = PatternRepo()
        self.banter_queue = BanterQueueDB(db_path=db_path)

        # Load canonical patterns
        if patterns_path:
            self.pattern_repo.load_jsonl(patterns_path)

        # Load and merge learned patterns
        if self._learned_path:
            self._load_learned()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def append_learned_smalltalk(self, entry: LearnedSmallTalk) -> None:
        """
        Persist a new learned smalltalk entry and merge into the live PatternRepo.

        Thread-safe (acquired lock).
        Merge semantics:
          - If pattern_id already exists in PatternRepo: new keywords are unioned in.
          - If pattern_id does not exist: a new SmallTalkPattern is created from this entry.

        Mirrors WishDB.append_learned_wish() and ComboDB.append_learned_combo().
        """
        with self._lock:
            # Persist to disk (atomic append via temp+rename)
            if self._learned_path:
                self._append_jsonl(self._learned_path, entry)

            # Merge into live PatternRepo immediately
            self._merge_learned(entry)

    # ------------------------------------------------------------------
    # Internal loading
    # ------------------------------------------------------------------

    def _load_learned(self) -> int:
        """
        Load learned smalltalk entries from learned_smalltalk.jsonl.

        Returns number of entries applied.
        Silently skips malformed lines (append-only safety).
        """
        applied = 0
        if not self._learned_path or not self._learned_path.exists():
            return 0
        with self._learned_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    data = json.loads(line)
                    entry = LearnedSmallTalk(**data)
                    self._merge_learned(entry)
                    applied += 1
                except Exception:
                    pass  # malformed line — skip
        return applied

    def _merge_learned(self, entry: LearnedSmallTalk) -> None:
        """
        Merge a learned smalltalk entry into the in-memory PatternRepo.

        If pattern_id already exists:
          - Keywords are union-merged (no duplicates, existing order preserved first)
          - response_template is updated if different
        If pattern_id does not exist:
          - A new SmallTalkPattern is created and added to the repo.

        The PatternRepo stores SmallTalkPattern objects (canonical model).
        LearnedSmallTalk fields map 1:1 to SmallTalkPattern fields.
        """
        existing_patterns = {p.id: p for p in self.pattern_repo.all()}

        if entry.pattern_id in existing_patterns:
            existing = existing_patterns[entry.pattern_id]
            # Union keywords
            existing_kws = set(existing.keywords)
            new_kws = [kw for kw in entry.keywords if kw not in existing_kws]
            merged_keywords = existing.keywords + new_kws

            # Rebuild pattern with merged keywords
            merged = SmallTalkPattern(
                id=existing.id,
                keywords=merged_keywords,
                response_template=entry.response_template or existing.response_template,
                priority=existing.priority,
                freshness_days=existing.freshness_days,
                min_glow=entry.min_glow,
                max_glow=entry.max_glow,
                confidence=max(existing.confidence, entry.confidence),
                formality=existing.formality,
                response_type=existing.response_type,
            )
            self.pattern_repo._patterns[merged.id] = merged
        else:
            # Create new SmallTalkPattern from learned entry
            new_pattern = SmallTalkPattern(
                id=entry.pattern_id,
                keywords=list(entry.keywords),
                response_template=entry.response_template,
                min_glow=entry.min_glow,
                max_glow=entry.max_glow,
                confidence=entry.confidence,
            )
            self.pattern_repo._patterns[new_pattern.id] = new_pattern

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _append_jsonl(path: Path, obj: LearnedSmallTalk) -> None:
        """
        Atomically append a LearnedSmallTalk as a JSON line to path.

        Uses temp file + os.replace() for atomicity (same as LocalStore).
        """
        import os
        import tempfile

        path.parent.mkdir(parents=True, exist_ok=True)

        # Read existing
        existing = ""
        if path.exists():
            try:
                existing = path.read_text(encoding="utf-8")
            except OSError:
                existing = ""

        if existing and not existing.endswith("\n"):
            existing += "\n"

        new_content = existing + obj.model_dump_json() + "\n"

        fd, tmp_path = tempfile.mkstemp(
            dir=str(path.parent), prefix=".tmp_", suffix=".jsonl"
        )
        try:
            os.write(fd, new_content.encode("utf-8"))
            os.fsync(fd)
        finally:
            os.close(fd)
        os.replace(tmp_path, str(path))
