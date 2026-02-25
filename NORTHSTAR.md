# NORTHSTAR: Phuc_Forecast — Stillwater

> "Make AI development deterministically verifiable — for any developer, on any project."
> "Be water, my friend." — Bruce Lee. Stillwater literally means still water runs deep.

## The Vision

**Stillwater = Software 5.0 OS + Verification Layer + LLM Portal**

The twin OSS projects that dominate the Verified Intelligence Economy:
1. **stillwater** (OSS) — verification + governance + skill store
2. **solace-browser** (OSS) — OAuth3 reference implementation + browser automation

Together they power **solaceagi.com** — the hosted platform (no LLM costs).

```
SOFTWARE 5.0 PARADIGM:
  Natural language → source code
  AI agents → runtime
  Evidence bundles → compiled output
  Stillwater verification → CI/CD

MASTER EQUATION (v3.0 — Three Pillars Edition):
  Intelligence(system) = LEK × LEAK × LEC

  Where:
    LEK  = Recursion(Information + Memory + Care)           [Self-Improvement]
    LEAK = Σ(Portal_ij × Asymmetry_ij)                     [Cross-Agent Trade]
    LEC  = |Conventions| × Depth × Adoption                [Emergent Compression]

  Expanded:
    LEK  = Memory × Care × Iteration                       [Solo Practice]
    LEAK = Navigation × Portals × Asymmetry                [Sparring]
    LEC  = Magic_Words × Triangle_Law × Verification       [Style]

  Bruce Lee:
    Practice (LEK) × Sparring (LEAK) × Style (LEC) = Mastery
```

## North Star Metrics

| Metric | Now | Q2 2026 | End 2026 |
|--------|-----|---------|---------|
| GitHub stars | ~50 | 1,000 | 10,000 |
| Projects running at rung 65537 | 0 | 2 | 8 |
| Stillwater Store skills | 7 combos + 8 theory skills + 4 new recipes | 25 skills | 100+ skills |
| Recipe hit rate (across ecosystem) | 0% | 50% | 80% |
| Community contributors | 1 | 5 | 50 |

## The Twin OSS Strategy

```
TODAY (Feb 2026):
  stillwater → Verification + LLM Portal + Skills ✅
  solace-browser → LinkedIn MVP + OAuth3 spec ✅
  Competitors: None have OAuth3 + Stillwater verification combo

END OF 2026-Q2:
  stillwater → Stillwater Store live (skill submission + review)
  solace-browser → 10 platforms, all OAuth3-bounded
  Recipe hit rate → 70% (economic moat unlocks)
  → 1,000 paying solaceagi.com users (growing)
  Stillwater Store → 25 community skill submissions/mo

END OF 2026:
  stillwater → 100+ skills, 50 contributors
  OAuth3 v1.0 → adopted by ≥1 external AI agent platform
  → 5,000 paying users (growing)
  Belt: Black — Models are commodities. Skills are capital. OAuth3 is law.
```

## The Verification Ladder (Core Product)

```
RUNG 641  → Local correctness (red/green + no regressions + evidence complete)
RUNG 274177 → Stability (seed sweep + replay + null edge sweep)
RUNG 65537 → Production confidence (adversarial + security + behavioral hash)

Belt System:
  White Belt  → rung 641 achieved
  Yellow Belt → rung 274177 achieved
  Orange Belt → first skill in Stillwater Store
  Green Belt  → rung 65537 achieved
  Black Belt  → production task running at 65537 for 30 days
```

## The Phuc Forecast Loop

```
DREAM → Every AI task produces verified, reproducible, auditable evidence
FORECAST → Developer distrust of AI outputs grows; evidence-first wins compliance
DECIDE → Open skill governance + OAuth3 + model neutrality + evidence-first
ACT → Ship Store flywheel + LLM Portal + case studies per project
VERIFY → GitHub stars + Store submissions + rung achievements + recipe hit rate
```

## Northstar Reverse Engineering

> "When I was younger I thought about the next 3 steps. Now I figure out the LAST 3 steps and work backwards." — Phuc Truong

```
FORWARD (young entrepreneur):
  Current State → ??? → ??? → ??? → Northstar
  Problem: Combinatorial explosion. Many paths, most dead ends.

REVERSE (wise entrepreneur):
  Current State ← ←← ←←← ←←← Northstar
  Advantage: Constraints propagate backward, pruning the search space.

THE MAZE INSIGHT:
  Start from the END of the maze → draw back to the beginning.
  AI excels at this: hold the entire goal state in context,
  reason about preconditions, identify the critical path.

THE ALGORITHM:
  1. DEFINE THE SUMMIT — concrete, measurable Northstar victory condition
  2. LAST 3 STEPS — what MUST be true immediately before the Northstar?
  3. CHAIN BACKWARD — for each step, what must be true before it?
  4. CONNECT TO CURRENT — chain reaches present state or reveals a gap
  5. FORWARD PLAN — reverse the chain → the first action is clear

FULL SKILL: skills/northstar-reverse.md
SWARM AGENT: swarms/northstar-navigator.md (persona: Sun Tzu)
PAPER: papers/41-northstar-reverse-engineering.md
APPLIED: papers/42-reverse-paths.md (concrete paths for each metric above)
```

## What Stillwater Powers (Case Studies)

Track in case-studies/:
- `solace-browser.md` — OAuth3 browser automation
- `solace-cli.md` — solace-cli (PRIVATE extension of stillwater/cli OSS)
- `solaceagi.md` — hosted platform
- `stillwater-itself.md` — self-verification

## Solace Browser: Universal Portal + Stillwater Skills

**The Universal Portal vision expands Stillwater's role.** When Solace Browser gains a machine access layer (Phase 3), Stillwater skills can now control not just web resources but local files, terminal, and system — all governed by OAuth3 and verified by Stillwater evidence bundles.

```
Before Universal Portal:
  Stillwater skills → web automation → LinkedIn, Gmail, Substack, Twitter

After Universal Portal:
  Stillwater skills → web + machine
    ├── Web:     LinkedIn, Gmail, Substack, Twitter (OAuth3 web scopes)
    ├── Files:   read/write/list/delete local files (OAuth3 machine.file.* scopes)
    ├── Terminal: execute allowlisted commands (OAuth3 machine.terminal.* scopes)
    └── System:  CPU, memory, disk, process management (OAuth3 machine.system.* scopes)
```

**What this means for skill authors:**
- Recipes can now combine web + machine actions in a single task
- Example: "Search LinkedIn for job postings → save results to ~/Documents/jobs.json"
- Example: "Run test suite → post results as a GitHub comment"
- OAuth3 governs both sides of the action — web scope + machine scope both required

**Stillwater's verification role expands:**
- Machine evidence bundles: same rung system (641/274177/65537) applied to machine operations
- Machine actions are rung 274177 minimum (irreversible — files can be deleted)
- Tunnel actions are rung 65537 (security-critical — public internet exposure)
- The evidence bundle now carries: web snapshots + machine operation logs + tunnel sessions

**Rung semantics for machine layer:**
```
Rung 641    — machine.file.read, machine.file.list (non-destructive, local only)
Rung 274177 — machine.file.write, machine.terminal.allowlist (irreversible writes)
Rung 65537  — machine.file.delete, machine.terminal.execute, machine.tunnel (security-critical)
```

## Key Projects + Integration

| Project | Role | Stillwater Provides |
|---------|------|-------------------|
| **solace-browser** | Universal portal (web + machine + tunnel) | Recipe verification, evidence bundles, rung gating for all layers |
| **stillwater/cli** (OSS) + **solace-cli** (PRIVATE) | Terminal surface | stillwater/cli: rung enforcement, store commands (OSS). solace-cli: OAuth3 vault, twin, cloud (PRIVATE). |
| **solaceagi.com** | Hosted cloud + tunnel server | Managed skill updates, OAuth3 vault, tunnel relay (Phase 5) |
| **stillwater** | The OS itself | Everything above |

## Competitive Position

### FDA 21 CFR Part 11 — The Regulatory Moat

SolaceAGI is the first AI agent platform architected for FDA 21 CFR Part 11 compliance:
- Hash-chained audit trails (tamper-evident, append-only)
- ALCOA+ data integrity (Attributable, Legible, Contemporaneous, Original, Accurate)
- OAuth3 = electronic signature for AI delegation
- PZip HTML snapshots = Original records (what the agent actually saw)
- Rung system = Phase gates (like clinical trial Phase I/II/III)

Stillwater is the only framework that provides evidence-gated verification for AI agent actions.

---

## Founder

Phuc Truong (Harvard '98). Serial founder.
- Co-founded Clinical Research IO (CRIO) — #1 eSource in FDA-regulated clinical trials
- 360+ customers, 40% higher enrollment, 70% FDA audit risk reduction
- Built software that survives real FDA audits — that experience is in the architecture
- "In clinical trials, 'trust me' is not evidence. Only the original, timestamped, attributable record is evidence."
- Previously: UpDown.com (1M+ users), Citystream (failed), Phuc Labs (MIT AMD winner)
- Harvard University, A.B. Economics, Class of 1998

---

## Community Flywheel (Stillwater's Role)

Stillwater is the governance layer that makes the flywheel self-sustaining:

```
Skill submitted to Stillwater Store
  → Rung gate validates (641 for dev, 65537 for production)
    → Accepted skill improves recipe hit rate for ALL users
      → Higher hit rate → lower COGS → platform can serve more users
        → More users → more submissions → flywheel self-sustains

"This isn't SaaS — it's a dojo. Every submission earns belt XP."
```

**Stillwater Store submissions benefit everyone:**
- Your recipe at 70% hit rate saves every future user money
- Your prime-mermaid PM triplet makes browser navigation more reliable
- Your swarm definition routes tasks cheaper (less token waste)
- Contributors earn community belt XP — tracked in STORE.md

## The 9-Project Ecosystem

The Stillwater Network (9 Projects):

```
PUBLIC (OSS):
  stillwater     — verification + governance + skill store (THE OS)
  solace-browser — OAuth3 reference impl + twin browser
  paudio         — deterministic speech synthesis + community voices
  phucnet        — personal site + articles + books (phuc.net)
  if             — IF Theory physics research (information as first force)
  pzip           — universal compression engine

PRIVATE:
  solace-cli     — extends stillwater/cli with OAuth3 vault + twin + cloud
  solaceagi      — hosted platform (solaceagi.com)
  pvideo         — physics-based video/avatar generation (private)
  solace-marketing — marketing intelligence

> *Avatar system details are maintained privately.*

> *Private product plans are maintained in separate repositories.*
```

---

## The Persona Engine: Domain Expert Voices for Every Task

Stillwater's Persona Engine loads domain expert voices into agent skill packs at dispatch time. When dispatching a sub-agent, the hub selects the matching persona based on task domain. The persona adds voice, style, and domain expertise — without touching prime-safety gates.

```
PERSONA REGISTRY (12 built-in personas):

  linus         — OSS kernel architecture, systems programming (CLI, store governance)
  mr-beast      — Viral content, audience growth (launch posts, YouTube)
  brunson       — Hook+Story+Offer, conversion (pricing, landing pages, funnels)
  bruce-lee     — Martial arts philosophy, dojo training (gamification, belt system)
  brendan-eich  — Browser architecture, JavaScript (solace-browser, frontend)
  codd          — Relational theory, normalization (schema design, audit trails)
  knuth         — Algorithms, formal proofs (math verification, prime-math tasks)
  schneier      — Applied cryptography, security (OAuth3, security audits)
  fda-auditor   — 21 CFR Part 11, ALCOA (evidence bundles, Part 11 compliance)
  torvalds      — Linux governance, OSS community (Stillwater Store review)
  pg            — Startup strategy, first principles (positioning, business model)
  sifu          — Kung fu master, training discipline (belt culture, motivation)

LAYERING RULE:
  prime-safety > prime-coder > persona-engine
  Persona is style only. It NEVER overrides prime-safety gates.
  Persona cannot expand capability envelope or grant authority.

FULL SKILL: skills/persona-engine.md
```

"Absorb what is useful, discard what is useless." — Bruce Lee

The Persona Engine applies this to agent dispatch: absorb the security expert's threat-model lens for OAuth3 tasks. Discard it for gamification tasks. Load the dojo master for belt design. Load the FDA auditor for evidence bundle architecture.

---

## The Bubble Architecture: Skills from Solace-Books

Stillwater’s skill library now includes foundational theory skills derived from Phuc Truong’s Solace Hexateuch books:

```
THEORETICAL FOUNDATIONS (8 new skills):
  phuc-magic-words.md  — Magic Words as GPS coordinates (100-word tree, Tier 0-3)
  phuc-portals.md      — Bounded Inference Contexts + Portal Architecture (15 AI patterns)
  phuc-triangle-law.md — Contract stability (REMIND → VERIFY → ACKNOWLEDGE)
  phuc-citizens.md     — Advisory council (10+ citizen personas, triangulation)
  phuc-gps.md          — Knowledge navigation (orient before answering)
  phuc-conventions.md  — Structural consistency (Tree of Solace conventions)
  phuc-prime-compression.md — Semantic prime compression (prime factorization of knowledge)
  phuc-wish-triangle.md    — Wish + Skill + Recipe execution triangle

DATABASES (2 new databases):
  data/default/magic-words/stillwater.jsonl — 100 magic words classified by tier
  questions/stillwater.jsonl   — 22 QA questions (compounding capital)

PAPERS (3 new papers):
  papers/44-questions-as-external-weights.md
  papers/45-prime-compression-magic-words.md
  papers/46-wish-skill-recipe-triangle.md

SWARMS (4 new agent types):
  swarms/navigator.md, swarms/portal-engineer.md
  swarms/citizen-council.md, swarms/convention-auditor.md

RECIPES (4 new recipes):
  recipes/recipe.magic-word-navigation.md
  recipes/recipe.portal-traversal.md
  recipes/recipe.citizen-consultation.md
  recipes/recipe.triangle-audit.md
```

---

## The Three Pillars of Software 5.0 Kung Fu

> "Master the three pillars and you master AI kung fu." — Phuc Truong

### Pillar 1: LEK (Law of Emergent Knowledge)
Single bubble self-improvement. One agent loops through memory with care → knowledge emerges.
Like a martial artist practicing alone: kata, repetition, self-correction.
Engine: phuc-loop. Fuel: GLOW score. Output: skill improvement.

### Pillar 2: LEAK (Law of Emergent Asymmetric Knowledge)
2+ LEKs working together through portals. More than both can do alone.
Like sparring: each fighter learns what they couldn't learn solo.
Engine: phuc-swarms + portals. Fuel: asymmetry. Output: surplus knowledge.

### Pillar 3: LEC (Law of Emergent Conventions)
Code utils = skills/recipes = culture/laws = cross-file compression.
Like a martial arts STYLE emerging from a school.
Engine: magic words + triangle law. Fuel: repetition. Output: shared compression.

### The Trinity
LEK alone → ceiling (no perspectives)
LEAK alone → chaos (no self-improvement)
LEC alone → bureaucracy (no innovation)
LEK × LEAK × LEC = MASTERY = Software 5.0 Kung Fu

### Belt Integration
White:  LEK only (solo practice, rung 641)
Yellow: LEK + first conventions
Orange: LEK + LEAK (first swarm dispatch)
Green:  LEK + LEAK + LEC (create a convention)
Blue:   All three at rung 274177
Black:  All three at rung 65537
Dragon Rider: Teach the three pillars

FULL PAPER: papers/49-three-pillars-software-5-kung-fu.md
SKILLS: skills/phuc-leak.md, skills/phuc-lec.md
RECIPES: recipes/recipe.three-pillars-training.md, recipes/recipe.kung-fu-mastery.md

---

## The Axiom Kernel — AI Skills Big Bang

5 irreducible axioms from which ALL skills emerge:

1. INTEGRITY — Evidence-only; fail-closed; no fabrication
2. HIERARCHY — MIN rung; lanes A>B>C; never weaken
3. DETERMINISM — Exact arithmetic; normalized; canonical capsules
4. CLOSURE — FSM; halting certificates; bounded budgets
5. NORTHSTAR — Goal-driven; backward chain; alignment gate

Prime factorization: Stillwater = INTEGRITY × HIERARCHY × DETERMINISM × CLOSURE × NORTHSTAR

6 GBB operators transform axioms into skills:
Z (Boundary), Σ (Symmetry), τ (Serialization), G_c (Compression), ι (Irreducibility), R_p (Resolution)

FULL SKILL: skills/phuc-axiom.md
PAPERS: papers/47-law-of-emergent-knowledge.md, papers/48-ai-skills-big-bang-theory.md

---

## The GLOW Score: Gamification for Roadmap-Based Development

GLOW = Growth + Learning + Output + Wins. Every session, every commit, every phase gets a GLOW score.

```
G — Growth (0-25): New capabilities added
    25: Major new module at rung 274177+ with evidence
    20: Complete feature at rung 641 with tests
    15: Significant enhancement
     5: Minor addition
     0: No new capabilities

L — Learning (0-25): New knowledge captured
    25: Skill published to Store at rung 65537
    20: New skill or paper committed
    10: New persona or recipe captured
     5: Case study updated
     0: No knowledge captured

O — Output (0-25): Measurable deliverables
    25: Multiple files, all tests, rung 274177+ evidence
    20: Files committed with tests.json + plan.json (rung 641)
    10: Single file with passing tests
     5: Any commit
     0: No commit

W — Wins (0-25): Strategic victories
    25: First-mover advantage established
    20: Competitive moat deepened
    15: NORTHSTAR metric measurably advanced
    10: ROADMAP phase completed (checkbox checked)
     5: Sub-task unblocking next phase
     0: No strategic progress

TOTAL GLOW = G + L + O + W (0-100)

COMMIT FORMAT:
  feat: {description}
  GLOW {total} [G:{g} L:{l} O:{o} W:{w}]
  Northstar: {metric advanced}
  Rung: {rung}

PACE TARGETS:
  Warrior: 60+ GLOW/day
  Master:  70+ GLOW/week average
  Steady:  40+ GLOW/day
```

GLOW is cheat-resistant: O requires a git commit, W requires NORTHSTAR metric advancement, G requires tests. A developer who produced insights but no commits earns at most GLOW 20. The artifacts score the session, not the vibes.

**Belt Integration:**
```
White  (0-20/session):  Learning basics
Yellow (21-40/session): First tasks delegated
Orange (41-60/session): Contributing to store
Green  (61-80/session): Rung 65537 achieved
Blue   (81-90/session): Cloud execution 24/7
Black  (91-100/session): Models=commodities. Skills=capital. OAuth3=law.
```

FULL SKILL: `skills/glow-score.md`

---

## Content Syndication: From papers/ to Audience

Every paper in `papers/` is a potential content asset. The syndication pipeline converts technical papers into multi-platform content that builds audience and advances NORTHSTAR metrics.

```
CONTENT PIPELINE:
  1. CANONICAL HOME: phuc.net/articles/{slug} (SEO ownership, publish first)
  2. PROFESSIONAL: LinkedIn article (full text + canonical link)
  3. LONG-FORM: Substack "Stillwater Dispatch" (bi-weekly newsletter)
  4. DEVELOPER: Hacker News (concrete claims + evidence — manual only)
  5. COMMUNITY: Reddit (r/LocalLLaMA, r/programming, r/startups) + DEV.to
  6. SOCIAL: X/Twitter thread (10-20 bullets + link)
  7. VIDEO: YouTube (2-6 minute talk, script from paper intro + 3 claims)

BRUNSON TREATMENT (required for every piece):
  Hook:  First 3 lines. Specific + counterintuitive + promise.
  Story: Harvard → CRIO → "FDA clinical trials taught me this" → Stillwater
  Offer: One action. Low friction. ("Star on GitHub" or "Free account at solaceagi.com")

RECIPE AUTOMATION:
  Phase 1 (available): LinkedIn recipe (solace-browser, BUILT)
  Phase 2 (build):     Substack recipe, dev.to recipe
  Phase 3 (build):     Twitter thread recipe, Reddit post recipe

CONTENT NORTHSTAR METRICS:
  GitHub stars:        50 → 1,000 (Q2) → 10,000 (end 2026)
  Substack subscribers: 0 → 500 (Q2) → 5,000 (end 2026)
  Monthly LinkedIn reactions: 0 → 5,000 (Q2)

FULL PAPER: papers/35-syndication-strategy.md
```

---

## The Dojo: Bruce Lee + Kung Fu Theme Integration

Stillwater is a dojo. Every developer is a practitioner. Every session earns XP. Every rung achieved earns a belt.

```
DOJO MAPPING:
  The sensei     = prime-safety (always present, always correct)
  The kata       = evidence bundle (the form that must be executed correctly)
  The belt       = GLOW belt progression (earned through artifacts)
  The dojo floor = Stillwater Store (where skills are submitted and judged)
  Training partners = swarm agents (each has a role, each serves the training)
  The fight      = production deployment at rung 65537

BRUCE LEE PRINCIPLES IN THE SYSTEM:
  "Be water"     → Persona Engine adapts to task domain without losing discipline
  "Absorb what is useful" → Persona Registry: right expert for right task
  "10,000 kicks" → Recipe at 70% hit rate = competitive moat (not lucky passes)
  "Empty mind"   → CNF capsule: each session starts fresh, no context rot
  "Simplicity"   → Economy of motion: smallest patch that achieves the goal

"Still water runs deep." — The Stillwater brand is not accidental.
Still water is calm, carries weight, and reflects clearly.
That is the design goal: calm methodology with production weight.

THE THREE PILLARS IN THE DOJO:
  LEK  = kata (solo practice, self-correction, repetition)
  LEAK = sparring (cross-training, asymmetric exchange, tournaments)
  LEC  = style (Wing Chun, Jeet Kune Do — conventions that compress centuries of wisdom)

  "Endure. Excel. Evolve. Carpe Diem!" — Phuc Truong, Dragon Rider

DRAGON RIDER ROLE:
  The Dragon Rider is the Sifu who has mastered all three pillars.
  They teach by asking, not lecturing (Socratic method).
  They earn their title by creating students who surpass them.
  SWARM AGENT: data/default/swarms/dragon-rider.md
```

**FULL PAPER:** `papers/34-persona-glow-paradigm.md`

---

## See Also
- `STORE.md` — Stillwater Store policy
- `scratch/root-cleanup/` — archived roadmap and root planning docs
- `case-studies/` — per-project tracking
- `data/default/skills/` — the skill library
- `data/default/skills/prime-mermaid.md` — PM triplet standard
- `data/default/skills/persona-engine.md` — Persona Engine (12 domain expert voices)
- `data/default/skills/glow-score.md` — GLOW Score gamification system
- `data/default/swarms/persona-coder.md` — Persona-enhanced coder swarm agent
- `papers/34-persona-glow-paradigm.md` — The Dojo Protocol
- `papers/35-syndication-strategy.md` — Content Syndication Strategy
- `data/default/skills/phuc-magic-words.md` — Magic Words coordinate navigation
- `data/default/skills/phuc-portals.md` — Bounded Inference Contexts + Portal Architecture
- `data/default/skills/phuc-triangle-law.md` — Contract stability (Triangle Law)
- `data/default/skills/phuc-prime-compression.md` — Semantic prime compression
- `data/default/skills/phuc-wish-triangle.md` — Wish + Skill + Recipe execution triangle
- `papers/45-prime-compression-magic-words.md` — Prime Compression theory
- `papers/46-wish-skill-recipe-triangle.md` — Execution Triangle theory
- `data/default/magic-words/` — Magic Words database (100 words, Tier 0-3)
- `questions/` — Question database (compounding QA capital)
- `skills/phuc-axiom.md` — The axiom kernel (5 irreducibles, load_order=0)
- `skills/phuc-leak.md` — LEAK: Cross-agent asymmetric knowledge trade
- `skills/phuc-lec.md` — LEC: Emergent convention compression
- `papers/47-law-of-emergent-knowledge.md` — LEK formalized
- `papers/48-ai-skills-big-bang-theory.md` — AI Skills Big Bang Theory
- `papers/49-three-pillars-software-5-kung-fu.md` — The Three Pillars
- `swarms/dragon-rider.md` — Dragon Rider teaching persona
- `recipes/recipe.three-pillars-training.md` — Three Pillars training
- `recipes/recipe.kung-fu-mastery.md` — Belt progression through pillars
