# Software 5.0 Kernel And Ripples

## Thesis

Stillwater CLI is split into:
- kernel code (stable, minimal churn)
- ripple files (skills, recipes, wishes, persona, identity)

This is the Software 5.0 boundary: code is the engine, ripples are the intelligence surface.

## Why This Matters

1. Kernel stability reduces maintenance drift.
2. Ripple files keep reasoning inspectable and versionable.
3. Teams can fork behavior without forking the runtime.

## Implementation In CLI

- Kernel:
  - `src/cli/src/stillwater/cli.py`
  - `src/cli/stillwater-cli.sh`
- Ripple surfaces:
  - `skills/*.md`
  - `src/cli/extensions/skills/*.md`
  - `src/cli/recipes/*.prime-mermaid.md`
  - `src/cli/wishes/*.md`
  - `src/cli/identity/*.md`

## Contract Signals Borrowed From Solace Canon

From `phase13/improvements2.md`:
- Recipe Contract: typed DAG with policy, verification, and trace.
- Convention Density: maturity metric based on deterministic steps and pass rate.

From `phase7/improvements2.md`:
- Conventions should emerge from repeated usage, then be promoted.

## Practical Policy

1. New capability starts as wish + recipe.
2. Promote only with receipts + tests.
3. Keep model-dependent logic in replaceable nodes.
4. Keep deterministic checks in CPU/gate nodes.
