# Have We Solved Math For LLMs?

Short answer: no.

It is not fair to claim "math is solved for LLMs" yet.

## What We Can Claim (Now)

1. We solved a reproducible **math orchestration framework** in Stillwater CLI.
2. We solved deterministic handling for a subset of math prompts:
- arithmetic expressions
- `gcd` / `lcm`
- modular exponent forms
3. We separated lanes so claims are auditable:
- `tool_assisted` lane (CPU receipts)
- `llm_only` lane (pure model)
- historical IMO runtime lane

## Harsh QA Evidence (2026-02-20 UTC)

1. Unit/integration tests:
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q cli/tests`
- result: `60 passed, 4 skipped`

2. IMO 2024 lane split (latest strict run):
- command: `./cli/stillwater-cli.sh qa-imo`
- report: `artifacts/imo_qa/qa-imo-20260220T153107Z/imo-qa-report.json`
- result:
  - tool-assisted: `6/6`
  - llm-only: `1/6`

3. PHUC 5-phase IMO lane (rung-gated):
- command: `./cli/stillwater-cli.sh imo-phuc --model llama3.1:8b --required-rung 65537 --json`
- report: `artifacts/imo_phuc/imo-phuc-20260220T140523413567Z/REPORT.json`
- result:
  - tool-assisted: `6/6`
  - strict pass: `true`
  - lane disclosure preserved (`tool_assisted` vs `llm_only`)

4. Historical IMO sweep (official PDFs, bounded sample):
- command: `./cli/stillwater-cli.sh imo-history bench --from-year 2022 --to-year 2022 --max-problems 2 --required-rung 641 --model llama3.1:8b --json`
- report: `artifacts/imo_history/imo-history-20260220T140350580010Z/report.json`
- result: `2/2` strict pass at rung `641` (runtime/orchestration quality gate)

5. 65537 gate honesty check (expected fail):
- command:
  - `./cli/stillwater-cli.sh imo-history bench --from-year 2022 --to-year 2022 --max-problems 2 --required-rung 65537 --model llama3.1:8b --json`
- report: `artifacts/imo_history/imo-history-20260220T140326225892Z/report.json`
- result:
  - strict fail (`pass_cases=0/2`)
  - reason: no oracle needles configured for historical cases, so `65537` is intentionally withheld

6. Historical oracle coverage snapshot:
- command:
  - `./cli/stillwater-cli.sh imo-history oracle-status --from-year 2022 --to-year 2024 --oracles-file cli/tests/math/imo_history_oracles.json --json`
- report: `artifacts/imo_oracle_status/imo-oracle-status-20260220T152610863412Z/report.json`
- result:
  - oracle-ready: `2/18` (`11.11%`)
  - missing oracle targets: `16/18`

## PHUC Forecast Cycle Applied

### DREAM
Goal: validate broad IMO coverage with transparent receipts and no hidden-route claims.

### FORECAST
Top risk: remote model instability (timeouts) can create false negatives in harsh QA.

### DECIDE
Harden verifier quality without hiding uncertainty:
1. add rung-gated expert council checks (`641/274177/65537`)
2. add semantic/alias/concept/section matchers
3. add historical anti-template grounding gates and oracle-required `65537` policy
4. keep fail-closed behavior for proof-grade claims

### ACT
Implemented in `cli/src/stillwater/cli.py`:
1. expert council config + aggregation
2. semantic matcher (`needle` + `aliases`)
3. concept/section gating (`concepts`, `required_sections`)
4. semantic rung ordering (`641 < 274177 < 65537`)
5. strict rung enforcement in `imo-phuc` and `imo-history bench`
6. historical `65537` now requires oracle targets (`needle`/`aliases`) and strong semantic match
7. historical oracle targets are externalized (`cli/tests/math/imo_history_oracles.json` or `imo-history bench --oracles-file ...`)
8. oracle templates can be generated directly from cached IMO datasets (`imo-history oracles-template ...`)
9. oracle coverage is now measurable (`imo-history oracle-status ...`) so distance-to-100% is explicit
10. broad `imo` route signal was removed to prevent official 2024 historical prompts from accidentally hitting the demo solver lane

### VERIFY
Validated with:
1. `60 passed, 4 skipped` in test suite
2. real remote Ollama `llama3.1:8b` runs
3. explicit expected-fail run at rung 65537 for historical case

## Why "Solved Math" Is Still Wrong

1. No official IMO grading equivalence.
2. No formal proof checker/theorem prover integration for general proofs.
3. Historical prompt grading is still policy-based, not theorem-certified equivalence.

## Correct Public Claim

Stillwater CLI does not solve all math for LLMs yet.
It provides a reproducible, auditable architecture that measurably improves math reliability, enforces honest rung-gated claims, and creates a credible path toward that goal.

## Next Hard Gates

1. Add theorem-check lane (Lean/Isabelle-style proof verification or equivalent).
2. Add rubric + witness graph proof graders for historical IMO prompts.
3. Require lane-separated reporting in all public math claims.
4. Keep "no hidden tools" disclosure mandatory.
5. Expand hidden holdout datasets and freeze benchmark snapshots for claim stability.

## Detailed Blueprint

For the full Software 5.0 architecture, algorithm, and mermaid flows, see:
- `cli/papers/math-secret-sauce.md`
