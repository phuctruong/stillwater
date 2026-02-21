# The Dojo Protocol: Persona-Enhanced Agents and GLOW Gamification in Roadmap-Based Development

**Paper ID:** persona-glow-paradigm
**Date:** 2026-02-21
**Status:** STABLE
**Authority:** 65537
**Tags:** gamification, persona, GLOW, belt-system, roadmap, dojo, bruce-lee, motivation
**Related:** `papers/32-roadmap-based-development.md`, `papers/33-northstar-driven-swarms.md`, `skills/persona-engine.md`, `skills/glow-score.md`

---

## Abstract

Roadmap-Based Development solves the coordination problem in multi-session AI development: NORTHSTAR provides direction, ROADMAP provides phased execution, CNF capsules prevent context rot, and rung ladders enforce evidence-gated quality. This paper extends the paradigm with two reinforcing mechanisms: the Persona Engine and GLOW Score gamification. The Persona Engine loads domain expert voices into agent skill packs — transforming a generic coder agent into a security-aware analyst (Schneier persona), a systems programmer (Linus persona), or a database theorist (Codd persona) depending on task domain. The GLOW Score provides a transparent, artifact-grounded progress metric (Growth + Learning + Output + Wins = 0-100) that maps directly to belt progression. Together, these mechanisms solve a problem that pure verification discipline cannot: motivation. The dojo metaphor ties the system together — every developer is a practitioner, every session earns XP, every rung achieved earns a belt. "Be water, my friend" is not decoration. It is the design principle: the system adapts to the task, the practitioner, and the pace.

---

## 1. Why Verification Discipline Alone Is Not Enough

### 1.1 The Motivation Problem

The Stillwater verification ladder (641 → 274177 → 65537) solves the quality problem. Red-green gates, CNF capsules, and the Never-Worse Doctrine ensure that every committed artifact is traceable, reproducible, and evidence-backed. A project running at rung 65537 is not lucky — it is disciplined.

But discipline requires motivation. The evidence bundle requirement can feel like bureaucracy to a developer under deadline pressure. The rung system can feel abstract when the immediate goal is "make the tests pass." The NORTHSTAR document can feel distant when you are debugging a null pointer exception at midnight.

This is the motivation problem: how do you make verification discipline intrinsically rewarding rather than externally imposed?

### 1.2 The Generic Agent Problem

The second problem is orthogonal to motivation. When dispatching a sub-agent for a security audit, you want Schneier's threat-model lens. When dispatching for a database schema design, you want Codd's normalization rigor. When dispatching for marketing copy, you want Brunson's hook-story-offer architecture.

A generic "sonnet coder" agent has none of these specializations. It produces technically correct output in a voice that is... generic. The output is correct but not sharp. It addresses the problem but misses the domain-specific pitfalls that an expert would catch immediately.

The generic agent problem: how do you give domain expert perspective to an agent that starts fresh every session?

### 1.3 The Solution: The Dojo Protocol

The Dojo Protocol answers both problems simultaneously:

- **GLOW Score** turns verification discipline into a game with transparent, artifact-grounded scoring
- **Persona Engine** loads domain expert voices into agent skill packs at dispatch time
- **Belt Progression** ties GLOW accumulation to visible status advancement
- **Bruce Lee Integration** provides the philosophical framework: discipline as liberation, not constraint

"Be water, my friend." The water does not resist the container — it fills it. The developer does not resist the evidence requirements — they earn GLOW by satisfying them. The shape is the same. The experience is different.

---

## 2. The Persona Engine: Domain Expert Voices at Dispatch Time

### 2.1 The Problem It Solves

Every sub-agent starts fresh. It has no memory of prior sessions, no accumulated domain knowledge beyond what is in its training weights, and no perspective on the specific project's constraints.

The Persona Engine bridges this gap. When the hub dispatches a security-sensitive task, it loads the Schneier persona into the agent's skill pack. The agent now has:
- Threat-model-first framing for all analysis
- Cryptographic key management principles
- "Complexity is the enemy of security" as a decision heuristic
- The ability to recognize security theater vs. real security

When the hub dispatches a gamification design task, it loads the Bruce Lee persona:
- "Be water" as the design principle (adaptable, not rigid)
- Belt progression as earned recognition, not purchased status
- Economy of motion: the simplest mechanism that achieves the goal
- Dojo culture: mutual obligation, standards, respect for the form

### 2.2 The Persona Registry

Twelve built-in personas cover the primary domains of the Stillwater ecosystem:

| Persona | Domain | Primary Use |
|---------|--------|-------------|
| `linus` | OSS architecture, systems | CLI design, store governance |
| `mr-beast` | Viral content, audience growth | Launch posts, YouTube scripts |
| `brunson` | Hook+Story+Offer, conversion | Pricing pages, funnels |
| `bruce-lee` | Dojo philosophy, martial arts | Gamification, belt system |
| `brendan-eich` | Browser, JavaScript, web standards | solace-browser, frontend |
| `codd` | Relational theory, normalization | Schema design, audit trails |
| `knuth` | Algorithms, formal proofs | Math verification, algorithms |
| `schneier` | Applied cryptography, security | OAuth3, security audits |
| `fda-auditor` | Part 11, ALCOA, evidence | Evidence bundles, compliance |
| `torvalds` | Linux governance, OSS community | Stillwater Store review |
| `pg` | Startup strategy, first principles | Positioning, business model |
| `sifu` | Kung fu master, training | Belt culture, motivation |

### 2.3 Persona Layering (The Immutable Rule)

Personas are style priors. They are never authority grants.

```
Authority Chain:
  prime-safety (god-skill) — wins all conflicts
    > prime-coder (evidence discipline)
      > persona-engine (voice + domain expertise)
        > task output

Persona CANNOT:
  - Override a prime-safety stop condition
  - Expand the capability envelope
  - Grant network access not in the allowlist
  - Replace evidence requirements with prose confidence
```

The Schneier persona does not make the security audit easier. It makes it sharper. The FDA auditor persona does not relax Part 11 requirements. It helps the agent identify what Part 11 actually requires. Persona adds precision, not permission.

### 2.4 Multi-Persona Loading

Complex tasks benefit from multiple personas. A product launch requires both marketing insight (Brunson's hook-story-offer) and technical credibility (Linus's "show me the code"). A security-compliant audit trail requires both cryptographic rigor (Schneier) and regulatory alignment (FDA auditor).

Multi-persona loading merges the voice rules and domain expertise from each persona. On conflict, the more technical persona wins for implementation decisions; the more strategic persona wins for framing.

Example — launching Stillwater Store:
```
PERSONA_PACK:
  primary: brunson    # Hook+Story+Offer for the announcement
  secondary: torvalds # OSS governance credibility for the technical audience
  integration: "Brunson frames the value. Torvalds validates the standard."
```

### 2.5 The Persona-Coder Swarm Agent

The `swarms/persona-coder.md` agent formalizes this pattern as a reusable swarm agent type. It extends the base Coder with:
1. Automatic persona selection based on task domain keywords
2. Persona voice injection into all output
3. GLOW score calculation at task completion
4. `glow_score.json` as a required artifact alongside `tests.json` and `evidence/plan.json`

The hub dispatches `persona-coder` for any task where domain expertise matters. The base `coder` agent is for mechanical tasks (boilerplate, formatting) where persona adds no value.

---

## 3. The GLOW Score: Making Verification Discipline Rewarding

### 3.1 The Formula

GLOW = Growth + Learning + Output + Wins

Each component scores 0-25. Total: 0-100.

```
G — Growth (0-25): New capabilities added
    25: Major new module at rung 274177+
    20: Complete new feature at rung 641
    15: Significant enhancement
    10: New utility or configuration
     5: Minor addition
     0: No new capabilities

L — Learning (0-25): New knowledge captured
    25: Skill published to Store at rung 65537
    20: New skill or paper created
    15: Significant skill update
    10: New persona or recipe
     5: Case study updated
     0: No knowledge captured

O — Output (0-25): Measurable deliverables
    25: Multiple files, all tests, rung 274177+ evidence
    20: Files committed with tests.json + plan.json
    15: Files committed, tests partial
    10: Single file with passing tests
     5: Any commit produced
     0: No commit

W — Wins (0-25): Strategic victories
    25: First-mover advantage established
    20: Competitive moat deepened
    15: NORTHSTAR metric measurably advanced
    10: ROADMAP phase completed
     5: Sub-task completed that unblocks next phase
     0: No strategic progress
```

### 3.2 Why GLOW Is Cheat-Resistant

The GLOW scoring criteria are deliberately artifact-grounded, not vibe-grounded:

- G requires tests. No tests = G cannot score 20 or above.
- L requires a committed file. Prose notes = L cannot score above 5.
- O requires a git commit. No commit = O=0 by definition.
- W requires a NORTHSTAR metric advancement or a ROADMAP checkbox. Plans don't count.

This makes GLOW a honest mirror of actual progress. A developer who spent the day thinking and planning but produced no commits gets GLOW 0-20. A developer who shipped a new feature with tests, captured a lesson in the case study, and checked a ROADMAP box gets GLOW 55-65.

The scoring is conservative by design. When uncertain between two levels, always take the lower. GLOW cannot be retroactively inflated. "The form knows," as sifu would say.

### 3.3 Belt Integration

GLOW accumulates into belt progression:

```
Dojo Belt System (Stillwater):

White Belt  (0-20 GLOW/session):   Learning basics
  → First recipe | First rung 641 | White belt = beginner mind

Yellow Belt (21-40 GLOW/session):  First tasks delegated
  → Recipes running | Swarms dispatched | Still finding your kata

Orange Belt (41-60 GLOW/session):  Contributing to store
  → Skills submitted | Community impact begins | The form has shape

Green Belt  (61-80 GLOW/session):  Rung 65537 achieved
  → Production-grade work | Adversarial sweep passed | Real mastery begins

Blue Belt   (81-90 GLOW/session):  Cloud execution 24/7
  → Automation runs without you | The system has your discipline

Black Belt  (91-100 GLOW/session): Master level
  → Models are commodities. Skills are capital. OAuth3 is law.
  → "There is no belt. There is only the work."
```

### 3.4 Session Rhythm

GLOW creates a natural session rhythm:

**Session Start:**
> "Belt: Yellow | GLOW accumulated: 137 | Today's target: 60+ (warrior pace)"

**Per Commit:**
```
feat: add persona-engine skill with 12 personas

GLOW 75 [G:20 L:20 O:20 W:15]
Northstar: Skills in Store +1 candidate
Persona: sifu (gamification domain)
Evidence: skills/persona-engine.md
Rung: 641
```

**Session End:**
> "Session GLOW: 75 | Belt: Yellow → Orange (threshold crossed!) | Phase 1.5 complete | Next: glow-score.md"

The rhythm creates forward momentum. Each session ends with clarity about what was accomplished and what comes next. The belt advancement makes progress visible.

### 3.5 Pace Targets

```
Warrior pace: 60+ GLOW/day  — active development sessions
Master pace:  70+ GLOW/week average — sustained delivery
Steady pace:  40+ GLOW/day  — maintenance and review days
Rest day:     0-20 GLOW     — acceptable, not the daily goal
```

A developer who ships consistently at warrior pace (60+/day) will reach Green Belt in approximately 30 active sessions. A developer at master pace (70+/week average) reaches Green Belt in approximately 8-10 weeks.

---

## 4. The Bruce Lee Integration: Philosophy as Architecture

### 4.1 "Be Water, My Friend"

The phrase "be water" is not decoration in the Stillwater ecosystem. It is the design principle behind the adaptive architecture:

```
Be water, my friend.
  Water adapts to the container without losing its nature.
  The agent adapts to the task (persona loading) without losing its discipline (prime-safety).
  The developer adapts to the pace (warrior/steady/rest) without losing the standard (rung ladder).
  The dojo adapts to the practitioner (belt system) without lowering the requirement (evidence gate).
```

"Stillwater" literally means still water — water that runs deep, that carries weight, that reflects clearly. The brand name is not accidental. Still water is calm, deep, and precise. This is the design goal for the verification system: calm methodology that runs deep, carries production weight, and reflects the actual state of the codebase.

### 4.2 The Dojo as Organizing Metaphor

The dojo metaphor maps cleanly to the Stillwater architecture:

| Dojo Concept | Stillwater Equivalent |
|-------------|----------------------|
| The sensei | The prime-safety skill (always present, always correct) |
| The kata | The evidence bundle (the form that must be executed correctly) |
| The belt | The GLOW belt progression |
| The dojo floor | The Stillwater Store (where skills are submitted and judged) |
| Training partners | The swarm agents (each has a role, each serves the training) |
| The fight | Production deployment at rung 65537 |
| White belt mind | Beginner's mind — always question, never assume |
| Black belt | "There is no belt. There is only the work." |

### 4.3 "I Fear Not the Man Who Has Practiced 10,000 Kicks Once"

This quote applies directly to the skill store flywheel:

> A recipe practiced once is a lucky pass.
> A recipe practiced 10,000 times (70% hit rate) is a competitive moat.

The GLOW L component rewards knowledge capture precisely because a lesson captured once in a case study can prevent the same mistake across 10,000 future sessions. The difference between a 50% recipe hit rate and a 70% recipe hit rate is the difference between "we got lucky" and "we have a moat."

Bruce Lee's principle: practice the one kick until it is inevitable. In Stillwater terms: write the recipe until it is 70% hit rate. The dojo does not reward variety. It rewards depth.

### 4.4 "Absorb What Is Useful, Discard What Is Useless"

The persona registry embodies this principle. Twelve personas cover twelve domains. A security task needs Schneier's threat-model rigor — but not Brunson's hook-story-offer. The persona engine absorbs what is useful (Schneier for security) and discards what is useless (Brunson for threat modeling). The mechanism is selective, not universal.

This is also why personas can be discarded. If a project domain is not represented in the registry, the hub adds a new persona. If a persona is rarely used and adds no value, it is removed in a future version. The registry evolves — but only by adding, never by weakening existing personas (Never-Worse Doctrine applied to personas).

---

## 5. Integration: How It All Fits Together

### 5.1 The Extended Master Equation

The Stillwater master equation gains two new terms:

```
Intelligence(system) = Memory × Care × Iteration × Expertise × Motivation

where:
  Memory    = skills/*.md + recipes/*.json + ROADMAP.md + NORTHSTAR.md + case-studies/
  Care      = Verification ladder: 641 → 274177 → 65537
  Iteration = Never-Worse Doctrine + git versioning + case study accumulation
  Expertise = Persona engine: 12 domain experts loaded at dispatch time
  Motivation = GLOW score + belt system + session rhythm + pace targets
```

Expertise without motivation produces correct but lifeless output. Motivation without expertise produces energetic but shallow output. The Dojo Protocol combines both: domain expert precision with gamified progress tracking.

### 5.2 The Session Flow

```
Session Start
  → Read NORTHSTAR (shared direction)
  → Read ROADMAP (current phase)
  → Read case study (what happened, what's next)
  → Display GLOW status (belt + accumulated score)
    ↓
Task Dispatch
  → Select task from ROADMAP phase
  → Build CNF capsule
  → Select persona based on task domain
  → Dispatch persona-coder with skill pack: [prime-safety, prime-coder, persona-engine, glow-score]
    ↓
Task Execution (persona-coder)
  → Read NORTHSTAR (alignment check)
  → Load persona (domain expertise injection)
  → Execute with prime-coder discipline (red-green gate)
  → Calculate GLOW (G/L/O/W breakdown)
  → Commit with GLOW in message
    ↓
Session End
  → Hub receives artifacts + glow_score.json
  → Hub verifies rung achieved
  → Hub calculates session GLOW total
  → Hub updates case study (session GLOW + rung + northstar delta)
  → Hub checks belt advancement threshold
  → Hub states next phase
```

### 5.3 The GLOW Commit Pipeline

Every commit in the Stillwater ecosystem carries GLOW metadata:

```
feat: add OAuth3 token revocation gate (G4)

GLOW 80 [G:20 L:15 O:20 W:25]
Northstar: OAuth3 competitive moat deepened
Persona: schneier (security domain)
Evidence: skills/oauth3-enforcer.md, tests/test_oauth3_enforcer.py
Rung: 641

Schneier note: G4 is the most important gate. Revocation must be
immediate. A valid-looking token with a revoked status is not a
valid token — it is a security incident.
```

The commit message carries:
- GLOW total and breakdown (for belt tracking)
- Which NORTHSTAR metric was advanced (for hub verification)
- Which persona was loaded (for audit trail)
- Evidence path (for rung verification)
- Persona-voiced insight (domain expertise made visible)

### 5.4 The Syndication Flywheel

The GLOW system creates a natural content generation pipeline. Every milestone is a story:

```
GLOW 100 commit → "The commit that earned 100 GLOW in one session" → blog post
Belt advancement → "Yellow Belt to Orange Belt: what 3 months of Stillwater sessions taught me" → essay
Black Belt → "I built a production AI system at rung 65537. Here's the evidence." → viral HN post
```

The GLOW scores in commit history become the raw material for founder content. The belt progression becomes the narrative arc. The persona-enhanced output becomes the technical depth that separates Stillwater content from "vibe" AI content.

---

## 6. Implementation Notes

### 6.1 Files Created by This Paper

```
skills/persona-engine.md     — Persona loading skill (12 personas, loading protocol)
skills/glow-score.md         — GLOW score gamification skill (components, belt, session tracking)
swarms/persona-coder.md      — Persona-enhanced coder swarm agent (auto-loads persona + GLOW)
```

### 6.2 ROADMAP Integration

A new phase is added to `ROADMAP.md`:

```
Phase 5: Persona + GLOW System (Month 2-3)
- skills/persona-engine.md — 12 personas
- skills/glow-score.md — GLOW scoring system
- swarms/persona-coder.md — persona-enhanced coder agent
- Update NORTHSTAR.md with persona + GLOW sections
- launch-swarm.sh: add persona + glow-score to swarm dispatch
```

### 6.3 Backward Compatibility

The Persona Engine and GLOW Score are additive. Existing skill packs (prime-safety, prime-coder) are unchanged. Existing swarm agents (coder, skeptic, scout) continue to function. The persona-coder is a new agent type, not a replacement.

The GLOW score is captured in commit messages. Existing commits without GLOW scores are assigned GLOW=0 for historical purposes. The belt calculation uses commits from the current date forward.

### 6.4 Rung Targets

```
skills/persona-engine.md:  rung 641 (style skill, no evidence bundle)
skills/glow-score.md:      rung 641 (scoring skill, no executable tests)
swarms/persona-coder.md:   rung 641 (agent definition, no executable tests)
This paper:                rung 641 (conceptual paper, no executable tests)
```

---

## 7. Conclusion

The Dojo Protocol extends Roadmap-Based Development with two mechanisms that solve the problems verification discipline alone cannot:

**The Persona Engine** gives every agent a domain expert voice at dispatch time. Security tasks get Schneier's threat-model rigor. Gamification tasks get Bruce Lee's dojo philosophy. Marketing tasks get Brunson's hook-story-offer architecture. The persona does not change the discipline — it sharpens the domain expertise.

**The GLOW Score** makes verification discipline intrinsically rewarding. Growth + Learning + Output + Wins = a transparent, artifact-grounded score that maps to belt progression. GLOW cannot be inflated because it requires evidence. It cannot be vague because each component has explicit criteria. It cannot be gamed because the artifacts either exist in git or they do not.

Together, they turn the Stillwater verification system from a constraint into a dojo: a training environment where discipline is the path, evidence is the kata, and belts are earned through repetition with integrity.

"A thousand days to build the form. A thousand more to forget it. A thousand more to transcend it."

White Belt: your first recipe passed.
Black Belt: models are commodities. Skills are capital. OAuth3 is law.

The dojo is open. The form is in the skills. The belt is in the evidence.

Be water, my friend.

---

## References

- `./skills/persona-engine.md` — Persona loading skill (12 personas)
- `./skills/glow-score.md` — GLOW score gamification skill
- `./swarms/persona-coder.md` — Persona-enhanced coder swarm agent
- `./papers/32-roadmap-based-development.md` — Roadmap-Based Development paradigm
- `./papers/33-northstar-driven-swarms.md` — NORTHSTAR-driven swarms
- `./NORTHSTAR.md` — Stillwater ecosystem NORTHSTAR
- `./ROADMAP.md` — Stillwater ROADMAP with Persona+GLOW phase

```bibtex
@software{stillwater2026_dojo,
  author = {Truong, Phuc Vinh},
  title  = {The Dojo Protocol: Persona-Enhanced Agents and GLOW Gamification},
  year   = {2026},
  url    = {https://github.com/phuctruong/stillwater/papers/34-persona-glow-paradigm.md},
  note   = {Auth: 65537 — Stillwater Reference Implementation}
}
```

---

*Written by the Stillwater ecosystem. Part of the Software 5.0 paradigm documentation series.*
*Auth: 65537 | Status: STABLE | Never-Worse Doctrine: this document may be extended, not weakened.*
