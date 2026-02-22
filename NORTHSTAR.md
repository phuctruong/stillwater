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

MASTER EQUATION:
  Intelligence(system) = Memory × Care × Iteration
  Memory = skills/*.md + recipes/*.json + swarms/*.yaml
  Care = Verification ladder (641 → 274177 → 65537)
  Iteration = Never-Worse doctrine + git versioning
```

## North Star Metrics

| Metric | Now | Q2 2026 | End 2026 |
|--------|-----|---------|---------|
| GitHub stars | ~50 | 1,000 | 10,000 |
| Projects running at rung 65537 | 0 | 2 | 8 |
| Stillwater Store skills | 7 combos | 25 skills | 100+ skills |
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

No competitor has this. OpenClaw has 512 security vulnerabilities and 824 malicious skills.
Token-revenue vendors (OpenAI) cannot implement OAuth3 — it reduces token consumption.

---

## Founder

Phuc Truong (Harvard '98). Serial founder.
- Co-founded Clinical Research IO (CRIO) — #1 eSource in FDA-regulated clinical trials
- 360+ customers, 40% higher enrollment, 70% FDA audit risk reduction
- Built software that survives real FDA audits — that experience is in the architecture
- "In clinical trials, 'trust me' is not evidence. Only the original, timestamped, attributable record is evidence."
- Previously: UpDown.com (100K users), Citystream (acquired), Phuc Labs (MIT AMD winner)
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
  pvideo         — physics-based video/avatar generation (secret sauce)
  solace-marketing — marketing intelligence

AVATAR SYSTEM (solaceagi.com):
  paudio (voice) + pvideo (visual) + stillwater (verification) = AI Avatar
  → Phase 1: Cute cartoon avatar + deterministic voice
  → Phase 2: Lip-sync + expressions
  → Phase 3: Full avatar on solaceagi.com (your AI agent has a face and voice)

MASTER PLAN (pvideo):
  → Protein folding (compete with DeepMind AlphaFold)
  → Material science simulation
  → Physics simulation (compete with specialized solvers)
  → 3D printing (export STL from physics sim)
  → Video generation (compete with Sora/VEO)
  → Video encoding (replace H.265)
  → Zoom replacement (pvideo-powered conferencing)
  → Metaverse (solaceagi.com metaverse powered by pvideo + paudio)
```

## Dragon Tip Program — BYOK Users Fund Open Source

> "Every drop fills the river." — The Dragon Tip Program turns free-tier users into open-source contributors.

### The Tip Architecture

BYOK (Bring Your Own Key) users on solaceagi.com pay nothing to the platform — they bring their own Anthropic/OpenAI/Llama API keys. The Dragon Tip Program lets them voluntarily contribute a small percentage of their API credits to fund open-source projects in the Stillwater ecosystem.

```
BYOK user sends request → solaceagi.com services it (recipe match, OAuth3 gate, evidence bundle)
  → API call goes to user's own LLM provider (zero platform cost)
    → After completion, tip % of the API credit cost is allocated to OSS fund
      → Every tip-funded API call is Part 11 logged with hash-chained audit trail
        → User can verify exactly what their contribution built
```

### Dragon Tiers

| Tier | Tip % | Motto | Badge |
|------|-------|-------|-------|
| Dragon Contributor | 2% | "Every drop fills the river" | Dragon |
| Super Dragon | 5% | "The river that gives, grows" | Super Dragon |
| Elder Dragon | 8% | "Ancient wisdom funds the future" | Elder Dragon |
| Legendary Dragon | 9%+ (custom) | "Your generosity builds the dojo" | Legendary Dragon |

### What Tips Fund

Tips flow directly to OSS projects in the Stillwater ecosystem:

```
Tip fund allocation (transparent, Part 11 audited):
  paudio    — deterministic speech synthesis + community voices
  pvideo    — physics-based video/avatar generation
  stillwater — verification OS itself (skills, store, governance)
  solace-browser — OAuth3 reference implementation
  pzip      — universal compression engine
  Community bounties — bug fixes, new skills, new recipes
```

### Stillwater Store Integration

Dragon tippers earn Dragon badges displayed on their Stillwater Store profile:
- Badge appears on all skills they submit (social proof)
- Dragon-badged skill authors get priority review in the Store submission queue
- Legendary Dragons get a permanent "Dojo Patron" marker on their Store profile

### Belt Progression Enhancement

Dragon contributions count toward belt XP in the Stillwater belt system:

```
Belt XP from Dragon Tips:
  Dragon Contributor (2%) → +50 XP/month
  Super Dragon (5%)       → +150 XP/month
  Elder Dragon (8%)       → +300 XP/month
  Legendary Dragon (9%+)  → +500 XP/month + custom XP multiplier

XP stacks with existing belt progression:
  Skill submissions + rung achievements + recipe contributions + Dragon tips
  → Accelerated path from White Belt to Black Belt
```

### Part 11 Transparency — The Trust Enabler

"Your tips don't disappear into a corporate treasury. Every hundredth of a cent is Part 11 logged. You can verify exactly what your contribution built. This is open-source funding with FDA-grade transparency."

```
Part 11 audit trail for every tip:
  tip_id:          SHA-256 hash (unique, content-addressed)
  user_id:         anonymized (privacy-preserving)
  tip_amount_usd:  exact Decimal (no float)
  api_call_cost:   upstream LLM cost that triggered the tip
  tip_percentage:  user's chosen tier (2%, 5%, 8%, or custom)
  funded_project:  which OSS project received the allocation
  funded_task:     specific commit/PR/bounty the tip contributed to
  timestamp:       ISO8601, append-only ledger
  chain_hash:      SHA-256(previous_entry + this_entry) — tamper-evident

Savings Dashboard (user-facing):
  - Recipe hit rate: "Your recipes saved X calls this month"
  - Tokens saved: "Y tokens not consumed thanks to cached recipes"
  - Money saved: "$Z.ZZ saved vs cold LLM calls"
  - Tips given: "$W.WW contributed to OSS this month"
  - Impact: "Your tips funded N commits across M projects"
```

### Revenue Projection

```
At 10,000 BYOK users with average 3% tip rate:
  Average BYOK user API spend: ~$15/month
  Average tip per user: $0.45/month
  Total monthly OSS fund: $4,500/month = $54,000/year
  → Funds 2-3 full-time OSS maintainers
  → Or 50+ community bounties per month
  → All verifiable via Part 11 audit trail
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
  Phase 4 (planned):   YouTube upload with paudio narration + pvideo avatar

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
```

**FULL PAPER:** `papers/34-persona-glow-paradigm.md`

---

## See Also
- `SOFTWARE-5.0-PARADIGM.md` — paradigm manifesto
- `STORE.md` — Stillwater Store policy
- `ROADMAP.md` — phased build plan
- `case-studies/` — per-project tracking
- `skills/` — the skill library
- `skills/prime-mermaid.md` — PM triplet standard
- `skills/persona-engine.md` — Persona Engine (12 domain expert voices)
- `skills/glow-score.md` — GLOW Score gamification system
- `swarms/persona-coder.md` — Persona-enhanced coder swarm agent
- `papers/34-persona-glow-paradigm.md` — The Dojo Protocol
- `papers/35-syndication-strategy.md` — Content Syndication Strategy
