"""Benchmark 3: Math Exactness.

LLM translates word problems to arithmetic expressions.
CPU evaluates with exact Fraction arithmetic (no float contamination).
"""

from __future__ import annotations

import re
import time
from fractions import Fraction

from stillwater.bench import BenchResult
from stillwater.llm import LLMClient

# Inline fixtures: (word problem, prompt, expected exact answer)
FIXTURES = [
    {
        "problem": "What is one third plus one sixth?",
        "prompt": (
            "Convert this math problem to a single arithmetic expression using "
            "fractions. Reply with ONLY the expression, nothing else.\n"
            "Example: 1/3 + 1/6\n\n"
            "Problem: What is one third plus one sixth?"
        ),
        "expected": Fraction(1, 2),
    },
    {
        "problem": "What is three quarters minus one half?",
        "prompt": (
            "Convert this math problem to a single arithmetic expression using "
            "fractions. Reply with ONLY the expression, nothing else.\n"
            "Example: 3/4 - 1/2\n\n"
            "Problem: What is three quarters minus one half?"
        ),
        "expected": Fraction(1, 4),
    },
    {
        "problem": "What is two fifths times five halves?",
        "prompt": (
            "Convert this math problem to a single arithmetic expression using "
            "fractions. Reply with ONLY the expression, nothing else.\n"
            "Example: 2/5 * 5/2\n\n"
            "Problem: What is two fifths times five halves?"
        ),
        "expected": Fraction(1, 1),
    },
    {
        "problem": "What is seven eighths divided by seven sixteenths?",
        "prompt": (
            "Convert this math problem to a single arithmetic expression using "
            "fractions. Reply with ONLY the expression, nothing else.\n"
            "Example: 7/8 / 7/16\n\n"
            "Problem: What is seven eighths divided by seven sixteenths?"
        ),
        "expected": Fraction(2, 1),
    },
    {
        "problem": "What is one third plus one third plus one third?",
        "prompt": (
            "Convert this math problem to a single arithmetic expression using "
            "fractions. Reply with ONLY the expression, nothing else.\n"
            "Example: 1/3 + 1/3 + 1/3\n\n"
            "Problem: What is one third plus one third plus one third?"
        ),
        "expected": Fraction(1, 1),
    },
    {
        "problem": "What is five sixths minus one third?",
        "prompt": (
            "Convert this math problem to a single arithmetic expression using "
            "fractions. Reply with ONLY the expression, nothing else.\n"
            "Example: 5/6 - 1/3\n\n"
            "Problem: What is five sixths minus one third?"
        ),
        "expected": Fraction(1, 2),
    },
    {
        "problem": "What is two thirds times three fourths?",
        "prompt": (
            "Convert this math problem to a single arithmetic expression using "
            "fractions. Reply with ONLY the expression, nothing else.\n"
            "Example: 2/3 * 3/4\n\n"
            "Problem: What is two thirds times three fourths?"
        ),
        "expected": Fraction(1, 2),
    },
    {
        "problem": "What is one half plus one quarter plus one eighth?",
        "prompt": (
            "Convert this math problem to a single arithmetic expression using "
            "fractions. Reply with ONLY the expression, nothing else.\n"
            "Example: 1/2 + 1/4 + 1/8\n\n"
            "Problem: What is one half plus one quarter plus one eighth?"
        ),
        "expected": Fraction(7, 8),
    },
    {
        "problem": "What is nine tenths divided by three fifths?",
        "prompt": (
            "Convert this math problem to a single arithmetic expression using "
            "fractions. Reply with ONLY the expression, nothing else.\n"
            "Example: 9/10 / 3/5\n\n"
            "Problem: What is nine tenths divided by three fifths?"
        ),
        "expected": Fraction(3, 2),
    },
    {
        "problem": "What is one seventh plus two sevenths?",
        "prompt": (
            "Convert this math problem to a single arithmetic expression using "
            "fractions. Reply with ONLY the expression, nothing else.\n"
            "Example: 1/7 + 2/7\n\n"
            "Problem: What is one seventh plus two sevenths?"
        ),
        "expected": Fraction(3, 7),
    },
]


def _parse_expression(expr: str) -> Fraction | None:
    """Safely evaluate a simple fraction arithmetic expression.

    Supports: integers, fractions (a/b), and operators +, -, *, /
    """
    # Clean up the expression
    expr = expr.strip().strip("`").strip()

    # Tokenize: numbers (with optional /denominator) and operators
    tokens = re.findall(r'\d+/\d+|\d+|[+\-*/]', expr)
    if not tokens:
        return None

    try:
        # Build result by processing tokens left to right with proper precedence
        # Simple approach: convert to Fraction operations
        # First pass: convert all number tokens to Fractions
        values: list[Fraction | str] = []
        for tok in tokens:
            if tok in "+-*/":
                values.append(tok)
            elif "/" in tok:
                num, den = tok.split("/")
                values.append(Fraction(int(num), int(den)))
            else:
                values.append(Fraction(int(tok)))

        # Second pass: handle * and / (higher precedence)
        i = 0
        reduced: list[Fraction | str] = []
        while i < len(values):
            if i + 2 < len(values) and values[i + 1] in ("*", "/"):
                left = values[i]
                assert isinstance(left, Fraction)
                while i + 2 < len(values) and values[i + 1] in ("*", "/"):
                    op = values[i + 1]
                    right = values[i + 2]
                    assert isinstance(right, Fraction)
                    if op == "*":
                        left = left * right
                    else:
                        left = left / right
                    i += 2
                reduced.append(left)
                i += 1
            else:
                reduced.append(values[i])
                i += 1

        # Third pass: handle + and -
        result = reduced[0]
        assert isinstance(result, Fraction)
        i = 1
        while i + 1 < len(reduced):
            op = reduced[i]
            right = reduced[i + 1]
            assert isinstance(right, Fraction)
            if op == "+":
                result = result + right
            elif op == "-":
                result = result - right
            i += 2

        return result
    except Exception:
        return None


def run(client: LLMClient) -> BenchResult:
    """Run math exactness benchmark."""
    details: list[dict] = []
    passed = 0
    t0 = time.perf_counter()

    for fixture in FIXTURES:
        try:
            llm_expr = client.generate(fixture["prompt"], temperature=0)
            cpu_result = _parse_expression(llm_expr)
            ok = cpu_result == fixture["expected"]
            if ok:
                passed += 1
            details.append({
                "problem": fixture["problem"],
                "llm_output": llm_expr,
                "cpu_result": str(cpu_result),
                "expected": str(fixture["expected"]),
                "passed": ok,
            })
        except Exception as e:
            details.append({
                "problem": fixture["problem"],
                "error": str(e),
                "passed": False,
            })

    elapsed = (time.perf_counter() - t0) * 1000
    return BenchResult(
        name="Math Exactness",
        passed=passed,
        total=len(FIXTURES),
        elapsed_ms=elapsed,
        details=details,
    )
