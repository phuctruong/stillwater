"""Tests for Tunnel Service (admin/services/tunnel_service.py).

Covers:
- Health endpoint (active_tunnels, total_tunnels fields)
- Service info endpoint
- Start tunnel — creates active tunnel
- Start tunnel — generates unique tunnel_id
- Start tunnel — returns tunnel_url
- Start tunnel — duplicate service_id (409 conflict)
- Stop tunnel — changes status to disconnected
- Stop tunnel — returns uptime
- Stop tunnel — non-existent tunnel (404)
- Tunnel status — lists all tunnels with uptime
- Tunnel status — empty when none started
- Tunneled services — only shows active tunnels
- Tunneled services — excludes disconnected
- Start then stop flow — full lifecycle
- Multiple tunnels for different services
"""

import pytest
from fastapi.testclient import TestClient

import admin.services.tunnel_service as tunnel_module
from admin.services.tunnel_service import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_tunnels():
    """Clear _tunnels state before each test."""
    tunnel_module._tunnels.clear()
    yield
    tunnel_module._tunnels.clear()


# ===== Health =====

def test_health_returns_ok():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_health_has_service_id():
    resp = client.get("/api/health")
    assert resp.json()["service_id"] == "tunnel-service"

def test_health_has_service_type():
    resp = client.get("/api/health")
    assert resp.json()["service_type"] == "tunnel"

def test_health_active_tunnels_zero_on_start():
    resp = client.get("/api/health")
    data = resp.json()
    assert data["active_tunnels"] == 0
    assert data["total_tunnels"] == 0

def test_health_active_tunnels_increments_after_start():
    client.post("/api/tunnel/start", json={
        "service_id": "svc-a",
        "service_port": 8100,
    })
    resp = client.get("/api/health")
    data = resp.json()
    assert data["active_tunnels"] == 1
    assert data["total_tunnels"] == 1

def test_health_total_includes_disconnected():
    resp = client.post("/api/tunnel/start", json={
        "service_id": "svc-b",
        "service_port": 8101,
    })
    tunnel_id = resp.json()["tunnel_id"]
    client.post("/api/tunnel/stop", json={"tunnel_id": tunnel_id})

    resp = client.get("/api/health")
    data = resp.json()
    assert data["active_tunnels"] == 0
    assert data["total_tunnels"] == 1


# ===== Service Info =====

def test_service_info_returns_200():
    resp = client.get("/api/service-info")
    assert resp.status_code == 200

def test_service_info_returns_port():
    resp = client.get("/api/service-info")
    assert resp.json()["port"] == 8793

def test_service_info_has_name():
    resp = client.get("/api/service-info")
    assert "Tunnel Service" in resp.json()["name"]

def test_service_info_type_is_tunnel():
    resp = client.get("/api/service-info")
    assert resp.json()["service_type"] == "tunnel"

def test_service_info_has_version():
    resp = client.get("/api/service-info")
    assert "version" in resp.json()


# ===== Start Tunnel =====

def test_start_tunnel_creates_active_tunnel():
    resp = client.post("/api/tunnel/start", json={
        "service_id": "recipe-engine",
        "service_port": 8790,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "active"
    assert data["service_id"] == "recipe-engine"
    assert data["service_port"] == 8790

def test_start_tunnel_generates_tunnel_id():
    resp = client.post("/api/tunnel/start", json={
        "service_id": "recipe-engine",
        "service_port": 8790,
    })
    data = resp.json()
    assert "tunnel_id" in data
    assert len(data["tunnel_id"]) == 16

def test_start_tunnel_returns_tunnel_url():
    resp = client.post("/api/tunnel/start", json={
        "service_id": "recipe-engine",
        "service_port": 8790,
    })
    data = resp.json()
    assert "tunnel_url" in data
    assert data["tunnel_url"] is not None
    assert "tunnel.solaceagi.com" in data["tunnel_url"]

def test_start_tunnel_url_contains_tunnel_id():
    resp = client.post("/api/tunnel/start", json={
        "service_id": "recipe-engine",
        "service_port": 8790,
    })
    data = resp.json()
    assert data["tunnel_id"] in data["tunnel_url"]

def test_start_tunnel_default_type_is_wss():
    resp = client.post("/api/tunnel/start", json={
        "service_id": "recipe-engine",
        "service_port": 8790,
    })
    data = resp.json()
    assert data["tunnel_type"] == "wss"
    assert data["tunnel_url"].startswith("wss://")

def test_start_tunnel_custom_type_https():
    resp = client.post("/api/tunnel/start", json={
        "service_id": "recipe-engine",
        "service_port": 8790,
        "tunnel_type": "https",
    })
    data = resp.json()
    assert data["tunnel_type"] == "https"
    assert data["tunnel_url"].startswith("https://")

def test_start_tunnel_custom_target_host():
    resp = client.post("/api/tunnel/start", json={
        "service_id": "recipe-engine",
        "service_port": 8790,
        "target_host": "my-server.example.com",
    })
    data = resp.json()
    assert "my-server.example.com" in data["tunnel_url"]

def test_start_tunnel_duplicate_service_id_returns_409():
    client.post("/api/tunnel/start", json={
        "service_id": "recipe-engine",
        "service_port": 8790,
    })
    resp = client.post("/api/tunnel/start", json={
        "service_id": "recipe-engine",
        "service_port": 8790,
    })
    assert resp.status_code == 409

def test_start_tunnel_duplicate_conflict_message_contains_service_id():
    client.post("/api/tunnel/start", json={
        "service_id": "recipe-engine",
        "service_port": 8790,
    })
    resp = client.post("/api/tunnel/start", json={
        "service_id": "recipe-engine",
        "service_port": 8790,
    })
    assert "recipe-engine" in resp.json()["detail"]

def test_start_tunnel_unique_ids_for_different_services():
    resp_a = client.post("/api/tunnel/start", json={
        "service_id": "svc-a",
        "service_port": 8100,
    })
    resp_b = client.post("/api/tunnel/start", json={
        "service_id": "svc-b",
        "service_port": 8101,
    })
    assert resp_a.json()["tunnel_id"] != resp_b.json()["tunnel_id"]

def test_start_tunnel_has_created_at():
    resp = client.post("/api/tunnel/start", json={
        "service_id": "svc-ts",
        "service_port": 8200,
    })
    data = resp.json()
    assert "created_at" in data
    assert data["created_at"] is not None


# ===== Stop Tunnel =====

def test_stop_tunnel_changes_status_to_disconnected():
    start_resp = client.post("/api/tunnel/start", json={
        "service_id": "svc-stop",
        "service_port": 8300,
    })
    tunnel_id = start_resp.json()["tunnel_id"]

    stop_resp = client.post("/api/tunnel/stop", json={"tunnel_id": tunnel_id})
    assert stop_resp.status_code == 200
    data = stop_resp.json()
    assert data["ok"] is True
    assert data["status"] == "disconnected"
    assert data["tunnel_id"] == tunnel_id

def test_stop_tunnel_returns_uptime():
    start_resp = client.post("/api/tunnel/start", json={
        "service_id": "svc-uptime",
        "service_port": 8301,
    })
    tunnel_id = start_resp.json()["tunnel_id"]

    stop_resp = client.post("/api/tunnel/stop", json={"tunnel_id": tunnel_id})
    data = stop_resp.json()
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0.0

def test_stop_tunnel_nonexistent_returns_404():
    resp = client.post("/api/tunnel/stop", json={"tunnel_id": "deadbeefdeadbeef"})
    assert resp.status_code == 404

def test_stop_tunnel_404_message_contains_tunnel_id():
    resp = client.post("/api/tunnel/stop", json={"tunnel_id": "deadbeefdeadbeef"})
    assert "deadbeefdeadbeef" in resp.json()["detail"]


# ===== Tunnel Status =====

def test_tunnel_status_empty_when_none_started():
    resp = client.get("/api/tunnel/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["tunnels"] == []

def test_tunnel_status_lists_all_tunnels():
    client.post("/api/tunnel/start", json={"service_id": "svc-x", "service_port": 8400})
    client.post("/api/tunnel/start", json={"service_id": "svc-y", "service_port": 8401})

    resp = client.get("/api/tunnel/status")
    data = resp.json()
    assert len(data["tunnels"]) == 2

def test_tunnel_status_includes_uptime_for_active():
    client.post("/api/tunnel/start", json={"service_id": "svc-up", "service_port": 8402})

    resp = client.get("/api/tunnel/status")
    tunnels = resp.json()["tunnels"]
    assert len(tunnels) == 1
    assert "uptime_seconds" in tunnels[0]
    assert tunnels[0]["uptime_seconds"] >= 0.0

def test_tunnel_status_uptime_zero_for_disconnected():
    start_resp = client.post("/api/tunnel/start", json={"service_id": "svc-disc", "service_port": 8403})
    tunnel_id = start_resp.json()["tunnel_id"]
    client.post("/api/tunnel/stop", json={"tunnel_id": tunnel_id})

    resp = client.get("/api/tunnel/status")
    tunnels = resp.json()["tunnels"]
    assert len(tunnels) == 1
    assert tunnels[0]["status"] == "disconnected"
    assert tunnels[0]["uptime_seconds"] == 0.0

def test_tunnel_status_has_required_fields():
    client.post("/api/tunnel/start", json={"service_id": "svc-fields", "service_port": 8404})

    resp = client.get("/api/tunnel/status")
    tunnel = resp.json()["tunnels"][0]
    for field in ("tunnel_id", "service_id", "service_port", "tunnel_type",
                  "target_host", "status", "created_at", "tunnel_url",
                  "bytes_transferred", "uptime_seconds"):
        assert field in tunnel, f"Missing field: {field}"

def test_tunnel_status_includes_disconnected_in_list():
    start_resp = client.post("/api/tunnel/start", json={"service_id": "svc-both", "service_port": 8405})
    tunnel_id = start_resp.json()["tunnel_id"]
    client.post("/api/tunnel/stop", json={"tunnel_id": tunnel_id})

    resp = client.get("/api/tunnel/status")
    statuses = [t["status"] for t in resp.json()["tunnels"]]
    assert "disconnected" in statuses


# ===== Tunneled Services =====

def test_tunneled_services_empty_when_none():
    resp = client.get("/api/tunnel/services")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["tunneled_services"] == []

def test_tunneled_services_shows_active():
    client.post("/api/tunnel/start", json={"service_id": "svc-active", "service_port": 8500})

    resp = client.get("/api/tunnel/services")
    services = resp.json()["tunneled_services"]
    assert len(services) == 1
    assert services[0]["service_id"] == "svc-active"

def test_tunneled_services_excludes_disconnected():
    start_resp = client.post("/api/tunnel/start", json={"service_id": "svc-gone", "service_port": 8501})
    tunnel_id = start_resp.json()["tunnel_id"]
    client.post("/api/tunnel/stop", json={"tunnel_id": tunnel_id})

    resp = client.get("/api/tunnel/services")
    services = resp.json()["tunneled_services"]
    assert services == []

def test_tunneled_services_only_shows_active_when_mixed():
    client.post("/api/tunnel/start", json={"service_id": "svc-stay", "service_port": 8502})
    gone_resp = client.post("/api/tunnel/start", json={"service_id": "svc-leave", "service_port": 8503})
    gone_id = gone_resp.json()["tunnel_id"]
    client.post("/api/tunnel/stop", json={"tunnel_id": gone_id})

    resp = client.get("/api/tunnel/services")
    services = resp.json()["tunneled_services"]
    assert len(services) == 1
    assert services[0]["service_id"] == "svc-stay"

def test_tunneled_services_has_tunnel_url():
    client.post("/api/tunnel/start", json={"service_id": "svc-url", "service_port": 8504})

    resp = client.get("/api/tunnel/services")
    service = resp.json()["tunneled_services"][0]
    assert "tunnel_url" in service
    assert service["tunnel_url"] is not None

def test_tunneled_services_has_tunnel_id():
    start_resp = client.post("/api/tunnel/start", json={"service_id": "svc-tid", "service_port": 8505})
    expected_id = start_resp.json()["tunnel_id"]

    resp = client.get("/api/tunnel/services")
    service = resp.json()["tunneled_services"][0]
    assert service["tunnel_id"] == expected_id


# ===== Full Lifecycle =====

def test_full_lifecycle_start_then_stop():
    # Start
    start_resp = client.post("/api/tunnel/start", json={
        "service_id": "lifecycle-svc",
        "service_port": 8600,
    })
    assert start_resp.status_code == 200
    tunnel_id = start_resp.json()["tunnel_id"]
    assert start_resp.json()["status"] == "active"

    # Verify visible in services
    services_resp = client.get("/api/tunnel/services")
    service_ids = [s["service_id"] for s in services_resp.json()["tunneled_services"]]
    assert "lifecycle-svc" in service_ids

    # Verify visible in status
    status_resp = client.get("/api/tunnel/status")
    active = [t for t in status_resp.json()["tunnels"] if t["status"] == "active"]
    assert any(t["tunnel_id"] == tunnel_id for t in active)

    # Stop
    stop_resp = client.post("/api/tunnel/stop", json={"tunnel_id": tunnel_id})
    assert stop_resp.json()["status"] == "disconnected"

    # Verify no longer in tunneled services
    services_resp = client.get("/api/tunnel/services")
    assert services_resp.json()["tunneled_services"] == []

    # Verify still in status list but disconnected
    status_resp = client.get("/api/tunnel/status")
    tunnel_entry = next(
        (t for t in status_resp.json()["tunnels"] if t["tunnel_id"] == tunnel_id),
        None,
    )
    assert tunnel_entry is not None
    assert tunnel_entry["status"] == "disconnected"


# ===== Multiple Tunnels =====

def test_multiple_tunnels_different_services():
    services = [
        ("svc-multi-a", 8700),
        ("svc-multi-b", 8701),
        ("svc-multi-c", 8702),
    ]
    tunnel_ids = []
    for svc_id, port in services:
        resp = client.post("/api/tunnel/start", json={
            "service_id": svc_id,
            "service_port": port,
        })
        assert resp.status_code == 200
        tunnel_ids.append(resp.json()["tunnel_id"])

    # All IDs are unique
    assert len(set(tunnel_ids)) == 3

    # All appear in status
    status_resp = client.get("/api/tunnel/status")
    assert len(status_resp.json()["tunnels"]) == 3

    # All appear in services
    services_resp = client.get("/api/tunnel/services")
    assert len(services_resp.json()["tunneled_services"]) == 3

    # Health reflects count
    health_resp = client.get("/api/health")
    assert health_resp.json()["active_tunnels"] == 3
    assert health_resp.json()["total_tunnels"] == 3

def test_multiple_tunnels_stop_one_leaves_others_active():
    resp_a = client.post("/api/tunnel/start", json={"service_id": "svc-keep-a", "service_port": 8800})
    resp_b = client.post("/api/tunnel/start", json={"service_id": "svc-keep-b", "service_port": 8801})
    resp_c = client.post("/api/tunnel/start", json={"service_id": "svc-stop-c", "service_port": 8802})

    stop_id = resp_c.json()["tunnel_id"]
    client.post("/api/tunnel/stop", json={"tunnel_id": stop_id})

    services_resp = client.get("/api/tunnel/services")
    active_ids = [s["service_id"] for s in services_resp.json()["tunneled_services"]]
    assert "svc-keep-a" in active_ids
    assert "svc-keep-b" in active_ids
    assert "svc-stop-c" not in active_ids

def test_same_service_can_restart_after_stop():
    start_resp = client.post("/api/tunnel/start", json={"service_id": "svc-restart", "service_port": 8900})
    tunnel_id = start_resp.json()["tunnel_id"]
    client.post("/api/tunnel/stop", json={"tunnel_id": tunnel_id})

    # Should be able to start again after stopping
    restart_resp = client.post("/api/tunnel/start", json={"service_id": "svc-restart", "service_port": 8900})
    assert restart_resp.status_code == 200
    assert restart_resp.json()["status"] == "active"
    assert restart_resp.json()["tunnel_id"] != tunnel_id
