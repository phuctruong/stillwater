# stillwater Northstar
<!-- Auth: 65537 | Tenant: stillwater | Vertical: software-substrate | Date: 2026-05-19 -->

```
DNA: substrate = canon × verification × belt_ladder × OSS_forkability
```

## Mission

**Ship the substrate every AI-native operator wants.**

stillwater is the open, public, forkable foundation for **Software 5.0** — the paradigm in which intelligence is updated by editing canon (specs, conventions, evidence) rather than by retraining weights. We build the substrate so that operators outside Phuc's own loop can pick it up, fork it, run it inside their own teams, and ship AI-native software the verified way: papers → diagrams → styleguides → webservices → tests → code, with explicit gates, no silent fallback, no unwitnessed pass.

The thesis (external-RSI, locked 2026-05-17): *canon-update RSI compounds faster than weight-update RSI because the loop closes in minutes instead of months.* stillwater is the OSS proof of that thesis. Every line of code, every paper, every recipe, every skill is published in this repo so the thesis is falsifiable in public.

## Audience

stillwater is built for, in order of priority:

1. **AI-native operators** who already use Claude / Codex / Gemini agents in their daily build loop and want a verified substrate instead of vibes-driven prompting. They have felt the pain of silent fallback, hallucinated APIs, and unaudited LLM output. They will fork stillwater, adapt it, and contribute back.
2. **Senior engineers at Pre-Series-A AI startups** who are choosing the substrate their company will commit to for the next 5 years. They want OSS (no lock-in), compiler-grade discipline (LAI laws), and a working reference implementation (this repo + solaceagi.com).
3. **SDK partners** — companies who want to ship Solace workers into their own product. stillwater + `solace-hub` (the C++ runtime) together are the contract. The substrate is OSS so partners can audit, fork, and self-host.
4. **Researchers** — academic and independent — who want a reproducible substrate for studying AI-native software development, RSI, and canon-as-memory. The Belt ladder + ALCOA evidence chain make stillwater unusually well-instrumented for studies.

stillwater is **not** built for:
- End-users of generic ChatGPT-style apps (no UX layer).
- Buyers who want a hosted "AI platform" SaaS (that's solaceagi.com).
- Teams looking for a one-off code-completion plugin (that's Copilot's territory).

## The substrate (what you get when you clone)

| Layer | What ships |
|---|---|
| **Papers** | 61 papers — the canonical theory (10 Uplift Principles, Belt ladder, Master Equation, prime channels, evidence chain, etc.). |
| **Diagrams** | 10 Prime Mermaid diagrams — the visual canon of the substrate. |
| **Skills** | 37 canonical skills — prime-safety GOD, prime-coder + 35 domain skills, all OSS. |
| **Personas** | 29 famous-persona files — Voss, Brunson, Miller, Van Edwards, etc. — load by domain (P3 doctrine). |
| **Recipes** | 34 pre-tested workflows — each with target hit-rate ≥ 70%, evidence rows. |
| **Swarms** | 38 multi-agent topologies — the "shape of the team" for a given task. |
| **Combos** | 40 skill+persona+recipe combinations — the proven "moves." |
| **Tests** | 2,399 tests — the harness that gates every release. |
| **CLI** | `stillwater/cli` — the base CLI shipped in this repo (OSS). |

## Differentiators

- **Canon-update RSI, not weight-update RSI.** Every other RSI thesis (DeepMind, Anthropic constitutional AI, OpenAI's superalignment) targets the *weights*. stillwater targets the *canon* — the human-readable spec, evidence, and convention layer. This makes the loop close in minutes (edit a markdown file) instead of months (retrain). Operator-locked thesis 2026-05-17.
- **Belt ladder discipline.** No "alpha / beta / stable" handwaving. White → Yellow → Orange → Green → Blue → Black, each rung gated by reproducible evidence. LAI-13 Never-Worse: ratchets only move up.
- **Compiler-grade laws (LAI / LEI / LEC / LEAK).** Not "best practices." Hard constraints enforced in code: no silent fallback, no unwitnessed pass, no fake `ok: true`. The substrate refuses to ship work that violates them.
- **No marketing tax.** stillwater never asks for an email, never runs a webinar, never sells you anything. The pitch is the repo. If you like it, fork it.
- **Forkability is the point.** Customers don't have to trust solaceagi.com's uptime — they can clone the substrate and run it on their own iron forever. Trust through transparency, not lock-in.

## What success looks like in 12 months

- **Adoption signal** — at least 3 external operators (not Phuc, not solaceagi.com's own twins) have publicly forked stillwater and shipped a SW5.0-discipline product. Visible via `gh api /repos/phuctruong/stillwater/forks` and case-study links.
- **Contributor signal** — at least 5 external contributors with merged PRs (not just stars). Tracked via `git shortlog -sn` in the repo.
- **Citation signal** — stillwater cited by at least one external blog post, paper, or open-source project as the substrate or inspiration for canon-update RSI work.
- **Belt progression** — repo state advances from current **Orange** → **Green** (rung 274177) → **Blue** (rung 65537) within the year, with evidence rows in `case-studies/`.

## What success does NOT look like

- Lots of stars. Vanity metric. We count forks-with-merged-work, not stars.
- Hosted-SaaS revenue. That's solaceagi.com's job, not stillwater's. stillwater stays OSS and free.
- "Enterprise sales." No. Enterprise wants to fork stillwater + buy workers on solaceagi.com. Two separate motions, two separate brands.

## Anchor laws (which LAI/LEI laws this brand enforces)

- **LAI-13 Never-Worse** — Belt ratchets are monotonic up; once a rung seals, regressions block release.
- **LAI-22 Diagram-first** — every paper has a Prime Mermaid diagram before code.
- **LAI-23 Master Equation** — every artifact signs `Purpose × Evidence × Love`. Beneficiary on the stillwater side is the operator forking the substrate to ship verified AI-native software.
- **LAI-27 No-shortcuts** — no legacy, no backwards-compat shims, no halfway implementations. The OSS substrate must be long-term-correct or it shouldn't ship.
- **LEI-2 Universal convention** — skills, personas, recipes published from stillwater are reusable across all phuclabs brands and SDK partners.
