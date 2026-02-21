# Case Study: SolaceAGI — Hosted Platform for Verified Delegated Intelligence

**Tracking since**: 2026-02-21
**Status**: Phase 0 DONE (refactor) → Phase 1 DONE (core backend) → Phase 2 next
**Rung**: 641 (46/46 tests pass)
**Belt**: Yellow

## Architecture

```
stillwater/cli (OSS)           ← base CLI, lives inside stillwater repo; anyone can use it
    │
    └── solace-cli (PRIVATE)   ← extends stillwater/cli; NOT open source
            │  adds: OAuth3 vault, twin browser orchestration, solaceagi.com connectivity
            │
            └── solaceagi.com (PAID) orchestrates everything
                    ├── solace-cli backend (private)
                    ├── solace-browser cloud twin
                    ├── BYOK: Anthropic/OpenAI/Llama (zero markup)
                    ├── Managed LLM: hosted LLM routing (no API key required)
                    └── Self-host option: deploy your own solace-cli + twin
```

**Day-one hosted LLM:** Proxy upstream LLM providers from launch. Zero GPU infra.

## What Exists

| Component | Status |
|-----------|--------|
| SOLACEAGI-WHITEPAPER.md | Written |
| NORTHSTAR.md | Updated (corrected architecture) |
| ROADMAP.md | Created (Phase 1 includes LLM proxy endpoint) |
| `web/` frontend | Live (login, pricing, store pages) |
| `solace/` research content | Refactored out (user cleaned up) |
| FastAPI backend | **COMPLETE** — 8 routers mounted |
| Stripe billing (billing.py) | **DONE** — checkout, webhook, portal, status |
| Firebase Auth (firebase_auth.py) | **DONE** — Google sign-in + dual auth |
| LLM proxy (llm_proxy.py) | **DONE** — Together.ai primary, OpenRouter fallback, 20% markup |
| OAuth3 vault (oauth3_vault.py) | **DONE** — issue/list/revoke/validate (AES-256-GCM) |
| User BYOK keys (users.py) | **DONE** — store/list/delete, cryptographic erasure |
| Evidence verify (verify.py) | **DONE** — POST /verify with rung checking |
| Cloud twin execution | Not yet (Phase 2) |
| Stillwater Store integration | Not yet (Phase 3) |

## Refactor Plan (Before Build)

**solaceagi/solace/ → solace-books/**
Content to move:
- Books (002-constitutional, 003-kungfu, etc.)
- Research and experimental content
- Tools and utilities that aren't core to hosted platform
- scratch/ in solace-books (gitignored)

**solaceagi/ after refactor = clean hosted platform:**
- `api/` — FastAPI backend (including api/llm.py for LLM proxy)
- `twin/` — Headless browser execution
- `store/` — Stillwater Store interface
- `vault/` — OAuth3 token management
- `web/` — Landing page

## Business Model

| Tier | Price | What |
|------|-------|------|
| Free | $0 | Local execution, BYOK, OSS client (stillwater/cli), community skills |
| Managed LLM | add-on | Hosted LLM routing (no API key needed) |
| Pro | paid tier | Cloud twin + OAuth3 vault + 90-day evidence + Managed LLM included |
| Enterprise | paid tier | SOC2 audit mode, team tokens, private store, dedicated nodes |

**Managed LLM economics:**
- Routes to upstream LLM providers (zero GPU infra required)
- Markup applied on upstream cost
- Recipe hit rate drives down per-task cost significantly

**BYOK economics:**
- Recipe replay drives COGS down dramatically at scale
- Recipe replay → sub-cent per task. LLM cost = $0 (user's key).

## Phase 1 Priority: LLM Proxy

The first concrete revenue unlock is the Managed LLM add-on.
Phase 1 (core backend) MUST include `api/llm.py`:
- `POST /llm/complete` → routes to upstream LLM provider (primary) or fallback
- Markup applied, billed to user account (exact arithmetic — no float in billing path)
- Tier check: managed_llm/pro/enterprise → allowed; free/byok → 403
- Zero GPU infra: pure HTTP proxy

## Build Log

| Build | Date | Tests | Rung | Commit |
|-------|------|-------|------|--------|
| Stripe billing (Phase 0.5) | 2026-02-21 | 15/15 | 641 | 145e60b |
| Firebase Auth | 2026-02-21 | 10/10 | 641 | cb912fe |
| Phase 1: LLM proxy + OAuth3 + users + verify | 2026-02-21 | 21/21 | 641 | a8c8c32 |

## Metrics

| Metric | Now | Target Q2 | Target EOY |
|--------|-----|-----------|-----------|
| Tests | 46 | 100+ | 200+ |
| API endpoints | 16 | 25+ | 40+ |
| Stripe products | 4 | 4 | 4 |
| Paying users | 0 | growing | growing |
| Recipe hit rate | 0% | 50% | 80% |
| API uptime | N/A | 99% | 99.9% |
