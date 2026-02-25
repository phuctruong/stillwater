from __future__ import annotations

from stillwater.cli import _aggregate_expert_council, _expert_vote


def _cfg(required_rung: int) -> dict:
    return {
        "required_rung": required_rung,
        "threshold_641": 0.5,
        "threshold_274177": 0.5,
        "threshold_65537": 0.5,
        "virtual_size": 65537,
    }


def test_ladder_order_65537_is_stricter_than_274177() -> None:
    votes = [_expert_vote("e1", True, "ok"), _expert_vote("e2", True, "ok")]
    gates = {"r641": True, "r274177": True, "r65537": False}
    out = _aggregate_expert_council(votes=votes, gates=gates, cfg=_cfg(65537))
    assert out["rung_achieved"] == 274177
    assert out["status"] == "FAIL"


def test_ladder_274177_passes_when_achieved() -> None:
    votes = [_expert_vote("e1", True, "ok"), _expert_vote("e2", True, "ok")]
    gates = {"r641": True, "r274177": True, "r65537": False}
    out = _aggregate_expert_council(votes=votes, gates=gates, cfg=_cfg(274177))
    assert out["rung_achieved"] == 274177
    assert out["status"] == "PASS"


def test_ladder_65537_requires_top_gate() -> None:
    votes = [_expert_vote("e1", True, "ok"), _expert_vote("e2", True, "ok")]
    gates = {"r641": True, "r274177": True, "r65537": True}
    out = _aggregate_expert_council(votes=votes, gates=gates, cfg=_cfg(65537))
    assert out["rung_achieved"] == 65537
    assert out["status"] == "PASS"
