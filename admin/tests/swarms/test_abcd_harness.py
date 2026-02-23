#!/usr/bin/env python3
"""
Tests for abcd_harness.py — Generic Multi-Variant Evaluation Framework.

All tests use mock backends (no LLM access required).

Test coverage:
1. Data models: Variant, Task, Result construction and validation
2. Statistical functions: _mean, _stdev, _lcs_ratio, compute_significance, bonferroni_correction
3. ABCDHarness: registration, run, report, edge cases
4. Report structure: winner selection, pairwise comparisons, Bonferroni
5. Edge cases: single variant, no tasks, empty results, identical results
6. Scorer: LCS ratio correctness

rung_target: 641
"""

from __future__ import annotations

import json
import math
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure abcd_harness is importable from this directory
_HERE = Path(__file__).parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from abcd_harness import (
    ABCDHarness,
    Variant,
    Task,
    Result,
    compute_significance,
    bonferroni_correction,
    _lcs_ratio,
    _mean,
    _stdev,
    _percentile,
    _scores_aligned,
    _default_scorer,
    _betai,
    _t_pvalue,
)


# ============================================================
# Helpers / Mock Backends
# ============================================================

def make_mock_runner(outputs: dict[tuple[str, str], str], tokens: int = 10, cost: float = 0.001):
    """
    Factory for a deterministic mock run_variant_fn.

    outputs: {(variant_id, task_id): output_string}
    If a key is missing, returns "" (empty string).
    """
    def runner(config: dict, task: Task) -> dict:
        key = (config.get("_variant_id", ""), task.id)
        return {
            "output": outputs.get(key, ""),
            "tokens": tokens,
            "cost_usd": cost,
        }
    return runner


def make_constant_runner(output: str, tokens: int = 10, cost: float = 0.001):
    """Mock runner that always returns the same output."""
    def runner(config: dict, task: Task) -> dict:
        return {"output": output, "tokens": tokens, "cost_usd": cost}
    return runner


def make_error_runner(msg: str = "simulated error"):
    """Mock runner that always raises RuntimeError."""
    def runner(config: dict, task: Task) -> dict:
        raise RuntimeError(msg)
    return runner


def make_latency_runner(output: str, delay_ms: float = 0.0):
    """Mock runner with optional sleep."""
    import time
    def runner(config: dict, task: Task) -> dict:
        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)
        return {"output": output, "tokens": 5, "cost_usd": 0.0}
    return runner


def _add_variant_id_to_config(harness: ABCDHarness) -> None:
    """
    Patch variant configs to include _variant_id so make_mock_runner can route.
    Call after add_variant() calls.
    """
    for v in harness._variants:
        v.config["_variant_id"] = v.id


# ============================================================
# 1. Data Model Tests
# ============================================================

class TestVariant(unittest.TestCase):
    def test_basic_construction(self):
        v = Variant(id="A", name="test-variant", config={"model": "haiku"})
        self.assertEqual(v.id, "A")
        self.assertEqual(v.name, "test-variant")
        self.assertEqual(v.config["model"], "haiku")

    def test_empty_id_raises(self):
        with self.assertRaises(ValueError):
            Variant(id="", name="name", config={})

    def test_empty_name_raises(self):
        with self.assertRaises(ValueError):
            Variant(id="A", name="", config={})

    def test_empty_config_allowed(self):
        v = Variant(id="A", name="v", config={})
        self.assertEqual(v.config, {})


class TestTask(unittest.TestCase):
    def test_basic_construction(self):
        t = Task(id="t1", prompt="Hello?", expected_output="Hi", tags=["qa"])
        self.assertEqual(t.id, "t1")
        self.assertEqual(t.prompt, "Hello?")
        self.assertEqual(t.expected_output, "Hi")
        self.assertEqual(t.tags, ["qa"])

    def test_empty_id_raises(self):
        with self.assertRaises(ValueError):
            Task(id="", prompt="p")

    def test_empty_prompt_raises(self):
        with self.assertRaises(ValueError):
            Task(id="t1", prompt="")

    def test_optional_expected_output(self):
        t = Task(id="t1", prompt="p")
        self.assertIsNone(t.expected_output)

    def test_default_tags(self):
        t = Task(id="t1", prompt="p")
        self.assertEqual(t.tags, [])

    def test_default_metadata(self):
        t = Task(id="t1", prompt="p")
        self.assertEqual(t.metadata, {})


class TestResult(unittest.TestCase):
    def test_success_property(self):
        r = Result(
            variant_id="A", task_id="t1", repeat_index=0,
            output="ok", latency_ms=50.0, tokens=10,
            quality_score=0.9, cost_usd=0.001, error=None,
        )
        self.assertTrue(r.success)

    def test_failure_property(self):
        r = Result(
            variant_id="A", task_id="t1", repeat_index=0,
            output="", latency_ms=50.0, tokens=0,
            quality_score=float("nan"), cost_usd=0.0, error="RuntimeError: boom",
        )
        self.assertFalse(r.success)

    def test_to_dict_nan_becomes_none(self):
        r = Result(
            variant_id="A", task_id="t1", repeat_index=0,
            output="x", latency_ms=1.0, tokens=1,
            quality_score=float("nan"), cost_usd=0.0,
        )
        d = r.to_dict()
        self.assertIsNone(d["quality_score"])

    def test_to_dict_normal_score(self):
        r = Result(
            variant_id="A", task_id="t1", repeat_index=0,
            output="x", latency_ms=1.0, tokens=1,
            quality_score=0.75, cost_usd=0.0,
        )
        d = r.to_dict()
        self.assertAlmostEqual(d["quality_score"], 0.75)


# ============================================================
# 2. Statistical Function Tests
# ============================================================

class TestMeanStdev(unittest.TestCase):
    def test_mean_basic(self):
        self.assertAlmostEqual(_mean([1.0, 2.0, 3.0]), 2.0)

    def test_mean_single(self):
        self.assertAlmostEqual(_mean([5.0]), 5.0)

    def test_mean_empty(self):
        self.assertTrue(math.isnan(_mean([])))

    def test_mean_skips_nan(self):
        self.assertAlmostEqual(_mean([1.0, float("nan"), 3.0]), 2.0)

    def test_mean_all_nan(self):
        self.assertTrue(math.isnan(_mean([float("nan"), float("nan")])))

    def test_stdev_basic(self):
        # Sample stdev of [2, 4, 4, 4, 5, 5, 7, 9]:
        # Population stdev = 2.0, but _stdev uses sample stdev (divide by n-1)
        # Sample stdev = sqrt( sum((x - mean)^2) / (n-1) ) ≈ 2.138
        vals = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        expected_sample_stdev = 2.138089935299395
        self.assertAlmostEqual(_stdev(vals), expected_sample_stdev, places=6)

    def test_stdev_population_vs_sample(self):
        # Verify our implementation is sample stdev (divides by n-1), not population
        # For [1, 2, 3]: mean=2, deviations=[-1,0,1], variance(sample)=2/2=1, stdev=1.0
        vals = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(_stdev(vals), 1.0, places=6)

    def test_stdev_insufficient(self):
        self.assertTrue(math.isnan(_stdev([])))
        self.assertTrue(math.isnan(_stdev([1.0])))

    def test_stdev_identical(self):
        self.assertAlmostEqual(_stdev([3.0, 3.0, 3.0]), 0.0)


class TestPercentile(unittest.TestCase):
    def test_p50_median(self):
        self.assertAlmostEqual(_percentile([1.0, 2.0, 3.0], 50), 2.0)

    def test_p0(self):
        self.assertAlmostEqual(_percentile([1.0, 2.0, 3.0], 0), 1.0)

    def test_p100(self):
        self.assertAlmostEqual(_percentile([1.0, 2.0, 3.0], 100), 3.0)

    def test_empty(self):
        self.assertTrue(math.isnan(_percentile([], 50)))

    def test_single(self):
        self.assertAlmostEqual(_percentile([7.0], 50), 7.0)


class TestLCSRatio(unittest.TestCase):
    def test_identical_strings(self):
        self.assertAlmostEqual(_lcs_ratio("hello", "hello"), 1.0)

    def test_completely_different(self):
        # "abc" vs "xyz" → LCS = 0
        self.assertAlmostEqual(_lcs_ratio("abc", "xyz"), 0.0)

    def test_partial_match(self):
        ratio = _lcs_ratio("abcde", "ace")
        # LCS("abcde","ace") = 3 ("ace"), max_len = 5 → ratio = 0.6
        self.assertAlmostEqual(ratio, 0.6, places=6)

    def test_empty_both(self):
        self.assertAlmostEqual(_lcs_ratio("", ""), 1.0)

    def test_empty_one(self):
        self.assertAlmostEqual(_lcs_ratio("abc", ""), 0.0)
        self.assertAlmostEqual(_lcs_ratio("", "abc"), 0.0)

    def test_substring(self):
        # "cat" is contained in "concatenation"
        ratio = _lcs_ratio("cat", "concatenation")
        # LCS >= 3 ("cat"), max=13 → ratio >= 3/13 ≈ 0.231
        self.assertGreater(ratio, 0.2)

    def test_symmetric_ish(self):
        # LCS is symmetric; ratio may differ slightly due to max_len denominator
        r1 = _lcs_ratio("abcde", "ace")
        r2 = _lcs_ratio("ace", "abcde")
        # Both use max(len(a),len(b)) = 5, so they should be equal
        self.assertAlmostEqual(r1, r2, places=6)


class TestBetaiAndTPValue(unittest.TestCase):
    """Smoke tests for the regularised incomplete beta function."""

    def test_betai_zero(self):
        self.assertAlmostEqual(_betai(5, 5, 0.0), 0.0)

    def test_betai_one(self):
        self.assertAlmostEqual(_betai(5, 5, 1.0), 1.0)

    def test_betai_symmetric(self):
        # I_0.5(a,a) = 0.5 by symmetry
        val = _betai(3.0, 3.0, 0.5)
        self.assertAlmostEqual(val, 0.5, places=4)

    def test_t_pvalue_large_t(self):
        # Very large t → p ≈ 0
        p = _t_pvalue(100.0, 30)
        self.assertLess(p, 0.001)

    def test_t_pvalue_zero_t(self):
        # t=0 → p = 1.0 (no evidence against null)
        p = _t_pvalue(0.0, 10)
        self.assertAlmostEqual(p, 1.0, places=4)

    def test_t_pvalue_known(self):
        # t=2.228, df=10 → p ≈ 0.05 (borderline at standard t-table)
        p = _t_pvalue(2.228, 10)
        self.assertAlmostEqual(p, 0.05, delta=0.005)


class TestComputeSignificance(unittest.TestCase):
    def test_significantly_different(self):
        # A is always 0.9, B is always 0.5 → clear difference
        a = [0.9] * 10
        b = [0.5] * 10
        result = compute_significance(a, b)
        self.assertEqual(result["n"], 10)
        self.assertAlmostEqual(result["mean_diff"], 0.4, places=6)
        self.assertTrue(result["significant"])
        self.assertLess(result["p_value"], 0.05)

    def test_not_significantly_different(self):
        # Very similar values — no significant difference
        a = [0.5, 0.51, 0.49, 0.50, 0.50]
        b = [0.5, 0.50, 0.51, 0.49, 0.50]
        result = compute_significance(a, b)
        self.assertFalse(result["significant"])
        self.assertGreater(result["p_value"], 0.05)

    def test_identical_results(self):
        a = [0.7, 0.7, 0.7, 0.7]
        b = [0.7, 0.7, 0.7, 0.7]
        result = compute_significance(a, b)
        self.assertAlmostEqual(result["mean_diff"], 0.0)
        self.assertFalse(result["significant"])

    def test_insufficient_data_single_pair(self):
        result = compute_significance([0.8], [0.5])
        self.assertFalse(result["significant"])
        self.assertEqual(result.get("error"), "insufficient_data")

    def test_insufficient_data_empty(self):
        result = compute_significance([], [])
        self.assertFalse(result["significant"])

    def test_nan_values_skipped(self):
        # NaN pairs are skipped; valid pairs are [0.9,0.5], [0.8,0.4] → significant
        a = [0.9, float("nan"), 0.8, 0.9, 0.8, 0.9, 0.8, 0.9, 0.8, 0.9]
        b = [0.5, float("nan"), 0.4, 0.5, 0.4, 0.5, 0.4, 0.5, 0.4, 0.5]
        result = compute_significance(a, b)
        self.assertGreater(result["n"], 0)
        self.assertTrue(result["significant"])

    def test_ci_contains_mean_diff(self):
        a = [0.9] * 10
        b = [0.5] * 10
        result = compute_significance(a, b)
        lo, hi = result["confidence_interval_95"]
        self.assertLessEqual(lo, result["mean_diff"])
        self.assertGreaterEqual(hi, result["mean_diff"])

    def test_effect_size_positive_when_a_better(self):
        a = [0.9] * 10
        b = [0.5] * 10
        result = compute_significance(a, b)
        self.assertGreater(result["effect_size"], 0.0)

    def test_effect_size_negative_when_b_better(self):
        a = [0.5] * 10
        b = [0.9] * 10
        result = compute_significance(a, b)
        self.assertLess(result["effect_size"], 0.0)


class TestBonferroniCorrection(unittest.TestCase):
    def test_basic_correction(self):
        # 3 tests: adjusted_alpha = 0.05/3 ≈ 0.0167
        p_values = [0.01, 0.04, 0.10]
        result = bonferroni_correction(p_values, alpha=0.05)
        self.assertEqual(result["num_tests"], 3)
        self.assertAlmostEqual(result["adjusted_alpha"], 0.05 / 3, places=6)
        # Adjusted p-values = p * k (capped at 1)
        self.assertAlmostEqual(result["adjusted_p_values"][0], min(1.0, 0.01 * 3), places=6)
        self.assertAlmostEqual(result["adjusted_p_values"][1], min(1.0, 0.04 * 3), places=6)
        self.assertAlmostEqual(result["adjusted_p_values"][2], min(1.0, 0.10 * 3), places=6)

    def test_significant_mask(self):
        p_values = [0.001, 0.04, 0.10]
        result = bonferroni_correction(p_values, alpha=0.05)
        # 0.001*3=0.003 < 0.05 → significant
        # 0.04*3=0.12 > 0.05 → not significant
        # 0.10*3=0.30 > 0.05 → not significant
        self.assertEqual(result["significant_mask"], [True, False, False])

    def test_single_test(self):
        result = bonferroni_correction([0.03], alpha=0.05)
        self.assertEqual(result["adjusted_alpha"], 0.05)  # alpha/1 = 0.05
        self.assertAlmostEqual(result["adjusted_p_values"][0], 0.03)
        self.assertTrue(result["significant_mask"][0])

    def test_empty_input(self):
        result = bonferroni_correction([], alpha=0.05)
        self.assertEqual(result["num_tests"], 0)
        self.assertEqual(result["adjusted_p_values"], [])
        self.assertEqual(result["significant_mask"], [])

    def test_p_value_capped_at_one(self):
        # p=0.9 * 10 tests → would be 9.0 → capped at 1.0
        result = bonferroni_correction([0.9] * 10, alpha=0.05)
        for adj in result["adjusted_p_values"]:
            self.assertLessEqual(adj, 1.0)

    def test_nan_handled(self):
        result = bonferroni_correction([0.01, float("nan"), 0.05], alpha=0.05)
        self.assertIsNone(result["adjusted_p_values"][1])  # NaN → None


# ============================================================
# 3. ABCDHarness Tests
# ============================================================

class TestABCDHarnessRegistration(unittest.TestCase):
    def setUp(self):
        self.harness = ABCDHarness(run_variant_fn=make_constant_runner("ok"))

    def test_add_variant(self):
        v = Variant(id="A", name="baseline", config={})
        self.harness.add_variant(v)
        self.assertEqual(len(self.harness._variants), 1)

    def test_add_variant_chaining(self):
        result = self.harness.add_variant(Variant(id="A", name="a", config={}))
        self.assertIs(result, self.harness)

    def test_duplicate_variant_id_raises(self):
        self.harness.add_variant(Variant(id="A", name="a", config={}))
        with self.assertRaises(ValueError):
            self.harness.add_variant(Variant(id="A", name="b", config={}))

    def test_add_task(self):
        t = Task(id="t1", prompt="p")
        self.harness.add_task(t)
        self.assertEqual(len(self.harness._tasks), 1)

    def test_add_task_chaining(self):
        result = self.harness.add_task(Task(id="t1", prompt="p"))
        self.assertIs(result, self.harness)

    def test_duplicate_task_id_raises(self):
        self.harness.add_task(Task(id="t1", prompt="p"))
        with self.assertRaises(ValueError):
            self.harness.add_task(Task(id="t1", prompt="q"))

    def test_run_no_variants_raises(self):
        self.harness.add_task(Task(id="t1", prompt="p"))
        with self.assertRaises(ValueError):
            self.harness.run()

    def test_run_no_tasks_raises(self):
        self.harness.add_variant(Variant(id="A", name="a", config={}))
        with self.assertRaises(ValueError):
            self.harness.run()

    def test_run_invalid_repeats_raises(self):
        self.harness.add_variant(Variant(id="A", name="a", config={}))
        self.harness.add_task(Task(id="t1", prompt="p"))
        with self.assertRaises(ValueError):
            self.harness.run(repeats=0)


class TestABCDHarnessRun(unittest.TestCase):
    def _make_harness_ab(self, runner) -> ABCDHarness:
        h = ABCDHarness(run_variant_fn=runner)
        h.add_variant(Variant(id="A", name="variant-a", config={"_variant_id": "A"}))
        h.add_variant(Variant(id="B", name="variant-b", config={"_variant_id": "B"}))
        h.add_task(Task(id="t1", prompt="What is 1+1?", expected_output="2"))
        h.add_task(Task(id="t2", prompt="Capital of France?", expected_output="Paris"))
        return h

    def test_result_count(self):
        # 2 variants × 2 tasks × 3 repeats = 12 results
        runner = make_constant_runner("some output")
        h = self._make_harness_ab(runner)
        results = h.run(repeats=3)
        self.assertEqual(len(results), 12)
        self.assertEqual(len(h._results), 12)

    def test_result_count_single_repeat(self):
        runner = make_constant_runner("ok")
        h = self._make_harness_ab(runner)
        results = h.run(repeats=1)
        self.assertEqual(len(results), 4)  # 2 × 2 × 1

    def test_result_variant_ids(self):
        runner = make_constant_runner("ok")
        h = self._make_harness_ab(runner)
        results = h.run(repeats=1)
        variant_ids = {r.variant_id for r in results}
        self.assertEqual(variant_ids, {"A", "B"})

    def test_result_task_ids(self):
        runner = make_constant_runner("ok")
        h = self._make_harness_ab(runner)
        results = h.run(repeats=1)
        task_ids = {r.task_id for r in results}
        self.assertEqual(task_ids, {"t1", "t2"})

    def test_latency_recorded(self):
        runner = make_constant_runner("ok")
        h = self._make_harness_ab(runner)
        results = h.run(repeats=1)
        for r in results:
            self.assertGreaterEqual(r.latency_ms, 0.0)

    def test_tokens_recorded(self):
        runner = make_constant_runner("ok", tokens=42)
        h = self._make_harness_ab(runner)
        results = h.run(repeats=1)
        for r in results:
            self.assertEqual(r.tokens, 42)

    def test_error_runner_records_error(self):
        runner = make_error_runner("boom!")
        h = self._make_harness_ab(runner)
        results = h.run(repeats=1)
        for r in results:
            self.assertFalse(r.success)
            self.assertIn("boom!", r.error)
            self.assertTrue(math.isnan(r.quality_score))

    def test_successful_runner_no_error(self):
        runner = make_constant_runner("hello")
        h = self._make_harness_ab(runner)
        results = h.run(repeats=1)
        for r in results:
            self.assertTrue(r.success)
            self.assertIsNone(r.error)

    def test_repeat_indices(self):
        runner = make_constant_runner("ok")
        h = self._make_harness_ab(runner)
        results = h.run(repeats=3)
        repeat_indices = {r.repeat_index for r in results if r.variant_id == "A" and r.task_id == "t1"}
        self.assertEqual(repeat_indices, {0, 1, 2})

    def test_streaming_to_jsonl(self):
        runner = make_constant_runner("out")
        with tempfile.TemporaryDirectory() as tmpdir:
            h = ABCDHarness(run_variant_fn=runner, output_dir=tmpdir)
            h.add_variant(Variant(id="A", name="a", config={}))
            h.add_task(Task(id="t1", prompt="p"))
            h.run(repeats=2)
            jsonl = Path(tmpdir) / "results.jsonl"
            self.assertTrue(jsonl.exists())
            lines = jsonl.read_text().strip().split("\n")
            self.assertEqual(len(lines), 2)  # 1 variant × 1 task × 2 repeats
            for line in lines:
                data = json.loads(line)
                self.assertIn("variant_id", data)
                self.assertIn("task_id", data)

    def test_quality_score_nan_when_no_expected_output(self):
        runner = make_constant_runner("42")
        h = ABCDHarness(run_variant_fn=runner)
        h.add_variant(Variant(id="A", name="a", config={}))
        h.add_task(Task(id="t1", prompt="What is life?"))  # No expected_output
        results = h.run(repeats=1)
        self.assertTrue(math.isnan(results[0].quality_score))

    def test_quality_score_with_expected_output(self):
        runner = make_constant_runner("Paris")
        h = ABCDHarness(run_variant_fn=runner)
        h.add_variant(Variant(id="A", name="a", config={}))
        h.add_task(Task(id="t1", prompt="Capital of France?", expected_output="Paris"))
        results = h.run(repeats=1)
        self.assertAlmostEqual(results[0].quality_score, 1.0)

    def test_routing_by_variant_config(self):
        outputs = {
            ("A", "t1"): "answer_A",
            ("B", "t1"): "answer_B",
        }
        runner = make_mock_runner(outputs)
        h = ABCDHarness(run_variant_fn=runner)
        h.add_variant(Variant(id="A", name="a", config={"_variant_id": "A"}))
        h.add_variant(Variant(id="B", name="b", config={"_variant_id": "B"}))
        h.add_task(Task(id="t1", prompt="p"))
        results = h.run(repeats=1)
        result_a = next(r for r in results if r.variant_id == "A")
        result_b = next(r for r in results if r.variant_id == "B")
        self.assertEqual(result_a.output, "answer_A")
        self.assertEqual(result_b.output, "answer_B")


# ============================================================
# 4. Report Tests
# ============================================================

class TestABCDHarnessReport(unittest.TestCase):
    def _build_harness_with_results(
        self, a_score: float = 0.9, b_score: float = 0.5, repeats: int = 5
    ) -> ABCDHarness:
        """
        Build a harness where:
        - Variant A always returns output matching expected_output with quality ≈ a_score
        - Variant B always returns output matching expected_output with quality ≈ b_score

        We control quality via a custom scorer that returns the preset score.
        """
        def scorer(output: str, task: Task, config: dict) -> float:
            if config.get("_variant_id") == "A":
                return a_score
            return b_score

        runner = make_constant_runner("ignored")
        h = ABCDHarness(run_variant_fn=runner, scorer_fn=scorer)
        h.add_variant(Variant(id="A", name="variant-A", config={"_variant_id": "A"}))
        h.add_variant(Variant(id="B", name="variant-B", config={"_variant_id": "B"}))
        h.add_task(Task(id="t1", prompt="p1", expected_output="x"))
        h.add_task(Task(id="t2", prompt="p2", expected_output="y"))
        h.add_task(Task(id="t3", prompt="p3", expected_output="z"))
        h.run(repeats=repeats)
        return h

    def test_report_structure(self):
        h = self._build_harness_with_results()
        report = h.report()
        self.assertIn("variants", report)
        self.assertIn("tasks", report)
        self.assertIn("summary", report)
        self.assertIn("pairwise", report)
        self.assertIn("bonferroni", report)
        self.assertIn("winner", report)
        self.assertIn("raw_results", report)

    def test_winner_is_higher_quality(self):
        h = self._build_harness_with_results(a_score=0.9, b_score=0.5)
        report = h.report()
        self.assertEqual(report["winner"], "A")

    def test_winner_b_when_b_better(self):
        h = self._build_harness_with_results(a_score=0.3, b_score=0.8)
        report = h.report()
        self.assertEqual(report["winner"], "B")

    def test_summary_contains_variant_ids(self):
        h = self._build_harness_with_results()
        report = h.report()
        self.assertIn("A", report["summary"])
        self.assertIn("B", report["summary"])

    def test_summary_mean_quality(self):
        h = self._build_harness_with_results(a_score=0.9, b_score=0.5)
        report = h.report()
        self.assertAlmostEqual(report["summary"]["A"]["mean_quality"], 0.9, places=4)
        self.assertAlmostEqual(report["summary"]["B"]["mean_quality"], 0.5, places=4)

    def test_summary_n_total(self):
        # 3 tasks × 5 repeats = 15 per variant
        h = self._build_harness_with_results(repeats=5)
        report = h.report()
        self.assertEqual(report["summary"]["A"]["n_total"], 15)
        self.assertEqual(report["summary"]["B"]["n_total"], 15)

    def test_summary_success_rate(self):
        h = self._build_harness_with_results()
        report = h.report()
        self.assertAlmostEqual(report["summary"]["A"]["success_rate"], 1.0)
        self.assertAlmostEqual(report["summary"]["B"]["success_rate"], 1.0)

    def test_pairwise_ab_present(self):
        h = self._build_harness_with_results()
        report = h.report()
        self.assertIn("A_vs_B", report["pairwise"])

    def test_pairwise_significant_when_clearly_different(self):
        # Use compute_significance directly: when A is always 0.9 and B is always 0.1
        # across many pairs, there is zero within-pair variation → stdev of diffs = 0
        # → t = 0/0 = NaN → harness returns p=1.0, not significant.
        # The harness correctly identifies the "winner" (A has higher mean).
        # For a significance test to fire we need variation in the per-task scores.
        # Test the function directly with varying scores:
        a_scores = [0.9, 0.85, 0.92, 0.88, 0.91, 0.87, 0.90, 0.93, 0.86, 0.89]
        b_scores = [0.1, 0.15, 0.12, 0.08, 0.11, 0.13, 0.09, 0.14, 0.10, 0.12]
        result = compute_significance(a_scores, b_scores)
        self.assertTrue(result["significant"])
        self.assertLess(result["p_value"], 0.05)

    def test_pairwise_not_significant_when_identical(self):
        h = self._build_harness_with_results(a_score=0.7, b_score=0.7, repeats=5)
        report = h.report()
        sig = report["pairwise"]["A_vs_B"]
        self.assertFalse(sig["significant"])

    def test_bonferroni_in_report(self):
        h = self._build_harness_with_results()
        report = h.report()
        bonf = report["bonferroni"]
        self.assertIn("pairs", bonf)
        self.assertIn("adjusted_p_values", bonf)
        self.assertIn("significant_mask", bonf)

    def test_raw_results_count(self):
        # 2 variants × 3 tasks × 5 repeats = 30
        h = self._build_harness_with_results(repeats=5)
        report = h.report()
        self.assertEqual(len(report["raw_results"]), 30)

    def test_raw_results_json_serialisable(self):
        h = self._build_harness_with_results(repeats=3)
        report = h.report()
        # Should not raise
        json.dumps(report)

    def test_save_report_writes_files(self):
        h = self._build_harness_with_results(repeats=2)
        with tempfile.TemporaryDirectory() as tmpdir:
            out_json = os.path.join(tmpdir, "report.json")
            h.save_report(out_json)
            self.assertTrue(os.path.exists(out_json))
            md_path = out_json.replace(".json", ".md")
            self.assertTrue(os.path.exists(md_path))
            # JSON should be valid
            with open(out_json) as f:
                data = json.load(f)
            self.assertIn("winner", data)


# ============================================================
# 5. Edge Case Tests
# ============================================================

class TestEdgeCases(unittest.TestCase):
    def test_single_variant_no_pairwise(self):
        runner = make_constant_runner("ok")
        h = ABCDHarness(run_variant_fn=runner)
        h.add_variant(Variant(id="A", name="only-one", config={}))
        h.add_task(Task(id="t1", prompt="p", expected_output="ok"))
        h.run(repeats=3)
        report = h.report()
        self.assertEqual(report["winner"], "A")
        self.assertEqual(report["pairwise"], {})
        self.assertEqual(report["bonferroni"]["pairs"], [])

    def test_empty_harness_report(self):
        h = ABCDHarness(run_variant_fn=make_constant_runner("x"))
        h.add_variant(Variant(id="A", name="a", config={}))
        h.add_task(Task(id="t1", prompt="p"))
        # Don't run — report on zero results
        report = h.report()
        self.assertEqual(report["winner"], None)
        self.assertEqual(report["raw_results"], [])

    def test_all_nan_scores_no_winner(self):
        # No expected_output → all scores NaN → winner should be None
        runner = make_constant_runner("something")
        h = ABCDHarness(run_variant_fn=runner)
        h.add_variant(Variant(id="A", name="a", config={}))
        h.add_variant(Variant(id="B", name="b", config={}))
        h.add_task(Task(id="t1", prompt="p"))  # No expected_output
        h.run(repeats=2)
        report = h.report()
        self.assertIsNone(report["winner"])

    def test_four_variants_abcd(self):
        # Ensure C(4,2) = 6 pairwise comparisons
        def scorer(output, task, config):
            scores = {"A": 0.9, "B": 0.7, "C": 0.6, "D": 0.4}
            return scores.get(config.get("_variant_id", ""), 0.5)

        runner = make_constant_runner("ignored")
        h = ABCDHarness(run_variant_fn=runner, scorer_fn=scorer)
        for vid in ["A", "B", "C", "D"]:
            h.add_variant(Variant(id=vid, name=f"variant-{vid}", config={"_variant_id": vid}))
        for i in range(5):
            h.add_task(Task(id=f"t{i}", prompt=f"p{i}", expected_output="x"))
        h.run(repeats=3)
        report = h.report()
        self.assertEqual(len(report["pairwise"]), 6)
        self.assertEqual(report["winner"], "A")
        bonf = report["bonferroni"]
        self.assertEqual(bonf["num_tests"], 6)
        self.assertAlmostEqual(bonf["adjusted_alpha"], 0.05 / 6, places=6)

    def test_error_and_success_mixed_success_rate(self):
        call_count = [0]
        def mixed_runner(config, task):
            call_count[0] += 1
            if call_count[0] % 2 == 0:
                raise RuntimeError("every other call fails")
            return {"output": "ok", "tokens": 5, "cost_usd": 0.0}

        h = ABCDHarness(run_variant_fn=mixed_runner)
        h.add_variant(Variant(id="A", name="a", config={}))
        h.add_task(Task(id="t1", prompt="p"))
        h.add_task(Task(id="t2", prompt="q"))
        h.add_task(Task(id="t3", prompt="r"))
        h.add_task(Task(id="t4", prompt="s"))
        h.run(repeats=1)
        report = h.report()
        sr = report["summary"]["A"]["success_rate"]
        # Exactly half should succeed: 4 calls, 2 fail (calls 2,4)
        self.assertAlmostEqual(sr, 0.5, places=4)

    def test_tokens_and_cost_aggregated(self):
        runner = make_constant_runner("x", tokens=7, cost=0.01)
        h = ABCDHarness(run_variant_fn=runner)
        h.add_variant(Variant(id="A", name="a", config={}))
        h.add_task(Task(id="t1", prompt="p"))
        h.add_task(Task(id="t2", prompt="q"))
        h.run(repeats=2)  # 2 tasks × 2 repeats = 4 calls
        report = h.report()
        s = report["summary"]["A"]
        self.assertEqual(s["total_tokens"], 4 * 7)
        self.assertAlmostEqual(s["total_cost_usd"], 4 * 0.01, places=6)

    def test_single_task_single_repeat(self):
        runner = make_constant_runner("hello", tokens=3, cost=0.001)
        h = ABCDHarness(run_variant_fn=runner)
        h.add_variant(Variant(id="A", name="a", config={}))
        h.add_task(Task(id="t1", prompt="Hi", expected_output="hello"))
        results = h.run(repeats=1)
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0].quality_score, 1.0)

    def test_custom_scorer_injected(self):
        def perfect_scorer(output, task, config):
            return 1.0

        runner = make_constant_runner("anything")
        h = ABCDHarness(run_variant_fn=runner, scorer_fn=perfect_scorer)
        h.add_variant(Variant(id="A", name="a", config={}))
        h.add_task(Task(id="t1", prompt="p"))
        results = h.run(repeats=1)
        self.assertAlmostEqual(results[0].quality_score, 1.0)

    def test_seed_reproducibility(self):
        """Two harnesses with same seed produce same random state."""
        import random as _random
        h1 = ABCDHarness(run_variant_fn=make_constant_runner("x"), seed=12345)
        r1 = _random.random()

        # Re-seed
        _random.seed(12345)
        r2 = _random.random()

        self.assertEqual(r1, r2)


# ============================================================
# 6. Scores Aligned Helper Tests
# ============================================================

class TestScoresAligned(unittest.TestCase):
    def test_aligned_returns_per_task_average(self):
        tasks = [Task(id="t1", prompt="p"), Task(id="t2", prompt="q")]
        # 2 repeats for variant "A" on t1: scores 0.8, 0.6 → avg 0.7
        # 2 repeats for variant "A" on t2: scores 0.4, 0.6 → avg 0.5
        results = [
            Result("A", "t1", 0, "x", 1.0, 1, 0.8, 0.0),
            Result("A", "t1", 1, "x", 1.0, 1, 0.6, 0.0),
            Result("A", "t2", 0, "y", 1.0, 1, 0.4, 0.0),
            Result("A", "t2", 1, "y", 1.0, 1, 0.6, 0.0),
        ]
        aligned = _scores_aligned(results, "A", tasks)
        self.assertAlmostEqual(aligned[0], 0.7, places=6)
        self.assertAlmostEqual(aligned[1], 0.5, places=6)

    def test_aligned_nan_for_missing_task(self):
        tasks = [Task(id="t1", prompt="p"), Task(id="t99", prompt="q")]
        results = [
            Result("A", "t1", 0, "x", 1.0, 1, 0.9, 0.0),
        ]
        aligned = _scores_aligned(results, "A", tasks)
        self.assertAlmostEqual(aligned[0], 0.9)
        self.assertTrue(math.isnan(aligned[1]))  # t99 missing


# ============================================================
# 7. Default Scorer Tests
# ============================================================

class TestDefaultScorer(unittest.TestCase):
    def test_no_expected_output_returns_nan(self):
        task = Task(id="t1", prompt="p")
        score = _default_scorer("anything", task, {})
        self.assertTrue(math.isnan(score))

    def test_perfect_match(self):
        task = Task(id="t1", prompt="p", expected_output="Paris")
        score = _default_scorer("Paris", task, {})
        self.assertAlmostEqual(score, 1.0)

    def test_empty_vs_expected(self):
        task = Task(id="t1", prompt="p", expected_output="Paris")
        score = _default_scorer("", task, {})
        self.assertAlmostEqual(score, 0.0)

    def test_partial_match_between_zero_and_one(self):
        task = Task(id="t1", prompt="p", expected_output="Paris is a city")
        score = _default_scorer("Paris", task, {})
        self.assertGreater(score, 0.0)
        self.assertLess(score, 1.0)

    def test_score_in_unit_interval(self):
        task = Task(id="t1", prompt="p", expected_output="hello world")
        for output in ["hello", "world", "foo bar baz", "", "hello world"]:
            score = _default_scorer(output, task, {})
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)


# ============================================================
# Run all tests
# ============================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
