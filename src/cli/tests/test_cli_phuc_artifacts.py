from __future__ import annotations

import json
from pathlib import Path

import pytest

from stillwater.cli import _load_json, main


def _imo_prompt_by_id(case_id: str) -> str:
    path = Path(__file__).resolve().parent / "math" / "imo_qa_cases.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("cases", []) if isinstance(payload, dict) else []
    for row in rows:
        if isinstance(row, dict) and str(row.get("id", "")).strip() == case_id:
            prompt = str(row.get("prompt", "")).strip()
            if prompt:
                return prompt
    raise AssertionError(f"Missing IMO case id in config: {case_id}")


def test_phuc_benchmark_artifacts_have_required_phase_files(capsys) -> None:
    rc = main(["twin", _imo_prompt_by_id("P5"), "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["route"]["action"] == "phuc_swarms_benchmark"
    if "benchmark solver failed" in str(payload.get("response", "")).lower():
        pytest.skip("phuc benchmark solver unavailable in this environment")

    out_dir = Path(payload["route"]["artifact_dir"])
    assert out_dir.exists()

    required = [
        "SWARM_SETTINGS.json",
        "ORCHESTRATION_DECISION.json",
        "CNF_BASE.json",
        "CNF_DELTA.scout.json",
        "CNF_DELTA.forecast.json",
        "CNF_DELTA.decide.json",
        "CNF_DELTA.solver.json",
        "CNF_DELTA.skeptic.json",
        "SCOUT_REPORT.json",
        "FORECAST_MEMO.json",
        "DECISION_RECORD.json",
        "PATCH_NOTES.json",
        "PATCH_PROPOSAL.diff",
        "SKEPTIC_VERDICT.json",
        "EDGECASE_REPORT.json",
        "PRIME_CHANNELS.jsonl",
    ]
    for name in required:
        assert (out_dir / name).exists(), name

    cnf_base = _load_json(out_dir / "CNF_BASE.json")
    assert cnf_base.get("phase_order")
    assert cnf_base.get("personas")
    assert cnf_base.get("skill_pack")
    assert cnf_base.get("mandatory_skill_pack")
    assert cnf_base.get("agent_skill_pack")
    assert cnf_base.get("recipe_pack")
    assert cnf_base.get("agent_recipe_pack")
    assert "prime-coder.md" in cnf_base.get("mandatory_skill_pack", [])
    assert "prime-math.md" in cnf_base.get("mandatory_skill_pack", [])

    cnf_delta_solver = _load_json(out_dir / "CNF_DELTA.solver.json")
    solver_skills = cnf_delta_solver.get("skill_pack", [])
    assert "prime-coder.md" in solver_skills
    assert "prime-math.md" in solver_skills

    swarm = _load_json(out_dir / "SWARM_SETTINGS.json")
    assert swarm.get("phase_order")
    assert swarm.get("personas")
    assert swarm.get("skill_pack")
    assert swarm.get("mandatory_skill_pack")
    assert swarm.get("agent_skill_pack")
    assert swarm.get("recipe_pack")
    assert swarm.get("agent_recipe_pack")

    orchestration = _load_json(out_dir / "ORCHESTRATION_DECISION.json")
    assert orchestration.get("decision") == "tool"
    assert orchestration.get("profile")

    scout = _load_json(out_dir / "SCOUT_REPORT.json")
    assert {
        "agent",
        "task_summary",
        "repro_command",
        "repro_commands",
        "suspect_files_ranked",
        "acceptance_criteria",
    }.issubset(set(scout.keys()))

    forecast = _load_json(out_dir / "FORECAST_MEMO.json")
    assert {"top_failure_modes_ranked", "stop_rules", "edge_cases_to_test", "compat_risks", "mitigations"}.issubset(
        set(forecast.keys())
    )

    decision = _load_json(out_dir / "DECISION_RECORD.json")
    assert {"chosen_approach", "alternatives_considered", "scope_locked", "required_verification_rung"}.issubset(
        set(decision.keys())
    )

    skeptic = _load_json(out_dir / "SKEPTIC_VERDICT.json")
    assert {"status", "rung_achieved", "evidence"}.issubset(set(skeptic.keys()))


def test_phuc_benchmark_agent_skill_pack_configurable(tmp_path: Path, monkeypatch, capsys) -> None:
    custom_swarm = tmp_path / "custom-swarm.prime-mermaid.md"
    custom_swarm.write_text(
        "\n".join(
            [
                "# custom swarm for unit test",
                "SETTING phase_order = DREAM,FORECAST,DECIDE,ACT,VERIFY",
                "SETTING mandatory_skill_pack = prime-safety.md,prime-coder.md,prime-math.md,phuc-context.md",
                "SETTING skill_pack = phuc-swarms.md,phuc-forecast.md",
                "SETTING agent_skill_policy = replace",
                "SETTING agent_skill_pack.solver = custom-solver.md,prime-math.md",
                "SETTING agent_skill_pack.skeptic = custom-skeptic.md",
                "SETTING recipe_pack = recipe.twin_orchestration.prime-mermaid.md",
                "SETTING agent_recipe_policy = replace",
                "SETTING agent_recipe_pack.solver = recipe.dojo_checkin.prime-mermaid.md",
                "SETTING context_mode = anti_rot_fresh_context_per_phase",
                "SETTING artifact_mode = machine_parseable_receipts_required",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("STILLWATER_SWARM_SETTINGS_FILE", str(custom_swarm))

    rc = main(["twin", _imo_prompt_by_id("P5"), "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["route"]["action"] == "phuc_swarms_benchmark"

    out_dir = Path(payload["route"]["artifact_dir"])
    swarm = _load_json(out_dir / "SWARM_SETTINGS.json")
    assert swarm.get("agent_skill_policy") == "replace"
    assert swarm.get("agent_recipe_policy") == "replace"
    solver_swarm_skills = swarm.get("agent_skill_pack", {}).get("solver", [])
    assert "custom-solver.md" in solver_swarm_skills

    cnf_delta_solver = _load_json(out_dir / "CNF_DELTA.solver.json")
    cnf_delta_skeptic = _load_json(out_dir / "CNF_DELTA.skeptic.json")
    solver_skills = cnf_delta_solver.get("skill_pack", [])
    skeptic_skills = cnf_delta_skeptic.get("skill_pack", [])
    assert "prime-coder.md" in solver_skills
    assert "prime-math.md" in solver_skills
    assert "custom-solver.md" in solver_skills
    assert "phuc-swarms.md" not in solver_skills
    assert "custom-skeptic.md" in skeptic_skills

    solver_recipes = cnf_delta_solver.get("recipe_pack", [])
    assert "recipe.dojo_checkin.prime-mermaid.md" in solver_recipes
    assert "recipe.twin_orchestration.prime-mermaid.md" not in solver_recipes
