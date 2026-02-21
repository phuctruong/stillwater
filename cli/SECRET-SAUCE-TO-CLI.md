# Secret Sauce -> CLI Mapping

This file maps root secret-sauce notebooks to CLI implementation paths.

## Notebook Mapping

1. `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`
- CLI path: `stillwater stack run`, `stillwater twin`
- recipe: `cli/recipes/recipe.twin_orchestration.prime-mermaid.md`
- parity test: `cli/tests/test_notebook_root_parity.py::test_root_notebook_has_cli_parity[PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb]`

2. `PHUC-SKILLS-SECRET-SAUCE.ipynb`
- CLI path: `stillwater skills-ab --backend mock|ollama`
- parity test: `cli/tests/test_notebook_root_parity.py::test_root_notebook_has_cli_parity[PHUC-SKILLS-SECRET-SAUCE.ipynb]`

3. `PRIME-MERMAID-LANGUAGE-SECRET-SAUCE.ipynb`
- CLI path: `stillwater recipe lint --prime-mermaid-only`
- parity test: `cli/tests/test_notebook_root_parity.py::test_root_notebook_has_cli_parity[PRIME-MERMAID-LANGUAGE-SECRET-SAUCE.ipynb]`

4. `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb`
- CLI path: `./cli/stillwater-cli.sh qa-imo` (IMO-2024 demo lane split)
- SWE-pattern PHUC pipeline path: `stillwater imo-phuc` / `./cli/stillwater-cli.sh qa-imo-phuc`
- historical sweep: `stillwater imo-history fetch/bench` (official IMO PDFs)
- generalized math route: `phuc_math_assist` in `cli/src/stillwater/cli.py`

## Implementation Artifacts Added

- wish: `cli/wishes/wish.cli.secret_sauce.integration.v1.md`
- wish graph: `cli/wishes/wish.cli.secret_sauce.integration.v1.prime-mermaid.md`
- how-to notebook: `cli/notebooks/HOW-TO-SECRET-SAUCE-INTEGRATION.ipynb`
- integration recipe: `cli/recipes/recipe.secret_sauce.integration.prime-mermaid.md`
