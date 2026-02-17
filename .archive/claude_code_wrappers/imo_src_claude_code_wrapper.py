"""Claude Code local wrapper - uses local CLI or API.

Implements the same interface as ClaudeClient but calls the Claude Code CLI.
Falls back to Anthropic API if CLI is not available or in nested sessions.

Auth: 65537
"""
from __future__ import annotations

import subprocess
import json
import os
from dataclasses import dataclass
from typing import Iterator, List

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

@dataclass(frozen=True)
class ClaudeCodeWrapper:
    """Claude Code wrapper with CLI and API fallback.

    Tries to use `claude` command locally first.
    Falls back to Anthropic API if CLI unavailable or in nested session.
    """

    model: str = "claude-haiku-4-5-20251001"
    max_tokens: int = 4096
    use_api: bool = False  # Set to True to force API

    def list_models(self) -> List[str]:
        """Return list of available Claude models."""
        return [
            "claude-haiku-4-5-20251001",
            "claude-sonnet-4-5-20250929",
            "claude-opus-4-6-20250514",
        ]

    def stream_chat(self, *, model: str, prompt: str) -> Iterator[str]:
        """Stream chat response using CLI or API fallback.

        Args:
            model: Model name
            prompt: User prompt

        Yields:
            Text chunks from the response
        """
        # Try CLI first (unless forced to use API)
        if not self.use_api:
            yield from self._try_cli(model, prompt)
        else:
            yield from self._use_api(model, prompt)

    def _try_cli(self, model: str, prompt: str) -> Iterator[str]:
        """Try to use local Claude Code CLI."""
        try:
            # Use subprocess to call claude command
            result = subprocess.run(
                ["claude", "chat", "--message", prompt],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                # Success - yield response
                response = result.stdout
                chunk_size = 100
                for i in range(0, len(response), chunk_size):
                    yield response[i:i+chunk_size]
                return
            elif "cannot be launched inside another" in result.stderr:
                # In nested session - fall back to API
                yield from self._use_api(model, prompt)
                return
            else:
                # CLI error - try API
                yield from self._use_api(model, prompt)
                return

        except FileNotFoundError:
            # CLI not found - use API
            yield from self._use_api(model, prompt)
        except subprocess.TimeoutExpired:
            yield "Error: Claude Code command timed out. Using API fallback...\n"
            yield from self._use_api(model, prompt)
        except Exception as e:
            yield f"CLI error ({type(e).__name__}). Using API fallback...\n"
            yield from self._use_api(model, prompt)

    def _use_api(self, model: str, prompt: str) -> Iterator[str]:
        """Fall back to Anthropic API."""
        if not HAS_ANTHROPIC:
            yield "Error: Anthropic library not installed. Install with: pip install anthropic"
            return

        try:
            api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
            if not api_key:
                yield "Error: ANTHROPIC_API_KEY not set. Set it or install Claude Code CLI."
                return

            client = anthropic.Anthropic(api_key=api_key)
            with client.messages.stream(
                model=model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            yield f"API error: {type(e).__name__}: {e}"

    def generate_text(self, *, model: str, prompt: str) -> str:
        """Generate complete text response (non-streaming).

        Args:
            model: Model name
            prompt: User prompt

        Returns:
            Complete response text
        """
        chunks = list(self.stream_chat(model=model, prompt=prompt))
        return "".join(chunks)


@dataclass(frozen=True)
class LocalHaikuClient:
    """Lightweight Haiku client for notebooks.

    Provides simple interface for prompting Haiku locally.
    """

    def prompt(self, text: str) -> str:
        """Send prompt to Haiku and get response.

        Args:
            text: Prompt to send

        Returns:
            Complete response from Haiku
        """
        wrapper = ClaudeCodeWrapper()
        return wrapper.generate_text(model="claude-haiku-4-5-20251001", prompt=text)

    def stream(self, text: str) -> Iterator[str]:
        """Stream response from Haiku.

        Args:
            text: Prompt to send

        Yields:
            Response text chunks
        """
        wrapper = ClaudeCodeWrapper()
        yield from wrapper.stream_chat(model="claude-haiku-4-5-20251001", prompt=text)


# Convenience functions for notebooks
def haiku(prompt: str) -> str:
    """Send prompt to Haiku and return response."""
    client = LocalHaikuClient()
    return client.prompt(prompt)


def haiku_stream(prompt: str) -> Iterator[str]:
    """Stream response from Haiku."""
    client = LocalHaikuClient()
    yield from client.stream(prompt)
