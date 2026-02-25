# Wish: `wish.cli.stack.run.v1`

Date: 2026-02-19  
Level: L1 wish notebook compatible  
Skills: `prime-wishes`, `phuc-forecast`, `prime-coder`, `prime-safety`, `phuc-context`

## Quest + belt

- Quest: "Forge the Full Stack Run"
- Current belt: `Yellow Belt`
- Target belt: `Brown Belt`
- Promotion gate: `stack run` PASS + `stack verify --strict` PASS + deterministic graph hash

## Capability

Provide one command (`stillwater stack run`) that executes a reproducible full-stack flow and stores replayable receipts.

## Non-goals

- No cloud scheduler orchestration
- No remote control plane
- No hidden state outside artifact bundle

## Acceptance tests

1. `stillwater stack run --profile offline` writes `manifest.json`, `stack.mmd`, and `stack.sha256`.
2. `stillwater stack verify --strict` passes for a successful run.
3. `stillwater replay <run_id>` prints prior steps with statuses.
