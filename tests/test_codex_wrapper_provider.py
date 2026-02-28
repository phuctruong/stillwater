#!/usr/bin/env python3
"""
tests/test_codex_wrapper_provider.py — wiring tests for the Codex wrapper provider.
"""

from __future__ import annotations

import sys
from pathlib import Path


CLI_SRC = Path(__file__).resolve().parent.parent / "src" / "cli" / "src"
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))


def test_codex_wrapper_provider_name() -> None:
    from stillwater.providers.codex_wrapper_provider import CodexWrapperProvider

    provider = CodexWrapperProvider(url="http://localhost:8081")
    assert provider.name == "codex-wrapper"


def test_codex_wrapper_provider_default_url(monkeypatch) -> None:
    from stillwater.providers.codex_wrapper_provider import CodexWrapperProvider

    monkeypatch.delenv("CODEX_WRAPPER_URL", raising=False)
    provider = CodexWrapperProvider()
    assert provider.url == "http://localhost:8081"


def test_provider_registry_has_codex_wrapper() -> None:
    from stillwater.provider_registry import PROVIDERS

    assert "codex-wrapper" in PROVIDERS
    assert PROVIDERS["codex-wrapper"]["base_url"] == "http://localhost:8081"


def test_resolve_provider_for_codex_default_model() -> None:
    from stillwater.provider_registry import resolve_provider_for_model

    assert resolve_provider_for_model("codex-default") == "codex-wrapper"


def test_get_provider_returns_codex_wrapper_instance() -> None:
    from stillwater.providers import get_provider

    provider = get_provider("codex-wrapper", url="http://localhost:8081")
    assert provider.name == "codex-wrapper"
