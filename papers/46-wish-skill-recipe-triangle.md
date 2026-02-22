# Paper #46: The Wish + Skill + Recipe Triangle
## Subtitle: The Fundamental Execution Model of Software 5.0

**Date:** 2026-02-22
**Author:** Phuc Tran
**Status:** Concept draft — not yet submitted
**Pillar:** P0 (Core Theory)
**GLOW:** W (Wisdom)
**Related papers:** #05 (Software 5.0), #23 (Extension Economy), #24 (Skill Scoring Theory), #44 (Questions as External Weights), #41 (Northstar Reverse Engineering)

---

### Abstract

Every AI-assisted software execution — from a single CLI command to a multi-agent swarm — involves three invisible layers: the user's intent (what they want), the constraints that make execution safe and expert (how to do it correctly), and the proven workflow that carries the execution (how to do it reliably). When all three are explicit and aligned, execution is verified, intentional, and expert. When any one is missing, execution degrades predictably: without intent, execution is aimless; without constraints, execution is dangerous; without a proven workflow, execution is fragile. This paper names these three layers the Wish, Skill, and Recipe vertices of a triangle, proposes a formal completeness check, and argues that Combos — the W_ + R_ pairs with skill packs already in use in Stillwater — are the canonical implementation of this triangle.

---

### 1. Introduction: The Problem of Unconstrained Execution

The dominant paradigm for AI-assisted software development is the chat prompt: a user describes what they want, an AI generates code or commands, and the user runs them. This paradigm has a structural flaw. It conflates three distinct concerns into a single undifferentiated text stream:

- **What the user wants** (capability, acceptance criteria, non-goals)
- **How to do it correctly** (domain expertise, safety gates, null-handling rules)
- **How to execute it step by step** (proven workflow, checkpoints, artifacts)

When these concerns are conflated, the AI is simultaneously responsible for understanding intent, applying expertise, and choosing a workflow. It fails at all three. Intent is under-specified, so the AI guesses. Expertise is not encoded in the prompt, so the AI improvises. The workflow is invented fresh for each execution, so it differs between sessions, between models, and between prompts.

The result is what practitioners observe daily: AI-generated code that works on the first attempt but fails on edge cases; correct plans that are executed incorrectly; technically valid implementations that miss the user's actual intent. These failures do not arise from model capability limits. They arise from the absence of a structured execution model.

Software 5.0 proposes that the solution is to make all three concerns explicit before execution begins. The Wish + Skill + Recipe Triangle is the formal structure for doing so.

---

### 2. The Triangle Model: Three Vertices

The triangle has three vertices. Each is necessary. None is sufficient alone.

```
         WISH (user intent / northstar)
          /\
         /  \
        /    \
       /      \
      /________\
  SKILL         RECIPE
(constraints)   (execution)
```

**The WISH vertex** encodes what the user wants. A properly formed wish contains: a one-sentence capability statement with a measurable success condition, an explicit list of non-goals (what this execution does NOT do), forbidden states (conditions that must never occur), acceptance tests (verifiable conditions that confirm the wish was fulfilled), and a northstar link (which long-term goal this wish advances). The wish is the contract between the user and the execution system. Without it, the agent has no objective to optimize for — every choice is arbitrary.

The WISH vertex is the most commonly under-specified. Users rarely provide non-goals. They rarely name forbidden states. They rarely link their request to a larger strategic goal. The Stillwater prime-wishes skill exists precisely to enforce wish completeness before execution begins.

**The SKILL vertex** encodes how to constrain the work. Skills are the expert brain of the system. A skill encodes domain knowledge that would be re-derived poorly on every execution without it: what domain does this execution touch, what states must never be reached, what evidence is required before claiming success, how to distinguish null inputs from zero inputs, and what rung of verification is required. The coder skill encodes red-green discipline (a fix is only valid if the repro fails before and passes after). The cleanup skill encodes archive-before-delete discipline. The math skill encodes the exact arithmetic requirement (no floats in verification paths).

The SKILL vertex is the most commonly missing. When users submit tasks to AI agents without providing skill files, the agents make up their own domain conventions. These improvised conventions are inconsistent, unverifiable, and non-transferable between sessions.

**The RECIPE vertex** encodes how to execute step by step. Recipes are the muscle memory of the system. A recipe encodes a proven workflow as a node graph: L1 (CPU preprocessing), L2 (fast heuristics), L3 (LLM reasoning), L4 (tool execution), L5 (judge verification). Each node has inputs, outputs, and failure behavior. Each recipe has checkpoints where execution can be halted and verified, a rollback plan for when a node fails, and an artifact contract specifying what the recipe produces.

The RECIPE vertex is the most commonly replaced by improvisation. An agent given a wish and a skill will invent a path. The invented path differs each time. It will be clever but not proven. It will handle the happy path but miss edge cases. It will not produce the artifacts the wish acceptance tests require.

---

### 3. Triangle Law: What Happens When a Vertex Is Missing

The behavior of a two-vertex system is predictable. Each missing vertex produces a characteristic failure mode.

**WISH only** (no Skill, no Recipe): Unconstrained execution. The agent knows the goal but has no domain expertise and no proven path. It will attempt to fulfill the wish by any means, including unsafe ones. It will not know when it has succeeded — the wish has no acceptance tests — so it will over-execute until it runs out of tokens or produces something that looks done. This is the chat-prompt paradigm: goal-directed but unsafe and unreliable.

**SKILL only** (no Wish, no Recipe): Purposeless expertise. The skill constraints are applied to an undefined purpose. The agent has safety gates and forbidden states but no objective. Constraints in a vacuum — mathematically precise but strategically irrelevant. This occurs when a session loads skill files but does not receive a well-formed wish. The agent enforces correctness criteria on a task that has not been defined.

**RECIPE only** (no Wish, no Skill): Aimless execution. The agent follows the proven workflow but has no goal and no constraints. It will produce the recipe's artifacts, which may not be what the user wants. And it will do so without domain expertise, so when the recipe encounters an edge case outside its happy path, it will fail without guidance.

**WISH + SKILL** (no Recipe): Expert knowledge of the goal, but the path is improvised each time. This is better than the above cases — the agent will not be unsafe or aimless — but it will be slow and inconsistent. Different sessions produce different execution paths for identical wishes. The expertise encoded in the skill cannot be applied to a reproducible workflow, so it is applied inconsistently.

**WISH + RECIPE** (no Skill): Reliable execution of the wrong thing. The proven workflow will run reliably, but it will not handle edge cases correctly. The recipe was written for a world where domain expertise guides the execution. Without it, the recipe executes outside its safety envelope. It will succeed on normal inputs and fail in unpredictable ways on boundary conditions.

**SKILL + RECIPE** (no Wish): Expert, reliable execution without purpose. This is the inverse of the aimless recipe case. The execution is both safe (skill constraints) and reliable (proven workflow), but it has no objective. The agent produces artifacts nobody asked for, following constraints that are not connected to any user goal.

**WISH + SKILL + RECIPE**: Verified, intentional, expert execution. This is the only configuration that achieves all three properties simultaneously.

---

### 4. Connection to the Broader Triangle Law

The Wish + Skill + Recipe Triangle is an instance of a more general principle already in the Stillwater ecosystem: the REMIND + VERIFY + ACKNOWLEDGE triangle (phuc-triangle-law.md). Both express the same underlying law: three necessary components, each insufficient alone, together necessary and sufficient for the desired property.

The parallel is not coincidental. The underlying structure is the same: every reliable system requires an intent layer (what we want), an enforcement layer (how to ensure correctness), and an execution layer (how to carry it out). The REMIND + VERIFY + ACKNOWLEDGE triangle applies this to contract stability. The Wish + Skill + Recipe triangle applies it to task execution.

The principle generalizes: any system that needs to reliably achieve a goal under constraints has a three-vertex structure. Missing any vertex produces a predictable failure mode. The failure mode depends on which vertex is missing. This is the Triangle Law.

---

### 5. Combos as the Canonical Implementation

The Stillwater ecosystem already implements the triangle. The implementation is called a Combo. A Combo file (combos/*.md) contains:

- A **W_ block**: the wish definition — capability, non-goals, forbidden states, acceptance tests
- A **skill pack declaration**: which skills govern this combo's execution
- An **R_ block**: the recipe — L1-L5 node graph, checkpoints, artifact contract

The bugfix combo (combos/bugfix.md) is a triangle instance. The W_BUGFIX_PR wish defines what success looks like (red repro fails, green repro passes, PR bundle produced). The prime-coder + prime-safety skill pack defines the constraints (Kent Gate is hard, no patch without repro, never weaken tests). The R_BUGFIX_PR recipe defines the execution (Node 1: intake, Node 3: RED run mandatory, Node 6: apply + GREEN run, Node 9: final seal).

The plan combo (combos/plan.md) is another triangle instance. The W_MODE_SPLIT wish defines the goal (strict separation between planning and executing). The prime-forecast skill defines the constraints (DREAM→FORECAST→DECIDE→ACT→VERIFY required). The R_PLAN_EXEC recipe defines the execution (intent classifier → plan compiler → mode enforcer → promotion gate).

Combos are pre-validated triangle instances. They represent the accumulated learning of the ecosystem about how to execute common workflows safely, expertly, and reliably. Using a combo means: the wish is well-formed, the skill is matched, the recipe is proven. The triangle completeness check is already done.

This has an important implication: the primary work of building a Software 5.0 ecosystem is not writing code — it is building combos. Each combo is a reusable, verified execution unit. The ecosystem's value scales with the number and quality of its combos. A codebase with 100 well-tested combos is not just 100 solved problems — it is 100 instances of the triangle, each encoding a piece of the ecosystem's accumulated expertise.

---

### 6. Implementation in Stillwater

The Stillwater implementation enforces the triangle through several mechanisms:

**At dispatch time**, phuc-orchestration requires every sub-agent dispatch to include a skill pack (the SKILL vertex) and a full CNF capsule (the WISH vertex). The SKILL_LESS_DISPATCH and FORGOTTEN_CAPSULE forbidden states block dispatch when either is absent.

**At execution time**, the prime-wishes skill enforces wish completeness. A wish cannot enter the WISH_SCOPED state without non-goals, forbidden states, and acceptance tests. The WISH_WITHOUT_NONGOALS and AMBIGUOUS_WISH forbidden states block execution when the WISH vertex is incomplete.

**At verification time**, the prime-coder skill enforces the recipe's evidence requirements. The UNWITNESSED_PASS forbidden state blocks any claim of success that is not backed by Lane A artifacts (tests.json, PATCH_DIFF). The recipe's artifact contract defines exactly what evidence is required.

The phuc-wish-triangle.md skill (new, this session) formalizes the triangle completeness check as a state machine. Before any execution begins, the system verifies: wish present and valid, skill matched and valid, recipe present and valid, all three vertices aligned, northstar link confirmed. Only after all five checks pass does execution begin.

The triangle completeness check runs in O(1) against pre-validated combos (skip vertex checks, go directly to alignment and northstar checks) and in O(n) for first-time executions (validate all three vertices from scratch).

---

### 7. Conclusion

The Wish + Skill + Recipe Triangle is the fundamental execution model of Software 5.0. It is not a new idea — it is the formal name for what successful AI-assisted software development has always required. Every reliable AI-assisted workflow has had an intent layer (the wish), an expertise layer (the skill), and an execution layer (the recipe). Combos in Stillwater are the existing implementation. The triangle names the structure, makes the completeness check explicit, and provides the failure mode vocabulary for diagnosing what went wrong when execution degrades.

The practical implication is immediate: before executing any AI-assisted task, identify all three vertices. If any is missing, stop and retrieve it. If all three are present, verify they are aligned. Only then execute. This is not bureaucratic overhead — it is the minimum structure for reliable execution. Below the triangle: improvisation.

The long-term implication is architectural: the primary capital of a Software 5.0 ecosystem is its collection of validated triangles — its combos. A team's ability to execute AI-assisted tasks reliably scales with the number and quality of combos it has accumulated. Building combos is the work of building the ecosystem. Each combo is a piece of crystallized expertise: intent, constraints, and execution path, validated together, available for reuse by any agent in any session.

"The triangle is the minimal unit of verified execution. Below the triangle: improvisation."

---

### Appendix: Triangle Completeness Checklist

Before any AI-assisted execution begins, answer all five questions:

1. **WISH**: Is the capability statement one measurable sentence? Are non-goals declared? Are forbidden states named? Are acceptance tests defined?
2. **SKILL**: Does a skill exist for this domain? Does its domain match the wish domain? Does it define forbidden states and verification gates?
3. **RECIPE**: Does a recipe or combo exist for this workflow? Does it have a node graph, checkpoints, and an artifact contract?
4. **ALIGNMENT**: Are the three vertices mutually consistent? Do skill constraints match recipe steps? Does the recipe produce the artifacts the wish acceptance tests require?
5. **NORTHSTAR**: Does the wish advance at least one northstar metric? If you cannot answer this, question whether the wish should be in the backlog.

If any answer is "no": stop. Retrieve the missing element. Do not execute.

If all answers are "yes": execute. The triangle is complete.
