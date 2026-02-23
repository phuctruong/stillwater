#!/usr/bin/env python3
"""
HTTP Provider - Generic HTTP/Ollama-compatible endpoint support.
Auth: 65537 | Version: 1.0.0

Supports any HTTP endpoint that implements the Ollama-compatible API:
  POST /api/generate with {"prompt": "...", "stream": false}

Examples:
  - Claude Code wrapper on localhost:8080
  - Ollama on localhost:11434
  - Any OpenAI-compatible API endpoint
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
import time
from typing import Optional
from .base import LLMProvider, LLMResponse
from ._helpers import make_request_id, iso_now, estimate_tokens


class HTTPProvider(LLMProvider):
    """Generic HTTP/Ollama-compatible endpoint provider."""

    def __init__(self, url: str = "http://localhost:8080", **kwargs):
        """Initialize HTTP provider with endpoint URL."""
        self.url = url.rstrip("/")
        self.base_url = f"{self.url}/api/generate"
        self._test_available = None

    @property
    def name(self) -> str:
        return "http"

    def complete(
        self,
        prompt: str,
        model: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float = 30.0,
    ) -> LLMResponse:
        """Send prompt to HTTP endpoint and return response."""
        start = time.monotonic()

        try:
            payload = {
                "prompt": prompt,
                "stream": False,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            request = urllib.request.Request(
                self.base_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                text = data.get("response", "")

            latency_ms = int((time.monotonic() - start) * 1000)

            return LLMResponse(
                text=text,
                model=model or "http",
                provider=self.name,
                input_tokens=estimate_tokens(prompt),
                output_tokens=estimate_tokens(text),
                cost_hundredths_cent=0,
                latency_ms=latency_ms,
                request_id=make_request_id(prompt),
                timestamp=iso_now(),
            )

        except Exception as e:
            raise RuntimeError(f"HTTP request failed: {e}")

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float = 30.0,
    ) -> LLMResponse:
        """Convert messages to prompt and send to HTTP endpoint. Extracts system prompt if present."""
        system_prompt = None
        user_parts = []

        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")

            # Extract system message separately
            if role == "system":
                system_prompt = content
            else:
                user_parts.append(f"{role}: {content}")

        prompt = "\n".join(user_parts)
        return self.complete_with_system(prompt, system=system_prompt, model=model, max_tokens=max_tokens, temperature=temperature, timeout=timeout)

    def complete_with_system(
        self,
        prompt: str,
        system: str = "",
        model: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float = 30.0,
    ) -> LLMResponse:
        """Send prompt with optional system message to HTTP endpoint."""
        start = time.monotonic()

        try:
            payload = {
                "prompt": prompt,
                "stream": False,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            # Add system prompt if provided
            if system:
                payload["system"] = system

            request = urllib.request.Request(
                self.base_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                text = data.get("response", "")

            latency_ms = int((time.monotonic() - start) * 1000)

            return LLMResponse(
                text=text,
                model=model or "http",
                provider=self.name,
                input_tokens=estimate_tokens(prompt),
                output_tokens=estimate_tokens(text),
                cost_hundredths_cent=0,
                latency_ms=latency_ms,
                request_id=make_request_id(prompt),
                timestamp=iso_now(),
            )

        except Exception as e:
            raise RuntimeError(f"HTTP request failed: {e}")

    def models(self) -> list[str]:
        """Return list of available models from HTTP endpoint."""
        try:
            request = urllib.request.Request(f"{self.url}/api/tags")
            with urllib.request.urlopen(request, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                return [m["name"] for m in data.get("models", []) if "name" in m]
        except Exception:
            return ["http"]

    def is_available(self) -> bool:
        """Check if HTTP endpoint is reachable."""
        if self._test_available is not None:
            return self._test_available

        try:
            request = urllib.request.Request(f"{self.url}/")
            with urllib.request.urlopen(request, timeout=2) as response:
                self._test_available = response.status in (200, 404, 405)
                return self._test_available
        except Exception:
            self._test_available = False
            return False
