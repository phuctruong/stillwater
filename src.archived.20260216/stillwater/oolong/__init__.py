"""Stillwater OOLONG solver: deterministic aggregation via Counter().

Public API:
    solve(context, question, task, task_group) -> str
    solve_and_check(context, question, expected, task, task_group) -> (str, bool)
"""

from .solver import solve, solve_and_check

__all__ = ["solve", "solve_and_check"]
