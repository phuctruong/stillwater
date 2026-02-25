from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from stillwater.audit_logger import AuditLogger
from stillwater.data_registry import DataRegistry
from stillwater.triple_twin import TripleTwinEngine


_NULL_HASH = "0" * 64


def _write_default(repo_root: Path, relative_path: str, content: str) -> None:
    target = repo_root / "data" / "default" / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _build_phase1_repo(repo_root: Path) -> None:
    _write_default(
        repo_root,
        "cpu-nodes/small-talk.md",
        (
            "---\n"
            "phase: phase1\n"
            "name: small-talk\n"
            "validator_model: haiku\n"
            "labels: [greeting, question, task]\n"
            "learnings_file: learned_phase1.jsonl\n"
            "---\n"
        ),
    )
    seeds = [
        {"keyword": "hello", "label": "greeting", "count": 25, "examples": [], "phase": "phase1"},
        {"keyword": "fix", "label": "task", "count": 25, "examples": [], "phase": "phase1"},
        {"keyword": "explain", "label": "question", "count": 25, "examples": [], "phase": "phase1"},
    ]
    _write_default(
        repo_root,
        "seeds/small-talk-seeds.jsonl",
        "\n".join(json.dumps(row) for row in seeds) + "\n",
    )


def _latest_audit_file(log_dir: Path) -> Path:
    files = sorted(log_dir.glob("audit-*.jsonl"))
    assert files, "No audit file was created"
    return files[-1]


def _read_entries(log_dir: Path) -> list[dict]:
    log_file = _latest_audit_file(log_dir)
    rows: list[dict] = []
    for line in log_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _run_engine_events(engine: TripleTwinEngine, count: int) -> None:
    for i in range(count):
        text = "fix bug now" if i % 2 else "hello there"
        engine.process(text)


@pytest.fixture()
def seeded_engine(tmp_path: Path) -> tuple[TripleTwinEngine, AuditLogger, Path]:
    repo_root = tmp_path / "repo"
    (repo_root / "data" / "default").mkdir(parents=True, exist_ok=True)
    (repo_root / "data" / "custom").mkdir(parents=True, exist_ok=True)
    log_dir = repo_root / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    _build_phase1_repo(repo_root)

    registry = DataRegistry(repo_root=repo_root)
    logger = AuditLogger(log_dir=log_dir)
    engine = TripleTwinEngine(
        registry=registry,
        llm_client=None,
        audit_logger=logger,
        session_id="sess-fda",
        user_id="fda-auditor",
    )
    return engine, logger, log_dir


@pytest.fixture()
def first_entry(seeded_engine: tuple[TripleTwinEngine, AuditLogger, Path]) -> dict:
    engine, _, log_dir = seeded_engine
    engine.process("hello there")
    entries = _read_entries(log_dir)
    assert entries
    return entries[0]


def test_hash_chain_integrity_with_100_engine_events(
    seeded_engine: tuple[TripleTwinEngine, AuditLogger, Path],
) -> None:
    engine, logger, log_dir = seeded_engine
    _run_engine_events(engine, 100)
    entries = _read_entries(log_dir)
    assert len(entries) == 100

    log_file = _latest_audit_file(log_dir)
    assert logger.verify_chain(log_file) is True

    previous = _NULL_HASH
    for idx, row in enumerate(entries, start=1):
        integrity = row["integrity"]
        assert integrity["chain_position"] == idx
        assert integrity["previous_hash"] == previous
        previous = integrity["entry_hash"]


def test_append_only_file_mode_never_uses_write_mode(
    seeded_engine: tuple[TripleTwinEngine, AuditLogger, Path],
) -> None:
    engine, _, _ = seeded_engine
    real_open = open
    modes: list[str] = []

    def tracking_open(file: object, mode: str = "r", *args: object, **kwargs: object):
        if str(file).endswith(".jsonl"):
            modes.append(mode)
        return real_open(file, mode, *args, **kwargs)

    with patch("builtins.open", side_effect=tracking_open):
        _run_engine_events(engine, 5)

    assert any("a" in mode for mode in modes)
    assert all("w" not in mode for mode in modes)


def test_alcoa_attributable_actor_fields_present(first_entry: dict) -> None:
    actor = first_entry["actor"]
    assert actor["user_id"] == "fda-auditor"
    assert actor["actor_type"]
    assert actor["session_id"]


def test_alcoa_legible_entry_is_json_serializable(first_entry: dict) -> None:
    payload = json.dumps(first_entry, sort_keys=True)
    assert payload.startswith("{")
    assert '"action"' in payload


def test_alcoa_contemporaneous_timestamp_is_iso_utc(first_entry: dict) -> None:
    ts = first_entry["timestamp"]
    assert ts.endswith("Z")
    datetime.fromisoformat(ts.rstrip("Z"))


def test_alcoa_original_first_entry_points_to_null_hash(first_entry: dict) -> None:
    assert first_entry["integrity"]["previous_hash"] == _NULL_HASH


def test_alcoa_accurate_hash_field_shape(
    seeded_engine: tuple[TripleTwinEngine, AuditLogger, Path],
) -> None:
    engine, logger, log_dir = seeded_engine
    _run_engine_events(engine, 3)
    row = _read_entries(log_dir)[-1]
    assert len(row["integrity"]["entry_hash"]) == 64
    assert logger.verify_chain(_latest_audit_file(log_dir)) is True


def test_alcoa_complete_required_sections_present(first_entry: dict) -> None:
    for key in ("entry_id", "timestamp", "actor", "action", "resource", "outcome", "integrity", "metadata"):
        assert key in first_entry
        assert first_entry[key] not in (None, "")


def test_alcoa_consistent_sequence_numbers_increment(
    seeded_engine: tuple[TripleTwinEngine, AuditLogger, Path],
) -> None:
    engine, _, log_dir = seeded_engine
    _run_engine_events(engine, 4)
    entries = _read_entries(log_dir)
    seq = [row["action"]["sequence_number"] for row in entries]
    assert seq == [1, 2, 3, 4]


def test_alcoa_enduring_log_persists_on_disk(
    seeded_engine: tuple[TripleTwinEngine, AuditLogger, Path],
) -> None:
    engine, _, log_dir = seeded_engine
    _run_engine_events(engine, 2)
    log_file = _latest_audit_file(log_dir)
    assert log_file.exists()
    assert log_file.stat().st_size > 0


def test_alcoa_available_export_readable_returns_content(
    seeded_engine: tuple[TripleTwinEngine, AuditLogger, Path],
) -> None:
    engine, logger, log_dir = seeded_engine
    _run_engine_events(engine, 2)
    log_file = _latest_audit_file(log_dir)
    exported = logger.export_readable(log_file)
    assert exported
    assert "entry_id" in exported


def test_alcoa_traceable_second_entry_links_to_first_hash(
    seeded_engine: tuple[TripleTwinEngine, AuditLogger, Path],
) -> None:
    engine, _, log_dir = seeded_engine
    _run_engine_events(engine, 2)
    first, second = _read_entries(log_dir)
    assert second["integrity"]["previous_hash"] == first["integrity"]["entry_hash"]


def test_tamper_detection_fails_when_middle_entry_is_modified(
    seeded_engine: tuple[TripleTwinEngine, AuditLogger, Path],
) -> None:
    engine, logger, log_dir = seeded_engine
    _run_engine_events(engine, 11)
    log_file = _latest_audit_file(log_dir)
    rows = _read_entries(log_dir)
    rows[5]["metadata"]["prediction_label"] = "tampered"
    log_file.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )
    assert logger.verify_chain(log_file) is False


def test_tamper_detection_fails_when_previous_hash_is_modified(
    seeded_engine: tuple[TripleTwinEngine, AuditLogger, Path],
) -> None:
    engine, logger, log_dir = seeded_engine
    _run_engine_events(engine, 5)
    log_file = _latest_audit_file(log_dir)
    rows = _read_entries(log_dir)
    rows[3]["integrity"]["previous_hash"] = "f" * 64
    log_file.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )
    assert logger.verify_chain(log_file) is False


def test_tamper_detection_fails_when_chain_position_is_modified(
    seeded_engine: tuple[TripleTwinEngine, AuditLogger, Path],
) -> None:
    engine, logger, log_dir = seeded_engine
    _run_engine_events(engine, 5)
    log_file = _latest_audit_file(log_dir)
    rows = _read_entries(log_dir)
    rows[4]["integrity"]["chain_position"] = 999
    log_file.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )
    assert logger.verify_chain(log_file) is False


def test_thread_safety_four_threads_twenty_five_events_each(
    seeded_engine: tuple[TripleTwinEngine, AuditLogger, Path],
) -> None:
    engine, logger, log_dir = seeded_engine

    def worker(prefix: str) -> None:
        for i in range(25):
            engine.process(f"fix bug {prefix}-{i}")

    threads = [threading.Thread(target=worker, args=(f"t{idx}",)) for idx in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    entries = _read_entries(log_dir)
    assert len(entries) == 100
    assert logger.verify_chain(_latest_audit_file(log_dir)) is True
