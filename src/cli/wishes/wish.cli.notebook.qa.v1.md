# Wish: `wish.cli.notebook.qa.v1`

Date: 2026-02-19  
Level: L1 wish notebook compatible  
Skills: `prime-wishes`, `phuc-forecast`, `prime-coder`, `prime-safety`, `phuc-context`

## Quest + belt

- Quest: "Prove the HOW-TO Arena"
- Current belt: `White Belt`
- Target belt: `Green Belt`
- Promotion gate: all `notebooks/HOW-TO-*.ipynb` execute with zero failures

## Capability

Provide a deterministic notebook QA loop that executes all HOW-TO notebooks and fails closed on errors.

## Non-goals

- No hidden pass via ignored stderr
- No notebook-only logic that bypasses CLI commands

## Acceptance tests

1. Every HOW-TO notebook executes via `nbconvert --execute`.
2. Notebook cells fail closed when subprocess return codes are non-zero.
3. QA emits a clear pass/fail summary and failing notebook path.
