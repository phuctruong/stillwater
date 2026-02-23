#!/usr/bin/env python3
"""
ABCD Test Harness — Generic Multi-Variant Evaluation Framework

Evaluates LLM models, skills, recipes, prompts, and swarm configurations
across N variants on a test suite, collecting metrics and computing statistics.

Design Goals:
- Pure Python stdlib (no pip dependencies for the harness itself)
- Configurable execution backend (default: /api/cli/run, swappable for any callable)
- Statistical rigor: paired t-test + Bonferroni correction for multiple comparisons
- Deterministic + reproducible results (seed-based)
- Streaming results (writes to JSONL immediately during long runs)

Usage:
    harness = ABCDHarness(seed=641)
    harness.add_variant(Variant(id="A", name="haiku-baseline", config={"model": "haiku"}))
    harness.add_variant(Variant(id="B", name="sonnet-skills", config={"model": "sonnet"}))
    harness.add_task(Task(id="t1", prompt="Sum [1,2,3]", expected_output="6"))
    results = harness.run(repeats=3)
    report = harness.report()

rung_target: 641
"""

from __future__ import annotations

import json
import math
import random
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional


# ============================================================
# Data Models
# ============================================================

@dataclass
class Variant:
    """A single configuration variant (A, B, C, D...) to be evaluated."""
    id: str           # Short label: "A", "B", "C", "D" or descriptive string
    name: str         # Human-readable name: "haiku-baseline", "sonnet-with-prime-coder"
    config: dict      # Arbitrary config: {"model": "haiku", "skill": "prime-coder", ...}

    def __post_init__(self):
        if not self.id:
            raise ValueError("Variant.id must not be empty")
        if not self.name:
            raise ValueError("Variant.name must not be empty")


@dataclass
class Task:
    """A single test case to run against all variants."""
    id: str                       # Unique task ID: "t1", "coding-01", etc.
    prompt: str                   # The input prompt/question
    expected_output: Optional[str] = None   # Ground truth (optional; used for auto-scoring)
    tags: list[str] = field(default_factory=list)  # Categorisation tags: ["coding", "hard"]
    metadata: dict = field(default_factory=dict)   # Extra data passed to run_variant

    def __post_init__(self):
        if not self.id:
            raise ValueError("Task.id must not be empty")
        if not self.prompt:
            raise ValueError("Task.prompt must not be empty")


@dataclass
class Result:
    """A single execution result: one variant × one task × one repeat."""
    variant_id: str
    task_id: str
    repeat_index: int            # 0-based repeat number
    output: str                  # Raw LLM / backend output
    latency_ms: float            # Wall-clock execution time in milliseconds
    tokens: int                  # Token count (0 if unavailable)
    quality_score: float         # Score in [0, 1]; NaN if not scoreable
    cost_usd: float              # Estimated cost in USD (0.0 if unavailable)
    error: Optional[str] = None  # Error message if execution failed; None on success
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metadata: dict = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.error is None

    def to_dict(self) -> dict:
        d = asdict(self)
        # JSON-safe NaN handling
        if math.isnan(self.quality_score):
            d["quality_score"] = None
        return d


# ============================================================
# Default Backend: /api/cli/run
# ============================================================

def _default_run_variant(variant_config: dict, task: Task) -> dict:
    """
    Default execution backend using the admin server's /api/cli/run endpoint.

    Returns a dict with keys: output (str), tokens (int), cost_usd (float)

    variant_config keys (all optional):
        model       — LLM model name (e.g. "haiku", "sonnet")
        skill       — Skill name to inject (e.g. "prime-coder")
        prompt_template — Jinja-like template; use {prompt} as placeholder
        endpoint    — Override the default http://localhost:8080/api/cli/run
        timeout     — Request timeout in seconds (default: 60)
    """
    endpoint = variant_config.get("endpoint", "http://localhost:8080/api/cli/run")
    timeout = variant_config.get("timeout", 60)

    # Build the effective prompt
    template = variant_config.get("prompt_template", "{prompt}")
    effective_prompt = template.replace("{prompt}", task.prompt)

    payload = {
        "prompt": effective_prompt,
        "model": variant_config.get("model", "haiku"),
        "skill": variant_config.get("skill"),
        "task_id": task.id,
        "metadata": task.metadata,
    }
    # Strip None values
    payload = {k: v for k, v in payload.items() if v is not None}

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "output": data.get("output", data.get("result", str(data))),
                "tokens": data.get("tokens", data.get("token_count", 0)),
                "cost_usd": data.get("cost_usd", data.get("cost", 0.0)),
            }
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Backend unreachable at {endpoint}: {exc}") from exc


# ============================================================
# Default Scorer: string similarity vs expected_output
# ============================================================

def _default_scorer(output: str, task: Task, variant_config: dict) -> float:
    """
    Default quality scorer.

    Returns a float in [0, 1]:
    - If task.expected_output is None → returns float('nan') (unscored)
    - Otherwise → normalised sequence-match ratio (longest common subsequence)
      using a simple stdlib-only implementation.

    Swap this out for an LLM-as-judge scorer in production.
    """
    if task.expected_output is None:
        return float("nan")

    return _lcs_ratio(output.strip(), task.expected_output.strip())


def _lcs_ratio(a: str, b: str) -> float:
    """
    Longest Common Subsequence (character-level) ratio using stdlib only.
    Returns len(LCS) / max(len(a), len(b)), bounded in [0, 1].

    Uses dynamic programming (DP table). For long strings (>2000 chars)
    we truncate to keep tests fast.
    """
    MAX_LEN = 2000
    a = a[:MAX_LEN]
    b = b[:MAX_LEN]

    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0

    m, n = len(a), len(b)
    # Two-row DP to reduce memory
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev, curr = curr, [0] * (n + 1)

    lcs_len = prev[n]
    return lcs_len / max(m, n)


# ============================================================
# Statistical Functions
# ============================================================

def _mean(values: list[float]) -> float:
    """Arithmetic mean of a list of floats. Returns nan for empty list."""
    valid = [v for v in values if not math.isnan(v)]
    if not valid:
        return float("nan")
    return sum(valid) / len(valid)


def _stdev(values: list[float], mean: Optional[float] = None) -> float:
    """Sample standard deviation. Returns nan for < 2 elements."""
    valid = [v for v in values if not math.isnan(v)]
    if len(valid) < 2:
        return float("nan")
    m = mean if mean is not None else _mean(valid)
    variance = sum((x - m) ** 2 for x in valid) / (len(valid) - 1)
    return math.sqrt(variance)


def _t_critical(df: int, alpha: float = 0.05) -> float:
    """
    Two-tailed t-critical value using a lookup table for common df values.
    Falls back to the normal approximation (z = 1.96) for df > 120.

    This is a stdlib-only approximation sufficient for significance testing.
    """
    # Student's t critical values for alpha=0.05 two-tailed
    # Source: standard t-tables
    _TABLE = {
        1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
        6: 2.447,  7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
        16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
        25: 2.060, 30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980,
    }
    if df in _TABLE:
        return _TABLE[df]
    if df > 120:
        return 1.960  # Normal approximation
    # Interpolate between nearest entries
    keys = sorted(_TABLE.keys())
    for i in range(len(keys) - 1):
        if keys[i] <= df <= keys[i + 1]:
            lo, hi = keys[i], keys[i + 1]
            t = (df - lo) / (hi - lo)
            return _TABLE[lo] + t * (_TABLE[hi] - _TABLE[lo])
    return 1.960


def compute_significance(
    results_a: list[float],
    results_b: list[float],
    alpha: float = 0.05,
) -> dict:
    """
    Compute paired t-test between two sets of quality scores.

    Paired test: each element in results_a corresponds to the same task
    as the corresponding element in results_b.

    Args:
        results_a: Quality scores for variant A (in task order).
        results_b: Quality scores for variant B (in task order).
        alpha:     Significance level (default 0.05).

    Returns a dict with:
        n               — number of valid pairs
        mean_diff       — mean(A) - mean(B)
        t_stat          — t-statistic
        p_value         — two-tailed p-value (approximated via t-distribution CDF)
        significant     — bool: p_value < alpha
        confidence_interval_95 — (lower, upper) of the difference
        effect_size     — Cohen's d for the paired differences
    """
    # Filter to valid (non-NaN) paired observations
    pairs = [
        (a, b)
        for a, b in zip(results_a, results_b)
        if not (math.isnan(a) or math.isnan(b))
    ]

    if len(pairs) < 2:
        return {
            "n": len(pairs),
            "mean_diff": float("nan"),
            "t_stat": float("nan"),
            "p_value": float("nan"),
            "significant": False,
            "confidence_interval_95": (float("nan"), float("nan")),
            "effect_size": float("nan"),
            "error": "insufficient_data",
        }

    diffs = [a - b for a, b in pairs]
    n = len(diffs)
    mean_d = _mean(diffs)
    std_d = _stdev(diffs, mean_d)

    if std_d == 0.0 or math.isnan(std_d):
        return {
            "n": n,
            "mean_diff": mean_d,
            "t_stat": 0.0,
            "p_value": 1.0,
            "significant": False,
            "confidence_interval_95": (0.0, 0.0),
            "effect_size": 0.0,
            "error": None,
        }

    se = std_d / math.sqrt(n)
    t_stat = mean_d / se
    df = n - 1

    # Approximate two-tailed p-value via the t-distribution CDF
    # Using the regularised incomplete beta function approximation (stdlib-only)
    p_value = _t_pvalue(t_stat, df)

    # 95% confidence interval on the mean difference
    t_crit = _t_critical(df, alpha)
    ci_lower = mean_d - t_crit * se
    ci_upper = mean_d + t_crit * se

    # Cohen's d for paired differences: mean_diff / std_diff
    effect_size = mean_d / std_d

    return {
        "n": n,
        "mean_diff": round(mean_d, 6),
        "t_stat": round(t_stat, 4),
        "p_value": round(p_value, 6),
        "significant": p_value < alpha,
        "confidence_interval_95": (round(ci_lower, 6), round(ci_upper, 6)),
        "effect_size": round(effect_size, 4),
        "error": None,
    }


def _t_pvalue(t: float, df: int) -> float:
    """
    Two-tailed p-value for t-statistic with df degrees of freedom.

    Uses the regularised incomplete beta function I_x(a, b) where
    x = df / (df + t^2), a = df/2, b = 0.5.

    This is a pure-Python approximation accurate to ~4 decimal places
    for typical sample sizes used in ABCD testing.
    """
    t_abs = abs(t)
    x = df / (df + t_abs ** 2)
    p_one_tail = 0.5 * _betai(df / 2.0, 0.5, x)
    p_two_tail = min(1.0, 2.0 * p_one_tail)
    return p_two_tail


def _betai(a: float, b: float, x: float) -> float:
    """
    Regularised incomplete beta function I_x(a, b) using continued fraction.
    Valid for 0 <= x <= 1. Used internally for t-distribution CDF.
    """
    if x < 0.0 or x > 1.0:
        raise ValueError(f"x must be in [0,1], got {x}")
    if x == 0.0:
        return 0.0
    if x == 1.0:
        return 1.0

    # Use symmetry to improve convergence: I_x(a,b) = 1 - I_{1-x}(b,a)
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - _betai(b, a, 1.0 - x)

    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(math.log(x) * a + math.log(1.0 - x) * b - lbeta) / a

    # Lentz's continued fraction algorithm
    # Reference: Numerical Recipes §6.4
    MAX_ITER = 200
    EPS = 3.0e-7
    FPMIN = 1.0e-30

    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d

    for m in range(1, MAX_ITER + 1):
        m2 = 2 * m
        # Even step
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        c = 1.0 + aa / c
        if abs(d) < FPMIN:
            d = FPMIN
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        # Odd step
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        c = 1.0 + aa / c
        if abs(d) < FPMIN:
            d = FPMIN
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < EPS:
            break

    return front * h


def bonferroni_correction(p_values: list[float], alpha: float = 0.05) -> dict:
    """
    Apply Bonferroni correction for multiple comparisons.

    For k simultaneous tests, the adjusted significance threshold is alpha/k.
    Equivalently, the adjusted p-values are p_i * k (capped at 1.0).

    Args:
        p_values: List of raw p-values from pairwise comparisons.
        alpha:    Family-wise error rate (default 0.05).

    Returns:
        adjusted_p_values   — list of corrected p-values
        adjusted_alpha      — Bonferroni-corrected threshold
        significant_mask    — bool list: True where adjusted p < alpha
        num_tests           — number of tests
    """
    k = len(p_values)
    if k == 0:
        return {
            "adjusted_p_values": [],
            "adjusted_alpha": alpha,
            "significant_mask": [],
            "num_tests": 0,
        }

    adjusted_alpha = alpha / k
    adjusted_p = [min(1.0, p * k) if not math.isnan(p) else float("nan") for p in p_values]
    significant = [
        (not math.isnan(p)) and (p < alpha)
        for p in adjusted_p
    ]

    return {
        "adjusted_p_values": [round(p, 6) if not math.isnan(p) else None for p in adjusted_p],
        "adjusted_alpha": round(adjusted_alpha, 6),
        "significant_mask": significant,
        "num_tests": k,
    }


# ============================================================
# Main Harness
# ============================================================

class ABCDHarness:
    """
    Multi-variant test harness for evaluating LLM configurations.

    Workflow:
        1. add_variant(...)  — register variants A, B, C, D...
        2. add_task(...)     — register test tasks
        3. run(repeats=3)    — execute all variant × task × repeat combinations
        4. report()          — compute stats and return structured report dict

    The run_variant callable is injected at construction time, defaulting to
    the admin server's /api/cli/run endpoint. Swap it for unit-testable mocks
    or direct LLM API callers.

    Example with a mock backend (no LLM needed):

        def mock_runner(config, task):
            return {"output": "42", "tokens": 10, "cost_usd": 0.0}

        harness = ABCDHarness(run_variant_fn=mock_runner)
    """

    def __init__(
        self,
        run_variant_fn: Optional[Callable[[dict, Task], dict]] = None,
        scorer_fn: Optional[Callable[[str, Task, dict], float]] = None,
        seed: int = 641,
        output_dir: Optional[str] = None,
    ):
        """
        Args:
            run_variant_fn: Callable(config, task) → {output, tokens, cost_usd}.
                            Defaults to _default_run_variant (admin server).
            scorer_fn:      Callable(output, task, config) → float in [0,1] or NaN.
                            Defaults to _default_scorer (LCS ratio vs expected_output).
            seed:           Random seed for reproducibility.
            output_dir:     Directory to stream JSONL results into. If None,
                            results are only kept in memory.
        """
        self._run_variant_fn = run_variant_fn or _default_run_variant
        self._scorer_fn = scorer_fn or _default_scorer
        self._seed = seed
        self._output_dir = Path(output_dir) if output_dir else None

        self._variants: list[Variant] = []
        self._tasks: list[Task] = []
        self._results: list[Result] = []

        random.seed(seed)

    # ----------------------------------------------------------
    # Registration
    # ----------------------------------------------------------

    def add_variant(self, variant: Variant) -> "ABCDHarness":
        """Register a variant. Returns self for chaining."""
        ids = {v.id for v in self._variants}
        if variant.id in ids:
            raise ValueError(f"Duplicate variant id: {variant.id!r}")
        self._variants.append(variant)
        return self

    def add_task(self, task: Task) -> "ABCDHarness":
        """Register a task. Returns self for chaining."""
        ids = {t.id for t in self._tasks}
        if task.id in ids:
            raise ValueError(f"Duplicate task id: {task.id!r}")
        self._tasks.append(task)
        return self

    # ----------------------------------------------------------
    # Execution
    # ----------------------------------------------------------

    def run(self, repeats: int = 3) -> list[Result]:
        """
        Execute all variant × task combinations, repeated `repeats` times.

        Each combination is independent; failures are recorded (not raised)
        so the full matrix completes even if some calls fail.

        Results are appended to self._results and optionally streamed to
        output_dir/results.jsonl.

        Args:
            repeats: Number of times each variant × task pair is repeated.
                     Minimum 1. Use >= 3 for meaningful statistics.

        Returns:
            List of Result objects (also stored in self._results).
        """
        if not self._variants:
            raise ValueError("No variants registered. Call add_variant() first.")
        if not self._tasks:
            raise ValueError("No tasks registered. Call add_task() first.")
        if repeats < 1:
            raise ValueError(f"repeats must be >= 1, got {repeats}")

        jsonl_file = None
        if self._output_dir:
            self._output_dir.mkdir(parents=True, exist_ok=True)
            jsonl_file = self._output_dir / "results.jsonl"

        new_results: list[Result] = []

        for repeat_idx in range(repeats):
            for variant in self._variants:
                for task in self._tasks:
                    result = self._execute_one(variant, task, repeat_idx)
                    new_results.append(result)
                    self._results.append(result)

                    # Stream to disk immediately
                    if jsonl_file:
                        with jsonl_file.open("a", encoding="utf-8") as fh:
                            fh.write(json.dumps(result.to_dict()) + "\n")

        return new_results

    def _execute_one(
        self, variant: Variant, task: Task, repeat_idx: int
    ) -> Result:
        """Execute a single variant × task × repeat combination."""
        start_ns = time.perf_counter_ns()
        error: Optional[str] = None
        output = ""
        tokens = 0
        cost_usd = 0.0

        try:
            backend_result = self._run_variant_fn(variant.config, task)
            output = str(backend_result.get("output", ""))
            tokens = int(backend_result.get("tokens", 0))
            cost_usd = float(backend_result.get("cost_usd", 0.0))
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"

        latency_ms = (time.perf_counter_ns() - start_ns) / 1_000_000

        # Score quality
        if error is None:
            try:
                quality_score = self._scorer_fn(output, task, variant.config)
            except Exception as exc:
                quality_score = float("nan")
                error = f"scoring_error: {exc}"
        else:
            quality_score = float("nan")

        return Result(
            variant_id=variant.id,
            task_id=task.id,
            repeat_index=repeat_idx,
            output=output,
            latency_ms=round(latency_ms, 3),
            tokens=tokens,
            quality_score=quality_score,
            cost_usd=cost_usd,
            error=error,
        )

    # ----------------------------------------------------------
    # Reporting
    # ----------------------------------------------------------

    def report(self) -> dict:
        """
        Compute statistics and produce a structured report.

        Returns a dict with:
            variants        — list of variant configs
            tasks           — list of task ids
            summary         — per-variant aggregate metrics
            pairwise        — pairwise significance tests (all combinations)
            bonferroni      — Bonferroni correction applied to pairwise p-values
            winner          — id of the variant with highest mean quality_score
                              (None if no scored results)
            raw_results     — list of all Result dicts
        """
        if not self._results:
            return {
                "variants": [asdict(v) for v in self._variants],
                "tasks": [asdict(t) for t in self._tasks],
                "summary": {},
                "pairwise": {},
                "bonferroni": {},
                "winner": None,
                "raw_results": [],
            }

        # --- Aggregate per-variant ---
        summary: dict[str, dict] = {}
        scores_by_variant: dict[str, list[float]] = {}
        latencies_by_variant: dict[str, list[float]] = {}

        for v in self._variants:
            v_results = [r for r in self._results if r.variant_id == v.id]
            scores = [r.quality_score for r in v_results if not math.isnan(r.quality_score)]
            latencies = [r.latency_ms for r in v_results]
            tokens_list = [r.tokens for r in v_results]
            costs = [r.cost_usd for r in v_results]

            scores_by_variant[v.id] = [r.quality_score for r in v_results]
            latencies_by_variant[v.id] = latencies

            n_total = len(v_results)
            n_success = sum(1 for r in v_results if r.success)
            mean_quality = _mean(scores) if scores else float("nan")
            std_quality = _stdev(scores, mean_quality) if len(scores) >= 2 else float("nan")

            summary[v.id] = {
                "variant_name": v.name,
                "n_total": n_total,
                "n_success": n_success,
                "success_rate": round(n_success / n_total, 4) if n_total > 0 else float("nan"),
                "mean_quality": round(mean_quality, 4) if not math.isnan(mean_quality) else None,
                "std_quality": round(std_quality, 4) if not math.isnan(std_quality) else None,
                "mean_latency_ms": round(_mean(latencies), 2),
                "p50_latency_ms": round(_percentile(latencies, 50), 2),
                "p95_latency_ms": round(_percentile(latencies, 95), 2),
                "total_tokens": sum(tokens_list),
                "total_cost_usd": round(sum(costs), 6),
            }

        # --- Pairwise significance (all variant pairs) ---
        import itertools
        pairwise: dict[str, dict] = {}
        pair_p_values: list[float] = []
        pair_labels: list[str] = []

        variant_ids = [v.id for v in self._variants]
        for id_a, id_b in itertools.combinations(variant_ids, 2):
            label = f"{id_a}_vs_{id_b}"
            # Align by task order for paired test
            scores_a = _scores_aligned(self._results, id_a, self._tasks)
            scores_b = _scores_aligned(self._results, id_b, self._tasks)
            sig = compute_significance(scores_a, scores_b)
            pairwise[label] = sig
            pair_p_values.append(sig["p_value"] if not math.isnan(sig.get("p_value", float("nan"))) else float("nan"))
            pair_labels.append(label)

        # --- Bonferroni correction ---
        bonf = bonferroni_correction(pair_p_values)
        bonferroni_report = {
            "pairs": pair_labels,
            **bonf,
        }

        # --- Winner ---
        winner = None
        best_mean = float("-inf")
        for vid, s in summary.items():
            mq = s["mean_quality"]
            if mq is not None and not math.isnan(mq) and mq > best_mean:
                best_mean = mq
                winner = vid

        return {
            "variants": [asdict(v) for v in self._variants],
            "tasks": [asdict(t) for t in self._tasks],
            "summary": summary,
            "pairwise": pairwise,
            "bonferroni": bonferroni_report,
            "winner": winner,
            "raw_results": [r.to_dict() for r in self._results],
        }

    def save_report(self, output_path: str) -> None:
        """
        Compute and save the report as JSON to output_path.
        Also writes a markdown summary alongside it.
        """
        report = self.report()
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report, indent=2, default=_json_default), encoding="utf-8")

        # Write markdown summary
        md_path = p.with_suffix(".md")
        md_path.write_text(_render_markdown(report), encoding="utf-8")


# ============================================================
# Helpers
# ============================================================

def _scores_aligned(
    results: list[Result], variant_id: str, tasks: list[Task]
) -> list[float]:
    """
    Return quality scores for variant_id, one per task (averaged across repeats).
    Preserves task order for paired t-test alignment.
    Returns NaN for tasks with no valid scores.
    """
    aligned = []
    for task in tasks:
        task_results = [
            r for r in results
            if r.variant_id == variant_id and r.task_id == task.id
        ]
        scores = [r.quality_score for r in task_results if not math.isnan(r.quality_score)]
        aligned.append(_mean(scores) if scores else float("nan"))
    return aligned


def _percentile(values: list[float], pct: float) -> float:
    """Compute percentile (0-100) of a list using linear interpolation."""
    if not values:
        return float("nan")
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    idx = (pct / 100.0) * (n - 1)
    lo = int(idx)
    hi = lo + 1
    if hi >= n:
        return sorted_vals[-1]
    frac = idx - lo
    return sorted_vals[lo] + frac * (sorted_vals[hi] - sorted_vals[lo])


def _json_default(obj):
    """JSON serialiser for NaN/Inf → null."""
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _render_markdown(report: dict) -> str:
    """Render a human-readable markdown summary of the report."""
    lines = [
        "# ABCD Test Report",
        "",
        f"**Generated**: {datetime.utcnow().isoformat()}Z",
        "",
        "## Summary",
        "",
        "| Variant | Name | Success Rate | Mean Quality | Mean Latency (ms) | Total Cost ($) |",
        "|---------|------|-------------|-------------|-------------------|----------------|",
    ]

    for vid, s in report.get("summary", {}).items():
        mq = f"{s['mean_quality']:.4f}" if s["mean_quality"] is not None else "N/A"
        sr = f"{s['success_rate']:.1%}" if s.get("success_rate") is not None else "N/A"
        lines.append(
            f"| {vid} | {s['variant_name']} | {sr} | {mq} | "
            f"{s['mean_latency_ms']:.1f} | {s['total_cost_usd']:.6f} |"
        )

    winner = report.get("winner")
    if winner:
        lines += ["", f"**Winner**: `{winner}` ({report['summary'][winner]['variant_name']})"]

    # Pairwise results
    pairwise = report.get("pairwise", {})
    bonf = report.get("bonferroni", {})
    adj_p = bonf.get("adjusted_p_values", [])
    sig_mask = bonf.get("significant_mask", [])
    pair_labels = bonf.get("pairs", [])

    if pairwise:
        lines += [
            "",
            "## Pairwise Significance (Bonferroni-corrected)",
            "",
            "| Pair | n | Mean Diff | t-stat | Raw p | Adj p | Significant |",
            "|------|---|-----------|--------|-------|-------|-------------|",
        ]
        for i, (label, sig) in enumerate(pairwise.items()):
            adj = adj_p[i] if i < len(adj_p) else None
            is_sig = sig_mask[i] if i < len(sig_mask) else False
            md = sig.get("mean_diff")
            t = sig.get("t_stat")
            p = sig.get("p_value")
            lines.append(
                f"| {label} | {sig.get('n', '?')} | "
                f"{'N/A' if md is None or (isinstance(md, float) and math.isnan(md)) else f'{md:.4f}'} | "
                f"{'N/A' if t is None or (isinstance(t, float) and math.isnan(t)) else f'{t:.3f}'} | "
                f"{'N/A' if p is None or (isinstance(p, float) and math.isnan(p)) else f'{p:.4f}'} | "
                f"{'N/A' if adj is None else f'{adj:.4f}'} | "
                f"{'YES' if is_sig else 'no'} |"
            )

    return "\n".join(lines) + "\n"
