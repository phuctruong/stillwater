"""Benchmark runner: orchestrator, table output, and certificate generation."""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
import time
from dataclasses import asdict

from stillwater.bench import BENCHMARKS, BenchResult
from stillwater.llm import LLMClient


def run_benchmark(name: str, client: LLMClient) -> BenchResult:
    """Run a single benchmark by name."""
    info = BENCHMARKS[name]
    module = importlib.import_module(info["module"])
    return module.run(client)


def run_all(
    client: LLMClient,
    names: list[str] | None = None,
    verbose: bool = False,
) -> tuple[list[BenchResult], dict]:
    """Run benchmarks and return results + certificate.

    Args:
        client: LLM client to use.
        names: Specific benchmarks to run (None = all).
        verbose: Print per-instance details.

    Returns:
        (results, certificate_dict)
    """
    out = sys.stdout
    bench_names = names or list(BENCHMARKS.keys())

    # Header
    from stillwater import __version__

    out.write(f"Stillwater Benchmark Suite v{__version__}\n")
    out.write(f"Model: {client.model} ({client.provider} @ {client.endpoint})\n")
    out.write("\n")

    results: list[BenchResult] = []
    total_passed = 0
    total_benchmarks = len(bench_names)

    for name in bench_names:
        info = BENCHMARKS[name]
        result = run_benchmark(name, client)
        results.append(result)

        # Determine pass/fail based on threshold
        threshold = info["threshold"]
        bench_passed = result.passed >= threshold
        if bench_passed:
            total_passed += 1

        status = "PASS" if bench_passed else "FAIL"
        score = f"({result.score:.1f})"
        elapsed = f"{result.elapsed_ms:.0f}ms"

        # Format: name .......... passed/total  STATUS  (score)  elapsed
        desc = info["description"]
        dots = "." * max(1, 34 - len(desc))
        out.write(
            f"  {desc} {dots} {result.passed:>2}/{result.total:<2}  "
            f"{status}  {score:>5}  {elapsed:>7}\n"
        )

        if verbose:
            for detail in result.details:
                p = "PASS" if detail.get("passed") else "FAIL"
                desc_key = (
                    detail.get("claim")
                    or detail.get("question")
                    or detail.get("instruction")
                    or detail.get("description")
                    or detail.get("test")
                    or detail.get("input", "")
                )
                out.write(f"    {p}: {desc_key[:60]}\n")

    out.write("\n")
    out.write(f"  Total: {total_passed}/{total_benchmarks} PASSED")

    # Build certificate
    cert = build_certificate(results, client)
    out.write(f" | Certificate: stillwater-bench-certificate.json\n")

    return results, cert


def build_certificate(results: list[BenchResult], client: LLMClient) -> dict:
    """Build a JSON proof certificate for benchmark results."""
    from stillwater import __version__

    cert: dict = {
        "version": __version__,
        "model": client.model,
        "provider": client.provider,
        "benchmarks": {},
        "hash": "",
        "status": "PASSED",
    }

    all_passed = True
    for result in results:
        name_key = result.name.lower().replace(" ", "_")
        info = next(
            (v for v in BENCHMARKS.values() if v["description"] == result.name),
            None,
        )
        threshold = info["threshold"] if info else result.total
        bench_passed = result.passed >= threshold

        if not bench_passed:
            all_passed = False

        cert["benchmarks"][name_key] = {
            "passed": result.passed,
            "total": result.total,
            "score": result.score,
            "elapsed_ms": round(result.elapsed_ms, 1),
            "ok": bench_passed,
        }

    cert["status"] = "PASSED" if all_passed else "FAILED"

    # Content-address the certificate
    cert_no_hash = {k: v for k, v in sorted(cert.items()) if k != "hash"}
    cert_json = json.dumps(cert_no_hash, sort_keys=True, separators=(",", ":"))
    cert["hash"] = hashlib.sha256(cert_json.encode()).hexdigest()

    return cert
