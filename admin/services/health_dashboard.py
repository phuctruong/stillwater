"""Health Dashboard service for system-wide status and probes."""

from __future__ import annotations

import json
import os
import re
import shutil
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from .base import StillwaterService
from .key_manager import KeyManager

SERVICE_ID = "health-dashboard"
SERVICE_TYPE = "observability"
VERSION = "0.1.0"
PORT = 8797

SERVICE_PORTS: dict[str, int] = {
    "admin": 8787,
    "llm-portal": 8788,
    "recipe-engine": 8789,
    "evidence-pipeline": 8790,
    "oauth3-service": 8791,
    "cpu-service": 8792,
    "tunnel-service": 8793,
    "cloud-bridge": 8794,
    "orchestration-service": 8795,
    "swarm-service": 8796,
    "health-dashboard": PORT,
}

KEY_PROVIDER_URLS: dict[str, str] = {
    "anthropic": "https://api.anthropic.com/v1/models",
    "openai": "https://api.openai.com/v1/models",
    "together": "https://api.together.xyz/v1/models",
    "openrouter": "https://openrouter.ai/api/v1/models",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models",
}


class HealthDashboardService(StillwaterService):
    """Unified health API across services, providers, keys, cloud, and OAuth3."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)
        self.key_manager = KeyManager(self.repo_root)
        self._last_key_checks: dict[str, dict[str, Any]] = {}
        super().__init__(
            service_id=SERVICE_ID,
            service_type=SERVICE_TYPE,
            name="Health Dashboard",
            version=VERSION,
            port=PORT,
            oauth3_scopes=["health.read"],
            evidence_capture=True,
        )

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _request_json(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        timeout: float = 2.0,
    ) -> tuple[int, Any, float, str | None]:
        data: bytes | None = None
        req_headers = dict(headers or {})
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            req_headers.setdefault("Content-Type", "application/json")
        req = urllib.request.Request(url=url, data=data, headers=req_headers, method=method)
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                latency_ms = round((time.monotonic() - t0) * 1000, 2)
                raw = resp.read().decode("utf-8", errors="replace")
                try:
                    body = json.loads(raw)
                except json.JSONDecodeError:
                    body = raw
                return resp.status, body, latency_ms, None
        except urllib.error.HTTPError as exc:
            latency_ms = round((time.monotonic() - t0) * 1000, 2)
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = raw
            return exc.code, body, latency_ms, None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            latency_ms = round((time.monotonic() - t0) * 1000, 2)
            return 0, None, latency_ms, str(exc)

    def _probe_service(self, service_id: str, port: int) -> dict[str, Any]:
        if service_id == self.service_id:
            return {"port": port, "status": "ok", "latency_ms": 0.0}
        status_code, body, latency_ms, error = self._request_json(
            f"http://127.0.0.1:{port}/api/health",
            timeout=2.0,
        )
        if error is not None:
            return {"port": port, "status": "down", "latency_ms": latency_ms, "error": error}
        if status_code == 200 and isinstance(body, dict) and body.get("status") == "ok":
            return {"port": port, "status": "ok", "latency_ms": latency_ms}
        return {
            "port": port,
            "status": "error",
            "latency_ms": latency_ms,
            "http_status": status_code,
            "error": f"unexpected health response from {service_id}",
        }

    def _services_status(self) -> dict[str, Any]:
        services: dict[str, Any] = {}
        for service_id, port in SERVICE_PORTS.items():
            services[service_id] = self._probe_service(service_id, port)
        ok_count = sum(1 for entry in services.values() if entry.get("status") == "ok")
        return {"services": services, "ok_count": ok_count, "total": len(services)}

    @staticmethod
    def _which_claude() -> str:
        return shutil.which("claude") or shutil.which("claude-code") or ""

    def _provider_key(self, provider: str) -> tuple[str, str]:
        if provider == "gemini":
            env_key = os.getenv("GEMINI_API_KEY", "").strip()
            if env_key:
                return env_key, "env"
            cfg = self.key_manager.load_config()
            file_key = str(cfg.get("providers", {}).get("gemini", {}).get("api_key", "")).strip()
            return file_key, "file" if file_key else "none"
        return self.key_manager.get_provider_key(provider)

    def _validate_provider_key(self, provider: str, key: str) -> tuple[bool, str, str | None]:
        url = KEY_PROVIDER_URLS[provider]
        if provider == "gemini":
            url = f"{url}?key={key}"
            headers = {"Content-Type": "application/json"}
        elif provider == "anthropic":
            headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
        else:
            headers = {"Authorization": f"Bearer {key}"}
        status_code, _, _, error = self._request_json(url, headers=headers, timeout=5.0)
        if error is not None:
            return False, "error", error
        if 200 <= status_code < 300:
            return True, "ok", None
        if status_code in (401, 403):
            return False, "auth_failed", f"http {status_code}"
        return False, "error", f"http {status_code}"

    def _llm_status(self) -> dict[str, Any]:
        cfg = self.key_manager.load_config()
        default_provider = str(cfg.get("default_provider", "claude-code"))
        providers: dict[str, Any] = {}

        claude_path = self._which_claude()
        providers["claude-code"] = {
            "available": bool(claude_path),
            "cli_path": claude_path,
            "status": "ok" if claude_path else "not_configured",
        }

        for provider in ("anthropic", "openai", "gemini", "together", "openrouter"):
            key, source = self._provider_key(provider)
            entry: dict[str, Any] = {
                "available": False,
                "has_key": bool(key),
                "source": source,
                "status": "not_configured",
            }
            if key:
                valid, status, error = self._validate_provider_key(provider, key)
                entry["available"] = valid
                entry["key_valid"] = valid
                entry["status"] = status
                if error:
                    entry["error"] = error
                self._last_key_checks[provider] = {
                    "valid": valid,
                    "status": status,
                    "error": error,
                    "last_tested": self._now_iso(),
                }
            providers[provider] = entry

        return {"default_provider": default_provider, "providers": providers}

    def _keys_status(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for provider in ("anthropic", "openai", "gemini", "together", "openrouter"):
            key, source = self._provider_key(provider)
            last = self._last_key_checks.get(provider, {})
            data[provider] = {
                "has_key": bool(key),
                "source": source,
                "valid": last.get("valid"),
                "status": last.get("status", "not_tested"),
                "last_tested": last.get("last_tested"),
                "error": last.get("error"),
            }
        return {"providers": data}

    @staticmethod
    def _extract_yaml_bool(content: str, key: str) -> bool | None:
        pattern = rf"^\s*{re.escape(key)}\s*:\s*(true|false)\s*$"
        match = re.search(pattern, content, flags=re.IGNORECASE | re.MULTILINE)
        if not match:
            return None
        return match.group(1).lower() == "true"

    @staticmethod
    def _extract_yaml_str(content: str, keys: tuple[str, ...]) -> str:
        for key in keys:
            pattern = rf'^\s*{re.escape(key)}\s*:\s*"?([^"\n#]+)"?\s*$'
            match = re.search(pattern, content, flags=re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                if value:
                    return value
        return ""

    def _load_cloud_config(self) -> dict[str, Any]:
        env_key = os.getenv("SOLACEAGI_API_KEY", "").strip()
        candidates = [
            self.repo_root / "data" / "custom" / "solaceagi-config.yaml",
            self.repo_root / "data" / "custom" / "solace_agi_config.yaml",
            self.repo_root / "data" / "default" / "solace_agi_config.yaml",
        ]
        content = ""
        for path in candidates:
            if path.exists():
                content = path.read_text(encoding="utf-8")
                if content:
                    break
        enabled = self._extract_yaml_bool(content, "enabled")
        if enabled is None:
            enabled = False
        api_key = env_key or self._extract_yaml_str(content, ("api_key",))
        api_url = self._extract_yaml_str(content, ("api_url", "base_url")) or "https://solaceagi.com/api"
        return {"enabled": enabled, "api_key": api_key, "api_url": api_url}

    def _cloud_status(self) -> dict[str, Any]:
        cfg = self._load_cloud_config()
        if not cfg["enabled"] or not cfg["api_key"]:
            return {
                "solaceagi_configured": False,
                "solaceagi_reachable": False,
                "tier": "free",
                "sync_status": "not_configured",
                "status": "not_configured",
            }

        headers = {"Authorization": f"Bearer {cfg['api_key']}"}
        status_code, body, latency_ms, error = self._request_json(
            "https://solaceagi.com/api/health",
            headers=headers,
            timeout=5.0,
        )
        if error is not None:
            return {
                "solaceagi_configured": True,
                "solaceagi_reachable": False,
                "tier": "unknown",
                "sync_status": "unreachable",
                "status": "unreachable",
                "error": error,
            }
        if status_code not in (200, 401, 403):
            return {
                "solaceagi_configured": True,
                "solaceagi_reachable": False,
                "tier": "unknown",
                "sync_status": "error",
                "status": "error",
                "error": f"http {status_code}",
            }
        if status_code in (401, 403):
            return {
                "solaceagi_configured": True,
                "solaceagi_reachable": True,
                "tier": "unknown",
                "sync_status": "auth_failed",
                "status": "auth_failed",
                "latency_ms": latency_ms,
            }

        tier_code, tier_body, _, tier_error = self._request_json(
            "https://solaceagi.com/api/v1/account/tier",
            headers=headers,
            timeout=5.0,
        )
        tier = "unknown"
        if tier_error is None and tier_code == 200 and isinstance(tier_body, dict):
            tier = str(tier_body.get("tier", "unknown"))
        if isinstance(body, dict):
            tier = str(body.get("tier", tier))
        return {
            "solaceagi_configured": True,
            "solaceagi_reachable": True,
            "tier": tier,
            "sync_status": "ok",
            "status": "ok",
            "latency_ms": latency_ms,
        }

    def _oauth3_status(self) -> dict[str, Any]:
        status_code, body, _, error = self._request_json(
            "http://127.0.0.1:8791/api/health",
            timeout=2.0,
        )
        if error is not None or status_code != 200 or not isinstance(body, dict):
            return {"active_tokens": 0, "scope_gates": "not_configured", "status": "down", "error": error}

        token_count = int(body.get("token_count", 0))
        scope_code, scope_body, _, scope_error = self._request_json(
            "http://127.0.0.1:8791/oauth3/scopes",
            timeout=2.0,
        )
        if scope_error is None and scope_code == 200 and isinstance(scope_body, dict) and scope_body.get("ok") is True:
            return {
                "active_tokens": token_count,
                "scope_gates": "configured",
                "scope_count": int(scope_body.get("count", 0)),
                "status": "ok",
            }
        return {
            "active_tokens": token_count,
            "scope_gates": "error",
            "status": "degraded",
            "error": scope_error or f"http {scope_code}",
        }

    @staticmethod
    def _overall_status(services: dict[str, Any]) -> str:
        entries = list(services.values())
        ok_count = sum(1 for entry in entries if entry.get("status") == "ok")
        if ok_count == 0:
            return "down"
        if ok_count == len(entries):
            return "healthy"
        return "degraded"

    def _full_status(self) -> dict[str, Any]:
        services_payload = self._services_status()
        llm = self._llm_status()
        cloud = self._cloud_status()
        oauth3 = self._oauth3_status()
        return {
            "status": self._overall_status(services_payload["services"]),
            "timestamp": self._now_iso(),
            "services": services_payload["services"],
            "llm": llm,
            "cloud": cloud,
            "oauth3": oauth3,
        }

    def health(self) -> dict:
        full = self._full_status()
        return {"overall": full["status"], "services_up": sum(1 for s in full["services"].values() if s["status"] == "ok")}

    def register_routes(self, app: FastAPI) -> None:
        @app.get("/api/health/full")
        async def full_health() -> dict[str, Any]:
            return self._full_status()

        @app.get("/api/health/llm")
        async def llm_health() -> dict[str, Any]:
            return self._llm_status()

        @app.get("/api/health/keys")
        async def keys_health() -> dict[str, Any]:
            # Refresh key checks by performing current provider validations.
            self._llm_status()
            return self._keys_status()

        @app.get("/api/health/cloud")
        async def cloud_health() -> dict[str, Any]:
            return self._cloud_status()

        @app.get("/api/health/oauth3")
        async def oauth3_health() -> dict[str, Any]:
            return self._oauth3_status()

        @app.get("/api/health/services")
        async def services_health() -> dict[str, Any]:
            return self._services_status()


def create_service(repo_root: Path | None = None) -> HealthDashboardService:
    root = repo_root or Path(__file__).resolve().parents[2]
    return HealthDashboardService(root)


service = create_service()
app = service.create_app()
