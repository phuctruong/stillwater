"""Cloud Bridge Service — map solaceagi.com API calls to local service endpoints.

Port: 8794
Purpose: Final piece connecting self-hosted stillwater services to the cloud platform.
Enables solaceagi.com to route requests to the user's local service mesh
and provides a registration/heartbeat protocol for cloud connectivity.

Tier enforcement:
- free: may only route to the LLM portal (service_type="llm")
- pro: may route to all registered services
- enterprise: may route to all registered services with priority
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import time
import urllib.request
import urllib.error
import json
from datetime import datetime, timezone
from typing import Any

SERVICE_ID = "cloud-bridge"
SERVICE_TYPE = "bridge"
VERSION = "0.1.0"
PORT = 8794

app = FastAPI(title="Stillwater Cloud Bridge", version=VERSION)

# ---------------------------------------------------------------------------
# In-memory state
# ---------------------------------------------------------------------------

_connection: dict | None = None          # current cloud connection record
_capabilities: dict[str, dict] = {}     # service_type → Capability dict
_route_log: list[dict] = []             # audit log of route requests

# Known service registry (service_type → default port) — used when
# capabilities have not been explicitly registered.
_DEFAULT_PORTS: dict[str, int] = {
    "admin":    8787,
    "llm":      8788,
    "recipe":   8789,
    "evidence": 8790,
    "oauth3":   8791,
    "cpu":      8792,
    "tunnel":   8793,
    "browser":  9222,
}

# Tiers that can access all services (beyond the free restriction)
_FULL_ACCESS_TIERS = {"pro", "enterprise"}

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ConnectRequest(BaseModel):
    api_key: str
    instance_id: str
    tier: str = "free"               # free | pro | enterprise
    metadata: dict = Field(default_factory=dict)

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
    endpoint: str                    # e.g. "/api/health"
    method: str = "GET"              # GET | POST | DELETE
    payload: dict | None = None
    headers: dict | None = None

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
    """Register a local service so the bridge can route to it."""
    service_id: str
    service_type: str
    port: int
    endpoints: list[str] = Field(default_factory=list)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _uptime() -> float:
    """Return uptime in seconds since connection was established, or 0."""
    if _connection is None:
        return 0.0
    return round(time.monotonic() - _connection["_start_monotonic"], 3)

def _tier_allows(tier: str, service_type: str) -> bool:
    """Return True if the given tier may route to service_type."""
    if tier in _FULL_ACCESS_TIERS:
        return True
    # free tier: only llm portal
    return service_type == "llm"

def _forward_http(url: str, method: str, payload: dict | None, extra_headers: dict | None) -> tuple[int, Any]:
    """
    Forward an HTTP request to a local service using stdlib urllib.
    Returns (status_code, parsed_body).
    Raises urllib.error.URLError on connection failure.
    """
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

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

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
    """Register this instance with solaceagi.com."""
    global _connection

    if _connection is not None:
        raise HTTPException(409, "Already connected. Disconnect first.")

    now = _now_iso()
    _connection = {
        "api_key": req.api_key,
        "instance_id": req.instance_id,
        "tier": req.tier,
        "connected_at": now,
        "last_heartbeat": now,
        "_start_monotonic": time.monotonic(),
        "metadata": req.metadata,
    }

    return {
        "ok": True,
        "instance_id": req.instance_id,
        "tier": req.tier,
        "connected_at": now,
    }

@app.post("/api/bridge/disconnect")
async def disconnect():
    """Unregister from solaceagi.com."""
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
    """Return current connection status."""
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

@app.post("/api/bridge/route", response_model=RouteResponse)
async def route(req: RouteRequest):
    """Route an incoming cloud request to a local service."""
    if _connection is None:
        raise HTTPException(403, "Not connected to cloud. Call /api/bridge/connect first.")

    tier = _connection["tier"]
    if not _tier_allows(tier, req.service_type):
        raise HTTPException(
            403,
            f"Tier '{tier}' is not allowed to route to service_type='{req.service_type}'. "
            "Upgrade to pro or enterprise.",
        )

    # Resolve capability
    cap = _capabilities.get(req.service_type)
    if cap is None:
        raise HTTPException(404, f"No registered capability for service_type='{req.service_type}'.")

    port = cap["port"]
    service_id = cap["service_id"]
    endpoint = req.endpoint if req.endpoint.startswith("/") else f"/{req.endpoint}"
    url = f"http://127.0.0.1:{port}{endpoint}"

    # Log the route attempt
    log_entry: dict[str, Any] = {
        "service_type": req.service_type,
        "endpoint": req.endpoint,
        "method": req.method,
        "url": url,
        "timestamp": _now_iso(),
    }
    _route_log.append(log_entry)

    # Forward the request
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
    """List all local services available for cloud routing."""
    return {
        "ok": True,
        "count": len(_capabilities),
        "capabilities": list(_capabilities.values()),
    }

@app.post("/api/bridge/capabilities/register")
async def register_capability(req: RegisterCapabilityRequest):
    """Register a local service so the bridge can route to it."""
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
    """Cloud sends periodic heartbeat; bridge responds with health summary."""
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
