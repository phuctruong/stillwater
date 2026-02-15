"""Tests for the LLM client (mocked, no real API calls)."""

from __future__ import annotations

import json
from unittest import mock

import pytest

from stillwater.config import StillwaterConfig, load_config
from stillwater.llm import LLMClient, LLMError


def _mock_config(provider: str = "ollama") -> StillwaterConfig:
    """Create a config pointing at nothing (tests will mock HTTP)."""
    from pathlib import Path

    cfg = load_config(path=Path("/nonexistent/stillwater.toml"))
    cfg.llm.provider = provider
    return cfg


def _ollama_response(text: str) -> mock.Mock:
    resp = mock.Mock()
    resp.status_code = 200
    resp.json.return_value = {"response": text}
    resp.raise_for_status = mock.Mock()
    return resp


def _openai_response(text: str) -> mock.Mock:
    resp = mock.Mock()
    resp.status_code = 200
    resp.json.return_value = {
        "choices": [{"message": {"content": text}}]
    }
    resp.raise_for_status = mock.Mock()
    return resp


class TestOllamaClient:
    def test_generate_basic(self) -> None:
        client = LLMClient(config=_mock_config("ollama"))
        with mock.patch("stillwater.llm.requests.post", return_value=_ollama_response("hello")):
            result = client.generate("say hello")
        assert result == "hello"

    def test_generate_with_temperature(self) -> None:
        client = LLMClient(config=_mock_config("ollama"))
        with mock.patch("stillwater.llm.requests.post", return_value=_ollama_response("ok")) as m:
            client.generate("test", temperature=0)
        payload = m.call_args[1]["json"]
        assert payload["options"]["temperature"] == 0
        assert payload["stream"] is False

    def test_model_override(self) -> None:
        client = LLMClient(config=_mock_config("ollama"), model="qwen2.5:7b")
        assert client.model == "qwen2.5:7b"

    def test_provider_property(self) -> None:
        client = LLMClient(config=_mock_config("ollama"))
        assert client.provider == "ollama"
        assert client.endpoint == "http://localhost:11434"

    def test_connection_error(self) -> None:
        client = LLMClient(config=_mock_config("ollama"))
        import requests
        with mock.patch(
            "stillwater.llm.requests.post",
            side_effect=requests.ConnectionError("refused"),
        ):
            with pytest.raises(LLMError, match="Ollama request failed"):
                client.generate("test")


class TestOpenAIClient:
    def test_generate_basic(self) -> None:
        client = LLMClient(config=_mock_config("openai"))
        with mock.patch("stillwater.llm.requests.post", return_value=_openai_response("world")):
            result = client.generate("say world")
        assert result == "world"

    def test_generate_sends_auth_header(self) -> None:
        cfg = _mock_config("openai")
        cfg.llm.openai.api_key = "sk-test-key"
        client = LLMClient(config=cfg)
        with mock.patch("stillwater.llm.requests.post", return_value=_openai_response("ok")) as m:
            client.generate("test")
        headers = m.call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer sk-test-key"

    def test_model_override(self) -> None:
        client = LLMClient(config=_mock_config("openai"), model="gpt-4o")
        assert client.model == "gpt-4o"

    def test_connection_error(self) -> None:
        client = LLMClient(config=_mock_config("openai"))
        import requests
        with mock.patch(
            "stillwater.llm.requests.post",
            side_effect=requests.ConnectionError("refused"),
        ):
            with pytest.raises(LLMError, match="OpenAI request failed"):
                client.generate("test")


class TestUnknownProvider:
    def test_unknown_provider_raises(self) -> None:
        cfg = _mock_config()
        cfg.llm.provider = "unknown"
        client = LLMClient(config=cfg)
        with pytest.raises(LLMError, match="unknown provider"):
            client.generate("test")
