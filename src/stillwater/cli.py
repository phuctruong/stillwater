from __future__ import annotations

import argparse
from pathlib import Path

from . import __version__


def _repo_root() -> Path:
    # `src/stillwater/cli.py` -> repo root is 3 parents up.
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stillwater",
        description="Stillwater OS helper CLI (repo-local).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="cmd", required=False)

    p_paths = sub.add_parser("paths", help="Print key repo paths.")
    p_paths.add_argument("--json", action="store_true", help="Machine-readable output.")

    p_print = sub.add_parser("print", help="Print suggested next steps.")

    ns = parser.parse_args(argv)

    root = _repo_root()
    notebooks = [
        "HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb",
        "HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb",
        "PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb",
    ]
    papers_index = "papers/00-index.md"
    mission = "MESSAGE-TO-HUMANITY.md"

    if ns.cmd == "paths":
        data = {
            "repo_root": str(root),
            "mission": str(root / mission),
            "papers_index": str(root / papers_index),
            "notebooks": [str(root / p) for p in notebooks],
        }
        if ns.json:
            import json

            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            print(f"repo_root: {data['repo_root']}")
            print(f"mission: {data['mission']}")
            print(f"papers_index: {data['papers_index']}")
            print("notebooks:")
            for p in data["notebooks"]:
                print(f"  - {p}")
        return 0

    # Default: print quick directions.
    if ns.cmd == "print" or ns.cmd is None:
        print("Key files:")
        print(f"  - {mission}")
        print(f"  - {papers_index}")
        print("Notebooks (demo mode runs offline by default):")
        for p in notebooks:
            print(f"  - {p}")
        print("")
        print("Run notebooks:")
        print("  python -m nbconvert --execute --to notebook --inplace <NOTEBOOK.ipynb>")
        print("")
        print("Enable LLM-backed runs (optional):")
        print("  export STILLWATER_ENABLE_LLM_REAL=1")
        print("  export STILLWATER_WRAPPER_URL=http://localhost:8080/api/generate")
        return 0

    return 0

