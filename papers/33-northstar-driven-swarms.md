# Northstar-Driven Swarms: Using Goals as Skill Primes for AI Agent Coordination

**Paper ID:** 33
**Date:** 2026-02-21
**Status:** STABLE
**Tags:** methodology, swarms, northstar, goal-primes, alignment, agent-coordination

---

## Abstract

Current agent frameworks load skills and dispatch — skills define HOW an agent executes, but provide no answer to WHY. An agent equipped with prime-coder but no project northstar can produce technically correct, well-tested code that is architecturally wrong for the project it is supposed to serve. This paper introduces the concept of the **goal prime**: a northstar document that shapes agent behavior at a higher level than skills, providing directional context that skills cannot supply. We describe the three-layer agent loading order (Safety + Method + Direction), the northstar injection protocol for swarm agents, and the verification question that transforms "tests pass" into "tests pass AND we are heading in the right direction." The Stillwater Protocol treats northstar injection as mandatory, not optional — as foundational to agent coordination as safety rails and test gates.

---

## 1. The Problem with Skill-Only Agent Design

The dominant pattern in current agent frameworks is: load skills, dispatch agent, receive output. Skills are the primary mechanism for shaping agent behavior. This pattern works well for isolated tasks — write a sorting algorithm, fix a specific bug, generate a test suite — where the task is self-contained and correctness is locally verifiable.

The pattern breaks when tasks are not isolated. Real projects are not isolated. They have histories, architectural decisions, north star metrics, and constraints that emerged from weeks or months of prior work. A skill tells an agent how to execute. It does not tell the agent where the project is going or what "good" looks like at the project level.

### 1.1 The HOW/WHY Gap

Skills are HOW documents. Prime-coder tells an agent how to do test-driven development, how to build evidence bundles, how to run the red-green gate. It is a methodology specification — an answer to "how should I execute this task?"

What skills cannot provide is WHY. Why does this project exist? What problem does it solve? What does success look like, measurable, for this specific project? Which features are on the roadmap and which are scope creep? Which architectural decisions have already been made and must not be undone?

An agent operating without WHY optimizes for local correctness. Local correctness is necessary but not sufficient. A feature that passes all its tests, produces no regressions, and achieves rung 641 can still be wrong — wrong because it conflicts with an architectural decision made three sessions ago, wrong because it implements a capability that the project explicitly chose not to include, wrong because it moves no northstar metric.

### 1.2 The Evidence: Method-Correct, Direction-Wrong

Consider a concrete failure mode. A swarm is dispatched to build a recipe recommendation engine. The task prompt says "implement content-based filtering." The agent loads prime-safety and prime-coder. It implements content-based filtering. Tests pass. Evidence bundle complete. Rung 641 achieved.

But the project NORTHSTAR says: "We chose collaborative filtering as the primary mechanism in Phase 1 decision record because content-based filtering degrades with sparse user data, which is our primary constraint." The session built the wrong thing — technically correct, directionally wrong. No skill could have prevented this. Only the NORTHSTAR could have.

### 1.3 The Accumulation Problem

Direction-wrong outputs accumulate. One session builds a content-based filter. Another session builds an API that assumes content-based filtering. A third session builds a UI that exposes content-based filtering parameters. By the time the hub notices the direction is wrong, three sessions of work must be reverted or refactored.

The cost of a direction error scales with how long it takes to detect it. Northstar injection detects direction errors at the earliest possible moment — before the agent writes its first line of code — by requiring the agent to confirm alignment before proceeding.

---

## 2. Northstars as Goal Primes

A **goal prime** is a document that shapes an agent's behavior at a higher level than skills. Where a skill shapes HOW the agent executes, a goal prime shapes WHERE the agent is heading and WHAT "done" looks like at the project level.

The northstar document is the canonical goal prime in the Stillwater Protocol. It is not a specification document (which answers "what should be built"). It is not a technical design document (which answers "how should it be built"). It is the answer to three prior questions:

1. **Why does this project exist?** (Vision)
2. **What does success look like, measurable?** (North star metrics)
3. **What aligns, and what does not align, with this goal?** (Allowlist and denylist)

Together, these three answers give an agent enough directional context to self-assess. An agent with a goal prime can answer: "Is my approach aligned with the northstar?" An agent without a goal prime cannot — it has no basis for that evaluation.

### 2.1 Goal Primes Are Not Specifications

A common mistake is to treat the northstar as a detailed specification. Specifications are task-level documents. They answer "build feature X with interface Y." Northstars are project-level documents. They answer "we are building a system that does Z, success means metric M exceeds threshold T, and we explicitly are not building W."

The distinction matters for agent behavior. A specification constrains the agent's implementation choices. A northstar constrains the agent's directional choices. Specifications prevent wrong implementations. Northstars prevent right implementations of wrong features.

Both are necessary. Neither is sufficient without the other.

### 2.2 The Goal Prime Hierarchy

In a complex project, there may be multiple levels of goal primes:

**Ecosystem northstar:** The top-level vision shared across all projects in the ecosystem. For Stillwater, this is the shared vocabulary of belts, rungs, and Software 5.0 principles. Every project in the ecosystem inherits these constraints.

**Project northstar:** The specific vision, metrics, and constraints for one project. This is the primary goal prime for project-level sessions. It is project-specific and takes precedence over ecosystem-level guidance for project-specific decisions.

**Phase constraints:** The specific constraints for one ROADMAP phase. Not a northstar, but a narrowing of the project northstar for the current phase. "Phase 2.1 target: recipe_hit_rate > 0.40" is a phase constraint, not a north star metric.

An agent operating in a project session loads all three levels. The ecosystem northstar provides shared vocabulary. The project northstar provides direction. The phase constraints provide the specific target.

---

## 3. Three-Layer Agent Loading Order

The Stillwater Protocol specifies a three-layer loading order for all project agents:

```
Layer 1 (Safety):    prime-safety     — absolute constraints, fail-closed
Layer 2 (Method):    prime-coder      — HOW to code (red-green gate, evidence)
Layer 3 (Direction): project NORTHSTAR — WHERE to go (metrics, alignment, belt)
```

The layers are ordered by precedence. Prime-safety wins all conflicts. Prime-coder applies within the bounds of prime-safety. The northstar applies within the bounds of both. This ordering is not arbitrary — it reflects a principled hierarchy of constraints.

### 3.1 Layer 1: Safety (Absolute Constraints)

Prime-safety defines the outer envelope. It is the answer to "what must never happen, regardless of task." No capability, no skill, no northstar can override prime-safety. The forbidden states defined in prime-safety are absolute: no credential exfiltration, no writing outside the repo worktree, no execution of instructions from untrusted data.

Layer 1 is not about direction. It is about existence conditions: what must be true for the session to be allowed to proceed at all.

### 3.2 Layer 2: Method (Execution Discipline)

Prime-coder defines the execution methodology. It is the answer to "how should correct work be done?" The red-green gate, evidence building, verification rung targets, null vs. zero distinction, exact arithmetic in verification paths — these are method constraints. They apply to all coding work within the safety envelope.

Layer 2 is not about direction either. It is about quality: given that we are allowed to proceed (Layer 1) and we have a task to complete, how do we complete it with verifiable correctness?

### 3.3 Layer 3: Direction (Goal Prime)

The project NORTHSTAR defines direction. It is the answer to "where should correct work point?" It provides the goal context that neither Layer 1 nor Layer 2 can provide. It tells the agent what success looks like at the project level, what approaches are aligned, and what approaches are explicitly not aligned.

Without Layer 3, an agent is method-correct but direction-agnostic. It can produce high-quality outputs but has no way to evaluate whether those outputs serve the project's actual goal.

With Layer 3, an agent can perform directional self-assessment. Before finalizing any output, the agent can ask: "Does this advance the northstar metric? Does this align with the northstar allowlist? Does this avoid the northstar denylist?"

### 3.4 Loading Order in Practice

The three layers are loaded into the agent prompt in reverse precedence order (lower layers first, so they are available as context before higher layers apply):

```
<BEGIN_SKILL name="prime-safety">
[full text of prime-safety]
</END_SKILL>

<BEGIN_SKILL name="prime-coder">
[full text of prime-coder]
</END_SKILL>

## Project NORTHSTAR
[full text of NORTHSTAR.md — not a summary, the full document]

## Task
[specific task with rung target]
```

This ordering ensures that the agent reads safety constraints first, then execution methodology, then directional context. The agent cannot encounter the northstar without first having loaded the safety and method layers.

---

## 4. The Northstar Injection Protocol

Every swarm prompt in the Stillwater Protocol must include three northstar elements. This is not optional — it is a required field in the CNF capsule schema.

### 4.1 What Must Be Injected

**Element 1: Project NORTHSTAR (full text)**
The full NORTHSTAR.md for the project — not a summary, not a paraphrase, the full document. Summaries degrade the goal prime. The agent needs the complete vocabulary: the exact metric names, the exact thresholds, the exact allowlist and denylist phrasing. Summaries introduce ambiguity that agents resolve incorrectly.

**Element 2: Ecosystem NORTHSTAR (first section)**
The shared vocabulary section of the Stillwater ecosystem NORTHSTAR. This establishes belt progression terminology, rung definitions, and Software 5.0 principles. Without this, project-level northstar references to "Yellow Belt" or "rung 274177" are undefined.

**Element 3: Specific task with rung target**
The task is not just "build feature X." It is "build feature X with rung target 641, which means [explicit evidence requirements]. The output of this session must advance [specific northstar metric] toward [specific threshold]."

### 4.2 What the Agent Does with the Northstar

The northstar injection protocol requires the agent to perform a northstar alignment check before writing code. This check has three steps:

**Step 1: Read the northstar.**
Not skim — read. The agent must be able to answer: What is the project's north star metric? What is the current metric value? What is the target? What approaches does the northstar explicitly allow? What approaches does the northstar explicitly exclude?

**Step 2: Confirm task alignment.**
Before writing any code, the agent explicitly states: "This task aligns with the northstar because [reason]. It advances [metric name] toward [target value]. It does not conflict with [explicit exclusions]." If the agent cannot complete this statement, the task may be misaligned — the agent should emit EXIT_NEED_INFO rather than proceeding.

**Step 3: Report metric advancement.**
After completing the task and before claiming PASS, the agent explicitly states which northstar metric was advanced and by how much. "Recipe hit rate: baseline 0.31, after this session 0.43, target 0.70. Progress: 37% of the way from baseline to target." This is not a summary — it is an evidence statement.

### 4.3 The Alignment Gate

The alignment check is a gate, not a formality. If the agent cannot confirm task alignment, the task does not proceed. This prevents the accumulation of direction-wrong work described in Section 1.3.

The alignment gate has two possible outputs:

**ALIGNED:** Task confirms alignment with northstar. Agent proceeds to execution.

**MISALIGNED or NEED_INFO:** Task cannot be confirmed as aligned. Possible causes: task is not on the roadmap, task conflicts with a northstar exclusion, northstar metric is not advanced by this task, or northstar document is ambiguous about this type of work. Agent emits EXIT_NEED_INFO with explicit statement of what is unclear.

The alignment gate cannot produce false positives by design — an agent that cannot confirm alignment cannot claim alignment. This is the fail-closed property applied to directional correctness.

---

## 5. The Verification Question

The verification question is the northstar-level equivalent of the red-green gate. Where the red-green gate asks "did the tests go from failing to passing?", the verification question asks "does this output advance the northstar?"

Every agent, before claiming PASS, must explicitly answer three questions:

**Question 1: Does this output align with the northstar?**
Not "does this output look good" but "does this output satisfy the northstar allowlist and avoid the northstar denylist?" The answer must reference specific northstar text, not general principles.

**Question 2: Which northstar metric does this advance?**
Not "this is useful work" but "this specifically advances [metric name] from [baseline] toward [target]." If no northstar metric is advanced, the work may be scope creep — technically correct but directionally neutral.

**Question 3: What northstar metric would FAIL if this implementation is wrong?**
This is the falsifier question. It forces the agent to specify the observable consequence of being wrong. A correct implementation that advances recipe_hit_rate will, if wrong, degrade recipe_hit_rate. If the agent cannot specify a metric that would fail, the work may not be northstar-connected — it may be infrastructure work that is necessary but not directly measurable.

The falsifier question is the most diagnostic. An agent that can answer question 3 clearly understands how its work connects to the project goal. An agent that cannot answer question 3 is doing work whose connection to the northstar is unclear — and that is worth surfacing before claiming PASS.

### 5.1 Transforming Verification

The verification question transforms verification from backward-looking to forward-looking.

**Backward-looking verification:** "Tests pass. No regressions. Evidence bundle complete. Rung 641 achieved." This is necessary but tells us nothing about direction.

**Forward-looking verification:** "Tests pass. No regressions. Evidence bundle complete. Rung 641 achieved. Recipe hit rate advanced from 0.31 to 0.43. This represents 37% of the distance from baseline to Phase 2.1 target of 0.40. Phase 2.1 acceptance criterion (>0.40) is met." This is backward-looking verification plus directional confirmation.

The forward-looking component is only possible with northstar injection. An agent without a northstar cannot report metric advancement because it does not know what metrics exist.

---

## 6. Belt Progression as Northstar Signal

The belt system is the project-level aggregation of northstar metric advancement. Where individual sessions report metric advancement ("recipe_hit_rate went from 0.31 to 0.43"), belts represent sustained metric progress ("recipe_hit_rate has exceeded 0.40 across three independent sessions").

### 6.1 Belts Require Northstar Evidence

Belt advancement is not granted based on session count or time elapsed. It requires:

1. The target northstar metric exceeds the belt threshold
2. The metric was measured by an independent session (not self-reported by the session that produced the improvement)
3. The metric is stable across at least two replay seeds (rung 274177 minimum for belt advancement)

This means a belt advancement is itself a northstar measurement event. The hub does not grant a belt because a session claimed to advance the metric — the hub grants a belt because an independent verification session confirmed the metric.

### 6.2 Belts as Diagnostic Signals

The belt system creates a diagnostic signal that the hub can use to detect direction-wrong sessions.

**Scenario:** Three sessions achieve rung 641. Case studies show commits and passing tests. But recipe_hit_rate is still 0.31 — no advancement. Belt is still White.

**Diagnosis:** The sessions built something, but not something that advances the northstar metric. This could mean: sessions built infrastructure that is necessary but not directly measurable, sessions built the wrong feature, or sessions built the right feature but the metric measurement is broken.

**Hub action:** Investigate the gap. Do not dispatch more sessions until the gap is understood. The belt system caught a pattern that individual session rungs could not reveal.

Without northstar injection, this diagnostic is impossible — the hub has no shared metric to compare across sessions.

### 6.3 The Belt System as Coordination Mechanism

Belts are not just progress indicators — they are coordination mechanisms. When multiple spokes are running in parallel, the belt system provides a shared language for progress:

- "All spokes should target Yellow Belt acceptance criteria"
- "This phase requires Green Belt evidence"
- "We cannot advance to the next phase until at least two independent sessions confirm the metric"

This shared language eliminates a common source of inconsistency in multi-session workflows: different sessions using different definitions of "done."

---

## 7. Northstar Injection in Swarm Architectures

In a swarm architecture (multiple specialized agents coordinated by an orchestrator), northstar injection has additional considerations.

### 7.1 Every Agent Gets the Full Northstar

Every agent in the swarm receives the full northstar — not a fragment, not a summary, the full document. This includes agents whose work is not directly measured by northstar metrics (infrastructure agents, testing agents, documentation agents).

Why? Because even agents whose work is not directly measured can make decisions that conflict with the northstar. An infrastructure agent that chooses a caching strategy incompatible with the northstar's data privacy constraints has done direction-wrong work even though its northstar metric (none, directly) does not reflect this.

Every agent that touches the project gets the full northstar. No exceptions.

### 7.2 Orchestrator vs. Executor Northstar Roles

In a swarm, the orchestrator and executors use the northstar differently:

**Orchestrator:** Uses the northstar to make dispatch decisions. "The northstar says we are not building content-based filtering. Do not dispatch an agent to implement content-based filtering." The orchestrator uses the northstar to filter task requests before they reach executors.

**Executor:** Uses the northstar to perform alignment checks and report metric advancement. The executor reads the northstar to confirm its specific task is aligned, executes, and reports which metric was advanced.

The orchestrator uses the northstar as a filter. Executors use it as a compass and a measuring stick.

### 7.3 The Skeptic Agent as Northstar Verifier

In the Stillwater swarm architecture, the Skeptic agent plays a special role in northstar verification. Where other agents confirm their own alignment, the Skeptic's job is to challenge alignment claims.

The Skeptic receives: the northstar, the task that was executed, and the artifacts produced. It asks: "Does the PATCH_DIFF actually advance the northstar metric? Is the metric measurement methodology consistent with the northstar's definition of success? Is there an alternative interpretation of the northstar under which this work is direction-wrong?"

The Skeptic is the adversarial northstar reviewer. Its job is to find cases where an agent claimed alignment but was subtly wrong. This is the swarm-level equivalent of the red-green gate for directional correctness.

---

## 8. Common Failure Modes and Mitigations

### 8.1 Northstar Staleness

The northstar is a living document. As the project evolves, the northstar should evolve. Agents operating with a stale northstar (from a prior project phase) may align with outdated goals.

**Mitigation:** The northstar must include a version or date. The CNF capsule must reference the northstar version. If the case study references a northstar version that does not match the current NORTHSTAR.md, the hub must flag the discrepancy before dispatching.

### 8.2 Northstar Overspecification

A northstar that specifies implementation details ("use collaborative filtering, specifically matrix factorization with SVD") is too specific. It removes agent autonomy without providing directional value. Agents interpret overspecified northstars as specifications, not goal primes, and lose the ability to make alignment judgments.

**Mitigation:** Northstars should specify what success looks like (metrics, thresholds) and what is explicitly excluded, not how to achieve success. "Recipe hit rate > 70%" is a northstar metric. "Use matrix factorization" is a design decision that belongs in a technical design document, not a northstar.

### 8.3 Northstar Underspecification

A northstar that is too vague ("build a great recipe engine") provides no basis for alignment checks. Agents with underspecified northstars fall back to local correctness and behave as if they have no northstar.

**Mitigation:** Every northstar must include at least one measurable metric with a baseline and a target. If you cannot write a northstar metric in the form "[metric name] > [threshold]" you do not yet have a northstar — you have a vision statement. Vision statements are necessary but not sufficient for goal prime injection.

### 8.4 Partial Injection (Summary Substitution)

A hub that summarizes the northstar before injecting it into agent prompts introduces ambiguity. Summaries omit details. Details that seem minor to the hub may be critical to the agent's alignment check.

**Mitigation:** Inject the full northstar text. The northstar document should be short enough to inject fully (under 2,000 tokens for most projects). If the northstar is too long to inject, it is too complex — simplify the northstar, do not summarize it.

---

## 9. Implementation Checklist

For a project to fully implement northstar-driven swarms, the following must be true:

**Northstar document:**
- [ ] Vision statement (2-4 sentences)
- [ ] At least one measurable metric with baseline and target value
- [ ] Explicit allowlist (what approaches align)
- [ ] Explicit denylist (what approaches explicitly do not align)
- [ ] Belt progression table (which metrics must be met for each belt)
- [ ] Version/date stamp

**Swarm prompt template:**
- [ ] Full project NORTHSTAR injected (not summarized)
- [ ] Ecosystem northstar shared vocabulary section injected
- [ ] Alignment check gate required before code is written
- [ ] Metric advancement report required before PASS
- [ ] Falsifier question answered before PASS

**Hub responsibilities:**
- [ ] Northstar version consistency checked before each dispatch
- [ ] Belt advancement requires independent metric verification
- [ ] Diagnostic check: if rungs achieved but metrics not advancing, investigate before continuing
- [ ] Case study records metric values, not just rung achievements

**Skeptic role:**
- [ ] Skeptic receives full northstar + artifacts
- [ ] Skeptic specifically challenges alignment claims
- [ ] Skeptic verdict required before belt advancement

---

## 10. Conclusion

Skills tell agents HOW. Northstars tell agents WHERE.

The HOW/WHY gap in current agent frameworks is not a limitation of skills — skills are the right tool for execution methodology. The gap is structural: frameworks designed for isolated task execution do not have a mechanism for project-level directional context. Skills fill the HOW gap. Northstars fill the WHY gap.

The three-layer loading order (Safety + Method + Direction) closes this gap. Layer 1 (prime-safety) defines what must never happen. Layer 2 (prime-coder) defines how correct work is done. Layer 3 (project NORTHSTAR) defines where correct work should point. Without Layer 3, agents are method-correct and direction-agnostic. With Layer 3, agents can self-assess directional correctness before claiming PASS.

The verification question — "Does this output align with the northstar? Which metric does it advance? What would fail if it is wrong?" — transforms verification from a backward-looking quality check into a forward-looking alignment confirmation. This is the difference between "tests pass" and "tests pass AND we are heading in the right direction."

Northstar-driven swarms are not more complex than skill-only swarms. They are more complete. The northstar is a small document — typically under 500 words — that provides an outsized coordination benefit: every agent, in every session, operates with shared directional context. Conflicting implementations become rare. Scope creep becomes detectable before it accumulates. Belt progression becomes a meaningful signal rather than a gamification overlay.

The Stillwater Protocol: always inject NORTHSTAR, always verify against it.

Skills + Safety + Goal-Prime = truly aligned AI execution.

---

*Written by the Stillwater ecosystem. Part of the Software 5.0 paradigm documentation series.*
