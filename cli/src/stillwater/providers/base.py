"""
Stillwater LLM Provider Base Class
Version: 1.0.0

Abstract base for all LLM providers. Each provider implements:
- complete(): single prompt -> response
- chat(): message list -> response
- models(): list available model names
- is_available(): check if API key / endpoint is configured
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LLMResponse:
    """
    Immutable response from an LLM call.

    All cost fields use int (hundredths of a cent) -- never float.
    """
    text: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    cost_hundredths_cent: int  # exact arithmetic, no float
    latency_ms: int
    request_id: str  # SHA-256 hex digest of request content
    timestamp: str  # ISO 8601

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for JSON logging."""
        return {
            "text": self.text,
            "model": self.model,
            "provider": self.provider,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_hundredths_cent": self.cost_hundredths_cent,
            "latency_ms": self.latency_ms,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
        }


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g. 'anthropic', 'openai', 'ollama')."""
        ...

    @abstractmethod
    def complete(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float = 30.0,
    ) -> LLMResponse:
        """
        Send a single prompt and return a structured response.

        Args:
            prompt: The user prompt.
            model: Model name to use.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.
            timeout: Request timeout in seconds.

        Returns:
            LLMResponse with all fields populated.
        """
        ...

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float = 30.0,
    ) -> LLMResponse:
        """
        Send a chat messages list (OpenAI format) and return structured response.

        Args:
            messages: List of {"role": str, "content": str} dicts.
            model: Model name to use.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.
            timeout: Request timeout in seconds.

        Returns:
            LLMResponse with all fields populated.
        """
        ...

    @abstractmethod
    def models(self) -> list[str]:
        """Return list of available model names for this provider."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured and ready (API key set, endpoint reachable, etc.)."""
        ...
