"""Benchmark 4: Compositional Generalization.

LLM parses natural language instructions into structured actions.
CPU executes via state machine. Tests multi-step composition.
"""

from __future__ import annotations

import json
import re
import time

from stillwater.bench import BenchResult
from stillwater.llm import LLMClient

# State machine: a simple grid world robot
# Actions: MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, PICK_UP, PUT_DOWN

FIXTURES = [
    {
        "instruction": "Move right twice, then move up once.",
        "prompt": (
            "Convert this instruction into a sequence of actions.\n"
            "Valid actions: MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, PICK_UP, PUT_DOWN\n"
            'Reply with ONLY a JSON array of actions, e.g. ["MOVE_RIGHT", "MOVE_UP"]\n\n'
            "Instruction: Move right twice, then move up once."
        ),
        "expected_actions": ["MOVE_RIGHT", "MOVE_RIGHT", "MOVE_UP"],
        "expected_state": {"x": 2, "y": 1},
    },
    {
        "instruction": "Move up three times, then move left two times.",
        "prompt": (
            "Convert this instruction into a sequence of actions.\n"
            "Valid actions: MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, PICK_UP, PUT_DOWN\n"
            'Reply with ONLY a JSON array of actions, e.g. ["MOVE_RIGHT", "MOVE_UP"]\n\n'
            "Instruction: Move up three times, then move left two times."
        ),
        "expected_actions": ["MOVE_UP", "MOVE_UP", "MOVE_UP", "MOVE_LEFT", "MOVE_LEFT"],
        "expected_state": {"x": -2, "y": 3},
    },
    {
        "instruction": "Pick up, move right once, put down.",
        "prompt": (
            "Convert this instruction into a sequence of actions.\n"
            "Valid actions: MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, PICK_UP, PUT_DOWN\n"
            'Reply with ONLY a JSON array of actions, e.g. ["MOVE_RIGHT", "MOVE_UP"]\n\n'
            "Instruction: Pick up, move right once, put down."
        ),
        "expected_actions": ["PICK_UP", "MOVE_RIGHT", "PUT_DOWN"],
        "expected_state": {"x": 1, "y": 0, "holding": False},
    },
    {
        "instruction": "Move down four times.",
        "prompt": (
            "Convert this instruction into a sequence of actions.\n"
            "Valid actions: MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, PICK_UP, PUT_DOWN\n"
            'Reply with ONLY a JSON array of actions, e.g. ["MOVE_RIGHT", "MOVE_UP"]\n\n'
            "Instruction: Move down four times."
        ),
        "expected_actions": ["MOVE_DOWN", "MOVE_DOWN", "MOVE_DOWN", "MOVE_DOWN"],
        "expected_state": {"x": 0, "y": -4},
    },
    {
        "instruction": "Move right once, move up once, move left once, move down once.",
        "prompt": (
            "Convert this instruction into a sequence of actions.\n"
            "Valid actions: MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, PICK_UP, PUT_DOWN\n"
            'Reply with ONLY a JSON array of actions, e.g. ["MOVE_RIGHT", "MOVE_UP"]\n\n'
            "Instruction: Move right once, move up once, move left once, move down once."
        ),
        "expected_actions": ["MOVE_RIGHT", "MOVE_UP", "MOVE_LEFT", "MOVE_DOWN"],
        "expected_state": {"x": 0, "y": 0},
    },
    {
        "instruction": "Pick up, move up twice, move right three times, put down.",
        "prompt": (
            "Convert this instruction into a sequence of actions.\n"
            "Valid actions: MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, PICK_UP, PUT_DOWN\n"
            'Reply with ONLY a JSON array of actions, e.g. ["MOVE_RIGHT", "MOVE_UP"]\n\n'
            "Instruction: Pick up, move up twice, move right three times, put down."
        ),
        "expected_actions": [
            "PICK_UP", "MOVE_UP", "MOVE_UP",
            "MOVE_RIGHT", "MOVE_RIGHT", "MOVE_RIGHT", "PUT_DOWN",
        ],
        "expected_state": {"x": 3, "y": 2, "holding": False},
    },
    {
        "instruction": "Move left once.",
        "prompt": (
            "Convert this instruction into a sequence of actions.\n"
            "Valid actions: MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, PICK_UP, PUT_DOWN\n"
            'Reply with ONLY a JSON array of actions, e.g. ["MOVE_RIGHT", "MOVE_UP"]\n\n'
            "Instruction: Move left once."
        ),
        "expected_actions": ["MOVE_LEFT"],
        "expected_state": {"x": -1, "y": 0},
    },
    {
        "instruction": "Move up once, then move up once more, then move up again.",
        "prompt": (
            "Convert this instruction into a sequence of actions.\n"
            "Valid actions: MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, PICK_UP, PUT_DOWN\n"
            'Reply with ONLY a JSON array of actions, e.g. ["MOVE_RIGHT", "MOVE_UP"]\n\n'
            "Instruction: Move up once, then move up once more, then move up again."
        ),
        "expected_actions": ["MOVE_UP", "MOVE_UP", "MOVE_UP"],
        "expected_state": {"x": 0, "y": 3},
    },
    {
        "instruction": "Move right five times, then move down two times.",
        "prompt": (
            "Convert this instruction into a sequence of actions.\n"
            "Valid actions: MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, PICK_UP, PUT_DOWN\n"
            'Reply with ONLY a JSON array of actions, e.g. ["MOVE_RIGHT", "MOVE_UP"]\n\n'
            "Instruction: Move right five times, then move down two times."
        ),
        "expected_actions": [
            "MOVE_RIGHT", "MOVE_RIGHT", "MOVE_RIGHT", "MOVE_RIGHT", "MOVE_RIGHT",
            "MOVE_DOWN", "MOVE_DOWN",
        ],
        "expected_state": {"x": 5, "y": -2},
    },
    {
        "instruction": "Pick up, put down.",
        "prompt": (
            "Convert this instruction into a sequence of actions.\n"
            "Valid actions: MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, PICK_UP, PUT_DOWN\n"
            'Reply with ONLY a JSON array of actions, e.g. ["MOVE_RIGHT", "MOVE_UP"]\n\n'
            "Instruction: Pick up, put down."
        ),
        "expected_actions": ["PICK_UP", "PUT_DOWN"],
        "expected_state": {"x": 0, "y": 0, "holding": False},
    },
]

VALID_ACTIONS = {"MOVE_UP", "MOVE_DOWN", "MOVE_LEFT", "MOVE_RIGHT", "PICK_UP", "PUT_DOWN"}


def _execute_actions(actions: list[str]) -> dict:
    """Execute actions in a simple grid-world state machine."""
    state = {"x": 0, "y": 0, "holding": False}
    for action in actions:
        if action == "MOVE_UP":
            state["y"] += 1
        elif action == "MOVE_DOWN":
            state["y"] -= 1
        elif action == "MOVE_LEFT":
            state["x"] -= 1
        elif action == "MOVE_RIGHT":
            state["x"] += 1
        elif action == "PICK_UP":
            state["holding"] = True
        elif action == "PUT_DOWN":
            state["holding"] = False
    return state


def _parse_actions(response: str) -> list[str] | None:
    """Parse LLM response into a list of valid actions."""
    # Try to find JSON array in response
    match = re.search(r'\[.*?\]', response, re.DOTALL)
    if match:
        try:
            actions = json.loads(match.group(0))
            if isinstance(actions, list) and all(
                isinstance(a, str) and a in VALID_ACTIONS for a in actions
            ):
                return actions
        except json.JSONDecodeError:
            pass
    return None


def run(client: LLMClient) -> BenchResult:
    """Run compositional generalization benchmark."""
    details: list[dict] = []
    passed = 0
    t0 = time.perf_counter()

    for fixture in FIXTURES:
        try:
            llm_response = client.generate(fixture["prompt"], temperature=0)
            actions = _parse_actions(llm_response)

            if actions is None:
                details.append({
                    "instruction": fixture["instruction"],
                    "llm_output": llm_response[:200],
                    "error": "unparseable actions",
                    "passed": False,
                })
                continue

            # CPU executes the state machine
            actual_state = _execute_actions(actions)
            expected_state = fixture["expected_state"]

            # Check that final state matches expected
            ok = all(
                actual_state.get(k) == v for k, v in expected_state.items()
            )
            if ok:
                passed += 1

            details.append({
                "instruction": fixture["instruction"],
                "actions": actions,
                "actual_state": actual_state,
                "expected_state": expected_state,
                "passed": ok,
            })
        except Exception as e:
            details.append({
                "instruction": fixture["instruction"],
                "error": str(e),
                "passed": False,
            })

    elapsed = (time.perf_counter() - t0) * 1000
    return BenchResult(
        name="Compositional Generalization",
        passed=passed,
        total=len(FIXTURES),
        elapsed_ms=elapsed,
        details=details,
    )
