# Wish: `wish.cli.replay.v1`

Date: 2026-02-19  
Level: L1  
Skills: `prime-wishes`, `phuc-forecast`, `prime-coder`

## Quest + belt

- Quest: "Replay the River"
- Current belt: `Yellow Belt`
- Target belt: `Brown Belt`
- Promotion gate: replay view + rerun receipts are deterministic

## Capability

Allow users to replay a prior stack run from `artifacts/runs/<run_id>/manifest.json`.

## Non-goals

- No distributed replay
- No speculative missing-step synthesis

## Acceptance tests

1. `stillwater replay <run_id>` prints profile, status, and step list.
2. `stillwater replay <run_id> --rerun` writes replay report artifact.
3. Replay fails closed when manifest is missing.
