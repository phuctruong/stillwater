# Case Study: SolaceBrowser — OAuth3 Reference Implementation

**Tracking since**: 2026-02-21
**Status**: Phase 1 COMPLETE → Phase 1.5 BUILD 1 COMPLETE (QA'd)
**Rung**: 641 (OAuth3 core verified)
**Belt**: Yellow

## What Was Built

| Component | Status | Stillwater Role |
|-----------|--------|----------------|
| LinkedIn PM triplet | done | SHA256 verified |
| Gmail PM triplet | done | SHA256 verified |
| Reddit PM triplet | done | SHA256 verified |
| HackerNews PM triplet | done | SHA256 verified |
| Notion PM triplet | done | SHA256 verified |
| LinkedIn recipes (6) | done | Lane A evidence |
| OAUTH3-WHITEPAPER.md | done | Constitution |
| ROADMAP.md v2 | done | 8 build prompts |

## Phase 1.5 BUILD 1 — OAuth3 Core (COMPLETE + QA'd)

| Item | Status | Rung | Date | QA Notes |
|------|--------|------|------|----------|
| oauth3/token.py | done | 641 | 2026-02-21 | AgencyToken dataclass (id, user, platform, scopes, expiry, revoked). from_dict() null-safe (scopes=None → ValueError). create() validates scopes against registry. |
| oauth3/scopes.py | done | 641 | 2026-02-21 | Scope registry (linkedin.*, gmail.*, hackernews.*). validate_scopes() rejects unknown scopes. |
| oauth3/enforcement.py | done | 641 | 2026-02-21 | G1-G4 gate enforcement on every recipe execution. step_up_confirmed parameter for re-auth flow. |
| oauth3/revocation.py | done | 641 | 2026-02-21 | Instant revocation via token file deletion. |
| oauth3/consent.py | done | 641 | 2026-02-21 | Consent flow (prompt user, record consent, return token). |
| tests/test_oauth3.py | done | 641 | 2026-02-21 | 61 tests (51 original + 10 QA-added). All passing. |

### QA Findings (pm-2026-02-21-004)

| Finding | Severity | Status | Fix |
|---------|----------|--------|-----|
| F1: from_dict() null scopes silently accepted | S2-MEDIUM | FIXED | Added ValueError on scopes=None |
| F2: step_up gate always blocks (no confirmed param) | S2-MEDIUM | FIXED | Added step_up_confirmed parameter |
| F3: pytest-httpbin crash (werkzeug compat) | S3-LOW | NOTED | Use `-p no:httpbin` flag in CI |
| F4: HTTP tests don't cover 401/402/403 | S3-LOW | DEFERRED | Phase 2 (integration tests) |
| F5: deprecated asyncio pattern | S3-LOW | DEFERRED | Phase 2 (async cleanup) |
| F6: unknown scope accepted at token creation | S2-MEDIUM | FIXED | Added validate_scopes() call in create() |

## Phase 1.5 BUILD 2 — OAuth3 Consent UI (COMPLETE)

| Item | Status | Rung | Date | Notes |
|------|--------|------|------|-------|
| consent_ui.py | done | 641 | 2026-02-21 | GET /consent, POST /oauth3/consent, GET /settings/tokens |
| Consent page | done | 641 | 2026-02-21 | Scope list with risk badges, step-up warning, grant/deny |
| Token management | done | 641 | 2026-02-21 | Table with revoke buttons, active/revoked status |
| Home page badges | done | 641 | 2026-02-21 | Green "N scopes granted" / gray "click to grant" |
| Open redirect sanitization | done | 641 | 2026-02-21 | Blocks absolute/protocol-relative/javascript: URLs |
| Cookie security | done | 641 | 2026-02-21 | HttpOnly, SameSite=Strict |
| tests/test_consent_ui.py | done | 641 | 2026-02-21 | 58 tests (10 test groups) |

## Metrics

| Metric | Value |
|--------|-------|
| PM triplets with SHA256 | 6/6 verified |
| Recipe hit rate | TBD (need prod data) |
| OAuth3 implementation | Phase 1.5 BUILD 2 complete |
| Platforms with PM maps | 5 |
| ROADMAP build prompts | 8 ready |
| Tests (total) | 119/119 passing (61 oauth3 + 58 consent UI) |
| QA findings fixed | 3/6 (3 deferred to Phase 2) |

## Build Log

| Build | Date | Tests | Rung | Commit |
|-------|------|-------|------|--------|
| Phase 1 (LinkedIn MVP) | 2026-02-21 | — | 641 | 0082fee |
| Phase 1.5 BUILD 1 (OAuth3 Core) | 2026-02-21 | 61/61 | 641 | df3ad49 |
| Phase 1.5 BUILD 2 (Consent UI) | 2026-02-21 | 58/58 | 641 | b593829 |

## Stillwater Evidence Bundles

- PM triplet SHA256: All 6 platforms verified (see primewiki/*/sha256 files)
- Git commits: 0082fee, 0fbf91f, df3ad49, b593829
- OAuth3 evidence: 119 tests, null-safety gates, scope validation, step-up re-auth, consent UI

## Key Insight

"We are not building a browser automation tool. We are publishing the consent standard for AI agents — OAuth3 — and solace-browser is the reference implementation." — NORTHSTAR.md
