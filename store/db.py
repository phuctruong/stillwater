"""
store/db.py — In-memory database with optional JSON-file persistence.

v1 design: single-process in-memory store backed by a JSON file.
The file is read on startup and written on mutation. No SQL required.

Thread safety: a threading.Lock guards all mutations (single-process only).
Multi-process / multi-worker deployment is out of scope for v1.

Rung target: 641
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import APIKey, ReviewRecord, SkillStatus

# Default data directory (can be overridden via env var for tests)
_DEFAULT_DATA_DIR = Path(__file__).parent.parent / "scratch" / "store_db"


def _data_dir() -> Path:
    env = os.environ.get("STILLWATER_STORE_DATA_DIR")
    return Path(env) if env else _DEFAULT_DATA_DIR


# ============================================================
# In-memory store (singleton)
# ============================================================

class _Store:
    """
    Singleton in-memory store with JSON-file backing.

    Schema:
      {
        "api_keys":    { key_id: {...APIKey fields...} },
        "skills":      { skill_id: {...ReviewRecord fields...} }
      }
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._api_keys:  Dict[str, dict] = {}
        self._skills:    Dict[str, dict] = {}
        self._loaded = False

    # ----------------------------------------------------------
    # Lifecycle
    # ----------------------------------------------------------

    def load(self, data_dir: Optional[Path] = None) -> None:
        """Load state from JSON files. Idempotent."""
        d = data_dir or _data_dir()
        d.mkdir(parents=True, exist_ok=True)

        keys_file   = d / "api_keys.json"
        skills_file = d / "skills.json"

        with self._lock:
            if keys_file.exists():
                self._api_keys = json.loads(keys_file.read_text(encoding="utf-8"))
            if skills_file.exists():
                self._skills = json.loads(skills_file.read_text(encoding="utf-8"))
            self._loaded = True

    def save(self, data_dir: Optional[Path] = None) -> None:
        """Persist state to JSON files."""
        d = data_dir or _data_dir()
        d.mkdir(parents=True, exist_ok=True)

        with self._lock:
            (d / "api_keys.json").write_text(
                json.dumps(self._api_keys, indent=2, default=str), encoding="utf-8"
            )
            (d / "skills.json").write_text(
                json.dumps(self._skills, indent=2, default=str), encoding="utf-8"
            )

    def reset(self) -> None:
        """Clear all data (used in tests)."""
        with self._lock:
            self._api_keys.clear()
            self._skills.clear()
            self._loaded = True

    # ----------------------------------------------------------
    # API Key operations
    # ----------------------------------------------------------

    def create_api_key(self, key_id: str, key_hash: str, name: str,
                       account_type: str = "human",
                       description: str = "") -> APIKey:
        record = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            account_type=account_type,
            description=description,
            created_at=datetime.now(timezone.utc),
        )
        with self._lock:
            self._api_keys[key_id] = record.model_dump(mode="json")
        return record

    def get_api_key_by_id(self, key_id: str) -> Optional[APIKey]:
        with self._lock:
            data = self._api_keys.get(key_id)
        if data is None:
            return None
        return APIKey(**data)

    def get_api_key_by_hash(self, key_hash: str) -> Optional[APIKey]:
        """Find an API key by its HMAC hash (used during auth)."""
        with self._lock:
            for data in self._api_keys.values():
                if data.get("key_hash") == key_hash:
                    return APIKey(**data)
        return None

    def update_api_key(self, key_id: str, updates: Dict[str, Any]) -> None:
        with self._lock:
            if key_id not in self._api_keys:
                raise KeyError(f"API key not found: {key_id}")
            self._api_keys[key_id].update(updates)

    def list_api_keys(self) -> List[APIKey]:
        with self._lock:
            return [APIKey(**d) for d in self._api_keys.values()]

    # ----------------------------------------------------------
    # Skill / submission operations
    # ----------------------------------------------------------

    def create_skill(self, record: ReviewRecord) -> ReviewRecord:
        data = record.model_dump(mode="json")
        with self._lock:
            self._skills[record.skill_id] = data
        return record

    def get_skill(self, skill_id: str) -> Optional[ReviewRecord]:
        with self._lock:
            data = self._skills.get(skill_id)
        if data is None:
            return None
        return ReviewRecord(**data)

    def get_skill_by_name(self, skill_name: str) -> Optional[ReviewRecord]:
        with self._lock:
            for data in self._skills.values():
                if data.get("skill_name") == skill_name:
                    return ReviewRecord(**data)
        return None

    def update_skill(self, skill_id: str, updates: Dict[str, Any]) -> None:
        with self._lock:
            if skill_id not in self._skills:
                raise KeyError(f"Skill not found: {skill_id}")
            self._skills[skill_id].update(updates)

    def list_skills(
        self,
        status: Optional[SkillStatus] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[List[ReviewRecord], int]:
        """
        Return paginated list of skills filtered by status.
        Returns (page_records, total_count).
        """
        with self._lock:
            all_data = list(self._skills.values())

        if status is not None:
            all_data = [d for d in all_data if d.get("status") == status.value]

        total = len(all_data)
        # Sort by submitted_at descending (newest first)
        all_data.sort(key=lambda d: d.get("submitted_at", ""), reverse=True)

        offset = (page - 1) * per_page
        page_data = all_data[offset : offset + per_page]
        records = [ReviewRecord(**d) for d in page_data]
        return records, total

    def count_recent_submissions(self, key_id: str, window_seconds: int = 86400) -> int:
        """Count submissions from this key_id in the last window_seconds."""
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
        with self._lock:
            count = 0
            for data in self._skills.values():
                if data.get("key_id") != key_id:
                    continue
                submitted_at_str = data.get("submitted_at", "")
                try:
                    # Python 3.10 fromisoformat() does not accept the 'Z' suffix
                    # produced by Pydantic v2 datetime serialization; normalise it.
                    normalised = submitted_at_str
                    if isinstance(normalised, str) and normalised.endswith("Z"):
                        normalised = normalised[:-1] + "+00:00"
                    submitted_at = datetime.fromisoformat(normalised)
                    if submitted_at.tzinfo is None:
                        submitted_at = submitted_at.replace(tzinfo=timezone.utc)
                    if submitted_at >= cutoff:
                        count += 1
                except (ValueError, TypeError):
                    pass
        return count


# Module-level singleton
_store = _Store()


def get_store() -> _Store:
    """Return the module-level store singleton."""
    return _store
