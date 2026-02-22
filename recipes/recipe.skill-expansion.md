---
id: recipe.skill-expansion
version: 1.0.0
title: Skill Expansion from 0 to 5/5 Binary Scorecard
description: Grow a minimal or partial skill file from 0→5/5 on the binary scorecard by systematically adding FSM with all states and transitions, forbidden states with detectors, verification ladder rungs, null/zero policy, and output contract. Encodes 9-skill expansion effort into a repeatable 45-minute structured protocol.
skill_pack:
  - prime-safety
  - prime-coder
compression_gain_estimate: "Encodes skill expansion work (9 skills x ~2 hours each) into a repeatable 45-minute structured protocol with scoring gates at each step"
steps:
  - step: 1
    action: "Score the current skill file against all 5 criteria using recipe.skill-completeness-audit logic; record baseline score (0–5) and list of missing criteria (C1–C5); write baseline_score.json to scratch/"
    artifact: "scratch/expansion/baseline_score.json — {file, c1, c2, c3, c4, c5, total, missing_criteria: []}"
    checkpoint: "Baseline score is recorded; missing_criteria list is accurate; if total is already 5, expansion is not needed — emit status=PASS and stop"
    rollback: "If scoring tool fails, manually inspect the file for all 5 section headers and record findings; do not proceed without a recorded baseline"
  - step: 2
    action: "If C1 (FSM) is missing: draft a minimal FSM block with STATE_SET (at minimum: INIT, INTAKE, NULL_CHECK, PLAN, PATCH, TEST, EVIDENCE_BUILD, EXIT_PASS, EXIT_NEED_INFO, EXIT_BLOCKED), TRANSITIONS covering all states, and INPUT_ALPHABET; insert after the skill header section"
    artifact: "Draft FSM block in scratch/expansion/draft_fsm.yaml; updated skill file with FSM section"
    checkpoint: "FSM has STATE_SET with at least 9 states; TRANSITIONS covers every state as a source at least once; no orphan states (states in STATE_SET not reachable from INIT)"
    rollback: "If FSM insertion breaks YAML structure, revert to pre-insertion file; re-draft FSM block and validate YAML before reinserting"
  - step: 3
    action: "If C2 (forbidden states) is missing: derive at least 5 forbidden states from the skill's domain; each must have a one-line description of the failure mode it prevents; insert FORBIDDEN_STATES block under FSM section"
    artifact: "FORBIDDEN_STATES block added to skill file; scratch/expansion/draft_forbidden_states.yaml"
    checkpoint: "At least 5 forbidden states listed; each has a name in SCREAMING_SNAKE_CASE and a description; no duplicate names"
    rollback: "If fewer than 5 natural forbidden states exist for this skill domain, derive generic safety forbidden states from prime-coder: UNWITNESSED_PASS, SILENT_RELAXATION, NULL_ZERO_CONFUSION, STACKED_SPECULATIVE_PATCHES, HIDDEN_IO"
  - step: 4
    action: "If C3 (verification ladder) is missing: add Verification_Rung_Target_Policy block declaring the skill's default rung target (641 for local correctness, 274177 if iterative methods present, 65537 if promotion/security); add rung requirements mapping to the skill's evidence schema"
    artifact: "Verification_Rung_Target_Policy block added to skill file"
    checkpoint: "Block specifies rung_target; lists at minimum 3 requirements for that rung; requirements reference artifacts the skill actually produces"
    rollback: "If rung cannot be determined, default to 641 with a note that higher rungs require explicit declaration; do not leave rung_target unset"
  - step: 5
    action: "If C4 (null/zero handling) is missing: add Null_vs_Zero_Policy block with explicit null handling rules; add null_checks_performed field to the skill's evidence schema; add NULL_ZERO_CONFUSION to forbidden states if not already present"
    artifact: "Null_vs_Zero_Policy block added; null_checks.json added to evidence schema if present"
    checkpoint: "Policy block has: null definition, zero definition, null_handling_rules list (at least 3 rules), fail_closed_on_null_in_critical_path: true"
    rollback: "If evidence schema does not exist in the skill, add minimal schema section alongside null policy; never add null policy without corresponding enforcement rule"
  - step: 6
    action: "If C5 (output contract) is missing: add Output_Contract block with required_on_success (status: PASS + include list) and required_on_failure (status: NEED_INFO_or_BLOCKED + include list); add structured_refusal_format with required_keys"
    artifact: "Output_Contract block added to skill file"
    checkpoint: "Block has required_on_success with status and include list; required_on_failure with status and include list; structured_refusal_format with at least 4 required keys"
    rollback: "If output contract conflicts with existing output sections, merge rather than duplicate; if merge is ambiguous, flag for human review and emit NEED_INFO"
  - step: 7
    action: "Re-score the expanded skill file against all 5 criteria; compute new score; compare to baseline; verify score improved by at least (5 - baseline) points (i.e., all missing criteria are now present)"
    artifact: "scratch/expansion/final_score.json — {file, c1, c2, c3, c4, c5, total, improvement: (total - baseline)}"
    checkpoint: "final_score.total == 5; improvement == (5 - baseline_score.total); no previously passing criteria regressed to failing"
    rollback: "If any criterion regressed or score is still < 5, identify remaining missing criteria and repeat the relevant step; do not emit PASS until total == 5"
  - step: 8
    action: "Write expansion summary to scratch/expansion/expansion_report.json: record baseline, final score, steps taken, sections added, any sections that required human review; flag as ready for skill-completeness-audit re-run"
    artifact: "scratch/expansion/expansion_report.json — {skill_file, baseline_score, final_score, steps_taken, sections_added, human_review_required: true|false}"
    checkpoint: "Report is well-formed JSON; final_score == 5; if human_review_required is true, list the specific items requiring review"
    rollback: "If report cannot be written (disk/permission error), emit summary to console and log path to scratch/expansion/expansion_run.log"
forbidden_states:
  - EXPANSION_WITHOUT_SCORING: "Adding sections to a skill file without first recording a baseline score — cannot verify improvement without a baseline"
  - FAKE_FSM_WITHOUT_TRANSITIONS: "Adding a STATE_SET list without corresponding TRANSITIONS block — an FSM without transitions is not an FSM"
  - REGRESSED_CRITERION: "A criterion that passed at baseline fails after expansion — expansion must be strictly additive, never harmful"
  - ORPHAN_STATE: "A state in STATE_SET that is not reachable from INIT via any transition path — creates unreachable dead zones in the FSM"
  - RUNG_TARGET_UNSET: "Completing expansion without setting a rung_target in the verification ladder section — every skill must declare its minimum verification strength"
  - PASS_BEFORE_RESCORE: "Emitting expansion PASS without running step 7 rescore — improvement must be verified, not assumed"
verification_checkpoint: "Run recipe.skill-completeness-audit on the expanded file: all 5 criteria (C1–C5) must return pass; additionally verify YAML structure: python3 -c \"import yaml; yaml.safe_load(open('skills/target_skill.md').read().split('---')[1])\" must exit 0 (or equivalent for non-YAML sections)"
rung_target: 641
---

# Recipe: Skill Expansion (0 to 5/5 Binary Scorecard)

## Purpose

Systematically grow a minimal or partial skill file to full 5/5 completeness by adding each missing section in dependency order. This recipe was designed after observing that 9 skills each required approximately 2 hours of manual expansion work — the same 5 sections were missing in most cases.

## When to Use

- When recipe.skill-completeness-audit flags a skill with score < 5
- When creating a new skill file from scratch
- When inheriting a skill file from another project that lacks the standard section set

## Section Dependency Order

The 5 criteria should be added in this order when multiple are missing:

1. **FSM (C1)** — foundational; forbidden states and ladder depend on it
2. **Forbidden States (C2)** — extends the FSM with negative constraints
3. **Verification Ladder (C3)** — declares what evidence the skill produces
4. **Null/Zero Policy (C4)** — scopes the input handling rules
5. **Output Contract (C5)** — defines what the skill emits on success/failure

## Key Rules

- Always score before and after; expansion must show measurable improvement
- Never leave orphan states in the FSM (states with no path from INIT)
- If fewer than 5 natural forbidden states exist, use the 5 generic safety states from prime-coder as a baseline
- Re-run recipe.skill-completeness-audit after expansion to confirm 5/5

## Notes

- This recipe is idempotent: if a skill already scores 5/5 at step 1, it exits cleanly
- The 45-minute estimate assumes one person working through all 5 steps sequentially; parallel section drafting can reduce this to ~20 minutes

---

## Three Pillars of Software 5.0 Kung Fu

| Pillar | How This Recipe Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | The before/after scoring gate (baseline_score.json → final_score.json) makes every expansion measurable — improvement is not assumed but verified, and the pattern of which sections required human review accumulates into better expansion heuristics for the next skill |
| **LEAK** (Cross-Agent Trade) | The expansion report (expansion_report.json) is a handoff artifact from the expander agent to the reviewer: it documents what was added, what score was achieved, and what items require human review — enabling a reviewer to verify the expansion without re-reading the full skill file |
| **LEC** (Emergent Conventions) | Enforces the section dependency order (FSM → forbidden states → verification ladder → null/zero policy → output contract) as a skill construction convention: every skill built through this recipe follows the same structural spine, making cross-skill navigation and auditing predictable |

**Belt Level:** Orange — demonstrates the ability to take a partial or skeletal skill file and systematically grow it to full 5/5 completeness without regressing previously passing criteria or introducing orphan states in the FSM.

**GLOW Score:** +5 per successful skill expansion from below 5/5 to exactly 5/5, confirmed by recipe.skill-completeness-audit rescore, with expansion_report.json showing baseline < 5 and final_score == 5.
