#!/usr/bin/env python3
"""
src/scripts/verify_hash.py

Read evidence/behavior_hash.json and verify all 3 seeds produce the same hash.

Exit codes:
    0 — consensus confirmed (all seeds match)
    1 — hash drift detected, or evidence file missing/malformed
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_FILE = REPO_ROOT / "evidence" / "behavior_hash.json"

REQUIRED_KEYS = {"seed_42", "seed_137", "seed_9001", "consensus", "generated"}


def main() -> int:
    print("Stillwater hash verifier (verify_hash.py)")
    print(f"Evidence file: {EVIDENCE_FILE}")
    print()

    # --- existence check ---
    if not EVIDENCE_FILE.exists():
        print(f"ERROR: evidence file not found: {EVIDENCE_FILE}")
        print("Run src/scripts/behavior_hash.py first to generate it.")
        return 1

    # --- parse ---
    try:
        data = json.loads(EVIDENCE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: could not parse evidence file: {exc}")
        return 1

    # --- schema check ---
    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        print(f"ERROR: evidence file missing required keys: {sorted(missing)}")
        return 1

    # --- type checks ---
    for seed_key in ("seed_42", "seed_137", "seed_9001"):
        val = data[seed_key]
        if not isinstance(val, str) or len(val) != 64:
            print(f"ERROR: {seed_key} is not a valid SHA-256 hex string (got: {val!r})")
            return 1

    if not isinstance(data["consensus"], bool):
        print(f"ERROR: 'consensus' must be bool, got {type(data['consensus']).__name__}")
        return 1

    # --- consensus check ---
    h42 = data["seed_42"]
    h137 = data["seed_137"]
    h9001 = data["seed_9001"]
    generated = data["generated"]

    unique = {h42, h137, h9001}

    print(f"Generated : {generated}")
    print(f"seed_42   : {h42[:32]}...")
    print(f"seed_137  : {h137[:32]}...")
    print(f"seed_9001 : {h9001[:32]}...")
    print()

    if len(unique) != 1:
        print("FAIL: hash drift detected across seeds!")
        print("Seeds do not all agree — behavioral non-determinism present.")
        return 1

    if not data["consensus"]:
        print("FAIL: 'consensus' field is false in evidence file.")
        return 1

    print(f"PASS: consensus confirmed (hash={h42[:32]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
