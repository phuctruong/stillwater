"""
Stillwater Anthropic Provider (Claude)
Version: 1.0.0

Uses stdlib urllib only -- no anthropic SDK dependency.
POST https://api.anthropic.com/v1/messages
"""

from __future__ import annotations

import os
import time
from typing import Optional

from .base import LLMProvider, LLMResponse
from ._http import http_post_json
from ._helpers import build_response, messages_to_prompt, estimate_tokens

_API_URL = "https://api.anthropic.com/v1/messages"
_API_VERSION = "2023-06-01"

_MODELS = [
    "claude-opus-4-20250514",
    "claude-sonnet-4-20250514",
    "claude-haiku-4-5-20251001",
]

_DEFAULT_MODEL = "claude-haiku-4-5-20251001"


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider using raw HTTP (no SDK)."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")

    @property
    def name(self) -> str:
        return "anthropic"

    def _get_key(self) -> str:
        """Return API key, refreshing from env if initially empty."""
        if not self._api_key:
            self._api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        return self._api_key

    def _key_suffix(self) -> str:
        """Last 4 chars of API key for debug (never full key)."""
        k = self._get_key()
        return f"...{k[-4:]}" if len(k) >= 4 else "***"

    def complete(
        self,
        prompt: str,
        model: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float = 30.0,
    ) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, model=model, max_tokens=max_tokens,
                         temperature=temperature, timeout=timeout)

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float = 30.0,
    ) -> LLMResponse:
        api_key = self._get_key()
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")

        resolved_model = model or _DEFAULT_MODEL

        # Separate system messages from user/assistant messages
        system_parts = []
        chat_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_parts.append(content)
            else:
                chat_messages.append({"role": role, "content": content})

        # Anthropic requires at least one user message
        if not chat_messages:
            chat_messages = [{"role": "user", "content": ""}]

        payload: dict = {
            "model": resolved_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": chat_messages,
        }
        if system_parts:
            payload["system"] = "\n".join(system_parts)

        headers = {
            "x-api-key": api_key,
            "anthropic-version": _API_VERSION,
        }

        request_content = messages_to_prompt(messages)
        start = time.monotonic()

        resp = http_post_json(_API_URL, payload, headers=headers, timeout=timeout)

        latency_ms = int((time.monotonic() - start) * 1000)

        # Parse response
        content_blocks = resp.get("content", [])
        text = ""
        for block in content_blocks:
            if isinstance(block, dict) and block.get("type") == "text":
                text += block.get("text", "")

        # Token usage from response
        usage = resp.get("usage", {})
        input_tokens = usage.get("input_tokens", estimate_tokens(request_content))
        output_tokens = usage.get("output_tokens", estimate_tokens(text))

        return build_response(
            text=text,
            model=resolved_model,
            provider=self.name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            request_content=request_content,
        )

    def models(self) -> list[str]:
        return list(_MODELS)

    def is_available(self) -> bool:
        return bool(self._get_key())
