#!/usr/bin/env python3
"""
Stillwater Provider Registry + Session Manager — Test Suite
Version: 1.0.0 | Target: 30+ tests | rung_target: 641

Tests:
  Group 1: PROVIDERS dict structure (static registry)
  Group 2: get_provider() — returns config, raises on unknown
  Group 3: list_providers() — sorted, complete
  Group 4: validate_provider() — key env var checks, Ollama, unknown
  Group 5: resolve_provider_for_model() — routing correctness
  Group 6: register_custom_provider() — dynamic registration
  Group 7: Session dataclass — creation, expiry, is_active, to_dict/from_dict
  Group 8: SessionManager.create_session() — fields, defaults, custom TTL
  Group 9: SessionManager.get_session() — found/not-found/expired
  Group 10: SessionManager.close_session() — marks closed, idempotent
  Group 11: SessionManager.list_active() — filters expired/closed, sorted
  Group 12: SessionManager.purge_expired() — removes expired from memory
  Group 13: Thread safety — concurrent session creates
  Group 14: Edge cases — empty skill pack, zero TTL validation

Run:
    cd /home/phuc/projects/stillwater
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_providers.py -v
"""

from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure the package is importable
CLI_SRC = Path(__file__).resolve().parent.parent / "cli" / "src"
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))


# ===========================================================================
# Group 1: PROVIDERS dict structure
# ===========================================================================

class TestProvidersDict:
    """PROVIDERS dict must have the right keys and structure for all providers."""

    def test_providers_is_dict(self):
        from stillwater.provider_registry import PROVIDERS
        assert isinstance(PROVIDERS, dict)

    def test_providers_has_anthropic(self):
        from stillwater.provider_registry import PROVIDERS
        assert "anthropic" in PROVIDERS

    def test_providers_has_openai(self):
        from stillwater.provider_registry import PROVIDERS
        assert "openai" in PROVIDERS

    def test_providers_has_ollama(self):
        from stillwater.provider_registry import PROVIDERS
        assert "ollama" in PROVIDERS

    def test_providers_has_together(self):
        from stillwater.provider_registry import PROVIDERS
        assert "together" in PROVIDERS

    def test_providers_has_openrouter(self):
        from stillwater.provider_registry import PROVIDERS
        assert "openrouter" in PROVIDERS

    def test_each_provider_has_base_url(self):
        from stillwater.provider_registry import PROVIDERS
        for name, config in PROVIDERS.items():
            assert "base_url" in config, f"Provider {name!r} missing base_url"
            assert isinstance(config["base_url"], str), f"Provider {name!r} base_url must be str"

    def test_each_provider_has_models_list(self):
        from stillwater.provider_registry import PROVIDERS
        for name, config in PROVIDERS.items():
            assert "models" in config, f"Provider {name!r} missing models"
            assert isinstance(config["models"], list), f"Provider {name!r} models must be list"

    def test_each_provider_has_api_key_env_key(self):
        """api_key_env must exist (may be None for Ollama)."""
        from stillwater.provider_registry import PROVIDERS
        for name, config in PROVIDERS.items():
            assert "api_key_env" in config, f"Provider {name!r} missing api_key_env"

    def test_ollama_api_key_env_is_none(self):
        """Ollama requires no API key."""
        from stillwater.provider_registry import PROVIDERS
        assert PROVIDERS["ollama"]["api_key_env"] is None

    def test_anthropic_models_include_claude_haiku(self):
        from stillwater.provider_registry import PROVIDERS
        models = PROVIDERS["anthropic"]["models"]
        assert any("haiku" in m for m in models)

    def test_openai_models_include_gpt4o(self):
        from stillwater.provider_registry import PROVIDERS
        models = PROVIDERS["openai"]["models"]
        assert "gpt-4o" in models
        assert "gpt-4o-mini" in models

    def test_anthropic_base_url_is_https(self):
        from stillwater.provider_registry import PROVIDERS
        assert PROVIDERS["anthropic"]["base_url"].startswith("https://")

    def test_openai_base_url_is_https(self):
        from stillwater.provider_registry import PROVIDERS
        assert PROVIDERS["openai"]["base_url"].startswith("https://")


# ===========================================================================
# Group 2: get_provider()
# ===========================================================================

class TestGetProvider:
    """get_provider(name) returns a copy of the config dict."""

    def test_get_anthropic_returns_dict(self):
        from stillwater.provider_registry import get_provider
        config = get_provider("anthropic")
        assert isinstance(config, dict)

    def test_get_openai_returns_dict(self):
        from stillwater.provider_registry import get_provider
        config = get_provider("openai")
        assert isinstance(config, dict)

    def test_get_ollama_returns_dict(self):
        from stillwater.provider_registry import get_provider
        config = get_provider("ollama")
        assert isinstance(config, dict)

    def test_get_unknown_raises_value_error(self):
        from stillwater.provider_registry import get_provider
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("nonexistent_provider_xyz")

    def test_get_unknown_error_message_contains_available(self):
        from stillwater.provider_registry import get_provider
        with pytest.raises(ValueError) as exc_info:
            get_provider("fake")
        assert "anthropic" in str(exc_info.value)

    def test_get_returns_copy_not_reference(self):
        """Mutating the returned dict must not affect the registry."""
        from stillwater.provider_registry import get_provider, PROVIDERS
        config = get_provider("openai")
        config["base_url"] = "http://tampered"
        assert PROVIDERS["openai"]["base_url"] != "http://tampered"

    def test_get_anthropic_has_api_key_env(self):
        from stillwater.provider_registry import get_provider
        config = get_provider("anthropic")
        assert config["api_key_env"] == "ANTHROPIC_API_KEY"

    def test_get_openai_has_api_key_env(self):
        from stillwater.provider_registry import get_provider
        config = get_provider("openai")
        assert config["api_key_env"] == "OPENAI_API_KEY"


# ===========================================================================
# Group 3: list_providers()
# ===========================================================================

class TestListProviders:
    """list_providers() returns sorted list of all provider names."""

    def test_list_returns_list(self):
        from stillwater.provider_registry import list_providers
        result = list_providers()
        assert isinstance(result, list)

    def test_list_contains_all_core_providers(self):
        from stillwater.provider_registry import list_providers
        result = list_providers()
        for name in ["anthropic", "openai", "ollama", "together", "openrouter"]:
            assert name in result, f"Provider {name!r} missing from list_providers()"

    def test_list_is_sorted(self):
        from stillwater.provider_registry import list_providers
        result = list_providers()
        assert result == sorted(result), "list_providers() must return sorted list"

    def test_list_length_at_least_five(self):
        from stillwater.provider_registry import list_providers
        result = list_providers()
        assert len(result) >= 5


# ===========================================================================
# Group 4: validate_provider()
# ===========================================================================

class TestValidateProvider:
    """validate_provider checks API key env vars (or Ollama reachability)."""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-1234"})
    def test_anthropic_valid_when_key_set(self):
        from stillwater.provider_registry import validate_provider
        assert validate_provider("anthropic") is True

    @patch.dict(os.environ, {}, clear=True)
    def test_anthropic_invalid_when_no_key(self):
        from stillwater.provider_registry import validate_provider
        assert validate_provider("anthropic") is False

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-openai-test"})
    def test_openai_valid_when_key_set(self):
        from stillwater.provider_registry import validate_provider
        assert validate_provider("openai") is True

    @patch.dict(os.environ, {}, clear=True)
    def test_openai_invalid_when_no_key(self):
        from stillwater.provider_registry import validate_provider
        assert validate_provider("openai") is False

    @patch.dict(os.environ, {"TOGETHER_API_KEY": "together-key-abc"})
    def test_together_valid_when_key_set(self):
        from stillwater.provider_registry import validate_provider
        assert validate_provider("together") is True

    @patch.dict(os.environ, {}, clear=True)
    def test_together_invalid_when_no_key(self):
        from stillwater.provider_registry import validate_provider
        assert validate_provider("together") is False

    def test_ollama_always_valid(self):
        """Ollama has no API key requirement; validate always returns True."""
        from stillwater.provider_registry import validate_provider
        assert validate_provider("ollama") is True

    def test_unknown_provider_returns_false(self):
        from stillwater.provider_registry import validate_provider
        assert validate_provider("does_not_exist") is False

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""})
    def test_empty_string_key_is_invalid(self):
        """An empty string key must count as invalid (not configured)."""
        from stillwater.provider_registry import validate_provider
        assert validate_provider("anthropic") is False


# ===========================================================================
# Group 5: resolve_provider_for_model()
# ===========================================================================

class TestResolveProviderForModel:
    """Correct provider is selected for each well-known model name."""

    def test_gpt4o_routes_to_openai(self):
        from stillwater.provider_registry import resolve_provider_for_model
        assert resolve_provider_for_model("gpt-4o") == "openai"

    def test_gpt4o_mini_routes_to_openai(self):
        from stillwater.provider_registry import resolve_provider_for_model
        assert resolve_provider_for_model("gpt-4o-mini") == "openai"

    def test_claude_haiku_routes_to_anthropic(self):
        from stillwater.provider_registry import resolve_provider_for_model
        assert resolve_provider_for_model("claude-haiku-4-5-20251001") == "anthropic"

    def test_claude_opus_routes_to_anthropic(self):
        from stillwater.provider_registry import resolve_provider_for_model
        assert resolve_provider_for_model("claude-opus-4-6") == "anthropic"

    def test_claude_sonnet_routes_to_anthropic(self):
        from stillwater.provider_registry import resolve_provider_for_model
        assert resolve_provider_for_model("claude-sonnet-4-6") == "anthropic"

    def test_llama_together_model_routes_to_together(self):
        from stillwater.provider_registry import resolve_provider_for_model
        assert resolve_provider_for_model("meta-llama/Llama-3.3-70B-Instruct") == "together"

    def test_ollama_prefix_routes_to_ollama(self):
        from stillwater.provider_registry import resolve_provider_for_model
        assert resolve_provider_for_model("ollama/llama3.1:8b") == "ollama"

    def test_llama3_prefix_routes_to_ollama(self):
        from stillwater.provider_registry import resolve_provider_for_model
        assert resolve_provider_for_model("llama3.1:8b") == "ollama"

    def test_unknown_model_returns_none(self):
        from stillwater.provider_registry import resolve_provider_for_model
        result = resolve_provider_for_model("totally-unknown-model-xyz-999")
        assert result is None


# ===========================================================================
# Group 6: register_custom_provider()
# ===========================================================================

class TestRegisterCustomProvider:
    """register_custom_provider() mutates PROVIDERS and list_providers()."""

    def test_register_custom_appears_in_list(self):
        from stillwater.provider_registry import register_custom_provider, list_providers, PROVIDERS
        # Clean up after test
        original_keys = set(PROVIDERS.keys())
        try:
            register_custom_provider(
                name="my-vllm",
                base_url="http://localhost:8000/v1",
                api_key_env="MY_VLLM_KEY",
                models=["my-model-7b"],
            )
            assert "my-vllm" in list_providers()
        finally:
            PROVIDERS.pop("my-vllm", None)

    def test_register_custom_config_correct(self):
        from stillwater.provider_registry import register_custom_provider, get_provider, PROVIDERS
        try:
            register_custom_provider(
                name="test-custom",
                base_url="https://custom.example.com/v1",
                api_key_env="CUSTOM_KEY",
                models=["custom-7b", "custom-13b"],
            )
            config = get_provider("test-custom")
            assert config["base_url"] == "https://custom.example.com/v1"
            assert config["api_key_env"] == "CUSTOM_KEY"
            assert "custom-7b" in config["models"]
        finally:
            PROVIDERS.pop("test-custom", None)


# ===========================================================================
# Group 7: Session dataclass
# ===========================================================================

class TestSession:
    """Session dataclass: creation, expiry logic, is_active, serialization."""

    def _make_session(self, ttl_seconds: int = 3600) -> "Session":
        from stillwater.session_manager import Session
        now = int(time.time())
        return Session(
            session_id="test-session-id",
            skill_pack=["prime-safety", "prime-coder"],
            active_task="test task",
            evidence_dir="/tmp/evidence",
            created_at=now,
            expires_at=now + ttl_seconds,
        )

    def test_session_fields(self):
        s = self._make_session()
        assert s.session_id == "test-session-id"
        assert "prime-safety" in s.skill_pack
        assert s.active_task == "test task"
        assert s.evidence_dir == "/tmp/evidence"
        assert isinstance(s.created_at, int)
        assert isinstance(s.expires_at, int)
        assert s.closed is False

    def test_session_not_expired_when_new(self):
        s = self._make_session(ttl_seconds=3600)
        assert s.is_expired() is False
        assert s.is_active() is True

    def test_session_expired_when_ttl_past(self):
        from stillwater.session_manager import Session
        past = int(time.time()) - 1  # 1 second in the past
        s = Session(
            session_id="x", skill_pack=[], active_task=None, evidence_dir=None,
            created_at=past - 100, expires_at=past,
        )
        assert s.is_expired() is True
        assert s.is_active() is False

    def test_session_expired_when_closed(self):
        s = self._make_session(ttl_seconds=3600)
        s.closed = True
        assert s.is_expired() is True

    def test_ttl_remaining_positive_for_new(self):
        s = self._make_session(ttl_seconds=3600)
        remaining = s.ttl_remaining_seconds()
        assert remaining > 0
        assert remaining <= 3600

    def test_ttl_remaining_zero_for_expired(self):
        from stillwater.session_manager import Session
        past = int(time.time()) - 1
        s = Session(
            session_id="y", skill_pack=[], active_task=None, evidence_dir=None,
            created_at=past - 100, expires_at=past,
        )
        assert s.ttl_remaining_seconds() == 0

    def test_to_dict_has_all_fields(self):
        s = self._make_session()
        d = s.to_dict()
        expected_keys = {
            "session_id", "skill_pack", "active_task", "evidence_dir",
            "created_at", "expires_at", "closed",
        }
        assert set(d.keys()) == expected_keys

    def test_from_dict_round_trip(self):
        s = self._make_session()
        d = s.to_dict()
        from stillwater.session_manager import Session
        s2 = Session.from_dict(d)
        assert s2.session_id == s.session_id
        assert s2.skill_pack == s.skill_pack
        assert s2.created_at == s.created_at
        assert s2.expires_at == s.expires_at
        assert s2.closed == s.closed

    def test_from_dict_missing_optional_fields_defaults(self):
        from stillwater.session_manager import Session
        now = int(time.time())
        d = {
            "session_id": "abc",
            "created_at": now,
            "expires_at": now + 100,
        }
        s = Session.from_dict(d)
        assert s.skill_pack == []
        assert s.active_task is None
        assert s.evidence_dir is None
        assert s.closed is False

    def test_timestamps_are_int_not_float(self):
        s = self._make_session()
        assert isinstance(s.created_at, int)
        assert isinstance(s.expires_at, int)


# ===========================================================================
# Group 8: SessionManager.create_session()
# ===========================================================================

class TestSessionManagerCreate:
    """create_session creates sessions with correct fields."""

    def test_create_returns_session(self):
        from stillwater.session_manager import SessionManager, Session
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=["prime-safety"])
        assert isinstance(s, Session)

    def test_create_unique_ids(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s1 = mgr.create_session(skill_pack=[])
        s2 = mgr.create_session(skill_pack=[])
        assert s1.session_id != s2.session_id

    def test_create_skill_pack_stored(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        skills = ["prime-safety", "prime-coder", "phuc-forecast"]
        s = mgr.create_session(skill_pack=skills)
        assert s.skill_pack == skills

    def test_create_active_task_stored(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[], active_task="fix bug #123")
        assert s.active_task == "fix bug #123"

    def test_create_evidence_dir_stored(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[], evidence_dir="/tmp/ev")
        assert s.evidence_dir == "/tmp/ev"

    def test_create_default_ttl_24h(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        # Should expire ~24h from now (within 5 seconds of 86400)
        remaining = s.ttl_remaining_seconds()
        assert remaining > 86400 - 5
        assert remaining <= 86400

    def test_create_custom_ttl(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[], ttl_seconds=300)
        remaining = s.ttl_remaining_seconds()
        assert remaining > 295
        assert remaining <= 300

    def test_create_not_closed(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        assert s.closed is False
        assert s.is_active() is True

    def test_create_invalid_skill_pack_raises(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        with pytest.raises(ValueError, match="skill_pack must be a list"):
            mgr.create_session(skill_pack="not-a-list")  # type: ignore

    def test_manager_invalid_ttl_raises(self):
        from stillwater.session_manager import SessionManager
        with pytest.raises(ValueError, match="default_ttl_seconds must be positive"):
            SessionManager(default_ttl_seconds=0)


# ===========================================================================
# Group 9: SessionManager.get_session()
# ===========================================================================

class TestSessionManagerGet:
    """get_session returns session or None correctly."""

    def test_get_existing_session(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=["prime-safety"])
        found = mgr.get_session(s.session_id)
        assert found is not None
        assert found.session_id == s.session_id

    def test_get_unknown_session_returns_none(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        assert mgr.get_session("00000000-0000-0000-0000-000000000000") is None

    def test_get_expired_session_returns_none(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        # Create session with TTL in the past
        s = mgr.create_session(skill_pack=[], ttl_seconds=1)
        # Force expire by mutating expires_at
        s.expires_at = int(time.time()) - 1
        found = mgr.get_session(s.session_id)
        assert found is None

    def test_get_closed_session_returns_none(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        mgr.close_session(s.session_id)
        found = mgr.get_session(s.session_id)
        assert found is None


# ===========================================================================
# Group 10: SessionManager.close_session()
# ===========================================================================

class TestSessionManagerClose:
    """close_session marks closed, is idempotent."""

    def test_close_marks_closed(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        mgr.close_session(s.session_id)
        assert s.closed is True

    def test_close_idempotent_unknown_id(self):
        """close_session on unknown ID is a no-op, does not raise."""
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        mgr.close_session("does-not-exist")  # must not raise

    def test_close_idempotent_already_closed(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        mgr.close_session(s.session_id)
        mgr.close_session(s.session_id)  # second close must not raise
        assert s.closed is True

    def test_close_removes_from_active(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        assert s.session_id in [x.session_id for x in mgr.list_active()]
        mgr.close_session(s.session_id)
        assert s.session_id not in [x.session_id for x in mgr.list_active()]


# ===========================================================================
# Group 11: SessionManager.list_active()
# ===========================================================================

class TestSessionManagerListActive:
    """list_active returns only non-expired, non-closed sessions."""

    def test_list_empty_initially(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        assert mgr.list_active() == []

    def test_list_after_create(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        active = mgr.list_active()
        assert len(active) == 1
        assert active[0].session_id == s.session_id

    def test_list_excludes_closed(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s1 = mgr.create_session(skill_pack=[])
        s2 = mgr.create_session(skill_pack=[])
        mgr.close_session(s1.session_id)
        active = mgr.list_active()
        ids = [s.session_id for s in active]
        assert s1.session_id not in ids
        assert s2.session_id in ids

    def test_list_excludes_expired(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        s.expires_at = int(time.time()) - 1  # expire it
        active = mgr.list_active()
        assert s.session_id not in [x.session_id for x in active]

    def test_list_sorted_by_created_at(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s1 = mgr.create_session(skill_pack=[])
        s2 = mgr.create_session(skill_pack=[])
        active = mgr.list_active()
        if len(active) == 2:
            assert active[0].created_at <= active[1].created_at


# ===========================================================================
# Group 12: SessionManager.purge_expired()
# ===========================================================================

class TestSessionManagerPurge:
    """purge_expired removes expired/closed sessions from memory."""

    def test_purge_removes_expired(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        s.expires_at = int(time.time()) - 1  # expire it
        before = mgr.session_count()
        removed = mgr.purge_expired()
        assert removed >= 1
        assert mgr.session_count() < before

    def test_purge_leaves_active(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        active = mgr.create_session(skill_pack=[])  # still active
        expired = mgr.create_session(skill_pack=[])
        expired.expires_at = int(time.time()) - 1  # expire it
        mgr.purge_expired()
        assert mgr.get_session(active.session_id) is not None

    def test_purge_returns_count(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s1 = mgr.create_session(skill_pack=[])
        s2 = mgr.create_session(skill_pack=[])
        s1.expires_at = int(time.time()) - 1
        s2.expires_at = int(time.time()) - 1
        removed = mgr.purge_expired()
        assert removed == 2

    def test_purge_removes_closed(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        mgr.close_session(s.session_id)
        removed = mgr.purge_expired()
        assert removed >= 1


# ===========================================================================
# Group 13: Thread safety
# ===========================================================================

class TestSessionManagerThreadSafety:
    """Concurrent creates/gets must not corrupt state."""

    def test_concurrent_creates_all_unique(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        results = []
        errors = []

        def create():
            try:
                s = mgr.create_session(skill_pack=["prime-safety"])
                results.append(s.session_id)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread errors: {errors}"
        assert len(results) == 20
        # All session IDs must be unique
        assert len(set(results)) == 20

    def test_concurrent_gets_no_crash(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        errors = []

        def get():
            try:
                mgr.get_session(s.session_id)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=get) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []


# ===========================================================================
# Group 14: Edge cases
# ===========================================================================

class TestEdgeCases:
    """Boundary conditions and edge cases."""

    def test_empty_skill_pack_is_valid(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        assert s.skill_pack == []
        assert s.is_active() is True

    def test_none_active_task_is_valid(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[], active_task=None)
        assert s.active_task is None

    def test_session_count_increments(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        assert mgr.session_count() == 0
        mgr.create_session(skill_pack=[])
        assert mgr.session_count() == 1
        mgr.create_session(skill_pack=[])
        assert mgr.session_count() == 2

    def test_list_all_includes_closed(self):
        from stillwater.session_manager import SessionManager
        mgr = SessionManager()
        s = mgr.create_session(skill_pack=[])
        mgr.close_session(s.session_id)
        all_sessions = mgr.list_all()
        ids = [x.session_id for x in all_sessions]
        assert s.session_id in ids

    def test_providers_module_imports(self):
        from stillwater.provider_registry import (
            PROVIDERS, get_provider, list_providers, validate_provider,
            resolve_provider_for_model, register_custom_provider,
        )
        assert PROVIDERS is not None
        assert callable(get_provider)
        assert callable(list_providers)
        assert callable(validate_provider)
        assert callable(resolve_provider_for_model)
        assert callable(register_custom_provider)

    def test_session_manager_module_imports(self):
        from stillwater.session_manager import Session, SessionManager
        assert Session is not None
        assert SessionManager is not None
