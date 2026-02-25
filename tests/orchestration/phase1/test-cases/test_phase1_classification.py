"""test_phase1_classification.py -- Parametrized tests for all 20 Phase 1 prompts.

Runs each prompt through the real TripleTwinEngine (CPU-only mode, default seeds)
and validates the classification result matches the simulation.

Rung: 641 -- deterministic, no network, no LLM.
"""

from __future__ import annotations

import pytest

from stillwater.triple_twin import TripleTwinEngine

from pathlib import Path
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "phase1_shared", Path(__file__).resolve().with_name("phase1_shared.py")
)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
HAPPY_PATH_INDICES = _mod.HAPPY_PATH_INDICES
PHASE1_DATASET = _mod.PHASE1_DATASET
PHASE1_THRESHOLD = _mod.PHASE1_THRESHOLD
SEED_CONFIDENCE = _mod.SEED_CONFIDENCE


# ---------------------------------------------------------------------------
# Full dataset: all 20 prompts
# ---------------------------------------------------------------------------


class TestPhase1AllPrompts:
    """Parametrized test covering every simulation prompt."""

    @pytest.mark.parametrize(
        "text,expected_label,verdict",
        PHASE1_DATASET,
        ids=[f"prompt-{i+1}" for i in range(len(PHASE1_DATASET))],
    )
    def test_phase1_classification(
        self,
        phase1_engine: TripleTwinEngine,
        text: str,
        expected_label: str,
        verdict: str,
    ) -> None:
        """Verify the engine produces the expected label for each prompt."""
        result = phase1_engine.process(text)
        assert result.phase1 is not None, "Phase 1 should always produce a result"

        actual_label = result.phase1.label
        assert actual_label == expected_label, (
            f"Input: {text!r}\n"
            f"Expected: {expected_label}, Got: {actual_label}\n"
            f"Verdict: {verdict}"
        )

    @pytest.mark.parametrize(
        "text,expected_label,verdict",
        PHASE1_DATASET,
        ids=[f"prompt-{i+1}" for i in range(len(PHASE1_DATASET))],
    )
    def test_phase1_handler_is_cpu(
        self,
        phase1_engine: TripleTwinEngine,
        text: str,
        expected_label: str,
        verdict: str,
    ) -> None:
        """All prompts should be handled by CPU (no LLM client configured)."""
        result = phase1_engine.process(text)
        assert result.phase1 is not None
        assert result.phase1.handled_by == "cpu", (
            f"Input: {text!r} -- expected cpu handler, got {result.phase1.handled_by}"
        )


# ---------------------------------------------------------------------------
# Happy path subset: only prompts with PASS verdict
# ---------------------------------------------------------------------------


# Extract just the happy-path prompts
_HAPPY_PROMPTS = [
    (PHASE1_DATASET[i][0], PHASE1_DATASET[i][1])
    for i in HAPPY_PATH_INDICES
]


class TestPhase1HappyPath:
    """Tests for the 9 happy-path prompts that should classify correctly."""

    @pytest.mark.parametrize(
        "text,expected_label",
        _HAPPY_PROMPTS,
        ids=[f"happy-{i+1}" for i in range(len(_HAPPY_PROMPTS))],
    )
    def test_happy_path_label(
        self,
        phase1_engine: TripleTwinEngine,
        text: str,
        expected_label: str,
    ) -> None:
        """Happy path prompts should match expected label exactly."""
        result = phase1_engine.process(text)
        assert result.phase1 is not None
        assert result.phase1.label == expected_label

    @pytest.mark.parametrize(
        "text,expected_label",
        _HAPPY_PROMPTS,
        ids=[f"happy-{i+1}" for i in range(len(_HAPPY_PROMPTS))],
    )
    def test_happy_path_confidence(
        self,
        phase1_engine: TripleTwinEngine,
        text: str,
        expected_label: str,
    ) -> None:
        """Happy path prompts with seed matches should have confidence ~0.8824."""
        result = phase1_engine.process(text)
        assert result.phase1 is not None
        assert abs(result.phase1.confidence - SEED_CONFIDENCE) < 0.001, (
            f"Input: {text!r}\n"
            f"Expected confidence ~{SEED_CONFIDENCE:.4f}, "
            f"got {result.phase1.confidence:.4f}"
        )

    @pytest.mark.parametrize(
        "text,expected_label",
        _HAPPY_PROMPTS,
        ids=[f"happy-{i+1}" for i in range(len(_HAPPY_PROMPTS))],
    )
    def test_happy_path_above_threshold(
        self,
        phase1_engine: TripleTwinEngine,
        text: str,
        expected_label: str,
    ) -> None:
        """Happy path prompts should have confidence above Phase 1 threshold."""
        result = phase1_engine.process(text)
        assert result.phase1 is not None
        assert result.phase1.confidence >= PHASE1_THRESHOLD


# ---------------------------------------------------------------------------
# Pipeline routing: small_talk stops, task continues
# ---------------------------------------------------------------------------


class TestPhase1Routing:
    """Verify that Phase 1 classification controls pipeline routing."""

    def test_greeting_stops_pipeline(self, phase1_engine: TripleTwinEngine) -> None:
        """A greeting classification should stop the pipeline (no Phase 2/3)."""
        result = phase1_engine.process("hello")
        assert result.phase1 is not None
        assert result.phase1.label == "greeting"
        assert result.phase2 is None, "Greeting should not reach Phase 2"
        assert result.phase3 is None, "Greeting should not reach Phase 3"
        assert result.final_action == "small_talk:greeting"

    def test_task_continues_pipeline(self, phase1_engine: TripleTwinEngine) -> None:
        """A task classification should proceed to Phase 2."""
        result = phase1_engine.process("fix the login bug")
        assert result.phase1 is not None
        assert result.phase1.label == "task"
        # Phase 2 may or may not be configured, but phase1 should not stop
        assert result.final_action is not None
        assert "small_talk" not in result.final_action

    def test_unknown_with_zero_confidence_routes_to_llm_fallback(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        """Unknown label with 0.0 confidence (no LLM) should produce unknown."""
        result = phase1_engine.process("")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"
        assert result.phase1.confidence == 0.0
