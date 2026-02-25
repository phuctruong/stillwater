# Wish: wish.cli.software5.papers.v1

Date: 2026-02-19T00:00:00Z
Level: L1

## Quest + Belt

- Quest: "Software 5.0 Scrolls"
- Current belt: White Belt
- Target belt: Green Belt
- Promotion gate: papers + books interfaces implemented and verified

## Capability

- Add a `src/cli/papers/` documentation spine for Stillwater CLI Software 5.0.
- Expose papers as first-class runtime assets (`papers list/show` + twin `/papers`).
- Ensure paper claims map to runnable commands/tests and root books.

## Non-goals

- No change to benchmark scoring policy.
- No new external provider integrations beyond existing Ollama support.

## Acceptance Tests

1. `python -m stillwater papers list --json` returns >= 1 paper.
2. `python -m stillwater papers show 00-index` succeeds.
3. `python -m stillwater twin "/papers" --json` routes to CPU.
4. `pytest -q src/cli/tests/test_cli_kernel_config.py` passes with external `papers_dirs`.

## Artifacts

- `src/cli/papers/*.md`
- `notebooks/HOW-TO-SOFTWARE-5.0-PAPERS.ipynb`
- test receipts from `src/cli/tests/*`
