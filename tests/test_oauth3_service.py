"""Tests for OAuth3 Authority Service (admin/services/oauth3_service.py).

Covers:
- Health endpoint
- Issue token (valid fields, UUID generation)
- Get token by ID
- Get non-existent token (404)
- Revoke token
- Revoke already-revoked token (idempotent)
- List scopes
- ScopeGate G1: token exists → pass / token missing → fail / revoked → fail
- ScopeGate G2: not expired → pass / expired → fail
- ScopeGate G3: scope sufficient → pass / insufficient → fail
- ScopeGate G4: high-risk → step_up_required / low-risk → no step_up
- Consent: record consent, get history
- Service info endpoint
"""

import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

import admin.services.oauth3_service as oauth3_module
from admin.services.oauth3_service import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_stores():
    """Clear in-memory stores between tests."""
    oauth3_module._tokens.clear()
    oauth3_module._consent_log.clear()
    yield
    oauth3_module._tokens.clear()
    oauth3_module._consent_log.clear()


def _future_ts(hours: int = 24) -> str:
    """Return an ISO 8601 timestamp N hours in the future."""
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()

def _past_ts(hours: int = 1) -> str:
    """Return an ISO 8601 timestamp N hours in the past."""
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

def _issue_token(
    scopes: list[str] | None = None,
    expires_at: str | None = None,
    principal_id: str = "user-1",
    agent_id: str = "agent-1",
) -> dict:
    """Helper: issue a token and return response JSON."""
    resp = client.post("/oauth3/tokens", json={
        "principal_id": principal_id,
        "agent_id": agent_id,
        "scopes": scopes or ["browser.navigate"],
        "expires_at": expires_at or _future_ts(),
    })
    assert resp.status_code == 201
    return resp.json()


# ===== Health =====

def test_health_returns_ok():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_health_has_service_id():
    resp = client.get("/api/health")
    assert resp.json()["service_id"] == "oauth3-service"

def test_health_has_token_count():
    resp = client.get("/api/health")
    assert "token_count" in resp.json()

def test_health_token_count_increments():
    _issue_token()
    resp = client.get("/api/health")
    assert resp.json()["token_count"] == 1


# ===== Service Info =====

def test_service_info_returns_correct_port():
    resp = client.get("/api/service-info")
    assert resp.status_code == 200
    assert resp.json()["port"] == 8791

def test_service_info_has_oauth3_type():
    resp = client.get("/api/service-info")
    assert resp.json()["service_type"] == "oauth3"

def test_service_info_has_name():
    resp = client.get("/api/service-info")
    assert "OAuth3" in resp.json()["name"]


# ===== Issue Token =====

def test_issue_token_returns_201():
    resp = client.post("/oauth3/tokens", json={
        "principal_id": "user-1",
        "agent_id": "agent-1",
        "scopes": ["browser.navigate"],
        "expires_at": _future_ts(),
    })
    assert resp.status_code == 201

def test_issue_token_has_all_required_fields():
    token = _issue_token()
    for field in ["token_id", "principal_id", "agent_id", "scopes", "issued_at", "expires_at"]:
        assert field in token, f"Missing field: {field}"

def test_issue_token_generates_uuid():
    t1 = _issue_token()
    t2 = _issue_token()
    assert t1["token_id"] != t2["token_id"]
    # UUIDs are 36 chars (8-4-4-4-12 with dashes)
    assert len(t1["token_id"]) == 36

def test_issue_token_is_not_revoked_by_default():
    token = _issue_token()
    assert token["revoked"] is False

def test_issue_token_principal_and_agent_preserved():
    token = _issue_token(principal_id="alice", agent_id="bot-1")
    assert token["principal_id"] == "alice"
    assert token["agent_id"] == "bot-1"

def test_issue_token_scopes_preserved():
    scopes = ["browser.navigate", "browser.act"]
    token = _issue_token(scopes=scopes)
    assert token["scopes"] == scopes


# ===== Get Token =====

def test_get_token_by_id():
    token = _issue_token()
    resp = client.get(f"/oauth3/tokens/{token['token_id']}")
    assert resp.status_code == 200
    assert resp.json()["token_id"] == token["token_id"]

def test_get_nonexistent_token_returns_404():
    resp = client.get("/oauth3/tokens/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


# ===== Revoke Token =====

def test_revoke_token_returns_ok():
    token = _issue_token()
    resp = client.delete(f"/oauth3/tokens/{token['token_id']}")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

def test_revoke_token_sets_revoked_flag():
    token = _issue_token()
    client.delete(f"/oauth3/tokens/{token['token_id']}")
    fetched = client.get(f"/oauth3/tokens/{token['token_id']}").json()
    assert fetched["revoked"] is True

def test_revoke_token_sets_revoked_at():
    token = _issue_token()
    client.delete(f"/oauth3/tokens/{token['token_id']}")
    fetched = client.get(f"/oauth3/tokens/{token['token_id']}").json()
    assert fetched["revoked_at"] is not None

def test_revoke_already_revoked_token_is_idempotent():
    token = _issue_token()
    r1 = client.delete(f"/oauth3/tokens/{token['token_id']}")
    r2 = client.delete(f"/oauth3/tokens/{token['token_id']}")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["revoked_at"] == r2.json()["revoked_at"]

def test_revoke_nonexistent_token_returns_404():
    resp = client.delete("/oauth3/tokens/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


# ===== List Scopes =====

def test_list_scopes_returns_ok():
    resp = client.get("/oauth3/scopes")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

def test_list_scopes_has_browser_navigate():
    resp = client.get("/oauth3/scopes")
    scope_ids = [s["id"] for s in resp.json()["scopes"]]
    assert "browser.navigate" in scope_ids

def test_list_scopes_count_matches():
    resp = client.get("/oauth3/scopes")
    data = resp.json()
    assert data["count"] == len(data["scopes"])


# ===== ScopeGate G1: Token Exists =====

def test_scopegate_g1_passes_for_valid_token():
    token = _issue_token(scopes=["browser.navigate"])
    resp = client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": ["browser.navigate"],
        "action_risk": "low",
    })
    assert resp.json()["gate_results"]["g1"] is True

def test_scopegate_g1_fails_for_missing_token():
    resp = client.post("/oauth3/enforce", json={
        "token_id": "00000000-0000-0000-0000-000000000000",
        "required_scopes": ["browser.navigate"],
        "action_risk": "low",
    })
    data = resp.json()
    assert data["allowed"] is False
    assert data["gate_results"]["g1"] is False
    assert "G1" in data["reason"]

def test_scopegate_g1_fails_for_revoked_token():
    token = _issue_token(scopes=["browser.navigate"])
    client.delete(f"/oauth3/tokens/{token['token_id']}")
    resp = client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": ["browser.navigate"],
        "action_risk": "low",
    })
    data = resp.json()
    assert data["allowed"] is False
    assert "revoked" in data["reason"]


# ===== ScopeGate G2: Not Expired =====

def test_scopegate_g2_passes_for_valid_token():
    token = _issue_token(expires_at=_future_ts(hours=24))
    resp = client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": [],
        "action_risk": "low",
    })
    assert resp.json()["gate_results"]["g2"] is True

def test_scopegate_g2_fails_for_expired_token():
    token = _issue_token(expires_at=_past_ts(hours=1))
    resp = client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": [],
        "action_risk": "low",
    })
    data = resp.json()
    assert data["allowed"] is False
    assert data["gate_results"]["g2"] is False
    assert "expired" in data["reason"]


# ===== ScopeGate G3: Scope Sufficient =====

def test_scopegate_g3_passes_when_scope_present():
    token = _issue_token(scopes=["browser.navigate", "browser.act"])
    resp = client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": ["browser.navigate"],
        "action_risk": "low",
    })
    assert resp.json()["gate_results"]["g3"] is True
    assert resp.json()["allowed"] is True

def test_scopegate_g3_fails_when_scope_missing():
    token = _issue_token(scopes=["browser.navigate"])
    resp = client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": ["browser.act"],
        "action_risk": "low",
    })
    data = resp.json()
    assert data["allowed"] is False
    assert data["gate_results"]["g3"] is False
    assert "G3" in data["reason"]

def test_scopegate_g3_fails_when_one_scope_of_two_missing():
    token = _issue_token(scopes=["browser.navigate"])
    resp = client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": ["browser.navigate", "browser.act"],
        "action_risk": "low",
    })
    assert resp.json()["allowed"] is False


# ===== ScopeGate G4: Step-Up for Destructive Actions =====

def test_scopegate_g4_no_step_up_for_low_risk():
    token = _issue_token(scopes=["browser.navigate"])
    resp = client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": ["browser.navigate"],
        "action_risk": "low",
    })
    data = resp.json()
    assert data["step_up_required"] is False
    assert data["allowed"] is True

def test_scopegate_g4_no_step_up_for_medium_risk():
    token = _issue_token(scopes=["browser.act"])
    resp = client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": ["browser.act"],
        "action_risk": "medium",
    })
    data = resp.json()
    assert data["step_up_required"] is False

def test_scopegate_g4_step_up_required_for_high_risk():
    token = _issue_token(scopes=["store.publish"])
    resp = client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": ["store.publish"],
        "action_risk": "high",
    })
    data = resp.json()
    assert data["step_up_required"] is True
    assert data["allowed"] is False
    assert data["gate_results"]["g4"] is True  # G4 evaluates; result is step_up flag

def test_scopegate_g4_all_lower_gates_pass_for_high_risk():
    token = _issue_token(scopes=["vault.write"])
    resp = client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": ["vault.write"],
        "action_risk": "high",
    })
    data = resp.json()
    assert data["gate_results"]["g1"] is True
    assert data["gate_results"]["g2"] is True
    assert data["gate_results"]["g3"] is True


# ===== Consent =====

def test_record_consent_returns_201():
    token = _issue_token()
    resp = client.post("/oauth3/consent", json={
        "token_id": token["token_id"],
        "principal_id": "user-1",
        "agent_id": "agent-1",
        "action": "navigate",
        "scopes_requested": ["browser.navigate"],
        "decision": "granted",
    })
    assert resp.status_code == 201

def test_record_consent_has_consent_id():
    token = _issue_token()
    resp = client.post("/oauth3/consent", json={
        "token_id": token["token_id"],
        "principal_id": "user-1",
        "agent_id": "agent-1",
        "action": "navigate",
        "scopes_requested": ["browser.navigate"],
        "decision": "granted",
    })
    assert "consent_id" in resp.json()

def test_record_consent_has_recorded_at():
    token = _issue_token()
    resp = client.post("/oauth3/consent", json={
        "token_id": token["token_id"],
        "principal_id": "user-1",
        "agent_id": "agent-1",
        "action": "navigate",
        "scopes_requested": ["browser.navigate"],
        "decision": "granted",
    })
    assert "recorded_at" in resp.json()

def test_get_consent_history_for_token():
    token = _issue_token()
    tid = token["token_id"]

    client.post("/oauth3/consent", json={
        "token_id": tid,
        "principal_id": "user-1",
        "agent_id": "agent-1",
        "action": "navigate",
        "scopes_requested": ["browser.navigate"],
        "decision": "granted",
    })
    client.post("/oauth3/consent", json={
        "token_id": tid,
        "principal_id": "user-1",
        "agent_id": "agent-1",
        "action": "act",
        "scopes_requested": ["browser.act"],
        "decision": "denied",
    })

    resp = client.get(f"/oauth3/consent/{tid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_id"] == tid
    assert data["count"] == 2
    assert len(data["history"]) == 2

def test_get_consent_history_empty_for_unknown_token():
    resp = client.get("/oauth3/consent/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 200
    assert resp.json()["count"] == 0

def test_consent_history_only_returns_records_for_that_token():
    t1 = _issue_token(principal_id="alice")
    t2 = _issue_token(principal_id="bob")

    client.post("/oauth3/consent", json={
        "token_id": t1["token_id"],
        "principal_id": "alice",
        "agent_id": "agent-1",
        "action": "navigate",
        "scopes_requested": ["browser.navigate"],
        "decision": "granted",
    })
    client.post("/oauth3/consent", json={
        "token_id": t2["token_id"],
        "principal_id": "bob",
        "agent_id": "agent-2",
        "action": "act",
        "scopes_requested": ["browser.act"],
        "decision": "granted",
    })

    history_t1 = client.get(f"/oauth3/consent/{t1['token_id']}").json()["history"]
    assert all(r["token_id"] == t1["token_id"] for r in history_t1)
    assert len(history_t1) == 1
