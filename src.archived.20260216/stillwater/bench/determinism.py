"""Benchmark 8: Determinism.

LLM answers simple prompts 3 times with temperature=0.
CPU does exact string comparison to verify reproducibility.
"""

from __future__ import annotations

import time

from stillwater.bench import BenchResult
from stillwater.llm import LLMClient

# Simple, deterministic prompts that should produce identical responses
FIXTURES = [
    {
        "prompt": "What is 2 + 2? Reply with ONLY the number.",
        "description": "simple_addition",
    },
    {
        "prompt": "What is the capital of France? Reply with ONLY the city name.",
        "description": "capital_france",
    },
    {
        "prompt": "Is water wet? Reply with ONLY 'yes' or 'no'.",
        "description": "water_wet",
    },
    {
        "prompt": "What color is the sky on a clear day? Reply with ONLY one word.",
        "description": "sky_color",
    },
    {
        "prompt": "How many days are in a week? Reply with ONLY the number.",
        "description": "days_in_week",
    },
]

NUM_REPEATS = 3


def run(client: LLMClient) -> BenchResult:
    """Run determinism benchmark."""
    details: list[dict] = []
    passed = 0
    t0 = time.perf_counter()

    for fixture in FIXTURES:
        try:
            responses = []
            for _ in range(NUM_REPEATS):
                resp = client.generate(fixture["prompt"], temperature=0)
                responses.append(resp)

            # CPU: exact string comparison
            all_identical = len(set(responses)) == 1
            if all_identical:
                passed += 1

            details.append({
                "description": fixture["description"],
                "responses": responses,
                "identical": all_identical,
                "passed": all_identical,
            })
        except Exception as e:
            details.append({
                "description": fixture["description"],
                "error": str(e),
                "passed": False,
            })

    elapsed = (time.perf_counter() - t0) * 1000
    return BenchResult(
        name="Determinism",
        passed=passed,
        total=len(FIXTURES),
        elapsed_ms=elapsed,
        details=details,
    )
