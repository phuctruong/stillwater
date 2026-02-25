# Stillwater CLI Papers (Software 5.0)

This folder defines the architecture thesis for the Stillwater CLI reference kernel.

Software 5.0, in this CLI, means:
- intelligence is externalized in readable artifacts
- behavior is replayable via recipes and receipts
- trust comes from verification, not model confidence
- persistence lives outside model weights

## Paper Map

1. `01-software-5.0-kernel-and-ripples.md`
2. `02-post-mainframe-ai-run-anywhere.md`
3. `03-recipes-over-weights.md`
4. `04-persistent-intelligence-and-books.md`
5. `05-trust-safety-proof-carrying-cli.md`
6. `06-open-core-extension-economy.md`
7. `07-have-we-solved-math-for-llms.md`
8. `math-secret-sauce.md`
9. `how-to-solve-math-with-tiny-llm.md`
10. `how-to-solve-math-with-tiny-model.md` (compatibility alias)
11. `math-article.md` (compatibility alias)
12. `08-imo-history-convergence-results.md`

## Reproducibility Commands

```bash
./src/cli/stillwater-cli.sh papers list
./src/cli/stillwater-cli.sh papers show 01-software-5.0-kernel-and-ripples
./src/cli/stillwater-cli.sh books list
./src/cli/stillwater-cli.sh twin "/papers"
./src/cli/stillwater-cli.sh qa-fast
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q src/cli/tests
```

## Code Coverage Map

| Paper theme | Command surface | Test proof |
|---|---|---|
| Kernel + ripples | `paths`, `skills`, `recipe`, `wish` | `src/cli/tests/test_cli_twin_features.py` |
| Run anywhere | `llm probe-ollama`, `llm models`, `twin --interactive` | `src/cli/tests/test_cli_llm_support.py` |
| Recipes over weights | `recipe lint/list/add`, `stack run/verify`, `replay` | `src/cli/tests/test_notebook_root_parity.py` |
| Persistent intelligence | `books list/show`, `papers list/show`, twin `/books` + `/papers` | `src/cli/tests/test_notebook_root_parity.py` |
| Trust and safety | `oolong run/verify`, receipts in `artifacts/` | `src/cli/tests/test_smoke_repo.py` |
| Extension economy | `STILLWATER_*` kernel overrides | `src/cli/tests/test_cli_kernel_config.py` |
| Math claim hygiene | `qa-imo`, `imo-history fetch/bench` | `src/cli/tests/test_cli_math_route.py` |
| Math core architecture | `qa-imo`, `qa-imo-phuc`, `qa-imo-history`, `twin --json` | `src/cli/tests/test_cli_math_route.py` |

## Source Stack

- Root papers: `papers/*.md` (especially `papers/05-software-5.0.md`)
- Root books: `books/PERSISTENT-INTELLIGENCE.md`, `books/HOW-HUMANS-OUTSOURCED-THEIR-MINDS.md`
- Solace canon signals:
  - `~/projects/your-private-extension/...
  - `~/projects/your-private-extension/...
  - `~/projects/your-private-extension/...
  - `~/projects/your-private-extension/...
- External market signal:
  - https://podcasts.happyscribe.com/all-in-with-chamath-jason-sacks-friedberg/debt-spiral-or-new-golden-age-super-bowl-insider-trading-booming-token-budgets-ferrari-s-new-ev
