"""Tests for admin/services — ServiceRegistry, models, persistence.

Rung target: 641 (unit tests only, no network, no side effects).
All HTTP calls are mocked; tmp_path is used for persistence.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Path setup — allow importing from admin/services without package install
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "admin"))

from services.models import (
    ServiceDescriptor,
    ServiceDiscoveryResult,
    ServiceHealth,
    ServiceRegistration,
    ServiceStatus,
    ServiceType,
)
from services.registry import KNOWN_PORTS, ServiceRegistry


# ===========================================================================
# Helpers
# ===========================================================================

def _make_registration(**kwargs) -> ServiceRegistration:
    defaults = dict(
        service_id="test-svc",
        service_type=ServiceType.CUSTOM,
        name="Test Service",
        port=9000,
    )
    defaults.update(kwargs)
    return ServiceRegistration(**defaults)


def _make_registry(tmp_path: Path) -> ServiceRegistry:
    return ServiceRegistry(persist_path=str(tmp_path / "registry.json"))


# ===========================================================================
# MODEL TESTS (8+ tests)
# ===========================================================================


class TestServiceDescriptor:
    def test_creation_with_valid_fields(self):
        desc = ServiceDescriptor(
            service_id="llm-portal",
            service_type=ServiceType.LLM,
            name="LLM Portal",
            port=8788,
        )
        assert desc.service_id == "llm-portal"
        assert desc.service_type == ServiceType.LLM
        assert desc.name == "LLM Portal"
        assert desc.port == 8788
        assert desc.host == "127.0.0.1"
        assert desc.version == "0.1.0"
        assert desc.status == ServiceStatus.STARTING

    def test_port_zero_fails(self):
        with pytest.raises(Exception):
            ServiceDescriptor(
                service_id="bad",
                service_type=ServiceType.CUSTOM,
                name="Bad",
                port=0,
            )

    def test_port_negative_fails(self):
        with pytest.raises(Exception):
            ServiceDescriptor(
                service_id="bad",
                service_type=ServiceType.CUSTOM,
                name="Bad",
                port=-1,
            )

    def test_port_above_max_fails(self):
        with pytest.raises(Exception):
            ServiceDescriptor(
                service_id="bad",
                service_type=ServiceType.CUSTOM,
                name="Bad",
                port=65536,
            )

    def test_port_boundary_values_valid(self):
        # 1 and 65535 are both valid
        d1 = ServiceDescriptor(
            service_id="a", service_type=ServiceType.CUSTOM, name="A", port=1
        )
        d2 = ServiceDescriptor(
            service_id="b", service_type=ServiceType.CUSTOM, name="B", port=65535
        )
        assert d1.port == 1
        assert d2.port == 65535

    def test_base_url_property(self):
        desc = ServiceDescriptor(
            service_id="s",
            service_type=ServiceType.RECIPE,
            name="Recipe",
            port=8789,
            host="192.168.1.10",
        )
        assert desc.base_url == "http://192.168.1.10:8789"

    def test_health_url_property(self):
        desc = ServiceDescriptor(
            service_id="s",
            service_type=ServiceType.RECIPE,
            name="Recipe",
            port=8789,
            health_endpoint="/api/health",
        )
        assert desc.health_url == "http://127.0.0.1:8789/api/health"

    def test_health_url_custom_endpoint(self):
        desc = ServiceDescriptor(
            service_id="s",
            service_type=ServiceType.CUSTOM,
            name="Custom",
            port=9000,
            health_endpoint="/healthz",
        )
        assert desc.health_url == "http://127.0.0.1:9000/healthz"

    def test_defaults_are_sensible(self):
        desc = ServiceDescriptor(
            service_id="x", service_type=ServiceType.CPU, name="CPU", port=8792
        )
        assert desc.evidence_capture is True
        assert desc.oauth3_scopes == []
        assert desc.metadata == {}
        assert desc.last_health_check == ""
        assert desc.registered_at != ""


class TestServiceTypeEnum:
    def test_all_expected_values_exist(self):
        expected = {"llm", "browser", "recipe", "evidence", "oauth3", "cpu", "tunnel", "custom"}
        actual = {t.value for t in ServiceType}
        assert expected == actual

    def test_is_string_enum(self):
        assert isinstance(ServiceType.LLM, str)
        assert ServiceType.LLM == "llm"


class TestServiceStatusEnum:
    def test_all_expected_values_exist(self):
        expected = {"online", "offline", "degraded", "starting"}
        actual = {s.value for s in ServiceStatus}
        assert expected == actual

    def test_is_string_enum(self):
        assert isinstance(ServiceStatus.ONLINE, str)
        assert ServiceStatus.ONLINE == "online"


class TestServiceRegistration:
    def test_creation_minimal(self):
        reg = _make_registration()
        assert reg.service_id == "test-svc"
        assert reg.port == 9000
        assert reg.host == "127.0.0.1"

    def test_registration_to_descriptor_fields_match(self):
        reg = _make_registration(
            service_id="my-svc",
            service_type=ServiceType.LLM,
            name="My LLM",
            port=8788,
            version="1.2.3",
            oauth3_scopes=["read", "write"],
            evidence_capture=False,
            metadata={"key": "value"},
        )
        # Manually construct a descriptor as registry.register() would do
        desc = ServiceDescriptor(
            service_id=reg.service_id,
            service_type=reg.service_type,
            name=reg.name,
            version=reg.version,
            host=reg.host,
            port=reg.port,
            health_endpoint=reg.health_endpoint,
            openapi_endpoint=reg.openapi_endpoint,
            oauth3_scopes=reg.oauth3_scopes,
            evidence_capture=reg.evidence_capture,
            metadata=reg.metadata,
            status=ServiceStatus.STARTING,
        )
        assert desc.service_id == "my-svc"
        assert desc.version == "1.2.3"
        assert desc.oauth3_scopes == ["read", "write"]
        assert desc.evidence_capture is False
        assert desc.metadata == {"key": "value"}


class TestServiceHealth:
    def test_creation(self):
        health = ServiceHealth(service_id="svc", status=ServiceStatus.ONLINE)
        assert health.service_id == "svc"
        assert health.status == ServiceStatus.ONLINE
        assert health.latency_ms == 0.0
        assert health.last_check != ""
        assert health.details == {}

    def test_creation_with_details(self):
        health = ServiceHealth(
            service_id="svc",
            status=ServiceStatus.DEGRADED,
            latency_ms=123.4,
            details={"memory_mb": 512},
        )
        assert health.latency_ms == 123.4
        assert health.details["memory_mb"] == 512


class TestServiceDiscoveryResult:
    def test_creation_empty(self):
        result = ServiceDiscoveryResult(discovered=[])
        assert result.discovered == []
        assert result.failed_ports == []
        assert result.scan_duration_ms == 0.0

    def test_creation_with_data(self):
        desc = ServiceDescriptor(
            service_id="found",
            service_type=ServiceType.LLM,
            name="Found",
            port=8788,
        )
        result = ServiceDiscoveryResult(
            discovered=[desc],
            failed_ports=[8789, 8790],
            scan_duration_ms=42.5,
        )
        assert len(result.discovered) == 1
        assert result.failed_ports == [8789, 8790]
        assert result.scan_duration_ms == 42.5


# ===========================================================================
# REGISTRY TESTS (12+ tests)
# ===========================================================================


class TestRegistryRegister:
    def test_register_returns_descriptor(self, tmp_path):
        registry = _make_registry(tmp_path)
        reg = _make_registration()
        desc = registry.register(reg)
        assert isinstance(desc, ServiceDescriptor)
        assert desc.service_id == "test-svc"

    def test_register_status_is_starting(self, tmp_path):
        registry = _make_registry(tmp_path)
        desc = registry.register(_make_registration())
        assert desc.status == ServiceStatus.STARTING

    def test_register_stores_in_registry(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration())
        assert registry.get("test-svc") is not None

    def test_register_duplicate_overwrites(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration(name="First", port=9000))
        registry.register(_make_registration(name="Second", port=9001))
        svc = registry.get("test-svc")
        assert svc is not None
        assert svc.name == "Second"
        assert svc.port == 9001

    def test_register_persists_to_disk(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration())
        persist_file = tmp_path / "registry.json"
        assert persist_file.exists()


class TestRegistryDeregister:
    def test_deregister_existing_returns_true(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration())
        result = registry.deregister("test-svc")
        assert result is True

    def test_deregister_removes_from_registry(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration())
        registry.deregister("test-svc")
        assert registry.get("test-svc") is None

    def test_deregister_nonexistent_returns_false(self, tmp_path):
        registry = _make_registry(tmp_path)
        result = registry.deregister("does-not-exist")
        assert result is False


class TestRegistryGet:
    def test_get_existing(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration())
        svc = registry.get("test-svc")
        assert svc is not None
        assert svc.service_id == "test-svc"

    def test_get_nonexistent_returns_none(self, tmp_path):
        registry = _make_registry(tmp_path)
        assert registry.get("ghost") is None


class TestRegistryListAll:
    def test_list_empty_registry(self, tmp_path):
        registry = _make_registry(tmp_path)
        assert registry.list_all() == []

    def test_list_multiple_services(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration(service_id="svc-a", port=9001))
        registry.register(_make_registration(service_id="svc-b", port=9002))
        registry.register(_make_registration(service_id="svc-c", port=9003))
        services = registry.list_all()
        assert len(services) == 3
        ids = {s.service_id for s in services}
        assert ids == {"svc-a", "svc-b", "svc-c"}


class TestRegistryHealthCheck:
    def test_health_check_unregistered_service(self, tmp_path):
        registry = _make_registry(tmp_path)
        health = registry.health_check("ghost-svc")
        assert health.status == ServiceStatus.OFFLINE
        assert "error" in health.details
        assert "not registered" in health.details["error"]

    def test_health_check_success(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration(service_id="live-svc", port=9100))

        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"status": "ok"}'
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            health = registry.health_check("live-svc")

        assert health.status == ServiceStatus.ONLINE
        assert health.latency_ms >= 0.0
        assert health.details == {"status": "ok"}

    def test_health_check_success_updates_descriptor_status(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration(service_id="live-svc", port=9100))

        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"status": "ok"}'
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            registry.health_check("live-svc")

        desc = registry.get("live-svc")
        assert desc is not None
        assert desc.status == ServiceStatus.ONLINE

    def test_health_check_timeout_marks_offline(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration(service_id="dead-svc", port=9200))

        import urllib.error

        with patch("urllib.request.urlopen", side_effect=TimeoutError("timed out")):
            health = registry.health_check("dead-svc")

        assert health.status == ServiceStatus.OFFLINE
        assert "error" in health.details

    def test_health_check_connection_refused_marks_offline(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration(service_id="refused-svc", port=9201))

        with patch(
            "urllib.request.urlopen",
            side_effect=ConnectionRefusedError("connection refused"),
        ):
            health = registry.health_check("refused-svc")

        assert health.status == ServiceStatus.OFFLINE
        desc = registry.get("refused-svc")
        assert desc is not None
        assert desc.status == ServiceStatus.OFFLINE

    def test_health_check_records_latency(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration(service_id="timed-svc", port=9300))

        mock_resp = MagicMock()
        mock_resp.read.return_value = b"{}"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            health = registry.health_check("timed-svc")

        # latency_ms is rounded to 2 decimal places and non-negative
        assert isinstance(health.latency_ms, float)
        assert health.latency_ms >= 0.0


class TestRegistryDiscover:
    def test_discover_no_services_running(self, tmp_path):
        registry = _make_registry(tmp_path)
        # All ports are closed — every probe raises ConnectionRefusedError
        with patch(
            "urllib.request.urlopen",
            side_effect=ConnectionRefusedError("refused"),
        ):
            result = registry.discover(timeout=0.1)

        assert result.discovered == []
        assert len(result.failed_ports) == len(KNOWN_PORTS)
        assert result.scan_duration_ms >= 0.0

    def test_discover_skips_already_registered(self, tmp_path):
        registry = _make_registry(tmp_path)
        # Pre-register the admin service
        registry.register(
            _make_registration(service_id="admin", service_type=ServiceType.CUSTOM, port=8787)
        )

        with patch(
            "urllib.request.urlopen",
            side_effect=ConnectionRefusedError("refused"),
        ):
            result = registry.discover(timeout=0.1)

        assert 8787 not in result.failed_ports

    def test_discover_registers_found_services(self, tmp_path):
        registry = _make_registry(tmp_path)

        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"status": "ok"}'
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        def selective_open(req, timeout=None):
            # Only "succeed" for port 8788 (llm-portal)
            url = req.full_url if hasattr(req, "full_url") else str(req)
            if ":8788/" in url:
                return mock_resp
            raise ConnectionRefusedError("refused")

        with patch("urllib.request.urlopen", side_effect=selective_open):
            result = registry.discover(timeout=0.1)

        found_ids = [d.service_id for d in result.discovered]
        assert "llm-portal" in found_ids
        assert registry.get("llm-portal") is not None


# ===========================================================================
# PERSISTENCE TESTS (5+ tests)
# ===========================================================================


class TestRegistryPersistence:
    def test_save_empty_registry_creates_file(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.save()
        persist_file = tmp_path / "registry.json"
        assert persist_file.exists()
        data = json.loads(persist_file.read_text())
        assert data == {}

    def test_save_and_load_round_trip(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration(service_id="alpha", port=9001))
        registry.register(_make_registration(service_id="beta", port=9002))

        # Load into a fresh registry from the same file
        registry2 = _make_registry(tmp_path)
        count = registry2.load()

        assert count == 2
        alpha = registry2.get("alpha")
        beta = registry2.get("beta")
        assert alpha is not None
        assert beta is not None
        assert alpha.port == 9001
        assert beta.port == 9002

    def test_load_nonexistent_file_returns_zero(self, tmp_path):
        registry = ServiceRegistry(persist_path=str(tmp_path / "does_not_exist.json"))
        count = registry.load()
        assert count == 0

    def test_load_corrupted_file_skips_invalid_entries(self, tmp_path):
        persist_file = tmp_path / "registry.json"
        # Write a JSON with one valid entry and one invalid (missing required fields)
        data = {
            "valid-svc": {
                "service_id": "valid-svc",
                "service_type": "custom",
                "name": "Valid",
                "version": "0.1.0",
                "host": "127.0.0.1",
                "port": 9000,
                "health_endpoint": "/api/health",
                "openapi_endpoint": "/openapi.json",
                "oauth3_scopes": [],
                "evidence_capture": True,
                "status": "starting",
                "registered_at": "2026-01-01T00:00:00",
                "last_health_check": "",
                "metadata": {},
            },
            "invalid-svc": {
                "bad_field": "this will fail validation",
                # missing required fields: service_id, service_type, name, port
            },
        }
        persist_file.write_text(json.dumps(data))

        registry = ServiceRegistry(persist_path=str(persist_file))
        count = registry.load()

        # Only the valid entry should be loaded; invalid one silently skipped
        assert count == 1
        assert registry.get("valid-svc") is not None
        assert registry.get("invalid-svc") is None

    def test_persist_path_directories_created(self, tmp_path):
        deep_path = str(tmp_path / "a" / "b" / "c" / "registry.json")
        registry = ServiceRegistry(persist_path=deep_path)
        registry.save()
        assert os.path.exists(deep_path)

    def test_round_trip_preserves_all_fields(self, tmp_path):
        registry = _make_registry(tmp_path)
        reg = ServiceRegistration(
            service_id="full-svc",
            service_type=ServiceType.LLM,
            name="Full Service",
            version="2.3.4",
            host="10.0.0.1",
            port=8888,
            health_endpoint="/health",
            openapi_endpoint="/api/openapi.json",
            oauth3_scopes=["llm:read", "llm:write"],
            evidence_capture=False,
            metadata={"region": "us-west-2"},
        )
        registry.register(reg)

        registry2 = _make_registry(tmp_path)
        registry2.load()
        desc = registry2.get("full-svc")

        assert desc is not None
        assert desc.service_type == ServiceType.LLM
        assert desc.version == "2.3.4"
        assert desc.host == "10.0.0.1"
        assert desc.port == 8888
        assert desc.health_endpoint == "/health"
        assert desc.openapi_endpoint == "/api/openapi.json"
        assert desc.oauth3_scopes == ["llm:read", "llm:write"]
        assert desc.evidence_capture is False
        assert desc.metadata == {"region": "us-west-2"}

    def test_deregister_persists_removal(self, tmp_path):
        registry = _make_registry(tmp_path)
        registry.register(_make_registration(service_id="temp-svc", port=9999))
        registry.deregister("temp-svc")

        registry2 = _make_registry(tmp_path)
        count = registry2.load()
        assert count == 0
        assert registry2.get("temp-svc") is None
