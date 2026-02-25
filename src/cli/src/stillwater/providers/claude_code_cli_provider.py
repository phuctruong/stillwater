"""
Stillwater Claude Code CLI Provider (local, no API key)
Version: 1.0.0

Shells out to the local 'claude-code' CLI tool instead of calling Anthropic API.
Supports: haiku, sonnet, opus (model switching via --model flag)
No API key needed — just call the CLI directly.

Usage:
  claude-code "What is 2+2?" --model haiku
  claude-code "What is 2+2?" --model sonnet
  claude-code "What is 2+2?" --model opus
"""

from __future__ import annotations

import subprocess
import time
from typing import Optional
from shutil import which

from .base import LLMProvider, LLMResponse
from ._helpers import build_response, messages_to_prompt, estimate_tokens

_DEFAULT_MODEL = "haiku"
_SUPPORTED_MODELS = ["haiku", "sonnet", "opus"]


class ClaudeCodeCLIProvider(LLMProvider):
    """Claude Code CLI provider -- free, no API key, local subprocess calls."""

    def __init__(self, model: Optional[str] = None) -> None:
        """Initialize with optional model override."""
        self._model = model or _DEFAULT_MODEL
        self._cli_path = which("claude-code")

    @property
    def name(self) -> str:
        return "claude-code-cli"

    def _run_cli(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float = 30.0,
    ) -> str:
        """
        Shell out to claude-code CLI.

        Format: claude-code "PROMPT" --model MODEL --max-tokens N --temperature T
        """
        if not self._cli_path:
            raise RuntimeError(
                "claude-code CLI not found in PATH. "
                "Install with: pip install -e src/cli/"
            )

        resolved_model = model or self._model

        # Build command: claude-code "prompt" --model haiku --max-tokens 1024 --temperature 0.7
        cmd = [
            self._cli_path,
            prompt,
            "--model",
            resolved_model,
            "--max-tokens",
            str(max_tokens),
            "--temperature",
            str(temperature),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,  # Don't raise on non-zero exit
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip()
                raise RuntimeError(
                    f"claude-code CLI exited with code {result.returncode}: {error_msg}"
                )

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"claude-code CLI timed out after {timeout}s")
        except Exception as e:
            raise RuntimeError(f"Failed to run claude-code CLI: {e}")

    def complete(
        self,
        prompt: str,
        model: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float = 30.0,
    ) -> LLMResponse:
        """
        Send a single prompt via CLI and return structured response.
        """
        resolved_model = model or self._model
        request_content = f"user: {prompt}"
        start = time.monotonic()

        text = self._run_cli(
            prompt,
            resolved_model,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
        )

        latency_ms = int((time.monotonic() - start) * 1000)

        # Token estimation (Claude uses ~1 token per word on average)
        input_tokens = estimate_tokens(prompt)
        output_tokens = estimate_tokens(text)

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
        """
        Send a chat messages list via CLI and return structured response.
        """
        resolved_model = model or self._model
        request_content = messages_to_prompt(messages)

        # Convert messages to prompt format
        prompt_parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            prompt_parts.append(f"{role}: {content}")
        prompt = "\n".join(prompt_parts)

        start = time.monotonic()

        text = self._run_cli(
            prompt,
            resolved_model,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
        )

        latency_ms = int((time.monotonic() - start) * 1000)

        input_tokens = estimate_tokens(request_content)
        output_tokens = estimate_tokens(text)

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
        """Return list of supported Claude models."""
        return _SUPPORTED_MODELS

    def is_available(self) -> bool:
        """Check if claude-code CLI is installed and executable."""
        if not self._cli_path:
            return False
        try:
            result = subprocess.run(
                [self._cli_path, "--version"],
                capture_output=True,
                timeout=2.0,
            )
            return result.returncode == 0
        except Exception:
            return False
