# Load Scout Skills Command

**Command:** `/load-scout-skills`
**Version:** 1.0.0
**Auth:** 65537 | **Northstar:** Phuc Forecast
**Type:** User-Invocable Skill (Claude Code Command)
**Status:** Production-Ready
**Date:** 2026-02-14

---

## PURPOSE

Load skills for **Scout Agent** role in Prime Swarm Orchestration.

Scout agents are responsible for:
- Exploration and analysis
- Pattern detection
- Problem understanding
- Architecture planning
- Manifold extraction (for math)

---

## USAGE

```bash
/load-scout-skills [task_type]
```

**Task types:**
- `swe-bench` - Software engineering benchmarks
- `imo-math` - IMO mathematics problems
- `general-coding` - Feature implementation
- `math-proof` - Theorem proving
- `physics` - IF Theory implementation

**Default:** `general-coding` (if no task type specified)

---

## SKILL LOADING BY TASK TYPE

### SWE-bench (Software Engineering)

```bash
/load-scout-skills swe-bench
```

**Skills loaded:**
- **shannon-compaction.md** - Interface-first context engineering (500→200 lines)
- **contract-compliance.md** - Surface lock enforcement
- **socratic-debugging.md** - Self-critique before execution
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Explore codebase, understand issue, identify patterns

---

### IMO Mathematics

```bash
/load-scout-skills imo-math
```

**Skills loaded:**
- **geometry-proof-pack.md** - Synthetic geometry with manifold extraction
- **epistemic-typing.md** - Lane A/B/C classification
- **trace-distiller.md** - Execution trace → witness conversion
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Understand problem, extract manifold, identify lemmas

---

### General Coding

```bash
/load-scout-skills general-coding
```

**Skills loaded:**
- **shannon-compaction.md** - Interface-first context engineering
- **recipe-selector.md** - CPU-first deterministic routing
- **socratic-debugging.md** - Self-critique before execution
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Understand requirements, explore code, plan architecture

---

### Math Proof

```bash
/load-scout-skills math-proof
```

**Skills loaded:**
- **epistemic-typing.md** - Lane A/B/C classification
- **axiomatic-truth-lanes.md** - Lane dominance: min lane wins
- **trace-distiller.md** - Execution trace → witness conversion
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Understand theorem, classify lane, identify approach

---

### Physics (IF Theory)

```bash
/load-scout-skills physics
```

**Skills loaded:**
- **geometric-big-bang.md** - IF Theory foundations
- **grammar-of-existence.md** - Ontological framework
- **prime-model-oop.md** - Prime-based object modeling
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Understand IF Theory chapter, identify physics requirements

---

## CONFIRMATION OUTPUT

```
✅ SCOUT SKILLS LOADED

Task Type: swe-bench
Agent Role: Scout (exploration + analysis)

Skills Active (4):
  ✓ shannon-compaction.md v0.3.0
  ✓ contract-compliance.md v1.0.0
  ✓ socratic-debugging.md v1.0.0
  ✓ counter-required-routering.md v1.0.0

Verification Framework:
✓ OAuth(39,63,91) → 641 → 274177 → 65537
✓ Counter Bypass: 100% accuracy
✓ Epistemic Hygiene: Active

SCOUT AGENT READY
```

---

## CUSTOMIZATION

To customize skills for a specific task type, edit this file:

```bash
# Edit skill list for swe-bench Scout
vim /home/phuc/projects/stillwater/canon/prime-skills/skills/load-scout-skills.md
```

**Skill directories:**
- `/home/phuc/projects/stillwater/canon/prime-skills/skills` - Coding skills
- `/home/phuc/projects/stillwater/canon/prime-math/skills` - Math skills
- `/home/phuc/projects/stillwater/canon/prime-physics/skills` - Physics skills

---

## INTEGRATION WITH SWARM

Scout agents are spawned by `/prime-swarm-orchestration`:

```bash
# Swarm automatically calls /load-scout-skills based on task_type
/prime-swarm-orchestration task_type=swe-bench model=haiku
  → Scout Agent: /load-scout-skills swe-bench
  → Solver Agent: /load-solver-skills swe-bench
  → Skeptic Agent: /load-skeptic-skills swe-bench
```

---

## VERIFICATION CHECKS

After loading, verify:

```bash
# Check Counter Bypass Protocol
assert counter_bypass_accuracy == 100.0

# Check skill versions
assert shannon_compaction_version >= "0.3.0"
assert socratic_debugging_version >= "1.0.0"

# Check verification framework
assert verification_ladder == "OAuth→641→274177→65537"
```

---

**Command:** `/load-scout-skills`
**Version:** 1.0.0
**Auth:** 65537 | **Northstar:** Phuc Forecast
**Status:** Production-Ready

*"Scout agents explore the territory. Load the right skills for the terrain."*
*"Auth: 65537"*
