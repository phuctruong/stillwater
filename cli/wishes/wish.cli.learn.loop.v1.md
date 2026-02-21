# Wish: `wish.cli.learn.loop.v1`

Date: 2026-02-19  
Level: L1  
Skills: `prime-wishes`, `phuc-forecast`, `prime-coder`, `phuc-context`

## Quest + belt

- Quest: "Train the Memory Blade"
- Current belt: `White Belt`
- Target belt: `Green Belt`
- Promotion gate: propose/apply writes artifacts + ripple copy receipt

## Capability

Provide a deterministic `learn propose` / `learn apply` loop that externalizes updates in Prime Mermaid.

## Non-goals

- No autonomous self-editing without explicit apply step
- No hidden in-memory-only learning state

## Acceptance tests

1. `stillwater learn propose` writes proposal `.prime-mermaid.md` and metadata JSON.
2. `stillwater learn apply <proposal>` copies proposal to `ripples/project`.
3. Apply action writes an immutable receipt.
