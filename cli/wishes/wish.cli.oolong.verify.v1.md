# Wish: `wish.cli.oolong.verify.v1`

Date: 2026-02-19  
Level: L1  
Skills: `prime-wishes`, `prime-math`, `prime-coder`, `prime-safety`

## Quest + belt

- Quest: "Defeat the Counting Illusion"
- Current belt: `Green Belt`
- Target belt: `Black Belt`
- Promotion gate: `stillwater oolong verify --strict` PASS

## Capability

Add strict verification for OOLONG runs with rung checks and counter-bypass completion signal.

## Non-goals

- No fabricated confidence when rungs fail
- No numeric answers without CPU witness path

## Acceptance tests

1. `stillwater oolong run` writes summary with parsed rung states.
2. `stillwater oolong verify --strict` passes only when all rung checks pass.
3. Verification fails closed on missing or malformed summary artifacts.
