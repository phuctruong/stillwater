#!/usr/bin/env python3
"""
Claude Code Local Wrapper - Uses Claude Code CLI with -p flag
Auth: 65537
Purpose: Unified wrapper for Claude Code CLI

This wrapper:
1. Uses local Claude Code CLI (claude-code command)
2. Sends prompts via -p flag to claude-code CLI
3. Parses and returns responses
4. Provides clean interface for patch generation, solving, etc.
5. Works with OOLONG, IMO, and SWE-bench

No server needed - directly invokes claude-code CLI
"""

import subprocess
import json
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any


class ClaudeCodeWrapper:
    """Wrapper for Claude Code CLI (uses -p flag for prompts)."""

    def __init__(
        self,
        cli_path: Optional[str] = None,
        model: str = "claude-haiku-4-5-20251001",
    ):
        """
        Initialize Claude Code wrapper.

        Args:
            cli_path: Path to claude-code CLI (auto-detect if None)
            model: Model to use (haiku, sonnet, opus) - may be overridden by CLI config
        """
        self.cli_path = cli_path or self._find_claude_cli()
        self.model = model
        self.localhost_url = "claude-code-cli"  # For compatibility
        self.server_running = self._check_cli()

    def _find_claude_cli(self) -> str:
        """Find Claude Code CLI in PATH or common locations."""
        # Check PATH
        result = subprocess.run(["which", "claude-code"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()

        # Check common locations
        common_paths = [
            "/usr/local/bin/claude-code",
            "/opt/claude-code/bin/claude-code",
            os.path.expanduser("~/.local/bin/claude-code"),
            "/usr/bin/claude-code",
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        return "claude-code"  # Hope it's in PATH

    def _check_cli(self) -> bool:
        """Check if Claude Code CLI is available."""
        try:
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def query(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> Optional[str]:
        """
        Query Claude Code CLI using -p flag.

        Args:
            prompt: User prompt
            system: System prompt (optional - prepended to prompt)
            temperature: Temperature (0.0 = deterministic)
            max_tokens: Max tokens in response

        Returns:
            Response text or None if error
        """
        if not self.server_running:
            print(f"⚠️  Claude Code CLI not found at {self.cli_path}")
            print(f"   Install with: pip install claude-code")
            return None

        try:
            # Combine system and user prompt
            full_prompt = prompt
            if system:
                full_prompt = f"{system}\n\n{prompt}"

            # Call claude-code CLI with -p flag for prompt
            cmd = [self.cli_path, "-p", full_prompt]

            # Add optional parameters
            if temperature != 0.7:  # 0.7 is default
                cmd.extend(["--temperature", str(temperature)])

            if max_tokens != 4096:  # 4096 is default
                cmd.extend(["--max-tokens", str(max_tokens)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                # Response is in stdout
                return result.stdout.strip()
            else:
                print(f"❌ Claude Code CLI error: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print(f"❌ Claude Code CLI timed out after 120 seconds")
            return None
        except FileNotFoundError:
            print(f"❌ Claude Code CLI not found: {self.cli_path}")
            return None
        except Exception as e:
            print(f"❌ Error calling Claude Code CLI: {e}")
            return None

    def generate_patch(
        self, problem_statement: str, repo_context: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a code patch for the given problem.

        Args:
            problem_statement: Description of the bug/feature
            repo_context: Optional context about the repository

        Returns:
            Unified diff format patch or None
        """
        prompt = f"""You are an expert code fixer. Generate a MINIMAL, REVERSIBLE patch.

PROBLEM:
{problem_statement}

{f'REPO CONTEXT:{chr(10)}{repo_context}' if repo_context else ''}

OUTPUT ONLY a unified diff (no explanation):
```diff
--- a/file/path
+++ b/file/path
@@ -start,count +start,count @@
 context
-removed
+added
```

Generate the patch:"""

        system = """You are an expert at writing minimal, surgical code patches.
- Only change what's necessary
- Use unified diff format
- Include context lines
- Ensure syntactically valid
- No refactoring, just fixes"""

        response = self.query(prompt, system=system, temperature=0.0)

        if response:
            # Extract diff block if wrapped in markdown
            if "```diff" in response:
                start = response.find("```diff") + 7
                end = response.find("```", start)
                return response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                return response[start:end].strip()
            return response

        return None

    def solve_math(self, problem: str) -> Optional[str]:
        """
        Solve a math problem.

        Args:
            problem: Math problem description

        Returns:
            Solution or None
        """
        prompt = f"""Solve this problem step-by-step with exact arithmetic.

PROBLEM:
{problem}

Requirements:
- Use exact arithmetic (fractions, not floats)
- Show all steps
- Verify the answer
- State the final answer clearly"""

        system = """You are a math expert using exact arithmetic.
- Use Fraction() for division
- Use integers where possible
- Show step-by-step work
- Double-check calculations"""

        return self.query(prompt, system=system, temperature=0.0)

    def solve_counting(self, query: str) -> Optional[str]:
        """
        Solve a counting problem (for OOLONG).

        Args:
            query: Counting problem

        Returns:
            Answer or None
        """
        prompt = f"""Solve this counting problem using exact enumeration.

PROBLEM:
{query}

Requirements:
- Enumerate all items exactly
- Use Python Counter for counting
- Return only the final count as a number
- Show brief working"""

        system = """You solve counting problems using exact enumeration.
- List all items explicitly
- Count exactly (not estimate)
- Use Python Counter() syntax
- Return just the number"""

        return self.query(prompt, system=system, temperature=0.0)

    def explain_code(self, code: str, question: str) -> Optional[str]:
        """
        Explain code behavior.

        Args:
            code: Code to explain
            question: What to explain

        Returns:
            Explanation or None
        """
        prompt = f"""Explain this code:

CODE:
{code}

QUESTION:
{question}

Answer clearly and concisely."""

        return self.query(prompt)

    def verify_solution(self, problem: str, solution: str) -> bool:
        """
        Verify if a solution is correct.

        Args:
            problem: Original problem
            solution: Proposed solution

        Returns:
            True if correct, False otherwise
        """
        prompt = f"""Verify if this solution is correct.

PROBLEM:
{problem}

SOLUTION:
{solution}

Answer: Is this solution correct? (YES/NO)
Briefly explain why."""

        response = self.query(prompt)

        if response:
            return "yes" in response.lower()

        return False


# Convenience function
def create_wrapper(model: str = "claude-haiku-4-5-20251001") -> ClaudeCodeWrapper:
    """Create and return a Claude Code wrapper."""
    wrapper = ClaudeCodeWrapper(model=model)
    if not wrapper.server_running:
        print(f"⚠️  Claude Code CLI not found at {wrapper.cli_path}")
        print(f"   Install with: pip install claude-code")
        print(f"   Or check: which claude-code")
    return wrapper


if __name__ == "__main__":
    # Test the wrapper
    wrapper = create_wrapper()

    if wrapper.server_running:
        print("✅ Claude Code CLI is available")
        print(f"   CLI path: {wrapper.cli_path}")

        # Test query
        response = wrapper.query("What is 2+2?", temperature=0.0)
        if response:
            print(f"Response: {response}")
        else:
            print("Failed to get response")
    else:
        print("❌ Claude Code CLI not found")
        print("Install with: pip install claude-code")
        print(f"Expected at: {wrapper.cli_path}")
