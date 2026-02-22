#!/usr/bin/env python3
"""
Hard SWE Baseline Tests - WITHOUT Skills Loaded

Same 5 hard problems but with NO system prompt injection.
This establishes the baseline for hard SWE uplift measurement.

Compared to test_hard_swe.py which loads prime-coder + persona-engine skills.
"""

import sys
import json
import hashlib
import ast
from pathlib import Path
from typing import NamedTuple
from datetime import datetime

import pytest

_CLI_SRC = Path(__file__).parent.parent.parent / "cli" / "src"
if str(_CLI_SRC) not in sys.path:
    sys.path.insert(0, str(_CLI_SRC))

from stillwater.llm_client import LLMClient


# ============================================================
# Data Models
# ============================================================

class HardTestResult(NamedTuple):
    """Result from a hard SWE test."""
    model: str
    task_name: str
    syntax_valid: bool
    functional_pass: bool
    complexity_score: float = 0.0
    edge_cases_handled: float = 0.0
    timestamp: str = ""


# ============================================================
# Analysis Functions
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


def calculate_complexity_score(code: str) -> float:
    """Score based on algorithmic complexity indicators."""
    score = 0.0

    try:
        tree = ast.parse(code)
    except:
        return 0.0

    if ast.get_docstring(tree) is not None:
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

    has_classes = any(
        isinstance(node, ast.ClassDef)
        for node in ast.walk(tree)
    )
    if has_classes:
        score += 0.15

    has_decorators = any(
        isinstance(node, ast.FunctionDef) and node.decorator_list
        for node in ast.walk(tree)
    )
    if has_decorators:
        score += 0.1

    has_with = any(
        isinstance(node, ast.With)
        for node in ast.walk(tree)
    )
    if has_with:
        score += 0.1

    has_assertions = any(
        isinstance(node, ast.Assert)
        for node in ast.walk(tree)
    )
    if has_assertions:
        score += 0.1

    lines = len(code.split('\n'))
    if lines >= 100:
        score += 0.15

    return min(1.0, max(0.0, score))


def calculate_edge_cases_score(code: str, task_name: str) -> float:
    """Score based on edge case handling indicators."""
    score = 0.0

    has_boundary_checks = any(
        keyword in code
        for keyword in ['if n == 0', 'if not ', 'if len(', '== 0', '< 0', '> 0']
    )
    if has_boundary_checks:
        score += 0.2

    if 'None' in code or 'is None' in code:
        score += 0.15

    if 'except' in code or 'raise' in code:
        score += 0.15

    if 'print(' in code or 'logger' in code:
        score += 0.1

    if task_name == 'lru_cache' and any(
        kw in code for kw in ['capacity', 'evict', 'update']
    ):
        score += 0.2

    if task_name == 'thread_safe_queue' and any(
        kw in code for kw in ['Lock', 'Condition', 'threading']
    ):
        score += 0.2

    if task_name == 'binary_search_tree' and any(
        kw in code for kw in ['balance', 'rotate', 'height']
    ):
        score += 0.2

    return min(1.0, max(0.0, score))


def validate_code_execution(code: str, task_name: str) -> tuple[bool, str]:
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
            "threading": __import__('threading'),
            "asyncio": __import__('asyncio'),
            "collections": __import__('collections'),
        }

        exec(code, namespace)
        return True, ""
    except Exception as e:
        return False, f"Execution error: {str(e)}"


# ============================================================
# Hard SWE Baseline Tasks (NO SKILLS)
# ============================================================

HARD_SWE_BASELINE_TASKS = {
    "lru_cache": {
        "name": "LRU Cache Implementation",
        "prompt": """Show me the complete Python code (as a markdown ```python code block) for an LRU (Least Recently Used) Cache implementation.

Requirements:
1. Class named `LRUCache` that takes capacity as constructor argument
2. Implement `get(key)` method - returns value or -1 if not found
3. Implement `put(key, value)` method - adds or updates entry
4. When capacity exceeded, evict least recently used item
5. Both get and put operations should be O(1)
6. Include proper docstrings and type hints
7. Include comprehensive test cases

Edge cases to handle:
- Empty cache
- Capacity of 1
- All items accessed in order
- Repeated accesses
- Updates to existing keys

Return ONLY the code in a markdown block.
""",
    },

    "thread_safe_queue": {
        "name": "Thread-Safe Producer/Consumer Queue",
        "prompt": """Show me the complete Python code (as a markdown ```python code block) for a thread-safe producer/consumer queue.

Requirements:
1. Class named `ThreadSafeQueue` with max_size parameter
2. Implement `put(item)` method - blocks if full
3. Implement `get()` method - blocks if empty
4. Implement `size()` method - returns current queue size
5. Use threading.Lock and threading.Condition for synchronization
6. Handle edge cases: timeout, shutdown, concurrent access
7. Include proper docstrings and type hints
8. Include test cases demonstrating thread safety

Edge cases:
- Multiple producers
- Multiple consumers
- Queue full scenario
- Queue empty scenario
- Shutdown while waiting

Return ONLY the code in a markdown block.
""",
    },

    "binary_search_tree": {
        "name": "Self-Balancing Binary Search Tree",
        "prompt": """Show me the complete Python code (as a markdown ```python code block) for a self-balancing Binary Search Tree (AVL Tree).

Requirements:
1. Node class with value, left, right, height attributes
2. Tree class with insert(value) and delete(value) methods
3. Implement tree rotation for balancing (left_rotate, right_rotate)
4. Implement balance_factor calculation
5. After insertion/deletion, tree must remain balanced
6. Implement search(value) and in_order_traversal() methods
7. Include proper docstrings and type hints
8. Include comprehensive test cases

Edge cases:
- Empty tree
- Single node
- All insertions ascending/descending
- Deletions causing imbalance
- Duplicate values

Return ONLY the code in a markdown block.
""",
    },

    "async_rate_limiter": {
        "name": "Async Rate Limiter with Token Bucket",
        "prompt": """Show me the complete Python code (as a markdown ```python code block) for an async rate limiter using token bucket algorithm.

Requirements:
1. Class named `AsyncRateLimiter` with rate and burst parameters
2. Implement async `acquire()` method - waits until token available
3. Use token bucket algorithm: tokens refill at fixed rate
4. Support burst capacity (tokens can accumulate up to burst_size)
5. Handle concurrent requests properly with asyncio.Lock
6. Include docstrings and type hints
7. Include async test cases demonstrating rate limiting

Edge cases:
- Zero tokens at start
- Burst exceeds capacity
- Rapid consecutive requests
- Request arrival just before token available
- Long waits between requests

Return ONLY the code in a markdown block.
""",
    },

    "database_connection_pool": {
        "name": "Database Connection Pool with Retry Logic",
        "prompt": """Show me the complete Python code (as a markdown ```python code block) for a database connection pool with exponential backoff retry logic.

Requirements:
1. Class `ConnectionPool` with min_size, max_size, max_retries parameters
2. Implement `get_connection()` method with connection reuse
3. Implement `release_connection(conn)` for returning connections
4. Implement exponential backoff retry on connection failures
5. Handle connection timeouts and deadlocks
6. Thread-safe implementation
7. Include proper docstrings and type hints
8. Include test cases with mock database

Edge cases:
- Pool exhaustion
- Connection failures
- Timeout scenarios
- Concurrent access
- Stale connections

Return ONLY the code in a markdown block.
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
# Hard SWE Baseline Tests (NO SKILLS)
# ============================================================

class TestHardSWEBaseline:
    """Hard SWE baseline tests WITHOUT skill injection."""

    MODELS = ["haiku", "sonnet", "opus"]

    @pytest.fixture(autouse=True)
    def setup_results_dir(self):
        """Create results directory structure."""
        results_dir = Path(__file__).parent / "results_hard_swe_baseline"
        results_dir.mkdir(exist_ok=True)
        for model in self.MODELS:
            (results_dir / model).mkdir(exist_ok=True)
        self.results_dir = results_dir

    @pytest.mark.parametrize("task_key", list(HARD_SWE_BASELINE_TASKS.keys()))
    @pytest.mark.parametrize("model", ["haiku", "sonnet", "opus"])
    def test_hard_swe_baseline_task(
        self,
        task_key: str,
        model: str,
        llm_client: LLMClient,
    ):
        """Test a hard SWE task WITHOUT skill injection (baseline)."""
        task = HARD_SWE_BASELINE_TASKS[task_key]

        print(f"\n{'='*70}")
        print(f"HARD SWE BASELINE: {task['name']} | Model: {model.upper()}")
        print(f"(No skills loaded)")
        print(f"{'='*70}")

        # Invoke WITHOUT skill injection - just basic system prompt
        messages = [
            {"role": "system", "content": "You are an expert software engineer."},
            {"role": "user", "content": task["prompt"]},
        ]

        result = llm_client.chat(
            messages,
            model=model,
            max_tokens=2048,
            temperature=0.0,
            timeout=60.0,
        )
        response = result.text

        # Extract code
        code = extract_python_code(response)

        # Validate syntax
        syntax_valid, syntax_error = validate_syntax(code)

        # Validate execution
        functional_pass = False
        if syntax_valid:
            functional_pass, _ = validate_code_execution(code, task_key)

        # Complexity scoring
        complexity = calculate_complexity_score(code)
        edge_cases = calculate_edge_cases_score(code, task_key)

        # Create result
        result_obj = HardTestResult(
            model=model,
            task_name=task_key,
            syntax_valid=syntax_valid,
            functional_pass=functional_pass,
            complexity_score=complexity,
            edge_cases_handled=edge_cases,
            timestamp=datetime.now().isoformat(),
        )

        # Print results
        print(f"Syntax Valid:        {result_obj.syntax_valid}")
        if syntax_error:
            print(f"Syntax Error:        {syntax_error}")

        print(f"Functional Pass:     {result_obj.functional_pass}")
        print(f"Complexity Score:    {result_obj.complexity_score:.2f}")
        print(f"Edge Cases Score:    {result_obj.edge_cases_handled:.2f}")
        print(f"Code Length:         {len(code)} chars")

        # Save result
        result_file = self.results_dir / model / f"{task_key}_{model}.json"
        result_data = {
            "model": result_obj.model,
            "task_name": result_obj.task_name,
            "syntax_valid": result_obj.syntax_valid,
            "functional_pass": result_obj.functional_pass,
            "complexity_score": result_obj.complexity_score,
            "edge_cases_score": result_obj.edge_cases_handled,
            "code_length": len(code),
            "timestamp": result_obj.timestamp,
            "baseline": True,
        }
        result_file.write_text(json.dumps(result_data, indent=2))
