"""Tests for admin/services/base.py — StillwaterService abstract base class.

Rung target: 641 (unit tests only, no real network, no side effects).
All HTTP calls are mocked; FastAPI TestClient is used for endpoint tests.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

# ---------------------------------------------------------------------------
# Path setup — allow importing from admin/services without package install
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "admin"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from services.base import StillwaterService


# ===========================================================================
# Concrete subclass fixtures
# ===========================================================================


class _ConcreteService(StillwaterService):
    """Minimal concrete subclass for testing the base class contract."""

    def health(self) -> dict:
        return {"provider": "test", "uptime_s": 42}

    def register_routes(self, app: FastAPI) -> None:
        @app.get("/api/custom")
        async def custom():
            return {"custom": True}


def _make_service(**kwargs) -> _ConcreteService:
    defaults = dict(
        service_id="test-svc",
        service_type="custom",
        name="Test Service",
        version="1.0.0",
        port=9000,
    )
    defaults.update(kwargs)
    return _ConcreteService(**defaults)


# ===========================================================================
# BASE CLASS CONTRACT TESTS
# ===========================================================================


class TestAbstractBaseClass:
    def test_cannot_instantiate_directly(self):
        """StillwaterService is abstract — direct instantiation must raise TypeError."""
        with pytest.raises(TypeError):
            StillwaterService(  # type: ignore[abstract]
                service_id="x",
                service_type="custom",
                name="X",
                version="0.1.0",
                port=9000,
            )

    def test_concrete_subclass_missing_health_raises(self):
        """Subclass missing health() cannot be instantiated."""
        class MissingHealth(StillwaterService):
            def register_routes(self, app: FastAPI) -> None:
                pass

        with pytest.raises(TypeError):
            MissingHealth(  # type: ignore[abstract]
                service_id="x",
                service_type="custom",
                name="X",
                version="0.1.0",
                port=9000,
            )

    def test_concrete_subclass_missing_register_routes_raises(self):
        """Subclass missing register_routes() cannot be instantiated."""
        class MissingRoutes(StillwaterService):
            def health(self) -> dict:
                return {}

        with pytest.raises(TypeError):
            MissingRoutes(  # type: ignore[abstract]
                service_id="x",
                service_type="custom",
                name="X",
                version="0.1.0",
                port=9000,
            )

    def test_concrete_subclass_with_both_methods_works(self):
        """Fully implemented subclass instantiates without error."""
        svc = _make_service()
        assert svc.service_id == "test-svc"

    def test_constructor_stores_all_fields(self):
        """Constructor correctly stores all provided fields."""
        svc = _make_service(
            service_id="my-svc",
            service_type="llm",
            name="My LLM",
            version="2.0.0",
            port=8788,
            oauth3_scopes=["llm:read", "llm:write"],
            evidence_capture=False,
            admin_url="http://127.0.0.1:9999",
        )
        assert svc.service_id == "my-svc"
        assert svc.service_type == "llm"
        assert svc.name == "My LLM"
        assert svc.version == "2.0.0"
        assert svc.port == 8788
        assert svc.oauth3_scopes == ["llm:read", "llm:write"]
        assert svc.evidence_capture is False
        assert svc.admin_url == "http://127.0.0.1:9999"

    def test_oauth3_scopes_defaults_to_empty_list(self):
        """oauth3_scopes defaults to [] when not provided."""
        svc = _make_service()
        assert svc.oauth3_scopes == []

    def test_evidence_capture_defaults_to_true(self):
        """evidence_capture defaults to True when not provided."""
        svc = _make_service()
        assert svc.evidence_capture is True

    def test_admin_url_defaults_to_localhost_8787(self):
        """admin_url defaults to http://127.0.0.1:8787."""
        svc = _make_service()
        assert svc.admin_url == "http://127.0.0.1:8787"

    def test_app_is_none_before_create_app(self):
        """_app attribute is None before create_app() is called."""
        svc = _make_service()
        assert svc._app is None


# ===========================================================================
# CREATE_APP TESTS
# ===========================================================================


class TestCreateApp:
    def test_create_app_returns_fastapi_instance(self):
        """create_app() returns a FastAPI instance."""
        svc = _make_service()
        app = svc.create_app()
        assert isinstance(app, FastAPI)

    def test_create_app_stores_app_on_self(self):
        """create_app() stores the created app in self._app."""
        svc = _make_service()
        app = svc.create_app()
        assert svc._app is app

    def test_app_title_matches_service_name(self):
        """FastAPI app title matches the service name."""
        svc = _make_service(name="My Service")
        app = svc.create_app()
        assert app.title == "My Service"

    def test_app_version_matches_service_version(self):
        """FastAPI app version matches the service version."""
        svc = _make_service(version="3.1.4")
        app = svc.create_app()
        assert app.version == "3.1.4"

    def test_custom_routes_are_registered(self):
        """Routes registered via register_routes() are accessible."""
        svc = _make_service()
        app = svc.create_app()
        client = TestClient(app, raise_server_exceptions=True)
        resp = client.get("/api/custom")
        assert resp.status_code == 200
        assert resp.json() == {"custom": True}


# ===========================================================================
# HEALTH ENDPOINT TESTS
# ===========================================================================


class TestHealthEndpoint:
    def test_health_returns_200(self):
        """GET /api/health returns HTTP 200."""
        svc = _make_service()
        app = svc.create_app()
        client = TestClient(app)
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_health_contains_status_ok(self):
        """Health response contains status: ok."""
        svc = _make_service()
        app = svc.create_app()
        client = TestClient(app)
        body = client.get("/api/health").json()
        assert body["status"] == "ok"

    def test_health_contains_service_id(self):
        """Health response contains correct service_id."""
        svc = _make_service(service_id="my-svc")
        app = svc.create_app()
        client = TestClient(app)
        body = client.get("/api/health").json()
        assert body["service_id"] == "my-svc"

    def test_health_contains_service_type(self):
        """Health response contains correct service_type."""
        svc = _make_service(service_type="llm")
        app = svc.create_app()
        client = TestClient(app)
        body = client.get("/api/health").json()
        assert body["service_type"] == "llm"

    def test_health_contains_version(self):
        """Health response contains correct version."""
        svc = _make_service(version="9.8.7")
        app = svc.create_app()
        client = TestClient(app)
        body = client.get("/api/health").json()
        assert body["version"] == "9.8.7"

    def test_health_merges_subclass_health_fields(self):
        """Health response includes fields returned by subclass health() method."""
        svc = _make_service()
        app = svc.create_app()
        client = TestClient(app)
        body = client.get("/api/health").json()
        # _ConcreteService.health() returns {"provider": "test", "uptime_s": 42}
        assert body["provider"] == "test"
        assert body["uptime_s"] == 42


# ===========================================================================
# SERVICE INFO ENDPOINT TESTS
# ===========================================================================


class TestServiceInfoEndpoint:
    def test_service_info_returns_200(self):
        """GET /api/service-info returns HTTP 200."""
        svc = _make_service()
        app = svc.create_app()
        client = TestClient(app)
        resp = client.get("/api/service-info")
        assert resp.status_code == 200

    def test_service_info_contains_all_expected_fields(self):
        """Service info response contains all required fields."""
        svc = _make_service(
            service_id="info-svc",
            service_type="recipe",
            name="Info Service",
            version="5.0.0",
            port=8789,
            oauth3_scopes=["recipe:run"],
            evidence_capture=True,
        )
        app = svc.create_app()
        client = TestClient(app)
        body = client.get("/api/service-info").json()
        assert body["service_id"] == "info-svc"
        assert body["service_type"] == "recipe"
        assert body["name"] == "Info Service"
        assert body["version"] == "5.0.0"
        assert body["port"] == 8789
        assert body["oauth3_scopes"] == ["recipe:run"]
        assert body["evidence_capture"] is True


# ===========================================================================
# EVIDENCE MIDDLEWARE TESTS
# ===========================================================================


class TestEvidenceMiddleware:
    def test_evidence_middleware_adds_x_service_id(self):
        """Evidence middleware adds X-Service-Id header."""
        svc = _make_service(service_id="ev-svc", evidence_capture=True)
        app = svc.create_app()
        client = TestClient(app)
        resp = client.get("/api/health")
        assert resp.headers.get("x-service-id") == "ev-svc"

    def test_evidence_middleware_adds_x_duration_ms(self):
        """Evidence middleware adds X-Duration-Ms header with a numeric value."""
        svc = _make_service(evidence_capture=True)
        app = svc.create_app()
        client = TestClient(app)
        resp = client.get("/api/health")
        duration_header = resp.headers.get("x-duration-ms")
        assert duration_header is not None
        # Should be parseable as a float
        duration = float(duration_header)
        assert duration >= 0.0

    def test_evidence_middleware_adds_x_timestamp(self):
        """Evidence middleware adds X-Timestamp header with an ISO datetime string."""
        svc = _make_service(evidence_capture=True)
        app = svc.create_app()
        client = TestClient(app)
        resp = client.get("/api/health")
        ts = resp.headers.get("x-timestamp")
        assert ts is not None
        assert len(ts) > 0
        # Should contain date separator
        assert "T" in ts or "-" in ts

    def test_evidence_middleware_disabled_no_x_service_id(self):
        """When evidence_capture=False, X-Service-Id header is NOT added."""
        svc = _make_service(evidence_capture=False)
        app = svc.create_app()
        client = TestClient(app)
        resp = client.get("/api/health")
        assert "x-service-id" not in resp.headers

    def test_evidence_middleware_disabled_no_x_duration_ms(self):
        """When evidence_capture=False, X-Duration-Ms header is NOT added."""
        svc = _make_service(evidence_capture=False)
        app = svc.create_app()
        client = TestClient(app)
        resp = client.get("/api/health")
        assert "x-duration-ms" not in resp.headers

    def test_evidence_middleware_disabled_no_x_timestamp(self):
        """When evidence_capture=False, X-Timestamp header is NOT added."""
        svc = _make_service(evidence_capture=False)
        app = svc.create_app()
        client = TestClient(app)
        resp = client.get("/api/health")
        assert "x-timestamp" not in resp.headers


# ===========================================================================
# REGISTRATION TESTS (mock HTTP)
# ===========================================================================


class TestRegisterWithAdmin:
    def test_register_calls_post_to_correct_url(self):
        """_register_with_admin() calls POST to {admin_url}/api/services/register."""
        svc = _make_service(admin_url="http://127.0.0.1:8787")

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            result = svc._register_with_admin()

        assert mock_open.called
        req_arg = mock_open.call_args[0][0]
        assert req_arg.full_url == "http://127.0.0.1:8787/api/services/register"

    def test_register_uses_post_method(self):
        """_register_with_admin() uses POST HTTP method."""
        svc = _make_service()

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            svc._register_with_admin()

        req_arg = mock_open.call_args[0][0]
        assert req_arg.method == "POST"

    def test_register_returns_true_on_200(self):
        """_register_with_admin() returns True when admin responds 200."""
        svc = _make_service()

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = svc._register_with_admin()

        assert result is True

    def test_register_returns_false_when_admin_not_running(self):
        """_register_with_admin() returns False when admin is not running (connection refused)."""
        svc = _make_service()

        with patch("urllib.request.urlopen", side_effect=ConnectionRefusedError("refused")):
            result = svc._register_with_admin()

        assert result is False

    def test_register_returns_false_on_timeout(self):
        """_register_with_admin() returns False on timeout."""
        svc = _make_service()

        with patch("urllib.request.urlopen", side_effect=TimeoutError("timed out")):
            result = svc._register_with_admin()

        assert result is False

    def test_register_payload_contains_service_id(self):
        """Registration payload includes correct service_id."""
        svc = _make_service(service_id="payload-svc")

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            svc._register_with_admin()

        req_arg = mock_open.call_args[0][0]
        payload = json.loads(req_arg.data.decode("utf-8"))
        assert payload["service_id"] == "payload-svc"

    def test_register_payload_contains_service_type(self):
        """Registration payload includes correct service_type."""
        svc = _make_service(service_type="llm")

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            svc._register_with_admin()

        req_arg = mock_open.call_args[0][0]
        payload = json.loads(req_arg.data.decode("utf-8"))
        assert payload["service_type"] == "llm"

    def test_register_payload_contains_port(self):
        """Registration payload includes correct port."""
        svc = _make_service(port=8788)

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            svc._register_with_admin()

        req_arg = mock_open.call_args[0][0]
        payload = json.loads(req_arg.data.decode("utf-8"))
        assert payload["port"] == 8788

    def test_register_payload_contains_oauth3_scopes(self):
        """Registration payload includes oauth3_scopes."""
        svc = _make_service(oauth3_scopes=["read", "write"])

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            svc._register_with_admin()

        req_arg = mock_open.call_args[0][0]
        payload = json.loads(req_arg.data.decode("utf-8"))
        assert payload["oauth3_scopes"] == ["read", "write"]

    def test_register_payload_contains_health_endpoint(self):
        """Registration payload includes health_endpoint."""
        svc = _make_service()

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            svc._register_with_admin()

        req_arg = mock_open.call_args[0][0]
        payload = json.loads(req_arg.data.decode("utf-8"))
        assert payload["health_endpoint"] == "/api/health"

    def test_register_payload_contains_version(self):
        """Registration payload includes version."""
        svc = _make_service(version="1.2.3")

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            svc._register_with_admin()

        req_arg = mock_open.call_args[0][0]
        payload = json.loads(req_arg.data.decode("utf-8"))
        assert payload["version"] == "1.2.3"

    def test_register_content_type_header_is_json(self):
        """Registration request has Content-Type: application/json."""
        svc = _make_service()

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            svc._register_with_admin()

        req_arg = mock_open.call_args[0][0]
        assert req_arg.get_header("Content-type") == "application/json"

    def test_register_uses_custom_admin_url(self):
        """_register_with_admin() uses the configured admin_url."""
        svc = _make_service(admin_url="http://10.0.0.1:9999")

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            svc._register_with_admin()

        req_arg = mock_open.call_args[0][0]
        assert "10.0.0.1:9999" in req_arg.full_url

    def test_register_silently_handles_generic_exception(self):
        """_register_with_admin() returns False on any unexpected exception."""
        svc = _make_service()

        with patch("urllib.request.urlopen", side_effect=OSError("network error")):
            result = svc._register_with_admin()

        assert result is False
