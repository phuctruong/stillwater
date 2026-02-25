"""Cloud Bridge Service with real solaceagi.com connectivity checks.

Port: 8794
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

SERVICE_ID = "cloud-bridge"
SERVICE_TYPE = "bridge"
VERSION = "0.2.0"
PORT = 8794
DEFAULT_CLOUD_API_URL = "https://www.solaceagi.com/api/v1"

REPO_ROOT = Path(__file__).resolve().parents[2]
CLOUD_CONFIG_PATHS = (
    REPO_ROOT / "data" / "custom" / "solaceagi-config.yaml",
    REPO_ROOT / "data" / "custom" / "solace_agi_config.yaml",
    REPO_ROOT / "data" / "default" / "solace_agi_config.yaml",
)

app = FastAPI(title="Stillwater Cloud Bridge", version=VERSION)

_connection: dict[str, Any] | None = None
_capabilities: dict[str, dict[str, Any]] = {}
_route_log: list[dict[str, Any]] = []

_DEFAULT_PORTS: dict[str, int] = {
    "admin": 8787,
    "llm": 8788,
    "recipe": 8789,
    "evidence": 8790,
    "oauth3": 8791,
    "cpu": 8792,
    "tunnel": 8793,
    "browser": 9222,
}
_FULL_ACCESS_TIERS = {"pro", "enterprise"}


class ConnectRequest(BaseModel):
    api_key: str
    instance_id: str
    tier: str = "free"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConnectionStatus(BaseModel):
    connected: bool
    instance_id: str | None = None
    tier: str | None = None
    connected_at: str | None = None
    last_heartbeat: str | None = None
    uptime_seconds: float = 0.0
    services_available: int = 0


class RouteRequest(BaseModel):
    service_type: str
    endpoint: str
    method: str = "GET"
    payload: dict[str, Any] | None = None
    headers: dict[str, str] | None = None


class RouteResponse(BaseModel):
    status_code: int
    body: Any
    service_id: str
    latency_ms: float


class Capability(BaseModel):
    service_id: str
    service_type: str
    port: int
    endpoints: list[str] = Field(default_factory=list)


class RegisterCapabilityRequest(BaseModel):
    service_id: str
    service_type: str
    port: int
    endpoints: list[str] = Field(default_factory=list)


class SyncSkillsRequest(BaseModel):
    direction: str = "both"
    payload: dict[str, Any] = Field(default_factory=dict)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uptime() -> float:
    if _connection is None:
        return 0.0
    return round(time.monotonic() - _connection["_start_monotonic"], 3)


def _tier_allows(tier: str, service_type: str) -> bool:
    if tier in _FULL_ACCESS_TIERS:
        return True
    return service_type == "llm"


def _extract_yaml_bool(content: str, key: str) -> bool | None:
    pattern = rf"^\s*{re.escape(key)}\s*:\s*(true|false)\s*$"
    match = re.search(pattern, content, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    return match.group(1).lower() == "true"


def _extract_yaml_str(content: str, keys: tuple[str, ...]) -> str:
    for key in keys:
        pattern = rf'^\s*{re.escape(key)}\s*:\s*"?([^"\n#]+)"?\s*$'
        match = re.search(pattern, content, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            value = match.group(1).strip()
            if value:
                return value
    return ""


def _normalize_cloud_url(url: str) -> str:
    clean = url.strip().rstrip("/")
    if not clean:
        return DEFAULT_CLOUD_API_URL
    if clean.endswith("/api"):
        return f"{clean}/v1"
    return clean


def _load_cloud_config() -> dict[str, Any]:
    env_key = os.getenv("SOLACEAGI_API_KEY", "").strip()
    content = ""
    for path in CLOUD_CONFIG_PATHS:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if content:
                break
    enabled = _extract_yaml_bool(content, "enabled")
    if enabled is None:
        enabled = bool(env_key)
    api_key = env_key or _extract_yaml_str(content, ("api_key",))
    api_url = _extract_yaml_str(content, ("api_url", "base_url"))
    return {
        "enabled": bool(enabled),
        "api_key": api_key,
        "api_url": _normalize_cloud_url(api_url),
    }


def _request_json(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    timeout: float = 8.0,
) -> tuple[int, Any, str | None]:
    data: bytes | None = None
    req_headers = dict(headers or {})
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url=url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = {"raw": raw}
            return resp.status, body, None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"raw": raw}
        return exc.code, body, None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        message = str(exc)
        if "timed out" in message.lower() or "timeout" in message.lower():
            return 0, {}, "connection timeout to www.solaceagi.com"
        return 0, {}, f"connection error to www.solaceagi.com: {exc}"


def _cloud_request(
    method: str,
    endpoint: str,
    api_key: str,
    payload: dict[str, Any] | None = None,
    timeout: float = 8.0,
) -> tuple[int, Any, str | None]:
    cfg = _load_cloud_config()
    url = f"{_normalize_cloud_url(str(cfg.get('api_url', DEFAULT_CLOUD_API_URL)))}{endpoint}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return _request_json(url, method=method, headers=headers, payload=payload, timeout=timeout)


def _cloud_status(*, api_key_override: str | None = None, force_enabled: bool = False) -> dict[str, Any]:
    cfg = _load_cloud_config()
    api_key = api_key_override or str(cfg.get("api_key", "")).strip()
    enabled = bool(cfg.get("enabled", False)) or force_enabled

    if not enabled or not api_key:
        return {
            "status": "not_configured",
            "message": "run: PUT /api/llm/keys/solaceagi to configure",
        }

    status_code, body, error = _cloud_request("GET", "/health", api_key, payload=None)
    if error is not None:
        return {"status": "unreachable", "error": error}
    if status_code in (401, 403):
        return {"status": "auth_failed", "error": "invalid API key"}
    if status_code < 200 or status_code >= 300:
        return {"status": "error", "error": f"cloud health http {status_code}"}

    tier = "unknown"
    if isinstance(body, dict):
        maybe_tier = body.get("tier")
        if isinstance(maybe_tier, str) and maybe_tier.strip():
            tier = maybe_tier.strip()

    if tier == "unknown":
        tier_code, tier_body, tier_error = _cloud_request("GET", "/account/tier", api_key, payload=None)
        if tier_error is None and tier_code == 200 and isinstance(tier_body, dict):
            maybe_tier = tier_body.get("tier")
            if isinstance(maybe_tier, str) and maybe_tier.strip():
                tier = maybe_tier.strip()

    return {
        "status": "ok",
        "tier": tier,
        "api_url": cfg.get("api_url", DEFAULT_CLOUD_API_URL),
    }


def _forward_http(url: str, method: str, payload: dict | None, extra_headers: dict | None) -> tuple[int, Any]:
    data: bytes | None = None
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    if payload is not None:
        data = json.dumps(payload).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()
            try:
                body = json.loads(raw)
            except ValueError:
                body = raw.decode(errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            body = json.loads(raw)
        except ValueError:
            body = raw.decode(errors="replace")
        return exc.code, body


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service_id": SERVICE_ID,
        "service_type": SERVICE_TYPE,
        "version": VERSION,
        "connected": _connection is not None,
        "connected_services": len(_capabilities),
    }


@app.get("/api/health/cloud")
async def cloud_health():
    status = _cloud_status()
    return {"ok": status.get("status") == "ok", "cloud": status}


@app.get("/api/service-info")
async def service_info():
    return {
        "service_id": SERVICE_ID,
        "service_type": SERVICE_TYPE,
        "name": "Cloud Bridge",
        "version": VERSION,
        "port": PORT,
    }


@app.post("/api/bridge/connect")
async def connect(req: ConnectRequest):
    global _connection

    if _connection is not None:
        raise HTTPException(409, "Already connected. Disconnect first.")
    if not req.api_key.strip():
        raise HTTPException(400, "api_key is required")

    cloud = _cloud_status(api_key_override=req.api_key.strip(), force_enabled=True)
    cloud_status = cloud.get("status")
    if cloud_status == "auth_failed":
        raise HTTPException(401, cloud.get("error", "invalid API key"))
    if cloud_status != "ok":
        raise HTTPException(503, cloud)

    now = _now_iso()
    _connection = {
        "api_key": req.api_key.strip(),
        "instance_id": req.instance_id,
        "tier": str(cloud.get("tier", req.tier)),
        "connected_at": now,
        "last_heartbeat": now,
        "_start_monotonic": time.monotonic(),
        "metadata": req.metadata,
    }

    return {
        "ok": True,
        "instance_id": req.instance_id,
        "tier": _connection["tier"],
        "connected_at": now,
    }


@app.post("/api/bridge/disconnect")
async def disconnect():
    global _connection

    if _connection is None:
        raise HTTPException(400, "Not connected.")

    instance_id = _connection["instance_id"]
    uptime = _uptime()
    _connection = None

    return {
        "ok": True,
        "instance_id": instance_id,
        "uptime_seconds": uptime,
    }


@app.get("/api/bridge/status", response_model=ConnectionStatus)
async def bridge_status():
    if _connection is None:
        return ConnectionStatus(connected=False)

    return ConnectionStatus(
        connected=True,
        instance_id=_connection["instance_id"],
        tier=_connection["tier"],
        connected_at=_connection["connected_at"],
        last_heartbeat=_connection["last_heartbeat"],
        uptime_seconds=_uptime(),
        services_available=len(_capabilities),
    )


@app.post("/api/bridge/sync/skills")
async def sync_skills(req: SyncSkillsRequest):
    if _connection is None:
        raise HTTPException(403, "Not connected to cloud. Call /api/bridge/connect first.")

    direction = req.direction.strip().lower() or "both"
    if direction not in {"up", "down", "both"}:
        raise HTTPException(400, "direction must be one of: up, down, both")

    status_code, body, error = _cloud_request(
        "POST",
        "/sync/skills",
        _connection["api_key"],
        payload={"direction": direction, **req.payload},
    )
    if error is not None:
        return {"ok": False, "status": "unreachable", "error": error}
    if status_code in (401, 403):
        return {"ok": False, "status": "auth_failed", "error": "invalid API key"}
    if status_code < 200 or status_code >= 300:
        return {
            "ok": False,
            "status": "error",
            "error": f"cloud sync http {status_code}",
            "response": body,
        }
    return {"ok": True, "status": "ok", "direction": direction, "response": body}


@app.post("/api/bridge/route", response_model=RouteResponse)
async def route(req: RouteRequest):
    if _connection is None:
        raise HTTPException(403, "Not connected to cloud. Call /api/bridge/connect first.")

    tier = _connection["tier"]
    if not _tier_allows(tier, req.service_type):
        raise HTTPException(
            403,
            f"Tier '{tier}' is not allowed to route to service_type='{req.service_type}'. Upgrade to pro or enterprise.",
        )

    cap = _capabilities.get(req.service_type)
    if cap is None:
        default_port = _DEFAULT_PORTS.get(req.service_type)
        if default_port is None:
            raise HTTPException(404, f"No registered capability for service_type='{req.service_type}'.")
        cap = {
            "service_id": f"{req.service_type}-service",
            "service_type": req.service_type,
            "port": default_port,
            "endpoints": [],
        }

    port = cap["port"]
    service_id = cap["service_id"]
    endpoint = req.endpoint if req.endpoint.startswith("/") else f"/{req.endpoint}"
    url = f"http://127.0.0.1:{port}{endpoint}"

    log_entry: dict[str, Any] = {
        "service_type": req.service_type,
        "endpoint": req.endpoint,
        "method": req.method,
        "url": url,
        "timestamp": _now_iso(),
    }
    _route_log.append(log_entry)

    t0 = time.monotonic()
    try:
        status_code, body = _forward_http(url, req.method, req.payload, req.headers)
    except Exception as exc:
        latency_ms = round((time.monotonic() - t0) * 1000, 2)
        log_entry["status_code"] = 502
        log_entry["latency_ms"] = latency_ms
        raise HTTPException(502, f"Failed to reach local service '{service_id}' at {url}: {exc}")

    latency_ms = round((time.monotonic() - t0) * 1000, 2)
    log_entry["status_code"] = status_code
    log_entry["latency_ms"] = latency_ms

    return RouteResponse(
        status_code=status_code,
        body=body,
        service_id=service_id,
        latency_ms=latency_ms,
    )


@app.get("/api/bridge/capabilities")
async def list_capabilities():
    return {
        "ok": True,
        "count": len(_capabilities),
        "capabilities": list(_capabilities.values()),
    }


@app.post("/api/bridge/capabilities/register")
async def register_capability(req: RegisterCapabilityRequest):
    cap = Capability(
        service_id=req.service_id,
        service_type=req.service_type,
        port=req.port,
        endpoints=req.endpoints,
    )
    _capabilities[req.service_type] = cap.model_dump()
    return {"ok": True, "registered": cap.model_dump()}


@app.post("/api/bridge/heartbeat")
async def heartbeat():
    if _connection is None:
        raise HTTPException(400, "Not connected. Cannot process heartbeat.")

    now = _now_iso()
    _connection["last_heartbeat"] = now

    return {
        "ok": True,
        "instance_id": _connection["instance_id"],
        "tier": _connection["tier"],
        "last_heartbeat": now,
        "uptime_seconds": _uptime(),
        "services_available": len(_capabilities),
        "health": "ok",
    }
