"""test_phase1_seeds.py -- Tests for seed file integrity and structure.

Validates the seeds JSONL file exists, parses correctly, has expected
distribution, and covers required labels.

Rung: 641 -- deterministic, no network, no LLM.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from stillwater.cpu_learner import CPULearner

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "phase1_shared", Path(__file__).resolve().with_name("phase1_shared.py")
)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PHASE1_LABELS = _mod.PHASE1_LABELS
SEED_CONFIDENCE = _mod.SEED_CONFIDENCE


# ===========================================================================
# File existence and parsing
# ===========================================================================


class TestSeedsFileIntegrity:
    """Basic integrity checks for the seeds JSONL file."""

    def test_seeds_file_exists(self, seeds_path: Path) -> None:
        """data/default/seeds/small-talk-seeds.jsonl must exist."""
        assert seeds_path.exists(), f"Seeds file not found: {seeds_path}"

    def test_seeds_file_not_empty(self, seeds_path: Path) -> None:
        content = seeds_path.read_text(encoding="utf-8").strip()
        assert len(content) > 0, "Seeds file is empty"

    def test_seeds_parse_jsonl(self, seeds_path: Path) -> None:
        """Every non-empty line must be valid JSON."""
        content = seeds_path.read_text(encoding="utf-8")
        line_count = 0
        for i, line in enumerate(content.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                assert isinstance(record, dict), f"Line {i}: expected dict, got {type(record)}"
                line_count += 1
            except json.JSONDecodeError as exc:
                pytest.fail(f"Line {i}: invalid JSON -- {exc}")

        assert line_count > 0, "No valid JSONL records found"

    def test_seeds_have_required_fields(self, seeds_records: list) -> None:
        """Each seed record must have: keyword, label, count, phase."""
        required = {"keyword", "label", "count", "phase"}
        for i, record in enumerate(seeds_records):
            missing = required - set(record.keys())
            assert not missing, (
                f"Seed #{i+1} ({record.get('keyword', '?')}): missing fields {missing}"
            )

    def test_seeds_all_phase1(self, seeds_records: list) -> None:
        """All seeds in small-talk-seeds.jsonl should be phase1."""
        for record in seeds_records:
            assert record["phase"] == "phase1", (
                f"Seed '{record['keyword']}' has phase={record['phase']}, expected phase1"
            )

    def test_seeds_keyword_not_empty(self, seeds_records: list) -> None:
        """No seed should have an empty keyword."""
        for record in seeds_records:
            assert record["keyword"].strip(), (
                f"Seed has empty keyword: {record}"
            )


# ===========================================================================
# Distribution analysis
# ===========================================================================


class TestSeedsDistribution:
    """Validate seed distribution across labels."""

    def test_seeds_distribution_no_single_label_above_90pct(
        self, seeds_records: list
    ) -> None:
        """Flag if any single label has > 90% of seeds (extreme imbalance)."""
        label_counts = Counter(r["label"] for r in seeds_records)
        total = len(seeds_records)
        for label, count in label_counts.items():
            pct = count / total * 100
            # This is a soft assertion: 87.8% task is the known BUG-P1-005
            # but we flag if it gets even worse (>90%)
            if pct > 90.0:
                pytest.fail(
                    f"Label '{label}' has {count}/{total} seeds ({pct:.1f}%) -- "
                    f"extreme imbalance (>90%)"
                )

    def test_seeds_have_at_least_6_labels(self, seeds_records: list) -> None:
        """The seeds should cover at least 6 distinct labels."""
        labels = set(r["label"] for r in seeds_records)
        assert len(labels) >= 6, (
            f"Expected at least 6 labels in seeds, got {len(labels)}: {sorted(labels)}"
        )

    def test_seeds_task_is_majority(self, seeds_records: list) -> None:
        """Document that 'task' is the dominant label (known BUG-P1-005)."""
        label_counts = Counter(r["label"] for r in seeds_records)
        max_label = label_counts.most_common(1)[0]
        assert max_label[0] == "task", (
            f"Expected 'task' as majority label, got '{max_label[0]}'"
        )

    def test_seeds_count_per_label(self, seeds_records: list) -> None:
        """Print seed counts per label for audit visibility."""
        label_counts = Counter(r["label"] for r in seeds_records)
        # Verify the counts match known state
        assert label_counts["greeting"] >= 1
        assert label_counts["gratitude"] >= 1
        assert label_counts["emotional_positive"] >= 1
        assert label_counts["emotional_negative"] >= 1
        assert label_counts["humor"] >= 1
        assert label_counts["small_talk"] >= 1
        assert label_counts["task"] >= 40  # known: 43


# ===========================================================================
# Stop word collision check
# ===========================================================================


class TestSeedsNoStopWordCollision:
    """Verify that seed keywords are not stop words (they would be filtered)."""

    def test_no_seed_keyword_is_stop_word(self, seeds_records: list) -> None:
        """A seed keyword that is also a stop word would never match user input."""
        for record in seeds_records:
            kw = record["keyword"]
            extracted = CPULearner.extract_keywords(kw)
            # The keyword itself should survive extraction
            assert kw in extracted, (
                f"Seed keyword '{kw}' (label={record['label']}) does not survive "
                f"keyword extraction -- it may be a stop word or too short. "
                f"Extracted from '{kw}': {extracted}"
            )

    def test_no_seed_keyword_shorter_than_3(self, seeds_records: list) -> None:
        """Seed keywords with len < 3 would be filtered by the extraction gate."""
        for record in seeds_records:
            kw = record["keyword"]
            assert len(kw) >= 3, (
                f"Seed keyword '{kw}' has len={len(kw)} < 3, would be filtered"
            )


# ===========================================================================
# Label coverage
# ===========================================================================


class TestAllLabelsHaveSeeds:
    """Verify which Phase 1 labels have at least 1 seed."""

    # Labels that SHOULD have seeds based on the cpu-node definition
    EXPECTED_SEEDED_LABELS = {
        "greeting", "gratitude", "emotional_positive", "emotional_negative",
        "humor", "small_talk", "task",
    }

    # Labels known to have ZERO seeds (documented bugs)
    KNOWN_UNSEEDED_LABELS = {"question", "off_domain", "unknown"}

    def test_expected_labels_have_seeds(self, seeds_records: list) -> None:
        """Each expected label should have at least 1 seed."""
        label_set = set(r["label"] for r in seeds_records)
        for label in self.EXPECTED_SEEDED_LABELS:
            assert label in label_set, (
                f"Label '{label}' has zero seeds -- expected at least 1"
            )

    def test_known_unseeded_labels_confirmed(self, seeds_records: list) -> None:
        """Confirm that known-unseeded labels still have no seeds."""
        label_set = set(r["label"] for r in seeds_records)
        for label in self.KNOWN_UNSEEDED_LABELS:
            assert label not in label_set, (
                f"Label '{label}' unexpectedly has seeds now. "
                f"If this was intentional, update KNOWN_UNSEEDED_LABELS."
            )

    def test_all_seed_labels_are_valid_phase1_labels(
        self, seeds_records: list
    ) -> None:
        """Every label in the seeds file should be a recognized Phase 1 label."""
        # The cpu-node defines these labels (plus off_domain which is in the node
        # but not in our PHASE1_LABELS constant -- include it here)
        valid_labels = set(PHASE1_LABELS) | {"off_domain"}
        for record in seeds_records:
            label = record["label"]
            assert label in valid_labels, (
                f"Seed keyword '{record['keyword']}' has unrecognized label "
                f"'{label}' -- expected one of {sorted(valid_labels)}"
            )

    def test_seeds_confidence_matches_formula(self, seeds_records: list) -> None:
        """All seeds with count=25 should have confidence ~0.8824."""
        for record in seeds_records:
            if record.get("count") == 25:
                expected = SEED_CONFIDENCE
                actual = record.get("confidence", 0)
                assert abs(actual - expected) < 0.001, (
                    f"Seed '{record['keyword']}': confidence={actual}, "
                    f"expected ~{expected:.4f} for count=25"
                )

    def test_seeds_no_duplicate_keywords(self, seeds_records: list) -> None:
        """Each keyword should appear only once in the seeds file."""
        keywords = [r["keyword"] for r in seeds_records]
        seen = set()
        duplicates = []
        for kw in keywords:
            if kw in seen:
                duplicates.append(kw)
            seen.add(kw)
        assert not duplicates, (
            f"Duplicate seed keywords found: {duplicates}"
        )
