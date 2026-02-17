"""
Prime Skills loader for SWE-bench patch generation.

Loads all 31+ Prime Skills and creates comprehensive prompts for LLM patch generation.
"""

from pathlib import Path
from typing import List, Dict


def get_skills_directory() -> Path:
    """Get the Prime Skills directory."""
    # Skills are in src/stillwater/skills/
    base_dir = Path(__file__).parent.parent / "skills"
    if not base_dir.exists():
        raise FileNotFoundError(f"Skills directory not found: {base_dir}")
    return base_dir


def load_all_skills() -> Dict[str, str]:
    """
    Load all Prime Skills from disk.

    Returns:
        Dictionary mapping skill name to skill content
    """
    skills_dir = get_skills_directory()
    skills = {}

    # Core skills (root directory)
    for skill_file in ["prime-coder.md", "prime-math.md", "prime-swarm-orchestration.md"]:
        skill_path = skills_dir / skill_file
        if skill_path.exists():
            skills[skill_file] = skill_path.read_text()

    # Category skills
    for category in ["coding", "math", "epistemic", "verification", "infrastructure"]:
        category_dir = skills_dir / category
        if category_dir.exists():
            for skill_file in category_dir.glob("*.md"):
                skills[skill_file.name] = skill_file.read_text()

    return skills


def get_essential_skills() -> List[str]:
    """
    Get list of essential skills for SWE-bench (31+ skills).

    Returns:
        List of skill filenames (in order of importance)
    """
    return [
        # Core (2)
        "prime-coder.md",
        "prime-math.md",

        # Coding (12)
        "wish-llm.md",
        "wish-qa.md",
        "recipe-selector.md",
        "recipe-generator.md",
        "llm-judge.md",
        "canon-patch-writer.md",
        "proof-certificate-builder.md",
        "trace-distiller.md",
        "socratic-debugging.md",
        "shannon-compaction.md",
        "contract-compliance.md",
        "red-green-gate.md",

        # Math (4)
        "counter-required-routering.md",
        "algebra-number-theory-pack.md",
        "combinatorics-pack.md",
        "geometry-proof-pack.md",

        # Epistemic (4)
        "dual-truth-adjudicator.md",
        "epistemic-typing.md",
        "axiomatic-truth-lanes.md",
        "non-conflation-guard.md",

        # Verification (6)
        "rival-gps-triangulation.md",
        "meta-genome-alignment.md",
        "semantic-drift-detector.md",
        "triple-leak-protocol.md",
        "hamiltonian-security.md",
        "golden-replay-seal.md",

        # Infrastructure (5)
        "tool-output-normalizer.md",
        "artifact-hash-manifest-builder.md",
        "deterministic-resource-governor.md",
        "capability-surface-guard.md",
    ]


def create_skills_summary() -> str:
    """
    Create a concise summary of Prime Skills for prompt injection.

    This is more compact than loading full skill content (which can be 200KB+).
    Instead, we load key principles and rules.
    """
    return """# PRIME SKILLS v1.0.0+ OPERATIONAL CONTROLS

## IDENTITY
- Auth: 65537 (F4 Fermat Prime)
- Northstar: Phuc Forecast
- LEK: Intelligence = Memory × Care × Iteration

## VERIFICATION LADDER (MANDATORY)
OAuth(39,63,91) → 641 → 274177 → 65537

Where:
- OAuth(39,63,91): Care + Bridge + Stability
- 641: Edge tests (minimum 5 cases)
- 274177: Stress tests (scale, performance)
- 65537: God approval (F4 Fermat - final validation)

## RED-GREEN GATE (MANDATORY)
1. Create failing test/repro (RED - must fail)
2. Apply patch (implementation)
3. Verify test passes (GREEN - must pass)
4. NO patch without verified RED → GREEN transition

## CORE PRINCIPLES

### Coding (prime-coder.md)
- State machines (explicit states, transitions, forbidden states)
- Evidence bundle (/evidence/ with plan.json, tests.json, artifacts.json)
- Minimal reversible patches (canon-patch-writer.md)
- Socratic self-critique BEFORE execution
- Shannon Compaction (interface-first, 500→200 witness lines)

### Math (prime-math.md)
- Counter Bypass Protocol: LLM classifies → CPU Counter enumerates
- NO LLM counting/aggregation (hallucination rate 60%)
- Witness typing: proof://, compute://, exhaustive://, canon://
- Hard arithmetic ceilings (>3 multiplications → tool)
- Dual-witness proofs (theorem closure playbooks)

### Epistemic (Lane Algebra)
- Lane A: Framework provable (highest truth)
- Lane B: Classical provable
- Lane C: Conjecture/guess (lowest truth)
- MIN rule: min(A,C) = C (cannot upgrade C to A)
- NO conflation (framework ≠ classical)

### Quality Gates (harsh QA)
- 5 Rivals validation (adversarial validation)
- Semantic drift detector (behavioral hash tracking)
- Meta-genome alignment (cross-skill consistency)
- Triple leak protocol (lane leakage detection)

## PATCH GENERATION RULES

1. **Localize**: Use grep, read files, understand codebase
2. **Plan**: State machine with explicit states
3. **Minimal**: Single-purpose, reversible patches
4. **Test**: Create RED test, apply patch, verify GREEN
5. **Evidence**: Generate /evidence/ bundle with artifacts
6. **Format**: Unified diff (git format-patch style)

## OUTPUT FORMAT

Return ONLY the unified diff patch:
```diff
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -line,count +line,count @@
 context
-removed line
+added line
 context
```

NO explanations. NO markdown. ONLY the patch.
"""


def count_skills_loaded() -> int:
    """Count how many skill files exist."""
    try:
        skills_dir = get_skills_directory()
        return len(list(skills_dir.rglob("*.md")))
    except:
        return 0


def load_skill_excerpts(max_excerpts: int = 15, chars_per_skill: int = 400) -> str:
    """
    Load key excerpts from top skills to enhance context without overwhelming token budget.

    Takes first N characters from each of the top M most important skills.

    Args:
        max_excerpts: Number of top skills to excerpt (default: 15)
        chars_per_skill: Characters to extract per skill (default: 400)

    Returns:
        Formatted string with excerpts from key skills
    """
    skills_dir = get_skills_directory()
    essential = get_essential_skills()[:max_excerpts]  # Top 15 skills

    excerpts = []
    for skill_name in essential:
        # Try root directory first
        skill_path = skills_dir / skill_name
        if not skill_path.exists():
            # Try subdirectories
            for subdir in ["coding", "math", "epistemic", "verification", "infrastructure"]:
                candidate = skills_dir / subdir / skill_name
                if candidate.exists():
                    skill_path = candidate
                    break

        if skill_path.exists():
            try:
                content = skill_path.read_text()
                # Extract first N chars (usually header + key points)
                excerpt = content[:chars_per_skill]
                # Clean up incomplete lines at end
                if len(content) > chars_per_skill:
                    last_newline = excerpt.rfind('\n')
                    if last_newline > 0:
                        excerpt = excerpt[:last_newline]

                excerpts.append(f"## {skill_name}\n{excerpt}\n[...truncated...]")
            except:
                continue

    if not excerpts:
        return ""

    return f"""# KEY SKILL EXCERPTS (Top {len(excerpts)} of {len(essential)})

{chr(10).join(excerpts)}"""
