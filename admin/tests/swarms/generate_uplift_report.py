#!/usr/bin/env python3
"""
Generate AI Uplift Benchmark Report
Compares baseline (no skills) vs. uplifted (with prime-coder) metrics
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def load_results(results_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Load all test results from directory."""
    results = {}

    for model_dir in results_dir.iterdir():
        if not model_dir.is_dir():
            continue

        model = model_dir.name
        results[model] = []

        for result_file in model_dir.glob("*.json"):
            try:
                data = json.loads(result_file.read_text())
                results[model].append(data)
            except Exception as e:
                print(f"Error loading {result_file}: {e}", file=sys.stderr)

    return results


def calculate_uplift_metrics(results: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """
    Calculate uplift metrics per model.

    Uses the benchmark framework from ai-uplift-benchmark.md:
    - Hallucination Rate (0-1, lower is better)
    - Evidence Completeness (0-10, higher is better)
    - Rung Achieved (0, 641, 274177, 65537)
    - Token Efficiency (ratio, 1.0 = baseline)
    """
    metrics = {}

    for model, tests in results.items():
        if not tests:
            continue

        benchmark_data = []
        for test in tests:
            if "benchmark_metrics" in test:
                benchmark_data.append(test["benchmark_metrics"])

        if benchmark_data:
            # Calculate averages
            avg_evidence = sum(b.get("evidence_completeness", 0) for b in benchmark_data) / len(benchmark_data)
            avg_hallucination = sum(b.get("hallucination_rate", 0) for b in benchmark_data) / len(benchmark_data)
            avg_rung = sum(b.get("rung_achieved", 0) for b in benchmark_data) / len(benchmark_data)
            avg_tokens = sum(b.get("token_efficiency", 1.0) for b in benchmark_data) / len(benchmark_data)

            metrics[model] = {
                "evidence_completeness": avg_evidence,
                "hallucination_rate": avg_hallucination,
                "rung_achieved": avg_rung,
                "token_efficiency": avg_tokens,
                "total_tests": len(tests),
            }

    return metrics


def calculate_uplift_score(metrics: Dict[str, Any]) -> float:
    """
    Calculate Uplift score using the formula:
    Uplift = (Skill_Quality × Verification_Rung) / (Hallucination_Rate × Token_Cost)

    Skill_Quality is estimated as 0.90 for prime-coder (from ai-uplift-benchmark.md)
    """
    skill_quality = 0.90  # prime-coder score

    hallucination_rate = metrics.get("hallucination_rate", 0.5)
    rung = metrics.get("rung_achieved", 0)
    token_cost = metrics.get("token_efficiency", 1.0)

    # Avoid division by zero
    if hallucination_rate == 0:
        hallucination_rate = 0.05

    uplift = (skill_quality * rung) / (hallucination_rate * token_cost)
    return uplift


def format_report(metrics: Dict[str, Dict]) -> str:
    """Format metrics into a readable report."""
    lines = []

    lines.append("\n" + "="*80)
    lines.append("AI UPLIFT BENCHMARK REPORT")
    lines.append("Prime-Coder Skill Loading Across Models")
    lines.append("="*80)
    lines.append(f"\nGenerated: {datetime.now().isoformat()}")
    lines.append(f"Framework: ai-uplift-benchmark.md v1.0.0")
    lines.append(f"Models Tested: {', '.join(sorted(metrics.keys()))}")

    # Per-model metrics
    lines.append("\n" + "-"*80)
    lines.append("DETAILED METRICS BY MODEL")
    lines.append("-"*80)

    for model in sorted(metrics.keys()):
        m = metrics[model]
        lines.append(f"\n{model.upper()}")
        lines.append(f"  Tests:                    {m['total_tests']}")
        lines.append(f"  Evidence Completeness:    {m['evidence_completeness']:.2f}/10")
        lines.append(f"  Hallucination Rate:       {m['hallucination_rate']:.2f} (lower is better)")
        lines.append(f"  Rung Achieved:            {int(m['rung_achieved'])} (target: 641)")
        lines.append(f"  Token Efficiency:         {m['token_efficiency']:.2f}x")

        # Calculate uplift
        uplift = calculate_uplift_score(m)
        lines.append(f"  Uplift Score:             {uplift:,.0f}")

    # Comparative analysis
    lines.append("\n" + "-"*80)
    lines.append("COMPARATIVE ANALYSIS")
    lines.append("-"*80)

    if len(metrics) > 1:
        models_sorted = sorted(metrics.keys(), key=lambda m: metrics[m]["evidence_completeness"], reverse=True)
        lines.append(f"\nBest Evidence Quality:  {models_sorted[0].upper()}")
        lines.append(f"Best Hallucination:     {min(metrics.keys(), key=lambda m: metrics[m]['hallucination_rate']).upper()}")
        lines.append(f"Highest Rung:           {max(metrics.keys(), key=lambda m: metrics[m]['rung_achieved']).upper()}")
        lines.append(f"Most Efficient:         {min(metrics.keys(), key=lambda m: metrics[m]['token_efficiency']).upper()}")

    # Summary
    lines.append("\n" + "-"*80)
    lines.append("SUMMARY")
    lines.append("-"*80)

    if metrics:
        avg_evidence = sum(m["evidence_completeness"] for m in metrics.values()) / len(metrics)
        avg_hallucination = sum(m["hallucination_rate"] for m in metrics.values()) / len(metrics)
        avg_rung = sum(m["rung_achieved"] for m in metrics.values()) / len(metrics)
        avg_tokens = sum(m["token_efficiency"] for m in metrics.values()) / len(metrics)

        lines.append(f"\nAverage Evidence Completeness:  {avg_evidence:.2f}/10")
        lines.append(f"Average Hallucination Rate:     {avg_hallucination:.2f}")
        lines.append(f"Average Rung:                   {int(avg_rung)}")
        lines.append(f"Average Token Efficiency:       {avg_tokens:.2f}x")

        # Comparison to benchmark baseline
        baseline_hallucination = 0.52  # From ai-uplift-benchmark.md
        baseline_evidence = 2.4

        lines.append(f"\nCOMPARISON TO BENCHMARK (ai-uplift-benchmark.md)")
        lines.append(f"  Evidence Completeness:  {avg_evidence:.2f} vs baseline {baseline_evidence:.2f} "
                    f"({(avg_evidence/baseline_evidence - 1)*100:+.0f}%)")
        lines.append(f"  Hallucination Rate:     {avg_hallucination:.2f} vs baseline {baseline_hallucination:.2f} "
                    f"({(avg_hallucination/baseline_hallucination - 1)*100:+.0f}%)")
        lines.append(f"  Rung Achieved:          {int(avg_rung)} vs baseline 0 (641+ is uplift success)")

    lines.append("\n" + "="*80)

    return "\n".join(lines)


def main():
    """Main entry point."""
    results_dir = Path(__file__).parent / "results"

    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}", file=sys.stderr)
        return 1

    # Load results
    results = load_results(results_dir)

    if not results:
        print("No test results found.", file=sys.stderr)
        return 1

    # Calculate metrics
    metrics = calculate_uplift_metrics(results)

    # Generate and print report
    report = format_report(metrics)
    print(report)

    # Save report
    report_file = results_dir.parent / "UPLIFT_REPORT.md"
    report_file.write_text(report)
    print(f"\nReport saved to: {report_file}")

    # Save metrics as JSON
    metrics_file = results_dir / "BENCHMARK_METRICS.json"
    metrics_file.write_text(json.dumps(metrics, indent=2))
    print(f"Metrics saved to: {metrics_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
