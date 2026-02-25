"""
Stillwater Ollama Provider (local/offline)
Version: 1.0.0

Uses stdlib urllib only.
POST http://localhost:11434/api/generate (generate endpoint)
POST http://localhost:11434/api/chat (chat endpoint)
GET  http://localhost:11434/api/tags (list models)

Free, no API key needed. URL is configurable.
"""

from __future__ import annotations

import os
import time
from typing import Optional

from .base import LLMProvider, LLMResponse
from ._http import http_post_json, http_get_json
from ._helpers import build_response, messages_to_prompt, estimate_tokens

_DEFAULT_URL = "http://localhost:11434"
_DEFAULT_MODEL = "llama3.1:8b"


class OllamaProvider(LLMProvider):
    """Ollama local provider -- free, no API key, configurable URL."""

    def __init__(self, url: Optional[str] = None) -> None:
        raw = url or os.environ.get("OLLAMA_URL", "") or os.environ.get("OLLAMA_HOST", "")
        self._url = raw.rstrip("/") if raw else _DEFAULT_URL

    @property
    def name(self) -> str:
        return "ollama"

    def complete(
        self,
        prompt: str,
        model: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float = 30.0,
    ) -> LLMResponse:
        resolved_model = model or _DEFAULT_MODEL

        payload: dict = {
            "model": resolved_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        request_content = f"user: {prompt}"
        start = time.monotonic()

        resp = http_post_json(
            f"{self._url}/api/generate", payload, timeout=timeout,
        )

        latency_ms = int((time.monotonic() - start) * 1000)

        text = resp.get("response", "")

        # Ollama returns eval_count/prompt_eval_count
        input_tokens = resp.get("prompt_eval_count", estimate_tokens(prompt))
        output_tokens = resp.get("eval_count", estimate_tokens(text))

        return build_response(
            text=text,
            model=resolved_model,
            provider=self.name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            request_content=request_content,
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float = 30.0,
    ) -> LLMResponse:
        resolved_model = model or _DEFAULT_MODEL

        payload = {
            "model": resolved_model,
            "messages": [{"role": m.get("role", "user"), "content": m.get("content", "")}
                         for m in messages],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        request_content = messages_to_prompt(messages)
        start = time.monotonic()

        resp = http_post_json(
            f"{self._url}/api/chat", payload, timeout=timeout,
        )

        latency_ms = int((time.monotonic() - start) * 1000)

        # Ollama chat returns {"message": {"role": "assistant", "content": "..."}}
        text = resp.get("message", {}).get("content", "")

        input_tokens = resp.get("prompt_eval_count", estimate_tokens(request_content))
        output_tokens = resp.get("eval_count", estimate_tokens(text))

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
        """Fetch models from Ollama /api/tags endpoint."""
        try:
            resp = http_get_json(f"{self._url}/api/tags", timeout=5.0)
            models_raw = resp.get("models", [])
            result = []
            for m in models_raw:
                if isinstance(m, dict) and isinstance(m.get("name"), str):
                    result.append(m["name"])
            return sorted(result)
        except Exception:
            return []

    def is_available(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            http_get_json(f"{self._url}/api/tags", timeout=3.0)
            return True
        except Exception:
            return False
