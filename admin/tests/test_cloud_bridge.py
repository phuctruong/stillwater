from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_DIR = REPO_ROOT / "admin"
for _path in (str(REPO_ROOT), str(ADMIN_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from services import cloud_bridge


def _reset_state() -> None:
    cloud_bridge._connection = None
    cloud_bridge._capabilities.clear()
    cloud_bridge._route_log.clear()


def test_cloud_status_not_configured_when_disabled(monkeypatch) -> None:
    monkeypatch.setattr(cloud_bridge, "_load_cloud_config", lambda: {"enabled": False, "api_key": "", "api_url": "https://www.solaceagi.com/api/v1"})
    out = cloud_bridge._cloud_status()
    assert out["status"] == "not_configured"


def test_cloud_status_not_configured_when_missing_key(monkeypatch) -> None:
    monkeypatch.setattr(cloud_bridge, "_load_cloud_config", lambda: {"enabled": True, "api_key": "", "api_url": "https://www.solaceagi.com/api/v1"})
    out = cloud_bridge._cloud_status()
    assert out["status"] == "not_configured"


def test_cloud_status_unreachable_on_error(monkeypatch) -> None:
    monkeypatch.setattr(cloud_bridge, "_load_cloud_config", lambda: {"enabled": True, "api_key": "k", "api_url": "https://www.solaceagi.com/api/v1"})
    monkeypatch.setattr(cloud_bridge, "_cloud_request", lambda *args, **kwargs: (0, {}, "connection timeout to www.solaceagi.com"))
    out = cloud_bridge._cloud_status()
    assert out["status"] == "unreachable"


def test_cloud_status_auth_failed_on_401(monkeypatch) -> None:
    monkeypatch.setattr(cloud_bridge, "_load_cloud_config", lambda: {"enabled": True, "api_key": "k", "api_url": "https://www.solaceagi.com/api/v1"})
    monkeypatch.setattr(cloud_bridge, "_cloud_request", lambda *args, **kwargs: (401, {"error": "bad"}, None))
    out = cloud_bridge._cloud_status()
    assert out["status"] == "auth_failed"


def test_cloud_status_error_on_non_2xx(monkeypatch) -> None:
    monkeypatch.setattr(cloud_bridge, "_load_cloud_config", lambda: {"enabled": True, "api_key": "k", "api_url": "https://www.solaceagi.com/api/v1"})
    monkeypatch.setattr(cloud_bridge, "_cloud_request", lambda *args, **kwargs: (500, {"error": "down"}, None))
    out = cloud_bridge._cloud_status()
    assert out["status"] == "error"


def test_cloud_status_uses_health_tier(monkeypatch) -> None:
    monkeypatch.setattr(cloud_bridge, "_load_cloud_config", lambda: {"enabled": True, "api_key": "k", "api_url": "https://www.solaceagi.com/api/v1"})
    monkeypatch.setattr(cloud_bridge, "_cloud_request", lambda *args, **kwargs: (200, {"tier": "pro"}, None))
    out = cloud_bridge._cloud_status()
    assert out["status"] == "ok"
    assert out["tier"] == "pro"


def test_cloud_status_falls_back_to_tier_endpoint(monkeypatch) -> None:
    monkeypatch.setattr(cloud_bridge, "_load_cloud_config", lambda: {"enabled": True, "api_key": "k", "api_url": "https://www.solaceagi.com/api/v1"})

    calls: list[str] = []

    def fake_request(method: str, endpoint: str, *args, **kwargs):
        calls.append(endpoint)
        if endpoint == "/health":
            return (200, {}, None)
        if endpoint == "/account/tier":
            return (200, {"tier": "enterprise"}, None)
        return (404, {}, None)

    monkeypatch.setattr(cloud_bridge, "_cloud_request", fake_request)
    out = cloud_bridge._cloud_status()
    assert out["status"] == "ok"
    assert out["tier"] == "enterprise"
    assert calls == ["/health", "/account/tier"]


def test_cloud_health_endpoint_not_configured(monkeypatch) -> None:
    _reset_state()
    monkeypatch.setattr(cloud_bridge, "_cloud_status", lambda **kwargs: {"status": "not_configured", "message": "run: PUT /api/llm/keys/solaceagi to configure"})
    with TestClient(cloud_bridge.app) as client:
        res = client.get("/api/health/cloud")
    assert res.status_code == 200
    assert res.json()["ok"] is False


def test_connect_rejects_auth_failed(monkeypatch) -> None:
    _reset_state()
    monkeypatch.setattr(cloud_bridge, "_cloud_status", lambda **kwargs: {"status": "auth_failed", "error": "invalid API key"})
    with TestClient(cloud_bridge.app) as client:
        res = client.post("/api/bridge/connect", json={"api_key": "bad", "instance_id": "i-1", "tier": "free", "metadata": {}})
    assert res.status_code == 401


def test_connect_success_sets_connection(monkeypatch) -> None:
    _reset_state()
    monkeypatch.setattr(cloud_bridge, "_cloud_status", lambda **kwargs: {"status": "ok", "tier": "pro"})
    with TestClient(cloud_bridge.app) as client:
        res = client.post("/api/bridge/connect", json={"api_key": "good", "instance_id": "i-1", "tier": "free", "metadata": {}})
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert body["tier"] == "pro"


def test_sync_skills_requires_connection() -> None:
    _reset_state()
    with TestClient(cloud_bridge.app) as client:
        res = client.post("/api/bridge/sync/skills", json={"direction": "both", "payload": {}})
    assert res.status_code == 403


def test_sync_skills_forwards_to_cloud(monkeypatch) -> None:
    _reset_state()
    cloud_bridge._connection = {
        "api_key": "k",
        "instance_id": "i-1",
        "tier": "pro",
        "connected_at": cloud_bridge._now_iso(),
        "last_heartbeat": cloud_bridge._now_iso(),
        "_start_monotonic": 0.0,
        "metadata": {},
    }
    monkeypatch.setattr(cloud_bridge, "_cloud_request", lambda *args, **kwargs: (200, {"synced": 3}, None))
    with TestClient(cloud_bridge.app) as client:
        res = client.post("/api/bridge/sync/skills", json={"direction": "up", "payload": {"project": "stillwater"}})
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert body["status"] == "ok"
    assert body["response"]["synced"] == 3
