#!/usr/bin/env python3
"""
Stillwater LLM Portal
Auth: 65537 | Status: STABLE | Version: 1.1.0 | Port: 8788

Web UI + OpenAI-compatible proxy for all LLM providers.
Reads llm_config.yaml to discover and route to any configured backend.

Phase 3 additions:
  - POST /api/providers/auth   Accept user-supplied API key (AES-256-GCM, memory-only)
  - GET  /api/providers        Extended: includes models[] + authenticated status
  - SessionManager             Per-process in-memory encrypted key store

Start:
    bash admin/start-llm-portal.sh
    # or directly:
    cd /path/to/stillwater
    uvicorn admin.llm_portal:app --host 0.0.0.0 --port 8788

Routes:
    GET  /                      Web UI (embedded dark-theme HTML)
    GET  /api/health            {"status": "ok", "active_provider": str}
    GET  /api/providers         All providers + reachability + models + authenticated
    POST /api/providers/switch  Switch active provider (in-session)
    POST /api/providers/auth    Supply API key for a provider (encrypted in session)
    GET  /api/history           Recent call log from ~/.stillwater/llm_calls.jsonl
    POST /v1/chat/completions   OpenAI-compatible proxy
    GET  /v1/models             OpenAI-compatible model list

Security:
    API keys supplied via /api/providers/auth are:
      - Encrypted with AES-256-GCM (256-bit key, 96-bit nonce per write)
      - Stored in process memory only (never written to disk, logs, or repr)
      - Wiped when the process exits (no persistence)
"""

from __future__ import annotations

import sys
import time
import uuid
from pathlib import Path
from typing import Any, Optional

# Add cli/src to path for llm_config_manager + stillwater package
_CLI_SRC = Path(__file__).parent.parent / "cli" / "src"
if str(_CLI_SRC) not in sys.path:
    sys.path.insert(0, str(_CLI_SRC))

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

try:
    from stillwater.llm_client import LLMClient, get_call_history  # type: ignore
except ImportError as e:
    raise ImportError(f"Could not import stillwater.llm_client: {e}") from e

try:
    from llm_config_manager import LLMConfigManager  # type: ignore
except ImportError:
    LLMConfigManager = None  # type: ignore

# Session manager import (Phase 3: encrypted key storage)
try:
    from admin.session_manager import SessionManager  # type: ignore
except ImportError:
    try:
        # Fallback for direct uvicorn invocation from repo root
        from session_manager import SessionManager  # type: ignore
    except ImportError:
        SessionManager = None  # type: ignore


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Stillwater LLM Portal",
    description="Universal LLM proxy with web UI. Auth: 65537.",
    version="1.1.0",
)

# Shared config manager (in-memory provider switching)
_config: Optional[Any] = None

# Shared session manager (Phase 3: AES-256-GCM key storage, memory-only)
_session: Optional[Any] = None


def _get_session() -> Optional[Any]:
    global _session
    if _session is None and SessionManager is not None:
        _session = SessionManager()
    return _session


def _get_config() -> Optional[Any]:
    global _config
    if _config is None and LLMConfigManager is not None:
        try:
            _config = LLMConfigManager()
        except Exception:
            pass
    return _config


def _make_client(provider: Optional[str] = None) -> LLMClient:
    """Create an LLMClient using the current active provider."""
    cfg = _get_config()
    if provider:
        return LLMClient(provider=provider)
    if cfg:
        return LLMClient(provider=cfg.active_provider)
    return LLMClient(provider="offline")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class SwitchProviderRequest(BaseModel):
    provider: str


class AuthProviderRequest(BaseModel):
    """Phase 3: Supply an API key for a provider (stored encrypted in session)."""
    provider: str
    api_key: str  # plaintext key from user — encrypted immediately on receipt


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "auto"
    messages: list[ChatMessage]
    temperature: float = 0.0
    max_tokens: int = 4096
    stream: bool = False


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """Serve the embedded dark-theme web UI."""
    return HTMLResponse(content=_HTML_UI)


@app.get("/api/health")
async def health() -> dict:
    cfg = _get_config()
    active = cfg.active_provider if cfg else "offline"
    return {"status": "ok", "active_provider": active, "portal_version": "1.1.0"}


@app.get("/api/providers")
async def list_providers() -> dict:
    """
    List all configured providers with live reachability status.

    Phase 3 additions per provider entry:
      - authenticated: bool — whether a user API key has been supplied via /api/providers/auth
      - requires_api_key: bool — from llm_config.yaml
    """
    cfg = _get_config()
    if cfg is None:
        return {"providers": [], "active": "offline"}

    session = _get_session()

    providers = []
    all_providers = cfg.list_providers()
    for name, info in all_providers.items():
        is_active = name == cfg.active_provider
        provider_type = info.get("type", "")
        requires_key = info.get("requires_api_key", False)

        # Quick reachability check (non-blocking, short timeout)
        reachable = None
        latency_ms = None
        if provider_type == "offline":
            reachable = True
            latency_ms = 0
        # Only probe localhost providers by default (fast); skip remote APIs
        elif provider_type == "http" and ("localhost" in info.get("url", "") or "127.0.0.1" in info.get("url", "")):
            try:
                import httpx
                start = time.monotonic()
                with httpx.Client(timeout=2.0) as client:
                    r = client.get(f"{info['url']}/")
                    if r.status_code in (200, 404, 405):
                        reachable = True
                        latency_ms = int((time.monotonic() - start) * 1000)
            except Exception:
                reachable = False

        # Phase 3: authenticated status from session
        authenticated = session.has_key(name) if session is not None else False

        providers.append({
            "id": name,
            "name": info.get("name", name),
            "url": info.get("url", ""),
            "type": provider_type,
            "model": cfg.config.get(name, {}).get("model", ""),
            "active": is_active,
            "reachable": reachable,
            "latency_ms": latency_ms,
            # Phase 3 additions
            "requires_api_key": requires_key,
            "authenticated": authenticated,
        })

    return {"providers": providers, "active": cfg.active_provider}


@app.post("/api/providers/auth")
async def auth_provider(req: AuthProviderRequest) -> dict:
    """
    Phase 3: Supply an API key for a provider.

    The key is immediately encrypted with AES-256-GCM and stored in process
    memory. It is NEVER written to disk, logged, or returned in any response.

    Returns:
        {"status": "authenticated", "provider": str}

    Errors:
        400 — unknown provider
        400 — empty API key (null != valid key)
        422 — missing required fields (Pydantic validation)
        503 — session manager unavailable
    """
    cfg = _get_config()
    session = _get_session()

    if session is None:
        raise HTTPException(status_code=503, detail="Session manager unavailable")

    # Validate provider exists in config
    if cfg is not None:
        known_providers = set(cfg.list_providers().keys())
        if req.provider not in known_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown provider: {req.provider!r}. Known: {sorted(known_providers)}",
            )

    # Validate key is non-empty (null != zero — never coerce)
    if not req.api_key or not req.api_key.strip():
        raise HTTPException(
            status_code=400,
            detail="api_key must be a non-empty string",
        )

    try:
        session.store_key(req.provider, req.api_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Return no key material — only status
    return {"status": "authenticated", "provider": req.provider}


@app.post("/api/providers/switch")
async def switch_provider(req: SwitchProviderRequest) -> dict:
    """Switch the active provider for this portal session."""
    cfg = _get_config()
    if cfg is None:
        raise HTTPException(status_code=503, detail="Config manager unavailable")
    try:
        cfg.switch_provider(req.provider)
        return {"ok": True, "active_provider": cfg.active_provider}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/history")
async def call_history(n: int = 50) -> dict:
    """Return recent LLM call log entries."""
    entries = get_call_history(n=min(n, 500))
    return {"entries": list(reversed(entries)), "total": len(entries)}


@app.post("/v1/chat/completions")
async def openai_chat_completions(req: ChatCompletionRequest) -> dict:
    """
    OpenAI-compatible chat completions proxy.
    Routes to the active provider (or the model name if it matches a provider).
    """
    # Determine provider: if model name matches a known provider, use it
    cfg = _get_config()
    provider = None
    if cfg and req.model in cfg.config:
        provider = req.model

    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    try:
        client = _make_client(provider=provider)
        start = time.monotonic()
        content = client.chat(messages)
        latency_ms = int((time.monotonic() - start) * 1000)
    except Exception as exc:
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


@app.get("/v1/models")
async def list_models() -> dict:
    """OpenAI-compatible model list (maps providers → model IDs)."""
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


# ---------------------------------------------------------------------------
# Embedded HTML Web UI (dark theme, no CDN)
# ---------------------------------------------------------------------------

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
  main { max-width: 1100px; margin: 0 auto; padding: 24px 16px; display: grid; gap: 24px; }
  section { background: var(--card); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
  section h2 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); padding: 14px 20px; border-bottom: 1px solid var(--border); }
  .providers-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(260px,1fr)); gap: 12px; padding: 16px; }
  .provider-card { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 14px; }
  .provider-card.active-card { border-color: var(--accent2); }
  .pcard-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
  .pcard-name { font-weight: 600; color: var(--header); font-size: 0.9rem; }
  .status-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--muted); flex-shrink: 0; }
  .status-dot.ok { background: var(--accent2); }
  .status-dot.fail { background: var(--warn); }
  .pcard-url { font-size: 0.72rem; color: var(--muted); margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .pcard-model { font-size: 0.72rem; color: var(--accent); margin-bottom: 10px; }
  .btn { display: inline-flex; align-items: center; gap: 6px; padding: 5px 14px; border-radius: 5px; font-size: 0.8rem; font-weight: 600; cursor: pointer; border: 1px solid var(--border); background: var(--card); color: var(--text); transition: all .15s; }
  .btn:hover { border-color: var(--accent); color: var(--accent); }
  .btn.btn-active { background: #1a3a2a; border-color: var(--accent2); color: var(--accent2); cursor: default; }
  .btn.btn-primary { background: var(--accent); border-color: var(--accent); color: #000; }
  .btn.btn-primary:hover { background: #79b8ff; }
  .chat-panel { padding: 16px; display: grid; gap: 12px; }
  .chat-row { display: grid; grid-template-columns: 1fr auto; gap: 8px; align-items: end; }
  textarea { width: 100%; background: var(--bg); border: 1px solid var(--border); border-radius: 6px; color: var(--text); padding: 10px; font-size: 0.9rem; font-family: inherit; resize: vertical; min-height: 80px; }
  textarea:focus { outline: none; border-color: var(--accent); }
  .chat-resp { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px; font-size: 0.9rem; min-height: 60px; white-space: pre-wrap; word-break: break-word; color: var(--accent2); }
  .chat-meta { font-size: 0.72rem; color: var(--muted); }
  table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
  th { text-align: left; padding: 8px 16px; color: var(--muted); border-bottom: 1px solid var(--border); font-weight: 600; }
  td { padding: 7px 16px; border-bottom: 1px solid #21262d; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #1c2128; }
  .tag { display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 0.7rem; font-weight: 600; }
  .tag-ok { background: #1a3a2a; color: var(--accent2); }
  .tag-err { background: #3a1a1a; color: var(--warn); }
  .spinner { display: none; width: 16px; height: 16px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin .7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>
<header>
  <h1>⚡ Stillwater LLM Portal</h1>
  <span class="badge">v1.0</span>
  <span class="active-pill" id="active-label">Loading...</span>
</header>
<main>

  <section>
    <h2>Providers</h2>
    <div class="providers-grid" id="providers-grid">
      <div style="padding:16px;color:var(--muted)">Loading providers...</div>
    </div>
  </section>

  <section>
    <h2>Chat Test</h2>
    <div class="chat-panel">
      <div class="chat-row">
        <textarea id="chat-input" placeholder="Type a message... (Shift+Enter for newline, Enter to send)">Hello! What can you do?</textarea>
        <button class="btn btn-primary" onclick="sendChat()" id="chat-btn">
          <span class="spinner" id="chat-spinner"></span>
          Send
        </button>
      </div>
      <div class="chat-resp" id="chat-resp">Response will appear here.</div>
      <div class="chat-meta" id="chat-meta"></div>
    </div>
  </section>

  <section>
    <h2>Call History</h2>
    <table>
      <thead><tr>
        <th>Time</th><th>Provider</th><th>Model</th><th>Latency</th><th>Prompt</th><th>Response</th><th>Status</th>
      </tr></thead>
      <tbody id="history-tbody"><tr><td colspan="7" style="color:var(--muted);text-align:center;padding:16px">Loading...</td></tr></tbody>
    </table>
  </section>

</main>
<script>
let activeProvider = 'offline';

async function loadProviders() {
  const r = await fetch('/api/providers');
  const data = await r.json();
  activeProvider = data.active;
  document.getElementById('active-label').textContent = 'Active: ' + data.active;
  const grid = document.getElementById('providers-grid');
  grid.innerHTML = '';
  for (const p of data.providers) {
    const isActive = p.active;
    const dotClass = p.reachable === true ? 'ok' : p.reachable === false ? 'fail' : '';
    const latency = p.latency_ms !== null ? p.latency_ms + 'ms' : '?';
    grid.innerHTML += `
      <div class="provider-card ${isActive ? 'active-card' : ''}">
        <div class="pcard-header">
          <span class="pcard-name">${p.name}</span>
          <span class="status-dot ${dotClass}" title="${p.reachable === true ? 'Reachable ('+latency+')' : p.reachable === false ? 'Unreachable' : 'Not probed'}"></span>
        </div>
        <div class="pcard-url">${p.url || '(local)'}</div>
        <div class="pcard-model">${p.model || p.type}</div>
        ${isActive
          ? '<button class="btn btn-active" disabled>✓ Active</button>'
          : `<button class="btn" onclick="setProvider('${p.id}')">Set Active</button>`
        }
      </div>`;
  }
}

async function setProvider(id) {
  const r = await fetch('/api/providers/switch', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({provider: id})
  });
  if (r.ok) { await loadProviders(); }
  else { alert('Failed to switch: ' + (await r.json()).detail); }
}

async function sendChat() {
  const input = document.getElementById('chat-input');
  const resp = document.getElementById('chat-resp');
  const meta = document.getElementById('chat-meta');
  const btn = document.getElementById('chat-btn');
  const spinner = document.getElementById('chat-spinner');
  const msg = input.value.trim();
  if (!msg) return;

  btn.disabled = true;
  spinner.style.display = 'inline-block';
  resp.textContent = 'Calling ' + activeProvider + '...';
  meta.textContent = '';

  const start = Date.now();
  try {
    const r = await fetch('/v1/chat/completions', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({model: 'auto', messages: [{role:'user', content: msg}]})
    });
    const data = await r.json();
    if (r.ok) {
      resp.textContent = data.choices[0].message.content;
      meta.textContent = 'Provider: ' + (data._meta?.provider || '?') + ' | Latency: ' + (data._meta?.latency_ms || (Date.now()-start)) + 'ms';
    } else {
      resp.textContent = 'Error: ' + (data.detail || JSON.stringify(data));
    }
  } catch(e) {
    resp.textContent = 'Network error: ' + e.message;
  }
  btn.disabled = false;
  spinner.style.display = 'none';
  loadHistory();
}

async function loadHistory() {
  const r = await fetch('/api/history?n=20');
  const data = await r.json();
  const tbody = document.getElementById('history-tbody');
  if (!data.entries.length) {
    tbody.innerHTML = '<tr><td colspan="7" style="color:var(--muted);text-align:center;padding:12px">No calls yet</td></tr>';
    return;
  }
  tbody.innerHTML = data.entries.map(e => {
    const ts = new Date(e.ts).toLocaleTimeString();
    const status = e.error ? `<span class="tag tag-err">ERR</span>` : `<span class="tag tag-ok">OK</span>`;
    return `<tr>
      <td>${ts}</td>
      <td>${e.provider}</td>
      <td style="color:var(--muted)">${e.model || '-'}</td>
      <td>${e.latency_ms}ms</td>
      <td>${e.prompt_chars}c</td>
      <td>${e.response_chars}c</td>
      <td>${status}</td>
    </tr>`;
  }).join('');
}

document.getElementById('chat-input').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); }
});

// Init
loadProviders();
loadHistory();
setInterval(loadHistory, 10000);
</script>
</body>
</html>"""
