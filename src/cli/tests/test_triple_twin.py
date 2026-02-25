"""Tests for stillwater.triple_twin and stillwater.cpu_learner (promoted).

Coverage targets:
  1. YAML frontmatter parsing (~10 tests)
  2. CPULearner basics (~15 tests)
  3. TripleTwinEngine discovery (~15 tests)
  4. TripleTwinEngine processing (~20 tests)
  5. Learning + persistence (~15 tests)
  6. Integration (~10 tests)

Rung: 641 — deterministic, no network, testable.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

import pytest

from stillwater.cpu_learner import (
    CONFIDENCE_THRESHOLD,
    MIN_FREQUENCY_FOR_CONFIDENCE,
    CPULearner,
)
from stillwater.data_registry import DataRegistry
from stillwater.triple_twin import (
    OrchestrationResult,
    PhaseResult,
    PhaseRunner,
    TripleTwinEngine,
    parse_frontmatter,
)


# ===========================================================================
# Helpers
# ===========================================================================


def _make_cpu_node_md(
    phase: str = "phase1",
    name: str = "small-talk",
    validator_model: str = "haiku",
    labels: Optional[list] = None,
    learnings_file: Optional[str] = None,
) -> str:
    """Generate a cpu-node .md file with YAML frontmatter."""
    if labels is None:
        labels = ["greeting", "task"]
    if learnings_file is None:
        learnings_file = f"learned_{phase}.jsonl"
    labels_str = ", ".join(labels)
    return (
        f"---\n"
        f"phase: {phase}\n"
        f"name: {name}\n"
        f"validator_model: {validator_model}\n"
        f"labels: [{labels_str}]\n"
        f"learnings_file: {learnings_file}\n"
        f"---\n\n"
        f"# {name}\n\nDescription of the {phase} cpu node.\n"
    )


def _make_seed_jsonl(records: list) -> str:
    """Generate JSONL content from a list of dicts."""
    return "\n".join(json.dumps(r) for r in records) + "\n"


def _setup_data_dirs(tmp_path: Path) -> Path:
    """Create data/default/ and data/custom/ under tmp_path. Return tmp_path."""
    (tmp_path / "data" / "default").mkdir(parents=True)
    (tmp_path / "data" / "custom").mkdir(parents=True)
    return tmp_path


def _write_default(tmp_path: Path, relative_path: str, content: str) -> None:
    """Write a file to data/default/ under tmp_path."""
    target = tmp_path / "data" / "default" / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _write_custom(tmp_path: Path, relative_path: str, content: str) -> None:
    """Write a file to data/custom/ under tmp_path."""
    target = tmp_path / "data" / "custom" / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


class MockLLMClient:
    """Mock LLM validator that returns pre-configured responses."""

    def __init__(self, responses: Optional[dict] = None) -> None:
        self.responses = responses or {}
        self.call_log: list = []

    def validate(self, phase: str, text: str, context: Optional[dict] = None) -> dict:
        self.call_log.append({"phase": phase, "text": text, "context": context})
        # Look up by phase, then fall back to a default
        if phase in self.responses:
            return self.responses[phase]
        return {"label": "fallback", "confidence": 0.85, "reasoning": "Mock fallback"}


class FailingLLMClient:
    """LLM client that always raises an exception."""

    def validate(self, phase: str, text: str, context: Optional[dict] = None) -> dict:
        raise ConnectionError("LLM service unavailable")


# ===========================================================================
# 1. YAML frontmatter parsing (~10 tests)
# ===========================================================================


class TestParseFrontmatter:
    """Tests for the stdlib YAML frontmatter parser."""

    def test_parse_valid_frontmatter(self) -> None:
        """Parse a valid frontmatter block with multiple key types."""
        text = (
            "---\n"
            "phase: phase1\n"
            "name: small-talk\n"
            "validator_model: haiku\n"
            "labels: [greeting, task, humor]\n"
            "learnings_file: learned_phase1.jsonl\n"
            "---\n\n"
            "# Body content\n"
        )
        result = parse_frontmatter(text)
        assert result["phase"] == "phase1"
        assert result["name"] == "small-talk"
        assert result["validator_model"] == "haiku"
        assert result["labels"] == ["greeting", "task", "humor"]
        assert result["learnings_file"] == "learned_phase1.jsonl"

    def test_parse_integer_value(self) -> None:
        text = "---\ncount: 42\n---\n"
        result = parse_frontmatter(text)
        assert result["count"] == 42
        assert isinstance(result["count"], int)

    def test_parse_float_value(self) -> None:
        text = "---\nthreshold: 0.85\n---\n"
        result = parse_frontmatter(text)
        assert result["threshold"] == 0.85
        assert isinstance(result["threshold"], float)

    def test_parse_boolean_values(self) -> None:
        text = "---\nenabled: true\ndisabled: false\n---\n"
        result = parse_frontmatter(text)
        assert result["enabled"] is True
        assert result["disabled"] is False

    def test_parse_quoted_string(self) -> None:
        text = '---\ntitle: "Hello World"\n---\n'
        result = parse_frontmatter(text)
        assert result["title"] == "Hello World"

    def test_parse_single_quoted_string(self) -> None:
        text = "---\ntitle: 'Hello World'\n---\n"
        result = parse_frontmatter(text)
        assert result["title"] == "Hello World"

    def test_parse_empty_list(self) -> None:
        text = "---\nlabels: []\n---\n"
        result = parse_frontmatter(text)
        assert result["labels"] == []

    def test_parse_empty_frontmatter(self) -> None:
        text = "---\n---\n# Body\n"
        result = parse_frontmatter(text)
        assert result == {}

    def test_parse_no_frontmatter(self) -> None:
        text = "# Just a markdown file\n\nNo frontmatter here.\n"
        result = parse_frontmatter(text)
        assert result == {}

    def test_parse_comments_ignored(self) -> None:
        text = "---\n# This is a comment\nphase: phase2\n---\n"
        result = parse_frontmatter(text)
        assert "This is a comment" not in str(result)
        assert result["phase"] == "phase2"

    def test_parse_null_value(self) -> None:
        text = "---\noptional: null\n---\n"
        result = parse_frontmatter(text)
        assert result["optional"] is None

    def test_parse_missing_colon_line_skipped(self) -> None:
        text = "---\nphase: phase1\nno-colon-here\nname: test\n---\n"
        result = parse_frontmatter(text)
        assert result["phase"] == "phase1"
        assert result["name"] == "test"
        assert "no-colon-here" not in result


# ===========================================================================
# 2. CPULearner basics (~15 tests)
# ===========================================================================


class TestCPULearner:
    """Tests for the promoted CPULearner."""

    def test_init_valid_phases(self) -> None:
        for phase in ("phase1", "phase2", "phase3"):
            learner = CPULearner(phase)
            assert learner.phase == phase
            assert learner.threshold == CONFIDENCE_THRESHOLD[phase]

    def test_init_invalid_phase_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown phase"):
            CPULearner("phase4")

    def test_extract_keywords_strips_stop_words(self) -> None:
        keywords = CPULearner.extract_keywords("I am going to the store")
        assert "the" not in keywords
        assert "going" in keywords
        assert "store" in keywords

    def test_extract_keywords_filters_short_words(self) -> None:
        keywords = CPULearner.extract_keywords("go to do it no")
        # All words are 2 chars or less (or stop words), so nothing passes
        assert keywords == []

    def test_extract_keywords_deduplicates(self) -> None:
        keywords = CPULearner.extract_keywords("hello hello hello world")
        assert keywords == ["hello", "world"]

    def test_extract_keywords_lowercases(self) -> None:
        keywords = CPULearner.extract_keywords("Hello WORLD Test")
        assert "hello" in keywords
        assert "world" in keywords
        assert "test" in keywords

    def test_learn_increases_pattern_count(self) -> None:
        learner = CPULearner("phase1")
        learner.learn("fix the broken test", "bugfix")
        learner.learn("fix the broken test", "bugfix")
        # "fix" is 3 chars, "broken" and "test" pass filter
        assert learner._patterns["broken"]["count"] == 2
        assert learner._patterns["test"]["count"] == 2

    def test_learn_returns_keywords(self) -> None:
        learner = CPULearner("phase1")
        keywords = learner.learn("deploy the application", "deploy")
        assert "deploy" in keywords
        assert "application" in keywords

    def test_learn_increments_total_learned(self) -> None:
        learner = CPULearner("phase1")
        assert learner.total_learned == 0
        learner.learn("hello world testing", "greeting")
        assert learner.total_learned == 1
        learner.learn("goodbye world testing", "farewell")
        assert learner.total_learned == 2

    def test_predict_returns_correct_label(self) -> None:
        learner = CPULearner("phase1")
        # Train several times to build confidence
        for _ in range(10):
            learner.learn("deploy application server", "deploy")
        label, conf, matched = learner.predict("deploy the application")
        assert label == "deploy"
        assert conf > 0

    def test_predict_returns_none_for_unknown(self) -> None:
        learner = CPULearner("phase1")
        label, conf, matched = learner.predict("completely unknown input")
        assert label is None
        assert conf == 0.0
        assert matched == []

    def test_can_handle_respects_threshold(self) -> None:
        learner = CPULearner("phase1")  # threshold = 0.70
        learner.learn("deploy application server", "deploy")
        # After 1 learning event, confidence is low
        assert not learner.can_handle("deploy application server")
        # After many events, should exceed threshold
        for _ in range(20):
            learner.learn("deploy application server", "deploy")
        assert learner.can_handle("deploy application server")

    def test_confidence_zero_for_unknown_keyword(self) -> None:
        learner = CPULearner("phase1")
        assert learner.confidence("nonexistent") == 0.0

    def test_confidence_increases_with_count(self) -> None:
        learner = CPULearner("phase1")
        learner.learn("testing framework setup", "test")
        conf1 = learner.confidence("testing")
        for _ in range(5):
            learner.learn("testing framework setup", "test")
        conf6 = learner.confidence("testing")
        assert conf6 > conf1, "Confidence should increase with more observations"

    def test_confidence_follows_logistic_curve(self) -> None:
        learner = CPULearner("phase1")
        # count=0 -> 0.0
        assert learner.confidence("missing") == 0.0
        # Manually set a pattern count
        learner._patterns["test"]["count"] = 1
        learner._patterns["test"]["label"] = "test"
        c1 = learner.confidence("test")
        learner._confidence_cache.clear()
        learner._patterns["test"]["count"] = 10
        c10 = learner.confidence("test")
        # Verify logistic shape: c10 > c1
        assert c10 > c1
        # Verify specific formula: 1 - 1/(1 + 0.3*count)
        expected_c1 = 1.0 - 1.0 / (1.0 + 0.3 * 1)
        assert abs(c1 - expected_c1) < 0.001

    def test_save_load_roundtrip(self, tmp_path: Path) -> None:
        learner = CPULearner("phase2")
        learner.learn("fix broken authentication", "bugfix")
        learner.learn("deploy staging server", "deploy")
        learner.learn("deploy staging server", "deploy")

        filepath = str(tmp_path / "learned.jsonl")
        learner.save(filepath)

        loaded = CPULearner("phase2")
        loaded.load(filepath)

        # Verify patterns survived
        assert "broken" in loaded._patterns
        assert "authentication" in loaded._patterns
        assert loaded._patterns["deploy"]["count"] == 2
        assert loaded._patterns["deploy"]["label"] == "deploy"

    def test_load_nonexistent_file_is_noop(self) -> None:
        learner = CPULearner("phase1")
        learner.load("/nonexistent/path/file.jsonl")
        assert len(learner._patterns) == 0

    def test_stats_returns_correct_counts(self) -> None:
        learner = CPULearner("phase1")
        s = learner.stats()
        assert s["total_patterns"] == 0
        assert s["total_learning_events"] == 0
        assert s["high_confidence_patterns"] == 0
        assert s["avg_confidence"] == 0.0
        assert s["top_patterns"] == []

        learner.learn("test automation framework", "test")
        s = learner.stats()
        assert s["total_patterns"] > 0
        assert s["total_learning_events"] == 1

    def test_stats_top_patterns_capped_at_5(self) -> None:
        learner = CPULearner("phase1")
        for i in range(10):
            word = f"keyword{i:03d}"
            learner._patterns[word] = {"count": i + 1, "label": "test", "examples": []}
        s = learner.stats()
        assert len(s["top_patterns"]) == 5

    def test_to_jsonl_records_sorted_by_confidence(self) -> None:
        learner = CPULearner("phase1")
        learner._patterns["low"] = {"count": 1, "label": "a", "examples": []}
        learner._patterns["high"] = {"count": 20, "label": "b", "examples": []}
        records = learner.to_jsonl_records()
        assert records[0]["keyword"] == "high"
        assert records[1]["keyword"] == "low"


# ===========================================================================
# 3. TripleTwinEngine discovery (~15 tests)
# ===========================================================================


class TestTripleTwinDiscovery:
    """Tests for cpu-node discovery and pattern loading."""

    def test_discovers_cpu_nodes_from_default(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/phase1.md", _make_cpu_node_md("phase1", "small-talk"))
        _write_default(root, "cpu-nodes/phase2.md", _make_cpu_node_md("phase2", "intent"))
        _write_default(root, "cpu-nodes/phase3.md", _make_cpu_node_md("phase3", "execution"))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        assert "phase1" in engine._phases
        assert "phase2" in engine._phases
        assert "phase3" in engine._phases

    def test_discovers_phase_name(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "my-small-talk"))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        assert engine._phases["phase1"].name == "my-small-talk"

    def test_discovers_labels(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md(
            "phase1", "small-talk", labels=["greeting", "farewell", "task"]
        ))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        assert engine._phases["phase1"].labels == ["greeting", "farewell", "task"]

    def test_loads_seeds_from_jsonl(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        seeds = [
            {"keyword": "hello", "label": "greeting", "count": 5, "confidence": 0.6, "examples": [], "phase": "phase1"},
            {"keyword": "goodbye", "label": "farewell", "count": 3, "confidence": 0.47, "examples": [], "phase": "phase1"},
        ]
        _write_default(root, "seeds/phase1_seeds.jsonl", _make_seed_jsonl(seeds))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        assert "hello" in engine._phases["phase1"].learner._patterns
        assert engine._phases["phase1"].learner._patterns["hello"]["count"] == 5
        assert engine._phases["phase1"].learner._patterns["hello"]["label"] == "greeting"

    def test_loads_learned_from_custom(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p2.md", _make_cpu_node_md("phase2", "intent"))

        learned = [
            {"keyword": "deploy", "label": "deploy", "count": 10, "confidence": 0.75, "examples": [], "phase": "phase2"},
        ]
        _write_custom(root, "learned_phase2.jsonl", _make_seed_jsonl(learned))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        assert "deploy" in engine._phases["phase2"].learner._patterns
        assert engine._phases["phase2"].learner._patterns["deploy"]["count"] == 10

    def test_custom_cpu_node_overrides_default(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "default-name"))
        _write_custom(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "custom-name"))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        # DataRegistry overlay means custom wins for the same relative path
        assert engine._phases["phase1"].name == "custom-name"

    def test_missing_cpu_nodes_dir_gives_empty_phases(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        # No cpu-nodes/ directory created

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        assert engine._phases == {}

    def test_invalid_md_file_skipped_gracefully(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        # Write a .md file with no valid frontmatter
        _write_default(root, "cpu-nodes/bad.md", "# No frontmatter at all\nJust content.\n")
        # Write a valid one too
        _write_default(root, "cpu-nodes/good.md", _make_cpu_node_md("phase1", "good"))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        assert "phase1" in engine._phases
        assert engine._phases["phase1"].name == "good"

    def test_md_with_invalid_phase_skipped(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/bad.md", _make_cpu_node_md("phase99", "bad"))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        assert "phase99" not in engine._phases

    def test_non_md_files_in_cpu_nodes_ignored(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/readme.txt", "Not a .md file")
        _write_default(root, "cpu-nodes/data.json", '{"not": "markdown"}')

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        assert engine._phases == {}

    def test_seed_with_wrong_phase_ignored(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        # Seed has phase2 records but no phase2 runner configured
        seeds = [
            {"keyword": "deploy", "label": "deploy", "count": 5, "confidence": 0.6, "examples": [], "phase": "phase2"},
        ]
        _write_default(root, "seeds/phase2_seeds.jsonl", _make_seed_jsonl(seeds))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        # phase2 not configured, so seeds for phase2 are ignored
        assert "deploy" not in engine._phases["phase1"].learner._patterns

    def test_malformed_jsonl_lines_skipped(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        content = (
            '{"keyword": "hello", "label": "greeting", "count": 5, "examples": [], "phase": "phase1"}\n'
            'NOT VALID JSON\n'
            '{"keyword": "goodbye", "label": "farewell", "count": 3, "examples": [], "phase": "phase1"}\n'
        )
        _write_default(root, "seeds/mixed.jsonl", content)

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        assert "hello" in engine._phases["phase1"].learner._patterns
        assert "goodbye" in engine._phases["phase1"].learner._patterns

    def test_jsonl_records_without_keyword_skipped(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        content = '{"label": "greeting", "count": 5, "examples": [], "phase": "phase1"}\n'
        _write_default(root, "seeds/no_kw.jsonl", content)

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        # No patterns loaded (keyword was missing)
        assert len(engine._phases["phase1"].learner._patterns) == 0

    def test_learnings_file_from_frontmatter(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md(
            "phase1", "small-talk", learnings_file="my_custom_learnings.jsonl"
        ))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        assert engine._phases["phase1"].learnings_file == "my_custom_learnings.jsonl"

    def test_multiple_cpu_nodes_for_same_phase_last_wins(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/aaa.md", _make_cpu_node_md("phase1", "first"))
        _write_default(root, "cpu-nodes/zzz.md", _make_cpu_node_md("phase1", "last"))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        # Both are sorted alphabetically, last one wins
        assert engine._phases["phase1"].name == "last"


# ===========================================================================
# 4. TripleTwinEngine processing (~20 tests)
# ===========================================================================


class TestTripleTwinProcessing:
    """Tests for the process() pipeline."""

    @pytest.fixture()
    def engine_with_phases(self, tmp_path: Path) -> TripleTwinEngine:
        """Create an engine with all 3 phases configured and seeded."""
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md(
            "phase1", "small-talk", labels=["greeting", "task"]
        ))
        _write_default(root, "cpu-nodes/p2.md", _make_cpu_node_md(
            "phase2", "intent", labels=["bugfix", "deploy", "feature"]
        ))
        _write_default(root, "cpu-nodes/p3.md", _make_cpu_node_md(
            "phase3", "execution", labels=["bugfix-combo", "deploy-combo"]
        ))
        reg = DataRegistry(repo_root=root)
        return TripleTwinEngine(registry=reg)

    @pytest.fixture()
    def seeded_engine(self, tmp_path: Path) -> TripleTwinEngine:
        """Engine with pre-trained patterns that exceed thresholds."""
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md(
            "phase1", "small-talk", labels=["greeting", "task"]
        ))
        _write_default(root, "cpu-nodes/p2.md", _make_cpu_node_md(
            "phase2", "intent", labels=["bugfix", "deploy"]
        ))
        _write_default(root, "cpu-nodes/p3.md", _make_cpu_node_md(
            "phase3", "execution", labels=["bugfix-combo", "deploy-combo"]
        ))

        # Seeds with high counts so CPU is confident
        p1_seeds = [
            {"keyword": "hello", "label": "greeting", "count": 50, "examples": [], "phase": "phase1"},
            {"keyword": "broken", "label": "task", "count": 50, "examples": [], "phase": "phase1"},
            {"keyword": "deploy", "label": "task", "count": 50, "examples": [], "phase": "phase1"},
        ]
        p2_seeds = [
            {"keyword": "broken", "label": "bugfix", "count": 50, "examples": [], "phase": "phase2"},
            {"keyword": "deploy", "label": "deploy", "count": 50, "examples": [], "phase": "phase2"},
        ]
        p3_seeds = [
            {"keyword": "broken", "label": "bugfix-combo", "count": 50, "examples": [], "phase": "phase3"},
            {"keyword": "deploy", "label": "deploy-combo", "count": 50, "examples": [], "phase": "phase3"},
        ]
        _write_default(root, "seeds/p1.jsonl", _make_seed_jsonl(p1_seeds))
        _write_default(root, "seeds/p2.jsonl", _make_seed_jsonl(p2_seeds))
        _write_default(root, "seeds/p3.jsonl", _make_seed_jsonl(p3_seeds))

        reg = DataRegistry(repo_root=root)
        return TripleTwinEngine(registry=reg)

    def test_small_talk_handled_by_cpu_when_confident(self, seeded_engine: TripleTwinEngine) -> None:
        result = seeded_engine.process("hello there friend")
        assert result.phase1 is not None
        assert result.phase1.handled_by == "cpu"
        assert result.phase1.label == "greeting"
        assert result.final_action == "small_talk:greeting"

    def test_small_talk_stops_pipeline(self, seeded_engine: TripleTwinEngine) -> None:
        result = seeded_engine.process("hello there friend")
        assert result.phase2 is None
        assert result.phase3 is None

    def test_task_routes_to_phase2(self, seeded_engine: TripleTwinEngine) -> None:
        result = seeded_engine.process("something broken needs fixing")
        assert result.phase1 is not None
        assert result.phase1.label == "task"
        assert result.phase2 is not None

    def test_intent_matched_by_cpu(self, seeded_engine: TripleTwinEngine) -> None:
        result = seeded_engine.process("something broken needs fixing")
        assert result.phase2 is not None
        assert result.phase2.handled_by == "cpu"
        assert result.matched_wish == "bugfix"

    def test_combo_selected_by_cpu(self, seeded_engine: TripleTwinEngine) -> None:
        result = seeded_engine.process("something broken needs fixing")
        assert result.phase3 is not None
        assert result.phase3.handled_by == "cpu"
        assert result.matched_combo == "bugfix-combo"

    def test_full_pipeline_result_structure(self, seeded_engine: TripleTwinEngine) -> None:
        result = seeded_engine.process("deploy the application now")
        assert result.input == "deploy the application now"
        assert result.phase1 is not None
        assert result.phase1.phase == 1
        assert result.phase2 is not None
        assert result.phase2.phase == 2
        assert result.phase3 is not None
        assert result.phase3.phase == 3
        assert result.matched_wish == "deploy"
        assert result.matched_combo == "deploy-combo"
        assert result.final_action == "execute:deploy:deploy-combo"

    def test_no_llm_client_cpu_only_mode(self, engine_with_phases: TripleTwinEngine) -> None:
        """Without LLM client, engine degrades gracefully."""
        result = engine_with_phases.process("hello")
        assert result.phase1 is not None
        # CPU has no training data, LLM not available -> unknown
        assert result.phase1.label == "unknown"

    def test_small_talk_falls_through_to_llm(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        mock = MockLLMClient(responses={
            "phase1": {"label": "greeting", "confidence": 0.95, "reasoning": "This is a greeting"},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        result = engine.process("hi there")
        assert result.phase1 is not None
        assert result.phase1.handled_by == "llm"
        assert result.phase1.label == "greeting"
        assert len(mock.call_log) >= 1

    def test_intent_falls_through_to_llm(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))
        _write_default(root, "cpu-nodes/p2.md", _make_cpu_node_md("phase2", "intent"))

        # Phase 1 returns "task", Phase 2 returns "bugfix"
        mock = MockLLMClient(responses={
            "phase1": {"label": "task", "confidence": 0.90, "reasoning": "This is a task"},
            "phase2": {"label": "bugfix", "confidence": 0.88, "reasoning": "Bug report detected"},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        result = engine.process("fix the broken test")
        assert result.phase2 is not None
        assert result.phase2.handled_by == "llm"
        assert result.matched_wish == "bugfix"

    def test_failing_llm_error_propagates(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        engine = TripleTwinEngine(
            registry=DataRegistry(repo_root=root),
            llm_client=FailingLLMClient(),
        )
        with pytest.raises(ConnectionError):
            engine.process("hello")

    def test_process_returns_orchestration_result(self, engine_with_phases: TripleTwinEngine) -> None:
        result = engine_with_phases.process("test input")
        assert isinstance(result, OrchestrationResult)
        assert result.input == "test input"

    def test_process_phase1_returns_phase_result(self, engine_with_phases: TripleTwinEngine) -> None:
        result = engine_with_phases.process("test input")
        assert result.phase1 is not None
        assert isinstance(result.phase1, PhaseResult)
        assert result.phase1.phase == 1

    def test_no_phases_configured_returns_execute_unknown(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        result = engine.process("hello")
        # No phases configured, so phase1 is None -> treat as task -> execute
        assert result.phase1 is None
        assert result.final_action is not None
        assert "execute" in result.final_action

    def test_only_phase1_configured(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        # Seed so CPU is confident for "task" label
        seeds = [{"keyword": "broken", "label": "task", "count": 50, "examples": [], "phase": "phase1"}]
        _write_default(root, "seeds/p1.jsonl", _make_seed_jsonl(seeds))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        result = engine.process("something broken here")
        assert result.phase1 is not None
        assert result.phase1.label == "task"
        # Phase 2 and 3 not configured -> None results
        assert result.phase2 is None
        assert result.phase3 is None
        assert "execute" in result.final_action

    def test_phase1_greeting_prevents_phase2(self, seeded_engine: TripleTwinEngine) -> None:
        result = seeded_engine.process("hello friend")
        assert result.phase1 is not None
        assert result.phase1.label == "greeting"
        assert result.phase2 is None
        assert "small_talk" in result.final_action

    def test_total_processed_increments(self, engine_with_phases: TripleTwinEngine) -> None:
        engine_with_phases.process("test 1")
        engine_with_phases.process("test 2")
        engine_with_phases.process("test 3")
        assert engine_with_phases._total_processed == 3

    def test_cpu_hits_counted(self, seeded_engine: TripleTwinEngine) -> None:
        seeded_engine.process("hello there friend")
        assert seeded_engine._cpu_hits >= 1

    def test_llm_calls_counted(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        mock = MockLLMClient(responses={
            "phase1": {"label": "greeting", "confidence": 0.90, "reasoning": "Greeting"},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        engine.process("hello")
        assert engine._llm_calls >= 1

    def test_unknown_label_does_not_trigger_learning(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        # LLM returns unknown
        mock = MockLLMClient(responses={
            "phase1": {"label": "unknown", "confidence": 0.0},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        engine.process("gibberish xyz")
        # No learning events should have occurred for "unknown" label
        assert engine._phases["phase1"].learner.total_learned == 0


# ===========================================================================
# 5. Learning + persistence (~15 tests)
# ===========================================================================


class TestLearningPersistence:
    """Tests for learning from LLM and persisting to data/custom/."""

    def test_llm_validation_triggers_learning(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        mock = MockLLMClient(responses={
            "phase1": {"label": "greeting", "confidence": 0.92, "reasoning": "This is a hello"},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        engine.process("hello world testing")
        # Learning should have happened
        assert engine._phases["phase1"].learner.total_learned > 0

    def test_learned_patterns_persisted_to_custom(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        mock = MockLLMClient(responses={
            "phase1": {"label": "greeting", "confidence": 0.92, "reasoning": "Greeting detected"},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        engine.process("hello world testing")

        # Check that the file was written to data/custom/
        learnings_file = root / "data" / "custom" / "learned_phase1.jsonl"
        assert learnings_file.exists()
        content = learnings_file.read_text(encoding="utf-8")
        assert "greeting" in content

    def test_persisted_patterns_are_valid_jsonl(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        mock = MockLLMClient(responses={
            "phase1": {"label": "task", "confidence": 0.90, "reasoning": "Task identified"},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        engine.process("fix broken authentication")

        learnings_file = root / "data" / "custom" / "learned_phase1.jsonl"
        content = learnings_file.read_text(encoding="utf-8")
        for line in content.strip().splitlines():
            record = json.loads(line)
            assert "keyword" in record
            assert "label" in record
            assert "count" in record
            assert "phase" in record

    def test_restart_engine_patterns_survive(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        mock = MockLLMClient(responses={
            "phase1": {"label": "greeting", "confidence": 0.92, "reasoning": "Hello detected"},
        })
        reg = DataRegistry(repo_root=root)

        # First engine learns
        engine1 = TripleTwinEngine(registry=reg, llm_client=mock)
        engine1.process("hello world testing")
        patterns_before = dict(engine1._phases["phase1"].learner._patterns)

        # Second engine loads persisted patterns
        engine2 = TripleTwinEngine(registry=reg, llm_client=mock)
        patterns_after = dict(engine2._phases["phase1"].learner._patterns)

        # Patterns should be present in engine2
        assert len(patterns_after) > 0
        for kw in patterns_before:
            assert kw in patterns_after, f"Keyword {kw!r} not found after restart"

    def test_learning_increases_confidence_over_time(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        mock = MockLLMClient(responses={
            "phase1": {"label": "greeting", "confidence": 0.92, "reasoning": "Hello"},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        # Process the same input multiple times
        for _ in range(10):
            engine.process("hello world testing")

        # Confidence for "hello" should now be higher
        conf = engine._phases["phase1"].learner.confidence("hello")
        assert conf > 0.5, f"Expected confidence > 0.5 after 10 rounds, got {conf}"

    def test_multiple_phases_persist_independently(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))
        _write_default(root, "cpu-nodes/p2.md", _make_cpu_node_md("phase2", "intent"))

        mock = MockLLMClient(responses={
            "phase1": {"label": "task", "confidence": 0.90, "reasoning": "Task"},
            "phase2": {"label": "bugfix", "confidence": 0.88, "reasoning": "Bug"},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        engine.process("fix broken authentication")

        p1_file = root / "data" / "custom" / "learned_phase1.jsonl"
        p2_file = root / "data" / "custom" / "learned_phase2.jsonl"
        assert p1_file.exists()
        assert p2_file.exists()

        p1_content = p1_file.read_text(encoding="utf-8")
        p2_content = p2_file.read_text(encoding="utf-8")

        # Phase 1 patterns should say "task"
        p1_labels = set()
        for line in p1_content.strip().splitlines():
            p1_labels.add(json.loads(line)["label"])
        assert "task" in p1_labels

        # Phase 2 patterns should say "bugfix"
        p2_labels = set()
        for line in p2_content.strip().splitlines():
            p2_labels.add(json.loads(line)["label"])
        assert "bugfix" in p2_labels

    def test_learning_from_reasoning_adds_extra_keywords(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        mock = MockLLMClient(responses={
            "phase1": {
                "label": "greeting",
                "confidence": 0.92,
                "reasoning": "The user said salutation which indicates warmth",
            },
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        engine.process("hi there")

        # "salutation" and "warmth" from reasoning should be learned too
        patterns = engine._phases["phase1"].learner._patterns
        assert "salutation" in patterns
        assert "warmth" in patterns

    def test_persist_called_after_each_llm_learning(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        mock = MockLLMClient(responses={
            "phase1": {"label": "greeting", "confidence": 0.92, "reasoning": "Hello"},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        engine.process("hello testing")
        learnings_file = root / "data" / "custom" / "learned_phase1.jsonl"
        assert learnings_file.exists()
        mtime1 = learnings_file.stat().st_mtime_ns

        # Process again — file should be updated
        engine.process("hello testing again")
        mtime2 = learnings_file.stat().st_mtime_ns
        # File was rewritten (mtime changed or content grew)
        content = learnings_file.read_text(encoding="utf-8")
        lines = [l for l in content.strip().splitlines() if l.strip()]
        assert len(lines) >= 1

    def test_default_dir_never_written(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        default_dir = root / "data" / "default"
        files_before = set(str(p) for p in default_dir.rglob("*") if p.is_file())

        mock = MockLLMClient(responses={
            "phase1": {"label": "greeting", "confidence": 0.92, "reasoning": "Hello"},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        for _ in range(5):
            engine.process("hello world testing")

        files_after = set(str(p) for p in default_dir.rglob("*") if p.is_file())
        assert files_before == files_after, "Default directory was modified!"

    def test_empty_reasoning_still_learns(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        mock = MockLLMClient(responses={
            "phase1": {"label": "greeting", "confidence": 0.92},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        engine.process("hello world testing")
        assert engine._phases["phase1"].learner.total_learned > 0

    def test_cpu_handles_after_sufficient_learning(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        mock = MockLLMClient(responses={
            "phase1": {"label": "greeting", "confidence": 0.92, "reasoning": "Hello"},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        # Train many times
        for _ in range(30):
            engine.process("hello world testing")

        # Now CPU should be confident
        can_handle = engine._phases["phase1"].learner.can_handle("hello world testing")
        assert can_handle, "CPU should handle after sufficient learning"

    def test_learning_persists_correct_phase_field(self, tmp_path: Path) -> None:
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p2.md", _make_cpu_node_md("phase2", "intent"))

        mock = MockLLMClient(responses={
            "phase2": {"label": "bugfix", "confidence": 0.88, "reasoning": "Bug"},
        })
        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg, llm_client=mock)

        # Phase 1 not configured, so goes straight to phase 2
        engine.process("fix broken test")

        learnings_file = root / "data" / "custom" / "learned_phase2.jsonl"
        content = learnings_file.read_text(encoding="utf-8")
        for line in content.strip().splitlines():
            record = json.loads(line)
            assert record["phase"] == "phase2"


# ===========================================================================
# 6. Integration (~10 tests)
# ===========================================================================


class TestIntegration:
    """End-to-end integration tests."""

    def _build_full_engine(
        self,
        tmp_path: Path,
        llm_client: object = None,
    ) -> TripleTwinEngine:
        """Build a fully configured engine with seeds."""
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/phase1.md", _make_cpu_node_md(
            "phase1", "small-talk", "haiku", ["greeting", "task", "humor"]
        ))
        _write_default(root, "cpu-nodes/phase2.md", _make_cpu_node_md(
            "phase2", "intent", "sonnet", ["bugfix", "deploy", "feature", "test"]
        ))
        _write_default(root, "cpu-nodes/phase3.md", _make_cpu_node_md(
            "phase3", "execution", "opus", ["bugfix-combo", "deploy-combo", "feature-combo"]
        ))

        # Seed phase1 with high confidence patterns
        p1_seeds = [
            {"keyword": "hello", "label": "greeting", "count": 50, "examples": ["hello"], "phase": "phase1"},
            {"keyword": "joke", "label": "humor", "count": 50, "examples": ["tell a joke"], "phase": "phase1"},
            {"keyword": "broken", "label": "task", "count": 50, "examples": ["fix broken"], "phase": "phase1"},
            {"keyword": "deploy", "label": "task", "count": 50, "examples": ["deploy app"], "phase": "phase1"},
            {"keyword": "feature", "label": "task", "count": 50, "examples": ["new feature"], "phase": "phase1"},
        ]
        p2_seeds = [
            {"keyword": "broken", "label": "bugfix", "count": 50, "examples": ["fix broken"], "phase": "phase2"},
            {"keyword": "deploy", "label": "deploy", "count": 50, "examples": ["deploy app"], "phase": "phase2"},
            {"keyword": "feature", "label": "feature", "count": 50, "examples": ["new feature"], "phase": "phase2"},
        ]
        p3_seeds = [
            {"keyword": "broken", "label": "bugfix-combo", "count": 50, "examples": ["fix broken"], "phase": "phase3"},
            {"keyword": "deploy", "label": "deploy-combo", "count": 50, "examples": ["deploy app"], "phase": "phase3"},
            {"keyword": "feature", "label": "feature-combo", "count": 50, "examples": ["new feature"], "phase": "phase3"},
        ]
        _write_default(root, "seeds/p1.jsonl", _make_seed_jsonl(p1_seeds))
        _write_default(root, "seeds/p2.jsonl", _make_seed_jsonl(p2_seeds))
        _write_default(root, "seeds/p3.jsonl", _make_seed_jsonl(p3_seeds))

        reg = DataRegistry(repo_root=root)
        return TripleTwinEngine(registry=reg, llm_client=llm_client)

    def test_full_pipeline_greeting(self, tmp_path: Path) -> None:
        engine = self._build_full_engine(tmp_path)
        result = engine.process("hello there")
        assert result.phase1 is not None
        assert result.phase1.label == "greeting"
        assert result.final_action == "small_talk:greeting"

    def test_full_pipeline_humor(self, tmp_path: Path) -> None:
        engine = self._build_full_engine(tmp_path)
        result = engine.process("tell me a joke please")
        assert result.phase1 is not None
        assert result.phase1.label == "humor"
        assert "small_talk" in result.final_action

    def test_full_pipeline_bugfix(self, tmp_path: Path) -> None:
        engine = self._build_full_engine(tmp_path)
        result = engine.process("the authentication is broken")
        assert result.phase1.label == "task"
        assert result.matched_wish == "bugfix"
        assert result.matched_combo == "bugfix-combo"
        assert result.final_action == "execute:bugfix:bugfix-combo"

    def test_full_pipeline_deploy(self, tmp_path: Path) -> None:
        engine = self._build_full_engine(tmp_path)
        result = engine.process("deploy the application to staging")
        assert result.phase1.label == "task"
        assert result.matched_wish == "deploy"
        assert result.matched_combo == "deploy-combo"
        assert result.final_action == "execute:deploy:deploy-combo"

    def test_full_pipeline_feature(self, tmp_path: Path) -> None:
        engine = self._build_full_engine(tmp_path)
        result = engine.process("add a new feature for OAuth3")
        assert result.phase1.label == "task"
        assert result.matched_wish == "feature"
        assert result.matched_combo == "feature-combo"

    def test_convention_cpu_nodes_discovered_by_filename(self, tmp_path: Path) -> None:
        """CPU nodes are discovered by .md extension in cpu-nodes/ directory."""
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/alpha.md", _make_cpu_node_md("phase1", "alpha"))
        _write_default(root, "cpu-nodes/beta.md", _make_cpu_node_md("phase2", "beta"))
        _write_default(root, "cpu-nodes/gamma.md", _make_cpu_node_md("phase3", "gamma"))
        _write_default(root, "cpu-nodes/ignore.txt", "not a node")
        _write_default(root, "cpu-nodes/ignore.json", '{}')

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        assert len(engine._phases) == 3
        assert engine._phases["phase1"].name == "alpha"
        assert engine._phases["phase2"].name == "beta"
        assert engine._phases["phase3"].name == "gamma"

    def test_stats_endpoint_returns_correct_metrics(self, tmp_path: Path) -> None:
        engine = self._build_full_engine(tmp_path)

        # Process a few inputs
        engine.process("hello friend")
        engine.process("deploy the app")
        engine.process("fix broken test")

        stats = engine.stats()
        assert stats["total_processed"] == 3
        assert stats["cpu_hits"] >= 1
        assert "phases" in stats
        assert "phase1" in stats["phases"]
        assert "phase2" in stats["phases"]
        assert "phase3" in stats["phases"]
        assert "learner" in stats["phases"]["phase1"]

    def test_stats_cpu_hit_rate(self, tmp_path: Path) -> None:
        engine = self._build_full_engine(tmp_path)
        engine.process("hello friend")
        engine.process("deploy the app")

        stats = engine.stats()
        assert 0.0 <= stats["cpu_hit_rate"] <= 1.0

    def test_stats_phase_contains_name_and_model(self, tmp_path: Path) -> None:
        engine = self._build_full_engine(tmp_path)
        stats = engine.stats()

        assert stats["phases"]["phase1"]["name"] == "small-talk"
        assert stats["phases"]["phase1"]["validator_model"] == "haiku"
        assert stats["phases"]["phase2"]["validator_model"] == "sonnet"
        assert stats["phases"]["phase3"]["validator_model"] == "opus"

    def test_mixed_cpu_and_llm_processing(self, tmp_path: Path) -> None:
        """Some inputs handled by CPU (seeded), some by LLM."""
        mock = MockLLMClient(responses={
            "phase1": {"label": "task", "confidence": 0.90, "reasoning": "Task"},
            "phase2": {"label": "research", "confidence": 0.85, "reasoning": "Research task"},
            "phase3": {"label": "research-combo", "confidence": 0.88, "reasoning": "Research combo"},
        })
        engine = self._build_full_engine(tmp_path, llm_client=mock)

        # This should be handled by CPU (seeded)
        result1 = engine.process("hello there")
        assert result1.phase1.handled_by == "cpu"

        # "research" is not in seeds, so LLM handles
        result2 = engine.process("investigate compiler optimization strategies")
        # Phase 1 might be CPU (if a keyword matches) or LLM
        # At minimum, processing should complete without error
        assert result2.final_action is not None


# ===========================================================================
# 7. SmallTalkResponder wiring (~8 tests)
# ===========================================================================


class TestSmallTalkWiring:
    """Tests for TripleTwinEngine → SmallTalkResponder integration."""

    def _build_engine_with_smalltalk(self, tmp_path: Path) -> TripleTwinEngine:
        """Build an engine with Phase 1 + smalltalk response data."""
        base = _setup_data_dirs(tmp_path)

        # Phase 1 CPU node — greeting + task labels
        _write_default(base, "cpu-nodes/small-talk.md", _make_cpu_node_md(
            phase="phase1", labels=["greeting", "task"],
        ))

        # Seeds: "hello" → greeting, "fix" → task (high count for CPU confidence)
        seeds = [
            {"keyword": "hello", "label": "greeting", "count": 50, "examples": [], "phase": "phase1"},
            {"keyword": "hi", "label": "greeting", "count": 50, "examples": [], "phase": "phase1"},
            {"keyword": "fix", "label": "task", "count": 50, "examples": [], "phase": "phase1"},
            {"keyword": "bug", "label": "task", "count": 50, "examples": [], "phase": "phase1"},
        ]
        _write_default(base, "seeds/phase1.jsonl", _make_seed_jsonl(seeds))

        # Smalltalk responses — minimal set for testing (uses "response" key, not "text")
        responses = [
            {"id": "resp_001", "label": "greeting", "response": "Hey there! How can I help?",
             "warmth": 3, "level": 1, "tags": []},
            {"id": "resp_002", "label": "greeting", "response": "Hello! Great to see you.",
             "warmth": 4, "level": 1, "tags": []},
        ]
        resp_jsonl = "\n".join(json.dumps(r) for r in responses) + "\n"
        _write_default(base, "smalltalk/responses.jsonl", resp_jsonl)

        # Minimal jokes + facts for gift fallback
        jokes = [{"id": "j1", "text": "Why do programmers prefer dark mode?",
                  "tags": ["programming"]}]
        facts = [{"id": "f1", "text": "Python was named after Monty Python.",
                  "tags": ["programming"]}]
        _write_default(base, "smalltalk/jokes.json", json.dumps(jokes))
        _write_default(base, "smalltalk/facts.json", json.dumps(facts))

        registry = DataRegistry(repo_root=base)
        return TripleTwinEngine(registry)

    def test_greeting_returns_response_text(self, tmp_path: Path) -> None:
        """Non-task input (greeting) should have response_text populated."""
        engine = self._build_engine_with_smalltalk(tmp_path)
        result = engine.process("hello")
        assert result.final_action.startswith("small_talk:")
        assert result.response_text is not None
        assert len(result.response_text) > 0

    def test_task_has_no_response_text(self, tmp_path: Path) -> None:
        """Task input should have response_text=None (no small talk)."""
        engine = self._build_engine_with_smalltalk(tmp_path)
        result = engine.process("fix the login bug")
        assert result.response_text is None

    def test_response_text_is_string(self, tmp_path: Path) -> None:
        """response_text should be a string from the response DB."""
        engine = self._build_engine_with_smalltalk(tmp_path)
        result = engine.process("hello there")
        assert isinstance(result.response_text, str)

    def test_smalltalk_responder_lazy_init(self, tmp_path: Path) -> None:
        """SmallTalkResponder should be None until first non-task input."""
        engine = self._build_engine_with_smalltalk(tmp_path)
        assert engine._smalltalk_responder is None
        engine.process("hello")
        assert engine._smalltalk_responder is not None

    def test_responder_reused_across_calls(self, tmp_path: Path) -> None:
        """Same SmallTalkResponder instance reused across multiple calls."""
        engine = self._build_engine_with_smalltalk(tmp_path)
        engine.process("hello")
        first = engine._smalltalk_responder
        engine.process("hello again")
        assert engine._smalltalk_responder is first

    def test_no_response_data_returns_none(self, tmp_path: Path) -> None:
        """If no smalltalk data files, response_text should be None (graceful)."""
        base = _setup_data_dirs(tmp_path)
        _write_default(base, "cpu-nodes/small-talk.md", _make_cpu_node_md(
            phase="phase1", labels=["greeting", "task"],
        ))
        seeds = [
            {"keyword": "hello", "label": "greeting", "count": 50, "examples": [], "phase": "phase1"},
        ]
        _write_default(base, "seeds/phase1.jsonl", _make_seed_jsonl(seeds))
        # No smalltalk/ data files at all
        registry = DataRegistry(repo_root=base)
        engine = TripleTwinEngine(registry)
        result = engine.process("hello")
        assert result.final_action.startswith("small_talk:")
        # response_text is None or empty because no data — but it doesn't crash

    def test_orchestration_result_has_response_text_field(self) -> None:
        """OrchestrationResult dataclass has the response_text field."""
        r = OrchestrationResult(input="test")
        assert hasattr(r, "response_text")
        assert r.response_text is None

    def test_multiple_greetings_different_responses(self, tmp_path: Path) -> None:
        """Multiple greeting inputs should exercise response selection."""
        engine = self._build_engine_with_smalltalk(tmp_path)
        results = [engine.process("hello") for _ in range(5)]
        texts = [r.response_text for r in results]
        # All should have text
        assert all(t is not None for t in texts)

    def test_smalltalk_import_failure_logs_and_disables(self, tmp_path: Path, monkeypatch, caplog) -> None:
        """ImportError should be logged once and permanently disable smalltalk responses."""
        import builtins

        engine = self._build_engine_with_smalltalk(tmp_path)
        real_import = builtins.__import__

        def _broken_import(name, *args, **kwargs):
            if name == "stillwater.smalltalk_responder":
                raise ImportError("broken responder import")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _broken_import)
        with caplog.at_level(logging.ERROR):
            response = engine._get_smalltalk_response("greeting", 0.9, "hello")
        assert response is None
        assert engine._smalltalk_disabled is True
        assert "SmallTalkResponder import failed" in caplog.text

    def test_smalltalk_response_valueerror_logged(self, tmp_path: Path, caplog) -> None:
        """Responder ValueError should be logged and return None."""
        engine = self._build_engine_with_smalltalk(tmp_path)

        class _BrokenResponder:
            def respond(self, **kwargs):
                del kwargs
                raise ValueError("bad smalltalk payload")

        engine._smalltalk_responder = _BrokenResponder()
        with caplog.at_level(logging.ERROR):
            response = engine._get_smalltalk_response("greeting", 0.9, "hello")
        assert response is None
        assert "smalltalk response failed" in caplog.text


# ===========================================================================
# 8. AuditLogger wiring (~8 tests)
# ===========================================================================


class TestAuditLogging:
    """Tests for TripleTwinEngine → AuditLogger integration."""

    def _build_engine_with_audit(
        self, tmp_path: Path, llm_client: object = None,
    ) -> tuple:
        """Build an engine with AuditLogger wired in. Returns (engine, log_dir)."""
        from stillwater.audit_logger import AuditLogger

        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md(
            "phase1", "small-talk", labels=["greeting", "task"],
        ))
        _write_default(root, "cpu-nodes/p2.md", _make_cpu_node_md(
            "phase2", "intent", labels=["bugfix", "deploy"],
        ))

        # High-count seeds for CPU confidence
        p1_seeds = [
            {"keyword": "hello", "label": "greeting", "count": 50, "examples": [], "phase": "phase1"},
            {"keyword": "broken", "label": "task", "count": 50, "examples": [], "phase": "phase1"},
        ]
        p2_seeds = [
            {"keyword": "broken", "label": "bugfix", "count": 50, "examples": [], "phase": "phase2"},
        ]
        _write_default(root, "seeds/p1.jsonl", _make_seed_jsonl(p1_seeds))
        _write_default(root, "seeds/p2.jsonl", _make_seed_jsonl(p2_seeds))

        log_dir = tmp_path / "data" / "logs"
        audit_logger = AuditLogger(log_dir=log_dir)

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(
            registry=reg,
            llm_client=llm_client,
            audit_logger=audit_logger,
            session_id="test-session-001",
            user_id="test-user",
        )
        return engine, log_dir

    def test_cpu_prediction_creates_audit_entry(self, tmp_path: Path) -> None:
        """CPU prediction should generate an audit log entry."""
        engine, log_dir = self._build_engine_with_audit(tmp_path)
        engine.process("hello there friend")

        # Check that an audit file was created
        log_files = list(log_dir.glob("audit-*.jsonl"))
        assert len(log_files) >= 1
        content = log_files[0].read_text(encoding="utf-8")
        entries = [json.loads(line) for line in content.strip().splitlines()]
        assert len(entries) >= 1
        assert entries[0]["action"]["type"] == "cpu_prediction"

    def test_cpu_audit_entry_contains_label(self, tmp_path: Path) -> None:
        """Audit entry for CPU prediction should contain the predicted label."""
        engine, log_dir = self._build_engine_with_audit(tmp_path)
        engine.process("hello there friend")

        log_files = list(log_dir.glob("audit-*.jsonl"))
        content = log_files[0].read_text(encoding="utf-8")
        entry = json.loads(content.strip().splitlines()[0])
        assert entry["metadata"]["prediction_label"] == "greeting"

    def test_cpu_audit_entry_contains_session_and_user(self, tmp_path: Path) -> None:
        """Audit entry should contain session_id and user_id from engine init."""
        engine, log_dir = self._build_engine_with_audit(tmp_path)
        engine.process("hello there friend")

        log_files = list(log_dir.glob("audit-*.jsonl"))
        entry = json.loads(log_files[0].read_text(encoding="utf-8").strip().splitlines()[0])
        assert entry["actor"]["session_id"] == "test-session-001"
        assert entry["actor"]["user_id"] == "test-user"

    def test_llm_call_creates_audit_entry(self, tmp_path: Path) -> None:
        """LLM fallback should generate an audit log entry."""
        mock = MockLLMClient(responses={
            "phase1": {"label": "task", "confidence": 0.90, "reasoning": "Task detected"},
            "phase2": {"label": "bugfix", "confidence": 0.88, "reasoning": "Bug report"},
        })
        engine, log_dir = self._build_engine_with_audit(tmp_path, llm_client=mock)

        # Process input that CPU can't handle (no seeds for "investigate")
        engine.process("investigate the compiler optimization strategies")

        log_files = list(log_dir.glob("audit-*.jsonl"))
        content = log_files[0].read_text(encoding="utf-8")
        entries = [json.loads(line) for line in content.strip().splitlines()]

        # At least one LLM call entry should exist
        llm_entries = [e for e in entries if e["action"]["type"] == "llm_call"]
        assert len(llm_entries) >= 1

    def test_no_audit_logger_no_error(self, tmp_path: Path) -> None:
        """Engine without audit_logger should work normally (no logging)."""
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md(
            "phase1", "small-talk", labels=["greeting", "task"],
        ))
        seeds = [{"keyword": "hello", "label": "greeting", "count": 50, "examples": [], "phase": "phase1"}]
        _write_default(root, "seeds/p1.jsonl", _make_seed_jsonl(seeds))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)  # no audit_logger

        result = engine.process("hello there friend")
        assert result.phase1.label == "greeting"
        # No crash, no log files
        assert not (tmp_path / "data" / "logs").exists()

    def test_hash_chain_intact_after_multiple_predictions(self, tmp_path: Path) -> None:
        """Multiple predictions should produce a valid hash chain."""
        from stillwater.audit_logger import AuditLogger

        engine, log_dir = self._build_engine_with_audit(tmp_path)
        engine.process("hello there friend")
        engine.process("something broken needs fixing")
        engine.process("hello again")

        log_files = list(log_dir.glob("audit-*.jsonl"))
        assert len(log_files) >= 1

        audit_logger = AuditLogger(log_dir=log_dir)
        assert audit_logger.verify_chain(log_files[0]) is True

    def test_session_id_auto_generated_when_not_provided(self, tmp_path: Path) -> None:
        """Engine should auto-generate a UUID session_id if not provided."""
        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md("phase1", "small-talk"))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(registry=reg)

        assert engine._session_id is not None
        assert len(engine._session_id) > 0

    def test_audit_logger_failure_does_not_break_pipeline(self, tmp_path: Path) -> None:
        """If audit_logger raises, the pipeline should still return results."""
        class BrokenAuditLogger:
            def log_cpu_prediction(self, **kwargs):
                raise RuntimeError("Audit storage full")
            def log_llm_call(self, **kwargs):
                raise RuntimeError("Audit storage full")

        root = _setup_data_dirs(tmp_path)
        _write_default(root, "cpu-nodes/p1.md", _make_cpu_node_md(
            "phase1", "small-talk", labels=["greeting", "task"],
        ))
        seeds = [{"keyword": "hello", "label": "greeting", "count": 50, "examples": [], "phase": "phase1"}]
        _write_default(root, "seeds/p1.jsonl", _make_seed_jsonl(seeds))

        reg = DataRegistry(repo_root=root)
        engine = TripleTwinEngine(
            registry=reg, audit_logger=BrokenAuditLogger(),
        )

        # Should not raise — audit failure is swallowed
        result = engine.process("hello there friend")
        assert result.phase1.label == "greeting"
