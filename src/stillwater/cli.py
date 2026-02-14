"""Stillwater OS command-line interface."""

from __future__ import annotations

import argparse
import json
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="stillwater", description="Stillwater OS"
    )
    subparsers = parser.add_subparsers(dest="command")

    verify_parser = subparsers.add_parser(
        "verify",
        help="Run the verification ladder",
        description="Run the verification ladder: OAuth(39,63,91) -> 641 -> 274177 -> 65537",
    )
    verify_parser.add_argument(
        "--verbose", action="store_true", help="Show detailed verification ladder output"
    )

    args = parser.parse_args()

    if args.command == "verify":
        from stillwater.harness.verify import run_verification

        passed, cert = run_verification(verbose=args.verbose)
        if passed:
            with open("stillwater-certificate.json", "w") as f:
                json.dump(cert, sort_keys=True, indent=2, fp=f)
            print("PASSED")
            sys.exit(0)
        else:
            print("FAILED")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
