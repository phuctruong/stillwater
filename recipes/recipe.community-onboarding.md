---
id: recipe.community-onboarding
version: 1.0.0
title: Community Contribution Onboarding (Skill / Recipe / Swarm Submission)
description: Guide a new contributor through the complete process of submitting a skill, recipe, or swarm definition to the community database — from reading the scoring rubric through PR creation with score evidence attached. Requires no prior context beyond this recipe.
skill_pack:
  - prime-safety
compression_gain_estimate: "Encodes community contribution process (6 steps with evidence requirements) into a self-contained guide requiring no prior contributor context"
steps:
  - step: 1
    action: "Read community/SCORING-RUBRIC.md in full; identify the scoring criteria applicable to your contribution type (skill / recipe / swarm); note required evidence fields for your target rung (641, 274177, or 65537)"
    artifact: "Personal notes or scratch/onboarding/rubric_summary.txt — key criteria and evidence fields for your contribution type"
    checkpoint: "You can state (without looking) the 5 binary scorecard criteria for skill files and the 10 required schema fields for recipe files; if not, re-read before proceeding"
    rollback: "If SCORING-RUBRIC.md does not exist, check community/ directory for equivalents (RUBRIC.md, CRITERIA.md); if none found, emit NEED_INFO — do not proceed without rubric"
  - step: 2
    action: "Create your contribution file using the appropriate template: for skills use the skill template with all 5 required sections; for recipes use the canonical recipe schema (all 10 required fields); for swarms use the swarm definition template; save to the appropriate directory (skills/, recipes/, swarms/)"
    artifact: "New skill/recipe/swarm file at the correct repo-relative path (no absolute paths)"
    checkpoint: "File uses YAML frontmatter with all required fields; no absolute paths; no private repo dependencies; file is saved under the correct directory"
    rollback: "If template is missing, use the canonical schema from recipes/README.md (for recipes) or CLAUDE.md (for skill structure); do not improvise schema fields"
  - step: 3
    action: "Self-score your contribution against the scoring rubric: for skills, run recipe.skill-completeness-audit or manually check all 5 criteria; for recipes, verify all 10 schema fields are present and non-empty; record your self-score in scratch/onboarding/self_score.json"
    artifact: "scratch/onboarding/self_score.json — {contribution_file, type: skill|recipe|swarm, criteria_results: {}, total_score, missing_fields: []}"
    checkpoint: "Self-score is complete; missing_fields is empty (or all gaps are addressed before submission); score matches rubric criteria, not your own invented criteria"
    rollback: "If self-score reveals missing fields, return to step 2 and fix before scoring; do not submit a contribution with known missing required fields"
  - step: 4
    action: "Collect submission evidence: run the contribution once (or trace through it manually for recipe/swarm files) and capture output; record any test results, repro outputs, or example runs; save evidence to scratch/onboarding/evidence/"
    artifact: "scratch/onboarding/evidence/ — contains at minimum: one example run or trace output, self_score.json, and a one-paragraph description of what problem the contribution solves"
    checkpoint: "Evidence directory is non-empty; at least one artifact demonstrates the contribution works or is coherent; problem description is present"
    rollback: "If contribution cannot be run (e.g., swarm definition without live infrastructure), provide a dry-run trace showing what each step would produce; do not submit with empty evidence"
  - step: 5
    action: "Open a pull request: commit your contribution file and evidence to a new branch named contrib/<your-handle>/<contribution-id>; PR title format: '[contrib] <type>: <id> (score: <X>/5)'; PR body must include: self-score breakdown, problem statement, one example run or trace"
    artifact: "GitHub pull request at the repository URL with attached evidence"
    checkpoint: "PR title matches required format; PR body has self-score + problem statement + example; branch name follows contrib/<handle>/<id> convention; no sensitive data (credentials, private paths) in diff"
    rollback: "If PR creation fails (permissions, branch conflict), create the branch locally and share the diff via the community discussion channel; note that PRs are the canonical submission path"
  - step: 6
    action: "Address reviewer feedback: for each BLOCK-level comment, make the required fix and update your self-score; for WARN-level comments, either fix or provide explicit justification for leaving as-is; re-request review after addressing all comments"
    artifact: "Updated contribution file with reviewer feedback addressed; updated self_score.json if score changed"
    checkpoint: "All BLOCK-level reviewer comments are resolved before re-requesting review; no new BLOCK violations introduced during fixes; self-score updated to reflect any changes"
    rollback: "If reviewer feedback is contradictory or unclear, request clarification in PR comments before making changes; never guess at reviewer intent for BLOCK-level issues"
forbidden_states:
  - SUBMISSION_WITHOUT_SCORE: "Opening a PR without a completed self-score in the PR body — reviewers cannot evaluate contributions without a score breakdown"
  - PR_WITHOUT_EVIDENCE: "Submitting a contribution with an empty evidence directory — every contribution must demonstrate it works or is coherent"
  - ABSOLUTE_PATH_IN_SUBMISSION: "Including any absolute path in a submitted skill, recipe, or swarm file — portability is a baseline requirement for community contributions"
  - SCORE_INFLATION: "Reporting a higher self-score than the rubric criteria actually support — scoring must follow the rubric exactly, not personal assessment"
  - BLOCK_COMMENT_IGNORED: "Re-requesting review without addressing all BLOCK-level reviewer comments — BLOCK comments are hard gates, not suggestions"
verification_checkpoint: "Before submitting PR: run recipe.portability-audit on your contribution file (zero BLOCK violations required); verify PR body contains self_score.json content; verify contribution file has all required schema fields by running: python3 -c \"import yaml; d=yaml.safe_load(open('your_file.md').read().split('---')[1]); required=['id','version','title','description','skill_pack','compression_gain_estimate','steps','forbidden_states','verification_checkpoint','rung_target']; missing=[k for k in required if k not in d]; assert not missing, f'Missing: {missing}'\""
rung_target: 641
---

# Recipe: Community Contribution Onboarding

## Purpose

Provide a complete, self-contained guide for new contributors to submit a skill, recipe, or swarm definition to the community database. Designed to require no prior contributor context — everything needed is either in this recipe or in the referenced files.

## When to Use

- First time submitting a skill, recipe, or swarm
- After a long break from contributing (re-orient yourself with the current rubric)
- When reviewing another contributor's submission (use self-scoring criteria as the review rubric)

## Contribution Types

| Type | Directory | Required Schema | Min Score |
|------|-----------|-----------------|-----------|
| Skill | `skills/` | 5 binary criteria (see rubric) | 5/5 |
| Recipe | `recipes/` | 10 required schema fields | All 10 present |
| Swarm | `swarms/` | Swarm template fields | Per rubric |

## PR Title Format

```
[contrib] <type>: <contribution-id> (score: <X>/5)
```

Example: `[contrib] recipe: recipe.null-zero-audit (score: 5/5)`

## Evidence Minimum Requirements

Every PR must include in the PR body:
1. Self-score breakdown (per-criterion pass/fail)
2. Problem statement (1 paragraph: what problem does this solve?)
3. Example run or trace (shows the contribution produces useful output)

## Notes

- The scoring rubric in `community/SCORING-RUBRIC.md` is authoritative; if rubric and this recipe conflict, rubric wins
- Do not skip the self-score step even if you are confident in your contribution — self-scoring catches issues before reviewer time is spent
- BLOCK-level reviewer comments are non-negotiable; WARN-level comments require either a fix or explicit justification

---

## Three Pillars of Software 5.0 Kung Fu

| Pillar | How This Recipe Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | Each submission cycle trains the contributor to score their own work against the community rubric, building internal calibration that improves accuracy of future self-scores and reduces reviewer round-trips |
| **LEAK** (Cross-Agent Trade) | Contributor and reviewer agents exchange scoring evidence through the PR diff: contributor posts self_score.json + example run, reviewer returns BLOCK/WARN annotations — each round reduces misalignment between contributor intent and community standard |
| **LEC** (Emergent Conventions) | Enforces the community submission standard as a reusable convention: the PR title format `[contrib] <type>: <id> (score: <X>/5)` and the three-part PR body (self-score + problem statement + example run) become the universal onboarding protocol |

**Belt Level:** Yellow — demonstrates ability to participate in the community skill economy: reading rubrics, self-scoring work, and completing the evidence-backed submission loop.

**GLOW Score:** +3 per successful merged contribution (skill/recipe/swarm with 5/5 self-score and reviewer PASS on first review cycle).
