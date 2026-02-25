from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_DIR = REPO_ROOT / "admin"
for _path in (str(REPO_ROOT), str(ADMIN_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from services.health_dashboard import HealthDashboardService, SERVICE_PORTS


def _service(tmp_path: Path) -> HealthDashboardService:
    repo = tmp_path / "repo"
    (repo / "data" / "custom").mkdir(parents=True, exist_ok=True)
    return HealthDashboardService(repo)


def test_probe_service_ok(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_request_json", lambda *args, **kwargs: (200, {"status": "ok"}, 1.5, None))
    out = svc._probe_service("admin", 8787)
    assert out["status"] == "ok"
    assert out["port"] == 8787


def test_probe_service_down_on_transport_error(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_request_json", lambda *args, **kwargs: (0, None, 2.2, "connection refused"))
    out = svc._probe_service("admin", 8787)
    assert out["status"] == "down"
    assert "error" in out


def test_probe_service_error_on_unexpected_response(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_request_json", lambda *args, **kwargs: (500, {"status": "fail"}, 3.1, None))
    out = svc._probe_service("admin", 8787)
    assert out["status"] == "error"
    assert out["http_status"] == 500


def test_services_status_reports_all_known_services(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_probe_service", lambda sid, port: {"port": port, "status": "ok", "latency_ms": 1.0})
    out = svc._services_status()
    assert out["total"] == len(SERVICE_PORTS)
    assert out["ok_count"] == len(SERVICE_PORTS)
    assert set(out["services"].keys()) == set(SERVICE_PORTS.keys())


def test_validate_provider_key_ok(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_request_json", lambda *args, **kwargs: (200, {}, 1.0, None))
    valid, status, error = svc._validate_provider_key("openai", "k")
    assert valid is True
    assert status == "ok"
    assert error is None


def test_validate_provider_key_auth_failed(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_request_json", lambda *args, **kwargs: (401, {}, 1.0, None))
    valid, status, error = svc._validate_provider_key("openai", "k")
    assert valid is False
    assert status == "auth_failed"
    assert "401" in str(error)


def test_validate_provider_key_transport_error(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_request_json", lambda *args, **kwargs: (0, None, 1.0, "timeout"))
    valid, status, error = svc._validate_provider_key("openai", "k")
    assert valid is False
    assert status == "error"
    assert error == "timeout"


def test_llm_status_includes_claude_code(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_which_claude", lambda: "/usr/bin/claude")
    monkeypatch.setattr(svc, "_provider_key", lambda provider: ("", "none"))
    out = svc._llm_status()
    assert out["providers"]["claude-code"]["available"] is True
    assert out["providers"]["claude-code"]["cli_path"] == "/usr/bin/claude"


def test_llm_status_marks_provider_not_configured(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_which_claude", lambda: "")
    monkeypatch.setattr(svc, "_provider_key", lambda provider: ("", "none"))
    out = svc._llm_status()
    assert out["providers"]["openai"]["status"] == "not_configured"
    assert out["providers"]["openai"]["has_key"] is False


def test_llm_status_records_last_key_check(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_which_claude", lambda: "")
    monkeypatch.setattr(svc, "_provider_key", lambda provider: ("k", "env") if provider == "openai" else ("", "none"))
    monkeypatch.setattr(svc, "_validate_provider_key", lambda provider, key: (True, "ok", None))
    out = svc._llm_status()
    assert out["providers"]["openai"]["key_valid"] is True
    assert "openai" in svc._last_key_checks
    assert svc._last_key_checks["openai"]["status"] == "ok"


def test_keys_status_uses_last_test_data(tmp_path: Path) -> None:
    svc = _service(tmp_path)
    svc._last_key_checks["openai"] = {
        "valid": True,
        "status": "ok",
        "error": None,
        "last_tested": "2026-02-24T00:00:00Z",
    }
    out = svc._keys_status()
    assert "openai" in out["providers"]
    assert out["providers"]["openai"]["last_tested"] == "2026-02-24T00:00:00Z"


def test_cloud_status_not_configured(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_load_cloud_config", lambda: {"enabled": False, "api_key": "", "api_url": ""})
    out = svc._cloud_status()
    assert out["status"] == "not_configured"
    assert out["solaceagi_configured"] is False


def test_cloud_status_unreachable(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_load_cloud_config", lambda: {"enabled": True, "api_key": "k", "api_url": "https://solaceagi.com/api"})
    monkeypatch.setattr(svc, "_request_json", lambda *args, **kwargs: (0, None, 3.0, "connection timeout"))
    out = svc._cloud_status()
    assert out["status"] == "unreachable"
    assert out["solaceagi_reachable"] is False


def test_cloud_status_auth_failed(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_load_cloud_config", lambda: {"enabled": True, "api_key": "k", "api_url": "https://solaceagi.com/api"})
    monkeypatch.setattr(svc, "_request_json", lambda *args, **kwargs: (401, {}, 2.0, None))
    out = svc._cloud_status()
    assert out["status"] == "auth_failed"
    assert out["solaceagi_reachable"] is True


def test_cloud_status_ok_reads_tier(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_load_cloud_config", lambda: {"enabled": True, "api_key": "k", "api_url": "https://solaceagi.com/api"})

    def _dispatcher(url, **kwargs):  # noqa: ANN001
        del kwargs
        if "account/tier" in url:
            return 200, {"tier": "pro"}, 1.5, None
        return 200, {"status": "ok"}, 1.2, None

    monkeypatch.setattr(svc, "_request_json", _dispatcher)
    out = svc._cloud_status()
    assert out["status"] == "ok"
    assert out["tier"] == "pro"


def test_oauth3_status_down(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_request_json", lambda *args, **kwargs: (0, None, 1.0, "refused"))
    out = svc._oauth3_status()
    assert out["status"] == "down"
    assert out["scope_gates"] == "not_configured"


def test_oauth3_status_ok(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)

    def _dispatcher(url, **kwargs):  # noqa: ANN001
        del kwargs
        if url.endswith("/oauth3/scopes"):
            return 200, {"ok": True, "count": 8}, 1.2, None
        return 200, {"status": "ok", "token_count": 4}, 1.1, None

    monkeypatch.setattr(svc, "_request_json", _dispatcher)
    out = svc._oauth3_status()
    assert out["status"] == "ok"
    assert out["active_tokens"] == 4
    assert out["scope_count"] == 8


def test_overall_status_down_when_none_ok(tmp_path: Path) -> None:
    svc = _service(tmp_path)
    out = svc._overall_status({"a": {"status": "down"}, "b": {"status": "error"}})
    assert out == "down"


def test_overall_status_degraded_when_mixed(tmp_path: Path) -> None:
    svc = _service(tmp_path)
    out = svc._overall_status({"a": {"status": "ok"}, "b": {"status": "down"}})
    assert out == "degraded"


def test_full_health_endpoint_contract(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_services_status", lambda: {"services": {"admin": {"status": "ok", "port": 8787}}, "ok_count": 1, "total": 1})
    monkeypatch.setattr(svc, "_llm_status", lambda: {"default_provider": "claude-code", "providers": {"claude-code": {"available": True}}})
    monkeypatch.setattr(svc, "_cloud_status", lambda: {"status": "not_configured"})
    monkeypatch.setattr(svc, "_oauth3_status", lambda: {"status": "down"})
    with TestClient(svc.create_app()) as client:
        res = client.get("/api/health/full")
    assert res.status_code == 200
    body = res.json()
    assert "status" in body
    assert "timestamp" in body
    assert "services" in body
    assert "llm" in body
    assert "cloud" in body
    assert "oauth3" in body


def test_services_endpoint_reports_all_service_ids(tmp_path: Path, monkeypatch) -> None:
    svc = _service(tmp_path)
    monkeypatch.setattr(svc, "_probe_service", lambda sid, port: {"port": port, "status": "ok", "latency_ms": 1.0})
    with TestClient(svc.create_app()) as client:
        res = client.get("/api/health/services")
    assert res.status_code == 200
    payload = res.json()
    assert payload["total"] == 11
    assert set(payload["services"].keys()) == set(SERVICE_PORTS.keys())
