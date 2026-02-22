#!/usr/bin/env python3
"""
Improved Swarm A|B Testing - With Metrics & Quality Signals
Auth: 65537 | Version: 2.0.0

A|B testing approaches:

1. PROMPT VARIANT A|B
   - A: Simple factual (all swarms should handle)
   - B: Domain-specific (tests swarm specialization)
   - Metric: Response length, latency, consistency

2. PERSONA VARIANT A|B (if applicable)
   - A: With primary persona
   - B: Without persona (baseline)
   - Metric: Style difference in responses

3. SKILL SUBSET A|B (if applicable)
   - A: Full skill pack
   - B: Minimal skill pack (just prime-safety)
   - Metric: Response quality impact

4. TEMPERATURE VARIANT A|B
   - A: Temperature=0 (deterministic)
   - B: Temperature=0.5 (creative)
   - Metric: Consistency score
"""

from __future__ import annotations

import sys
import json
import hashlib
from pathlib import Path
from typing import NamedTuple

import pytest
import yaml

_CLI_SRC = Path(__file__).parent.parent.parent / "cli" / "src"
if str(_CLI_SRC) not in sys.path:
    sys.path.insert(0, str(_CLI_SRC))

from stillwater.llm_client import LLMClient


# ============================================================
# Data Models
# ============================================================

class TestResult(NamedTuple):
    """Single test result."""
    swarm_name: str
    variant: str
    test_type: str
    prompt: str
    response: str
    latency_ms: int
    response_length: int
    response_hash: str
    quality_score: float  # 0-1


class ABComparison(NamedTuple):
    """A|B comparison result."""
    swarm_name: str
    test_type: str
    variant_a: TestResult
    variant_b: TestResult
    latency_delta_ms: int
    length_delta: int
    consistency_score: float
    winner: str  # "a", "b", or "tie"


# ============================================================
# Quality Metrics
# ============================================================

def calculate_quality_score(response: str) -> float:
    """
    Calculate response quality score (0-1).

    Factors:
    - Length (longer usually better, but not always)
    - Structure (has paragraphs, lists, code blocks)
    - No error messages
    - Grammar indicators
    """
    score = 0.0

    # Length score (optimal 100-500 chars)
    length = len(response)
    if 100 <= length <= 500:
        score += 0.3
    elif 50 <= length <= 1000:
        score += 0.15

    # Structure score
    if "\n" in response:
        score += 0.15  # Has line breaks
    if "```" in response or "- " in response:
        score += 0.15  # Has code/lists

    # No error signals
    error_keywords = ["error", "failed", "exception", "traceback", "undefined"]
    if not any(keyword in response.lower() for keyword in error_keywords):
        score += 0.2

    # Grammar/completeness
    if response.endswith((".","!","?")) or response.endswith(")"):
        score += 0.15

    return min(1.0, score)


def consistency_score(response_a: str, response_b: str) -> float:
    """
    Calculate consistency between two responses.

    Higher score = more similar (for temperature=0 tests)
    """
    # Simple Levenshtein-based similarity
    if response_a == response_b:
        return 1.0

    a_set = set(response_a.lower().split())
    b_set = set(response_b.lower().split())

    if not a_set or not b_set:
        return 0.0

    intersection = len(a_set & b_set)
    union = len(a_set | b_set)

    return intersection / union if union > 0 else 0.0


# ============================================================
# Test Fixtures
# ============================================================

@pytest.fixture(scope="session")
def llm_client() -> LLMClient:
    """LLM client for testing."""
    return LLMClient(provider="http", config={"http": {"url": "http://localhost:8080"}})


def get_all_swarms(swarms_dir: Path) -> list[str]:
    """Get all swarm names."""
    return sorted([
        f.stem for f in swarms_dir.glob("*.md")
        if f.name != "README.md"
    ])


def load_swarm_metadata(swarm_file: Path) -> dict:
    """Load YAML from swarm file."""
    content = swarm_file.read_text(encoding="utf-8")
    if not content.startswith("---"):
        raise ValueError(f"Invalid swarm format: {swarm_file.name}")

    lines = content.split("\n")
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].startswith("---"):
            end_idx = i
            break

    if end_idx is None:
        raise ValueError(f"Malformed YAML in {swarm_file.name}")

    yaml_text = "\n".join(lines[1:end_idx])
    return yaml.safe_load(yaml_text) or {}


# ============================================================
# A|B Test Classes
# ============================================================

class TestPromptVariants:
    """A|B test with different prompts."""

    PROMPTS = {
        "a": "What is the capital of France?",
        "b": "Design a REST API endpoint for user registration with validation",
    }

    @pytest.mark.parametrize("swarm_name", get_all_swarms(Path(__file__).parent.parent.parent.parent / "swarms"))
    def test_prompt_variants(
        self,
        swarm_name: str,
        llm_client: LLMClient,
    ):
        """Compare responses to prompt A (factual) vs B (domain-specific)."""
        swarms_dir = Path(__file__).parent.parent.parent.parent / "swarms"
        swarm_file = swarms_dir / f"{swarm_name}.md"
        metadata = load_swarm_metadata(swarm_file)

        results = {}

        for variant in ["a", "b"]:
            prompt = self.PROMPTS[variant]

            # Build system prompt
            skill_pack = metadata.get("skill_pack", [])
            system_parts = []
            for skill_name in skill_pack:
                system_parts.append(f"## SKILL: {skill_name}")

            system_prompt = "\n\n---\n\n".join(system_parts)

            # Invoke
            try:
                result = llm_client.chat(
                    [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    model="haiku",
                    max_tokens=256,
                    temperature=0.0,
                    timeout=30.0,
                )

                results[variant] = TestResult(
                    swarm_name=swarm_name,
                    variant=variant,
                    test_type="prompt",
                    prompt=prompt,
                    response=result.text,
                    latency_ms=result.latency_ms,
                    response_length=len(result.text),
                    response_hash=hashlib.md5(result.text.encode()).hexdigest(),
                    quality_score=calculate_quality_score(result.text),
                )
            except Exception as e:
                pytest.fail(f"{swarm_name} (variant {variant}): {e}")

        # Compare
        result_a = results["a"]
        result_b = results["b"]

        print(f"\n{swarm_name} - Prompt Variants:")
        print(f"  A (factual):      {result_a.response_length:3d} chars, {result_a.latency_ms:4d}ms, quality={result_a.quality_score:.2f}")
        print(f"  B (domain):       {result_b.response_length:3d} chars, {result_b.latency_ms:4d}ms, quality={result_b.quality_score:.2f}")
        print(f"  Length delta:     {result_b.response_length - result_a.response_length:+4d} chars")
        print(f"  Latency delta:    {result_b.latency_ms - result_a.latency_ms:+4d}ms")

        # Assertions
        assert result_a.response, f"{swarm_name} A: empty response"
        assert result_b.response, f"{swarm_name} B: empty response"
        assert result_a.quality_score > 0, f"{swarm_name} A: poor quality"
        assert result_b.quality_score > 0, f"{swarm_name} B: poor quality"


class TestTemperatureConsistency:
    """A|B test: deterministic vs creative responses."""

    @pytest.mark.parametrize("swarm_name", get_all_swarms(Path(__file__).parent.parent.parent.parent / "swarms")[:5])
    def test_temperature_consistency(
        self,
        swarm_name: str,
        llm_client: LLMClient,
    ):
        """Test temperature=0 (deterministic) vs temperature=0.5 (creative)."""
        swarms_dir = Path(__file__).parent.parent.parent.parent / "swarms"
        swarm_file = swarms_dir / f"{swarm_name}.md"
        metadata = load_swarm_metadata(swarm_file)

        prompt = "What is the capital of France?"
        skill_pack = metadata.get("skill_pack", [])
        system_parts = [f"## SKILL: {s}" for s in skill_pack]
        system_prompt = "\n\n---\n\n".join(system_parts)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        results = {}

        # Test with temperature=0 (deterministic)
        result_det = llm_client.chat(
            messages, model="haiku", temperature=0.0, timeout=30.0
        )
        results["deterministic"] = result_det

        # Test with temperature=0.5 (creative)
        result_creative = llm_client.chat(
            messages, model="haiku", temperature=0.5, timeout=30.0
        )
        results["creative"] = result_creative

        consistency = consistency_score(result_det.text, result_creative.text)

        print(f"\n{swarm_name} - Temperature Consistency:")
        print(f"  Temperature=0:    {len(result_det.text):3d} chars")
        print(f"  Temperature=0.5:  {len(result_creative.text):3d} chars")
        print(f"  Consistency:      {consistency:.2f} (1.0=identical, 0.0=different)")

        # Assertions
        assert result_det.text, f"{swarm_name}: empty response at temp=0"
        assert result_creative.text, f"{swarm_name}: empty response at temp=0.5"
        # At temperature=0, we expect high consistency (>0.7)
        assert consistency > 0.7, f"{swarm_name}: temp=0 not deterministic enough (consistency={consistency:.2f})"


class TestPersonaImpact:
    """A|B test: with vs without persona."""

    @pytest.mark.parametrize("swarm_name", get_all_swarms(Path(__file__).parent.parent.parent.parent / "swarms")[:3])
    def test_persona_impact(
        self,
        swarm_name: str,
        llm_client: LLMClient,
    ):
        """Test impact of persona on response style."""
        swarms_dir = Path(__file__).parent.parent.parent.parent / "swarms"
        personas_dir = Path(__file__).parent.parent.parent.parent / "personas"
        swarm_file = swarms_dir / f"{swarm_name}.md"
        metadata = load_swarm_metadata(swarm_file)

        prompt = "What is the capital of France?"
        skill_pack = metadata.get("skill_pack", [])

        # Variant A: with persona
        system_a_parts = [f"## SKILL: {s}" for s in skill_pack]
        persona_config = metadata.get("persona", {})
        if isinstance(persona_config, dict):
            primary = persona_config.get("primary")
            if primary:
                persona_file = personas_dir / f"{primary}.md"
                if not persona_file.exists():
                    matches = list(personas_dir.rglob(f"{primary}.md"))
                    if matches:
                        persona_file = matches[0]

                if persona_file.exists():
                    content = persona_file.read_text(encoding="utf-8")
                    # Extract QUICK LOAD
                    start = content.find("<!-- QUICK LOAD")
                    end = content.find("-->", start)
                    if start != -1 and end != -1:
                        persona_content = content[start:end+3].strip()
                        system_a_parts.append(f"## PERSONA: {primary}\n{persona_content}")

        system_a = "\n\n---\n\n".join(system_a_parts)

        # Variant B: without persona (just skills)
        system_b = "\n\n---\n\n".join([f"## SKILL: {s}" for s in skill_pack])

        # Test both
        result_a = llm_client.chat(
            [{"role": "system", "content": system_a}, {"role": "user", "content": prompt}],
            model="haiku", temperature=0.0, timeout=30.0
        )

        result_b = llm_client.chat(
            [{"role": "system", "content": system_b}, {"role": "user", "content": prompt}],
            model="haiku", temperature=0.0, timeout=30.0
        )

        consistency = consistency_score(result_a.text, result_b.text)

        print(f"\n{swarm_name} - Persona Impact:")
        print(f"  With persona:     {len(result_a.text):3d} chars")
        print(f"  Without persona:  {len(result_b.text):3d} chars")
        print(f"  Similarity:       {consistency:.2f} (1.0=identical, 0.0=completely different)")

        # Assertions
        assert result_a.text, f"{swarm_name}: empty response with persona"
        assert result_b.text, f"{swarm_name}: empty response without persona"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
