from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_DIR = REPO_ROOT / "admin"
for _path in (str(REPO_ROOT), str(ADMIN_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from services.llm_wrapper import LLMWrapper


def _wrapper() -> LLMWrapper:
    return LLMWrapper(REPO_ROOT)


def test_malformed_openai_raises(monkeypatch) -> None:
    wrapper = _wrapper()
    monkeypatch.setattr(wrapper.key_manager, "get_provider_key", lambda _: ("k", "env"))
    monkeypatch.setattr(wrapper, "_post_json", lambda *args, **kwargs: {"choices": []})
    with pytest.raises(RuntimeError, match="malformed response from openai"):
        wrapper._call_openai("hi")


def test_malformed_together_raises(monkeypatch) -> None:
    wrapper = _wrapper()
    monkeypatch.setattr(wrapper.key_manager, "get_provider_key", lambda _: ("k", "env"))
    monkeypatch.setattr(wrapper, "_post_json", lambda *args, **kwargs: {"choices": []})
    with pytest.raises(RuntimeError, match="malformed response from together"):
        wrapper._call_together("hi")


def test_malformed_openrouter_raises(monkeypatch) -> None:
    wrapper = _wrapper()
    monkeypatch.setattr(wrapper.key_manager, "get_provider_key", lambda _: ("k", "env"))
    monkeypatch.setattr(wrapper, "_post_json", lambda *args, **kwargs: {"choices": []})
    with pytest.raises(RuntimeError, match="malformed response from openrouter"):
        wrapper._call_openrouter("hi")


def test_no_provider_fallback(monkeypatch) -> None:
    wrapper = _wrapper()
    called = {"claude": False}
    monkeypatch.setattr(
        wrapper,
        "_config",
        lambda: {"default_provider": "openai", "providers": {"openai": {"default_model": "gpt-4o"}}},
    )
    monkeypatch.setattr(wrapper, "_call_openai", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(
        wrapper,
        "_call_claude_code",
        lambda *args, **kwargs: called.__setitem__("claude", True) or "ok",
    )

    result = wrapper.complete(prompt="hello")
    assert result["ok"] is False
    assert result["provider"] == "openai"
    assert called["claude"] is False


def test_keyboardinterrupt_propagates(monkeypatch) -> None:
    wrapper = _wrapper()
    monkeypatch.setattr(
        wrapper,
        "_config",
        lambda: {"default_provider": "openai", "providers": {"openai": {"default_model": "gpt-4o"}}},
    )
    monkeypatch.setattr(
        wrapper,
        "_call_openai",
        lambda *args, **kwargs: (_ for _ in ()).throw(KeyboardInterrupt()),
    )

    with pytest.raises(KeyboardInterrupt):
        wrapper.complete(prompt="hello")


def test_gemini_cli_real() -> None:
    if os.getenv("RUN_GEMINI_REAL_TEST", "").strip() != "1":
        pytest.skip("set RUN_GEMINI_REAL_TEST=1 to run real Gemini CLI integration")
    wrapper = _wrapper()
    if not wrapper._which_gemini():
        pytest.skip("gemini CLI not installed")
    try:
        out = wrapper._call_gemini_cli("Reply exactly: GEMINI_OK", model="gemini-3-flash-preview")
    except RuntimeError as exc:
        pytest.skip(f"gemini CLI not usable in this environment: {exc}")
    assert isinstance(out, str)
    assert out.strip()


def test_gemini_api_key_missing_raises(monkeypatch) -> None:
    wrapper = _wrapper()
    monkeypatch.setattr(wrapper.key_manager, "get_provider_key", lambda _: ("", "none"))
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY not configured"):
        wrapper._call_gemini_api("hi")


def test_gemini_api_malformed_raises(monkeypatch) -> None:
    wrapper = _wrapper()
    monkeypatch.setattr(wrapper.key_manager, "get_provider_key", lambda _: ("k", "env"))
    monkeypatch.setattr(wrapper, "_post_json", lambda *args, **kwargs: {})
    with pytest.raises(RuntimeError, match="malformed Gemini response: no candidates"):
        wrapper._call_gemini_api("hi")


def test_gemini_provider_listed(monkeypatch) -> None:
    wrapper = _wrapper()
    monkeypatch.setattr(wrapper, "_which_claude", lambda: "/usr/bin/claude")
    monkeypatch.setattr(wrapper, "_which_gemini", lambda: "/usr/bin/gemini")
    monkeypatch.setattr(
        wrapper,
        "_config",
        lambda: {
            "default_provider": "gemini-cli",
            "providers": {
                "claude-code": {"default_model": "sonnet"},
                "gemini-cli": {"default_model": "gemini-2.5-flash"},
                "gemini-api": {"default_model": "gemini-2.5-flash"},
            },
        },
    )
    monkeypatch.setattr(
        wrapper.key_manager,
        "get_provider_key",
        lambda provider: ("g-key", "env") if provider == "gemini-api" else ("", "none"),
    )
    rows = {item["provider"]: item for item in wrapper.list_providers()}
    assert "gemini-cli" in rows
    assert rows["gemini-cli"]["available"] is True
    assert rows["gemini-cli"]["cli_path"] == "/usr/bin/gemini"
    assert "gemini-api" in rows
    assert rows["gemini-api"]["has_key"] is True
