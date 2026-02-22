---
id: recipe.skill-completeness-audit
version: 1.0.0
title: Skill Completeness Audit (5/5 Binary Scorecard)
description: Run a 5/5 binary scorecard across all skill files checking for FSM presence, forbidden states, verification ladder, null/zero handling, and output contract. Flags any skill file that fails one or more criteria.
skill_pack:
  - prime-safety
  - prime-coder
compression_gain_estimate: "Encodes 2 hours of swarm-level skill auditing into a 15-minute automated binary scorecard sweep"
steps:
  - step: 1
    action: "Enumerate all skill files by globbing skills/*.md and skills/**/*.md; record file list in scratch/skill_audit_filelist.txt"
    artifact: "scratch/skill_audit_filelist.txt — sorted list of all skill file paths"
    checkpoint: "File list is non-empty; each entry is a repo-relative path resolving under skills/"
    rollback: "If glob returns empty, widen to *.yaml and *.yml; if still empty, emit NEED_INFO with missing skills directory note"
  - step: 2
    action: "For each skill file, check criterion C1: FSM present — grep for 'State_Machine:' or 'STATE_SET:' or '## State Machine'; record pass/fail per file"
    artifact: "scratch/skill_audit_c1.json — {file, c1_pass: true|false, evidence_line}"
    checkpoint: "JSON is well-formed; every enumerated file has an entry"
    rollback: "If grep tool unavailable, fall back to Read + manual scan; log tool fallback in scratch/skill_audit_run.log"
  - step: 3
    action: "For each skill file, check criterion C2: forbidden states defined — grep for 'FORBIDDEN_STATES:' or 'Forbidden_States:' or 'forbidden_states:'; record pass/fail"
    artifact: "scratch/skill_audit_c2.json — {file, c2_pass: true|false, evidence_line}"
    checkpoint: "Every file has an entry; no entry has null for c2_pass"
    rollback: "Same fallback as step 2"
  - step: 4
    action: "For each skill file, check criterion C3: verification ladder present — grep for 'Verification_Ladder:' or 'RUNG_' or 'verification_rung'; record pass/fail"
    artifact: "scratch/skill_audit_c3.json — {file, c3_pass: true|false, evidence_line}"
    checkpoint: "Every file has an entry"
    rollback: "Same fallback as step 2"
  - step: 5
    action: "For each skill file, check criterion C4: null/zero handling — grep for 'Null_vs_Zero' or 'null_handling' or 'NULL_ZERO' or 'null_check'; record pass/fail"
    artifact: "scratch/skill_audit_c4.json — {file, c4_pass: true|false, evidence_line}"
    checkpoint: "Every file has an entry"
    rollback: "Same fallback as step 2"
  - step: 6
    action: "For each skill file, check criterion C5: output contract — grep for 'Output_Contract:' or 'output_contract' or 'required_on_success'; record pass/fail"
    artifact: "scratch/skill_audit_c5.json — {file, c5_pass: true|false, evidence_line}"
    checkpoint: "Every file has an entry"
    rollback: "Same fallback as step 2"
  - step: 7
    action: "Merge C1–C5 results per file; compute total score (0–5); emit scorecard as scratch/skill_audit_scorecard.json with fields: {file, c1, c2, c3, c4, c5, total, pass}"
    artifact: "scratch/skill_audit_scorecard.json — one entry per skill file with all 5 criteria + total"
    checkpoint: "JSON parses; every entry has all 6 fields (c1–c5, total); total == sum(c1..c5); pass == (total == 5)"
    rollback: "If merge fails, re-run individual criterion files and merge manually; do not emit partial scorecard"
  - step: 8
    action: "Flag all failing skills (total < 5) to stdout; list missing criteria per file; emit summary line: 'X/Y skills passed 5/5'"
    artifact: "Console output + scratch/skill_audit_failures.txt listing file + missing criteria"
    checkpoint: "Summary line present; failure file lists only skills with total < 5"
    rollback: "If output fails, write raw scorecard.json path to console and instruct caller to inspect directly"
forbidden_states:
  - AUDIT_WITHOUT_CRITERIA: "Scanning skill files without all 5 criteria defined before scan begins"
  - PASS_WITH_MISSING_SECTIONS: "Reporting a skill as 5/5 when any criterion grep returned no match"
  - AUDIT_PARTIAL: "Emitting scorecard before all skill files have been checked for all 5 criteria"
  - SILENT_FILE_SKIP: "Omitting a skill file from the audit without logging the skip reason"
  - NULL_ZERO_CONFUSION: "Treating a grep with 0 results as null/error rather than a clean false"
verification_checkpoint: "Run: grep -c 'c1_pass' scratch/skill_audit_scorecard.json | verify count equals number of skill files; run: python3 -c \"import json; d=json.load(open('scratch/skill_audit_scorecard.json')); assert all(e['total']==sum([e['c1'],e['c2'],e['c3'],e['c4'],e['c5']]) for e in d)\" — both checks must pass"
rung_target: 641
---

# Recipe: Skill Completeness Audit (5/5 Binary Scorecard)

## Purpose

Run a deterministic, automated 5-criterion binary scorecard across every skill file in the repository. Each skill is graded PASS (5/5) or flagged with the specific missing sections. Designed to replace 2 hours of manual swarm audit with a 15-minute automated sweep.

## When to Use

- Before a skill promotion sweep (to ensure all skills meet rung 641 minimums)
- After adding new skill files (to catch missing sections early)
- As a CI gate on PRs that touch `skills/`

## 5 Criteria (Binary: 0 or 1 each)

| # | Criterion | Detection Pattern |
|---|-----------|-------------------|
| C1 | FSM present | `State_Machine:` or `STATE_SET:` or `## State Machine` |
| C2 | Forbidden states defined | `FORBIDDEN_STATES:` or `forbidden_states:` |
| C3 | Verification ladder | `Verification_Ladder:` or `RUNG_` or `verification_rung` |
| C4 | Null/zero handling | `Null_vs_Zero` or `NULL_ZERO` or `null_handling` |
| C5 | Output contract | `Output_Contract:` or `required_on_success` |

## Output Artifacts

- `scratch/skill_audit_scorecard.json` — machine-parseable per-file scorecard
- `scratch/skill_audit_failures.txt` — list of failing files with missing criteria
- `scratch/skill_audit_run.log` — tool call log and any fallback events

## Notes

- All grep patterns are case-insensitive anchored to field names; literal string matches only
- A score of 0 results from a grep with zero matches — this is NOT an error; it is a clean false
- Do not conflate "grep returned empty" (zero hits, valid result) with "grep failed" (tool error)

---

## Three Pillars of Software 5.0 Kung Fu

| Pillar | How This Recipe Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | Each audit run produces a scorecard that reveals which criteria are most commonly missing across the skill corpus — tracking failure patterns over time guides skill authors toward the sections that the community most frequently omits, improving the average skill quality with each audit cycle |
| **LEAK** (Cross-Agent Trade) | The skill_audit_scorecard.json is a shared artifact between the auditor agent and the expansion agent: the auditor identifies gaps (C1–C5 failures), the expander fills them using recipe.skill-expansion — the scorecard is the handoff contract that makes this division of labor precise |
| **LEC** (Emergent Conventions) | Enforces the 5-criterion binary scorecard as the community-wide skill completeness standard: FSM + forbidden states + verification ladder + null/zero handling + output contract become the non-negotiable structural conventions that every skill must satisfy before promotion |

**Belt Level:** Yellow — demonstrates the ability to assess any skill file against a structured rubric, produce a machine-parseable scorecard, and identify specific gaps rather than making vague quality judgments.

**GLOW Score:** +3 per successful audit run where skill_audit_scorecard.json is emitted with every file checked, total == sum(C1..C5) verified, and the summary line X/Y skills passed 5/5 is printed.
