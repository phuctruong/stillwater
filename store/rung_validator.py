"""
store/rung_validator.py — Evidence bundle validator for Stillwater Store submissions.

Verifies that a submission's evidence directory satisfies the rung_target claim
before the skill is submitted to the Store. This is the client-side gate.

Class: RungValidator
  verify_evidence(evidence_dir, rung_target) → "VALID" | "INVALID"

Rung target: 641 (local correctness + tests passing)
Network: OFF — no HTTP calls; local file operations only.

Verification protocol (rung 641):
  1. All three required files must exist: plan.json, tests.json, behavior_hash.txt
  2. All files must be valid JSON
  3. plan.json must contain: rung_target (int), task_family (str), files_changed (list)
  4. tests.json must contain: test_command (str), exit_code (int)
  5. behavior_hash.txt must contain: seed_42, seed_137, seed_9001 (all present)
  6. All three seed hashes must agree (3-seed consensus, fail-closed on mismatch)
  7. rung_target argument must be a valid rung value (641 / 274177 / 65537)

Fail-closed rules:
  - null rung_target → INVALID (null != 0; null != rung 641)
  - any missing file → INVALID
  - any malformed JSON → INVALID
  - any missing required field → INVALID
  - seed mismatch (any two seeds disagree) → INVALID
  - unknown rung_target value → INVALID

Design decisions:
  - "VALID" / "INVALID" strings (not True/False) to prevent boolean coercion bugs.
  - No float arithmetic in verification path (exact string comparison of hashes).
  - Exceptions caught internally; caller always gets VALID or INVALID.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

# Valid rung values per stillwater verification ladder
VALID_RUNGS = frozenset({641, 274177, 65537})

# Required evidence filenames
REQUIRED_EVIDENCE_FILES = frozenset({"plan.json", "tests.json", "behavior_hash.txt"})

# Required fields per evidence file
PLAN_REQUIRED_FIELDS = frozenset({"rung_target", "task_family", "files_changed"})
TESTS_REQUIRED_FIELDS = frozenset({"test_command", "exit_code"})
BEHAVIOR_REQUIRED_SEEDS = frozenset({"seed_42", "seed_137", "seed_9001"})

# Sentinel return values
_VALID = "VALID"
_INVALID = "INVALID"


class RungValidator:
    """
    Validates a local evidence directory against the claimed rung before submission.

    Usage:
        validator = RungValidator()
        status = validator.verify_evidence(
            evidence_dir=Path("evidence/"),
            rung_target=641,
        )
        assert status == "VALID"  # only then submit

    Fail-closed: any missing data, schema violation, or seed mismatch → "INVALID".
    """

    def verify_evidence(
        self,
        evidence_dir: Path,
        rung_target: Optional[int],
    ) -> str:
        """
        Verify evidence directory against the claimed rung.

        Args:
            evidence_dir: Path to directory containing evidence files.
            rung_target:  Rung being claimed (must be 641, 274177, or 65537).
                          None or invalid value → INVALID (fail-closed).

        Returns:
            "VALID"   — all checks pass; safe to submit.
            "INVALID" — one or more checks failed; do not submit.
        """
        # Gate 1: rung_target must be a known valid rung (null != 0 rule)
        if rung_target is None:
            return _INVALID
        if rung_target not in VALID_RUNGS:
            return _INVALID

        evidence_dir = Path(evidence_dir)

        # Gate 2: evidence directory must exist
        if not evidence_dir.exists() or not evidence_dir.is_dir():
            return _INVALID

        # Gate 3: all required files must exist
        for fname in REQUIRED_EVIDENCE_FILES:
            if not (evidence_dir / fname).exists():
                return _INVALID

        # Gate 4: all files must be valid JSON
        parsed: Dict[str, Any] = {}
        for fname in REQUIRED_EVIDENCE_FILES:
            raw = (evidence_dir / fname).read_text(encoding="utf-8")
            try:
                parsed[fname] = json.loads(raw)
            except json.JSONDecodeError:
                return _INVALID

        # Gate 5: plan.json schema check
        plan = parsed["plan.json"]
        if not isinstance(plan, dict):
            return _INVALID
        for field in PLAN_REQUIRED_FIELDS:
            if field not in plan:
                return _INVALID

        # Gate 6: tests.json schema check
        tests = parsed["tests.json"]
        if not isinstance(tests, dict):
            return _INVALID
        for field in TESTS_REQUIRED_FIELDS:
            if field not in tests:
                return _INVALID

        # Gate 7: behavior_hash.txt — all three seeds present and agreeing
        behavior = parsed["behavior_hash.txt"]
        if not isinstance(behavior, dict):
            return _INVALID
        for seed_key in BEHAVIOR_REQUIRED_SEEDS:
            if seed_key not in behavior:
                return _INVALID

        # 3-seed consensus check (exact string comparison — no float)
        seed_values = [behavior[k] for k in sorted(BEHAVIOR_REQUIRED_SEEDS)]
        first = seed_values[0]
        for val in seed_values[1:]:
            if val != first:
                return _INVALID

        return _VALID
