# Case Study: Solace Browser MVP — Open-Source AI Twin Browser

**Status:** 🟡 IN PROGRESS
**Started:** 2026-02-21
**Completed:** TBD
**Rung Target:** 641 (local correctness) → 274177 (stability) on promotion
**Authored by:** Phuc Truong + Claude Sonnet 4.6

---

## The Mission

> "Log in once. Solace handles the rest."

Build the first open-source AI twin browser using the Stillwater workflow — proving that:
1. A haiku main session + sonnet/opus swarms can build a real product end-to-end
2. The Phuc-Orchestration dispatch model (no inline deep work) produces verifiable artifacts
3. Stillwater Store can distribute browser intelligence (PrimeWiki + PrimeMermaid + recipes)

**This case study tracks the full arc**: spec → clean repo → builder session → open-source release.

---

## What We're Building

| Feature | Description | Status |
|---------|-------------|--------|
| Home Page | Custom start page — 6 supported sites with session status | 🟡 Specced |
| Activity View | Twin orchestrator logs + PrimeWiki + Mermaid state diagram + HTML viewer | 🟡 Specced |
| Kanban UI | Recipe task queue (Queue → Running → Done → Failed) | 🟡 Specced |
| LinkedIn Recipes (6) | discover-posts, create-post, edit-post, delete-post, react, comment | 🟡 Specced |

**Existing infrastructure (already built, 30K+ lines):**
- Persistent browser server (40+ HTTP endpoints at port 9222)
- Anti-detection suite (canvas/WebGL/JA3/Bezier mouse/inertia scroll)
- Recipe system (27 existing recipes)
- Session persistence + fingerprint sync
- PrimeWiki knowledge graphs
- Stillwater OS integration

**New code needed (estimate):**
- `ui_server.py` — ~300 lines (3 routes: home, activity, kanban + task queue API)
- `logs/activity.jsonl` format — 10 lines (log schema)
- 6 LinkedIn recipe JSON files — ~100 lines each

---

## The Stillwater Workflow Being Proven

```
1. Main session (haiku) reads NORTHSTAR.md + BUILD-SPEC.md
2. haiku dispatches coder swarms (sonnet) for each feature
3. skeptic swarm (sonnet) verifies each feature against QA-CHECKLIST.md
4. QA session (this session) audits artifacts
5. On pass: git commit + open-source push
```

**This is the MVP of the Stillwater workflow.** Every step is evidence for the paradigm.

---

## The Open-Source Plan

| Component | License | Why |
|-----------|---------|-----|
| `solace-browser` client (persistent_browser_server.py + UI) | MIT | "Share fire" — anyone can self-host |
| Recipe format spec | MIT | Open standard creates network effects |
| Anti-detection framework | MIT | Security audit = community trust |
| Recipe LIBRARY (solaceagi.com cache) | Private | The 70% hit rate = the economic moat |
| Cloud browser farm | Private | Infrastructure = natural barrier |
| Session vault + fingerprint sync service | Private | Differentiator vs self-hosted |

**Bitwarden model:** Open client (audit it, self-host it) + paid cloud (zero friction, managed).

---

## North Star Metrics

| Metric | Target (3mo) | Target (6mo) |
|--------|-------------|-------------|
| Recipe hit rate (cloud) | 50% | 70% |
| Cloud task success rate | 70% | 85% |
| GitHub stars | 100 | 1,000 |
| Paying users (cloud) | 10 | 100 |
| Community recipe contributions | 5 | 50 |

---

## Session Log

### Session 1 — 2026-02-21 (this session)

**What happened:**
- Defined 4 MVP features with full build spec (`specs/BUILD-SPEC.md`)
- Created QA checklist for auditor session (`specs/QA-CHECKLIST.md`)
- Updated NORTHSTAR.md with Phase 1 sprint
- Defined open-source strategy (Bitwarden model)
- Defined Stillwater Store content types for browser intelligence (PrimeWiki + PrimeMermaid)
- Repo cleanup plan created (scratch/ dir for suspicious files)

**Artifacts produced:**
- `specs/BUILD-SPEC.md` — full feature spec with UI mockups, API contracts, acceptance criteria
- `specs/QA-CHECKLIST.md` — line-by-line verification checklist
- Updated `NORTHSTAR.md`
- Updated `STORE.md` (new content types: prime-wiki, prime-mermaid)

**Rung:** 641 (specced, not yet built)

---

### Session 2 — TBD (builder session, haiku main + sonnet swarms)

**Goal:** Build all 4 features per BUILD-SPEC.md
**Model:** haiku (main), sonnet (coder/skeptic swarms)
**Expected artifacts:**
- `ui_server.py` with 3 routes + task queue API
- `recipes/linkedin-discover-posts.recipe.json`
- `recipes/linkedin-create-post.recipe.json`
- `recipes/linkedin-edit-post.recipe.json`
- `recipes/linkedin-delete-post.recipe.json`
- `recipes/linkedin-react-post.recipe.json`
- `recipes/linkedin-comment-post.recipe.json`
- `logs/activity.jsonl` (test data)

**Status:** 🔴 NOT STARTED

---

### Session 3 — TBD (QA session, this session resumes)

**Goal:** Verify build against QA-CHECKLIST.md
**Model:** sonnet (QA auditor)
**Pass criteria:**
- All P0 checklist items pass
- End-to-end test: `linkedin-discover-posts` runs successfully
- No red flags

**Status:** 🔴 NOT STARTED

---

### Session 4 — TBD (open-source release)

**Goal:** Push to GitHub public, update README, announce
**Actions:**
- Verify repo is clean (no credentials, no private data)
- Update README.md with "How to self-host" section
- Tag v1.0.0
- Push to public GitHub
- Post to HackerNews / Reddit / LinkedIn

**Status:** 🔴 NOT STARTED

---

## Evidence Trail

| Session | Evidence | Rung | Status |
|---------|----------|------|--------|
| 1 | `specs/BUILD-SPEC.md`, `specs/QA-CHECKLIST.md` | C (spec) | ✅ |
| 2 | `ui_server.py`, 6 recipe JSON files | 641 | 🔴 |
| 3 | QA sign-off in `specs/QA-CHECKLIST.md` | 641 | 🔴 |
| 4 | GitHub release tag, push confirmation | 641 | 🔴 |

---

## Lessons Learned (updated live)

_Will be filled in as sessions complete._

---

## Why This Matters

This is the proof of concept for the entire Stillwater paradigm:

> Can haiku (coordination) + sonnet swarms (work) build a real open-source product
> with deterministic evidence at every step?

If yes: the Stillwater workflow is validated. Every future project can follow this template.
If no: we learn exactly where the workflow breaks and fix it.

**Either outcome advances the mission.** That's the Phuc_Forecast northstar.

---

*Case Study: solace-browser-mvp | Started: 2026-02-21 | Stillwater v1.5.0*
