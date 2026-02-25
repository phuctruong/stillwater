"""Append-only hash-chained audit trail for recipe execution."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_json(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class AuditChain:
    def __init__(self, session_id: str | None = None, base_dir: str | Path = "~/.solace/audit") -> None:
        self.base_dir = Path(base_dir).expanduser()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        if session_id is None:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            session_id = f"audit-{stamp}-{uuid.uuid4().hex[:8]}"
        self.session_id = session_id
        self.session_dir = self.base_dir / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.session_dir / "index.json"
        self._counter = 0
        self.previous_hash = ""
        self._load_state()

    def _load_state(self) -> None:
        if not self.index_path.exists():
            return
        data = json.loads(self.index_path.read_text(encoding="utf-8"))
        self._counter = int(data.get("count", 0))
        self.previous_hash = str(data.get("last_hash", "")) if data.get("last_hash") else ""

    def _save_state(self) -> None:
        self.index_path.write_text(
            json.dumps(
                {
                    "session_id": self.session_id,
                    "count": self._counter,
                    "last_hash": self.previous_hash,
                    "updated_at": _utc_now_iso(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def _next_event_id(self) -> str:
        return f"e{self._counter + 1:06d}"

    def log_event(self, event_type: str, details: Dict[str, Any]) -> str:
        event_id = self._next_event_id()
        event = {
            "event_id": event_id,
            "session_id": self.session_id,
            "timestamp": _utc_now_iso(),
            "type": event_type,
            "details": details,
            "previous_hash": self.previous_hash,
        }
        event_hash = _sha256_hex(_canonical_json(event))
        event["hash"] = event_hash
        (self.session_dir / f"{event_id}.json").write_text(json.dumps(event, indent=2), encoding="utf-8")
        self._counter += 1
        self.previous_hash = event_hash
        self._save_state()
        return event_hash

    def log_classification(
        self,
        email: Dict[str, Any],
        classification: str,
        confidence: float,
        routed_to: str,
    ) -> str:
        return self.log_event(
            "CLASSIFICATION",
            {
                "email_subject": email.get("subject", ""),
                "email_sender": email.get("sender", ""),
                "classification": classification,
                "confidence": float(confidence),
                "routed_to": routed_to,
            },
        )

    def log_archive(self, email_ids: list[str], success: bool, halt_reason: str | None = None) -> str:
        return self.log_event(
            "ARCHIVE",
            {
                "email_count": len(email_ids),
                "email_ids": list(email_ids),
                "success": bool(success),
                "halt_reason": halt_reason,
            },
        )

    def verify_chain(self) -> Dict[str, Any]:
        expected_prev = ""
        checked = 0
        for path in sorted(self.session_dir.glob("e*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            event_hash = str(data.get("hash", ""))
            prev_hash = str(data.get("previous_hash", ""))
            materialized = dict(data)
            materialized.pop("hash", None)
            recomputed = _sha256_hex(_canonical_json(materialized))
            if prev_hash != expected_prev:
                return {
                    "valid": False,
                    "reason": "previous_hash_mismatch",
                    "event_file": str(path),
                    "expected_previous_hash": expected_prev,
                    "actual_previous_hash": prev_hash,
                }
            if event_hash != recomputed:
                return {
                    "valid": False,
                    "reason": "event_hash_mismatch",
                    "event_file": str(path),
                    "expected_hash": recomputed,
                    "actual_hash": event_hash,
                }
            expected_prev = event_hash
            checked += 1
        return {"valid": True, "events_checked": checked, "last_hash": expected_prev}

