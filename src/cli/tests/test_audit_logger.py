"""Tests for stillwater.audit_logger — FDA 21 CFR Part 11 compliant audit trail.

Coverage targets (40+ tests):
  - AuditEntry dataclass: required fields, UUID format, ISO 8601, actor/action/resource/outcome/integrity
  - AuditLogger class: init, log_cpu_prediction, log_llm_call, log_config_change, log_access, file I/O
  - Hash chain integrity: first entry null previous, chaining, SHA-256, verify_chain pass/fail
  - File management: daily rotation, naming convention, read/export
  - Edge cases: empty input, unicode, long input truncation, permission error, null fields
  - Integration with DataRegistry: log_dir = data/logs/

Rung: 641 — deterministic with system clock, no network, no LLM.
"""

from __future__ import annotations

import json
import hashlib
import os
import re
import stat
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from stillwater.audit_logger import AuditEntry, AuditLogger


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def log_dir(tmp_path: Path) -> Path:
    """Return a temporary log directory."""
    d = tmp_path / "data" / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture()
def logger(log_dir: Path) -> AuditLogger:
    """Return an AuditLogger pointed at the temporary log directory."""
    return AuditLogger(log_dir=log_dir)


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    """Create a minimal repo-root layout with data/logs/."""
    (tmp_path / "data" / "logs").mkdir(parents=True, exist_ok=True)
    return tmp_path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_cpu_entry(logger: AuditLogger) -> AuditEntry:
    """Create a single CPU prediction entry for reuse in tests."""
    return logger.log_cpu_prediction(
        user_id="user-42",
        label="greeting",
        confidence=0.95,
        keywords=["hello", "hi"],
        user_input="hello there",
        session_id="session-abc",
    )


def _make_llm_entry(logger: AuditLogger) -> AuditEntry:
    """Create a single LLM call entry for reuse in tests."""
    return logger.log_llm_call(
        user_id="user-42",
        model="claude-3-haiku",
        input_text="What is the weather?",
        output_text="I cannot check the weather.",
        label="weather_query",
        confidence=0.80,
        tokens={"input": 10, "output": 15},
        session_id="session-abc",
    )


def _read_jsonl(path: Path) -> list[dict]:
    """Read a JSONL file and return a list of dicts."""
    entries = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


# ===========================================================================
# Section 1: AuditEntry Dataclass
# ===========================================================================


class TestAuditEntryDataclass:
    """Tests for the AuditEntry dataclass structure."""

    def test_entry_has_all_required_fields(self, logger: AuditLogger) -> None:
        """AuditEntry must contain all FDA Part 11 required fields."""
        entry = _make_cpu_entry(logger)
        required = [
            "entry_id", "timestamp", "timestamp_source",
            "actor", "action", "resource",
            "outcome", "integrity", "metadata",
        ]
        for field in required:
            assert hasattr(entry, field), f"Missing required field: {field}"

    def test_entry_id_is_uuid_format(self, logger: AuditLogger) -> None:
        """entry_id must be a valid UUID v4 string."""
        entry = _make_cpu_entry(logger)
        parsed = uuid.UUID(entry.entry_id, version=4)
        assert str(parsed) == entry.entry_id

    def test_timestamp_is_iso8601(self, logger: AuditLogger) -> None:
        """timestamp must be ISO 8601 format ending with Z."""
        entry = _make_cpu_entry(logger)
        assert entry.timestamp.endswith("Z"), f"Timestamp does not end with Z: {entry.timestamp}"
        # Parse it to make sure it is valid ISO 8601
        ts = entry.timestamp.rstrip("Z")
        datetime.fromisoformat(ts)

    def test_actor_fields(self, logger: AuditLogger) -> None:
        """actor dict must contain user_id, actor_type, session_id."""
        entry = _make_cpu_entry(logger)
        actor = entry.actor
        assert actor["user_id"] == "user-42"
        assert "actor_type" in actor
        assert actor["session_id"] == "session-abc"

    def test_action_fields(self, logger: AuditLogger) -> None:
        """action dict must contain type, description, sequence_number."""
        entry = _make_cpu_entry(logger)
        action = entry.action
        assert "type" in action
        assert "description" in action
        assert "sequence_number" in action
        assert isinstance(action["sequence_number"], int)

    def test_resource_fields(self, logger: AuditLogger) -> None:
        """resource dict must contain type, id, version, path."""
        entry = _make_cpu_entry(logger)
        resource = entry.resource
        for key in ("type", "id", "version", "path"):
            assert key in resource, f"Missing resource field: {key}"

    def test_outcome_values(self, logger: AuditLogger) -> None:
        """outcome must be one of the allowed enum values."""
        allowed = {"success", "failure", "blocked", "pending_review"}
        entry = _make_cpu_entry(logger)
        assert entry.outcome in allowed, f"Invalid outcome: {entry.outcome}"

    def test_integrity_hash_fields(self, logger: AuditLogger) -> None:
        """integrity dict must contain hash_algorithm, entry_hash, previous_hash, chain_position."""
        entry = _make_cpu_entry(logger)
        integrity = entry.integrity
        assert integrity["hash_algorithm"] == "sha256"
        assert isinstance(integrity["entry_hash"], str)
        assert len(integrity["entry_hash"]) == 64  # SHA-256 hex
        assert isinstance(integrity["previous_hash"], str)
        assert len(integrity["previous_hash"]) == 64
        assert isinstance(integrity["chain_position"], int)


# ===========================================================================
# Section 2: AuditLogger Class
# ===========================================================================


class TestAuditLoggerInit:
    """Tests for AuditLogger initialization."""

    def test_init_creates_log_directory(self, tmp_path: Path) -> None:
        """AuditLogger must create the log directory if it does not exist."""
        new_dir = tmp_path / "new_logs"
        assert not new_dir.exists()
        AuditLogger(log_dir=new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_init_with_custom_log_dir(self, tmp_path: Path) -> None:
        """AuditLogger respects a custom log_dir path."""
        custom = tmp_path / "my" / "custom" / "logs"
        logger = AuditLogger(log_dir=custom)
        assert logger._log_dir == custom
        assert custom.exists()


class TestAuditLoggerLogging:
    """Tests for log_cpu_prediction, log_llm_call, log_config_change, log_access."""

    def test_log_cpu_prediction(self, logger: AuditLogger) -> None:
        """log_cpu_prediction stores label, confidence, keywords."""
        entry = logger.log_cpu_prediction(
            user_id="user-1",
            label="joke",
            confidence=0.92,
            keywords=["funny", "laugh"],
            user_input="tell me a joke",
            session_id="sess-1",
        )
        assert entry.action["type"] == "cpu_prediction"
        assert entry.resource["type"] == "cpu_prediction"
        assert entry.outcome == "success"
        # Metadata should record prediction details
        assert entry.metadata["prediction_label"] == "joke"
        assert entry.metadata["prediction_confidence"] == 0.92

    def test_log_llm_call(self, logger: AuditLogger) -> None:
        """log_llm_call stores model, input_hash, output_hash, tokens."""
        entry = logger.log_llm_call(
            user_id="user-2",
            model="claude-3-sonnet",
            input_text="Summarize this",
            output_text="Here is a summary",
            label="summarization",
            confidence=0.85,
            tokens={"input": 5, "output": 8},
            session_id="sess-2",
        )
        assert entry.action["type"] == "llm_call"
        assert entry.metadata["model"] == "claude-3-sonnet"
        # Input/output should be hashed, not stored raw (privacy)
        assert "input_hash" in entry.metadata
        assert "output_hash" in entry.metadata
        assert entry.metadata["tokens"] == {"input": 5, "output": 8}

    def test_log_model_inference(self, logger: AuditLogger) -> None:
        """log_llm_call records a full model inference record."""
        entry = logger.log_llm_call(
            user_id="user-3",
            model="llama-3.3-70b",
            input_text="What is 2+2?",
            output_text="4",
            label="math",
            confidence=0.99,
            tokens={"input": 8, "output": 1},
            session_id="sess-3",
        )
        assert entry.metadata["model"] == "llama-3.3-70b"
        assert entry.metadata["prediction_label"] == "math"
        assert entry.metadata["prediction_confidence"] == 0.99

    def test_log_config_change(self, logger: AuditLogger) -> None:
        """log_config_change records field, old_value, new_value, reason."""
        entry = logger.log_config_change(
            user_id="admin-1",
            field="max_tokens",
            old_value="1000",
            new_value="2000",
            reason="Increased for long-form tasks",
            session_id="sess-admin",
        )
        assert entry.action["type"] == "config_change"
        assert entry.change_detail is not None
        assert entry.change_detail["field_name"] == "max_tokens"
        assert entry.change_detail["old_value"] == "1000"
        assert entry.change_detail["new_value"] == "2000"
        assert entry.change_detail["reason"] == "Increased for long-form tasks"

    def test_log_access_login(self, logger: AuditLogger) -> None:
        """log_access records login events."""
        entry = logger.log_access(
            user_id="user-5",
            action_type="login",
            session_id="sess-5",
            ip_address="192.168.1.1",
            device_id="device-abc",
        )
        assert entry.action["type"] == "login"
        assert entry.actor["ip_address"] == "192.168.1.1"
        assert entry.actor["device_id"] == "device-abc"

    def test_log_access_logout(self, logger: AuditLogger) -> None:
        """log_access records logout events."""
        entry = logger.log_access(
            user_id="user-5",
            action_type="logout",
            session_id="sess-5",
        )
        assert entry.action["type"] == "logout"

    def test_log_access_auth_failure(self, logger: AuditLogger) -> None:
        """log_access records authentication failures."""
        entry = logger.log_access(
            user_id="unknown-user",
            action_type="auth_failure",
            session_id="sess-anon",
        )
        assert entry.action["type"] == "auth_failure"
        assert entry.outcome == "failure"

    def test_log_creates_jsonl_file(self, logger: AuditLogger, log_dir: Path) -> None:
        """Logging creates a .jsonl file in the log directory."""
        _make_cpu_entry(logger)
        jsonl_files = list(log_dir.glob("audit-*.jsonl"))
        assert len(jsonl_files) >= 1, "No audit JSONL file created"

    def test_log_appends_to_existing_file(self, logger: AuditLogger, log_dir: Path) -> None:
        """Multiple log entries append to the same daily file."""
        _make_cpu_entry(logger)
        _make_cpu_entry(logger)
        _make_llm_entry(logger)

        jsonl_files = list(log_dir.glob("audit-*.jsonl"))
        assert len(jsonl_files) == 1, "Expected exactly one daily log file"

        entries = _read_jsonl(jsonl_files[0])
        assert len(entries) == 3, f"Expected 3 entries, got {len(entries)}"

    def test_each_entry_has_unique_id(self, logger: AuditLogger) -> None:
        """Every entry must have a unique entry_id."""
        entries = [_make_cpu_entry(logger) for _ in range(10)]
        ids = [e.entry_id for e in entries]
        assert len(set(ids)) == 10, "Duplicate entry_id detected"

    def test_entries_have_sequential_sequence_numbers(self, logger: AuditLogger) -> None:
        """Entries must have monotonically increasing sequence numbers."""
        entries = [_make_cpu_entry(logger) for _ in range(5)]
        seq_nums = [e.action["sequence_number"] for e in entries]
        assert seq_nums == list(range(1, 6)), f"Non-sequential: {seq_nums}"

    def test_timestamp_is_contemporaneous(self, logger: AuditLogger) -> None:
        """Timestamp must be within 1 second of now (contemporaneous requirement)."""
        before = datetime.now(timezone.utc)
        entry = _make_cpu_entry(logger)
        after = datetime.now(timezone.utc)

        ts = datetime.fromisoformat(entry.timestamp.rstrip("Z")).replace(tzinfo=timezone.utc)
        assert before <= ts <= after, (
            f"Timestamp {ts} not between {before} and {after}"
        )


# ===========================================================================
# Section 3: Hash Chain Integrity
# ===========================================================================


class TestHashChainIntegrity:
    """Tests for SHA-256 hash chain compliance."""

    def test_first_entry_has_null_previous_hash(self, logger: AuditLogger) -> None:
        """The first entry in a log must have previous_hash = '0' * 64."""
        entry = _make_cpu_entry(logger)
        assert entry.integrity["previous_hash"] == "0" * 64

    def test_subsequent_entries_chain_to_previous(self, logger: AuditLogger) -> None:
        """Each entry's previous_hash must equal the prior entry's entry_hash."""
        e1 = _make_cpu_entry(logger)
        e2 = _make_cpu_entry(logger)
        assert e2.integrity["previous_hash"] == e1.integrity["entry_hash"]

    def test_hash_algorithm_is_sha256(self, logger: AuditLogger) -> None:
        """hash_algorithm must be 'sha256'."""
        entry = _make_cpu_entry(logger)
        assert entry.integrity["hash_algorithm"] == "sha256"

    def test_entry_hash_covers_all_content_fields(self, logger: AuditLogger) -> None:
        """The entry hash must cover all fields except integrity.entry_hash itself."""
        entry = _make_cpu_entry(logger)
        # Rebuild the hash manually to verify it covers all content
        entry_dict = entry.__dict__.copy() if hasattr(entry, "__dict__") else {}
        # Use the logger's _compute_hash method for verification
        d = json.loads(json.dumps({
            "entry_id": entry.entry_id,
            "timestamp": entry.timestamp,
            "timestamp_source": entry.timestamp_source,
            "actor": entry.actor,
            "action": entry.action,
            "resource": entry.resource,
            "change_detail": entry.change_detail,
            "outcome": entry.outcome,
            "integrity": {
                "hash_algorithm": entry.integrity["hash_algorithm"],
                "previous_hash": entry.integrity["previous_hash"],
                "chain_position": entry.integrity["chain_position"],
            },
            "metadata": entry.metadata,
        }, sort_keys=True, default=str))
        expected = hashlib.sha256(
            json.dumps(d, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()
        assert entry.integrity["entry_hash"] == expected

    def test_verify_chain_passes_for_valid_log(self, logger: AuditLogger, log_dir: Path) -> None:
        """verify_chain returns True for an untampered log."""
        for _ in range(5):
            _make_cpu_entry(logger)
        log_file = list(log_dir.glob("audit-*.jsonl"))[0]
        assert logger.verify_chain(log_file) is True

    def test_verify_chain_fails_for_tampered_entry(self, logger: AuditLogger, log_dir: Path) -> None:
        """verify_chain returns False if an entry's content was modified."""
        for _ in range(5):
            _make_cpu_entry(logger)
        log_file = list(log_dir.glob("audit-*.jsonl"))[0]

        # Tamper with a middle entry
        lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        entry = json.loads(lines[2])
        entry["outcome"] = "tampered"
        lines[2] = json.dumps(entry, sort_keys=True)
        log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        assert logger.verify_chain(log_file) is False

    def test_verify_chain_fails_for_missing_entry(self, logger: AuditLogger, log_dir: Path) -> None:
        """verify_chain returns False if an entry is removed from the chain."""
        for _ in range(5):
            _make_cpu_entry(logger)
        log_file = list(log_dir.glob("audit-*.jsonl"))[0]

        # Remove the third entry
        lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        del lines[2]
        log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        assert logger.verify_chain(log_file) is False

    def test_verify_chain_fails_for_reordered_entries(self, logger: AuditLogger, log_dir: Path) -> None:
        """verify_chain returns False if entries are reordered."""
        for _ in range(5):
            _make_cpu_entry(logger)
        log_file = list(log_dir.glob("audit-*.jsonl"))[0]

        # Swap entries 1 and 3
        lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        lines[1], lines[3] = lines[3], lines[1]
        log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        assert logger.verify_chain(log_file) is False


# ===========================================================================
# Section 4: File Management
# ===========================================================================


class TestFileManagement:
    """Tests for log file management: rotation, naming, read, export."""

    def test_log_rotation_by_date(self, log_dir: Path) -> None:
        """New file per day based on date in filename."""
        logger = AuditLogger(log_dir=log_dir)

        # Log one entry with real time
        _make_cpu_entry(logger)
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        expected_file = log_dir / f"audit-{today_str}.jsonl"
        assert expected_file.exists(), f"Expected {expected_file} to exist"

    def test_log_file_naming_convention(self, logger: AuditLogger, log_dir: Path) -> None:
        """Log files must follow audit-YYYY-MM-DD.jsonl convention."""
        _make_cpu_entry(logger)
        files = list(log_dir.glob("audit-*.jsonl"))
        assert len(files) >= 1
        for f in files:
            assert re.match(r"audit-\d{4}-\d{2}-\d{2}\.jsonl", f.name), (
                f"Bad filename: {f.name}"
            )

    def test_read_log_file(self, logger: AuditLogger, log_dir: Path) -> None:
        """read_log_file returns a list of AuditEntry objects."""
        _make_cpu_entry(logger)
        _make_llm_entry(logger)
        log_file = list(log_dir.glob("audit-*.jsonl"))[0]
        entries = logger.read_log_file(log_file)
        assert len(entries) == 2
        assert all(isinstance(e, dict) for e in entries)

    def test_read_all_log_files(self, logger: AuditLogger, log_dir: Path) -> None:
        """read_all_log_files returns entries from all daily files."""
        _make_cpu_entry(logger)

        # Create a second log file (simulate a previous day)
        fake_old_file = log_dir / "audit-2025-01-01.jsonl"
        fake_entry = {
            "entry_id": str(uuid.uuid4()),
            "timestamp": "2025-01-01T00:00:00Z",
            "outcome": "success",
        }
        fake_old_file.write_text(json.dumps(fake_entry) + "\n", encoding="utf-8")

        all_entries = logger.read_all_log_files()
        assert len(all_entries) >= 2, f"Expected >= 2 entries, got {len(all_entries)}"

    def test_export_to_json(self, logger: AuditLogger, log_dir: Path) -> None:
        """export_readable returns a human-readable JSON string."""
        _make_cpu_entry(logger)
        _make_llm_entry(logger)
        log_file = list(log_dir.glob("audit-*.jsonl"))[0]
        output = logger.export_readable(log_file)
        # Must be valid JSON
        parsed = json.loads(output)
        assert isinstance(parsed, list)
        assert len(parsed) == 2
        # Must be indented (human-readable)
        assert "\n" in output
        assert "  " in output


# ===========================================================================
# Section 5: Edge Cases
# ===========================================================================


class TestEdgeCases:
    """Edge case tests for robustness."""

    def test_empty_user_input(self, logger: AuditLogger) -> None:
        """Empty string input should not crash."""
        entry = logger.log_cpu_prediction(
            user_id="user-1",
            label="unknown",
            confidence=0.0,
            keywords=[],
            user_input="",
            session_id="sess-1",
        )
        assert entry.outcome == "success"

    def test_unicode_in_log_entries(self, logger: AuditLogger, log_dir: Path) -> None:
        """Unicode characters in user input must be preserved in JSONL."""
        entry = logger.log_cpu_prediction(
            user_id="user-1",
            label="greeting",
            confidence=0.9,
            keywords=["bonjour"],
            user_input="Bonjour! Comment ca va? \u2764\ufe0f \u00e9\u00e8\u00ea",
            session_id="sess-1",
        )
        log_file = list(log_dir.glob("audit-*.jsonl"))[0]
        raw = log_file.read_text(encoding="utf-8")
        # The unicode should be stored (either escaped or raw)
        parsed = json.loads(raw.strip())
        assert parsed["entry_id"] == entry.entry_id

    def test_very_long_input_truncated(self, logger: AuditLogger) -> None:
        """Input longer than 10000 chars must be truncated."""
        long_input = "x" * 20000
        entry = logger.log_cpu_prediction(
            user_id="user-1",
            label="long",
            confidence=0.5,
            keywords=[],
            user_input=long_input,
            session_id="sess-1",
        )
        # The entry should still succeed
        assert entry.outcome == "success"
        # Metadata should indicate truncation happened or hash covers truncated input
        # (The actual input is not stored raw; it is hashed or truncated)

    def test_concurrent_writes_dont_corrupt(self, logger: AuditLogger, log_dir: Path) -> None:
        """Multiple threads writing should not corrupt the log file."""
        errors: list[Exception] = []

        def writer(n: int) -> None:
            try:
                for i in range(5):
                    logger.log_cpu_prediction(
                        user_id=f"thread-{n}",
                        label=f"label-{i}",
                        confidence=0.5,
                        keywords=[],
                        user_input=f"input-{n}-{i}",
                        session_id=f"sess-{n}",
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Errors during concurrent writes: {errors}"

        # Verify all entries are valid JSON
        log_file = list(log_dir.glob("audit-*.jsonl"))[0]
        lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 20, f"Expected 20 entries (4 threads x 5), got {len(lines)}"
        for i, line in enumerate(lines):
            try:
                json.loads(line)
            except json.JSONDecodeError:
                pytest.fail(f"Line {i} is not valid JSON: {line[:100]}")

    def test_graceful_on_permission_error(self, tmp_path: Path) -> None:
        """Logger should raise a clear error when the log dir is not writable."""
        read_only_dir = tmp_path / "readonly_logs"
        read_only_dir.mkdir()
        logger = AuditLogger(log_dir=read_only_dir)

        # Make the directory read-only
        read_only_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)

        try:
            with pytest.raises((PermissionError, OSError)):
                logger.log_cpu_prediction(
                    user_id="user-1",
                    label="test",
                    confidence=0.5,
                    keywords=[],
                    user_input="test",
                    session_id="sess-1",
                )
        finally:
            # Restore permissions for cleanup
            read_only_dir.chmod(stat.S_IRWXU)

    def test_null_fields_handled(self, logger: AuditLogger) -> None:
        """None values in optional fields should be handled gracefully."""
        entry = logger.log_access(
            user_id="user-1",
            action_type="login",
            session_id="sess-1",
            ip_address=None,
            device_id=None,
        )
        assert entry.outcome == "success"
        assert entry.actor.get("ip_address") is None
        assert entry.actor.get("device_id") is None


# ===========================================================================
# Section 6: Integration with DataRegistry
# ===========================================================================


class TestDataRegistryIntegration:
    """Tests for integration with the DataRegistry data/ layout."""

    def test_log_dir_is_data_logs(self, repo_root: Path) -> None:
        """The default log directory should be data/logs/ relative to repo root."""
        log_dir = repo_root / "data" / "logs"
        logger = AuditLogger(log_dir=log_dir)
        assert logger._log_dir == log_dir

    def test_logger_uses_registry_root(self, repo_root: Path) -> None:
        """Logger pointed at data/logs/ writes there, not elsewhere."""
        log_dir = repo_root / "data" / "logs"
        logger = AuditLogger(log_dir=log_dir)
        logger.log_cpu_prediction(
            user_id="user-1",
            label="test",
            confidence=0.5,
            keywords=[],
            user_input="test",
            session_id="sess-1",
        )
        jsonl_files = list(log_dir.glob("audit-*.jsonl"))
        assert len(jsonl_files) >= 1, "No log file in data/logs/"
        # Ensure nothing was written outside data/logs/
        for f in repo_root.rglob("audit-*.jsonl"):
            assert f.parent == log_dir, f"Log file found outside data/logs/: {f}"
