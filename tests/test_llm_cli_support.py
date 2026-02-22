#!/usr/bin/env python3
"""
llm_cli_support — Comprehensive Test Suite
Version: 1.0.0 | Target: 30+ tests | All HTTP mocked

Persona: Linus Torvalds — brutally practical, test every edge case, trust nothing.

Run:
    pytest /home/phuc/projects/stillwater/tests/test_llm_cli_support.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Path setup — same pattern used by other test files in this repo.
# ---------------------------------------------------------------------------
CLI_SRC = Path(__file__).resolve().parent.parent / "cli" / "src"
if str(CLI_SRC) not in sys.path:
    sys.path.insert(0, str(CLI_SRC))

from stillwater.llm_cli_support import (  # noqa: E402
    _norm_url,
    _dedupe_keep_order,
    _split_urls,
    _load_llm_config,
    _solace_remote_url,
    candidate_ollama_urls,
    probe_ollama_url,
    probe_ollama_urls,
    choose_preferred_ollama_url,
    update_llm_config_text,
    update_llm_config_file,
)


# ===========================================================================
# Group 1: _norm_url
# ===========================================================================


class TestNormUrl:
    def test_empty_string_returns_empty(self):
        assert _norm_url("") == ""

    def test_none_coerced_returns_empty(self):
        # The function does (value or ""), so None triggers the same path.
        assert _norm_url(None) == ""  # type: ignore[arg-type]

    def test_whitespace_only_returns_empty(self):
        assert _norm_url("   ") == ""

    def test_url_with_http_scheme_unchanged(self):
        assert _norm_url("http://localhost:11434") == "http://localhost:11434"

    def test_url_with_https_scheme_unchanged(self):
        assert _norm_url("https://example.com") == "https://example.com"

    def test_bare_host_gets_http_prepended(self):
        assert _norm_url("localhost:11434") == "http://localhost:11434"

    def test_bare_hostname_no_port_gets_http(self):
        assert _norm_url("myhost") == "http://myhost"

    def test_trailing_slash_stripped(self):
        assert _norm_url("http://localhost:11434/") == "http://localhost:11434"

    def test_multiple_trailing_slashes_stripped(self):
        assert _norm_url("http://localhost:11434///") == "http://localhost:11434"

    def test_leading_whitespace_stripped(self):
        assert _norm_url("  http://localhost:11434") == "http://localhost:11434"

    def test_trailing_whitespace_stripped(self):
        assert _norm_url("http://localhost:11434  ") == "http://localhost:11434"

    def test_path_component_preserved(self):
        # Trailing slash after a path segment should be stripped too.
        assert _norm_url("http://host:8080/v1/") == "http://host:8080/v1"

    def test_ip_address_gets_http_scheme(self):
        assert _norm_url("192.168.1.100:11434") == "http://192.168.1.100:11434"


# ===========================================================================
# Group 2: _dedupe_keep_order
# ===========================================================================


class TestDedupeKeepOrder:
    def test_empty_iterable(self):
        assert _dedupe_keep_order([]) == []

    def test_no_duplicates_preserved_as_is(self):
        result = _dedupe_keep_order(
            ["http://localhost:11434", "http://127.0.0.1:11434"]
        )
        assert result == ["http://localhost:11434", "http://127.0.0.1:11434"]

    def test_duplicates_removed_first_seen_wins(self):
        result = _dedupe_keep_order(
            ["http://localhost:11434", "http://localhost:11434"]
        )
        assert result == ["http://localhost:11434"]

    def test_order_preserved_with_duplicates(self):
        raw = ["http://b.com", "http://a.com", "http://b.com", "http://c.com"]
        assert _dedupe_keep_order(raw) == [
            "http://b.com",
            "http://a.com",
            "http://c.com",
        ]

    def test_empty_strings_skipped(self):
        result = _dedupe_keep_order(["", "http://localhost:11434", ""])
        assert result == ["http://localhost:11434"]

    def test_whitespace_strings_skipped(self):
        result = _dedupe_keep_order(["  ", "http://host:11434"])
        assert result == ["http://http://host:11434"] or result == ["http://host:11434"]
        # _norm_url strips whitespace and prepends http:// only if no "://",
        # so "  " becomes "" (skipped) and "http://host:11434" stays.
        assert _dedupe_keep_order(["  ", "http://host:11434"]) == [
            "http://host:11434"
        ]

    def test_bare_url_normalised_before_dedup(self):
        # "localhost:11434" and "http://localhost:11434" should be the same after norm.
        result = _dedupe_keep_order(["localhost:11434", "http://localhost:11434"])
        assert result == ["http://localhost:11434"]
        assert len(result) == 1


# ===========================================================================
# Group 3: _split_urls
# ===========================================================================


class TestSplitUrls:
    def test_empty_string_returns_empty_list(self):
        assert _split_urls("") == []

    def test_none_returns_empty_list(self):
        assert _split_urls(None) == []  # type: ignore[arg-type]

    def test_single_url_no_comma(self):
        assert _split_urls("http://localhost:11434") == ["http://localhost:11434"]

    def test_comma_separated_urls(self):
        raw = "http://a.com,http://b.com,http://c.com"
        assert _split_urls(raw) == ["http://a.com", "http://b.com", "http://c.com"]

    def test_whitespace_around_commas_stripped(self):
        raw = "http://a.com , http://b.com"
        assert _split_urls(raw) == ["http://a.com", "http://b.com"]

    def test_empty_segments_between_commas_skipped(self):
        raw = "http://a.com,,http://b.com"
        assert _split_urls(raw) == ["http://a.com", "http://b.com"]

    def test_trailing_comma_ignored(self):
        raw = "http://a.com,"
        assert _split_urls(raw) == ["http://a.com"]


# ===========================================================================
# Group 4: _load_llm_config
# ===========================================================================


class TestLoadLlmConfig:
    def test_missing_file_returns_empty_dict(self, tmp_path):
        result = _load_llm_config(tmp_path)
        assert result == {}

    def test_valid_yaml_dict_returned(self, tmp_path):
        pytest.importorskip("yaml")
        cfg_path = tmp_path / "llm_config.yaml"
        cfg_path.write_text("provider: ollama\nollama:\n  url: http://localhost:11434\n")
        result = _load_llm_config(tmp_path)
        assert result["provider"] == "ollama"
        assert result["ollama"]["url"] == "http://localhost:11434"

    def test_non_dict_yaml_returns_empty_dict(self, tmp_path):
        pytest.importorskip("yaml")
        cfg_path = tmp_path / "llm_config.yaml"
        cfg_path.write_text("- item1\n- item2\n")
        result = _load_llm_config(tmp_path)
        assert result == {}

    def test_empty_yaml_file_returns_empty_dict(self, tmp_path):
        pytest.importorskip("yaml")
        cfg_path = tmp_path / "llm_config.yaml"
        cfg_path.write_text("")
        result = _load_llm_config(tmp_path)
        assert result == {}

    def test_yaml_import_failure_returns_empty_dict(self, tmp_path):
        cfg_path = tmp_path / "llm_config.yaml"
        cfg_path.write_text("provider: ollama\n")
        # Simulate yaml not being installed by patching builtins.__import__.
        import builtins
        original_import = builtins.__import__

        def broken_import(name, *args, **kwargs):
            if name == "yaml":
                raise ImportError("no module named yaml")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=broken_import):
            result = _load_llm_config(tmp_path)
        assert result == {}


# ===========================================================================
# Group 5: _solace_remote_url
# ===========================================================================


class TestSolaceRemoteUrl:
    def test_missing_file_returns_empty(self, tmp_path):
        missing = tmp_path / "settings.json"
        assert _solace_remote_url(missing) == ""

    def test_invalid_json_returns_empty(self, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text("{not valid json}")
        assert _solace_remote_url(p) == ""

    def test_json_not_a_dict_returns_empty(self, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text('["a", "b"]')
        assert _solace_remote_url(p) == ""

    def test_no_ollama_host_returns_empty(self, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text(json.dumps({"ollama_port": 11434}))
        assert _solace_remote_url(p) == ""

    def test_empty_ollama_host_returns_empty(self, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text(json.dumps({"ollama_host": "  ", "ollama_port": 11434}))
        assert _solace_remote_url(p) == ""

    def test_custom_host_and_port(self, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text(json.dumps({"ollama_host": "192.168.68.100", "ollama_port": 11434}))
        result = _solace_remote_url(p)
        assert result == "http://192.168.68.100:11434"

    def test_missing_port_defaults_to_11434(self, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text(json.dumps({"ollama_host": "remotehost"}))
        result = _solace_remote_url(p)
        assert result == "http://remotehost:11434"

    def test_invalid_port_defaults_to_11434(self, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text(json.dumps({"ollama_host": "remotehost", "ollama_port": "not-a-number"}))
        result = _solace_remote_url(p)
        assert result == "http://remotehost:11434"

    def test_trailing_slash_stripped(self, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text(json.dumps({"ollama_host": "remotehost", "ollama_port": 8080}))
        result = _solace_remote_url(p)
        assert not result.endswith("/")
        assert result == "http://remotehost:8080"


# ===========================================================================
# Group 6: candidate_ollama_urls
# ===========================================================================


class TestCandidateOllamaUrls:
    def test_always_includes_localhost(self, tmp_path):
        urls = candidate_ollama_urls(repo_root=tmp_path, env={})
        assert "http://localhost:11434" in urls

    def test_always_includes_127_0_0_1(self, tmp_path):
        urls = candidate_ollama_urls(repo_root=tmp_path, env={})
        assert "http://127.0.0.1:11434" in urls

    def test_explicit_urls_appear_first(self, tmp_path):
        urls = candidate_ollama_urls(
            repo_root=tmp_path,
            explicit_urls=["http://explicit.host:11434"],
            env={},
        )
        assert urls[0] == "http://explicit.host:11434"

    def test_stillwater_ollama_url_env_var(self, tmp_path):
        env = {"STILLWATER_OLLAMA_URL": "http://custom.host:11434"}
        urls = candidate_ollama_urls(repo_root=tmp_path, env=env)
        assert "http://custom.host:11434" in urls

    def test_solace_ollama_host_env_var(self, tmp_path):
        env = {"SOLACE_OLLAMA_HOST": "192.168.1.50", "SOLACE_OLLAMA_PORT": "11435"}
        urls = candidate_ollama_urls(repo_root=tmp_path, env=env)
        assert "http://192.168.1.50:11435" in urls

    def test_ollama_host_env_var(self, tmp_path):
        env = {"OLLAMA_HOST": "10.0.0.1", "OLLAMA_PORT": "9999"}
        urls = candidate_ollama_urls(repo_root=tmp_path, env=env)
        assert "http://10.0.0.1:9999" in urls

    def test_deduplication_applied(self, tmp_path):
        # Providing the same URL as explicit and via env should only appear once.
        env = {"STILLWATER_OLLAMA_URL": "http://localhost:11434"}
        urls = candidate_ollama_urls(repo_root=tmp_path, env=env)
        assert urls.count("http://localhost:11434") == 1

    def test_solace_settings_path_used(self, tmp_path):
        settings = tmp_path / "settings.json"
        settings.write_text(json.dumps({"ollama_host": "remotenode", "ollama_port": 11434}))
        urls = candidate_ollama_urls(
            repo_root=tmp_path,
            env={},
            solace_settings_path=settings,
        )
        assert "http://remotenode:11434" in urls

    def test_llm_config_yaml_url_included(self, tmp_path):
        pytest.importorskip("yaml")
        cfg = tmp_path / "llm_config.yaml"
        cfg.write_text("ollama:\n  url: http://yaml.host:11434\n")
        urls = candidate_ollama_urls(repo_root=tmp_path, env={})
        assert "http://yaml.host:11434" in urls

    def test_stillwater_ollama_urls_env_var_multi(self, tmp_path):
        env = {"STILLWATER_OLLAMA_URLS": "http://a.com:11434,http://b.com:11434"}
        urls = candidate_ollama_urls(repo_root=tmp_path, env=env)
        assert "http://a.com:11434" in urls
        assert "http://b.com:11434" in urls

    def test_result_is_list_no_duplicates(self, tmp_path):
        urls = candidate_ollama_urls(repo_root=tmp_path, env={})
        assert len(urls) == len(set(urls))


# ===========================================================================
# Group 7: probe_ollama_url
# ===========================================================================


class TestProbeOllamaUrl:
    def test_success_returns_reachable_true(self):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2:latest"},
                {"name": "mistral:7b"},
            ]
        }
        with patch("requests.get", return_value=mock_response):
            result = probe_ollama_url(url="http://localhost:11434")
        assert result["reachable"] is True
        assert result["url"] == "http://localhost:11434"
        assert result["host"] == "localhost"
        assert result["model_count"] == 2
        assert "llama3.2:latest" in result["models"]
        assert "mistral:7b" in result["models"]

    def test_success_models_sorted(self):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "models": [{"name": "z-model"}, {"name": "a-model"}]
        }
        with patch("requests.get", return_value=mock_response):
            result = probe_ollama_url(url="http://localhost:11434")
        assert result["models"] == ["a-model", "z-model"]

    def test_success_empty_models_list(self):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"models": []}
        with patch("requests.get", return_value=mock_response):
            result = probe_ollama_url(url="http://localhost:11434")
        assert result["model_count"] == 0
        assert result["models"] == []

    def test_connection_error_propagates(self):
        with patch("requests.get", side_effect=ConnectionError("refused")):
            with pytest.raises(ConnectionError):
                probe_ollama_url(url="http://localhost:11434")

    def test_url_normalised_before_request(self):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}
        with patch("requests.get", return_value=mock_response) as mock_get:
            probe_ollama_url(url="localhost:11434")
        # The actual URL passed to requests.get must include the scheme.
        called_url = mock_get.call_args[0][0]
        assert called_url.startswith("http://")

    def test_payload_with_no_models_key(self):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}
        with patch("requests.get", return_value=mock_response):
            result = probe_ollama_url(url="http://localhost:11434")
        assert result["model_count"] == 0

    def test_duplicate_model_names_deduped(self):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "models": [{"name": "llama3"}, {"name": "llama3"}]
        }
        with patch("requests.get", return_value=mock_response):
            result = probe_ollama_url(url="http://localhost:11434")
        assert result["model_count"] == 1


# ===========================================================================
# Group 8: probe_ollama_urls
# ===========================================================================


class TestProbeOllamaUrls:
    def _mock_get_factory(self, reachable_hosts: set):
        """Returns a requests.get mock that succeeds for hosts in reachable_hosts."""
        def mock_get(url, timeout=None):
            from urllib.parse import urlparse
            host = urlparse(url).hostname
            if host in reachable_hosts:
                r = MagicMock()
                r.raise_for_status.return_value = None
                r.json.return_value = {"models": []}
                return r
            raise ConnectionError(f"Cannot reach {host}")
        return mock_get

    def test_empty_urls_returns_empty_list(self):
        result = probe_ollama_urls(urls=[])
        assert result == []

    def test_empty_string_urls_skipped(self):
        result = probe_ollama_urls(urls=["", "  "])
        assert result == []

    def test_reachable_url_marked_true(self):
        with patch("requests.get", side_effect=self._mock_get_factory({"localhost"})):
            result = probe_ollama_urls(urls=["http://localhost:11434"])
        assert len(result) == 1
        assert result[0]["reachable"] is True

    def test_unreachable_url_marked_false(self):
        with patch("requests.get", side_effect=self._mock_get_factory(set())):
            result = probe_ollama_urls(urls=["http://dead.host:11434"])
        assert len(result) == 1
        assert result[0]["reachable"] is False
        assert "error" in result[0]

    def test_mix_of_reachable_and_unreachable(self):
        with patch(
            "requests.get",
            side_effect=self._mock_get_factory({"localhost"}),
        ):
            result = probe_ollama_urls(
                urls=["http://localhost:11434", "http://dead.host:11434"]
            )
        assert len(result) == 2
        assert result[0]["reachable"] is True
        assert result[1]["reachable"] is False

    def test_unreachable_entry_has_zero_model_count(self):
        with patch("requests.get", side_effect=ConnectionError("nope")):
            result = probe_ollama_urls(urls=["http://bad.host:11434"])
        assert result[0]["model_count"] == 0
        assert result[0]["models"] == []


# ===========================================================================
# Group 9: choose_preferred_ollama_url
# ===========================================================================


class TestChoosePreferredOllamaUrl:
    def test_empty_probes_returns_empty_string(self):
        assert choose_preferred_ollama_url([]) == ""

    def test_no_reachable_returns_empty_string(self):
        probes = [
            {"url": "http://dead.host:11434", "reachable": False, "host": "dead.host"}
        ]
        assert choose_preferred_ollama_url(probes) == ""

    def test_prefers_localhost_over_remote(self):
        probes = [
            {
                "url": "http://remote.host:11434",
                "reachable": True,
                "host": "remote.host",
            },
            {
                "url": "http://localhost:11434",
                "reachable": True,
                "host": "localhost",
            },
        ]
        assert choose_preferred_ollama_url(probes) == "http://localhost:11434"

    def test_prefers_127_0_0_1_over_remote(self):
        probes = [
            {
                "url": "http://remote.host:11434",
                "reachable": True,
                "host": "remote.host",
            },
            {
                "url": "http://127.0.0.1:11434",
                "reachable": True,
                "host": "127.0.0.1",
            },
        ]
        assert choose_preferred_ollama_url(probes) == "http://127.0.0.1:11434"

    def test_fallback_to_first_reachable_remote(self):
        probes = [
            {
                "url": "http://dead.host:11434",
                "reachable": False,
                "host": "dead.host",
            },
            {
                "url": "http://alive.remote:11434",
                "reachable": True,
                "host": "alive.remote",
            },
        ]
        assert choose_preferred_ollama_url(probes) == "http://alive.remote:11434"

    def test_only_unreachable_entries_returns_empty(self):
        probes = [
            {"url": "http://a.com:11434", "reachable": False, "host": "a.com"},
            {"url": "http://b.com:11434", "reachable": False, "host": "b.com"},
        ]
        assert choose_preferred_ollama_url(probes) == ""


# ===========================================================================
# Group 10: update_llm_config_text
# ===========================================================================


class TestUpdateLlmConfigText:
    def test_empty_text_adds_provider(self):
        result = update_llm_config_text("", provider="ollama")
        assert 'provider: "ollama"' in result

    def test_existing_provider_replaced(self):
        text = 'provider: "openai"\n'
        result = update_llm_config_text(text, provider="ollama")
        assert 'provider: "ollama"' in result
        assert "openai" not in result

    def test_ollama_url_creates_section_if_missing(self):
        result = update_llm_config_text("", ollama_url="http://localhost:11434")
        assert "ollama:" in result
        assert '  url: "http://localhost:11434"' in result

    def test_ollama_url_normalised(self):
        result = update_llm_config_text("", ollama_url="localhost:11434/")
        assert '  url: "http://localhost:11434"' in result

    def test_ollama_url_replaced_in_existing_section(self):
        text = "ollama:\n  url: \"http://old.host:11434\"\n"
        result = update_llm_config_text(text, ollama_url="http://new.host:11434")
        assert '  url: "http://new.host:11434"' in result
        assert "old.host" not in result

    def test_ollama_model_creates_section_key(self):
        result = update_llm_config_text("", ollama_model="llama3.2:latest")
        assert "ollama:" in result
        assert '  model: "llama3.2:latest"' in result

    def test_ollama_model_replaced_in_existing_section(self):
        text = "ollama:\n  model: \"old-model\"\n"
        result = update_llm_config_text(text, ollama_model="new-model")
        assert '  model: "new-model"' in result
        assert "old-model" not in result

    def test_no_kwargs_returns_text_with_newline(self):
        text = "provider: \"ollama\"\n"
        result = update_llm_config_text(text)
        assert result.endswith("\n")

    def test_result_always_ends_with_newline(self):
        result = update_llm_config_text("", provider="ollama", ollama_url="http://h:11434")
        assert result.endswith("\n")

    def test_existing_section_key_insertion(self):
        # Section exists but key is absent — new key inserted right after header.
        text = "ollama:\n  url: \"http://localhost:11434\"\n"
        result = update_llm_config_text(text, ollama_model="phi3:mini")
        assert '  model: "phi3:mini"' in result
        assert '  url: "http://localhost:11434"' in result

    def test_multiple_updates_at_once(self):
        result = update_llm_config_text(
            "",
            provider="ollama",
            ollama_url="http://localhost:11434",
            ollama_model="llama3",
        )
        assert 'provider: "ollama"' in result
        assert '  url: "http://localhost:11434"' in result
        assert '  model: "llama3"' in result


# ===========================================================================
# Group 11: update_llm_config_file
# ===========================================================================


class TestUpdateLlmConfigFile:
    def test_creates_file_if_missing(self, tmp_path):
        path = update_llm_config_file(
            repo_root=tmp_path,
            provider="ollama",
        )
        assert path.exists()
        content = path.read_text()
        assert 'provider: "ollama"' in content

    def test_round_trip_with_all_fields(self, tmp_path):
        update_llm_config_file(
            repo_root=tmp_path,
            provider="ollama",
            ollama_url="http://localhost:11434",
            ollama_model="mistral:7b",
        )
        content = (tmp_path / "llm_config.yaml").read_text()
        assert 'provider: "ollama"' in content
        assert '  url: "http://localhost:11434"' in content
        assert '  model: "mistral:7b"' in content

    def test_updates_existing_file(self, tmp_path):
        cfg = tmp_path / "llm_config.yaml"
        cfg.write_text('provider: "openai"\n')
        update_llm_config_file(repo_root=tmp_path, provider="ollama")
        content = cfg.read_text()
        assert 'provider: "ollama"' in content
        assert "openai" not in content

    def test_returns_path_object(self, tmp_path):
        result = update_llm_config_file(repo_root=tmp_path, provider="ollama")
        assert isinstance(result, Path)
        assert result == tmp_path / "llm_config.yaml"

    def test_file_ends_with_newline(self, tmp_path):
        update_llm_config_file(
            repo_root=tmp_path,
            provider="ollama",
            ollama_url="http://localhost:11434",
        )
        content = (tmp_path / "llm_config.yaml").read_text()
        assert content.endswith("\n")
