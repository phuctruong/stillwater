# Hello, Stillwater — A 5-Minute Tutorial

> "Absorb what is useful, discard what is useless, and add what is specifically your own." — Bruce Lee

This tutorial walks through your first Stillwater workflow from zero to evidence bundle.

## What you'll build

A verified task run with:
- A skill loaded (prime-safety)
- An evidence artifact written
- SHA-256 verification

## Step 1: Install (30 seconds)
```bash
pip install -e ".[dev]"
stillwater --version   # should print: stillwater 1.x.x
```

## Step 2: Your first dry run (1 minute)
```bash
stillwater run "What are the key principles of Software 5.0?" --dry-run
# Output:
# [dry-run] run_id: run-abc12345
# [dry-run] task: What are the key principles of Software 5.0?
# [dry-run] skill: none
# [dry-run] prompt length: 46 chars
# Wrote: artifacts/runs/run-abc12345/manifest.json
```

## Step 3: Add a skill (2 minutes)
```bash
# List available skills
stillwater skills list

# Run with the prime-safety skill loaded
stillwater run "Review this code for security issues" --skill prime-safety --dry-run

# The skill adds 466 lines of security discipline to your prompt
```

## Step 4: Run with a real LLM (1 minute)
```bash
# Option A: Use Anthropic API
export ANTHROPIC_API_KEY=your-key
stillwater run "Summarize the Software 5.0 paradigm" --skill prime-coder

# Option B: Use local Ollama
# First: ollama pull llama3.1:8b
stillwater run "Summarize Software 5.0" --skill prime-coder

# Either way: artifacts are written to artifacts/runs/<run-id>/
```

## Step 5: Verify your run (30 seconds)
```bash
ls artifacts/runs/
cat artifacts/runs/<your-run-id>/manifest.json | python3 -m json.tool
```

## What just happened?

You just produced a **verifiable AI run**:
- The task is recorded with SHA-256
- The skill used is recorded
- The response is written to `response.txt`
- The manifest.json is machine-parseable

This is **Verification Rung 641** — local correctness. No other AI framework produces this by default.

## Next steps

- Run [the A/B benchmark](../HOW-TO-CRUSH-SWE-BENCHMARK.ipynb)
- Browse [skills/](../skills/) for more skills
- Read [papers/05-software-5.0.md](../papers/05-software-5.0.md) for the theory
- Contribute a skill: [community/SKILL-AUTHORING-GUIDE.md](../community/SKILL-AUTHORING-GUIDE.md)

## The Belt System

| Rung | Belt | What it means |
|---|---|---|
| 641 | Yellow | Local correctness: task ran, artifacts written, no errors |
| 274177 | Green | Stability: same result across 3+ seeds, replay verified |
| 65537 | Blue | Promotion: adversarial sweep, security gate, drift explained |

You just earned **Yellow Belt** on your first run.
