#!/usr/bin/env python3
"""
Stillwater Universal LLM Client
Auth: 65537 | Status: STABLE | Version: 1.0.0

Standard library for ALL code to access LLMs with per-call logging/tracking.
Routes calls to any configured provider (Ollama, Claude CLI, Anthropic API, OpenAI, etc.)
Logs every call to ~/.stillwater/llm_calls.jsonl for analysis.

Usage:
    from stillwater.llm_client import llm_call, llm_chat, LLMClient

    # Simple (uses active provider from llm_config.yaml):
    response = llm_call("What is 2+2?")

    # With provider override:
    response = llm_call("Summarize this", provider="ollama", model="llama3.1:8b")

    # Chat format (OpenAI messages):
    response = llm_chat([{"role": "user", "content": "Hello"}], provider="claude")

    # Full client with connection test:
    client = LLMClient(provider="offline")
    ok, latency_ms, err = client.test_connection()

    # View call history:
    from stillwater.llm_client import get_call_history
    history = get_call_history(n=20)
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Add cli/src to path so llm_config_manager is importable
_CLI_SRC = Path(__file__).parent.parent
if str(_CLI_SRC) not in sys.path:
    sys.path.insert(0, str(_CLI_SRC))

try:
    from llm_config_manager import LLMConfigManager  # type: ignore
except ImportError:
    LLMConfigManager = None  # type: ignore

try:
    import httpx
    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False

try:
    import anthropic as _anthropic_module
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

# Default log file — user home, not repo (no gitignore needed)
_LOG_DIR = Path.home() / ".stillwater"
_LOG_FILE = _LOG_DIR / "llm_calls.jsonl"

_DEFAULT_TIMEOUT = 60.0  # seconds


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _log_call(
    provider: str,
    model: str,
    prompt_chars: int,
    response_chars: int,
    latency_ms: int,
    error: Optional[str] = None,
) -> None:
    """Append one JSON line to ~/.stillwater/llm_calls.jsonl."""
    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "provider": provider,
            "model": model,
            "prompt_chars": prompt_chars,
            "response_chars": response_chars,
            "latency_ms": latency_ms,
            "error": error,
        }
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
# HTTP helpers
# ---------------------------------------------------------------------------

def _http_post(url: str, payload: dict, timeout: float = _DEFAULT_TIMEOUT) -> dict:
    """POST JSON payload to url. Returns parsed response dict."""
    if _HAS_HTTPX:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=payload, headers={"Content-Type": "application/json"})
            resp.raise_for_status()
            return resp.json()
    else:
        # Fallback: urllib.request
        import urllib.request
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))


def _http_post_with_auth(url: str, payload: dict, api_key: str, timeout: float = _DEFAULT_TIMEOUT) -> dict:
    """POST with Bearer Authorization header."""
    if _HAS_HTTPX:
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()
    else:
        import urllib.request
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))


def _http_get(url: str, timeout: float = _DEFAULT_TIMEOUT) -> dict:
    """GET url. Returns parsed response dict."""
    if _HAS_HTTPX:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.json()
    else:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# LLMClient
# ---------------------------------------------------------------------------

class LLMClient:
    """
    Universal LLM client. Routes to any configured provider with per-call logging.

    Args:
        provider: Provider name from llm_config.yaml (e.g. "ollama", "claude-code",
                  "claude", "openai"). If None, uses active provider from config.
        config_path: Optional path to llm_config.yaml (auto-discovered if None).
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        config_path: Optional[Path] = None,
    ) -> None:
        self._config_manager: Optional[Any] = None
        self._provider_config: dict = {}
        self.provider_name: str = "offline"

        if LLMConfigManager is not None:
            try:
                kwargs = {}
                if config_path:
                    kwargs["config_path"] = config_path
                self._config_manager = LLMConfigManager(**kwargs)
                if provider:
                    self._config_manager.switch_provider(provider)
                self.provider_name = self._config_manager.active_provider
                self._provider_config = self._config_manager.get_active_provider_config()
            except Exception as exc:
                # Degrade gracefully to offline
                self.provider_name = provider or "offline"
                self._provider_config = {"type": "offline", "url": "", "name": "Offline"}
        else:
            # No config manager available — offline only
            self.provider_name = provider or "offline"
            self._provider_config = {"type": "offline", "url": "", "name": "Offline"}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def call(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Send a prompt to the configured LLM provider. Returns response text.

        Args:
            prompt: User prompt text.
            system: Optional system message.
            model: Override model name (uses config default if None).

        Returns:
            Response text string.

        Raises:
            RuntimeError: If the provider call fails.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages, model=model)

    def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
    ) -> str:
        """
        Send a chat messages list (OpenAI format) to the provider.

        Args:
            messages: List of {"role": ..., "content": ...} dicts.
            model: Override model name.

        Returns:
            Response text string.
        """
        provider_type = self._provider_config.get("type", "offline")
        url = self._provider_config.get("url", "")
        _model = model or self._provider_config.get("model", "")
        prompt_text = " ".join(m.get("content", "") for m in messages)

        start = time.monotonic()
        error: Optional[str] = None
        result = ""

        try:
            result = self._dispatch(provider_type, url, messages, _model, prompt_text)
        except Exception as exc:
            error = str(exc)
            raise RuntimeError(f"LLM call failed [{self.provider_name}]: {exc}") from exc
        finally:
            latency_ms = int((time.monotonic() - start) * 1000)
            _log_call(
                provider=self.provider_name,
                model=_model,
                prompt_chars=len(prompt_text),
                response_chars=len(result),
                latency_ms=latency_ms,
                error=error,
            )

        return result

    def test_connection(self) -> tuple[bool, int, Optional[str]]:
        """
        Test connectivity to the configured provider.

        Returns:
            Tuple of (ok: bool, latency_ms: int, error: str | None)
        """
        start = time.monotonic()
        try:
            result = self.call("ping", model=self._provider_config.get("model", ""))
            latency_ms = int((time.monotonic() - start) * 1000)
            return True, latency_ms, None
        except Exception as exc:
            latency_ms = int((time.monotonic() - start) * 1000)
            return False, latency_ms, str(exc)

    # ------------------------------------------------------------------
    # Private dispatch
    # ------------------------------------------------------------------

    def _dispatch(
        self,
        provider_type: str,
        url: str,
        messages: list[dict],
        model: str,
        prompt_text: str,
    ) -> str:
        """Route to the correct backend."""

        # --- Offline ---
        if provider_type == "offline" or self.provider_name == "offline":
            snippet = prompt_text[:50].replace("\n", " ")
            return f"[offline: {snippet}]"

        # --- HTTP: localhost claude_code_wrapper (/api/generate, Ollama-compat) ---
        if provider_type == "http" and ("localhost" in url or "127.0.0.1" in url):
            user_content = next(
                (m["content"] for m in reversed(messages) if m.get("role") == "user"), prompt_text
            )
            system_content = next(
                (m["content"] for m in messages if m.get("role") == "system"), None
            )
            payload: dict = {"prompt": user_content, "stream": False}
            if model:
                payload["model"] = model
            if system_content:
                payload["system"] = system_content
            resp = _http_post(f"{url}/api/generate", payload)
            return resp.get("response", "")

        # --- HTTP: remote Ollama (/api/chat) ---
        if provider_type == "http":
            payload = {
                "model": model or "llama3.1:8b",
                "messages": messages,
                "stream": False,
            }
            resp = _http_post(f"{url}/api/chat", payload)
            # Ollama returns: {"message": {"role": "assistant", "content": "..."}}
            return resp.get("message", {}).get("content", "")

        # --- API: Anthropic ---
        if provider_type == "api" and "anthropic.com" in url:
            if not _HAS_ANTHROPIC:
                raise RuntimeError("anthropic SDK not installed. Run: pip install anthropic")
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            if not api_key:
                raise RuntimeError("ANTHROPIC_API_KEY environment variable not set")
            client = _anthropic_module.Anthropic(api_key=api_key)
            # Separate system from messages
            system_msgs = [m["content"] for m in messages if m.get("role") == "system"]
            user_msgs = [m for m in messages if m.get("role") != "system"]
            kwargs: dict = {
                "model": model or "claude-haiku-4-5-20251001",
                "max_tokens": 4096,
                "messages": user_msgs,
            }
            if system_msgs:
                kwargs["system"] = " ".join(system_msgs)
            response = client.messages.create(**kwargs)
            return response.content[0].text if response.content else ""

        # --- API: OpenAI-compatible (OpenAI, OpenRouter, TogetherAI, Gemini, etc.) ---
        if provider_type == "api":
            # Find the API key from environment variables listed in config
            env_vars = self._provider_config.get("environment_variables", [])
            api_key = ""
            for var in env_vars:
                api_key = os.environ.get(var, "")
                if api_key:
                    break
            if not api_key:
                raise RuntimeError(
                    f"API key not found. Set one of: {env_vars}"
                )
            payload = {
                "model": model or self._provider_config.get("model", "gpt-4o-mini"),
                "messages": messages,
            }
            resp = _http_post_with_auth(f"{url}/chat/completions", payload, api_key)
            choices = resp.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""

        raise RuntimeError(f"Unknown provider type: {provider_type!r}")


# ---------------------------------------------------------------------------
# Top-level convenience functions
# ---------------------------------------------------------------------------

def llm_call(
    prompt: str,
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    system: Optional[str] = None,
) -> str:
    """
    One-liner LLM call using the active provider from llm_config.yaml.

    Args:
        prompt: User prompt.
        provider: Override provider (e.g. "ollama", "claude", "offline").
        model: Override model name.
        system: Optional system prompt.

    Returns:
        Response text string.

    Example:
        from stillwater.llm_client import llm_call
        answer = llm_call("What is the capital of France?")
        offline = llm_call("test", provider="offline")
    """
    client = LLMClient(provider=provider)
    return client.call(prompt, system=system, model=model)


def llm_chat(
    messages: list[dict],
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    """
    Chat with any LLM using OpenAI messages format.

    Args:
        messages: List of {"role": "user"|"assistant"|"system", "content": str}.
        provider: Override provider.
        model: Override model name.

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
    return client.chat(messages, model=model)
