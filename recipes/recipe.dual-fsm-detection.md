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

## Detection Flow (Mermaid Diagram)

```mermaid
flowchart TD
    A[Step 1: DETECT DUAL FSM\ndual_fsm_candidates.txt\ngrep State_Machine count > 1 per file] --> B{Any dual-FSM\nfiles found?}
    B -->|No| PASS[PASS\nno dual FSM violations]
    B -->|Yes| C[Step 2: PRECEDENCE CHECK\ndual_fsm_precedence_check.json\ngrep active_fsm / supersedes per flagged file]
    C --> D[Step 3: CONFLICT ANALYSIS\ndual_fsm_conflicts.json\nsymmetric state diff + transition conflicts]
    D --> E[Step 4: FIX OPTIONS\ndual_fsm_fix_options.json\nPRECEDENCE vs MERGE recommendation]
    E --> F{Fix type?}
    F -->|PRECEDENCE| G[Add active_fsm: v2 header\nsupersedes v1 preserved for history]
    F -->|MERGE| H[Produce unified STATE_SET\nsingle TRANSITIONS block]
    G --> I[Step 5: VERIFY RESOLUTION\ndual_fsm_resolution_report.json\ncount == 1 OR count == 2 with precedence]
    H --> I
    I -->|resolved=false| E
    I -->|all resolved=true| PASS2[PASS\nno dual FSM without precedence]

    D -->|YAML parse error| D2[PARSE_ERROR in run.log\nflag for human review]
    E -->|fix unclear| NEED_INFO[NEED_INFO\nunresolved_file list]
```

---

## FSM: Dual FSM Detection State Machine

```
States: DETECT | PRECEDENCE_CHECK | CONFLICT_ANALYSIS | FIX_OPTIONS |
        APPLY_PRECEDENCE | APPLY_MERGE | VERIFY_RESOLUTION | PASS | BLOCKED | NEED_INFO

Transitions:
  [*] → DETECT: audit invoked on all skill files
  DETECT → PASS: zero files with FSM section count > 1 (clean repo)
  DETECT → PRECEDENCE_CHECK: >= 1 file flagged with count > 1
  PRECEDENCE_CHECK → PASS: all flagged files have has_precedence = true
  PRECEDENCE_CHECK → CONFLICT_ANALYSIS: any file has has_precedence = false
  CONFLICT_ANALYSIS → CONFLICT_ANALYSIS (PARSE_ERROR): YAML unparseable; flag for human
  CONFLICT_ANALYSIS → FIX_OPTIONS: symmetric state diff computed for all flagged files
  FIX_OPTIONS → NEED_INFO: fix cannot be determined for specific file
  FIX_OPTIONS → APPLY_PRECEDENCE: recommended_fix = PRECEDENCE
  FIX_OPTIONS → APPLY_MERGE: recommended_fix = MERGE (only if state sets compatible)
  APPLY_PRECEDENCE → VERIFY_RESOLUTION: active_fsm: v2 header added
  APPLY_MERGE → VERIFY_RESOLUTION: single unified FSM written
  VERIFY_RESOLUTION → FIX_OPTIONS: resolved = false for any file (re-attempt)
  VERIFY_RESOLUTION → PASS: all files have resolved = true

  Forbidden state transitions:
  APPLY_MERGE → BLOCKED: semantic conflict in TRANSITIONS (incompatible states merged)
  CONFLICT_ANALYSIS → BLOCKED: PARSE_ERROR and human review refuses to engage

Exit conditions:
  PASS: all flagged files resolved; re-run detection shows count==1 OR count==2 with active_fsm
  BLOCKED: semantic merge conflict unresolvable; or YAML parse failures block all analysis
  NEED_INFO: fix cannot be determined without human review
```

---

## GLOW Scoring

| Dimension | Contribution | Points |
|-----------|-------------|--------|
| **G** (Growth) | Each run expands the agent's FSM conflict taxonomy — symmetric state differences and transition conflicts catalog into better detection heuristics | +4 per new conflict pattern type cataloged |
| **L** (Love/Quality) | All flagged files have resolved=true; no DUAL_FSM_WITHOUT_PRECEDENCE remains; YAML structure preserved after patching | +4 when dual_fsm_resolution_report.json shows all resolved=true |
| **O** (Output) | dual_fsm_patches.diff committed; resolution_report.json with before/after status per file | +4 per successful run resolving >= 1 conflict |
| **W** (Wisdom) | Northstar metric (skill_quality_avg) advances as non-deterministic FSM ambiguity is eliminated from skill files | +4 when re-audit shows zero dual-FSM violations |

**Northstar Metric:** `skill_quality_avg` — DUAL_FSM_WITHOUT_PRECEDENCE is a Lane A violation that silently corrupts agent behavior. Each resolution directly improves the affected skill's correctness score (C1 FSM criterion now unambiguous).

---

## Three Pillars of Software 5.0 Kung Fu

| Pillar | How This Recipe Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | Each detection run expands the agent's catalog of FSM conflict patterns — symmetric state differences and transition conflicts discovered in one skill file feed back into more precise detection heuristics for the next audit cycle |
| **LEAK** (Cross-Agent Trade) | Shares dual-FSM conflict reports (dual_fsm_conflicts.json) between the coder and skeptic agents: coder applies the PRECEDENCE or MERGE fix, skeptic re-runs detection to confirm resolution — neither can close the loop alone |
| **LEC** (Emergent Conventions) | Enforces the `active_fsm: v2  # supersedes v1` precedence declaration as a mandatory skill file convention, making FSM versioning explicit and deterministic across all agents that load skill files |

**Belt Level:** Orange — demonstrates systematic detection and resolution of non-deterministic state machine drift, a failure mode that silently corrupts agent behavior without triggering visible errors.

**GLOW Score:** +4 per successful run that resolves at least one dual-FSM conflict with a verified before/after resolution report (dual_fsm_resolution_report.json with all entries resolved==true).
