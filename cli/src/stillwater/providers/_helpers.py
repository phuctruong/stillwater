"""
Shared helpers for LLM providers.
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone

from .base import LLMResponse
from .pricing import estimate_cost


def make_request_id(content: str) -> str:
    """Generate SHA-256 hex digest of request content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def iso_now() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def build_response(
    text: str,
    model: str,
    provider: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    request_content: str,
) -> LLMResponse:
    """Build an LLMResponse with cost calculation and request ID."""
    return LLMResponse(
        text=text,
        model=model,
        provider=provider,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_hundredths_cent=estimate_cost(input_tokens, output_tokens, model),
        latency_ms=latency_ms,
        request_id=make_request_id(request_content),
        timestamp=iso_now(),
    )


def messages_to_prompt(messages: list[dict[str, str]]) -> str:
    """Flatten a messages list into a single prompt string (for request ID hashing)."""
    return "\n".join(
        f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages
    )


def estimate_tokens(text: str) -> int:
    """
    Rough token estimate: ~4 characters per token.
    Used only when the API doesn't return token counts.
    """
    return max(1, len(text) // 4)
