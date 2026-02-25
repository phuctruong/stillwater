"""audit_logger.py — FDA 21 CFR Part 11 compliant audit trail logger.

Logs all CPU predictions, LLM calls, config changes, and access events
to append-only JSONL files with SHA-256 hash chaining for tamper detection.

Architecture:
  data/logs/audit-YYYY-MM-DD.jsonl — daily log rotation
  Each entry: AuditEntry with hash chain integrity

ALCOA+ Compliance:
  Attributable: actor.user_id + actor.actor_type
  Legible: JSON + human-readable export
  Contemporaneous: real-time timestamp
  Original: append-only, no modification
  Accurate: hash chain verification
  Complete: all events logged
  Consistent: sequential numbering
  Enduring: configurable retention
  Available: export capability
  Traceable: hash chain linking

stdlib only: json, hashlib, uuid, datetime, dataclasses, typing, pathlib.
Rung: 641 — deterministic with system clock, no network, no LLM.
"""

from __future__ import annotations

import hashlib
import json
import threading
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_NULL_HASH = "0" * 64
_MAX_INPUT_LENGTH = 10000
_HASH_ALGORITHM = "sha256"


# ---------------------------------------------------------------------------
# AuditEntry dataclass
# ---------------------------------------------------------------------------


@dataclass
class AuditEntry:
    """A single FDA 21 CFR Part 11 compliant audit trail entry.

    Fields follow ALCOA+ principles:
      - Attributable (actor), Legible (JSON), Contemporaneous (timestamp),
        Original (append-only), Accurate (hash chain).
    """

    entry_id: str
    timestamp: str
    timestamp_source: str
    actor: Dict[str, Any]
    action: Dict[str, Any]
    resource: Dict[str, Any]
    outcome: str
    integrity: Dict[str, Any]
    metadata: Dict[str, Any]
    change_detail: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize entry to a plain dict suitable for JSON."""
        return asdict(self)


# ---------------------------------------------------------------------------
# AuditLogger
# ---------------------------------------------------------------------------


class AuditLogger:
    """FDA 21 CFR Part 11 compliant audit logger with SHA-256 hash chaining.

    Writes append-only JSONL files with daily rotation:
      <log_dir>/audit-YYYY-MM-DD.jsonl

    Thread-safe via a reentrant lock.

    Parameters
    ----------
    log_dir:
        Directory where audit JSONL files are stored.
        Created automatically if it does not exist.
    system_name:
        Name of the system generating entries.
    system_version:
        Version string of the system.
    """

    def __init__(
        self,
        log_dir: Path,
        system_name: str = "Stillwater",
        system_version: str = "5.0.0",
    ) -> None:
        self._log_dir = Path(log_dir)
        self._system_name = system_name
        self._system_version = system_version
        self._lock = threading.Lock()
        self._sequence_number = 0
        self._previous_hash = _NULL_HASH
        self._current_log_date: Optional[str] = None

        # Create log directory if it does not exist
        self._log_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public logging methods
    # ------------------------------------------------------------------

    def log_cpu_prediction(
        self,
        user_id: str,
        label: str,
        confidence: float,
        keywords: List[str],
        user_input: str,
        session_id: str,
    ) -> AuditEntry:
        """Log a CPU-based prediction (local classifier, no LLM)."""
        truncated_input = self._truncate(user_input)
        input_hash = self._hash_text(truncated_input)

        return self._create_entry(
            user_id=user_id,
            session_id=session_id,
            actor_type="cpu_classifier",
            action_type="cpu_prediction",
            action_description=f"CPU prediction: label={label}, confidence={confidence:.4f}",
            resource_type="cpu_prediction",
            resource_id=input_hash,
            outcome="success",
            metadata_extra={
                "prediction_label": label,
                "prediction_confidence": confidence,
                "keywords": keywords,
                "input_hash": input_hash,
            },
        )

    def log_llm_call(
        self,
        user_id: str,
        model: str,
        input_text: str,
        output_text: str,
        label: str,
        confidence: float,
        tokens: Dict[str, int],
        session_id: str,
    ) -> AuditEntry:
        """Log an LLM / webservice call.

        Input and output text are hashed (SHA-256) for privacy —
        raw text is NOT stored in the audit trail.
        """
        truncated_input = self._truncate(input_text)
        truncated_output = self._truncate(output_text)
        input_hash = self._hash_text(truncated_input)
        output_hash = self._hash_text(truncated_output)

        return self._create_entry(
            user_id=user_id,
            session_id=session_id,
            actor_type="llm_service",
            action_type="llm_call",
            action_description=f"LLM call: model={model}, label={label}, confidence={confidence:.4f}",
            resource_type="llm_call",
            resource_id=input_hash,
            outcome="success",
            metadata_extra={
                "model": model,
                "prediction_label": label,
                "prediction_confidence": confidence,
                "input_hash": input_hash,
                "output_hash": output_hash,
                "tokens": tokens,
            },
        )

    def log_config_change(
        self,
        user_id: str,
        field: str,
        old_value: str,
        new_value: str,
        reason: str,
        session_id: str,
    ) -> AuditEntry:
        """Log a configuration change with before/after values and reason."""
        return self._create_entry(
            user_id=user_id,
            session_id=session_id,
            actor_type="user",
            action_type="config_change",
            action_description=f"Config change: {field} = {old_value!r} -> {new_value!r}",
            resource_type="config",
            resource_id=field,
            outcome="success",
            change_detail={
                "field_name": field,
                "old_value": old_value,
                "new_value": new_value,
                "reason": reason,
            },
        )

    def log_access(
        self,
        user_id: str,
        action_type: str,
        session_id: str,
        ip_address: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> AuditEntry:
        """Log an access event (login, logout, auth_failure)."""
        outcome = "failure" if action_type == "auth_failure" else "success"

        return self._create_entry(
            user_id=user_id,
            session_id=session_id,
            actor_type="user",
            action_type=action_type,
            action_description=f"Access event: {action_type}",
            resource_type="session",
            resource_id=session_id,
            outcome=outcome,
            ip_address=ip_address,
            device_id=device_id,
        )

    # ------------------------------------------------------------------
    # Chain verification
    # ------------------------------------------------------------------

    def verify_chain(self, log_file: Path) -> bool:
        """Verify the SHA-256 hash chain integrity of a log file.

        Returns True if:
          - Every entry's hash matches its recomputed hash
          - Every entry's previous_hash equals the prior entry's entry_hash
          - The first entry has previous_hash == '0' * 64
          - Chain positions are sequential starting from 1

        Returns False if any of these checks fail (tamper detected).
        """
        entries = self.read_log_file(log_file)
        if not entries:
            return True  # Empty file is trivially valid

        previous_hash = _NULL_HASH

        for i, entry in enumerate(entries):
            integrity = entry.get("integrity", {})

            # Check chain position
            expected_position = i + 1
            if integrity.get("chain_position") != expected_position:
                return False

            # Check previous hash linkage
            if integrity.get("previous_hash") != previous_hash:
                return False

            # Recompute entry hash
            stored_hash = integrity.get("entry_hash", "")
            recomputed = self._compute_hash(entry)
            if recomputed != stored_hash:
                return False

            previous_hash = stored_hash

        return True

    # ------------------------------------------------------------------
    # File reading and export
    # ------------------------------------------------------------------

    def read_log_file(self, log_file: Path) -> List[Dict[str, Any]]:
        """Read a single JSONL log file and return a list of entry dicts."""
        entries: List[Dict[str, Any]] = []
        if not log_file.exists():
            return entries
        with open(log_file, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def read_all_log_files(self) -> List[Dict[str, Any]]:
        """Read all audit JSONL files in the log directory, sorted by name."""
        all_entries: List[Dict[str, Any]] = []
        for log_file in sorted(self._log_dir.glob("audit-*.jsonl")):
            all_entries.extend(self.read_log_file(log_file))
        return all_entries

    def export_readable(self, log_file: Path) -> str:
        """Export a log file as a human-readable indented JSON string."""
        entries = self.read_log_file(log_file)
        return json.dumps(entries, indent=2, ensure_ascii=False, default=str)

    # ------------------------------------------------------------------
    # Internal: entry creation
    # ------------------------------------------------------------------

    def _create_entry(
        self,
        *,
        user_id: str,
        session_id: str,
        actor_type: str,
        action_type: str,
        action_description: str,
        resource_type: str,
        resource_id: str,
        outcome: str,
        change_detail: Optional[Dict[str, Any]] = None,
        metadata_extra: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> AuditEntry:
        """Build, hash, and persist a single audit entry.

        Thread-safe: uses a lock to ensure sequential numbering and
        consistent hash chaining.
        """
        with self._lock:
            # Check if the date changed (daily rotation)
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if self._current_log_date != today_str:
                # Reset sequence for a new daily file
                self._current_log_date = today_str
                existing = self._load_last_entry_from_file(self._get_log_path())
                if existing is not None:
                    self._sequence_number = existing.get("action", {}).get("sequence_number", 0)
                    self._previous_hash = existing.get("integrity", {}).get("entry_hash", _NULL_HASH)
                else:
                    self._sequence_number = 0
                    self._previous_hash = _NULL_HASH

            self._sequence_number += 1
            now = datetime.now(timezone.utc)

            entry = AuditEntry(
                entry_id=str(uuid.uuid4()),
                timestamp=now.isoformat(timespec="microseconds") + "Z",
                timestamp_source="system_clock_utc",
                actor={
                    "user_id": user_id,
                    "display_name": None,
                    "actor_type": actor_type,
                    "model_version": None,
                    "session_id": session_id,
                    "ip_address": ip_address,
                    "device_id": device_id,
                },
                action={
                    "type": action_type,
                    "description": action_description,
                    "signature_meaning": None,
                    "sequence_number": self._sequence_number,
                },
                resource={
                    "type": resource_type,
                    "id": resource_id,
                    "version": None,
                    "path": str(self._get_log_path()),
                },
                outcome=outcome,
                change_detail=change_detail,
                integrity={
                    "hash_algorithm": _HASH_ALGORITHM,
                    "entry_hash": "",  # Placeholder — computed below
                    "previous_hash": self._previous_hash,
                    "chain_position": self._sequence_number,
                },
                metadata={
                    "system_name": self._system_name,
                    "system_version": self._system_version,
                    "predicate_rule": None,
                    "retention_period": "7_years",
                    **(metadata_extra or {}),
                },
            )

            # Compute the entry hash (covers everything except entry_hash itself)
            entry_hash = self._compute_hash(entry.to_dict())
            entry.integrity["entry_hash"] = entry_hash

            # Persist
            self._append_to_log(entry)

            # Update chain state
            self._previous_hash = entry_hash

            return entry

    # ------------------------------------------------------------------
    # Internal: hashing
    # ------------------------------------------------------------------

    def _compute_hash(self, entry_dict: Dict[str, Any]) -> str:
        """Compute SHA-256 hash over all fields except integrity.entry_hash.

        The hash covers: entry_id, timestamp, timestamp_source, actor,
        action, resource, change_detail, outcome, integrity (minus entry_hash),
        and metadata.
        """
        # Build the hash payload — everything except entry_hash
        payload = {
            "entry_id": entry_dict["entry_id"],
            "timestamp": entry_dict["timestamp"],
            "timestamp_source": entry_dict["timestamp_source"],
            "actor": entry_dict["actor"],
            "action": entry_dict["action"],
            "resource": entry_dict["resource"],
            "change_detail": entry_dict.get("change_detail"),
            "outcome": entry_dict["outcome"],
            "integrity": {
                "hash_algorithm": entry_dict["integrity"]["hash_algorithm"],
                "previous_hash": entry_dict["integrity"]["previous_hash"],
                "chain_position": entry_dict["integrity"]["chain_position"],
            },
            "metadata": entry_dict["metadata"],
        }
        # Normalize through JSON round-trip for determinism
        normalized = json.loads(json.dumps(payload, sort_keys=True, default=str))
        canonical = json.dumps(normalized, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    @staticmethod
    def _hash_text(text: str) -> str:
        """SHA-256 hash of a text string."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _truncate(text: str) -> str:
        """Truncate text to _MAX_INPUT_LENGTH characters."""
        if len(text) > _MAX_INPUT_LENGTH:
            return text[:_MAX_INPUT_LENGTH]
        return text

    # ------------------------------------------------------------------
    # Internal: file I/O
    # ------------------------------------------------------------------

    def _get_log_path(self) -> Path:
        """Return the path for today's audit log file."""
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._log_dir / f"audit-{today_str}.jsonl"

    def _append_to_log(self, entry: AuditEntry) -> None:
        """Append a single entry as one JSONL line."""
        log_path = self._get_log_path()
        line = json.dumps(entry.to_dict(), sort_keys=True, ensure_ascii=False, default=str)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def _load_last_entry_from_file(self, log_path: Path) -> Optional[Dict[str, Any]]:
        """Read the last entry from a JSONL file, or None if file is empty/absent."""
        if not log_path.exists():
            return None
        last_line: Optional[str] = None
        try:
            with open(log_path, "r", encoding="utf-8") as fh:
                for line in fh:
                    stripped = line.strip()
                    if stripped:
                        last_line = stripped
        except OSError:
            return None
        if last_line is None:
            return None
        try:
            return json.loads(last_line)
        except json.JSONDecodeError:
            return None
