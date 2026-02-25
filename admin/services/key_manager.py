"""Key manager for LLM provider secrets and swarm model overrides."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = {
    "default_provider": "claude-code",
    "providers": {
        "claude-code": {"enabled": True, "command": "claude", "default_model": "sonnet"},
        "gemini-cli": {"enabled": True, "command": "gemini", "default_model": "gemini-2.5-flash"},
        "gemini-api": {"enabled": False, "api_key": "", "default_model": "gemini-2.5-flash"},
        "anthropic": {"enabled": False, "api_key": "", "default_model": "claude-sonnet-4-6"},
        "openai": {"enabled": False, "api_key": "", "default_model": "gpt-4o"},
        "together": {
            "enabled": False,
            "api_key": "",
            "default_model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        },
        "openrouter": {"enabled": False, "api_key": "", "default_model": "anthropic/claude-sonnet-4-6"},
    },
}

ENV_KEY_MAP = {
    "gemini": "GEMINI_API_KEY",
    "gemini-api": "GEMINI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "together": "TOGETHER_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}
logger = logging.getLogger(__name__)


class KeyManager:
    def __init__(self, repo_root: Path, config_path: Path | None = None) -> None:
        self.repo_root = Path(repo_root)
        self.config_path = config_path or self.repo_root / "data" / "custom" / "llm-config.yaml"
        self.model_override_path = self.repo_root / "data" / "custom" / "swarm-model-overrides.json"

    @staticmethod
    def mask_key(key: str) -> str:
        if not key:
            return ""
        if len(key) <= 8:
            return "*" * len(key)
        return f"{key[:3]}...****{key[-4:]}"

    @staticmethod
    def key_hash8(key: str) -> str:
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:8] if key else ""

    def _parse_bool(self, value: str) -> bool:
        return value.strip().lower() in {"true", "yes", "1", "on"}

    def load_config(self) -> dict[str, Any]:
        cfg = json.loads(json.dumps(DEFAULT_CONFIG))
        if not self.config_path.exists():
            return cfg

        current_provider: str | None = None
        for raw_line in self.config_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.rstrip()
            if not line or line.lstrip().startswith("#"):
                continue
            if not line.startswith(" "):
                if line.startswith("default_provider:"):
                    cfg["default_provider"] = line.split(":", 1)[1].strip()
                continue
            if line.startswith("  ") and line.strip().endswith(":") and not line.startswith("    "):
                current_provider = line.strip()[:-1]
                cfg["providers"].setdefault(current_provider, {})
                continue
            if line.startswith("    ") and ":" in line and current_provider:
                key, value = line.strip().split(":", 1)
                value = value.strip().strip('"')
                if key == "enabled":
                    cfg["providers"][current_provider][key] = self._parse_bool(value)
                else:
                    cfg["providers"][current_provider][key] = value
        return cfg

    def save_config(self, cfg: dict[str, Any]) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        providers = cfg.get("providers", {})
        lines = [
            "# LLM Provider Configuration",
            f"default_provider: {cfg.get('default_provider', 'claude-code')}",
            "providers:",
        ]
        for provider in sorted(providers.keys()):
            p = providers[provider]
            lines.append(f"  {provider}:")
            for key in ("enabled", "command", "api_key", "default_model"):
                if key not in p:
                    continue
                value = p[key]
                if isinstance(value, bool):
                    rendered = "true" if value else "false"
                else:
                    rendered = f'"{value}"'
                lines.append(f"    {key}: {rendered}")
        self.config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def get_provider_key(self, provider: str) -> tuple[str, str]:
        env_var = ENV_KEY_MAP.get(provider)
        if env_var:
            env_key = os.getenv(env_var, "").strip()
            if env_key:
                return env_key, "env"
        cfg = self.load_config()
        key = str(cfg.get("providers", {}).get(provider, {}).get("api_key", "")).strip()
        return key, "file" if key else "none"

    def set_api_key(self, provider: str, api_key: str) -> dict[str, Any]:
        cfg = self.load_config()
        providers = cfg.setdefault("providers", {})
        providers.setdefault(provider, {})
        providers[provider]["api_key"] = api_key
        providers[provider]["enabled"] = True
        self.save_config(cfg)
        return {
            "provider": provider,
            "has_key": bool(api_key),
            "key_masked": self.mask_key(api_key),
            "key_hash": self.key_hash8(api_key),
        }

    def delete_api_key(self, provider: str) -> dict[str, Any]:
        cfg = self.load_config()
        providers = cfg.setdefault("providers", {})
        providers.setdefault(provider, {})
        providers[provider]["api_key"] = ""
        self.save_config(cfg)
        return {"provider": provider, "has_key": False}

    def list_key_status(self) -> dict[str, Any]:
        cfg = self.load_config()
        out: dict[str, Any] = {"providers": {}}
        for provider in sorted(cfg.get("providers", {}).keys()):
            key, source = self.get_provider_key(provider)
            out["providers"][provider] = {
                "has_key": bool(key),
                "source": source,
                "key_masked": self.mask_key(key),
            }
        return out

    def get_swarm_model(self, swarm_id: str, default_model: str) -> str:
        if not self.model_override_path.exists():
            return default_model
        try:
            data = json.loads(self.model_override_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("swarm model overrides file is corrupt: %s", self.model_override_path)
            return default_model
        return str(data.get(swarm_id, default_model))

    def set_swarm_model(self, swarm_id: str, model: str) -> dict[str, Any]:
        data: dict[str, str] = {}
        if self.model_override_path.exists():
            try:
                data = json.loads(self.model_override_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"swarm model overrides file is corrupt: {self.model_override_path}") from exc
        data[swarm_id] = model
        self.model_override_path.parent.mkdir(parents=True, exist_ok=True)
        self.model_override_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {"swarm_id": swarm_id, "model": model}
