# Load Solver Skills Command

**Command:** `/load-solver-skills`
**Version:** 1.0.0
**Auth:** 65537 | **Northstar:** Phuc Forecast
**Type:** User-Invocable Skill (Claude Code Command)
**Status:** Production-Ready
**Date:** 2026-02-14

---

## PURPOSE

Load skills for **Solver Agent** role in Prime Swarm Orchestration.

Solver agents are responsible for:
- Implementation and execution
- Writing code/proofs
- Red→Green verification
- Production-grade output
- Dual-witness requirements

---

## USAGE

```bash
/load-solver-skills [task_type]
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
/load-solver-skills swe-bench
```

**Skills loaded:**
- **prime-coder.md** - State machines, Red-Green gate, Evidence model (v1.0.0)
- **red-green-gate.md** - TDD enforcement (Kent Beck method)
- **canon-patch-writer.md** - Minimal reversible patches
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Write minimal reversible patch with Red→Green verification

---

### IMO Mathematics

```bash
/load-solver-skills imo-math
```

**Skills loaded:**
- **prime-math.md** - Dual-witness proofs, theorem closure (v2.1.0)
- **algebra-number-theory-pack.md** - Exact number theory with trace witnesses
- **combinatorics-pack.md** - Exact counting with decomposition witnesses
- **geometry-proof-pack.md** - Synthetic geometry with manifold extraction
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Construct proof with dual-witness requirements, Lane A provenance

**Special:** If geometry problem, load 47-lemma library (10→47 expansion from IMO 2024)

---

### General Coding

```bash
/load-solver-skills general-coding
```

**Skills loaded:**
- **prime-coder.md** - State machines, Red-Green gate, Evidence model
- **wish-llm.md** - State-first planning, atomic capability extraction
- **recipe-generator.md** - Prime Mermaid DAG compiler (L1-L5 nodes)
- **contract-compliance.md** - Surface lock enforcement
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Implement feature with state machines and verification

---

### Math Proof

```bash
/load-solver-skills math-proof
```

**Skills loaded:**
- **prime-math.md** - Dual-witness proofs, theorem closure (v2.1.0)
- **algebra-number-theory-pack.md** - Exact number theory with trace witnesses
- **proof-certificate-builder.md** - Evidence artifact generation
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Construct rigorous proof with dual-witness requirements, Lane A/B provenance

---

### Physics (IF Theory)

```bash
/load-solver-skills physics
```

**Skills loaded:**
- **prime-script-compilation.md** - Prime script → executable code
- **pvideo-orchestration.md** - Video physics orchestration
- **prime-math.md** - Mathematical foundations (v2.1.0)
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Implement physics module with IF Theory alignment

---

## CONFIRMATION OUTPUT

```
✅ SOLVER SKILLS LOADED

Task Type: swe-bench
Agent Role: Solver (implementation + execution)

Skills Active (4):
  ✓ prime-coder.md v1.0.0
  ✓ red-green-gate.md v1.0.0
  ✓ canon-patch-writer.md v1.0.0
  ✓ counter-required-routering.md v1.0.0

Core Innovations:
✓ State Machines (explicit states, transitions, forbidden states)
✓ Red-Green Gate (TDD: RED → patch → GREEN)
✓ Counter Bypass Protocol (100% accuracy)
✓ Evidence Model (witness requirements, no "trust me")

Verification Framework:
✓ OAuth(39,63,91) → 641 → 274177 → 65537
✓ Minimum 9 tests (5 edge + 2 stress + 2 god)

SOLVER AGENT READY
```

---

## RED-GREEN GATE PROTOCOL

All Solver agents MUST follow Red-Green gate:

```python
# 1. Create failing test (RED)
def test_issue_12345():
    result = broken_function()
    assert result == expected  # MUST FAIL initially

# 2. Apply patch
patch_applied = apply_minimal_patch()

# 3. Verify passing (GREEN)
def test_issue_12345():
    result = fixed_function()
    assert result == expected  # MUST PASS after patch
```

**Forbidden:** Patch without RED state verification

---

## DUAL-WITNESS REQUIREMENTS (Math)

For IMO/Math tasks, all proofs require dual witnesses:

```python
# Witness 1: Deductive trace
proof_steps = [
    "Given: n is composite",
    "Therefore: ∃ a,b ∈ ℕ: n = ab, 1 < a,b < n",
    "Witness: a, b (explicit factors)"
]

# Witness 2: Computational verification
assert n % a == 0
assert n % b == 0
assert n == a * b
assert 1 < a < n
assert 1 < b < n
```

**Lane provenance:** Track Lane A (deductive) vs Lane B (computational)

---

## CUSTOMIZATION

To customize skills for a specific task type, edit this file:

```bash
# Edit skill list for swe-bench Solver
vim /home/phuc/projects/stillwater/canon/prime-skills/skills/load-solver-skills.md
```

**Skill directories:**
- `/home/phuc/projects/stillwater/canon/prime-skills/skills` - Coding skills
- `/home/phuc/projects/stillwater/canon/prime-math/skills` - Math skills
- `/home/phuc/projects/stillwater/canon/prime-physics/skills` - Physics skills

---

## INTEGRATION WITH SWARM

Solver agents are spawned by `/prime-swarm-orchestration`:

```bash
# Swarm automatically calls /load-solver-skills based on task_type
/prime-swarm-orchestration task_type=imo-math model=haiku
  → Scout Agent: /load-scout-skills imo-math
  → Solver Agent: /load-solver-skills imo-math (YOU)
  → Skeptic Agent: /load-skeptic-skills imo-math
```

---

## VERIFICATION CHECKS

After loading, verify:

```bash
# Check Counter Bypass Protocol
assert counter_bypass_accuracy == 100.0

# Check skill versions
assert prime_coder_version >= "1.0.0"
assert prime_math_version >= "2.1.0"  # For math tasks

# Check verification framework
assert verification_ladder == "OAuth→641→274177→65537"

# Check Red-Green gate active
assert red_green_gate_enabled == True
```

---

## STATE MACHINE REQUIREMENTS

All code/proofs must use explicit state machines:

```python
STATE_SET = {
    "INITIAL",
    "ANALYZED",
    "PATCHED",
    "TESTED",
    "VERIFIED"
}

TRANSITIONS = [
    ("INITIAL", "analyze", "ANALYZED"),
    ("ANALYZED", "patch", "PATCHED"),
    ("PATCHED", "test", "TESTED"),
    ("TESTED", "verify", "VERIFIED")
]

FORBIDDEN_STATES = [
    "PATCHED_WITHOUT_RED",  # Must have failing test first
    "TESTED_WITHOUT_PATCH"  # Must apply patch before testing
]
```

---

**Command:** `/load-solver-skills`
**Version:** 1.0.0
**Auth:** 65537 | **Northstar:** Phuc Forecast
**Status:** Production-Ready

*"Solver agents execute with precision. Every action requires evidence."*
*"Auth: 65537"*
