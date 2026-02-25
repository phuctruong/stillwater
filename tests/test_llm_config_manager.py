#!/usr/bin/env python3
"""
Stillwater LLM Config Manager — Test Suite
Version: 1.0.0 | Target: 28 tests | rung_target: 641

Tests:
  Group 1: Module import and class availability
  Group 2: Initialization — explicit config_path
  Group 3: Initialization — missing file raises FileNotFoundError
  Group 4: Config loading — YAML parsing (PyYAML path)
  Group 5: Config loading — manual YAML fallback parser
  Group 6: Provider getters (url, name, model, type)
  Group 7: requires_api_key() and get_required_env_vars()
  Group 8: Provider selection — switch_provider() + active_provider
  Group 9: list_providers() — structure and completeness
  Group 10: validate_setup() — api-type with env vars
  Group 11: validate_setup() — cli-type (mocked subprocess)
  Group 12: validate_setup() — http/localhost (mocked requests)
  Group 13: Module-level helpers (get_llm_url, get_llm_provider)
  Group 14: Edge cases — empty config, malformed lines, missing fields

Run:
    cd /home/phuc/projects/stillwater
    python -m pytest tests/test_llm_config_manager.py -v --tb=short
"""

from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure the src/cli/src package is importable without installing
CLI_SRC = Path(__file__).resolve().parent.parent / "src" / "cli" / "src"
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))


# ---------------------------------------------------------------------------
# Helpers — build minimal valid YAML config files in tmp_path
# ---------------------------------------------------------------------------

MINIMAL_YAML = textwrap.dedent("""\
    provider: "claude-code"

    claude-code:
      name: "Claude Code"
      type: "http"
      url: "http://localhost:8080"
      model: "claude-haiku-4-5-20251001"
      requires_api_key: false
      environment_variables: []
""")

MULTI_PROVIDER_YAML = textwrap.dedent("""\
    provider: "openai"

    openai:
      name: "OpenAI"
      type: "api"
      url: "https://api.openai.com/v1"
      model: "gpt-4o-mini"
      requires_api_key: true
      environment_variables:
        - "OPENAI_API_KEY"

    claude:
      name: "Anthropic Claude"
      type: "api"
      url: "https://api.anthropic.com/v1"
      model: "claude-haiku-4-5-20251001"
      requires_api_key: true
      environment_variables:
        - "ANTHROPIC_API_KEY"

    ollama:
      name: "Ollama (Local)"
      type: "http"
      url: "http://localhost:11434"
      model: "llama3.1:8b"
      requires_api_key: false
      environment_variables: []
""")

CLI_PROVIDER_YAML = textwrap.dedent("""\
    provider: "my-cli"

    my-cli:
      name: "My CLI Provider"
      type: "cli"
      url: "claude-code"
      requires_api_key: false
      environment_variables: []
""")

LOCALHOST_HTTP_YAML = textwrap.dedent("""\
    provider: "local"

    local:
      name: "Local HTTP Server"
      type: "http"
      url: "http://localhost:9999"
      requires_api_key: false
      environment_variables: []
""")


def _write_config(tmp_path: Path, content: str) -> Path:
    """Write a YAML config file to tmp_path and return its path."""
    cfg = tmp_path / "llm_config.yaml"
    cfg.write_text(content)
    return cfg


# ===========================================================================
# Group 1: Import smoke tests
# ===========================================================================

class TestImports:
    """All expected names are importable."""

    def test_import_llm_config_manager_class(self):
        from llm_config_manager import LLMConfigManager
        assert LLMConfigManager is not None

    def test_import_get_llm_config(self):
        from llm_config_manager import get_llm_config
        assert callable(get_llm_config)

    def test_import_get_llm_url(self):
        from llm_config_manager import get_llm_url
        assert callable(get_llm_url)

    def test_import_get_llm_provider(self):
        from llm_config_manager import get_llm_provider
        assert callable(get_llm_provider)

    def test_import_switch_llm_provider(self):
        from llm_config_manager import switch_llm_provider
        assert callable(switch_llm_provider)

    def test_import_setup_llm_client_for_notebook(self):
        from llm_config_manager import setup_llm_client_for_notebook
        assert callable(setup_llm_client_for_notebook)


# ===========================================================================
# Group 2: Initialization — explicit config_path
# ===========================================================================

class TestInitialization:
    """LLMConfigManager loads a valid config file when path is supplied."""

    def test_init_with_explicit_path(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.config_path == cfg

    def test_active_provider_set_from_config(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.active_provider == "claude-code"

    def test_config_is_dict(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert isinstance(mgr.config, dict)

    def test_multi_provider_active_set_correctly(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.active_provider == "openai"

    def test_default_active_provider_fallback(self, tmp_path):
        """When 'provider' key is absent, should default to 'claude-code'."""
        from llm_config_manager import LLMConfigManager
        content = textwrap.dedent("""\
            claude-code:
              name: "Test"
              type: "http"
              url: "http://localhost:8080"
        """)
        cfg = _write_config(tmp_path, content)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.active_provider == "claude-code"


# ===========================================================================
# Group 3: Missing config file raises FileNotFoundError
# ===========================================================================

class TestMissingConfig:
    """FileNotFoundError when config file does not exist."""

    def test_missing_file_raises(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        nonexistent = tmp_path / "does_not_exist.yaml"
        with pytest.raises(FileNotFoundError):
            LLMConfigManager(config_path=nonexistent)

    def test_missing_file_error_contains_path(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        nonexistent = tmp_path / "missing.yaml"
        with pytest.raises(FileNotFoundError, match="missing.yaml"):
            LLMConfigManager(config_path=nonexistent)


# ===========================================================================
# Group 4: YAML parsing via PyYAML
# ===========================================================================

class TestYAMLLoading:
    """Config loaded correctly via PyYAML when available."""

    def test_provider_key_parsed(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert "openai" in mgr.config

    def test_nested_dict_parsed(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert isinstance(mgr.config.get("openai"), dict)

    def test_url_value_read(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.config["openai"]["url"] == "https://api.openai.com/v1"

    def test_boolean_requires_api_key_parsed(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.config["openai"]["requires_api_key"] is True
        assert mgr.config["ollama"]["requires_api_key"] is False

    def test_list_env_vars_parsed(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        env_vars = mgr.config["openai"]["environment_variables"]
        assert isinstance(env_vars, list)
        assert "OPENAI_API_KEY" in env_vars


# ===========================================================================
# Group 5: Manual YAML fallback parser (_parse_yaml_manually)
# ===========================================================================

class TestManualYAMLParser:
    """_parse_yaml_manually produces correct output when yaml lib absent."""

    def test_manual_parser_reads_top_level_key(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        # Invoke directly — always available regardless of yaml import
        result = mgr._parse_yaml_manually()
        assert "provider" in result or "claude-code" in result

    def test_manual_parser_skips_comments(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        content = textwrap.dedent("""\
            # This is a comment
            provider: "offline"

            # Another comment
            offline:
              name: "Offline"
              type: "offline"
              url: ""
        """)
        cfg = _write_config(tmp_path, content)
        mgr = LLMConfigManager(config_path=cfg)
        result = mgr._parse_yaml_manually()
        # Comment lines must not appear as keys
        comment_keys = [k for k in result if k.startswith("#")]
        assert comment_keys == []

    def test_manual_parser_strips_quoted_strings(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        content = textwrap.dedent("""\
            provider: "claude-code"

            claude-code:
              name: "My Provider"
              type: "http"
              url: "http://localhost:8080"
        """)
        cfg = _write_config(tmp_path, content)
        mgr = LLMConfigManager(config_path=cfg)
        result = mgr._parse_yaml_manually()
        # URL should not include surrounding quotes
        if "claude-code" in result and isinstance(result["claude-code"], dict):
            assert result["claude-code"]["url"] == "http://localhost:8080"

    def test_manual_parser_handles_empty_lines(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        content = textwrap.dedent("""\
            provider: "offline"


            offline:
              name: "Offline"
              url: ""
        """)
        cfg = _write_config(tmp_path, content)
        mgr = LLMConfigManager(config_path=cfg)
        # Must not crash on empty lines
        result = mgr._parse_yaml_manually()
        assert isinstance(result, dict)


# ===========================================================================
# Group 6: Provider getters
# ===========================================================================

class TestProviderGetters:
    """get_provider_url, get_provider_name, get_provider_model, get_provider_type."""

    def test_get_provider_url(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.get_provider_url() == "https://api.openai.com/v1"

    def test_get_provider_name(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.get_provider_name() == "OpenAI"

    def test_get_provider_model(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.get_provider_model() == "gpt-4o-mini"

    def test_get_provider_type_api(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.get_provider_type() == "api"

    def test_get_provider_type_http(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.get_provider_type() == "http"

    def test_get_provider_name_falls_back_to_key(self, tmp_path):
        """If 'name' field absent, falls back to provider key."""
        from llm_config_manager import LLMConfigManager
        content = textwrap.dedent("""\
            provider: "myprovider"

            myprovider:
              type: "api"
              url: "https://example.com"
              requires_api_key: false
              environment_variables: []
        """)
        cfg = _write_config(tmp_path, content)
        mgr = LLMConfigManager(config_path=cfg)
        # name absent → falls back to active_provider key
        assert mgr.get_provider_name() == "myprovider"

    def test_get_provider_model_empty_when_absent(self, tmp_path):
        """Returns empty string when 'model' key is absent."""
        from llm_config_manager import LLMConfigManager
        content = textwrap.dedent("""\
            provider: "simple"

            simple:
              name: "Simple Provider"
              type: "api"
              url: "https://example.com"
              requires_api_key: false
              environment_variables: []
        """)
        cfg = _write_config(tmp_path, content)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.get_provider_model() == ""

    def test_get_active_provider_config_unknown_raises(self, tmp_path):
        """ValueError when active_provider not in config."""
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        mgr.active_provider = "nonexistent"
        with pytest.raises(ValueError, match="Unknown provider"):
            mgr.get_active_provider_config()


# ===========================================================================
# Group 7: requires_api_key() and get_required_env_vars()
# ===========================================================================

class TestApiKeyChecks:
    """requires_api_key and get_required_env_vars return correct values."""

    def test_requires_api_key_true(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.requires_api_key() is True

    def test_requires_api_key_false(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.requires_api_key() is False

    def test_get_required_env_vars_returns_list(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        env_vars = mgr.get_required_env_vars()
        assert isinstance(env_vars, list)

    def test_get_required_env_vars_correct_value(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert "OPENAI_API_KEY" in mgr.get_required_env_vars()

    def test_get_required_env_vars_empty_when_no_key(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.get_required_env_vars() == []


# ===========================================================================
# Group 8: switch_provider() and active_provider
# ===========================================================================

class TestSwitchProvider:
    """switch_provider() changes active_provider; unknown raises ValueError."""

    def test_switch_to_known_provider(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        mgr.switch_provider("claude")
        assert mgr.active_provider == "claude"

    def test_switch_updates_getters(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        mgr.switch_provider("claude")
        assert mgr.get_provider_url() == "https://api.anthropic.com/v1"

    def test_switch_to_unknown_raises(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        with pytest.raises(ValueError, match="Unknown provider"):
            mgr.switch_provider("totally_unknown_xyz")

    def test_switch_to_same_provider_is_idempotent(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        mgr.switch_provider("openai")
        assert mgr.active_provider == "openai"


# ===========================================================================
# Group 9: list_providers()
# ===========================================================================

class TestListProviders:
    """list_providers() returns dict with url-bearing providers."""

    def test_list_providers_returns_dict(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        result = mgr.list_providers()
        assert isinstance(result, dict)

    def test_list_providers_contains_all_url_providers(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        result = mgr.list_providers()
        assert "openai" in result
        assert "claude" in result
        assert "ollama" in result

    def test_list_providers_entry_has_name_url_type(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        result = mgr.list_providers()
        for provider_key, info in result.items():
            assert "name" in info, f"Missing 'name' in {provider_key}"
            assert "url" in info, f"Missing 'url' in {provider_key}"
            assert "type" in info, f"Missing 'type' in {provider_key}"

    def test_list_providers_url_values_correct(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        result = mgr.list_providers()
        assert result["openai"]["url"] == "https://api.openai.com/v1"

    def test_list_providers_skips_non_dict_keys(self, tmp_path):
        """'provider' top-level string key must not appear in list_providers."""
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        result = mgr.list_providers()
        # 'provider' is a string, not a dict — should not be in result
        assert "provider" not in result


# ===========================================================================
# Group 10: validate_setup() — API-type providers
# ===========================================================================

class TestValidateSetupAPI:
    """validate_setup checks env vars for api-type providers."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"})
    def test_api_provider_valid_when_key_present(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        is_valid, msg = mgr.validate_setup()
        assert is_valid is True
        assert "OpenAI" in msg

    @patch.dict(os.environ, {}, clear=True)
    def test_api_provider_invalid_when_key_missing(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        is_valid, msg = mgr.validate_setup()
        assert is_valid is False
        assert "OPENAI_API_KEY" in msg

    def test_validate_returns_tuple(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        result = mgr.validate_setup()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_validate_first_element_is_bool(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        is_valid, _ = mgr.validate_setup()
        assert isinstance(is_valid, bool)

    def test_validate_second_element_is_str(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        _, msg = mgr.validate_setup()
        assert isinstance(msg, str)


# ===========================================================================
# Group 11: validate_setup() — CLI-type providers
# ===========================================================================

class TestValidateSetupCLI:
    """validate_setup uses subprocess.run to check CLI availability."""

    def test_cli_provider_valid_when_found(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, CLI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result):
            is_valid, msg = mgr.validate_setup()

        assert is_valid is True

    def test_cli_provider_invalid_when_not_found(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, CLI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)

        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch("subprocess.run", return_value=mock_result):
            is_valid, msg = mgr.validate_setup()

        assert is_valid is False

    def test_cli_provider_invalid_on_exception(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, CLI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)

        with patch("subprocess.run", side_effect=OSError("file not found")):
            is_valid, msg = mgr.validate_setup()

        assert is_valid is False
        assert "Error" in msg


# ===========================================================================
# Group 12: validate_setup() — HTTP/localhost providers
# ===========================================================================

class TestValidateSetupHTTPLocalhost:
    """validate_setup uses requests.get for http providers on localhost."""

    def test_localhost_provider_valid_when_server_up(self, tmp_path):
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, LOCALHOST_HTTP_YAML)
        mgr = LLMConfigManager(config_path=cfg)

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("requests.get", return_value=mock_response):
            is_valid, msg = mgr.validate_setup()

        assert is_valid is True

    def test_localhost_provider_invalid_on_connection_error(self, tmp_path):
        import requests as requests_lib
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, LOCALHOST_HTTP_YAML)
        mgr = LLMConfigManager(config_path=cfg)

        with patch("requests.get", side_effect=requests_lib.exceptions.ConnectionError("refused")):
            is_valid, msg = mgr.validate_setup()

        assert is_valid is False

    def test_localhost_provider_valid_on_404_response(self, tmp_path):
        """404 still means server is up; should return valid."""
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, LOCALHOST_HTTP_YAML)
        mgr = LLMConfigManager(config_path=cfg)

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("requests.get", return_value=mock_response):
            is_valid, msg = mgr.validate_setup()

        assert is_valid is True


# ===========================================================================
# Group 13: Module-level helpers
# ===========================================================================

class TestModuleLevelHelpers:
    """get_llm_url and get_llm_provider delegate to global config instance."""

    def test_setup_llm_client_for_notebook_returns_dict(self, tmp_path, capsys):
        from llm_config_manager import LLMConfigManager, setup_llm_client_for_notebook
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)

        with patch("llm_config_manager.get_llm_config", return_value=mgr):
            result = setup_llm_client_for_notebook()

        assert isinstance(result, dict)

    def test_setup_llm_client_for_notebook_has_required_keys(self, tmp_path):
        from llm_config_manager import LLMConfigManager, setup_llm_client_for_notebook
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)

        with patch("llm_config_manager.get_llm_config", return_value=mgr):
            result = setup_llm_client_for_notebook()

        required_keys = {"provider", "url", "model", "type", "name"}
        assert required_keys.issubset(set(result.keys()))

    def test_setup_notebook_provider_value(self, tmp_path):
        from llm_config_manager import LLMConfigManager, setup_llm_client_for_notebook
        cfg = _write_config(tmp_path, MINIMAL_YAML)
        mgr = LLMConfigManager(config_path=cfg)

        with patch("llm_config_manager.get_llm_config", return_value=mgr):
            result = setup_llm_client_for_notebook()

        assert result["provider"] == "claude-code"


# ===========================================================================
# Group 14: Edge cases
# ===========================================================================

class TestEdgeCases:
    """Edge cases: empty config, malformed lines, missing fields."""

    def test_config_with_only_provider_key(self, tmp_path):
        """Config with only 'provider' key — getters raise ValueError."""
        from llm_config_manager import LLMConfigManager
        content = "provider: orphan\n"
        cfg = _write_config(tmp_path, content)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.active_provider == "orphan"
        with pytest.raises(ValueError):
            mgr.get_provider_url()

    def test_manual_parser_graceful_on_no_colon_line(self, tmp_path):
        """_parse_yaml_manually must not crash on lines with no colon."""
        from llm_config_manager import LLMConfigManager
        # Write a valid YAML file so __init__ succeeds via PyYAML
        valid_content = textwrap.dedent("""\
            provider: "offline"

            offline:
              name: "Offline"
              url: ""
              type: "offline"
              requires_api_key: false
              environment_variables: []
        """)
        cfg = _write_config(tmp_path, valid_content)
        mgr = LLMConfigManager(config_path=cfg)

        # Now patch the file on disk so _parse_yaml_manually sees the no-colon line
        content_with_bad_line = valid_content + "this line has no colon\n"
        cfg.write_text(content_with_bad_line)

        result = mgr._parse_yaml_manually()
        assert isinstance(result, dict)

    def test_provider_with_no_environment_variables_field(self, tmp_path):
        """get_required_env_vars returns [] when field absent."""
        from llm_config_manager import LLMConfigManager
        content = textwrap.dedent("""\
            provider: "bare"

            bare:
              name: "Bare"
              type: "api"
              url: "https://example.com"
              requires_api_key: false
        """)
        cfg = _write_config(tmp_path, content)
        mgr = LLMConfigManager(config_path=cfg)
        assert mgr.get_required_env_vars() == []

    def test_list_providers_empty_when_no_url_providers(self, tmp_path):
        """If no provider dict has a 'url' key, list_providers returns {}."""
        from llm_config_manager import LLMConfigManager
        content = "provider: nothing\n"
        cfg = _write_config(tmp_path, content)
        mgr = LLMConfigManager(config_path=cfg)
        result = mgr.list_providers()
        assert result == {}

    def test_multiple_switches_chain_correctly(self, tmp_path):
        """Switching provider multiple times ends on last switch."""
        from llm_config_manager import LLMConfigManager
        cfg = _write_config(tmp_path, MULTI_PROVIDER_YAML)
        mgr = LLMConfigManager(config_path=cfg)
        mgr.switch_provider("claude")
        mgr.switch_provider("ollama")
        mgr.switch_provider("claude")
        assert mgr.active_provider == "claude"
        assert mgr.get_provider_url() == "https://api.anthropic.com/v1"
