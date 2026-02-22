# Case Study: SolaceAGI — Hosted Platform for Verified Delegated Intelligence

**Tracking since**: 2026-02-21
**Status**: ALL PHASES DONE (0–6 + GA4 Analytics + Persona + Stripe + Social Share) — 955/955 tests passing
**Rung**: 65537 (tunnel server) / 641 (all other phases)
**Belt**: Orange
**Deployments**: QA + Prod pushed (2026-02-22)

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

| Component | Status | Phase | Tests |
|-----------|--------|-------|-------|
| SOLACEAGI-WHITEPAPER.md | Written | — | — |
| NORTHSTAR.md | Updated (corrected architecture) | — | — |
| ROADMAP.md | Created (all phases documented) | — | — |
| `web/` frontend | Live (login, pricing, store, history pages) | — | — |
| `solace/` research content | Refactored out (user cleaned up) | 0 | — |
| FastAPI backend | **COMPLETE** — 8 routers mounted | 1 | 76 |
| Stripe billing (billing.py) | **DONE** — checkout, webhook, portal, status | 1 | 15 |
| Firebase Auth (firebase_auth.py) | **DONE** — Google sign-in + dual auth | 1 | 10 |
| LLM proxy (llm_proxy.py) | **DONE** — Together.ai primary, OpenRouter fallback, 20% markup | 1 | 21 |
| OAuth3 vault (oauth3_vault.py) | **DONE** — issue/list/revoke/validate (AES-256-GCM) | 1 | — |
| User BYOK keys (users.py) | **DONE** — store/list/delete, cryptographic erasure | 1 | — |
| Evidence verify (verify.py) | **DONE** — POST /verify with rung checking | 1 | — |
| Cloud twin (twin/) | **DONE** — CloudBrowser + RecipeExecutor + EvidenceBuilder + SessionSync | 2 | 83 |
| PZip storage layer | **DONE** — snapshot.py + history.py + compression.py + history API + Kanban UI | 2.5 | 81 |
| Dragon Tip Program | **DONE** — tip/engine.py + transparency.py + tiers.py + tracking/usage.py + api/tips.py | 2.7 | 83 |
| Stillwater Store frontend | **DONE** — store/api.py + publish.py + attribution.py + registry.py | 3 | 71 |
| Persona System integration | **DONE** — POST /persona/select + LLM proxy persona_hint | 3.5 | — |
| Launch (billing tiers + rate limits + GDPR) | **DONE** | 4 | — |
| GA4 Analytics integration | **DONE** | 5 | — |
| Social share registration | **DONE** — social share endpoints registered | 6 | — |
| Stripe billing (4 products, 4 prices, webhooks) | **DONE** — checkout, webhook (prod + QA), portal, status | — | 15 |
| Docker import fix (store modules) | **DONE** — missing store modules resolved | — | — |

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

### Dragon Tip Program (NEW — BYOK OSS Funding)

Turns free-tier BYOK users into voluntary OSS contributors. After each API call, a user-chosen percentage of the API credit cost flows to the open-source fund.

| Dragon Tier | Tip % | Motto |
|-------------|-------|-------|
| Dragon Contributor | 2% | "Every drop fills the river" |
| Super Dragon | 5% | "The river that gives, grows" |
| Elder Dragon | 8% | "Ancient wisdom funds the future" |
| Legendary Dragon | 9%+ | "Your generosity builds the dojo" |

**Key design decisions:**
- Opt-in only (default = 0%). User must explicitly choose a Dragon tier.
- Full Part 11 transparency: every tip is hash-chained (SHA-256, append-only, publicly verifiable).
- Savings dashboard shows recipe hit rate + tokens saved + money saved — creates natural conversion to tipping.
- Dragon badges appear on Stillwater Store profile. Tip XP stacks with belt progression.
- Tips fund: paudio, pvideo, stillwater, solace-browser, pzip, and community bounties.

**Revenue projection:** 10K BYOK users at avg 3% tip = ~$4,500/month OSS fund ($54K/year).

**Implementation:** Phase 2.7 in ROADMAP.md — `tip/engine.py`, `tip/transparency.py`, `tip/tiers.py`, `tracking/usage.py`, `api/tips.py`, `api/usage_api.py`.

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
| httpx + cryptography fix (Phase 1 bugfix) | 2026-02-21 | 46/46 | 641 | 9ba6585 |
| Phase 2: Cloud Twin (twin/ package) | 2026-02-21 | 83/83 | 641 | — |
| Phase 2.5: PZip Storage Layer | 2026-02-21 | 81/81 | 641 | — |
| Phase 2.7: Dragon Tip Program | 2026-02-21 | 83/83 | 641 | — |
| Phase 3: Stillwater Store Frontend | 2026-02-21 | 71/71 | 641 | — |
| Phase 3.5: Persona System | 2026-02-21 | — | 641 | — |
| Phase 4: Launch (billing tiers + rate limits + GDPR) | 2026-02-21 | — | 641 | — |
| Phase 5: GA4 Analytics | 2026-02-21 | — | 641 | — |
| Phase 6: Social share registration | 2026-02-22 | — | 641 | 9b577af |
| Stripe: 4 products + 4 prices + webhook (prod + QA) | 2026-02-22 | 15/15 | 641 | — |
| Docker import fix (missing store modules) | 2026-02-22 | — | 641 | — |
| Full suite green (955/955) | 2026-02-22 | 955/955 | 641 | — |
| QA + Prod deployment | 2026-02-22 | 955/955 | 641 | — |

## Metrics

| Metric | Now | Target Q2 | Target EOY |
|--------|-----|-----------|-----------|
| Tests | 955/955 | 1,000+ | 1,200+ |
| Phases complete | 8/8 (0–6 + Persona + GA4 all DONE) | 8/8 | 8/8 |
| API endpoints | 35+ | 50+ | 70+ |
| Stripe products | 4 (prod + QA webhooks live) | 4 | 4 |
| Paying users | 0 | growing | growing |
| Recipe hit rate | 0% | 50% | 80% |
| API uptime | N/A | 99% | 99.9% |
| Cloud twin | DONE (83 tests) | live | 99.9% uptime |
| PZip compression ratio | > 2:1 (verified) | > 4:1 with GAR | > 10:1 |
| Dragon Tip hash chain | 100-record integrity verified | live | public |

## Retroactive QA (2026-02-21) — Persona-Enhanced

| Metric | Value |
|--------|-------|
| Tests run | 283 |
| Tests passed | 283 |
| Security findings | 1 HIGH + 1 MEDIUM + 1 LOW (all FIXED) |
| Persona stack | Schneier + Kent Beck + Werner Vogels |
| Ghost master effectiveness | Caught private key leak on public endpoint (HIGH — would have been a production incident) |
| Rung achieved | 641 (pending HIGH fix deployment) |
