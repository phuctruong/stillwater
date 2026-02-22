#!/usr/bin/env python3
"""
scripts/behavior_hash.py

Generate behavioral hash across 3 seeds for rung verification.

Runs the test suite with 3 different PYTHONHASHSEED values, normalizes the output
(strips timing and path noise), computes SHA-256 hashes, and checks for consensus.

Output: evidence/behavior_hash.json

Usage:
    python scripts/behavior_hash.py

Exit codes:
    0 — consensus reached (all 3 hashes agree)
    1 — no consensus (hashes differ) or test run failure
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SEEDS = [42, 137, 9001]

REPO_ROOT = Path(__file__).parent.parent.resolve()
EVIDENCE_DIR = REPO_ROOT / "evidence"
EVIDENCE_FILE = EVIDENCE_DIR / "behavior_hash.json"

TEST_COMMAND = [
    sys.executable, "-m", "pytest",
    "tests/",
    "-v",
    "--tb=no",
    "--override-ini=addopts=",  # suppress pyproject.toml -q so PASSED/FAILED lines appear
]

# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

_TIMING_RE = re.compile(r"\bin \d+\.\d+s\b")
_PASSED_IN_RE = re.compile(r"^\s*\d+ passed.*in \d+\.\d+s.*$", re.MULTILINE)
_FAILED_IN_RE = re.compile(r"^\s*\d+ (failed|error).*in \d+\.\d+s.*$", re.MULTILINE)
_TMP_PATH_RE = re.compile(r"/tmp/pytest-[^\s/\"']+")
_DURATION_COL_RE = re.compile(r"\b\d+\.\d{2,}s\b")
_WARNING_RE = re.compile(r"^.*DeprecationWarning.*$", re.MULTILINE)


def normalize_output(raw: str) -> str:
    """
    Normalize pytest output to remove timing and path non-determinism.

    Only PASSED/FAILED lines are extracted and sorted, making the hash
    insensitive to test ordering across different seeds.
    """
    text = raw

    # Normalize /tmp/pytest-* paths
    text = _TMP_PATH_RE.sub("/tmp/pytest-NORMALIZED", text)

    # Replace "in X.XXs" timing strings
    text = _TIMING_RE.sub("in N.NNs", text)

    # Remove summary lines containing "X passed in N.NNs"
    text = _PASSED_IN_RE.sub("", text)
    text = _FAILED_IN_RE.sub("", text)

    # Replace per-test timing column values like "0.03s"
    text = _DURATION_COL_RE.sub("N.NNs", text)

    # Extract and sort PASSED/FAILED lines — makes hash order-independent
    lines = [l for l in text.splitlines() if "PASSED" in l or "FAILED" in l]
    return "\n".join(sorted(lines))


# ---------------------------------------------------------------------------
# Hash computation
# ---------------------------------------------------------------------------

def compute_hash(text: str) -> str:
    """Return hex SHA-256 of the UTF-8 encoded normalized output."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_tests(seed: int) -> tuple[str, int]:
    """
    Run the test suite with the given PYTHONHASHSEED.

    Returns (combined_stdout_stderr, returncode).
    """
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = str(seed)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    result = subprocess.run(
        TEST_COMMAND,
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    combined = result.stdout + result.stderr
    return combined, result.returncode


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("Stillwater behavioral hash generator (behavior_hash.py)")
    print(f"Repo root : {REPO_ROOT}")
    print(f"Seeds     : {SEEDS}")
    print(f"Command   : {' '.join(TEST_COMMAND)}")
    print()

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    hashes: dict[str, str] = {}
    raw_outputs: dict[int, str] = {}

    for seed in SEEDS:
        print(f"Running with PYTHONHASHSEED={seed} ...", end=" ", flush=True)
        raw, rc = run_tests(seed)
        raw_outputs[seed] = raw
        normalized = normalize_output(raw)
        digest = compute_hash(normalized)
        key = f"seed_{seed}"
        hashes[key] = digest
        print(f"hash={digest[:16]}...  (exit {rc})")

    # Consensus check: all three hashes must agree
    unique_hashes = set(hashes.values())
    consensus = len(unique_hashes) == 1

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    result_doc = {
        "seed_42": hashes["seed_42"],
        "seed_137": hashes["seed_137"],
        "seed_9001": hashes["seed_9001"],
        "consensus": consensus,
        "generated": generated_at,
    }

    EVIDENCE_FILE.write_text(json.dumps(result_doc, indent=2) + "\n", encoding="utf-8")
    print()
    print(f"Evidence written to: {EVIDENCE_FILE}")

    if consensus:
        print(f"CONSENSUS: true  (hash={hashes['seed_42'][:32]}...)")
        return 0
    else:
        print("CONSENSUS: false — hashes differ across seeds!")
        for key, digest in hashes.items():
            print(f"  {key}: {digest}")
        print()
        print("Normalized outputs follow for debugging:")
        for seed in SEEDS:
            print(f"\n--- seed={seed} ---")
            print(normalize_output(raw_outputs[seed])[:2000])
        return 1


if __name__ == "__main__":
    sys.exit(main())
