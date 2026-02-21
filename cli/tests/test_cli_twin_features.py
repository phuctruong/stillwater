from __future__ import annotations

import json
from pathlib import Path

from stillwater.cli import _default_twin_skills, _repo_root, main


def _load_imo_qa_cases() -> list[tuple[str, str, str]]:
    path = Path(__file__).resolve().parent / "math" / "imo_qa_cases.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("cases", []) if isinstance(payload, dict) else []
    out: list[tuple[str, str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("id", "")).strip()
        prompt = str(row.get("prompt", "")).strip()
        needle = str(row.get("needle", "")).strip()
        if case_id and prompt and needle:
            out.append((case_id, prompt, needle))
    return out


def _imo_prompt_by_id(case_id: str) -> str:
    for cid, prompt, _ in _load_imo_qa_cases():
        if cid == case_id:
            return prompt
    raise AssertionError(f"Missing IMO case id in config: {case_id}")


def test_init_identity_stack(tmp_path: Path) -> None:
    rc = main(["init", "identity-stack", "--dir", str(tmp_path), "--json"])
    assert rc == 0
    assert (tmp_path / "SOUL.md").exists()
    assert (tmp_path / "RIPPLE-IDENTITY.prime-mermaid.md").exists()


def test_recipe_add_and_list(tmp_path: Path, capsys) -> None:
    rc_add = main(["recipe", "add", "unit_test_recipe", "--dir", str(tmp_path), "--json"])
    assert rc_add == 0
    _ = capsys.readouterr()

    rc_list = main(["recipe", "list", "--dir", str(tmp_path), "--json"])
    assert rc_list == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["count"] >= 1
    assert any("recipe.unit_test_recipe.prime-mermaid.md" in p for p in payload["recipes"])


def test_twin_cpu_prepass_json(capsys) -> None:
    rc = main(["twin", "/skills", "--json"])
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["ok"] is True
    assert payload["source"] == "CPU"
    assert "swarm_settings_file" in payload["route"]
    assert "loaded_recipes" in payload["route"]


def test_twin_cpu_papers_json(capsys) -> None:
    rc = main(["twin", "/papers", "--json"])
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["ok"] is True
    assert payload["source"] == "CPU"


def test_twin_cpu_imo_fact_router(capsys) -> None:
    for _cid, prompt, needle in _load_imo_qa_cases():
        rc = main(["twin", prompt, "--json"])
        assert rc == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["ok"] is True
        assert payload["source"] == "CPU"
        assert payload["route"]["action"] == "phuc_swarms_benchmark"
        assert payload["route"].get("swarm_settings_file")
        assert isinstance(payload["route"].get("personas"), dict)
        assert payload["route"]["phuc_decision"]["decision"] == "tool"
        assert needle.lower() in payload["response"].lower()


def test_default_twin_skills_cover_root_phuc_skills() -> None:
    root = _repo_root()
    expected = {path.name for path in (root / "skills").glob("phuc-*.md")}
    selected = set(_default_twin_skills(root))
    assert expected.issubset(selected)


def test_twin_llm_only_bypasses_cpu_benchmark(monkeypatch, capsys) -> None:
    from stillwater import llm_cli_support
    import requests

    monkeypatch.setattr(
        llm_cli_support,
        "candidate_ollama_urls",
        lambda repo_root, explicit_urls=None: ["http://fake-ollama:11434"],
    )
    monkeypatch.setattr(
        llm_cli_support,
        "probe_ollama_urls",
        lambda urls, timeout_seconds=2.0: [
            {"url": "http://fake-ollama:11434", "reachable": True, "models": ["llama3.1:8b"]}
        ],
    )
    monkeypatch.setattr(
        llm_cli_support,
        "choose_preferred_ollama_url",
        lambda probes: "http://fake-ollama:11434",
    )

    class _FakeResp:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"message": {"content": "fake-llm-response"}}

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: _FakeResp())

    rc = main(
        [
            "twin",
            _imo_prompt_by_id("P5"),
            "--llm-only",
            "--model",
            "llama3.1:8b",
            "--json",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["source"] == "LLM"
    assert payload["route"]["action"] == "ollama_chat"
    assert payload["route"]["llm_only"] is True
    assert payload["route"]["cpu_prepass_action"] == "llm_only_bypass"


def test_twin_generic_prompt_records_llm_phuc_decision(monkeypatch, capsys) -> None:
    from stillwater import llm_cli_support
    import requests

    monkeypatch.setattr(
        llm_cli_support,
        "candidate_ollama_urls",
        lambda repo_root, explicit_urls=None: ["http://fake-ollama:11434"],
    )
    monkeypatch.setattr(
        llm_cli_support,
        "probe_ollama_urls",
        lambda urls, timeout_seconds=2.0: [
            {"url": "http://fake-ollama:11434", "reachable": True, "models": ["llama3.1:8b"]}
        ],
    )
    monkeypatch.setattr(
        llm_cli_support,
        "choose_preferred_ollama_url",
        lambda probes: "http://fake-ollama:11434",
    )

    class _FakeResp:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"message": {"content": "generic-llm-answer"}}

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: _FakeResp())

    rc = main(
        [
            "twin",
            "Explain why context windows matter for agent reliability.",
            "--model",
            "llama3.1:8b",
            "--json",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["source"] == "LLM"
    assert payload["route"]["action"] == "ollama_chat"
    assert payload["route"]["cpu_prepass_action"] == "llm_fallback"
    assert payload["route"]["phuc_decision"]["decision"] == "llm"
