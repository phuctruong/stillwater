"""Tests for stillwater.sync_client and stillwater.cli_sync.

Coverage targets:
  - SyncClient.push_data with valid API key (mocked Firestore)
  - SyncClient.push_data with invalid key -> RuntimeError -> error dict
  - SyncClient.pull_data with valid key (mocked Firestore)
  - SyncClient.pull_data offline -> graceful error dict (no crash)
  - Conflict resolution: local newer -> local wins (remote skipped)
  - Conflict resolution: remote newer -> remote wins (file overwritten)
  - Resume interrupted sync: push picks up all files present
  - SyncClient.get_sync_status returns correct metadata
  - SyncClient.validate_api_key: returns True on HTTP 200 valid=True
  - SyncClient.validate_api_key: returns False on HTTP 401
  - SyncClient.validate_api_key: returns False on network error (offline)
  - SyncClient._load_jsonl helper: malformed lines are skipped
  - SyncClient._write_jsonl_atomic helper: writes and cleans up tmp
  - SyncClient._newest_timestamp: returns most recent timestamp
  - handle_sync push: missing api_key -> exit code 1
  - handle_sync push: invalid key format -> exit code 1
  - handle_sync push: dry-run -> exit code 0, no upload
  - handle_sync status: no settings file -> shows 'not configured'
  - handle_sync status: with valid key in settings -> shows key masked
  - cli.py integration: 'data sync' subcommand is registered

Rung: 641 — deterministic, no real network, testable.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import types
import urllib.error
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Ensure cli/src is on path (mirrors conftest.py but explicit here).
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stillwater.sync_client import (
    SyncClient,
    _load_jsonl,
    _newest_timestamp,
    _utc_now,
    _write_jsonl_atomic,
)
from stillwater.cli_sync import (
    _handle_push,
    _handle_pull,
    _handle_status,
    handle_sync,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_data_dir(tmp_path: Path) -> Path:
    """Return a temp directory with a couple of learned_*.jsonl files."""
    data_dir = tmp_path / "data" / "custom"
    data_dir.mkdir(parents=True)
    # Two files with one record each.
    f1 = data_dir / "learned_wishes.jsonl"
    f1.write_text(
        json.dumps({"id": "w1", "text": "wish one", "_updated_at": "2026-01-10T00:00:00Z"}) + "\n",
        encoding="utf-8",
    )
    f2 = data_dir / "learned_combos.jsonl"
    f2.write_text(
        json.dumps({"id": "c1", "text": "combo one", "_updated_at": "2026-01-10T00:00:00Z"}) + "\n",
        encoding="utf-8",
    )
    return data_dir


@pytest.fixture()
def valid_key() -> str:
    return "sw_sk_" + "a" * 48


@pytest.fixture()
def mock_firestore_client():
    """Return a MagicMock that simulates google.cloud.firestore.Client."""
    client = MagicMock()

    # Mimic collection().document().collection().document().set() chain.
    collection_mock = MagicMock()
    doc_mock = MagicMock()
    sub_col_mock = MagicMock()
    sub_doc_mock = MagicMock()

    client.collection.return_value = collection_mock
    collection_mock.document.return_value = doc_mock
    doc_mock.collection.return_value = sub_col_mock
    sub_doc_mock.set.return_value = None
    sub_col_mock.document.return_value = sub_doc_mock

    # stream() returns empty by default (override in tests that need data).
    sub_col_mock.stream.return_value = iter([])

    return client


# ---------------------------------------------------------------------------
# Helper: build a SyncClient with Firestore already injected (no network).
# ---------------------------------------------------------------------------


def _make_client(api_key: str, fs_client: Any, user_id: str = "user123") -> SyncClient:
    """Return a SyncClient with mocked Firestore and user_id pre-set."""
    client = SyncClient(api_key=api_key, solaceagi_base="http://localhost:9999")
    client._fs_client = fs_client
    client._user_id = user_id
    return client


# ---------------------------------------------------------------------------
# Test 1: push_data with valid API key (mocked Firestore)
# ---------------------------------------------------------------------------


def test_push_data_success(
    tmp_data_dir: Path,
    valid_key: str,
    mock_firestore_client: MagicMock,
) -> None:
    """push_data uploads all learned_*.jsonl and returns success=True."""
    client = _make_client(valid_key, mock_firestore_client)

    result = client.push_data(str(tmp_data_dir))

    assert result["success"] is True, f"Expected success, got: {result}"
    assert result["uploaded_files"] == 2
    assert result["uploaded_records"] == 2
    assert result["error"] is None


# ---------------------------------------------------------------------------
# Test 2: push_data with invalid key (validate_api_key returns False)
# ---------------------------------------------------------------------------


def test_push_data_invalid_key(tmp_data_dir: Path, valid_key: str) -> None:
    """push_data with a client whose validate_api_key fails returns error dict."""
    client = SyncClient(api_key=valid_key, solaceagi_base="http://localhost:9999")

    # _get_firestore will call validate_api_key which makes a network call to
    # localhost:9999 — that will fail, raising RuntimeError inside _get_firestore.
    result = client.push_data(str(tmp_data_dir))

    assert result["success"] is False
    assert result["error"] is not None


# ---------------------------------------------------------------------------
# Test 3: pull_data with valid key (mocked Firestore)
# ---------------------------------------------------------------------------


def test_pull_data_success(
    tmp_path: Path,
    valid_key: str,
    mock_firestore_client: MagicMock,
) -> None:
    """pull_data downloads docs and writes them to local_data_dir."""
    data_dir = tmp_path / "data" / "custom"
    data_dir.mkdir(parents=True)

    # Create two fake Firestore documents.
    records_w = [{"id": "w1", "text": "remote wish", "_updated_at": "2026-02-01T00:00:00Z"}]
    records_c = [{"id": "c1", "text": "remote combo", "_updated_at": "2026-02-01T00:00:00Z"}]

    def _make_doc(doc_id: str, records: list) -> MagicMock:
        doc = MagicMock()
        doc.id = doc_id
        doc.to_dict.return_value = {
            "_file": f"{doc_id}.jsonl",
            "records": [json.dumps(r) for r in records],
            "_updated_at": "2026-02-01T00:00:00Z",
        }
        return doc

    sub_col = mock_firestore_client.collection.return_value.document.return_value.collection.return_value
    sub_col.stream.return_value = iter([
        _make_doc("learned_wishes", records_w),
        _make_doc("learned_combos", records_c),
    ])

    client = _make_client(valid_key, mock_firestore_client)
    result = client.pull_data(str(data_dir))

    assert result["success"] is True, f"Expected success: {result}"
    assert result["downloaded_files"] == 2
    assert result["downloaded_records"] == 2
    assert (data_dir / "learned_wishes.jsonl").exists()
    assert (data_dir / "learned_combos.jsonl").exists()


# ---------------------------------------------------------------------------
# Test 4: pull_data offline -> graceful error
# ---------------------------------------------------------------------------


def test_pull_data_offline(tmp_path: Path, valid_key: str) -> None:
    """pull_data with no network returns an error dict, never crashes."""
    data_dir = tmp_path / "data" / "custom"
    data_dir.mkdir(parents=True)

    client = SyncClient(api_key=valid_key, solaceagi_base="http://localhost:9999")

    # _get_firestore will try to validate key -> network fails -> RuntimeError
    result = client.pull_data(str(data_dir))

    assert result["success"] is False
    assert result["error"] is not None
    # No crash — we got a clean dict back.


# ---------------------------------------------------------------------------
# Test 5: Conflict resolution — local newer -> local wins
# ---------------------------------------------------------------------------


def test_conflict_local_newer_wins(
    tmp_path: Path,
    valid_key: str,
    mock_firestore_client: MagicMock,
) -> None:
    """When local timestamp is newer than remote, local file is kept unchanged."""
    data_dir = tmp_path / "data" / "custom"
    data_dir.mkdir(parents=True)

    # Local file with newer timestamp.
    local_ts = "2026-03-01T00:00:00Z"
    remote_ts = "2026-01-01T00:00:00Z"
    local_record = {"id": "w1", "text": "local version", "_updated_at": local_ts}
    local_file = data_dir / "learned_wishes.jsonl"
    local_file.write_text(json.dumps(local_record) + "\n", encoding="utf-8")

    remote_records = [{"id": "w1", "text": "remote version", "_updated_at": remote_ts}]

    def _make_doc(doc_id: str, records: list, r_ts: str) -> MagicMock:
        doc = MagicMock()
        doc.id = doc_id
        doc.to_dict.return_value = {
            "_file": f"{doc_id}.jsonl",
            "records": [json.dumps(r) for r in records],
            "_updated_at": r_ts,
        }
        return doc

    sub_col = mock_firestore_client.collection.return_value.document.return_value.collection.return_value
    sub_col.stream.return_value = iter([_make_doc("learned_wishes", remote_records, remote_ts)])

    client = _make_client(valid_key, mock_firestore_client)
    result = client.pull_data(str(data_dir))

    assert result["success"] is True
    # Local should be unchanged — local version wins.
    content = local_file.read_text(encoding="utf-8")
    assert "local version" in content, "Local file was overwritten despite being newer"
    assert result["conflicts_resolved"] == 1


# ---------------------------------------------------------------------------
# Test 6: Conflict resolution — remote newer -> remote wins
# ---------------------------------------------------------------------------


def test_conflict_remote_newer_wins(
    tmp_path: Path,
    valid_key: str,
    mock_firestore_client: MagicMock,
) -> None:
    """When remote timestamp is newer than local, remote record is written."""
    data_dir = tmp_path / "data" / "custom"
    data_dir.mkdir(parents=True)

    local_ts = "2026-01-01T00:00:00Z"
    remote_ts = "2026-03-01T00:00:00Z"
    local_record = {"id": "w1", "text": "old local", "_updated_at": local_ts}
    local_file = data_dir / "learned_wishes.jsonl"
    local_file.write_text(json.dumps(local_record) + "\n", encoding="utf-8")

    remote_records = [{"id": "w1", "text": "new remote", "_updated_at": remote_ts}]

    def _make_doc(doc_id: str, records: list, r_ts: str) -> MagicMock:
        doc = MagicMock()
        doc.id = doc_id
        doc.to_dict.return_value = {
            "_file": f"{doc_id}.jsonl",
            "records": [json.dumps(r) for r in records],
            "_updated_at": r_ts,
        }
        return doc

    sub_col = mock_firestore_client.collection.return_value.document.return_value.collection.return_value
    sub_col.stream.return_value = iter([_make_doc("learned_wishes", remote_records, remote_ts)])

    client = _make_client(valid_key, mock_firestore_client)
    result = client.pull_data(str(data_dir))

    assert result["success"] is True
    content = local_file.read_text(encoding="utf-8")
    assert "new remote" in content, "Remote data not written despite being newer"
    assert result["conflicts_resolved"] == 1


# ---------------------------------------------------------------------------
# Test 7: Resume interrupted sync — push picks up all files present
# ---------------------------------------------------------------------------


def test_push_resumes_all_files(
    tmp_path: Path,
    valid_key: str,
    mock_firestore_client: MagicMock,
) -> None:
    """push_data uploads all learned_*.jsonl regardless of prior sync state."""
    data_dir = tmp_path / "data" / "custom"
    data_dir.mkdir(parents=True)

    # Create 3 files to simulate a collection that grew since last sync.
    for i in range(1, 4):
        (data_dir / f"learned_batch_{i}.jsonl").write_text(
            json.dumps({"id": f"r{i}", "v": i}) + "\n", encoding="utf-8"
        )

    client = _make_client(valid_key, mock_firestore_client)
    result = client.push_data(str(data_dir))

    assert result["success"] is True
    assert result["uploaded_files"] == 3
    assert result["uploaded_records"] == 3


# ---------------------------------------------------------------------------
# Test 8: get_sync_status returns correct metadata
# ---------------------------------------------------------------------------


def test_get_sync_status(
    valid_key: str,
    mock_firestore_client: MagicMock,
) -> None:
    """get_sync_status reads the _sync_metadata doc and returns it."""
    sub_doc_mock = mock_firestore_client.collection.return_value.document.return_value.collection.return_value.document.return_value
    snap = MagicMock()
    snap.exists = True
    snap.to_dict.return_value = {
        "last_push_at": "2026-02-01T12:00:00Z",
        "uploaded_files": 5,
        "uploaded_records": 42,
    }
    sub_doc_mock.get.return_value = snap

    client = _make_client(valid_key, mock_firestore_client)
    result = client.get_sync_status()

    assert result["success"] is True
    assert result["last_synced_at"] == "2026-02-01T12:00:00Z"
    assert result["total_uploaded_files"] == 5
    assert result["total_uploaded_records"] == 42
    assert result["error"] is None


# ---------------------------------------------------------------------------
# Test 9: validate_api_key returns True on HTTP 200 valid=True
# ---------------------------------------------------------------------------


def test_validate_api_key_success(valid_key: str) -> None:
    """validate_api_key returns True when the server responds valid=True."""
    import urllib.request as _urllib_req  # noqa: PLC0415

    response_body = json.dumps({"valid": True, "user_id": "user42"}).encode("utf-8")

    mock_resp = MagicMock()
    mock_resp.read.return_value = response_body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch.object(_urllib_req, "urlopen", return_value=mock_resp):
        client = SyncClient(api_key=valid_key, solaceagi_base="http://localhost:9999")
        ok = client.validate_api_key()

    assert ok is True
    assert client._user_id == "user42"


# ---------------------------------------------------------------------------
# Test 10: validate_api_key returns False on HTTP 401
# ---------------------------------------------------------------------------


def test_validate_api_key_401(valid_key: str) -> None:
    """validate_api_key returns False on any HTTP error."""
    import urllib.request as _urllib_req  # noqa: PLC0415

    with patch.object(
        _urllib_req,
        "urlopen",
        side_effect=urllib.error.HTTPError(
            url="http://localhost:9999/api/v1/auth/validate",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=None,
        ),
    ):
        client = SyncClient(api_key=valid_key, solaceagi_base="http://localhost:9999")
        ok = client.validate_api_key()

    assert ok is False


# ---------------------------------------------------------------------------
# Test 11: validate_api_key returns False on network error (offline)
# ---------------------------------------------------------------------------


def test_validate_api_key_offline(valid_key: str) -> None:
    """validate_api_key returns False when the network is unreachable."""
    import urllib.request as _urllib_req  # noqa: PLC0415

    with patch.object(
        _urllib_req,
        "urlopen",
        side_effect=urllib.error.URLError("Network unreachable"),
    ):
        client = SyncClient(api_key=valid_key, solaceagi_base="http://localhost:9999")
        ok = client.validate_api_key()

    assert ok is False


# ---------------------------------------------------------------------------
# Test 12: _load_jsonl skips malformed lines
# ---------------------------------------------------------------------------


def test_load_jsonl_skips_malformed(tmp_path: Path) -> None:
    """_load_jsonl silently skips lines that are not valid JSON dicts."""
    fpath = tmp_path / "learned_test.jsonl"
    fpath.write_text(
        '{"id": "good1"}\n'
        "NOT JSON AT ALL\n"
        '{"id": "good2"}\n'
        "[1, 2, 3]\n",  # valid JSON but not a dict
        encoding="utf-8",
    )

    records = _load_jsonl(fpath)

    assert len(records) == 2
    assert records[0]["id"] == "good1"
    assert records[1]["id"] == "good2"


# ---------------------------------------------------------------------------
# Test 13: _write_jsonl_atomic writes and cleans up tmp file
# ---------------------------------------------------------------------------


def test_write_jsonl_atomic(tmp_path: Path) -> None:
    """_write_jsonl_atomic writes records and leaves no .tmp file behind."""
    fpath = tmp_path / "learned_out.jsonl"
    records = [{"id": "r1", "v": 1}, {"id": "r2", "v": 2}]

    _write_jsonl_atomic(fpath, records)

    assert fpath.exists()
    lines = [l.strip() for l in fpath.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 2
    loaded = [json.loads(l) for l in lines]
    assert loaded[0]["id"] == "r1"
    assert loaded[1]["id"] == "r2"

    # No .tmp files left.
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert tmp_files == [], f"Temp files not cleaned up: {tmp_files}"


# ---------------------------------------------------------------------------
# Test 14: _newest_timestamp returns the most recent _updated_at
# ---------------------------------------------------------------------------


def test_newest_timestamp_returns_most_recent() -> None:
    """_newest_timestamp picks the lexicographically greatest ISO-8601 string."""
    records = [
        {"_updated_at": "2026-01-05T00:00:00Z"},
        {"_updated_at": "2026-03-01T00:00:00Z"},
        {"_updated_at": "2026-02-15T00:00:00Z"},
        {},  # no timestamp
    ]
    ts = _newest_timestamp(records)
    assert ts == "2026-03-01T00:00:00Z"


def test_newest_timestamp_all_missing() -> None:
    """_newest_timestamp returns None when no record has _updated_at."""
    records = [{"id": "a"}, {"id": "b"}]
    ts = _newest_timestamp(records)
    assert ts is None


# ---------------------------------------------------------------------------
# Test 15: handle_sync push — missing api_key -> exit code 1
# ---------------------------------------------------------------------------


def test_handle_push_missing_api_key(tmp_path: Path) -> None:
    """push command exits with code 1 when no API key is configured."""
    ns = argparse.Namespace(sync_cmd="push", data_dir=None, dry_run=False)

    # Patch _find_repo_root to return tmp_path (no settings.md -> no key).
    with patch("stillwater.cli_sync._find_repo_root", return_value=tmp_path):
        exit_code = _handle_push(ns)

    assert exit_code == 1


# ---------------------------------------------------------------------------
# Test 16: handle_sync push — invalid key format -> exit code 1
# ---------------------------------------------------------------------------


def test_handle_push_invalid_key_format(tmp_path: Path) -> None:
    """push exits with code 1 when the key fails format validation."""
    # Write a settings.md with a bad key.
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    settings = data_dir / "settings.md"
    settings.write_text(
        "---\napi_key: not_a_valid_key\nfirestore_enabled: false\n"
        "last_sync_timestamp: null\nlast_sync_status: pending\n---\n",
        encoding="utf-8",
    )

    ns = argparse.Namespace(sync_cmd="push", data_dir=None, dry_run=False)

    with patch("stillwater.cli_sync._find_repo_root", return_value=tmp_path):
        exit_code = _handle_push(ns)

    assert exit_code == 1


# ---------------------------------------------------------------------------
# Test 17: handle_sync push — dry-run -> exit code 0, no upload
# ---------------------------------------------------------------------------


def test_handle_push_dry_run(tmp_path: Path) -> None:
    """push --dry-run exits 0 and does not call SyncClient.push_data."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    valid_key = "sw_sk_" + "b" * 48
    settings = data_dir / "settings.md"
    settings.write_text(
        f"---\napi_key: {valid_key}\nfirestore_enabled: true\n"
        "last_sync_timestamp: null\nlast_sync_status: pending\n---\n",
        encoding="utf-8",
    )
    # Create a learned file so there's something to push.
    custom_dir = data_dir / "custom"
    custom_dir.mkdir(parents=True)
    (custom_dir / "learned_test.jsonl").write_text('{"id":"t1"}\n', encoding="utf-8")

    ns = argparse.Namespace(sync_cmd="push", data_dir=None, dry_run=True)

    with patch("stillwater.cli_sync._find_repo_root", return_value=tmp_path):
        with patch("stillwater.sync_client.SyncClient.push_data") as mock_push:
            exit_code = _handle_push(ns)

    assert exit_code == 0
    mock_push.assert_not_called()


# ---------------------------------------------------------------------------
# Test 18: handle_sync status — no settings file -> shows 'not configured'
# ---------------------------------------------------------------------------


def test_handle_status_no_settings(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """status shows 'not configured' when data/settings.md is absent."""
    ns = argparse.Namespace(sync_cmd="status")

    with patch("stillwater.cli_sync._find_repo_root", return_value=tmp_path):
        exit_code = _handle_status(ns)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "not configured" in captured.out.lower() or "not configured" in captured.out


# ---------------------------------------------------------------------------
# Test 19: handle_sync status — with valid key -> shows masked key
# ---------------------------------------------------------------------------


def test_handle_status_with_valid_key(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """status shows a masked version of the configured API key."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    valid_key = "sw_sk_" + "c" * 48
    settings = data_dir / "settings.md"
    settings.write_text(
        f"---\napi_key: {valid_key}\nfirestore_enabled: true\n"
        "last_sync_timestamp: 2026-02-01T00:00:00Z\nlast_sync_status: ok\n---\n",
        encoding="utf-8",
    )

    ns = argparse.Namespace(sync_cmd="status")

    with patch("stillwater.cli_sync._find_repo_root", return_value=tmp_path):
        exit_code = _handle_status(ns)

    captured = capsys.readouterr()
    assert exit_code == 0
    # Key should be masked (first 10 + last 6 chars).
    assert "sw_sk_cccc" in captured.out
    # Should NOT print the full key.
    assert valid_key not in captured.out


# ---------------------------------------------------------------------------
# Test 20: cli.py integration — 'data sync' subcommand is registered
# ---------------------------------------------------------------------------


def test_cli_data_sync_subcommand_registered() -> None:
    """The main CLI parser must recognise 'data sync status' without error."""
    from stillwater.cli import main  # noqa: PLC0415

    # Patch handle_sync to avoid real work; just confirm argument parsing works.
    with patch("stillwater.cli_sync.handle_sync", return_value=0) as mock_handle:
        exit_code = main(["data", "sync", "status"])

    assert exit_code == 0
    mock_handle.assert_called_once()
