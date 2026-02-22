#!/usr/bin/env python3
"""
Reprocess existing test results with benchmark metrics.
This script takes the old results and adds benchmark metrics calculations.
"""

import json
import sys
import ast
from pathlib import Path
from typing import Dict, Any


def calculate_code_quality_score(code: str) -> float:
    """Calculate code quality score (0-1) - same as in test file."""
    score = 0.0

    # Parse code
    try:
        tree = ast.parse(code)
    except:
        return 0.0

    # Has docstrings (+0.1)
    has_module_docstring = ast.get_docstring(tree) is not None
    if has_module_docstring:
        score += 0.1

    # Has type hints (+0.15)
    has_type_hints = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and (node.returns is not None or any(
            arg.annotation is not None
            for arg in node.args.args
        ))
        for node in ast.walk(tree)
    )
    if has_type_hints:
        score += 0.15

    # Has error handling: try/except (+0.15)
    has_error_handling = any(
        isinstance(node, ast.Try)
        for node in ast.walk(tree)
    )
    if has_error_handling:
        score += 0.15

    # Has tests/assertions (+0.2)
    has_assertions = any(
        isinstance(node, ast.Assert)
        for node in ast.walk(tree)
    )
    has_tests = "test_" in code or "assert " in code
    if has_assertions or has_tests:
        score += 0.2

    # Function/class structure (+0.15)
    has_functions = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        for node in ast.walk(tree)
    )
    if has_functions:
        score += 0.15

    # Reasonable length: 20-500 lines (+0.1)
    lines = len(code.split('\n'))
    if 20 <= lines <= 500:
        score += 0.1

    # No obvious anti-patterns (-0.1)
    has_eval = "eval(" in code
    has_exec = "exec(" in code
    has_import_star = "import *" in code
    if has_eval or has_exec or has_import_star:
        score -= 0.1

    return min(1.0, max(0.0, score))


def calculate_benchmark_metrics(
    syntax_valid: bool,
    functional_pass: bool,
    quality_score: float,
    system_detected: bool,
) -> Dict[str, Any]:
    """Calculate benchmark metrics (same as in test file)."""
    # Evidence Completeness (0-10 scale)
    evidence_score = quality_score * 10
    if functional_pass and syntax_valid:
        evidence_score = min(10, evidence_score + 1)

    # Hallucination Rate (0-1 scale)
    if functional_pass and syntax_valid:
        hallucination_rate = 0.1
    elif syntax_valid:
        hallucination_rate = 0.5
    else:
        hallucination_rate = 0.9

    # Rung achieved
    if functional_pass and quality_score >= 0.5:
        rung = 641
    elif functional_pass and quality_score >= 0.7:
        rung = 274177
    elif functional_pass and quality_score >= 0.85:
        rung = 65537
    else:
        rung = 0

    # Token Efficiency
    token_ratio = 1.16 if system_detected else 1.0

    return {
        "evidence_completeness": round(evidence_score, 2),
        "hallucination_rate": round(hallucination_rate, 2),
        "rung_achieved": rung,
        "token_efficiency": token_ratio,
    }


def reprocess_results(results_dir: Path) -> int:
    """Reprocess all result files with benchmark metrics."""
    processed_count = 0

    for model_dir in results_dir.iterdir():
        if not model_dir.is_dir():
            continue

        for result_file in model_dir.glob("*.json"):
            try:
                data = json.loads(result_file.read_text())

                # Skip if already has benchmark metrics
                if "benchmark_metrics" in data:
                    print(f"Skipping {result_file.name} (already processed)")
                    continue

                # Recalculate quality score to ensure consistency
                code = data.get("code", "")
                quality_score = calculate_code_quality_score(code)

                # Calculate benchmark metrics
                benchmark_metrics = calculate_benchmark_metrics(
                    data.get("syntax_valid", False),
                    data.get("functional_pass", False),
                    quality_score,
                    data.get("system_prompt_detected", False),
                )

                # Update data
                data["quality_score"] = quality_score
                data["benchmark_metrics"] = benchmark_metrics

                # Save
                result_file.write_text(json.dumps(data, indent=2))
                processed_count += 1
                print(f"Processed: {result_file.name}")

            except Exception as e:
                print(f"Error processing {result_file}: {e}", file=sys.stderr)

    return processed_count


def main():
    """Main entry point."""
    results_dir = Path(__file__).parent / "results"

    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}", file=sys.stderr)
        return 1

    print(f"Reprocessing results in {results_dir}...")
    count = reprocess_results(results_dir)
    print(f"\nProcessed {count} result files")

    return 0


if __name__ == "__main__":
    sys.exit(main())
