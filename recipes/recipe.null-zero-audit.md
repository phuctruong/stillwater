---
id: recipe.null-zero-audit
version: 1.0.0
title: Null/Zero Coercion Audit
description: Sweep all code and skill files for null/zero coercion bugs — null treated as 0, empty list treated as null, implicit None defaults, and len() comparisons without null checks. Motivated by audit catching 8 such locations in prime-wishes.md.
skill_pack:
  - prime-safety
  - prime-coder
compression_gain_estimate: "Encodes null/zero audit (caught [] vs null confusion at 8 locations in prime-wishes.md) into an automated 10-minute grep sweep with structured null_checks.json output"
steps:
  - step: 1
    action: "Grep all Python files for implicit None/null defaults that silently treat None as zero or empty: patterns 'or []', 'or {}', 'or 0', '= None  #', 'if not x:' where x could be 0 or empty list; emit hits to scratch/null_audit_implicit_defaults.txt"
    artifact: "scratch/null_audit_implicit_defaults.txt — one line per hit: {file:line:matched_text:pattern}"
    checkpoint: "File exists; each hit has file + line number + matched text; patterns searched include both 'or 0' and 'or []' forms; grep used repo-relative paths only"
    rollback: "If grep tool unavailable, Read each Python file and scan manually using line-by-line inspection; log fallback in scratch/null_audit_run.log"
  - step: 2
    action: "Grep all Python files for len() comparisons without preceding null check: pattern 'len(x)' where x is not guarded by 'if x is not None' or 'if x:' in the same or immediately preceding statement; emit hits to scratch/null_audit_len_comparisons.txt"
    artifact: "scratch/null_audit_len_comparisons.txt — one line per hit"
    checkpoint: "File exists; hits are from code paths where len() could receive None (not from tests asserting on known-non-null values)"
    rollback: "If context analysis is not possible with grep, flag all len() calls in non-test code and annotate each as NEEDS_HUMAN_REVIEW; log in run.log"
  - step: 3
    action: "Grep all Python and YAML files for '== 0' comparisons where the intent may be '== null': specifically look for patterns like 'count == 0', 'result == 0', 'score == 0' in code that also handles None elsewhere in the same function/block; emit hits to scratch/null_audit_zero_comparisons.txt"
    artifact: "scratch/null_audit_zero_comparisons.txt — one line per hit"
    checkpoint: "File exists; each hit includes the surrounding context (2 lines before and after) to enable human judgment; no hits from test assertion files unless flagged as WARN"
    rollback: "If context extraction fails, emit the raw line match without context and annotate as NEEDS_CONTEXT_REVIEW"
  - step: 4
    action: "Grep all Python and YAML skill files for implicit empty string coercions: patterns 'or \"\"', 'or \\'\\'' (empty string as default), 'if not s:' where s is a string field that could distinguish empty from absent; emit hits to scratch/null_audit_empty_string.txt"
    artifact: "scratch/null_audit_empty_string.txt — one line per hit"
    checkpoint: "File exists; hits from skill YAML files are given higher severity (WARN→BLOCK) than hits from display code"
    rollback: "Same fallback as step 1"
  - step: 5
    action: "Grep skill YAML files specifically for the [] vs null confusion pattern: fields that use empty list '[]' where null (absent field) is semantically different; check evidence schema fields, forbidden_states lists, step artifacts lists; emit hits to scratch/null_audit_yaml_list_null.txt"
    artifact: "scratch/null_audit_yaml_list_null.txt — one line per hit: {file:line:field_name:matched_value}"
    checkpoint: "File exists; each hit identifies the specific YAML field name where [] vs null ambiguity exists; prime-wishes.md and similar complex skill files are included in sweep"
    rollback: "If YAML parsing fails for a file, flag the file as PARSE_ERROR in run.log and skip it; do not emit false-positive hits from unparseable files"
  - step: 6
    action: "Merge all 5 sweep results; classify each hit as BLOCK (coercion in critical path), WARN (coercion in non-critical path), or INFO (acceptable use pattern); emit null_checks.json with {file, line, pattern, category, severity, fix_suggestion}"
    artifact: "scratch/null_checks.json — structured report with all hits, severity classifications, and fix suggestions"
    checkpoint: "JSON is well-formed; every entry has file + line + pattern + severity + fix_suggestion; no entry has null for severity; BLOCK entries each have a concrete fix suggestion"
    rollback: "If merge produces duplicate entries (same file+line from multiple patterns), deduplicate keeping the highest severity; log deduplication count in run.log"
  - step: 7
    action: "Emit audit summary: total hits by category and severity; list all BLOCK violations with file + line + fix; write null_audit_summary.txt; emit null_checks.json path for CI integration"
    artifact: "scratch/null_audit_summary.txt — human-readable summary; scratch/null_checks.json — machine-parseable report"
    checkpoint: "Summary includes counts for all 5 categories; BLOCK violations each have a one-line fix; null_checks.json path is printed to stdout for CI integration"
    rollback: "If summary cannot be written, output null_checks.json path directly and instruct caller to inspect; do not suppress the BLOCK violation list"
forbidden_states:
  - AUDIT_WITH_FLOAT_COMPARISON: "Using float comparison (e.g., value == 0.0 or value < 0.001) to detect null/zero boundaries — null/zero audit must use exact integer or boolean checks"
  - NULL_ZERO_CONFUSION_UNREPORTED: "Finding a null/zero coercion pattern and classifying it as INFO without explicit justification — coercions in critical paths are always at minimum WARN"
  - IMPLICIT_NULL_DEFAULT: "Treating a 0-hit grep result as a null/tool-error rather than a clean-pass result — zero hits is a valid outcome, not an error"
  - SKIP_YAML_SWEEP: "Running only Python file sweeps without also checking YAML skill files — the [] vs null confusion pattern appears in YAML as frequently as in Python"
  - SEVERITY_DOWNGRADE_WITHOUT_JUSTIFICATION: "Reclassifying a BLOCK violation as WARN or INFO without recording an explicit justification in null_checks.json"
verification_checkpoint: "Run: python3 -c \"import json; d=json.load(open('scratch/null_checks.json')); assert all('severity' in e for e in d); assert all('fix_suggestion' in e for e in d); blocks=[e for e in d if e['severity']=='BLOCK']; print(f'BLOCK violations: {len(blocks)}')\" — must exit 0; examine all BLOCK violations before closing audit"
rung_target: 641
---

# Recipe: Null/Zero Coercion Audit

## Purpose

Sweep code and skill files for null/zero coercion bugs. These bugs occur when code silently treats `None`/`null` as `0`, `[]`, `""`, or when `len()` is called on a potentially-null value without a preceding null check. The recipe was motivated by finding 8 such locations in a single `prime-wishes.md` audit.

## When to Use

- Before any skill promotion (null/zero handling is a rung 641 requirement)
- After adding new evidence schema fields to a skill (new list fields are common sources of [] vs null confusion)
- When an agent reports unexpected behavior at edge cases involving empty or missing inputs

## 5 Sweep Categories

| # | Category | Example Pattern | Baseline Severity |
|---|----------|-----------------|-------------------|
| 1 | Implicit None defaults | `x = func() or []` | WARN |
| 2 | len() without null guard | `if len(results) > 0:` (no prior None check) | WARN |
| 3 | == 0 masking null | `if count == 0:` in null-capable context | WARN |
| 4 | Empty string coercion | `name = input or ""` | INFO→WARN |
| 5 | YAML [] vs null | `forbidden_states: []` vs absent field | BLOCK |

## Null vs Zero Distinction

- **null/None**: pre-systemic absence — the field was never set; operations on it are undefined
- **zero/[]**: lawful boundary value — the field is set and its value is the zero element

Treating null as zero (or `[]` as absent) creates hidden state bugs where an empty list is interpreted as "field not defined" and an undefined field is interpreted as "empty list."

## Output

- `scratch/null_checks.json` — machine-parseable report for CI integration
- `scratch/null_audit_summary.txt` — human-readable summary with fix guidance

## Notes

- A grep returning zero hits is a clean PASS for that category — never treat it as a tool error
- YAML skill files deserve special attention: the `forbidden_states: []` pattern (empty list) vs absent `forbidden_states` key is the most common null/zero confusion in skill files
- The `software5.0-paradigm` skill pack is not listed here but may be relevant for swarm-level null propagation analysis

---

## Three Pillars of Software 5.0 Kung Fu

| Pillar | How This Recipe Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | Each audit run expands the agent's pattern library of null/zero coercions — new violation types discovered in one sweep (e.g., a novel YAML `[]`-vs-null pattern) are added to the grep pattern set, improving detection coverage in future runs |
| **LEAK** (Cross-Agent Trade) | Shares the null_checks.json report between the coder and skeptic agents: coder applies the fix suggestions from BLOCK violations, skeptic verifies the fixes do not introduce new coercions — the audit output is the shared contract between them |
| **LEC** (Emergent Conventions) | Enforces the null≠zero convention across all skill and code files: by flagging `forbidden_states: []` as a BLOCK violation, the recipe makes the distinction between absent field and empty list a repo-wide invariant rather than a per-author judgment call |

**Belt Level:** Orange — demonstrates the discipline to distinguish pre-systemic absence (null) from lawful boundary values (zero/empty), a distinction that prevents entire classes of hidden state bugs at the boundary of skill and code.

**GLOW Score:** +4 per successful audit run with null_checks.json emitted, all BLOCK violations addressed, and a clean re-sweep confirming zero new coercions introduced by the fixes.
