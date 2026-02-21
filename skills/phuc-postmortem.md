# phuc-postmortem — QA-to-Improvement Feedback Loop

**Skill ID:** phuc-postmortem
**Version:** 1.0.0
**Authority:** 65537
**Role:** Extract learnings from every QA round and feed them back into skills/recipes/swarms
**Load Order:** After prime-safety, before any domain skill
**Conflict Resolution:** Strengthens all other skills (never weakens)

---

## 0) Purpose

Every QA round produces findings. Most teams log them and move on. Stillwater turns every finding into a permanent system improvement. This skill ensures that:

1. No finding is lost (logged to postmortem registry)
2. Every finding produces at least one improvement (skill patch, recipe fix, swarm update, or new forbidden state)
3. The system only gets smarter (never-worse doctrine applied to QA itself)

> "A mistake repeated is a decision." — Paulo Coelho
> "Absorb what is useful, discard what is useless, and add what is specifically your own." — Bruce Lee

---

## 1) The Postmortem Loop (MANDATORY after every QA round)

```
QA_ROUND_COMPLETE
  │
  ├── 1. EXTRACT: List all findings (pass AND fail)
  │     → Each finding gets a finding_id, severity, category
  │
  ├── 2. CLASSIFY: Map each finding to a system component
  │     → skill | recipe | swarm | paper | CLAUDE.md | NORTHSTAR | ROADMAP
  │
  ├── 3. ROOT_CAUSE: Why did this happen?
  │     → missing_gate | wrong_default | ambiguous_spec | no_test | drift
  │
  ├── 4. IMPROVE: Create the fix
  │     → Add forbidden state | Add gate check | Fix default | Add test
  │     → Patch the actual skill/recipe/swarm file
  │
  ├── 5. VERIFY: Confirm the fix prevents recurrence
  │     → Re-run the check that found the issue → must pass
  │
  └── 6. REGISTER: Log to postmortem registry
        → postmortem_registry.jsonl (append-only)
```

---

## 2) Finding Classification

### Severity Levels

| Severity | Criteria | Required Response |
|----------|----------|-------------------|
| S0-CRITICAL | Security vulnerability, data loss, credential leak | Immediate fix + forbidden state + skill patch |
| S1-HIGH | Wrong output, broken gate, missed validation | Fix within same session + skill/recipe patch |
| S2-MEDIUM | Inconsistency, wrong default, ambiguous spec | Fix within same session or next build |
| S3-LOW | Style issue, wrong URL, non-portable path | Fix in batch, no urgency |
| S4-OBSERVATION | Not a bug — improvement opportunity | Log for future consideration |

### Root Cause Categories

| Category | What Went Wrong | Standard Fix |
|----------|-----------------|-------------|
| `missing_gate` | No check existed for this case | Add gate to relevant skill's FSM |
| `wrong_default` | Default value was incorrect or unsafe | Fix default + add forbidden state for old default |
| `ambiguous_spec` | Spec allowed multiple interpretations | Tighten spec language (MUST/MUST NOT) |
| `no_test` | No verification existed | Add to QA checklist or test suite |
| `drift` | System evolved but docs/skills didn't update | Sync all affected files |
| `missing_context` | Sub-agent lacked context to get it right | Add to CNF capsule template |
| `hardcoded_value` | Value should be configurable or derived | Extract to config or derive from source of truth |
| `cross_project_inconsistency` | Projects disagree on a shared value | Update all projects from single source of truth |

---

## 3) Improvement Types

Every finding MUST produce at least one of these improvements:

### A. Forbidden State Addition
When a finding reveals a failure mode, add it to the relevant skill:
```
forbidden_states:
  - WRONG_REPO_URL   # Found: oauth3-spec had phuc-io instead of phuctruong
```

### B. Gate Addition
When a finding reveals a missing check:
```yaml
gates:
  - G_REPO_URL: All repo URLs must match github.com/phuctruong/*
```

### C. Recipe Fix
When a finding reveals a process gap:
```json
{"step": "verify_metadata", "check": "repo_url matches NORTHSTAR.repository"}
```

### D. Swarm Update
When a finding reveals an agent produced wrong output:
```yaml
anti_patterns:
  - name: "The Assumed URL"
    description: "Agent guesses repo URL instead of reading from NORTHSTAR or pyproject.toml"
    fix: "Always read repo URL from source of truth file"
```

### E. Checklist Addition
When a finding reveals a QA gap:
```markdown
- [ ] All URLs in generated files match the canonical repo URL
```

### F. CNF Capsule Enhancement
When a finding reveals missing context in sub-agent dispatches:
```yaml
cnf_capsule_required_fields:
  - repo_url: "Read from NORTHSTAR.md or pyproject.toml, never guess"
```

---

## 4) State Machine

```
States:
  INIT → INTAKE_FINDINGS → CLASSIFY → ROOT_CAUSE → PLAN_IMPROVEMENTS →
  APPLY_IMPROVEMENTS → VERIFY_FIXES → REGISTER → EXIT_IMPROVED

Transitions:
  INTAKE_FINDINGS → CLASSIFY:
    guard: findings_list.length > 0
  CLASSIFY → ROOT_CAUSE:
    guard: all findings have severity + category
  ROOT_CAUSE → PLAN_IMPROVEMENTS:
    guard: all findings have root_cause
  PLAN_IMPROVEMENTS → APPLY_IMPROVEMENTS:
    guard: each finding has >= 1 planned improvement
  APPLY_IMPROVEMENTS → VERIFY_FIXES:
    guard: all planned improvements applied to files
  VERIFY_FIXES → REGISTER:
    guard: re-check confirms fix works
  REGISTER → EXIT_IMPROVED:
    guard: postmortem_registry.jsonl updated

Forbidden States:
  - FINDING_WITHOUT_IMPROVEMENT: Every finding MUST produce >= 1 improvement
  - IMPROVEMENT_WITHOUT_VERIFY: Every improvement MUST be verified
  - UNREGISTERED_POSTMORTEM: Every QA round MUST be logged to registry
  - SAME_FINDING_TWICE: If a finding recurs, the previous fix was insufficient → escalate severity
  - PROSE_ONLY_FIX: "We'll be more careful" is NOT a fix. Code/config/skill change required.
  - BLAME_THE_MODEL: "The model hallucinated" is NOT a root cause. Missing gate is.
```

---

## 5) Postmortem Registry Schema

Append to `postmortem_registry.jsonl` (one JSON per line):

```json
{
  "postmortem_id": "pm-2026-02-21-001",
  "date": "2026-02-21",
  "qa_round": "stillwater Phase 1 OAuth3 spec review",
  "findings": [
    {
      "finding_id": "F001",
      "severity": "S3-LOW",
      "category": "hardcoded_value",
      "description": "OAuth3 spec line 9 had wrong repo URL (phuc-io instead of phuctruong)",
      "root_cause": "Sub-agent guessed repo URL instead of reading from NORTHSTAR or pyproject.toml",
      "improvements": [
        {
          "type": "forbidden_state",
          "target": "skills/phuc-postmortem.md",
          "change": "Added ASSUMED_URL forbidden state"
        },
        {
          "type": "cnf_capsule",
          "target": "skills/phuc-orchestration.md",
          "change": "Add repo_url to required CNF capsule fields"
        },
        {
          "type": "swarm_anti_pattern",
          "target": "swarms/coder.md",
          "change": "Add 'The Assumed URL' anti-pattern"
        }
      ],
      "verified": true,
      "recurrence_count": 0
    }
  ],
  "system_improvements_count": 3,
  "rung": 641
}
```

---

## 6) Integration with Phuc-Orchestration

### When the Hub (Opus) receives QA results:

```
1. Hub receives QA report from Skeptic/Auditor sub-agent
2. Hub loads phuc-postmortem skill
3. Hub runs the Postmortem Loop (Section 1)
4. Hub dispatches improvements:
   - Skill patches → sonnet coder sub-agent
   - Swarm updates → haiku janitor sub-agent
   - Spec fixes → sonnet coder sub-agent
5. Hub verifies all improvements applied
6. Hub logs to postmortem_registry.jsonl
7. Hub updates case study with postmortem summary
```

### CNF Capsule Enhancement (from this QA round):

Add to every coder sub-agent dispatch:
```yaml
required_context:
  repo_url: "Read from NORTHSTAR.md repository field or pyproject.toml [project.urls]"
  repo_owner: "phuctruong (NOT phuc-io, NOT phuc-net, NOT phucnet)"
  project_name: "Read from NORTHSTAR.md or directory name"
  # NEVER guess these values. Always read from source of truth.
```

---

## 7) Recurring Finding Escalation

If the same finding appears in two QA rounds:

| Recurrence | Escalation |
|------------|------------|
| 1st occurrence | Normal fix (gate/forbidden state/recipe) |
| 2nd occurrence | Severity +1, root cause must be deeper (why didn't the first fix work?) |
| 3rd occurrence | CRITICAL: the fix approach is wrong. Redesign the gate. |

---

## 8) NORTHSTAR Alignment

This skill advances the NORTHSTAR metric: **Recipe hit rate / System quality**

Every postmortem improvement:
- Adds a gate that prevents the same mistake → fewer failures
- Adds context to CNF capsules → better sub-agent output
- Adds anti-patterns to swarms → agents avoid known traps
- Makes the system smarter without retraining any model

This IS Software 5.0: the skill library only gets stronger.

> "The master has failed more times than the beginner has tried."
> Every postmortem is a kata. The dojo grows stronger with each one.

---

## 9) Quick Reference

```
After every QA round:
  1. List findings (severity S0-S4)
  2. Classify (which file? which root cause?)
  3. Fix (forbidden state / gate / recipe / swarm / capsule)
  4. Verify (re-run the check)
  5. Register (postmortem_registry.jsonl)

Forbidden:
  - FINDING_WITHOUT_IMPROVEMENT
  - IMPROVEMENT_WITHOUT_VERIFY
  - SAME_FINDING_TWICE (escalate!)
  - PROSE_ONLY_FIX ("we'll be careful" is not a fix)
  - BLAME_THE_MODEL (missing gate is the real cause)
```

---

## Revision History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-02-21 | Initial skill. Born from OAuth3 spec QA finding (wrong repo URL). |
