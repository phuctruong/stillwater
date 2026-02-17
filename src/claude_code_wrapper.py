#!/usr/bin/env python3
"""
Claude Code Local Wrapper - Uses Claude Code CLI and localhost
Auth: 65537
Purpose: Unified wrapper for Claude Code local server

This wrapper:
1. Connects to local Claude Code server (default localhost:8080)
2. Uses Claude Code CLI for inference
3. Provides clean interface for patch generation, solving, etc.
4. Works with OOLONG, IMO, and SWE-bench

No Anthropic API key needed - uses local Claude Code installation
"""

import subprocess
import json
import os
import requests
from pathlib import Path
from typing import Optional, Dict, Any
import time


class ClaudeCodeWrapper:
    """Wrapper for Claude Code local server."""

    def __init__(
        self,
        localhost_url: str = "http://localhost:8080",
        cli_path: Optional[str] = None,
        model: str = "claude-4.5-sonnet",  # or claude-haiku, claude-opus, etc.
    ):
        """
        Initialize Claude Code wrapper.

        Args:
            localhost_url: URL of Claude Code local server
            cli_path: Path to claude-code CLI (auto-detect if None)
            model: Model to use (haiku, sonnet, opus)
        """
        self.localhost_url = localhost_url
        self.cli_path = cli_path or self._find_claude_cli()
        self.model = model
        self.server_running = self._check_server()

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
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        return "claude-code"  # Hope it's in PATH

    def _check_server(self) -> bool:
        """Check if Claude Code local server is running."""
        try:
            response = requests.get(f"{self.localhost_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False

    def start_server(self) -> bool:
        """Start Claude Code local server."""
        try:
            # Try to start server
            subprocess.Popen(
                [self.cli_path, "server", "--host", "localhost", "--port", "8080"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(2)
            return self._check_server()
        except Exception as e:
            print(f"❌ Failed to start Claude Code server: {e}")
            return False

    def query(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> Optional[str]:
        """
        Query Claude Code local server.

        Args:
            prompt: User prompt
            system: System prompt (optional)
            temperature: Temperature (0.0 = deterministic)
            max_tokens: Max tokens in response

        Returns:
            Response text or None if error
        """
        if not self.server_running:
            print(f"⚠️  Claude Code server not responding at {self.localhost_url}")
            print(f"   Try: claude-code server --host localhost --port 8080")
            return None

        try:
            # Use local HTTP interface
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            response = requests.post(
                f"{self.localhost_url}/v1/chat/completions",
                json=payload,
                timeout=120,
            )

            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
            else:
                print(f"❌ Server returned {response.status_code}: {response.text}")
                return None

        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to Claude Code server at {self.localhost_url}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
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
        print(f"⚠️  Claude Code server not running at {wrapper.localhost_url}")
        print(f"   Start with: claude-code server --host localhost --port 8080")
    return wrapper


if __name__ == "__main__":
    # Test the wrapper
    wrapper = create_wrapper()

    if wrapper.server_running:
        print("✅ Claude Code server is running")

        # Test query
        response = wrapper.query("What is 2+2?", temperature=0.0)
        print(f"Response: {response}")
    else:
        print("❌ Claude Code server not running")
        print("Start with: claude-code server --host localhost --port 8080")
