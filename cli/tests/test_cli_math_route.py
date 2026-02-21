from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from stillwater.cli import main


def _imo_route_prompt(case_id: str) -> str:
    path = Path(__file__).resolve().parent / "math" / "imo_route_cases.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("cases", []) if isinstance(payload, dict) else []
    for row in rows:
        if isinstance(row, dict) and str(row.get("id", "")).strip() == case_id:
            prompt = str(row.get("prompt", "")).strip()
            if prompt:
                return prompt
    raise AssertionError(f"Missing IMO route case id in config: {case_id}")


def test_twin_math_route_arithmetic_cpu(capsys) -> None:
    rc = main(["twin", "What is 137 * 241?", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["source"] == "CPU"
    assert payload["route"]["action"] == "phuc_math_assist"
    assert payload["route"]["profile"] == "math"
    assert "33017" in payload["response"]


def test_twin_math_route_gcd_cpu(capsys) -> None:
    rc = main(["twin", "Find gcd(123456, 7890).", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["source"] == "CPU"
    assert payload["route"]["action"] == "phuc_math_assist"
    assert payload["route"]["profile"] == "math"
    assert "6" in payload["response"]


def test_twin_math_route_modexp_cpu(capsys) -> None:
    rc = main(["twin", "Compute the remainder when 7^222 is divided by 1000.", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["source"] == "CPU"
    assert payload["route"]["action"] == "phuc_math_assist"
    assert payload["route"]["profile"] == "math"
    assert "49" in payload["response"]


def test_twin_imo_history_outline_prompt_routes_to_cpu_tool(capsys) -> None:
    prompt = (
        "IMO 2022 P1. Solve this problem with a rigorous outline.\n\n"
        "Oracle anchor: leftmost n coins are of the same type\n\n"
        "Oracle concepts: chain, leftmost n coins, same type\n\n"
        "The Bank of Oslo issues two types of coin and asks when the leftmost n coins become the same type.\n\n"
        "Return: assumptions, core idea, and verification checklist."
    )
    rc = main(["twin", prompt, "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["source"] == "CPU"
    assert payload["route"]["action"] == "phuc_imo_history_assist"
    phuc = payload["route"].get("phuc_decision", {})
    assert isinstance(phuc, dict)
    assert phuc.get("decision") == "tool"
    assert phuc.get("profile") == "imo_history"
    assert "Assumptions" in payload["response"]
    assert "Core idea" in payload["response"]
    assert "Verification checklist" in payload["response"]
    assert "leftmost n coins are of the same type" in payload["response"]


def test_twin_historical_imo_prompt_avoids_2024_demo_solver(monkeypatch, capsys) -> None:
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
            return {"message": {"content": "historical-imo-llm-response"}}

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: _FakeResp())

    rc = main(
        [
            "twin",
            _imo_route_prompt("historical_imo_2020_p1"),
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
    phuc = payload["route"].get("phuc_decision", {})
    if isinstance(phuc, dict):
        assert phuc.get("profile", "") != "imo"
    assert payload["route"].get("cpu_prepass_action", "") != "phuc_swarms_benchmark"


def test_twin_official_imo_2024_prompt_avoids_demo_solver(monkeypatch, capsys) -> None:
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
            return {"message": {"content": "official-imo-2024-llm-response"}}

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: _FakeResp())

    rc = main(
        [
            "twin",
            _imo_route_prompt("historical_imo_2024_official_p1"),
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
    phuc = payload["route"].get("phuc_decision", {})
    if isinstance(phuc, dict):
        assert phuc.get("profile", "") != "imo"
    assert payload["route"].get("cpu_prepass_action", "") != "phuc_swarms_benchmark"


def test_imo_phuc_pipeline_writes_phase_artifacts(monkeypatch, capsys) -> None:
    from stillwater import cli as cli_mod

    cases_path = Path(__file__).resolve().parent / "math" / "imo_qa_cases.json"
    run_id = "test-imo-phuc-pass"

    def _fake_twin(*, root, prompt, model, timeout, url=None, llm_only=False, retries=0):
        if llm_only:
            return {
                "ok": True,
                "returncode": 0,
                "payload": {
                    "source": "LLM",
                    "response": "baseline",
                    "route": {
                        "action": "ollama_chat",
                        "phuc_decision": {"decision": "llm", "profile": "imo", "reason": "llm-only"},
                    },
                },
            }
        return {
            "ok": True,
            "returncode": 0,
            "payload": {
                "source": "CPU",
                "response": (
                    "2^(2024-factors) with 2024 prime factors and empty and property holds "
                    "and ∠YPX + ∠KIL = 180 and monochromatic triangle with one color "
                    "and f(x)=x identity function"
                ),
                "route": {
                    "action": "phuc_swarms_benchmark",
                    "phuc_decision": {"decision": "tool", "profile": "imo", "reason": "matched route"},
                },
            },
        }

    monkeypatch.setattr(cli_mod, "_run_twin_subprocess", _fake_twin)

    rc = main(
        [
            "imo-phuc",
            "--cases-file",
            str(cases_path),
            "--run-id",
            run_id,
            "--json",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["strict_pass"] is True
    assert payload["tool_assisted_score"] == payload["total_cases"]
    assert payload["llm_only_score"] <= payload["total_cases"]
    memory = payload.get("memory_loop", {})
    assert isinstance(memory, dict)
    assert "ledger" in memory
    assert "board_json" in memory
    assert "board_md" in memory

    root = Path(__file__).resolve().parents[2]
    out_dir = root / "artifacts" / "imo_phuc" / run_id
    assert out_dir.exists()
    assert (out_dir / "REPORT.json").exists()
    assert (out_dir / "REPORT.md").exists()
    ledger_path = root / str(memory["ledger"])
    board_json_path = root / str(memory["board_json"])
    board_md_path = root / str(memory["board_md"])
    assert ledger_path.exists()
    assert board_json_path.exists()
    assert board_md_path.exists()
    assert f"\"run_id\": \"{run_id}\"" in ledger_path.read_text(encoding="utf-8")
    for case in payload["rows"]:
        case_dir = Path(case["artifact_dir"])
        assert (case_dir / "SCOUT_REPORT.json").exists()
        assert (case_dir / "FORECAST_MEMO.json").exists()
        assert (case_dir / "DECISION_RECORD.json").exists()
        assert (case_dir / "ACT_RESULT.json").exists()
        assert (case_dir / "SKEPTIC_VERDICT.json").exists()


def test_imo_phuc_no_strict_override(monkeypatch, capsys) -> None:
    from stillwater import cli as cli_mod

    cases_path = Path(__file__).resolve().parent / "math" / "imo_qa_cases.json"

    def _fake_fail(*, root, prompt, model, timeout, url=None, llm_only=False, retries=0):
        if llm_only:
            return {
                "ok": True,
                "returncode": 0,
                "payload": {
                    "source": "LLM",
                    "response": "baseline",
                    "route": {"action": "ollama_chat", "phuc_decision": {"decision": "llm", "profile": "imo"}},
                },
            }
        return {
            "ok": True,
            "returncode": 0,
            "payload": {
                "source": "CPU",
                "response": "wrong answer",
                "route": {
                    "action": "phuc_swarms_benchmark",
                    "phuc_decision": {"decision": "tool", "profile": "imo"},
                },
            },
        }

    monkeypatch.setattr(cli_mod, "_run_twin_subprocess", _fake_fail)

    rc_strict = main(["imo-phuc", "--cases-file", str(cases_path), "--run-id", "test-imo-phuc-fail", "--json"])
    out_strict = json.loads(capsys.readouterr().out)
    assert out_strict["strict_pass"] is False
    assert rc_strict == 1

    rc_nonstrict = main(
        [
            "imo-phuc",
            "--cases-file",
            str(cases_path),
            "--run-id",
            "test-imo-phuc-fail-nonstrict",
            "--no-strict",
            "--json",
        ]
    )
    out_nonstrict = json.loads(capsys.readouterr().out)
    assert out_nonstrict["strict_pass"] is False
    assert rc_nonstrict == 0


def test_imo_history_bench_writes_phuc_phase_artifacts(monkeypatch, capsys, tmp_path) -> None:
    from stillwater import cli as cli_mod
    captured: dict[str, str] = {}
    oracle_path = tmp_path / "oracles.json"
    oracle_path.write_text(
        json.dumps(
            {
                "version": 1,
                "cases": [
                    {
                        "year": 2024,
                        "problem_id": "P1",
                        "needle": "constructive argument",
                        "aliases": ["constructive proof"],
                        "concepts": ["constructive", "sequence"],
                        "required_sections": ["assumptions", "core idea", "verification checklist"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    def _fake_dataset(root, year, lang):
        return {
            "year": int(year),
            "lang": str(lang),
            "problems": [
                {
                    "id": "P1",
                    "statement": "Let n be positive. Provide a constructive argument outline.",
                }
            ],
        }

    def _fake_twin(*, root, prompt, model, timeout, url=None, llm_only=False, retries=0):
        if not captured.get("prompt"):
            captured["prompt"] = str(prompt)
        return {
            "ok": True,
            "returncode": 0,
            "payload": {
                "source": "LLM" if llm_only else "CPU",
                "response": "assumptions, core idea, verification checklist",
                "route": {
                    "action": "ollama_chat" if llm_only else "phuc_swarms_benchmark",
                    "phuc_decision": {
                        "decision": "llm" if llm_only else "tool",
                        "profile": "math" if llm_only else "imo",
                        "reason": "test-double",
                    },
                },
            },
        }

    monkeypatch.setattr(cli_mod, "_load_cached_imo_year_dataset", _fake_dataset)
    monkeypatch.setattr(cli_mod, "_run_twin_subprocess", _fake_twin)

    rc = main(
        [
            "imo-history",
            "bench",
            "--from-year",
            "2024",
            "--to-year",
            "2024",
            "--max-problems",
            "1",
            "--oracles-file",
            str(oracle_path),
            "--json",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["strict_ok"] is True
    assert payload["total_cases"] == 1
    assert payload["ok_cases"] == 1
    assert payload["phuc_phase_counts"]["PASS"] == 1
    memory = payload.get("memory_loop", {})
    assert isinstance(memory, dict)
    root = Path(__file__).resolve().parents[2]
    assert (root / str(memory["ledger"])).exists()
    assert (root / str(memory["board_json"])).exists()
    assert (root / str(memory["board_md"])).exists()
    row = payload["rows"][0]
    assert row["phuc_status"] == "PASS"
    case_dir = Path(row["artifact_dir"])
    assert (case_dir / "SCOUT_REPORT.json").exists()
    assert (case_dir / "FORECAST_MEMO.json").exists()
    assert (case_dir / "DECISION_RECORD.json").exists()
    assert (case_dir / "ACT_RESULT.json").exists()
    assert (case_dir / "SKEPTIC_VERDICT.json").exists()
    assert "Solve this problem with a rigorous outline." in captured.get("prompt", "")
    assert "Oracle anchor: constructive argument" in captured.get("prompt", "")
    assert "Oracle concepts: constructive, sequence" in captured.get("prompt", "")
    assert "Return: assumptions, core idea, and verification checklist." in captured.get("prompt", "")


def test_imo_history_required_rung_65537_blocks_lower_rung(monkeypatch, capsys, tmp_path) -> None:
    from stillwater import cli as cli_mod

    def _fake_dataset(root, year, lang):
        return {
            "year": int(year),
            "lang": str(lang),
            "problems": [
                {
                    "id": "P1",
                    "statement": "Let n be positive. Provide a constructive argument outline.",
                }
            ],
        }

    def _fake_twin(*, root, prompt, model, timeout, url=None, llm_only=False, retries=0):
        return {
            "ok": True,
            "returncode": 0,
            "payload": {
                "source": "CPU",
                "response": "deterministic benchmark summary without the requested structured headings",
                "route": {
                    "action": "phuc_swarms_benchmark",
                    "phuc_decision": {"decision": "tool", "profile": "imo", "reason": "test-double"},
                },
            },
        }

    monkeypatch.setattr(cli_mod, "_load_cached_imo_year_dataset", _fake_dataset)
    monkeypatch.setattr(cli_mod, "_run_twin_subprocess", _fake_twin)
    empty_oracle_path = tmp_path / "imo_history_oracles.empty.test.json"
    empty_oracle_path.write_text(json.dumps({"version": 1, "cases": []}), encoding="utf-8")

    rc = main(
        [
            "imo-history",
            "bench",
            "--from-year",
            "2024",
            "--to-year",
            "2024",
            "--max-problems",
            "1",
            "--required-rung",
            "65537",
            "--oracles-file",
            str(empty_oracle_path),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert payload["required_rung"] == 65537
    assert payload["strict_ok"] is False
    assert payload["pass_cases"] == 0
    row = payload["rows"][0]
    assert row["phuc_status"] == "FAIL"
    assert row["rung_achieved"] in {641, 274177}


def test_imo_history_65537_requires_oracle_even_with_structured_response(monkeypatch, capsys, tmp_path) -> None:
    from stillwater import cli as cli_mod

    def _fake_dataset(root, year, lang):
        return {
            "year": int(year),
            "lang": str(lang),
            "problems": [
                {
                    "id": "P1",
                    "statement": "Let n be positive. Provide a constructive argument outline.",
                }
            ],
        }

    def _fake_twin(*, root, prompt, model, timeout, url=None, llm_only=False, retries=0):
        return {
            "ok": True,
            "returncode": 0,
            "payload": {
                "source": "CPU",
                "response": (
                    "Assumptions: n is positive. "
                    "Core idea: give a constructive argument. "
                    "Verification checklist: validate each constructive argument step."
                ),
                "route": {
                    "action": "phuc_swarms_benchmark",
                    "phuc_decision": {"decision": "tool", "profile": "imo", "reason": "test-double"},
                },
            },
        }

    monkeypatch.setattr(cli_mod, "_load_cached_imo_year_dataset", _fake_dataset)
    monkeypatch.setattr(cli_mod, "_run_twin_subprocess", _fake_twin)
    empty_oracle_path = tmp_path / "imo_history_oracles.empty.test.json"
    empty_oracle_path.write_text(json.dumps({"version": 1, "cases": []}), encoding="utf-8")

    rc = main(
        [
            "imo-history",
            "bench",
            "--from-year",
            "2024",
            "--to-year",
            "2024",
            "--max-problems",
            "1",
            "--required-rung",
            "65537",
            "--oracles-file",
            str(empty_oracle_path),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 1
    row = payload["rows"][0]
    assert row["phuc_status"] == "FAIL"
    assert row["rung_achieved"] == 274177
    assert row["oracle_available"] is False
    assert any("oracle_guard_65537" in reason for reason in row.get("phuc_fail_reasons", []))


def test_imo_history_65537_passes_with_matching_oracle(monkeypatch, capsys, tmp_path) -> None:
    from stillwater import cli as cli_mod

    def _fake_dataset(root, year, lang):
        return {
            "year": int(year),
            "lang": str(lang),
            "problems": [
                {
                    "id": "P1",
                    "statement": "Let n be positive. Provide a constructive argument outline.",
                }
            ],
        }

    def _fake_twin(*, root, prompt, model, timeout, url=None, llm_only=False, retries=0):
        return {
            "ok": True,
            "returncode": 0,
            "payload": {
                "source": "CPU",
                "response": (
                    "Assumptions: IMO 2024 P1, let n be positive. "
                    "Core idea: use an extremal reduction, then contradiction on parity drift, then closure by invariant bounds. "
                    "Verification checklist: test boundary witness, parity branch, and contradiction exit conditions. "
                    "Final marker: constructive argument validated."
                ),
                "route": {
                    "action": "phuc_swarms_benchmark",
                    "phuc_decision": {"decision": "tool", "profile": "imo", "reason": "test-double"},
                },
            },
        }

    oracle_path = tmp_path / "oracles.json"
    oracle_path.write_text(
        json.dumps(
            {
                "version": 1,
                "cases": [
                    {
                        "year": 2024,
                        "problem_id": "P1",
                        "needle": "constructive argument validated",
                        "aliases": ["constructive argument"],
                        "concepts": ["constructive argument", "invariant"],
                        "required_sections": ["assumptions", "core idea", "verification checklist"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli_mod, "_load_cached_imo_year_dataset", _fake_dataset)
    monkeypatch.setattr(cli_mod, "_run_twin_subprocess", _fake_twin)

    rc = main(
        [
            "imo-history",
            "bench",
            "--from-year",
            "2024",
            "--to-year",
            "2024",
            "--max-problems",
            "1",
            "--required-rung",
            "65537",
            "--oracles-file",
            str(oracle_path),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["strict_ok"] is True
    assert payload["oracles_loaded"] == 1
    row = payload["rows"][0]
    assert row["phuc_status"] == "PASS"
    assert row["rung_achieved"] == 65537
    assert row["oracle_available"] is True
    assert row["oracle_pass_65537"] is True
    assert row["oracle_concept_pass_65537"] is True
    assert row["oracle_required_sections_pass_65537"] is True
    assert row["oracle_concept_coverage"] == 1.0
    assert row["oracle_required_section_hits"] == 3
    assert row["anti_parrot_pass_65537"] is True
    assert row["oracle_quality_pass_65537"] is True


def test_imo_history_65537_fails_on_parroted_response(monkeypatch, capsys, tmp_path) -> None:
    from stillwater import cli as cli_mod

    def _fake_dataset(root, year, lang):
        return {
            "year": int(year),
            "lang": str(lang),
            "problems": [
                {
                    "id": "P1",
                    "statement": "Let n be positive. Provide a constructive argument outline.",
                }
            ],
        }

    def _fake_twin(*, root, prompt, model, timeout, url=None, llm_only=False, retries=0):
        return {
            "ok": True,
            "returncode": 0,
            "payload": {
                "source": "CPU",
                "response": (
                    "Assumptions: solve this problem with a rigorous outline and constructive argument. "
                    "Core idea: solve this problem with a rigorous outline and constructive argument with invariant. "
                    "Verification checklist: solve this problem with a rigorous outline and constructive argument checks. "
                    "Final marker: constructive argument validated."
                ),
                "route": {
                    "action": "phuc_swarms_benchmark",
                    "phuc_decision": {"decision": "tool", "profile": "imo", "reason": "test-double"},
                },
            },
        }

    oracle_path = tmp_path / "oracles.json"
    oracle_path.write_text(
        json.dumps(
            {
                "version": 1,
                "cases": [
                    {
                        "year": 2024,
                        "problem_id": "P1",
                        "needle": "constructive argument validated",
                        "aliases": ["constructive argument"],
                        "concepts": ["constructive argument", "invariant"],
                        "required_sections": ["assumptions", "core idea", "verification checklist"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli_mod, "_load_cached_imo_year_dataset", _fake_dataset)
    monkeypatch.setattr(cli_mod, "_run_twin_subprocess", _fake_twin)

    rc = main(
        [
            "imo-history",
            "bench",
            "--from-year",
            "2024",
            "--to-year",
            "2024",
            "--max-problems",
            "1",
            "--required-rung",
            "65537",
            "--oracles-file",
            str(oracle_path),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 1
    row = payload["rows"][0]
    assert row["phuc_status"] == "FAIL"
    assert row["rung_achieved"] == 274177
    assert row["anti_parrot_pass_65537"] is False
    fail_reasons = row.get("phuc_fail_reasons", [])
    assert any("anti_parrot_guard_65537" in reason for reason in fail_reasons)


def test_imo_history_274177_fails_when_oracle_concepts_sections_missing(monkeypatch, capsys, tmp_path) -> None:
    from stillwater import cli as cli_mod

    def _fake_dataset(root, year, lang):
        return {
            "year": int(year),
            "lang": str(lang),
            "problems": [
                {
                    "id": "P1",
                    "statement": "Let n be positive. Provide a constructive argument outline.",
                }
            ],
        }

    def _fake_twin(*, root, prompt, model, timeout, url=None, llm_only=False, retries=0):
        return {
            "ok": True,
            "returncode": 0,
            "payload": {
                "source": "CPU",
                "response": (
                    "Assumptions: n is positive. "
                    "Core idea: give a constructive argument. "
                    "Verification checklist: validate each constructive argument step. "
                    "Final marker: constructive argument validated."
                ),
                "route": {
                    "action": "phuc_swarms_benchmark",
                    "phuc_decision": {"decision": "tool", "profile": "imo", "reason": "test-double"},
                },
            },
        }

    oracle_path = tmp_path / "oracles.json"
    oracle_path.write_text(
        json.dumps(
            {
                "version": 1,
                "cases": [
                    {
                        "year": 2024,
                        "problem_id": "P1",
                        "needle": "",
                        "aliases": [],
                        "concepts": ["invariant"],
                        "required_sections": ["counterexample analysis"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli_mod, "_load_cached_imo_year_dataset", _fake_dataset)
    monkeypatch.setattr(cli_mod, "_run_twin_subprocess", _fake_twin)

    rc = main(
        [
            "imo-history",
            "bench",
            "--from-year",
            "2024",
            "--to-year",
            "2024",
            "--max-problems",
            "1",
            "--required-rung",
            "274177",
            "--oracles-file",
            str(oracle_path),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 1
    row = payload["rows"][0]
    assert row["phuc_status"] == "FAIL"
    assert row["rung_achieved"] == 641
    assert row["oracle_concept_pass_274177"] is False
    assert row["oracle_required_sections_pass_274177"] is False
    fail_reasons = row.get("phuc_fail_reasons", [])
    assert any("concept_guard_274177" in reason for reason in fail_reasons)
    assert any("section_guard_274177" in reason for reason in fail_reasons)


def test_imo_history_oracles_template_generation_and_merge(monkeypatch, capsys, tmp_path) -> None:
    from stillwater import cli as cli_mod

    def _fake_dataset(root, year, lang):
        return {
            "year": int(year),
            "lang": str(lang),
            "problems": [
                {
                    "id": "P1",
                    "statement": "Given n, prove a constructive argument for a sequence.",
                }
            ],
        }

    monkeypatch.setattr(cli_mod, "_load_cached_imo_year_dataset", _fake_dataset)

    out_path = tmp_path / "imo_history_oracles.generated.json"
    rc = main(
        [
            "imo-history",
            "oracles-template",
            "--from-year",
            "2024",
            "--to-year",
            "2024",
            "--out",
            str(out_path),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["cases_written"] == 1
    generated = json.loads(out_path.read_text(encoding="utf-8"))
    assert len(generated["cases"]) == 1
    row = generated["cases"][0]
    assert row["year"] == 2024
    assert row["problem_id"] == "P1"
    assert row["needle"] == ""
    assert isinstance(row.get("statement_excerpt"), str)

    out_path.write_text(
        json.dumps(
            {
                "version": 1,
                "description": "seeded",
                "cases": [
                    {
                        "year": 2024,
                        "problem_id": "P1",
                        "needle": "seeded-oracle",
                        "aliases": ["seed-alias"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    rc_merge = main(
        [
            "imo-history",
            "oracles-template",
            "--from-year",
            "2024",
            "--to-year",
            "2024",
            "--out",
            str(out_path),
            "--json",
        ]
    )
    _ = capsys.readouterr().out
    assert rc_merge == 0
    merged = json.loads(out_path.read_text(encoding="utf-8"))
    assert merged["cases"][0]["needle"] == "seeded-oracle"
    assert "seed-alias" in merged["cases"][0].get("aliases", [])

    rc_overwrite = main(
        [
            "imo-history",
            "oracles-template",
            "--from-year",
            "2024",
            "--to-year",
            "2024",
            "--out",
            str(out_path),
            "--no-merge-existing",
            "--json",
        ]
    )
    _ = capsys.readouterr().out
    assert rc_overwrite == 0
    overwritten = json.loads(out_path.read_text(encoding="utf-8"))
    assert overwritten["cases"][0]["needle"] == ""


def test_imo_history_oracle_status_reports_coverage(monkeypatch, capsys, tmp_path) -> None:
    from stillwater import cli as cli_mod

    def _fake_dataset(root, year, lang):
        return {
            "year": int(year),
            "lang": str(lang),
            "problems": [
                {"id": "P1", "statement": "Given n, prove constructive argument."},
                {"id": "P2", "statement": "Find all integers satisfying condition."},
            ],
        }

    oracle_path = tmp_path / "oracles.json"
    oracle_path.write_text(
        json.dumps(
            {
                "version": 1,
                "cases": [
                    {
                        "year": 2024,
                        "problem_id": "P1",
                        "needle": "constructive argument",
                        "aliases": ["constructive proof"],
                        "concepts": ["constructive"],
                        "required_sections": ["assumptions"],
                    },
                    {
                        "year": 2024,
                        "problem_id": "P2",
                        "needle": "",
                        "aliases": [],
                        "concepts": ["invariant"],
                        "required_sections": ["verification checklist"],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cli_mod, "_load_cached_imo_year_dataset", _fake_dataset)

    rc = main(
        [
            "imo-history",
            "oracle-status",
            "--from-year",
            "2024",
            "--to-year",
            "2024",
            "--oracles-file",
            str(oracle_path),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["ok"] is True
    assert payload["total_problems"] == 2
    assert payload["oracle_ready"] == 1
    assert payload["oracle_missing"] == 1
    assert payload["with_concepts"] == 2
    assert payload["with_required_sections"] == 2
    assert payload["ready_ratio"] == 0.5
    assert payload["oracle_quality_ready"] == 0
    assert payload["oracle_quality_strong"] == 0
    assert payload["quality_ready_ratio"] == 0.0
    assert payload["per_year"]["2024"]["ready"] == 1
    assert payload["per_year"]["2024"]["missing"] == 1
    assert payload["per_year"]["2024"]["quality_ready"] == 0


def test_imo_history_bench_defaults_blank_llm_profile_to_math(monkeypatch, capsys) -> None:
    from stillwater import cli as cli_mod

    def _fake_dataset(root, year, lang):
        return {
            "year": int(year),
            "lang": str(lang),
            "problems": [
                {
                    "id": "P1",
                    "statement": "Let n be positive. Provide a constructive argument outline.",
                }
            ],
        }

    def _fake_twin(*, root, prompt, model, timeout, url=None, llm_only=False, retries=0):
        return {
            "ok": True,
            "returncode": 0,
            "payload": {
                "source": "LLM",
                "response": "Assumptions, core idea, verification checklist.",
                "route": {
                    "action": "ollama_chat",
                    "phuc_decision": {"decision": "llm", "profile": "", "reason": "fallback"},
                },
            },
        }

    monkeypatch.setattr(cli_mod, "_load_cached_imo_year_dataset", _fake_dataset)
    monkeypatch.setattr(cli_mod, "_run_twin_subprocess", _fake_twin)

    rc = main(
        [
            "imo-history",
            "bench",
            "--from-year",
            "2024",
            "--to-year",
            "2024",
            "--max-problems",
            "1",
            "--required-rung",
            "641",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    row = payload["rows"][0]
    assert row["action"] == "ollama_chat"
    assert row["source"] == "LLM"
    assert row["profile"] == "math"
    assert payload["route_counts"]["LLM::ollama_chat::math"] == 1


def test_imo_phuc_rejects_invalid_required_rung(capsys) -> None:
    rc = main(["imo-phuc", "--required-rung", "999"])
    assert rc == 1
    assert "--required-rung must be one of 641, 274177, 65537" in capsys.readouterr().out


def test_imo_history_autolearn_applies_improved_oracles(monkeypatch, capsys, tmp_path) -> None:
    from stillwater import cli as cli_mod

    oracle_path = tmp_path / "imo_history_oracles.json"
    oracle_path.write_text(json.dumps({"version": 1, "cases": []}), encoding="utf-8")

    def _fake_dataset(root, year, lang):
        return {
            "year": int(year),
            "lang": str(lang),
            "problems": [
                {
                    "id": "P1",
                    "statement": "Given n, provide a constructive argument for the sequence claim.",
                }
            ],
        }

    call_count = {"n": 0}

    def _fake_subprocess_run(cmd, cwd=None, env=None, text=True, capture_output=True, check=False):
        call_count["n"] += 1
        assert "imo-history" in cmd and "bench" in cmd
        if call_count["n"] == 1:
            payload = {
                "run_id": "bench-1",
                "strict_ok": False,
                "total_cases": 1,
                "ok_cases": 1,
                "pass_cases": 0,
                "oracle_configured_cases": 0,
                "oracle_pass_cases": 0,
                "oracle_quality_ready_cases": 0,
                "artifact_dir": str(tmp_path / "bench-1"),
                "rows": [
                    {
                        "year": 2024,
                        "problem_id": "P1",
                        "phuc_status": "FAIL",
                        "oracle_available": False,
                        "oracle_quality_ready": False,
                        "response_text": (
                            "Assumptions: case context.\n"
                            "Core idea: use invariant and case split.\n"
                            "Verification checklist: verify boundary cases.\n"
                            "Final claim:\n- constructive argument validated sequence claim"
                        ),
                    }
                ],
            }
            return SimpleNamespace(returncode=1, stdout=json.dumps(payload), stderr="")
        payload = {
            "run_id": "bench-2",
            "strict_ok": True,
            "total_cases": 1,
            "ok_cases": 1,
            "pass_cases": 1,
            "oracle_configured_cases": 1,
            "oracle_pass_cases": 1,
            "oracle_quality_ready_cases": 1,
            "artifact_dir": str(tmp_path / "bench-2"),
            "rows": [
                {
                    "year": 2024,
                    "problem_id": "P1",
                    "phuc_status": "PASS",
                    "oracle_available": True,
                    "oracle_quality_ready": True,
                    "response_text": "Final claim: constructive argument validated sequence claim",
                }
            ],
        }
        return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(cli_mod, "_load_cached_imo_year_dataset", _fake_dataset)
    monkeypatch.setattr(cli_mod.subprocess, "run", _fake_subprocess_run)

    rc = main(
        [
            "imo-history",
            "autolearn",
            "--from-year",
            "2024",
            "--to-year",
            "2024",
            "--max-problems",
            "1",
            "--max-iterations",
            "2",
            "--oracles-file",
            str(oracle_path),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["improved"] is True
    assert payload["applied"] is True
    assert payload["best_iteration"] == 2
    learned = json.loads(oracle_path.read_text(encoding="utf-8"))
    assert isinstance(learned.get("cases"), list) and learned["cases"]
    row = learned["cases"][0]
    assert row["year"] == 2024
    assert row["problem_id"] == "P1"
    assert str(row.get("needle", "")).strip() != ""


def test_imo_history_autolearn_fail_closed_when_not_improved(monkeypatch, capsys, tmp_path) -> None:
    from stillwater import cli as cli_mod

    oracle_path = tmp_path / "imo_history_oracles.json"
    original_payload = {"version": 1, "cases": []}
    oracle_path.write_text(json.dumps(original_payload), encoding="utf-8")

    def _fake_dataset(root, year, lang):
        return {
            "year": int(year),
            "lang": str(lang),
            "problems": [{"id": "P1", "statement": "Given n, provide a constructive argument."}],
        }

    def _fake_subprocess_run(cmd, cwd=None, env=None, text=True, capture_output=True, check=False):
        payload = {
            "run_id": "bench-static",
            "strict_ok": False,
            "total_cases": 1,
            "ok_cases": 1,
            "pass_cases": 0,
            "oracle_configured_cases": 0,
            "oracle_pass_cases": 0,
            "oracle_quality_ready_cases": 0,
            "artifact_dir": str(tmp_path / "bench-static"),
            "rows": [
                {
                    "year": 2024,
                    "problem_id": "P1",
                    "phuc_status": "FAIL",
                    "oracle_available": False,
                    "oracle_quality_ready": False,
                    "response_text": "Final claim: constructive argument validated",
                }
            ],
        }
        return SimpleNamespace(returncode=1, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(cli_mod, "_load_cached_imo_year_dataset", _fake_dataset)
    monkeypatch.setattr(cli_mod.subprocess, "run", _fake_subprocess_run)

    rc = main(
        [
            "imo-history",
            "autolearn",
            "--from-year",
            "2024",
            "--to-year",
            "2024",
            "--max-problems",
            "1",
            "--max-iterations",
            "2",
            "--oracles-file",
            str(oracle_path),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert payload["improved"] is False
    assert payload["applied"] is False
    assert json.loads(oracle_path.read_text(encoding="utf-8")) == original_payload


def test_math_universal_gate_passes_when_all_requirements_pass(monkeypatch, capsys, tmp_path) -> None:
    from stillwater import cli as cli_mod

    proof_cases = tmp_path / "proof_cases.json"
    proof_cases.write_text(
        json.dumps(
            {
                "version": 1,
                "cases": [
                    {"id": "expr", "kind": "expr_equals", "expr": "2 + 3 * 4", "expected": 14},
                    {"id": "gcd", "kind": "gcd", "a": 123456, "b": 7890, "expected": 6},
                ],
            }
        ),
        encoding="utf-8",
    )
    empty_oracles = tmp_path / "empty_oracles.json"
    empty_oracles.write_text(json.dumps({"version": 1, "cases": []}), encoding="utf-8")

    cfg_path = tmp_path / "universal.json"
    cfg_path.write_text(
        json.dumps(
            {
                "version": 1,
                "defaults": {
                    "lang": "eng",
                    "model": "llama3.1:8b",
                    "timeout": 45.0,
                    "max_problems": 0,
                    "fetch_missing": False,
                },
                "heldout_profiles": [
                    {
                        "label": "heldout",
                        "from_year": 2024,
                        "to_year": 2024,
                        "required_rung": 65537,
                        "oracles_file": str(empty_oracles),
                        "min_pass_ratio": 1.0,
                        "require_strict": True,
                    }
                ],
                "proof_artifacts": {
                    "required": True,
                    "cases_file": str(proof_cases),
                    "required_min_pass_ratio": 1.0,
                },
                "generalization_profiles": [
                    {
                        "label": "gen",
                        "from_year": 2024,
                        "to_year": 2024,
                        "required_rung": 641,
                        "oracles_file": str(empty_oracles),
                        "min_pass_ratio": 0.5,
                        "require_strict": False,
                    }
                ],
                "stability": {
                    "profile": {
                        "label": "stable",
                        "from_year": 2024,
                        "to_year": 2024,
                        "required_rung": 641,
                        "oracles_file": str(empty_oracles),
                        "min_pass_ratio": 0.5,
                        "require_strict": False,
                    },
                    "models": ["llama3.1:8b", "qwen2.5-coder:7b"],
                    "urls": ["", "http://fake-ollama:11434"],
                    "required_all": True,
                },
            }
        ),
        encoding="utf-8",
    )

    def _fake_bench(
        *,
        root,
        from_year,
        to_year,
        lang,
        model,
        url,
        timeout,
        max_problems,
        oracles_file,
        required_rung,
        fetch_missing,
        llm_only=False,
    ):
        return {
            "ok": True,
            "report": {
                "run_id": f"bench-{required_rung}",
                "strict_ok": True,
                "total_cases": 4,
                "pass_cases": 4,
                "artifact_dir": str(tmp_path / f"bench-{required_rung}"),
            },
        }

    monkeypatch.setattr(cli_mod, "_run_imo_history_bench_subprocess", _fake_bench)

    rc = main(["math-universal", "--config", str(cfg_path), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["overall_ok"] is True
    assert payload["universal_claim_ready"] is True
    assert payload["gates"]["heldout"]["ok"] is True
    assert payload["gates"]["proof_artifacts"]["ok"] is True
    assert payload["gates"]["generalization"]["ok"] is True
    assert payload["gates"]["stability"]["ok"] is True
    assert len(payload["gates"]["stability"]["rows"]) == 2


def test_math_universal_gate_fails_on_proof_artifacts(monkeypatch, capsys, tmp_path) -> None:
    from stillwater import cli as cli_mod

    proof_cases = tmp_path / "proof_cases_fail.json"
    proof_cases.write_text(
        json.dumps(
            {
                "version": 1,
                "cases": [{"id": "expr", "kind": "expr_equals", "expr": "2 + 2", "expected": 5}],
            }
        ),
        encoding="utf-8",
    )
    empty_oracles = tmp_path / "empty_oracles.json"
    empty_oracles.write_text(json.dumps({"version": 1, "cases": []}), encoding="utf-8")

    cfg_path = tmp_path / "universal_fail.json"
    cfg_path.write_text(
        json.dumps(
            {
                "version": 1,
                "defaults": {"lang": "eng", "model": "llama3.1:8b", "timeout": 45.0, "fetch_missing": False},
                "heldout_profiles": [
                    {
                        "label": "heldout",
                        "from_year": 2024,
                        "to_year": 2024,
                        "required_rung": 65537,
                        "oracles_file": str(empty_oracles),
                        "min_pass_ratio": 1.0,
                        "require_strict": True,
                    }
                ],
                "proof_artifacts": {
                    "required": True,
                    "cases_file": str(proof_cases),
                    "required_min_pass_ratio": 1.0,
                },
                "generalization_profiles": [
                    {
                        "label": "gen",
                        "from_year": 2024,
                        "to_year": 2024,
                        "required_rung": 641,
                        "oracles_file": str(empty_oracles),
                        "min_pass_ratio": 0.5,
                        "require_strict": False,
                    }
                ],
                "stability": {
                    "profile": {
                        "label": "stable",
                        "from_year": 2024,
                        "to_year": 2024,
                        "required_rung": 641,
                        "oracles_file": str(empty_oracles),
                        "min_pass_ratio": 0.5,
                        "require_strict": False,
                    },
                    "models": ["llama3.1:8b"],
                    "urls": [],
                    "required_all": True,
                },
            }
        ),
        encoding="utf-8",
    )

    def _fake_bench(
        *,
        root,
        from_year,
        to_year,
        lang,
        model,
        url,
        timeout,
        max_problems,
        oracles_file,
        required_rung,
        fetch_missing,
        llm_only=False,
    ):
        return {
            "ok": True,
            "report": {
                "run_id": "bench",
                "strict_ok": True,
                "total_cases": 4,
                "pass_cases": 4,
                "artifact_dir": str(tmp_path / "bench"),
            },
        }

    monkeypatch.setattr(cli_mod, "_run_imo_history_bench_subprocess", _fake_bench)

    rc = main(["math-universal", "--config", str(cfg_path), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert payload["overall_ok"] is False
    assert payload["gates"]["proof_artifacts"]["ok"] is False
    assert payload["gates"]["heldout"]["ok"] is True
