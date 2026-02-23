from __future__ import annotations

import json
from pathlib import Path

import stillwater.llm_cli_support as llm


def test_update_llm_config_text_updates_provider_and_ollama_fields() -> None:
    old = (
        'provider: "claude-code"\n'
        "\n"
        "ollama:\n"
        '  url: "http://localhost:11434"\n'
        '  model: "llama3.1:8b"\n'
    )
    new = llm.update_llm_config_text(
        old,
        provider="ollama",
        ollama_url="localhost:11434",
        ollama_model="qwen2.5-coder:7b",
    )
    assert 'provider: "ollama"' in new
    assert '  url: "http://localhost:11434"' in new
    assert '  model: "qwen2.5-coder:7b"' in new


def test_candidate_ollama_urls_reads_solace_settings(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True)
    (repo_root / "llm_config.yaml").write_text(
        'provider: "ollama"\nollama:\n  url: "http://localhost:11434"\n',
        encoding="utf-8",
    )
    solace_settings = tmp_path / "settings.json"
    solace_settings.write_text(
        json.dumps({"ollama_host": "localhost", "ollama_port": 11434}),
        encoding="utf-8",
    )
    urls = llm.candidate_ollama_urls(
        repo_root=repo_root,
        explicit_urls=None,
        env={},
        solace_settings_path=solace_settings,
    )
    assert "http://localhost:11434" in urls
    assert "http://localhost:11434" in urls


def test_choose_preferred_ollama_url_prefers_localhost() -> None:
    probes = [
        {"url": "http://localhost:11434", "reachable": True, "host": "localhost"},
        {"url": "http://localhost:11434", "reachable": True, "host": "localhost"},
    ]
    assert llm.choose_preferred_ollama_url(probes) == "http://localhost:11434"


def test_probe_ollama_urls_handles_unreachable_endpoint() -> None:
    probes = llm.probe_ollama_urls(urls=["http://127.0.0.1:1"], timeout_seconds=0.001)
    assert len(probes) == 1
    assert probes[0]["reachable"] is False
