---
id: recipe.portability-audit
version: 1.0.0
title: Portability Audit (Absolute Paths, Private Deps, Float in Verification)
description: Detect absolute paths, private repository dependencies, host-specific environment artifacts, and float literals in verification paths across all skill and recipe files. Found 4 portability failures in one audit session — encodes that work into a 5-minute grep sweep.
skill_pack:
  - prime-safety
  - prime-coder
compression_gain_estimate: "Encodes portability failure detection (found 4 violations in one audit session) into a 5-minute automated grep sweep"
steps:
  - step: 1
    action: "Grep all skill and recipe files for absolute path patterns: patterns '/home/', '/Users/', '/root/', '/opt/', '/var/', '/etc/', '/tmp/' appearing in non-comment YAML or Markdown fields; emit hits to scratch/portability_abs_paths.txt"
    artifact: "scratch/portability_abs_paths.txt — one line per hit: {file:line:matched_text}"
    checkpoint: "File exists (may be empty if no violations); each hit line has file + line number + matched text; grep used repo-relative paths only"
    rollback: "If grep tool unavailable, use Read on each file and scan manually; log fallback in scratch/portability_run.log"
  - step: 2
    action: "Grep all skill and recipe files for private repository dependency patterns: 'git+ssh://', 'git+https://.*private', internal hostname patterns (e.g., '.internal', '.corp', '.local' in URLs), hardcoded IP addresses; emit hits to scratch/portability_private_deps.txt"
    artifact: "scratch/portability_private_deps.txt — one line per hit: {file:line:matched_text}"
    checkpoint: "File exists; each hit includes file + line + pattern that matched"
    rollback: "Same fallback as step 1"
  - step: 3
    action: "Grep all skill and recipe files for host-specific environment variable references that hardcode hostnames or user-specific paths: '$HOME', '$USER', '$HOSTNAME', 'os.environ[\"HOME\"]', 'Path.home()'; emit hits to scratch/portability_host_env.txt"
    artifact: "scratch/portability_host_env.txt — one line per hit"
    checkpoint: "File exists; distinguish between $HOME in example comments (INFO) vs $HOME used as a literal config value (VIOLATION)"
    rollback: "If ambiguous, classify conservatively as VIOLATION and note in run.log for human review"
  - step: 4
    action: "Grep all Python and shell files under skills/ and recipes/ for float literals in verification-path code: patterns like '== 0.0', '< 0.1', '> 1e-', '/ 100.0', 'math.isclose', 'np.allclose', 'pytest.approx'; emit hits to scratch/portability_float_verification.txt"
    artifact: "scratch/portability_float_verification.txt — one line per hit"
    checkpoint: "File exists; hits are from code files only (not YAML comments or display-only strings)"
    rollback: "If hit is in display-only path (e.g., print() or f-string for logging), reclassify as INFO; exact arithmetic required only in comparison/hash paths"
  - step: 5
    action: "Merge all four violation files; classify each hit as BLOCK (must fix before promotion), WARN (should fix), or INFO (acceptable); emit portability_report.json with {file, line, pattern, category, severity}"
    artifact: "scratch/portability_report.json — list of all violations with severity classification"
    checkpoint: "JSON is well-formed; every entry has file + line + pattern + severity; no entry has null severity"
    rollback: "If merge produces duplicate entries (same file+line), deduplicate keeping the highest severity classification"
  - step: 6
    action: "Emit summary: count of BLOCK + WARN + INFO violations per category; list all BLOCK violations with fix guidance; write portability_summary.txt"
    artifact: "scratch/portability_summary.txt — human-readable summary with counts and BLOCK-level fix guidance"
    checkpoint: "Summary includes counts for all 4 categories (abs_paths, private_deps, host_env, float_verification); BLOCK violations each have a one-line fix suggestion"
    rollback: "If summary fails, output portability_report.json path directly and instruct caller to inspect"
forbidden_states:
  - AUDIT_PARTIAL: "Emitting portability_report.json before all 4 grep sweeps (steps 1–4) have completed"
  - PASS_WITH_ABSOLUTE_PATH: "Classifying a skill or recipe file as portable when it contains an absolute path in a non-comment config field"
  - FLOAT_IN_VERIFICATION_IGNORED: "Finding a float literal in a verification comparison path and classifying it as INFO without explicit justification"
  - NULL_ZERO_CONFUSION: "Treating a grep with zero hits as a tool error rather than a clean-pass result"
  - PRIVATE_DEP_SILENT_SKIP: "Skipping a file from the private-dep sweep without logging the skip reason"
verification_checkpoint: "Run: python3 -c \"import json; d=json.load(open('scratch/portability_report.json')); blocks=[e for e in d if e['severity']=='BLOCK']; print(f'BLOCK violations: {len(blocks)}'); assert all('file' in e and 'severity' in e for e in d)\" — must exit 0; zero BLOCK violations required for a portable skill set"
rung_target: 641
---

# Recipe: Portability Audit

## Purpose

Sweep all skill, recipe, and core files for portability violations: absolute paths, private repository dependencies, host-specific environment references, and float literals in verification paths. This recipe was motivated by 4 portability failures found in a single audit session, which would have caused reproduction failures on other machines.

## When to Use

- Before publishing a skill or recipe to the community database
- Before any benchmark or promotion claim (portability is a rung 641 prerequisite)
- After onboarding a new contributor's submission

## 4 Violation Categories

| Category | Severity Baseline | Example Pattern |
|----------|------------------|-----------------|
| Absolute paths | BLOCK | `/home/phuc/`, `/Users/`, `/opt/` |
| Private repo deps | BLOCK | `git+ssh://`, `.corp`, `.internal` |
| Host-specific env | WARN | `$HOSTNAME`, `Path.home()` as literal config |
| Float in verification | WARN→BLOCK | `math.isclose`, `== 0.0` in test assertions |

## Severity Rules

- **BLOCK**: Must be fixed before any promotion claim; portability is a Lane A invariant
- **WARN**: Should be fixed; acceptable for local iteration but blocks community submission
- **INFO**: Acceptable in display/comment context; logged for awareness only

## Notes

- A grep returning zero hits is NOT an error — it is a clean PASS for that category
- Do not use `$HOME` or `~` as config values; use `EVIDENCE_ROOT` relative paths per the portability spec
- Float literals in `print()` or logging f-strings are acceptable; float in `assert`, `==`, `<`, `>` comparisons in test/verification code is BLOCK

---

## Audit Flow (Mermaid Diagram)

```mermaid
flowchart TD
    A[Step 1: SCAN absolute paths\nportability_abs_paths.txt\n/home/ /Users/ /root/ /opt/ /var/] --> B[Step 2: SCAN private deps\nportability_private_deps.txt\ngit+ssh:// .corp .internal hardcoded IPs]
    B --> C[Step 3: SCAN host env refs\nportability_host_env.txt\n$HOME $USER $HOSTNAME os.environ HOME]
    C --> D[Step 4: SCAN float in verification\nportability_float_verification.txt\n== 0.0 math.isclose np.allclose pytest.approx]
    D --> E[Step 5: MERGE + CLASSIFY\nportability_report.json\nBLOCK | WARN | INFO per hit]
    E --> F[Step 6: SUMMARY\nportability_summary.txt\ncounts per category + BLOCK fixes]

    A -->|grep unavailable| A2[FALLBACK: Read manual scan\nlog in portability_run.log]
    E -->|duplicate file+line| E2[DEDUP: keep highest severity]
    F -->|zero BLOCK| PASS[PASS\nportable skill set confirmed]
    F -->|BLOCK violations| FIX[FIX required\nbefore community submission]
```

---

## FSM: Portability Audit State Machine

```
States: SCAN_ABS_PATHS | SCAN_PRIVATE_DEPS | SCAN_HOST_ENV |
        SCAN_FLOAT_VERIFY | MERGE_CLASSIFY | SUMMARY | PASS | BLOCKED

Transitions:
  [*] → SCAN_ABS_PATHS: audit invoked on skills/ and recipes/
  SCAN_ABS_PATHS → SCAN_PRIVATE_DEPS: portability_abs_paths.txt written (may be empty)
  SCAN_PRIVATE_DEPS → SCAN_HOST_ENV: portability_private_deps.txt written
  SCAN_HOST_ENV → SCAN_FLOAT_VERIFY: portability_host_env.txt written
  SCAN_FLOAT_VERIFY → MERGE_CLASSIFY: portability_float_verification.txt written
  MERGE_CLASSIFY → SUMMARY: portability_report.json with all hits classified
  SUMMARY → PASS: zero BLOCK violations in portability_report.json
  SUMMARY → BLOCKED: BLOCK violations present (must fix before community submission)

  Fallback branch:
  ANY_SCAN → FALLBACK_READ: grep unavailable; Read + manual scan; log fallback

Exit conditions:
  PASS: python3 verification exits 0; BLOCK violations: 0
  BLOCKED: any BLOCK violation confirmed; skill/recipe not portable
```

---

## When a BLOCK Violation Is Found

| Violation | Example | Fix |
|-----------|---------|-----|
| Absolute path | `/home/phuc/projects/...` | Replace with `EVIDENCE_ROOT`-relative path |
| Private repo dep | `git+ssh://git@github.com/...` | Remove or replace with published package |
| Host-specific env | `$HOSTNAME` as literal config | Use `PORTABILITY_ENV_VAR` from project spec |
| Float in verification | `assert result == 0.0` | Replace with `assert result == 0` (exact int) |

## GLOW Scoring

| Dimension | Contribution | Points |
|-----------|-------------|--------|
| **G** (Growth) | New portability violation type discovered (e.g., novel host-specific env var) added to grep pattern set for future sweeps | +3 per new pattern type identified |
| **L** (Love/Quality) | Zero BLOCK violations confirmed after sweep; float in verification eliminated; paths repo-relative only | +3 per clean audit run |
| **O** (Output) | portability_report.json emitted with all violations classified; portability_summary.txt with BLOCK fix guidance | +3 per complete audit run |
| **W** (Wisdom) | Northstar metric (community_contributors + recipe_hit_rate) advanced — portable skills can be submitted to the Stillwater Store and replayed by anyone | +3 when BLOCK violations resolved and skill submitted to Store |

**Northstar Metric:** `community_contributors` + `recipe_hit_rate` — portability is the baseline requirement for community participation. A skill with zero BLOCK violations can be submitted to the Stillwater Store, enabling other contributors to replay it. Each Store submission increases recipe_hit_rate across the ecosystem.

---

## Three Pillars of Software 5.0 Kung Fu

| Pillar | How This Recipe Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | Each portability audit run refines the agent's violation taxonomy — newly discovered portability patterns (e.g., a novel host-specific env var) are added to the grep sweep, shrinking the gap between what the recipe detects and what actually breaks reproducibility on other machines |
| **LEAK** (Cross-Agent Trade) | The portability_report.json is a shared contract between the contributor agent and the community reviewer: BLOCK violations must be cleared before the contributor can claim the skill is portable, making the report the evidence token that enables reviewer trust without re-reading the full file |
| **LEC** (Emergent Conventions) | Enforces repo-relative paths and `EVIDENCE_ROOT`-anchored references as a universal portability convention: any skill or recipe that hardcodes `/home/` or `/Users/` is provably non-portable, and this recipe makes that a detectable, actionable violation rather than an implicit assumption |

**Belt Level:** Yellow — demonstrates that contributions are reproducible beyond the author's machine, a prerequisite for community participation and the first rung of public trust.

**GLOW Score:** +3 per successful audit run with portability_report.json emitted and zero BLOCK violations confirmed (clean sweep or all BLOCKs resolved before report emission).
