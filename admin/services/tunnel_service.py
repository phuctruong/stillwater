"""Tunnel Service — expose registered services for remote access.

Purpose: Any service in the mesh can be tunneled for external access.
This enables:
- solaceagi.com connecting to user's local services
- Self-hosters exposing services to their own infrastructure
- Browser-to-admin communication across networks
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import hashlib
import json
import time
import urllib.request
from datetime import datetime
from typing import Any

SERVICE_ID = "tunnel-service"
SERVICE_TYPE = "tunnel"
VERSION = "0.1.0"
PORT = 8793

app = FastAPI(title="Stillwater Tunnel Service", version=VERSION)

# Active tunnels
_tunnels: dict[str, dict] = {}

class TunnelRequest(BaseModel):
    service_id: str
    service_port: int
    tunnel_type: str = "wss"  # wss (WebSocket Secure) or https
    target_host: str = "tunnel.solaceagi.com"
    oauth3_token: str | None = None
    metadata: dict = Field(default_factory=dict)

class TunnelStatus(BaseModel):
    tunnel_id: str
    service_id: str
    service_port: int
    tunnel_type: str
    target_host: str
    status: str  # active, connecting, disconnected, error
    created_at: str
    tunnel_url: str | None = None
    bytes_transferred: int = 0
    uptime_seconds: float = 0.0

class TunnelStopRequest(BaseModel):
    tunnel_id: str

# --- Helpers ---

def _generate_tunnel_id(service_id: str) -> str:
    ts = datetime.utcnow().isoformat()
    return hashlib.sha256(f"{service_id}:{ts}".encode()).hexdigest()[:16]

# --- Endpoints ---

@app.get("/api/health")
async def health():
    active = sum(1 for t in _tunnels.values() if t.get("status") == "active")
    return {
        "status": "ok",
        "service_id": SERVICE_ID,
        "service_type": SERVICE_TYPE,
        "version": VERSION,
        "active_tunnels": active,
        "total_tunnels": len(_tunnels),
    }

@app.get("/api/service-info")
async def service_info():
    return {
        "service_id": SERVICE_ID,
        "service_type": SERVICE_TYPE,
        "name": "Tunnel Service",
        "version": VERSION,
        "port": PORT,
    }

@app.post("/api/tunnel/start", response_model=TunnelStatus)
async def start_tunnel(req: TunnelRequest):
    # Check if service is already tunneled
    for tid, t in _tunnels.items():
        if t.get("service_id") == req.service_id and t.get("status") == "active":
            raise HTTPException(409, f"Service {req.service_id} already has an active tunnel")

    tunnel_id = _generate_tunnel_id(req.service_id)
    now = datetime.utcnow().isoformat()

    # In production, this would open a WebSocket to target_host
    # For now, create the tunnel record
    tunnel_url = f"{req.tunnel_type}://{req.target_host}/{tunnel_id}"

    tunnel_data = {
        "tunnel_id": tunnel_id,
        "service_id": req.service_id,
        "service_port": req.service_port,
        "tunnel_type": req.tunnel_type,
        "target_host": req.target_host,
        "status": "active",
        "created_at": now,
        "tunnel_url": tunnel_url,
        "bytes_transferred": 0,
        "start_time": time.monotonic(),
        "oauth3_token": req.oauth3_token,
        "metadata": req.metadata,
    }
    _tunnels[tunnel_id] = tunnel_data

    return TunnelStatus(
        tunnel_id=tunnel_id,
        service_id=req.service_id,
        service_port=req.service_port,
        tunnel_type=req.tunnel_type,
        target_host=req.target_host,
        status="active",
        created_at=now,
        tunnel_url=tunnel_url,
    )

@app.post("/api/tunnel/stop")
async def stop_tunnel(req: TunnelStopRequest):
    tunnel = _tunnels.get(req.tunnel_id)
    if not tunnel:
        raise HTTPException(404, f"Tunnel {req.tunnel_id} not found")

    tunnel["status"] = "disconnected"
    uptime = time.monotonic() - tunnel.get("start_time", time.monotonic())

    return {
        "ok": True,
        "tunnel_id": req.tunnel_id,
        "status": "disconnected",
        "uptime_seconds": round(uptime, 2),
    }

@app.get("/api/tunnel/status")
async def tunnel_status():
    statuses = []
    for tid, t in _tunnels.items():
        uptime = 0.0
        if t.get("status") == "active" and "start_time" in t:
            uptime = time.monotonic() - t["start_time"]
        statuses.append(TunnelStatus(
            tunnel_id=t["tunnel_id"],
            service_id=t["service_id"],
            service_port=t["service_port"],
            tunnel_type=t["tunnel_type"],
            target_host=t["target_host"],
            status=t["status"],
            created_at=t["created_at"],
            tunnel_url=t.get("tunnel_url"),
            bytes_transferred=t.get("bytes_transferred", 0),
            uptime_seconds=round(uptime, 2),
        ))
    return {"ok": True, "tunnels": [s.model_dump() for s in statuses]}

@app.get("/api/tunnel/services")
async def tunneled_services():
    """List which services are currently tunneled."""
    active = [
        {"service_id": t["service_id"], "tunnel_id": t["tunnel_id"], "tunnel_url": t.get("tunnel_url")}
        for t in _tunnels.values()
        if t.get("status") == "active"
    ]
    return {"ok": True, "tunneled_services": active}
