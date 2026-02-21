"""
Stillwater Together.ai Provider
Version: 1.0.0

Uses stdlib urllib only.
POST https://api.together.xyz/v1/chat/completions (OpenAI-compatible)
"""

from __future__ import annotations

import os
import time
from typing import Optional

from .base import LLMProvider, LLMResponse
from ._http import http_post_json
from ._helpers import build_response, messages_to_prompt, estimate_tokens

_API_URL = "https://api.together.xyz/v1/chat/completions"

_MODELS = [
    "meta-llama/Llama-3.3-70B-Instruct",
]

_DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct"


class TogetherProvider(LLMProvider):
    """Together.ai provider using OpenAI-compatible API."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.environ.get("TOGETHER_API_KEY", "")

    @property
    def name(self) -> str:
        return "together"

    def _get_key(self) -> str:
        if not self._api_key:
            self._api_key = os.environ.get("TOGETHER_API_KEY", "")
        return self._api_key

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
            raise RuntimeError("TOGETHER_API_KEY not set")

        resolved_model = model or _DEFAULT_MODEL

        payload = {
            "model": resolved_model,
            "messages": [{"role": m.get("role", "user"), "content": m.get("content", "")}
                         for m in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
        }

        request_content = messages_to_prompt(messages)
        start = time.monotonic()

        resp = http_post_json(_API_URL, payload, headers=headers, timeout=timeout)

        latency_ms = int((time.monotonic() - start) * 1000)

        # Parse OpenAI-compatible response
        choices = resp.get("choices", [])
        text = ""
        if choices:
            text = choices[0].get("message", {}).get("content", "")

        usage = resp.get("usage", {})
        input_tokens = usage.get("prompt_tokens", estimate_tokens(request_content))
        output_tokens = usage.get("completion_tokens", estimate_tokens(text))

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
