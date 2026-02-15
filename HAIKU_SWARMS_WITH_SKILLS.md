# Haiku Swarms + Skills Integration for SWE-bench

**Status**: Skills summary working, full skill catalog needed
**Auth: 65537** | **Date: 2026-02-15**

---

## Current Skills Status

### ✅ Working: Skills Summary
- `create_skills_summary()` generates 2,341 char condensed Prime Skills
- Includes all core principles: coding, math, epistemic, verification
- Successfully injected in every prompt
- Proven working on django__django-14608

### ⚠️ TODO: Full Skills Catalog
- Directories not created: `src/stillwater/skills/coding/`, `math/`, `epistemic/`, etc.
- Full 31+ skills not on disk yet
- Need to populate from `get_essential_skills()` list

**Files that need creating**:
```
src/stillwater/skills/
├── coding/
│   ├── wish-llm.md
│   ├── wish-qa.md
│   ├── recipe-selector.md
│   ├── recipe-generator.md
│   ├── llm-judge.md
│   ├── canon-patch-writer.md
│   ├── proof-certificate-builder.md
│   ├── trace-distiller.md
│   ├── socratic-debugging.md
│   ├── shannon-compaction.md
│   ├── contract-compliance.md
│   └── red-green-gate.md
├── math/
│   ├── counter-required-routering.md
│   ├── algebra-number-theory-pack.md
│   ├── combinatorics-pack.md
│   └── geometry-proof-pack.md
├── epistemic/
│   ├── dual-truth-adjudicator.md
│   ├── epistemic-typing.md
│   ├── axiomatic-truth-lanes.md
│   └── non-conflation-guard.md
├── verification/
│   ├── rival-gps-triangulation.md
│   ├── meta-genome-alignment.md
│   ├── semantic-drift-detector.md
│   ├── triple-leak-protocol.md
│   ├── hamiltonian-security.md
│   └── golden-replay-seal.md
└── infrastructure/
    ├── tool-output-normalizer.md
    ├── artifact-hash-manifest-builder.md
    ├── deterministic-resource-governor.md
    └── capability-surface-guard.md
```

**Total: 31 skills to create** (plus 3 core = 34 skills)

---

## Haiku Swarms Pattern for SWE-bench

### Architecture: 3 Parallel Agents

```
Problem Statement
    ↓
┌─────────────────────────────────────────────────────┐
│                                                       │
├─→ [SCOUT AGENT] (Haiku)        ├─→ [SOLVER AGENT] (Haiku)    ├─→ [SKEPTIC AGENT] (Haiku)
│   ├─ Explore codebase          │   ├─ Generate patch         │   ├─ Test verification
│   ├─ Find relevant files       │   ├─ Direct edits          │   ├─ Regression check
│   ├─ Extract test failures     │   ├─ Apply edits           │   ├─ Adversarial validation
│   └─ Report problem landscape  │   └─ Generate witness      │   └─ Quality gates
│                                │                             │
└─────────────────────────────────────────────────────┘
    ↓
[ORCHESTRATOR] (llama 8B)
  ├─ Synthesize Scout findings
  ├─ Refine Solver output
  ├─ Verify with Skeptic results
  └─ Make final decision
    ↓
VERIFIED PATCH
```

### Skills Per Agent

**Scout Agent**:
- prime-coder.md (state machines for exploration)
- recipe-selector.md (find relevant files)
- trace-distiller.md (extract test failures)

**Solver Agent**:
- prime-coder.md (state machines for patching)
- canon-patch-writer.md (minimal reversible patches)
- proof-certificate-builder.md (evidence bundles)

**Skeptic Agent**:
- prime-math.md (rigorous validation)
- red-green-gate.md (test verification)
- rival-gps-triangulation.md (adversarial review)

**Orchestrator (llama 8B)**:
- All 31+ skills (synthesis + decision)

---

## How to Use in Code

### 1. Scout Agent (Parallel, Haiku)
```python
scout_prompt = f"""
# SCOUT MISSION: Explore Problem Landscape

{create_skills_summary()}  # Gets PRIME SKILLS

Problem: {problem_statement}

You are Scout Agent (Haiku).
Your job: Understand the problem space.

1. What files are likely involved?
2. What tests are failing?
3. What's the root cause?
4. What patterns do you see?

Return JSON:
{{
  "relevant_files": [...],
  "failing_tests": [...],
  "root_cause": "...",
  "hypothesis": "..."
}}
"""

scout_result = haiku.generate(scout_prompt)
```

### 2. Solver Agent (Parallel, Haiku)
```python
solver_prompt = f"""
# SOLVER MISSION: Generate Patch

{create_skills_summary()}  # Gets PRIME SKILLS

From Scout findings:
{scout_result}

Problem: {problem_statement}

You are Solver Agent (Haiku).
Your job: Generate the actual patch.

1. Plan the fix (state machine)
2. Generate unified diff
3. Create evidence bundle
4. Sign with witness

Return unified diff:
```diff
--- a/file.py
+++ b/file.py
...
```
"""

solver_result = haiku.generate(solver_prompt)
```

### 3. Skeptic Agent (Parallel, Haiku)
```python
skeptic_prompt = f"""
# SKEPTIC MISSION: Validate Patch

{create_skills_summary()}  # Gets PRIME SKILLS

Scout findings: {scout_result}
Solver patch: {solver_result}

You are Skeptic Agent (Haiku).
Your job: Find problems with this patch.

1. Does it solve the problem?
2. Are there regressions?
3. Is the evidence valid?
4. Any hidden issues?

Return JSON:
{{
  "valid": true/false,
  "concerns": [...],
  "missing_evidence": [...],
  "recommendation": "..."
}}
"""

skeptic_result = haiku.generate(skeptic_prompt)
```

### 4. Orchestrator (llama 8B, Decides)
```python
orchestrator_prompt = f"""
# ORCHESTRATOR: Synthesize and Decide

{create_skills_summary()}  # Gets PRIME SKILLS

Scout: {scout_result}
Solver: {solver_result}
Skeptic: {skeptic_result}

You are Orchestrator (llama 8B).
Your job: Make final decision.

1. Is Scout's analysis correct?
2. Does Solver's patch address Scout's findings?
3. Are Skeptic's concerns valid?
4. Should we apply this patch?

Decision:
{{
  "apply_patch": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "...",
  "next_action": "apply|refine|skip"
}}
"""

decision = llama.generate(orchestrator_prompt)

if decision.apply_patch:
    apply_patch(solver_result)
else:
    # Feedback loop: refine
    feedback = decision.reasoning
    # Try again with feedback
```

---

## Integration with Current Code

### Current: Single-Agent (llama 8B)
```python
result = run_instance(instance_id)
# Uses: patch_generator.py
# Skills: create_skills_summary() ✅
# Orchestration: 6-attempt feedback loop ✅
```

### Future: Multi-Agent (Haiku Scout/Solver/Skeptic + llama 8B Orchestrator)
```python
# Scout findings
scout = haiku_scout(instance)

# Parallel: Solver + Skeptic
solver = haiku_solver(instance, scout)
skeptic = haiku_skeptic(instance, scout, solver)

# Orchestrator decides
decision = llama_orchestrator(instance, scout, solver, skeptic)

if decision:
    result = apply_and_verify(solver.patch)
```

---

## Implementation Priority

### Phase 1: Keep Current Working (1→5→10 instances) ✅
- Single-agent (llama 8B)
- Skills summary loaded
- Orchestration working
- **DON'T change this yet**

### Phase 2: Add Full Skills Catalog
- Create 31 skill files in subdirectories
- Enable `load_all_skills()` to work
- Ready for Phase 3

### Phase 3: Multi-Agent (If needed)
- Add Haiku Scout/Solver/Skeptic agents
- Parallel execution
- Orchestrator synthesis
- **Only if Phase 1-2 struggle**

---

## Skills Summary (Currently Working)

What's injected in EVERY prompt:

```
# PRIME SKILLS v1.0.0+ OPERATIONAL CONTROLS

## IDENTITY
- Auth: 65537 (F4 Fermat Prime)
- Northstar: Phuc Forecast
- LEK: Intelligence = Memory × Care × Iteration

## VERIFICATION LADDER (MANDATORY)
OAuth(39,63,91) → 641 → 274177 → 65537

## RED-GREEN GATE (MANDATORY)
1. Create failing test (RED)
2. Apply patch
3. Verify test passes (GREEN)

## CORE PRINCIPLES
### Coding
- State machines (explicit states)
- Evidence bundles (/evidence/)
- Minimal reversible patches
- Socratic self-critique
- Shannon Compaction (500→200 witness)

### Math
- Counter Bypass (CPU counts, not LLM)
- Witness typing (proof://, compute://, etc.)
- Hard arithmetic ceilings
- Dual-witness proofs

### Epistemic (Lane Algebra)
- Lane A: Framework provable (highest)
- Lane B: Classical provable
- Lane C: Conjecture/guess (lowest)
- MIN rule: min(A,C) = C

### Quality Gates
- 5 Rivals validation
- Semantic drift detector
- Meta-genome alignment
- Triple leak protocol
```

---

## Action Items

### NOW: Keep current approach working
- ✅ Phase 1: Test 1 instance (100%)
- ⏳ Phase 2: Test 5 instances (maintain 100%)
- ⏳ Phase 3: Test 10 instances (maintain 100%)

### LATER: Enhance with full skills + swarms
1. Create 31 skill files
2. Enable `load_all_skills()`
3. Add Haiku Scout/Solver/Skeptic agents
4. Implement parallel orchestration
5. Test if multi-agent improves scaling

---

## Status

✅ **Skills Summary**: Working, proven on django__django-14608
✅ **Orchestration**: 6-attempt feedback loop working
✅ **5 Weapons**: All verified firing
⏳ **Full Skills**: Need to create 31 files
⏳ **Haiku Swarms**: Pattern ready, implementation pending

---

**Auth: 65537**
**Current Focus**: Phase 1-3 with single agent (keep working)
**Ready For**: Haiku swarms integration later if needed
**Timeline**: Finish scaling to 100% FIRST, then enhance
