"""
Stillwater Provider Registry — High-Level Facade
Version: 1.0.0 | Auth: 641 | Status: STABLE

High-level provider registry for multi-provider LLM routing.
Wraps the low-level providers/ package with a simpler dict-based API.

Supported providers:
    anthropic   — Claude (claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001)
    openai      — GPT (gpt-4o, gpt-4o-mini)
    ollama      — Local Ollama (configurable endpoint, free)
    together    — Together.ai (meta-llama/Llama-3.3-70B-Instruct, etc.)
    openrouter  — OpenRouter (aggregated multi-vendor)
    custom      — Custom endpoint {base_url, api_key, model_id}

Usage:
    from stillwater.providers import PROVIDERS, get_provider, list_providers, validate_provider

    all_names = list_providers()             # ["anthropic", "openai", "ollama", ...]
    config    = get_provider("anthropic")    # {base_url, api_key_env, models: list}
    ok        = validate_provider("openai")  # True iff OPENAI_API_KEY is set (or ollama reachable)

Note: this module is the high-level facade. The low-level provider classes live in
stillwater.providers.anthropic_provider etc. and are imported via
`from stillwater.providers import get_provider as _get_llm_provider`.
"""

from __future__ import annotations

import os
from typing import Any, Optional

# ---------------------------------------------------------------------------
# PROVIDERS dict — static registry of all known providers
# ---------------------------------------------------------------------------
# Each entry: {base_url, api_key_env, models: list[str]}
# base_url: the API endpoint root
# api_key_env: env var name that holds the API key (None for Ollama — no key needed)
# models: canonical model IDs for this provider

PROVIDERS: dict[str, dict[str, Any]] = {
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "api_key_env": "ANTHROPIC_API_KEY",
        "models": [
            "claude-opus-4-6",
            "claude-sonnet-4-6",
            "claude-haiku-4-5-20251001",
        ],
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "models": [
            "gpt-4o",
            "gpt-4o-mini",
        ],
    },
    "ollama": {
        "base_url": os.environ.get("OLLAMA_URL", "http://localhost:11434"),
        "api_key_env": None,  # No API key needed for local Ollama
        "models": [
            "llama3.1:8b",
            "llama3.1:70b",
            "codellama:13b",
            "mistral:7b",
        ],
    },
    "codex-wrapper": {
        "base_url": os.environ.get("CODEX_WRAPPER_URL", "http://localhost:8081"),
        "api_key_env": None,
        "models": [
            "codex-default",
        ],
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "api_key_env": "TOGETHER_API_KEY",
        "models": [
            "meta-llama/Llama-3.3-70B-Instruct",
            "meta-llama/Llama-3.1-8B-Instruct-Turbo",
        ],
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "models": [
            "anthropic/claude-3-haiku",
            "openai/gpt-4o-mini",
            "meta-llama/llama-3.3-70b-instruct",
        ],
    },
}

# ---------------------------------------------------------------------------
# Model → provider routing table
# ---------------------------------------------------------------------------
# Maps model name prefixes/exact IDs to provider names.

_MODEL_PROVIDER_MAP: dict[str, str] = {
    # Anthropic
    "claude-opus-4-6": "anthropic",
    "claude-sonnet-4-6": "anthropic",
    "claude-haiku-4-5-20251001": "anthropic",
    "claude-opus-4-20250514": "anthropic",
    "claude-sonnet-4-20250514": "anthropic",
    # OpenAI
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    "codex-default": "codex-wrapper",
    # Together
    "meta-llama/Llama-3.3-70B-Instruct": "together",
    "meta-llama/Llama-3.1-8B-Instruct-Turbo": "together",
    # Ollama (prefix match: checked separately)
}

_OLLAMA_PREFIXES = ("ollama/", "llama3", "codellama", "mistral", "llava")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_provider(name: str) -> dict[str, Any]:
    """Return the provider config dict for the given name.

    Args:
        name: Provider name (e.g. 'anthropic', 'openai', 'ollama').

    Returns:
        Dict with keys: base_url, api_key_env, models.

    Raises:
        ValueError: If the provider name is not registered.
    """
    if name not in PROVIDERS:
        raise ValueError(
            f"Unknown provider: {name!r}. Available: {sorted(PROVIDERS.keys())}"
        )
    return dict(PROVIDERS[name])  # return a copy


def list_providers() -> list[str]:
    """Return all registered provider names (sorted alphabetically)."""
    return sorted(PROVIDERS.keys())


def validate_provider(name: str) -> bool:
    """Check whether the given provider is configured and ready.

    For key-based providers: returns True iff the API key env var is set and non-empty.
    For Ollama (no key needed): returns True iff OLLAMA_URL is set OR the
        default localhost:11434 is assumed reachable (no actual TCP check).
    For unknown provider names: returns False.

    Args:
        name: Provider name.

    Returns:
        True if the provider appears configured; False otherwise.
    """
    if name not in PROVIDERS:
        return False

    config = PROVIDERS[name]
    api_key_env = config.get("api_key_env")

    if api_key_env is None:
        # Ollama — no API key required; presence of OLLAMA_URL or default is sufficient
        return True

    # Key-based provider: check the env var
    key = os.environ.get(api_key_env, "")
    return bool(key)


def resolve_provider_for_model(model: str) -> Optional[str]:
    """Return the provider name for the given model, or None if unknown.

    Checks exact model map first, then Ollama prefixes.

    Args:
        model: Model name (e.g. 'gpt-4o', 'claude-opus-4-6').

    Returns:
        Provider name string, or None if no mapping found.
    """
    if model in _MODEL_PROVIDER_MAP:
        return _MODEL_PROVIDER_MAP[model]

    # Ollama prefix check
    for prefix in _OLLAMA_PREFIXES:
        if model.startswith(prefix):
            return "ollama"

    return None


def register_custom_provider(
    name: str,
    base_url: str,
    api_key_env: Optional[str],
    models: list[str],
) -> None:
    """Register a custom provider in the PROVIDERS registry.

    Allows dynamic registration of custom endpoints (e.g. self-hosted vLLM,
    LM Studio, etc.).

    Args:
        name:        Provider identifier (e.g. 'my-vllm').
        base_url:    API endpoint root URL.
        api_key_env: Env var name for the API key, or None if no key required.
        models:      List of model IDs this provider supports.

    Note:
        This mutates the module-level PROVIDERS dict. In tests, restore with
        `del PROVIDERS[name]` or use monkeypatching.
    """
    PROVIDERS[name] = {
        "base_url": base_url,
        "api_key_env": api_key_env,
        "models": list(models),
    }
