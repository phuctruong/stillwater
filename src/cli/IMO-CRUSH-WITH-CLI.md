# How To Crush IMO With Stillwater CLI

This document defines a transparent benchmark protocol for IMO-style prompts.

## Goal

Show two lanes side-by-side:
1. `tool_assisted` lane: PHUC swarms benchmark orchestration (`phuc_swarms_benchmark`)
2. `llm_only` lane: same prompts, forced direct LLM (`--llm-only`)

This prevents hidden-routing claims and makes expert review straightforward.

Note: in normal mode, every prompt goes through generalized PHUC route decision first; this may select tools for benchmark-like prompts and LLM for generic prompts.

## One-Command QA

```bash
./src/cli/stillwater-cli.sh qa-imo
./src/cli/stillwater-cli.sh qa-imo-phuc
./src/cli/stillwater-cli.sh imo-phuc --required-rung 65537 --model llama3.1:8b
```

Historical IMO sweep (official PDFs + orchestration runtime check):

```bash
./src/cli/stillwater-cli.sh imo-history fetch --from-year 2020 --to-year 2024
./src/cli/stillwater-cli.sh imo-history oracles-template --from-year 2020 --to-year 2024 --fetch-missing --out src/cli/tests/math/imo_history_oracles.json
./src/cli/stillwater-cli.sh imo-history oracle-status --from-year 2020 --to-year 2024 --oracles-file src/cli/tests/math/imo_history_oracles.json --json
./src/cli/stillwater-cli.sh imo-history bench --from-year 2020 --to-year 2024 --fetch-missing --model llama3.1:8b --required-rung 65537
./src/cli/stillwater-cli.sh imo-history bench --from-year 2020 --to-year 2024 --fetch-missing --model llama3.1:8b --required-rung 65537 --oracles-file src/cli/tests/math/imo_history_oracles.json
./src/cli/stillwater-cli.sh imo-history autolearn --from-year 2020 --to-year 2024 --fetch-missing --model llama3.1:8b --required-rung 65537 --max-iterations 3 --oracles-file src/cli/tests/math/imo_history_oracles.json
./src/cli/stillwater-cli.sh math-universal --config src/cli/tests/math/universal_math_gate.json --json
./src/cli/stillwater-cli.sh qa-math-universal
```

Quick QA wrapper:

```bash
./src/cli/stillwater-cli.sh qa-imo-history
```

Output receipts:
- `artifacts/imo_qa/<run_id>/imo-qa-report.md`
- `artifacts/imo_qa/<run_id>/imo-qa-report.json`
- `artifacts/imo_qa/<run_id>/llm-status.txt`
- `artifacts/imo_qa/<run_id>/models.json`
- `artifacts/imo_phuc/<run_id>/REPORT.md` (SWE-pattern PHUC 5-phase receipts)
- `artifacts/imo_phuc/<run_id>/<case_id>/{SCOUT_REPORT,FORECAST_MEMO,DECISION_RECORD,ACT_RESULT,SKEPTIC_VERDICT}.json`
- `artifacts/imo_history/<run_id>/cases/<year>/<problem_id>/{SCOUT_REPORT,FORECAST_MEMO,DECISION_RECORD,ACT_RESULT,SKEPTIC_VERDICT}.json`
- `artifacts/imo_autolearn/<run_id>/{report.json,report.md,iter-*/BENCH_RUN.json,iter-*/PROPOSALS.json}`
- `artifacts/imo_memory/runs.jsonl` (cross-run memory ledger)
- `artifacts/imo_memory/board.md` and `artifacts/imo_memory/board.json` (recursive improvement board)

Config source:
- `src/cli/tests/math/imo_qa_cases.json` (question prompts + match needles)
- `src/cli/tests/math/imo_history_defaults.json` (history sweep defaults)
- `src/cli/tests/math/imo_history_oracles.json` (historical proof-grade oracle targets)
- `src/cli/tests/math/imo_history_oracles.empty.json` (empty oracle baseline for no-hint generalization)
- `src/cli/tests/math/proof_artifact_cases.json` (deterministic proof-artifact checks)
- `src/cli/tests/math/universal_math_gate.json` (universal-claim gate config)
- `imo_qa_cases.json` supports optional `aliases`, `concepts`, and `required_sections` for stronger semantic verification

## Default Strict Pass Criteria

`qa-imo` returns success only if:
1. target model is listed on reachable Ollama endpoint
2. `tool_assisted` lane scores `N/N`, where `N` is the number of configured cases in `src/cli/tests/math/imo_qa_cases.json`

`qa-imo-phuc` (`stillwater imo-phuc`) returns success only if:
1. every case passes the VERIFY gate
2. tool-assisted lane is `CPU + phuc_swarms_benchmark + needle_match`
3. expert council meets the selected rung gate (`--required-rung`, default `65537`)

`imo-history bench` strict pass is based on PHUC verdict pass count (`phuc_status=PASS`) and rung gate, not just subprocess success.
`imo-history oracles-template` preserves existing oracle fields by default; use `--no-merge-existing` only when intentionally resetting.
Rung `65537` now also enforces anti-parrot checks and oracle quality tiers (standard/strong), not just keyword/anchor hits.
At rung `65537`, historical cases must also have configured oracle targets and semantic match.
If oracle `concepts` / `required_sections` are present, rung `274177`+ also enforces those coverage checks.
Historical bench prompts now inject `Oracle anchor` / `Oracle concepts` and use the CPU `imo_history` tool lane (`phuc_imo_history_assist`) when route signals match.
`imo-history autolearn` runs a fail-closed memory loop: benchmark -> propose oracle updates -> re-benchmark -> apply only on measured improvement (or dry-run with `--no-apply`).

Current model defaults:
- `STILLWATER_IMO_MODEL=llama3.1:8b`
- `STILLWATER_IMO_TIMEOUT=30`

## No-Cheat Disclosure Rules

1. Always publish both lane scores together.
2. Clearly label lane semantics:
- `tool_assisted`: deterministic CPU solver + PHUC artifacts
- `llm_only`: pure remote model response path
- `imo-history`: historical orchestration/routing stability with PHUC phase receipts, not official proof grading
3. Include route receipts (`route.action`, `source`, model/url).
4. Never present tool-assisted score as pure model score.
5. Keep a durable memory loop (`artifacts/imo_memory/*`) so failures become reusable fixes, not repeated cost.
6. Publish rung target and achieved rung per case (`required_rung`, `rung_achieved`).

## Universal-Claim Gate

Run one report that operationalizes the four universal requirements:

```bash
./src/cli/stillwater-cli.sh math-universal --config src/cli/tests/math/universal_math_gate.json --json
```

The gate is PASS only if all are true:
1. held-out benchmark breadth gate passes
2. proof-artifact gate passes
3. no-oracle generalization gate passes
4. model/provider stability matrix gate passes

## Manual Spot Checks

Tool-assisted route (expected CPU benchmark action):
```bash
./src/cli/stillwater-cli.sh twin "In any 2-coloring of K6, what exists by R(3,3)=6?" --json
```

Pure model route (expected `source=LLM`, `action=ollama_chat`):
```bash
./src/cli/stillwater-cli.sh twin "In any 2-coloring of K6, what exists by R(3,3)=6?" --llm-only --model llama3.1:8b --json
```

Kernel/swarm settings disclosure:
```bash
./src/cli/stillwater-cli.sh twin "/kernel" --json
```
