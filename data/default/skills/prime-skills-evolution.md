<!-- QUICK LOAD
SKILL: prime-skills-evolution v1.1.0
PURPOSE: Central law for evolving prime skills with Software 5.0 constraints.
TRIGGER: Any update to skills/prime-*.md or retroactive rule migration.
GATE: generalizability>=4, specificity<=2, glow_delta>=+10, evidence-backed.
FLOW: 4W+H -> evaluate -> apply minimal diff -> serialize -> report token delta.
SERIALIZE: scratch/skill-memory.jsonl + scratch/skill-memory-log.md.
-->
name: prime-skills-evolution
version: 1.1.0
authority: 65537
status: STABLE

# prime-skills-evolution

## Software 5.0 Contract

- Follow `DREAM -> FORECAST -> DECIDE -> ACT -> VERIFY`.
- Use 4W+H before rule acceptance: `WHY WHAT WHEN WHO HOW`.
- Keep fallback ban: no silent pass/fake success/broad swallow.
- Prefer reusable law over repo-specific workaround.
- Keep diffs minimal and token-aware.

## Acceptance Gate

Accept only if all pass:
- `generalizability_score >= 4/5`
- `project_specificity_score <= 2/5`
- `predicted_glow_delta >= +10`
- backed by a real failure, repeated gap, or verified contract miss
- does not weaken existing hard gates

## Anti-Overfit Gate

Reject if any true:
- machine/user-specific behavior is presented as universal law
- hardcoded one-repo convention without transfer value
- prose confidence with no machine-checkable evidence

## Token Policy

- Do not duplicate protocol text across multiple prime skills.
- Keep shared policy here; keep domain skills to short rule references.
- Remove comments that do not change behavior or safety.

## Canonical Rule Registry

- `S5-EVO-CODER-01` `ENGINE_STATE_STABILITY`:
  never reset long-lived engine state per request unless reset/session key explicitly changes.
- `S5-EVO-CODER-02` `SCOPED_REGRESSION_ISOLATION`:
  if full suite has unrelated red tests, report touched-scope green evidence + unrelated red list.
- `S5-EVO-API-01` `PROVIDER_TEST_STRICT_MODE`:
  provider test endpoints must support strict mode (no fallback masking).
- `S5-EVO-API-02` `HEALTH_ENDPOINT_CONTRACT`:
  expose stable `/api/health` when orchestration depends on it.
- `S5-EVO-TEST-01` `STATE_PERSISTENCE_REGRESSION_TEST`:
  add repeated-call tests for aggregate state persistence.
- `S5-EVO-SAFETY-01` `EPHEMERAL_SECRET_HYGIENE`:
  remove temporary secrets before final seal unless user says keep.
- `S5-EVO-SAFETY-02` `SECRET_LEAK_PROOF`:
  run plaintext leak scan after secret-related verification.
- `S5-EVO-OPS-01` `EXTERNAL_RUNNING_TOLERANCE`:
  treat healthy pre-existing services as external-running, not startup failure.
- `S5-EVO-OPS-02` `LIFECYCLE_CHAIN_PROOF`:
  verify `start -> health -> status -> stop` in one chained proof.

## Serialization Contract

For every accepted update append JSONL row to `scratch/skill-memory.jsonl` with:
- `timestamp`
- `change_id`
- `skill`
- `rule_ids`
- `what_changed`
- `why_generalizable`
- `generalizability_score`
- `project_specificity_score`
- `glow_delta`
- `token_delta_estimate`
- `evidence_ref`
- `status`

Also append short summary to `scratch/skill-memory-log.md`.

## Output Contract

Report:
- files changed
- accepted/rejected updates
- token delta estimate
- residual risks
