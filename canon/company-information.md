# stillwater — Company Information
<!-- Auth: 65537 | Tenant: stillwater | Parent: phuclabs | Date: 2026-05-19 -->

```
DNA: stillwater = OSS_substrate × verification × canon_update_RSI × belt_ladder
```

This is the public-canonical brand record stillwater's Solace workers read at runtime. stillwater is the **OSS substrate for SW5.0** — the Software 5.0 paradigm in which intelligence is updated by editing canon (specs, conventions, evidence), not by retraining weights. The brand is maintained by **Phuc Truong** under the **phuclabs umbrella**.

## Identity

| Field | Value | Source |
|---|---|---|
| Brand name | stillwater | repo + GitHub |
| Long name | Stillwater OS — Software 5.0 Dojo | `~/projects/stillwater/README.md` |
| Parent brand | phuclabs (umbrella) | `~/projects/phuclabs/canon/brand-portfolio.md` |
| Public domain | UNKNOWN — flagged. Likely candidate `stillwater.phuc.net` or `sw5.dev`; verify with operator | — |
| Public repo | https://github.com/phuctruong/stillwater | `gh repo view phuctruong/stillwater` |
| License | OSS (see `LICENSE` in repo) | repo root |
| Vertical (Solace) | software-substrate | NEW vertical, introduced by this brand-spawn |
| Status | active (OSS — no paying customers) | brand-portfolio.md row #5 |
| Founded | UNKNOWN — Phuc internal use predates public release; verify | — |

## What stillwater is (and is not)

**stillwater is:** the open, public, free, forkable substrate for AI-native operators who want to build software the SW5.0 way — papers → diagrams → styleguides → webservices → tests → code, every step verified, no silent fallback. Includes the **`stillwater/cli`** (base CLI shipped in this repo) plus the canonical skills, personas, recipes, and Belt ladder.

**stillwater is NOT:** a hosted service, a SaaS, or a billed product. It is the OSS foundation that the commercial layer (solaceagi.com) builds on. Paying customers buy *workers on solaceagi.com*; they may also clone stillwater to self-host the substrate — that is encouraged.

**Critical distinction (from `~/.claude/CLAUDE.md`):**
- `stillwater/cli` (this repo) = **OSS** — anyone clones stillwater and gets the CLI.
- `solace-cli` (separate repo `~/projects/solace-cli/`) = **PRIVATE extension** — adds OAuth3 vault + twin browser + solaceagi.com cloud connectivity. Not part of stillwater's OSS surface. Reference only.

## The 10 Uplift Principles (substrate DNA)

Stillwater's substrate is organized around 10 principles (Paper 17 in the repo's `papers/`). These are the categories every SW5.0 system must satisfy:

| # | Principle | One-line meaning |
|---|---|---|
| P1 | Gamification | Belt ladder (White → Yellow → Orange → Green → Blue → Black), rung system, GLOW scores |
| P2 | Magic Words | DNA equations, /distill, prime channels [2][3][5][7][11][13] |
| P3 | Famous Personas | 29 experts on call — load by domain, never always-on |
| P4 | Skills | 37 canonical skills (prime-safety GOD, prime-coder + 35 domain) |
| P5 | Recipes | 34 recipes — pre-tested workflows with target hit-rate ≥ 70% |
| P6 | Access Tools | CLI + LLM Portal (6 providers) + service mesh + OAuth3 |
| P7 | Memory | Skill memory, evidence chains, case studies, audit logs |
| P8 | Care | EQ stack (5 skills), SmallTalkResponder (WARM), Anti-Clippy |
| P9 | Knowledge | 61 papers + 10 diagrams, Three Pillars, Axiom Kernel |
| P10 | God | 65537 = divine prime, evidence = truth, code is sacred |

## The core loop

```
DREAM → FORECAST → DECIDE → ACT → VERIFY
```

No silent fallback. No unwitnessed pass. No fake `ok: true` on failure. Every step writes evidence; every evidence row signs `Purpose × Evidence × Love`.

## Belt ladder (gamified rungs)

| Belt | Rung | Meaning | Repo status |
|---|---:|---|---|
| White | setup | Project runs locally | DONE |
| Yellow | 641 | Local correctness: failing case reproduced, fix verified | DONE |
| **Orange** | **Store** | **First skill in Stillwater Store** | **CURRENT** |
| Green | 274177 | Stability sweeps + edge/null checks | NEXT |
| Blue | 65537 | Adversarial / security-grade release gate | — |
| Black | 30d @ 65537 | Production task running at 65537 for 30 days | — |

## Worker fleet (deliberate, not auto-attached)

Per the phuclabs spawn pattern — *"different brands need different workers"* (operator directive 2026-05-19) — stillwater's fleet is intentionally **small** because the brand is internal-ops-light (OSS, no sales motion, no outreach campaigns):

| Worker | Role | Status |
|---|---|---|
| **atlas** | Orchestrator — sequences contributor onboarding, release announcements, doc rebuilds | canonical (live in `companies/__canonical/workers/atlas`) |
| **mavis** | Technical documentation worker — drafts apps notes, paper summaries, recipe READMEs, contributor guides | canonical (renamed from data-quality `mira` 2026-05-18) |
| **custom-release-worker** | PROPOSED — packages a new stillwater release (tag, changelog, GitHub release notes, npm/pypi sync if added later). Not yet implemented; flagged for v2.0 phase. | PROPOSED (not in `companies/__canonical/workers/` yet) |

No outreach workers (hana / scout / ilan / kira) — stillwater grows by contributors and word-of-mouth, not cold email. No vision/browser workers — substrate work is text + code, not screenshots.

## Marketing voice

**Builder-to-builder, code-first.** No marketing copy. No buyer-personas funnel. The audience is AI-native operators and senior engineers who already know what RSI, SDK design, and compiler-grade discipline mean. The pitch is: *here is the substrate that makes canon-update RSI work; here is the evidence; here is the repo.*

stillwater never asks for "leads." It asks for **contributors** (PRs, papers, skills, recipes) and **forks** (operators self-hosting SW5.0 inside their own org).

## Promotion graph (phuclabs DAG)

- **Promoted by:** solaceagi.com (the commercial driver — sells the workers that run on stillwater) + phuc.net (the megaphone for SW5.0 thinking).
- **Promotes:** the SW5.0 paradigm itself — *canon-update RSI > weight-update RSI* — and by transitive citation, IF Theory + bounded math + pzip (all phuclabs OSS brands that build on or use SW5.0 conventions).

## What this brand does NOT do

- **No paid tier.** Everything in this repo is free, forkable, OSS-licensed.
- **No managed SaaS.** If you want managed runtime + workers, that's solaceagi.com — a separate brand under the same phuclabs umbrella.
- **No telemetry phone-home.** stillwater does not call any network endpoint by default.
- **No closed-source plugins shipped from this repo.** Private extensions (e.g. `solace-cli`) live in their own repos; stillwater never ships private blobs.

## Anchor laws

- **LAI-13 Never-Worse** — every Belt rung is monotonic up; once a rung seals, regressions are blocked until explained.
- **LAI-22 Diagram-first** — every paper has a Prime Mermaid diagram before code.
- **LAI-23 Master Equation** — every claim signs `Purpose × Evidence × Love`.
- **LEI-2 Universal convention** — skills/personas/recipes are reused across all phuclabs brands; they live in `~/projects/solace-cli/data/default/` (reference library) and stillwater is the OSS publication channel for them.

## Honest-unknowns ledger

| Item | Status | Resolver |
|---|---|---|
| Public domain (marketing URL) | UNKNOWN | operator (Phuc) |
| `custom-release-worker` implementation | PROPOSED — not yet built | future swarm |
| Paying customers | 0 (OSS — no revenue motion) | n/a, by design |
| Stars / contributors at Day-0 | 6 stars / 1 fork (as of `gh repo view` on 2026-05-19) | GitHub API |
