"""Safety gates for recipe execution."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_text(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


class SafetyGate:
    """Enforce scope, budget, confirmation, and snapshot requirements."""

    def __init__(
        self,
        *,
        session_id: str = "default",
        budget_path: str | Path | None = None,
        snapshot_dir: str | Path = "~/.solace/snapshots",
        archive_limit: int = 10,
        confirmation_threshold: int = 5,
        confirmation_fn: Callable[[int], bool] | None = None,
        scope_validator: Callable[[str, str], bool] | None = None,
    ) -> None:
        self.session_id = session_id
        self.archive_limit = int(archive_limit)
        self.confirmation_threshold = int(confirmation_threshold)
        self.confirmation_fn = confirmation_fn
        self.scope_validator = scope_validator

        if budget_path is None:
            budget_path = Path("~/.solace/budget").expanduser() / f"{session_id}.json"
        self.budget_path = Path(budget_path).expanduser()
        self.budget_path.parent.mkdir(parents=True, exist_ok=True)

        self.snapshot_dir = Path(snapshot_dir).expanduser()
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def _load_budget(self) -> dict[str, int]:
        if not self.budget_path.exists():
            return {}
        raw = self.budget_path.read_text(encoding="utf-8")
        if not raw.strip():
            return {}
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("budget file must be a JSON object")
        out: dict[str, int] = {}
        for key, value in parsed.items():
            out[str(key)] = int(value)
        return out

    def _save_budget(self, budget: Mapping[str, int]) -> None:
        self.budget_path.write_text(json.dumps(dict(budget), indent=2), encoding="utf-8")

    def check_scope(self, token_id: str, required_scope: str) -> tuple[bool, str]:
        if not token_id or not required_scope:
            return False, "EXIT_SCOPE_DENIED"
        if self.scope_validator is None:
            return False, "EXIT_SCOPE_DENIED"
        ok = bool(self.scope_validator(token_id, required_scope))
        return (True, "OK") if ok else (False, "EXIT_SCOPE_DENIED")

    def check_budget(self, budget_type: str, limit: int) -> tuple[bool, str, int]:
        if not budget_type:
            return False, "EXIT_BUDGET_EXCEEDED", 0
        limit = int(limit)
        if limit <= 0:
            return False, "EXIT_BUDGET_EXCEEDED", 0
        counters = self._load_budget()
        used = int(counters.get(budget_type, 0))
        if used >= limit:
            return False, "EXIT_BUDGET_EXCEEDED", 0
        return True, "OK", limit - used

    def consume_budget(self, budget_type: str, amount: int = 1) -> int:
        if amount <= 0:
            raise ValueError(f"amount must be positive, got {amount!r}")
        counters = self._load_budget()
        updated = int(counters.get(budget_type, 0)) + int(amount)
        counters[budget_type] = updated
        self._save_budget(counters)
        return updated

    def require_confirmation(self, email_count: int) -> tuple[bool, str]:
        if int(email_count) <= self.confirmation_threshold:
            return True, "OK"
        if self.confirmation_fn is None:
            return False, "EXIT_CONFIRMATION_DENIED"
        approved = bool(self.confirmation_fn(int(email_count)))
        return (True, "OK") if approved else (False, "EXIT_CONFIRMATION_DENIED")

    def snapshot_pre_action(self, payload: object) -> tuple[bool, str, str | None]:
        try:
            canonical = _canonical_json(payload)
            digest = _sha256_text(canonical)
            path = self.snapshot_dir / f"{digest}.json"
            path.write_text(
                json.dumps(
                    {
                        "snapshot_hash": digest,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "session_id": self.session_id,
                        "payload": payload,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            return True, "OK", digest
        except Exception:
            return False, "EXIT_SNAPSHOT_FAILED", None

