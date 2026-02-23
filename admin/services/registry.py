"""Service Registry — central registration, health checking, and persistence."""

import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

from .models import (
    ServiceDescriptor,
    ServiceHealth,
    ServiceStatus,
    ServiceRegistration,
    ServiceDiscoveryResult,
    ServiceType,
)

# Known service ports for auto-discovery
KNOWN_PORTS: dict[int, tuple[str, ServiceType, str]] = {
    8787: ("admin", ServiceType.CUSTOM, "Stillwater Admin"),
    8788: ("llm-portal", ServiceType.LLM, "LLM Portal"),
    8789: ("recipe-engine", ServiceType.RECIPE, "Recipe Engine"),
    8790: ("evidence-pipeline", ServiceType.EVIDENCE, "Evidence Pipeline"),
    8791: ("oauth3-authority", ServiceType.OAUTH3, "OAuth3 Authority"),
    8792: ("cpu-service", ServiceType.CPU, "CPU Service"),
    9222: ("browser", ServiceType.BROWSER, "Solace Browser"),
}


class ServiceRegistry:
    def __init__(self, persist_path: str | None = None):
        self._services: dict[str, ServiceDescriptor] = {}
        self._persist_path = persist_path or str(
            Path.home() / ".stillwater" / "service_registry.json"
        )

    def register(self, registration: ServiceRegistration) -> ServiceDescriptor:
        """Register a new service. Returns the created descriptor.

        If a service with the same service_id already exists it is overwritten.
        """
        descriptor = ServiceDescriptor(
            service_id=registration.service_id,
            service_type=registration.service_type,
            name=registration.name,
            version=registration.version,
            host=registration.host,
            port=registration.port,
            health_endpoint=registration.health_endpoint,
            openapi_endpoint=registration.openapi_endpoint,
            oauth3_scopes=registration.oauth3_scopes,
            evidence_capture=registration.evidence_capture,
            metadata=registration.metadata,
            status=ServiceStatus.STARTING,
        )
        self._services[registration.service_id] = descriptor
        self.save()
        return descriptor

    def deregister(self, service_id: str) -> bool:
        """Remove a service from the registry. Returns True if it existed."""
        if service_id in self._services:
            del self._services[service_id]
            self.save()
            return True
        return False

    def get(self, service_id: str) -> ServiceDescriptor | None:
        """Return a registered service by ID, or None if not found."""
        return self._services.get(service_id)

    def list_all(self) -> list[ServiceDescriptor]:
        """Return all registered services."""
        return list(self._services.values())

    def health_check(self, service_id: str, timeout: float = 2.0) -> ServiceHealth:
        """Probe a service's health endpoint and update its status in the registry."""
        descriptor = self._services.get(service_id)
        if not descriptor:
            return ServiceHealth(
                service_id=service_id,
                status=ServiceStatus.OFFLINE,
                details={"error": "Service not registered"},
            )

        start = time.monotonic()
        try:
            req = urllib.request.Request(descriptor.health_url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                latency = (time.monotonic() - start) * 1000
                body = json.loads(resp.read().decode())
                new_status = ServiceStatus.ONLINE
                descriptor.status = new_status
                health = ServiceHealth(
                    service_id=service_id,
                    status=new_status,
                    latency_ms=round(latency, 2),
                    details=body,
                )
                descriptor.last_health_check = health.last_check
                return health
        except urllib.error.HTTPError as exc:
            latency = (time.monotonic() - start) * 1000
            # Service responded but with an error status code (e.g. 5xx) → DEGRADED
            new_status = ServiceStatus.DEGRADED if exc.code >= 500 else ServiceStatus.OFFLINE
            descriptor.status = new_status
            return ServiceHealth(
                service_id=service_id,
                status=new_status,
                latency_ms=round(latency, 2),
                details={"error": str(exc), "http_status": exc.code},
            )
        except Exception as exc:
            latency = (time.monotonic() - start) * 1000
            descriptor.status = ServiceStatus.OFFLINE
            return ServiceHealth(
                service_id=service_id,
                status=ServiceStatus.OFFLINE,
                latency_ms=round(latency, 2),
                details={"error": str(exc)},
            )

    def discover(self, timeout: float = 1.0) -> ServiceDiscoveryResult:
        """Auto-discover services on known ports.

        Ports that are already registered are skipped. Newly found services
        are registered with ONLINE status.
        """
        discovered: list[ServiceDescriptor] = []
        failed_ports: list[int] = []
        start = time.monotonic()

        for port, (sid, stype, name) in KNOWN_PORTS.items():
            if sid in self._services:
                continue  # Already registered — skip
            url = f"http://127.0.0.1:{port}/api/health"
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=timeout) as _resp:
                    reg = ServiceRegistration(
                        service_id=sid,
                        service_type=stype,
                        name=name,
                        port=port,
                    )
                    desc = self.register(reg)
                    desc.status = ServiceStatus.ONLINE
                    self.save()
                    discovered.append(desc)
            except Exception:
                failed_ports.append(port)

        duration = (time.monotonic() - start) * 1000
        return ServiceDiscoveryResult(
            discovered=discovered,
            failed_ports=failed_ports,
            scan_duration_ms=round(duration, 2),
        )

    def save(self) -> None:
        """Persist the registry to a JSON file, creating directories as needed."""
        os.makedirs(os.path.dirname(self._persist_path), exist_ok=True)
        data = {sid: desc.model_dump() for sid, desc in self._services.items()}
        with open(self._persist_path, "w") as fh:
            json.dump(data, fh, indent=2, default=str)

    def load(self) -> int:
        """Load the registry from a JSON file.

        Returns the number of services successfully loaded.
        Invalid entries are silently skipped.
        """
        if not os.path.exists(self._persist_path):
            return 0
        with open(self._persist_path) as fh:
            data = json.load(fh)
        count = 0
        for sid, desc_data in data.items():
            try:
                self._services[sid] = ServiceDescriptor(**desc_data)
                count += 1
            except Exception:
                pass  # Skip invalid / corrupted entries
        return count
