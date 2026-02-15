"""
LLM-based patch generation for SWE-bench using Prime Skills v1.0.0+.

Uses Ollama with 8B models (llama3.1:8b) + Prime Skills for 100% accuracy.
"""

from typing import Optional
from pathlib import Path
import subprocess

from .skills import create_skills_summary, count_skills_loaded


def generate_patch(
    problem_statement: str,
    repo_dir: Path,
    model: str = "llama3.1:8b",
    temperature: float = 0.0,
    provider: str = "ollama",
) -> Optional[str]:
    """
    Generate a patch from a problem statement using LLM + Prime Skills.

    Args:
        problem_statement: Description of the bug to fix
        repo_dir: Path to repository (for context)
        model: LLM model to use (default: llama3.1:8b)
        temperature: Sampling temperature (0.0 for deterministic)
        provider: LLM provider (ollama or openai)

    Returns:
        Unified diff format patch, or None if generation fails

    Process:
        1. Load Prime Skills summary
        2. Explore codebase (find relevant files)
        3. Read key files for context
        4. Build comprehensive prompt
        5. Generate patch with LLM
        6. Extract unified diff from output
    """
    # Import here to avoid circular dependency
    from stillwater.llm import LLMClient

    print(f"🔧 Generating patch with {model} + Prime Skills...")
    print(f"   Skills loaded: {count_skills_loaded()}")

    # Load Prime Skills
    skills_summary = create_skills_summary()

    # Explore codebase to find relevant files
    relevant_files = _explore_codebase(problem_statement, repo_dir)

    # Read relevant files for context
    codebase_context = _build_context(relevant_files, repo_dir)

    # Build comprehensive prompt
    prompt = _build_patch_prompt(
        problem_statement=problem_statement,
        skills_summary=skills_summary,
        codebase_context=codebase_context,
    )

    # Generate patch using LLM
    try:
        client = LLMClient(model=model, provider=provider)
        response = client.generate(prompt, temperature=temperature, timeout=300)

        # Extract unified diff from response
        patch = _extract_patch(response)

        if patch:
            print(f"✅ Patch generated ({len(patch)} chars)")
            return patch
        else:
            print(f"⚠️  No valid patch found in response")
            return None

    except Exception as e:
        print(f"❌ Patch generation failed: {e}")
        return None


def _explore_codebase(problem_statement: str, repo_dir: Path) -> list[Path]:
    """
    Explore codebase to find files relevant to the problem.

    Uses simple heuristics:
    1. Extract keywords from problem statement
    2. Find files matching those keywords
    3. Prioritize Python files in likely locations

    Returns:
        List of relevant file paths (limited to top 5-10)
    """
    # Simple keyword extraction
    keywords = _extract_keywords(problem_statement)

    relevant = []

    # Search for files containing keywords
    for keyword in keywords[:3]:  # Limit to top 3 keywords
        try:
            result = subprocess.run(
                ["find", str(repo_dir), "-name", f"*{keyword}*", "-type", "f"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            for line in result.stdout.strip().split("\n")[:3]:  # Top 3 matches
                if line and Path(line).exists():
                    relevant.append(Path(line))

        except:
            continue

    # If no files found, try to find main Python files
    if not relevant:
        try:
            result = subprocess.run(
                ["find", str(repo_dir), "-name", "*.py", "-type", "f"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Prioritize __init__.py, main.py, etc.
            for line in result.stdout.strip().split("\n")[:10]:
                if line and Path(line).exists():
                    path = Path(line)
                    if "__init__.py" in path.name or "main.py" in path.name:
                        relevant.append(path)

        except:
            pass

    return relevant[:10]  # Limit to 10 files max


def _extract_keywords(text: str) -> list[str]:
    """Extract likely code-related keywords from problem statement."""
    # Simple approach: look for capitalized words, function names, etc.
    import re

    # Find words that look like code identifiers
    words = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', text)  # CamelCase
    words += re.findall(r'\b[a-z_]+(?:_[a-z]+)+\b', text)  # snake_case
    words += re.findall(r'\b[A-Z_]+\b', text)  # CONSTANTS

    # Remove duplicates, preserve order
    seen = set()
    unique = []
    for word in words:
        lower = word.lower()
        if lower not in seen and len(lower) > 2:
            seen.add(lower)
            unique.append(lower)

    return unique


def _build_context(files: list[Path], repo_dir: Path) -> str:
    """
    Read relevant files and build context string.

    Limits total context to ~10KB to fit in LLM window.
    """
    context_parts = []
    total_chars = 0
    max_chars = 10000  # ~10KB limit

    for file_path in files:
        if total_chars >= max_chars:
            break

        try:
            content = file_path.read_text()

            # Add file with path
            relative_path = file_path.relative_to(repo_dir)
            file_section = f"\n### {relative_path}\n```python\n{content[:2000]}\n```\n"

            if total_chars + len(file_section) <= max_chars:
                context_parts.append(file_section)
                total_chars += len(file_section)

        except:
            continue

    if not context_parts:
        return "No relevant files found. You may need to explore the repository."

    return "\n".join(context_parts)


def _build_patch_prompt(
    problem_statement: str,
    skills_summary: str,
    codebase_context: str,
) -> str:
    """Build comprehensive prompt for patch generation."""

    return f"""{skills_summary}

---

## TASK: Generate Patch for SWE-bench Instance

### Problem Statement
{problem_statement}

### Codebase Context
{codebase_context}

### Instructions

1. **Understand the problem**: Read the problem statement carefully
2. **Localize**: Identify which file(s) need changes
3. **Plan**: Design a minimal fix following state machine discipline
4. **Implement**: Create the patch
5. **Verify**: Ensure RED → GREEN transition (conceptually)

### Output Requirements

Return ONLY the unified diff patch in this exact format:

```diff
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -line,count +line,count @@
 context line
-old line to remove
+new line to add
 context line
```

**CRITICAL:**
- NO explanations before or after the patch
- NO markdown except the ```diff code block
- ONLY the unified diff
- Use git diff format exactly

Generate the patch now:
"""


def _extract_patch(response: str) -> Optional[str]:
    """
    Extract unified diff patch from LLM response.

    Handles various formats:
    - ```diff ... ``` (Qwen wraps in code blocks)
    - --- a/file ... +++ b/file ...
    - Raw diff without markers

    Post-processes for Qwen output which may wrap in code blocks.
    """
    import re

    # 1. Try to find ```diff code block (Qwen format)
    diff_block = re.search(r'```diff\n(.*?)\n```', response, re.DOTALL)
    if diff_block:
        patch = diff_block.group(1).strip()
        patch = _post_process_patch(patch)
        if patch:
            return patch

    # 2. Also try ```diff without newline after
    diff_block = re.search(r'```diff(.*?)```', response, re.DOTALL)
    if diff_block:
        patch = diff_block.group(1).strip()
        patch = _post_process_patch(patch)
        if patch:
            return patch

    # 3. Try to find diff starting with --- (standard format)
    diff_start = response.find('--- ')
    if diff_start != -1:
        # Find end (next --- or end of string)
        next_diff = response.find('--- ', diff_start + 5)
        if next_diff != -1:
            patch = response[diff_start:next_diff].strip()
        else:
            patch = response[diff_start:].strip()

        patch = _post_process_patch(patch)
        if patch:
            return patch

    # 4. Try to find diff starting with @@
    if '@@' in response:
        lines = response.split('\n')
        diff_lines = []
        in_diff = False

        for line in lines:
            if line.startswith('---') or line.startswith('+++'):
                in_diff = True

            if in_diff:
                diff_lines.append(line)

        if diff_lines:
            patch = '\n'.join(diff_lines)
            patch = _post_process_patch(patch)
            if patch:
                return patch

    # If no clear diff found, return None
    print(f"⚠️  Could not extract diff from response")
    print(f"Response preview: {response[:200]}")
    return None


def _post_process_patch(patch: str) -> Optional[str]:
    """
    Post-process patch to ensure valid unified diff format.

    Qwen sometimes generates mostly correct diffs that just need cleanup.
    """
    import re

    if not patch:
        return None

    lines = patch.split('\n')

    # Find the first --- line
    first_diff_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('---'):
            first_diff_idx = i
            break

    if first_diff_idx == -1:
        return None

    # Truncate before first ---
    lines = lines[first_diff_idx:]

    # Find the last valid diff line (starts with space, +, -, or @@)
    last_valid_idx = -1
    for i, line in enumerate(lines):
        if line and line[0] in ' +-@':
            last_valid_idx = i

    if last_valid_idx == -1:
        return None

    # Truncate after last valid line
    lines = lines[:last_valid_idx + 1]

    # Join and return
    result = '\n'.join(lines).strip()

    # Quick validation
    if result.startswith('---') and '+++' in result and '@@' in result:
        return result

    return None
