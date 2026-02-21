# The Extension Economy: Skills, Recipes, and the Economics of Compressible Intelligence

**Status:** Draft (open-source; claims typed by lane below)
**Last updated:** 2026-02-20
**Scope:** The economic structure of Software 5.0 — why skill libraries produce increasing returns, how compression gain is measured, and why the extension economy is the next platform shift.
**Auth:** 65537 (project tag; see `papers/03-verification-ladder.md`)

---

## Claim Hygiene

Every empirical claim in this paper is tagged with its epistemic lane:

- **[A]** Lane A — directly witnessed by executable artifact in this repo
- **[B]** Lane B — framework principle, derivable from stated axioms or established computer science
- **[C]** Lane C — heuristic or reasoned forecast; useful but not proven
- **[*]** Lane STAR — unknown or insufficient evidence; stated honestly

See `papers/01-lane-algebra.md` for the formal epistemic typing system.

---

## Reproduce / Verify In This Repo

Core patterns referenced:
- `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb` — Counter Bypass (compression in action)
- `skills/*.md` — loadable operational contracts (the library layer)
- `PHUC-SKILLS-SECRET-SAUCE.ipynb` — skill composition mechanics
- `llm_config.yaml` — model-agnostic deployment (portability evidence)

---

## Abstract

**[C] Thesis:** In Software 5.0, the dominant competitive advantage shifts from model size to skill library depth — the ability to compress domain expertise into portable, composable, versioned skill files.

Software platforms succeed when they enable an extension economy: a community of contributors who build specialized capabilities on top of a stable base. UNIX had shell scripts. Emacs had packages. VSCode has extensions. npm has packages. Each platform's value is not the base system alone, but the community-created depth layered on top.

Software 5.0 creates the conditions for an analogous extension economy in AI behavior engineering. The base system is a capable LLM. The extensions are skills and recipes: versioned, gated, composable files that encode domain expertise in a form cheaper and more reliable than re-deriving it from the LLM at each invocation.

This paper argues that the skill library is a compression artifact, that compression gain is measurable, that skills exhibit increasing returns to adoption, and that this structure makes the extension economy the dominant competitive force in AI deployment over the next five years.

---

## 1. Introduction: The Three Layers

### 1.1 The Layer Architecture

Software 5.0 systems operate across three distinct layers, each with different economics:

```
Layer 1: Model Weights
  - What: the frozen statistical approximation of human knowledge
  - Economics: training cost ~$10M–$100M; inference cost ~$0.001/1K tokens
  - Update cycle: months to years
  - Composability: zero (weights from different models do not merge)
  - Portability: platform-specific (CUDA, ROCm, Metal)

Layer 2: Prompts
  - What: natural language instructions that steer the model at runtime
  - Economics: low creation cost; paid per invocation (tokens)
  - Update cycle: minutes to hours
  - Composability: weak (concatenation, not structured composition)
  - Portability: model-sensitive (tuned prompts may not transfer)

Layer 3: Skills (Software 5.0)
  - What: versioned, structured operational contracts with FSMs, gates, evidence
  - Economics: creation cost ~hours; subsequent invocations pay loading cost only
  - Update cycle: PR-review cycle (days)
  - Composability: strong (structured composition with conflict detection)
  - Portability: model-agnostic (load into any capable LLM session)
```

**[B]** The key economic asymmetry: weights and prompts pay their cost at every invocation. Skills pay their creation cost once and amortize it across all future invocations. This is the fundamental reason why the extension economy converges on skills as the dominant form of value storage.

### 1.2 Why This Paper Now

**[C]** The extension economy is not yet the dominant mode of AI deployment (as of 2026). The current mode is prompt engineering and fine-tuning. But the conditions for a platform shift are present: capable base models exist, skill composition is demonstrably possible, and the economic pressure toward externalization is structural.

**[A]** This repo demonstrates the extension economy in miniature: `skills/*.md` files loaded into LLM sessions replace ad-hoc prompt engineering with structured, gated, composable operational contracts. The model does not change. The behavior changes because the skill changes.

---

## 2. The Compression Gain Metric

### 2.1 Why Compression Is the Right Frame

A skill is a compression artifact. It takes domain expertise — reasoning patterns that an LLM would reconstruct from scratch each invocation, costing tokens — and encodes that expertise in a form that can be loaded at near-zero marginal cost.

**[B]** The compression gain of a skill is the ratio of what it would cost to re-derive the knowledge via LLM tokens versus what it costs to load the skill and execute the gated procedure.

### 2.2 The Compression Gain Formula

Define compression gain G for a skill S applied to N invocations:

```
G(S, N) = (N × C_derive - C_create - N × C_load) / (N × C_derive)

where:
  C_derive = token cost to derive the skill's behavior from scratch per invocation
  C_create = one-time cost to extract, gate, and version the skill
  C_load   = marginal cost to load the skill text into context per invocation
  N        = number of invocations over the skill's lifetime
```

**[B]** As N grows, C_create amortizes toward zero and C_load (context tokens for the skill text) is typically small relative to C_derive (tokens spent re-deriving complex behavior). For large N, G(S, N) converges toward 1 minus the load fraction.

**[C]** For a skill like `prime-coder.md` (encoding a complex multi-phase state machine with 20+ forbidden states), C_derive from scratch might be 10,000 tokens of reasoning, while C_load is the token count of the skill file (approximately 6,000 tokens). After roughly 6 invocations, the skill becomes net-positive on compression gain.

### 2.3 Measuring Quality-Adjusted Compression Gain

Raw token savings overstate gain if the derived-from-scratch behavior is worse in quality. The quality-adjusted metric:

```
G_quality(S, N, Q) = G(S, N) × (Q_skill / Q_derived)

where:
  Q_skill   = quality of skill-loaded behavior (e.g., fraction of tasks passing rung 641)
  Q_derived = quality of ad-hoc-derived behavior (typically lower; no gates, no FSM)
```

**[B]** Skills with hard gates and forbidden states systematically produce higher Q_skill than ad-hoc prompting, because the skill enforces behavior that the LLM would not consistently produce without constraints. The quality multiplier amplifies compression gain beyond the raw token calculation.

**[A]** Evidence for this in-repo: the `prime-coder.md` skill produces consistent red/green gate enforcement and evidence artifact generation across sessions. Without the skill loaded, sessions routinely skip evidence steps (this is observable by comparing session transcripts with and without skill loading).

---

## 3. Extension Economics: Increasing Returns

### 3.1 Why Skills Have Increasing Returns

Standard goods exhibit diminishing returns: producing more units eventually becomes more expensive. Skills exhibit the opposite: increasing returns to adoption.

**[B]** The mechanism is straightforward: a skill's creation cost C_create is fixed. Every new user, task, or deployment that loads the skill adds to N without adding to C_create. The per-invocation cost approaches C_load (a near-constant), meaning average cost falls monotonically as adoption grows.

This is the same increasing-returns dynamic that software itself exhibits: writing a program costs fixed effort; distributing it to millions costs near zero. Skills are software for AI behavior.

### 3.2 The Composability Multiplier

Skills exhibit a second source of increasing returns: composability.

**[B]** When two skills compose correctly, the combined system enforces the union of their constraints, producing behavior that neither skill alone mandates. This means the effective capability of the library grows faster than the linear sum of individual skills.

```
effective_capability(library) ≥ Σ capability(skill_i)
```

The inequality is strict because composed skills enforce mutually reinforcing constraints. `prime-coder.md` + `phuc-forecast.md` + `prime-safety.md` produces coding behavior with planning discipline and safety constraints — a combination that no single skill achieves and that would require extensive ad-hoc prompting to approximate.

**[A]** This is demonstrated in `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`: swarm agents load multiple skills simultaneously; their behavior exhibits properties of all loaded skills without explicit per-session instruction.

### 3.3 The Network Effect in Skill Libraries

**[C]** A skill library exhibits network effects: each new high-quality skill makes all other skills more valuable by expanding what compositions are possible.

The analogy is programming languages and their standard libraries. Python's `requests` library is valuable because it composes with every other Python library that needs HTTP. A skill that handles context hygiene (`phuc-context.md`) is valuable because it composes with every skill that requires coherent context across iterations.

**[C]** As the skill library grows past a critical threshold, the cost of building new AI-powered workflows falls sharply: instead of engineering behavior from scratch, developers load the relevant skills and write only the task-specific logic. This is the same inflection point that happened with pip/npm — once the ecosystem was rich enough, building from scratch became the wrong default.

---

## 4. The Recipe as a Unit of Compressible Workflow

### 4.1 Skills vs. Recipes

**[B]** Skills and recipes are distinct but complementary compression artifacts:

```
Skills:
  - What: operational constraints (FSM, forbidden states, output contracts)
  - Scope: behavioral — what the agent must/must not do
  - Format: structured markdown (machine-parseable, human-readable)
  - Lifetime: long (versioned, never-worse doctrine)
  - Example: prime-coder.md, phuc-forecast.md

Recipes:
  - What: step sequences (inputs → steps → artifacts → outputs)
  - Scope: procedural — how to accomplish a specific task family
  - Format: notebook, script, or structured template
  - Lifetime: medium (re-gated on environment change)
  - Example: Counter Bypass pipeline, red/green gate repro script
```

Skills govern behavior; recipes encode procedure. A complete Software 5.0 artifact typically combines both: a recipe loads skills to govern each step, and the skill specifies what artifacts the recipe step must produce.

### 4.2 Recipes and Reproducibility

**[A]** The key reproducibility property of recipes: they are replayable. A recipe specifies inputs, steps, expected artifacts, and verification checks. Running the recipe again on the same inputs produces the same artifacts (modulo environmental variation, which is tracked in env_snapshot.json).

This is in contrast to ad-hoc LLM sessions: two sessions given the same prompt may produce different sequences of actions, different artifacts, and different outcomes. A recipe eliminates this variance for the workflow structure; the LLM variance is confined to the steps where LLM judgment is genuinely needed.

### 4.3 Recipe Compression Gain

The compression gain formula from section 2 applies equally to recipes:

**[C]** A recipe encoding the Counter Bypass pattern (parse → LLM classify → Counter() aggregate → normalize) compresses roughly 2,000 tokens of reasoning (what an LLM would spend working through the algorithm) into a reusable script of ~200 lines of Python. Across 100 invocations, the token savings are approximately 200,000 tokens — a compression gain of roughly 99% for the aggregation reasoning.

**[B]** The exact savings depend on context and task; the structural argument holds regardless of specific numbers: once the procedure is encoded in executable form, future invocations pay execution cost, not derivation cost.

---

## 5. Community Dynamics: How Skill Libraries Grow

### 5.1 The Bootstrap Problem

Every community platform faces a bootstrap problem: the platform is only valuable when there are many contributors, but contributors only appear when the platform is already valuable.

**[B]** Skill libraries face the same bootstrap problem. The solution is the same as it was for open-source libraries: start with high-value foundational skills that cover universal needs (context hygiene, coding discipline, planning loops), demonstrate value early, then expand the long tail of specialized skills as the community grows.

**[A]** This repo's skill library bootstrapped with exactly this pattern: `prime-coder.md`, `phuc-forecast.md`, and `prime-safety.md` cover fundamental needs for any AI-powered engineering session. They are high-value from day one, before the library reaches critical mass.

### 5.2 The Contribution Flywheel

**[C]** The healthy contribution flywheel for a skill library:

```
1. User encounters task X requiring repeated pattern P
2. User extracts P into candidate skill
3. Community gates the skill (rung 641 minimum)
4. Gated skill enters library
5. All future users of task X family load the skill
6. More users → more feedback → better skill quality
7. Better quality → more trust → more loading → more contributions
```

Each loop strengthens the library and lowers the marginal cost of the next contribution, because contributors can build on existing skills rather than starting from zero.

### 5.3 The Specialization Long Tail

**[C]** Platform ecosystems consistently develop a specialization long tail: a small number of universally-used skills (standard library) and a large number of narrowly-specialized skills (domain expertise).

For AI skill libraries, the long tail might include: skills for SQL query optimization, regulatory compliance checking, academic paper review, code security auditing, and thousands of other specialized domains. Each domain expert contributes their patterns; every deployment benefits without the domain expertise being re-derived from scratch.

**[B]** The quality gate is what prevents the long tail from becoming noise: a skill at rung 641 minimum has been verified to produce consistent, auditable behavior. The rung declaration is the quality signal that lets users navigate a large library without manually reviewing every skill.

---

## 6. Failure Modes: Skill Rot, Recipe Staleness, Compatibility Drift

### 6.1 Skill Rot

**[B]** Skill rot occurs when a skill's behavior diverges from its declared guarantees over time, typically because:

1. The base model changes and the skill's assumptions no longer hold
2. The task domain evolves and the skill's patterns are no longer correct
3. Composability breaks as other skills add constraints that conflict with the rotting skill

**[B]** Detection mechanism: behavioral hash tracking. Each skill maintains a behavioral hash — a normalized fingerprint of the behavior it produces on canonical test inputs. When the hash drifts unexpectedly after a model upgrade or skill update, the skill requires re-gating before it can be used for promotion claims.

**[A]** This is operationalized in `prime-coder.md`: `behavior_hash.txt` and `behavior_hash_verify.txt` are required evidence artifacts. Unexplained drift blocks promotion.

### 6.2 Recipe Staleness

**[C]** Recipes are more vulnerable to staleness than skills because they encode specific environmental assumptions (model version, API endpoints, data formats). A recipe that worked with model version X may produce wrong artifacts with model version Y, even if the skill it loads is unchanged.

**[B]** The mitigation: env_snapshot.json records the environment at time of gating. Re-gating is required when the snapshot's key fields change (git_commit, model version, OS/arch). This is a hard evidence requirement, not a recommendation.

### 6.3 Compatibility Drift

**[B]** As a skill library grows, compatibility drift becomes a real risk: two skills that were independently correct may interact in unexpected ways when composed. Skill A's forbidden states may conflict with skill B's required behaviors.

**[B]** The mitigation is compositional testing: when adding a new skill to the library, run a compatibility sweep against the existing high-priority skills (standard library). Any conflict is logged; the stricter-wins rule resolves most conflicts deterministically.

**[C]** Long-term, a skill compatibility matrix — listing which pairs of skills have been tested for compositional conflicts — becomes a necessary part of the library's metadata. Without it, users cannot confidently compose skills without manual review.

---

## 7. Conclusion: The Extension Economy as the Next Platform Shift

### 7.1 Summary of Arguments

This paper has argued:

1. **[B]** Skills and recipes are compression artifacts that amortize derivation cost across invocations, producing increasing returns as adoption grows.

2. **[B]** The compression gain is measurable and converges to a high value for skills that encode complex, repeatedly-needed reasoning patterns.

3. **[B]** Skills exhibit network effects through composability: the effective capability of the library grows faster than the linear sum of individual skills.

4. **[A]** This repo demonstrates the extension economy in miniature: a small library of high-quality skills produces behavior that would require extensive ad-hoc prompting to approximate.

5. **[C]** The natural evolution of a well-governed skill library is a community marketplace with quality gates, version control, and economic incentives for contributors.

### 7.2 The Platform Shift Claim

**[C]** Platform shifts in software history follow a consistent pattern: a new abstraction layer becomes the dominant site of value creation, displacing the previous layer.

UNIX displaced hardware-specific programming. C displaced assembly. Python displaced C for scripting. npm displaced local scripting for web development. Each shift was enabled by a combination of: a stable base platform, a contribution mechanism (packages/extensions), a quality signal (stars/downloads/tests), and network effects (composability).

Software 5.0 skill libraries have all four elements. The base platform exists (capable LLMs). The contribution mechanism exists (git PRs with rung gates). The quality signal exists (verification rung). Composability exists (structured skill loading with conflict resolution).

**[*]** Whether this shift happens in two years or ten, and whether the dominant library is open-source or proprietary, is unknown. The structural conditions are present. The timing and winner are forecasts.

### 7.3 What This Means for Practitioners

**[B]** The practical implication for AI engineering teams today:

- Invest in skill extraction as a first-class engineering activity, not an afterthought
- Gate skills rigorously (rung 641 minimum for internal use; rung 65537 for shared use)
- Track behavioral hashes across model upgrades
- Treat the skill library as the primary intellectual asset of an AI deployment, not the prompt collection

**[B]** Teams that build deep, well-gated skill libraries will compound capability across model generations — because the skills transfer, even when the weights do not. Teams that treat each model upgrade as a reset will re-derive the same patterns, at the same cost, every time.

---

## References

- `papers/05-software-5.0.md` — Software 5.0 theoretical foundation
- `papers/01-lane-algebra.md` — epistemic typing (A/B/C/STAR, MIN rule)
- `papers/03-verification-ladder.md` — 641 → 274177 → 65537 rung gates
- `papers/02-counter-bypass.md` — LLM classify + CPU enumerate (recipe compression example)
- `skills/prime-coder.md` — primary skill example (behavioral hash, never-worse doctrine)
- `skills/phuc-forecast.md` — planning loop skill (composability example)
- `PHUC-SKILLS-SECRET-SAUCE.ipynb` — skill composition demonstration
- `HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb` — recipe compression in action
- Karpathy, A. (2017). "Software 2.0." Medium.

---

**Auth: 65537** (project tag; see `papers/03-verification-ladder.md`)
**License:** Apache 2.0
**Citation:**
```bibtex
@software{stillwater2026_extension_economy,
  author = {Truong, Phuc Vinh},
  title = {The Extension Economy: Skills, Recipes, and the Economics of Compressible Intelligence},
  year = {2026},
  url = {https://github.com/phuctruong/stillwater/papers/23-software-5.0-extension-economy.md},
  note = {Auth: 65537}
}
```
