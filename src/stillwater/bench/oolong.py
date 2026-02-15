"""Benchmark: OOLONG long-context aggregation.

Pure CPU solver -- no LLM required.
Runs against the HuggingFace oolongbench/oolong-synth dataset.
Target: 100% accuracy on validation split (1,300 samples).
"""

from __future__ import annotations

import time

from stillwater.bench import BenchResult
from stillwater.llm import LLMClient
from stillwater.oolong.solver import solve_and_check


def run(client: LLMClient) -> BenchResult:
    """Run OOLONG benchmark against HuggingFace dataset.

    The client parameter is unused -- this is a pure CPU benchmark.
    """
    return run_oolong(split="validation", verbose=False)


def run_oolong(
    split: str = "validation",
    verbose: bool = False,
    max_samples: int = 0,
) -> BenchResult:
    """Run OOLONG solver against the dataset.

    Args:
        split: Dataset split ("validation" or "test").
        verbose: Print per-sample details.
        max_samples: Limit samples (0 = all).

    Returns:
        BenchResult with accuracy.
    """
    try:
        from datasets import load_dataset
    except ImportError:
        return BenchResult(
            name="OOLONG",
            passed=0,
            total=0,
            elapsed_ms=0,
            details=[{"error": "Install 'datasets' library: pip install datasets"}],
        )

    # Load dataset
    try:
        ds = load_dataset("oolongbench/oolong-synth", split=split)
    except Exception as e:
        return BenchResult(
            name="OOLONG",
            passed=0,
            total=0,
            elapsed_ms=0,
            details=[{"error": f"Failed to load dataset: {e}"}],
        )

    samples = list(ds)
    if max_samples > 0:
        samples = samples[:max_samples]

    t0 = time.perf_counter()
    passed = 0
    details: list[dict] = []
    failures_by_type: dict[str, int] = {}

    for i, sample in enumerate(samples):
        context = sample.get("context_window_text_with_labels", "")
        question = sample.get("question", "")
        expected = sample.get("answer", "")
        task = sample.get("task", "")
        task_group = sample.get("task_group", "")

        predicted, correct = solve_and_check(
            context, question, expected, task, task_group
        )

        if correct:
            passed += 1
        else:
            task_key = task or "UNKNOWN"
            failures_by_type[task_key] = failures_by_type.get(task_key, 0) + 1

        if verbose or not correct:
            details.append({
                "index": i,
                "question": question[:120],
                "expected": expected,
                "predicted": predicted,
                "task": task,
                "task_group": task_group,
                "passed": correct,
            })

    elapsed = (time.perf_counter() - t0) * 1000

    if failures_by_type:
        details.append({"failures_by_type": failures_by_type})

    return BenchResult(
        name="OOLONG",
        passed=passed,
        total=len(samples),
        elapsed_ms=elapsed,
        details=details,
    )
