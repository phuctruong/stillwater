"""
Database layer for Intent Twin (Phase 2).

Handles:
- Loading wishes from wishes.jsonl (canonical, checked-in)
- Loading learned_wishes.jsonl (appended by LLM feedback loop)
- Merging learned keywords into the live WishDatabase
- Persisting new learned wishes discovered during sessions

All I/O happens at startup or in background LLM feedback path.
Hot path (CPU match) does ZERO disk I/O.

rung_target: 641 (deterministic, testable, offline-first)
"""

from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import LearnedWish, LookupEntry, Wish, WishDatabase


# ---------------------------------------------------------------------------
# WishDB — main database class
# ---------------------------------------------------------------------------

class WishDB:
    """
    Loads and maintains the wish database.

    Startup sequence:
      1. Load canonical wishes from wishes.jsonl
      2. Load learned_wishes.jsonl and merge new keywords
      3. Build keyword index
      4. Hot path: in-memory only (no disk I/O)

    Thread safety: append_learned_wish() uses a lock.
    """

    def __init__(
        self,
        wishes_path: Optional[str] = None,
        learned_path: Optional[str] = None,
    ) -> None:
        """
        Args:
            wishes_path:  Path to wishes.jsonl (defaults to same dir as this file).
            learned_path: Path to learned_wishes.jsonl (defaults to same dir).
        """
        _here = Path(__file__).parent
        self._wishes_path = Path(wishes_path) if wishes_path else _here / "wishes.jsonl"
        self._learned_path = (
            Path(learned_path) if learned_path else _here / "learned_wishes.jsonl"
        )
        self._lock = threading.Lock()
        self.db = WishDatabase()
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, wish_id: str) -> Optional[Wish]:
        """Look up a wish by id."""
        return self.db.get(wish_id)

    def lookup_by_keyword(self, keyword: str) -> List[Wish]:
        """Return all wishes that contain this keyword."""
        return self.db.lookup_by_keyword(keyword)

    def all_wishes(self) -> List[Wish]:
        """Return all loaded wishes (for inspection/tests)."""
        return self.db.all_wishes()

    def count(self) -> int:
        """Return total number of wishes in the database."""
        return self.db.count()

    def append_learned_wish(self, entry: LearnedWish) -> None:
        """
        Persist a new learned wish entry and merge it into the live DB.

        Thread-safe (acquired lock).
        Idempotent: duplicate keywords are ignored by WishDatabase.add().
        """
        with self._lock:
            # Persist to disk (append-only JSONL)
            self._append_jsonl(self._learned_path, entry)

            # Merge into live DB immediately
            self._merge_learned(entry)

    def reload(self) -> None:
        """
        Re-read both files from disk and rebuild the database.

        Useful after an external process writes new learned_wishes.
        Thread-safe.
        """
        with self._lock:
            self.db = WishDatabase()
            self._load()

    # ------------------------------------------------------------------
    # Internal loading
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load canonical + learned wishes. Called at init and reload()."""
        self._load_wishes()
        self._load_learned()

    def _load_wishes(self) -> int:
        """
        Load canonical wishes from wishes.jsonl.

        Returns number of wishes loaded.
        Silently skips malformed lines.
        """
        loaded = 0
        if not self._wishes_path.exists():
            return 0
        with self._wishes_path.open("r", encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    data = json.loads(line)
                    wish = Wish(**data)
                    self.db.add(wish)
                    loaded += 1
                except Exception:
                    pass  # malformed line — append-only safety
        return loaded

    def _load_learned(self) -> int:
        """
        Load learned wishes from learned_wishes.jsonl and merge keywords.

        Returns number of entries applied.
        """
        applied = 0
        if not self._learned_path.exists():
            return 0
        with self._learned_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    data = json.loads(line)
                    entry = LearnedWish(**data)
                    self._merge_learned(entry)
                    applied += 1
                except Exception:
                    pass
        return applied

    def _merge_learned(self, entry: LearnedWish) -> None:
        """
        Merge learned keywords into an existing wish.

        If the wish_id doesn't exist yet, the entry is silently dropped
        (we only learn extensions to known wishes, not new wishes from
        scratch — that would require LLM-authored canonical wishes).
        """
        wish = self.db.get(entry.wish_id)
        if wish is None:
            return

        # Build augmented keyword list (no duplicates, preserve order)
        existing = set(wish.keywords)
        new_keywords = [kw for kw in entry.keywords if kw not in existing]
        if not new_keywords:
            return

        # Create updated wish (Pydantic models are immutable — rebuild)
        updated = Wish(
            id=wish.id,
            name=wish.name,
            description=wish.description,
            keywords=wish.keywords + new_keywords,
            skill_pack_hint=entry.skill_pack_hint or wish.skill_pack_hint,
            confidence=max(wish.confidence, entry.confidence),
            category=wish.category,
        )
        self.db.add(updated)

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _append_jsonl(path: Path, obj) -> None:
        """Append a Pydantic model as a JSON line to path."""
        path.parent.mkdir(parents=True, exist_ok=True)
        line = obj.model_dump_json() + "\n"
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line)


# ---------------------------------------------------------------------------
# LookupLog — lightweight in-memory log of CPU match events
# ---------------------------------------------------------------------------

class LookupLog:
    """
    Tracks CPU match events in memory for LLM feedback processing.

    Not persisted to disk — exists only for the current session.
    The LLM feedback loop reads from this log to confirm/correct matches
    and write new entries to learned_wishes.jsonl.
    """

    def __init__(self) -> None:
        self._entries: List[LookupEntry] = []
        self._lock = threading.Lock()

    def record(self, entry: LookupEntry) -> None:
        """Append a lookup event."""
        with self._lock:
            self._entries.append(entry)

    def pending_validation(self) -> List[LookupEntry]:
        """Return entries that have not yet been LLM-validated."""
        with self._lock:
            return [e for e in self._entries if e.llm_confirmed is None]

    def confirm(self, prompt: str, wish_id: str, new_keywords: List[str]) -> None:
        """Mark the most recent entry for this prompt as LLM-confirmed."""
        with self._lock:
            for entry in reversed(self._entries):
                if entry.prompt == prompt and entry.llm_confirmed is None:
                    entry.llm_confirmed = True
                    entry.llm_wish_id = wish_id
                    entry.llm_new_keywords = new_keywords
                    break

    def correct(
        self,
        prompt: str,
        correct_wish_id: str,
        new_keywords: List[str],
    ) -> None:
        """Mark the most recent entry for this prompt as LLM-corrected."""
        with self._lock:
            for entry in reversed(self._entries):
                if entry.prompt == prompt and entry.llm_confirmed is None:
                    entry.llm_confirmed = False
                    entry.llm_wish_id = correct_wish_id
                    entry.llm_new_keywords = new_keywords
                    break

    def all(self) -> List[LookupEntry]:
        with self._lock:
            return list(self._entries)

    def count(self) -> int:
        with self._lock:
            return len(self._entries)
