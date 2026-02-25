# AGENTS.md — Stillwater Software 5.0 Contract

## Session Boot

- Use `.claude/commands/software5` as the startup protocol.
- Resolve 4W+H before execution: `WHY WHAT WHEN WHO HOW`.
- If any 4W+H probe is unresolved, ask before coding.

## Northstar

- `NORTHSTAR`: `Phuc_Forecast`
- `RUNG_TARGET`: `65537`
- Prefer improvements that compound reusable skill law over one-off patches.

## Core Laws

- `prime-safety` wins all conflicts.
- Fallback ban: no silent success, no broad exception swallow, no fake pass.
- Evidence first: no PASS claim without executable artifacts.
- Scratch-first: use `scratch/` for working notes/artifacts until verified.

## Mandatory Pipeline

1. Diagram
2. Webservice
3. Unit test
4. Stillwater service wiring
5. CLI/docs

No skipping steps for net-new capabilities.

## Skill Loading Order

1. `prime-safety`
2. `prime-coder`
3. domain skill(s)
4. optional modifier skill(s)

## Skill Evolution

- Use `skills/prime-skills-evolution.md` for any `skills/prime-*.md` change.
- Apply acceptance gate before adding rules.
- Serialize accepted updates to:
  - `scratch/skill-memory.jsonl`
  - `scratch/skill-memory-log.md`

## Coordination

- `scratch/todo.md` is the Claude<->Codex async task board.
- Mark work with evidence and explicit status changes.

## Evidence Minimum

For material changes provide:
- changed file list
- test or health proof
- residual risks/open issues
