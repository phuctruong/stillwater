---
id: recipe.dual-fsm-detection
version: 1.0.0
title: Dual FSM Detection and Resolution
description: Detect and fix ambiguous dual FSM definitions within the same skill file, where two State Machine sections exist without an explicit precedence declaration, creating silent drift between versions. Failure mode discovered during prime-wishes.md audit.
skill_pack:
  - prime-safety
  - prime-coder
compression_gain_estimate: "Encodes failure mode discovered in prime-wishes.md audit (dual FSM without precedence) into a preventive 3-minute automated check"
steps:
  - step: 1
    action: "Grep all skill files for multiple occurrences of FSM-section markers in the same file: count occurrences of 'State_Machine:', 'STATE_SET:', '## State Machine', '### State Machine' per file; flag any file with count > 1"
    artifact: "scratch/dual_fsm_candidates.txt — one line per flagged file: {file, fsm_section_count, line_numbers}"
    checkpoint: "File exists; each flagged entry has file + count + line numbers of each FSM section; count field is an integer not null"
    rollback: "If grep tool unavailable, Read each skill file and scan for section markers manually; log fallback in scratch/dual_fsm_run.log"
  - step: 2
    action: "For each flagged file, check whether a precedence declaration exists: grep for 'precedence:', 'supersedes:', 'replaces:', 'ACTIVE_FSM:', 'active_fsm:' within the file; record presence/absence"
    artifact: "scratch/dual_fsm_precedence_check.json — {file, fsm_count, has_precedence: true|false, precedence_line}"
    checkpoint: "Every flagged file has an entry; has_precedence is boolean not null; files with fsm_count == 1 are excluded"
    rollback: "If precedence detection is ambiguous (partial match), classify conservatively as has_precedence=false and flag for human review"
  - step: 3
    action: "For each file with dual FSM and no precedence, analyze both FSM sections: extract STATE_SET from each, compute symmetric difference to find states present in one but not the other; emit transition conflicts"
    artifact: "scratch/dual_fsm_conflicts.json — {file, fsm_v1_states: [], fsm_v2_states: [], states_only_in_v1: [], states_only_in_v2: [], transition_conflicts: []}"
    checkpoint: "JSON is well-formed; every flagged file has an entry; state lists are sorted (deterministic output)"
    rollback: "If state extraction fails (malformed YAML), log parse error in run.log and mark file as PARSE_ERROR; do not attempt conflict analysis on unparseable files"
  - step: 4
    action: "For files with conflicts, generate fix options: Option A — add precedence declaration to make one FSM authoritative; Option B — merge FSMs into single unified definition; emit fix_options.json with recommended option per file"
    artifact: "scratch/dual_fsm_fix_options.json — {file, recommended_fix: 'PRECEDENCE'|'MERGE', rationale, draft_precedence_block}"
    checkpoint: "Every conflicted file has a recommended_fix; MERGE is only recommended if state sets are compatible (no semantic conflicts); PRECEDENCE preferred for version upgrades"
    rollback: "If fix cannot be determined, emit status=NEED_INFO with unresolved_file list; do not apply any fix without human confirmation"
  - step: 5
    action: "Apply recommended fixes: for PRECEDENCE option, add 'active_fsm: v2  # supersedes v1' header to the file's FSM section; for MERGE, produce a merged STATE_SET and TRANSITIONS block; write patched files"
    artifact: "Patched skill files with precedence declarations or merged FSM; scratch/dual_fsm_patches.diff"
    checkpoint: "After patching, re-run step 1 grep; each patched file must now either have count==1 (MERGE) or count==2 with has_precedence==true (PRECEDENCE); no new dual-FSM violations introduced"
    rollback: "If patching breaks file structure (YAML parse error after edit), revert using scratch/dual_fsm_patches.diff; log revert in run.log; escalate to human"
  - step: 6
    action: "Verify all flagged files are resolved: re-run step 1 + step 2 checks on patched files; emit dual_fsm_resolution_report.json with before/after status per file"
    artifact: "scratch/dual_fsm_resolution_report.json — {file, before: {fsm_count, has_precedence}, after: {fsm_count, has_precedence}, resolved: true|false}"
    checkpoint: "All entries have resolved==true; no file has dual FSM without precedence after patching"
    rollback: "If any file has resolved==false, re-examine that file's structure and repeat steps 4–5 with narrowed scope"
forbidden_states:
  - DUAL_FSM_WITHOUT_PRECEDENCE: "A skill file contains two or more State Machine sections with no active_fsm or precedence declaration — creates silent non-deterministic behavior"
  - SILENT_DEPRECATION: "Leaving an old FSM version in a file without marking it deprecated or superseded — leads to agents using the wrong state machine"
  - MERGE_WITH_SEMANTIC_CONFLICT: "Merging two FSMs that have incompatible transition rules for the same state without resolving the conflict first"
  - PARSE_ERROR_IGNORED: "Skipping a file that failed YAML parsing without logging the error and flagging for human review"
  - FIX_WITHOUT_RECHECK: "Applying a precedence or merge fix without re-running the detection check to confirm resolution"
verification_checkpoint: "Run detection sweep on all patched files: grep count of 'State_Machine:' per file must be either 1 (clean) or 2 with 'active_fsm:' present in same file; python3 verification: import subprocess; result = subprocess.run(['grep', '-c', 'State_Machine:', file], capture_output=True); assert result.stdout.strip() in ['1','2'] — for count==2 files, additionally assert 'active_fsm:' in open(file).read()"
rung_target: 641
---

# Recipe: Dual FSM Detection and Resolution

## Purpose

Detect skill files that contain two or more State Machine (FSM) definitions without an explicit precedence declaration. This failure mode was discovered during a prime-wishes.md audit where a v1 and v2 FSM coexisted in the same file with no indication of which was authoritative, causing downstream agents to make different (and incompatible) assumptions about valid states.

## When to Use

- After a skill file undergoes a major version upgrade (where old FSM may persist)
- As part of the skill completeness audit (recipe.skill-completeness-audit)
- When an agent reports "invalid state" errors that don't match the current skill documentation

## Root Cause of Dual FSM Drift

When a skill file is upgraded from v1 to v2:
1. Author adds new FSM section but forgets to remove or clearly deprecate the old one
2. Different agents load the file and parse different sections (depending on parser strategy)
3. FSM transitions diverge: one agent may accept states the other rejects
4. Result: non-deterministic behavior that is hard to debug

## Fix Options

| Option | When to Use | Effect |
|--------|-------------|--------|
| PRECEDENCE | FSMs are genuinely different versions | Add `active_fsm: v2` declaration; v1 remains for historical reference |
| MERGE | FSMs are meant to be complementary | Combine into single unified STATE_SET + TRANSITIONS |

## Notes

- Prefer PRECEDENCE over MERGE unless state sets are strictly compatible
- After any fix, always re-run the detection check to confirm resolution
- The DUAL_FSM_WITHOUT_PRECEDENCE forbidden state is a Lane A violation — it creates non-deterministic agent behavior

---

## Three Pillars of Software 5.0 Kung Fu

| Pillar | How This Recipe Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | Each detection run expands the agent's catalog of FSM conflict patterns — symmetric state differences and transition conflicts discovered in one skill file feed back into more precise detection heuristics for the next audit cycle |
| **LEAK** (Cross-Agent Trade) | Shares dual-FSM conflict reports (dual_fsm_conflicts.json) between the coder and skeptic agents: coder applies the PRECEDENCE or MERGE fix, skeptic re-runs detection to confirm resolution — neither can close the loop alone |
| **LEC** (Emergent Conventions) | Enforces the `active_fsm: v2  # supersedes v1` precedence declaration as a mandatory skill file convention, making FSM versioning explicit and deterministic across all agents that load skill files |

**Belt Level:** Orange — demonstrates systematic detection and resolution of non-deterministic state machine drift, a failure mode that silently corrupts agent behavior without triggering visible errors.

**GLOW Score:** +4 per successful run that resolves at least one dual-FSM conflict with a verified before/after resolution report (dual_fsm_resolution_report.json with all entries resolved==true).
