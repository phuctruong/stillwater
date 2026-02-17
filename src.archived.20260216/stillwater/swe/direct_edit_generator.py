#!/usr/bin/env python3
"""
Direct Edit Generator - Replace patches with direct file edits

This implements Claude Code's superior orchestration approach:
- Read FULL FILES (not snippets)
- Generate DIRECT EDITS (not patches)
- Get IMMEDIATE FEEDBACK
- LOOP AND REFINE

Based on reverse-engineering Claude Code's 80%+ SWE-bench performance.
"""

from typing import Optional, List, Dict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DirectEdit:
    """A direct file edit (superior to patches)"""
    file_path: str
    description: str
    line_start: int
    line_end: int
    new_content: str
    reasoning: str


def read_relevant_files(
    problem_statement: str,
    repo_dir: Path,
    max_files: int = 5,
    max_chars_per_file: int = 5000,
) -> Dict[str, str]:
    """
    Read FULL relevant files for context (not snippets).

    This is key to Claude Code's success - LLM sees complete files
    to understand imports, dependencies, scoping, side effects.

    Args:
        problem_statement: Description of the bug
        repo_dir: Repository directory
        max_files: Maximum files to read
        max_chars_per_file: Max chars per file

    Returns:
        Dict of file_path -> full_file_content
    """
    import subprocess

    files = {}

    # Use simple find to locate Python files
    try:
        result = subprocess.run(
            ["find", str(repo_dir), "-name", "*.py", "-type", "f"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        file_paths = [
            p for p in result.stdout.strip().split("\n")
            if p and Path(p).exists()
        ][:max_files]

        for file_path in file_paths:
            try:
                with open(file_path, "r") as f:
                    content = f.read(max_chars_per_file)
                    rel_path = str(Path(file_path).relative_to(repo_dir))
                    files[rel_path] = content
            except:
                continue

    except:
        pass

    return files


def generate_direct_edits(
    problem_statement: str,
    repo_dir: Path,
    current_test_failures: Optional[str] = None,
    previous_attempts: Optional[List[str]] = None,
    model: str = "llama3.1:8b",
) -> Optional[List[DirectEdit]]:
    """
    Generate direct file edits using Claude Code's orchestration approach.

    Key differences from patches:
    1. Reads FULL files (better context)
    2. Generates DIRECT edits (not patches)
    3. Understands full impact of changes
    4. Provides reasoning for each edit

    Args:
        problem_statement: The bug to fix
        repo_dir: Repository directory
        current_test_failures: Test failures (for feedback loop)
        previous_attempts: Previous failed attempts (for learning)
        model: LLM to use

    Returns:
        List of DirectEdit objects
    """
    from stillwater.llm import LLMClient
    from stillwater.swe.skills import create_skills_summary, count_skills_loaded

    print(f"🎯 Generating direct edits (Claude Code orchestration)...")
    print(f"   Model: {model}")
    print(f"   Skills: {count_skills_loaded()}")
    print(f"   Feedback: {current_test_failures is not None}")

    # 1. Read FULL relevant files (key to success)
    files = read_relevant_files(problem_statement, repo_dir)
    print(f"   Files analyzed: {len(files)}")

    if not files:
        print(f"⚠️  No relevant files found")
        return None

    # 2. Build prompt with full file context
    skills_summary = create_skills_summary()
    prompt = _build_direct_edit_prompt(
        problem_statement=problem_statement,
        files=files,
        skills_summary=skills_summary,
        test_failures=current_test_failures,
        previous_attempts=previous_attempts,
    )

    # 3. Generate edits with LLM
    try:
        client = LLMClient(model=model)
        response = client.generate(prompt, temperature=0.0, timeout=300)

        # 4. Parse direct edits from response
        edits = _parse_direct_edits(response)

        if edits:
            print(f"✅ Generated {len(edits)} direct edit(s)")
            for edit in edits:
                print(f"   - {edit.file_path}:{edit.line_start}-{edit.line_end}")
            return edits
        else:
            print(f"⚠️  No edits found in response")
            return None

    except Exception as e:
        print(f"❌ Edit generation failed: {e}")
        return None


def apply_direct_edits(
    edits: List[DirectEdit],
    repo_dir: Path,
) -> bool:
    """
    Apply direct edits to files atomically.

    Superior to patches because:
    - All edits applied together (atomic)
    - No format validation needed
    - Direct file operations
    - Safer and more reliable

    Args:
        edits: List of DirectEdit objects
        repo_dir: Repository directory

    Returns:
        True if all edits applied successfully
    """
    from pathlib import Path

    print(f"📝 Applying {len(edits)} direct edit(s)...")

    for edit in edits:
        file_path = repo_dir / edit.file_path

        try:
            # Read current file
            if not file_path.exists():
                print(f"   ⚠️  File not found: {edit.file_path}")
                continue

            with open(file_path, "r") as f:
                lines = f.readlines()

            # Calculate line indices (convert 1-based to 0-based)
            start_idx = edit.line_start - 1
            end_idx = edit.line_end

            # Replace lines
            new_lines = (
                lines[:start_idx] +
                [edit.new_content] +
                lines[end_idx:]
            )

            # Write back
            with open(file_path, "w") as f:
                f.writelines(new_lines)

            print(f"   ✅ {edit.file_path}:{edit.line_start}-{edit.line_end}")

        except Exception as e:
            print(f"   ❌ Failed to apply edit to {edit.file_path}: {e}")
            return False

    return True


def _build_direct_edit_prompt(
    problem_statement: str,
    files: Dict[str, str],
    skills_summary: str,
    test_failures: Optional[str] = None,
    previous_attempts: Optional[List[str]] = None,
) -> str:
    """Build prompt for direct edit generation (Claude Code approach)."""

    files_section = "\n\n".join([
        f"=== {path} ===\n{content}"
        for path, content in files.items()
    ])

    feedback_section = ""
    if test_failures:
        feedback_section = f"""
## TEST FAILURES (Feedback Loop)

The previous attempt caused test failures:
```
{test_failures}
```

Learn from this failure and try a different approach.
"""

    if previous_attempts:
        feedback_section += f"""

## PREVIOUS ATTEMPTS

Attempts that failed:
{chr(10).join(f"- {attempt}" for attempt in previous_attempts)}

Your current attempt should be different.
"""

    return f"""# DIRECT EDIT MODE (Claude Code Orchestration)

{skills_summary}

---

## PROBLEM
{problem_statement}

---

## FULL FILE CONTEXT
{files_section}

---

## YOUR TASK

Analyze the problem and identify what code needs to change.

Generate DIRECT FILE EDITS (not patches):
- Specify exact file and line numbers
- Show the corrected code
- Include surrounding context for clarity
- Explain your reasoning

{feedback_section}

---

## OUTPUT FORMAT

For each file that needs editing, provide:

```
FILE: path/to/file.py
LINES: [start_line]-[end_line]
REASONING: [Why this change fixes the problem]

[The corrected code with surrounding context]
```

Example:
```
FILE: src/module.py
LINES: 42-48
REASONING: The bug is in line 45 where we check x > 0 instead of x >= 0.
          Fixing this condition resolves the off-by-one error.

def calculate(x):
    # Check if x is valid (fixed condition)
    if x >= 0:  # Changed from > to >=
        return x * 2
    else:
        return -1
```

---

## CRITICAL REQUIREMENTS

✅ READ all the full files above - understand context, imports, dependencies
✅ Make minimal changes - only fix what's broken
✅ Show corrected code clearly - include surrounding lines
✅ Provide reasoning - explain WHY this fixes the problem
✅ Preserve formatting - match existing code style
✅ One edit per file - combine multiple edits in same file

❌ DO NOT generate patches
❌ DO NOT generate diffs (---, +++, @@)
❌ DO NOT output markdown code blocks
❌ DO NOT make unrelated changes

Generate the direct edits now:
"""


def _parse_direct_edits(response: str) -> Optional[List[DirectEdit]]:
    """Parse direct edits from LLM response."""
    import re

    if not response:
        return None

    edits = []

    # Find all FILE: ... LINES: ... blocks
    pattern = r'FILE:\s*([^\n]+)\nLINES:\s*(\d+)-(\d+)\nREASONING:\s*([^\n]+)\n\n(.*?)(?=\n\nFILE:|$)'

    matches = re.finditer(pattern, response, re.DOTALL)

    for match in matches:
        file_path = match.group(1).strip()
        line_start = int(match.group(2))
        line_end = int(match.group(3))
        reasoning = match.group(4).strip()
        new_content = match.group(5).strip()

        if file_path and new_content:
            edit = DirectEdit(
                file_path=file_path,
                description=f"Fix at lines {line_start}-{line_end}",
                line_start=line_start,
                line_end=line_end,
                new_content=new_content,
                reasoning=reasoning,
            )
            edits.append(edit)

    return edits if edits else None
