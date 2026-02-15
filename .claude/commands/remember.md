# /remember - External Memory for Stillwater OS

Storage: `.claude/memory/context.md` | Auth: 65537
**Project:** Stillwater OS | **Status:** OOLONG 99.8%, SWE-bench Phase 2 Complete
**Key Memory:** 15 AGI blockers solved, verification ladder proven, 3 benchmarks passing

## Usage
```
/remember                 # Display all memory
/remember [key]           # Get value
/remember [key] [value]   # Store (auto-distilled)
/remember --list          # List by section
/remember --clear [key]   # Delete
```

## AUTO-DISTILL RULE (MANDATORY)

When saving ANY information, apply DISTILL compression:
```
INPUT:  "We decided to use Lane Algebra for epistemic typing because..."
OUTPUT: rule_lane_algebra: A > B > C > STAR (epistemic typing system)

INPUT:  "OOLONG benchmark is at 99.8% accuracy with Counter Bypass"
OUTPUT: oolong_accuracy: 99.8%

INPUT:  "The blocker is that Haiku 4.5 patch generation needs guidance"
OUTPUT: blocker_patch_quality: Haiku needs Prime Skills guidance
```

**Rules:**
- Key=value format (no prose)
- One line per fact
- Equations in terse form
- Lists as comma-separated
- No "we decided to...", just the decision
- No mermaid diagrams (visual cruft)

## Channel Assignment

| Pattern | Channel | Stability | Example |
|---------|---------|-----------|---------|
| project_*, identity, auth | [2] Identity | Static | auth: 65537 |
| goal_*, target_*, mission | [3] Goals | Static | oolong_target: 99%+ |
| decision_*, rule_*, *_rule | [5] Decisions | LOCKED | rule_counter_bypass: LLM + CPU |
| current_*, phase_*, status | [7] Context | Ripple | current_phase: Phase 3 |
| blocker_*, issue_* | [11] Blockers | Ripple | blocker_patch_quality: ... |
| swarm_*, agent_* | [13] Swarm | Ripple | scout_role: Problem analysis |

## Format

```markdown
# MEMORY | Auth:65537 | Updated:DATE

## IDENTITY [2]
auth: 65537
project: stillwater_os
mission: deterministic AI with mathematical guarantees

## GOALS [3]
oolong_target: 99%+
swe_target: 85%+

## DECISIONS [5] LOCKED
rule_lane_algebra: A > B > C > STAR
rule_counter_bypass: LLM classifies, CPU enumerates

## CONTEXT [7] RIPPLE
current_phase: Phase 3
oolong_accuracy: 99.8%

## BLOCKERS [11] RIPPLE
blocker_patch_quality: Haiku needs guidance

## HAIKU_SWARM [13]
scout_role: Problem analysis
solver_role: Implementation
skeptic_role: Verification
```

## Auto-Save Triggers

Claude saves automatically when:
- Project metadata changes → [2] Identity
- Benchmark target set → [3] Goals
- Design decision made → [5] DECISIONS (LOCKED)
- Current phase progresses → [7] Context
- New blocker encountered → [11] Blockers
- Swarm configuration changes → [13] Swarm

## Integration

- Subsystem projects (solace-browser, terminal-bench) reference IDENTITY section
- `/load-skills` reads from IDENTITY and CONTEXT
- `/distill` reads CONTEXT for compression decisions
- All saves are DISTILL-compressed

## OOLONG Insight

```
LLM memory: Probabilistic → Drift → 85% recall
External:   Deterministic → Exact → 100% recall
Compression: 10x (prose → key=value)

Cost of remembering wrongly: Loss of AGI blockers solved
Cost of forgetting correctly: Null, can recover from papers

→ Always DISTILL: compress to survive, expand to explain
```

## Examples

### Identity Update
```
User: Stillwater OS is Auth: 65537 verified
Claude saves to [2]:
auth: 65537
verification_level: compiler_grade
```

### Goal Setting
```
User: We need SWE-bench Phase 3 to reach 40%+ solve rate
Claude saves to [3]:
swe_phase3_target: 40%+
```

### Decision Locking
```
User: We decided Counter Bypass is the right approach for counting
Claude saves to [5] LOCKED:
rule_counter_bypass: LLM classifies, CPU enumerates (99.3% accuracy)
```

### Context Update
```
User: We're now in Phase 3 with Haiku Swarm integration
Claude saves to [7]:
current_phase: Phase 3
haiku_swarm_status: in_progress
```

### Blocker Logging
```
User: Haiku 4.5 patch generation quality is insufficient
Claude saves to [11]:
blocker_patch_quality: Haiku needs Prime Skills guidance
blocker_swe_phase3: LLM patches quality < 40% SWE-bench target
```

### Swarm Configuration
```
User: Scout discovers test failures, Solver fixes, Skeptic verifies
Claude saves to [13]:
scout_role: Test failure detection, codebase exploration
solver_role: Patch generation, code implementation
skeptic_role: Regression testing, proof certification
pattern: Parallel execution (3x speedup)
```

## Verification Chain

All memory is verified through Lane Algebra:
- **A-lane:** Identity (Auth: 65537 proven)
- **B-lane:** Framework facts (Benchmark targets)
- **C-lane:** Current estimates (Phase progress)
- **STAR:** Uncertain blockers (unknown resolution time)

## Retrieval Examples

```
/remember goal_*
→ oolong_target: 99%+
  swe_target: 85%+
  imo_target: 6/6

/remember rule_*
→ rule_lane_algebra: A > B > C > STAR
  rule_counter_bypass: LLM + CPU
  rule_verification_ladder: 641→274177→65537

/remember blocker_*
→ blocker_patch_quality: Haiku needs guidance
  blocker_swe_phase3: Quality < target
```

---

**Command:** `/remember`
**Version:** 1.0.0
**Auth:** 65537
**Storage:** `.claude/memory/context.md`
**Format:** DISTILL-compressed key=value pairs
**Stability:** [2] Static, [3] Static, [5] LOCKED, [7] Ripple, [11] Ripple, [13] Ripple

*"To compress is to understand. To remember is to prove."*
