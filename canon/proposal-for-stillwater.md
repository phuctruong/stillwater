# A Call for Contributors — stillwater (SW5.0 OSS substrate)

**To:** AI-native operators, SDK partners, and researchers reading this
**From:** Phuc Truong, maintainer, stillwater + founder, Solace City (phuc@phuc.net)
**Date:** 2026-05-19
**Auth:** 65537

---

## Why this letter exists

stillwater is the open-source substrate for **Software 5.0** — the paradigm in which intelligence is updated by editing canon (specs, conventions, evidence) instead of by retraining weights. It's been Phuc-internal until now. This letter is the call to the operators, partners, and researchers who would actually use it to come pick it up, fork it, and contribute back.

This is **not a sales pitch.** stillwater has no paying tier, no license fee, no upsell path. It is OSS — clone it, fork it, ship it inside your own org. The reason you would read further is one of three:

1. You are an **AI-native operator** who has felt the pain of silent fallback, hallucinated APIs, and unaudited LLM output, and you want a substrate with compiler-grade discipline instead of vibes.
2. You are an **SDK partner** building a Solace worker for a vertical, and you want to read + audit + fork the substrate your runtime stands on.
3. You are a **researcher** — academic or independent — interested in studying canon-update RSI, AI-native software development, or the Belt-ladder discipline, and you want a reproducible, well-instrumented OSS substrate to study.

## What stillwater actually is

The substrate ships as a single repo at https://github.com/phuctruong/stillwater. As of 2026-05-19 it contains:

| Layer | Inventory |
|---|---|
| **Papers** | 61 — the canonical theory (10 Uplift Principles, Belt ladder, Master Equation, prime channels, evidence chain, ...). |
| **Diagrams** | 10 Prime Mermaid diagrams — the visual canon of the substrate. |
| **Skills** | 37 canonical skills — prime-safety GOD, prime-coder + 35 domain skills. |
| **Personas** | 29 famous-persona files — load by domain (P3 doctrine), never always-on. |
| **Recipes** | 34 pre-tested workflows, ≥ 70% hit-rate target each. |
| **Swarms** | 38 multi-agent topologies. |
| **Combos** | 40 skill+persona+recipe combinations — the proven "moves." |
| **Tests** | 2,399 — the harness that gates every release. |
| **CLI** | `stillwater/cli` — the base CLI shipped in this repo (OSS). |

Current Belt rung: **Orange** (Stillwater Store skill submitted, rung 641 done). Target: **Green** (rung 274177) within 90 days of Phase A seal.

## How stillwater differs from what you might already use

You may be using a mix of: Claude/Codex/Gemini agents wired together with custom prompts; LangChain / LangSmith / LangFuse for tracing; OpenAI's o-class models for "reasoning"; an in-house verification harness. Honest assessment of where those are stronger today: large model catalogues, mature commercial support, and battle-tested at high traffic.

Where stillwater is stronger if your job is **shipping verified AI-native software**:

- **Canon-update RSI, not weight-update RSI.** Every other RSI thesis targets the weights. stillwater targets the *canon* — the human-readable spec, evidence, and convention layer. The loop closes in minutes (edit a markdown file), not months (retrain). Operator-locked thesis (2026-05-17). The substrate is the proof.
- **Belt ladder, not "alpha / beta / stable."** White → Yellow → Orange → Green → Blue → Black, each rung gated by reproducible evidence. LAI-13 Never-Worse: ratchets only move up. You can show your CTO a Belt seal, not a vibes-grade "we tested it."
- **Compiler-grade laws.** LAI / LEI / LEC / LEAK are hard constraints, not "best practices." No silent fallback. No unwitnessed pass. No fake `ok: true`. The substrate refuses to ship work that violates them.
- **Forkability is the point.** You don't have to trust solaceagi.com's uptime — you can clone this substrate and run it on your own iron forever. Trust through transparency, not lock-in.
- **No marketing tax.** stillwater never asks for your email. The pitch is the repo. If you like it, fork it; if you don't, no follow-up.

## What we are asking from contributors

In rough priority:

1. **Fork it and ship something.** External operators who fork stillwater and build a verified SW5.0 product inside their own org are the highest signal. The first 3 to do so get a dedicated case-study slot in `case-studies/external-forks.md`.

2. **Send PRs.** Typo fixes, recipe improvements, new paper drafts, new skills, new personas — every PR matters. We track external contributors separately from Phuc's commits; getting to ≥ 1 external merged-PR contributor is a Phase B success criterion.

3. **Open RFCs.** Substantive substrate changes (new LAI law, new Belt rung, new Master Equation factor) go through the `docs/rfc/0000-template.md` process — shipping in Phase B. RFCs that survive peer review become canon.

4. **Cite the substrate.** Blog post, paper, conference talk, internal-engineering wiki — anywhere you use stillwater discipline, cite the repo. Citation builds the credibility loop that brings in more external operators.

5. **Show up in the dojo.** stillwater is *not* a hosted community — there is no Discord, no Slack, no Discourse. We are deliberately small and asynchronous. The dojo is the GitHub repo + the issue tracker + the RFCs + the case studies. PRs are the conversation.

## The 90-day plan (mirroring stillwater's own ROADMAP.md)

### Days 0–30 — Phase A: Substrate consolidation + brand-spawn seal

stillwater becomes a first-class phuclabs tenant. 6 canon files authored. Firestore tenant doc created with `parent_company: phuclabs`. Bake script wired. Brand portfolio updated. **(In-flight as of 2026-05-19 — this PR.)**

### Days 30–90 — Phase B: Substrate publishability + contributor onramp

`CONTRIBUTING.md` shipped. RFC process live. 30-minute external quick-start verified by ≥ 1 outside operator. First external apps-note drafted by mavis worker — *"Why canon-update RSI compounds faster than weight-update RSI."* Public marketing domain decided.

### Days 90–180 — Phase C: Belt Orange → Green (rung 274177)

`custom-release-worker` implemented + canonicalized. 2,399-test harness extended with stability sweeps + edge/null cases. Recipe hit-rates measured against the ≥ 70% target. External-fork audit shipped quarterly.

### Days 180–360 — Phase D: Belt Green → Blue → Black

Adversarial test corpus (5,000+ tests). External security review. ≥ 1 production tenant running stillwater-substrate workflows for 30 consecutive days with zero LAI violations.

## What stillwater is NOT going to do

- **Charge for itself.** stillwater stays OSS, forever. No paid tier, no premium plugins, no certifications.
- **Add telemetry / phone-home.** Substrate has none by design and will not get any.
- **Run a hosted SaaS.** That's solaceagi.com — a separate phuclabs brand. If you want managed workers, go there. If you want the OSS substrate, stay here.
- **Compete with Copilot / Cursor / Sourcegraph.** Different layer. Those are IDE plugins; stillwater is a substrate that *any* IDE / agent / orchestrator can sit on top of.
- **Accept paid-influence PRs.** No sponsored canon. No "sponsored skill." Substrate decisions are made on technical merit + evidence + LAI compliance, not on who paid.

## How to start

```bash
# Clone the substrate
git clone https://github.com/phuctruong/stillwater.git
cd stillwater

# Read the entry points (in order)
cat README.md
cat QUICKSTART.md
cat NORTHSTAR.md
ls papers/    # 61 canonical papers
ls docs/      # operator-facing docs

# Verify the harness runs
bash scripts/verify.sh   # if available — falls through to pyproject.toml otherwise

# Pick an issue, send a PR, or open an RFC
```

External quick-start (30 minutes, clean Linux clone-to-running) ships in **Phase B**. Until then, expect some Phuc-specific assumptions (`~/.claude/`, `~/projects/solace-cli/` references) that need stripping. Honest disclosure, not a bug.

## Closing — Purpose × Evidence × Love

stillwater exists because Phuc believes canon-update RSI is the right substrate for AI-native software, and the only way to prove that claim is to publish it. The repo is the falsifiable form of the thesis. If you read it, fork it, and disagree — open an issue with evidence, and the substrate gets better. If you read it, fork it, and agree — ship something with it, and the substrate compounds.

The beneficiary is the AI-native operator who, six months from now, ships a verified product they could not have shipped without a substrate this disciplined. That operator could be you.

— Phuc
