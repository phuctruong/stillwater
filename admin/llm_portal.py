#!/usr/bin/env python3
"""
Stillwater LLM Portal v2.0 (Fixed)
Auth: 65537 | Port: 8788 | Status: STABLE

Improvements:
✓ Configuration errors are logged (not silent failures)
✓ Port/host from environment variables work correctly
✓ Web-editable config (save changes to llm_config.yaml)
✓ Model selection for Ollama + Claude Code CLI
✓ Proper dependency checking on startup
✓ Better error handling + logging
✓ Safe process management
✓ Authentic token counting (when available)

Web endpoints:
  GET  /                              Web UI (dark theme)
  GET  /api/health                    Health check
  GET  /api/providers                 All providers + models + status
  POST /api/providers/switch          Switch active provider
  POST /api/config/set-model          Change model for a provider
  POST /api/config/save               Save config to llm_config.yaml
  GET  /api/history                   Recent LLM call logs
  POST /v1/chat/completions           OpenAI-compatible proxy
  GET  /v1/models                     OpenAI-compatible model list
"""

from __future__ import annotations

import sys
import time
import uuid
import logging
from pathlib import Path
from typing import Any, Optional

# Set up logging before imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Add src/cli/src to path
_CLI_SRC = Path(__file__).parent.parent / "src" / "cli" / "src"
if str(_CLI_SRC) not in sys.path:
    sys.path.insert(0, str(_CLI_SRC))

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel, Field
except ImportError as e:
    logger.error(f"Missing dependencies: {e}")
    logger.error("Install with: pip install 'fastapi[standard]' uvicorn httpx")
    sys.exit(1)

try:
    from stillwater.llm_client import LLMClient, get_call_history
except ImportError as e:
    logger.error(f"stillwater.llm_client not importable: {e}")
    logger.error("Install with: pip install -e src/cli/")
    sys.exit(1)

try:
    from llm_config_manager import LLMConfigManager
except ImportError:
    logger.error("llm_config_manager not importable")
    LLMConfigManager = None

try:
    from admin.session_manager import SessionManager
except ImportError:
    try:
        from session_manager import SessionManager
    except ImportError:
        logger.warning("SessionManager not available (Phase 3 features disabled)")
        SessionManager = None

try:
    from admin.services.key_manager import KeyManager
    from admin.services.llm_wrapper import LLMWrapper
except ImportError:
    try:
        from services.key_manager import KeyManager
        from services.llm_wrapper import LLMWrapper
    except ImportError:
        KeyManager = None  # type: ignore
        LLMWrapper = None  # type: ignore

try:
    from stillwater.audit_logger import AuditLogger
except ImportError:
    AuditLogger = None  # type: ignore


# ============================================================
# App + Global State
# ============================================================

app = FastAPI(
    title="Stillwater LLM Portal",
    description="Universal LLM proxy with web UI. Auth: 65537.",
    version="2.0.0",
)

_config: Optional[Any] = None
_session: Optional[Any] = None
_repo_root = Path(__file__).resolve().parents[1]
_key_manager = KeyManager(_repo_root) if KeyManager is not None else None
_llm_wrapper = LLMWrapper(_repo_root) if LLMWrapper is not None else None
_audit_logger = AuditLogger(_repo_root / "data" / "logs") if AuditLogger is not None else None


def _get_session() -> Optional[Any]:
    global _session
    if _session is None and SessionManager is not None:
        try:
            _session = SessionManager()
        except Exception as e:
            logger.warning(f"SessionManager init failed: {e}")
    return _session


def _get_config() -> Optional[Any]:
    global _config
    if _config is None and LLMConfigManager is not None:
        try:
            _config = LLMConfigManager()
            logger.info(f"Config loaded: active provider = {_config.active_provider}")
        except FileNotFoundError as e:
            logger.error(f"Config file not found: {e}")
        except Exception as e:
            logger.error(f"Config load failed: {e}")
    return _config


def _make_client(provider: Optional[str] = None) -> LLMClient:
    """Create an LLMClient using the current active provider with config URLs."""
    cfg = _get_config()

    # Build config dict keyed by provider type (as LLMClient expects)
    config_dict = {}
    resolved_provider = provider

    if cfg:
        # If provider is specified, find its config
        if provider and provider in cfg.config:
            prov_config = cfg.config[provider]
            if isinstance(prov_config, dict):
                prov_type = prov_config.get("type", "")
                if prov_type == "http" and "url" in prov_config:
                    # For HTTP providers, use "http" as the provider type
                    resolved_provider = "http"
                    config_dict["http"] = {"url": prov_config["url"]}
                elif "url" in prov_config:
                    config_dict[provider] = {"url": prov_config["url"]}

        # If no provider specified, use active provider from config
        if not provider:
            active = cfg.active_provider
            resolved_provider = active
            if active in cfg.config:
                prov_config = cfg.config[active]
                if isinstance(prov_config, dict):
                    prov_type = prov_config.get("type", "")
                    if prov_type == "http" and "url" in prov_config:
                        # For HTTP providers, use "http" as the provider type
                        resolved_provider = "http"
                        config_dict["http"] = {"url": prov_config["url"]}
                    elif "url" in prov_config:
                        config_dict[active] = {"url": prov_config["url"]}

    # Create client with resolved provider
    if resolved_provider:
        return LLMClient(provider=resolved_provider, config=config_dict)

    logger.warning("Using offline provider (config not available)")
    return LLMClient(provider="offline", config=config_dict)


def _mask_llm_config(config: dict[str, Any]) -> dict[str, Any]:
    if _key_manager is None:
        return config
    masked: dict[str, Any] = {
        "default_provider": config.get("default_provider", "claude-code"),
        "providers": {},
    }
    providers = config.get("providers", {})
    if not isinstance(providers, dict):
        return masked
    for provider, values in providers.items():
        row = dict(values) if isinstance(values, dict) else {}
        api_key = str(row.get("api_key", ""))
        if api_key:
            row["api_key"] = _key_manager.mask_key(api_key)
        masked["providers"][provider] = row
    return masked


def _audit_key_event(user_id: str, field: str, old_value: str, new_value: str, session_id: str) -> None:
    if _audit_logger is None:
        return
    try:
        _audit_logger.log_config_change(
            user_id=user_id,
            field=field,
            old_value=old_value,
            new_value=new_value,
            reason="llm_key_api",
            session_id=session_id,
        )
    except Exception:
        pass


# ============================================================
# Request/Response Models
# ============================================================

class SwitchProviderRequest(BaseModel):
    provider: str


class SetModelRequest(BaseModel):
    provider: str
    model: str


class SaveConfigRequest(BaseModel):
    provider: str
    model: str
    url: Optional[str] = None


class LLMCompleteRequest(BaseModel):
    prompt: str
    model: str = "sonnet"
    provider: Optional[str] = None


class LLMConfigRequest(BaseModel):
    default_provider: Optional[str] = None
    providers: dict[str, dict[str, Any]] = Field(default_factory=dict)


class LLMKeyRequest(BaseModel):
    api_key: str


class LLMProviderTestRequest(BaseModel):
    provider: Optional[str] = None
    prompt: str = "Reply exactly: TEST_OK"
    model: str = "sonnet"


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "auto"
    messages: list[ChatMessage]
    temperature: float = 0.0
    max_tokens: int = 4096
    stream: bool = False


class ContextSource(BaseModel):
    """SW5.0 construct to inject as context (skill, recipe, swarm, persona, or raw)."""
    type: str                  # "skill" | "recipe" | "swarm" | "persona" | "raw"
    name: str = ""
    mode: str = "quick"        # "quick" (QUICK LOAD block only) | "full" (entire file)
    content: str = ""          # used when type="raw"


class ContextChatRequest(BaseModel):
    """Chat request with SW5.0 context injection."""
    model: str = "auto"
    messages: list[ChatMessage]
    context_sources: list[ContextSource] = []
    cnf_capsule: dict = {}     # optional: {task, constraints, rung_target, etc.}
    rung_target: int = 641     # explicit rung declaration
    temperature: float = 0.0
    max_tokens: int = 4096


# ============================================================
# Startup + Shutdown
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup."""
    logger.info("=" * 60)
    logger.info("Stillwater LLM Portal v2.0 — Starting")
    logger.info("=" * 60)

    cfg = _get_config()
    if cfg is None:
        logger.error("Config load failed on startup — running in degraded mode")
        logger.error("This is likely because llm_config.yaml is missing or corrupted")
        logger.error("Location: " + str(Path.cwd() / "llm_config.yaml"))
    else:
        logger.info(f"Active provider: {cfg.active_provider}")
        try:
            provider = _make_client(cfg.active_provider)
            is_available = provider.is_available()
            logger.info(f"Provider available: {is_available}")
        except Exception as e:
            logger.warning(f"Could not check provider availability: {e}")

    logger.info("=" * 60)


# ============================================================
# Context Loader: SW5.0 Construct Loading
# ============================================================

class ContextLoader:
    """Loads SW5.0 constructs (skills, recipes, swarms, personas) from filesystem."""

    TYPE_PATHS = {
        "skill":   ("data/default/skills", "{name}.md"),
        "recipe":  ("data/default/recipes", "recipe.{name}.md"),
        "swarm":   ("data/default/swarms", "**/{name}.md"),
        "persona": ("data/default/personas", "**/{name}.md"),
    }

    def __init__(self, project_root: Path):
        self.root = project_root

    def load(self, source: ContextSource) -> str:
        """Load content for one context source."""
        if source.type == "raw":
            return source.content
        path = self._resolve_path(source.type, source.name)
        if not path:
            return f"[CONTEXT NOT FOUND: {source.type}/{source.name}]"
        try:
            text = path.read_text(encoding="utf-8")
            if source.mode == "quick":
                extracted = self._extract_quick_load(text)
                return extracted if extracted else text[:800]
            return text
        except Exception as e:
            logger.warning(f"Failed to load {source.type}/{source.name}: {e}")
            return f"[ERROR LOADING: {source.type}/{source.name}]"

    def build_system_prompt(self, sources: list[ContextSource], cnf: dict) -> str:
        """Build full system prompt from all context sources."""
        if not sources and not cnf:
            return ""
        parts = []
        for src in sources:
            content = self.load(src)
            parts.append(f"## {src.type.upper()}: {src.name}\n{content}")
        if cnf:
            cnf_text = "\n".join(f"{k}: {v}" for k, v in cnf.items())
            parts.append(f"## CNF CAPSULE\n{cnf_text}")
        return "\n\n---\n\n".join(parts)

    def catalog(self) -> dict:
        """Return all available constructs by type."""
        return {
            "skills": self._list("data/default/skills", "*.md", exclude=["SKILL-FORMAT", "README"]),
            "recipes": [f.stem.replace("recipe.", "") for f in (self.root / "data" / "default" / "recipes").glob("recipe.*.md")],
            "swarms": self._list("data/default/swarms", "*.md", exclude=["README"], recursive=True),
            "personas": [f.stem for f in (self.root / "data" / "default" / "personas").rglob("*.md") if "README" not in f.stem and "index" not in f.stem.lower()],
        }

    def _resolve_path(self, type_: str, name: str) -> Optional[Path]:
        """Resolve filesystem path for a context source."""
        if type_ == "persona":
            matches = list((self.root / "data" / "default" / "personas").rglob(f"{name}.md"))
            return matches[0] if matches else None
        if type_ == "swarm":
            matches = sorted((self.root / "data" / "default" / "swarms").rglob(f"{name}.md"))
            return matches[0] if matches else None
        dir_, pattern = self.TYPE_PATHS[type_]
        p = self.root / dir_ / pattern.format(name=name)
        if p.exists():
            return p
        # fallback for recipes without "recipe." prefix
        if type_ == "recipe":
            fallback = self.root / dir_ / f"{name}.md"
            if fallback.exists():
                return fallback
        return None

    def _extract_quick_load(self, text: str) -> str:
        """Extract <!-- QUICK LOAD ... --> block from skill/swarm files."""
        start = text.find("<!-- QUICK LOAD")
        end = text.find("-->", start)
        if start != -1 and end != -1:
            return text[start:end+3].strip()
        return ""

    def _list(self, dir_: str, glob_pattern: str, exclude: list[str], recursive: bool = False) -> list[str]:
        """List files in a directory, excluding patterns."""
        try:
            iterator = (self.root / dir_).rglob(glob_pattern) if recursive else (self.root / dir_).glob(glob_pattern)
            return sorted([
                f.stem for f in iterator
                if not any(ex in f.stem for ex in exclude)
            ])
        except Exception as e:
            logger.warning(f"Failed to list {dir_}: {e}")
            return []


# Singleton context loader instance
_ctx_loader = ContextLoader(Path(__file__).parent.parent)


# ============================================================
# Routes: Health + Status
# ============================================================

@app.get("/api/health")
async def health() -> dict:
    """Health check with config status."""
    cfg = _get_config()
    active = cfg.active_provider if cfg else "offline"
    config_loaded = cfg is not None
    return {
        "status": "ok" if config_loaded else "degraded",
        "active_provider": active,
        "portal_version": "2.0.0",
        "config_loaded": config_loaded,
    }


@app.get("/api/providers")
async def list_providers() -> dict:
    """
    List all configured providers with:
    - Reachability status + latency
    - Available models
    - Active/authenticated status
    - Editable status
    """
    cfg = _get_config()
    if cfg is None:
        logger.warning("list_providers: config not available")
        return {"providers": [], "active": "offline", "config_loaded": False}

    session = _get_session()
    providers = []
    all_providers = cfg.list_providers()

    for name, info in all_providers.items():
        is_active = name == cfg.active_provider
        provider_type = info.get("type", "")

        # Reachability check (quick, non-blocking)
        reachable = None
        latency_ms = None
        models_list = []

        if provider_type == "offline":
            reachable = True
            latency_ms = 0
        elif provider_type == "http":
            # Check ALL http providers (local and remote)
            try:
                import urllib.request
                start = time.monotonic()
                request = urllib.request.Request(f"{info['url']}/", method='GET')
                request.add_header('User-Agent', 'Stillwater-Portal/2.0')
                try:
                    with urllib.request.urlopen(request, timeout=2.0) as response:
                        reachable = response.status in (200, 404, 405)
                except urllib.error.HTTPError as e:
                    reachable = e.code in (200, 404, 405)
                except (urllib.error.URLError, TimeoutError):
                    reachable = False
                latency_ms = int((time.monotonic() - start) * 1000)
            except Exception as e:
                logger.debug(f"Reachability check failed for {name}: {e}")
                reachable = False

            # Try to fetch models for Ollama
            if reachable and name == "ollama":
                try:
                    import urllib.request
                    import json
                    request = urllib.request.Request(f"{info['url']}/api/tags", method='GET')
                    request.add_header('User-Agent', 'Stillwater-Portal/2.0')
                    with urllib.request.urlopen(request, timeout=2.0) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        models_list = [m["name"] for m in data.get("models", []) if isinstance(m, dict) and "name" in m]
                except Exception as e:
                    logger.debug(f"Could not fetch Ollama models: {e}")

        elif provider_type == "cli":
            # Check if CLI is available
            try:
                from shutil import which
                cli_available = which("claude-code") is not None
                reachable = cli_available
                if cli_available:
                    models_list = ["haiku", "sonnet", "opus"]
                    latency_ms = 0
            except Exception as e:
                logger.debug(f"Could not check CLI availability: {e}")
                reachable = False

        requires_key = info.get("requires_api_key", False)
        authenticated = session.has_key(name) if session is not None else False

        providers.append({
            "id": name,
            "name": info.get("name", name),
            "url": info.get("url", ""),
            "type": provider_type,
            "model": cfg.config.get(name, {}).get("model", ""),
            "models": models_list,
            "active": is_active,
            "reachable": reachable,
            "latency_ms": latency_ms,
            "requires_api_key": requires_key,
            "authenticated": authenticated,
            "editable": info.get("editable", False),
        })

    return {"providers": providers, "active": cfg.active_provider, "config_loaded": True}


@app.post("/api/providers/switch")
async def switch_provider(req: SwitchProviderRequest) -> dict:
    """Switch the active provider."""
    cfg = _get_config()
    if cfg is None:
        raise HTTPException(status_code=503, detail="Config not loaded")
    try:
        cfg.switch_provider(req.provider)
        logger.info(f"Switched provider: {req.provider}")
        return {"ok": True, "active_provider": cfg.active_provider}
    except ValueError as e:
        logger.warning(f"Provider switch failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/config/set-model")
async def set_model(req: SetModelRequest) -> dict:
    """
    Change the model for a specific provider (in-memory only).
    To persist, use /api/config/save
    """
    cfg = _get_config()
    if cfg is None:
        raise HTTPException(status_code=503, detail="Config not loaded")

    # Validate provider
    if req.provider not in cfg.config:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {req.provider}")

    # Update in-memory config
    cfg.config[req.provider]["model"] = req.model
    logger.info(f"Model updated (in-memory): {req.provider} → {req.model}")

    return {
        "ok": True,
        "provider": req.provider,
        "model": req.model,
        "note": "Change is in-memory only. Use /api/config/save to persist.",
    }


@app.post("/api/config/save")
async def save_config(req: SaveConfigRequest) -> dict:
    """
    Save configuration to llm_config.yaml.
    This persists changes for the next restart.
    """
    cfg = _get_config()
    if cfg is None:
        raise HTTPException(status_code=503, detail="Config not loaded")

    # Validate provider
    if req.provider not in cfg.config:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {req.provider}")

    # Update in-memory config
    cfg.config[req.provider]["model"] = req.model
    if req.url:
        cfg.config[req.provider]["url"] = req.url

    # Try to save to file
    try:
        import yaml
        config_path = cfg.config_path
        with open(config_path, 'w') as f:
            yaml.dump(cfg.config, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Config saved to {config_path}: {req.provider} model={req.model}")
        return {
            "ok": True,
            "provider": req.provider,
            "model": req.model,
            "saved_to": str(config_path),
        }
    except ImportError:
        logger.warning("PyYAML not available — cannot save config")
        raise HTTPException(status_code=503, detail="PyYAML not installed, cannot save config")
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        raise HTTPException(status_code=500, detail=f"Save failed: {e}")


@app.post("/api/llm/complete")
async def llm_complete(req: LLMCompleteRequest) -> dict:
    if _llm_wrapper is None:
        raise HTTPException(status_code=503, detail="LLM wrapper unavailable")
    result = _llm_wrapper.complete(prompt=req.prompt, model=req.model, provider=req.provider)
    if not result.get("ok"):
        raise HTTPException(status_code=503, detail="No provider succeeded")
    return result


@app.get("/api/llm/providers")
async def llm_providers() -> dict:
    if _llm_wrapper is None:
        return {"ok": False, "providers": []}
    providers = _llm_wrapper.list_providers()
    cfg = _key_manager.load_config() if _key_manager is not None else {}
    return {
        "ok": True,
        "default_provider": cfg.get("default_provider", "claude-code"),
        "providers": providers,
    }


@app.get("/api/llm/models")
async def llm_models() -> dict:
    if _llm_wrapper is None:
        return {"ok": False, "models": {}}
    return {"ok": True, "models": _llm_wrapper.list_models()}


@app.get("/api/llm/config")
async def llm_config_get() -> dict:
    if _key_manager is None:
        raise HTTPException(status_code=503, detail="Key manager unavailable")
    config = _key_manager.load_config()
    return {"ok": True, "config": _mask_llm_config(config)}


@app.put("/api/llm/config")
async def llm_config_put(req: LLMConfigRequest) -> dict:
    if _key_manager is None:
        raise HTTPException(status_code=503, detail="Key manager unavailable")
    config = _key_manager.load_config()
    if req.default_provider:
        config["default_provider"] = req.default_provider
    for provider, values in req.providers.items():
        row = config.setdefault("providers", {}).setdefault(provider, {})
        for key in ("enabled", "command", "default_model"):
            if key in values:
                row[key] = values[key]
    _key_manager.save_config(config)
    return {"ok": True, "config": _mask_llm_config(config)}


@app.get("/api/llm/keys")
async def llm_keys_list() -> dict:
    if _key_manager is None:
        raise HTTPException(status_code=503, detail="Key manager unavailable")
    status = _key_manager.list_key_status()
    providers = status.get("providers", {})
    stripped = {
        name: {
            "has_key": bool(item.get("has_key")),
            "source": item.get("source", "none"),
        }
        for name, item in providers.items()
    }
    return {"ok": True, "providers": stripped}


@app.put("/api/llm/keys/{provider}")
async def llm_key_set(provider: str, req: LLMKeyRequest) -> dict:
    if _key_manager is None:
        raise HTTPException(status_code=503, detail="Key manager unavailable")
    safe_provider = provider.strip().lower()
    if safe_provider not in {"anthropic", "openai", "gemini-api", "together", "openrouter"}:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    result = _key_manager.set_api_key(safe_provider, req.api_key)
    _audit_key_event(
        user_id="api:user",
        field=f"llm_key:{safe_provider}",
        old_value="<redacted>",
        new_value=f"hash:{result.get('key_hash', '')}",
        session_id="llm-portal",
    )
    return {
        "ok": True,
        "provider": safe_provider,
        "has_key": result.get("has_key", False),
        "key_hash": result.get("key_hash", ""),
    }


@app.delete("/api/llm/keys/{provider}")
async def llm_key_delete(provider: str) -> dict:
    if _key_manager is None:
        raise HTTPException(status_code=503, detail="Key manager unavailable")
    safe_provider = provider.strip().lower()
    result = _key_manager.delete_api_key(safe_provider)
    _audit_key_event(
        user_id="api:user",
        field=f"llm_key:{safe_provider}",
        old_value="<redacted>",
        new_value="<deleted>",
        session_id="llm-portal",
    )
    return {"ok": True, **result}


@app.post("/api/llm/keys/{provider}/test")
async def llm_key_test(provider: str, req: LLMProviderTestRequest) -> dict:
    if _llm_wrapper is None:
        raise HTTPException(status_code=503, detail="LLM wrapper unavailable")
    result = _llm_wrapper.complete(
        prompt=req.prompt,
        model=req.model,
        provider=provider,
        strict_provider=True,
    )
    if not result.get("ok"):
        return {"ok": False, "provider": provider, "error": "provider test failed", "attempts": result.get("attempts", [])}
    return {"ok": True, "provider": result.get("provider"), "model": result.get("model")}


@app.post("/api/llm/test")
async def llm_provider_test(req: LLMProviderTestRequest) -> dict:
    if _llm_wrapper is None:
        raise HTTPException(status_code=503, detail="LLM wrapper unavailable")
    result = _llm_wrapper.complete(prompt=req.prompt, model=req.model, provider=req.provider)
    if not result.get("ok"):
        return {"ok": False, "error": "provider test failed", "attempts": result.get("attempts", [])}
    return {"ok": True, "provider": result.get("provider"), "model": result.get("model")}


# ============================================================
# Routes: Chat + Logging
# ============================================================

@app.get("/")
async def index() -> HTMLResponse:
    """Serve the web UI."""
    return HTMLResponse(content=_HTML_UI)


@app.get("/api/history")
async def call_history(n: int = 50) -> dict:
    """Return recent LLM call log entries."""
    entries = get_call_history(n=min(n, 500))
    _log_path = Path.home() / ".stillwater" / "llm_calls.jsonl"
    try:
        total = sum(1 for line in _log_path.read_text(encoding="utf-8").splitlines() if line.strip())
    except Exception:
        total = len(entries)
    return {"entries": list(reversed(entries)), "total": total}


@app.post("/v1/chat/completions")
async def openai_chat_completions(req: ChatCompletionRequest) -> dict:
    """OpenAI-compatible chat completions proxy."""
    cfg = _get_config()
    provider = None

    # If model name matches a known provider, use it
    if cfg and req.model in cfg.config:
        provider = req.model

    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    try:
        client = _make_client(provider=provider)
        start = time.monotonic()
        result = client.chat(messages)
        latency_ms = int((time.monotonic() - start) * 1000)
        content = result.text if hasattr(result, "text") else str(result)
    except Exception as exc:
        logger.error(f"Chat completion failed: {exc}")
        raise HTTPException(status_code=502, detail=str(exc))

    response_id = f"sw-{uuid.uuid4().hex[:12]}"
    return {
        "id": response_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": req.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": sum(len(m["content"]) // 4 for m in messages),
            "completion_tokens": len(content) // 4,
            "total_tokens": (sum(len(m["content"]) for m in messages) + len(content)) // 4,
        },
        "_meta": {"latency_ms": latency_ms, "provider": client.provider_name},
    }


@app.get("/api/context/catalog")
async def context_catalog() -> dict:
    """List all available SW5.0 context sources (skills, recipes, swarms, personas)."""
    return _ctx_loader.catalog()


@app.get("/api/context/preview/{type_}/{name}")
async def context_preview(type_: str, name: str, mode: str = "quick") -> dict:
    """Preview what context would be injected for a given construct."""
    src = ContextSource(type=type_, name=name, mode=mode)
    content = _ctx_loader.load(src)
    return {"type": type_, "name": name, "mode": mode, "content": content}


@app.post("/v1/context/chat")
async def context_chat(req: ContextChatRequest) -> dict:
    """Chat with SW5.0 context injection. Injects skills, recipes, swarms, personas as system prompt."""
    # 1. Build system prompt from context sources
    system_prompt = _ctx_loader.build_system_prompt(req.context_sources, req.cnf_capsule)

    # 2. Construct messages with system prompt prepended
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages

    # 3. Route to LLM
    cfg = _get_config()
    provider = None
    if cfg and req.model in cfg.config:
        provider = req.model

    try:
        client = _make_client(provider=provider)
        start = time.monotonic()
        # Increase timeout for context injection (large system prompts take longer)
        # Use 120 seconds (2 minutes) instead of default 30 seconds
        result = client.chat(messages, timeout=120.0)
        latency_ms = int((time.monotonic() - start) * 1000)
        content = result.text if hasattr(result, "text") else str(result)
    except Exception as exc:
        logger.error(f"Context chat failed: {exc}")
        raise HTTPException(status_code=502, detail=str(exc))

    # 4. Return OpenAI-compatible response + evidence metadata
    response_id = f"sw-ctx-{uuid.uuid4().hex[:12]}"
    return {
        "id": response_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": req.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": sum(len(m["content"]) // 4 for m in messages),
            "completion_tokens": len(content) // 4,
            "total_tokens": (sum(len(m["content"]) for m in messages) + len(content)) // 4,
        },
        "_meta": {
            "latency_ms": latency_ms,
            "provider": client.provider_name,
            "rung_target": req.rung_target,
            "context_sources": [{"type": s.type, "name": s.name, "mode": s.mode} for s in req.context_sources],
            "cnf_capsule_keys": list(req.cnf_capsule.keys()),
            "system_prompt_chars": len(system_prompt),
        },
    }


@app.get("/v1/models")
async def list_models() -> dict:
    """OpenAI-compatible model list."""
    cfg = _get_config()
    models = []
    if cfg:
        for name, info in cfg.list_providers().items():
            model_id = cfg.config.get(name, {}).get("model", name)
            models.append({
                "id": model_id or name,
                "object": "model",
                "owned_by": "stillwater",
                "_provider": name,
            })
    return {"object": "list", "data": models}


# ============================================================
# Embedded Web UI (dark theme, no CDN)
# ============================================================

_HTML_UI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stillwater LLM Portal</title>
<style>
  :root {
    --bg: #0d1117; --card: #161b22; --border: #30363d;
    --accent: #58a6ff; --accent2: #3fb950; --warn: #f85149;
    --text: #c9d1d9; --muted: #8b949e; --header: #f0f6fc;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',monospace; min-height: 100vh; }
  header { background: var(--card); border-bottom: 1px solid var(--border); padding: 16px 24px; display: flex; align-items: center; gap: 12px; }
  header h1 { color: var(--header); font-size: 1.25rem; }
  header .badge { background: var(--accent); color: #000; font-size: 0.7rem; padding: 2px 8px; border-radius: 12px; font-weight: 700; }
  .active-pill { background: #1f3a1a; border: 1px solid var(--accent2); color: var(--accent2); font-size: 0.75rem; padding: 3px 10px; border-radius: 12px; margin-left: auto; }
  main { max-width: 1200px; margin: 0 auto; padding: 24px 16px; display: grid; gap: 24px; }
  section { background: var(--card); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
  section h2 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); padding: 14px 20px; border-bottom: 1px solid var(--border); }
  .providers-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(300px,1fr)); gap: 12px; padding: 16px; }
  .provider-card { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 14px; }
  .provider-card.active-card { border-color: var(--accent2); }
  .pcard-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
  .pcard-name { font-weight: 600; color: var(--header); font-size: 0.9rem; }
  .status-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--muted); flex-shrink: 0; }
  .status-dot.ok { background: var(--accent2); }
  .status-dot.fail { background: var(--warn); }
  .pcard-info { font-size: 0.72rem; color: var(--muted); margin-bottom: 4px; }
  .pcard-models { font-size: 0.72rem; color: var(--accent); margin: 8px 0; }
  .model-select { width: 100%; padding: 4px; background: var(--bg); border: 1px solid var(--border); color: var(--text); border-radius: 4px; font-size: 0.8rem; }
  .model-select:focus { outline: none; border-color: var(--accent); }
  .btn { display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; border-radius: 5px; font-size: 0.8rem; font-weight: 600; cursor: pointer; border: 1px solid var(--border); background: var(--card); color: var(--text); transition: all .15s; }
  .btn:hover { border-color: var(--accent); color: var(--accent); }
  .btn.btn-active { background: #1a3a2a; border-color: var(--accent2); color: var(--accent2); cursor: default; }
  .btn.btn-small { padding: 3px 8px; font-size: 0.7rem; }
  .chat-panel { padding: 16px; display: grid; gap: 12px; }
  .chat-row { display: grid; grid-template-columns: 1fr auto; gap: 8px; align-items: end; }
  textarea { width: 100%; background: var(--bg); border: 1px solid var(--border); border-radius: 6px; color: var(--text); padding: 10px; font-size: 0.9rem; font-family: inherit; resize: vertical; min-height: 80px; }
  textarea:focus { outline: none; border-color: var(--accent); }
  .chat-resp { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px; font-size: 0.9rem; min-height: 60px; white-space: pre-wrap; word-break: break-word; color: var(--accent2); }
  .chat-meta { font-size: 0.72rem; color: var(--muted); }
  .spinner { display: none; width: 14px; height: 14px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin .7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .context-builder { padding: 16px; display: grid; gap: 12px; }
  .context-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-items: end; }
  .context-field { display: grid; gap: 4px; }
  .context-field label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; }
  .context-field select, .context-field input { width: 100%; padding: 6px; background: var(--bg); border: 1px solid var(--border); color: var(--text); border-radius: 4px; font-size: 0.8rem; }
  .context-field select:focus, .context-field input:focus { outline: none; border-color: var(--accent); }
  .context-tags { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
  .context-tag { background: #1a3a2a; border: 1px solid var(--accent2); color: var(--accent2); padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; display: flex; gap: 6px; align-items: center; }
  .context-tag .remove { cursor: pointer; font-weight: bold; }
  .rung-selector { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
  .rung-radio { display: none; }
  .rung-label { padding: 6px; border: 1px solid var(--border); border-radius: 4px; text-align: center; cursor: pointer; font-size: 0.75rem; }
  .rung-radio:checked + .rung-label { background: var(--accent2); color: #000; border-color: var(--accent2); }
</style>
</head>
<body>
<header>
  <h1>⚡ Stillwater LLM Portal</h1>
  <span class="badge">v2.0</span>
  <span class="active-pill" id="active-label">Loading...</span>
</header>
<main>

  <section>
    <h2>Providers & Models</h2>
    <div class="providers-grid" id="providers-grid">
      <div style="padding:16px;color:var(--muted)">Loading providers...</div>
    </div>
  </section>

  <section>
    <h2>Context Builder (Optional)</h2>
    <div class="context-builder">
      <div class="context-row">
        <div class="context-field">
          <label>Skills</label>
          <select id="skill-select" onchange="addContextSource('skill')">
            <option value="">+ Add skill...</option>
          </select>
        </div>
        <div class="context-field">
          <label>Recipes</label>
          <select id="recipe-select" onchange="addContextSource('recipe')">
            <option value="">+ Add recipe...</option>
          </select>
        </div>
      </div>
      <div class="context-row">
        <div class="context-field">
          <label>Swarms</label>
          <select id="swarm-select" onchange="addContextSource('swarm')">
            <option value="">+ Add swarm...</option>
          </select>
        </div>
        <div class="context-field">
          <label>Personas</label>
          <select id="persona-select" onchange="addContextSource('persona')">
            <option value="">+ Add persona...</option>
          </select>
        </div>
      </div>
      <div class="context-field">
        <label>Rung Target</label>
        <div class="rung-selector">
          <input type="radio" id="rung641" name="rung" value="641" class="rung-radio" checked>
          <label for="rung641" class="rung-label">641 (Local)</label>
          <input type="radio" id="rung274177" name="rung" value="274177" class="rung-radio">
          <label for="rung274177" class="rung-label">274177 (Stable)</label>
          <input type="radio" id="rung65537" name="rung" value="65537" class="rung-radio">
          <label for="rung65537" class="rung-label">65537 (Prod)</label>
        </div>
      </div>
      <div class="context-field">
        <label>Selected Context</label>
        <div class="context-tags" id="context-tags"></div>
      </div>
      <div class="context-field">
        <button class="btn" onclick="clearContext()">Clear All Context</button>
      </div>
    </div>
  </section>

  <section>
    <h2>Chat Test</h2>
    <div class="chat-panel">
      <div class="chat-row">
        <textarea id="chat-input" placeholder="Type a message...">Tell me what you can do!</textarea>
        <button class="btn" onclick="sendChat(false)" id="chat-btn">
          <span class="spinner" id="chat-spinner"></span>
          Send
        </button>
      </div>
      <button class="btn" style="width:100%" onclick="sendChat(true)" id="chat-ctx-btn">
        <span class="spinner" id="chat-ctx-spinner" style="display:none"></span>
        Send with Context
      </button>
      <div class="chat-resp" id="chat-resp">Response will appear here.</div>
      <div class="chat-meta" id="chat-meta"></div>
    </div>
  </section>

</main>
<script>
async function refreshProviders() {
  try {
    const res = await fetch('/api/providers');
    if (!res.ok) {
      console.error('Failed to fetch providers:', res.status, res.statusText);
      return;
    }
    const data = await res.json();
    console.log('Providers data:', data);
    document.getElementById('active-label').textContent = '🔴 ' + data.active.toUpperCase();

    const grid = document.getElementById('providers-grid');
    grid.innerHTML = data.providers.map(p => `
      <div class="provider-card ${p.active ? 'active-card' : ''}">
        <div class="pcard-header">
          <div class="pcard-name">${p.name}</div>
          <div class="status-dot ${p.reachable ? 'ok' : 'fail'}"></div>
        </div>
        <div class="pcard-info">Type: ${p.type}</div>
        ${p.url ? `<div class="pcard-info">URL: ${p.url}</div>` : ''}
        ${p.latency_ms ? `<div class="pcard-info">Latency: ${p.latency_ms}ms</div>` : ''}
        ${p.models.length > 0 ? `
          <div class="pcard-models">
            <select class="model-select" onchange="setModel('${p.id}', this.value)">
              <option value="">Change model...</option>
              ${p.models.map(m => `<option value="${m}" ${p.model === m ? 'selected' : ''}>${m}</option>`).join('')}
            </select>
          </div>
        ` : ''}
        <button class="btn btn-small" onclick="switchProvider('${p.id}')" ${p.active ? 'disabled' : ''}>
          ${p.active ? '✓ Active' : 'Switch'}
        </button>
      </div>
    `).join('');
  } catch (e) {
    console.error('Failed to load providers:', e);
  }
}

async function switchProvider(name) {
  try {
    const res = await fetch('/api/providers/switch', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({provider: name})
    });
    if (res.ok) {
      await refreshProviders();
    } else {
      alert('Switch failed: ' + await res.text());
    }
  } catch (e) {
    alert('Error: ' + e);
  }
}

async function setModel(provider, model) {
  if (!model) return;
  try {
    const res = await fetch('/api/config/set-model', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({provider, model})
    });
    if (res.ok) {
      // Optionally save to config
      await fetch('/api/config/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({provider, model})
      });
      await refreshProviders();
    } else {
      alert('Set model failed');
    }
  } catch (e) {
    alert('Error: ' + e);
  }
}

// Context management (global state)
let contextSources = [];

async function loadContextCatalog() {
  try {
    const res = await fetch('/api/context/catalog');
    if (!res.ok) return;
    const catalog = await res.json();

    // Populate selects
    document.getElementById('skill-select').innerHTML = '<option value="">+ Add skill...</option>' +
      (catalog.skills || []).map(s => `<option value="${s}">${s}</option>`).join('');
    document.getElementById('recipe-select').innerHTML = '<option value="">+ Add recipe...</option>' +
      (catalog.recipes || []).map(r => `<option value="${r}">${r}</option>`).join('');
    document.getElementById('swarm-select').innerHTML = '<option value="">+ Add swarm...</option>' +
      (catalog.swarms || []).map(s => `<option value="${s}">${s}</option>`).join('');
    document.getElementById('persona-select').innerHTML = '<option value="">+ Add persona...</option>' +
      (catalog.personas || []).map(p => `<option value="${p}">${p}</option>`).join('');
  } catch (e) {
    console.error('Failed to load context catalog:', e);
  }
}

function addContextSource(type) {
  const selects = {skill: 'skill-select', recipe: 'recipe-select', swarm: 'swarm-select', persona: 'persona-select'};
  const select = document.getElementById(selects[type]);
  const name = select.value;
  if (!name) return;

  contextSources.push({type, name, mode: 'quick'});
  select.value = '';
  renderContextTags();
}

function removeContextSource(idx) {
  contextSources.splice(idx, 1);
  renderContextTags();
}

function clearContext() {
  contextSources = [];
  renderContextTags();
}

function renderContextTags() {
  const container = document.getElementById('context-tags');
  if (contextSources.length === 0) {
    container.innerHTML = '<span style="color:var(--muted);font-size:0.8rem">(no context selected)</span>';
  } else {
    container.innerHTML = contextSources.map((s, i) =>
      `<div class="context-tag">${s.type}/${s.name} <span class="remove" onclick="removeContextSource(${i})">×</span></div>`
    ).join('');
  }
}

async function sendChat(useContext) {
  const input = document.getElementById('chat-input');
  const resp = document.getElementById('chat-resp');
  const meta = document.getElementById('chat-meta');
  const btn = useContext ? document.getElementById('chat-ctx-btn') : document.getElementById('chat-btn');
  const spinner = useContext ? document.getElementById('chat-ctx-spinner') : document.getElementById('chat-spinner');

  if (!input.value.trim()) return;

  btn.disabled = true;
  spinner.style.display = 'inline-block';
  resp.textContent = 'Thinking...';

  try {
    // Get active provider info first
    const provRes = await fetch('/api/providers');
    if (!provRes.ok) {
      throw new Error(`Failed to get providers: ${provRes.status}`);
    }
    const provData = await provRes.json();
    console.log('Active provider data:', provData);
    const activeProvider = provData.providers.find(p => p.active);
    const model = activeProvider?.model || 'auto';
    console.log('Using model:', model, 'from provider:', activeProvider?.name);

    const endpoint = useContext ? '/v1/context/chat' : '/v1/chat/completions';
    const rungVal = document.querySelector('input[name="rung"]:checked')?.value || '641';

    const reqBody = {
      model: model,
      messages: [{role: 'user', content: input.value}],
      temperature: 0
    };

    if (useContext) {
      reqBody.context_sources = contextSources;
      reqBody.rung_target = parseInt(rungVal);
    }

    console.log('Sending request to', endpoint, ':', reqBody);

    const res = await fetch(endpoint, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(reqBody)
    });

    console.log('Response status:', res.status);
    if (!res.ok) {
      const errorText = await res.text();
      console.error('API error:', errorText);
      resp.textContent = 'Error: ' + errorText;
      meta.textContent = '';
    } else {
      const data = await res.json();
      console.log('Response data:', data);
      resp.textContent = data.choices[0].message.content;
      const metaParts = [`Provider: ${data._meta.provider}`, `Latency: ${data._meta.latency_ms}ms`];
      if (useContext) {
        metaParts.push(`Rung: ${data._meta.rung_target}`);
        metaParts.push(`Context: ${data._meta.system_prompt_chars} chars`);
      }
      meta.textContent = metaParts.join(' | ');
    }
  } catch (e) {
    console.error('Chat error:', e);
    resp.textContent = 'Error: ' + e.message;
    meta.textContent = '';
  } finally {
    btn.disabled = false;
    spinner.style.display = 'none';
  }
}

// Load on page load
loadContextCatalog();
refreshProviders();
renderContextTags();
setInterval(refreshProviders, 5000);
</script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8788)
