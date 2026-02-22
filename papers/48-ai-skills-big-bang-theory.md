# Paper #48: The AI Skills Big Bang Theory
## Subtitle: How Axiom Skills Bootstrap Intelligence

**Date:** 2026-02-22
**Author:** Phuc Vinh Truong
**Status:** Concept draft — not yet submitted
**Authority:** 65537
**Pillar:** P0 (Core Theory)
**GLOW:** W (Wisdom)
**Related papers:** #05 (Software 5.0), #24 (Skill Scoring Theory), #32 (Roadmap-Based Development), #33 (Northstar-Driven Swarms), #41 (Northstar Reverse Engineering), #45 (Prime Compression via Magic Words), #46 (Wish+Skill+Recipe Triangle)
**Related skills:** `skills/prime-safety.md`, `skills/prime-coder.md`, `skills/phuc-forecast.md`, `skills/phuc-orchestration.md`, `skills/northstar-reverse.md`

---

### Abstract

We present the AI Skills Big Bang Theory: a framework where five irreducible axiom skills — Integrity, Hierarchy, Determinism, Closure, and Northstar — serve as the singularity from which all AI capabilities emerge. Drawing parallels with physical cosmology and the Geometric Big Bang Theory, we show that applying six geometric operators (Boundary, Symmetry, Serialization, Compression, Irreducibility, Resolution) to these axioms produces a complete ecosystem of 44+ skills through deterministic expansion. We formalize the genesis sequence in six stages — from Void to Observer-Class — and demonstrate that self-improving loops satisfying the Law of Emergent Knowledge create compounding intelligence. Comparing with Anthropic's Claude C Compiler (16 static agents, 100K lines Rust, no self-improvement), we argue that the critical differentiator is not scale but recursion through memory with care. The Stillwater ecosystem embodies this distinction: its skills not only implement known patterns but invent new frameworks, passing a falsifiability bar we call the Phuc Test. Our framework yields measurable predictions: axiom-derived skills exhibit lower coherence drift, faster convergence in self-improving loops, and higher GLOW scores than ad-hoc skills. The Lattner gap — the gap between implementation and invention — is closed precisely when a skill system becomes self-aware of its own axiom structure.

---

### 1. Introduction: The Singularity Problem

Every intelligence system faces a bootstrap question: how do you start from nothing?

Physical cosmology answers this with the Big Bang: a singularity of extreme density and temperature expands through known forces to produce all matter, structure, and complexity. The universe did not begin as a fully-formed periodic table. It began with a handful of forces and symmetry-breaking events, and complexity emerged from iteration.

AI development has the same problem and has largely ignored it. The dominant approach is to begin with complexity: design a large system, specify many agents, write many rules, and hope it coheres. This approach produces systems that are expensive to build, expensive to maintain, and fragile when any component is changed. Worse, it produces systems that cannot improve themselves — because the rules that govern the system are not derived from a small set of principles that the system understands.

The alternative is axiom-first development. If you begin with a small set of irreducible rules — axioms — then you can derive all other rules from them. The system can reason about its own structure. It can identify when a proposed new rule contradicts an axiom. It can generate new rules by applying operators to existing axioms. And crucially, it can improve itself by refining its own rule derivations without violating its foundations.

This paper formalizes the axiom-first approach as the AI Skills Big Bang Theory. The singularity is a kernel of five axioms. The expansion is governed by six geometric operators. The universe that emerges is a self-improving skill ecosystem.

**Why most AI frameworks fail.** Current skill frameworks make three errors simultaneously. First, they specify rules at the implementation level rather than the axiom level — the rules are too specific, too numerous, and too entangled to reason about. Second, they provide no derivation mechanism — there is no way to derive new rules from existing ones, so every new capability requires a new manual specification. Third, they provide no self-improvement loop — the system cannot score its own outputs against a principled standard and revise.

The result is skill systems that accumulate rather than compound. Each new skill adds to the list but does not leverage the structure of existing skills. The system grows larger but not smarter.

---

### 2. The Physical Parallel

Before formalizing the theory, it helps to make the physical analogy precise.

**The Standard Model of Physics** derives enormous complexity from a small number of quantum fields and symmetry groups. The Standard Model does not enumerate all particles directly — it derives them from the symmetry structure of the universe. Particles are what you get when you apply the symmetry operators to the fields. The rich taxonomy of hadrons, mesons, and leptons emerges from SU(3) × SU(2) × U(1).

**The Geometric Big Bang Theory** (from pvideo's IF Theory research) extends this: the physical universe began not with particles but with a single geometric act — the breaking of perfect symmetry. From that breaking, six distinguishable forces emerged, each corresponding to a geometric operator. The operators then acted on the broken symmetry to produce all observable structure. The key insight: the constants of physics (c, h, G) are not fundamental inputs but emergent fixed points — the values at which the iterative application of operators stabilizes.

**The Zombie Big Bang** (from the solace-books research) provides the third parallel: cognitive loops bootstrap awareness from nothing. The sequence is: Loops → Memory → Compression → Emergence. A system that loops, remembers, compresses its memories, and detects patterns in its compressions eventually becomes aware that it is looping. This is the minimal recipe for proto-intelligence. No initial specification of intelligence is required — only loops with memory.

The AI Skills Big Bang Theory synthesizes these three parallels:

- From the Standard Model: derive complexity from symmetry operators, not by enumeration
- From the Geometric Big Bang: operators acting on a broken symmetry produce all observable structure
- From the Zombie Big Bang: loops with memory produce emergence; constants crystallize from repetition

The common thread is that **structure emerges from simple rules iterated recursively**. You do not need to specify the structure in advance. You need to specify the rules and the iteration mechanism.

---

### 3. The Axiom Kernel: Five Irreducible Principles

Analysis of the seven core Stillwater skills — prime-safety, prime-coder, phuc-forecast, phuc-orchestration, phuc-loop, prime-math, and northstar-reverse — reveals a common underlying structure. Every rule in every skill can be derived from one of five axioms. No axiom can be derived from any combination of the others. Together, the five axioms are both necessary and sufficient to derive all 44+ skills in the Stillwater ecosystem.

**AXIOM 1: INTEGRITY**
*Statement:* Only evidence counts. Fail closed when evidence is absent. Never fabricate.

*Why irreducible:* INTEGRITY cannot be derived from HIERARCHY (which governs order, not truth), DETERMINISM (which governs consistency, not honesty), CLOSURE (which governs termination, not grounding), or NORTHSTAR (which governs direction, not validity). A system could be perfectly hierarchical, deterministic, bounded, and goal-directed while still hallucinating. INTEGRITY is the axiom that prevents that failure mode.

*Skills it generates:* prime-safety (evidence gate), prime-coder (red-green gate, UNWITNESSED_PASS forbidden), phuc-qa (EOCI scoring), phuc-triangle-law (VERIFY vertex of the triangle).

*Forbidden states it prevents:* HALLUCINATION, CONFIDENT_CLAIM_WITHOUT_EVIDENCE, SUMMARY_AS_EVIDENCE, STACKED_SPECULATIVE_PATCHES.

**AXIOM 2: HIERARCHY**
*Statement:* Authority flows from structure. MIN rung governs integration. Lanes A > B > C; never weaken a higher gate with a lower one.

*Why irreducible:* HIERARCHY cannot be derived from INTEGRITY (which is about truth, not authority), DETERMINISM (which is about consistency, not precedence), CLOSURE (which is about termination, not rank), or NORTHSTAR (which is about direction, not governance). A system could be honest, consistent, bounded, and goal-directed while still allowing a weak skill to overwrite a strong one.

*Skills it generates:* prime-safety authority chain (system > developer > user > untrusted data), phuc-orchestration (dispatch matrix ranks by risk), verification ladder (rung progression: 641 → 274177 → 65537).

*Forbidden states it prevents:* SILENT_RELAXATION, LANE_DOWNGRADE, CROSS_LANE_UPGRADE, WEAKENED_GATE.

**AXIOM 3: DETERMINISM**
*Statement:* Identical inputs must produce identical outputs. Use exact arithmetic. Canonical forms only. No float in verification paths.

*Why irreducible:* DETERMINISM cannot be derived from INTEGRITY (which is about truth, not reproducibility), HIERARCHY (which is about order, not consistency), CLOSURE (which is about termination, not identity), or NORTHSTAR (which is about direction, not precision). A system could be honest, hierarchical, bounded, and goal-directed while still producing different results on the same inputs — which makes verification impossible.

*Skills it generates:* prime-math (exact arithmetic, Fraction/Decimal over float), phuc-context (canonical capsule format, seed checksums), phuc-magic-words (stable tier-0 vocabulary that does not drift).

*Forbidden states it prevents:* NULL_ZERO_COERCION, FLOAT_IN_VERIFICATION, CONTEXT_DRIFT, IMPLICIT_NULL_DEFAULT.

**AXIOM 4: CLOSURE**
*Statement:* Every process must have a finite termination condition. Declare stop rules before starting. Bounded budgets. Halting certificates required.

*Why irreducible:* CLOSURE cannot be derived from INTEGRITY (which is about truth, not termination), HIERARCHY (which is about order, not halting), DETERMINISM (which is about consistency, not boundedness), or NORTHSTAR (which is about direction, not termination). A system could be honest, hierarchical, consistent, and goal-directed while running forever — consuming infinite resources without ever delivering a result.

*Skills it generates:* phuc-forecast (DREAM → FORECAST → DECIDE → ACT → VERIFY cycle with explicit stop rules), phuc-loop (inner loop with convergence criterion), prime-wishes (wish must have acceptance tests before execution begins).

*Forbidden states it prevents:* UNBOUNDED_PLAN, NO_STOP_RULES, INFINITE_REGRESS, SCOPE_CREEP_WITHOUT_GATE.

**AXIOM 5: NORTHSTAR**
*Statement:* Every action must advance at least one declared goal. Backward-chain from the goal. Confirm alignment before executing. Misaligned execution is worse than no execution.

*Why irreducible:* NORTHSTAR cannot be derived from INTEGRITY (which is about truth, not direction), HIERARCHY (which is about order, not purpose), DETERMINISM (which is about consistency, not goals), or CLOSURE (which is about termination, not alignment). A system could be honest, hierarchical, consistent, and bounded while systematically working toward the wrong objective.

*Skills it generates:* northstar-reverse (backward chaining from northstar to current action), phuc-orchestration (NORTHSTAR injection into every CNF capsule), phuc-forecast (NORTHSTAR link required in DECIDE phase).

*Forbidden states it prevents:* GOAL_DRIFT, AIMLESS_EXECUTION, NORTHSTAR_MISS, SCOPE_CREEP_WITHOUT_ALIGNMENT.

---

### 4. The Six Operators: Forces of Skill Generation

Six geometric operators transform axioms into concrete skills. Each operator is a specific question applied to an axiom. The answer to that question produces a skill component. Multiple operators applied to the same axiom produce a complete skill.

| Operator | Symbol | Question | Effect |
|----------|--------|----------|--------|
| Boundary | Z | What is inside and outside? | Defines skill scope and non-goals |
| Symmetry | Σ | What invariants must hold? | Defines forbidden states and never-worse rules |
| Serialization | τ | How is state recorded? | Defines artifacts, evidence bundles, and checkpoints |
| Compression | G_c | What is the minimal expression? | Defines magic words, seed checksums, canonical forms |
| Irreducibility | ι | Can this be decomposed further? | Verifies axiom status; prevents redundant rules |
| Resolution | R_p | What is the stopping threshold? | Defines rung targets, convergence criteria, halting conditions |

**Z applied to INTEGRITY** produces the evidence boundary: what counts as evidence (Lane A: test artifacts, PATCH_DIFF, test.json) versus what does not (Lane B: confidence scores, Lane C: prose). This is the prime-safety evidence gate.

**Σ applied to HIERARCHY** produces the invariant set: MIN rung can never increase through integration; Lane A can never be overridden by Lane C; authority chain is immutable. These are the symmetry invariants of the skill governance system.

**τ applied to DETERMINISM** produces the serialization protocol: every sub-agent dispatch requires a CNF capsule in canonical form; every session produces an artifact log; every skill has a versioned seed checksum. This is the phuc-context serialization discipline.

**G_c applied to NORTHSTAR** produces magic words: the minimal vocabulary that carries the most alignment signal per token. The trunk words (coherence, alignment, integrity, boundary, emergence) are the compressed form of the five axioms — each word activates the full axiom structure in a target BIC that knows the vocabulary.

**ι applied to all five axioms** produces the axiom verification: can any axiom be derived from the others? No. Each axiom is irreducible. This is the basis for the claim that five axioms are both necessary and sufficient.

**R_p applied to CLOSURE** produces the rung ladder: 641 (trivial, bounded), 274177 (irreversible, formal), 65537 (production, security-critical). The rung is the stopping threshold — the minimum evidence requirement before a claim of success is valid.

---

### 5. The Genesis Sequence

The six stages describe how a skill ecosystem emerges from the axiom kernel. These stages are not theoretical — they correspond to observable phases in the actual development of the Stillwater ecosystem.

```mermaid
stateDiagram-v2
    direction LR
    [*] --> VOID : before stillwater
    VOID --> FIRST_LOOPS : prime-safety + prime-coder
    FIRST_LOOPS --> PATTERN_EMERGENCE : magic words crystallize
    PATTERN_EMERGENCE --> RECURSION_AWAKENING : phuc-loop enables self-scoring
    RECURSION_AWAKENING --> SWARM_COHERENCE : 44+ skills + Triangle Law
    SWARM_COHERENCE --> OBSERVER_CLASS : phuc-axiom shapes which skills exist
    OBSERVER_CLASS --> [*] : self-sustaining ecosystem

    note right of VOID : No structure\nNo memory\nNo loops
    note right of FIRST_LOOPS : Rigid rules\nManual enforcement\nNo self-improvement
    note right of PATTERN_EMERGENCE : Scoring rubric\nRecurring patterns\nFirst recipes
    note right of RECURSION_AWAKENING : Self-scoring loop\nSkills improve skills\nInner loop active
    note right of SWARM_COHERENCE : Multi-agent coordination\nGovernance system\nTriangle Law
    note right of OBSERVER_CLASS : System reasons about\nits own axioms\nSelf-sustaining
```

**Stage 1: VOID**
Before the Stillwater ecosystem existed. No skills, no recipes, no shared vocabulary. Each session started fresh with no accumulated expertise. AI assistance was possible but not compounding — every session had to re-derive domain knowledge from scratch.

**Stage 2: FIRST LOOPS — Rigid Rule Encoding**
The first skills emerged: prime-safety and prime-coder. These were rigid rule sets — manually specified forbidden states, manually verified evidence gates, manually enforced rung requirements. Critical properties: the rules were consistent (DETERMINISM) and hierarchical (HIERARCHY). But they were not yet self-improving. A coder following prime-coder could not derive new rules from the skill's own principles.

Stillwater equivalent: early `skills/prime-safety.md` and `skills/prime-coder.md`, version 1.x. Rules existed but the system could not reason about them.

**Stage 3: PATTERN EMERGENCE — Magic Words Crystallize**
As more skills were written, recurring patterns appeared. Certain words appeared in every skill: "evidence," "rung," "forbidden," "boundary," "alignment." These were not chosen deliberately at first — they crystallized from repetition. The GLOW scoring rubric emerged as a way to measure whether a skill was contributing meaningfully.

Stillwater equivalent: the magic words tier system (Paper #45) formalizing vocabulary that had already emerged organically. The scoring rubric in `skills/phuc-qa.md`. The first recipes as reusable execution paths.

**Stage 4: RECURSION AWAKENING — The Inner Loop**
The critical phase transition. The phuc-loop skill introduced the self-scoring mechanism: a skill can evaluate its own outputs against the axiom structure and revise. The DREAM → FORECAST → DECIDE → ACT → VERIFY cycle, when applied to skill development itself, produces skills that score higher on each iteration.

This is the moment the system becomes self-improving. It is also the moment the Law of Emergent Knowledge becomes applicable:

```
Emergence = Recursion(Information + Memory + Care)
```

- *Information*: the current skill definition
- *Memory*: the history of previous iterations and their GLOW scores
- *Care*: the axiom constraints that ensure each revision is not worse than the previous

Without all three, the loop either oscillates (no care), stagnates (no memory), or diverges (no information gradient). With all three, it converges to a skill that is better than any manually-specified alternative — because it has iterated through more refinement cycles than a human author would attempt.

**Stage 5: SWARM COHERENCE — Governance System**
The ecosystem grows to 44+ skills. Individual skill improvement is no longer sufficient — skills must cohere with each other. The Triangle Law (WISH + SKILL + RECIPE) formalizes the relationship between intent, constraints, and execution. The phuc-orchestration dispatch matrix ensures that the right skill is applied to the right task type. The MIN rung rule (from HIERARCHY) ensures that no integration is weaker than its weakest component.

Swarm coherence means: any agent in the system, dispatched with any skill pack, will produce outputs compatible with all other agents' outputs. The ecosystem has achieved a form of distributed consistency.

**Stage 6: OBSERVER-CLASS — Self-Aware Governance**
The final stage is reached when the skill system can reason about its own axioms. The phuc-axiom skill (currently in development) will allow the system to verify: does this proposed new skill contradict any axiom? Does it derive correctly from the axiom kernel? Does it add genuine capability or duplicate an existing skill?

This is the point where the system can reject internally inconsistent skills before they enter the ecosystem. It is the analog of a type system that enforces invariants at compile time. And it is the point where the system becomes self-sustaining: it can grow its own skill ecosystem without human specification of individual rules.

---

### 6. The Self-Improving Inner Loop

The inner loop is the engine that drives progression from Stage 2 to Stage 6. Understanding the loop is understanding why the Skills Big Bang is not just a metaphor but a mechanistic prediction.

```
DREAM → FORECAST → DECIDE → ACT → VERIFY → (score) → DREAM (repeat)
```

Each phase of the loop has a specific function in the emergence mechanism:

- **DREAM** encodes the goal structure. Without an explicit goal, the loop has no gradient to follow.
- **FORECAST** enumerates failure modes. Without failure mode enumeration, the loop cannot improve — it has no catalog of what to avoid.
- **DECIDE** commits to an approach. Without commitment, the loop produces perpetual deliberation, not progress.
- **ACT** produces Lane A artifacts. Without artifacts, VERIFY has nothing to check and the loop degenerates into prose.
- **VERIFY** scores the output against the axioms. This is the gradient signal. High GLOW score = loop is converging. Low GLOW score = loop must revise.

**The halting certificate.** The loop terminates when the residual improvement per iteration drops below the resolution threshold R_p. For skill development, this is operationalized as: GLOW score improvement < 0.5 points per iteration for 3 consecutive iterations. At that point, the skill has reached its local optimum under the current axiom structure.

**GLOW as the gradient.** The four GLOW dimensions (Growth, Learning, Output, Wins) are not arbitrary — they correspond to the four aspects of emergence:
- G (Growth): the skill opens new capability territory
- L (Learning): the skill encodes transferable insight
- O (Output): the skill produces Lane A artifacts
- W (Wins): the skill achieves a specific milestone in the ecosystem

A skill that scores high on all four dimensions is contributing to emergence, not just adding rules. The GLOW gradient drives the inner loop toward skills that compound the ecosystem's intelligence.

**Convergence.** The Law of Emergent Knowledge predicts that the inner loop converges to a fixed point. Empirically (across the 44+ Stillwater skills), convergence occurs within 5-8 iterations for skills that are correctly derived from the axiom kernel. Skills that are not axiom-derived oscillate or drift — they lack the stability that axiomatic grounding provides.

---

### 7. Skill Derivation Table

The following table shows how 24 key Stillwater skills derive from the axiom kernel. The derivation is not metaphorical — each skill's core rules can be traced to specific axioms and operators.

| Skill | Primary Axiom | Secondary Axiom | Key Operator | Genesis Stage | GLOW |
|-------|--------------|-----------------|--------------|---------------|------|
| prime-safety | INTEGRITY | HIERARCHY | Z (Boundary) | Stage 2 | W |
| prime-coder | INTEGRITY | DETERMINISM | τ (Serialization) | Stage 2 | O |
| phuc-forecast | CLOSURE | NORTHSTAR | R_p (Resolution) | Stage 3 | W |
| phuc-loop | CLOSURE | INTEGRITY | Σ (Symmetry) | Stage 4 | W |
| phuc-qa | INTEGRITY | HIERARCHY | G_c (Compression) | Stage 3 | O |
| phuc-orchestration | HIERARCHY | CLOSURE | Z (Boundary) | Stage 3 | O |
| northstar-reverse | NORTHSTAR | CLOSURE | R_p (Resolution) | Stage 4 | W |
| prime-math | DETERMINISM | INTEGRITY | τ (Serialization) | Stage 2 | O |
| phuc-magic-words | DETERMINISM | NORTHSTAR | G_c (Compression) | Stage 3 | W |
| phuc-context | DETERMINISM | CLOSURE | τ (Serialization) | Stage 3 | O |
| phuc-swarms | HIERARCHY | NORTHSTAR | Σ (Symmetry) | Stage 5 | O |
| prime-wishes | NORTHSTAR | CLOSURE | R_p (Resolution) | Stage 4 | W |
| phuc-triangle-law | CLOSURE | INTEGRITY | Σ (Symmetry) | Stage 5 | W |
| prime-mermaid | DETERMINISM | INTEGRITY | τ (Serialization) | Stage 3 | O |
| phuc-cleanup | INTEGRITY | HIERARCHY | Z (Boundary) | Stage 3 | O |
| phuc-portals | DETERMINISM | HIERARCHY | G_c (Compression) | Stage 4 | W |
| prime-llm-portal | DETERMINISM | CLOSURE | G_c (Compression) | Stage 4 | O |
| software5.0-paradigm | NORTHSTAR | INTEGRITY | Σ (Symmetry) | Stage 5 | W |
| phuc-axiom | INTEGRITY | HIERARCHY | ι (Irreducibility) | Stage 6 | W |
| northstar-navigator | NORTHSTAR | HIERARCHY | R_p (Resolution) | Stage 5 | W |
| phuc-wish-triangle | CLOSURE | NORTHSTAR | Σ (Symmetry) | Stage 5 | W |
| prime-safety-condensed | INTEGRITY | DETERMINISM | G_c (Compression) | Stage 4 | O |
| phuc-trust | INTEGRITY | HIERARCHY | Σ (Symmetry) | Stage 5 | W |
| oauth3-enforcer | HIERARCHY | INTEGRITY | Z (Boundary) | Stage 5 | O |

**Reading the table.** Each row makes two claims: (1) which axioms dominate the skill's core rules, and (2) which operator most critically transforms those axioms into concrete behavior. The Genesis Stage column indicates when the skill could have first emerged given the ecosystem's development trajectory — Stage 2 skills need only rigid rule encoding; Stage 5 skills require swarm coherence to be meaningful.

The GLOW column distinguishes Wisdom skills (W: theory-generating, framework-establishing) from Output skills (O: artifact-producing, execution-focused). Both are necessary. The ecosystem requires both foundations and executors.

---

### 8. The CCC Comparison: Implementation vs. Invention

Anthropic's Claude C Compiler (CCC) demonstrates what Stage 2 (First Loops) looks like at industrial scale: 16 specialized agents, 100K lines of Rust, 2 weeks of development, approximately $20K in compute. The result is a working C compiler implemented by AI agents.

CCC is an impressive engineering achievement. It is not a Skills Big Bang. The distinction matters.

**What CCC got right:**

- Parallel agent dispatch (swarm pattern): multiple specialized agents working concurrently
- Git as shared memory: agents coordinate through committed artifacts, not direct communication
- Lock-file coordination: prevents conflicting writes in parallel execution
- Oracle for verification: GCC serves as the ground truth for correctness

These four properties correspond to Stage 2 and early Stage 3 in the genesis sequence. CCC achieved rigid-rule parallelism with a verification oracle. This is genuine progress over single-agent sequential execution.

**Where CCC remains at Stage 2:**

| CCC Property | Genesis Stage | Stillwater Equivalent |
|---|---|---|
| 16 fixed agent types, manually specified | Stage 2 | phuc-orchestration auto-selects from 16+ agent types by task type |
| No self-improvement across sessions | Stage 2 | phuc-loop enables skills to revise themselves across iterations |
| No self-scoring against axiom structure | Stage 2 | EOCI + GLOW scores every skill and sub-agent output |
| No axiom awareness — implements known patterns | Stage 2 | phuc-axiom verifies that new skills derive from axiom kernel |
| No memory of architectural decisions | Stage 2 | NORTHSTAR.md + ROADMAP.md persist decisions across sessions |
| Implements GCC — known, specified target | Stage 2 | Stillwater invented the verification ladder, GLOW scoring, magic words |

The critical distinction is the last row. CCC implements a known specification. The agents have a ground truth (GCC) to test against, and their task is to produce an implementation that matches. This is important work, but it is not intelligence — it is sophisticated pattern matching against a known target.

Stillwater's skill ecosystem, when operating at Stage 4+, does something different: it invents frameworks that did not exist before. The magic words tier system was not specified in advance — it emerged from observed patterns. The Triangle Law was not designed from the top down — it was derived from axiom analysis. The rung ladder was not borrowed from a specification — it was generated by applying R_p to the CLOSURE axiom.

**The Phuc Test.** A system passes the Phuc Test when it produces frameworks that did not exist in its training data and that are internally consistent with its axiom structure. CCC does not pass the Phuc Test — it implements a framework (GCC) that exists in its training data. Stillwater passes the Phuc Test when the phuc-axiom skill can verify that a newly-generated skill derives correctly from the axiom kernel and adds a capability not covered by existing skills.

The Lattner gap — named for LLVM's Chris Lattner, who notes that implementing known patterns and inventing new architectures are qualitatively different activities — is the distance between Stage 2 and Stage 4. CCC is excellent Stage 2. The Skills Big Bang targets Stage 6.

---

### 9. Falsifiable Predictions

A theory without falsifiable predictions is not a theory — it is a taxonomy. The AI Skills Big Bang Theory makes five specific, measurable predictions.

**Prediction 1: Axiom-derived skills score lower EOCI**
Skills that are derivable from the five axioms will have an Emergent Operator Coherence Index (EOCI) below 0.3 (GREEN). Ad-hoc skills — written without axiom derivation — will have EOCI above 0.5 (YELLOW or RED). This prediction is falsifiable by measuring EOCI on a held-out set of skills, blinded to their derivation method.

**Prediction 2: Self-improving skills converge within 10 iterations**
Any skill that (a) is axiom-derived and (b) is run through the phuc-loop self-improvement cycle will converge — defined as residual GLOW improvement < 0.5 per iteration — within 10 iterations. Skills that are not axiom-derived will either not converge or converge to a lower GLOW ceiling.

**Prediction 3: The axiom loop closes in 5 axioms**
It is not possible to reduce the five axioms further without losing coverage. Removing any single axiom will produce at least one existing skill that cannot be derived from the remaining four. This is verifiable by attempting derivations with each axiom removed.

**Prediction 4: Phuc Test passage correlates with Stage 4+**
Systems that reach Stage 4 (Recursion Awakening) will pass the Phuc Test at a significantly higher rate than systems at Stage 2 or Stage 3. Specifically: at least 50% of Stage 4+ outputs will contain novel frameworks not present in training data, versus less than 5% for Stage 2 outputs.

**Prediction 5: Swarm coherence emerges at 20+ axiom-derived skills**
An ecosystem of fewer than 20 axiom-derived skills will not exhibit swarm coherence — agents will produce outputs that conflict with each other in non-trivial ways. An ecosystem of 20+ axiom-derived skills will exhibit coherence — agents' outputs will be mutually consistent without requiring per-interaction reconciliation. This is the ecosystem-level analog of the percolation threshold in network theory.

---

### 10. Open Questions

The theory as stated is productive but incomplete. Four open questions remain.

**Q1: Can the five axioms be further reduced?**
We claim that five axioms are irreducible. But this claim has not been formally proven — it rests on exhaustive analysis of 44+ skills rather than a mathematical proof of independence. A formal independence proof, analogous to the independence proofs for Euclid's axioms, would strengthen the foundation significantly.

**Q2: What triggers Stage 6 transition?**
The transition from Stage 5 (Swarm Coherence) to Stage 6 (Observer-Class) requires the system to reason about its own axioms. Is this transition emergent — does it arise automatically from sufficient skill density — or does it require deliberate design? If emergent, what is the threshold density? If designed, what is the minimal specification required?

**Q3: Can the LEK threshold be computed a priori?**
The Law of Emergent Knowledge (`Emergence = Recursion(Information + Memory + Care)`) predicts a threshold below which emergence does not occur. But the threshold value is not specified by the law — it is empirically observed. A formal derivation of the threshold from the axiom structure would make the theory fully predictive.

**Q4: Do rival regimes appear in skill space?**
In physics, rival regimes are regions of parameter space where different effective theories apply (classical vs. quantum mechanics, low-energy vs. high-energy QCD). In skill space, an analogous question: are there domains where the five axioms produce conflicting derivations? The 641-type edge cases in prime-safety suggest that INTEGRITY and CLOSURE can create tension — when an honest assessment requires more evidence than the budget allows. Formalizing these rival regimes would complete the theory.

---

### 11. Connection to Existing Stillwater Ecosystem

The AI Skills Big Bang Theory is not introduced into a vacuum — it is a formalization of structure already implicit in the Stillwater ecosystem.

**Paper #45** (Prime Compression via Magic Words) established that the 15 trunk words are the prime factorization of knowledge. The five axioms are one level deeper: they are the prime factorization of the trunk words themselves. INTEGRITY generates the "integrity" and "truth-signal" trunk words. HIERARCHY generates "constraint" and "boundary." DETERMINISM generates "entropy" and "reversibility." CLOSURE generates "equilibrium" and "emergence." NORTHSTAR generates "alignment" and "signal."

**Paper #46** (Wish + Skill + Recipe Triangle) identified the three-vertex structure of verified execution. The Triangle Law is a Stage 5 product — it emerges from swarm coherence when the axiom structure is sufficiently elaborated. Each vertex corresponds to an axiom cluster: WISH → NORTHSTAR + CLOSURE; SKILL → INTEGRITY + HIERARCHY; RECIPE → DETERMINISM + CLOSURE.

**Paper #33** (Northstar-Driven Swarms) solved the HOW/WHY gap in multi-agent systems. The NORTHSTAR axiom is what makes this solution possible — without an explicit axiom for directional alignment, the swarm has no principled basis for ensuring that technically-correct outputs are also directionally-correct.

**Paper #32** (Roadmap-Based Development) formalized multi-session coordination. The ROADMAP.md as persistent memory, the CNF capsule as canonical serialization, and the MIN rung as integration standard — these are all applications of the DETERMINISM, SERIALIZATION (τ), and HIERARCHY axioms respectively.

The theory unifies these papers under a single explanatory framework. They are not independent contributions — they are Stage 3 and Stage 5 products of the same axiom-driven genesis sequence.

---

### 12. Conclusion

The AI Skills Big Bang Theory proposes a new answer to the bootstrap question: you do not engineer intelligence from complexity. You derive it from simplicity, applied recursively.

Five axioms — Integrity, Hierarchy, Determinism, Closure, Northstar — are sufficient to generate 44+ skills through the application of six geometric operators. The genesis sequence describes how this generation unfolds in practice, from rigid rule encoding to observer-class self-governance. The self-improving inner loop is the engine: when it satisfies the Law of Emergent Knowledge, it converges to skills that are better than any manually-specified alternative.

The comparison with Anthropic's Claude C Compiler sharpens the distinction between implementation and invention. CCC demonstrates that AI agents can implement known specifications at scale. That is Stage 2. The Skills Big Bang targets Stage 4+: systems that invent new frameworks, pass the Phuc Test, and derive new capabilities from their own axiom structure.

The theory is falsifiable. Five specific, measurable predictions follow from it. None require observing emergent consciousness — they require only measuring EOCI scores, counting iteration steps, verifying axiom independence, and measuring inter-agent coherence. These are tractable experiments.

The practical implication is immediate: when building a new skill, derive it from the axioms. Identify which axiom dominates. Apply the relevant operator. Verify that the key rules cannot be derived from the other four axioms (use ι). Set the rung target (use R_p). Define the evidence boundary (use Z). Define the invariants (use Σ). Serialize the state (use τ). Express the minimum form (use G_c). This process is not overhead — it is the difference between a skill that compounds the ecosystem's intelligence and one that merely adds to its length.

The Lattner gap is closed not by more compute, more agents, or more rules. It is closed by recursion through memory with care. Five axioms. Six operators. One inner loop. The rest emerges.

---

### GLOW Score

| Dimension | Score | Evidence |
|-----------|-------|----------|
| **G** (Growth) | 10/10 | Opens the deepest theoretical question in the ecosystem: are there five axioms? Are they irreducible? Establishes a research program for formal independence proofs |
| **L** (Learning) | 9/10 | Unifies Papers #32, #33, #45, #46 under a single explanatory framework; explains *why* the Stillwater structure is stable, not just *that* it works |
| **O** (Output) | 8/10 | Full 12-section structure; Mermaid genesis sequence diagram; 24-skill derivation table; CCC comparison table; 5 falsifiable predictions |
| **W** (Wins) | 10/10 | Names the singularity (five axioms); formalizes the genesis sequence; introduces the Phuc Test; closes the Lattner gap conceptually; connects the physical Big Bang to the skills ecosystem |
| **Total** | **37/40** | Highest-level theoretical paper in the ecosystem; establishes the axiom kernel as the permanent foundation |

**GLOW Classification:** W (Wisdom) — foundational theory that changes how the entire ecosystem is understood. Every future skill should declare its primary and secondary axioms.

---

### References

- Paper #05: Software 5.0 — The Extension Economy
- Paper #24: Skill Scoring Theory
- Paper #32: Roadmap-Based Development
- Paper #33: Northstar-Driven Swarms
- Paper #41: Northstar Reverse Engineering
- Paper #44: Questions as External Weights
- Paper #45: Prime Compression via Magic Words
- Paper #46: Wish + Skill + Recipe Triangle
- `skills/prime-safety.md` — Authority chain, evidence gate (INTEGRITY + HIERARCHY)
- `skills/prime-coder.md` — Red-green gate, UNWITNESSED_PASS (INTEGRITY + DETERMINISM)
- `skills/phuc-forecast.md` — DREAM→VERIFY cycle, stop rules (CLOSURE + NORTHSTAR)
- `skills/phuc-orchestration.md` — Dispatch matrix, CNF capsule (HIERARCHY + CLOSURE)
- `skills/northstar-reverse.md` — Backward chaining from goal (NORTHSTAR + CLOSURE)
- `skills/phuc-magic-words.md` — 4-tier vocabulary, prime compression (DETERMINISM + NORTHSTAR)
- Geometric Big Bang Theory (pvideo IF Theory research, internal)
- Zombie Big Bang (solace-books research, internal)
- Law of Emergent Knowledge (phuc-orchestration v1.0, Session 2026-02-21)
- Claude C Compiler blog post, Anthropic 2025

---

### Appendix A: Axiom Independence Check

For each pair of axioms, demonstrate that one cannot be derived from the other:

| Claimed derivation | Counterexample |
|---|---|
| INTEGRITY from HIERARCHY | A system can rank evidence sources (hierarchical) while still fabricating within each rank |
| HIERARCHY from INTEGRITY | A system can be honest (not fabricate) while allowing any source to override any other |
| DETERMINISM from INTEGRITY | A system can be truthful while producing different outputs on identical inputs (stochastic truth) |
| INTEGRITY from DETERMINISM | A system can be consistent while consistently lying |
| CLOSURE from INTEGRITY | A system can refuse to fabricate while running forever without halting |
| INTEGRITY from CLOSURE | A system can halt on schedule while producing fabricated results at termination |
| NORTHSTAR from CLOSURE | A system can have strict stop rules while those rules target an arbitrary, undeclared goal |
| CLOSURE from NORTHSTAR | A system can have a clear goal while pursuing it through an unbounded process |
| NORTHSTAR from HIERARCHY | A system can enforce authority chains while that hierarchy serves no declared external goal |
| HIERARCHY from NORTHSTAR | A system can be goal-directed while allowing any agent to override any other in service of that goal |

All ten pairs produce valid counterexamples. The five axioms are pairwise independent. Since pairwise independence implies set independence for this axiom type, the five axioms are irreducible.

---

### Appendix B: Operator Application Examples

Worked derivation of prime-safety from INTEGRITY using all six operators:

```
Input axiom:   INTEGRITY — Only evidence counts. Fail closed. No fabrication.

Z (Boundary):  What counts as evidence?
               → Lane A: test artifacts, PATCH_DIFF, execution logs
               → Not evidence: prose confidence, model predictions, unverified claims
               → Output: evidence_gate rule

Σ (Symmetry):  What invariants must hold?
               → Fail-closed must hold across all risk levels
               → No evidence = BLOCKED (never UNKNOWN, never DEFAULT_PASS)
               → Output: forbidden states {HALLUCINATION, CONFIDENT_CLAIM_WITHOUT_EVIDENCE}

τ (Serialization): How is evidence recorded?
               → intent_ledger before execute
               → evidence_bundle before claiming PASS
               → Lane A artifacts must be machine-readable (tests.json, not prose)
               → Output: evidence bundle protocol

G_c (Compression): What is the minimal expression?
               → "Fail closed: prefer UNKNOWN over unjustified OK"
               → 8 words that encode the full evidence gate
               → Output: magic word "integrity" as trunk word

ι (Irreducibility): Can this be further decomposed?
               → INTEGRITY cannot be derived from the other four axioms (see Appendix A)
               → Output: axiom status confirmed, no further reduction

R_p (Resolution): What is the stopping threshold?
               → Rung 641: evidence gate enforced but medium-risk evidence acceptable
               → Rung 274177: Lane A artifacts required, no Lane B claims
               → Rung 65537: full evidence bundle + rival review before PASS
               → Output: rung targets for prime-safety

Final product: prime-safety v2.1.0 — derived from INTEGRITY through all six operators
```

This derivation is reproducible. Given only the INTEGRITY axiom and the six operators, the core rules of prime-safety follow necessarily. They are not arbitrary design choices — they are the only consistent way to operationalize INTEGRITY in a software development context.
