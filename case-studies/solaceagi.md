# Case Study: SolaceAGI — Hosted Platform for Verified Delegated Intelligence

**Tracking since**: 2026-02-21
**Status**: Whitepaper written → Refactor planned → Build planning
**Rung**: TBD
**Belt**: White

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
| `web/` frontend | Exists (legacy) |
| `solace/` research content | Needs → solace-books |
| FastAPI backend | Partial (needs rebuild) |
| LLM proxy (POST /llm/complete) | Not implemented |
| OAuth3 vault | Not implemented |
| Cloud twin execution | Not implemented |
| Stillwater Store integration | Not implemented |

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

## Metrics

| Metric | Now | Target Q2 | Target EOY |
|--------|-----|-----------|-----------|
| Paying users | 0 | growing | growing |
| Recipe hit rate | 0% | 50% | 80% |
| API uptime | N/A | 99% | 99.9% |
| Managed LLM add-on users | 0 | growing | growing |
