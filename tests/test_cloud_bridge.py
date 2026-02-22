"""Tests for Cloud Bridge Service (admin/services/cloud_bridge.py).

Covers:
- Health (3 tests)
- Service Info (3 tests)
- Connect/Disconnect (6 tests)
- Status (4 tests)
- Route (8 tests) — uses unittest.mock to avoid real HTTP calls
- Capabilities (4 tests)
- Heartbeat (4 tests)
- Integration (3 tests)
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

import admin.services.cloud_bridge as bridge_module
from admin.services.cloud_bridge import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    """Reset all in-memory state before and after each test."""
    bridge_module._connection = None
    bridge_module._capabilities.clear()
    bridge_module._route_log.clear()
    yield
    bridge_module._connection = None
    bridge_module._capabilities.clear()
    bridge_module._route_log.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _connect(api_key="key-abc", instance_id="inst-1", tier="pro"):
    """Helper: connect to cloud and return response JSON."""
    resp = client.post("/api/bridge/connect", json={
        "api_key": api_key,
        "instance_id": instance_id,
        "tier": tier,
    })
    assert resp.status_code == 200, resp.text
    return resp.json()

def _register_cap(service_type="llm", service_id="llm-portal", port=8788, endpoints=None):
    """Helper: register a capability and return response JSON."""
    resp = client.post("/api/bridge/capabilities/register", json={
        "service_id": service_id,
        "service_type": service_type,
        "port": port,
        "endpoints": endpoints or ["/api/health", "/api/chat"],
    })
    assert resp.status_code == 200, resp.text
    return resp.json()

def _mock_forward(status_code=200, body=None):
    """Return a patch context that makes _forward_http return (status_code, body)."""
    if body is None:
        body = {"status": "ok"}
    return patch.object(bridge_module, "_forward_http", return_value=(status_code, body))


# ===========================================================================
# Health
# ===========================================================================

def test_health_returns_ok():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_health_has_service_id():
    resp = client.get("/api/health")
    assert resp.json()["service_id"] == "cloud-bridge"

def test_health_connected_false_before_connect():
    resp = client.get("/api/health")
    data = resp.json()
    assert data["connected"] is False
    assert data["connected_services"] == 0


# ===========================================================================
# Service Info
# ===========================================================================

def test_service_info_returns_200():
    resp = client.get("/api/service-info")
    assert resp.status_code == 200

def test_service_info_has_correct_port():
    resp = client.get("/api/service-info")
    assert resp.json()["port"] == 8794

def test_service_info_has_service_type_bridge():
    resp = client.get("/api/service-info")
    assert resp.json()["service_type"] == "bridge"


# ===========================================================================
# Connect / Disconnect
# ===========================================================================

def test_connect_success():
    resp = client.post("/api/bridge/connect", json={
        "api_key": "key-xyz",
        "instance_id": "inst-42",
        "tier": "pro",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True

def test_connect_already_connected_returns_409():
    _connect()
    resp = client.post("/api/bridge/connect", json={
        "api_key": "key-xyz",
        "instance_id": "inst-99",
        "tier": "pro",
    })
    assert resp.status_code == 409

def test_disconnect_success():
    _connect()
    resp = client.post("/api/bridge/disconnect")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

def test_disconnect_when_not_connected_returns_400():
    resp = client.post("/api/bridge/disconnect")
    assert resp.status_code == 400

def test_connect_stores_instance_id():
    _connect(instance_id="inst-stored")
    status = client.get("/api/bridge/status").json()
    assert status["instance_id"] == "inst-stored"

def test_connect_tier_preserved():
    _connect(tier="enterprise")
    status = client.get("/api/bridge/status").json()
    assert status["tier"] == "enterprise"


# ===========================================================================
# Status
# ===========================================================================

def test_status_disconnected_when_not_connected():
    resp = client.get("/api/bridge/status")
    assert resp.status_code == 200
    assert resp.json()["connected"] is False

def test_status_connected_after_connect():
    _connect()
    resp = client.get("/api/bridge/status")
    assert resp.json()["connected"] is True

def test_status_uptime_is_non_negative():
    _connect()
    resp = client.get("/api/bridge/status")
    assert resp.json()["uptime_seconds"] >= 0.0

def test_status_last_heartbeat_updates_after_heartbeat():
    _connect()
    # Record last_heartbeat before heartbeat
    before = client.get("/api/bridge/status").json()["last_heartbeat"]
    # Issue a heartbeat
    client.post("/api/bridge/heartbeat")
    after = client.get("/api/bridge/status").json()["last_heartbeat"]
    # Timestamps are ISO strings; after >= before lexicographically
    assert after >= before


# ===========================================================================
# Route
# ===========================================================================

def test_route_to_known_service_returns_response():
    _connect(tier="pro")
    _register_cap(service_type="llm", port=8788)
    with _mock_forward(200, {"result": "pong"}):
        resp = client.post("/api/bridge/route", json={
            "service_type": "llm",
            "endpoint": "/api/health",
            "method": "GET",
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status_code"] == 200
    assert data["body"] == {"result": "pong"}

def test_route_to_unknown_service_returns_404():
    _connect(tier="pro")
    # No capability registered for "unknown"
    resp = client.post("/api/bridge/route", json={
        "service_type": "unknown",
        "endpoint": "/api/health",
        "method": "GET",
    })
    assert resp.status_code == 404

def test_route_when_not_connected_returns_403():
    resp = client.post("/api/bridge/route", json={
        "service_type": "llm",
        "endpoint": "/api/health",
        "method": "GET",
    })
    assert resp.status_code == 403

def test_route_free_tier_restricted_to_llm():
    _connect(tier="free")
    _register_cap(service_type="recipe", service_id="recipe-engine", port=8789)
    resp = client.post("/api/bridge/route", json={
        "service_type": "recipe",
        "endpoint": "/api/health",
        "method": "GET",
    })
    assert resp.status_code == 403

def test_route_pro_tier_can_reach_all_services():
    _connect(tier="pro")
    _register_cap(service_type="recipe", service_id="recipe-engine", port=8789)
    with _mock_forward(200, {"status": "ok"}):
        resp = client.post("/api/bridge/route", json={
            "service_type": "recipe",
            "endpoint": "/api/health",
            "method": "GET",
        })
    assert resp.status_code == 200

def test_route_log_grows_with_each_request():
    _connect(tier="pro")
    _register_cap(service_type="llm", port=8788)
    assert len(bridge_module._route_log) == 0
    with _mock_forward(200, {}):
        client.post("/api/bridge/route", json={
            "service_type": "llm",
            "endpoint": "/api/health",
            "method": "GET",
        })
    assert len(bridge_module._route_log) == 1
    with _mock_forward(200, {}):
        client.post("/api/bridge/route", json={
            "service_type": "llm",
            "endpoint": "/api/chat",
            "method": "POST",
            "payload": {"prompt": "hi"},
        })
    assert len(bridge_module._route_log) == 2

def test_route_response_includes_latency_ms():
    _connect(tier="pro")
    _register_cap(service_type="llm", port=8788)
    with _mock_forward(200, {"ok": True}):
        resp = client.post("/api/bridge/route", json={
            "service_type": "llm",
            "endpoint": "/api/health",
            "method": "GET",
        })
    data = resp.json()
    assert "latency_ms" in data
    assert data["latency_ms"] >= 0.0

def test_route_method_preserved_in_log():
    _connect(tier="pro")
    _register_cap(service_type="llm", port=8788)
    with _mock_forward(200, {}):
        client.post("/api/bridge/route", json={
            "service_type": "llm",
            "endpoint": "/api/chat",
            "method": "POST",
            "payload": {"messages": []},
        })
    log_entry = bridge_module._route_log[-1]
    assert log_entry["method"] == "POST"


# ===========================================================================
# Capabilities
# ===========================================================================

def test_capabilities_empty_initially():
    resp = client.get("/api/bridge/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 0
    assert data["capabilities"] == []

def test_register_capability_succeeds():
    resp = client.post("/api/bridge/capabilities/register", json={
        "service_id": "llm-portal",
        "service_type": "llm",
        "port": 8788,
        "endpoints": ["/api/health", "/api/chat"],
    })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

def test_capabilities_list_matches_registered():
    _register_cap(service_type="llm", port=8788)
    _register_cap(service_type="recipe", service_id="recipe-engine", port=8789)
    resp = client.get("/api/bridge/capabilities")
    assert resp.json()["count"] == 2

def test_capabilities_include_endpoint_list():
    _register_cap(service_type="llm", port=8788, endpoints=["/api/health", "/api/chat", "/api/models"])
    resp = client.get("/api/bridge/capabilities")
    caps = resp.json()["capabilities"]
    assert len(caps) == 1
    assert "/api/health" in caps[0]["endpoints"]
    assert "/api/chat" in caps[0]["endpoints"]
    assert "/api/models" in caps[0]["endpoints"]


# ===========================================================================
# Heartbeat
# ===========================================================================

def test_heartbeat_when_connected_returns_ok():
    _connect()
    resp = client.post("/api/bridge/heartbeat")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

def test_heartbeat_when_not_connected_returns_400():
    resp = client.post("/api/bridge/heartbeat")
    assert resp.status_code == 400

def test_heartbeat_updates_last_heartbeat_timestamp():
    _connect()
    hb1 = client.post("/api/bridge/heartbeat").json()["last_heartbeat"]
    hb2 = client.post("/api/bridge/heartbeat").json()["last_heartbeat"]
    # Both are valid ISO timestamps; second must be >= first
    assert hb2 >= hb1

def test_heartbeat_returns_health_summary():
    _connect()
    _register_cap(service_type="llm", port=8788)
    resp = client.post("/api/bridge/heartbeat")
    data = resp.json()
    assert data["health"] == "ok"
    assert data["services_available"] == 1
    assert "uptime_seconds" in data
    assert data["instance_id"] is not None


# ===========================================================================
# Integration
# ===========================================================================

def test_integration_connect_register_route():
    """Connect → register capability → route request — full happy path."""
    _connect(tier="pro")
    _register_cap(service_type="evidence", service_id="evidence-pipeline", port=8790)

    with _mock_forward(200, {"chain_length": 5}):
        resp = client.post("/api/bridge/route", json={
            "service_type": "evidence",
            "endpoint": "/api/evidence/chain",
            "method": "GET",
        })

    assert resp.status_code == 200
    data = resp.json()
    assert data["status_code"] == 200
    assert data["body"]["chain_length"] == 5
    assert data["service_id"] == "evidence-pipeline"

def test_integration_full_lifecycle():
    """Connect → heartbeat → route → disconnect — verify state clears."""
    _connect(tier="enterprise")
    _register_cap(service_type="llm", port=8788)

    # Heartbeat should succeed
    hb = client.post("/api/bridge/heartbeat")
    assert hb.status_code == 200

    # Route should succeed
    with _mock_forward(200, {"tokens": 42}):
        route_resp = client.post("/api/bridge/route", json={
            "service_type": "llm",
            "endpoint": "/api/chat",
            "method": "POST",
            "payload": {"messages": [{"role": "user", "content": "hi"}]},
        })
    assert route_resp.status_code == 200

    # Disconnect
    disc = client.post("/api/bridge/disconnect")
    assert disc.status_code == 200
    assert disc.json()["ok"] is True

    # Status should show disconnected
    status = client.get("/api/bridge/status")
    assert status.json()["connected"] is False

def test_integration_disconnect_clears_connection_state():
    """After disconnect, heartbeat and route should both fail."""
    _connect(tier="pro")
    _register_cap(service_type="llm", port=8788)

    client.post("/api/bridge/disconnect")

    # Heartbeat must fail
    hb = client.post("/api/bridge/heartbeat")
    assert hb.status_code == 400

    # Route must fail
    route_resp = client.post("/api/bridge/route", json={
        "service_type": "llm",
        "endpoint": "/api/health",
        "method": "GET",
    })
    assert route_resp.status_code == 403
