"""
Stillwater LLM Provider Registry
Version: 1.0.0

Central registry for all LLM providers. Auto-discovers available providers
from environment variables and configuration.

Usage:
    from stillwater.providers import get_provider, list_available_providers

    providers = list_available_providers()
    anthropic = get_provider("anthropic")
"""

from __future__ import annotations

from typing import Optional

from .base import LLMProvider, LLMResponse
from .pricing import MODEL_PRICING, estimate_cost, get_pricing, resolve_model_name
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider
from .together_provider import TogetherProvider
from .openrouter_provider import OpenRouterProvider
from .ollama_provider import OllamaProvider
from .claude_code_cli_provider import ClaudeCodeCLIProvider
from .codex_wrapper_provider import CodexWrapperProvider
from .http_provider import HTTPProvider


# Registry of all provider classes, keyed by name
_PROVIDER_CLASSES: dict[str, type[LLMProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "together": TogetherProvider,
    "openrouter": OpenRouterProvider,
    "ollama": OllamaProvider,
    "claude-code-cli": ClaudeCodeCLIProvider,
    "codex-wrapper": CodexWrapperProvider,
    "http": HTTPProvider,
}

# Provider priority for auto-selection (cheapest first)
PROVIDER_PRIORITY: list[str] = [
    "claude-code-cli",  # free (local, no API key)
    "ollama",           # free (local)
    "codex-wrapper",    # free (local, no API key)
    "together",         # market rate
    "openai",           # gpt-4o-mini: $0.15/M input
    "openrouter",       # variable
    "anthropic",        # haiku: $0.80/M input
]


def get_provider(name: str, **kwargs) -> LLMProvider:
    """
    Get a provider instance by name.

    Args:
        name: Provider name (e.g. 'anthropic', 'openai', 'ollama').
        **kwargs: Passed to provider constructor (e.g. api_key=, url=).

    Returns:
        LLMProvider instance.

    Raises:
        ValueError: If provider name is unknown.
    """
    cls = _PROVIDER_CLASSES.get(name)
    if cls is None:
        raise ValueError(
            f"Unknown provider: {name!r}. Available: {sorted(_PROVIDER_CLASSES.keys())}"
        )
    return cls(**kwargs)


def list_available_providers() -> list[str]:
    """
    Return names of providers that have valid configuration (API keys set, etc.)
    Checks each registered provider's is_available() method.
    """
    available = []
    for name in PROVIDER_PRIORITY:
        try:
            provider = get_provider(name)
            if provider.is_available():
                available.append(name)
        except Exception:
            pass
    return available


def get_cheapest_provider() -> Optional[str]:
    """Return the name of the cheapest available provider, or None."""
    available = list_available_providers()
    return available[0] if available else None


__all__ = [
    "LLMProvider",
    "LLMResponse",
    "AnthropicProvider",
    "OpenAIProvider",
    "TogetherProvider",
    "OpenRouterProvider",
    "OllamaProvider",
    "ClaudeCodeCLIProvider",
    "CodexWrapperProvider",
    "HTTPProvider",
    "get_provider",
    "list_available_providers",
    "get_cheapest_provider",
    "estimate_cost",
    "get_pricing",
    "resolve_model_name",
    "MODEL_PRICING",
    "PROVIDER_PRIORITY",
]
