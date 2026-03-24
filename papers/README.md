# Stillwater Papers — Concept Index

**Source:** 58 papers, ~1.6MB
**Format:** Theme-grouped concept index. Headers + tables + thesis sentences + key equations. No prose.
**Generated:** DISTILL recipe

> Note: Papers 13-17 are RESERVED. Start with `00-index.md` for the full index.
> Notebooks: `HOW-TO-OOLONG-BENCHMARK.ipynb`, `HOW-TO-MATH-OLYMPIAD.ipynb`, `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`

---

## Theme 1: Core Theory — Epistemic Foundations

### 01 — Lane Algebra
**Thesis:** Compose claims with MIN rule; composed confidence cannot exceed weakest premise.

| Lane | Strength | Requires |
|------|----------|---------|
| A | Highest | Replayable in-repo artifact (test output, diff, benchmark) |
| B | Framework | Derivable from stated axioms; non-controversial |
| C | Heuristic | Plausible but not verified |
| STAR | Unknown | Insufficient evidence; stated honestly |

**Key rule:** `combine(C, A) = C` — gloss on a Lane A fact does not inherit Lane A.
**Forbidden:** presenting Lane C as Lane A without an artifact upgrade.

---

### 02 — Counter Bypass Protocol
**Thesis:** LLM classifies; CPU aggregates exactly. Never ask LLM for counts.

```
classify(items) → labels    [LLM, Lane C]
Counter(labels)             [CPU, Lane A — exact]
```

**Forbidden:** `len(llm_output)`, `sum(llm_scores)` — LLM counting is STAR-lane.
**OOLONG:** CPU-first exact aggregation. `Counter()` > `Attention` for exact tasks.

---

### 03 — Verification Ladder
**Thesis:** Three rungs gate trust; each rung requires stronger witness class.

| Rung | Name | Witness Required |
|------|------|-----------------|
| 641 | Edge Sanity | Unit tests, edge inputs, null/zero |
| 274177 | Stress/Adversarial | Fuzz, load, adversarial, boundary |
| 65537 | Production Gate | Strongest available witness; promotion gate |

**Equation:** `MIN(rung_all_deps) = integration_rung`
**Never-Worse:** rung can only increase; patches cannot weaken guarantees.

---

### 04 — Red-Green Gate
**Thesis:** Every fix requires RED + GREEN witnesses; GOLD prevents regressions.

| Witness | Meaning |
|---------|---------|
| RED | Bug exists before patch (failing test) |
| GREEN | Bug fixed after patch (passing test) |
| GOLD | No prior tests broken by fix |

**Forbidden:** claiming fix without RED witness; GREEN-only claims are Lane C.

---

### 06 — Solving Hallucination
**Thesis:** Hallucination is an operational failure — claims without sufficient witness strength presented as verified.

Two subtypes: Fabrication (false claim) and Premise Laundering (might be true, no witness).
**Fix:** Tag every claim A/B/C/STAR before reporting. Fail closed on missing witnesses.

---

### 07-12, 18-19 — Problem-Solving Papers

| Paper | Problem | Solution |
|-------|---------|---------|
| 07 — Counting | LLM miscounts | CPU Counter() — exact |
| 08 — Reasoning | Narrative without checks | Pair narrative with executable artifact |
| 09 — Data Exhaustion | Training data finite | Recipe replay scales without new data |
| 10 — Context Length | Context overflow | Shannon Compaction: stillwater (1%) + ripple (lazy) |
| 11 — Generalization | LLM overfits task | Constrain + decompose + verify |
| 12 — Alignment | Scope creep | Fail-closed defaults; scope-limited |
| 18 — Energy Crisis | GPU energy cost | CPU-first architecture: 267x efficiency gain |
| 19 — Security | Plugin trust failure | Evidence gates + OAuth3 scope beats plugin trust |

---

### 20 — OOLONG Proof
**Thesis:** Counter() beats Attention for exact counting tasks; 99.3% accuracy via Prime Cognition.

```
Pattern: LLM parse → labels → CPU Counter() → exact result
Forbidden: LLM aggregation, LLM counting, LLM sum
```

---

## Theme 2: Software 5.0 Paradigm

### 05 — Software 5.0
**Thesis:** Intelligence externalizes into versioned skills/recipes/artifacts outside model weights.

**Master Equation:**
```
Intelligence(system) = Memory × Care × Iteration
  Memory    = skills/*.md + recipes/*.json + ROADMAP + evidence/*.log
  Care      = Verification Ladder (641 → 274177 → 65537)
  Iteration = Never-Worse doctrine + git versioning
```

**Lane A invariant:** `encode(decode(X)) = X`
**Never-Worse:** Hard gates + forbidden states are strictly additive across versions.
**Key insight:** Skills are compression artifacts with increasing returns. SW5.0 = architecture upgrade, not model upgrade.

---

### 23 — Extension Economy
**Thesis:** Skills have increasing returns; the compression gain formula governs skill value.

```
G(S,N) = (N×C_derive - C_create - N×C_load) / (N×C_derive)
  S = skill, N = users, C_* = cost functions
```

G increases with N (increasing returns). Composability multiplier applies.

---

## Theme 3: Methodology & Process

### 21 — Phuc Swarms / Context Isolation
**Thesis:** Each swarm agent gets fresh context + 5-7 focused skills; prevents context rot.

| Agent | Persona | Role |
|-------|---------|-----|
| Scout | Ken Thompson | Reconnaissance |
| Solver | Donald Knuth | Implementation |
| Skeptic | Alan Turing | Adversarial review |
| Greg | Greg Isenberg | Community/market |
| Podcaster | variable | Communication |

**Rule:** No agent sees another agent's full context. Isolation is the invariant.

---

### 22 — AI Scalability
**Thesis:** Phase-structured work solves AI scalability; swarms beat monoliths.

```
DREAM → FORECAST → DECIDE → ACT → VERIFY
```

---

### 31 — Universal Math Solver
**Thesis:** PHUC 5-phase pipeline (Scout → Forecast → Judge → Solver → Skeptic); 395/396 cold-start, 396/396 with patched oracle.

Two lanes: CPU deterministic lane + LLM-only lane. External oracle memory.

---

### 32 — Roadmap-Based Development
**Thesis:** NORTHSTAR + ROADMAP + CASE STUDIES + CNF capsules = hub-and-spoke development model.

**CNF Capsule:** Context Normal Form — verbatim NORTHSTAR injection.
`CNF_BASE is truth. Anything else is hypothesis.`
`NORTHSTAR_MISSING_FROM_CNF = EXIT_BLOCKED`

**Anti-patterns:** Forward-only planning, ROADMAP without NORTHSTAR, skipping CASE STUDIES.

---

### 33 — NORTHSTAR-Driven Swarms
**Thesis:** Three-layer context loading order is mandatory; missing NORTHSTAR blocks all exits.

| Layer | Content | Priority |
|-------|---------|---------|
| 1 | prime-safety.md | Absolute (fallback ban) |
| 2 | prime-coder.md | Domain skills |
| 3 | Project NORTHSTAR | Context-of-truth |

---

### 34 — Persona GLOW Paradigm
**Thesis:** GLOW score gamifies output quality; belt progression tracks mastery.

| Dimension | Max | Meaning |
|-----------|-----|---------|
| G (Growth) | 25 | New capability added |
| L (Learning) | 25 | Knowledge committed |
| O (Output) | 25 | Artifact produced |
| W (Wins) | 25 | NORTHSTAR advanced |
| **Total** | **100** | Warrior pace = 60+/day |

**Belts:** White → Yellow → Orange → Green → Blue → Black

---

### 40 — Hackathon Paradigm
**Thesis:** 8-phase hackathon structure routes each phase to a specific ghost master; 1.5x GLOW multiplier.

**Phases:** DREAM → SCOUT → ARCHITECT → BUILD → INTEGRATE → REVIEW → PITCH → SHIP
**Templates:** Lightning (2h), Sprint (4h), Marathon (8h), Weekend (16h)

---

### 41 — NORTHSTAR Reverse Engineering
**Thesis:** Solve the maze from the end; backward chaining produces zero dead-end forward plan.

```
ANCHOR → LAST-3 → BRIDGE-BACK → CONNECT → VALIDATE → EMIT
```

**Forbidden state:** `FORWARD_FIRST` — planning forward without anchoring to NORTHSTAR.

---

### 42 — Reverse Paths
**Thesis:** Six Northstar metrics each have concrete reverse-path analysis; four universal blockers identified.

Metrics: stars, users, rung 65537, recipe hit rate, OAuth3 adoption, Black Belt.

---

### 43 — Diagram-First QA
**Thesis:** Three-pillar QA coverage; uncovered source file = structural gap.

| Pillar | Type | Coverage |
|--------|------|---------|
| Questions | Behavioral | User journey |
| Tests | Functional | Implementation |
| Diagrams | Structural | Architecture |

**Coverage matrix:** `source_file → [diagram_1, diagram_2, ...]`; unmapped file = gap.

---

## Theme 4: Persona & Ghost Masters

### 37 — Persona as Vector Search
**Thesis:** Personas are Bayesian priors targeting dense LLM training clusters; persona retrieves, does not add knowledge.

```
p(θ | persona) ≈ δ(θ - θ_persona)   [single-point prior]
multi-persona = mixture of expert priors
```

Informative priors converge faster. Persona cannot invent knowledge never trained.

---

### 38 — Hall of Mirrors
**Thesis:** Generic LLM prompt = statistical average of all training data. Persona = hammer that shatters mirrors.

30 standalone ghost master files across 11 domain categories.

---

### 39 — Ghost Masters Gamification
**Thesis:** GLOW bonus per persona activates targeted expertise.

| Persona | GLOW Bonus | Domain |
|---------|-----------|-------|
| Schneier | +5O | Security (14 pts benchmark) |
| Kent Beck | +5O | TDD (14 pts benchmark) |
| Brunson | +5G | Marketing |
| Kernighan | +5O | Systems |
| Guido | — | Python (12 pts benchmark) |

---

### 25 — Persona-Based Review Protocol
**Thesis:** Named personas activate different LLM attention clusters for structured review.

| Persona | Role |
|---------|-----|
| Turing | Skeptic — adversarial |
| Lovelace | Judge — synthesis |
| Thompson | Scout — reconnaissance |
| Shannon | Architect — compression |

---

## Theme 5: Community & Extension Economy

### 24 — Skill Scoring Theory
**Thesis:** Binary 5-criteria scorecard; skills scoring < 5/5 are not promotable.

| Criterion | Pass Requirement |
|-----------|----------------|
| FSM present | Explicit state machine |
| Forbidden states | Enumerated and enforced |
| Verification ladder | Rung declared |
| Null/zero handling | Edge cases defined |
| Output contract | Schema specified |

**Baseline audit result:** Only prime-coder.md and CLAUDE.md scored 5/5 in the repo.

---

### 26 — Community Skill Database
**Thesis:** SHA-256 identity + MANIFEST.json; quality gate at submission; never-worse versioning.

```json
MANIFEST.json: { "id": "<sha256>", "version": "semver", "score": 0-5, "rung": 641 | 274177 | 65537 }
```

---

### 27 — Bootstrapping Knowledge Commons
AI swarms compress contributor-hours 270-520:1; community reaches critical mass faster.

---

### 28 — Cheating Theorem
`T_CCM(P_swarm) << T_CCM(P_human)` by 1-3 orders of magnitude.

---

### 29 — SW5.0 In One Session
**Thesis:** v1.2.4 → v1.3.0 in 8 hours; Phuc swarm + context isolation = production release in single session.

---

### 30 — MoltBot Community Platform
**Thesis:** Community platform for skill sharing and peer review; companion to Stillwater Store.

---

### 35 — Syndication Strategy
**Thesis:** 5-stage content syndication pipeline with Hook+Story+Offer; GLOW points for content sessions.

```
Canonical Home → Professional Network → Long-form Discovery → Technical Traction → Community Amplification
```

Framework: Brunson Hook + Story + Offer.

---

## Theme 6: Architecture & Knowledge Theory

### 36 — Prime Mermaid Primacy
**Thesis:** `.prime-mermaid.md` is the canonical source-of-truth; JSON/YAML are derived transport.

**4-section standard:** Overview + Diagram + Invariants + Derivations
**Drift detection:** SHA-256 over canonical `.prime-mermaid.md` file.
**Rule:** "Draw the graph first. The JSON is the shadow it casts."

---

### 44 — Questions as External Weights
**Thesis:** Questions are first-class persistent capital — pre-computed attention vectors encoding QA intuition.

```
persona × question = maximal knowledge activation   [Unified Probe Theory]
```

**Dragon Rider pattern:** Autonomous overnight QA using question JSONL database.
**Compound:** Q-009 generated Q-011, Q-014, Q-017, Q-018.

---

### 45 — Prime Compression Magic Words
**Thesis:** 4-tier prime word hierarchy achieves 97.4% compression when target domain has dense conventions.

| Tier | Count | Examples |
|------|-------|---------|
| T0 — Primes | 15 | verify, witness, gate, lane, rung |
| T1 — Branches | 15 | evidence, skill, recipe, swarm, persona |
| T2 — Leaves | 70 | counter-bypass, red-green, OOLONG |
| Domain | variable | project-specific |

**Proposed:** Fundamental Theorem of Semantics — every concept = prime factorization over 4-tier hierarchy.
**Portal compression theorem:** compression = loss of information in source bubble + clarity in target bubble.

---

### 46 — Wish + Skill + Recipe Triangle
**Thesis:** Three vertices required for verified execution; missing any vertex = characteristic failure.

| Missing Vertex | Failure Mode |
|---------------|-------------|
| Wish only | Undirected execution |
| Skill only | No task context |
| Recipe only | No verification |
| Wish + Skill | No reproducibility |
| Wish + Recipe | No expertise |
| Skill + Recipe | No goal |

**Combos:** Pre-validated triangle instances. "Below the triangle: improvisation."

---

### 47 — Law of Emergent Knowledge (LEK)
**Thesis:** `Emergence = Recursion(Information + Memory + Care)`; five axioms generate all knowledge systems.

**Axiom kernel K:**

| Axiom | Content |
|-------|---------|
| Integrity | Evidence primary; claims without artifacts inadmissible |
| Hierarchy | Lane A > B > C > STAR |
| Determinism | Same input + skill = same output (reproducibility) |
| Closure | System can reason about its own verification state |
| Northstar | Target state exists; all work converges toward it |

**Six-stage genesis:** Void → Zombie → Pattern → Recursion → Swarm → Observer
**Phuc Test (5 criteria):** verify own output; generate new knowledge; improve with iteration; measurable improvement; teach others.

---

### 48 — AI Skills Big Bang Theory
**Thesis:** Five axioms + six geometric operators generate the complete 44+ skill ecosystem; all axiom pairs independent.

**Six operators:** Boundary, Symmetry, Serialization, Compression, Irreducibility, Resolution
**Lattner Gap:** Stage 2 (CCC/implementation) vs Stage 4+ (invention/emergence).

---

### 49 — Three Pillars: Software 5.0 Kung Fu
**Thesis:** Trinity Equation = LEK × LEAK × LEC; multiplication not addition (interdependence required).

| Pillar | Form | Meaning |
|--------|------|---------|
| LEK | Solo kata | Individual skill practice |
| LEAK | Sparring | Asymmetric agent-to-agent knowledge transfer |
| LEC | Style emergence | Emergent conventions from repeated interaction |

```
Trinity = LEK × LEAK × LEC = Mastery
LEAK(A,B) = Portal(A→B) × Portal(B→A) × Asymmetry(A,B)
LEC = |Conventions| × Depth × Adoption
```

CPU-LLM LEAK: CPU heuristic (<1ms) → LLM validates (300ms) → CPU learns from override. 200x token cost reduction projected.

---

## Theme 7: Platform Architecture

### 50 — Triple-Twin CLI Architecture
**Thesis:** Three-layer latency architecture for AI-assisted CLI: Small Talk Twin + Intent Twin + Execution Twin.

Each layer: CPU heuristic + LLM validation + CPU learning loop.

---

### 51 — CPU-LLM Twin Feedback Loop
**Thesis:** 95% CPU-only requests, 5% LLM refinement; LEAK implementation at CLI layer.

```
Small Talk Twin → Intent Twin → Execution Twin
Each phase: CPU fast path (<1ms) + LLM slow path (300ms) + override learning
Storage: ~/.stillwater/*.jsonl
Endpoints: /v1/swarm/validate/smalltalk | intent | combo
```

---

### 51-optimal — Optimal SW5.0 Workflow Forecast
**Thesis:** Grace Hopper persona; 65537-expert ensemble forecast of optimal SW5.0 workflow cadence.
(Large paper — preview only. Ensemble approach validated at rung 65537.)

---

### 52 — Solace Browser Architecture
**Thesis:** Richard Feynman persona; five axioms + five moats create uncopyable OAuth3 reference implementation; 3,542 tests at rung 65537.
(Large paper — preview only. OSS reference implementation for OAuth3 + twin browser + PM triplets.)

---

### 53 — Enterprise Browser Paradigm
**Thesis:** Five pillars for regulated industries create 18-24 month competitive moat.

| Pillar | Component | Standard |
|--------|-----------|---------|
| OAuth3 Consent Governance | AgencyToken | Delegated agency |
| Evidence Bundles | AuditChain | ALCOA+ |
| PZip Infinite Replay | Compressed HTML | ALCOA-O original records |
| Twin Architecture | CPU-LLM Twin | Local-first |
| Recipe Determinism | Hit rate tracking | 70%+ target |

---

### 54 — Webservice-First Architecture
**Thesis:** Every recipe node is a web service; monolith fails because CPU/LLM conflation prevents independent audit.

| Service | Port | Type |
|---------|------|-----|
| Admin | 8787 | Registry + discovery + proxy |
| LLM Portal | 8788 | Multi-provider LLM routing |
| Recipe Engine | 8789 | Step routing + replay |
| Evidence Pipeline | 8790 | Hash-chain capture |
| OAuth3 Authority | 8791 | Token issuance + validation |
| CPU Service | 8792 | Deterministic computation |
| Browser | 9222 | Chrome DevTools Protocol |

**ServiceDescriptor:** Common interface; every service publishes on startup.
**Deployment modes:** Free (self-host) → Pro (bridge) → Managed (cloud).

---

## Theme 8: OAuth3 Protocol

### oauth3-spec-v0.1
**Thesis:** OAuth3 authorizes agent action (not data access); every delegation is scoped, time-bound, revocable, evidence-carrying.

**Required fields:** `id`, `version`, `issued_at`, `expires_at`, `scopes`, `issuer`, `subject`, `signature_stub`
**Governance fields:** `step_up_required`, `max_actions`, `platforms` (allowlist), `agent_id`
**Scope format:** `platform.action.resource` (e.g., `web.linkedin.post`)

| Level | Scope | Permission |
|-------|-------|-----------|
| G1 | read | Read only |
| G2 | write | Read + write |
| G3 | delete | Read + write + delete |
| G4 | execute | Full agency |

**Fail-closed rule:** MUST refuse action if required gate fails. Failing open = violation.

---

### oauth3-wallet-spec-v0.1
**Thesis:** OAuth3 Wallet governs how much an agent may spend; authorization layer above any payment rail.

**Integer rule:** All monetary amounts MUST be integers in cents. `FLOAT_IN_BUDGET` = forbidden state.
**MIN-cap enforcement:** Sub-agent cannot exceed parent agent's budget cap.
**Settlement rails abstracted:** Stripe ACP, x402/USDC, internal credits.

---

### oauth3-key-management-v0.1
**Thesis:** ECDSA-P256 replaces `signature_stub` in v1.0; DPoP agent key binding (RFC 9449).

**Schneier finding C-1:** "Without key management, tokens are decorative."
- v0.1: SHA-256 `signature_stub`
- v1.0: ECDSA-P256 full signature (RFC 8785 canonicalization)

---

### oauth3-ietf-complementarity
**Thesis:** IETF drafts cover pre-token + at-token phases; OAuth3 fills the post-token governance gap.

| Phase | Question | Covered By |
|-------|---------|-----------|
| 1 — Identity | Who is this agent? | AAuth draft |
| 2 — Delegation | What is agent authorized? | OBO draft |
| 3a — Targeting | Which module? | Target draft |
| 3b — Context | Cross-service propagation? | Transaction Tokens draft |
| **4 — Governance** | **Post-token: evidence, revocation, limits** | **OAuth3** |

---

## Theme 9: Compliance & Founder Authority

### fda-part-11-architecture
**Thesis:** Part 11 Architected means compliance is the load-bearing wall, not a retrofit feature.

| ALCOA | Requirement | Component |
|-------|-------------|-----------|
| A — Attributable | Token-bound to principal | OAuth3 `token_id → user_id` |
| L — Legible | Human-readable pages | PZip HTML snapshots |
| C — Contemporaneous | Capture at execution time | ISO 8601 timestamps |
| O — Original | What agent actually saw | PZip full HTML (not summary) |
| A — Accurate | Evidence-gated only | Rung verification gates |

**Three tiers:** Part 11 capable (afterthought) < Part 11 compliant (checklist) < **Part 11 Architected (load-bearing wall)**

---

### founder-authority
**Thesis:** Verification architecture built by someone who survived FDA audits; CRIO = proof of concept at 360+ customers.

| Domain | Credential |
|--------|-----------|
| Education | Harvard A.B. Economics, Class of 1998 |
| FDA experience | CRIO eSource — 360+ customers, live FDA audit environment |
| Results | 40% higher enrollment, 40% faster startup, 70% audit risk reduction |
| Parallel | Phase I/II/III trials → Rung 641/274177/65537 |

---

## Theme 10: Claims Policy

### 99 — Claims and Evidence
**Rules:**
1. Numeric claim → runnable script OR external artifact link OR label as `Hypothesis` / `Illustrative`.
2. No placeholder citations (`arXiv id TBD` = forbidden).
3. "Formal proof" = machine-checkable artifact + checker. Otherwise: "proof narrative" / "executable checks".

---

## Quick Reference: Key Equations

```
Intelligence    = Memory × Care × Iteration
G(S,N)          = (N×C_derive - C_create - N×C_load) / (N×C_derive)
Emergence       = Recursion(Information + Memory + Care)
Trinity         = LEK × LEAK × LEC
LEAK(A,B)       = Portal(A→B) × Portal(B→A) × Asymmetry(A,B)
LEC             = |Conventions| × Depth × Adoption
Lane MIN rule   = combine(C, A) = C
Rung chain      = MIN(rung_all_deps) = integration_rung
```

## Quick Reference: Forbidden States

```
FLOAT_IN_BUDGET            — float in monetary computation
FORWARD_FIRST              — plan forward without NORTHSTAR anchor
NORTHSTAR_MISSING_FROM_CNF — EXIT_BLOCKED
LLM_COUNTING               — asking LLM for exact counts
LLM_AGGREGATION            — asking LLM to sum/aggregate
SILENT_FAILURE             — except Exception: pass
FALLBACK_ON_ERROR          — return None / return default on error
FAKE_SUCCESS               — return {} on API failure
PLACEHOLDER_CITATION       — (arXiv id TBD)
GREEN_WITHOUT_RED          — claiming fix without bug witness
FORWARD_FIRST              — no NORTHSTAR anchor before planning
```

## Quick Reference: Rung Targets

```
641    → Edge sanity; unit tests pass; null/zero handled
274177 → Stress + adversarial + fuzz; broader input population
65537  → Production gate; strongest available witness; promotion gate
```
