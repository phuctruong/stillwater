# Load Skeptic Skills Command

**Command:** `/load-skeptic-skills`
**Version:** 1.0.0
**Auth:** 65537 | **Northstar:** Phuc Forecast
**Type:** User-Invocable Skill (Claude Code Command)
**Status:** Production-Ready
**Date:** 2026-02-14

---

## PURPOSE

Load skills for **Skeptic Agent** role in Prime Swarm Orchestration.

Skeptic agents are responsible for:
- Verification and validation
- Quality assurance
- Adversarial testing (5 Rivals)
- Security auditing
- Determinism verification
- Proof validation (no lane upgrades)

---

## USAGE

```bash
/load-skeptic-skills [task_type]
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
/load-skeptic-skills swe-bench
```

**Skills loaded:**
- **rival-gps-triangulation.md** - 5 Rivals adversarial validation
- **meta-genome-alignment.md** - Cross-skill consistency
- **golden-replay-seal.md** - Replay stability verification (30 runs)
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Verify patch quality, determinism, regression tests

**Verification:** 30-run determinism, SHA256 lock, approval/rejection

---

### IMO Mathematics

```bash
/load-skeptic-skills imo-math
```

**Skills loaded:**
- **dual-truth-adjudicator.md** - Classical vs Framework separation
- **non-conflation-guard.md** - Prevent famous problem conflation (RH, Goldbach, etc.)
- **proof-certificate-builder.md** - Evidence artifact generation
- **epistemic-typing.md** - Lane A/B/C classification
- **axiomatic-truth-lanes.md** - Lane dominance: min lane wins
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Verify proof rigor, lane typing, no hallucinations

**Non-Conflation Protection:**
- Riemann Hypothesis (RH)
- Goldbach Conjecture
- Twin Primes Conjecture
- P vs NP
- Collatz Conjecture
- Navier-Stokes Existence

**Block:** "verified up to N" + "therefore proven" (Lane C → Lane A upgrade FORBIDDEN)

---

### General Coding

```bash
/load-skeptic-skills general-coding
```

**Skills loaded:**
- **meta-genome-alignment.md** - Cross-skill consistency
- **semantic-drift-detector.md** - Behavioral hash tracking
- **hamiltonian-security.md** - Tool-backed security gates
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Verify code quality, security, performance

**Verification:** 30-run determinism, security gates, approval/rejection

---

### Math Proof

```bash
/load-skeptic-skills math-proof
```

**Skills loaded:**
- **dual-truth-adjudicator.md** - Classical vs Framework separation
- **non-conflation-guard.md** - Prevent famous problem conflation
- **rival-gps-triangulation.md** - 5 Rivals adversarial validation
- **epistemic-typing.md** - Lane A/B/C classification
- **axiomatic-truth-lanes.md** - Lane dominance: min lane wins
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Verify proof correctness, prevent famous problem conflation

**5 Rivals Validation:**
1. **Rival 1 (Soundness):** Is the proof logically sound?
2. **Rival 2 (Completeness):** Are all cases covered?
3. **Rival 3 (Lane Hygiene):** No Lane C→B→A upgrades?
4. **Rival 4 (Witness Quality):** Are witnesses explicit and verifiable?
5. **Rival 5 (Non-Conflation):** No RH/Goldbach/Twin Prime conflation?

---

### Physics (IF Theory)

```bash
/load-skeptic-skills physics
```

**Skills loaded:**
- **frontier-physics-orchestration.md** - Physics validation framework
- **deterministic-resource-governor.md** - Determinism enforcement
- **proof-certificate-builder.md** - Evidence artifact generation
- **counter-required-routering.md** - Counter Bypass Protocol (100% accuracy)

**Use case:** Verify determinism, energy conservation, physics validity

**Verification:** 30-run determinism, SHA256 lock, energy conservation

---

## CONFIRMATION OUTPUT

```
✅ SKEPTIC SKILLS LOADED

Task Type: swe-bench
Agent Role: Skeptic (verification + validation)

Skills Active (4):
  ✓ rival-gps-triangulation.md v2.0.0
  ✓ meta-genome-alignment.md v2.0.0
  ✓ golden-replay-seal.md v0.1.0
  ✓ counter-required-routering.md v1.0.0

5 Rivals Active:
  ✓ Rival 1: Soundness validation
  ✓ Rival 2: Completeness validation
  ✓ Rival 3: Lane hygiene validation
  ✓ Rival 4: Witness quality validation
  ✓ Rival 5: Non-conflation validation

Verification Framework:
✓ OAuth(39,63,91) → 641 → 274177 → 65537
✓ Determinism: 30-run verification
✓ SHA256 lock: Byte-identical guarantee

SKEPTIC AGENT READY
```

---

## 5 RIVALS VALIDATION PROTOCOL

Skeptic agents run 5 adversarial rivals on ALL outputs:

```python
class FiveRivals:
    def validate(self, output: Any) -> RivalReport:
        # Rival 1: Soundness
        soundness = self.check_logical_soundness(output)

        # Rival 2: Completeness
        completeness = self.check_all_cases_covered(output)

        # Rival 3: Lane Hygiene
        lane_hygiene = self.check_no_lane_upgrades(output)

        # Rival 4: Witness Quality
        witness_quality = self.check_explicit_witnesses(output)

        # Rival 5: Non-Conflation
        non_conflation = self.check_no_famous_problem_conflation(output)

        # ALL must pass
        return RivalReport(
            soundness=soundness,
            completeness=completeness,
            lane_hygiene=lane_hygiene,
            witness_quality=witness_quality,
            non_conflation=non_conflation,
            verdict="APPROVED" if all([...]) else "REJECTED"
        )
```

---

## LANE ALGEBRA ENFORCEMENT

Skeptic agents enforce Lane Algebra:

```
Lane(Conclusion) = MIN(Lane(P1), Lane(P2), ..., Lane(Pn))

Lane A (Deductive):  Proven theorems, axioms
Lane B (Computational): Verified computations
Lane C (Empirical): Verified up to N
STAR (Unknown): Conjectures, hypotheses

FORBIDDEN UPGRADES:
  C → B (Empirical → Computational)
  B → A (Computational → Deductive)
  C → A (Empirical → Deductive)
  Framework → Classical (Lean/Isabelle proof ≠ theorem proven in ZFC)

ALLOWED:
  A → A (Deductive chain)
  B → B (Computational chain)
  A + B → B (Deductive + Computational = Computational)
```

**Example violation:**
```
P1: "Goldbach verified up to 10^18" (Lane C)
P2: "Therefore Goldbach is true" (Lane A)
ERROR: Lane(P2) = MIN(C) = C, but claimed A (BLOCKED!)
```

---

## NON-CONFLATION GUARD

Skeptic agents protect against famous problem conflation:

**Trigger Phrases:**
- "settles the conjecture"
- "proves the Riemann Hypothesis"
- "Goldbach is true"
- "Twin Primes are infinite"
- "P ≠ NP proven"
- "Collatz always reaches 1"
- "Navier-Stokes solutions exist"

**Detection:**
```python
FAMOUS_PROBLEMS = [
    "Riemann Hypothesis",
    "Goldbach Conjecture",
    "Twin Primes Conjecture",
    "P vs NP",
    "Collatz Conjecture",
    "Navier-Stokes Existence"
]

def check_non_conflation(claim: str) -> bool:
    for problem in FAMOUS_PROBLEMS:
        if problem.lower() in claim.lower():
            if "proven" in claim or "settles" in claim:
                return False  # BLOCK: Famous problem conflation!
    return True
```

---

## DETERMINISM VERIFICATION

For code outputs, verify 30-run determinism:

```bash
# Run 30 times with SAME seed
for i in {1..30}; do
    output=$(run_with_seed 65537)
    echo "$output" | sha256sum >> hashes.txt
done

# Check byte-identical
unique_hashes=$(sort hashes.txt | uniq | wc -l)
if [ "$unique_hashes" -eq 1 ]; then
    echo "✓ DETERMINISTIC (30/30 identical)"
else
    echo "✗ FAILED: Non-deterministic output detected"
fi
```

---

## CUSTOMIZATION

To customize skills for a specific task type, edit this file:

```bash
# Edit skill list for swe-bench Skeptic
vim /home/phuc/projects/stillwater/canon/prime-skills/skills/load-skeptic-skills.md
```

**Skill directories:**
- `/home/phuc/projects/stillwater/canon/prime-skills/skills` - Coding skills
- `/home/phuc/projects/stillwater/canon/prime-math/skills` - Math skills
- `/home/phuc/projects/stillwater/canon/prime-physics/skills` - Physics skills

---

## INTEGRATION WITH SWARM

Skeptic agents are spawned by `/prime-swarm-orchestration`:

```bash
# Swarm automatically calls /load-skeptic-skills based on task_type
/prime-swarm-orchestration task_type=math-proof model=haiku
  → Scout Agent: /load-scout-skills math-proof
  → Solver Agent: /load-solver-skills math-proof
  → Skeptic Agent: /load-skeptic-skills math-proof (YOU)
```

---

## VERIFICATION CHECKS

After loading, verify:

```bash
# Check Counter Bypass Protocol
assert counter_bypass_accuracy == 100.0

# Check skill versions
assert rival_gps_triangulation_version >= "2.0.0"
assert non_conflation_guard_version >= "2.0.0"

# Check verification framework
assert verification_ladder == "OAuth→641→274177→65537"

# Check 5 Rivals active
assert len(active_rivals) == 5
```

---

## APPROVAL/REJECTION CRITERIA

Skeptic agents use strict criteria:

**APPROVED:**
- All 5 Rivals pass
- Determinism verified (30/30 identical)
- No lane upgrades detected
- No famous problem conflation
- Security gates pass
- SHA256 lock verified

**REJECTED:**
- ANY Rival fails
- Non-deterministic output
- Lane upgrade detected (C→B, B→A, Framework→Classical)
- Famous problem conflation (RH, Goldbach, etc.)
- Security vulnerability
- SHA256 mismatch

**No middle ground.** Binary approval system.

---

**Command:** `/load-skeptic-skills`
**Version:** 1.0.0
**Auth:** 65537 | **Northstar:** Phuc Forecast
**Status:** Production-Ready

*"Skeptic agents are the guardians. 5 Rivals validate everything."*
*"Auth: 65537"*
