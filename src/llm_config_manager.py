#!/usr/bin/env python3
"""
Stillwater OS - LLM Configuration Manager
Auth: 65537
Purpose: Centralized LLM endpoint management across all notebooks and solvers

This module allows easy switching between different LLM providers while maintaining
a single configuration point.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json

try:
    import yaml
except ImportError:
    yaml = None


class LLMConfigManager:
    """Manages LLM configuration and provides unified interface for all providers."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to llm_config.yaml. If None, searches for it in repo root.
        """
        self.config_path = config_path or self._find_config()
        self.config = self._load_config()
        self.active_provider = self.config.get("provider", "claude-code")

    def _find_config(self) -> Path:
        """Find llm_config.yaml in repository."""
        current = Path.cwd()

        # Check current directory
        if (current / "llm_config.yaml").exists():
            return current / "llm_config.yaml"

        # Check parent directories (for notebook execution)
        for parent in current.parents:
            if (parent / "llm_config.yaml").exists():
                return parent / "llm_config.yaml"

        # Fallback to repo root assumption
        repo_root = Path(__file__).parent.parent
        return repo_root / "llm_config.yaml"

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        if yaml is None:
            # Fallback: simple YAML parsing without yaml library
            return self._parse_yaml_manually()

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _parse_yaml_manually(self) -> Dict[str, Any]:
        """Simple YAML parser for when PyYAML is not available."""
        config = {}
        current_section = None

        with open(self.config_path) as f:
            for line in f:
                line = line.rstrip()

                # Skip comments and empty lines
                if not line.strip() or line.strip().startswith("#"):
                    continue

                # Check if this is a section header (no indentation, ends with ':')
                if line and not line[0].isspace() and line.endswith(":"):
                    current_section = line[:-1]  # Remove the colon
                    if current_section != "provider":
                        config[current_section] = {}
                    continue

                # Parse key-value pairs
                if current_section and line.startswith("  "):
                    key, _, value = line.strip().partition(":")
                    if _:
                        # Simple value parsing
                        value = value.strip()
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.lower() == "true":
                            value = True
                        elif value.lower() == "false":
                            value = False
                        config[current_section][key] = value
                elif not line.startswith("  ") and ":" in line:
                    # Top-level key-value
                    key, _, value = line.partition(":")
                    key = key.strip()
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    config[key] = value

        return config

    def get_active_provider_config(self) -> Dict[str, Any]:
        """Get configuration for the active provider."""
        provider_config = self.config.get(self.active_provider, {})
        if not provider_config:
            raise ValueError(f"Unknown provider: {self.active_provider}")
        return provider_config

    def get_provider_url(self) -> str:
        """Get the URL/endpoint for the active provider."""
        config = self.get_active_provider_config()
        return config.get("url", "")

    def get_provider_name(self) -> str:
        """Get the human-readable name of the active provider."""
        config = self.get_active_provider_config()
        return config.get("name", self.active_provider)

    def get_provider_model(self) -> str:
        """Get the model name for the active provider (if applicable)."""
        config = self.get_active_provider_config()
        return config.get("model", "")

    def get_provider_type(self) -> str:
        """Get provider type: 'http' or 'api'."""
        config = self.get_active_provider_config()
        return config.get("type", "http")

    def requires_api_key(self) -> bool:
        """Check if active provider requires an API key."""
        config = self.get_active_provider_config()
        return config.get("requires_api_key", False)

    def get_required_env_vars(self) -> list:
        """Get list of required environment variables for active provider."""
        config = self.get_active_provider_config()
        return config.get("environment_variables", [])

    def validate_setup(self) -> tuple[bool, str]:
        """Validate that the active provider is properly configured.

        Returns:
            Tuple of (is_valid, message)
        """
        if self.requires_api_key():
            missing = []
            for env_var in self.get_required_env_vars():
                if not os.environ.get(env_var):
                    missing.append(env_var)

            if missing:
                return False, f"Missing API keys: {', '.join(missing)}"

        return True, f"✅ {self.get_provider_name()} is configured"

    def switch_provider(self, provider: str):
        """Switch to a different provider.

        Args:
            provider: Name of provider (e.g., "openai", "claude", "openrouter")
        """
        if provider not in self.config:
            raise ValueError(f"Unknown provider: {provider}")
        self.active_provider = provider

    def list_providers(self) -> Dict[str, str]:
        """Get list of all available providers and their URLs."""
        providers = {}
        for key, config in self.config.items():
            if isinstance(config, dict) and "url" in config:
                providers[key] = {
                    "name": config.get("name", key),
                    "url": config.get("url", ""),
                    "type": config.get("type", ""),
                }
        return providers

    def print_status(self):
        """Print current configuration status."""
        print("\n" + "=" * 80)
        print("LLM CONFIGURATION STATUS")
        print("=" * 80)
        print(f"\nActive Provider: {self.active_provider}")
        print(f"Provider Name: {self.get_provider_name()}")
        print(f"URL/Endpoint: {self.get_provider_url()}")

        if self.get_provider_model():
            print(f"Model: {self.get_provider_model()}")

        is_valid, msg = self.validate_setup()
        print(f"Status: {msg}")

        print("\n" + "-" * 80)
        print("Available Providers:")
        for provider_name, provider_info in self.list_providers().items():
            marker = "→ " if provider_name == self.active_provider else "  "
            print(f"{marker}{provider_name:20} {provider_info['name']:30} {provider_info['url']}")

        print("\n" + "-" * 80)
        print("To switch providers:")
        print("  import os")
        print("  os.environ['ACTIVE_LLM_PROVIDER'] = 'openai'  # or any other provider")
        print("  # Then export API key: OPENAI_API_KEY=sk-...")
        print("=" * 80 + "\n")


def get_llm_config() -> LLMConfigManager:
    """Get or create the global LLM configuration manager."""
    global _llm_config_instance
    if "_llm_config_instance" not in globals():
        _llm_config_instance = LLMConfigManager()
    return _llm_config_instance


def setup_llm_client_for_notebook() -> Dict[str, Any]:
    """Setup LLM client configuration for use in Jupyter notebooks.

    Returns:
        Dictionary with configuration for the notebook to use.
    """
    config = get_llm_config()

    is_valid, msg = config.validate_setup()
    print(msg)

    if not is_valid:
        print(f"⚠️  Setup incomplete. Required: {', '.join(config.get_required_env_vars())}")

    return {
        "provider": config.active_provider,
        "url": config.get_provider_url(),
        "model": config.get_provider_model(),
        "type": config.get_provider_type(),
        "name": config.get_provider_name(),
    }


def get_llm_url() -> str:
    """Get the active LLM endpoint URL."""
    return get_llm_config().get_provider_url()


def get_llm_provider() -> str:
    """Get the active LLM provider name."""
    return get_llm_config().active_provider


def switch_llm_provider(provider: str):
    """Switch to a different LLM provider."""
    get_llm_config().switch_provider(provider)
    print(f"✅ Switched to {provider}")


if __name__ == "__main__":
    # Test the configuration manager
    config = LLMConfigManager()
    config.print_status()
