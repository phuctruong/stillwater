#!/usr/bin/env python3
"""
Stillwater LLM Provider Implementations — Comprehensive Test Suite
Version: 1.0.0 | Target: 80+ tests | rung_target: 641
All HTTP calls are mocked — no real network traffic.

Providers tested:
  - OpenAIProvider      (10+ tests)
  - TogetherProvider    (10+ tests)
  - OpenRouterProvider  (10+ tests)
  - AnthropicProvider   (10+ tests, extends minimal existing coverage)
  - OllamaProvider      (10+ tests, extends minimal existing coverage)
  - Provider registry   (list_available_providers, get_cheapest_provider, PROVIDERS)

Run:
    cd /home/phuc/projects/stillwater
    python -m pytest tests/test_provider_implementations.py -v --tb=short
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure the package is importable
CLI_SRC = Path(__file__).resolve().parent.parent / "src" / "cli" / "src"
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))


# ===========================================================================
# Shared mock response builders
# ===========================================================================

def _openai_response(text: str = "OpenAI answer", input_tokens: int = 20, output_tokens: int = 10) -> dict:
    return {
        "choices": [{"message": {"content": text, "role": "assistant"}}],
        "usage": {"prompt_tokens": input_tokens, "completion_tokens": output_tokens},
        "model": "gpt-4o-mini",
    }


def _openai_response_no_usage(text: str = "NoUsage answer") -> dict:
    """OpenAI response without usage block — triggers estimate_tokens fallback."""
    return {
        "choices": [{"message": {"content": text, "role": "assistant"}}],
    }


def _together_response(text: str = "Together answer", input_tokens: int = 15, output_tokens: int = 8) -> dict:
    return {
        "choices": [{"message": {"content": text, "role": "assistant"}}],
        "usage": {"prompt_tokens": input_tokens, "completion_tokens": output_tokens},
        "model": "meta-llama/Llama-3.3-70B-Instruct",
    }


def _openrouter_response(text: str = "OpenRouter answer", input_tokens: int = 12, output_tokens: int = 6) -> dict:
    return {
        "choices": [{"message": {"content": text, "role": "assistant"}}],
        "usage": {"prompt_tokens": input_tokens, "completion_tokens": output_tokens},
        "model": "openai/gpt-4o-mini",
    }


def _anthropic_response(text: str = "Anthropic answer", input_tokens: int = 18, output_tokens: int = 9) -> dict:
    return {
        "content": [{"type": "text", "text": text}],
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
        "model": "claude-haiku-4-5-20251001",
    }


def _anthropic_multi_block_response() -> dict:
    """Anthropic response with multiple content blocks."""
    return {
        "content": [
            {"type": "text", "text": "Part one. "},
            {"type": "text", "text": "Part two."},
        ],
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }


def _ollama_generate_response(text: str = "Ollama says hello", prompt_eval: int = 12, eval_count: int = 5) -> dict:
    return {
        "response": text,
        "prompt_eval_count": prompt_eval,
        "eval_count": eval_count,
    }


def _ollama_chat_response(text: str = "Ollama chat answer", prompt_eval: int = 10, eval_count: int = 7) -> dict:
    return {
        "message": {"role": "assistant", "content": text},
        "prompt_eval_count": prompt_eval,
        "eval_count": eval_count,
    }


def _make_http_error(status_code: int, body: str = "", url: str = "http://api.example.com"):
    from stillwater.providers._http import HTTPError
    return HTTPError(status_code, body, url)


# ===========================================================================
# Group 1: OpenAIProvider
# ===========================================================================

class TestOpenAIProvider:
    """Complete coverage of OpenAIProvider with mocked HTTP."""

    # --- Instantiation ---

    def test_init_with_explicit_api_key(self):
        from stillwater.providers.openai_provider import OpenAIProvider
        p = OpenAIProvider(api_key="sk-explicit-key")
        assert p._api_key == "sk-explicit-key"

    def test_init_reads_env_var(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-from-env"}, clear=True):
            from stillwater.providers.openai_provider import OpenAIProvider
            p = OpenAIProvider()
            assert p._get_key() == "sk-from-env"

    def test_name_property(self):
        from stillwater.providers.openai_provider import OpenAIProvider
        p = OpenAIProvider(api_key="x")
        assert p.name == "openai"

    def test_is_available_with_key(self):
        from stillwater.providers.openai_provider import OpenAIProvider
        p = OpenAIProvider(api_key="sk-test")
        assert p.is_available() is True

    @patch.dict(os.environ, {}, clear=True)
    def test_is_available_without_key(self):
        from stillwater.providers.openai_provider import OpenAIProvider
        p = OpenAIProvider(api_key="")
        assert p.is_available() is False

    def test_models_list_contains_gpt4o(self):
        from stillwater.providers.openai_provider import OpenAIProvider
        p = OpenAIProvider(api_key="x")
        models = p.models()
        assert "gpt-4o" in models
        assert "gpt-4o-mini" in models
        assert isinstance(models, list)

    # --- complete() ---

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_complete_returns_llm_response(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        from stillwater.providers.base import LLMResponse
        mock_http.return_value = _openai_response("Hello from OpenAI")

        p = OpenAIProvider(api_key="sk-test")
        r = p.complete("Say hello")

        assert isinstance(r, LLMResponse)

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_complete_text_extracted(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response("The answer is 42")

        p = OpenAIProvider(api_key="sk-test")
        r = p.complete("What is the answer?")

        assert r.text == "The answer is 42"

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_complete_provider_name(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response()

        p = OpenAIProvider(api_key="sk-test")
        r = p.complete("test")

        assert r.provider == "openai"

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_complete_token_counts(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response(input_tokens=100, output_tokens=50)

        p = OpenAIProvider(api_key="sk-test")
        r = p.complete("test")

        assert r.input_tokens == 100
        assert r.output_tokens == 50

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_complete_cost_is_int(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response(input_tokens=1_000_000, output_tokens=500_000)

        p = OpenAIProvider(api_key="sk-test")
        r = p.complete("test", model="gpt-4o-mini")

        assert isinstance(r.cost_hundredths_cent, int)

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_complete_default_model_used(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response()

        p = OpenAIProvider(api_key="sk-test")
        r = p.complete("test")

        # Default model is gpt-4o-mini
        assert r.model == "gpt-4o-mini"

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_complete_explicit_model(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response()

        p = OpenAIProvider(api_key="sk-test")
        r = p.complete("test", model="gpt-4o")

        assert r.model == "gpt-4o"

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_complete_request_id_is_sha256(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response()

        p = OpenAIProvider(api_key="sk-test")
        r = p.complete("test")

        assert len(r.request_id) == 64
        assert all(c in "0123456789abcdef" for c in r.request_id)

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_complete_latency_ms_is_int(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response()

        p = OpenAIProvider(api_key="sk-test")
        r = p.complete("test")

        assert isinstance(r.latency_ms, int)
        assert r.latency_ms >= 0

    # --- chat() ---

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_chat_basic(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response("Chat response")

        p = OpenAIProvider(api_key="sk-test")
        r = p.chat([{"role": "user", "content": "Hello"}])

        assert r.text == "Chat response"

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_chat_sends_auth_header(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response()

        p = OpenAIProvider(api_key="sk-my-real-key")
        p.chat([{"role": "user", "content": "Hi"}])

        call_kwargs = mock_http.call_args
        # headers are passed as kwarg
        headers = call_kwargs[1].get("headers", {})
        assert "Authorization" in headers
        assert "sk-my-real-key" in headers["Authorization"]

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_chat_multi_turn(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response("Multi-turn response")

        p = OpenAIProvider(api_key="sk-test")
        r = p.chat([
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"},
        ])

        assert r.text == "Multi-turn response"
        payload = mock_http.call_args[0][1]
        assert len(payload["messages"]) == 3

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_chat_empty_choices_returns_empty_text(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = {"choices": [], "usage": {"prompt_tokens": 5, "completion_tokens": 0}}

        p = OpenAIProvider(api_key="sk-test")
        r = p.chat([{"role": "user", "content": "test"}])

        assert r.text == ""

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_chat_no_usage_falls_back_to_estimate(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response_no_usage("Estimated token response")

        p = OpenAIProvider(api_key="sk-test")
        r = p.chat([{"role": "user", "content": "test prompt here"}])

        assert r.text == "Estimated token response"
        assert r.input_tokens >= 1
        assert r.output_tokens >= 1

    # --- Error handling ---

    def test_no_api_key_raises_runtime_error(self):
        from stillwater.providers.openai_provider import OpenAIProvider
        with patch.dict(os.environ, {}, clear=True):
            p = OpenAIProvider(api_key="")
            with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
                p.complete("test")

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_http_401_propagates(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.side_effect = _make_http_error(401, "Unauthorized")

        p = OpenAIProvider(api_key="sk-bad-key")
        with pytest.raises(Exception) as exc_info:
            p.complete("test")
        assert "401" in str(exc_info.value)

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_http_429_propagates(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.side_effect = _make_http_error(429, "Rate limit exceeded")

        p = OpenAIProvider(api_key="sk-test")
        with pytest.raises(Exception) as exc_info:
            p.complete("test")
        assert "429" in str(exc_info.value)

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_http_500_propagates(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.side_effect = _make_http_error(500, "Internal Server Error")

        p = OpenAIProvider(api_key="sk-test")
        with pytest.raises(Exception) as exc_info:
            p.complete("test")
        assert "500" in str(exc_info.value)

    # --- Cost calculation ---

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_cost_gpt4o_mini_exact_arithmetic(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        # gpt-4o-mini: input=15_00, output=60_00 per 1M tokens
        # 1M input tokens => (1_000_000 * 1500) // 1_000_000 = 1500
        mock_http.return_value = _openai_response(input_tokens=1_000_000, output_tokens=0)

        p = OpenAIProvider(api_key="sk-test")
        r = p.complete("test", model="gpt-4o-mini")

        assert isinstance(r.cost_hundredths_cent, int)
        assert r.cost_hundredths_cent == 1500

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_cost_never_float(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response(input_tokens=777, output_tokens=333)

        p = OpenAIProvider(api_key="sk-test")
        r = p.complete("test", model="gpt-4o")

        assert isinstance(r.cost_hundredths_cent, int)
        assert not isinstance(r.cost_hundredths_cent, float)

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_complete_wraps_to_chat(self, mock_http):
        """complete() is a thin wrapper — verify http_post_json called exactly once."""
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response()

        p = OpenAIProvider(api_key="sk-test")
        p.complete("single prompt")

        assert mock_http.call_count == 1


# ===========================================================================
# Group 2: TogetherProvider
# ===========================================================================

class TestTogetherProvider:
    """Complete coverage of TogetherProvider with mocked HTTP."""

    # --- Instantiation ---

    def test_init_with_explicit_api_key(self):
        from stillwater.providers.together_provider import TogetherProvider
        p = TogetherProvider(api_key="tg-explicit-key")
        assert p._api_key == "tg-explicit-key"

    def test_init_reads_env_var(self):
        with patch.dict(os.environ, {"TOGETHER_API_KEY": "tg-from-env"}, clear=True):
            from stillwater.providers.together_provider import TogetherProvider
            p = TogetherProvider()
            assert p._get_key() == "tg-from-env"

    def test_name_property(self):
        from stillwater.providers.together_provider import TogetherProvider
        p = TogetherProvider(api_key="x")
        assert p.name == "together"

    def test_is_available_with_key(self):
        from stillwater.providers.together_provider import TogetherProvider
        p = TogetherProvider(api_key="tg-key")
        assert p.is_available() is True

    @patch.dict(os.environ, {}, clear=True)
    def test_is_available_without_key(self):
        from stillwater.providers.together_provider import TogetherProvider
        p = TogetherProvider(api_key="")
        assert p.is_available() is False

    def test_models_list(self):
        from stillwater.providers.together_provider import TogetherProvider
        p = TogetherProvider(api_key="x")
        models = p.models()
        assert isinstance(models, list)
        assert len(models) >= 1
        assert "meta-llama/Llama-3.3-70B-Instruct" in models

    # --- complete() ---

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_complete_returns_llm_response(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        from stillwater.providers.base import LLMResponse
        mock_http.return_value = _together_response("Together answer")

        p = TogetherProvider(api_key="tg-test")
        r = p.complete("Hello Together")

        assert isinstance(r, LLMResponse)

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_complete_text_extracted(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _together_response("Llama says hi")

        p = TogetherProvider(api_key="tg-test")
        r = p.complete("Say hi")

        assert r.text == "Llama says hi"

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_complete_provider_is_together(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _together_response()

        p = TogetherProvider(api_key="tg-test")
        r = p.complete("test")

        assert r.provider == "together"

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_complete_default_model(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _together_response()

        p = TogetherProvider(api_key="tg-test")
        r = p.complete("test")

        assert r.model == "meta-llama/Llama-3.3-70B-Instruct"

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_complete_token_counts(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _together_response(input_tokens=30, output_tokens=15)

        p = TogetherProvider(api_key="tg-test")
        r = p.complete("test")

        assert r.input_tokens == 30
        assert r.output_tokens == 15

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_complete_cost_is_int(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _together_response(input_tokens=500_000, output_tokens=200_000)

        p = TogetherProvider(api_key="tg-test")
        r = p.complete("test")

        assert isinstance(r.cost_hundredths_cent, int)
        assert not isinstance(r.cost_hundredths_cent, float)

    # --- chat() ---

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_chat_basic(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _together_response("Chat from Together")

        p = TogetherProvider(api_key="tg-test")
        r = p.chat([{"role": "user", "content": "Hello"}])

        assert r.text == "Chat from Together"

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_chat_sends_auth_header(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _together_response()

        p = TogetherProvider(api_key="tg-my-key")
        p.chat([{"role": "user", "content": "Hi"}])

        headers = mock_http.call_args[1].get("headers", {})
        assert "Authorization" in headers
        assert "tg-my-key" in headers["Authorization"]

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_chat_payload_has_model(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _together_response()

        p = TogetherProvider(api_key="tg-test")
        p.chat([{"role": "user", "content": "test"}], model="meta-llama/Llama-3.3-70B-Instruct")

        payload = mock_http.call_args[0][1]
        assert payload["model"] == "meta-llama/Llama-3.3-70B-Instruct"

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_chat_empty_choices_returns_empty_text(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = {"choices": [], "usage": {"prompt_tokens": 5, "completion_tokens": 0}}

        p = TogetherProvider(api_key="tg-test")
        r = p.chat([{"role": "user", "content": "test"}])

        assert r.text == ""

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_chat_request_id_sha256(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _together_response()

        p = TogetherProvider(api_key="tg-test")
        r = p.chat([{"role": "user", "content": "test"}])

        assert len(r.request_id) == 64

    # --- Error handling ---

    def test_no_api_key_raises(self):
        from stillwater.providers.together_provider import TogetherProvider
        with patch.dict(os.environ, {}, clear=True):
            p = TogetherProvider(api_key="")
            with pytest.raises(RuntimeError, match="TOGETHER_API_KEY"):
                p.complete("test")

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_http_401_propagates(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.side_effect = _make_http_error(401, "Unauthorized")

        p = TogetherProvider(api_key="tg-bad")
        with pytest.raises(Exception) as exc_info:
            p.complete("test")
        assert "401" in str(exc_info.value)

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_http_429_propagates(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.side_effect = _make_http_error(429, "Rate limited")

        p = TogetherProvider(api_key="tg-test")
        with pytest.raises(Exception) as exc_info:
            p.complete("test")
        assert "429" in str(exc_info.value)

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_http_500_propagates(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.side_effect = _make_http_error(500, "Server error")

        p = TogetherProvider(api_key="tg-test")
        with pytest.raises(Exception) as exc_info:
            p.complete("test")
        assert "500" in str(exc_info.value)

    # --- Cost calculation ---

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_cost_llama_exact(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        # meta-llama/Llama-3.3-70B-Instruct: input=59_00, output=59_00 per 1M
        # 1M input => (1_000_000 * 5900) // 1_000_000 = 5900
        mock_http.return_value = _together_response(input_tokens=1_000_000, output_tokens=0)

        p = TogetherProvider(api_key="tg-test")
        r = p.complete("test", model="meta-llama/Llama-3.3-70B-Instruct")

        assert isinstance(r.cost_hundredths_cent, int)
        assert r.cost_hundredths_cent == 5900

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_cost_not_float(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _together_response(input_tokens=12345, output_tokens=6789)

        p = TogetherProvider(api_key="tg-test")
        r = p.complete("test")

        assert isinstance(r.cost_hundredths_cent, int)

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_complete_http_called_once(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _together_response()

        p = TogetherProvider(api_key="tg-test")
        p.complete("test")

        assert mock_http.call_count == 1


# ===========================================================================
# Group 3: OpenRouterProvider
# ===========================================================================

class TestOpenRouterProvider:
    """Complete coverage of OpenRouterProvider with mocked HTTP."""

    # --- Instantiation ---

    def test_init_with_explicit_api_key(self):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        p = OpenRouterProvider(api_key="or-explicit-key")
        assert p._api_key == "or-explicit-key"

    def test_init_reads_env_var(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "or-from-env"}, clear=True):
            from stillwater.providers.openrouter_provider import OpenRouterProvider
            p = OpenRouterProvider()
            assert p._get_key() == "or-from-env"

    def test_name_property(self):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        p = OpenRouterProvider(api_key="x")
        assert p.name == "openrouter"

    def test_is_available_with_key(self):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        p = OpenRouterProvider(api_key="or-key")
        assert p.is_available() is True

    @patch.dict(os.environ, {}, clear=True)
    def test_is_available_without_key(self):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        p = OpenRouterProvider(api_key="")
        assert p.is_available() is False

    def test_models_list_multi_vendor(self):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        p = OpenRouterProvider(api_key="x")
        models = p.models()
        assert isinstance(models, list)
        assert any("anthropic" in m for m in models)
        assert any("openai" in m for m in models)

    # --- complete() ---

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_complete_returns_llm_response(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        from stillwater.providers.base import LLMResponse
        mock_http.return_value = _openrouter_response("Routed via OpenRouter")

        p = OpenRouterProvider(api_key="or-test")
        r = p.complete("Route this prompt")

        assert isinstance(r, LLMResponse)

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_complete_text_extracted(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _openrouter_response("OpenRouter text output")

        p = OpenRouterProvider(api_key="or-test")
        r = p.complete("test")

        assert r.text == "OpenRouter text output"

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_complete_provider_is_openrouter(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _openrouter_response()

        p = OpenRouterProvider(api_key="or-test")
        r = p.complete("test")

        assert r.provider == "openrouter"

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_complete_default_model(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _openrouter_response()

        p = OpenRouterProvider(api_key="or-test")
        r = p.complete("test")

        assert r.model == "openai/gpt-4o-mini"

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_complete_explicit_model(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _openrouter_response()

        p = OpenRouterProvider(api_key="or-test")
        r = p.complete("test", model="anthropic/claude-sonnet-4-20250514")

        assert r.model == "anthropic/claude-sonnet-4-20250514"

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_complete_token_counts(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _openrouter_response(input_tokens=50, output_tokens=25)

        p = OpenRouterProvider(api_key="or-test")
        r = p.complete("test")

        assert r.input_tokens == 50
        assert r.output_tokens == 25

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_complete_cost_is_int(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _openrouter_response(input_tokens=100_000, output_tokens=50_000)

        p = OpenRouterProvider(api_key="or-test")
        r = p.complete("test")

        assert isinstance(r.cost_hundredths_cent, int)

    # --- chat() ---

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_chat_basic(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _openrouter_response("Chat via OpenRouter")

        p = OpenRouterProvider(api_key="or-test")
        r = p.chat([{"role": "user", "content": "Hello"}])

        assert r.text == "Chat via OpenRouter"

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_chat_sends_authorization_header(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _openrouter_response()

        p = OpenRouterProvider(api_key="or-my-key")
        p.chat([{"role": "user", "content": "test"}])

        headers = mock_http.call_args[1].get("headers", {})
        assert "Authorization" in headers
        assert "or-my-key" in headers["Authorization"]

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_chat_sends_http_referer_header(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _openrouter_response()

        p = OpenRouterProvider(api_key="or-test")
        p.chat([{"role": "user", "content": "test"}])

        headers = mock_http.call_args[1].get("headers", {})
        assert "HTTP-Referer" in headers

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_chat_sends_x_title_header(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _openrouter_response()

        p = OpenRouterProvider(api_key="or-test")
        p.chat([{"role": "user", "content": "test"}])

        headers = mock_http.call_args[1].get("headers", {})
        assert "X-Title" in headers

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_chat_empty_choices_returns_empty_text(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = {"choices": [], "usage": {"prompt_tokens": 3, "completion_tokens": 0}}

        p = OpenRouterProvider(api_key="or-test")
        r = p.chat([{"role": "user", "content": "test"}])

        assert r.text == ""

    # --- Error handling ---

    def test_no_api_key_raises(self):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        with patch.dict(os.environ, {}, clear=True):
            p = OpenRouterProvider(api_key="")
            with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
                p.complete("test")

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_http_401_propagates(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.side_effect = _make_http_error(401, "Bad credentials")

        p = OpenRouterProvider(api_key="or-bad")
        with pytest.raises(Exception) as exc_info:
            p.complete("test")
        assert "401" in str(exc_info.value)

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_http_429_propagates(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.side_effect = _make_http_error(429, "Too many requests")

        p = OpenRouterProvider(api_key="or-test")
        with pytest.raises(Exception) as exc_info:
            p.complete("test")
        assert "429" in str(exc_info.value)

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_http_500_propagates(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.side_effect = _make_http_error(500, "Gateway error")

        p = OpenRouterProvider(api_key="or-test")
        with pytest.raises(Exception) as exc_info:
            p.complete("test")
        assert "500" in str(exc_info.value)

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_request_id_is_sha256(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _openrouter_response()

        p = OpenRouterProvider(api_key="or-test")
        r = p.complete("test prompt")

        assert len(r.request_id) == 64
        assert all(c in "0123456789abcdef" for c in r.request_id)

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_latency_ms_is_non_negative_int(self, mock_http):
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _openrouter_response()

        p = OpenRouterProvider(api_key="or-test")
        r = p.complete("test")

        assert isinstance(r.latency_ms, int)
        assert r.latency_ms >= 0


# ===========================================================================
# Group 4: AnthropicProvider (extends minimal existing coverage)
# ===========================================================================

class TestAnthropicProvider:
    """Extended AnthropicProvider tests beyond what test_llm_client.py covers."""

    # --- Instantiation ---

    def test_init_with_explicit_api_key(self):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        p = AnthropicProvider(api_key="sk-ant-explicit")
        assert p._api_key == "sk-ant-explicit"

    def test_init_reads_env_var(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-env-key"}, clear=True):
            from stillwater.providers.anthropic_provider import AnthropicProvider
            p = AnthropicProvider()
            assert p._get_key() == "sk-ant-env-key"

    def test_name_property(self):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        p = AnthropicProvider(api_key="x")
        assert p.name == "anthropic"

    def test_key_suffix_last_4_chars(self):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        p = AnthropicProvider(api_key="sk-ant-abcd1234")
        suffix = p._key_suffix()
        assert "1234" in suffix
        assert len(suffix) <= 7  # "...XXXX"

    def test_key_suffix_short_key(self):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        p = AnthropicProvider(api_key="abc")
        suffix = p._key_suffix()
        assert suffix == "***"

    def test_models_list_contains_all_three(self):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        p = AnthropicProvider(api_key="x")
        models = p.models()
        assert "claude-opus-4-20250514" in models
        assert "claude-sonnet-4-20250514" in models
        assert "claude-haiku-4-5-20251001" in models

    # --- complete() ---

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_complete_default_model(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response()

        p = AnthropicProvider(api_key="sk-test")
        r = p.complete("test")

        assert r.model == "claude-haiku-4-5-20251001"

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_complete_explicit_model(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response()

        p = AnthropicProvider(api_key="sk-test")
        r = p.complete("test", model="claude-opus-4-20250514")

        assert r.model == "claude-opus-4-20250514"

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_complete_token_counts_from_response(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response(input_tokens=42, output_tokens=21)

        p = AnthropicProvider(api_key="sk-test")
        r = p.complete("test")

        assert r.input_tokens == 42
        assert r.output_tokens == 21

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_complete_cost_is_int(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response(input_tokens=500_000, output_tokens=250_000)

        p = AnthropicProvider(api_key="sk-test")
        r = p.complete("test", model="claude-haiku-4-5-20251001")

        assert isinstance(r.cost_hundredths_cent, int)
        assert not isinstance(r.cost_hundredths_cent, float)

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_complete_cost_haiku_exact(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        # claude-haiku-4-5-20251001: input=80_00, output=400_00 per 1M
        # 1M input => (1_000_000 * 8000) // 1_000_000 = 8000
        mock_http.return_value = _anthropic_response(input_tokens=1_000_000, output_tokens=0)

        p = AnthropicProvider(api_key="sk-test")
        r = p.complete("test", model="claude-haiku-4-5-20251001")

        assert r.cost_hundredths_cent == 8000

    # --- chat() ---

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_chat_separates_system_message(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response()

        p = AnthropicProvider(api_key="sk-test")
        p.chat([
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ])

        payload = mock_http.call_args[0][1]
        assert "system" in payload
        assert payload["system"] == "You are a helpful assistant"
        # User message must still be in messages
        assert any(m["role"] == "user" for m in payload["messages"])

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_chat_multiple_system_messages_joined(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response()

        p = AnthropicProvider(api_key="sk-test")
        p.chat([
            {"role": "system", "content": "Rule A"},
            {"role": "system", "content": "Rule B"},
            {"role": "user", "content": "Hello"},
        ])

        payload = mock_http.call_args[0][1]
        assert payload["system"] == "Rule A\nRule B"

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_chat_no_system_no_system_key(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response()

        p = AnthropicProvider(api_key="sk-test")
        p.chat([{"role": "user", "content": "Hello"}])

        payload = mock_http.call_args[0][1]
        assert "system" not in payload

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_chat_empty_messages_gets_default_user(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response()

        p = AnthropicProvider(api_key="sk-test")
        p.chat([])

        payload = mock_http.call_args[0][1]
        assert len(payload["messages"]) >= 1
        assert payload["messages"][0]["role"] == "user"

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_chat_multi_block_response_concatenated(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_multi_block_response()

        p = AnthropicProvider(api_key="sk-test")
        r = p.chat([{"role": "user", "content": "test"}])

        assert r.text == "Part one. Part two."

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_chat_sends_api_key_header(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response()

        p = AnthropicProvider(api_key="sk-ant-12345678")
        p.chat([{"role": "user", "content": "test"}])

        headers = mock_http.call_args[1].get("headers", {})
        assert "x-api-key" in headers
        assert headers["x-api-key"] == "sk-ant-12345678"

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_chat_sends_anthropic_version_header(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response()

        p = AnthropicProvider(api_key="sk-test")
        p.chat([{"role": "user", "content": "test"}])

        headers = mock_http.call_args[1].get("headers", {})
        assert "anthropic-version" in headers

    # --- Error handling ---

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_http_401_propagates(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.side_effect = _make_http_error(401, "Invalid API key")

        p = AnthropicProvider(api_key="sk-bad")
        with pytest.raises(Exception) as exc_info:
            p.complete("test")
        assert "401" in str(exc_info.value)

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_http_429_propagates(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.side_effect = _make_http_error(429, "Rate limit exceeded")

        p = AnthropicProvider(api_key="sk-test")
        with pytest.raises(Exception) as exc_info:
            p.complete("test")
        assert "429" in str(exc_info.value)

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_http_500_propagates(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.side_effect = _make_http_error(500, "Internal error")

        p = AnthropicProvider(api_key="sk-test")
        with pytest.raises(Exception) as exc_info:
            p.complete("test")
        assert "500" in str(exc_info.value)

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_latency_ms_is_non_negative_int(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response()

        p = AnthropicProvider(api_key="sk-test")
        r = p.complete("test")

        assert isinstance(r.latency_ms, int)
        assert r.latency_ms >= 0

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_timestamp_is_iso8601(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response()

        p = AnthropicProvider(api_key="sk-test")
        r = p.complete("test")

        assert "T" in r.timestamp
        assert ("+" in r.timestamp or "Z" in r.timestamp)


# ===========================================================================
# Group 5: OllamaProvider (extends minimal existing coverage)
# ===========================================================================

class TestOllamaProvider:
    """Extended OllamaProvider tests beyond what test_llm_client.py covers."""

    # --- Instantiation ---

    def test_init_default_url(self):
        from stillwater.providers.ollama_provider import OllamaProvider
        with patch.dict(os.environ, {}, clear=True):
            p = OllamaProvider()
            assert p._url == "http://localhost:11434"

    def test_init_custom_url(self):
        from stillwater.providers.ollama_provider import OllamaProvider
        p = OllamaProvider(url="http://192.168.1.50:11434")
        assert p._url == "http://192.168.1.50:11434"

    def test_init_strips_trailing_slash(self):
        from stillwater.providers.ollama_provider import OllamaProvider
        p = OllamaProvider(url="http://localhost:11434/")
        assert p._url == "http://localhost:11434"

    @patch.dict(os.environ, {"OLLAMA_URL": "http://remote-host:11434"}, clear=True)
    def test_init_from_ollama_url_env(self):
        from stillwater.providers.ollama_provider import OllamaProvider
        p = OllamaProvider()
        assert p._url == "http://remote-host:11434"

    @patch.dict(os.environ, {"OLLAMA_HOST": "http://host-from-env:11434"}, clear=True)
    def test_init_from_ollama_host_env(self):
        from stillwater.providers.ollama_provider import OllamaProvider
        p = OllamaProvider()
        assert p._url == "http://host-from-env:11434"

    def test_name_property(self):
        from stillwater.providers.ollama_provider import OllamaProvider
        p = OllamaProvider()
        assert p.name == "ollama"

    # --- complete() ---

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_complete_text_extracted(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_generate_response("Ollama complete response")

        p = OllamaProvider(url="http://localhost:11434")
        r = p.complete("Tell me something")

        assert r.text == "Ollama complete response"

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_complete_provider_is_ollama(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_generate_response()

        p = OllamaProvider()
        r = p.complete("test")

        assert r.provider == "ollama"

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_complete_default_model(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_generate_response()

        p = OllamaProvider()
        r = p.complete("test")

        assert r.model == "llama3.1:8b"

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_complete_explicit_model(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_generate_response()

        p = OllamaProvider()
        r = p.complete("test", model="codellama:13b")

        assert r.model == "codellama:13b"

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_complete_uses_generate_endpoint(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_generate_response()

        p = OllamaProvider(url="http://localhost:11434")
        p.complete("test")

        called_url = mock_http.call_args[0][0]
        assert "/api/generate" in called_url

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_complete_stream_false_in_payload(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_generate_response()

        p = OllamaProvider()
        p.complete("test")

        payload = mock_http.call_args[0][1]
        assert payload["stream"] is False

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_complete_token_counts_from_eval_count(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_generate_response(prompt_eval=25, eval_count=12)

        p = OllamaProvider()
        r = p.complete("test")

        assert r.input_tokens == 25
        assert r.output_tokens == 12

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_complete_cost_is_zero(self, mock_http):
        """Ollama is free — cost must always be 0."""
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_generate_response(prompt_eval=1_000_000, eval_count=1_000_000)

        p = OllamaProvider()
        r = p.complete("test", model="ollama/llama3.1:8b")

        assert r.cost_hundredths_cent == 0
        assert isinstance(r.cost_hundredths_cent, int)

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_complete_no_eval_count_falls_back_to_estimate(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = {"response": "fallback response"}  # no eval counts

        p = OllamaProvider()
        r = p.complete("test prompt here")

        assert r.input_tokens >= 1
        assert r.output_tokens >= 1

    # --- chat() ---

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_chat_text_extracted(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_chat_response("Ollama chat text")

        p = OllamaProvider()
        r = p.chat([{"role": "user", "content": "Hi"}])

        assert r.text == "Ollama chat text"

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_chat_uses_chat_endpoint(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_chat_response()

        p = OllamaProvider(url="http://localhost:11434")
        p.chat([{"role": "user", "content": "test"}])

        called_url = mock_http.call_args[0][0]
        assert "/api/chat" in called_url

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_chat_stream_false(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_chat_response()

        p = OllamaProvider()
        p.chat([{"role": "user", "content": "test"}])

        payload = mock_http.call_args[0][1]
        assert payload["stream"] is False

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_chat_token_counts(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_chat_response(prompt_eval=30, eval_count=15)

        p = OllamaProvider()
        r = p.chat([{"role": "user", "content": "test"}])

        assert r.input_tokens == 30
        assert r.output_tokens == 15

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_chat_provider_is_ollama(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_chat_response()

        p = OllamaProvider()
        r = p.chat([{"role": "user", "content": "Hi"}])

        assert r.provider == "ollama"

    # --- models() and is_available() ---

    @patch("stillwater.providers.ollama_provider.http_get_json")
    def test_models_returns_sorted_names(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = {
            "models": [
                {"name": "zephyr:7b"},
                {"name": "codellama:13b"},
                {"name": "llama3.1:8b"},
            ]
        }
        p = OllamaProvider()
        models = p.models()

        assert models == sorted(models)
        assert "llama3.1:8b" in models

    @patch("stillwater.providers.ollama_provider.http_get_json")
    def test_models_uses_tags_endpoint(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = {"models": []}

        p = OllamaProvider(url="http://localhost:11434")
        p.models()

        called_url = mock_http.call_args[0][0]
        assert "/api/tags" in called_url

    @patch("stillwater.providers.ollama_provider.http_get_json")
    def test_models_returns_empty_on_error(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.side_effect = ConnectionError("refused")

        p = OllamaProvider()
        models = p.models()

        assert models == []

    @patch("stillwater.providers.ollama_provider.http_get_json")
    def test_is_available_true_when_reachable(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = {"models": [{"name": "llama3.1:8b"}]}

        p = OllamaProvider()
        assert p.is_available() is True

    @patch("stillwater.providers.ollama_provider.http_get_json")
    def test_is_available_false_when_unreachable(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.side_effect = Exception("Connection refused")

        p = OllamaProvider()
        assert p.is_available() is False

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_http_500_propagates_from_chat(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.side_effect = _make_http_error(500, "Ollama server error")

        p = OllamaProvider()
        with pytest.raises(Exception) as exc_info:
            p.chat([{"role": "user", "content": "test"}])
        assert "500" in str(exc_info.value)

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_request_id_is_sha256(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_generate_response()

        p = OllamaProvider()
        r = p.complete("test prompt for sha256")

        assert len(r.request_id) == 64
        assert all(c in "0123456789abcdef" for c in r.request_id)

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_custom_url_used_in_request(self, mock_http):
        """Verify the configured URL is actually used in the HTTP call."""
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_generate_response()

        p = OllamaProvider(url="http://localhost:11434")
        p.complete("test")

        called_url = mock_http.call_args[0][0]
        assert "localhost:11434" in called_url


# ===========================================================================
# Group 6: Provider registry (PROVIDERS dict, list_available_providers,
#           get_cheapest_provider, get_provider)
# ===========================================================================

class TestProviderRegistry:
    """Provider registry — PROVIDERS dict, discovery, cheapest selection."""

    def test_providers_dict_has_five_entries(self):
        from stillwater.providers import _PROVIDER_CLASSES
        assert len(_PROVIDER_CLASSES) >= 5

    def test_providers_dict_has_anthropic(self):
        from stillwater.providers import _PROVIDER_CLASSES
        assert "anthropic" in _PROVIDER_CLASSES

    def test_providers_dict_has_openai(self):
        from stillwater.providers import _PROVIDER_CLASSES
        assert "openai" in _PROVIDER_CLASSES

    def test_providers_dict_has_together(self):
        from stillwater.providers import _PROVIDER_CLASSES
        assert "together" in _PROVIDER_CLASSES

    def test_providers_dict_has_openrouter(self):
        from stillwater.providers import _PROVIDER_CLASSES
        assert "openrouter" in _PROVIDER_CLASSES

    def test_providers_dict_has_ollama(self):
        from stillwater.providers import _PROVIDER_CLASSES
        assert "ollama" in _PROVIDER_CLASSES

    def test_get_provider_anthropic(self):
        from stillwater.providers import get_provider
        p = get_provider("anthropic")
        assert p.name == "anthropic"

    def test_get_provider_openai(self):
        from stillwater.providers import get_provider
        p = get_provider("openai")
        assert p.name == "openai"

    def test_get_provider_together(self):
        from stillwater.providers import get_provider
        p = get_provider("together")
        assert p.name == "together"

    def test_get_provider_openrouter(self):
        from stillwater.providers import get_provider
        p = get_provider("openrouter")
        assert p.name == "openrouter"

    def test_get_provider_ollama(self):
        from stillwater.providers import get_provider
        p = get_provider("ollama")
        assert p.name == "ollama"

    def test_get_provider_unknown_raises_value_error(self):
        from stillwater.providers import get_provider
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("nonexistent-provider-xyz")

    def test_get_provider_error_message_lists_available(self):
        from stillwater.providers import get_provider
        with pytest.raises(ValueError) as exc_info:
            get_provider("fake")
        msg = str(exc_info.value)
        assert "anthropic" in msg

    def test_provider_priority_ollama_in_top_two(self):
        from stillwater.providers import PROVIDER_PRIORITY
        assert "ollama" in PROVIDER_PRIORITY[:2]

    def test_provider_priority_has_all_five(self):
        from stillwater.providers import PROVIDER_PRIORITY
        for name in ["ollama", "together", "openai", "openrouter", "anthropic"]:
            assert name in PROVIDER_PRIORITY

    @patch.dict(os.environ, {}, clear=True)
    def test_list_available_empty_no_keys_no_ollama(self):
        from stillwater.providers import list_available_providers
        from stillwater.providers.ollama_provider import OllamaProvider

        with patch.object(OllamaProvider, "is_available", return_value=False):
            available = list_available_providers()
            assert available == []

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-key"}, clear=True)
    def test_list_available_includes_anthropic_when_key_set(self):
        from stillwater.providers import list_available_providers
        from stillwater.providers.ollama_provider import OllamaProvider

        with patch.object(OllamaProvider, "is_available", return_value=False):
            available = list_available_providers()
            assert "anthropic" in available

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-openai-test"}, clear=True)
    def test_list_available_includes_openai_when_key_set(self):
        from stillwater.providers import list_available_providers
        from stillwater.providers.ollama_provider import OllamaProvider

        with patch.object(OllamaProvider, "is_available", return_value=False):
            available = list_available_providers()
            assert "openai" in available

    @patch.dict(os.environ, {"TOGETHER_API_KEY": "tg-test-key"}, clear=True)
    def test_list_available_includes_together_when_key_set(self):
        from stillwater.providers import list_available_providers
        from stillwater.providers.ollama_provider import OllamaProvider

        with patch.object(OllamaProvider, "is_available", return_value=False):
            available = list_available_providers()
            assert "together" in available

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "or-test-key"}, clear=True)
    def test_list_available_includes_openrouter_when_key_set(self):
        from stillwater.providers import list_available_providers
        from stillwater.providers.ollama_provider import OllamaProvider

        with patch.object(OllamaProvider, "is_available", return_value=False):
            available = list_available_providers()
            assert "openrouter" in available

    def test_list_available_includes_ollama_when_reachable(self):
        from stillwater.providers import list_available_providers
        from stillwater.providers.ollama_provider import OllamaProvider

        with patch.object(OllamaProvider, "is_available", return_value=True):
            with patch.dict(os.environ, {}, clear=True):
                available = list_available_providers()
                assert "ollama" in available

    def test_list_available_follows_priority_order(self):
        from stillwater.providers import list_available_providers, PROVIDER_PRIORITY
        from stillwater.providers.ollama_provider import OllamaProvider

        with patch.object(OllamaProvider, "is_available", return_value=True):
            with patch.dict(os.environ, {
                "ANTHROPIC_API_KEY": "sk-ant",
                "OPENAI_API_KEY": "sk-oa",
            }, clear=True):
                available = list_available_providers()
                # verify ordering matches PROVIDER_PRIORITY
                priority_filtered = [p for p in PROVIDER_PRIORITY if p in available]
                assert priority_filtered == available

    @patch.dict(os.environ, {}, clear=True)
    def test_get_cheapest_provider_none_when_no_providers(self):
        from stillwater.providers import get_cheapest_provider
        from stillwater.providers.ollama_provider import OllamaProvider

        with patch.object(OllamaProvider, "is_available", return_value=False):
            result = get_cheapest_provider()
            assert result is None

    def test_get_cheapest_provider_ollama_when_available(self):
        from stillwater.providers import get_cheapest_provider
        from stillwater.providers.ollama_provider import OllamaProvider

        with patch.object(OllamaProvider, "is_available", return_value=True):
            with patch.dict(os.environ, {}, clear=True):
                result = get_cheapest_provider()
                assert result == "ollama"

    @patch.dict(os.environ, {"TOGETHER_API_KEY": "tg-key"}, clear=True)
    def test_get_cheapest_provider_together_without_ollama(self):
        from stillwater.providers import get_cheapest_provider
        from stillwater.providers.ollama_provider import OllamaProvider

        with patch.object(OllamaProvider, "is_available", return_value=False):
            result = get_cheapest_provider()
            assert result == "together"

    def test_get_provider_with_kwargs_passed_through(self):
        from stillwater.providers import get_provider
        # Verify kwargs are forwarded to provider constructor
        p = get_provider("anthropic", api_key="sk-forwarded-key")
        assert p._api_key == "sk-forwarded-key"

    def test_get_provider_ollama_with_url_kwarg(self):
        from stillwater.providers import get_provider
        p = get_provider("ollama", url="http://custom-host:11434")
        assert p._url == "http://custom-host:11434"


# ===========================================================================
# Group 7: Token estimation helpers
# ===========================================================================

class TestTokenEstimation:
    """Token estimation utility tests."""

    def test_estimate_tokens_basic(self):
        from stillwater.providers._helpers import estimate_tokens
        # 12 chars / 4 = 3
        assert estimate_tokens("hello world!") == 3

    def test_estimate_tokens_empty_returns_one(self):
        from stillwater.providers._helpers import estimate_tokens
        assert estimate_tokens("") == 1

    def test_estimate_tokens_minimum_is_one(self):
        from stillwater.providers._helpers import estimate_tokens
        assert estimate_tokens("a") == 1  # 1 char / 4 = 0, clamped to 1

    def test_estimate_tokens_long_text(self):
        from stillwater.providers._helpers import estimate_tokens
        text = "x" * 400  # 400 chars
        assert estimate_tokens(text) == 100

    def test_estimate_tokens_returns_int(self):
        from stillwater.providers._helpers import estimate_tokens
        result = estimate_tokens("some text here in a prompt")
        assert isinstance(result, int)

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_openai_uses_token_estimate_without_usage(self, mock_http):
        """When API returns no usage, estimate_tokens is used as fallback."""
        from stillwater.providers.openai_provider import OpenAIProvider
        from stillwater.providers._helpers import estimate_tokens
        prompt_text = "what is the meaning of life"
        mock_http.return_value = _openai_response_no_usage("Forty two")

        p = OpenAIProvider(api_key="sk-test")
        r = p.chat([{"role": "user", "content": prompt_text}])

        # Tokens come from estimate_tokens fallback
        expected_input = estimate_tokens(f"user: {prompt_text}")
        assert r.input_tokens == expected_input

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_ollama_uses_token_estimate_without_eval_count(self, mock_http):
        """When Ollama returns no eval_count, estimate_tokens is used."""
        from stillwater.providers.ollama_provider import OllamaProvider
        from stillwater.providers._helpers import estimate_tokens
        prompt_text = "describe the universe in one word"
        mock_http.return_value = {"response": "Vast"}  # no eval counts

        p = OllamaProvider()
        r = p.complete(prompt_text)

        expected_output = estimate_tokens("Vast")
        assert r.output_tokens == expected_output


# ===========================================================================
# Group 8: Cost calculation cross-provider verification
# ===========================================================================

class TestCostCalculationCrossProvider:
    """Verify cost is always integer, never float, across all providers."""

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_anthropic_haiku_cost_integer(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response(input_tokens=999_999, output_tokens=123_456)

        p = AnthropicProvider(api_key="sk-test")
        r = p.complete("test", model="claude-haiku-4-5-20251001")

        assert isinstance(r.cost_hundredths_cent, int)

    @patch("stillwater.providers.anthropic_provider.http_post_json")
    def test_anthropic_sonnet_cost_integer(self, mock_http):
        from stillwater.providers.anthropic_provider import AnthropicProvider
        mock_http.return_value = _anthropic_response(input_tokens=100_000, output_tokens=50_000)

        p = AnthropicProvider(api_key="sk-test")
        r = p.complete("test", model="claude-sonnet-4-20250514")

        assert isinstance(r.cost_hundredths_cent, int)

    @patch("stillwater.providers.openai_provider.http_post_json")
    def test_openai_gpt4o_cost_integer(self, mock_http):
        from stillwater.providers.openai_provider import OpenAIProvider
        mock_http.return_value = _openai_response(input_tokens=200_000, output_tokens=100_000)

        p = OpenAIProvider(api_key="sk-test")
        r = p.complete("test", model="gpt-4o")

        assert isinstance(r.cost_hundredths_cent, int)

    @patch("stillwater.providers.together_provider.http_post_json")
    def test_together_cost_integer(self, mock_http):
        from stillwater.providers.together_provider import TogetherProvider
        mock_http.return_value = _together_response(input_tokens=500_000, output_tokens=250_000)

        p = TogetherProvider(api_key="tg-test")
        r = p.complete("test", model="meta-llama/Llama-3.3-70B-Instruct")

        assert isinstance(r.cost_hundredths_cent, int)

    @patch("stillwater.providers.ollama_provider.http_post_json")
    def test_ollama_cost_always_zero(self, mock_http):
        from stillwater.providers.ollama_provider import OllamaProvider
        mock_http.return_value = _ollama_generate_response(prompt_eval=999_999, eval_count=999_999)

        p = OllamaProvider()
        r = p.complete("test", model="ollama/anything")

        assert r.cost_hundredths_cent == 0
        assert isinstance(r.cost_hundredths_cent, int)

    @patch("stillwater.providers.openrouter_provider.http_post_json")
    def test_openrouter_unknown_model_cost_zero(self, mock_http):
        """Unknown model in pricing table returns 0 cost."""
        from stillwater.providers.openrouter_provider import OpenRouterProvider
        mock_http.return_value = _openrouter_response(input_tokens=100_000, output_tokens=50_000)

        p = OpenRouterProvider(api_key="or-test")
        r = p.complete("test", model="some/unknown-model-xyz-999")

        assert isinstance(r.cost_hundredths_cent, int)
        assert r.cost_hundredths_cent == 0

    def test_no_float_in_pricing_table(self):
        from stillwater.providers.pricing import MODEL_PRICING
        for model, prices in MODEL_PRICING.items():
            assert isinstance(prices["input"], int), f"float found in {model} input"
            assert isinstance(prices["output"], int), f"float found in {model} output"

    def test_estimate_cost_always_returns_int(self):
        from stillwater.providers.pricing import estimate_cost
        for tokens in [1, 100, 1000, 10_000, 1_000_000]:
            cost = estimate_cost(tokens, tokens, "gpt-4o-mini")
            assert isinstance(cost, int), f"Float found at tokens={tokens}"

    def test_cost_arithmetic_no_float_drift_across_1000_calls(self):
        """Accumulated cost must remain exact integer across many calls."""
        from stillwater.providers.pricing import estimate_cost
        total = 0
        for _ in range(1_000):
            total += estimate_cost(1_000, 500, "claude-haiku-4-5-20251001")
        assert isinstance(total, int)
        # 1000 input * 8000 // 1M = 8; 500 output * 40000 // 1M = 20; per call = 28
        # 1000 calls = 28_000
        assert total == 28_000
