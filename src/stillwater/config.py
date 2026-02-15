"""Configuration loading for Stillwater OS.

Loads from stillwater.toml with environment variable overrides.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]


@dataclass
class OllamaConfig:
    host: str = "localhost"
    port: int = 11434
    model: str = "llama3.1:8b"

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


@dataclass
class OpenAIConfig:
    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-4o-mini"


@dataclass
class LLMConfig:
    provider: str = "ollama"
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)


@dataclass
class StillwaterConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)


def _find_config_file() -> Path | None:
    """Search for stillwater.toml in CWD and parents."""
    current = Path.cwd()
    for directory in [current, *current.parents]:
        candidate = directory / "stillwater.toml"
        if candidate.is_file():
            return candidate
    return None


def load_config(path: Path | None = None) -> StillwaterConfig:
    """Load configuration from stillwater.toml with env var overrides.

    Priority: env vars > toml file > defaults.
    """
    cfg = StillwaterConfig()

    # Load TOML if available
    toml_path = path or _find_config_file()
    if toml_path and toml_path.is_file() and tomllib is not None:
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)

        llm = data.get("llm", {})
        if "provider" in llm:
            cfg.llm.provider = llm["provider"]

        ollama = llm.get("ollama", {})
        if "host" in ollama:
            cfg.llm.ollama.host = ollama["host"]
        if "port" in ollama:
            cfg.llm.ollama.port = int(ollama["port"])
        if "model" in ollama:
            cfg.llm.ollama.model = ollama["model"]

        openai = llm.get("openai", {})
        if "base_url" in openai:
            cfg.llm.openai.base_url = openai["base_url"]
        if "api_key" in openai:
            cfg.llm.openai.api_key = openai["api_key"]
        if "model" in openai:
            cfg.llm.openai.model = openai["model"]

    # Env var overrides
    if v := os.environ.get("STILLWATER_LLM_PROVIDER"):
        cfg.llm.provider = v
    if v := os.environ.get("STILLWATER_OLLAMA_HOST"):
        cfg.llm.ollama.host = v
    if v := os.environ.get("STILLWATER_OLLAMA_PORT"):
        cfg.llm.ollama.port = int(v)
    if v := os.environ.get("STILLWATER_OLLAMA_MODEL"):
        cfg.llm.ollama.model = v
    if v := os.environ.get("STILLWATER_OPENAI_BASE_URL"):
        cfg.llm.openai.base_url = v
    if v := os.environ.get("STILLWATER_OPENAI_API_KEY"):
        cfg.llm.openai.api_key = v
    if v := os.environ.get("STILLWATER_OPENAI_MODEL"):
        cfg.llm.openai.model = v

    return cfg
