"""
Database layer for Execution Twin (Phase 3).

Handles:
- Loading combos from combos.jsonl (canonical, checked-in)
- Loading learned_combos.jsonl (appended by LLM feedback loop)
- Merging learned combos into the live ComboDatabase
- Persisting new learned combos discovered during sessions

All I/O happens at startup or in background LLM feedback path.
Hot path (CPU match) does ZERO disk I/O.

rung_target: 641 (deterministic, testable, offline-first)
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import List, Optional

from .models import Combo, ComboDatabase, ComboLookupEntry, LearnedCombo


# ---------------------------------------------------------------------------
# ComboDB — main database class
# ---------------------------------------------------------------------------

class ComboDB:
    """
    Loads and maintains the combo database.

    Startup sequence:
      1. Load canonical combos from combos.jsonl
      2. Load learned_combos.jsonl and merge updates
      3. Hot path: in-memory only (no disk I/O)

    Thread safety: append_learned_combo() uses a lock.
    """

    def __init__(
        self,
        combos_path: Optional[str] = None,
        learned_path: Optional[str] = None,
    ) -> None:
        """
        Args:
            combos_path:  Path to combos.jsonl (defaults to same dir as this file).
            learned_path: Path to learned_combos.jsonl (defaults to same dir).
        """
        _here = Path(__file__).parent
        self._combos_path = Path(combos_path) if combos_path else _here / "combos.jsonl"
        self._learned_path = (
            Path(learned_path) if learned_path else _here / "learned_combos.jsonl"
        )
        self._lock = threading.Lock()
        self.db = ComboDatabase()
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, wish_id: str) -> Optional[Combo]:
        """Look up a combo by wish_id. O(1) dict lookup."""
        return self.db.get(wish_id)

    def all_combos(self) -> List[Combo]:
        """Return all loaded combos (for inspection/tests)."""
        return self.db.all_combos()

    def count(self) -> int:
        """Return total number of combos in the database."""
        return self.db.count()

    def combos_by_swarm(self, swarm: str) -> List[Combo]:
        """Return all combos targeting a specific swarm agent."""
        return self.db.combos_by_swarm(swarm)

    def append_learned_combo(self, entry: LearnedCombo) -> None:
        """
        Persist a new learned combo entry and merge it into the live DB.

        Thread-safe (acquired lock).
        Overwrites: if the wish_id already has a combo, the learned one
        replaces it if the confidence is higher, otherwise it's ignored.
        """
        with self._lock:
            # Persist to disk (append-only JSONL)
            self._append_jsonl(self._learned_path, entry)

            # Merge into live DB immediately
            self._merge_learned(entry)

    def reload(self) -> None:
        """
        Re-read both files from disk and rebuild the database.

        Useful after an external process writes new learned_combos.
        Thread-safe.
        """
        with self._lock:
            self.db = ComboDatabase()
            self._load()

    # ------------------------------------------------------------------
    # Internal loading
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load canonical + learned combos. Called at init and reload()."""
        self._load_combos()
        self._load_learned()

    def _load_combos(self) -> int:
        """
        Load canonical combos from combos.jsonl.

        Returns number of combos loaded.
        Silently skips malformed lines.
        """
        loaded = 0
        if not self._combos_path.exists():
            return 0
        with self._combos_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    data = json.loads(line)
                    combo = Combo(**data)
                    self.db.add(combo)
                    loaded += 1
                except Exception:
                    pass  # malformed line — append-only safety
        return loaded

    def _load_learned(self) -> int:
        """
        Load learned combos from learned_combos.jsonl and merge.

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
                    entry = LearnedCombo(**data)
                    self._merge_learned(entry)
                    applied += 1
                except Exception:
                    pass
        return applied

    def _merge_learned(self, entry: LearnedCombo) -> None:
        """
        Merge a learned combo into the live database.

        Rules:
        - If wish_id doesn't exist yet: create a new Combo entry from it.
        - If wish_id exists: overwrite only if learned confidence >= existing.
        - recipe must include 'prime-safety' or it is rejected.
        """
        if not entry.recipe:
            return
        if "prime-safety" not in entry.recipe:
            return  # Safety gate: reject combos without prime-safety

        existing = self.db.get(entry.wish_id)
        if existing is not None and entry.confidence < existing.confidence:
            return  # Keep the higher-confidence combo

        # Build updated or new Combo
        new_combo = Combo(
            wish_id=entry.wish_id,
            swarm=entry.swarm,  # type: ignore[arg-type]
            recipe=entry.recipe,
            confidence=entry.confidence,
            description=f"Learned combo (source={entry.source})",
            category=existing.category if existing else "general",
        )
        self.db.add(new_combo)

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
# ComboLookupLog — lightweight in-memory log of CPU match events
# ---------------------------------------------------------------------------

class ComboLookupLog:
    """
    Tracks CPU combo lookup events in memory for LLM feedback processing.

    Not persisted to disk — exists only for the current session.
    The LLM feedback loop reads from this log to confirm/correct matches
    and write new entries to learned_combos.jsonl.
    """

    def __init__(self) -> None:
        self._entries: List[ComboLookupEntry] = []
        self._lock = threading.Lock()

    def record(self, entry: ComboLookupEntry) -> None:
        """Append a lookup event."""
        with self._lock:
            self._entries.append(entry)

    def pending_validation(self) -> List[ComboLookupEntry]:
        """Return entries that have not yet been LLM-validated."""
        with self._lock:
            return [e for e in self._entries if e.llm_confirmed is None]

    def confirm(
        self,
        wish_id: str,
        swarm: str,
        recipe: List[str],
    ) -> None:
        """Mark the most recent entry for this wish_id as LLM-confirmed."""
        with self._lock:
            for entry in reversed(self._entries):
                if entry.wish_id == wish_id and entry.llm_confirmed is None:
                    entry.llm_confirmed = True
                    entry.llm_swarm = swarm
                    entry.llm_recipe = recipe
                    break

    def correct(
        self,
        wish_id: str,
        correct_swarm: str,
        correct_recipe: List[str],
    ) -> None:
        """Mark the most recent entry for this wish_id as LLM-corrected."""
        with self._lock:
            for entry in reversed(self._entries):
                if entry.wish_id == wish_id and entry.llm_confirmed is None:
                    entry.llm_confirmed = False
                    entry.llm_swarm = correct_swarm
                    entry.llm_recipe = correct_recipe
                    break

    def all(self) -> List[ComboLookupEntry]:
        with self._lock:
            return list(self._entries)

    def count(self) -> int:
        with self._lock:
            return len(self._entries)
