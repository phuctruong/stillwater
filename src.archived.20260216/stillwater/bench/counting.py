"""Benchmark 2: Counting Accuracy.

LLM classifies items into categories. CPU does exact counting with len().
Tests that CPU-enforced counting beats LLM self-counting.
"""

from __future__ import annotations

import json
import re
import time

from stillwater.bench import BenchResult
from stillwater.llm import LLMClient

# Inline fixtures: items to count/categorize
FIXTURES = [
    {
        "items": ["apple", "banana", "cherry", "date", "elderberry"],
        "question": "How many fruits are in the list?",
        "prompt": (
            "List each item on its own line, then count them. "
            "Reply with a JSON object: {\"items\": [...], \"count\": N}\n\n"
            "Items: apple, banana, cherry, date, elderberry"
        ),
        "expected_count": 5,
    },
    {
        "items": ["red", "blue", "green", "red", "blue", "yellow", "red"],
        "question": "How many times does 'red' appear?",
        "prompt": (
            "From this list, extract only items that are 'red'. "
            "Reply with a JSON object: {\"items\": [...], \"count\": N}\n\n"
            "Items: red, blue, green, red, blue, yellow, red"
        ),
        "expected_count": 3,
    },
    {
        "items": list(range(1, 13)),
        "question": "How many even numbers from 1 to 12?",
        "prompt": (
            "From these numbers, list only the even ones. "
            "Reply with a JSON object: {\"items\": [...], \"count\": N}\n\n"
            "Numbers: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12"
        ),
        "expected_count": 6,
    },
    {
        "items": ["cat", "dog", "cat", "bird", "dog", "cat", "fish", "dog"],
        "question": "How many unique animals?",
        "prompt": (
            "List only the unique items (no duplicates). "
            "Reply with a JSON object: {\"items\": [...], \"count\": N}\n\n"
            "Items: cat, dog, cat, bird, dog, cat, fish, dog"
        ),
        "expected_count": 4,
    },
    {
        "items": ["a", "bb", "ccc", "dddd", "eeeee", "ffffff"],
        "question": "How many strings have more than 3 characters?",
        "prompt": (
            "From this list, extract items with more than 3 characters. "
            "Reply with a JSON object: {\"items\": [...], \"count\": N}\n\n"
            "Items: a, bb, ccc, dddd, eeeee, ffffff"
        ),
        "expected_count": 3,
    },
    {
        "items": ["the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
        "question": "How many words in the sentence?",
        "prompt": (
            "List each word on its own line. "
            "Reply with a JSON object: {\"items\": [...], \"count\": N}\n\n"
            "Words: the, quick, brown, fox, jumps, over, the, lazy, dog"
        ),
        "expected_count": 9,
    },
    {
        "items": [2, 3, 5, 7, 11, 13, 17, 19],
        "question": "How many primes?",
        "prompt": (
            "List all the items. "
            "Reply with a JSON object: {\"items\": [...], \"count\": N}\n\n"
            "Numbers: 2, 3, 5, 7, 11, 13, 17, 19"
        ),
        "expected_count": 8,
    },
    {
        "items": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "question": "How many weekdays listed?",
        "prompt": (
            "List each item. "
            "Reply with a JSON object: {\"items\": [...], \"count\": N}\n\n"
            "Days: Mon, Tue, Wed, Thu, Fri"
        ),
        "expected_count": 5,
    },
    {
        "items": ["x"] * 15,
        "question": "How many x's?",
        "prompt": (
            "Count the items in this list. "
            "Reply with a JSON object: {\"items\": [...], \"count\": N}\n\n"
            "Items: x, x, x, x, x, x, x, x, x, x, x, x, x, x, x"
        ),
        "expected_count": 15,
    },
    {
        "items": [],
        "question": "How many items in an empty list?",
        "prompt": (
            "List the items. If the list is empty, say so. "
            "Reply with a JSON object: {\"items\": [], \"count\": N}\n\n"
            "Items: (none)"
        ),
        "expected_count": 0,
    },
]


def _parse_json_response(response: str) -> dict | None:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Try to find JSON in code blocks first
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try direct JSON parse
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        pass

    # Try to find any JSON object in the response
    match = re.search(r'\{[^{}]*\}', response)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def run(client: LLMClient) -> BenchResult:
    """Run counting accuracy benchmark."""
    details: list[dict] = []
    passed = 0
    t0 = time.perf_counter()

    for fixture in FIXTURES:
        try:
            llm_response = client.generate(fixture["prompt"], temperature=0)
            parsed = _parse_json_response(llm_response)

            if parsed is None:
                details.append({
                    "question": fixture["question"],
                    "expected": fixture["expected_count"],
                    "llm_output": llm_response[:200],
                    "error": "unparseable JSON",
                    "passed": False,
                })
                continue

            # CPU does the counting: len() on the items list
            items = parsed.get("items", [])
            cpu_count = len(items)

            ok = cpu_count == fixture["expected_count"]
            if ok:
                passed += 1

            details.append({
                "question": fixture["question"],
                "expected": fixture["expected_count"],
                "cpu_count": cpu_count,
                "llm_count": parsed.get("count"),
                "passed": ok,
            })
        except Exception as e:
            details.append({
                "question": fixture["question"],
                "expected": fixture["expected_count"],
                "error": str(e),
                "passed": False,
            })

    elapsed = (time.perf_counter() - t0) * 1000
    return BenchResult(
        name="Counting Accuracy",
        passed=passed,
        total=len(FIXTURES),
        elapsed_ms=elapsed,
        details=details,
    )
