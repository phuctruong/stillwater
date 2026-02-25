# Stillwater CLI Manual

This manual defines the reference model:
- `stillwater` is the kernel.
- project-specific intelligence lives in extension files.
- Prime Mermaid is the canonical externalized reasoning language.

## Kernel Versus Extension

Kernel responsibilities (`src/cli/src/stillwater/`):
- command routing and runtime orchestration
- CPU prepass and guardrails
- local/remote Ollama connectivity
- receipts, replay, verification, and QA flows
- generalized PHUC route decision for every prompt (decide tool-assisted vs LLM path)

Extension responsibilities (default `src/cli/extensions/` or `STILLWATER_EXTENSION_ROOT`):
- skills (`skills/*.md`)
- recipes (`recipes/*.prime-mermaid.md`)
- persona (`personas/default.md`)
- identity overlays (`identity/*.md`)
- splash/prompt personality (`splash.txt`, env vars)

Trade-secret model:
- open-source the kernel and baseline public skills.
- keep private advantage in extension packs (skills, recipes, personas, memory strategy).

## Convention-Over-Configuration

Primary convention:
1. Keep kernel code stable.
2. Customize by editing extension files.
3. Track behavior changes as wishes + notebooks + receipts.
4. Use `src/cli/kernel_config.yaml` for file-path defaults; use env vars for per-run overrides.

Supported override environment variables:
- `STILLWATER_EXTENSION_ROOT`
- `STILLWATER_SKILL_DIRS`
- `STILLWATER_RECIPE_DIRS`
- `STILLWATER_IDENTITY_DIR`
- `STILLWATER_PERSONA_FILE`
- `STILLWATER_SOUL_FILE`
- `STILLWATER_SPLASH_FILE`
- `STILLWATER_HISTORY_FILE`
- `STILLWATER_PROMPT_PREFIX`
- `STILLWATER_ASSISTANT_PREFIX`
- `STILLWATER_BOOK_DIRS`
- `STILLWATER_PAPER_DIRS`
- `STILLWATER_KERNEL_CONFIG`
- `STILLWATER_SWARM_SETTINGS_FILE`

Inspect resolved paths:

```bash
./src/cli/stillwater-cli.sh paths
./src/cli/stillwater-cli.sh twin "/kernel"
./src/cli/stillwater-cli.sh books list
./src/cli/stillwater-cli.sh papers list
./src/cli/stillwater-cli.sh cleanup scan --json
```

Software 5.0 docs:
- `src/cli/papers/00-index.md`
- `notebooks/HOW-TO-SOFTWARE-5.0-PAPERS.ipynb`
- `src/cli/settings/SWARM-ORCHESTRATION.prime-mermaid.md` (externalized swarm contract)

## Clone-To-First-Run Workflow

1. Configure model connectivity.
2. Verify kernel paths.
3. Start twin interactive mode.
4. Run QA fast path.
5. Run notebook path for proof.

```bash
./src/cli/stillwater-cli.sh llm set-ollama --auto-url --activate
./src/cli/stillwater-cli.sh llm models
./src/cli/stillwater-cli.sh twin "/kernel"
./src/cli/stillwater-cli.sh twin --interactive
./src/cli/stillwater-cli.sh qa-fast
./src/cli/stillwater-cli.sh qa-imo
./src/cli/stillwater-cli.sh qa-imo-history
./src/cli/stillwater-cli.sh qa-notebooks
```

## IMO Proof Protocol (Expert-Friendly)

Use:
- `src/cli/IMO-CRUSH-WITH-CLI.md`
- `./src/cli/stillwater-cli.sh qa-imo`
- `./src/cli/stillwater-cli.sh imo-history fetch --from-year 2020 --to-year 2024`
- `./src/cli/stillwater-cli.sh imo-history oracles-template --from-year 2020 --to-year 2024 --fetch-missing --out src/cli/tests/math/imo_history_oracles.json`
- `./src/cli/stillwater-cli.sh imo-history oracle-status --from-year 2020 --to-year 2024 --oracles-file src/cli/tests/math/imo_history_oracles.json --json`
- `./src/cli/stillwater-cli.sh imo-history bench --from-year 2020 --to-year 2024 --fetch-missing --model llama3.1:8b`
- `./src/cli/stillwater-cli.sh imo-history autolearn --from-year 2020 --to-year 2024 --fetch-missing --model llama3.1:8b --required-rung 65537 --max-iterations 3 --oracles-file src/cli/tests/math/imo_history_oracles.json`
- `./src/cli/stillwater-cli.sh math-universal --config src/cli/tests/math/universal_math_gate.json --json`
- `./src/cli/stillwater-cli.sh qa-math-universal`
- `src/cli/tests/math/imo_qa_cases.json` (editable case config)
- `src/cli/tests/math/imo_history_defaults.json` (editable history defaults)
- `src/cli/tests/math/imo_history_oracles.json` (editable historical oracle targets)
- `src/cli/tests/math/proof_artifact_cases.json` (deterministic proof-artifact config)
- `src/cli/tests/math/universal_math_gate.json` (universal claim gate config)

This intentionally reports two lanes:
1. `tool_assisted` (PHUC swarms deterministic benchmark route)
2. `llm_only` (pure remote model with `--llm-only`)
3. historical IMO runtime lane (`imo-history`) for orchestration stability across years

Notes:
- `imo-history` at rung `641`/`274177` is an orchestration/runtime quality gate.
- if oracle `concepts` / `required_sections` are configured, rung `274177` and `65537` enforce those coverage gates.
- historical rung `65537` is intentionally fail-closed unless oracle targets are configured and matched.
- historical bench prompts include `Oracle anchor` + `Oracle concepts` hints so the `imo_history` CPU tool lane can be evaluated deterministically.
- `qa-imo-history` defaults to rung `65537` (override with `STILLWATER_IMO_HISTORY_REQUIRED_RUNG`).
- `qa-imo-history` defaults to years `2020..2024` and `max_problems=0` (run all problems in range).
- `imo-history oracles-template` now preserves existing oracle fields by default; pass `--no-merge-existing` to intentionally reset.
- `imo-history oracle-status` is the canonical distance-to-100% report.
- `imo-history autolearn` is the closed-loop updater: benchmark -> propose oracle patches -> re-verify -> apply only on measured improvement.
- Use `oracle_quality_ready`/`quality_ready_ratio` for strict-quality readiness (not just raw target presence).
- `math-universal` is the strict universal-claim gate:
  - held-out breadth
  - proof artifacts
  - no-oracle generalization
  - model/provider stability

Publishing both lanes avoids “hidden tool use” confusion during math/AI expert review.

## Bruce Lee Dojo Loop

Use this loop for every capability:
1. `Absorb`: observe current behavior and artifacts.
2. `Discard`: remove unverifiable or noisy steps.
3. `Add`: encode new behavior in skills/recipes/wishes.
4. `Verify`: pass belts using tests and receipts.

Belts:
- White: scaffold works and runs.
- Yellow: deterministic CPU and receipts.
- Green: remote/local model portability.
- Brown: replay and regression stability.
- Black: benchmark claims with reproducible proof.

## Wishes + Notebooks Together

Wishes define the contract:
- capability
- non-goals
- belt gates
- acceptance tests

Notebooks execute the contract:
- run commands
- collect evidence
- output artifacts

Rule:
- no promotion to higher belt without notebook receipts that satisfy the wish.

Secret-sauce bridge:
- `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb` -> stack/twin orchestration parity tests.
- `PHUC-SKILLS-SECRET-SAUCE.ipynb` -> `skills-ab` parity tests.
- `PRIME-MERMAID-LANGUAGE-SECRET-SAUCE.ipynb` -> recipe lint and contract tests.

## Identity Stack

Identity files live in `src/cli/identity/` and can be overridden in extensions:
- `SOUL.md` mission and ethics
- `IDENTITY.md` invariants
- `AGENTS.md` operating contract
- `USER.md` user preferences
- `HEARTBEAT.md` operational cadence
- `BOOTSTRAP.md` startup sequence
- `MEMORY.md` durable memory map
- `RIPPLE-IDENTITY.prime-mermaid.md` graph contract

## Solace-CLI As Extension (Reference)

Use `~/projects/solace-cli` as a private extension on top of stillwater kernel:
1. keep kernel in `~/projects/stillwater/src/cli/src/stillwater/`
2. place custom files in `~/projects/solace-cli/stillwater_extension/`
3. run stillwater with extension env and remote Ollama defaults

This gives:
- one stable OSS base
- one private high-alpha overlay
- minimal fork drift
