"""OAuth3 Authority Service — token management, scope enforcement, consent tracking.

Port: 8791
Purpose: Issue/revoke agency tokens, enforce ScopeGate G1-G4, record consent.
In-memory storage with optional JSON persistence.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import uuid

SERVICE_ID = "oauth3-service"
SERVICE_TYPE = "oauth3"
VERSION = "0.1.0"
PORT = 8791

app = FastAPI(title="Stillwater OAuth3 Authority Service", version=VERSION)

# --- In-memory stores ---

_tokens: dict[str, dict] = {}
_consent_log: list[dict] = []

# Default scope registry
_scopes: dict[str, dict] = {
    "browser.navigate": {
        "id": "browser.navigate",
        "description": "Navigate browser to URLs",
        "risk": "low",
    },
    "browser.act": {
        "id": "browser.act",
        "description": "Perform click/type actions in browser",
        "risk": "medium",
    },
    "browser.read": {
        "id": "browser.read",
        "description": "Read DOM content from browser",
        "risk": "low",
    },
    "store.read": {
        "id": "store.read",
        "description": "Read from the skill store",
        "risk": "low",
    },
    "store.write": {
        "id": "store.write",
        "description": "Write to the skill store",
        "risk": "medium",
    },
    "store.publish": {
        "id": "store.publish",
        "description": "Publish skills to the store",
        "risk": "high",
    },
    "vault.read": {
        "id": "vault.read",
        "description": "Read from the OAuth3 vault",
        "risk": "high",
    },
    "vault.write": {
        "id": "vault.write",
        "description": "Write tokens to the OAuth3 vault",
        "risk": "high",
    },
}

# --- Models ---

class AgencyToken(BaseModel):
    token_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    principal_id: str  # User who authorized
    agent_id: str  # Agent performing action
    scopes: list[str]  # e.g. ["browser.navigate", "browser.act"]
    issued_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: str  # ISO 8601
    revoked: bool = False
    revoked_at: str | None = None
    metadata: dict = Field(default_factory=dict)

class TokenIssueRequest(BaseModel):
    principal_id: str
    agent_id: str
    scopes: list[str]
    expires_at: str
    metadata: dict = Field(default_factory=dict)

class RevokeResponse(BaseModel):
    ok: bool
    token_id: str
    revoked_at: str

class ScopeCheckRequest(BaseModel):
    token_id: str
    required_scopes: list[str]
    action_risk: str = "low"  # low, medium, high

class ScopeCheckResult(BaseModel):
    allowed: bool
    gate_results: dict  # {g1: bool, g2: bool, g3: bool, g4: bool}
    reason: str | None = None
    step_up_required: bool = False

class ConsentRequest(BaseModel):
    token_id: str
    principal_id: str
    agent_id: str
    action: str
    scopes_requested: list[str]
    decision: str  # "granted" | "denied"
    metadata: dict = Field(default_factory=dict)

class ConsentRecord(BaseModel):
    consent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token_id: str
    principal_id: str
    agent_id: str
    action: str
    scopes_requested: list[str]
    decision: str
    recorded_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict = Field(default_factory=dict)

# --- Helpers ---

def _is_expired(token: dict) -> bool:
    """Return True if the token's expires_at is in the past."""
    try:
        expires = datetime.fromisoformat(token["expires_at"])
        # Make timezone-aware if naive
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expires
    except (ValueError, KeyError):
        return True  # Fail closed: treat invalid expiry as expired

def _scope_sufficient(token_scopes: list[str], required_scopes: list[str]) -> bool:
    """Return True if all required scopes are present in token scopes."""
    return all(s in token_scopes for s in required_scopes)

def _action_is_destructive(action_risk: str) -> bool:
    """Return True if action risk level triggers step-up auth."""
    return action_risk == "high"

# --- Endpoints ---

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service_id": SERVICE_ID,
        "service_type": SERVICE_TYPE,
        "version": VERSION,
        "token_count": len(_tokens),
    }

@app.get("/api/service-info")
async def service_info():
    return {
        "service_id": SERVICE_ID,
        "service_type": SERVICE_TYPE,
        "name": "OAuth3 Authority Service",
        "version": VERSION,
        "port": PORT,
    }

# --- Token CRUD ---

@app.post("/oauth3/tokens", response_model=AgencyToken, status_code=201)
async def issue_token(req: TokenIssueRequest):
    """Issue a new agency token."""
    token = AgencyToken(
        principal_id=req.principal_id,
        agent_id=req.agent_id,
        scopes=req.scopes,
        expires_at=req.expires_at,
        metadata=req.metadata,
    )
    _tokens[token.token_id] = token.model_dump()
    return token

@app.get("/oauth3/tokens/{token_id}", response_model=AgencyToken)
async def get_token(token_id: str):
    """Retrieve a token by ID."""
    if token_id not in _tokens:
        raise HTTPException(status_code=404, detail=f"Token {token_id} not found")
    return AgencyToken(**_tokens[token_id])

@app.delete("/oauth3/tokens/{token_id}", response_model=RevokeResponse)
async def revoke_token(token_id: str):
    """Revoke a token. Idempotent — revoking an already-revoked token succeeds."""
    if token_id not in _tokens:
        raise HTTPException(status_code=404, detail=f"Token {token_id} not found")

    now = datetime.now(timezone.utc).isoformat()
    token = _tokens[token_id]

    if not token.get("revoked"):
        token["revoked"] = True
        token["revoked_at"] = now

    return RevokeResponse(ok=True, token_id=token_id, revoked_at=token["revoked_at"])

# --- Scope Registry ---

@app.get("/oauth3/scopes")
async def list_scopes():
    """List all registered scopes."""
    return {
        "ok": True,
        "count": len(_scopes),
        "scopes": list(_scopes.values()),
    }

# --- ScopeGate Enforcement ---

@app.post("/oauth3/enforce", response_model=ScopeCheckResult)
async def enforce_scope(req: ScopeCheckRequest):
    """
    Run ScopeGate G1-G4 check.

    G1: Token exists and is not revoked.
    G2: Token is not expired.
    G3: Token scopes are sufficient for the required scopes.
    G4: If action_risk == "high", step-up auth is required.
    """
    gate_results = {"g1": False, "g2": False, "g3": False, "g4": False}

    # G1: Token exists and not revoked
    token_data = _tokens.get(req.token_id)
    if token_data is None:
        return ScopeCheckResult(
            allowed=False,
            gate_results=gate_results,
            reason="G1 failed: token not found",
            step_up_required=False,
        )
    if token_data.get("revoked"):
        return ScopeCheckResult(
            allowed=False,
            gate_results=gate_results,
            reason="G1 failed: token is revoked",
            step_up_required=False,
        )
    gate_results["g1"] = True

    # G2: Not expired
    if _is_expired(token_data):
        return ScopeCheckResult(
            allowed=False,
            gate_results=gate_results,
            reason="G2 failed: token is expired",
            step_up_required=False,
        )
    gate_results["g2"] = True

    # G3: Scope sufficient
    token_scopes = token_data.get("scopes", [])
    if not _scope_sufficient(token_scopes, req.required_scopes):
        missing = [s for s in req.required_scopes if s not in token_scopes]
        return ScopeCheckResult(
            allowed=False,
            gate_results=gate_results,
            reason=f"G3 failed: missing scopes {missing}",
            step_up_required=False,
        )
    gate_results["g3"] = True

    # G4: Step-up required for high-risk actions
    step_up_required = _action_is_destructive(req.action_risk)
    gate_results["g4"] = True  # G4 passes (we set step_up_required flag, not block)

    return ScopeCheckResult(
        allowed=not step_up_required,  # High-risk actions require explicit step-up
        gate_results=gate_results,
        reason="step-up authentication required" if step_up_required else None,
        step_up_required=step_up_required,
    )

# --- Consent Tracking ---

@app.post("/oauth3/consent", response_model=ConsentRecord, status_code=201)
async def record_consent(req: ConsentRequest):
    """Record a consent decision."""
    record = ConsentRecord(
        token_id=req.token_id,
        principal_id=req.principal_id,
        agent_id=req.agent_id,
        action=req.action,
        scopes_requested=req.scopes_requested,
        decision=req.decision,
        metadata=req.metadata,
    )
    _consent_log.append(record.model_dump())
    return record

@app.get("/oauth3/consent/{token_id}")
async def get_consent_history(token_id: str):
    """Get consent history for a specific token."""
    history = [r for r in _consent_log if r.get("token_id") == token_id]
    return {
        "ok": True,
        "token_id": token_id,
        "count": len(history),
        "history": history,
    }
