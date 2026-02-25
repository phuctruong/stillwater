# Math Test Configs

This directory is the configuration source for IMO/math QA inputs.

Files:
- `imo_qa_cases.json`: prompts + expected match needles for `qa-imo` and CLI twin IMO router tests.
- `imo_history_defaults.json`: default year range and limits for `qa-imo-history` (`from_year: 2020`, `to_year: 2024`, `max_problems: 0` means run all in range).
- `imo_history_oracles.json`: optional proof-grade oracle targets for `imo-history bench` (`year` + `problem_id` -> `needle`/`aliases`).
- `imo_history_oracles.empty.json`: intentionally empty oracle file for no-hint generalization checks.
- `imo_route_cases.json`: IMO routing-only prompts for unit tests (for example, historical IMO prompts).
- `proof_artifact_cases.json`: deterministic proof-artifact checks (`expr_equals`, `gcd`, `lcm`, `modexp`, `deterministic_prompt`).
- `universal_math_gate.json`: config for `math-universal` gate suite (held-out breadth + proof artifacts + no-oracle generalization + stability matrix).

How to add more math questions:
1. Edit `imo_qa_cases.json`.
2. Add a new object to `cases`:
   - `id`: short label
   - `prompt`: question text
   - `needle`: substring expected in response for strict-match scoring
   - `aliases` (optional): semantic equivalents accepted by the matcher
   - `concepts` (optional): domain concepts expected in final response
   - `required_sections` (optional): section markers expected in final response
3. Run:
   - `./src/cli/stillwater-cli.sh qa-imo`
   - `./src/cli/stillwater-cli.sh imo-phuc --required-rung 65537 --model llama3.1:8b`
   - `./src/cli/stillwater-cli.sh imo-history bench --required-rung 65537 --from-year 2024 --to-year 2024 --max-problems 6`
   - `./src/cli/stillwater-cli.sh imo-history bench --required-rung 65537 --oracles-file src/cli/tests/math/imo_history_oracles.json --from-year 2024 --to-year 2024 --max-problems 6`
   - `./src/cli/stillwater-cli.sh imo-history autolearn --required-rung 65537 --from-year 2020 --to-year 2024 --max-iterations 3 --oracles-file src/cli/tests/math/imo_history_oracles.json`
   - `./src/cli/stillwater-cli.sh math-universal --config src/cli/tests/math/universal_math_gate.json --json`
   - `./src/cli/stillwater-cli.sh qa-math-universal`
   - `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q src/cli/tests`

No code changes are required for adding new QA cases.

Notes:
- `imo-history` is primarily an orchestration/runtime benchmark.
- Rung `274177`+ enforces oracle `concepts` / `required_sections` when those fields are present.
- Rung `65537` is intentionally blocked unless each case has oracle needles (`needle`/`aliases`) configured and matched.
- Bootstrap oracles quickly:
  - `./src/cli/stillwater-cli.sh imo-history oracles-template --from-year 2020 --to-year 2024 --fetch-missing --out src/cli/tests/math/imo_history_oracles.json`
  - default behavior preserves existing oracle fields; use `--no-merge-existing` only when intentionally resetting.
- Check progress to 65537 coverage:
  - `./src/cli/stillwater-cli.sh imo-history oracle-status --from-year 2020 --to-year 2024 --oracles-file src/cli/tests/math/imo_history_oracles.json --json`
  - Prefer `oracle_quality_ready` / `quality_ready_ratio` over raw `oracle_ready` for strict-quality tracking.
- Closed-loop self-learning:
  - `imo-history autolearn` runs `bench` iteratively, proposes oracle updates for failing/weak cases, and only writes changes when measured metrics improve.
  - Use `--no-apply` for dry-run previews.
- Universal-claim gates:
  - `math-universal` executes four gates from config:
    - held-out benchmark breadth
    - formal proof-artifact checks
    - no-oracle generalization checks
    - model/provider stability matrix
  - Universal claim readiness requires all four gates to pass in one report.
