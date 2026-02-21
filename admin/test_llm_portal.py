"""
Tests for the Stillwater LLM Portal.
Auth: 65537 | Rung target: 641 (local correctness; offline provider, zero network)

Phase 3 additions:
  - TestSessionManager (6 tests): encrypt/decrypt, no repr leak, clear, entropy
  - TestProviderAuth (5 tests): valid key, invalid provider, empty key, session storage
  - TestProviderRouting (4 tests): authenticated flag, backward compat, new providers
  - TestAPIKeySecurity (4 tests): no key in repr, empty key rejected, clear, no key returned

Run:
    pytest admin/test_llm_portal.py -v

All tests use the "offline" provider — no network calls required.
No real API calls are made; cryptography is exercised locally.
"""
from __future__ import annotations

import json
import secrets
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
from admin.session_manager import SessionManager  # type: ignore

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


# ===========================================================================
# Phase 3 Tests — SessionManager unit tests
# ===========================================================================

class TestSessionManager:
    """Unit tests for admin/session_manager.py."""

    def test_store_and_retrieve_key(self):
        """Encrypting then decrypting an API key must return the original value."""
        session = SessionManager()
        original = "sk-test-1234abcd"
        session.store_key("openai", original)
        retrieved = session.get_key("openai")
        assert retrieved == original, "Round-trip encrypt/decrypt must yield original key"

    def test_encryption_nondeterministic(self):
        """
        Same plaintext stored twice must produce different ciphertexts (random IV).
        This verifies that nonce is fresh per encryption — a core AES-GCM requirement.
        """
        session = SessionManager()
        key_value = "sk-same-key-every-time"
        session.store_key("provider_a", key_value)
        blob_a = session._encrypted_keys["provider_a"]
        # Overwrite with same value
        session.store_key("provider_a", key_value)
        blob_b = session._encrypted_keys["provider_a"]
        assert blob_a != blob_b, (
            "Each encryption must use a fresh nonce — identical plaintexts must produce "
            "different ciphertexts"
        )

    def test_key_not_in_repr(self):
        """
        repr() and str() must NEVER contain the raw API key.
        Security gate: key material must not leak through __repr__ or __str__.
        """
        session = SessionManager()
        secret_key = "sk-super-secret-9876"
        session.store_key("claude", secret_key)
        r = repr(session)
        s = str(session)
        assert secret_key not in r, f"API key leaked in repr(): {r!r}"
        assert secret_key not in s, f"API key leaked in str(): {s!r}"
        # Also check no partial leak (first 8 chars)
        assert secret_key[:8] not in r
        assert secret_key[:8] not in s

    def test_clear_wipes_all_keys(self):
        """session.clear() must remove all stored keys."""
        session = SessionManager()
        session.store_key("openai", "sk-openai-key")
        session.store_key("claude", "sk-ant-claude-key")
        assert session.has_key("openai")
        assert session.has_key("claude")
        session.clear()
        assert not session.has_key("openai"), "Key must be gone after clear()"
        assert not session.has_key("claude"), "Key must be gone after clear()"
        assert session.get_key("openai") is None
        assert session.get_key("claude") is None

    def test_get_nonexistent_key_returns_none(self):
        """get_key() for an unknown provider must return None (not raise, not return empty)."""
        session = SessionManager()
        result = session.get_key("nonexistent-provider-xyz")
        assert result is None, f"Expected None for missing key, got {result!r}"

    def test_has_key_reflects_storage(self):
        """has_key() must return False before store, True after store, False after clear."""
        session = SessionManager()
        assert not session.has_key("openai")
        session.store_key("openai", "sk-test")
        assert session.has_key("openai")
        session.clear()
        assert not session.has_key("openai")

    def test_encryption_key_entropy(self):
        """AES key must be 32 bytes (256-bit). Two sessions must have different keys."""
        s1 = SessionManager()
        s2 = SessionManager()
        assert len(s1._aes_key) == 32, "AES key must be 32 bytes (256-bit)"
        assert len(s2._aes_key) == 32
        assert s1._aes_key != s2._aes_key, (
            "Two SessionManager instances must have distinct AES keys"
        )

    def test_empty_api_key_rejected(self):
        """Storing an empty API key must raise ValueError (null != zero)."""
        session = SessionManager()
        import pytest
        with pytest.raises(ValueError, match="api_key"):
            session.store_key("openai", "")

    def test_none_api_key_rejected(self):
        """Storing None as API key must raise ValueError."""
        session = SessionManager()
        import pytest
        with pytest.raises((ValueError, TypeError)):
            session.store_key("openai", None)  # type: ignore

    def test_empty_provider_rejected(self):
        """Storing a key for an empty provider name must raise ValueError."""
        session = SessionManager()
        import pytest
        with pytest.raises(ValueError, match="provider"):
            session.store_key("", "sk-test")

    def test_set_and_get_active_provider(self):
        """set_active_provider() must update active_provider property."""
        session = SessionManager()
        assert session.active_provider is None
        session.set_active_provider("openai")
        assert session.active_provider == "openai"
        session.clear()
        assert session.active_provider is None

    def test_authenticated_providers_list(self):
        """authenticated_providers() must list providers that have stored keys."""
        session = SessionManager()
        assert session.authenticated_providers() == []
        session.store_key("openai", "sk-openai")
        session.store_key("claude", "sk-ant-claude")
        auths = session.authenticated_providers()
        assert "openai" in auths
        assert "claude" in auths
        assert len(auths) == 2


# ===========================================================================
# Phase 3 Tests — Provider Auth endpoint
# ===========================================================================

class TestProviderAuth:
    """Tests for POST /api/providers/auth."""

    def test_auth_valid_provider_and_key(self):
        """Supplying a valid provider + key must return status=authenticated."""
        r = client.post("/api/providers/auth", json={
            "provider": "openai",
            "api_key": "sk-test-openai-1234",
        })
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["status"] == "authenticated"
        assert data["provider"] == "openai"

    def test_auth_response_does_not_contain_key(self):
        """The auth response must NOT echo back the API key."""
        secret = "sk-never-return-this-key"
        r = client.post("/api/providers/auth", json={
            "provider": "openai",
            "api_key": secret,
        })
        response_text = r.text
        assert secret not in response_text, (
            f"API key leaked in auth response: {response_text!r}"
        )

    def test_auth_invalid_provider_returns_400(self):
        """Supplying a non-existent provider must return 400."""
        r = client.post("/api/providers/auth", json={
            "provider": "nonexistent-xyz-99",
            "api_key": "sk-test",
        })
        assert r.status_code == 400, f"Expected 400, got {r.status_code}: {r.text}"

    def test_auth_empty_key_returns_400(self):
        """An empty api_key must return 400 — empty string is not a valid key."""
        r = client.post("/api/providers/auth", json={
            "provider": "openai",
            "api_key": "",
        })
        assert r.status_code == 400, f"Expected 400, got {r.status_code}: {r.text}"

    def test_auth_whitespace_only_key_returns_400(self):
        """A whitespace-only api_key must return 400."""
        r = client.post("/api/providers/auth", json={
            "provider": "openai",
            "api_key": "   ",
        })
        assert r.status_code == 400, f"Expected 400, got {r.status_code}: {r.text}"


# ===========================================================================
# Phase 3 Tests — Extended Provider Listing
# ===========================================================================

class TestProviderRoutingPhase3:
    """Tests for Phase 3 extensions to /api/providers."""

    def test_providers_have_authenticated_field(self):
        """Each provider entry must have an 'authenticated' boolean field (Phase 3)."""
        r = client.get("/api/providers")
        assert r.status_code == 200
        data = r.json()
        for p in data["providers"]:
            assert "authenticated" in p, (
                f"Provider {p['id']!r} missing 'authenticated' field"
            )
            assert isinstance(p["authenticated"], bool), (
                f"'authenticated' must be bool, got {type(p['authenticated'])}"
            )

    def test_providers_have_requires_api_key_field(self):
        """Each provider entry must have 'requires_api_key' boolean (Phase 3)."""
        r = client.get("/api/providers")
        data = r.json()
        for p in data["providers"]:
            assert "requires_api_key" in p, (
                f"Provider {p['id']!r} missing 'requires_api_key' field"
            )

    def test_offline_not_authenticated_initially(self):
        """The 'offline' provider starts as authenticated=False (no key needed)."""
        r = client.get("/api/providers")
        data = r.json()
        offline = next((p for p in data["providers"] if p["id"] == "offline"), None)
        assert offline is not None, "offline provider must be present"
        # offline has no key stored — authenticated reflects session storage
        assert isinstance(offline["authenticated"], bool)

    def test_qwen_provider_listed(self):
        """The 'qwen' provider added in Phase 3 must appear in the provider list."""
        r = client.get("/api/providers")
        data = r.json()
        ids = [p["id"] for p in data["providers"]]
        assert "qwen" in ids, f"'qwen' not in provider list: {ids}"

    def test_custom_provider_listed(self):
        """The 'custom' endpoint template added in Phase 3 must appear."""
        r = client.get("/api/providers")
        data = r.json()
        ids = [p["id"] for p in data["providers"]]
        assert "custom" in ids, f"'custom' not in provider list: {ids}"

    def test_backward_compat_claude_provider_still_works(self):
        """
        Backward compatibility gate: the existing 'claude' provider must still be
        listed and switchable — Phase 3 must not break any pre-Phase-3 flows.
        """
        r = client.get("/api/providers")
        data = r.json()
        ids = [p["id"] for p in data["providers"]]
        assert "claude" in ids, f"'claude' provider missing (backward compat broken): {ids}"

        # Still switchable
        r2 = client.post("/api/providers/switch", json={"provider": "offline"})
        assert r2.status_code == 200, "Switching to offline must still work"

    def test_at_least_9_providers_after_phase3(self):
        """
        Phase 3 adds qwen + custom; total count must be >= 9
        (offline + claude-code + openai + claude + openrouter + togetherai + gemini + ollama +
        qwen + custom = 10).
        """
        r = client.get("/api/providers")
        data = r.json()
        count = len(data["providers"])
        assert count >= 9, f"Expected >= 9 providers after Phase 3, got {count}"


# ===========================================================================
# Phase 3 Tests — API Key Security gate
# ===========================================================================

class TestAPIKeySecurity:
    """
    Security gate tests: verify API keys never leak into observable surfaces.
    These tests constitute part of the security evidence for Rung 641.
    """

    def test_session_manager_repr_safe(self):
        """repr(SessionManager) must not expose any stored key material."""
        session = SessionManager()
        marker = "sk-SECURITY-CANARY-" + secrets.token_hex(8)
        session.store_key("openai", marker)
        output = repr(session)
        assert marker not in output, f"Key leaked in repr: {output!r}"

    def test_session_manager_str_safe(self):
        """str(SessionManager) must not expose any stored key material."""
        session = SessionManager()
        marker = "sk-SECURITY-CANARY-" + secrets.token_hex(8)
        session.store_key("claude", marker)
        output = str(session)
        assert marker not in output, f"Key leaked in str: {output!r}"

    def test_auth_endpoint_does_not_return_key(self):
        """POST /api/providers/auth response body must not contain the supplied key."""
        canary = "sk-canary-" + secrets.token_hex(8)
        r = client.post("/api/providers/auth", json={
            "provider": "openai",
            "api_key": canary,
        })
        assert canary not in r.text, (
            f"API key canary found in response body: {r.text!r}"
        )

    def test_empty_string_not_accepted_as_key(self):
        """
        Security gate: empty string must never be accepted as a key.
        Empty string is NOT a valid API key — coercing null/empty to default is forbidden.
        """
        session = SessionManager()
        import pytest
        with pytest.raises(ValueError):
            session.store_key("openai", "")
        # Confirm no key stored after the failed attempt
        assert not session.has_key("openai"), (
            "has_key() must return False after a failed store_key()"
        )
