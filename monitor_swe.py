#!/usr/bin/env python3
"""Monitor SWE-bench run progress."""

import json
import time
from pathlib import Path

PROGRESS_FILE = Path("stillwater-swe-lite-progress.json")

def monitor():
    while True:
        try:
            with open(PROGRESS_FILE) as f:
                prog = json.load(f)

            completed = len(prog.get("completed", []))
            verified = sum(1 for r in prog.get("results", []) if r.get("verified"))

            print(f"\rProgress: {completed}/300 ({completed/3:.1f}%) | Verified: {verified} | Failed: {completed-verified}", end="", flush=True)

            if completed >= 300:
                print("\n✅ Run complete!")
                break

        except FileNotFoundError:
            print("\rWaiting for progress file...", end="", flush=True)
        except Exception as e:
            print(f"\n⚠️  Error: {e}")

        time.sleep(5)

if __name__ == "__main__":
    try:
        monitor()
    except KeyboardInterrupt:
        print("\n\n⏸️  Monitoring stopped")
