from __future__ import annotations

import io
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_DIR = REPO_ROOT / "admin"
CLI_SRC = REPO_ROOT / "src" / "cli" / "src"
for _path in (str(REPO_ROOT), str(ADMIN_DIR), str(CLI_SRC)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import services.oauth3_service as oauth3_module
from services.oauth3_service import app as oauth3_app
from services.orchestration_service import OrchestrationService


class _HTTPResponse:
    def __init__(self, status: int, body: bytes):
        self.status = status
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture()
def oauth_client(tmp_path: Path, monkeypatch) -> TestClient:
    oauth3_module._tokens.clear()
    oauth3_module._consent_log.clear()
    oauth3_module._step_up_log.clear()
    audit_path = tmp_path / "oauth3" / "oauth3_audit.jsonl"
    monkeypatch.setattr(oauth3_module, "AUDIT_PATH", audit_path)
    with TestClient(oauth3_app) as client:
        yield client
    oauth3_module._tokens.clear()
    oauth3_module._consent_log.clear()
    oauth3_module._step_up_log.clear()


@pytest.fixture()
def orchestration_client(tmp_path: Path, monkeypatch, oauth_client: TestClient) -> TestClient:
    repo = tmp_path / "repo"
    (repo / "data" / "default" / "cpu-nodes").mkdir(parents=True, exist_ok=True)
    (repo / "data" / "default" / "seeds").mkdir(parents=True, exist_ok=True)
    (repo / "data" / "default" / "smalltalk").mkdir(parents=True, exist_ok=True)
    (repo / "data" / "custom").mkdir(parents=True, exist_ok=True)

    (repo / "data" / "default" / "cpu-nodes" / "phase1.md").write_text(
        """---
phase: 1
name: phase1-smalltalk
validator_model: haiku
labels: [greeting, task, question]
learnings_file: learned_phase1.jsonl
---
# phase1
""",
        encoding="utf-8",
    )
    (repo / "data" / "default" / "cpu-nodes" / "phase2.md").write_text(
        """---
phase: 2
name: phase2-intent
validator_model: sonnet
labels: [bugfix, research]
learnings_file: learned_phase2.jsonl
---
# phase2
""",
        encoding="utf-8",
    )
    (repo / "data" / "default" / "cpu-nodes" / "phase3.md").write_text(
        """---
phase: 3
name: phase3-exec
validator_model: sonnet
labels: [bugfix-combo, default-combo]
learnings_file: learned_phase3.jsonl
---
# phase3
""",
        encoding="utf-8",
    )

    (repo / "data" / "default" / "seeds" / "phase1.jsonl").write_text(
        json.dumps({"keyword": "hello", "label": "greeting", "count": 30, "examples": [], "phase": "phase1"})
        + "\n",
        encoding="utf-8",
    )
    (repo / "data" / "default" / "seeds" / "phase2.jsonl").write_text(
        json.dumps({"keyword": "bug", "label": "bugfix", "count": 30, "examples": [], "phase": "phase2"})
        + "\n",
        encoding="utf-8",
    )
    (repo / "data" / "default" / "seeds" / "phase3.jsonl").write_text(
        json.dumps({"keyword": "bug", "label": "bugfix-combo", "count": 30, "examples": [], "phase": "phase3"})
        + "\n",
        encoding="utf-8",
    )

    (repo / "data" / "default" / "smalltalk" / "responses.jsonl").write_text(
        json.dumps({"id": "r1", "label": "greeting", "response": "Hello.", "warmth": 2, "level": 1}) + "\n",
        encoding="utf-8",
    )
    (repo / "data" / "default" / "smalltalk" / "compliments.jsonl").write_text("", encoding="utf-8")
    (repo / "data" / "default" / "smalltalk" / "reminders.jsonl").write_text("", encoding="utf-8")
    (repo / "data" / "default" / "smalltalk" / "config.jsonl").write_text(
        json.dumps({"key": "cpu_first", "value": True}) + "\n",
        encoding="utf-8",
    )
    (repo / "data" / "default" / "smalltalk" / "jokes.json").write_text("[]\n", encoding="utf-8")
    (repo / "data" / "default" / "smalltalk" / "facts.json").write_text("[]\n", encoding="utf-8")

    monkeypatch.setenv("STILLWATER_OAUTH3_ENFORCE_MUTATIONS", "1")
    original_urlopen = urllib.request.urlopen

    def relay(req, timeout=3.0):  # type: ignore[no-untyped-def]
        if isinstance(req, urllib.request.Request) and req.full_url.endswith("/api/oauth3/validate"):
            payload = json.loads((req.data or b"{}").decode("utf-8"))
            res = oauth_client.post("/api/oauth3/validate", json=payload)
            if res.status_code >= 400:
                raise urllib.error.HTTPError(
                    req.full_url,
                    res.status_code,
                    "oauth3 validate failed",
                    hdrs=None,
                    fp=io.BytesIO(res.content),
                )
            return _HTTPResponse(res.status_code, res.content)
        return original_urlopen(req, timeout=timeout)

    monkeypatch.setattr(urllib.request, "urlopen", relay)

    service = OrchestrationService(repo)
    app = service.create_app()
    with TestClient(app) as client:
        yield client



def _grant(
    client: TestClient,
    *,
    scopes: list[str] | None = None,
    ttl_seconds: int | None = None,
    expires_at: str | None = None,
) -> dict:
    body: dict[str, object] = {
        "principal_id": "user-1",
        "agent_id": "agent-1",
        "scopes": scopes or ["store.write"],
    }
    if ttl_seconds is not None:
        body["ttl_seconds"] = ttl_seconds
    if expires_at is not None:
        body["expires_at"] = expires_at
    res = client.post("/api/oauth3/grant", json=body)
    assert res.status_code == 201
    return res.json()


def _audit_lines(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# 1) Token grant flow

def test_grant_flow_returns_scoped_token(oauth_client: TestClient) -> None:
    data = _grant(oauth_client, scopes=["store.write", "browser.read"])
    assert data["ok"] is True
    assert data["token_id"]
    assert data["token_hash"]
    assert sorted(data["scopes"]) == ["browser.read", "store.write"]


def test_grant_rejects_non_positive_ttl(oauth_client: TestClient) -> None:
    res = oauth_client.post(
        "/api/oauth3/grant",
        json={"principal_id": "u", "agent_id": "a", "scopes": ["store.write"], "ttl_seconds": 0},
    )
    assert res.status_code == 400


# 2) Token validation flow

def test_validate_success_for_matching_scope(oauth_client: TestClient) -> None:
    granted = _grant(oauth_client, scopes=["store.write"])
    res = oauth_client.post(
        "/api/oauth3/validate",
        json={"token_id": granted["token_id"], "required_scope": "store.write", "action_risk": "low"},
    )
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_validate_without_token_fails_401(oauth_client: TestClient) -> None:
    res = oauth_client.post(
        "/api/oauth3/validate",
        json={"token_id": "00000000-0000-0000-0000-000000000000", "required_scope": "store.write", "action_risk": "low"},
    )
    assert res.status_code == 401


def test_validate_wrong_scope_fails_403(oauth_client: TestClient) -> None:
    granted = _grant(oauth_client, scopes=["browser.read"])
    res = oauth_client.post(
        "/api/oauth3/validate",
        json={"token_id": granted["token_id"], "required_scope": "store.write", "action_risk": "low"},
    )
    assert res.status_code == 403


# 3) Revocation flow

def test_revoke_then_validate_fails_401(oauth_client: TestClient) -> None:
    granted = _grant(oauth_client, scopes=["store.write"])
    revoke = oauth_client.post("/api/oauth3/revoke", json={"token_id": granted["token_id"]})
    assert revoke.status_code == 200

    res = oauth_client.post(
        "/api/oauth3/validate",
        json={"token_id": granted["token_id"], "required_scope": "store.write", "action_risk": "low"},
    )
    assert res.status_code == 401


def test_revoke_unknown_token_404(oauth_client: TestClient) -> None:
    res = oauth_client.post("/api/oauth3/revoke", json={"token_id": "00000000-0000-0000-0000-000000000000"})
    assert res.status_code == 404


# 4) Step-up flow

def test_high_risk_validate_requires_step_up(oauth_client: TestClient) -> None:
    granted = _grant(oauth_client, scopes=["store.write"])
    res = oauth_client.post(
        "/api/oauth3/validate",
        json={"token_id": granted["token_id"], "required_scope": "store.write", "action_risk": "high"},
    )
    assert res.status_code == 401


def test_step_up_then_high_risk_validate_passes(oauth_client: TestClient) -> None:
    granted = _grant(oauth_client, scopes=["store.write"])
    step = oauth_client.post(
        "/api/oauth3/step-up",
        json={"token_id": granted["token_id"], "scopes": ["store.write"], "approver": "admin"},
    )
    assert step.status_code == 200

    res = oauth_client.post(
        "/api/oauth3/validate",
        json={"token_id": granted["token_id"], "required_scope": "store.write", "action_risk": "high"},
    )
    assert res.status_code == 200


def test_step_up_rejects_scope_not_in_token(oauth_client: TestClient) -> None:
    granted = _grant(oauth_client, scopes=["browser.read"])
    res = oauth_client.post(
        "/api/oauth3/step-up",
        json={"token_id": granted["token_id"], "scopes": ["store.write"], "approver": "admin"},
    )
    assert res.status_code == 403


def test_step_up_rejects_revoked_token(oauth_client: TestClient) -> None:
    granted = _grant(oauth_client, scopes=["store.write"])
    oauth_client.post("/api/oauth3/revoke", json={"token_id": granted["token_id"]})
    res = oauth_client.post(
        "/api/oauth3/step-up",
        json={"token_id": granted["token_id"], "scopes": ["store.write"], "approver": "admin"},
    )
    assert res.status_code == 401


# 5) Expiry flow

def test_ttl_expiry_enforced(oauth_client: TestClient) -> None:
    granted = _grant(oauth_client, scopes=["store.write"], ttl_seconds=1)
    time.sleep(1.2)
    res = oauth_client.post(
        "/api/oauth3/validate",
        json={"token_id": granted["token_id"], "required_scope": "store.write", "action_risk": "low"},
    )
    assert res.status_code == 401


def test_explicit_expired_timestamp_is_rejected(oauth_client: TestClient) -> None:
    past = (datetime.now(timezone.utc) - timedelta(seconds=3)).isoformat()
    granted = _grant(oauth_client, scopes=["store.write"], expires_at=past)
    res = oauth_client.post(
        "/api/oauth3/validate",
        json={"token_id": granted["token_id"], "required_scope": "store.write", "action_risk": "low"},
    )
    assert res.status_code == 401


# 6) Orchestration integration (protected mutations)

def test_orchestration_mutation_without_token_401(orchestration_client: TestClient) -> None:
    res = orchestration_client.post("/api/orchestrate/process", json={"text": "hello"})
    assert res.status_code == 401


def test_orchestration_mutation_with_wrong_scope_403(
    orchestration_client: TestClient,
    oauth_client: TestClient,
) -> None:
    granted = _grant(oauth_client, scopes=["browser.read"])
    res = orchestration_client.post(
        "/api/orchestrate/process",
        json={"text": "hello"},
        headers={"Authorization": f"Bearer {granted['token_id']}"},
    )
    assert res.status_code == 403


def test_orchestration_mutation_with_valid_scope_200(
    orchestration_client: TestClient,
    oauth_client: TestClient,
) -> None:
    granted = _grant(oauth_client, scopes=["store.write"])
    res = orchestration_client.post(
        "/api/orchestrate/process",
        json={"text": "hello"},
        headers={"Authorization": f"Bearer {granted['token_id']}"},
    )
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_orchestration_rejects_revoked_token(
    orchestration_client: TestClient,
    oauth_client: TestClient,
) -> None:
    granted = _grant(oauth_client, scopes=["store.write"])
    oauth_client.post("/api/oauth3/revoke", json={"token_id": granted["token_id"]})
    res = orchestration_client.post(
        "/api/orchestrate/process",
        json={"text": "hello"},
        headers={"Authorization": f"Bearer {granted['token_id']}"},
    )
    assert res.status_code == 401


# 7) Audit logging (hash only)

def test_audit_log_created_on_grant(oauth_client: TestClient) -> None:
    granted = _grant(oauth_client, scopes=["store.write"])
    lines = _audit_lines(oauth3_module.AUDIT_PATH)
    assert lines
    assert any(row.get("event") == "grant" for row in lines)
    assert all("token_hash" in row for row in lines)
    assert all(row.get("token_hash") != granted["token_id"] for row in lines)


def test_audit_log_contains_no_raw_token_id(oauth_client: TestClient) -> None:
    granted = _grant(oauth_client, scopes=["store.write"])
    oauth_client.post(
        "/api/oauth3/validate",
        json={"token_id": granted["token_id"], "required_scope": "store.write", "action_risk": "low"},
    )
    raw = oauth3_module.AUDIT_PATH.read_text(encoding="utf-8")
    assert granted["token_id"] not in raw


def test_audit_records_denied_scope(oauth_client: TestClient) -> None:
    granted = _grant(oauth_client, scopes=["browser.read"])
    oauth_client.post(
        "/api/oauth3/validate",
        json={"token_id": granted["token_id"], "required_scope": "store.write", "action_risk": "low"},
    )
    lines = _audit_lines(oauth3_module.AUDIT_PATH)
    denied = [row for row in lines if row.get("event") == "validate_denied"]
    assert denied


# 8) Legacy endpoint compatibility sanity checks

def test_legacy_enforce_endpoint_still_works(oauth_client: TestClient) -> None:
    granted = _grant(oauth_client, scopes=["store.write"])
    res = oauth_client.post(
        "/oauth3/enforce",
        json={"token_id": granted["token_id"], "required_scopes": ["store.write"], "action_risk": "low"},
    )
    assert res.status_code == 200
    assert res.json()["allowed"] is True


def test_consent_endpoint_records_and_reads_history(oauth_client: TestClient) -> None:
    granted = _grant(oauth_client, scopes=["store.write"])
    create = oauth_client.post(
        "/oauth3/consent",
        json={
            "token_id": granted["token_id"],
            "principal_id": "user-1",
            "agent_id": "agent-1",
            "action": "process",
            "scopes_requested": ["store.write"],
            "decision": "granted",
        },
    )
    assert create.status_code == 201

    history = oauth_client.get(f"/oauth3/consent/{granted['token_id']}")
    assert history.status_code == 200
    assert history.json()["count"] == 1


def test_grant_uses_default_ttl_when_not_provided(oauth_client: TestClient) -> None:
    before = datetime.now(timezone.utc)
    granted = _grant(oauth_client, scopes=["store.write"])
    expires = datetime.fromisoformat(granted["expires_at"])
    assert expires.tzinfo is not None
    assert expires > before + timedelta(minutes=30)
