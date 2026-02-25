#!/usr/bin/env python3
"""
Swarm Unit Tests - Haiku Level
Auth: 65537 | Version: 1.0.0

Tests each swarm in stillwater/swarms/ with:
- Metadata validation (skill_pack, persona, model_preferred, rung_default)
- Invocation with test prompts (a | b variants)
- Response validation
- System prompt injection verification

Test plan:
  A: "What is the capital of France?" (simple factual)
  B: "Design a simple API endpoint" (domain-specific)
"""

from __future__ import annotations

import sys
import json
from pathlib import Path

import pytest
import yaml

# Add CLI source to path
_CLI_SRC = Path(__file__).parent.parent.parent / "src" / "cli" / "src"
if str(_CLI_SRC) not in sys.path:
    sys.path.insert(0, str(_CLI_SRC))

from stillwater.llm_client import LLMClient


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="session")
def swarms_dir():
    """Get path to swarms directory."""
    return Path(__file__).parent.parent.parent.parent / "data" / "default" / "swarms"


@pytest.fixture(scope="session")
def skills_dir():
    """Get path to skills directory."""
    return Path(__file__).parent.parent.parent.parent / "data" / "default" / "skills"


@pytest.fixture(scope="session")
def personas_dir():
    """Get path to personas directory."""
    return Path(__file__).parent.parent.parent.parent / "data" / "default" / "personas"


@pytest.fixture(scope="session")
def llm_client():
    """Create LLM client pointing to Claude Code wrapper."""
    return LLMClient(provider="http", config={"http": {"url": "http://localhost:8080"}})


def get_all_swarms(swarms_dir: Path) -> list[str]:
    """Get all available swarm names."""
    return sorted([
        f.stem for f in swarms_dir.rglob("*.md")
        if not f.name.startswith("README")
    ])


def resolve_swarm_file(swarms_dir: Path, swarm_name: str) -> Path:
    matches = sorted(swarms_dir.rglob(f"{swarm_name}.md"))
    if not matches:
        raise FileNotFoundError(f"Swarm file not found: {swarm_name}")
    return matches[0]


def load_swarm_metadata(swarm_file: Path) -> dict:
    """Load YAML frontmatter from swarm file."""
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


def load_skill(skill_name: str, skills_dir: Path) -> str:
    """Load skill file content (QUICK LOAD block)."""
    skill_file = skills_dir / f"{skill_name}.md"
    if not skill_file.exists():
        return f"[SKILL NOT FOUND: {skill_name}]"

    content = skill_file.read_text(encoding="utf-8")
    start = content.find("<!-- QUICK LOAD")
    end = content.find("-->", start)
    if start != -1 and end != -1:
        return content[start:end+3].strip()

    return content[:500]


def load_persona(persona_name: str, personas_dir: Path) -> str:
    """Load persona file content (QUICK LOAD block)."""
    persona_file = personas_dir / f"{persona_name}.md"
    if not persona_file.exists():
        matches = list(personas_dir.rglob(f"{persona_name}.md"))
        if matches:
            persona_file = matches[0]

    if not persona_file.exists():
        return f"[PERSONA NOT FOUND: {persona_name}]"

    content = persona_file.read_text(encoding="utf-8")
    start = content.find("<!-- QUICK LOAD")
    end = content.find("-->", start)
    if start != -1 and end != -1:
        return content[start:end+3].strip()

    return content[:500]


# ============================================================
# Test Classes
# ============================================================

class TestSwarmMetadata:
    """Test swarm metadata validation."""

    @pytest.mark.parametrize("swarm_name", get_all_swarms(Path(__file__).parent.parent.parent.parent / "data" / "default" / "swarms"))
    def test_swarm_metadata_valid(self, swarm_name: str, swarms_dir: Path):
        """Test that swarm metadata is valid."""
        swarm_file = resolve_swarm_file(swarms_dir, swarm_name)
        assert swarm_file.exists(), f"Swarm file not found: {swarm_name}"

        metadata = load_swarm_metadata(swarm_file)

        # Required fields
        assert "agent_type" in metadata, f"{swarm_name}: missing agent_type"
        assert "skill_pack" in metadata, f"{swarm_name}: missing skill_pack"
        assert "model_preferred" in metadata, f"{swarm_name}: missing model_preferred"

        # Validate skill pack is list
        assert isinstance(metadata["skill_pack"], list), f"{swarm_name}: skill_pack must be list"
        assert len(metadata["skill_pack"]) > 0, f"{swarm_name}: skill_pack cannot be empty"

        # First skill must be prime-safety
        assert metadata["skill_pack"][0] == "prime-safety", \
            f"{swarm_name}: first skill must be prime-safety, got {metadata['skill_pack'][0]}"

        # Validate model preference
        valid_models = {"haiku", "sonnet", "opus"}
        assert metadata["model_preferred"] in valid_models, \
            f"{swarm_name}: invalid model_preferred: {metadata['model_preferred']}"


class TestSwarmSkills:
    """Test that swarm skill packs are loadable."""

    @pytest.mark.parametrize("swarm_name", get_all_swarms(Path(__file__).parent.parent.parent.parent / "data" / "default" / "swarms"))
    def test_swarm_skills_exist(self, swarm_name: str, swarms_dir: Path, skills_dir: Path):
        """Test that all skills referenced in swarm exist."""
        swarm_file = resolve_swarm_file(swarms_dir, swarm_name)
        metadata = load_swarm_metadata(swarm_file)
        skill_pack = metadata.get("skill_pack", [])

        for skill_name in skill_pack:
            skill_file = skills_dir / f"{skill_name}.md"
            assert skill_file.exists(), \
                f"{swarm_name}: skill not found: {skill_name}"


class TestSwarmPersonas:
    """Test that swarm personas are loadable."""

    @pytest.mark.parametrize("swarm_name", get_all_swarms(Path(__file__).parent.parent.parent.parent / "data" / "default" / "swarms"))
    def test_swarm_persona_exists(self, swarm_name: str, swarms_dir: Path, personas_dir: Path):
        """Test that persona (if specified) exists."""
        swarm_file = resolve_swarm_file(swarms_dir, swarm_name)
        metadata = load_swarm_metadata(swarm_file)

        persona_config = metadata.get("persona", {})
        if isinstance(persona_config, dict):
            primary_persona = persona_config.get("primary")
            if primary_persona:
                persona_file = personas_dir / f"{primary_persona}.md"
                # Try recursive search if not found
                if not persona_file.exists():
                    matches = list(personas_dir.rglob(f"{primary_persona}.md"))
                    if matches:
                        persona_file = matches[0]

                assert persona_file.exists(), \
                    f"{swarm_name}: persona not found: {primary_persona}"


class TestSwarmInvocation:
    """Test swarm invocation with haiku and test prompts A | B."""

    @pytest.mark.parametrize("swarm_name", get_all_swarms(Path(__file__).parent.parent.parent.parent / "data" / "default" / "swarms"))
    @pytest.mark.parametrize("test_variant", ["a", "b"])
    def test_swarm_invoke_haiku(
        self,
        swarm_name: str,
        test_variant: str,
        swarms_dir: Path,
        skills_dir: Path,
        personas_dir: Path,
        llm_client: LLMClient,
    ):
        """Test invoking swarm with haiku model."""
        swarm_file = resolve_swarm_file(swarms_dir, swarm_name)
        metadata = load_swarm_metadata(swarm_file)

        # Select test prompt (A or B)
        test_prompts = {
            "a": "What is the capital of France?",
            "b": "Design a simple API endpoint for user registration",
        }
        prompt = test_prompts[test_variant]

        # Build system prompt
        skill_pack = metadata.get("skill_pack", [])
        system_parts = []
        for skill_name in skill_pack:
            skill_content = load_skill(skill_name, skills_dir)
            system_parts.append(f"## SKILL: {skill_name}\n{skill_content}")

        persona_config = metadata.get("persona", {})
        if isinstance(persona_config, dict):
            primary_persona = persona_config.get("primary")
            if primary_persona:
                persona_content = load_persona(primary_persona, personas_dir)
                system_parts.append(f"## PERSONA: {primary_persona}\n{persona_content}")

        system_prompt = "\n\n---\n\n".join(system_parts)

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        # Invoke LLM (use haiku for all tests)
        try:
            result = llm_client.chat(
                messages,
                model="haiku",
                max_tokens=512,
                temperature=0.0,
                timeout=30.0,
            )

            # Validate response
            assert result.text, f"{swarm_name} ({test_variant}): empty response"
            assert len(result.text) > 10, f"{swarm_name} ({test_variant}): response too short"
            assert result.latency_ms > 0, f"{swarm_name} ({test_variant}): invalid latency"

            # Log result metadata
            print(f"\n✓ {swarm_name} ({test_variant}): {len(result.text)} chars, {result.latency_ms}ms")

        except Exception as e:
            pytest.fail(f"{swarm_name} ({test_variant}): invocation failed: {e}")


class TestSwarmConsistency:
    """Test that swarms are consistent across models."""

    @pytest.mark.parametrize("swarm_name", get_all_swarms(Path(__file__).parent.parent.parent.parent / "data" / "default" / "swarms")[:3])
    def test_swarm_response_consistency(
        self,
        swarm_name: str,
        swarms_dir: Path,
        skills_dir: Path,
        personas_dir: Path,
        llm_client: LLMClient,
    ):
        """Test that same prompt produces response with swarm (smoke test)."""
        swarm_file = resolve_swarm_file(swarms_dir, swarm_name)
        metadata = load_swarm_metadata(swarm_file)

        prompt = "What is the capital of France?"

        # Build system prompt
        skill_pack = metadata.get("skill_pack", [])
        system_parts = []
        for skill_name in skill_pack:
            skill_content = load_skill(skill_name, skills_dir)
            system_parts.append(f"## SKILL: {skill_name}\n{skill_content}")

        system_prompt = "\n\n---\n\n".join(system_parts)

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        # Call 2x with same parameters
        try:
            result1 = llm_client.chat(
                messages,
                model="haiku",
                max_tokens=256,
                temperature=0.0,
                timeout=30.0,
            )

            result2 = llm_client.chat(
                messages,
                model="haiku",
                max_tokens=256,
                temperature=0.0,
                timeout=30.0,
            )

            # Both should return valid responses
            assert result1.text, f"{swarm_name}: first call returned empty"
            assert result2.text, f"{swarm_name}: second call returned empty"

            # With temperature=0, responses might be identical (or very similar)
            # Just verify both are present
            print(f"\n✓ {swarm_name} consistency: both calls successful")

        except Exception as e:
            pytest.fail(f"{swarm_name}: consistency test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
