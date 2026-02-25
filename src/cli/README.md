# Stillwater CLI (Kernel + Extensions)

Stillwater CLI is the reference AGI CLI framework:
- stable kernel in `src/cli/src/stillwater/`
- customizable intelligence in extension files
- Prime Mermaid as canonical externalized reasoning

## Start Here

```bash
./src/cli/stillwater-cli.sh llm set-ollama --auto-url --activate
./src/cli/stillwater-cli.sh llm models
./src/cli/stillwater-cli.sh twin "/kernel"
./src/cli/stillwater-cli.sh twin --interactive
./src/cli/stillwater-cli.sh imo-history fetch --from-year 2020 --to-year 2024
./src/cli/stillwater-cli.sh imo-history bench --from-year 2020 --to-year 2024 --fetch-missing --model llama3.1:8b
```

## Core Design

1. Kernel code is durable and mostly unchanged.
2. Custom behavior ships as files: skills, recipes, personas, identity ripples.
3. Receipts and replay are mandatory for serious claims.
4. Every prompt passes through PHUC orchestration routing (tool vs LLM decision), with `--llm-only` as explicit override.
5. Math routing is now split:
- deterministic `phuc_math_assist` for computable prompts (`gcd`, modular arithmetic, arithmetic expressions)
- historical IMO prompts (non-2024) route to generalized math orchestration + LLM instead of the 2024 demo solver

See the full guide: `src/cli/MANUAL.md`.
Kernel defaults are in `src/cli/kernel_config.yaml` (override with `STILLWATER_KERNEL_CONFIG`).
Swarm orchestration settings are externalized in `src/cli/settings/SWARM-ORCHESTRATION.prime-mermaid.md`.

## Extension Layout

Default extension root is `src/cli/extensions/` (or set `STILLWATER_EXTENSION_ROOT`):
- `skills/*.md`
- `recipes/*.prime-mermaid.md`
- `personas/default.md`
- `identity/*.md`
- `splash.txt`

Inspect resolved paths:

```bash
./src/cli/stillwater-cli.sh paths
./src/cli/stillwater-cli.sh twin "/kernel"
./src/cli/stillwater-cli.sh books list
./src/cli/stillwater-cli.sh papers list
./src/cli/stillwater-cli.sh cleanup scan --json
```

Software 5.0 paper spine:
- `src/cli/papers/00-index.md`
- `notebooks/HOW-TO-SOFTWARE-5.0-PAPERS.ipynb`

## Dojo Workflow (Bruce Lee Theme)

1. Absorb: run current stack and inspect artifacts.
2. Discard: remove non-deterministic or low-signal behaviors.
3. Add: encode improvements in wishes + recipes + skills.
4. Verify: pass tests and notebook gates before promotion.

## Wishes + Notebooks

- Wishes define capability contracts and belt gates.
- HOW-TO notebooks execute those contracts and produce proof.

Primary paths:
- `src/cli/wishes/README.md`
- `src/cli/wishes/outline.md`
- `notebooks/README.md`
- `notebooks/HOW-TO-SECRET-SAUCE-INTEGRATION.ipynb`
- `src/cli/SECRET-SAUCE-TO-CLI.md`

Run harsh QA:

```bash
./src/cli/stillwater-cli.sh qa-fast
./src/cli/stillwater-cli.sh qa-imo
./src/cli/stillwater-cli.sh qa-imo-phuc
./src/cli/stillwater-cli.sh qa-notebooks
./src/cli/stillwater-cli.sh qa-secret-sauce
./src/cli/stillwater-cli.sh qa-imo-history
./src/cli/stillwater-cli.sh qa
```

## IMO Benchmark Protocol

Use the transparent two-lane protocol in `src/cli/IMO-CRUSH-WITH-CLI.md`.

Quick run:

```bash
./src/cli/stillwater-cli.sh qa-imo
./src/cli/stillwater-cli.sh imo-phuc --required-rung 65537 --model llama3.1:8b
./src/cli/stillwater-cli.sh imo-history oracles-template --from-year 2020 --to-year 2024 --fetch-missing --out src/cli/tests/math/imo_history_oracles.json
./src/cli/stillwater-cli.sh imo-history oracle-status --from-year 2020 --to-year 2024 --oracles-file src/cli/tests/math/imo_history_oracles.json --json
./src/cli/stillwater-cli.sh imo-history bench --from-year 2024 --to-year 2024 --required-rung 641 --max-problems 6
```

Editable case config:
- `src/cli/tests/math/imo_qa_cases.json`
- `src/cli/tests/math/imo_history_defaults.json`

This reports:
- `tool_assisted` lane (PHUC swarms deterministic route)
- `llm_only` lane (`--llm-only` remote model baseline)
- persistent memory loop receipts under `artifacts/imo_memory/` for cross-run improvement
- rung-gated expert council verdicts (`641 -> 274177 -> 65537`) with configurable settings in `src/cli/settings/SWARM-ORCHESTRATION.prime-mermaid.md`
- semantic matcher support for IMO case needles (use `aliases`, `concepts`, `required_sections` in `src/cli/tests/math/imo_qa_cases.json`)
- historical `imo-history` rung `65537` requires per-case oracle needles/aliases (otherwise max rung is capped below promotion)
- historical oracle config path: `src/cli/tests/math/imo_history_oracles.json` (override with `imo-history bench --oracles-file ...`)

## Remote Ollama Support

Detection order:
1. explicit CLI URL
2. `STILLWATER_OLLAMA_URL` / `STILLWATER_OLLAMA_URLS`
3. local defaults (`localhost:11434`, `127.0.0.1:11434`)
4. `llm_config.yaml` (`ollama.url`)
5. `~/projects/solace-cli/solace_cli/settings.json` (remote host hint)
