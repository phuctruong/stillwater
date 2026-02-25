"""Tests for stillwater.orchestrator — ServiceEndpoint + ServiceOrchestrator.

All HTTP calls are mocked via unittest.mock. No real network calls.
"""
from __future__ import annotations

import io
import json
import urllib.error
import urllib.request
from unittest.mock import MagicMock, patch, call

import pytest

from stillwater.orchestrator import ServiceEndpoint, ServiceOrchestrator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(payload: dict, status: int = 200):
    """Build a mock urllib response object."""
    body = json.dumps(payload).encode("utf-8")
    resp = MagicMock()
    resp.status = status
    resp.read.return_value = body
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def _services_payload(*svcs: dict) -> dict:
    """Wrap service dicts in the admin API envelope."""
    return {"services": list(svcs)}


_SVC_LLM = {
    "service_id": "llm-portal",
    "service_type": "llm",
    "name": "LLM Portal",
    "host": "127.0.0.1",
    "port": 8788,
    "status": "online",
}

_SVC_CPU = {
    "service_id": "cpu-service",
    "service_type": "cpu",
    "name": "CPU Service",
    "host": "127.0.0.1",
    "port": 8792,
    "status": "online",
}

_SVC_RECIPE = {
    "service_id": "recipe-engine",
    "service_type": "recipe",
    "name": "Recipe Engine",
    "host": "127.0.0.1",
    "port": 8789,
    "status": "online",
}

_SVC_EVIDENCE = {
    "service_id": "evidence-pipeline",
    "service_type": "evidence",
    "name": "Evidence Pipeline",
    "host": "127.0.0.1",
    "port": 8790,
    "status": "online",
}

_SVC_OAUTH3 = {
    "service_id": "oauth3-authority",
    "service_type": "oauth3",
    "name": "OAuth3 Authority",
    "host": "127.0.0.1",
    "port": 8791,
    "status": "online",
}

_SVC_BROWSER = {
    "service_id": "browser",
    "service_type": "browser",
    "name": "Browser",
    "host": "127.0.0.1",
    "port": 9222,
    "status": "online",
}


# ===========================================================================
# ServiceEndpoint tests (4)
# ===========================================================================

class TestServiceEndpoint:
    def test_creation_with_all_fields(self):
        """ServiceEndpoint stores all supplied fields."""
        ep = ServiceEndpoint(
            service_id="llm-portal",
            service_type="llm",
            name="LLM Portal",
            host="127.0.0.1",
            port=8788,
            status="online",
        )
        assert ep.service_id == "llm-portal"
        assert ep.service_type == "llm"
        assert ep.name == "LLM Portal"
        assert ep.host == "127.0.0.1"
        assert ep.port == 8788
        assert ep.status == "online"

    def test_base_url_auto_generated_from_host_and_port(self):
        """base_url is constructed from host:port when not provided."""
        ep = ServiceEndpoint(
            service_id="cpu-service",
            service_type="cpu",
            name="CPU",
            host="192.168.1.10",
            port=8792,
            status="online",
        )
        assert ep.base_url == "http://192.168.1.10:8792"

    def test_custom_base_url_overrides_auto_generation(self):
        """Explicitly supplied base_url is not overwritten by __post_init__."""
        ep = ServiceEndpoint(
            service_id="llm-portal",
            service_type="llm",
            name="LLM Portal",
            host="127.0.0.1",
            port=8788,
            status="online",
            base_url="https://custom.host:443",
        )
        assert ep.base_url == "https://custom.host:443"

    def test_dataclass_field_defaults(self):
        """base_url defaults to empty string before __post_init__ sets it."""
        ep = ServiceEndpoint(
            service_id="x",
            service_type="x",
            name="X",
            host="localhost",
            port=1234,
            status="unknown",
        )
        # After __post_init__, base_url must be set
        assert ep.base_url == "http://localhost:1234"


# ===========================================================================
# Orchestrator availability tests (4)
# ===========================================================================

class TestOrchestratorAvailability:
    def test_is_available_returns_true_when_admin_responds_200(self):
        """is_available() returns True when admin returns HTTP 200."""
        orch = ServiceOrchestrator()
        resp = _make_response({"services": []}, status=200)
        with patch("urllib.request.urlopen", return_value=resp):
            result = orch.is_available()
        assert result is True

    def test_is_available_returns_false_when_admin_not_running(self):
        """is_available() returns False when connection is refused."""
        orch = ServiceOrchestrator()
        with patch("urllib.request.urlopen", side_effect=OSError("Connection refused")):
            result = orch.is_available()
        assert result is False

    def test_is_available_caches_result_does_not_call_twice(self):
        """Second call to is_available() uses cached value without HTTP round-trip."""
        orch = ServiceOrchestrator()
        resp = _make_response({"services": []}, status=200)
        with patch("urllib.request.urlopen", return_value=resp) as mock_open:
            orch.is_available()
            orch.is_available()
            # urlopen should only be called once
            assert mock_open.call_count == 1

    def test_reset_cached_availability(self):
        """Resetting _available to None forces a fresh check on next call."""
        orch = ServiceOrchestrator()
        # First call: available
        resp = _make_response({"services": []}, status=200)
        with patch("urllib.request.urlopen", return_value=resp):
            assert orch.is_available() is True

        # Reset and simulate down
        orch._available = None
        with patch("urllib.request.urlopen", side_effect=OSError("down")):
            assert orch.is_available() is False


# ===========================================================================
# Discovery tests (4)
# ===========================================================================

class TestDiscovery:
    def test_discover_parses_services_correctly(self):
        """discover() builds ServiceEndpoint objects from admin payload."""
        orch = ServiceOrchestrator()
        payload = _services_payload(_SVC_LLM, _SVC_CPU)
        resp = _make_response(payload)
        with patch("urllib.request.urlopen", return_value=resp):
            services = orch.discover()

        assert "llm-portal" in services
        assert "cpu-service" in services
        llm = services["llm-portal"]
        assert llm.service_type == "llm"
        assert llm.port == 8788
        assert llm.base_url == "http://127.0.0.1:8788"

    def test_discover_sets_available_true_on_success(self):
        """discover() marks orchestrator available when admin responds."""
        orch = ServiceOrchestrator()
        resp = _make_response(_services_payload(_SVC_LLM))
        with patch("urllib.request.urlopen", return_value=resp):
            orch.discover()
        assert orch._available is True

    def test_discover_with_empty_service_list(self):
        """discover() with no services returns empty dict, still available."""
        orch = ServiceOrchestrator()
        resp = _make_response({"services": []})
        with patch("urllib.request.urlopen", return_value=resp):
            services = orch.discover()
        assert services == {}
        assert orch._available is True

    def test_discover_with_network_error_sets_available_false(self):
        """discover() sets _available=False when network call fails."""
        orch = ServiceOrchestrator()
        with patch("urllib.request.urlopen", side_effect=OSError("timeout")):
            services = orch.discover()
        assert services == {}
        assert orch._available is False


# ===========================================================================
# Service lookup tests (4)
# ===========================================================================

class TestServiceLookup:
    def _orch_with_services(self) -> ServiceOrchestrator:
        orch = ServiceOrchestrator()
        resp = _make_response(_services_payload(_SVC_LLM, _SVC_CPU, _SVC_RECIPE))
        with patch("urllib.request.urlopen", return_value=resp):
            orch.discover()
        return orch

    def test_get_service_finds_registered_service(self):
        """get_service() returns the correct ServiceEndpoint by ID."""
        orch = self._orch_with_services()
        svc = orch.get_service("llm-portal")
        assert svc is not None
        assert svc.service_id == "llm-portal"
        assert svc.name == "LLM Portal"

    def test_get_service_returns_none_for_unknown(self):
        """get_service() returns None for an unregistered service ID."""
        orch = self._orch_with_services()
        svc = orch.get_service("nonexistent-service")
        assert svc is None

    def test_get_service_by_type_finds_by_type(self):
        """get_service_by_type() returns an endpoint matching the given type."""
        orch = self._orch_with_services()
        svc = orch.get_service_by_type("cpu")
        assert svc is not None
        assert svc.service_id == "cpu-service"

    def test_get_service_by_type_returns_none_for_unknown_type(self):
        """get_service_by_type() returns None when no service matches the type."""
        orch = self._orch_with_services()
        svc = orch.get_service_by_type("pvideo")
        assert svc is None


# ===========================================================================
# Intent routing tests (5)
# ===========================================================================

class TestIntentRouting:
    def _orch_all_services(self) -> ServiceOrchestrator:
        orch = ServiceOrchestrator()
        resp = _make_response(_services_payload(
            _SVC_LLM, _SVC_CPU, _SVC_RECIPE, _SVC_EVIDENCE, _SVC_OAUTH3, _SVC_BROWSER,
        ))
        with patch("urllib.request.urlopen", return_value=resp):
            orch.discover()
        return orch

    def test_route_intent_hash_to_cpu_service(self):
        """route_intent('hash') routes to cpu-service."""
        orch = self._orch_all_services()
        result = orch.route_intent("hash")
        assert result["ok"] is True
        assert result["routed"] is True
        assert result["service_id"] == "cpu-service"

    def test_route_intent_chat_to_llm_portal(self):
        """route_intent('chat') routes to llm-portal."""
        orch = self._orch_all_services()
        result = orch.route_intent("chat")
        assert result["ok"] is True
        assert result["service_id"] == "llm-portal"
        assert result["base_url"] == "http://127.0.0.1:8788"

    def test_route_intent_recipe_to_recipe_engine(self):
        """route_intent('recipe') routes to recipe-engine."""
        orch = self._orch_all_services()
        result = orch.route_intent("recipe")
        assert result["ok"] is True
        assert result["service_id"] == "recipe-engine"

    def test_route_intent_evidence_to_evidence_pipeline(self):
        """route_intent('evidence') routes to evidence-pipeline."""
        orch = self._orch_all_services()
        result = orch.route_intent("evidence")
        assert result["ok"] is True
        assert result["service_id"] == "evidence-pipeline"

    def test_route_intent_unknown_returns_error(self):
        """route_intent() with an unmapped intent returns ok=False."""
        orch = self._orch_all_services()
        result = orch.route_intent("unknown-thing")
        assert result["ok"] is False
        assert result["routed"] is False
        assert "Unknown intent" in result["error"]

    def test_route_intent_service_not_in_registry_returns_error(self):
        """route_intent() returns error when intent maps to a service not discovered."""
        orch = ServiceOrchestrator()  # no services discovered
        result = orch.route_intent("chat")
        assert result["ok"] is False
        assert result["routed"] is False
        assert "llm-portal" in result["error"]

    def test_route_intent_case_insensitive(self):
        """route_intent() normalises intent to lowercase before matching."""
        orch = self._orch_all_services()
        result = orch.route_intent("HASH")
        assert result["ok"] is True
        assert result["service_id"] == "cpu-service"


# ===========================================================================
# call_service tests (3)
# ===========================================================================

class TestCallService:
    def _orch_with_llm(self) -> ServiceOrchestrator:
        orch = ServiceOrchestrator()
        resp = _make_response(_services_payload(_SVC_LLM))
        with patch("urllib.request.urlopen", return_value=resp):
            orch.discover()
        return orch

    def test_successful_post_call(self):
        """call_service() returns parsed JSON from a successful POST."""
        orch = self._orch_with_llm()
        service_resp = _make_response({"ok": True, "choices": [{"text": "hello"}]})
        with patch("urllib.request.urlopen", return_value=service_resp):
            result = orch.call_service(
                "llm-portal",
                "/v1/chat/completions",
                data={"model": "llama3", "messages": []},
            )
        assert result["ok"] is True
        assert "choices" in result

    def test_service_not_found(self):
        """call_service() returns error dict when service_id is not in registry."""
        orch = self._orch_with_llm()
        result = orch.call_service("nonexistent", "/ping")
        assert result["ok"] is False
        assert "nonexistent" in result["error"]

    def test_network_error_handling(self):
        """call_service() returns ok=False dict on network-level exceptions."""
        orch = self._orch_with_llm()
        with patch("urllib.request.urlopen", side_effect=OSError("connection refused")):
            result = orch.call_service("llm-portal", "/v1/chat/completions", data={})
        assert result["ok"] is False
        assert "connection refused" in result["error"]

    def test_http_error_returns_parsed_json_body(self):
        """call_service() parses JSON error body from HTTPError when available."""
        orch = self._orch_with_llm()
        error_payload = json.dumps({"ok": False, "error": "rate limited"}).encode()
        fp = io.BytesIO(error_payload)
        http_err = urllib.error.HTTPError(
            url="http://127.0.0.1:8788/v1/chat/completions",
            code=429,
            msg="Too Many Requests",
            hdrs=MagicMock(),  # type: ignore[arg-type]
            fp=fp,
        )
        with patch("urllib.request.urlopen", side_effect=http_err):
            result = orch.call_service("llm-portal", "/v1/chat/completions", data={})
        assert result["ok"] is False
        assert "rate limited" in result["error"]

    def test_http_error_non_json_body_returns_fallback(self):
        """call_service() returns a plain error dict when HTTP error body is not JSON."""
        orch = self._orch_with_llm()
        fp = io.BytesIO(b"Internal Server Error")
        http_err = urllib.error.HTTPError(
            url="http://127.0.0.1:8788/v1/chat/completions",
            code=500,
            msg="Internal Server Error",
            hdrs=MagicMock(),  # type: ignore[arg-type]
            fp=fp,
        )
        with patch("urllib.request.urlopen", side_effect=http_err):
            result = orch.call_service("llm-portal", "/v1/chat/completions", data={})
        assert result["ok"] is False
        assert "500" in result["error"]

    def test_get_method_sends_no_body(self):
        """call_service() with method=GET and no data sends a GET request."""
        orch = self._orch_with_llm()
        service_resp = _make_response({"ok": True, "models": ["llama3"]})
        with patch("urllib.request.urlopen", return_value=service_resp) as mock_open:
            result = orch.call_service("llm-portal", "/v1/models", method="GET")
        assert result["ok"] is True
        # The Request passed to urlopen should have no body
        req_arg = mock_open.call_args[0][0]
        assert req_arg.method == "GET"
        assert req_arg.data is None


# ===========================================================================
# Composition tests (2)
# ===========================================================================

class TestComposeResults:
    def test_compose_results_all_ok(self):
        """compose_results() with all-success results returns ok=True and no errors."""
        orch = ServiceOrchestrator()
        results = [
            {"ok": True, "data": "a"},
            {"ok": True, "data": "b"},
        ]
        composed = orch.compose_results(results)
        assert composed["ok"] is True
        assert composed["service_count"] == 2
        assert composed["errors"] is None
        assert composed["results"] == results

    def test_compose_results_with_mixed_ok_and_error(self):
        """compose_results() with any failure returns ok=False and collects errors."""
        orch = ServiceOrchestrator()
        results = [
            {"ok": True, "data": "a"},
            {"ok": False, "error": "timeout"},
            {"ok": False, "error": "not found"},
        ]
        composed = orch.compose_results(results)
        assert composed["ok"] is False
        assert composed["service_count"] == 3
        assert "timeout" in composed["errors"]
        assert "not found" in composed["errors"]


# ===========================================================================
# Status tests (1)
# ===========================================================================

class TestStatus:
    def test_status_returns_expected_structure(self):
        """status() returns admin_available, admin_url, service_count, and services dict."""
        orch = ServiceOrchestrator(admin_url="http://127.0.0.1:8787")
        resp = _make_response(_services_payload(_SVC_LLM, _SVC_CPU))
        with patch("urllib.request.urlopen", return_value=resp):
            orch.discover()

        st = orch.status()
        assert st["admin_available"] is True
        assert st["admin_url"] == "http://127.0.0.1:8787"
        assert st["service_count"] == 2
        assert "llm-portal" in st["services"]
        assert "cpu-service" in st["services"]
        llm_entry = st["services"]["llm-portal"]
        assert llm_entry["name"] == "LLM Portal"
        assert llm_entry["type"] == "llm"
        assert llm_entry["port"] == 8788
        assert llm_entry["status"] == "online"

    def test_status_before_discover_shows_no_services(self):
        """status() before any discover() call shows empty services dict."""
        orch = ServiceOrchestrator()
        st = orch.status()
        assert st["service_count"] == 0
        assert st["services"] == {}
        assert st["admin_available"] is None
