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

    # connect subcommand
    connect_parser = subparsers.add_parser(
        "connect",
        help="Test LLM connectivity",
        description="Test connection to the configured LLM and list available models",
    )
    connect_parser.add_argument(
        "--model", default=None, help="Override LLM model"
    )
    connect_parser.add_argument(
        "--provider", default=None, help="LLM provider: ollama or openai"
    )

    # chat subcommand
    chat_parser = subparsers.add_parser(
        "chat",
        help="Send a prompt to the LLM",
        description="Send a single prompt and print the response",
    )
    chat_parser.add_argument(
        "prompt",
        help="The prompt to send",
    )
    chat_parser.add_argument(
        "--model", default=None, help="Override LLM model"
    )
    chat_parser.add_argument(
        "--provider", default=None, help="LLM provider: ollama or openai"
    )
    chat_parser.add_argument(
        "--temperature", type=float, default=None, help="Temperature (0 for deterministic)"
    )

    # verify subcommand
    verify_parser = subparsers.add_parser(
        "verify",
        help="Run the verification ladder",
        description="Run the verification ladder: OAuth(39,63,91) -> 641 -> 274177 -> 65537",
    )
    verify_parser.add_argument(
        "--verbose", action="store_true", help="Show detailed verification ladder output"
    )

    # bench subcommand
    bench_parser = subparsers.add_parser(
        "bench",
        help="Run the benchmark suite",
        description="Run Stillwater benchmarks against an LLM",
    )
    bench_parser.add_argument(
        "benchmark",
        nargs="?",
        default=None,
        help="Specific benchmark to run (default: all)",
    )
    bench_parser.add_argument(
        "--model", default=None, help="Override LLM model"
    )
    bench_parser.add_argument(
        "--provider", default=None, help="LLM provider: ollama or openai"
    )
    bench_parser.add_argument(
        "--verbose", action="store_true", help="Show per-instance details"
    )

    # oolong subcommand (standalone OOLONG benchmark)
    oolong_parser = subparsers.add_parser(
        "oolong",
        help="Run the OOLONG benchmark (CPU-only, no LLM required)",
        description="Run OOLONG long-context aggregation benchmark with deterministic solver",
    )
    oolong_parser.add_argument(
        "--split", default="validation", help="Dataset split: validation or test"
    )
    oolong_parser.add_argument(
        "--max-samples", type=int, default=0, help="Limit number of samples (0 = all)"
    )
    oolong_parser.add_argument(
        "--verbose", action="store_true", help="Show per-sample details"
    )

    args = parser.parse_args()

    if args.command == "connect":
        _cmd_connect(args)

    elif args.command == "chat":
        _cmd_chat(args)

    elif args.command == "verify":
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

    elif args.command == "bench":
        from stillwater.bench import BENCHMARKS
        from stillwater.bench.runner import run_all
        from stillwater.llm import LLMClient

        names = None
        if args.benchmark:
            if args.benchmark not in BENCHMARKS:
                print(f"Unknown benchmark: {args.benchmark}")
                print(f"Available: {', '.join(BENCHMARKS.keys())}")
                sys.exit(1)
            names = [args.benchmark]

        client = LLMClient(model=args.model, provider=args.provider)
        results, cert = run_all(client, names=names, verbose=args.verbose)

        with open("stillwater-bench-certificate.json", "w") as f:
            json.dump(cert, sort_keys=True, indent=2, fp=f)

        all_ok = cert["status"] == "PASSED"
        sys.exit(0 if all_ok else 1)

    elif args.command == "oolong":
        _cmd_oolong(args)

    else:
        parser.print_help()


def _cmd_connect(args: argparse.Namespace) -> None:
    """Test LLM connectivity: show config, list models, send test prompt."""
    import requests
    from stillwater.config import load_config
    from stillwater.llm import LLMClient, LLMError

    cfg = load_config()
    client = LLMClient(config=cfg, model=args.model, provider=args.provider)

    print(f"Provider:  {client.provider}")
    print(f"Endpoint:  {client.endpoint}")
    print(f"Model:     {client.model}")
    print()

    # Test connectivity
    if client.provider == "ollama":
        # List available models
        try:
            resp = requests.get(
                f"{client.endpoint}/api/tags", timeout=10
            )
            resp.raise_for_status()
            models = resp.json().get("models", [])
            if models:
                print(f"Available models ({len(models)}):")
                for m in models:
                    name = m.get("name", "?")
                    size = m.get("size", 0)
                    size_gb = size / (1024 ** 3) if size else 0
                    marker = "  <--" if name == client.model else ""
                    print(f"  {name:30s} {size_gb:5.1f} GB{marker}")
            else:
                print("No models found. Pull one with: ollama pull llama3.1:8b")
                sys.exit(1)
        except requests.ConnectionError:
            print(f"FAILED: Cannot connect to {client.endpoint}")
            print(f"Is Ollama running? Check: curl {client.endpoint}/api/tags")
            sys.exit(1)
        except requests.RequestException as e:
            print(f"FAILED: {e}")
            sys.exit(1)

        print()

    # Send test prompt
    print("Testing generation...")
    try:
        response = client.generate("Reply with exactly: OK", temperature=0, timeout=30)
        print(f"Response:  {response}")
        print()
        print("CONNECTED")
    except LLMError as e:
        print(f"FAILED: {e}")
        sys.exit(1)


def _cmd_chat(args: argparse.Namespace) -> None:
    """Send a single prompt and print the response."""
    from stillwater.llm import LLMClient, LLMError

    client = LLMClient(model=args.model, provider=args.provider)

    try:
        response = client.generate(
            args.prompt,
            temperature=args.temperature,
        )
        print(response)
    except LLMError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _cmd_oolong(args: argparse.Namespace) -> None:
    """Run OOLONG benchmark standalone."""
    from stillwater.bench.oolong import run_oolong

    print("Stillwater OOLONG Benchmark")
    print(f"Split: {args.split}")
    if args.max_samples:
        print(f"Max samples: {args.max_samples}")
    print("Solver: CPU-only (Counter + regex)")
    print()

    result = run_oolong(
        split=args.split,
        verbose=args.verbose,
        max_samples=args.max_samples,
    )

    if result.total == 0:
        for d in result.details:
            if "error" in d:
                print(f"Error: {d['error']}")
        sys.exit(1)

    # Print results
    print(f"Results: {result.passed}/{result.total} ({result.score:.1%})")
    print(f"Elapsed: {result.elapsed_ms:.0f}ms")

    # Print failures if any
    failures = [d for d in result.details if isinstance(d, dict) and not d.get("passed", True)]
    if failures and args.verbose:
        print(f"\nFailures ({len(failures)}):")
        for f in failures[:20]:
            print(f"  [{f.get('index', '?')}] {f.get('task', '')} | "
                  f"expected={f.get('expected', '')} got={f.get('predicted', '')}")
            print(f"       Q: {f.get('question', '')[:100]}")

    # Print failure summary by type
    for d in result.details:
        if isinstance(d, dict) and "failures_by_type" in d:
            print(f"\nFailures by task type:")
            for task_type, count in sorted(d["failures_by_type"].items()):
                print(f"  {task_type}: {count}")

    # Generate certificate
    cert = {
        "benchmark": "oolong",
        "dataset": "oolongbench/oolong-synth",
        "split": args.split,
        "total": result.total,
        "correct": result.passed,
        "accuracy": result.score,
        "elapsed_ms": round(result.elapsed_ms, 1),
        "status": "PASSED" if result.ok else "FAILED",
    }

    import hashlib
    cert_json = json.dumps({k: v for k, v in sorted(cert.items()) if k != "hash"},
                          sort_keys=True, separators=(",", ":"))
    cert["hash"] = f"sha256:{hashlib.sha256(cert_json.encode()).hexdigest()}"

    cert_path = "stillwater-oolong-certificate.json"
    with open(cert_path, "w") as f:
        json.dump(cert, sort_keys=True, indent=2, fp=f)

    print(f"\nCertificate: {cert_path}")
    print("PASSED" if result.ok else "FAILED")
    sys.exit(0 if result.ok else 1)


if __name__ == "__main__":
    main()
