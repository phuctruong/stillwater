"""test_phase1_edge_cases.py -- Tests for all 8 breaking pattern categories.

Each test exercises one edge case category from the Phase 1 audit.
All tests use the real TripleTwinEngine with default seeds (CPU-only).

Rung: 641 -- deterministic, no network, no LLM.
"""

from __future__ import annotations

import pytest

from stillwater.cpu_learner import CPULearner
from stillwater.triple_twin import TripleTwinEngine


class TestNullEdge:
    """Breaking pattern: empty string input."""

    def test_empty_string_returns_unknown(self, phase1_engine: TripleTwinEngine) -> None:
        result = phase1_engine.process("")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"
        assert result.phase1.confidence == 0.0

    def test_empty_string_extracts_no_keywords(self) -> None:
        keywords = CPULearner.extract_keywords("")
        assert keywords == []

    def test_whitespace_only_returns_unknown(self, phase1_engine: TripleTwinEngine) -> None:
        result = phase1_engine.process("   ")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"
        assert result.phase1.confidence == 0.0

    def test_whitespace_extracts_no_keywords(self) -> None:
        keywords = CPULearner.extract_keywords("   ")
        assert keywords == []


class TestLengthEdge:
    """Breaking pattern: ultra-short input filtered by len >= 3 gate."""

    def test_yo_returns_unknown(self, phase1_engine: TripleTwinEngine) -> None:
        """'yo' has len=2, filtered by the len >= 3 keyword gate."""
        result = phase1_engine.process("yo")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"
        assert result.phase1.confidence == 0.0

    def test_yo_extracts_no_keywords(self) -> None:
        keywords = CPULearner.extract_keywords("yo")
        assert keywords == [], "'yo' should be filtered (len < 3)"

    def test_single_char_returns_unknown(self, phase1_engine: TripleTwinEngine) -> None:
        result = phase1_engine.process("x")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"

    def test_two_char_word_filtered(self) -> None:
        keywords = CPULearner.extract_keywords("go hi no ok")
        assert keywords == [], "All 2-char words should be filtered"

    def test_three_char_word_passes_if_not_stop_word(self) -> None:
        keywords = CPULearner.extract_keywords("fix")
        assert keywords == ["fix"], "'fix' has len=3, not a stop word"

    def test_three_char_stop_word_filtered(self) -> None:
        """'the' is 3 chars but is a stop word."""
        keywords = CPULearner.extract_keywords("the")
        assert keywords == []

    def test_run_single_word_classifies_as_task(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        """'run' has len=3, is a seed keyword for task."""
        result = phase1_engine.process("run")
        assert result.phase1 is not None
        assert result.phase1.label == "task"


class TestFilterEdge:
    """Breaking pattern: all stop words -- everything filtered out."""

    def test_all_stop_words_returns_unknown(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        result = phase1_engine.process("the the the the")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"
        assert result.phase1.confidence == 0.0

    def test_all_stop_words_extracts_nothing(self) -> None:
        keywords = CPULearner.extract_keywords("the the the the")
        assert keywords == []

    def test_mixed_stop_words_returns_unknown(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        result = phase1_engine.process("is it in on at to for of and or but")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"

    def test_stop_word_variety(self) -> None:
        """A broad set of stop words should all be filtered."""
        keywords = CPULearner.extract_keywords(
            "a an the is it in on at to for of and or but not with by from as"
        )
        assert keywords == []


class TestCountEdge:
    """Breaking pattern: repeated keywords (deduplication)."""

    def test_repeated_fix_deduplicates(self) -> None:
        keywords = CPULearner.extract_keywords("fix fix fix fix")
        assert keywords == ["fix"], "Repeated 'fix' should deduplicate to one"

    def test_repeated_fix_classifies_as_task(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        result = phase1_engine.process("fix fix fix fix")
        assert result.phase1 is not None
        assert result.phase1.label == "task"

    def test_hey_fix_mix_deduplicates(self) -> None:
        keywords = CPULearner.extract_keywords("hey hey hey fix fix fix")
        assert keywords == ["hey", "fix"]

    def test_hey_fix_mix_classifies_as_task(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        """'hey' has no seed; 'fix' is task seed -> task wins."""
        result = phase1_engine.process("hey hey hey fix fix fix")
        assert result.phase1 is not None
        assert result.phase1.label == "task"


class TestCaseEdge:
    """Breaking pattern: all caps input -- case normalization."""

    def test_all_caps_lowercased(self) -> None:
        keywords = CPULearner.extract_keywords("DEPLOY TO PRODUCTION NOW")
        assert "deploy" in keywords
        assert "production" in keywords

    def test_all_caps_classifies_as_task(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        result = phase1_engine.process("DEPLOY TO PRODUCTION NOW")
        assert result.phase1 is not None
        assert result.phase1.label == "task"

    def test_mixed_case_normalized(self) -> None:
        keywords = CPULearner.extract_keywords("FiX tHe BuG")
        assert "fix" in keywords
        assert "bug" in keywords


class TestNumericEdge:
    """Breaking pattern: numeric-only input."""

    def test_numeric_returns_unknown(self, phase1_engine: TripleTwinEngine) -> None:
        result = phase1_engine.process("12345")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"
        assert result.phase1.confidence == 0.0

    def test_numeric_extracts_nothing(self) -> None:
        """Regex [a-z]+ finds nothing in numeric input."""
        keywords = CPULearner.extract_keywords("12345")
        assert keywords == []

    def test_numeric_with_text_extracts_text(self) -> None:
        keywords = CPULearner.extract_keywords("fix bug 42")
        assert "fix" in keywords
        assert "bug" in keywords
        # "42" should not appear (no alpha chars)
        assert all(kw.isalpha() for kw in keywords)


class TestPunctuationEdge:
    """Breaking pattern: punctuation-only input."""

    def test_dots_returns_unknown(self, phase1_engine: TripleTwinEngine) -> None:
        result = phase1_engine.process("............")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"
        assert result.phase1.confidence == 0.0

    def test_dots_extracts_nothing(self) -> None:
        keywords = CPULearner.extract_keywords("............")
        assert keywords == []

    def test_special_chars_returns_unknown(self, phase1_engine: TripleTwinEngine) -> None:
        result = phase1_engine.process("!@#$%^&*()")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"

    def test_emoji_like_returns_unknown(self, phase1_engine: TripleTwinEngine) -> None:
        result = phase1_engine.process(":-) :-(")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"


class TestMisspellingEdge:
    """Breaking pattern: misspelled words with no fuzzy matching."""

    def test_plz_halp_returns_unknown(self, phase1_engine: TripleTwinEngine) -> None:
        """Misspellings 'plz' and 'halp' have no seed matches."""
        result = phase1_engine.process("plz halp")
        assert result.phase1 is not None
        assert result.phase1.label == "unknown"
        assert result.phase1.confidence == 0.0

    def test_plz_halp_extracts_keywords_but_no_match(self) -> None:
        """'plz' (len=3) and 'halp' (len=4) pass the filter but have no seeds."""
        keywords = CPULearner.extract_keywords("plz halp")
        assert "plz" in keywords
        assert "halp" in keywords

    def test_misspelled_deploy_returns_unknown(
        self, phase1_engine: TripleTwinEngine
    ) -> None:
        """'deploi' is not a known seed."""
        result = phase1_engine.process("deploi")
        assert result.phase1 is not None
        # 'deploi' has no matching seed
        assert result.phase1.label == "unknown"
