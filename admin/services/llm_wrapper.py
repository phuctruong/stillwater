"""LLM wrapper with strict provider selection and key-manager integration."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .key_manager import KeyManager


class LLMWrapper:
    """Default LLM backend with strict provider selection."""

    def __init__(self, repo_root: Path, config_path: Path | None = None) -> None:
        self.repo_root = Path(repo_root)
        self.key_manager = KeyManager(repo_root=self.repo_root, config_path=config_path)

    def _config(self) -> dict[str, Any]:
        return self.key_manager.load_config()

    @staticmethod
    def _which_claude() -> str:
        return shutil.which("claude") or shutil.which("claude-code") or ""

    @staticmethod
    def _which_gemini() -> str:
        return shutil.which("gemini") or ""

    def _call_claude_code(self, prompt: str, model: str = "sonnet") -> str:
        cmd_path = self._which_claude()
        if not cmd_path:
            raise RuntimeError("claude-code CLI not found")
        cmd = [cmd_path, "--print", prompt]
        # Model flags vary by install; keep default CLI model unless env/model wiring is configured.
        proc = subprocess.run(
            cmd,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
            env=dict(os.environ),
        )
        if proc.returncode != 0:
            raise RuntimeError(f"claude-code failed: {proc.stderr.strip() or proc.stdout.strip()}")
        return (proc.stdout or "").strip()

    def _call_gemini_cli(self, prompt: str, model: str | None = None) -> str:
        cmd_path = self._which_gemini()
        if not cmd_path:
            raise RuntimeError("gemini CLI not found")
        if model:
            cmd = [cmd_path, "-m", model, "-p", prompt, "--output-format", "json"]
        else:
            cmd = [cmd_path, "-p", prompt, "--output-format", "json"]
        cmdline = " ".join(shlex.quote(part) for part in cmd)
        try:
            proc = subprocess.run(
                ["/bin/bash", "-lc", cmdline],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
                env=dict(os.environ),
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("gemini CLI timed out") from exc
        if proc.returncode != 0:
            message = proc.stderr.strip() or proc.stdout.strip()
            raise RuntimeError(f"gemini CLI failed (exit {proc.returncode}): {message}")
        raw = (proc.stdout or "").strip()
        lines = raw.splitlines()
        if lines and "Loaded cached credentials" in lines[0]:
            raw = "\n".join(lines[1:]).strip()
        text = raw
        if raw:
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = None
            if isinstance(payload, dict):
                response = payload.get("response")
                if isinstance(response, str) and response.strip():
                    text = response.strip()
        if not text:
            raise RuntimeError("gemini CLI returned empty response")
        return text

    def _post_json(self, url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url=url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        for k, v in headers.items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"provider HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"provider request failed: {exc}") from exc

    def _call_anthropic(self, prompt: str, model: str = "claude-sonnet-4-6") -> str:
        key, _ = self.key_manager.get_provider_key("anthropic")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not configured")
        payload = {
            "model": model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
        out = self._post_json(
            "https://api.anthropic.com/v1/messages",
            payload,
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
            },
        )
        content = out.get("content", [])
        if content and isinstance(content, list):
            first = content[0]
            if isinstance(first, dict):
                text = first.get("text")
                if isinstance(text, str) and text.strip():
                    return text.strip()
        raise RuntimeError("malformed response from anthropic: missing content field")

    @staticmethod
    def _parse_chat_completion(provider: str, data: dict[str, Any]) -> str:
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError(f"malformed response from {provider}: missing choices field")
        first = choices[0]
        if not isinstance(first, dict):
            raise RuntimeError(f"malformed response from {provider}: invalid first choice")
        message = first.get("message")
        if not isinstance(message, dict):
            raise RuntimeError(f"malformed response from {provider}: missing message field")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(f"malformed response from {provider}: missing content field")
        return content.strip()

    def _call_openai(self, prompt: str, model: str = "gpt-4o") -> str:
        key, _ = self.key_manager.get_provider_key("openai")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not configured")
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        out = self._post_json(
            "https://api.openai.com/v1/chat/completions",
            payload,
            headers={"Authorization": f"Bearer {key}"},
        )
        return self._parse_chat_completion("openai", out)

    def _call_together(self, prompt: str, model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo") -> str:
        key, _ = self.key_manager.get_provider_key("together")
        if not key:
            raise RuntimeError("TOGETHER_API_KEY not configured")
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        out = self._post_json(
            "https://api.together.xyz/v1/chat/completions",
            payload,
            headers={"Authorization": f"Bearer {key}"},
        )
        return self._parse_chat_completion("together", out)

    def _call_openrouter(self, prompt: str, model: str = "anthropic/claude-sonnet-4-6") -> str:
        key, _ = self.key_manager.get_provider_key("openrouter")
        if not key:
            raise RuntimeError("OPENROUTER_API_KEY not configured")
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        out = self._post_json(
            "https://openrouter.ai/api/v1/chat/completions",
            payload,
            headers={"Authorization": f"Bearer {key}"},
        )
        return self._parse_chat_completion("openrouter", out)

    def _call_gemini_api(self, prompt: str, model: str = "gemini-2.5-flash") -> str:
        key, _ = self.key_manager.get_provider_key("gemini-api")
        if not key:
            raise RuntimeError("GEMINI_API_KEY not configured")
        out = self._post_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
            {"contents": [{"parts": [{"text": prompt}]}]},
            headers={},
        )
        candidates = out.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise RuntimeError(f"malformed Gemini response: no candidates. Got: {list(out.keys())}")
        first = candidates[0]
        if not isinstance(first, dict):
            raise RuntimeError("malformed Gemini response: no content.parts in first candidate")
        content = first.get("content")
        if not isinstance(content, dict):
            raise RuntimeError("malformed Gemini response: no content.parts in first candidate")
        parts = content.get("parts")
        if not isinstance(parts, list) or not parts:
            raise RuntimeError("malformed Gemini response: no content.parts in first candidate")
        first_part = parts[0]
        if not isinstance(first_part, dict):
            raise RuntimeError("malformed Gemini response: empty text in first part")
        text = first_part.get("text")
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("malformed Gemini response: empty text in first part")
        return text.strip()

    def list_providers(self) -> list[dict[str, Any]]:
        cfg = self._config()
        providers = []
        claude_path = self._which_claude()
        providers.append(
            {
                "provider": "claude-code",
                "available": bool(claude_path),
                "source": "local-cli",
                "cli_path": claude_path,
                "default_model": cfg.get("providers", {}).get("claude-code", {}).get("default_model", "sonnet"),
            },
        )
        gemini_path = self._which_gemini()
        providers.append(
            {
                "provider": "gemini-cli",
                "available": bool(gemini_path),
                "source": "local-cli",
                "cli_path": gemini_path,
                "default_model": cfg.get("providers", {}).get("gemini-cli", {}).get(
                    "default_model",
                    "gemini-2.5-flash",
                ),
            },
        )

        for name in ("anthropic", "openai", "gemini-api", "together", "openrouter"):
            key, source = self.key_manager.get_provider_key(name)
            providers.append(
                {
                    "provider": name,
                    "available": bool(key),
                    "source": source,
                    "has_key": bool(key),
                    "key_masked": self.key_manager.mask_key(key),
                    "default_model": cfg.get("providers", {}).get(name, {}).get("default_model", ""),
                },
            )
        return providers

    def list_models(self) -> dict[str, list[str]]:
        return {
            "claude-code": ["haiku", "sonnet", "opus"],
            "gemini-cli": [
                "gemini-3-flash-preview",
                "gemini-3-pro-preview",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-2.5-pro",
            ],
            "gemini-api": [
                "gemini-3-flash-preview",
                "gemini-3-pro-preview",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-2.5-pro",
            ],
            "anthropic": ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-6"],
            "openai": ["gpt-4o-mini", "gpt-4o", "o3"],
            "together": ["meta-llama/Llama-3.3-70B-Instruct-Turbo"],
            "openrouter": ["anthropic/claude-sonnet-4-6", "openai/gpt-4o"],
        }

    def complete(
        self,
        prompt: str,
        model: str = "sonnet",
        provider: str | None = None,
        strict_provider: bool = False,
    ) -> dict[str, Any]:
        cfg = self._config()
        requested = provider or cfg.get("default_provider", "claude-code")
        selected_model = model
        del strict_provider  # retained for API compatibility; no implicit fallback is allowed.
        try:
            if requested == "claude-code":
                text = self._call_claude_code(prompt, model=model)
            elif requested == "gemini-cli":
                selected_model = cfg.get("providers", {}).get("gemini-cli", {}).get("default_model", "gemini-2.5-flash")
                if model and model != "sonnet":
                    selected_model = model
                text = self._call_gemini_cli(prompt, model=selected_model)
            elif requested == "gemini-api":
                selected_model = cfg.get("providers", {}).get("gemini-api", {}).get("default_model", "gemini-2.5-flash")
                if model and model != "sonnet":
                    selected_model = model
                text = self._call_gemini_api(prompt, model=selected_model)
            elif requested == "anthropic":
                default_model = cfg.get("providers", {}).get("anthropic", {}).get("default_model", "claude-sonnet-4-6")
                text = self._call_anthropic(prompt, model=default_model)
            elif requested == "openai":
                default_model = cfg.get("providers", {}).get("openai", {}).get("default_model", "gpt-4o")
                text = self._call_openai(prompt, model=default_model)
            elif requested == "together":
                default_model = cfg.get("providers", {}).get("together", {}).get(
                    "default_model",
                    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
                )
                text = self._call_together(prompt, model=default_model)
            elif requested == "openrouter":
                default_model = cfg.get("providers", {}).get("openrouter", {}).get(
                    "default_model",
                    "anthropic/claude-sonnet-4-6",
                )
                text = self._call_openrouter(prompt, model=default_model)
            else:
                return {"ok": False, "provider": requested, "error": f"unsupported provider: {requested}"}
            return {"ok": True, "provider": requested, "model": selected_model, "completion": text}
        except (RuntimeError, OSError, urllib.error.URLError, TimeoutError) as exc:
            return {"ok": False, "provider": requested, "error": str(exc)}
