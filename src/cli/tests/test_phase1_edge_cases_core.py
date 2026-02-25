from __future__ import annotations

import json
from pathlib import Path

import pytest

from stillwater.cpu_learner import CPULearner


REPO_ROOT = Path(__file__).resolve().parents[3]
PHASE1_SEEDS = REPO_ROOT / "data" / "default" / "seeds" / "small-talk-seeds.jsonl"


def _load_seeded_phase1_learner() -> CPULearner:
    learner = CPULearner("phase1")
    for line in PHASE1_SEEDS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        if record.get("phase") != "phase1":
            continue
        keyword = record["keyword"]
        learner._patterns[keyword] = {
            "count": int(record.get("count", 1)),
            "label": record.get("label", "unknown"),
            "examples": list(record.get("examples", [])),
        }
    return learner


@pytest.fixture()
def phase1_learner() -> CPULearner:
    return _load_seeded_phase1_learner()


@pytest.mark.parametrize(
    ("text", "expected_label"),
    [
        ("", None),
        ("a", None),
        ("?", None),
        ("the the the", None),
        ("12345", None),
        ("...", None),
        ("DEPLOY NOW", "task"),
        ("fix fix fix", "task"),
        ("HELLO THERE", "greeting"),
        ("thanks so much", "gratitude"),
        ("tell me a joke please", "humor"),
        ("weather today", "small_talk"),
        ("I am sad", "emotional_negative"),
        ("I am happy", "emotional_positive"),
        ("create docs", "task"),
        ("refactor the auth module", "task"),
        ("explain architecture", "question"),
        ("clarify deployment steps", "question"),
        ("describe the pipeline", "task"),
        ("understand oauth flow", "question"),
    ],
)
def test_phase1_edge_cases_matrix(
    phase1_learner: CPULearner,
    text: str,
    expected_label: str | None,
) -> None:
    label, confidence, matched = phase1_learner.predict(text)
    if expected_label is None:
        assert label is None
        assert confidence == 0.0
        assert matched == []
    else:
        assert label == expected_label
        assert confidence > 0.0
        assert matched


def test_bug_p1_001_tie_break_prefers_task_order_independent(
    phase1_learner: CPULearner,
) -> None:
    for text in ("hello fix tests", "fix hello tests"):
        label, confidence, _ = phase1_learner.predict(text)
        assert label == "task"
        assert confidence > 0.0


def test_ultra_long_input_with_embedded_task_keyword(
    phase1_learner: CPULearner,
) -> None:
    text = ("x" * 12000) + " fix now"
    label, confidence, matched = phase1_learner.predict(text)
    assert label == "task"
    assert confidence > 0.0
    assert "fix" in matched


@pytest.mark.xfail(reason="BUG-P1-002: what/how/why are filtered as stop words", strict=False)
def test_bug_p1_002_question_words_only_should_route_to_question(
    phase1_learner: CPULearner,
) -> None:
    label, _, _ = phase1_learner.predict("what how why")
    assert label == "question"


@pytest.mark.xfail(reason="BUG-P1-003: ultra-short inputs bypass keyword extraction", strict=False)
def test_bug_p1_003_ultra_short_question_mark_should_route(
    phase1_learner: CPULearner,
) -> None:
    label, _, _ = phase1_learner.predict("?")
    assert label in {"question", "small_talk"}


@pytest.mark.xfail(reason="BUG-P1-005: phase1 seed set is task-biased", strict=False)
def test_bug_p1_005_seed_distribution_should_not_be_task_dominated() -> None:
    task_count = 0
    total = 0
    for line in PHASE1_SEEDS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        total += 1
        if record.get("label") == "task":
            task_count += 1
    assert total > 0
    assert (task_count / total) <= 0.60
