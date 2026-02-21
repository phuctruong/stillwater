from __future__ import annotations

from stillwater.cli import _expand_semantic_aliases, _imo_phuc_eval_lane, _math_expert_council_config, _semantic_match_score


def _fake_run(response: str) -> dict:
    return {
        "ok": True,
        "returncode": 0,
        "payload": {
            "source": "CPU",
            "response": response,
            "route": {
                "action": "phuc_swarms_benchmark",
                "phuc_decision": {"decision": "tool", "profile": "imo", "reason": "test"},
            },
        },
    }


def test_semantic_match_angle_equivalence() -> None:
    targets = _expand_semantic_aliases("∠YPX + ∠KIL = 180")
    meta = _semantic_match_score("angle ypx + angle kil = 180", targets)
    assert meta["matched"] is True
    assert meta["score"] >= 0.92


def test_semantic_match_monochromatic_alias() -> None:
    targets = _expand_semantic_aliases("monochromatic triangle")
    meta = _semantic_match_score("A same color triangle exists in K6.", targets)
    assert meta["matched"] is True


def test_semantic_match_rejects_unrelated_text() -> None:
    targets = _expand_semantic_aliases("f(x)=x")
    meta = _semantic_match_score("The answer is unclear and does not specify a function.", targets)
    assert meta["matched"] is False
    assert meta["score"] == 0.0


def test_eval_lane_accepts_semantic_alias_match() -> None:
    cfg = _math_expert_council_config(settings={}, default_required_rung=641)
    cfg["required_rung"] = 641
    out = _imo_phuc_eval_lane(
        run=_fake_run("A same color triangle must exist."),
        needle="monochromatic triangle",
        aliases=[],
        lane_name="tool_assisted",
        council_cfg=cfg,
    )
    assert out["match"] is True
    assert out["council"]["status"] == "PASS"


def test_eval_lane_65537_requires_strong_match() -> None:
    cfg = _math_expert_council_config(settings={}, default_required_rung=65537)
    cfg["required_rung"] = 65537
    out = _imo_phuc_eval_lane(
        run=_fake_run("Triangle exists, same color."),
        needle="monochromatic triangle",
        aliases=[],
        lane_name="tool_assisted",
        council_cfg=cfg,
    )
    assert out["match"] is True
    assert out["match_score"] < 0.92
    assert out["council"]["status"] == "FAIL"
    assert out["council"]["rung_achieved"] in {641, 274177}


def test_eval_lane_274177_checks_concept_coverage() -> None:
    cfg = _math_expert_council_config(settings={}, default_required_rung=274177)
    cfg["required_rung"] = 274177
    out = _imo_phuc_eval_lane(
        run=_fake_run("This answer mentions a triangle but not the color property."),
        needle="monochromatic triangle",
        aliases=[],
        concepts=["triangle", "color"],
        lane_name="tool_assisted",
        council_cfg=cfg,
    )
    assert out["match"] is False
    assert out["council"]["status"] == "FAIL"


def test_eval_lane_65537_checks_required_sections() -> None:
    cfg = _math_expert_council_config(settings={}, default_required_rung=65537)
    cfg["required_rung"] = 65537
    out = _imo_phuc_eval_lane(
        run=_fake_run("monochromatic triangle exists, but no structured proof sections are provided"),
        needle="monochromatic triangle",
        aliases=[],
        required_sections=["assumptions", "core idea", "verification checklist"],
        lane_name="tool_assisted",
        council_cfg=cfg,
    )
    assert out["match"] is True
    assert out["council"]["status"] == "FAIL"
