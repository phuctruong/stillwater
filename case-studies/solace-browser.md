# Case Study: SolaceBrowser — OAuth3 Reference Implementation

**Tracking since**: 2026-02-21
**Status**: Phase 1 COMPLETE → Phase 1.5 IN PROGRESS
**Rung**: 641 (LinkedIn MVP verified)
**Belt**: 🟡 Yellow

## What Was Built

| Component | Status | Stillwater Role |
|-----------|--------|----------------|
| LinkedIn PM triplet | ✅ Committed | SHA256 verified |
| Gmail PM triplet | ✅ Committed | SHA256 verified |
| Reddit PM triplet | ✅ Committed | SHA256 verified |
| HackerNews PM triplet | ✅ Committed | SHA256 verified |
| Notion PM triplet | ✅ Committed | SHA256 verified |
| LinkedIn recipes (6) | ✅ Committed | Lane A evidence |
| OAUTH3-WHITEPAPER.md | ✅ Committed | Constitution |
| ROADMAP.md v2 | ✅ Committed | 8 build prompts |

## Phase 1.5 — OAuth3 Core (Next)

- [ ] `oauth3/token.py` — AgencyToken schema
- [ ] `oauth3/scopes.py` — scope registry (linkedin.*, gmail.*, hackernews.*)
- [ ] `oauth3/enforcement.py` — gate on every recipe execution
- [ ] `oauth3/revocation.py` — instant kill switch
- [ ] `/consent?scopes=...` — consent UI
- [ ] POST /run-recipe with OAuth3 enforcement

## Metrics

| Metric | Value |
|--------|-------|
| PM triplets with SHA256 | 6/6 verified |
| Recipe hit rate | TBD (need prod data) |
| OAuth3 implementation | 0% |
| Platforms with PM maps | 5 |
| ROADMAP build prompts | 8 ready |

## Stillwater Evidence Bundles

- PM triplet SHA256: All 6 platforms verified (see primewiki/*/sha256 files)
- Git commits: 0082fee, 0fbf91f
- Next evidence: OAuth3 agency token creation + scope enforcement

## Key Insight

"We are not building a browser automation tool. We are publishing the consent standard for AI agents — OAuth3 — and solace-browser is the reference implementation." — NORTHSTAR.md
