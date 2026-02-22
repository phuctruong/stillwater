"""Service Orchestrator — thin routing layer between CLI and web services.

The orchestrator discovers services from the admin registry, routes commands
to the appropriate services, and composes multi-service results.

If admin is not running, falls back to direct execution (existing CLI behavior).
"""

import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ServiceEndpoint:
    """Describes a discovered service."""
    service_id: str
    service_type: str
    name: str
    host: str
    port: int
    status: str
    base_url: str = ""

    def __post_init__(self):
        if not self.base_url:
            self.base_url = f"http://{self.host}:{self.port}"


class ServiceOrchestrator:
    """Discovers services from admin registry, routes requests to them.

    Usage:
        orch = ServiceOrchestrator()
        if orch.is_available():
            services = orch.discover()
            result = orch.call_service("llm-portal", "/v1/chat/completions", {...})
        else:
            # Fall back to direct execution
    """

    def __init__(self, admin_url: str = "http://127.0.0.1:8787"):
        self.admin_url = admin_url
        self._services: dict[str, ServiceEndpoint] = {}
        self._available: bool | None = None  # None = not checked yet

    def is_available(self, timeout: float = 1.0) -> bool:
        """Check if admin gateway is running."""
        if self._available is not None:
            return self._available
        try:
            req = urllib.request.Request(
                f"{self.admin_url}/api/services",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                self._available = resp.status == 200
        except Exception:
            self._available = False
        return self._available

    def discover(self, timeout: float = 2.0) -> dict[str, ServiceEndpoint]:
        """Fetch all registered services from admin."""
        try:
            req = urllib.request.Request(
                f"{self.admin_url}/api/services",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
                services = data.get("services", [])
                self._services = {}
                for svc in services:
                    endpoint = ServiceEndpoint(
                        service_id=svc.get("service_id", ""),
                        service_type=svc.get("service_type", ""),
                        name=svc.get("name", ""),
                        host=svc.get("host", "127.0.0.1"),
                        port=svc.get("port", 0),
                        status=svc.get("status", "offline"),
                    )
                    self._services[endpoint.service_id] = endpoint
                self._available = True
        except Exception:
            self._available = False
        return self._services

    def get_service(self, service_id: str) -> ServiceEndpoint | None:
        """Get a specific service endpoint."""
        return self._services.get(service_id)

    def get_service_by_type(self, service_type: str) -> ServiceEndpoint | None:
        """Get the first service matching a type."""
        for svc in self._services.values():
            if svc.service_type == service_type:
                return svc
        return None

    def call_service(
        self,
        service_id: str,
        path: str,
        data: dict | None = None,
        method: str = "POST",
        timeout: float = 30.0,
    ) -> dict:
        """Call a service endpoint. Returns JSON response."""
        svc = self._services.get(service_id)
        if not svc:
            return {"ok": False, "error": f"Service {service_id} not found"}

        url = f"{svc.base_url}{path}"

        try:
            if data is not None:
                body = json.dumps(data).encode("utf-8")
                req = urllib.request.Request(
                    url, data=body,
                    headers={"Content-Type": "application/json"},
                    method=method,
                )
            else:
                req = urllib.request.Request(url, method=method)

            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            try:
                return json.loads(body)
            except Exception:
                return {"ok": False, "error": f"HTTP {e.code}: {body[:200]}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def route_intent(self, intent: str, **kwargs) -> dict:
        """Route a user intent to the correct service chain.

        Intent mapping:
        - "hash", "rung", "math" → CPU service
        - "llm", "chat", "complete" → LLM Portal
        - "recipe", "run-recipe" → Recipe Engine
        - "evidence", "capture" → Evidence Pipeline
        - "token", "scope", "consent" → OAuth3
        - "browse", "navigate", "click" → Browser
        """
        intent_lower = intent.lower()

        service_map = {
            "hash": "cpu-service",
            "rung": "cpu-service",
            "math": "cpu-service",
            "validate": "cpu-service",
            "llm": "llm-portal",
            "chat": "llm-portal",
            "complete": "llm-portal",
            "recipe": "recipe-engine",
            "run-recipe": "recipe-engine",
            "evidence": "evidence-pipeline",
            "capture": "evidence-pipeline",
            "token": "oauth3-authority",
            "scope": "oauth3-authority",
            "consent": "oauth3-authority",
            "browse": "browser",
            "navigate": "browser",
            "click": "browser",
            "screenshot": "browser",
        }

        service_id = service_map.get(intent_lower)
        if not service_id:
            return {"ok": False, "error": f"Unknown intent: {intent}", "routed": False}

        svc = self._services.get(service_id)
        if not svc:
            return {"ok": False, "error": f"Service {service_id} not available", "routed": False}

        return {
            "ok": True,
            "routed": True,
            "service_id": service_id,
            "service_type": svc.service_type,
            "base_url": svc.base_url,
            "intent": intent,
        }

    def compose_results(self, results: list[dict]) -> dict:
        """Compose results from multiple service calls into a unified response."""
        all_ok = all(r.get("ok", False) for r in results)
        errors = [r.get("error") for r in results if r.get("error")]

        return {
            "ok": all_ok,
            "results": results,
            "service_count": len(results),
            "errors": errors if errors else None,
        }

    def status(self) -> dict:
        """Get status of all discovered services."""
        return {
            "admin_available": self._available,
            "admin_url": self.admin_url,
            "service_count": len(self._services),
            "services": {
                sid: {
                    "name": svc.name,
                    "type": svc.service_type,
                    "port": svc.port,
                    "status": svc.status,
                }
                for sid, svc in self._services.items()
            },
        }
