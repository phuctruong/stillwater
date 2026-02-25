#!/usr/bin/env python3
"""
ABCD Baseline Testing - WITHOUT Skills Loaded

Tests the same tasks but with NO system prompt injection.
This establishes the baseline for uplift measurement.

Compared to test_abcd_coding.py which loads prime-coder skills.
"""

import sys
import json
import hashlib
import ast
import subprocess
from pathlib import Path
from typing import NamedTuple
from datetime import datetime

import pytest
import yaml

_CLI_SRC = Path(__file__).parent.parent.parent / "src" / "cli" / "src"
if str(_CLI_SRC) not in sys.path:
    sys.path.insert(0, str(_CLI_SRC))

from stillwater.llm_client import LLMClient


# ============================================================
# Data Models
# ============================================================

class CodingTestResult(NamedTuple):
    """Result from a single coding task."""
    model: str
    task_name: str
    syntax_valid: bool
    functional_pass: bool
    quality_score: float = 0.0
    timestamp: str = ""
    code_hash: str = ""


# ============================================================
# Code Analysis Functions
# ============================================================

def validate_syntax(code: str) -> tuple[bool, str]:
    """Check if code is valid Python syntax."""
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Parse error: {str(e)}"


def extract_python_code(response: str) -> str:
    """Extract Python code block from response."""
    if "```python" in response:
        start = response.find("```python") + len("```python")
        end = response.find("```", start)
        if end > start:
            code = response[start:end].strip()
            if code:
                return code

    if "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        if end > start:
            code = response[start:end].strip()
            if code:
                return code

    lines = response.split('\n')
    code_lines = []
    in_code = False

    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(kw) for kw in ['def ', 'class ', 'import ', 'from ', '@', 'if ', 'for ', 'while ']):
            in_code = True

        if in_code:
            code_lines.append(line)

    if code_lines:
        return '\n'.join(code_lines).strip()

    return response.strip()


def calculate_code_quality_score(code: str) -> float:
    """Calculate code quality score (0-1)."""
    score = 0.0

    try:
        tree = ast.parse(code)
    except Exception:
        return 0.0

    has_module_docstring = ast.get_docstring(tree) is not None
    if has_module_docstring:
        score += 0.1

    has_type_hints = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and (node.returns is not None or any(
            arg.annotation is not None
            for arg in node.args.args
        ))
        for node in ast.walk(tree)
    )
    if has_type_hints:
        score += 0.15

    has_error_handling = any(
        isinstance(node, ast.Try)
        for node in ast.walk(tree)
    )
    if has_error_handling:
        score += 0.15

    has_assertions = any(
        isinstance(node, ast.Assert)
        for node in ast.walk(tree)
    )
    has_tests = "test_" in code or "assert " in code
    if has_assertions or has_tests:
        score += 0.2

    has_functions = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        for node in ast.walk(tree)
    )
    if has_functions:
        score += 0.15

    lines = len(code.split('\n'))
    if 20 <= lines <= 500:
        score += 0.1

    has_eval = "eval(" in code
    has_exec = "exec(" in code
    has_import_star = "import *" in code
    if has_eval or has_exec or has_import_star:
        score -= 0.1

    return min(1.0, max(0.0, score))


def validate_code_functionality(code: str, task_name: str) -> tuple[bool, str]:
    """Test if code runs without errors."""
    valid, error = validate_syntax(code)
    if not valid:
        return False, error

    try:
        namespace = {
            "__name__": "__main__",
            "print": print,
            "len": len,
            "range": range,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "sum": sum,
            "max": max,
            "min": min,
            "sorted": sorted,
            "enumerate": enumerate,
            "zip": zip,
        }

        exec(code, namespace)
        return True, ""
    except Exception as e:
        return False, f"Execution error: {str(e)}"


# ============================================================
# Baseline Tasks (Same 4 Tasks, No Skills)
# ============================================================

BASELINE_TASKS = {
    "task_1_simple_sum": {
        "name": "Simple Sum Function",
        "prompt": """Show me the complete Python code (as a markdown ```python code block) for a function that sums all integers in a list.

Requirements:
1. Function should be named `sum_integers`
2. It should handle empty lists (return 0)
3. Include docstring
4. Include type hints
5. Include test cases in the code block

Example:
    sum_integers([1, 2, 3]) -> 6
    sum_integers([]) -> 0

Return ONLY the code in a markdown block, no explanations.
""",
    },
    "task_2_palindrome": {
        "name": "Palindrome Checker",
        "prompt": """Show me the complete Python code (as a markdown ```python code block) for a function that checks if a string is a palindrome.

Requirements:
1. Function should be named `is_palindrome`
2. Should be case-insensitive
3. Should ignore spaces and punctuation
4. Include docstring with examples
5. Include type hints
6. Include comprehensive test cases

Example:
    is_palindrome("A man, a plan, a canal: Panama") -> True
    is_palindrome("hello") -> False

Return ONLY the code in a markdown block, no explanations.
""",
    },
    "task_3_fibonacci": {
        "name": "Fibonacci Generator",
        "prompt": """Show me the complete Python code (as a markdown ```python code block) for a function that generates Fibonacci numbers.

Requirements:
1. Function should be named `fibonacci`
2. Takes `n` parameter (number of Fibonacci numbers to generate)
3. Should return a list of Fibonacci numbers
4. Should handle edge cases (n=0, n=1, negative n)
5. Include docstring with examples
6. Include type hints
7. Include error handling for invalid input

Example:
    fibonacci(5) -> [0, 1, 1, 2, 3]
    fibonacci(0) -> []

Return ONLY the code in a markdown block, no explanations.
""",
    },
    "task_4_dict_merge": {
        "name": "Dictionary Merger",
        "prompt": """Show me the complete Python code (as a markdown ```python code block) for a function that merges multiple dictionaries.

Requirements:
1. Function should be named `merge_dicts`
2. Takes variable number of dictionaries as arguments
3. Later dictionaries override earlier ones on key conflicts
4. Should handle None values gracefully
5. Include docstring
6. Include type hints with typing.Dict, typing.Any
7. Include comprehensive error handling
8. Include test cases for edge cases

Example:
    merge_dicts({"a": 1}, {"b": 2}) -> {"a": 1, "b": 2}
    merge_dicts({"a": 1}, {"a": 2}) -> {"a": 2}

Return ONLY the code in a markdown block, no explanations.
""",
    },
}


# ============================================================
# Test Fixtures
# ============================================================

@pytest.fixture(scope="session")
def llm_client() -> LLMClient:
    """LLM client for testing."""
    return LLMClient(provider="http", config={"http": {"url": "http://localhost:8080"}})


# ============================================================
# Baseline Test Class (NO SKILLS)
# ============================================================

class TestABCDBaseline:
    """ABCD baseline testing without skill injection."""

    MODELS = ["haiku", "sonnet", "opus"]

    @pytest.fixture(autouse=True)
    def setup_results_dir(self):
        """Create results directory structure."""
        results_dir = Path(__file__).parent / "results_baseline"
        results_dir.mkdir(exist_ok=True)
        for model in self.MODELS:
            (results_dir / model).mkdir(exist_ok=True)
        self.results_dir = results_dir

    @pytest.mark.parametrize("task_key", list(BASELINE_TASKS.keys()))
    @pytest.mark.parametrize("model", ["haiku", "sonnet", "opus"])
    def test_baseline_task(
        self,
        task_key: str,
        model: str,
        llm_client: LLMClient,
    ):
        """Test a single task WITHOUT skill injection (baseline)."""
        task = BASELINE_TASKS[task_key]

        print(f"\n{'='*70}")
        print(f"BASELINE TEST: {task['name']} | Model: {model.upper()}")
        print(f"(No skills loaded)")
        print(f"{'='*70}")

        # Invoke WITHOUT skill injection - just basic system prompt
        messages = [
            {"role": "system", "content": "You are a helpful Python coding assistant."},
            {"role": "user", "content": task["prompt"]},
        ]

        result = llm_client.chat(
            messages,
            model=model,
            max_tokens=1024,
            temperature=0.0,
            timeout=60.0,
        )
        response = result.text

        # Extract code
        code = extract_python_code(response)

        # Validate syntax
        syntax_valid, syntax_error = validate_syntax(code)

        # Functional test
        functional_pass = False
        if syntax_valid:
            functional_pass, _ = validate_code_functionality(code, task_key)

        # Quality score
        quality_score = calculate_code_quality_score(code)

        # Create result
        result_obj = CodingTestResult(
            model=model,
            task_name=task_key,
            syntax_valid=syntax_valid,
            functional_pass=functional_pass,
            quality_score=quality_score,
            timestamp=datetime.now().isoformat(),
            code_hash=hashlib.md5(code.encode()).hexdigest()[:8],
        )

        # Print results
        print(f"Syntax Valid:        {result_obj.syntax_valid}")
        if syntax_error:
            print(f"Syntax Error:        {syntax_error}")

        print(f"Functional Pass:     {result_obj.functional_pass}")
        print(f"Quality Score:       {result_obj.quality_score:.2f}")
        print(f"Code Length:         {len(code)} chars")

        # Save result
        result_file = self.results_dir / model / f"{task_key}_{model}.json"
        result_data = {
            "model": result_obj.model,
            "task_name": result_obj.task_name,
            "syntax_valid": result_obj.syntax_valid,
            "functional_pass": result_obj.functional_pass,
            "quality_score": result_obj.quality_score,
            "timestamp": result_obj.timestamp,
            "code": code,
            "baseline": True,
        }
        result_file.write_text(json.dumps(result_data, indent=2))


# ============================================================
# Summary Report
# ============================================================

class TestBaselineSummary:
    """Generate baseline comparison report."""

    def test_generate_baseline_report(self):
        """Generate baseline results summary."""
        results_dir = Path(__file__).parent / "results_baseline"

        if not results_dir.exists():
            pytest.skip("No baseline results directory")

        print("\n" + "="*70)
        print("BASELINE RESULTS SUMMARY (No Skills Loaded)")
        print("="*70)
        print()

        model_metrics = {}

        for model in ["haiku", "sonnet", "opus"]:
            model_dir = results_dir / model
            if not model_dir.exists():
                continue

            results = []
            for result_file in model_dir.glob("*.json"):
                try:
                    data = json.loads(result_file.read_text())
                    results.append(data)
                except Exception:
                    pass

            if results:
                syntax_rate = sum(1 for r in results if r.get("syntax_valid")) / len(results)
                functional_rate = sum(1 for r in results if r.get("functional_pass")) / len(results)
                quality_avg = sum(r.get("quality_score", 0) for r in results) / len(results)

                model_metrics[model] = {
                    "syntax_rate": syntax_rate,
                    "functional_rate": functional_rate,
                    "quality_avg": quality_avg,
                    "total_tests": len(results),
                }

        print(f"{'Model':<12} {'Syntax':<10} {'Functional':<12} {'Quality':<10}")
        print("-"*70)

        for model in ["haiku", "sonnet", "opus"]:
            if model not in model_metrics:
                print(f"{model:<12} {'N/A':<10} {'N/A':<12} {'N/A':<10}")
            else:
                m = model_metrics[model]
                print(
                    f"{model:<12} "
                    f"{m['syntax_rate']:.1%}  "
                    f"{m['functional_rate']:.1%}  "
                    f"{m['quality_avg']:.2f}"
                )

        print()
