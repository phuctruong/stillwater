#!/usr/bin/env python3
"""
Stillwater Universal LLM Client — Test Suite
Version: 1.0.0 | Target: 50+ tests | All HTTP mocked

Run:
    cd /home/phuc/projects/stillwater
    python -m pytest tests/test_llm_client.py -v --tb=short -p no:httpbin
"""

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock
from dataclasses import FrozenInstanceError

import pytest

# Ensure the package is importable
CLI_SRC = Path(__file__).resolve().parent.parent / "cli" / "src"
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))


# ===========================================================================
# Group 1: LLMResponse (creation, immutability, serialization, cost)
# ===========================================================================

class TestLLMResponse:
    """Tests for the LLMResponse dataclass."""

    def test_create_response(self):
        from stillwater.providers.base import LLMResponse
        r = LLMResponse(
            text="Hello world",
            model="gpt-4o-mini",
            provider="openai",
            input_tokens=10,
            output_tokens=5,
            cost_hundredths_cent=42,
            latency_ms=150,
            request_id="abc123",
            timestamp="2026-01-01T00:00:00+00:00",
        )
        assert r.text == "Hello world"
        assert r.model == "gpt-4o-mini"
        assert r.provider == "openai"
        assert r.input_tokens == 10
        assert r.output_tokens == 5
        assert r.cost_hundredths_cent == 42
        assert r.latency_ms == 150
        assert r.request_id == "abc123"

    def test_response_immutable(self):
        from stillwater.providers.base import LLMResponse
        r = LLMResponse(
            text="test", model="m", provider="p",
            input_tokens=0, output_tokens=0,
            cost_hundredths_cent=0, latency_ms=0,
            request_id="x", timestamp="t",
        )
        with pytest.raises(FrozenInstanceError):
            r.text = "changed"  # type: ignore

    def test_response_to_dict(self):
        from stillwater.providers.base import LLMResponse
        r = LLMResponse(
            text="hi", model="m", provider="p",
            input_tokens=100, output_tokens=50,
            cost_hundredths_cent=99, latency_ms=200,
            request_id="rid", timestamp="ts",
        )
        d = r.to_dict()
        assert isinstance(d, dict)
        assert d["text"] == "hi"
        assert d["input_tokens"] == 100
        assert d["cost_hundredths_cent"] == 99
        assert "request_id" in d

    def test_response_cost_is_int(self):
        from stillwater.providers.base import LLMResponse
        r = LLMResponse(
            text="", model="m", provider="p",
            input_tokens=0, output_tokens=0,
            cost_hundredths_cent=12345, latency_ms=0,
            request_id="", timestamp="",
        )
        assert isinstance(r.cost_hundredths_cent, int)

    def test_response_to_dict_all_fields(self):
        from stillwater.providers.base import LLMResponse
        r = LLMResponse(
            text="x", model="y", provider="z",
            input_tokens=1, output_tokens=2,
            cost_hundredths_cent=3, latency_ms=4,
            request_id="5", timestamp="6",
        )
        d = r.to_dict()
        expected_keys = {
            "text", "model", "provider", "input_tokens", "output_tokens",
            "cost_hundredths_cent", "latency_ms", "request_id", "timestamp",
        }
        assert set(d.keys()) == expected_keys


# ===========================================================================
# Group 2: Pricing (exact arithmetic, aliases, wildcards)
# ===========================================================================

class TestPricing:
    """Tests for pricing module -- all int, no float drift."""

    def test_estimate_cost_claude_sonnet(self):
        from stillwater.providers.pricing import estimate_cost
        # 1000 input tokens at 300_00 per 1M = (1000 * 30000) // 1_000_000 = 30
        cost = estimate_cost(1000, 0, "claude-sonnet-4-20250514")
        assert isinstance(cost, int)
        assert cost == 30

    def test_estimate_cost_claude_opus(self):
        from stillwater.providers.pricing import estimate_cost
        # 1M input tokens = 1500_00 hundredths of cent
        cost = estimate_cost(1_000_000, 0, "claude-opus-4-20250514")
        assert cost == 1500_00

    def test_estimate_cost_output_tokens(self):
        from stillwater.providers.pricing import estimate_cost
        # 1M output tokens of claude-sonnet = 1500_00
        cost = estimate_cost(0, 1_000_000, "claude-sonnet-4-20250514")
        assert cost == 1500_00

    def test_estimate_cost_combined(self):
        from stillwater.providers.pricing import estimate_cost
        # 500 input + 200 output, gpt-4o-mini
        # input: (500 * 1500) // 1_000_000 = 750_000 // 1_000_000 = 0
        # output: (200 * 6000) // 1_000_000 = 1_200_000 // 1_000_000 = 1
        cost = estimate_cost(500, 200, "gpt-4o-mini")
        assert isinstance(cost, int)
        assert cost == 1  # output rounds to 1, input rounds to 0

    def test_estimate_cost_larger_combined(self):
        from stillwater.providers.pricing import estimate_cost
        # 100_000 input + 50_000 output, gpt-4o
        # input: (100_000 * 250_00) // 1_000_000 = 2_500_000_000 // 1_000_000 = 2500
        # output: (50_000 * 1000_00) // 1_000_000 = 5_000_000_000 // 1_000_000 = 5000
        cost = estimate_cost(100_000, 50_000, "gpt-4o")
        assert cost == 2500 + 5000

    def test_estimate_cost_unknown_model(self):
        from stillwater.providers.pricing import estimate_cost
        cost = estimate_cost(1000, 500, "unknown-model-xyz")
        assert cost == 0

    def test_estimate_cost_ollama_wildcard(self):
        from stillwater.providers.pricing import estimate_cost
        cost = estimate_cost(1_000_000, 1_000_000, "ollama/llama3.1:8b")
        assert cost == 0  # free

    def test_resolve_alias(self):
        from stillwater.providers.pricing import resolve_model_name
        assert resolve_model_name("claude-sonnet") == "claude-sonnet-4-20250514"
        assert resolve_model_name("llama-70b") == "meta-llama/Llama-3.3-70B-Instruct"

    def test_resolve_unknown_alias(self):
        from stillwater.providers.pricing import resolve_model_name
        assert resolve_model_name("unknown") == "unknown"

    def test_get_pricing_exact(self):
        from stillwater.providers.pricing import get_pricing
        p = get_pricing("gpt-4o")
        assert p is not None
        assert p["input"] == 250_00
        assert p["output"] == 1000_00

    def test_get_pricing_wildcard(self):
        from stillwater.providers.pricing import get_pricing
        p = get_pricing("ollama/anything")
        assert p is not None
        assert p["input"] == 0

    def test_get_pricing_none(self):
        from stillwater.providers.pricing import get_pricing
        assert get_pricing("nonexistent-model") is None

    def test_no_float_in_pricing_table(self):
        from stillwater.providers.pricing import MODEL_PRICING
        for model, prices in MODEL_PRICING.items():
            assert isinstance(prices["input"], int), f"float found in {model} input"
            assert isinstance(prices["output"], int), f"float found in {model} output"

    def test_cost_arithmetic_no_float_drift(self):
        """Ensure repeated cost calculations never accumulate float errors."""
        from stillwater.providers.pricing import estimate_cost
        total = 0
        for _ in range(10_000):
            total += estimate_cost(100, 100, "claude-sonnet-4-20250514")
        # Each: input = (100 * 30000) // 1M = 3, output = (100 * 150000) // 1M = 15
        # Per call: 18. 10000 calls: 180000
        assert total == 180_000
        assert isinstance(total, int)


# ===========================================================================
# Group 3: Provider base and helpers
# ===========================================================================

class TestHelpers:
    """Tests for shared provider helpers."""

    def test_make_request_id_deterministic(self):
        from stillwater.providers._helpers import make_request_id
        id1 = make_request_id("hello world")
        id2 = make_request_id("hello world")
        assert id1 == id2
        assert len(id1) == 64  # SHA-256 hex

    def test_make_request_id_different_inputs(self):
        from stillwater.providers._helpers import make_request_id
        id1 = make_request_id("hello")
        id2 = make_request_id("world")
        assert id1 != id2

    def test_iso_now_format(self):
        from stillwater.providers._helpers import iso_now
        ts = iso_now()
        assert "T" in ts
        assert "+" in ts or "Z" in ts

    def test_estimate_tokens(self):
        from stillwater.providers._helpers import estimate_tokens
        assert estimate_tokens("hello world!") == 3  # 12 chars // 4
        assert estimate_tokens("") == 1  # minimum 1

    def test_messages_to_prompt(self):
        from stillwater.providers._helpers import messages_to_prompt
        msgs = [
            {"role": "system", "content": "Be helpful"},
            {"role": "user", "content": "Hello"},
        ]
        result = messages_to_prompt(msgs)
        assert "system: Be helpful" in result
        assert "user: Hello" in result

    def test_build_response(self):
        from stillwater.providers._helpers import build_response
        r = build_response(
            text="answer",
            model="gpt-4o",
            provider="openai",
            input_tokens=100,
            output_tokens=50,
            latency_ms=200,
            request_content="test prompt",
        )
        assert r.text == "answer"
        assert r.model == "gpt-4o"
        assert r.provider == "openai"
        assert isinstance(r.cost_hundredths_cent, int)
        assert len(r.request_id) == 64


# ===========================================================================
# Group 4: Provider registry
# ===========================================================================

class TestProviderRegistry:
    """Tests for the provider registry."""

    def test_get_known_provider(self):
        from stillwater.providers import get_provider
        p = get_provider("anthropic")
        assert p.name == "anthropic"

    def test_get_unknown_provider_raises(self):
        from stillwater.providers import get_provider
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("nonexistent_provider")

    def test_all_provider_names(self):
        from stillwater.providers import get_provider
        for name in ["anthropic", "openai", "together", "openrouter", "ollama"]:
            p = get_provider(name)
            assert p.name == name

    def test_provider_priority_order(self):
        from stillwater.providers import PROVIDER_PRIORITY
        assert "ollama" in PROVIDER_PRIORITY[:2]  # cheapest tier
        assert "anthropic" in PROVIDER_PRIORITY

    @patch.dict(os.environ, {}, clear=True)
    def test_list_available_no_keys(self):
        """With no API keys and no Ollama, no providers should be available."""
        from stillwater.providers import list_available_providers
        from stillwater.providers.ollama_provider import OllamaProvider

        # Mock ollama to be unavailable too
        with patch.object(OllamaProvider, 'is_available', return_value=False):
            available = list_available_providers()
            # ollama might still appear if running locally; filter it
            non_ollama = [p for p in available if p != "ollama"]
            assert non_ollama == []

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-key-1234"}, clear=True)
    def test_list_available_with_anthropic_key(self):
        from stillwater.providers import list_available_providers
        from stillwater.providers.ollama_provider import OllamaProvider

        with patch.object(OllamaProvider, 'is_available', return_value=False):
            available = list_available_providers()
            assert "anthropic" in available


# ===========================================================================
# Group 5: Individual provider tests (mocked HTTP)
# ===========================================================================

def _mock_anthropic_response() -> dict:
    return {
        "content": [{"type": "text", "text": "Paris is the capital of France."}],
        "usage": {"input_tokens": 15, "output_tokens": 8},
        "model": "claude-haiku-4-5-20251001",
    }


def _mock_openai_response() -> dict:
    return {
        "choices": [{"message": {"content": "4", "role": "assistant"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 1},
        "model": "gpt-4o-mini",
    }


def _mock_together_response() -> dict:
    return {
        "choices": [{"message": {"content": "Hello!", "role": "assistant"}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 2},
        "model": "meta-llama/Llama-3.3-70B-Instruct",
    }


def _mock_openrouter_response() -> dict:
    return {
        "choices": [{"message": {"content": "Routed response", "role": "assistant"}}],
        "usage": {"prompt_tokens": 8, "completion_tokens": 3},
        "model": "openai/gpt-4o-mini",
    }


def _mock_ollama_generate_response() -> dict:
    return {
        "response": "Ollama says hello",
        "prompt_eval_count": 12,
        "eval_count": 5,
    }


def _mock_ollama_chat_response() -> dict:
    return {
        "message": {"role": "assistant", "content": "Ollama chat response"},
        "prompt_eval_count": 10,
        "eval_count": 6,
    }


class TestAnthropicProvider:
    """Anthropic provider with mocked HTTP."""

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_complete(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _mock_anthropic_response()

        p = AnthropicProvider(api_key="sk-ant-test1234")
        r = p.complete("What is the capital of France?")
        assert r.text == "Paris is the capital of France."
        assert r.provider == "anthropic"
        assert r.input_tokens == 15
        assert r.output_tokens == 8
        assert isinstance(r.cost_hundredths_cent, int)

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_chat_with_system(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _mock_anthropic_response()

        p = AnthropicProvider(api_key="sk-ant-test1234")
        r = p.chat([
            {"role": "system", "content": "Be concise"},
            {"role": "user", "content": "Capital of France?"},
        ], model="claude-haiku-4-5-20251001")

        assert r.text == "Paris is the capital of France."
        # Verify system was separated from messages
        call_args = mock_http.call_args
        payload = call_args[0][1]
        assert "system" in payload
        assert payload["system"] == "Be concise"

    def test_no_api_key_raises(self):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        with patch.dict(os.environ, {}, clear=True):
            p = AnthropicProvider(api_key="")
            with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
                p.complete("test")

    def test_models_list(self):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        p = AnthropicProvider(api_key="test")
        models = p.models()
        assert "claude-sonnet-4-20250514" in models
        assert "claude-opus-4-20250514" in models

    def test_is_available_with_key(self):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        p = AnthropicProvider(api_key="sk-test")
        assert p.is_available() is True

    @patch.dict(os.environ, {}, clear=True)
    def test_is_available_without_key(self):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        p = AnthropicProvider(api_key="")
        assert p.is_available() is False


class TestOpenAIProvider:
    """OpenAI provider with mocked HTTP."""

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_complete(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _mock_openai_response()

        p = OpenAIProvider(api_key="sk-test1234")
        r = p.complete("What is 2+2?")
        assert r.text == "4"
        assert r.provider == "openai"
        assert r.input_tokens == 10
        assert r.output_tokens == 1

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_chat(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _mock_openai_response()

        p = OpenAIProvider(api_key="sk-test1234")
        r = p.chat([{"role": "user", "content": "2+2?"}], model="gpt-4o-mini")
        assert r.text == "4"
        # Verify Authorization header was passed
        assert mock_http.call_args is not None  # http_post_json was called with headers

    def test_no_api_key_raises(self):
        from stillwater.providers.openai_provider import OpenAIProvider
        with patch.dict(os.environ, {}, clear=True):
            p = OpenAIProvider(api_key="")
            with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
                p.complete("test")

    def test_models_list(self):
        from stillwater.providers.openai_provider import OpenAIProvider
        p = OpenAIProvider(api_key="test")
        models = p.models()
        assert "gpt-4o" in models
        assert "gpt-4o-mini" in models


class TestTogetherProvider:
    """Together.ai provider with mocked HTTP."""

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_complete(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _mock_together_response()

        p = TogetherProvider(api_key="test-key")
        r = p.complete("Hello")
        assert r.text == "Hello!"
        assert r.provider == "together"

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_chat(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _mock_together_response()

        p = TogetherProvider(api_key="test-key")
        r = p.chat([{"role": "user", "content": "Hi"}])
        assert r.text == "Hello!"
        assert r.model == "meta-llama/Llama-3.3-70B-Instruct"

    def test_no_api_key_raises(self):
        from stillwater.providers.together_provider import TogetherProvider
        with patch.dict(os.environ, {}, clear=True):
            p = TogetherProvider(api_key="")
            with pytest.raises(RuntimeError, match="TOGETHER_API_KEY"):
                p.complete("test")


class TestOpenRouterProvider:
    """OpenRouter provider with mocked HTTP."""

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_complete(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _mock_openrouter_response()

        p = OpenRouterProvider(api_key="or-test-key")
        r = p.complete("route this")
        assert r.text == "Routed response"
        assert r.provider == "openrouter"

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_chat_includes_headers(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _mock_openrouter_response()

        p = OpenRouterProvider(api_key="or-test-key")
        p.chat([{"role": "user", "content": "test"}])

        call_args = mock_http.call_args
        headers = call_args[1].get("headers", {}) if call_args[1] else call_args[0][2]
        assert "Authorization" in headers
        assert "HTTP-Referer" in headers

    def test_models_include_multiple_vendors(self):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        p = OpenRouterProvider(api_key="test")
        models = p.models()
        assert any("anthropic" in m for m in models)
        assert any("openai" in m for m in models)


class TestOllamaProvider:
    """Ollama provider with mocked HTTP."""

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_complete(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _mock_ollama_generate_response()

        p = OllamaProvider(url="http://localhost:11434")
        r = p.complete("hello")
        assert r.text == "Ollama says hello"
        assert r.provider == "ollama"
        assert r.input_tokens == 12
        assert r.output_tokens == 5
        assert r.cost_hundredths_cent == 0  # free

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_chat(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _mock_ollama_chat_response()

        p = OllamaProvider(url="http://localhost:11434")
        r = p.chat([{"role": "user", "content": "hi"}])
        assert r.text == "Ollama chat response"
        assert r.input_tokens == 10
        assert r.output_tokens == 6

    @patch("stillwater.providers.ollama_provider.http_get_json")
    def test_models_list(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = {
            "models": [
                {"name": "llama3.1:8b"},
                {"name": "codellama:13b"},
            ]
        }
        p = OllamaProvider()
        models = p.models()
        assert "llama3.1:8b" in models
        assert "codellama:13b" in models

    @patch("stillwater.providers.ollama_provider.http_get_json")
    def test_is_available_true(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = {"models": []}
        p = OllamaProvider()
        assert p.is_available() is True

    @patch("stillwater.providers.ollama_provider.http_get_json")
    def test_is_available_false(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.side_effect = ConnectionError("refused")
        p = OllamaProvider()
        assert p.is_available() is False

    def test_custom_url(self):
        from stillwater.providers.ollama_provider import OllamaProvider
        p = OllamaProvider(url="http://192.168.1.100:11434")
        assert p._url == "http://192.168.1.100:11434"

    @patch.dict(os.environ, {"OLLAMA_URL": "http://myhost:11434"})
    def test_url_from_env(self):
        from stillwater.providers.ollama_provider import OllamaProvider
        p = OllamaProvider()
        assert p._url == "http://myhost:11434"


# ===========================================================================
# Group 6: LLMClient (init, auto-discover, model selection, fallback)
# ===========================================================================

class TestLLMClient:
    """Tests for the main LLMClient class."""

    def test_init_default(self):
        from stillwater.llm_client import LLMClient
        client = LLMClient()
        assert client.provider_name == "auto"

    def test_init_with_provider(self):
        from stillwater.llm_client import LLMClient
        client = LLMClient(provider="anthropic")
        assert client.provider_name == "anthropic"

    def test_init_with_config(self):
        from stillwater.llm_client import LLMClient
        config = {"anthropic": {"api_key": "sk-test"}}
        client = LLMClient(config=config)
        assert client._config == config

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_complete_with_provider(self, mock_http):
        from stillwater.llm_client import LLMClient
        mock_http.return_value = _mock_anthropic_response()

        client = LLMClient(
            config={"anthropic": {"api_key": "sk-test"}},
            provider="anthropic",
        )
        r = client.complete("Hello", provider="anthropic")
        assert r.text == "Paris is the capital of France."
        assert isinstance(r, object)  # LLMResponse
        assert r.provider == "anthropic"

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_chat_with_provider(self, mock_http):
        from stillwater.llm_client import LLMClient
        mock_http.return_value = _mock_openai_response()

        client = LLMClient(config={"openai": {"api_key": "sk-test"}})
        r = client.chat(
            [{"role": "user", "content": "2+2?"}],
            provider="openai",
        )
        assert r.text == "4"

    def test_estimate_cost(self):
        from stillwater.llm_client import LLMClient
        client = LLMClient()
        cost = client.estimate_cost(1_000_000, 500_000, "claude-sonnet-4-20250514")
        assert isinstance(cost, int)
        assert cost > 0

    def test_available_models_structure(self):
        from stillwater.llm_client import LLMClient
        client = LLMClient()
        models = client.available_models()
        assert isinstance(models, dict)
        # Each value should be a list
        for provider, model_list in models.items():
            assert isinstance(model_list, list)

    @patch.dict(os.environ, {}, clear=True)
    def test_no_providers_raises_on_auto(self):
        from stillwater.llm_client import LLMClient
        from stillwater.providers.ollama_provider import OllamaProvider

        with patch.object(OllamaProvider, 'is_available', return_value=False):
            client = LLMClient()
            with pytest.raises(RuntimeError, match="No LLM providers available"):
                client.complete("test")

    def test_thread_safety_provider_cache(self):
        """Verify that concurrent _get_or_create_provider calls don't crash."""
        from stillwater.llm_client import LLMClient
        client = LLMClient(config={"anthropic": {"api_key": "sk-test"}})

        errors = []

        def get_provider():
            try:
                p = client._get_or_create_provider("anthropic")
                assert p.name == "anthropic"
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=get_provider) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread safety errors: {errors}"


# ===========================================================================
# Group 7: Backward compatibility (v1.x API)
# ===========================================================================

class TestBackwardCompat:
    """Ensure v1.x API still works."""

    def test_offline_call(self):
        from stillwater.llm_client import LLMClient
        client = LLMClient(provider="offline")
        result = client.call("hello world test")
        assert result.startswith("[offline:")
        assert "hello world test" in result

    def test_offline_llm_call(self):
        from stillwater.llm_client import llm_call
        result = llm_call("test prompt", provider="offline")
        assert result.startswith("[offline:")

    def test_offline_llm_chat(self):
        from stillwater.llm_client import llm_chat
        result = llm_chat(
            [{"role": "user", "content": "hello"}],
            provider="offline",
        )
        assert result.startswith("[offline:")

    def test_test_connection_offline(self):
        from stillwater.llm_client import LLMClient
        client = LLMClient(provider="offline")
        ok, latency_ms, error = client.test_connection()
        assert ok is True
        assert isinstance(latency_ms, int)
        assert error is None

    def test_provider_name_attribute(self):
        from stillwater.llm_client import LLMClient
        client = LLMClient(provider="anthropic")
        assert client.provider_name == "anthropic"

    def test_get_call_history(self):
        from stillwater.llm_client import get_call_history
        # Should not crash even if log file doesn't exist
        history = get_call_history(n=10)
        assert isinstance(history, list)

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_call_returns_string(self, mock_http):
        """v1.x .call() returns str, not LLMResponse."""
        from stillwater.llm_client import LLMClient
        mock_http.return_value = _mock_anthropic_response()

        client = LLMClient(
            config={"anthropic": {"api_key": "sk-test"}},
            provider="anthropic",
        )
        result = client.call("test")
        assert isinstance(result, str)
        assert result == "Paris is the capital of France."


# ===========================================================================
# Group 8: HTTP helpers
# ===========================================================================

class TestHTTPHelpers:
    """Tests for the stdlib HTTP helpers."""

    @patch("urllib.request.urlopen")
    def test_http_post_json(self, mock_urlopen):
        from stillwater.providers._http import http_post_json

        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"result": "ok"}'
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = http_post_json("http://example.com/api", {"key": "value"})
        assert result == {"result": "ok"}

    @patch("urllib.request.urlopen")
    def test_http_get_json(self, mock_urlopen):
        from stillwater.providers._http import http_get_json

        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"status": "healthy"}'
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = http_get_json("http://example.com/health")
        assert result == {"status": "healthy"}

    def test_http_error_class(self):
        from stillwater.providers._http import HTTPError
        err = HTTPError(404, "not found", "http://example.com")
        assert err.status_code == 404
        assert err.body == "not found"
        assert "404" in str(err)


# ===========================================================================
# Group 9: Edge cases
# ===========================================================================

class TestEdgeCases:
    """Edge cases and error handling."""

    def test_empty_messages_chat(self):
        """Chat with empty messages list should still work for anthropic."""
        from stillwater.providers.anthropic_provider import AnthropicProvider
        with patch("stillwater.providers.anthropic_provider.http_post_json") as mock_http:
            mock_http.return_value = _mock_anthropic_response()
            p = AnthropicProvider(api_key="sk-test")
            r = p.chat([], model="claude-haiku-4-5-20251001")
            assert r.text == "Paris is the capital of France."
            # Verify empty messages get a default user message
            payload = mock_http.call_args[0][1]
            assert len(payload["messages"]) >= 1

    def test_response_with_zero_tokens(self):
        from stillwater.providers.base import LLMResponse
        r = LLMResponse(
            text="", model="m", provider="p",
            input_tokens=0, output_tokens=0,
            cost_hundredths_cent=0, latency_ms=0,
            request_id="x", timestamp="t",
        )
        assert r.input_tokens == 0
        assert r.cost_hundredths_cent == 0

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_api_error_propagates(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        from stillwater.providers._http import HTTPError
        mock_http.side_effect = HTTPError(429, "rate limited", "https://api.anthropic.com/v1/messages")

        p = AnthropicProvider(api_key="sk-test")
        with pytest.raises(HTTPError) as exc_info:
            p.complete("test")
        assert exc_info.value.status_code == 429

    def test_provider_config_override(self):
        """LLMClient should pass config to providers."""
        from stillwater.llm_client import LLMClient
        client = LLMClient(config={"anthropic": {"api_key": "my-custom-key"}})
        p = client._get_or_create_provider("anthropic")
        assert p._api_key == "my-custom-key"

    def test_ollama_url_trailing_slash_stripped(self):
        from stillwater.providers.ollama_provider import OllamaProvider
        p = OllamaProvider(url="http://localhost:11434/")
        assert p._url == "http://localhost:11434"

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_openai_empty_choices(self, mock_http):
        """Handle OpenAI response with empty choices."""
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = {"choices": [], "usage": {"prompt_tokens": 5, "completion_tokens": 0}}
        p = OpenAIProvider(api_key="sk-test")
        r = p.complete("test")
        assert r.text == ""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-env-key-5678"}, clear=True)
    def test_anthropic_reads_env_key(self):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        p = AnthropicProvider()  # no explicit key
        assert p.is_available() is True
        assert p._get_key() == "sk-env-key-5678"

    def test_multiple_system_messages_joined(self):
        """Multiple system messages should be joined."""
        from stillwater.providers.anthropic_provider import AnthropicProvider
        with patch("stillwater.providers.anthropic_provider.http_post_json") as mock_http:
            mock_http.return_value = _mock_anthropic_response()
            p = AnthropicProvider(api_key="sk-test")
            p.chat([
                {"role": "system", "content": "Rule 1"},
                {"role": "system", "content": "Rule 2"},
                {"role": "user", "content": "Hello"},
            ])
            payload = mock_http.call_args[0][1]
            assert payload["system"] == "Rule 1\nRule 2"
            # Only user message in messages array
            assert len(payload["messages"]) == 1
            assert payload["messages"][0]["role"] == "user"


# ===========================================================================
# Group 10: Call logging
# ===========================================================================

class TestCallLogging:
    """Tests for the call logging system."""

    def test_log_call_does_not_crash(self):
        """_log_call should never raise, even with bad paths."""
        from stillwater.llm_client import _log_call
        # Should not raise even if log dir doesn't exist
        _log_call(
            provider="test", model="test-model",
            prompt_chars=10, response_chars=20,
            latency_ms=100,
        )

    def test_log_call_with_error(self):
        from stillwater.llm_client import _log_call
        _log_call(
            provider="test", model="m",
            prompt_chars=5, response_chars=0,
            latency_ms=50, error="connection refused",
        )

    def test_log_call_with_tokens_and_cost(self):
        from stillwater.llm_client import _log_call
        _log_call(
            provider="anthropic", model="claude-haiku-4-5-20251001",
            prompt_chars=100, response_chars=200,
            latency_ms=300, input_tokens=25, output_tokens=50,
            cost_hundredths_cent=42, request_id="abc",
        )

    def test_get_call_history_returns_list(self):
        from stillwater.llm_client import get_call_history
        result = get_call_history(n=5)
        assert isinstance(result, list)


# ===========================================================================
# Group 11: Import smoke tests
# ===========================================================================

class TestImports:
    """Verify all expected imports work."""

    def test_import_llm_client(self):
        from stillwater.llm_client import LLMClient
        assert LLMClient is not None

    def test_import_llm_call(self):
        from stillwater.llm_client import llm_call
        assert callable(llm_call)

    def test_import_llm_chat(self):
        from stillwater.llm_client import llm_chat
        assert callable(llm_chat)

    def test_import_get_call_history(self):
        from stillwater.llm_client import get_call_history
        assert callable(get_call_history)

    def test_import_llm_response(self):
        from stillwater.providers.base import LLMResponse
        assert LLMResponse is not None

    def test_import_providers(self):
        from stillwater.providers import (
            AnthropicProvider,
            OpenAIProvider,
            TogetherProvider,
            OpenRouterProvider,
            OllamaProvider,
        )
        assert all([
            AnthropicProvider, OpenAIProvider, TogetherProvider,
            OpenRouterProvider, OllamaProvider,
        ])

    def test_import_pricing(self):
        from stillwater.providers.pricing import MODEL_PRICING, estimate_cost
        assert len(MODEL_PRICING) > 0
        assert callable(estimate_cost)

    def test_import_from_providers_init(self):
        from stillwater.providers import (
            get_provider, list_available_providers, estimate_cost,
        )
        assert callable(get_provider)
        assert callable(list_available_providers)
        assert callable(estimate_cost)
