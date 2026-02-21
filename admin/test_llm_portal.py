"""
Tests for the Stillwater LLM Portal.
Auth: 65537 | Rung target: 641 (local correctness; offline provider, zero network)

Run:
    pytest admin/test_llm_portal.py -v

All tests use the "offline" provider — no network calls required.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure cli/src is on the path before importing portal
_CLI_SRC = Path(__file__).parent.parent / "cli" / "src"
if str(_CLI_SRC) not in sys.path:
    sys.path.insert(0, str(_CLI_SRC))

_REPO_ROOT = Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi.testclient import TestClient

from admin.llm_portal import app  # type: ignore

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health():
    """Portal must return status=ok."""
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "active_provider" in data
    assert "portal_version" in data


# ---------------------------------------------------------------------------
# Provider list
# ---------------------------------------------------------------------------

def test_list_providers_returns_multiple():
    """At least 7 providers should be configured (offline + 7 in llm_config.yaml)."""
    r = client.get("/api/providers")
    assert r.status_code == 200
    data = r.json()
    assert "providers" in data
    assert "active" in data
    assert len(data["providers"]) >= 7, f"Expected >=7 providers, got {len(data['providers'])}"


def test_list_providers_have_required_fields():
    """Each provider entry must have id, name, url, type, active fields."""
    r = client.get("/api/providers")
    data = r.json()
    for p in data["providers"]:
        for field in ("id", "name", "url", "type", "active"):
            assert field in p, f"Missing field {field!r} in provider {p}"


def test_offline_provider_is_listed():
    """The 'offline' provider must be present."""
    r = client.get("/api/providers")
    data = r.json()
    ids = [p["id"] for p in data["providers"]]
    assert "offline" in ids, f"'offline' not in providers: {ids}"


# ---------------------------------------------------------------------------
# Provider switching
# ---------------------------------------------------------------------------

def test_switch_to_offline():
    """Switching to offline must succeed and report active=offline."""
    r = client.post("/api/providers/switch", json={"provider": "offline"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["active_provider"] == "offline"


def test_switch_to_invalid_provider_returns_400():
    """Switching to a non-existent provider must return 400."""
    r = client.post("/api/providers/switch", json={"provider": "nonexistent-xyz-99"})
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# OpenAI-compatible proxy (offline)
# ---------------------------------------------------------------------------

def _ensure_offline():
    """Switch to offline before testing completions."""
    client.post("/api/providers/switch", json={"provider": "offline"})


def test_openai_chat_completions_offline():
    """POST /v1/chat/completions with offline provider must return valid response."""
    _ensure_offline()
    r = client.post("/v1/chat/completions", json={
        "model": "offline",
        "messages": [{"role": "user", "content": "Hello, what can you do?"}],
    })
    assert r.status_code == 200
    data = r.json()
    assert "choices" in data
    assert len(data["choices"]) == 1
    assert "message" in data["choices"][0]
    assert "content" in data["choices"][0]["message"]
    content = data["choices"][0]["message"]["content"]
    assert len(content) > 0, "Response content must be non-empty"
    assert "offline" in content.lower() or "Hello" in content or len(content) > 0


def test_openai_chat_completions_response_shape():
    """Response must have OpenAI-compatible shape."""
    _ensure_offline()
    r = client.post("/v1/chat/completions", json={
        "model": "offline",
        "messages": [{"role": "user", "content": "ping"}],
    })
    data = r.json()
    assert "id" in data
    assert data["id"].startswith("sw-")
    assert data["object"] == "chat.completion"
    assert "created" in data
    assert "usage" in data


def test_openai_models_list():
    """GET /v1/models must return list with at least one model."""
    r = client.get("/v1/models")
    assert r.status_code == 200
    data = r.json()
    assert data["object"] == "list"
    assert len(data["data"]) >= 1


# ---------------------------------------------------------------------------
# Call history
# ---------------------------------------------------------------------------

def test_call_history_returns_list():
    """GET /api/history must return a list."""
    r = client.get("/api/history")
    assert r.status_code == 200
    data = r.json()
    assert "entries" in data
    assert isinstance(data["entries"], list)
    assert "total" in data


def test_call_logged_after_completion():
    """After making a completion, history must grow."""
    _ensure_offline()
    r0 = client.get("/api/history?n=500")
    before = r0.json()["total"]

    client.post("/v1/chat/completions", json={
        "model": "offline",
        "messages": [{"role": "user", "content": "log test call " + "x" * 20}],
    })

    r1 = client.get("/api/history?n=500")
    after = r1.json()["total"]
    assert after > before, f"History didn't grow: before={before}, after={after}"


# ---------------------------------------------------------------------------
# Unit tests for llm_client directly
# ---------------------------------------------------------------------------

def test_llm_client_offline_direct():
    """LLMClient with offline provider must return without error."""
    from stillwater.llm_client import LLMClient  # type: ignore
    c = LLMClient(provider="offline")
    result = c.call("What is 2+2?")
    assert isinstance(result, str)
    assert len(result) > 0
    assert "offline" in result.lower()


def test_llm_call_convenience_offline():
    """Top-level llm_call() with offline provider must work."""
    from stillwater.llm_client import llm_call  # type: ignore
    result = llm_call("Hello world", provider="offline")
    assert isinstance(result, str)
    assert len(result) > 0


def test_llm_chat_convenience_offline():
    """Top-level llm_chat() with offline messages must work."""
    from stillwater.llm_client import llm_chat  # type: ignore
    msgs = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Test message"},
    ]
    result = llm_chat(msgs, provider="offline")
    assert isinstance(result, str)


def test_llm_client_test_connection_offline():
    """test_connection() on offline provider must return True."""
    from stillwater.llm_client import LLMClient  # type: ignore
    c = LLMClient(provider="offline")
    ok, latency_ms, error = c.test_connection()
    assert ok is True
    assert error is None
    assert latency_ms >= 0


def test_get_call_history():
    """get_call_history() must return a list."""
    from stillwater.llm_client import get_call_history, llm_call  # type: ignore
    # Make a call to ensure at least one entry
    llm_call("history test", provider="offline")
    history = get_call_history(n=10)
    assert isinstance(history, list)
    assert len(history) >= 1
    entry = history[-1]
    for field in ("ts", "provider", "model", "prompt_chars", "response_chars", "latency_ms"):
        assert field in entry, f"Missing field {field!r} in history entry"


# ---------------------------------------------------------------------------
# Web UI
# ---------------------------------------------------------------------------

def test_root_returns_html():
    """GET / must return HTML."""
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "Stillwater LLM Portal" in r.text
    assert "providers-grid" in r.text
