# Recipes

Recipes are reusable, structured playbooks that encode multi-step engineering or analysis workflows into deterministic, verifiable protocols. Each recipe compresses hours of manual or swarm-level work into a reproducible checklist with explicit artifact contracts, checkpoints, and rollback procedures.

---

## Canonical Recipe Schema (All 10 Fields Required)

Every recipe file in this directory uses the following YAML frontmatter schema. A recipe file is **BLOCKED** if any field is missing.

```yaml
---
id: recipe.<name>                        # Unique identifier, kebab-case
version: 1.0.0                           # Semantic version
title: <human-readable title>            # Descriptive title
description: <1-2 sentences>             # What it does and why
skill_pack:                              # Skill files that power this recipe
  - <skill1>
  - <skill2>
compression_gain_estimate: "<string>"    # What work does this recipe compress and by how much
steps:                                   # Ordered list of steps (at least 3)
  - step: 1
    action: <what to do>
    artifact: <output produced>
    checkpoint: <how to verify the step succeeded>
    rollback: <what to do if this step fails>
forbidden_states:                        # Failure modes this recipe prevents
  - <FORBIDDEN_STATE_NAME>: <one-line description>
verification_checkpoint: <final end-to-end check>   # How to verify the whole recipe ran correctly
rung_target: 641 | 274177 | 65537       # Minimum verification rung this recipe targets
---
```

### Field Definitions

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique recipe identifier; must match filename (`recipe.<name>.md`) |
| `version` | Yes | Semantic version of this recipe definition |
| `title` | Yes | Human-readable name for the recipe |
| `description` | Yes | 1–2 sentences: what the recipe does and the problem it solves |
| `skill_pack` | Yes | List of skill identifiers that supply the rules/gates this recipe uses |
| `compression_gain_estimate` | Yes | How much work this recipe encodes (e.g., "3 hours → 15 minutes") |
| `steps` | Yes | Ordered steps; each must have `action`, `artifact`, `checkpoint`, `rollback` |
| `forbidden_states` | Yes | States this recipe explicitly prevents; each must have a description |
| `verification_checkpoint` | Yes | Final end-to-end check to confirm the recipe ran correctly |
| `rung_target` | Yes | Target verification rung: 641 (local), 274177 (stability), 65537 (promotion) |

### Rung Targets

- **641**: Local correctness — red/green gate + no regressions + evidence complete
- **274177**: Stability — adds seed sweep, replay stability, null edge case sweep
- **65537**: Promotion — adds adversarial sweep, refusal check, security gate, drift explanation

---

## Contribution Guidelines

Before submitting a new recipe, read `community/SCORING-RUBRIC.md` for full contribution rules. Every submission must include a self-score and evidence in the PR body.

For a step-by-step contribution walkthrough, follow `recipe.community-onboarding`.

File counts and manifest information are maintained in `MANIFEST.json` — do not hardcode counts here.

---

## Recipe Index

| Recipe ID | Title | Description |
|-----------|-------|-------------|
| `recipe.skill-completeness-audit` | Skill Completeness Audit (5/5 Binary Scorecard) | Run a 5-criterion binary scorecard across all skill files; flag any with missing FSM, forbidden states, verification ladder, null/zero handling, or output contract |
| `recipe.swarm-pipeline` | Standard Swarm Pipeline | Reusable 9-step Scout→Forecaster→Judge→Solver(parallel)→Skeptic→Podcast coordination chain with explicit artifact handoff contracts |
| `recipe.portability-audit` | Portability Audit | Detect absolute paths, private repo dependencies, host-specific artifacts, and float in verification paths across all skill and recipe files |
| `recipe.dual-fsm-detection` | Dual FSM Detection and Resolution | Detect and fix skill files with two or more State Machine sections lacking a precedence declaration — prevents non-deterministic agent behavior |
| `recipe.skill-expansion` | Skill Expansion (0 to 5/5 Binary Scorecard) | Grow a minimal skill file to full 5/5 completeness by adding FSM, forbidden states, verification ladder, null/zero policy, and output contract in dependency order |
| `recipe.community-onboarding` | Community Contribution Onboarding | Complete self-contained guide for new contributors submitting a skill, recipe, or swarm — from rubric reading through PR creation with evidence |
| `recipe.paper-from-run` | Paper Extraction from Completed Swarm Run | Extract a publishable research paper from swarm run artifacts (LESSONS.md + RECIPE.md) with typed claims [A/B/C] and sequential numbering |
| `recipe.null-zero-audit` | Null/Zero Coercion Audit | Sweep all code and skill files for null/zero coercion bugs across 5 pattern categories; outputs structured `null_checks.json` for CI integration |
