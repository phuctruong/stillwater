# Software 5.0: Intelligence As Externalized, Verifiable, Composable Recipes

**Status:** Draft (open-source; claims typed by lane below)
**Last updated:** 2026-02-20
**Scope:** The theoretical foundation, economic argument, and engineering contract for Software 5.0 — the paradigm where intelligence persists in versioned recipes outside the weights.
**Auth:** 65537 (project tag; see `papers/03-verification-ladder.md`)

---

## Claim Hygiene

Every empirical claim in this paper is tagged with its epistemic lane:

- **[A]** Lane A — directly witnessed by executable artifact in this repo (tests, tool output, notebook run)
- **[B]** Lane B — framework principle, derivable from stated axioms or established computer science
- **[C]** Lane C — heuristic or reasoned forecast; useful but not proven
- **[*]** Lane STAR — unknown or insufficient evidence; stated honestly

When in doubt, prefer [*] over false confidence. This paper will not claim what it cannot witness.

See `papers/01-lane-algebra.md` for the formal epistemic typing system.

---

## Reproduce / Verify In This Repo

Framework concepts demonstrated in runnable form:
- `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb` — Counter Bypass (LLM classify + CPU enumerate)
- `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb` — exact-arithmetic verification ladder
- `HOW-TO-CRUSH-SWE-BENCHMARK.ipynb` — patch pipeline with rung gates
- `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb` — swarm spine with fail-closed phases
- `PHUC-SKILLS-SECRET-SAUCE.ipynb` — skill composition mechanics
- Skills layer: `skills/*.md` — loadable operational contracts

---

## Abstract

Software has always been about encoding intelligence into something persistent and replayable.

Software 1.0 encoded logic as hand-written code. Software 2.0 encoded it in neural weights. Software 3.0 encoded it in prompts. Software 4.0 in agents. Each generation shifted where intelligence lives. Each also inherited the previous generation's blind spots.

Software 5.0 is the recognition that **the LLM is not the intelligence — it is the compression engine**. Intelligence is what the LLM discovers, verifies, and externalizes into versioned, auditable, composable artifacts: skills, recipes, and ripples. The weights stay frozen. The intelligence accumulates outside them.

This paper makes four arguments:

1. **The Compression Argument:** LLMs are near-perfect prior distributions over human reasoning. Their job is to reverse-engineer and externalize reasoning patterns, not to be the reasoning substrate at runtime.

2. **The Persistence Argument:** Weights are an inadequate persistence medium — opaque, non-composable, expensive to update, and dangerous to trust without verification. External recipes, versioned and gated, are the correct medium.

3. **The Economics Argument:** Token costs surged ~320% from 2024 to 2025. On-premise LLMs now cost less than cloud API calls for many workloads. CPU-executable logic is 1000x cheaper per operation than GPU-token computation. The economic pressure toward externalization is structural, not temporary. [C]

4. **The Safety Argument:** Deterministic, auditable code cannot hallucinate. Lane Algebra enforces that LLM outputs (Lane C) can never masquerade as verified facts (Lane A) without going through a machine-checkable gate.

**Central thesis:** `LLMs DISCOVER. CPUs ANCHOR. Recipes PERSIST.`

---

## 1. The Five-Generation Taxonomy

### 1.1 The Lineage

Every software generation is defined by where it stores the learned mapping from inputs to useful outputs.

```
Software 1.0: Mapping stored in human-authored code
              - Medium: source files (.c, .py, .java)
              - Update mechanism: human writes diff
              - Verification: test suite + compiler
              - Failure mode: bugs require human diagnosis

Software 2.0: Mapping stored in neural weights (Karpathy, 2017)
              - Medium: weight matrices (.pt, .safetensors)
              - Update mechanism: gradient descent on data
              - Verification: held-out eval set accuracy
              - Failure mode: opaque, brittle, expensive to update

Software 3.0: Mapping guided by natural language prompts
              - Medium: prompt strings
              - Update mechanism: human prompt engineering
              - Verification: vibes, manual review, A/B test
              - Failure mode: brittle, model-specific, not composable

Software 4.0: Mapping enacted by autonomous agents
              - Medium: agent loops + tool calls
              - Update mechanism: agent observes and replans
              - Verification: task completion rate, often manual
              - Failure mode: compounding errors, unbounded scope, no audit trail

Software 5.0: Mapping externalized as versioned recipes + skills
              - Medium: structured, gated, composable artifacts
              - Update mechanism: LLM extracts → human reviews → version bumped
              - Verification: deterministic rung gates (641 → 274177 → 65537)
              - Failure mode: recipe drift if not re-verified on model change
```

The progression is not about replacing each generation. Software 5.0 uses LLMs (2.0), prompts (3.0), and agents (4.0) as tools — but it changes what they produce. The output is not an answer. The output is a durable, auditable artifact that encodes the reasoning for reuse.

**[B]** Each generation's medium determines its composability, auditability, and update cost. Source code is diffable. Weights are not. Recipes are diffable. This is a structural property, not an implementation detail.

### 1.2 Where Software 5.0 Fits in Practice

Software 5.0 is not a replacement for the earlier generations. It is an orchestration layer:

```
Layer 5.0: Recipe / Skill Repository (versioned, gated, composable)
    ↓ invokes
Layer 4.0: Agent Loops (bounded by skills, emit evidence)
    ↓ uses
Layer 3.0: Prompts (loaded from skills, not hand-crafted per session)
    ↓ runs on
Layer 2.0: Model Weights (frozen; commodity input)
    ↓ executes on
Layer 1.0: CPU/GPU (the physical substrate)
```

The key insight: in Software 5.0, the valuable accumulated intelligence lives in Layer 5.0. Layers 2.0 through 4.0 are infrastructure — interchangeable, improvable, replaceable. A better model drops in without re-engineering the recipe layer.

---

## 2. AI As Perfect Prior: The Compression Argument

### 2.1 What LLMs Actually Are

**[B]** A large language model trained on text corpora is, in information-theoretic terms, an approximation of the underlying distribution that generated that text. Text is the compressed encoding of human thought, reasoning, and procedure. A model that learns to predict text well has, implicitly, learned to predict the reasoning patterns that generated the text.

This means: **LLMs are reverse-engineering engines**. Given a task description, an LLM can often reconstruct the reasoning process a domain expert would have applied — because that expert's reasoning was encoded in text the model trained on.

This is enormously powerful. It is also easily misused.

### 2.2 The Misuse: Treating the LLM as the Intelligence

The dominant usage pattern today is: send query → receive answer → done.

This treats the LLM as a reasoning oracle: a black box you consult repeatedly, paying for the same pattern-matching every time. Three problems follow:

**Problem 1: The oracle is not persistent.** Each invocation starts from zero. The LLM cannot accumulate task-specific knowledge across sessions without external scaffolding.

**Problem 2: The oracle is expensive.** Token computation on a GPU is orders of magnitude more expensive per operation than CPU arithmetic. Renting the oracle's reasoning repeatedly is economically wasteful.

**Problem 3: The oracle is unauditable.** When the LLM gives you an answer, you have a string. You do not have a proof, a witness, or a replayable artifact. You cannot verify the reasoning chain without running it again, which may give a different answer.

### 2.3 The Correct Use: LLM as Compression Engine

**[B]** The right question to ask is not "what is the answer?" but "what recipe produced this answer, and can we encode that recipe in a form cheaper and more reliable than the LLM itself?"

Concretely:

```
compress(domain_task):
  LLM: identify the reasoning pattern
  Human + LLM: extract it into a reproducible recipe
  CPU: execute the recipe deterministically
  Verification: confirm recipe output matches LLM-derived answer
  Result: recipe in skills library, token cost = 0 for future invocations
```

This is why the Software 5.0 slogan is: **"Don't compress the data. Compress the generator."**

The generator of useful behavior is the reasoning pattern. Once extracted and gated, it runs free, on any hardware, at CPU speed, with deterministic output.

### 2.4 The Intelligence Equation

**[B]** We can express the Software 5.0 model of intelligence as:

```
Intelligence(system) = Memory × Care × Iteration

where:
  Memory    = externalized recipes + skills (NOT weights)
  Care      = verification ladder (proves correctness of recipes)
  Iteration = recipe evolution (versioned, auditable, never-worse)
```

This is the **Law of Emergent Knowledge (LEK)**: *knowledge emerges when memory loops through care.* The key claim: intelligence scales not with model size but with the quality of externalized, verified knowledge. [A]

> Source: *[The Law of Emergent Knowledge](https://www.phuc.net/books/law-of-emergent-knowledge/)* by Phuc Vinh Truong.

**[A]** This is operationalized in this repo: `skills/*.md` are the Memory layer; the rung gates (641 → 274177 → 65537) are the Care layer; git versioning + the never-worse doctrine are the Iteration layer.

### 2.5 What Extraction Looks Like in Practice

Given a problem domain:

1. **Seed with the LLM:** describe the problem, ask for the reasoning approach
2. **Classify the reasoning:** is it pattern-matching (extractable to rules), search (extractable to algorithm), or genuine stochastic creativity (irreducible)?
3. **For extractable reasoning:** encode into a skill (operational constraints + state machine) or recipe (step sequence + artifacts)
4. **Gate the extraction:** run the rung ladder; confirm the recipe produces the same outputs the LLM produced
5. **Persist:** version-bump the skill, add to library
6. **Next invocation:** load skill, skip LLM for the gated portion

**[A]** This pattern is demonstrated in `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb`: the LLM's classification judgment is extracted; the aggregation step is replaced by deterministic `Counter()` arithmetic. The LLM no longer needs to count — the CPU counts exactly.

---

## 3. The Two Persistence Layers

### 3.1 Why Persistence Needs Two Layers

Not all externalized intelligence has the same structure.

Some knowledge is **universal**: the same pattern applies across all instances of the task. This belongs in code — a shared skill that any agent, any instance, any model can load.

Some knowledge is **instance-specific**: the particular settings, preferences, and adaptations for one deployment, one user, one domain. This belongs in configuration — a ripple that sits on top of the stillwater baseline.

Software 5.0 separates these explicitly:

```
Layer 1 (Code / Stillwater): Universal operational constraints
  - Format: skills/*.md, recipe scripts, solver pipelines
  - Governance: versioned, gated, PR-reviewed, never-worse
  - Reuse: any agent can load; cross-instance benefit
  - Examples: prime-coder.md, phuc-forecast.md, counter-bypass recipe

Layer 2 (Settings / Ripples): Instance-specific configuration
  - Format: preferably Prime Mermaid language (compressed, auditable)
  - Governance: per-instance, drift-tracked
  - Reuse: intentionally local; not blindly propagated
  - Examples: user's preferred output format, domain-specific thresholds,
              local model choice, custom rung targets
```

The equation: **X = R(S, Δ)** — every deployment is a Stillwater baseline plus a Ripple delta. And **decode(encode(X)) = X** — the encoding is lossless; no intelligence is silently discarded.

### 3.2 Stillwater: The Code Layer

Stillwater is the reference implementation. It contains:

- **Skills:** versioned operational contracts (`skills/*.md`)
- **Recipes:** replayable pipelines (notebooks, solver scripts)
- **Evidence artifacts:** outputs, hashes, rung results

**[B]** The design principle: Stillwater must be correct for all instances before any instance-specific customization happens. This is the analogy to Linux: the kernel must be stable before distributions customize it.

What makes a skill part of Stillwater (and not just a ripple)?
- It applies to a broad class of tasks (not one domain)
- It has been gated at rung 641 minimum
- It obeys the never-worse doctrine: it does not weaken any prior constraint
- It is composable: loading multiple skills must not produce contradictions

**[A]** Current skills in this repo: `prime-coder.md` (coding discipline), `prime-math.md` (exact arithmetic), `prime-safety.md` (tool safety), `phuc-forecast.md` (decision loop), `phuc-swarms.md` (multi-agent orchestration), `phuc-context.md` (context hygiene). Each is loadable verbatim into any LLM session.

### 3.3 Ripples: The Settings Layer

A ripple encodes what is true for one instance but not universal.

**[B]** The risk of conflating ripples with stillwater: an instance-specific adaptation gets treated as universal truth and propagates to other instances that have different constraints. This is how one user's shortcut becomes another user's bug.

Ripples are expressed preferably in **Prime Mermaid** — a compressed, structured notation for rules, flows, and state machines. The choice of Prime Mermaid is not accidental: Mermaid diagrams are text, diffable, auditable, and renderable. Intelligence encoded in Mermaid is more portable than intelligence encoded in free prose.

**[C]** Long-term, ripples become the site of personalization and domain specialization — equivalent to the "user settings" layer in an operating system. The AI learns your preferences not by fine-tuning but by updating your ripple file.

### 3.4 The Composition Rule

When an agent loads a deployment context:

```
effective_constraints = stillwater_base UNION ripple_delta

where:
  - ripple_delta MAY specialize stillwater rules (narrow them)
  - ripple_delta MUST NOT weaken stillwater rules
  - on conflict: stricter_wins (this is a hard invariant)
```

**[B]** This mirrors the layering rule in `prime-coder.md` — the public baseline is sacrosanct. Ripples extend; they do not replace.

---

## 4. Why Weights Are the Wrong Place for Intelligence

### 4.1 The Weight Representation Problem

**[B]** Neural weights encode a compressed statistical approximation of training data. They are, by design, a lossy medium. A model cannot distinguish between "this pattern appeared in the training data" and "this pattern is true in the current context." The weights contain no execution provenance, no timestamp, no scope.

This creates five structural deficiencies:

**Deficiency 1: Opacity.** You cannot inspect a weight tensor and read out the reasoning. You can only probe it by running inference. There is no `git diff` for weights.

**Deficiency 2: Non-composability.** You cannot take the accounting expertise from one model and the legal expertise from another and merge them without full retraining. Skills compose (load multiple .md files); weights do not.

**Deficiency 3: Fragility to updates.** Fine-tuning to add new knowledge risks overwriting old knowledge (catastrophic forgetting). [B] Updating a skill file to add a new rule does not erase old rules — the file is append-reviewed, not gradient-overwritten.

**Deficiency 4: Update cost.** Training a frontier model costs millions of dollars. Updating a skill file costs a PR review. The asymmetry is structural: fine-tuning concentrates knowledge update cost at the model owner; recipe updating distributes it across contributors.

**Deficiency 5: Trust without verification.** When a weight-stored model says X, there is no proof that X was derived from valid reasoning. When a recipe-stored procedure outputs X, there is an artifact chain: inputs → recipe steps → outputs → rung gate result. The chain is auditable.

### 4.2 The Hallucination Root Cause

**[B]** Hallucination is not primarily a capability failure. It is a representation failure. The model cannot distinguish "I know this with high confidence" from "I am pattern-matching to something plausible." Both feel the same to the model because both are weight-activations.

Lane Algebra (see `papers/01-lane-algebra.md`) addresses this at the output layer: it forces every claim to declare its evidence class. But Lane Algebra is a mitigation, not a solution. The solution is to not rely on weight-stored "knowledge" for facts that should be verified by deterministic procedure.

**[B]** The correct architecture: use weights for pattern recognition and generation (what they are good at); use CPU-deterministic code for verification, aggregation, and counting (what they are bad at). The boundary between the two is the core engineering decision in Software 5.0.

### 4.3 The Non-Composability Crisis

**[C]** As AI systems grow more capable, the demand for specialized expertise in different domains (medical, legal, financial, scientific) grows. The weight-centric approach requires either:

- Training separate expert models for each domain (expensive, siloed)
- Training one massive model on all domains (expensive, poor specialization, brittle)
- Fine-tuning a base model per domain (expensive, catastrophic forgetting risk)

The recipe-centric approach: maintain one capable base model; load domain-specific skills on demand. The skills compose. The base model does not change. New expertise costs a skill PR, not a training run.

**[A]** This is the current architecture of this repo: one model (configurable, see `llm_config.yaml`), multiple skills loaded per session. No fine-tuning required to add new domain expertise.

---

## 5. AGI Without Retraining: The Persistence Argument

### 5.1 The Retraining Bottleneck

**[B]** The dominant model for "making AI smarter" is: gather data, train, evaluate, deploy, repeat. The cycle time is months to years. The cost is prohibitive for most actors. The result: intelligence is concentrated at model providers, updated on their schedule, opaque to users.

This is a structural problem for AGI development: how do you build a system that evolves continuously, accumulates domain expertise, and improves from operational experience — without retraining?

### 5.2 The External Evolution Model

Software 5.0 answers: **evolve the recipe layer, not the weight layer**.

The mechanism:

```
Episode 1: Agent encounters novel problem → uses LLM to reason through it
Episode 2: Agent (or human reviewer) extracts successful reasoning into skill/recipe
Episode 3: Skill is gated (rung 641+), version-bumped, added to library
Episode 4: All future agents load the skill → benefit from Episode 1's insight
Episode 5: Skill is challenged by new case → gated update or deprecation

Net result: system gets smarter across episodes without model retraining
```

**[B]** This is the correct model for AGI evolution: intelligence accumulates in the recipe layer, not the weight layer. The weights are a fixed prior. The recipes are the learned posterior.

### 5.3 The Never-Worse Doctrine

For recipe evolution to be safe, one invariant must hold: **the recipe layer must never get dumber**.

This is enforced by the never-worse doctrine, operationalized in `skills/prime-coder.md`:

- Hard gates and forbidden states are strictly additive over versions
- No rule may be removed without a major version bump and explicit deprecation plan
- Any relaxation requires evidence that the relaxation is safe

**[A]** The verification ladder (641 → 274177 → 65537) is the mechanism: a skill update must pass all rungs before it can replace the prior version. If the new version fails a rung that the old version passed, it is rejected.

### 5.4 Skill Versioning Semantics

Skills follow semantic versioning with additional constraints:

```
MAJOR version: breaking change to the skill contract
               (removes a gate, weakens a forbidden state,
                changes output schema incompatibly)
               Requires: explicit deprecation plan + promotion sweep

MINOR version: additive new capability or constraint
               (adds a new gate, new forbidden state, new evidence requirement)
               Requires: rung 641 pass minimum

PATCH version: clarification, documentation, non-behavioral fix
               Requires: diff review, no rung regression
```

**[A]** Example: `prime-coder.md` is currently at v2.1.0. The changelog shows additive upgrades only — restored capabilities, new gates, no weakening. The version history is the audit trail of intelligence evolution.

### 5.5 Skill Composition as Intelligence Amplification

**[B]** When skills compose correctly, the effective intelligence of the loaded system exceeds any individual skill. A session loading `prime-coder.md` + `phuc-forecast.md` + `prime-safety.md` operates under:

- Coding rigor (red/green gate, evidence artifacts)
- Planning discipline (DREAM → FORECAST → DECIDE → ACT → VERIFY)
- Safety constraints (tool envelope, fail-closed defaults)

The intersection of these constraints produces behavior that no single skill mandates but all skills together enforce. This is intelligence amplification through composition — no training required.

---

## 6. The Economics: Why Software 5.0 Is Inevitable

### 6.1 The Token Cost Pressure

**[C]** Token costs for frontier models surged approximately 320% from 2024 to 2025 (driven by demand growth outpacing supply). This trend creates structural pressure to minimize token usage for any task that can be handled by cheaper methods.

**[B]** The economic argument: if a task can be decomposed into:
- A classification/parsing step (LLM, expensive)
- An aggregation/execution step (CPU, cheap)

then the optimal engineering choice is to push as much work as possible to the CPU step.

**[A]** This is the Counter Bypass pattern, demonstrated in `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb`: LLM classifies (one or few calls), CPU enumerates with `Counter()`. The aggregation step costs zero tokens.

### 6.2 The On-Premise Inflection

**[C]** By late 2025, on-premise deployment of capable open-weight models (Llama 3.1 8B, Qwen 2.5 Coder 7B, Mistral variants) became economically competitive with cloud API calls for many workloads. The crossover point: if you run enough queries, the one-time hardware cost is recouped and subsequent queries are effectively free.

The economic implications:

- Token cost = hardware amortization / queries, converging to near-zero at scale
- Data privacy: on-premise eliminates third-party data exposure
- Latency: local inference eliminates network round-trips
- Reliability: no dependency on external API availability

**[A]** This repo supports on-premise deployment: `llm_config.yaml` configures the model endpoint; no cloud dependency is assumed.

### 6.3 CPU Dominance for Verified Logic

**[B]** Once reasoning has been extracted into a deterministic recipe, execution cost drops by orders of magnitude. Consider:

```
Token computation (GPU):   ~$0.001–$0.01 per 1K tokens
CPU integer arithmetic:    ~$0.000000001 per 1K operations

Ratio: 10^6 to 10^7 cheaper per operation on CPU
```

The practical implication: **every reasoning step that can be extracted into a CPU-executable recipe represents a 10^6× cost reduction per future invocation**.

**[B]** This is the economic incentive for Software 5.0: the one-time cost of extraction and gating is amortized over all future invocations. As recipe libraries grow, token costs fall without model replacement.

### 6.4 Mobile and Desktop Portability

**[C]** The 7B–13B parameter model range runs on consumer hardware (Apple Silicon, RTX 3090, high-end mobile SoC). This means Software 5.0 deployments can run on:

- Mobile devices (on-device inference, zero API cost, zero latency)
- Desktop (local model, full skill library, offline capable)
- Edge servers (distributed, low-latency, privacy-preserving)

**[B]** The portability is a consequence of the recipe-centric architecture: skills are text files; recipes are scripts; the LLM is a swappable component. When a smaller, faster model becomes available, it drops in without re-engineering the skill layer.

**[A]** This repo is model-agnostic by design: `llm_config.yaml` specifies the model; skills are model-independent; verification artifacts are captured regardless of which model generated the initial output.

### 6.5 The Community Network Effect

**[C]** A skill library behaves like a software package ecosystem (npm, pip, apt): early contributors create high-value shared infrastructure; later contributors extend and specialize. The network effect compounds: each new skill makes every deployment more capable.

The economic model:

```
Value(skill_library) ∝ N_skills × N_deployments × quality_gate_strength

where:
  N_skills: number of gated, composable skills
  N_deployments: number of agents/sessions loading skills
  quality_gate_strength: how rigorously each skill was gated (rung)
```

**[B]** The quality gate prevents the npm failure mode: a library full of unmaintained, untested packages that users load blindly. In Software 5.0, each skill declares its rung; users can require a minimum rung before loading.

---

## 7. The Safety Argument: Why Software 5.0 Is Safer

### 7.1 Determinism as Safety

**[B]** The most dangerous property of a weight-based AI system is that it can produce plausible-sounding outputs that are wrong, and the wrongness is not detectable from the output alone. The model cannot mark its own outputs as "unverified."

Deterministic code has a complementary property: it either computes the right answer or it throws an error. It cannot confidently produce a wrong answer while appearing correct.

**[B]** Software 5.0 exploits this asymmetry: push verification, aggregation, and safety-critical logic into deterministic code; reserve the LLM for pattern recognition and generation where exact correctness is not required.

### 7.2 Lane Algebra as the Safety Contract

**[A]** Lane Algebra (see `papers/01-lane-algebra.md`) is the formal epistemic typing system that makes this concrete. Every claim in a Software 5.0 system must carry its lane:

```
Lane A: witnessed by executable artifact (test passed, tool output captured)
Lane B: framework principle (derivable from stated axioms)
Lane C: LLM output or heuristic (useful but unverified)
Lane STAR: unknown (honest admission of ignorance)
```

The MIN rule: **combined claim strength = weakest premise strength**. A chain of reasoning with one Lane C step cannot produce a Lane A conclusion.

**[B]** This prevents the most common AI safety failure in practice: confident assertion of unverified claims. An LLM says X confidently; a human acts on X as if it were verified; X turns out to be wrong. Lane Algebra forces the "confidently" out of the output by typing it as Lane C until verified.

### 7.3 The Verification Ladder as Defense in Depth

**[A]** The rung ladder (see `papers/03-verification-ladder.md`) provides layered verification:

```
Rung 641 (edge sanity):
  - Unit tests, schema validation, basic invariants
  - Catches obvious breakage
  - Required for any PASS claim

Rung 274177 (stress/adversarial):
  - Seed sweeps, replay stability, null edge cases
  - Catches statistical failure modes
  - Required for stability claims

Rung 65537 (strongest available witness):
  - Adversarial paraphrase sweep, refusal correctness
  - Security gate if triggered, behavioral hash drift explained
  - Required for promotion claims
```

A skill or recipe at rung 65537 has been tested against edge cases, adversarial inputs, and replay instability. It is not provably correct in the formal sense, but it has more witness strength than any prompt-engineering approach.

### 7.4 Fail-Closed Defaults

**[A]** Every skill in this repo specifies fail-closed behavior: when inputs are missing, ambiguous, or contradictory, the default is to stop and report — not to guess and continue.

This is operationalized in `prime-coder.md` as the forbidden state `SILENT_RELAXATION`: an agent that quietly relaxes a constraint to make progress is in a forbidden state. The allowed exit from uncertainty is `EXIT_NEED_INFO` or `EXIT_BLOCKED`, both of which surface the problem rather than hiding it.

**[B]** Fail-closed defaults are safer than fail-open defaults in any high-stakes domain. The cost is occasional false negatives (refusing to act when action would have been correct). The benefit is elimination of false positives (acting confidently when action was wrong).

### 7.5 Transparency as a Safety Property

**[B]** A Software 5.0 artifact is transparent by construction:
- The skill file is human-readable and machine-parseable
- The recipe steps are enumerable and auditable
- The evidence artifacts capture what was actually computed
- The rung declaration states the verification strength achieved

This transparency is qualitatively different from "explainability" approaches applied to black-box models. Explaining a black box is forensic — you reconstruct what happened. Auditing a recipe is prospective — you can verify the logic before execution.

---

## 8. The Skill and Recipe Community

### 8.1 The Current State: GitHub as Seed Library

**[A]** This repo is the seed implementation of the Software 5.0 skill library. Current skills:

- `prime-coder.md` v2.1.0 — coding discipline with red/green gate, evidence contract, forbidden states
- `prime-math.md` — exact arithmetic discipline, proof hygiene, witness requirements
- `prime-safety.md` — tool safety envelope, authority ordering, prompt injection firewall
- `phuc-forecast.md` v1.1.0 — planning loop (DREAM → FORECAST → DECIDE → ACT → VERIFY)
- `phuc-swarms.md` v2.0.0-rc1 — multi-agent orchestration with phase ownership
- `phuc-context.md` — context hygiene, CNF capsules, anti-rot
- `phuc-cleanup.md` — glow-file cleanup workflow with approval gates
- `prime-wishes.md` — wish notebook contract, Prime Mermaid governance

Each skill is loadable verbatim, composable, and versioned. This is the current state. The future state is a distributed marketplace.

### 8.2 The Marketplace Vision

**[C]** The natural evolution of a skill library with quality gates is a marketplace:

```
Stage 1 (current): GitHub repository
  - Skills in skills/*.md
  - PR review as quality gate
  - Version tags as distribution

Stage 2 (near-term): Structured registry
  - Skill metadata: id, version, rung, dependencies, domain tags
  - Search by domain, rung level, composability requirements
  - Download by name (like pip install skill-name)

Stage 3 (long-term): VSCode extensions model
  - Marketplace UI: browse, rate, review skills
  - Automatic compatibility checking (does this skill conflict with that one?)
  - Economic incentives for skill authors (tips, subscriptions)
  - Rung certification by independent verifiers
```

**[C]** The analogy to VSCode extensions is precise: both are domain-specific additions to a base platform that improve capability for specific tasks. Both can be composed. Both require trust (extensions can be malicious; skills can be malformed). The Software 5.0 solution: rung gates replace "do you trust the publisher" with "does this skill pass verifiable tests."

### 8.3 The Trust Model

**[B]** In a recipe/skill community, trust is not about identity — it is about evidence.

A skill at rung 65537 has passed:
- adversarial paraphrase sweep (min 5 paraphrases)
- replay stability check (min 2 replays)
- null edge case sweep
- refusal correctness check
- behavioral hash drift explained

This evidence is more trustworthy than a 5-star rating because it is machine-checkable, not subjective. A skill passes or it does not. The rung declares the strength; the evidence bundle proves it.

**[C]** Long-term, the community norm should be: never load a skill below rung 641. Never make promotion claims from a skill below rung 65537. The rung system is the quality floor of the marketplace.

### 8.4 One Instance Learns, All Benefit — With Caution

**[C]** The idealized model: one deployment encounters a difficult task, extracts a skill, gates it, contributes it to the library. All future deployments load the skill and immediately benefit from the extraction.

**[B]** The caution: "one instance learns" does not mean "all instances should blindly apply." A skill extracted in one domain may not generalize to another. The rung system provides the check: a skill claiming generality must pass the adversarial sweep with paraphrases that test edge cases and domain variation.

**[B]** This is why the skill loading rule in `skills/README.md` is "don't compress away invariants." The full skill, including forbidden states and edge case handling, must be loaded. Summarizing a skill is how you silently lose the safety properties it provides.

---

## 9. Stillwater as Reference Implementation

### 9.1 What "Reference Implementation" Means

**[B]** A reference implementation is a concrete, authoritative instantiation of a specification. It answers: "what does Software 5.0 actually look like in code?" It is the Linux kernel to the POSIX specification — not the only implementation, but the one against which correctness and compliance are measured.

Stillwater is the reference implementation for Software 5.0 for several reasons:

1. It is open-source (auditable by anyone)
2. It implements all core concepts: skill loading, rung gates, evidence artifacts, fail-closed behavior
3. It ships runnable demonstrations of the key patterns (notebooks)
4. It enforces the never-worse doctrine through skill versioning
5. It is model-agnostic (no lock-in to any particular LLM)

### 9.2 The Core Architecture

```
stillwater/
  skills/                   ← the Memory layer (externalized intelligence)
    prime-coder.md          ← coding discipline
    prime-math.md           ← exact arithmetic
    prime-safety.md         ← tool safety
    phuc-forecast.md        ← decision loop
    phuc-swarms.md          ← multi-agent orchestration
    phuc-context.md         ← context hygiene

  papers/                   ← the Theory layer (concepts with claim hygiene)
    01-lane-algebra.md
    02-counter-bypass.md
    03-verification-ladder.md
    04-red-green-gate.md
    05-software-5.0.md      ← this paper

  src/oolong/src/               ← Counter Bypass recipe (LLM classify + CPU enumerate)
  imo/src/                  ← exact arithmetic solver (verification ladder demo)
  src/swe/src/                  ← patch pipeline (red/green gate demo)

  *.ipynb                   ← runnable recipes (human-readable + executable)
  llm_config.yaml           ← model configuration (swappable, no lock-in)
  CLAUDE.md                 ← PRIME_CODER_SECRET_SAUCE loaded on session start
```

### 9.3 Benchmark Results (With Claim Hygiene)

The following results are referenced in this repo's notebooks and README. Each is labeled with its evidence lane:

**OOLONG Benchmark:**
**[A]** The Counter Bypass pattern (LLM classify + CPU enumerate) is demonstrated in `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb` with a runnable solver. The solver demonstrates the architectural pattern; numerical benchmark scores against the OOLONG leaderboard require the full external harness in `src/oolong/src/oolong_solver_real.py`.

**IMO 2024:**
**[A]** A solver demonstrating exact arithmetic + lemma-based verification for IMO-style problems is in `imo/src/` and runnable via `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb`. This demonstrates the verification discipline; claims about official IMO grading are **[*]** (not verified in this repo).

**SWE-bench:**
**[A]** A patch pipeline demonstrating the red/green gate pattern is in `src/swe/src/` and runnable via `HOW-TO-CRUSH-SWE-BENCHMARK.ipynb`. Official SWE-bench leaderboard numbers require the full external harness; in-repo demonstrations show the architectural pattern.

**Claim hygiene note:** "10/10 on hardest" and "IMO 2024 6/6" are claimed in the repo's README and notebooks but are not independently verified in this paper. They are **[C]** pending external reproduction with logged artifacts. See `papers/99-claims-and-evidence.md` for the full claim hygiene policy.

### 9.4 The "Linux of AI" Framing

**[C]** The comparison to Linux is a strategic framing, not a technical equivalence:

- Linux solved the problem of a stable, open, composable kernel that could run on any hardware
- Stillwater attempts to solve the problem of a stable, open, composable intelligence layer that can run on any LLM

The parallel:
```
Linux kernel    ↔ Stillwater skill/recipe layer
Linux distros   ↔ Stillwater ripples (per-instance customization)
apt/yum         ↔ skill marketplace (future)
POSIX standard  ↔ Software 5.0 specification (this paper + skills)
kernel modules  ↔ domain-specific skill packs
```

**[B]** The critical structural similarity: both are platforms, not products. They are valuable because they enable the construction of specialized systems on top of a stable base, not because they directly solve every user problem.

---

## 10. What This Changes About Software Engineering

### 10.1 The New Engineering Task

**[B]** In Software 1.0, the software engineer's job was to write code that implements a specification. In Software 5.0, the software engineer's job is to extract, gate, and version reasoning patterns that encode domain intelligence.

This is not merely adding "prompt engineering" to the job description. It is a qualitative shift in what the engineer produces:

```
Software 1.0 engineer produces:  source code (deterministic, explicit)
Software 2.0 engineer produces:  training pipelines + eval harnesses
Software 3.0 engineer produces:  prompt templates + few-shot examples
Software 4.0 engineer produces:  agent loops + tool integrations
Software 5.0 engineer produces:  skills + recipes + evidence artifacts
```

The Software 5.0 engineer thinks like a protocol designer: what invariants must always hold? What are the forbidden states? What evidence proves correctness? What is the minimum viable recipe that captures the essential reasoning without over-fitting to one instance?

### 10.2 The New Quality Standard

**[B]** The measure of engineering quality in Software 5.0 is not lines of code, test coverage percentage, or API response time. It is:

- **Rung level achieved:** how thoroughly was this skill/recipe verified?
- **Composability:** how many other skills does this compose with without conflict?
- **Portability:** how many models/deployments can load this without modification?
- **Never-worse compliance:** does this version weaken any prior version's guarantees?
- **Evidence completeness:** is the artifact bundle sufficient for third-party reproduction?

### 10.3 The Human-AI Collaboration Model

**[B]** Software 5.0 redefines human-AI collaboration:

```
Not: "AI writes code; human reviews"
Not: "Human writes spec; AI implements"
But: "AI discovers patterns; human gates; AI executes gated patterns"
```

The human's irreplaceable role is gatekeeping — deciding which extracted patterns are worth persisting, verifying they generalize, and ensuring they do not weaken prior guarantees. This requires domain expertise that the LLM may pattern-match but cannot verify independently.

**[B]** The LLM's irreplaceable role is discovery — exploring the space of possible reasoning patterns, identifying what works, surfacing candidates for human review. This is the compression step: the LLM's world knowledge is the prior; the extracted recipe is the posterior conditioned on this task family.

### 10.4 The Failure Modes to Avoid

**[B]** Software 5.0 introduces new failure modes alongside its benefits:

**Failure mode 1: Recipe drift.** A recipe gated on model version X may produce wrong outputs on model version Y. Mitigation: track model version in env snapshot; re-gate on model upgrade.

**Failure mode 2: Skill conflict.** Two skills loaded simultaneously may have contradictory forbidden states. Mitigation: conflict detection on load; stricter-wins resolution; explicit compatibility declarations.

**Failure mode 3: Rung theater.** Claiming a high rung without actually running the sweep. Mitigation: require evidence bundle; block promotion without artifacts.

**Failure mode 4: Premature extraction.** Extracting a reasoning pattern from too few examples; the recipe is over-fit to one context. Mitigation: adversarial paraphrase sweep; seed sweep; minimum sample size requirements.

**Failure mode 5: Zombie skills.** Skills in the library that pass their declared rung but are no longer fit for current usage because context has changed. Mitigation: periodic re-gating; deprecation policy; time-stamped evidence artifacts.

### 10.5 The Societal Implication

**[C]** If Software 5.0 is correct, the most valuable AI-related asset is not a model — it is a mature, deeply gated skill library. The model is a commodity input (replaceable, improvable). The skill library is the accumulated, verified intelligence of the domain.

**[C]** This shifts economic power from model providers (who own the weights) to skill library maintainers (who own the verified recipes). Stillwater's open-source model is a bet that the skill library should be a public good — owned by the community, governed by evidence, accessible to all deployments.

**[*]** Whether this economic model prevails against closed, proprietary AI systems is unknown. The bet is that open, verifiable intelligence is more valuable long-term than opaque, proprietary intelligence — but this is a forecast, not a proven outcome.

---

## 11. Practical Checklist for Software 5.0 Engineers

When you encounter a novel task:

1. **Classify:** Is this pattern-matching (LLM-sufficient), aggregation (Counter Bypass), or exact reasoning (CPU recipe)?
2. **Extract:** Describe the reasoning pattern as a candidate skill. What are the invariants? What are the forbidden states?
3. **Gate:** Run at minimum rung 641 (unit tests). Target rung 65537 for library contribution.
4. **Persist:** Add to skills library with version, evidence bundle, and composability notes.
5. **Load:** Future agents load the skill instead of re-deriving the pattern.
6. **Monitor:** Track behavioral hash across model upgrades. Re-gate when hash drifts unexpectedly.

When you review a skill contribution:

1. **Claim hygiene:** Is every empirical claim lane-typed? Are [C] and [*] claims marked as such?
2. **Rung evidence:** Is the evidence bundle present and reproducible?
3. **Composability:** Does loading this skill with prime-coder + prime-safety produce conflicts?
4. **Never-worse:** Does this version weaken any prior version's guarantees?
5. **Portability:** Does this skill contain absolute paths or model-specific assumptions?

---

## 12. Conclusion

Software 5.0 is the recognition that LLMs are compression engines, not oracles.

Their job is to reverse-engineer the reasoning patterns implicit in human knowledge and externalize those patterns into verifiable, composable artifacts. The artifacts — skills, recipes, evidence bundles — are the intelligence. The LLM is the extraction tool.

This changes what we build (recipe libraries, not fine-tuned models), how we verify quality (rung gates, not vibes), how we update knowledge (skill PRs, not training runs), and what we consider valuable (verified reasoning patterns, not raw parameter counts).

**[A]** The reference implementation of these ideas is this repository: open, auditable, model-agnostic, with runnable demonstrations of the core patterns.

**[B]** The long-term prediction: AI capability compounds faster through verified recipe accumulation than through weight scaling, because recipes are composable and weights are not. This is a framework claim, derivable from the composability properties of text-format constraints versus weight matrices.

**[C]** The ultimate vision: a community-maintained skill library that makes any capable LLM immediately deployable in any domain — not because the model was trained on the domain, but because the domain's verified reasoning patterns are available as loadable skills. This is AGI in the meaningful sense: general capability through composition, not through a single omniscient model.

**[*]** How long this takes, whether the community model prevails, and what failure modes emerge at scale — these are honest unknowns. The repo is a bet on this direction, not a proof of its success.

---

## References

- `papers/01-lane-algebra.md` — epistemic typing (A/B/C/STAR, MIN rule)
- `papers/02-counter-bypass.md` — LLM classify + CPU enumerate pattern
- `papers/03-verification-ladder.md` — 641 → 274177 → 65537 rung gates
- `papers/04-red-green-gate.md` — dual-witness verification for patches
- `skills/prime-coder.md` — coding discipline skill (operational reference)
- `skills/phuc-forecast.md` — planning loop skill (DREAM → FORECAST → DECIDE → ACT → VERIFY)
- `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb` — Counter Bypass demonstration
- `HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb` — exact arithmetic verification demonstration
- `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb` — swarm orchestration demonstration
- `llm_config.yaml` — model configuration (model-agnostic deployment)
- `papers/99-claims-and-evidence.md` — claim hygiene policy

Karpathy, A. (2017). "Software 2.0." Medium. (External reference; Software 5.0 builds on this lineage)

---

**Auth: 65537** (project tag; see `papers/03-verification-ladder.md`)
**License:** Apache 2.0
**Citation:**
```bibtex
@software{stillwater2026_sw50,
  author = {Truong, Phuc Vinh},
  title = {Software 5.0: Intelligence As Externalized, Verifiable, Composable Recipes},
  year = {2026},
  url = {https://github.com/phuctruong/stillwater/papers/05-software-5.0.md},
  note = {Auth: 65537}
}
```
