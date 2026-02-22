#!/usr/bin/env python3
"""
Stillwater Universal LLM Client -- model-neutral, provider-agnostic.
Auth: 65537 | Status: STABLE | Version: 2.0.0

Zero external SDK dependencies. Uses only stdlib (urllib, http.client, json).
Thread-safe. All cost math uses int (hundredths of a cent) -- never float.

Usage:
    from stillwater.llm_client import LLMClient

    client = LLMClient()  # auto-discovers providers from env
    response = client.complete("What is 2+2?", model="auto")

    # Or specific provider:
    response = client.complete("Hello", provider="anthropic", model="claude-sonnet-4-20250514")

    # Chat format (OpenAI-compatible messages):
    response = client.chat([{"role": "user", "content": "Hello"}])

    # List what's available:
    client.available_providers()   # ["ollama", "anthropic", ...]
    client.available_models()      # {"anthropic": ["claude-sonnet-4-20250514", ...], ...}

    # Cost estimation (exact int arithmetic):
    cost = client.estimate_cost(1000, 500, "claude-sonnet-4-20250514")  # hundredths of cent

Backward compatibility:
    from stillwater.llm_client import llm_call, llm_chat, get_call_history
    answer = llm_call("What is 2+2?")
    answer = llm_chat([{"role": "user", "content": "Hello"}])
"""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from .providers.base import LLMResponse
from .providers.pricing import estimate_cost as _estimate_cost
from .providers._helpers import make_request_id, iso_now, estimate_tokens
from .providers import (
    get_provider,
    list_available_providers,
    get_cheapest_provider,
    LLMProvider,
)

# ---------------------------------------------------------------------------
# Call logging (backward compatible with v1.x)
# ---------------------------------------------------------------------------

_LOG_DIR = Path.home() / ".stillwater"
_LOG_FILE = _LOG_DIR / "llm_calls.jsonl"
_log_lock = threading.Lock()


def _log_call(
    provider: str,
    model: str,
    prompt_chars: int,
    response_chars: int,
    latency_ms: int,
    error: Optional[str] = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost_hundredths_cent: int = 0,
    request_id: str = "",
) -> None:
    """Append one JSON line to ~/.stillwater/llm_calls.jsonl. Thread-safe."""
    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "provider": provider,
            "model": model,
            "prompt_chars": prompt_chars,
            "response_chars": response_chars,
            "latency_ms": latency_ms,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_hundredths_cent": cost_hundredths_cent,
            "request_id": request_id,
            "error": error,
        }
        with _log_lock:
            with _LOG_FILE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # Never let logging crash the caller


def get_call_history(n: int = 100) -> list[dict]:
    """Return the last n LLM call log entries from ~/.stillwater/llm_calls.jsonl."""
    if not _LOG_FILE.exists():
        return []
    try:
        lines = _LOG_FILE.read_text(encoding="utf-8").splitlines()
        entries = []
        for line in lines:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return entries[-n:]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Callback dispatch helper
# ---------------------------------------------------------------------------


def _fire_callbacks(
    response: LLMResponse,
    tip_callback: Optional[Callable] = None,
    usage_tracker: Any = None,
) -> None:
    """
    Invoke optional post-call hooks after a successful LLM call.

    Both hooks receive a plain dict extracted from the LLMResponse so they
    have no dependency on the LLMResponse type.

    Args:
        response:      Completed LLMResponse.
        tip_callback:  Optional callable(dict) — post-call hook.
        usage_tracker: Optional SessionUsageTracker (or any object with a
                       usage_callback(dict) method).
    """
    if tip_callback is None and usage_tracker is None:
        return

    result_dict = response.to_dict()

    if tip_callback is not None:
        try:
            tip_callback(result_dict)
        except Exception:
            pass  # Never let tip callbacks crash the caller

    if usage_tracker is not None:
        callback = getattr(usage_tracker, "usage_callback", None)
        if callable(callback):
            try:
                callback(result_dict)
            except Exception:
                pass  # Never let tracker crashes affect callers


# ---------------------------------------------------------------------------
# LLMClient
# ---------------------------------------------------------------------------

class LLMClient:
    """
    Universal LLM client. Provider-agnostic, thread-safe, zero SDK dependencies.

    Auto-discovers available providers from environment variables:
        ANTHROPIC_API_KEY, OPENAI_API_KEY, TOGETHER_API_KEY,
        OPENROUTER_API_KEY, OLLAMA_URL

    Args:
        config: Optional dict with provider-specific config overrides.
        provider: Legacy v1.x compat -- pre-select a provider by name.
    """

    def __init__(
        self,
        config: Optional[dict] = None,
        provider: Optional[str] = None,
    ) -> None:
        self._config = config or {}
        self._providers: dict[str, LLMProvider] = {}
        self._lock = threading.Lock()
        self._default_provider: Optional[str] = provider
        self._default_timeout: float = 30.0

        # v1.x backward compatibility: expose provider_name attribute
        self.provider_name: str = provider or "auto"

    def _is_offline(self, provider: Optional[str] = None) -> bool:
        """Check if we should use offline mode."""
        if provider == "offline":
            return True
        if self._default_provider == "offline" or self.provider_name == "offline":
            return True
        return False

    def _offline_response(self, content: str, latency_ms: int = 0) -> LLMResponse:
        """Generate an offline echo response."""
        snippet = content[:50].replace("\n", " ")
        text = f"[offline: {snippet}]"
        return LLMResponse(
            text=text,
            model="offline",
            provider="offline",
            input_tokens=estimate_tokens(content),
            output_tokens=estimate_tokens(text),
            cost_hundredths_cent=0,
            latency_ms=latency_ms,
            request_id=make_request_id(content),
            timestamp=iso_now(),
        )

    def _get_or_create_provider(self, name: str) -> LLMProvider:
        """Get cached provider instance or create one. Thread-safe."""
        with self._lock:
            if name not in self._providers:
                kwargs = {}
                provider_config = self._config.get(name, {})
                if isinstance(provider_config, dict):
                    if "api_key" in provider_config:
                        kwargs["api_key"] = provider_config["api_key"]
                    if "url" in provider_config:
                        kwargs["url"] = provider_config["url"]
                self._providers[name] = get_provider(name, **kwargs)
            return self._providers[name]

    def _resolve_provider(self, provider: Optional[str]) -> str:
        """
        Resolve which provider to use.

        Priority:
        1. Explicit provider argument
        2. Default provider from constructor
        3. Cheapest available (auto)
        4. Raise RuntimeError if none available
        """
        if provider and provider != "auto":
            return provider

        if self._default_provider and self._default_provider != "auto":
            return self._default_provider

        cheapest = get_cheapest_provider()
        if cheapest:
            return cheapest

        raise RuntimeError(
            "No LLM providers available. Set one of: "
            "ANTHROPIC_API_KEY, OPENAI_API_KEY, TOGETHER_API_KEY, "
            "OPENROUTER_API_KEY, or start Ollama."
        )

    def complete(
        self,
        prompt: str,
        model: str = "auto",
        provider: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: Optional[float] = None,
        tip_callback: Optional[Callable] = None,
        usage_tracker: Any = None,
    ) -> LLMResponse:
        """
        Send a single prompt to an LLM provider.

        Args:
            prompt: The user prompt.
            model: Model name, or "auto" to use provider default.
            provider: Provider name, or None for auto-select.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.
            timeout: Request timeout in seconds (default: 30).
            tip_callback: Optional callable(dict) — post-call hook. Called
                         after each successful response with the result dict.
            usage_tracker: Optional SessionUsageTracker — usage hook. Called
                          after each successful response via usage_callback(dict).

        Returns:
            LLMResponse with text, tokens, cost, latency, etc.
        """
        # Handle offline mode
        if self._is_offline(provider):
            start = time.monotonic()
            response = self._offline_response(prompt, int((time.monotonic() - start) * 1000))
            _log_call(
                provider="offline", model="offline",
                prompt_chars=len(prompt), response_chars=len(response.text),
                latency_ms=response.latency_ms,
            )
            _fire_callbacks(response, tip_callback=tip_callback, usage_tracker=usage_tracker)
            return response

        resolved_provider = self._resolve_provider(provider)
        p = self._get_or_create_provider(resolved_provider)
        resolved_model = "" if model == "auto" else model
        _timeout = timeout if timeout is not None else self._default_timeout

        start = time.monotonic()
        error: Optional[str] = None
        response: Optional[LLMResponse] = None

        try:
            response = p.complete(
                prompt, model=resolved_model, max_tokens=max_tokens,
                temperature=temperature, timeout=_timeout,
            )
        except Exception as exc:
            error = str(exc)
            latency_ms = int((time.monotonic() - start) * 1000)
            _log_call(
                provider=resolved_provider, model=resolved_model,
                prompt_chars=len(prompt), response_chars=0,
                latency_ms=latency_ms, error=error,
            )
            raise

        _log_call(
            provider=response.provider, model=response.model,
            prompt_chars=len(prompt), response_chars=len(response.text),
            latency_ms=response.latency_ms,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_hundredths_cent=response.cost_hundredths_cent,
            request_id=response.request_id,
        )
        _fire_callbacks(response, tip_callback=tip_callback, usage_tracker=usage_tracker)
        return response

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str = "auto",
        provider: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: Optional[float] = None,
        tip_callback: Optional[Callable] = None,
        usage_tracker: Any = None,
    ) -> LLMResponse:
        """
        Send chat messages (OpenAI format) to an LLM provider.

        Args:
            messages: List of {"role": str, "content": str} dicts.
            model: Model name, or "auto" to use provider default.
            provider: Provider name, or None for auto-select.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.
            timeout: Request timeout in seconds (default: 30).
            tip_callback: Optional callable(dict) — post-call hook. Called
                         after each successful response with the result dict.
            usage_tracker: Optional SessionUsageTracker — usage hook. Called
                          after each successful response via usage_callback(dict).

        Returns:
            LLMResponse with text, tokens, cost, latency, etc.
        """
        prompt_text = " ".join(m.get("content", "") for m in messages)

        # Handle offline mode
        if self._is_offline(provider):
            start = time.monotonic()
            response = self._offline_response(prompt_text, int((time.monotonic() - start) * 1000))
            _log_call(
                provider="offline", model="offline",
                prompt_chars=len(prompt_text), response_chars=len(response.text),
                latency_ms=response.latency_ms,
            )
            _fire_callbacks(response, tip_callback=tip_callback, usage_tracker=usage_tracker)
            return response

        resolved_provider = self._resolve_provider(provider)
        p = self._get_or_create_provider(resolved_provider)
        resolved_model = "" if model == "auto" else model
        _timeout = timeout if timeout is not None else self._default_timeout

        start = time.monotonic()
        error: Optional[str] = None
        response: Optional[LLMResponse] = None

        try:
            response = p.chat(
                messages, model=resolved_model, max_tokens=max_tokens,
                temperature=temperature, timeout=_timeout,
            )
        except Exception as exc:
            error = str(exc)
            latency_ms = int((time.monotonic() - start) * 1000)
            _log_call(
                provider=resolved_provider, model=resolved_model,
                prompt_chars=len(prompt_text), response_chars=0,
                latency_ms=latency_ms, error=error,
            )
            raise

        _log_call(
            provider=response.provider, model=response.model,
            prompt_chars=len(prompt_text), response_chars=len(response.text),
            latency_ms=response.latency_ms,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_hundredths_cent=response.cost_hundredths_cent,
            request_id=response.request_id,
        )
        _fire_callbacks(response, tip_callback=tip_callback, usage_tracker=usage_tracker)
        return response

    def available_providers(self) -> list[str]:
        """List providers that have valid API keys / endpoints configured."""
        return list_available_providers()

    def available_models(self) -> dict[str, list[str]]:
        """Return {provider_name: [model_names]} for all available providers."""
        result: dict[str, list[str]] = {}
        for name in self.available_providers():
            try:
                p = self._get_or_create_provider(name)
                result[name] = p.models()
            except Exception:
                result[name] = []
        return result

    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> int:
        """
        Estimate cost in hundredths of a cent (exact int arithmetic).

        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
            model: Model name.

        Returns:
            Cost in hundredths of a cent (int).
        """
        return _estimate_cost(input_tokens, output_tokens, model)

    # ------------------------------------------------------------------
    # v1.x backward compatibility methods
    # ------------------------------------------------------------------

    def call(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        v1.x compatible: send prompt, return text string.

        If provider is "offline", returns a bracketed echo (no network).
        """
        if self._default_provider == "offline" or self.provider_name == "offline":
            snippet = prompt[:50].replace("\n", " ")
            return f"[offline: {snippet}]"

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.chat(messages, model=model or "auto")
            return response.text
        except Exception as exc:
            raise RuntimeError(
                f"LLM call failed [{self.provider_name}]: {exc}"
            ) from exc

    def test_connection(self) -> tuple[bool, int, Optional[str]]:
        """
        v1.x compatible: test connectivity.

        Returns:
            Tuple of (ok: bool, latency_ms: int, error: str | None)
        """
        start = time.monotonic()
        try:
            self.call("ping")
            latency_ms = int((time.monotonic() - start) * 1000)
            return True, latency_ms, None
        except Exception as exc:
            latency_ms = int((time.monotonic() - start) * 1000)
            return False, latency_ms, str(exc)


# ---------------------------------------------------------------------------
# Top-level convenience functions (v1.x backward compatibility)
# ---------------------------------------------------------------------------

def llm_call(
    prompt: str,
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    system: Optional[str] = None,
    tip_callback: Optional[Callable] = None,
    usage_tracker: Any = None,
) -> str:
    """
    One-liner LLM call. Returns response text string.

    Args:
        prompt: User prompt.
        provider: Override provider (e.g. "anthropic", "openai", "offline").
        model: Override model name.
        system: Optional system prompt.
        tip_callback: Optional callable(dict) — post-call hook. Called after
                     each successful response with the result dict.
        usage_tracker: Optional SessionUsageTracker instance. Called after each
                      successful response via usage_callback(dict).

    Returns:
        Response text string.

    Example:
        from stillwater.llm_client import llm_call
        answer = llm_call("What is the capital of France?")
        offline = llm_call("test", provider="offline")
    """
    client = LLMClient(provider=provider)

    # For offline mode, use v1.x path (no HTTP) — still fire callbacks via chat()
    if provider == "offline":
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            response = client.chat(
                messages, model=model or "auto",
                tip_callback=tip_callback, usage_tracker=usage_tracker,
            )
            return response.text
        except Exception:
            # Fallback to v1.x call() for pure offline echo
            return client.call(prompt, system=system, model=model)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat(
            messages, model=model or "auto",
            tip_callback=tip_callback, usage_tracker=usage_tracker,
        )
        return response.text
    except Exception as exc:
        raise RuntimeError(f"LLM call failed: {exc}") from exc


def llm_chat(
    messages: list[dict],
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    tip_callback: Optional[Callable] = None,
    usage_tracker: Any = None,
) -> str:
    """
    Chat with any LLM using OpenAI messages format. Returns response text.

    Args:
        messages: List of {"role": "user"|"assistant"|"system", "content": str}.
        provider: Override provider.
        model: Override model name.
        tip_callback: Optional callable(dict) — post-call hook. Called after
                     each successful response with the result dict.
        usage_tracker: Optional SessionUsageTracker instance. Called after each
                      successful response via usage_callback(dict).

    Returns:
        Response text string.

    Example:
        from stillwater.llm_client import llm_chat
        response = llm_chat([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ])
    """
    client = LLMClient(provider=provider)

    if provider == "offline" or not provider:
        # For offline mode, use v1.x compatible .call()
        if provider == "offline":
            prompt_text = " ".join(m.get("content", "") for m in messages)
            # Fire callbacks via chat() which handles offline internally
            try:
                response = client.chat(
                    messages, model=model or "auto",
                    tip_callback=tip_callback, usage_tracker=usage_tracker,
                )
                return response.text
            except Exception:
                return client.call(prompt_text, model=model)

    try:
        response = client.chat(
            messages, model=model or "auto",
            tip_callback=tip_callback, usage_tracker=usage_tracker,
        )
        return response.text
    except Exception as exc:
        raise RuntimeError(f"LLM chat failed: {exc}") from exc
