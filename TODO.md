# TODO — Stillwater OS (Next Improvements)

**Date:** 2026-02-19  
**Goal:** close the remaining gap to a consistent 10/10 “skeptic-proof” system.

---

## 1) Receipts everywhere (highest ROI)

- Add a **PZIP development receipts harness** (mirror `artifacts/skills_ab/runs/<run_id>/manifest.json`): prompts, diffs, commands, outputs, hashes.
- Add a **SWE receipts harness** (even if “external data required”): at minimum record instance IDs, dataset hash, test commands, patch diffs, and per-instance verdicts.
- Add a `stillwater replay <run_id>` command to **re-hash and validate** a run directory against its manifest.

## 2) REAL backend becomes a first-class signal

- Make `.github/workflows/integration-ollama.yml` a repeatable “signal job”:
  - pinned model name + timeouts + budgets
  - scheduled runs on self-hosted runner
  - store artifact bundles for regressions

## 3) Release discipline (reduce churn)

- Add a lightweight release checklist (e.g., `RELEASE.md` or `scripts/release.sh`):
  - clean tree required
  - run CI-equivalent gates locally
  - regen generated docs
  - single tag + GitHub Release

## 4) Cost accounting (beyond proxies)

- Keep `eval_count`/`wall_seconds`, but add optional “true token/cost” capture when backends expose it.
- Define one canonical “cost report” schema so A/B comparisons stay stable.

## 5) Claims hygiene (turn narrative into evidence)

- For any external benchmark % claim:
  - ship a runnable harness + pinned inputs
  - ship logs/receipts + hashes
  - otherwise label as “hypothesis / anecdote”

## 6) More case studies (with receipts)

- Add 2–3 more “built with Stillwater” projects:
  - each with a reproducible harness or receipts bundle
  - one “tiny model” case and one “frontier model” case
  - publish a consistent scoreboard format

