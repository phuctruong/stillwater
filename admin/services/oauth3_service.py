"""OAuth3 Authority Service — token management, scope enforcement, consent tracking.

Port: 8791
Purpose: Issue/revoke agency tokens, enforce ScopeGate G1-G4, record consent.
In-memory storage with optional JSON persistence.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import hashlib
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
_step_up_log: dict[str, dict[str, Any]] = {}

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
    "gmail.read.inbox": {
        "id": "gmail.read.inbox",
        "description": "Read inbox message list and metadata",
        "risk": "low",
    },
    "gmail.read.labels": {
        "id": "gmail.read.labels",
        "description": "Read Gmail labels",
        "risk": "low",
    },
    "gmail.read.thread": {
        "id": "gmail.read.thread",
        "description": "Read full Gmail thread content",
        "risk": "low",
    },
    "gmail.modify.label": {
        "id": "gmail.modify.label",
        "description": "Apply or remove Gmail labels",
        "risk": "medium",
    },
    "gmail.modify.archive": {
        "id": "gmail.modify.archive",
        "description": "Archive Gmail messages",
        "risk": "high",
    },
    "gmail.send.reply": {
        "id": "gmail.send.reply",
        "description": "Send reply in existing Gmail thread",
        "risk": "high",
    },
    "gmail.send.compose": {
        "id": "gmail.send.compose",
        "description": "Compose and send new Gmail message",
        "risk": "high",
    },
    "gmail.delete.message": {
        "id": "gmail.delete.message",
        "description": "Delete Gmail message",
        "risk": "high",
    },
}

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = REPO_ROOT / "artifacts" / "oauth3" / "oauth3_audit.jsonl"

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


class GrantRequest(BaseModel):
    principal_id: str
    agent_id: str
    scopes: list[str]
    expires_at: str | None = None
    ttl_seconds: int | None = None
    metadata: dict = Field(default_factory=dict)


class ValidateRequest(BaseModel):
    token_id: str
    required_scope: str
    action_risk: str = "low"


class RevokeRequest(BaseModel):
    token_id: str


class StepUpRequest(BaseModel):
    token_id: str
    scopes: list[str]
    approver: str = "api:user"
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


def _token_hash(token_id: str) -> str:
    return hashlib.sha256(token_id.encode("utf-8")).hexdigest()[:12]


def _write_audit(event: str, token_id: str, details: dict[str, Any] | None = None) -> None:
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "token_hash": _token_hash(token_id),
        "details": details or {},
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def _require_existing_active_token(token_id: str) -> dict[str, Any]:
    token = _tokens.get(token_id)
    if token is None:
        raise HTTPException(status_code=401, detail="token not found")
    if token.get("revoked"):
        raise HTTPException(status_code=401, detail="token revoked")
    if _is_expired(token):
        raise HTTPException(status_code=401, detail="token expired")
    return token

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
    _write_audit(
        "grant",
        token.token_id,
        {
            "principal_id": req.principal_id,
            "agent_id": req.agent_id,
            "scopes": req.scopes,
            "expires_at": req.expires_at,
        },
    )
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
        _write_audit("revoke", token_id, {"revoked_at": now})

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


# --- TASK-029 API aliases ---

@app.post("/api/oauth3/grant", status_code=201)
async def api_grant(req: GrantRequest):
    expires_at = req.expires_at
    if not expires_at:
        ttl = int(req.ttl_seconds if req.ttl_seconds is not None else 3600)
        if ttl <= 0:
            raise HTTPException(status_code=400, detail="ttl_seconds must be > 0")
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=ttl)).isoformat()

    token = await issue_token(
        TokenIssueRequest(
            principal_id=req.principal_id,
            agent_id=req.agent_id,
            scopes=req.scopes,
            expires_at=expires_at,
            metadata=req.metadata,
        ),
    )
    return {
        "ok": True,
        "token_id": token.token_id,
        "token_hash": _token_hash(token.token_id),
        "scopes": token.scopes,
        "expires_at": token.expires_at,
    }


@app.post("/api/oauth3/step-up")
async def api_step_up(req: StepUpRequest):
    token = _require_existing_active_token(req.token_id)
    granted_scopes = set(token.get("scopes", []))
    for scope in req.scopes:
        if scope not in granted_scopes:
            raise HTTPException(status_code=403, detail=f"scope not granted in token: {scope}")
    _step_up_log[req.token_id] = {
        "scopes": sorted(set(req.scopes)),
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "approver": req.approver,
        "metadata": req.metadata,
    }
    _write_audit("step_up", req.token_id, {"scopes": sorted(set(req.scopes)), "approver": req.approver})
    return {"ok": True, "token_id": req.token_id, "step_up": _step_up_log[req.token_id]}


@app.post("/api/oauth3/validate")
async def api_validate(req: ValidateRequest):
    token = _require_existing_active_token(req.token_id)
    scopes = token.get("scopes", [])
    if req.required_scope not in scopes:
        _write_audit("validate_denied", req.token_id, {"reason": "scope_mismatch", "required_scope": req.required_scope})
        raise HTTPException(status_code=403, detail=f"scope denied: {req.required_scope}")

    if _action_is_destructive(req.action_risk):
        step_up = _step_up_log.get(req.token_id, {})
        step_up_scopes = set(step_up.get("scopes", []))
        if req.required_scope not in step_up_scopes:
            _write_audit(
                "validate_denied",
                req.token_id,
                {"reason": "step_up_required", "required_scope": req.required_scope},
            )
            raise HTTPException(status_code=401, detail=f"step-up required for scope: {req.required_scope}")

    _write_audit("validate_ok", req.token_id, {"required_scope": req.required_scope, "action_risk": req.action_risk})
    return {
        "ok": True,
        "token_id": req.token_id,
        "token_hash": _token_hash(req.token_id),
        "required_scope": req.required_scope,
        "action_risk": req.action_risk,
    }


@app.post("/api/oauth3/revoke")
async def api_revoke(req: RevokeRequest):
    result = await revoke_token(req.token_id)
    return {"ok": result.ok, "token_id": result.token_id, "revoked_at": result.revoked_at}
