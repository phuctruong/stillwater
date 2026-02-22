---
id: recipe.triangle-audit
version: 1.0.0
title: Triangle Law Audit (Contract Stability Verification)
description: Audit all contracts in a codebase for REMIND-VERIFY-ACKNOWLEDGE (triangle law) completeness. Enumerates all contracts (interfaces, specs, skills, CI rules), checks each for all three triangle vertices, flags contracts with missing vertices, and generates a repair plan ordered by severity.
skill_pack:
  - prime-safety
  - phuc-triangle-law
  - phuc-conventions
compression_gain_estimate: "Encodes a full contract stability audit (typically 2–4 hours of manual review across interfaces, specs, skills, and CI rules) into a 30-minute systematic triangle vertex check with an ordered repair plan"
steps:
  - step: 1
    action: "Enumerate all contracts: glob for interfaces (*.d.ts, *.pyi, *.go interface files), specs (specs/*.md, ROADMAP.md, NORTHSTAR.md), skills (skills/*.md), and CI rules (.github/workflows/*.yml, Makefile targets); emit scratch/triangle_audit_contracts.json with full file list and contract type per file"
    artifact: "scratch/triangle_audit_contracts.json — {contracts: [{path: '<repo-relative>', type: '<interface|spec|skill|ci_rule>', discovered_by: '<glob pattern>'}], total_count: 0}"
    checkpoint: "contracts list is non-empty; each entry has path + type + discovered_by; total_count equals length of contracts list; no duplicates"
    rollback: "If any glob returns empty, log the empty category in scratch/triangle_audit_run.log and continue; a category with no contracts is a valid result; emit NEED_INFO only if ALL categories are empty"
  - step: 2
    action: "Check REMIND vertex for each contract: for each contract file, grep for REMIND indicators — comments/sections that declare 'what this contract does before it executes' (e.g., 'Purpose:', 'Input:', 'Pre-condition:', '## Input Contract', 'REMIND:'); record pass/fail per contract; emit scratch/triangle_audit_remind.json"
    artifact: "scratch/triangle_audit_remind.json — {results: [{path, type, remind_pass: true|false, evidence_line: '<line number or null>', indicator_found: '<matched text or null>'}]}"
    checkpoint: "Every contract from step 1 has an entry; remind_pass is a boolean (never null); evidence_line is null if remind_pass is false (not missing, just not applicable)"
    rollback: "If grep tool unavailable, fall back to Read + manual scan for each file; log tool fallback in scratch/triangle_audit_run.log; do not skip any file"
  - step: 3
    action: "Check VERIFY vertex for each contract: grep for VERIFY indicators — evidence of enforcement or checking after execution (e.g., 'Verification_Ladder:', 'RUNG_', 'checkpoint:', 'assert', 'test:', 'CI:', '## Verification', 'VERIFY:'); record pass/fail per contract"
    artifact: "scratch/triangle_audit_verify.json — {results: [{path, type, verify_pass: true|false, evidence_line: '<line number or null>', indicator_found: '<matched text or null>'}]}"
    checkpoint: "Every contract from step 1 has an entry; verify_pass is a boolean (never null); at least one entry has verify_pass == true (otherwise the codebase has no verification at all, which is a BLOCK)"
    rollback: "Same fallback as step 2; if no verification indicators found in the entire codebase, emit BLOCKED with reason 'ZERO_VERIFICATION_CONTRACTS'"
  - step: 4
    action: "Check ACKNOWLEDGE vertex for each contract: grep for ACKNOWLEDGE indicators — evidence of receipt confirmation or completion logging (e.g., 'PASS', 'stop_reason:', 'exit_code:', '## Output Contract', 'required_on_success:', 'ACKNOWLEDGE:', 'status: PASS'); record pass/fail per contract"
    artifact: "scratch/triangle_audit_acknowledge.json — {results: [{path, type, acknowledge_pass: true|false, evidence_line: '<line number or null>', indicator_found: '<matched text or null>'}]}"
    checkpoint: "Every contract from step 1 has an entry; acknowledge_pass is a boolean (never null)"
    rollback: "Same fallback as steps 2–3"
  - step: 5
    action: "Flag missing vertices: merge REMIND/VERIFY/ACKNOWLEDGE results per contract; for each contract compute triangle_score (0–3: count of present vertices); classify contracts as COMPLETE (3/3), PARTIAL (1–2/3), or BROKEN (0/3); emit scratch/triangle_audit_flags.json"
    artifact: "scratch/triangle_audit_flags.json — {contracts: [{path, type, remind_pass, verify_pass, acknowledge_pass, triangle_score: 0|1|2|3, status: 'COMPLETE|PARTIAL|BROKEN', missing_vertices: []}]}"
    checkpoint: "triangle_score equals sum(remind_pass + verify_pass + acknowledge_pass) for every entry; missing_vertices lists the vertices where pass == false; status is consistent with triangle_score (COMPLETE iff score==3, BROKEN iff score==0)"
    rollback: "If merge fails for any contract, treat the contract as BROKEN (assume all three vertices missing) and log the merge failure in scratch/triangle_audit_run.log"
  - step: 6
    action: "Generate repair plan: for each PARTIAL or BROKEN contract, emit a repair action specifying which vertex is missing and what the minimal fix is; order by severity (BROKEN first, then PARTIAL by contract type: skill > spec > interface > ci_rule); emit scratch/triangle_audit_repair_plan.json"
    artifact: "scratch/triangle_audit_repair_plan.json — {repairs: [{priority: <integer>, path, type, status, missing_vertices: [], repair_action: '<one sentence describing minimal fix>', estimated_effort: '<LOW|MED|HIGH>'}], total_broken: 0, total_partial: 0, total_complete: 0}"
    checkpoint: "repairs list is sorted by priority (ascending integer); BROKEN contracts have lower priority numbers (higher urgency) than PARTIAL; total_broken + total_partial + total_complete equals total contract count from step 1"
    rollback: "If repair plan cannot be generated for a specific contract (unclear fix), set repair_action to 'MANUAL_REVIEW_REQUIRED' and estimated_effort to 'HIGH'; do not skip the entry"
  - step: 7
    action: "Emit final audit summary: summarize the findings as a scorecard — total contracts, complete count, partial count, broken count, overall triangle health score (percent complete); emit scratch/triangle_audit_summary.json and print human-readable summary to console"
    artifact: "scratch/triangle_audit_summary.json — {total_contracts: 0, complete: 0, partial: 0, broken: 0, triangle_health_pct: 0.0, overall_verdict: '<HEALTHY|NEEDS_REPAIR|CRITICAL>', top_3_repairs: [<first 3 from repair_plan>]}"
    checkpoint: "triangle_health_pct = (complete / total_contracts) * 100; overall_verdict is HEALTHY if pct >= 80, NEEDS_REPAIR if 50–79, CRITICAL if < 50; top_3_repairs has at most 3 entries (may be fewer if fewer repairs needed)"
    rollback: "If total_contracts is 0 (no contracts found), emit NEED_INFO with message 'No contracts found; verify repo_root and glob patterns'; do not emit a summary for an empty audit"
forbidden_states:
  - AUDIT_WITHOUT_ENUMERATION: "Checking triangle vertices without first completing step 1 (full contract enumeration); partial enumeration produces misleading health scores"
  - VERTEX_ASSUMED: "Marking a vertex as present without a matching grep result or read evidence; indicator_found must be non-null for any pass == true entry"
  - PARTIAL_SCORECARD: "Emitting triangle_audit_summary.json before all three vertex checks (steps 2–4) are complete for all contracts"
  - SEVERITY_INVERSION: "Placing PARTIAL contracts before BROKEN contracts in the repair plan priority order"
  - NULL_ZERO_CONFUSION: "Treating a grep returning 0 matches as a tool error; 0 matches is a valid false result for that vertex"
  - SKIP_CATEGORY: "Omitting one of the four contract types (interface, spec, skill, ci_rule) without logging the skip with reason"
  - REPAIR_WITHOUT_EVIDENCE: "Proposing a repair action without identifying the specific missing vertex and the specific file"
  - ZERO_VERIFICATION_PASS: "Emitting PASS overall when total_broken > 0 AND status is CRITICAL"
verification_checkpoint: "Run: python3 -c \"import json; s=json.load(open('scratch/triangle_audit_summary.json')); assert s['total_contracts'] == s['complete'] + s['partial'] + s['broken']; assert abs(s['triangle_health_pct'] - (s['complete']/s['total_contracts'])*100) < 0.01\" — must exit 0; Run: python3 -c \"import json; f=json.load(open('scratch/triangle_audit_flags.json')); assert all(c['triangle_score'] == sum([c['remind_pass'],c['verify_pass'],c['acknowledge_pass']]) for c in f['contracts'])\" — must exit 0"
rung_target: 274177
---

# Recipe: Triangle Law Audit (Contract Stability Verification)

## Purpose

Systematically verify that every contract in a codebase satisfies the Triangle Law: all three vertices of REMIND, VERIFY, and ACKNOWLEDGE must be present. A contract with missing vertices is unstable — it either does not declare what it does (missing REMIND), does not check whether it worked (missing VERIFY), or does not confirm completion (missing ACKNOWLEDGE). This audit surfaces every gap and generates a prioritized repair plan.

## When to Use

- Before a release or promotion sweep (confirm contracts are stable)
- When onboarding a new contributor (audit what is explicit vs. implicit)
- After adding new skill files or interface definitions (check triangle completeness)
- As a CI gate on PRs that add or modify skill, spec, or interface files

## Triangle Law Vertices

| Vertex | Question It Answers | Typical Indicators |
|--------|--------------------|--------------------|
| REMIND | "What does this contract do before it runs?" | `Purpose:`, `Input:`, `Pre-condition:`, `## Input Contract`, `REMIND:` |
| VERIFY | "How do we check it worked?" | `Verification_Ladder:`, `RUNG_`, `checkpoint:`, `assert`, `test:`, `## Verification` |
| ACKNOWLEDGE | "How do we confirm completion?" | `PASS`, `stop_reason:`, `exit_code:`, `required_on_success:`, `ACKNOWLEDGE:` |

A COMPLETE contract has all three. A BROKEN contract has none.

## Triangle Health Score

```
triangle_health_pct = (complete_contracts / total_contracts) * 100

HEALTHY:      >= 80%  — triangle law is well-followed
NEEDS_REPAIR: 50–79%  — significant gaps; repair before promotion
CRITICAL:     < 50%   — majority of contracts are unstable; immediate repair required
```

## Contract Types Audited

| Type | Examples |
|------|---------|
| interface | `*.d.ts`, `*.pyi`, Go interface files |
| spec | `specs/*.md`, `ROADMAP.md`, `NORTHSTAR.md` |
| skill | `skills/*.md` |
| ci_rule | `.github/workflows/*.yml`, `Makefile` targets |

## Repair Plan Priority

Contracts are repaired in this order:
1. BROKEN skills (skill contracts with no vertices — highest risk)
2. BROKEN specs
3. BROKEN interfaces
4. BROKEN CI rules
5. PARTIAL skills (missing 1–2 vertices)
6. PARTIAL specs
7. PARTIAL interfaces
8. PARTIAL CI rules

## Rung Target: 274177

This recipe targets rung 274177 (stability) because:
- The audit covers multiple contract types across the full codebase
- The health score computation must be deterministic and reproducible
- The repair plan must be stable across two runs on the same repo state

Rung 641 would be insufficient for a repair plan used in promotion decisions.

## Output Artifacts

- `scratch/triangle_audit_contracts.json` — full contract enumeration
- `scratch/triangle_audit_remind.json` — REMIND vertex check results
- `scratch/triangle_audit_verify.json` — VERIFY vertex check results
- `scratch/triangle_audit_acknowledge.json` — ACKNOWLEDGE vertex check results
- `scratch/triangle_audit_flags.json` — per-contract triangle scores and status
- `scratch/triangle_audit_repair_plan.json` — prioritized repair plan
- `scratch/triangle_audit_summary.json` — overall health scorecard
- `scratch/triangle_audit_run.log` — tool fallbacks and skip reasons

## Notes

- A vertex check returning 0 matches is a clean false, not an error. Do not confuse missing indicators with a failed grep.
- The repair plan proposes minimal fixes only — add the missing vertex indicators, do not rewrite the contract.
- COMPLETE contracts require no action; they appear only in the summary count, not in the repair plan.
