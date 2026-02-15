"""
LLM-based patch generation for SWE-bench.

Converts problem statements into unified diff patches.

This is Phase 2 of the implementation plan.
Currently a placeholder - will integrate with stillwater.llm.
"""

from typing import Optional
from pathlib import Path


def generate_patch(
    problem_statement: str,
    repo_dir: Path,
    model: str = "llama3.1:8b",
    temperature: float = 0.0,
) -> Optional[str]:
    """
    Generate a patch from a problem statement.

    Args:
        problem_statement: Description of the bug to fix
        repo_dir: Path to repository (for context)
        model: LLM model to use
        temperature: Sampling temperature (0.0 for deterministic)

    Returns:
        Unified diff format patch, or None if generation fails

    TODO:
        - Integrate with stillwater.llm.LLMClient
        - Implement codebase exploration (grep, read files)
        - Build context window with relevant code
        - Prompt engineering for patch generation
        - Parse LLM output to extract unified diff
    """
    raise NotImplementedError("Patch generation not yet implemented (Phase 2)")
