"""Tests for the configuration system."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from stillwater.config import StillwaterConfig, load_config


def test_defaults_no_file() -> None:
    """Defaults work with no config file."""
    cfg = load_config(path=Path("/nonexistent/stillwater.toml"))
    assert cfg.llm.provider == "ollama"
    assert cfg.llm.ollama.host == "localhost"
    assert cfg.llm.ollama.port == 11434
    assert cfg.llm.ollama.model == "llama3.1:8b"
    assert cfg.llm.openai.model == "gpt-4o-mini"


def test_load_from_toml(tmp_path: Path) -> None:
    """Loads values from a TOML file."""
    toml = tmp_path / "stillwater.toml"
    toml.write_text(textwrap.dedent("""\
        [llm]
        provider = "openai"

        [llm.ollama]
        host = "remote-host"
        port = 9999
        model = "qwen2.5:7b"

        [llm.openai]
        base_url = "https://custom.api/v1"
        api_key = "sk-test"
        model = "gpt-4o"
    """))
    cfg = load_config(path=toml)
    assert cfg.llm.provider == "openai"
    assert cfg.llm.ollama.host == "remote-host"
    assert cfg.llm.ollama.port == 9999
    assert cfg.llm.ollama.model == "qwen2.5:7b"
    assert cfg.llm.openai.base_url == "https://custom.api/v1"
    assert cfg.llm.openai.api_key == "sk-test"
    assert cfg.llm.openai.model == "gpt-4o"


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment variables override TOML and defaults."""
    monkeypatch.setenv("STILLWATER_LLM_PROVIDER", "openai")
    monkeypatch.setenv("STILLWATER_OLLAMA_HOST", "env-host")
    monkeypatch.setenv("STILLWATER_OLLAMA_PORT", "5555")
    monkeypatch.setenv("STILLWATER_OLLAMA_MODEL", "env-model:8b")
    monkeypatch.setenv("STILLWATER_OPENAI_BASE_URL", "https://env.api/v1")
    monkeypatch.setenv("STILLWATER_OPENAI_API_KEY", "sk-env")
    monkeypatch.setenv("STILLWATER_OPENAI_MODEL", "env-gpt")

    cfg = load_config(path=Path("/nonexistent/stillwater.toml"))
    assert cfg.llm.provider == "openai"
    assert cfg.llm.ollama.host == "env-host"
    assert cfg.llm.ollama.port == 5555
    assert cfg.llm.ollama.model == "env-model:8b"
    assert cfg.llm.openai.base_url == "https://env.api/v1"
    assert cfg.llm.openai.api_key == "sk-env"
    assert cfg.llm.openai.model == "env-gpt"


def test_env_overrides_toml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Env vars take precedence over TOML values."""
    toml = tmp_path / "stillwater.toml"
    toml.write_text(textwrap.dedent("""\
        [llm]
        provider = "ollama"

        [llm.ollama]
        model = "toml-model:8b"
    """))
    monkeypatch.setenv("STILLWATER_OLLAMA_MODEL", "env-model:7b")
    cfg = load_config(path=toml)
    assert cfg.llm.provider == "ollama"
    assert cfg.llm.ollama.model == "env-model:7b"


def test_ollama_base_url() -> None:
    """OllamaConfig.base_url property constructs URL correctly."""
    cfg = load_config(path=Path("/nonexistent/stillwater.toml"))
    assert cfg.llm.ollama.base_url == "http://localhost:11434"


def test_partial_toml(tmp_path: Path) -> None:
    """Partial TOML files use defaults for missing values."""
    toml = tmp_path / "stillwater.toml"
    toml.write_text(textwrap.dedent("""\
        [llm]
        provider = "openai"
    """))
    cfg = load_config(path=toml)
    assert cfg.llm.provider == "openai"
    assert cfg.llm.ollama.host == "localhost"
    assert cfg.llm.ollama.model == "llama3.1:8b"
