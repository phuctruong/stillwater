# stillwater Roadmap
<!-- Auth: 65537 | Tenant: stillwater | Date: 2026-05-19 -->

```
DNA: substrate_growth = belt_ratchet × external_forks × contributor_PRs × release_cadence
```

This roadmap describes how stillwater advances over the next 4 phases (90-day windows, mirroring gatan's structure). Dates flagged **UNKNOWN** require operator confirmation. Workers tick autonomously against this roadmap once Phase A is sealed.

---

## Phase A — Substrate consolidation + brand-spawn seal (Q2 2026, 0–30 days from 2026-05-19)

**Owner role:** atlas (orchestrator) + Phuc (operator)

**Why first:** before promoting stillwater to external operators, the brand must satisfy the **7 symmetric properties** from `~/projects/phuclabs/canon/brand-portfolio.md`. The phuclabs spawn pattern (`canon/standards/phuclabs-brand-spawn-pattern.md`) is the checklist. As of 2026-05-19 stillwater is the only phuclabs portfolio brand without a Firestore tenant doc; this phase closes that gap.

### P0 deliverables

1. **6 canon files authored** in `~/projects/stillwater/canon/` — `company-information.md`, `NORTHSTAR.md`, `ROADMAP.md` (this file), `SCOREBOARD.md`, `proposal-for-stillwater.md`, `tenant-repo-layout.md`. **(this PR)**
2. **Firestore tenant entry** `companies/stillwater` created with `parent_company: phuclabs`, `vertical: software-substrate`, `tier: starter`, `repo_path: /home/phuc/projects/stillwater`. **(this PR)**
3. **`bake_website_to_static.py` wiring** — REPO_PATHS gets a `stillwater` entry mirroring the pzip / phucnet pattern so `bake --twin stillwater` works. **(this PR)**
4. **Brand-portfolio update** — `~/projects/phuclabs/canon/brand-portfolio.md` row #5 (stillwater) flips from `tenant: TBD` to `tenant: companies/stillwater`. **(this PR)**
5. **`qa` branch created** — stillwater repo currently has only `main`; a `qa` branch is required so the bake script's autodeploy loop can latch on later. **(this PR)**

### Success criteria

- All 7 symmetric properties from `brand-portfolio.md` pass for stillwater.
- `gcloud firestore documents get companies/stillwater` returns a doc with `parent_company: phuclabs`.
- `git log origin/main -1` on stillwater shows the canon-spawn commit.
- No `BRAND_WITHOUT_TENANT` or `MISSING_BRAND_PORTFOLIO_ENTRY` forbidden states fire.

---

## Phase B — Substrate publishability + contributor onramp (Q3 2026, days 30–90)

**Owner role:** atlas (orchestrator) + mavis (technical-docs worker) + Phuc

**Why second:** stillwater currently exists at https://github.com/phuctruong/stillwater (6 stars / 1 fork as of 2026-05-19). To become *forkable in practice* — not just in license — the substrate needs an external-friendly onramp: a `CONTRIBUTING.md`, a `RFC-0000-process.md`, and a 30-minute quick-start that an outside operator can complete without Phuc's intervention.

### P0 deliverables

1. **Public marketing surface** — operator decides the domain. Candidates: `stillwater.phuc.net` (subdomain of personal site), `sw5.dev`, or `stillwater.solaceagi.com/docs`. **Status: UNKNOWN — verify with operator before purchase.**
2. **30-minute external quick-start** — a doc in `docs/QUICKSTART-EXTERNAL.md` that walks a clean-Linux clone-to-running in ≤ 30 minutes with no Phuc-specific assumptions (no `~/.claude/`, no `~/projects/solace-cli/` references for runtime).
3. **CONTRIBUTING.md** — rules for external PRs: how to write a paper, how to add a skill, how to add a recipe, how to ratchet a Belt, evidence-row requirements.
4. **RFC process** — `docs/rfc/0000-template.md` + a `RFC-0001` worked example for adding a new LAI law. The RFC process is the canon-update channel for outside contributors.
5. **First external apps-note** — drafted by mavis worker — *"Why canon-update RSI compounds faster than weight-update RSI: the stillwater proof."* Targets builder-to-builder audience (HN, Lobsters, /r/MachineLearning).

### Success criteria

- Quick-start completed successfully by ≥ 1 outside operator (any feedback writes evidence row).
- ≥ 1 external PR merged (any size — typo, recipe, paper).
- Apps-note draft sealed in `papers/` and announced on phuc.net + solaceagi.com.
- Public marketing domain decided + DNS configured.

---

## Phase C — Belt-ladder advancement: Orange → Green (Q4 2026, days 90–180, **dates UNKNOWN — verify**)

**Owner role:** atlas + custom-release-worker (PROPOSED) + Phuc

**Why third:** the repo is currently sealed at **Orange** (Stillwater Store skill submitted, rung 641 done). The next gate is **Green** (rung 274177 — stability sweeps + edge/null checks). Crossing Green is the credibility signal that external operators check before betting their build loop on the substrate.

### P0 deliverables

1. **Implement `custom-release-worker`** — PROPOSED in `company-information.md`. Packages a stillwater release: tag, semver bump, CHANGELOG entry, GitHub release notes, evidence chain. Lives in `companies/__canonical/workers/release/` once promoted.
2. **Rung 274177 evidence sweep** — run the 2,399-test harness across edge/null inputs. Every failing case writes a paper + a recipe. Every fix writes an evidence row.
3. **External-fork audit** — review forks at `gh api /repos/phuctruong/stillwater/forks` quarterly; record interesting external work in `case-studies/external-forks.md`.
4. **Recipe hit-rate validation** — measure the 34 recipes against their declared ≥ 70% target on a fresh corpus. Recipes below target either get fixed or get archived (LAI-6 selective forgetting).

### Success criteria

- Belt seal flips from Orange → Green; README updated; evidence row in `case-studies/`.
- `custom-release-worker` shipped + canonical-promoted to `companies/__canonical/workers/release/`.
- ≥ 3 external forks doing real work (not just star-and-forget).

---

## Phase D — Belt-ladder advancement: Green → Blue + Black setup (Q1 2027 – Q2 2027, **dates UNKNOWN**)

**Owner role:** atlas + custom-release-worker + the broader contributor community

**Why fourth:** Blue = rung 65537 = adversarial / security-grade release gate. Black = 30 days at 65537 in production. These are the rungs that turn "interesting OSS project" into "substrate you can build your company on."

### P0 deliverables

1. **Adversarial test corpus** — extend the 2,399-test harness with red-team prompts, prompt-injection samples, and skill-misuse cases. Target: 5,000+ tests.
2. **Security review** — external (not Phuc) security review of the substrate. Findings logged as papers, fixes shipped as PRs.
3. **30-day production marker** — at least one Solace tenant (Phuc-side or external) runs SW5.0-substrate-backed workflows in production for 30 consecutive days with no Blue-rung regressions.
4. **Belt promotion** — Green → Blue → Black ratcheted with full evidence trail in `case-studies/belt-progression.md`.

### Success criteria

- Belt seals through Blue and ratchets at Black (30d @ 65537).
- ≥ 1 production tenant running stillwater-substrate workflows for 30+ days with zero LAI violations.
- Adversarial test corpus is in the harness and gates every PR.

---

## Out-of-scope (explicitly)

- **Hosted SaaS for stillwater itself.** Not built here. Workers run on solaceagi.com (separate phuclabs brand).
- **Closed-source plugins.** Anything Solace-private (e.g. `solace-cli` OAuth3 vault, twin-browser bridge) lives in its own repo. stillwater stays purely OSS.
- **Paid certifications / badges.** No belt fees. Belts are earned via merged PRs + evidence, not paid.
- **Acquisitions / partnerships requiring NDA.** stillwater is OSS; partnerships happen on the solaceagi.com side.

## Honest-unknowns ledger

| Item | Status | Resolver |
|---|---|---|
| Public marketing-site domain | UNKNOWN — flagged in Firestore as `(TBD)` | operator (Phuc) |
| Phase B–D start dates | UNKNOWN | operator calendar |
| `custom-release-worker` design | PROPOSED — not yet implemented | future swarm |
| External-contributor signal at Day-0 | 6 stars / 1 fork (`gh repo view` 2026-05-19) | GitHub API |
| Paying customers / revenue | 0 (OSS — intentional) | n/a |
