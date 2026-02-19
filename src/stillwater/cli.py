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

    p_skills_ab = sub.add_parser("skills-ab", help="Run the skills A/B/AB/ABC benchmark (local-first).")
    p_skills_ab.add_argument("--backend", choices=["auto", "ollama", "mock"], default="auto")
    p_skills_ab.add_argument("--ollama-url", default="http://localhost:11434")
    p_skills_ab.add_argument("--model", default=None, help="Model name (backend-specific).")
    p_skills_ab.add_argument("--no-cache", action="store_true", help="Disable response caching.")
    p_skills_ab.add_argument("--timeout", type=float, default=60.0, help="Backend request timeout in seconds.")
    p_skills_ab.add_argument("--seed", type=int, default=1337, help="Determinism seed (mock backend).")
    p_skills_ab.add_argument("--run-id", default=None, help="Optional run id for receipts (default: UTC timestamp).")
    p_skills_ab.add_argument("--no-record-prompts", action="store_true", help="Do not write raw prompt/response receipts.")

    p_gen = sub.add_parser("gen-ai-steroids-readme", help="Generate ai-steroids-results/README.md (or check it).")
    p_gen.add_argument("--check", action="store_true", help="Exit non-zero if README would change.")

    ns = parser.parse_args(argv)

    root = _repo_root()
    notebooks = [
        "HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb",
        "HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb",
        "HOW-TO-CRUSH-SWE-BENCHMARK.ipynb",
        "PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb",
        "PHUC-SKILLS-SECRET-SAUCE.ipynb",
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

    if ns.cmd == "skills-ab":
        from .skills_ab import SkillsABConfig, run_skills_ab

        cfg = SkillsABConfig(
            repo_root=root,
            skills_dir=root / "skills",
            artifacts_dir=root / "artifacts" / "skills_ab",
            backend=ns.backend,
            ollama_url=ns.ollama_url,
            model=ns.model or ("mock-kungfu-v1" if ns.backend == "mock" else "qwen2.5-coder:7b"),
            use_cache=(not ns.no_cache),
            seed=ns.seed,
            run_id=ns.run_id,
            request_timeout_seconds=ns.timeout,
            record_prompts=(not ns.no_record_prompts),
        )
        run_skills_ab(cfg)
        print(f"Wrote: {cfg.artifacts_dir / 'results.json'}")
        print(f"Wrote: {cfg.artifacts_dir / 'report.md'}")
        return 0

    if ns.cmd == "gen-ai-steroids-readme":
        from .gen_ai_steroids_readme import generate_readme

        out_path = root / "ai-steroids-results" / "README.md"
        new_text = generate_readme(root=root)
        if ns.check and out_path.exists():
            old = out_path.read_text(encoding="utf-8")
            if old != new_text:
                print(f"README out of date: {out_path}")
                return 1
            return 0
        out_path.write_text(new_text, encoding="utf-8")
        print(f"Wrote: {out_path}")
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
