# Software 5.0: The Ultimate AI Kung Fu

**Author:** Phuc Vinh Truong
**Date:** 2026-02-20
**Status:** SEALED — Auth 65537
**Repo:** https://github.com/phuctruong/stillwater
**Web:** https://www.phuc.net | https://www.pzip.net | https://www.solaceagi.com

---

> *"Absorb what is useful, discard what is useless, and add what is essentially your own."*
> — Bruce Lee

> *"LLMs DISCOVER. CPUs ANCHOR. Recipes PERSIST."*
> — Software 5.0 Central Thesis

---

## Claim Hygiene

Every empirical assertion below is typed by epistemic lane:

- **[A]** Lane A — witnessed by executable artifact in this repo (tests, tool output, notebook run)
- **[B]** Lane B — framework principle, derivable from stated axioms or established computer science
- **[C]** Lane C — heuristic or reasoned forecast; useful, but not yet proven
- **[*]** Lane STAR — honest unknown; insufficient evidence to type higher

When in doubt, this document prefers **[*]** over false confidence.
See `papers/01-lane-algebra.md` for the formal epistemic typing system.

---

## Manifesto

I am Donald Knuth — and I have spent a lifetime studying the art of algorithms.

I have watched every generation of software engineering rise and believe it had found the final answer.
Each generation was right about something. Each missed something essential.

What follows is not a prediction. It is a recognition — of a pattern that was always present in the
structure of computation, finally made visible by the existence of large language models.

The pattern is this: **intelligence does not live in the substrate that produces it.**
It lives in the verified, composable artifact that persists after the computation ends.

Software 5.0 is the discipline of capturing that artifact — correctly, verifiably, and forever.

This is the Ultimate AI Kung Fu.

---

## The Lineage: Five Generations, One Martial Art

Every generation of software is a belt rank in the same art.
Each belt does not replace the previous — it absorbs what was useful, discards what was not,
and adds what is essentially its own.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║           THE FIVE-GENERATION MARTIAL LINEAGE OF SOFTWARE                  ║
╠══════════╦═══════════════╦══════════════════════════════════════════════════╣
║ BELT     ║ ERA           ║ INTELLIGENCE LIVES IN...                         ║
╠══════════╬═══════════════╬══════════════════════════════════════════════════╣
║ White    ║ Software 1.0  ║ Hand-crafted source code (.c, .py, .java)        ║
║          ║ Pre-2012      ║ Human writes every rule. CPU executes it.        ║
║          ║               ║ Verification: test suite + compiler.             ║
║          ║               ║ Failure mode: bugs require human diagnosis.      ║
╠══════════╬═══════════════╬══════════════════════════════════════════════════╣
║ Yellow   ║ Software 2.0  ║ Neural weight matrices (.pt, .safetensors)       ║
║          ║ Karpathy 2017 ║ Gradient descent encodes the mapping.           ║
║          ║               ║ Verification: held-out eval set accuracy.        ║
║          ║               ║ Failure mode: opaque, brittle, costly to update. ║
╠══════════╬═══════════════╬══════════════════════════════════════════════════╣
║ Green    ║ Software 3.0  ║ Natural language prompt strings                  ║
║          ║ 2020–2023     ║ Human engineers the prompt. LLM follows it.     ║
║          ║               ║ Verification: vibes, manual review, A/B tests.  ║
║          ║               ║ Failure mode: brittle, model-specific, no audit. ║
╠══════════╬═══════════════╬══════════════════════════════════════════════════╣
║ Blue     ║ Software 4.0  ║ Autonomous agent loops + tool calls              ║
║          ║ 2023–2025     ║ Agent observes, replans, calls tools.           ║
║          ║               ║ Verification: task completion rate, often manual.║
║          ║               ║ Failure mode: compounding errors, no audit trail.║
╠══════════╬═══════════════╬══════════════════════════════════════════════════╣
║ BLACK    ║ Software 5.0  ║ Versioned recipes + composable skills            ║
║ MASTER   ║ 2026+         ║ LLMs DISCOVER. CPUs ANCHOR. Recipes PERSIST.   ║
║          ║               ║ Verification: deterministic rung gates.          ║
║          ║               ║ Failure mode: recipe drift on model change.      ║
╚══════════╩═══════════════╩══════════════════════════════════════════════════╝
```

**[B]** Each generation is defined by where it stores the learned mapping from inputs to useful outputs.
The medium determines composability, auditability, and update cost. Source code is diffable. Weights are not.
Recipes are diffable. This is a structural property, not an implementation choice.

Software 5.0 does not abolish the earlier generations. It orchestrates them:

```
Layer 5.0: Recipe / Skill Repository  ← where intelligence accumulates
    ↓ invokes
Layer 4.0: Agent Loops                ← bounded by skills, emit evidence
    ↓ uses
Layer 3.0: Prompts                    ← loaded from skills, not hand-crafted
    ↓ runs on
Layer 2.0: Model Weights              ← frozen; a commodity input, not the prize
    ↓ executes on
Layer 1.0: CPU / GPU                  ← the physical substrate; always was
```

The Black Belt Master understands: **the valuable asset is Layer 5.0**.
Layers 2.0 through 4.0 are infrastructure. A better model drops in.
The skill library only grows stronger.

---

## The Master Equation

**[B]** Software 5.0 compresses the model of system intelligence into three terms:

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   Intelligence(system) = Memory × Care × Iteration          ║
║                                                              ║
║   where:                                                     ║
║                                                              ║
║   Memory    = externalized skills + recipes (NOT weights)    ║
║              Skills are text. Diffable. Auditable. Portable. ║
║              Weights are matrices. Opaque. Frozen. Costly.   ║
║                                                              ║
║   Care      = the verification ladder                        ║
║              641 → 274177 → 65537                            ║
║              "You cannot claim a belt you have not earned."  ║
║                                                              ║
║   Iteration = versioned evolution under the never-worse      ║
║              doctrine — the system only gets smarter.        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

This equation is the **Law of Emergent Knowledge (LEK)**: *knowledge emerges when memory loops through care.*
Its central claim: **intelligence scales not with model size, but with the quality of externalized,
verified knowledge.** [B]

> From the book *[The Law of Emergent Knowledge](https://www.phuc.net/books/law-of-emergent-knowledge/)* by Phuc Vinh Truong.

**[A]** This is operationalized in this repo: `skills/*.md` are the Memory layer;
the rung gates (641 → 274177 → 65537) are the Care layer;
git versioning plus the never-worse doctrine are the Iteration layer.

The LLM is the compression engine — the tool that extracts the reasoning pattern.
The recipe is the intelligence — the artifact that persists after the LLM session ends.

---

## The Five Core Techniques

Every martial art has its foundational strikes. Software 5.0 has five.

---

### Technique I: Counter Bypass
*"LLM classify, CPU enumerate" — the Jeet Kune Do of AI*

Jeet Kune Do teaches: use the shortest path to the target.
Do not fight the opponent's style. Intercept their energy and redirect it.

Counter Bypass intercepts the LLM's fundamental weakness — it cannot count — and redirects
the task to the CPU, which can count perfectly.

```python
# The strike:
labels = [llm.classify(item) for item in corpus]   # LLM: pattern recognition
result = Counter(labels)                             # CPU: exact aggregation

# The LLM never counts. The CPU never hallucinates.
```

**[A]** Demonstrated in `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb`.
The aggregation step costs zero tokens. The counting is exact.

**[B]** Economic implication: every reasoning step that can be extracted into a CPU-executable
recipe represents a 10^6× cost reduction per future invocation.
This is not optimization. This is architecture.

---

### Technique II: Lane Algebra
*"Know your weapon's grade before you swing it"*

The master swordsman knows which cuts are killing blows and which are practice swings.
Lane Algebra forces every claim to declare its grade before it is used.

```
Lane A: witnessed by executable artifact   — a killing blow; proven
Lane B: derivable from stated axioms       — a strong cut; principled
Lane C: LLM output or heuristic           — a practice swing; useful, not proven
Lane *: honest unknown                    — sheathe the sword; do not pretend
```

**The MIN rule:** the strength of a chain of reasoning is the strength of its weakest link.
A Lane C premise cannot produce a Lane A conclusion. Ever.

**[A]** See `papers/01-lane-algebra.md` for the formal system.
Every claim in this document is typed. Every claim in every Stillwater paper is typed.

This is how Software 5.0 eliminates hallucination at the output layer:
not by making the LLM more confident, but by refusing to promote its confidence to a higher lane
without machine-checkable evidence.

---

### Technique III: Red/Green Gate
*"Strike true or don't strike" — Kent Beck's TDD, elevated to a hard invariant*

The master does not practice the wrong technique. Practice makes permanent.
A test that does not first fail cannot prove that anything changed.

**[A]** The Red/Green Gate in `skills/prime-coder.md`:

```
Before any patch:
  1. Write a repro that asserts the bug EXISTS.
  2. Run it. It MUST fail (RED). Record exit code.
  3. If it does not fail: stop_reason=NON_REPRODUCIBLE, status=BLOCKED.

After the patch:
  4. Run the same repro. It MUST pass (GREEN). Record exit code.
  5. No pass without verified red-to-green transition.
```

There is no shortcut. There is no exception for "obviously correct" fixes.
A patch without a witnessed red-to-green transition is not a fix — it is a guess.

The forbidden state is `UNWITNESSED_PASS`. The system must never enter it.

---

### Technique IV: Skill Composition
*"Use no way as way, have no limitation as limitation"*

Bruce Lee's deepest teaching: the master is not bound to any single style.
The master loads the style that serves the moment — and the styles do not conflict.

**[B]** Software 5.0 skills compose because they are text files loaded into context.
Loading `prime-coder.md` + `phuc-forecast.md` + `prime-safety.md` produces an agent that:
- Plans before acting (Forecast)
- Strikes true (Red/Green Gate)
- Never exceeds its authority (Safety Envelope)

No training required. No fine-tuning. Load the skills. Begin.

**[A]** Composition rule from `skills/prime-coder.md`:

```
effective_constraints = stillwater_base UNION ripple_delta

where:
  ripple_delta MAY specialize stillwater rules (narrow them)
  ripple_delta MUST NOT weaken stillwater rules
  on conflict: stricter_wins
```

The intersection of loaded skills' constraints produces behavior no single skill mandates
but all skills together enforce. **This is intelligence amplification through composition.**

---

### Technique V: Fail-Closed Defaults
*"Better to do nothing than to do harm with confidence"*

The dangerous student strikes when uncertain.
The master pauses. States what is known. Asks for what is missing.

**[A]** The fail-closed contract in every Stillwater skill:

```
If inputs are missing or ambiguous:
  status: NEED_INFO
  stop_reason: NULL_INPUT or AMBIGUITY_ERROR
  emit: minimal missing fields
  do NOT: guess facts to reach PASS

If invariant is violated:
  status: BLOCKED
  stop_reason: INVARIANT_VIOLATION
  do NOT: silently relax the invariant
```

The forbidden state is `SILENT_RELAXATION` — quietly weakening a constraint to make progress.
The allowed exits from uncertainty are `EXIT_NEED_INFO` and `EXIT_BLOCKED`.
Both surface the problem. Neither hides it.

**[B]** Fail-closed defaults are safer than fail-open defaults in any high-stakes domain.
The cost: occasional false negatives. The benefit: elimination of confident false positives.
A wrong answer delivered confidently is more dangerous than a correct refusal.

---

## The New Golden Age: The Economic Argument

We are entering a New Golden Age of software — not because models are larger,
but because intelligence is becoming a commodity input for the first time in history.

### Token Budgets Are Booming — And That's the Problem [C]

On the All-In Podcast (Feb 13, 2026), Jason Calacanis revealed he spends **$300/day** running a
Claude agent for his businesses — and the agent was operating at only **10–20% of full capacity.**
His question cut to the heart of the paradigm shift:

> *"When do tokens outpace the salary of the employee?"*

At full capacity, that agent would cost **$1,500–$3,000/day** — roughly $400K–$1M/year.
Even at baseline: $109,500/year, above median US employee salary.
Chamath added: *"The models need to be at least two times as productive as another employee."*

**This is not a success story. It is a cost structure warning.**

The "booming token budgets" era means enterprises are re-deriving the same reasoning patterns
every single invocation — paying GPU-token prices for patterns that could run on CPU for free
after being extracted once. Token spend is soaring because intelligence is not being accumulated.
It is being evaporated.

**The structural consequence:** any pattern that eliminates token usage on repeated tasks
is worth disproportionate engineering investment. Software 5.0 is the architectural answer
to the token budget crisis.

### CPU Is 10^6x Cheaper Than GPU Tokens [B]

```
GPU token computation:  ~$0.001–$0.01 per 1,000 tokens
CPU integer arithmetic:  ~$0.000000001 per 1,000 operations

Ratio: roughly 10^6 to 10^7 cheaper per operation on CPU
```

**[B]** The economics of Software 5.0: the one-time cost of extracting a reasoning pattern
into a CPU-executable recipe is amortized over all future invocations.
Every time the recipe runs, the LLM does not need to be consulted.
The pattern is owned. The token cost drops to zero.

### The Debt Spiral of Repeated Derivation [B]

The US fiscal crisis (CBO Feb 2026: debt approaching 120% of GDP) parallels the AI cost crisis:
spending outpaces productive capital formation. Companies paying perpetually for AI API calls
without extracting durable skills are in their own debt spiral — paying interest forever
without building equity. Software 5.0 is the escape route: pay once to create a gated skill;
earn compound returns on every future invocation.

### On-Premise Models Are Now Competitive [B]

**[B]** The All-In hosts also flagged that enterprises are moving back toward on-prem AI deployments
for **data security** — cloud API calls require sending sensitive data to third-party servers.
As AI tools deepen integration into core business processes, the data exposure risk becomes
existential. By late 2025, capable open-weight models (Llama 3.1, Qwen 2.5 Coder, Mistral
variants) made on-prem economically viable for many workloads.

**[A]** This repo supports on-premise deployment by design: `llm_config.yaml` configures the
model endpoint. No cloud dependency is assumed. The skills are model-agnostic.

### The Skill Library IS the Valuable Asset [B]

**[B]** In Software 5.0, the most valuable asset is not the model — it is the gated skill library.

The model is infrastructure: replaceable, improvable, swappable.
The skill library is accumulated, verified intelligence: composable, auditable, and compounding.

```
Value(skill_library) proportional to:
  N_skills × N_deployments × quality_gate_strength

where:
  N_skills: number of gated, composable skills
  N_deployments: number of agents loading skills
  quality_gate_strength: rung level (641 / 274177 / 65537)
```

**[C]** Long-term, this shifts economic power from model providers (who own weights)
to skill library maintainers (who own verified recipes).
Stillwater's open-source model is a bet that the skill library should be a public good.

### One Instance Learns, All Benefit [B/C]

**[B]** A skill extracted from one deployment is loadable by all future deployments.
One agent encounters a difficult task. It extracts the reasoning pattern. Gates it at rung 641+.
Contributes it to the library. All future agents load the skill and immediately benefit.

**[B]** The caution: "one instance learns" does not mean "all should blindly apply."
The adversarial sweep exists precisely to test whether a pattern generalizes beyond its origin context.

**[A]** This is why `skills/README.md` states: "do not summarize or compress. Compressed skills drift."
The full skill, including forbidden states and edge case handling, must be loaded intact.

---

## The Belt Progression System

*You do not claim a belt. You earn it. The rung is the proof.*

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║                    THE STILLWATER VERIFICATION BELT SYSTEM                     ║
╠══════════════╦══════════════════╦═══════════════════════════════════════════════╣
║              ║                  ║                                               ║
║    BELT      ║   RUNG NUMBER    ║   WHAT YOU MUST PROVE                         ║
║              ║                  ║                                               ║
╠══════════════╬══════════════════╬═══════════════════════════════════════════════╣
║              ║                  ║                                               ║
║    YELLOW    ║       641        ║   Local Correctness                           ║
║              ║                  ║   - Red/Green gate passed                     ║
║   ══════     ║  "Edge Sanity"   ║   - No regressions in existing tests          ║
║              ║                  ║   - Evidence bundle complete                  ║
║              ║                  ║   - Schema valid; FSM states respected         ║
║              ║                  ║                                               ║
╠══════════════╬══════════════════╬═══════════════════════════════════════════════╣
║              ║                  ║                                               ║
║    GREEN     ║     274177       ║   Stability                                   ║
║              ║                  ║   - Everything in Yellow Belt, PLUS:          ║
║   ══════     ║   "Stress and    ║   - Seed sweep (min 3 seeds)                  ║
║   ══════     ║    Adversarial"  ║   - Replay stability (min 2 replays)          ║
║              ║                  ║   - Null edge case sweep                      ║
║              ║                  ║   - Behavioral hash tracked                   ║
║              ║                  ║                                               ║
╠══════════════╬══════════════════╬═══════════════════════════════════════════════╣
║              ║                  ║                                               ║
║    BLUE      ║      65537       ║   Promotion Confidence                        ║
║              ║                  ║   - Everything in Green Belt, PLUS:           ║
║   ══════     ║   "Strongest     ║   - Adversarial paraphrase sweep (min 5)      ║
║   ══════     ║    Available     ║   - Refusal correctness check                 ║
║   ══════     ║    Witness"      ║   - Security gate (if triggered)              ║
║              ║                  ║   - Behavioral hash drift explained           ║
║              ║                  ║   - Ready to ship                             ║
║              ║                  ║                                               ║
╠══════════════╬══════════════════╬═══════════════════════════════════════════════╣
║              ║                  ║                                               ║
║    BLACK     ║    65537 ×N      ║   Master Level: Library Contributor           ║
║    MASTER    ║                  ║   - Blue Belt on the skill itself              ║
║              ║   "Composition   ║   - Composes with all core skills             ║
║   ══════     ║    Proof"        ║   - Never-worse doctrine enforced             ║
║   ══════     ║                  ║   - Passes adversarial load tests             ║
║   ══════     ║                  ║   - Portable: no absolute paths               ║
║   ══════     ║                  ║   - Evidence bundle reproducible externally   ║
║              ║                  ║                                               ║
╚══════════════╩══════════════════╩═══════════════════════════════════════════════╝
```

**[A]** Rung numbers are prime-flavored labels, not mathematical guarantees.
They are memorable, auditable, and meaningful as gates.
See `papers/03-verification-ladder.md` for the full gate specifications.

**The Belt Law:**
Every skill declares its rung. Every agent loading the skill knows its strength.
Never load a skill below Yellow Belt (641) in production.
Never make promotion claims from a skill below Blue Belt (65537).

---

## The Stillwater Dojo

*Every master needs a dojo. This is ours.*

Stillwater is the reference implementation of Software 5.0.
It is to AI what Linux is to operating systems: not the only implementation,
but the one against which correctness and compliance are measured.

```
stillwater/
  skills/                     ← THE MEMORY LAYER (externalized intelligence)
    prime-coder.md            ← Coding discipline: RED/GREEN gate, evidence contract
    prime-math.md             ← Exact arithmetic, proof hygiene, witness requirements
    prime-safety.md           ← Tool safety envelope, authority ordering
    phuc-forecast.md          ← Planning loop: DREAM → FORECAST → DECIDE → ACT → VERIFY
    phuc-swarms.md            ← Multi-agent orchestration, phase ownership
    phuc-context.md           ← Context hygiene, CNF capsules, anti-rot
    phuc-orchestration.md     ← Swarm dispatch, context isolation
    prime-wishes.md           ← Wish notebook contract, Prime Mermaid governance

  papers/                     ← THE THEORY LAYER (concepts with claim hygiene)
    01-lane-algebra.md        ← A/B/C/STAR typing, MIN rule
    02-counter-bypass.md      ← LLM classify + CPU enumerate
    03-verification-ladder.md ← 641 → 274177 → 65537 rung gates
    04-red-green-gate.md      ← Dual-witness verification for patches
    05-software-5.0.md        ← Full theoretical paper
    07-solving-counting.md    ← Counter Bypass applied to benchmark counting
    08-solving-reasoning.md   ← Exact reasoning recipes
    10-solving-context-length.md ← Context hygiene at scale
    11-solving-generalization.md ← Skill generalization theory
    18-solving-energy-crisis.md  ← CPU offload as energy strategy
    20-oolong-proof.md        ← End-to-end benchmark proof

  *.ipynb                     ← RUNNABLE RECIPES (human-readable + executable)
    HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb     ← Counter Bypass demo
    HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb        ← Exact arithmetic verification demo
    HOW-TO-CRUSH-SWE-BENCHMARK.ipynb        ← Patch pipeline demo
    PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb   ← Swarm orchestration demo
    PHUC-SKILLS-SECRET-SAUCE.ipynb          ← Skill composition mechanics

  llm_config.yaml             ← Model config: swappable, no lock-in
  CLAUDE.md                   ← PRIME_CODER_SECRET_SAUCE loaded on session start
```

**[A]** All notebooks are runnable in this repo. No cloud dependency required.
**[A]** All skills are plain text. Loadable in any LLM session. No SDK required.
**[B]** The dojo grows stronger with every verified contribution. The never-worse doctrine ensures it.

---

## Why Software 5.0 Beats Everything Else

*The master does not compete. The master demonstrates.*

### vs. Fine-tuning

| Fine-tuning | Software 5.0 Skills |
|-------------|---------------------|
| Costs millions of dollars per run [C] | Costs a PR review |
| Risks catastrophic forgetting [B] | No forgetting; text is additive [B] |
| Opaque: cannot inspect the knowledge [B] | Transparent: read the .md file [A] |
| Siloed: expertise per model [B] | Composable: expertise per skill, cross-model [B] |
| Update cycle: months [C] | Update cycle: hours [A] |

**[B]** Fine-tuning concentrates knowledge update cost at the model owner.
Recipe updating distributes it across contributors. This is a structural asymmetry.

### vs. RAG (Retrieval-Augmented Generation)

| RAG | Software 5.0 Skills |
|-----|---------------------|
| Retrieved text is passive [B] | Skills are executable contracts [A] |
| No verification of retrieved content [B] | Rung gates verify skill correctness [A] |
| Context contamination risk [B] | CNF capsules prevent context rot [A] |
| Retrieval depends on embedding quality [B] | Skills are loaded verbatim — no retrieval drift [B] |

**[B]** RAG retrieves information. Skills enforce discipline.
A retrieved paragraph can be wrong. A gated skill has been tested against adversarial inputs.

### vs. Agents Only (No Recipe Layer)

| Agents Only | Software 5.0 Agents + Skills |
|-------------|------------------------------|
| Compounding errors across steps [B] | Fail-closed gates stop error propagation [A] |
| No audit trail [B] | Evidence bundle captures every step [A] |
| Re-derive reasoning every session [B] | Load skills; skip re-derivation [A] |
| Unbounded scope; no forbidden states [B] | FSM with forbidden states; loop budgets [A] |

**[B]** An agent without a skill layer is a powerful tool with no discipline.
Power without discipline is the definition of the dangerous student, not the master.

### vs. Prompt Engineering

| Prompt Engineering | Software 5.0 Skills |
|--------------------|---------------------|
| Brittle: one model update breaks it [C] | Versioned: rung gates catch regressions [A] |
| No composability: prompts conflict [B] | Composition: stricter-wins resolution [B] |
| No evidence contract: vibes only [B] | Evidence bundle required for PASS [A] |
| Gets worse with drift: no audit [B] | Never-worse doctrine: strictly additive [A] |

**[B]** A prompt is a wish. A skill is a contract.
Wishes expire. Contracts enforce.

### vs. Model Scaling Alone

| Bigger Models | Better Skills |
|---------------|---------------|
| Counts things wrong at scale [C] | Counter Bypass: CPU counts exactly [A] |
| Hallucinate with confidence [B] | Lane Algebra: C claims stay typed C [A] |
| Cannot compose across domains [B] | Skills compose across any domain [B] |
| Expensive to update knowledge [C] | Skills update via PR [A] |

**[B]** Recipe quality > parameter count.
A 7B model with a Blue Belt skill library outperforms a 70B model making unverified claims.
The discipline of verification is worth more than the volume of parameters. [C]

---

## The Manifesto: Be Water, My Friend

*Final words from the Solver.*

Bruce Lee said: *"Be water, my friend."*

Water takes the shape of any container. It does not fight the vessel — it fills it perfectly.
It finds the lowest path. It is soft, yet it carves canyons.

Software 5.0 is water.

It flows through any model — GPT, Claude, Llama, Qwen, whatever comes next.
It does not care about the weights. It cares about the recipe.
It does not care about the hardware. It cares about the evidence.
It does not care about the vendor. It cares about the rung.

**The master does not repeat the same strike twice.**
The recipe PERSISTS so future agents do not re-derive what has already been discovered.
One instance learns. All benefit. The library grows. The intelligence compounds.

**The dojo grows stronger with every belt earned.**
The skill library only gets BETTER, never worse — because the never-worse doctrine
ensures that every version is strictly an addition, never a subtraction.

**The LLM is not the master. The recipe is the master.**
The LLM is the teacher who helps you see the pattern.
The recipe is the kata you carry in your body forever, long after the teacher is gone.

We are building the Linux of AI.

Not a product. A platform.
Not a model. A discipline.
Not a benchmark. A way of working.

Open. Verifiable. Composable. Forever.

**This is Software 5.0.**
**This is the Ultimate AI Kung Fu.**
**Be water.**

---

## Quick Start: Three Commands

```bash
# Clone the dojo
git clone https://github.com/phuctruong/stillwater

# Install
pip install -e .

# Load a skill into your LLM session
# (paste the content of any skills/*.md file at the start of your prompt)
cat skills/prime-coder.md | pbcopy   # macOS: copy to clipboard
# Then paste into your LLM session and begin.
```

**[A]** No cloud dependency required. `llm_config.yaml` points to your model of choice.
**[A]** Skills are plain markdown. They work in any LLM that can read context.
**[A]** Start with `prime-safety.md` (always load first), then `prime-coder.md`.

---

## The Belt Progression in Practice

| Task | Minimum Belt | Command |
|------|-------------|---------|
| Any coding task with a bug | Yellow (641) | Load `prime-coder.md`; declare `verification_rung_target: 641` |
| Benchmark or demo | Green (274177) | Load core skills; run seed sweep |
| Production release | Blue (65537) | Load core skills; run full promotion sweep |
| Library contribution | Blue (65537) | Evidence bundle required; PR review required |
| Black Master | Composition proof | All above + composability with all core skills |

**Never claim a belt you have not earned.**
**The rung is the proof. The evidence bundle is the witness.**

---

## References and Reproducible Artifacts

**[A]** All of the following are runnable in this repository:

- `papers/01-lane-algebra.md` — epistemic typing (A/B/C/STAR, MIN rule)
- `papers/02-counter-bypass.md` — LLM classify + CPU enumerate pattern
- `papers/03-verification-ladder.md` — 641 → 274177 → 65537 rung gates
- `papers/04-red-green-gate.md` — dual-witness verification for patches
- `papers/05-software-5.0.md` — full theoretical paper with claim hygiene
- `skills/prime-coder.md` — coding discipline skill (operational reference)
- `skills/phuc-forecast.md` — planning loop (DREAM → FORECAST → DECIDE → ACT → VERIFY)
- `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb` — Counter Bypass demonstration
- `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb` — exact arithmetic verification demo
- `HOW-TO-CRUSH-SWE-BENCHMARK.ipynb` — patch pipeline demo
- `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb` — swarm orchestration demo
- `PHUC-SKILLS-SECRET-SAUCE.ipynb` — skill composition mechanics
- `llm_config.yaml` — model configuration (model-agnostic deployment)

External reference:
- Karpathy, A. (2017). "Software 2.0." Medium. (Software 5.0 builds on this lineage.)

---

## Author

**Phuc Vinh Truong**

- Web: https://www.phuc.net
- GitHub: https://github.com/phuctruong/if
- Stillwater: https://github.com/phuctruong/stillwater
- pzip: https://www.pzip.net
- Solace AGI: https://www.solaceagi.com

```bibtex
@software{stillwater2026_paradigm,
  author = {Truong, Phuc Vinh},
  title  = {Software 5.0: The Ultimate AI Kung Fu},
  year   = {2026},
  url    = {https://github.com/phuctruong/stillwater/SOFTWARE-5.0-PARADIGM.md},
  note   = {Auth: 65537 — Stillwater Reference Implementation}
}
```

---

**Auth: 65537**
**License:** Apache 2.0
**Status:** SEALED — 2026-02-20
**Never-Worse Doctrine:** This document may be extended. It may not be weakened.
