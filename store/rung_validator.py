"""
store/rung_validator.py — Evidence bundle validator for Stillwater Store submissions.

Verifies that a submission's evidence directory satisfies the rung_target claim
before the skill is submitted to the Store. This is the client-side gate.

Class: RungValidator
  verify_evidence(evidence_dir, rung_target) → "VALID" | "INVALID"
  validate_bundle(bundle_path) → dict with status and errors
  verify_rung(rung_claimed, bundle_path) → "VALID" | "INVALID"
  compute_behavior_hash(test_output, seed) → str (sha256 hex)

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

Rung ladder:
  rung 641:    tests.json (exit_code=0, pass_count>0, fail_count=0) + plan.json
  rung 274177: above + behavior_hash.txt with 3-seed consensus
  rung 65537:  above + security_scan.json with status=PASS

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
  - compute_behavior_hash: normalizes test output before hashing (sort lines, strip).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# Valid rung values per stillwater verification ladder
VALID_RUNGS = frozenset({641, 274177, 65537})

# Required evidence filenames
REQUIRED_EVIDENCE_FILES = frozenset({"plan.json", "tests.json", "behavior_hash.txt"})

# Required fields per evidence file
PLAN_REQUIRED_FIELDS = frozenset({"rung_target", "task_family", "files_changed"})
TESTS_REQUIRED_FIELDS = frozenset({"test_command", "exit_code"})
BEHAVIOR_REQUIRED_SEEDS = frozenset({"seed_42", "seed_137", "seed_9001"})

# Behavior hash: 64 hex chars = valid SHA-256
_HASH_HEX_LENGTH = 64

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

    # ------------------------------------------------------------------
    # Primary interface (used by StillwaterStoreClient)
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Spec-required interface: validate_bundle, verify_rung, compute_behavior_hash
    # ------------------------------------------------------------------

    def validate_bundle(self, bundle_path: Path) -> Dict[str, Any]:
        """
        Validate an evidence bundle directory. Returns a result dict with:
          status: "VALID" | "INVALID"
          errors: list of error strings describing what failed

        Required files: tests.json, plan.json, behavior_hash.txt
        tests.json must have: exit_code=0, pass_count > 0, fail_count == 0
        behavior_hash.txt must be valid SHA-256 (64 hex chars) for all seeds
        plan.json must have: goal, constraints, rung_target fields

        Args:
            bundle_path: Path to directory containing evidence files.

        Returns:
            {"status": "VALID"|"INVALID", "errors": [...]}
        """
        bundle_path = Path(bundle_path)
        errors: List[str] = []

        # Check directory exists
        if not bundle_path.exists() or not bundle_path.is_dir():
            return {"status": _INVALID, "errors": [f"Bundle directory not found: {bundle_path}"]}

        # Check required files exist
        required_files = {"tests.json", "plan.json", "behavior_hash.txt"}
        for fname in required_files:
            if not (bundle_path / fname).exists():
                errors.append(f"Missing required file: {fname}")

        if errors:
            return {"status": _INVALID, "errors": errors}

        # Parse and validate tests.json
        try:
            tests = json.loads((bundle_path / "tests.json").read_text(encoding="utf-8"))
            if not isinstance(tests, dict):
                errors.append("tests.json must be a JSON object")
            else:
                if tests.get("exit_code") != 0:
                    errors.append(f"tests.json: exit_code must be 0, got {tests.get('exit_code')!r}")
                pass_count = tests.get("pass_count", tests.get("passed"))
                fail_count = tests.get("fail_count", tests.get("failed"))
                if pass_count is None:
                    errors.append("tests.json: missing pass_count (or passed) field")
                elif pass_count <= 0:
                    errors.append(f"tests.json: pass_count must be > 0, got {pass_count}")
                if fail_count is None:
                    errors.append("tests.json: missing fail_count (or failed) field")
                elif fail_count != 0:
                    errors.append(f"tests.json: fail_count must be 0, got {fail_count}")
        except json.JSONDecodeError as exc:
            errors.append(f"tests.json: invalid JSON — {exc}")

        # Parse and validate plan.json
        try:
            plan = json.loads((bundle_path / "plan.json").read_text(encoding="utf-8"))
            if not isinstance(plan, dict):
                errors.append("plan.json must be a JSON object")
            else:
                for field in ("goal", "constraints", "rung_target"):
                    if field not in plan:
                        errors.append(f"plan.json: missing required field '{field}'")
                if "rung_target" in plan and plan["rung_target"] not in VALID_RUNGS:
                    errors.append(
                        f"plan.json: rung_target {plan['rung_target']!r} is not a valid rung "
                        f"(must be one of {sorted(VALID_RUNGS)})"
                    )
        except json.JSONDecodeError as exc:
            errors.append(f"plan.json: invalid JSON — {exc}")

        # Parse and validate behavior_hash.txt
        try:
            behavior = json.loads((bundle_path / "behavior_hash.txt").read_text(encoding="utf-8"))
            if not isinstance(behavior, dict):
                errors.append("behavior_hash.txt must be a JSON object")
            else:
                for seed_key in BEHAVIOR_REQUIRED_SEEDS:
                    if seed_key not in behavior:
                        errors.append(f"behavior_hash.txt: missing required seed '{seed_key}'")
                    else:
                        h = behavior[seed_key]
                        if not isinstance(h, str) or len(h) != _HASH_HEX_LENGTH:
                            errors.append(
                                f"behavior_hash.txt: {seed_key} must be a 64-char hex SHA-256 string"
                            )
                        else:
                            try:
                                int(h, 16)
                            except ValueError:
                                errors.append(
                                    f"behavior_hash.txt: {seed_key} contains non-hex characters"
                                )
        except json.JSONDecodeError as exc:
            errors.append(f"behavior_hash.txt: invalid JSON — {exc}")

        status = _VALID if not errors else _INVALID
        return {"status": status, "errors": errors}

    def verify_rung(self, rung_claimed: Optional[int], bundle_path: Path) -> str:
        """
        Check that rung_claimed is supported by the evidence in bundle_path.

        Rung ladder:
          rung 641:    tests.json (exit_code=0) + plan.json required
          rung 274177: above + behavior_hash.txt with 3-seed consensus
          rung 65537:  above + security_scan.json with status=PASS

        Args:
            rung_claimed: Rung being claimed (641, 274177, or 65537).
            bundle_path:  Path to evidence directory.

        Returns:
            "VALID"   — evidence supports the rung claim.
            "INVALID" — evidence does not support the rung claim.
        """
        # Null rung → reject (fail-closed; null != 0)
        if rung_claimed is None:
            return _INVALID
        if rung_claimed not in VALID_RUNGS:
            return _INVALID

        bundle_path = Path(bundle_path)
        if not bundle_path.exists() or not bundle_path.is_dir():
            return _INVALID

        # Rung 641: tests.json + plan.json
        if not (bundle_path / "tests.json").exists():
            return _INVALID
        if not (bundle_path / "plan.json").exists():
            return _INVALID

        try:
            tests = json.loads((bundle_path / "tests.json").read_text(encoding="utf-8"))
            if not isinstance(tests, dict) or tests.get("exit_code") != 0:
                return _INVALID
        except (json.JSONDecodeError, OSError):
            return _INVALID

        if rung_claimed == 641:
            return _VALID

        # Rung 274177: above + behavior_hash.txt with 3-seed replay
        if not (bundle_path / "behavior_hash.txt").exists():
            return _INVALID

        try:
            behavior = json.loads((bundle_path / "behavior_hash.txt").read_text(encoding="utf-8"))
            if not isinstance(behavior, dict):
                return _INVALID
            for seed_key in BEHAVIOR_REQUIRED_SEEDS:
                if seed_key not in behavior:
                    return _INVALID
            # 3-seed consensus
            seed_values = [behavior[k] for k in sorted(BEHAVIOR_REQUIRED_SEEDS)]
            if len(set(seed_values)) != 1:
                return _INVALID
        except (json.JSONDecodeError, OSError):
            return _INVALID

        if rung_claimed == 274177:
            return _VALID

        # Rung 65537: above + security_scan.json with status=PASS
        if not (bundle_path / "security_scan.json").exists():
            return _INVALID

        try:
            scan = json.loads((bundle_path / "security_scan.json").read_text(encoding="utf-8"))
            if not isinstance(scan, dict) or scan.get("status") != "PASS":
                return _INVALID
        except (json.JSONDecodeError, OSError):
            return _INVALID

        return _VALID

    @staticmethod
    def compute_behavior_hash(test_output: str, seed: int) -> str:
        """
        Compute a deterministic SHA-256 hash of test output for a given seed.

        Normalization:
          1. Split test_output into lines
          2. Strip leading/trailing whitespace from each line
          3. Filter empty lines
          4. Sort lines (deterministic across run order variations)
          5. Prepend seed as first element
          6. Join with newline
          7. Encode to UTF-8 and sha256

        Args:
            test_output: Raw test output string.
            seed:        Integer seed (42, 137, or 9001 for the 3-seed protocol).

        Returns:
            64-char lowercase hex SHA-256 string.
        """
        lines = [line.strip() for line in test_output.splitlines()]
        lines = [line for line in lines if line]  # filter empties
        lines.sort()
        canonical = f"seed={seed}\n" + "\n".join(lines)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
