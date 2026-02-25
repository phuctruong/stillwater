# Reverse-Path Engineering: Solving the Stillwater Northstar from the End

**Paper ID:** reverse-paths
**Date:** 2026-02-21
**Status:** STABLE
**Author:** Phuc Truong (with Claude Sonnet 4.6)
**Tags:** northstar, strategy, reverse-engineering, planning

---

## The Paradigm

Traditional planning asks: "What are the next 3 steps?"
Reverse-path engineering asks: "What are the LAST 3 steps before victory?"

The insight is borrowed from maze-solving algorithms. Solving a maze from the start is prone to dead ends. Solving from the exit backward finds the critical path immediately, because every reverse step is a necessary precondition — not a hopeful guess.

Applied to Northstar planning:

1. Define the summit state with precision (measurable, not vague)
2. Work backward: what must be true immediately before the summit is reached?
3. Continue backward until you reach current state
4. The chain is your critical path
5. The first step in the chain (closest to current state) is your first action

This method filters out wishful thinking. You cannot reverse-engineer toward a vague goal. You must define the summit precisely enough to ask "what must be true one step before this?" If you cannot answer that, your Northstar is not yet concrete enough to execute against.

---

## Current State Snapshot (2026-02-21)

Before reverse engineering begins, the current state must be established precisely:

| Project | Belt | Rung | Key Facts |
|---------|------|------|-----------|
| stillwater | Orange | 65537 CI | 445 tests, 15+ skills, 19 swarm types, 50 personas, CI badge live |
| solace-browser | Orange | 274177 | 2,441 tests, OAuth3 core complete, 5 platforms, machine access layer done |
| solaceagi | Orange | 641 | 955 tests, FastAPI + Stripe + LLM proxy + cloud twin all built |
| solace-cli | White | — | ROADMAP written, no code yet |
| GitHub stars | — | — | ~50 stars |
| Paying users | — | — | 0 |
| Recipe hit rate | — | — | 0% (no production traffic) |
| External OAuth3 adopters | — | — | 0 |
| Community contributors | — | — | 1 (Phuc) |

---

## Northstar 1: 10,000 GitHub Stars by End of 2026

### Summit State

The stillwater GitHub repository has 10,000 stars. GitHub's trending algorithm surfaces it weekly. New stars arrive at 50+/day without active promotion. The repository is cited in HN comments and dev blog posts as the reference for AI agent verification.

### The Last 3 Steps

| Step | State | Precondition |
|------|-------|--------------|
| Step -1 | Viral loop active: each 100 new stars generates ~120 new viewers who then star | Requires: repo demonstrates something most developers want but cannot find elsewhere; README converts at >2% |
| Step -2 | Repository crosses 3,000 stars — the GitHub trending critical mass threshold | Requires: at least one major distribution event (HN front page, influential developer tweet, or tech newsletter feature) that brings 500+ new visitors in 48 hours |
| Step -3 | Repository is featured in a high-trust channel: HN "Show HN" reaching front page, or a developer with >50K followers shares it with a concrete claim | Requires: a specific, falsifiable, counterintuitive claim with working code evidence (not a promise) |

### Backward Chain

| Chain Position | State | Action Needed |
|---------------|-------|---------------|
| -3 (trigger event) | HN front page or influencer share | Ship something concrete that can be demonstrated in 60 seconds: "Watch an AI agent complete a Gmail task with OAuth3 consent and a verifiable evidence bundle — no trust required" |
| -4 (demo ready) | Working end-to-end demo of OAuth3 + evidence bundle | solace-browser BUILD 12 (Tunnel Engine) complete; solaceagi.com live with free tier; demo video recorded |
| -5 (platform live) | solaceagi.com publicly accessible free tier | Phase 4 (launch: billing tiers + rate limits + GDPR) complete in solaceagi |
| -6 (content engine) | Papers syndicated to LinkedIn, Substack, HN, Reddit | Content syndication pipeline from papers/ active; papers 32-40 distributed |
| -7 (evidence of claims) | Concrete benchmark: "70% recipe hit rate on Gmail tasks" | Minimum 100 production Gmail tasks executed with logged hit rates |
| -8 (early adopters) | 10-50 developers using stillwater locally, submitting issues and stars | OSS README explains value in 30 seconds; quick-start works in <5 minutes; first non-Phuc contributor |
| -9 (today) | ~50 stars, 1 contributor | Ship BUILD 12 (Tunnel Engine at rung 65537) → launch solaceagi.com → execute content syndication |

### Critical Path

The critical path is: **BUILD 12 → solaceagi launch → end-to-end demo → HN "Show HN" post**

The bottleneck is not code — it is having something publicly accessible that a developer can experience in under 60 seconds. All the code exists. The gap is: no one can try it yet.

### Parallelizable Work

- Content syndication (papers 32-40 to LinkedIn/Substack) can start immediately, independent of BUILD 12
- GitHub README rewrite for 30-second value prop can start immediately
- Substack "Stillwater Dispatch" newsletter setup can start immediately
- HN "Show HN" post draft can be written now, held until solaceagi.com is live

### Gaps and Blockers

- BUILD 12 (Tunnel Engine, rung 65537) is the single most critical blocker — without it, no public demo
- No quick-start guide for local stillwater installation exists yet
- No Substack newsletter yet (0 subscribers)
- No YouTube channel with demo video

> **First Action:** Write and publish the "Show HN" draft post NOW (before the platform is live) so it is refined and ready. Simultaneously, assign BUILD 12 (Tunnel Engine) as the immediate next swarm dispatch.

---

## Northstar 2: 5,000 Paying Users by End of 2026

### Summit State

solaceagi.com has a growing subscriber base. Recipe hit rate across the ecosystem is above 70%, meaning per-task cost is low enough to maintain margin at scale. The billing infrastructure is handling upgrades, downgrades, and churn automatically via Stripe.

### The Last 3 Steps

| Step | State | Precondition |
|------|-------|--------------|
| Step -1 | Organic growth sustains 500+ new paying users/month without paid acquisition | Requires: word-of-mouth loop where existing users bring colleagues; store skill submissions generating backlinks |
| Step -2 | 1,000 paying users reached; Stripe MRR dashboard shows consistent weekly growth curve | Requires: a clear conversion funnel from free tier → Managed LLM or Pro (the free tier must deliver enough value that 5-10% upgrade voluntarily) |
| Step -3 | Free tier has 5,000+ registered users who have completed at least one task | Requires: solaceagi.com publicly accessible, free tier frictionless (no credit card), and at least one distribution event bringing new signups |

### Backward Chain

| Chain Position | State | Action Needed |
|---------------|-------|---------------|
| -3 (free signup) | 5,000 free users | HN/Product Hunt launch with working demo; "free forever" BYOK tier clearly explained in landing page |
| -4 (landing page converts) | Landing page converts visitors to free signups | Hook/Story/Offer treatment applied to homepage; demo video above the fold; one-click Google sign-in |
| -5 (free tier works) | Free tier users complete at least one task successfully | Recipe hit rate >0% in production; at least LinkedIn or Gmail recipe working end-to-end via cloud twin |
| -6 (cloud twin live) | Cloud twin executing recipes reliably | Phase 2 (Cloud Twin) in solaceagi deployed and running; tunnel server at tunnel.solaceagi.com live |
| -7 (billing operational) | Stripe billing handles upgrades/downgrades automatically | Phase 4 (billing tiers + rate limits + GDPR) complete; Stripe webhook handling churn and upgrades |
| -8 (Managed LLM working) | Users can run tasks without their own API key | LLM proxy routing upstream providers; tier check enforced; billing by token cost with exact Decimal arithmetic |
| -9 (today) | 0 paying users | Deploy solaceagi.com Phase 4; establish public URL; begin content distribution |

### Critical Path

**Phase 4 (solaceagi launch) → public URL → free tier onboarding → first 100 users → optimize conversion → scale content**

The conversion funnel must be designed before the launch, not after. The current architecture supports everything; what is missing is a deployed, publicly accessible instance and a clear onboarding flow.

### Parallelizable Work

- Pricing page A/B copy can be written now
- BYOK onboarding flow UX design is independent of infrastructure
- Substack "Stillwater Dispatch" audience building can start before platform launch

### Gaps and Blockers

- solaceagi.com is NOT yet publicly accessible (Phase 3.5 and 4 not complete)
- No onboarding email sequence exists
- Recipe hit rate at 0% — free tier users will encounter cold-start failures
- Tunnel server (`tunnel.solaceagi.com`) not yet deployed

> **First Action:** Deploy solaceagi.com to a public URL with Phase 0-3 (what is already built). Gate behind a waitlist if Phase 4 is not ready. Start collecting emails NOW. The waitlist itself is marketing.

---

## Northstar 3: 8 Projects at Rung 65537

### Summit State

Eight distinct projects or modules in the Stillwater ecosystem have achieved rung 65537: full production confidence including adversarial testing, security gate (semgrep + bandit clean), behavioral hash with 3-seed consensus, and 30 continuous days of CI green. Each has a deployed GitHub Actions badge. The verification ladder is self-sustaining — new contributions must pass rung 274177 to merge.

### The Last 3 Steps

| Step | State | Precondition |
|------|-------|--------------|
| Step -1 | 8th project achieves 30 continuous CI-green days and rung 65537 seal | Requires: all 7 prior projects already at 65537; adversarial test suite passing; no regressions for 30 days |
| Step -2 | 7 projects at 65537; 8th is at 274177 with 30-day CI run in progress | Requires: each project has its own CI workflow (not shared), independent behavioral hash, and domain-specific adversarial tests |
| Step -3 | Projects 5-7 are at rung 274177; each has a plan to reach 65537 within 90 days | Requires: rung_validator.py deployed in each project; security gate configured; CI running daily |

### Current Rung Status and Gaps

| Project | Current Rung | Gap to 65537 |
|---------|-------------|--------------|
| stillwater itself | 65537 CI badge deployed | 30-day continuous green needed to seal |
| solace-browser tunnel engine | 65537 (planned, BUILD 12) | BUILD 12 not yet complete |
| solace-browser machine access | 274177 | Security adversarial tests needed |
| solaceagi tunnel server | 65537 (planned) | Server not deployed |
| solaceagi LLM proxy | 641 | Stability sweep + adversarial tests needed |
| solace-cli OAuth3 vault | White (no code) | Full implementation required first |
| solaceagi billing | 641 | Float-in-billing gate audit needed |
| solaceagi cloud twin | 641 | Seed sweep + replay tests needed |

### Backward Chain

| Chain Position | State | Action Needed |
|---------------|-------|---------------|
| -3 (projects 5-7 at 274177) | solaceagi LLM proxy + billing + cloud twin at 274177 | Seed sweep (3 seeds) + replay tests + null edge sweep for each |
| -4 (solace-cli has code) | solace-cli OAuth3 vault at 641 minimum | Launch solace-cli OAuth3 commands swarm; implement vault at rung 641 |
| -5 (solace-browser BUILD 12 done) | Tunnel engine at 65537 | BUILD 12 complete; TLS + OAuth3-pinned WebSocket + adversarial traffic tests |
| -6 (security gates per project) | Each project has semgrep + bandit CI configured | Copy stillwater's verify.yml pattern into each project's CI |
| -7 (stillwater sealed) | stillwater 30-day continuous CI green | No regressions for 30 days post-Phase 4 |
| -8 (today) | 1 project at 65537 CI (not yet 30-day sealed), 1 at 274177, 6 at 641 or below | Ship BUILD 12; configure CI for solaceagi; launch solace-cli |

### Critical Path

**BUILD 12 (tunnel, 65537) → solaceagi CI setup (274177 → 65537) → solace-cli code (641 → 274177) → 30-day seals for all**

The rung ladder is a quality discipline, not a one-time gate. The 30-day continuous green requirement is the hardest part — it requires stable, maintained code with no regressions over time.

### Parallelizable Work

- Setting up CI workflows for solaceagi and solace-browser is independent of their rung level
- Behavioral hash generation can be set up in all projects simultaneously
- The `rung_validator.py` from stillwater Store SDK can be reused in all projects

### Gaps and Blockers

- solace-cli has zero code — it cannot achieve any rung until the OAuth3 vault is built
- No automated adversarial test suite pattern exists yet (only manual security review done so far)
- The "30-day continuous green" requirement means the clock cannot start until regressions are eliminated

> **First Action:** Add CI workflows to solaceagi and solace-browser TODAY (copy stillwater's verify.yml). Start the 30-day clock running even at rung 641. Upgrade rung level while CI is already running — this saves 30 days of clock time.

---

## Northstar 4: 80% Recipe Hit Rate

### Summit State

80% of tasks submitted to solaceagi.com are served from cached recipe replay rather than cold LLM calls. The recipe library covers all major task categories on the 10 most popular platforms.

### The Last 3 Steps

| Step | State | Precondition |
|------|-------|--------------|
| Step -1 | 80% hit rate achieved and sustained across 10,000+ tasks logged | Requires: recipe library covers the 20% of task types that represent 80% of user demand (Pareto distribution holds); recipe matching logic has low false-negative rate |
| Step -2 | Hit rate at 65-75%; gap analysis shows which task categories are missing recipes | Requires: usage analytics dashboard showing hit/miss by task type; community submitting recipes for gap categories |
| Step -3 | Hit rate at 50% (Q2 target); at least 50 recipes across 5 platforms deployed | Requires: LinkedIn (6 recipes), Gmail (6 recipes), Reddit (4), Notion (4), HackerNews (4), plus 6 more recipe categories covering 50% of actual user demand |

### Current Recipe Inventory vs. 80% Target

| Platform | Recipes Built | Estimated Task Coverage |
|----------|-------------|------------------------|
| LinkedIn | 6 | ~15% of LinkedIn automation demand |
| Gmail | 6 | ~20% of Gmail automation demand |
| Reddit | ~4 | ~10% of Reddit demand |
| Notion | ~4 | ~8% of Notion demand |
| HackerNews | ~4 | ~5% of HN demand |
| Substack | ~4 | ~10% of Substack demand |
| Twitter/X | ~4 | ~8% of Twitter demand |
| **Total** | **~32 recipes** | **~0% hit rate (no production traffic)** |

### Backward Chain

| Chain Position | State | Action Needed |
|---------------|-------|---------------|
| -3 (50% hit rate, 50 recipes) | 50 recipes live, production traffic routed | Expand recipe library with community submissions; add 20 new recipes covering top missing task types |
| -4 (recipe matching tuned) | Recipe matching algorithm has <10% false-negative rate | Implement fuzzy intent matching (task description → recipe selector); A/B test matching against cold LLM |
| -5 (production analytics) | Hit rate dashboard showing miss categories | GA4 analytics (already started in solaceagi) + recipe hit/miss logging per task type |
| -6 (first production traffic) | solaceagi.com has 100+ real tasks completed | Platform publicly accessible; first 100 users onboarded and completing tasks |
| -7 (recipes in platform) | All 32 existing recipes loaded into solaceagi recipe store | recipes/*.json from solace-browser loaded into solaceagi recipe registry and served via cloud twin |
| -8 (today) | 32 recipes built but 0 production traffic; hit rate unmeasurable | Deploy solaceagi; load existing recipes; instrument hit rate tracking |

### Critical Path

**Deploy solaceagi → load 32 existing recipes → instrument hit rate → analyze gaps → expand library → iterate to 80%**

The 80% target cannot be reached without production data. The recipes exist but are not yet serving real requests. Every day without a deployed platform is a day without hit rate data — and without data, the gap to 80% is invisible.

### Parallelizable Work

- Recipe hit rate instrumentation code can be written before the platform launches
- Community skill submission form for the Stillwater Store can be opened now (before 80% target)
- Recipe gap analysis framework (which task types are most common) can be designed from first principles

### Gaps and Blockers

- No production traffic means hit rate is literally unmeasurable today
- Recipe matching algorithm has not been implemented — recipes are stored but no matching logic routes incoming tasks to them
- The Stillwater Store submission flow for community recipes is not yet public

> **First Action:** Write the recipe matching algorithm (task description → best recipe selector with confidence score). This is the core technical component that enables hit rate. Build it before the platform launches so the first user generates a measured hit rate rather than always falling through to cold LLM.

---

## Northstar 5: OAuth3 Adopted by an External Platform

### Summit State

At least one external AI agent platform — not built by Phuc — has implemented OAuth3 as its authorization layer. The implementation references the solace-browser OAuth3 whitepaper, uses the AgencyToken schema, and respects the G1-G4 gate contract. This external adoption marks OAuth3 as a de facto standard, not a single-vendor protocol.

### The Last 3 Steps

| Step | State | Precondition |
|------|-------|--------------|
| Step -1 | External platform ships OAuth3 support and announces it publicly | Requires: the external platform's engineering team has reviewed the spec, found it implementable, and prioritized it; Phuc or the community has answered their implementation questions |
| Step -2 | External platform's engineering team is actively implementing OAuth3 | Requires: the spec is clear enough that a team unfamiliar with Stillwater can implement it without asking Phuc; reference test suite allows them to verify their implementation |
| Step -3 | An external developer or team expresses serious interest in implementing OAuth3 | Requires: the spec is publicly available at a stable URL; OAuth3 is mentioned in at least one high-traffic developer forum (HN, r/LocalLLaMA, AI agent Discord servers) |

### Backward Chain

| Chain Position | State | Action Needed |
|---------------|-------|---------------|
| -3 (external interest) | Developer publicly asks about OAuth3 adoption | papers/oauth3-spec-v0.1.md syndicated to HN, r/LocalLLaMA, AI safety forums; presented as "the missing auth standard for AI agents" |
| -4 (spec is complete enough) | OAuth3 spec v1.0 published with reference implementation + conformance test suite | Upgrade from v0.1 (794 lines, 5 sections) to v1.0 with: implementation guide, error codes, conformance tests, and a reference implementation in Python |
| -5 (reference impl public) | solace-browser oauth3/ module published as standalone pip package | Extract solace-browser's oauth3/ directory into `pip install oauth3-agency`; this makes adoption trivially easy |
| -6 (spec published at stable URL) | oauth3.dev or oauth3.solaceagi.com serves the spec | Register a domain; publish the spec as a static site (GitHub Pages minimum); include Brunson-treated explainer |
| -7 (consent gap documented) | "Existing browser automation tools have no consent model; OAuth3 solves this" is a published, citable claim | papers/oauth3-spec-v0.1.md already exists — syndicate the consent gap analysis |
| -8 (today) | spec exists as a paper; not yet published at a stable URL | Publish oauth3 spec to a dedicated URL; extract oauth3/ as a pip package |

### Critical Path

**Publish spec at stable URL → extract pip package → publish competitive claim (already written) → HN post "OAuth3: consent layer for AI agents" → field adoption inquiries**

The spec and competitive analysis already exist. This Northstar is primarily a distribution and positioning challenge. The technical work is already done. What is missing is: a stable public URL for the spec and a pip-installable reference implementation.

### Parallelizable Work

- GitHub Pages publication of the spec is independent of pip package extraction
- Writing the HN post can happen before the stable URL exists (draft it now, publish when URL is live)
- Reaching out to AI agent framework maintainers (LangChain, AutoGen, crewAI) can happen via GitHub issues before the stable URL is live

### Gaps and Blockers

- No dedicated spec URL (oauth3.dev or similar) — spec lives buried in a GitHub repo's papers/ directory
- OAuth3 pip package does not exist — developers cannot `pip install` the reference implementation
- No conformance test suite — external implementors cannot verify they implemented it correctly

> **First Action:** Publish `papers/oauth3-spec-v0.1.md` to a GitHub Pages site at `phuctruong.github.io/oauth3-spec` today. Add a "Adopt OAuth3" section to the README. Post a link in r/LocalLLaMA with the title "OAuth3: the missing consent layer for AI agents (reference implementation in Python, MIT licensed)".

---

## Northstar 6: Black Belt

### Summit State

Black Belt means: Models = commodities. Skills = capital. OAuth3 = law.

Operationally: at least one production task is running at rung 65537 continuously for 30 days. The Stillwater Store has 100+ skills submitted by community contributors. The ecosystem demonstrates that any developer can build, verify, and share AI agent skills without depending on any single LLM vendor. The dojo is self-sustaining.

### The Last 3 Steps

| Step | State | Precondition |
|------|-------|--------------|
| Step -1 | 100+ community skills in the Store; at least 3 non-Phuc contributors have achieved Green Belt or higher | Requires: Stillwater Store is live, skill submission is frictionless, belt XP is visibly tracked, at least one "celebrity" contributor (OSS-famous developer) has submitted a skill |
| Step -2 | At least one production task has run continuously at rung 65537 for 30 days with zero regressions | Requires: a real user is running a real production task (not a demo) through solaceagi.com at rung 65537; the CI badge reflects this |
| Step -3 | Community has submitted at least 25 skills to the Store; at least one skill was rejected by the rung gate and resubmitted with a fix | Requires: Store is live and publicly accepting submissions; the rung gate is enforced (not just advisory); at least 5 contributors beyond Phuc |

### Backward Chain

| Chain Position | State | Action Needed |
|---------------|-------|---------------|
| -3 (25 community skills) | 25 skills in Store from 5+ contributors | Run a "Skill Sprint" — a public hackathon where developers compete to submit skills; GLOW score leaderboard is visible; first prizes are Pro account credits |
| -4 (Store live and enforcing gates) | Stillwater Store enforces rung gate on submission; Store API returning 422 on sub-641 submissions | src/store/client.py + src/store/rung_validator.py already built; need the Store server at solaceagi.com/stillwater to enforce gates in CI |
| -5 (first external Green Belt) | One non-Phuc developer has achieved rung 65537 on a submission | Requires: documentation shows exactly how to achieve rung 65537; the rung_validator.py is runnable locally before submission |
| -6 (production tasks running) | At least 10 users running recurring tasks via solaceagi.com | Requires: solaceagi.com live with Pro tier; cloud twin executing tasks on schedule; evidence bundles stored for 90 days |
| -7 (belt progression visible) | Belt XP is publicly visible per contributor on Store profile | Store profile page showing belt, GLOW score, submitted skills |
| -8 (Store fully live) | Store is publicly accepting submissions and tracking XP | Store API is live (already built); frontend is live; STORE.md GLOW requirements are published |
| -9 (today) | Store API built; no public submissions yet; belt tracking exists in spec only | Publish STORE.md with GLOW score requirements; add belt badge to Store profile |

### Critical Path

**Deploy Store publicly → publish GLOW score requirements → host first Skill Sprint → accumulate 25 community skills → continuous production traffic → 30-day rung 65537 seal → Black Belt**

The Black Belt is not a technical achievement — it is a cultural one. The skills exist. The code exists. What does not exist yet is a community of practitioners. Building that community requires: public platform, visible progress tracking (GLOW score leaderboard), and a reason to contribute (belt XP + skill recognition).

### Parallelizable Work

- Writing the "Skill Sprint" announcement post is independent of the platform launch
- GLOW score leaderboard design is independent of the Store backend being live
- Belt XP specification for STORE.md can be written and published before the Store is live

### Gaps and Blockers

- 0 community contributors beyond Phuc — the entire dojo has one practitioner
- Belt XP is specified in NORTHSTAR.md but not yet displayed anywhere publicly
- The Skill Sprint concept exists in papers/ but has never been run
- No Discord or community channel exists for Stillwater practitioners

> **First Action:** Open a GitHub Discussions thread on the stillwater repo titled "First Skill Sprint: submit a skill, earn your belt." This costs zero engineering time and starts building community before the platform is fully live.

---

## Cross-Northstar Analysis: The Shared Critical Path

Despite having six distinct Northstar metrics, the reverse chains converge on a small set of shared bottlenecks:

### The Four Universal Blockers

| Blocker | Northstars It Blocks | Resolution |
|---------|---------------------|------------|
| solaceagi.com not publicly accessible | #2 (paying users), #4 (hit rate), #6 (black belt) | Deploy Phase 4; minimum viable public URL with waitlist if needed |
| BUILD 12 (Tunnel Engine, rung 65537) not complete | #1 (stars), #3 (rung 65537), #6 (black belt) | Dispatch as next swarm: `./launch-swarm.sh solace-browser tunnel-engine` |
| No public URL for OAuth3 spec | #5 (external adoption) | GitHub Pages publication: 30 minutes of work |
| Community is 1 person | #6 (black belt), #1 (stars) | GitHub Discussions + content syndication |

### The Minimal First-Week Action Plan

If only four actions are possible in the next 7 days, they are:

1. **Dispatch BUILD 12** (Tunnel Engine) — unblocks 3 Northstars
2. **Deploy solaceagi.com Phase 4 to a public URL** — unblocks 3 Northstars
3. **Publish OAuth3 spec to GitHub Pages** — unblocks external adoption
4. **Open GitHub Discussions "First Skill Sprint"** — starts community building at zero cost

These four actions are parallelizable. None depends on another.

### The Compounding Effect

The Northstars are not independent. Each one feeds the others:

```
BUILD 12 live
  → solaceagi.com public demo
    → HN front page
      → 500+ GitHub stars
        → 10 new contributors
          → 5 Skill Sprint submissions
            → Belt XP visible
              → More contributors
                → Recipe hit rate climbs
                  → COGS drops
                    → Margin enables marketing
                      → More paying users
                          → OAuth3 adoption by external platform
```

The flywheel is not missing any components. It is missing activation energy. That activation energy is: a publicly accessible demo of something a developer has never seen before.

---

## Timing Summary

| Northstar | Q2 2026 Milestone | End 2026 Target | First Action |
|-----------|------------------|-----------------|-------------|
| 10,000 GitHub stars | 1,000 stars | 10,000 stars | Dispatch BUILD 12; draft HN post |
| 5,000 paying users | 1,000 paying users | 5,000 paying users | Deploy solaceagi.com Phase 4 |
| 8 projects at rung 65537 | 2 projects at 65537 | 8 projects at 65537 | Add CI to all projects today |
| 80% recipe hit rate | 50% hit rate | 80% hit rate | Build recipe matching algorithm |
| OAuth3 external adoption | Spec at stable URL | 1+ external adopter | GitHub Pages publication |
| Black Belt | Orange Belt → Green | Black Belt | GitHub Discussions Skill Sprint |

---

## The Maze-Exit View

Each Northstar, solved from the end, points to the same exit. The maze has one critical corridor:

**BUILD 12 → solaceagi.com public → demo → distribution → community → flywheel**

Everything else — the OAuth3 spec URL, the Store GLOW requirements, the belt XP leaderboard, the recipe matching algorithm — can be executed in parallel while traversing this main corridor. They are optimizations that increase the flywheel's speed once it starts spinning. But the flywheel cannot start spinning without the main corridor.

The maze is not complex. The exit is visible. The first step into the critical corridor is BUILD 12.

---

*"Still water runs deep. But first, the water must flow."*

*Paper 42 — Reverse Paths. 2026-02-21.*
