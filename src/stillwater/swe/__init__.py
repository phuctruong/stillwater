"""
SWE-bench harness with Red-Green-God verification gates.

This module implements a mathematically verified approach to code patching
that guarantees no test regressions.

Architecture:
    1. Red Gate: Validate baseline tests PASS before patching
    2. Green Gate: Verify tests still PASS after patching
    3. God Gate: Check patch determinism (same input → same patch)

Usage:
    from stillwater.swe import run_instance

    result = run_instance(
        instance_id="django__django-12345",
        problem_statement="Fix the bug in...",
        base_commit="abc123",
        repo_url="https://github.com/django/django"
    )

    if result.verified:
        print(f"✅ Patch verified: {result.certificate}")
    else:
        print(f"❌ Patch rejected: {result.reason}")
"""

from .loader import load_instance, load_dataset
from .gates import RedGate, GreenGate, GodGate
from .environment import setup_environment, apply_test_patch
from .runner import run_instance, run_batch

__all__ = [
    "load_instance",
    "load_dataset",
    "RedGate",
    "GreenGate",
    "GodGate",
    "setup_environment",
    "apply_test_patch",
    "run_instance",
    "run_batch",
]
