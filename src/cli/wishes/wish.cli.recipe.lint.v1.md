# Wish: `wish.cli.recipe.lint.v1`

Date: 2026-02-19  
Level: L1  
Skills: `prime-wishes`, `prime-coder`, `prime-safety`

## Quest + belt

- Quest: "Seal the Prime Mermaid Contract"
- Current belt: `White Belt`
- Target belt: `Green Belt`
- Promotion gate: `stillwater recipe lint --prime-mermaid-only` PASS

## Capability

Enforce Prime Mermaid-first externalization rules over wish/ripple/recipe directories.

## Non-goals

- No mutation or auto-fix of violating files
- No blocking of derived artifact JSON inside `artifacts/`

## Acceptance tests

1. Lint command scans configured directories.
2. Lint fails when source YAML/JSON appears in governed paths.
3. Lint passes when governed paths are Prime Mermaid compliant.
