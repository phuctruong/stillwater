# Solve the Maze From the End: Northstar Reverse Engineering for AI-Driven Development

**Paper ID:** northstar-reverse-engineering
**Date:** 2026-02-21
**Status:** STABLE
**Authority:** 65537
**Version:** 1.0.0
**Tags:** methodology, planning, backward-chaining, northstar, maze, cognitive-load, verification-ladder, software-5.0
**Related:** `papers/33-northstar-driven-swarms.md`, `papers/32-roadmap-based-development.md`, `skills/northstar-reverse.md`, `swarms/northstar-navigator.md`, `SOFTWARE-5.0-PARADIGM.md`

---

## Claim Hygiene

Every empirical claim in this paper is tagged with its epistemic lane:

- **[A]** Lane A — directly witnessed by executable artifact in this repo
- **[B]** Lane B — framework principle, derivable from stated axioms or established theory
- **[C]** Lane C — heuristic or reasoned forecast; useful but not proven
- **[*]** Lane STAR — unknown or insufficient evidence; stated honestly

See `papers/01-lane-algebra.md` for the formal epistemic typing system.

---

## Abstract

Forward planning is the natural human instinct: assess the current situation, identify the next three steps, begin executing. For simple problems, this works. For complex, goal-driven problems — the kind that take months, span multiple teams, and require every decision to compound toward an economic or technical outcome — forward planning produces combinatorial explosion. The search space branches with every decision. Most paths lead nowhere. **[B]** Backward chaining from a fully specified goal state closes the search space before it opens. This paper introduces Northstar Reverse Engineering: a planning paradigm in which every plan begins at the NORTHSTAR victory condition and works backward to the current state, producing a forward plan whose steps are derived from goal-preconditions rather than current capabilities. The paradigm is natural for AI: transformers hold entire solution spaces in context, attention mechanisms trace back from target states, and backward chaining is computationally equivalent to how LLMs predict sequence continuations in reverse. Applied to Software 5.0 development, Northstar Reverse Engineering feeds directly into the verification ladder, the evidence bundle system, and the never-worse doctrine.

---

## 1. The Founder's Insight: The Last Three Steps

> "When I was younger I thought about the next 3 steps. Now I figure out the LAST 3 steps and work backwards."
> — Phuc Truong

**[C]** Young entrepreneurs plan forward. They assess the current situation — the code that exists, the users they have, the capital in the bank — and project three steps outward. "We need a login page. Then we need a dashboard. Then we need to send emails." The steps feel concrete because they are grounded in what is visible today. They feel urgent because they are actionable immediately.

**[C]** The problem: forward planning from the current state produces decisions that are locally sensible but globally misaligned. The login page gets built. The dashboard gets built. The email system gets built. Three months later, the founder realizes none of these things close the gap to the northstar metric. The product has features. The northstar has not moved.

**[B]** Experienced entrepreneurs make a different move. They identify the NORTHSTAR victory condition — the concrete, measurable state that constitutes success — and then ask: what are the last three things that must be true before that condition is met? Not the first three things to do, but the last three preconditions before the goal is reachable.

**[C]** This inversion changes everything. The last three steps before the northstar are highly constrained. The northstar is a specific state — recipe hit rate > 70%, or rung 65537 achieved on two projects, or MRR > $18K/month. The preconditions for that state are not optional. They are necessary. Identifying them is a process of logical derivation, not creative brainstorming. And once the last three are identified, the three before those are also constrained. The chain propagates backward through the entire problem space, and by the time it reaches today, the first step is not "what should we build?" but "here is the single most constrained action that unblocks the next link in the chain."

### The Maze Metaphor

**[B]** Everyone who has solved a physical maze knows the trick: start from the end.

```
FORWARD (naive approach):
  Start → ??? → ??? → dead end → backtrack → ??? → dead end → ...

BACKWARD (expert approach):
  End → last junction → second-to-last junction → ... → Start
  Result: One path. No dead ends. No backtracking.
```

The maze metaphor is not decorative. It is structural. When you start from the beginning of a maze, every junction presents a choice, and most choices lead to dead ends. The search space branches exponentially. When you start from the end, the exit is fixed. Every junction traced backward has exactly one correct backward step (the one that leads toward the exit). The search space shrinks exponentially.

**[B]** Planning is a maze. The NORTHSTAR is the exit. Northstar Reverse Engineering starts from the exit.

---

## 2. Why AI Makes This Natural

### 2.1 LLMs Hold Entire Solution Spaces in Context

**[B]** Human working memory holds approximately 7 ± 2 items at once. A human planner reasoning forward from the current state can hold a few branches of the decision tree in mind before the cognitive load becomes untenable. This is why forward planning naturally telescopes to "the next three steps" — beyond three steps, the branches multiply faster than working memory can track.

**[B]** An LLM with a 200,000-token context window does not have this constraint. It can hold the entire NORTHSTAR document, the entire ROADMAP, the entire case study history, and the full backward chain simultaneously. The cognitive bottleneck that makes forward planning a practical necessity for humans does not apply to LLM-assisted planning.

**[C]** This means that for AI-assisted planning, the natural approach is backward chaining — the approach that is theoretically optimal but cognitively prohibitive for humans. The LLM can hold the victory condition, every intermediate precondition, and the connection back to the current state in a single context window, without losing track of any link in the chain.

### 2.2 Backward Chaining Is Computationally Natural for Transformers

**[B]** Transformers predict the next token given all prior tokens. But they are also trained to predict masked tokens given surrounding context — including tokens that come later in the sequence. The attention mechanism operates bidirectionally during training. A model that has learned to predict "what comes next" has also implicitly learned "what must have come before."

**[C]** When a transformer is given a NORTHSTAR victory condition and asked "what must be true immediately before this is achievable?", it is performing a task that is structurally similar to backward prediction: given the goal state, predict the immediately preceding state. This is within the natural capability envelope of modern LLMs. They are not being asked to extrapolate; they are being asked to identify preconditions — a task that requires the same pattern-matching over learned knowledge that next-token prediction requires.

**[C]** Forward planning, by contrast, requires open-ended generation. "Given the current state, generate the next step." This is harder to constrain, because the space of possible next steps is large and most of them are not optimal. Backward chaining from a fixed goal is more constrained: the space of necessary preconditions is much smaller than the space of possible next steps.

### 2.3 Attention Literally Traces from Goal to Precondition

**[C]** The attention mechanism in a transformer computes relationships between all tokens in context simultaneously. When processing a backward-chaining prompt, attention weights connect the goal state tokens directly to the precondition tokens, weighted by learned semantic relevance. The model does not need to "search" for preconditions — it computes their relationship to the goal state in a single forward pass.

**[C]** This is analogous to solving the maze: once the exit is fixed, every junction's relationship to the exit is a function of the maze structure. Attention computes these relationships directly, rather than exploring paths sequentially.

---

## 3. The Algorithm: ANCHOR → LAST-3 → BRIDGE-BACK → CONNECT → VALIDATE → EMIT

**[A]** The following algorithm is implemented in `skills/northstar-reverse.md` and executed by `swarms/northstar-navigator.md`. **[A]** The northstar-navigator swarm agent type (Claude Shannon persona) executes this algorithm as its primary FSM path.

### Step 1: ANCHOR

Define the Northstar victory condition in concrete, measurable terms.

- Not "we succeed when the product is good." That is not a victory condition.
- Not "we succeed when users are happy." That has no threshold.
- The victory condition: "recipe hit rate > 70% on the canonical test set of 1,000 recipes, measured independently." That is an anchor.

The anchor must be:
- Measurable (exact metric, exact threshold)
- Achievable in principle (not "all users are delighted")
- Verifiable by an independent agent that did not produce it
- Referenced in the NORTHSTAR document (not invented in the planning session)

### Step 2: LAST-3

Identify the three states that must be true immediately before the anchor is reachable.

For recipe hit rate > 70%:
1. A recipe library exists with at least N recipes covering the canonical test set
2. The recipe matching engine achieves < X% false-negative rate on the library
3. The task execution engine can execute matched recipes without manual intervention

These are not tasks. They are states. They are preconditions. If any one of them is absent, the anchor is not reachable. That is what makes them the LAST-3.

**[B]** The LAST-3 are the most constrained preconditions. They are not aspirational — they are necessary. If you cannot identify at least three states that are both necessary and verifiable, the anchor is underspecified.

### Step 3: BRIDGE-BACK

For each LAST-3 state, identify its own preconditions. Continue backward, one level at a time.

```
Anchor: recipe_hit_rate > 70%
  ← LAST-3 State 1: recipe library covers canonical test set
      ← Level 2: recipe capture pipeline captures successful tasks
          ← Level 3: recipe format is defined and parseable
              ← Level 4: recipe schema exists (current state? check case study)
```

Continue until one of two things happens:
1. The chain reaches a state that already exists (confirmed by case study or ROADMAP checkbox)
2. The chain reaches a gap — a state that must exist but does not yet

### Step 4: CONNECT

Connect the backward chain to the current state.

Read the case study. Read the ROADMAP checkboxes. Find where the chain connects.

- Connection point: the earliest chain state that already exists
- Gap: the distance between the connection point and the next unmet state in the chain

**[B]** The gap is the work. Everything else in the plan is sequencing. If there is no gap — if the backward chain connects all the way to the current state — the northstar should be achievable immediately, which means either the anchor threshold was set too low, or the current state is better than the case study suggests.

### Step 5: VALIDATE

Before emitting the plan, validate three things:

1. **Logical necessity**: every link in the chain is necessary, not merely useful. "It would be nice to have" is not a chain link.
2. **No FORWARD_FIRST violation**: confirm that every step in the forward plan is derived from the backward chain, not from "what feels like the next thing to do." This is the primary failure mode.
3. **Measurability**: every state in the chain has a verifiable signal. If you cannot say what artifact or metric confirms a state is met, the state is underspecified.

### Step 6: EMIT

Reverse the backward chain to produce the forward plan.

The chain, read backward from current state to anchor, is the forward plan. Step 1 is the first gap in the chain. Step N is the state immediately before the anchor. The anchor is the PASS condition.

Emit:
- `northstar-reverse-plan.json` — the full backward derivation plus forward plan, machine-readable
- `forward-plan.md` — the human-readable forward plan with stop rules and verification signals

### Worked Example

**Project:** SolaceBrowser
**NORTHSTAR metric:** Recipe hit rate > 70%
**Current state (from case study):** Phase 1 complete — 6 LinkedIn recipes captured, recipe matching engine not yet built

**ANCHOR:** recipe_hit_rate > 70% on canonical test set of 1,000 recipes, measured by independent agent

**LAST-3:**
1. Recipe library contains ≥ 500 recipes covering canonical test set domains
2. Recipe matching engine achieves < 10% false-negative rate (recipe exists but not matched)
3. Task execution engine can run matched recipes without human intervention at rung 641

**BRIDGE-BACK:**
```
State 1 (recipe library ≥ 500)
    ← recipe capture pipeline auto-captures from successful task runs
        ← recipe format v2 supports auto-capture (not just manual creation)
            ← recipe schema validated at rung 274177

State 2 (matching engine < 10% FNR)
    ← matching engine trained/configured on captured library
        ← matching engine exists with defined interface
            ← matching engine spec written

State 3 (execution engine runs recipes at rung 641)
    ← execution engine integrates with Phase 1 browser automation
        ← Phase 1 automation is at rung 641 (DONE — case study confirms)
```

**CONNECT:**
- State 3 chain connects at "Phase 1 automation is at rung 641" — confirmed by case study
- State 2 chain breaks at "matching engine spec written" — does not exist
- State 1 chain breaks at "recipe format v2 supports auto-capture" — Phase 1 format is manual-only

**GAP:** Two parallel workstreams — recipe format v2 + matching engine spec

**FORWARD PLAN** (reversed chain):
1. Write matching engine spec (unblocks State 2 chain)
2. Upgrade recipe format to v2 with auto-capture support (unblocks State 1 chain)
3. Build matching engine to spec at rung 641
4. Build recipe capture pipeline using v2 format
5. Run 6 Phase 1 LinkedIn recipes through capture pipeline — target: 6 recipes auto-captured
6. Validate matching engine on 6 auto-captured recipes — target: 0 false-negatives
7. Expand recipe library to 50 recipes — target: matching FNR < 20%
8. Scale to 500 recipes — target: matching FNR < 10% (State 2 met)
9. Measure recipe_hit_rate on canonical test set — target: > 70% (ANCHOR met)

**[C]** Notice what is absent from this forward plan: any step that was generated by asking "what should we build next?" Every step is derived from the backward chain. The plan is goal-constrained, not capability-constrained.

---

## 4. Comparison: Forward Planning vs. Backward Planning

### When Forward Planning Is Appropriate

**[B]** Forward planning is not always wrong. It is appropriate when:
- The problem is well-understood and the path to the goal is known
- The goal is close enough that combinatorial explosion does not occur
- The constraints are tight enough that most forward paths converge
- The cost of backtracking is low (so dead ends are not expensive)

Examples: writing a unit test, fixing a known bug with a known fix, implementing a feature with a complete spec. In these cases, the current state fully determines the next steps, and the goal is close enough that forward planning terminates quickly.

**[B]** Forward planning is inappropriate when:
- The goal is far from the current state (months of work)
- The path is uncertain (multiple plausible approaches)
- Backtracking is expensive (wrong architectural decisions compound)
- The northstar metric must be maximized (not just "do the next thing")

### The Combinatorial Argument

**[B]** Assume each planning step has K possible choices. Forward planning from the current state produces K^N possible plans of length N. Most of these plans do not reach the northstar. The planner must search through K^N plans to find those that do.

**[B]** Backward chaining from the northstar produces a much smaller search space. At each backward step, only the states that are necessary preconditions of the next state are candidates. The number of necessary preconditions is typically much smaller than K. The backward search space is constrained by logical necessity; the forward search space is constrained only by imagination.

**[C]** For a typical software project with K=5 choices per step and N=10 steps, forward planning explores up to 5^10 = ~10 million possible plans. Backward chaining from a specific northstar metric typically identifies 2-4 necessary preconditions per step, giving 3^10 = ~60,000 candidate chains. But most of these are pruned immediately because they do not connect to the current state — the practical search space is far smaller.

### Why Backward Wins for Complex Goals

**[B]** Complex goals have this property: the northstar state is highly constrained (specific metric, specific threshold), while the current state is relatively unconstrained (many possible next steps). Backward chaining propagates the constraints from the highly-constrained northstar toward the unconstrained current state. By the time the chain reaches today, the first step is almost uniquely determined.

**[C]** Forward planning tries to find the optimal path by exploring from a low-constraint start toward a high-constraint end. Most exploration is wasted on paths that don't reach the goal. Backward planning finds the optimal path by propagating high-constraint information from the end toward the low-constraint start. Almost no exploration is wasted.

---

## 5. The 3-Step Chunk Rule

### Cognitive Load Theory

**[B]** Cognitive load theory (Sweller, 1988) identifies two types of cognitive load: intrinsic (inherent task complexity) and extraneous (how the task is presented). Working memory handles approximately 7 ± 2 independent items simultaneously.

**[B]** A plan with 20 steps overloads working memory. The planner cannot hold all steps in mind simultaneously and loses track of which steps depend on which. This produces the "next three steps" heuristic: most humans naturally narrow their planning horizon to approximately three steps, because that is within working memory capacity.

### Why Groups of 3 Work

**[C]** The LAST-3 naming in Northstar Reverse Engineering is not arbitrary. Three is large enough to capture the actual dependency structure of most planning problems (most goals have 2-4 necessary immediate preconditions) and small enough to fit within working memory for human review.

**[B]** More fundamentally: three states per backward-chaining level produces a tree structure that is easy to validate. For each state, you ask: (1) is this necessary? (2) is it verifiable? (3) is it the most constrained precondition at this level? Three questions per state, three states per level. This is the unit of planning effort.

**[C]** The 3-step chunk rule also applies to the forward plan. Every third step should be a checkpoint — a measurable signal that confirms the chain is still connected to the northstar. Without checkpoints every three steps, execution entropy accumulates: small deviations from the plan compound, and by step 10, the team is building something that no longer traces to the northstar.

### Applied to Software Development

**[A]** The ROADMAP.md structure in the Stillwater ecosystem enforces 3-step chunking implicitly. Each ROADMAP phase is a bounded unit of work with a specific acceptance criterion. Phases are grouped into belts (White → Yellow → Orange). Each belt corresponds to approximately 3 phases. This structure is the 3-step chunk rule applied at the macro level.

**[A]** The never-worse doctrine enforces it at the micro level: each phase rung must be ≥ prior phase rung. This means each chunk of 3 phases must maintain or improve the verification standard. The never-worse constraint propagates forward from the northstar (highest rung = production confidence) down to each phase (minimum rung = local correctness).

---

## 6. Integration with Software 5.0: Verification Ladder, Evidence Bundles, Never-Worse

### 6.1 How Backward Planning Feeds the Verification Ladder

**[A]** The verification ladder has three rungs: 641 (local correctness), 274177 (stability), 65537 (production confidence). **[B]** These rungs are not arbitrary — they correspond to three levels of constraint propagation from the northstar.

**[B]** Rung 65537 is the northstar rung: the state where an implementation is trusted for production. When backward chaining from a production-grade northstar, the ANCHOR must require rung 65537. The LAST-3 states must each be achievable at a rung that supports 65537. If any LAST-3 state is only achievable at rung 641, the chain is broken — the northstar cannot be reached without revisiting that state.

**[B]** This creates a natural backward propagation of rung requirements. The northstar requires 65537. The LAST-3 require at least 274177. The bridge-back states require at least 641. The forward plan then enforces this: early steps achieve 641, middle steps stabilize to 274177, final steps promote to 65537. The rung progression is derived from the backward chain, not imposed by convention.

### 6.2 Evidence Bundles as Chain Verification

**[A]** Each step in the forward plan produces an evidence bundle: tests.json, PATCH_DIFF, repro_red.log, repro_green.log, plan.json. **[B]** In the Northstar Reverse Engineering paradigm, evidence bundles serve a dual purpose: they verify local correctness (as they always do) and they confirm chain-link completion.

**[B]** A chain-link is complete when the state it describes is verifiable by the evidence bundle. If the forward plan step says "recipe matching engine achieves < 10% FNR," the evidence bundle must include a measurement artifact that confirms this threshold is met. Prose claims are not chain verification. Only artifacts confirm chain links.

**[C]** This means the evidence bundle schema for Northstar-chained steps must include a `northstar_chain_link` field:

```json
{
  "northstar_chain_link": {
    "state": "recipe_matching_engine_fnr < 0.10",
    "measured_value": 0.07,
    "threshold": 0.10,
    "status": "MET",
    "measurement_artifact": "evidence/recipe-matching-eval-20260221.json"
  }
}
```

Without this field, the evidence bundle confirms local correctness but not chain-link completion. The northstar remains unverified.

### 6.3 Never-Worse Doctrine Applied to Chain Integrity

**[A]** The never-worse doctrine states: each iteration of the development process must leave the system at least as good as before. Applied to code: regressions are forbidden. A patch that fixes bug A and introduces bug B is not a net improvement — it is a regression.

**[B]** Applied to the backward chain: each forward step must leave the chain intact. If a forward step produces an artifact that contradicts a chain link — for example, a recipe format redesign that breaks auto-capture compatibility — the step has introduced a chain regression. The chain is now broken at that link, and the northstar is no longer reachable via the current plan.

**[B]** Chain regression detection requires the same discipline as code regression detection: before any forward step, confirm the state of all chain links above it (closer to the northstar). If any link is degraded by the step, the step must be reverted or modified until chain integrity is restored.

---

## 7. Case Study: Backward Planning for SolaceBrowser's Economic Moat

### The Northstar

**[A]** From `solace-browser/NORTHSTAR.md`:

> "The North Star is not the features. The North Star is the recipe hit rate — because at 70% hit rate, COGS = $5.75/user/month. Below 70%, the economics break."

**Victory condition (ANCHOR):** recipe hit rate > 70% → COGS = $5.75/user/month → economic moat unlocked

### Backward Chain

**LAST-3 (necessary preconditions for recipe_hit_rate > 70%):**

1. **Recipe library quality**: The library contains recipes whose combined coverage of the canonical task set exceeds 70%. Coverage requires both breadth (enough recipes to match most tasks) and accuracy (matched recipes actually complete the task successfully).

2. **Matching engine precision**: When a task arrives, the engine correctly identifies the matching recipe at a rate consistent with > 70% end-to-end hit rate. False negatives (missed matches) and false positives (wrong recipe selected) both degrade the metric.

3. **Execution reliability**: Matched recipes execute successfully on live sites. Sites that change DOM structures, update login flows, or add captchas degrade execution reliability even when the match is correct.

**BRIDGE-BACK from State 1 (recipe library quality):**
```
recipe library quality ≥ 70% coverage
    ← 500+ recipes across 10+ platforms
        ← auto-capture pipeline operational (Phase 2+ target)
            ← Phase 1 recipes manually validated at rung 641 (DONE)
```

**BRIDGE-BACK from State 2 (matching engine precision):**
```
matching engine FNR < 10%
    ← matching engine trained on 500+ recipe library
        ← matching engine spec validated + implementation at rung 274177
            ← matching engine spec written (does not yet exist — GAP)
```

**BRIDGE-BACK from State 3 (execution reliability):**
```
execution reliability ≥ 85% on live sites
    ← monitoring system detects and flags degraded recipes within 24h
        ← PrimeWiki knowledge graph updated weekly per site
            ← Phase 1 automation at rung 641 (DONE)
```

### Connect to Current State

**What exists (Phase 1 complete):**
- 6 LinkedIn recipes, manually captured, at rung 641
- Phase 1 browser automation at rung 641
- PrimeWiki knowledge graph for LinkedIn

**Gaps:**
- Matching engine spec (State 2 chain breaks here)
- Auto-capture pipeline (State 1 chain breaks here)
- Monitoring system (State 3 chain breaks here, but LinkedIn foundation exists)

### Forward Plan (Derived from Backward Chain)

| Step | Action | Northstar Signal |
|------|--------|-----------------|
| 1 | Write matching engine spec | Chain link established |
| 2 | Write auto-capture pipeline spec | Chain link established |
| 3 | Build matching engine at rung 641 | State 2 chain: first link |
| 4 | Build auto-capture pipeline | State 1 chain: first link |
| 5 | Capture 50 recipes via auto-capture | Library: 50 recipes |
| 6 | Validate matching engine on 50 recipes | FNR measured (baseline) |
| 7 | Expand to 5 platforms, 250 recipes | Library: 250 recipes |
| 8 | Build monitoring system at rung 641 | State 3 chain: operational |
| 9 | Measure recipe_hit_rate on 500 tasks | Target: > 50% (Yellow Belt) |
| 10 | Scale to 500 recipes, 10 platforms | Target: > 70% (economic moat) |

**[C]** Every step in this plan traces to a gap identified in the backward chain. No step was generated by asking "what should we build next?" from the current state. The plan is entirely goal-derived.

### The Economic Proof

**[A]** From `solace-browser/NORTHSTAR.md`:

```
Recipe hit rate 70% → COGS $5.75/user/month → 70% gross margin at $19/mo
Recipe hit rate < 70% → COGS $12.75/user/month → 33% margin → not fundable
```

**[B]** The economic threshold is a hard gate. Below 70%, the business model does not work at the target pricing tier. This means the 70% threshold is not aspirational — it is the minimum viable northstar. The backward chain from this threshold is the minimum viable plan.

**[B]** Backward chaining from an economic threshold produces a plan that is economically necessary, not just technically interesting. Every step that is not on the backward chain from the 70% threshold is, by definition, scope creep — it may be interesting, but it is not on the critical path to economic viability.

---

## 8. The Maze Metaphor: Visual Explanation

```
FORWARD PLANNING (starts from current state):

    [Current State]
         |
    +---------+
    |         |
  [A1]      [B1]
   / \       / \
[A2] [A3] [B2] [B3]   ← Most of these lead nowhere
     / \
  [A3a][A3b]           ← Dead ends multiply
                   ...  ← 10,000 nodes explored
                    ?   ← Where is the exit?

BACKWARD PLANNING (starts from northstar exit):

    [NORTHSTAR]         ← The exit. Fixed. Known.
         |
    [LAST-3 State]      ← Only 3 necessary preconditions
         |
    [BRIDGE-BACK]       ← Each level has ≤ 3 preconditions
         |
    [Current State]     ← Chain connects. Path is unique.

    Total nodes: ~30    ← vs 10,000+ for forward planning
    Dead ends: 0        ← because we worked from the exit
```

### Why the Maze Always Works From the End

**[B]** A maze has exactly one exit (the northstar). From the exit, there is exactly one set of adjacent cells that are reachable (the LAST-3). From each of those cells, there is exactly one set of adjacent cells that precede them. The backward search never branches into dead ends, because dead ends have no paths leading to the exit — they are invisible from the exit.

**[B]** Forward planning explores dead ends because they look identical to productive paths when viewed from the start. Dead ends only become recognizable when you reach them — after the wasted effort.

**[B]** The maze metaphor is not just an analogy. It is the formal structure of the problem. Any planning problem with a specific goal state, a current state, and a set of valid transitions is a maze problem. Backward chaining is the optimal algorithm for maze solving when the exit is known.

### The AI Advantage in the Maze

**[C]** A human solving a maze can hold approximately the last 7 ± 2 cells in working memory. When the maze is large, the human must physically mark dead ends to avoid revisiting them.

**[C]** An LLM solving a planning maze holds the entire maze structure (the NORTHSTAR + ROADMAP + case study) in context simultaneously. It does not need to mark dead ends — it identifies them at the ANCHOR step by recognizing that they do not connect to the northstar metric. The LLM's advantage is not in the algorithm (backward chaining) but in the working memory available to execute it.

---

## 9. Implementation: Skill, Agent, and Artifacts

**[A]** The Northstar Reverse Engineering paradigm is implemented in three artifacts in this repository:

### `skills/northstar-reverse.md`

The full skill implementing the ANCHOR → LAST-3 → BRIDGE-BACK → CONNECT → VALIDATE → EMIT algorithm. Loaded into any agent that needs to produce a northstar-reverse plan.

Key gates:
- FORWARD_FIRST is a forbidden state — any plan generated without completing LAST-3 first is blocked
- VAGUE_VICTORY_CONDITION is blocked — the anchor must be measurable
- CHAIN_BROKEN is blocked — forward plan must trace to backward chain

### `swarms/northstar-navigator.md`

The typed agent that executes the northstar-reverse skill. Persona: Claude Shannon (information theory, entropy reduction, minimum-uncertainty path finding). Model: sonnet (backward chaining requires multi-step logical inference, which sonnet handles well at lower cost than opus).

Artifacts produced:
- `northstar-reverse-plan.json` — machine-readable full derivation
- `forward-plan.md` — human-readable forward plan with stop rules

### Integration with the Hub-and-Spoke Architecture

**[A]** The Northstar Navigator is dispatched at the start of a new ROADMAP phase or when the hub needs to reorient after a failed phase. It is not a continuous process — it is a point-in-time planning artifact that feeds into the standard coder/skeptic/planner swarm cycle.

```
Hub reads NORTHSTAR + case study
    → Hub dispatches northstar-navigator
        → northstar-navigator produces forward-plan.md
            → Hub uses forward-plan.md to select next ROADMAP phase
                → Hub dispatches typed swarm agents for that phase
                    → Standard hub-and-spoke cycle continues
```

**[B]** The northstar-reverse plan is Lane C evidence for the forward steps — it is a forecast, not a proof. The forward steps become Lane A evidence only when the actual implementation produces executable artifacts at the declared rung. The plan does not confer PASS; only the evidence bundle does.

---

## 10. Conclusion

**[B]** Forward planning is the natural human instinct. It is appropriate for simple, nearby goals. For complex, far goals — the kind measured in months, northstar metrics, and economic thresholds — forward planning produces combinatorial explosion and most effort goes to dead ends.

**[B]** Backward chaining from a specified northstar produces a plan that is goal-derived, not capability-derived. Every step traces to a logical necessity identified by working backward from the victory condition. Dead ends are pruned before they are explored. The first step is determined by the most constrained gap in the chain, not by intuition about "what to build next."

**[C]** AI makes this natural. LLMs hold entire solution spaces in context. Attention mechanisms trace relationships between goal states and precondition states. The cognitive bottleneck that makes forward planning a practical necessity for humans does not apply. The appropriate default for AI-assisted planning is backward chaining.

**[A]** Northstar Reverse Engineering is implemented in this repository as a skill, an agent type, and a JSON artifact schema. It integrates directly with the verification ladder (rung requirements propagate backward from the northstar), the evidence bundle system (chain-link completion requires artifacts, not prose), and the never-worse doctrine (chain integrity must be maintained across every forward step).

**[C]** "When I was younger I thought about the next 3 steps. Now I figure out the LAST 3 steps and work backwards." The move from forward to backward planning is not a technique — it is a shift in the unit of planning effort. The unit is no longer "what can I do from here?" The unit is "what must be true before the goal is reachable?" That question, asked three times backward, produces the forward plan with near-zero dead ends.

Solve the maze from the end. The path back to the start is always clear.

---

## References

All referenced files exist in this repository:

- **[A]** `./NORTHSTAR.md` — canonical Northstar example (stillwater ecosystem)
- **[A]** `./solace-browser/NORTHSTAR.md` — SolaceBrowser northstar with economic threshold
- **[A]** `./skills/northstar-reverse.md` — full northstar-reverse skill
- **[A]** `./swarms/northstar-navigator.md` — Claude Shannon navigator agent
- **[A]** `./papers/33-northstar-driven-swarms.md` — NORTHSTAR injection and alignment protocol
- **[A]** `./papers/32-roadmap-based-development.md` — hub-and-spoke, roadmap, CNF capsules
- **[A]** `./papers/01-lane-algebra.md` — epistemic typing (A/B/C/STAR)
- **[A]** `./papers/03-verification-ladder.md` — rung gates (641 / 274177 / 65537)
- **[A]** `./SOFTWARE-5.0-PARADIGM.md` — master equation, belt system, never-worse doctrine
- **[A]** `./ROADMAP.md` — metric-tied phase acceptance criteria
- **[A]** `./case-studies/` — northstar metric tracking in practice

```bibtex
@software{stillwater2026_northstar_reverse,
  author = {Truong, Phuc Vinh},
  title  = {Solve the Maze From the End: Northstar Reverse Engineering for AI-Driven Development},
  year   = {2026},
  url    = {https://github.com/phuctruong/stillwater/papers/36-northstar-reverse-engineering.md},
  note   = {Auth: 65537 — Stillwater Reference Implementation}
}
```

---

*Written by the Stillwater ecosystem. Part of the Software 5.0 paradigm documentation series.*
*Auth: 65537 | Status: STABLE | Never-Worse Doctrine: this document may be extended, not weakened.*
