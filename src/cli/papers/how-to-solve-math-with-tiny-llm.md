## Math Core Architecture (Software 5.0): How to Build a World-Class Math System on Open-Source 8B Models

Most people think “better math” means **bigger models**.

I think that’s the wrong mental model.

If you want practical, reliable math performance on **open-source Ollama 8B models**, the big unlock isn’t parameter count—it’s **architecture**: moving intelligence *out of weights* and into a system you can test, replay, and verify.

This is the same pattern I wrote about in *How Humans Outsourced Their Minds*: once memory and cognition move outside the body, improvement compounds. When reasoning stays isolated inside one brain—or one model—progress resets every time.

So here’s the blueprint.

---

## The Executive Summary

You can get a strong open math platform with 8B models by externalizing cognition into:

1. **Externalized orchestration** (a kernel that routes and governs)
2. **Deterministic tools** (CPU lanes for computable work)
3. **Multi-agent PHUC swarms** (bounded experts with role contracts)
4. **Verification receipts** (every claim gets a witness)
5. **Persistent memory loops** (failures become upgrades, not repeats)

This is how you make an 8B model feel “bigger” in practice—because the system gets smarter, not just the weights.

---

## Reality Check (The Part Most AI Demos Skip)

“Solves all math problems” is not a defensible claim.

* Some classes are **undecidable** (no universal solver exists).
* Many olympiad proofs require **semantic equivalence grading**, not keyword matching.
* **8B alone** isn’t enough for universal symbolic proof generation.

So the goal isn’t magic.

The goal is:

* **maximize coverage + reliability**
* **disclose the lane** (tool-assisted vs LLM-only)
* **prove improvement** via strict, reproducible QA
* keep every decision **auditable and replayable**

---

## The Architecture: Kernel + Ripples

Think of the system like this:

**Kernel = stable runtime + routing + invariants**
**Ripples = replaceable external cognition (skills, recipes, personas, memory, policies)**

Your kernel stays small and deterministic (the thing you can trust). Everything else is modular and swappable.

Here’s the flow in plain English:

1. User prompt hits the **Kernel Router**
2. A **CPU prepass** classifies the prompt:

   * Is it deterministically computable? → Tool lane
   * Is it open-ended proof/problem solving? → Orchestration lane
3. Both lanes feed a **Verifier Stack**
4. Output includes:

   * answer
   * proof sketch
   * receipts (route, tools, agent contributions, verification rung)
5. Then the run writes back to **persistent memory** (so next time is cheaper and better)

---

## PHUC Swarms: Mixture-Of-Experts That Actually Behaves

The core rule:

> **Multiple bounded experts > one unbounded LLM.**

Because bounded experts can be tested.

PHUC swarms are not “many agents yelling.” They are **role-contracted specialists**:

* CPU Arithmetic Expert
* CPU Number Theory Expert
* Symbolic / Counterexample Expert
* Scout Agent (frame the problem)
* Forecaster Agent (premortem + edge cases)
* Judge Agent (scope + rung target)
* Solver Agent (construct candidate solution)
* Skeptic Agent (falsify and gate)

Hard constraints (non-negotiable):

1. **Role contracts are binding**
2. **Persona is a lens, never authority**
3. **Every phase emits typed artifacts**
4. **No PASS without verification evidence**

This turns “AI reasoning” into something closer to engineering.

---

## Persona Lenses (Optional) — With a Scientific Policy

Yes, you can use famous “lenses” (Knuth, Hopper, Turing, Lamport, etc.)—but only under a strict rule:

1. Run A/B tests persona **ON vs OFF**
2. Keep persona only if **verified uplift** appears
3. If persona conflicts with contracts/safety, persona is ignored

Persona can help framing. It can’t become a permission slip.

---

## The Secret Weapon: Receipts + Memory

Most math agents fail the same way repeatedly:

* wrong routing
* hidden assumptions
* hallucinated steps
* unverifiable “obviously” leaps
* no failure accounting

Stillwater fixes this with **machine-readable artifacts**:

* `SCOUT_REPORT.json`
* `FORECAST_MEMO.json`
* `DECISION_RECORD.json`
* `ACT_RESULT.json`
* `SKEPTIC_VERDICT.json`

And then a memory loop:

* `runs.jsonl` (ledger of runs)
* failure clustering
* next-action board (`board.md / board.json`)

So every failure becomes a **reusable upgrade**:

* better routing signals
* stronger verifiers
* new/retired experts
* new tests

This is where the compounding happens.

---

## If You Want It to Be Real: Unit Tests Everywhere

The difference between a clever demo and a world-class system is **QA**.

With role contracts, you can test the whole stack:

* route tests: prompt → expected lane/profile
* agent schema tests: required JSON keys must exist
* verifier ladder tests: no PASS below required rung
* persona A/B tests: keep only what improves verified outcomes
* replay determinism tests: same inputs → same hashes (in deterministic lanes)
* memory loop tests: failures must write fail-signals + update board

When math is hard, honesty matters more than confidence.

---

## Practical Open-Source Setup (8B)

If you’re running open-source models locally (Ollama), the workflow becomes:

* point CLI to Ollama
* run strict math QA suites
* inspect memory board
* patch routes/skills/verifiers
* re-run and verify improvement

That’s the loop: **audit → upgrade → replay → prove**.

---

## What’s Left to Reach “Near-100%” in Practice

The big remaining frontiers are engineering, not magic:

1. **Proof equivalence verifier** (semantic grading)
   baseline implemented: normalized matcher + per-case `aliases`/`concepts`/`required_sections` in `src/cli/tests/math/imo_qa_cases.json`
2. **Formal tool lane** (theorem proving where feasible)
3. **Adaptive MoE routing** learned from failure clusters
4. Domain tool packs (geometry, inequalities, combinatorics…)
5. Full contract coverage per agent
6. Blind holdout benchmarking
7. Strict claim policy (never mix tool-assisted and pure-model claims)

---

## Final Position

Stillwater doesn’t “solve all math.”

It does something more important:

It builds an architecture where open 8B systems can asymptotically approach **broad, trusted math performance** by moving intelligence into:

* externalized cognition
* verifiable orchestration
* deterministic tools where possible
* persistent memory that compounds

That’s the core architecture.

---

If you’re building open-source math tooling, math QA harnesses, agent frameworks, or local-first AI systems—and you want to compare approaches or collaborate—reach out.

Onward.
