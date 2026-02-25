"""test_phase1_bugs.py -- Tests that document known Phase 1 bugs.

Each test captures the current (buggy) behavior so that:
  1. We have a regression baseline showing what the engine actually does today.
  2. When a bug is fixed, the test will start failing, signaling the fix landed.

Bug index:
  BUG-P1-001: First-match-wins tie-breaking (4 affected prompts)
  BUG-P1-002: Dead "question" label (no seeds, stop words consume keywords)
  BUG-P1-003: Ultra-short bypass (len < 3 filter drops valid greetings)
  BUG-P1-005: 87.8% task bias in seed distribution

Rung: 641 -- deterministic, no network, no LLM.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from stillwater.cpu_learner import CPULearner
from stillwater.triple_twin import TripleTwinEngine

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "phase1_shared", Path(__file__).resolve().with_name("phase1_shared.py")
)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PHASE1_LABELS = _mod.PHASE1_LABELS
SEED_CONFIDENCE = _mod.SEED_CONFIDENCE


# ===========================================================================
# BUG-P1-001: First-match-wins tie-breaking
# ===========================================================================


class TestBugP1001TieBreaking:
    """BUG-P1-001: When multiple keywords have equal confidence (all seeds
    at count=25 -> 0.8824), the FIRST keyword in extraction order wins.

    Root cause: CPULearner.predict() iterates keywords in order. The first
    keyword matching a seed sets best_label. Later keywords with the same
    confidence hit the `elif conf == best_conf` branch which appends to
    matched[] but does NOT update best_label.

    Impact: Mixed small-talk + task inputs are classified by whichever
    category keyword appears first. Greetings/gratitude/humor words that
    start sentences always beat task keywords that follow.
    """

    def test_greeting_beats_task_prompt3(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        """Prompt #3: 'Hello! Can you fix the broken tests?'
        Keywords: [hello, fix, broken, tests]
        'hello' is first -> greeting. Should ideally be task.
        """
        result = phase1_engine.process("Hello! Can you fix the broken tests?")
        assert result.phase1 is not None
        # CURRENT BEHAVIOR (buggy): greeting wins because 'hello' is first
        assert result.phase1.label == "greeting", (
            "BUG-P1-001: Expected current behavior 'greeting' "
            "(first-match-wins). If this fails, the bug may be fixed."
        )
        # The pipeline STOPS at phase1 -- the task never reaches Phase 2
        assert result.phase2 is None
        assert result.final_action == "small_talk:greeting"

    @pytest.mark.xfail(
        reason="BUG-P1-001: Should be 'task' but first-match-wins gives 'greeting'",
        strict=True,
    )
    def test_greeting_beats_task_prompt3_desired(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        """Desired behavior: mixed greeting+task should classify as task."""
        result = phase1_engine.process("Hello! Can you fix the broken tests?")
        assert result.phase1 is not None
        assert result.phase1.label == "task"

    def test_gratitude_beats_task_prompt5(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        """Prompt #5: 'thanks for fixing that, now deploy it'
        Keywords: [thanks, fixing, deploy]
        'thanks' is first -> gratitude. Should ideally be task.
        """
        result = phase1_engine.process("thanks for fixing that, now deploy it")
        assert result.phase1 is not None
        assert result.phase1.label == "gratitude", (
            "BUG-P1-001: Expected current behavior 'gratitude'."
        )

    @pytest.mark.xfail(
        reason="BUG-P1-001: Should be 'task' but first-match-wins gives 'gratitude'",
        strict=True,
    )
    def test_gratitude_beats_task_prompt5_desired(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        result = phase1_engine.process("thanks for fixing that, now deploy it")
        assert result.phase1 is not None
        assert result.phase1.label == "task"

    def test_humor_beats_task_prompt18(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        """Prompt #18: 'tell me a joke about security vulnerabilities'
        Keywords: [tell, joke, security, vulnerabilities]
        'joke' matches humor seed first. 'security' matches task seed later.
        """
        result = phase1_engine.process(
            "tell me a joke about security vulnerabilities"
        )
        assert result.phase1 is not None
        assert result.phase1.label == "humor", (
            "BUG-P1-001: Expected current behavior 'humor'."
        )

    def test_small_talk_beats_task_prompt19(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        """Prompt #19: 'good morning! how's the weather? also please review my PR'
        Keywords: [good, morning, weather, review]
        'weather' matches small_talk seed. 'review' matches task seed.
        """
        result = phase1_engine.process(
            "good morning! how's the weather? also please review my PR"
        )
        assert result.phase1 is not None
        assert result.phase1.label == "small_talk", (
            "BUG-P1-001: Expected current behavior 'small_talk'."
        )

    def test_all_equal_confidence_seeds(self, cpu_learner: CPULearner) -> None:
        """Verify the root cause: all seeds share the same confidence."""
        confidences = set()
        for kw in cpu_learner._patterns:
            conf = cpu_learner.confidence(kw)
            confidences.add(round(conf, 4))
        assert len(confidences) == 1, (
            f"Expected all seeds to have identical confidence, got {confidences}"
        )
        assert round(SEED_CONFIDENCE, 4) in confidences


# ===========================================================================
# BUG-P1-002: Dead "question" label
# ===========================================================================


class TestBugP1002DeadQuestion:
    """BUG-P1-002: The 'question' label can never fire because:
    1. No seeds exist for the 'question' label.
    2. Question words (what, how, why, where, when, who, which) are ALL
       stop words, so they get filtered before reaching the learner.

    The cpu-node doc lists 'question' as a valid label with keywords
    [what, how, why, explain, curious], but all of those except 'explain'
    and 'curious' are stop words, and neither has a seed.
    """

    def test_question_has_no_seeds(self, seeds_records: list) -> None:
        """Verify there are zero seeds with label='question'."""
        question_seeds = [r for r in seeds_records if r.get("label") == "question"]
        assert len(question_seeds) == 0, (
            f"BUG-P1-002: Expected 0 question seeds, found {len(question_seeds)}"
        )

    def test_question_words_are_stop_words(self) -> None:
        """The question-indicator words are all stop words."""
        question_words = ["what", "how", "why", "where", "when", "who", "which"]
        for word in question_words:
            keywords = CPULearner.extract_keywords(word)
            assert keywords == [], f"'{word}' should be filtered as a stop word"

    def test_what_is_this_returns_unknown(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        """'what is this?' -> all words are stop words -> unknown."""
        result = phase1_engine.process("what is this?")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"
        assert result.phase1.confidence == 0.0

    def test_how_does_this_work_returns_unknown(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        """Pure question with only stop words returns unknown."""
        result = phase1_engine.process("how does this work?")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"

    def test_explain_survives_filter_but_no_seed(self) -> None:
        """'explain' passes the filter (len=7, not stop word) but has no seed."""
        keywords = CPULearner.extract_keywords("explain this")
        assert "explain" in keywords

    @pytest.mark.xfail(
        reason="BUG-P1-002: 'question' label has no seeds; question words are stop words",
        strict=True,
    )
    def test_question_label_desired(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        """Desired: 'what is this?' should classify as 'question'."""
        result = phase1_engine.process("what is this?")
        assert result.phase1 is not None
        assert result.phase1.label == "question"


# ===========================================================================
# BUG-P1-003: Ultra-short bypass
# ===========================================================================


class TestBugP1003UltraShort:
    """BUG-P1-003: Input shorter than 3 characters is silently dropped by
    the keyword extraction regex + len >= 3 filter. Words like 'yo', 'hi',
    'go' are completely invisible to the learner.

    This is not necessarily wrong (it is an intentional design choice), but
    it means common greetings like 'hi' and 'yo' can never be learned.
    """

    def test_yo_filtered_out(self) -> None:
        keywords = CPULearner.extract_keywords("yo")
        assert keywords == [], "'yo' (len=2) should be filtered"

    def test_hi_filtered_out(self) -> None:
        keywords = CPULearner.extract_keywords("hi")
        assert keywords == [], "'hi' (len=2) is also a stop word"

    def test_go_filtered_out(self) -> None:
        keywords = CPULearner.extract_keywords("go")
        assert keywords == [], "'go' (len=2) should be filtered"

    def test_yo_returns_unknown(self, phase1_engine: TripleTwinEngine) -> None:
        result = phase1_engine.process("yo")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"
        assert result.phase1.confidence == 0.0

    def test_single_char_filtered(self) -> None:
        keywords = CPULearner.extract_keywords("a")
        assert keywords == [], "'a' is a stop word and len < 3"

    @pytest.mark.xfail(
        reason="BUG-P1-003: 'yo' is a valid greeting but filtered by len<3",
        strict=True,
    )
    def test_yo_desired_greeting(self, phase1_engine: TripleTwinEngine) -> None:
        """Desired: 'yo' should classify as greeting."""
        result = phase1_engine.process("yo")
        assert result.phase1 is not None
        assert result.phase1.label == "greeting"


# ===========================================================================
# BUG-P1-005: 87.8% task bias in seed distribution
# ===========================================================================


class TestBugP1005SeedBias:
    """BUG-P1-005: 43 out of 49 seeds (87.8%) map to 'task'. Only 6 seeds
    cover the remaining 5 non-task labels (greeting, gratitude,
    emotional_positive, emotional_negative, humor, small_talk).

    Impact: The CPU learner has a heavy prior toward 'task'. Any input
    containing even one task-related word will be classified as task,
    even if the overall intent is something else.
    """

    def test_task_bias_percentage(self, seeds_records: list) -> None:
        """Verify that task seeds represent ~87.8% of total seeds."""
        label_counts = Counter(r["label"] for r in seeds_records)
        total = len(seeds_records)
        task_count = label_counts.get("task", 0)
        task_pct = task_count / total * 100 if total > 0 else 0

        assert task_pct > 80.0, (
            f"Expected task bias > 80%, got {task_pct:.1f}% "
            f"({task_count}/{total})"
        )

    def test_non_task_labels_underrepresented(self, seeds_records: list) -> None:
        """Non-task labels should each have at most 1-2 seeds."""
        label_counts = Counter(r["label"] for r in seeds_records)
        non_task_labels = {
            label: count
            for label, count in label_counts.items()
            if label != "task"
        }
        for label, count in non_task_labels.items():
            assert count <= 2, (
                f"Non-task label '{label}' has {count} seeds "
                f"(expected <= 2 given current bias)"
            )

    def test_question_and_off_domain_have_zero_seeds(self, seeds_records: list) -> None:
        """Labels 'question' and 'off_domain' have zero seeds."""
        label_counts = Counter(r["label"] for r in seeds_records)
        assert label_counts.get("question", 0) == 0
        assert label_counts.get("off_domain", 0) == 0

    def test_total_seed_count(self, seeds_records: list) -> None:
        """Verify total seed count matches expectations."""
        # As of the simulation: 49 seeds (was 50 in simulation summary header,
        # but actual line count is 49 -- the 50th may be a blank line)
        assert len(seeds_records) >= 49, (
            f"Expected at least 49 seeds, got {len(seeds_records)}"
        )

    def test_all_seeds_have_count_25(self, seeds_records: list) -> None:
        """All shipped seeds should have count=25."""
        for record in seeds_records:
            assert record.get("count") == 25, (
                f"Seed '{record.get('keyword')}' has count={record.get('count')}, "
                f"expected 25"
            )
