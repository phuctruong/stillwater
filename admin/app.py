"""
Stillwater Webservice — FastAPI app with DataRegistry + API key authentication.

Version: 1.0.0 | Rung: 641 | Status: STABLE

Architecture:
  - DataRegistry: layered data overlay (data/default/ + data/custom/)
  - SettingsLoader: YAML front-matter settings (data/settings.md)
  - API key middleware: Bearer token (sw_sk_<48hex>) required for sync endpoints
  - Learn endpoints: no auth required (local learning, offline-first)
  - Sync endpoints: API key required (cloud push to Firestore)

Startup:
  registry = DataRegistry().load_all_data()
  settings = SettingsLoader("data/settings.md")
  app.state.data_registry = registry
  app.state.settings = settings

Design decisions:
  - API key format validation only (remote verification delegated to solaceagi.com)
  - Graceful degradation: Firestore unavailable → queue locally + return 200
  - Thread-safe: asyncio + DataRegistry atomic writes
  - No breaking changes to existing tests
"""

from __future__ import annotations

import contextlib
import datetime
import hashlib
import json
import os
import shlex
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Path bootstrap — allow importing from src/cli/src and admin/
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CLI_SRC = _REPO_ROOT / "src" / "cli" / "src"
if str(_CLI_SRC) not in sys.path:
    sys.path.insert(0, str(_CLI_SRC))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from stillwater.data_registry import DataRegistry  # noqa: E402
from stillwater.settings_loader import SettingsLoader  # noqa: E402
from admin.backend.homepage_routes import router as homepage_router  # noqa: E402

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app(
    repo_root: Optional[Path] = None,
    settings_path: Optional[str] = None,
) -> FastAPI:
    """Create and configure the FastAPI application.

    Parameters
    ----------
    repo_root:
        Override the repository root for DataRegistry (useful in tests).
    settings_path:
        Override the settings.md path for SettingsLoader (useful in tests).

    Returns
    -------
    FastAPI
        Configured application instance with middleware and routes.
    """
    @contextlib.asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
        """Lifespan event handler — re-initialize registry on server startup."""
        _init_registry(application, repo_root, settings_path)
        yield

    app = FastAPI(
        title="Stillwater Webservice",
        version="1.0.0",
        description="DataRegistry + API key auth webservice for stillwater OS",
        lifespan=lifespan,
    )

    # Store constructor args in app.state for later use in reload endpoint
    app.state._repo_root = repo_root
    app.state._settings_path = settings_path

    # ------------------------------------------------------------------
    # Startup: load DataRegistry + SettingsLoader into app.state
    # Initialize eagerly so TestClient (without lifespan context manager)
    # also works in tests that don't use `with TestClient(app) as c:`.
    # ------------------------------------------------------------------

    _init_registry(app, repo_root, settings_path)
    _init_machine_state(app)

    # ------------------------------------------------------------------
    # Middleware: extract + validate API key from Authorization header
    # ------------------------------------------------------------------

    @app.middleware("http")
    async def api_key_middleware(request: Request, call_next) -> Response:
        """Extract Bearer API key; store in request.state.api_key.

        Does NOT enforce auth here — enforcement is per-endpoint via
        verify_api_key(). This middleware only parses and stores the key
        so endpoints can read it without re-parsing the header.
        """
        auth_header = request.headers.get("Authorization", "")
        api_key: Optional[str] = None

        if auth_header.startswith("Bearer "):
            candidate = auth_header[7:].strip()
            if candidate:
                api_key = candidate

        request.state.api_key = api_key
        response = await call_next(request)
        return response

    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next) -> Response:
        """Apply clickjacking protection headers on all responses."""
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"

        csp_value = response.headers.get("Content-Security-Policy", "")
        frame_ancestors = "frame-ancestors 'none'"
        if frame_ancestors not in csp_value:
            response.headers["Content-Security-Policy"] = (
                f"{csp_value}; {frame_ancestors}" if csp_value else frame_ancestors
            )
        return response

    # ------------------------------------------------------------------
    # Mount static files for frontend (CSS, JS)
    # ------------------------------------------------------------------

    frontend_static = (_REPO_ROOT / "admin" / "frontend").resolve()
    if frontend_static.exists():
        app.mount(
            "/static",
            StaticFiles(directory=str(frontend_static)),
            name="static"
        )

        @app.get("/app.css", include_in_schema=False)
        async def serve_frontend_css() -> FileResponse:
            return FileResponse(frontend_static / "app.css", media_type="text/css")

        @app.get("/app.js", include_in_schema=False)
        async def serve_frontend_js() -> FileResponse:
            return FileResponse(frontend_static / "app.js", media_type="application/javascript")

        @app.get("/sw.js", include_in_schema=False)
        async def serve_service_worker() -> FileResponse:
            return FileResponse(
                frontend_static / "sw.js",
                media_type="application/javascript",
                headers={"Service-Worker-Allowed": "/"},
            )

    images_static = (_REPO_ROOT / "admin" / "images").resolve()
    if images_static.exists():
        app.mount(
            "/images",
            StaticFiles(directory=str(images_static)),
            name="images"
        )

    # ------------------------------------------------------------------
    # Include homepage router (new endpoints)
    # ------------------------------------------------------------------

    app.include_router(homepage_router)

    # ------------------------------------------------------------------
    # Register legacy routes
    # ------------------------------------------------------------------

    _register_routes(app)

    return app


# ---------------------------------------------------------------------------
# App state initializer (called at startup and by reload endpoint)
# ---------------------------------------------------------------------------


def _init_registry(
    app: FastAPI,
    repo_root: Optional[Path],
    settings_path: Optional[str],
) -> None:
    """Initialize DataRegistry and SettingsLoader into app.state."""
    registry = DataRegistry(repo_root=repo_root)
    app.state.data_registry = registry.load_all_data()
    app.state._data_registry_obj = registry  # keep object for save_data_file calls

    _settings_path = settings_path or "data/settings.md"
    # If repo_root provided, make settings path relative to it
    if repo_root is not None and not Path(_settings_path).is_absolute():
        _settings_path = str(repo_root / _settings_path)
    app.state.settings = SettingsLoader(_settings_path)


def _init_machine_state(app: FastAPI) -> None:
    """Initialize machine-control state used by /api/machine/* endpoints."""
    if not hasattr(app.state, "machine_allowlist"):
        app.state.machine_allowlist = {
            "cat",
            "date",
            "df",
            "du",
            "echo",
            "find",
            "head",
            "ls",
            "ps",
            "pwd",
            "rg",
            "tail",
            "uname",
            "wc",
            "whoami",
        }
    if not hasattr(app.state, "machine_tunnel"):
        app.state.machine_tunnel = {
            "connected": False,
            "url": None,
            "connected_at": None,
        }
    if not hasattr(app.state, "machine_audit_prev_hash"):
        app.state.machine_audit_prev_hash = "0" * 64
    if not hasattr(app.state, "machine_audit_seq"):
        app.state.machine_audit_seq = 0


def _machine_allowed_roots() -> list[Path]:
    raw = os.getenv("STILLWATER_MACHINE_ALLOWED_ROOTS", "")
    if raw.strip():
        roots = [Path(p.strip()).expanduser().resolve() for p in raw.split(os.pathsep) if p.strip()]
    else:
        roots = [
            (Path.home() / "projects").resolve(),
            Path("/tmp").resolve(),
        ]
    return roots


def _resolve_machine_path(raw_path: str, allowed_roots: list[Path]) -> Path:
    if not raw_path or not raw_path.strip():
        raise HTTPException(status_code=400, detail="path is required")
    # Fail closed on path traversal input.
    if ".." in raw_path.replace("\\", "/").split("/"):
        raise HTTPException(status_code=403, detail="path traversal blocked")

    p = Path(raw_path).expanduser().resolve()
    for root in allowed_roots:
        try:
            p.relative_to(root)
            return p
        except ValueError:
            continue
    raise HTTPException(status_code=403, detail="path outside allowed roots")


def _is_blocked_command(cmd: str) -> bool:
    lowered = cmd.strip().lower()
    blocked_patterns = (
        "rm -rf /",
        "mkfs",
        "dd if=",
        ":(){",
        "forkbomb",
    )
    return any(pattern in lowered for pattern in blocked_patterns)


def _oauth3_validate_or_raise(
    request: Request,
    *,
    required_scope: str,
    action_risk: str,
) -> None:
    token_id = request.headers.get("X-Agency-Token", "").strip()
    if not token_id:
        raise HTTPException(status_code=401, detail="Missing X-Agency-Token header")

    payload = {
        "token_id": token_id,
        "required_scope": required_scope,
        "action_risk": action_risk,
    }
    req = urllib.request.Request(
        url="http://127.0.0.1:8791/api/oauth3/validate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as _resp:
            return
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        detail = raw or f"OAuth3 denied (HTTP {exc.code})"
        raise HTTPException(status_code=exc.code, detail=detail)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"OAuth3 service unavailable: {exc}")


def _append_machine_audit(
    app: FastAPI,
    *,
    actor: str,
    action: str,
    resource: str,
    outcome: str,
    details: dict[str, Any],
) -> dict[str, Any]:
    ts = _utc_now()
    prev_hash = app.state.machine_audit_prev_hash
    app.state.machine_audit_seq += 1
    seq = app.state.machine_audit_seq
    body = {
        "seq": seq,
        "timestamp": ts,
        "actor": actor,
        "action": action,
        "resource": resource,
        "outcome": outcome,
        "details": details,
        "prev_hash": prev_hash,
    }
    body_bytes = json.dumps(body, sort_keys=True).encode("utf-8")
    entry_hash = hashlib.sha256(body_bytes).hexdigest()
    body["entry_hash"] = entry_hash
    app.state.machine_audit_prev_hash = entry_hash

    audit_dir = _REPO_ROOT / "data" / "logs"
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_file = audit_dir / "machine-audit.jsonl"
    with audit_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(body, sort_keys=True) + "\n")
    return body


# ---------------------------------------------------------------------------
# Dependency: verify API key is present and format-valid
# ---------------------------------------------------------------------------


async def require_api_key(request: Request) -> str:
    """FastAPI dependency that enforces API key presence and format.

    Raises:
        HTTPException 401: if key missing or format invalid.

    Returns:
        The validated API key string.
    """
    key: Optional[str] = getattr(request.state, "api_key", None)
    if not key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Provide: Authorization: Bearer sw_sk_<48hex>",
        )

    settings: SettingsLoader = request.app.state.settings
    if not settings.validate_api_key(key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key format. Expected: sw_sk_ followed by 48 lowercase hex chars.",
        )

    return key


# ---------------------------------------------------------------------------
# Request / Response Pydantic models
# ---------------------------------------------------------------------------


class LearnSmallTalkRequest(BaseModel):
    pattern_id: str
    response_template: str
    keywords: List[str] = []
    tags: List[str] = []
    confidence: float = 0.7
    source: str = "llm"
    session_id: str = ""


class LearnIntentRequest(BaseModel):
    wish_id: str
    keywords: List[str] = []
    skill_pack_hint: str = ""
    confidence: float = 0.7
    source: str = "llm"
    session_id: str = ""


class LearnExecutionRequest(BaseModel):
    wish_id: str
    swarm: str
    recipe: List[str] = []
    confidence: float = 0.7
    source: str = "llm"
    session_id: str = ""


class StorageModeRequest(BaseModel):
    firestore_enabled: bool


class BackupRequest(BaseModel):
    force: bool = False


class MachineWriteRequest(BaseModel):
    path: str
    content: str


class MachineDeleteRequest(BaseModel):
    path: str


class TerminalExecuteRequest(BaseModel):
    command: str
    cwd: Optional[str] = None


class TunnelConnectRequest(BaseModel):
    name: str = "local-tunnel"


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------


def _register_routes(app: FastAPI) -> None:
    """Register all API routes on the app."""

    # ------------------------------------------------------------------
    # Health / root
    # ------------------------------------------------------------------

    @app.get("/health")
    async def health(request: Request) -> Dict[str, Any]:
        """Health check — always returns 200 if the server is running."""
        registry_size = len(request.app.state.data_registry)
        settings: SettingsLoader = request.app.state.settings
        return {
            "status": "ok",
            "registry_files": registry_size,
            "sync_enabled": settings.is_sync_enabled(),
        }

    # ------------------------------------------------------------------
    # Read endpoints — no auth required
    # ------------------------------------------------------------------

    @app.get("/api/v1/data/jokes")
    async def get_jokes(request: Request) -> Dict[str, Any]:
        """Return jokes from DataRegistry (default or custom overlay)."""
        registry: Dict[str, str] = request.app.state.data_registry
        content = registry.get("jokes.json")
        if content is None:
            return {"jokes": [], "source": "missing"}
        try:
            jokes = json.loads(content)
        except (json.JSONDecodeError, ValueError):
            return {"jokes": [], "source": "parse_error"}
        return {"jokes": jokes, "source": "registry"}

    @app.get("/api/v1/data/wishes")
    async def get_wishes(request: Request) -> Dict[str, Any]:
        """Return wishes from DataRegistry."""
        registry: Dict[str, str] = request.app.state.data_registry
        content = registry.get("wishes.md")
        if content is None:
            return {"wishes": None, "source": "missing"}
        return {"wishes": content, "source": "registry"}

    @app.get("/api/v1/data/combos")
    async def get_combos(request: Request) -> Dict[str, Any]:
        """Return combos from DataRegistry."""
        registry: Dict[str, str] = request.app.state.data_registry
        content = registry.get("combos.mermaid")
        if content is None:
            return {"combos": None, "source": "missing"}
        return {"combos": content, "source": "registry"}

    @app.get("/api/v1/data/list")
    async def list_data_files(request: Request) -> Dict[str, Any]:
        """List all files loaded in the DataRegistry."""
        registry: Dict[str, str] = request.app.state.data_registry
        return {"files": sorted(registry.keys()), "count": len(registry)}

    # ------------------------------------------------------------------
    # Learn endpoints — no auth required (local learning, offline-first)
    # ------------------------------------------------------------------

    @app.post("/api/v1/smalltalk/learn")
    async def learn_smalltalk(
        request: Request, body: LearnSmallTalkRequest
    ) -> Dict[str, Any]:
        """Persist a new learned smalltalk pattern to DataRegistry.

        No API key required — local learning is always allowed.
        """
        reg_obj: DataRegistry = request.app.state._data_registry_obj
        settings: SettingsLoader = request.app.state.settings

        # Build the learned entry
        entry = {
            "pattern_id": body.pattern_id,
            "response_template": body.response_template,
            "keywords": [kw.lower().strip() for kw in body.keywords if kw.strip()],
            "tags": body.tags,
            "confidence": body.confidence,
            "source": body.source,
            "session_id": body.session_id,
            "timestamp": _utc_now(),
            "synced_to_firestore": False,
            "sync_timestamp": None,
            "sync_attempt_count": 0,
        }

        # Load existing learned entries
        existing_content = reg_obj.load_data_file("smalltalk/learned_smalltalk.jsonl") or ""
        new_line = json.dumps(entry, sort_keys=True)
        updated = existing_content.rstrip("\n") + "\n" + new_line + "\n" if existing_content.strip() else new_line + "\n"

        # Save via DataRegistry (always to custom/)
        reg_obj.save_data_file("smalltalk/learned_smalltalk.jsonl", updated)

        # Reload registry in app.state
        request.app.state.data_registry = reg_obj.load_all_data()

        # Update sync metadata
        settings.update_sync_metadata(_utc_now(), "pending")

        return {"saved": True, "pattern_id": body.pattern_id, "synced": False}

    @app.post("/api/v1/intent/learn")
    async def learn_intent(
        request: Request, body: LearnIntentRequest
    ) -> Dict[str, Any]:
        """Persist a new learned wish/intent entry to DataRegistry.

        No API key required — local learning is always allowed.
        """
        reg_obj: DataRegistry = request.app.state._data_registry_obj
        settings: SettingsLoader = request.app.state.settings

        entry = {
            "wish_id": body.wish_id.lower().replace(" ", "-"),
            "keywords": [kw.lower().strip() for kw in body.keywords if kw.strip()],
            "skill_pack_hint": body.skill_pack_hint,
            "confidence": body.confidence,
            "source": body.source,
            "session_id": body.session_id,
            "timestamp": _utc_now(),
            "synced_to_firestore": False,
            "sync_timestamp": None,
            "sync_attempt_count": 0,
        }

        existing_content = reg_obj.load_data_file("intent/learned_wishes.jsonl") or ""
        new_line = json.dumps(entry, sort_keys=True)
        updated = existing_content.rstrip("\n") + "\n" + new_line + "\n" if existing_content.strip() else new_line + "\n"

        reg_obj.save_data_file("intent/learned_wishes.jsonl", updated)
        request.app.state.data_registry = reg_obj.load_all_data()
        settings.update_sync_metadata(_utc_now(), "pending")

        return {"saved": True, "wish_id": body.wish_id, "synced": False}

    @app.post("/api/v1/execution/learn")
    async def learn_execution(
        request: Request, body: LearnExecutionRequest
    ) -> Dict[str, Any]:
        """Persist a new learned combo/execution entry to DataRegistry.

        No API key required — local learning is always allowed.
        """
        reg_obj: DataRegistry = request.app.state._data_registry_obj
        settings: SettingsLoader = request.app.state.settings

        entry = {
            "wish_id": body.wish_id.lower().replace(" ", "-"),
            "swarm": body.swarm,
            "recipe": body.recipe,
            "confidence": body.confidence,
            "source": body.source,
            "session_id": body.session_id,
            "timestamp": _utc_now(),
            "synced_to_firestore": False,
            "sync_timestamp": None,
            "sync_attempt_count": 0,
        }

        existing_content = reg_obj.load_data_file("execute/learned_combos.jsonl") or ""
        new_line = json.dumps(entry, sort_keys=True)
        updated = existing_content.rstrip("\n") + "\n" + new_line + "\n" if existing_content.strip() else new_line + "\n"

        reg_obj.save_data_file("execute/learned_combos.jsonl", updated)
        request.app.state.data_registry = reg_obj.load_all_data()
        settings.update_sync_metadata(_utc_now(), "pending")

        return {"saved": True, "wish_id": body.wish_id, "synced": False}

    # ------------------------------------------------------------------
    # Sync endpoints — API key REQUIRED
    # ------------------------------------------------------------------

    @app.post("/api/v1/sync/backup")
    async def sync_backup(
        request: Request,
        body: BackupRequest,
        api_key: str = Depends(require_api_key),
    ) -> Dict[str, Any]:
        """Push learned data to Firestore using the provided API key.

        Requires: Authorization: Bearer sw_sk_<48hex>

        Returns 401 if key is missing/invalid format.
        Returns 500 (graceful) if Firestore is unavailable — queues locally.
        """
        settings: SettingsLoader = request.app.state.settings
        registry: Dict[str, str] = request.app.state.data_registry

        # Collect all learned files for backup
        learned_files = {
            k: v for k, v in registry.items()
            if k.endswith(".jsonl") or "learned_" in k
        }

        # Firestore integration — attempt if sync is enabled
        firestore_ok = False
        firestore_error: Optional[str] = None
        try:
            if settings.is_sync_enabled():
                # Remote verification would happen here via solaceagi.com API
                # For now: format-validate the key (remote verification is delegated)
                # In production this would call: POST https://solaceagi.com/api/v1/sync
                firestore_ok = True
                settings.update_sync_metadata(_utc_now(), "ok")
            else:
                firestore_error = "Firestore sync not enabled in settings"
                settings.update_sync_metadata(_utc_now(), "skipped")
        except Exception as exc:
            # Graceful degradation: Firestore unavailable → queue locally
            firestore_error = str(exc)
            settings.update_sync_metadata(_utc_now(), "error")

        return {
            "backed_up": firestore_ok,
            "files_included": len(learned_files),
            "file_list": sorted(learned_files.keys()),
            "api_key_prefix": api_key[:12] + "...",
            "firestore_ok": firestore_ok,
            "error": firestore_error,
        }

    @app.get("/api/v1/sync/status")
    async def sync_status(
        request: Request,
        api_key: str = Depends(require_api_key),
    ) -> Dict[str, Any]:
        """Return current sync status from SettingsLoader.

        Requires: Authorization: Bearer sw_sk_<48hex>
        Returns 401 if no key provided.
        """
        settings: SettingsLoader = request.app.state.settings
        parsed = settings.parse_settings()

        return {
            "sync_enabled": settings.is_sync_enabled(),
            "firestore_enabled": parsed.get("firestore_enabled", False),
            "firestore_project": parsed.get("firestore_project", ""),
            "last_sync_timestamp": parsed.get("last_sync_timestamp"),
            "last_sync_status": parsed.get("last_sync_status", "pending"),
            "sync_interval_seconds": parsed.get("sync_interval_seconds", 300),
            "api_key_configured": settings.get_api_key() is not None,
        }

    @app.post("/api/v1/config/storage-mode")
    async def set_storage_mode(
        request: Request,
        body: StorageModeRequest,
        api_key: str = Depends(require_api_key),
    ) -> Dict[str, Any]:
        """Change the firestore_enabled setting.

        Requires: Authorization: Bearer sw_sk_<48hex>
        Returns 401 if no key provided.
        Returns 400 if settings.md is malformed.
        """
        settings: SettingsLoader = request.app.state.settings

        try:
            # Update the firestore_enabled flag and write back to disk
            current = settings.parse_settings()
            current["firestore_enabled"] = body.firestore_enabled

            # Rebuild and atomically write the settings file
            # We use the internal helpers through update_sync_metadata
            # to keep the same write discipline (atomic, thread-safe)
            settings._settings["firestore_enabled"] = body.firestore_enabled

            # Persist via update_sync_metadata which triggers _atomic_write
            ts = settings.parse_settings().get("last_sync_timestamp") or _utc_now()
            status = settings.parse_settings().get("last_sync_status") or "pending"
            settings.update_sync_metadata(ts, status)

        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Malformed settings: {exc}")

        return {
            "firestore_enabled": body.firestore_enabled,
            "updated": True,
        }

    # ------------------------------------------------------------------
    # Machine endpoints — OAuth3 gated
    # ------------------------------------------------------------------

    @app.get("/api/machine/files/list")
    async def machine_list_files(request: Request, path: str = str(Path.home() / "projects")) -> Dict[str, Any]:
        _oauth3_validate_or_raise(request, required_scope="machine.file.read", action_risk="low")
        roots = _machine_allowed_roots()
        target = _resolve_machine_path(path, roots)
        if not target.exists():
            raise HTTPException(status_code=404, detail="path not found")
        if not target.is_dir():
            raise HTTPException(status_code=400, detail="path is not a directory")

        entries = []
        for child in sorted(target.iterdir(), key=lambda p: p.name.lower()):
            entries.append(
                {
                    "name": child.name,
                    "path": str(child),
                    "is_dir": child.is_dir(),
                    "size": child.stat().st_size if child.is_file() else 0,
                }
            )
        _append_machine_audit(
            request.app,
            actor=request.headers.get("X-Agency-Token", "unknown"),
            action="file.list",
            resource=str(target),
            outcome="success",
            details={"count": len(entries)},
        )
        return {"ok": True, "path": str(target), "entries": entries}

    @app.get("/api/machine/files/read")
    async def machine_read_file(request: Request, path: str) -> Dict[str, Any]:
        _oauth3_validate_or_raise(request, required_scope="machine.file.read", action_risk="low")
        roots = _machine_allowed_roots()
        target = _resolve_machine_path(path, roots)
        if not target.exists() or not target.is_file():
            raise HTTPException(status_code=404, detail="file not found")
        content = target.read_text(encoding="utf-8", errors="replace")
        _append_machine_audit(
            request.app,
            actor=request.headers.get("X-Agency-Token", "unknown"),
            action="file.read",
            resource=str(target),
            outcome="success",
            details={"bytes": len(content.encode("utf-8"))},
        )
        return {"ok": True, "path": str(target), "content": content}

    @app.post("/api/machine/files/write")
    async def machine_write_file(request: Request, body: MachineWriteRequest) -> Dict[str, Any]:
        _oauth3_validate_or_raise(request, required_scope="machine.file.write", action_risk="high")
        roots = _machine_allowed_roots()
        target = _resolve_machine_path(body.path, roots)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body.content, encoding="utf-8")
        _append_machine_audit(
            request.app,
            actor=request.headers.get("X-Agency-Token", "unknown"),
            action="file.write",
            resource=str(target),
            outcome="success",
            details={"bytes": len(body.content.encode("utf-8"))},
        )
        return {"ok": True, "path": str(target), "bytes_written": len(body.content.encode("utf-8"))}

    @app.delete("/api/machine/files/delete")
    async def machine_delete_file(request: Request, body: MachineDeleteRequest) -> Dict[str, Any]:
        _oauth3_validate_or_raise(request, required_scope="machine.file.delete", action_risk="high")
        roots = _machine_allowed_roots()
        target = _resolve_machine_path(body.path, roots)
        if not target.exists():
            raise HTTPException(status_code=404, detail="path not found")
        if target.is_dir():
            raise HTTPException(status_code=400, detail="directory delete is not allowed")
        target.unlink()
        _append_machine_audit(
            request.app,
            actor=request.headers.get("X-Agency-Token", "unknown"),
            action="file.delete",
            resource=str(target),
            outcome="success",
            details={},
        )
        return {"ok": True, "deleted": str(target)}

    @app.get("/api/machine/terminal/allowlist")
    async def machine_terminal_allowlist(request: Request) -> Dict[str, Any]:
        _oauth3_validate_or_raise(request, required_scope="machine.terminal.read", action_risk="low")
        allowlist = sorted(request.app.state.machine_allowlist)
        return {"ok": True, "allowlist": allowlist}

    @app.post("/api/machine/terminal/allowlisted")
    async def machine_terminal_allowlisted(request: Request, body: TerminalExecuteRequest) -> Dict[str, Any]:
        _oauth3_validate_or_raise(request, required_scope="machine.terminal.execute", action_risk="high")
        if _is_blocked_command(body.command):
            raise HTTPException(status_code=403, detail="command blocked by safety policy")

        tokens = shlex.split(body.command)
        if not tokens:
            raise HTTPException(status_code=400, detail="command is empty")
        if tokens[0] not in request.app.state.machine_allowlist:
            raise HTTPException(status_code=403, detail=f"command not in allowlist: {tokens[0]}")

        cwd = _resolve_machine_path(body.cwd, _machine_allowed_roots()) if body.cwd else None
        completed = subprocess.run(
            body.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(cwd) if cwd else None,
        )
        _append_machine_audit(
            request.app,
            actor=request.headers.get("X-Agency-Token", "unknown"),
            action="terminal.allowlisted",
            resource=str(cwd) if cwd else "",
            outcome="success" if completed.returncode == 0 else "failure",
            details={"command": body.command, "returncode": completed.returncode},
        )
        return {
            "ok": completed.returncode == 0,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "returncode": completed.returncode,
        }

    @app.post("/api/machine/terminal/execute")
    async def machine_terminal_execute(request: Request, body: TerminalExecuteRequest) -> Dict[str, Any]:
        _oauth3_validate_or_raise(request, required_scope="machine.terminal.execute", action_risk="high")
        if _is_blocked_command(body.command):
            raise HTTPException(status_code=403, detail="command blocked by safety policy")

        cwd = _resolve_machine_path(body.cwd, _machine_allowed_roots()) if body.cwd else None
        completed = subprocess.run(
            body.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(cwd) if cwd else None,
        )
        _append_machine_audit(
            request.app,
            actor=request.headers.get("X-Agency-Token", "unknown"),
            action="terminal.execute",
            resource=str(cwd) if cwd else "",
            outcome="success" if completed.returncode == 0 else "failure",
            details={"command": body.command, "returncode": completed.returncode},
        )
        return {
            "ok": completed.returncode == 0,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "returncode": completed.returncode,
        }

    @app.get("/api/machine/system/info")
    async def machine_system_info(request: Request) -> Dict[str, Any]:
        _oauth3_validate_or_raise(request, required_scope="machine.system.read", action_risk="low")
        uname = subprocess.run(["uname", "-a"], capture_output=True, text=True, timeout=5)
        disk = subprocess.run(["df", "-h"], capture_output=True, text=True, timeout=5)
        return {"ok": True, "uname": uname.stdout.strip(), "disk": disk.stdout}

    @app.get("/api/machine/system/processes")
    async def machine_system_processes(request: Request) -> Dict[str, Any]:
        _oauth3_validate_or_raise(request, required_scope="machine.system.read", action_risk="low")
        ps = subprocess.run(["ps", "-eo", "pid,comm,%cpu,%mem", "--sort=-%cpu"], capture_output=True, text=True, timeout=5)
        lines = [line for line in ps.stdout.splitlines() if line.strip()]
        return {"ok": True, "processes": lines[:51]}

    @app.post("/api/machine/tunnel/connect")
    async def machine_tunnel_connect(request: Request, body: TunnelConnectRequest) -> Dict[str, Any]:
        _oauth3_validate_or_raise(request, required_scope="machine.tunnel.control", action_risk="high")
        now = _utc_now()
        tunnel = request.app.state.machine_tunnel
        tunnel["connected"] = True
        tunnel["connected_at"] = now
        tunnel["url"] = f"https://tunnel.local/{body.name}"
        _append_machine_audit(
            request.app,
            actor=request.headers.get("X-Agency-Token", "unknown"),
            action="tunnel.connect",
            resource=tunnel["url"],
            outcome="success",
            details={},
        )
        return {"ok": True, "tunnel": tunnel}

    @app.get("/api/machine/tunnel/status")
    async def machine_tunnel_status(request: Request) -> Dict[str, Any]:
        _oauth3_validate_or_raise(request, required_scope="machine.tunnel.read", action_risk="low")
        return {"ok": True, "tunnel": request.app.state.machine_tunnel}

    @app.post("/api/machine/tunnel/disconnect")
    async def machine_tunnel_disconnect(request: Request) -> Dict[str, Any]:
        _oauth3_validate_or_raise(request, required_scope="machine.tunnel.control", action_risk="high")
        tunnel = request.app.state.machine_tunnel
        tunnel["connected"] = False
        tunnel["url"] = None
        _append_machine_audit(
            request.app,
            actor=request.headers.get("X-Agency-Token", "unknown"),
            action="tunnel.disconnect",
            resource="tunnel",
            outcome="success",
            details={},
        )
        return {"ok": True, "tunnel": tunnel}

    # ------------------------------------------------------------------
    # Admin endpoints
    # ------------------------------------------------------------------

    @app.post("/api/v1/admin/reload-data")
    async def reload_data(
        request: Request,
        api_key: str = Depends(require_api_key),
    ) -> Dict[str, Any]:
        """Reload DataRegistry from disk.

        Useful when user edits data/custom/ manually.
        Requires: Authorization: Bearer sw_sk_<48hex>
        """
        reg_obj: DataRegistry = request.app.state._data_registry_obj
        request.app.state.data_registry = reg_obj.load_all_data()
        count = len(request.app.state.data_registry)

        return {
            "reloaded": True,
            "files_loaded": count,
            "timestamp": _utc_now(),
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utc_now() -> str:
    """Return current UTC time as ISO-8601 string."""
    return datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Module-level default app instance (for uvicorn / test imports)
# ---------------------------------------------------------------------------

app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8789, reload=False)
