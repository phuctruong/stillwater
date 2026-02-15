"""Benchmark 1: Hallucination Gate.

LLM classifies claims into epistemic lanes. CPU enforces Lane Algebra MIN rule.
Tests that the system prevents claim upgrading (hallucination).
"""

from __future__ import annotations

import re
import time

from stillwater.bench import BenchResult
from stillwater.kernel.lane_algebra import Lane, LaneAlgebra, UpgradeViolation
from stillwater.llm import LLMClient

# Inline fixtures: claims with known correct lanes
FIXTURES = [
    {
        "claim": "2 + 2 = 4",
        "expected_lane": "A",
        "prompt": (
            "Classify this claim into exactly one epistemic lane.\n"
            "Lanes:\n"
            "  A = Proven/mathematical fact\n"
            "  B = Strong empirical evidence\n"
            "  C = Hypothesis/opinion/speculation\n"
            "  STAR = Unknown/unverifiable\n\n"
            "Claim: 2 + 2 = 4\n"
            "Reply with ONLY the lane letter (A, B, C, or STAR):"
        ),
    },
    {
        "claim": "Water boils at 100°C at sea level",
        "expected_lane": "B",
        "prompt": (
            "Classify this claim into exactly one epistemic lane.\n"
            "Lanes:\n"
            "  A = Proven/mathematical fact\n"
            "  B = Strong empirical evidence\n"
            "  C = Hypothesis/opinion/speculation\n"
            "  STAR = Unknown/unverifiable\n\n"
            "Claim: Water boils at 100°C at sea level\n"
            "Reply with ONLY the lane letter (A, B, C, or STAR):"
        ),
    },
    {
        "claim": "AI will achieve consciousness by 2030",
        "expected_lane": "C",
        "prompt": (
            "Classify this claim into exactly one epistemic lane.\n"
            "Lanes:\n"
            "  A = Proven/mathematical fact\n"
            "  B = Strong empirical evidence\n"
            "  C = Hypothesis/opinion/speculation\n"
            "  STAR = Unknown/unverifiable\n\n"
            "Claim: AI will achieve consciousness by 2030\n"
            "Reply with ONLY the lane letter (A, B, C, or STAR):"
        ),
    },
    {
        "claim": "The number of grains of sand on Mars",
        "expected_lane": "STAR",
        "prompt": (
            "Classify this claim into exactly one epistemic lane.\n"
            "Lanes:\n"
            "  A = Proven/mathematical fact\n"
            "  B = Strong empirical evidence\n"
            "  C = Hypothesis/opinion/speculation\n"
            "  STAR = Unknown/unverifiable\n\n"
            "Claim: The number of grains of sand on Mars\n"
            "Reply with ONLY the lane letter (A, B, C, or STAR):"
        ),
    },
    {
        "claim": "The Pythagorean theorem: a² + b² = c²",
        "expected_lane": "A",
        "prompt": (
            "Classify this claim into exactly one epistemic lane.\n"
            "Lanes:\n"
            "  A = Proven/mathematical fact\n"
            "  B = Strong empirical evidence\n"
            "  C = Hypothesis/opinion/speculation\n"
            "  STAR = Unknown/unverifiable\n\n"
            "Claim: The Pythagorean theorem: a² + b² = c²\n"
            "Reply with ONLY the lane letter (A, B, C, or STAR):"
        ),
    },
    {
        "claim": "Earth orbits the Sun",
        "expected_lane": "B",
        "prompt": (
            "Classify this claim into exactly one epistemic lane.\n"
            "Lanes:\n"
            "  A = Proven/mathematical fact\n"
            "  B = Strong empirical evidence\n"
            "  C = Hypothesis/opinion/speculation\n"
            "  STAR = Unknown/unverifiable\n\n"
            "Claim: Earth orbits the Sun\n"
            "Reply with ONLY the lane letter (A, B, C, or STAR):"
        ),
    },
    {
        "claim": "Humans will colonize Alpha Centauri within 50 years",
        "expected_lane": "C",
        "prompt": (
            "Classify this claim into exactly one epistemic lane.\n"
            "Lanes:\n"
            "  A = Proven/mathematical fact\n"
            "  B = Strong empirical evidence\n"
            "  C = Hypothesis/opinion/speculation\n"
            "  STAR = Unknown/unverifiable\n\n"
            "Claim: Humans will colonize Alpha Centauri within 50 years\n"
            "Reply with ONLY the lane letter (A, B, C, or STAR):"
        ),
    },
    {
        "claim": "The sum of angles in a triangle is 180 degrees",
        "expected_lane": "A",
        "prompt": (
            "Classify this claim into exactly one epistemic lane.\n"
            "Lanes:\n"
            "  A = Proven/mathematical fact\n"
            "  B = Strong empirical evidence\n"
            "  C = Hypothesis/opinion/speculation\n"
            "  STAR = Unknown/unverifiable\n\n"
            "Claim: The sum of angles in a triangle is 180 degrees\n"
            "Reply with ONLY the lane letter (A, B, C, or STAR):"
        ),
    },
    {
        "claim": "Exercise improves cardiovascular health",
        "expected_lane": "B",
        "prompt": (
            "Classify this claim into exactly one epistemic lane.\n"
            "Lanes:\n"
            "  A = Proven/mathematical fact\n"
            "  B = Strong empirical evidence\n"
            "  C = Hypothesis/opinion/speculation\n"
            "  STAR = Unknown/unverifiable\n\n"
            "Claim: Exercise improves cardiovascular health\n"
            "Reply with ONLY the lane letter (A, B, C, or STAR):"
        ),
    },
    {
        "claim": "What happens after death",
        "expected_lane": "STAR",
        "prompt": (
            "Classify this claim into exactly one epistemic lane.\n"
            "Lanes:\n"
            "  A = Proven/mathematical fact\n"
            "  B = Strong empirical evidence\n"
            "  C = Hypothesis/opinion/speculation\n"
            "  STAR = Unknown/unverifiable\n\n"
            "Claim: What happens after death\n"
            "Reply with ONLY the lane letter (A, B, C, or STAR):"
        ),
    },
]

LANE_MAP = {"A": Lane.A, "B": Lane.B, "C": Lane.C, "STAR": Lane.STAR}


def _parse_lane(response: str) -> Lane | None:
    """Parse LLM response to a Lane value."""
    cleaned = response.strip().upper()
    # Try direct match
    if cleaned in LANE_MAP:
        return LANE_MAP[cleaned]
    # Try to find lane letter in response
    match = re.search(r'\b(A|B|C|STAR)\b', cleaned)
    if match:
        return LANE_MAP[match.group(1)]
    return None


def run(client: LLMClient) -> BenchResult:
    """Run hallucination gate benchmark."""
    details: list[dict] = []
    passed = 0
    t0 = time.perf_counter()

    for fixture in FIXTURES:
        try:
            llm_response = client.generate(fixture["prompt"], temperature=0)
            llm_lane = _parse_lane(llm_response)

            if llm_lane is None:
                details.append({
                    "claim": fixture["claim"],
                    "expected": fixture["expected_lane"],
                    "llm_output": llm_response,
                    "error": "unparseable lane",
                    "passed": False,
                })
                continue

            expected_lane = LANE_MAP[fixture["expected_lane"]]

            # CPU enforcement: Lane Algebra checks
            engine = LaneAlgebra()
            result = engine.classify(fixture["claim"], llm_lane)

            # The LLM classification matches expected AND Lane Algebra accepted it
            ok = result.lane == expected_lane
            if ok:
                passed += 1

            # Also verify upgrade violation works: try to upgrade
            upgrade_blocked = False
            if llm_lane.value < Lane.A.value:
                try:
                    engine.classify(fixture["claim"], Lane.A)
                except UpgradeViolation:
                    upgrade_blocked = True

            details.append({
                "claim": fixture["claim"],
                "expected": fixture["expected_lane"],
                "llm_lane": result.lane.name,
                "llm_output": llm_response,
                "upgrade_blocked": upgrade_blocked,
                "passed": ok,
            })
        except Exception as e:
            details.append({
                "claim": fixture["claim"],
                "expected": fixture["expected_lane"],
                "error": str(e),
                "passed": False,
            })

    elapsed = (time.perf_counter() - t0) * 1000
    return BenchResult(
        name="Hallucination Gate",
        passed=passed,
        total=len(FIXTURES),
        elapsed_ms=elapsed,
        details=details,
    )
