from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import admin.app as admin_app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("STILLWATER_MACHINE_ALLOWED_ROOTS", str(tmp_path))
    app = admin_app.create_app()
    return TestClient(app)


def _allow_machine(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(admin_app, "_oauth3_validate_or_raise", lambda *args, **kwargs: None)


def test_machine_list_requires_token(client: TestClient) -> None:
    resp = client.get("/api/machine/files/list")
    assert resp.status_code == 401


def test_machine_list_directory_success(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    resp = client.get("/api/machine/files/list", params={"path": str(tmp_path)})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert any(e["name"] == "a.txt" for e in resp.json()["entries"])


def test_machine_list_missing_path_404(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    missing = tmp_path / "does-not-exist-xyz"
    resp = client.get("/api/machine/files/list", params={"path": str(missing)})
    assert resp.status_code == 404


def test_machine_list_not_directory_400(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    f = tmp_path / "file.txt"
    f.write_text("x", encoding="utf-8")
    resp = client.get("/api/machine/files/list", params={"path": str(f)})
    assert resp.status_code == 400


def test_machine_read_file_success(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    f = tmp_path / "readme.txt"
    f.write_text("hello", encoding="utf-8")
    resp = client.get("/api/machine/files/read", params={"path": str(f)})
    assert resp.status_code == 200
    assert resp.json()["content"] == "hello"


def test_machine_read_path_traversal_blocked(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    resp = client.get("/api/machine/files/read", params={"path": "../../../etc/passwd"})
    assert resp.status_code == 403


def test_machine_read_outside_root_blocked(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    resp = client.get("/api/machine/files/read", params={"path": "/etc/passwd"})
    assert resp.status_code == 403


def test_machine_write_and_read_roundtrip(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    target = tmp_path / "note.txt"
    w = client.post("/api/machine/files/write", json={"path": str(target), "content": "abc"})
    assert w.status_code == 200
    r = client.get("/api/machine/files/read", params={"path": str(target)})
    assert r.status_code == 200
    assert r.json()["content"] == "abc"


def test_machine_write_path_traversal_blocked(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    resp = client.post("/api/machine/files/write", json={"path": "../bad.txt", "content": "x"})
    assert resp.status_code == 403


def test_machine_delete_file_success(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    target = tmp_path / "delete-me.txt"
    target.write_text("x", encoding="utf-8")
    resp = client.request("DELETE", "/api/machine/files/delete", json={"path": str(target)})
    assert resp.status_code == 200
    assert target.exists() is False


def test_machine_delete_missing_404(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    target = tmp_path / "missing.txt"
    resp = client.request("DELETE", "/api/machine/files/delete", json={"path": str(target)})
    assert resp.status_code == 404


def test_machine_delete_directory_rejected(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    d = tmp_path / "dir"
    d.mkdir()
    resp = client.request("DELETE", "/api/machine/files/delete", json={"path": str(d)})
    assert resp.status_code == 400


def test_terminal_allowlist_endpoint(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    resp = client.get("/api/machine/terminal/allowlist")
    assert resp.status_code == 200
    assert "ls" in resp.json()["allowlist"]


def test_terminal_allowlisted_requires_allowlisted_command(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    resp = client.post("/api/machine/terminal/allowlisted", json={"command": "python -V"})
    assert resp.status_code == 403


def test_terminal_allowlisted_blocks_rm_rf(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    resp = client.post("/api/machine/terminal/allowlisted", json={"command": "rm -rf /"})
    assert resp.status_code == 403


def test_terminal_allowlisted_executes(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    resp = client.post("/api/machine/terminal/allowlisted", json={"command": "echo hello"})
    assert resp.status_code == 200
    assert "hello" in resp.json()["stdout"]


def test_terminal_execute_blocks_dd_if(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    resp = client.post("/api/machine/terminal/execute", json={"command": "dd if=/dev/zero of=/tmp/x"})
    assert resp.status_code == 403


def test_terminal_execute_runs_command(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    resp = client.post("/api/machine/terminal/execute", json={"command": "echo exec-ok"})
    assert resp.status_code == 200
    assert "exec-ok" in resp.json()["stdout"]


def test_terminal_execute_respects_cwd_guard(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    resp = client.post(
        "/api/machine/terminal/execute",
        json={"command": "pwd", "cwd": "/etc"},
    )
    assert resp.status_code == 403


def test_system_info(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    resp = client.get("/api/machine/system/info")
    assert resp.status_code == 200
    assert "uname" in resp.json()


def test_system_processes(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    resp = client.get("/api/machine/system/processes")
    assert resp.status_code == 200
    assert isinstance(resp.json()["processes"], list)


def test_tunnel_connect_status_disconnect(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    connected = client.post("/api/machine/tunnel/connect", json={"name": "qa"})
    assert connected.status_code == 200
    assert connected.json()["tunnel"]["connected"] is True

    status = client.get("/api/machine/tunnel/status")
    assert status.status_code == 200
    assert status.json()["tunnel"]["connected"] is True

    disconnected = client.post("/api/machine/tunnel/disconnect")
    assert disconnected.status_code == 200
    assert disconnected.json()["tunnel"]["connected"] is False


def test_machine_audit_written_for_actions(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _allow_machine(monkeypatch)
    target = tmp_path / "audit.txt"
    client.post("/api/machine/files/write", json={"path": str(target), "content": "audit"})
    client.get("/api/machine/files/read", params={"path": str(target)})
    audit_file = Path("/home/phuc/projects/stillwater/data/logs/machine-audit.jsonl")
    assert audit_file.exists()
    lines = [line for line in audit_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) >= 2
    row = json.loads(lines[-1])
    assert "entry_hash" in row
    assert "prev_hash" in row


def test_oauth_service_unavailable_is_503(client: TestClient) -> None:
    resp = client.get(
        "/api/machine/files/list",
        params={"path": "/tmp"},
        headers={"X-Agency-Token": "tok"},
    )
    assert resp.status_code == 503
