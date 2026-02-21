# Case Study: SolaceBrowser — OAuth3 Reference Implementation

**Tracking since**: 2026-02-21
**Status**: Phase 1 COMPLETE → Phase 1.5 COMPLETE → Phase 2 BUILD 7 COMPLETE (Gmail Recipes)
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
| Gmail PM JSON triplet (3 files) | done | selectors + urls + actions |
| Gmail recipes (6) | done | Lane A evidence, OAuth3 scoped |
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

## Phase 1.5 BUILD 3 — Step-Up Authorization (COMPLETE)

| Item | Status | Rung | Date | Notes |
|------|--------|------|------|-------|
| step_up.py | done | 641 | 2026-02-21 | Step-up re-authentication flow, challenge+response, user re-consent |
| tests/test_step_up.py | done | 641 | 2026-02-21 | 29 tests covering step-up workflow, re-auth challenge, scope upgrade |

## Phase 1.5 BUILD 5 — HTML Snapshot Capture (COMPLETE)

| Item | Status | Rung | Date | Notes |
|------|--------|------|------|-------|
| snapshot.py | done | 641 | 2026-02-21 | HTML snapshot capture, DOM serialization, timestamp recording |
| tests/test_snapshot.py | done | 641 | 2026-02-21 | 18 tests covering snapshot capture, serialization, cleanup |

## Phase 2 BUILD 7 — Gmail Recipes (COMPLETE)

| Item | Status | Rung | Date | Notes |
|------|--------|------|------|-------|
| primewiki/gmail/selectors.json | done | 641 | 2026-02-21 | Complete CSS selector catalog: login, inbox, compose, thread, search, actions, navigation |
| primewiki/gmail/urls.json | done | 641 | 2026-02-21 | Gmail URL map: base URLs, search patterns, auth URLs, navigation paths, URL detection |
| primewiki/gmail/actions.json | done | 641 | 2026-02-21 | Action catalog with OAuth3 scopes, risk levels, anti-detection rules, sequences |
| recipes/gmail/gmail-read-inbox.json | done | 641 | 2026-02-21 | Read latest N emails (subject, sender, date, read/starred status). Scope: gmail.read.inbox |
| recipes/gmail/gmail-compose-email.json | done | 641 | 2026-02-21 | Compose+send with human typing (80-200ms), Ctrl+Enter send. Scope: gmail.compose.send |
| recipes/gmail/gmail-search-emails.json | done | 641 | 2026-02-21 | Search by query (supports Gmail operators). Scope: gmail.read.search |
| recipes/gmail/gmail-reply-email.json | done | 641 | 2026-02-21 | Reply to email in thread view. Scopes: gmail.read.inbox + gmail.compose.reply |
| recipes/gmail/gmail-label-emails.json | done | 641 | 2026-02-21 | Apply labels via dropdown. Scope: gmail.organize.label |
| recipes/gmail/gmail-archive-emails.json | done | 641 | 2026-02-21 | Archive from thread or inbox. Scope: gmail.organize.archive |
| tests/test_gmail_recipes.py | done | 641 | 2026-02-21 | 308 tests (13 test classes). Schema, steps, OAuth3 scopes, selectors, credentials, evidence, PM triplet, cross-recipe, anti-detection, I/O schema, metadata, error handling |

### BUILD 7 Highlights
- **6 Gmail recipes**: read-inbox, compose-email, search-emails, reply-email, label-emails, archive-emails
- **3 PM triplet JSON files**: selectors.json (complete CSS catalog), urls.json (navigation map), actions.json (action sequences with OAuth3 scopes)
- **Anti-detection patterns enforced**: human_type for To field (80-200ms), Enter after autocomplete, Ctrl+Enter for send, no .fill() anywhere
- **OAuth3 scopes per recipe**: gmail.read.inbox, gmail.compose.send, gmail.read.search, gmail.compose.reply, gmail.organize.label, gmail.organize.archive
- **Evidence bundles**: screenshots, HTML snapshots, action logs, agency_token, selector_matches
- **308 tests across 13 test classes**: TestRecipeFileExistence, TestRecipeSchema, TestOAuth3Scopes, TestStepSequence, TestSelectorFormat, TestNoHardcodedCredentials, TestEvidenceBundle, TestPMTriplet, TestCrossRecipeConsistency, TestAntiDetection, TestInputOutputSchema, TestMetadata, TestErrorHandling

## Metrics

| Metric | Value |
|--------|-------|
| PM triplets with SHA256 | 6/6 verified |
| Gmail PM JSON triplet | 3/3 (selectors.json + urls.json + actions.json) |
| Recipe hit rate | TBD (need prod data) |
| OAuth3 implementation | Phase 1.5 complete (5 builds) |
| Gmail recipes | 6/6 complete (BUILD 7) |
| Platforms with PM maps | 5 (+ Gmail JSON triplet) |
| Platforms with recipes | 2 (LinkedIn: 6, Gmail: 6) |
| ROADMAP build prompts | 8 ready |
| Tests (total) | 474/474 passing (61 oauth3 + 58 consent UI + 29 step-up + 18 snapshot + 308 gmail recipes) |
| QA findings fixed | 3/6 (3 deferred to Phase 2) |

## Build Log

| Build | Date | Tests | Rung | Commit |
|-------|------|-------|------|--------|
| Phase 1 (LinkedIn MVP) | 2026-02-21 | — | 641 | 0082fee |
| Phase 1.5 BUILD 1 (OAuth3 Core) | 2026-02-21 | 61/61 | 641 | df3ad49 |
| Phase 1.5 BUILD 2 (Consent UI) | 2026-02-21 | 58/58 | 641 | b593829 |
| Phase 1.5 BUILD 3 (Step-Up Authorization) | 2026-02-21 | 29/29 | 641 | 8df920e |
| Phase 1.5 BUILD 5 (HTML Snapshot Capture) | 2026-02-21 | 18/18 | 641 | 223ca2e |
| Phase 2 BUILD 7 (Gmail Recipes) | 2026-02-21 | 308/308 | 641 | pending |

## Stillwater Evidence Bundles

- PM triplet SHA256: All 6 platforms verified (see primewiki/*/sha256 files)
- Git commits: 0082fee, 0fbf91f, df3ad49, b593829
- OAuth3 evidence: 119 tests, null-safety gates, scope validation, step-up re-auth, consent UI
- Gmail BUILD 7 evidence: 308 tests, 6 recipes, 3 PM JSON files, OAuth3 scope enforcement, anti-detection patterns verified

## Key Insight

"We are not building a browser automation tool. We are publishing the consent standard for AI agents — OAuth3 — and solace-browser is the reference implementation." — NORTHSTAR.md
