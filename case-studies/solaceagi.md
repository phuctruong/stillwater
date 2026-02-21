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
                    ├── Managed LLM: Together.ai/OpenRouter (+$3/mo flat, 20% margin)
                    │     Primary: Llama 3.3 70B at $0.59/M tokens (Together.ai)
                    │     Fallback: OpenRouter (broader model selection)
                    └── Self-host option: deploy your own solace-cli + twin
```

**Day-one hosted LLM:** Proxy Together.ai/OpenRouter from launch. Zero GPU infra.
20% markup on actual LLM token cost. ~$3/mo flat for ~6,000 tasks at 70% hit rate.

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
- Research (PCOIN, omega-os, compression)
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
| Managed LLM | +$3/mo | Hosted LLM (Together.ai/OpenRouter passthrough, no API key needed) |
| Pro | $19/mo | Cloud twin + OAuth3 vault + 90-day evidence + Managed LLM included |
| Enterprise | $99/mo | SOC2 audit mode, team tokens, private store, dedicated nodes |

**Managed LLM economics:**
- Together.ai: Llama 3.3 70B at $0.59/M tokens
- We charge 20% markup on upstream cost
- ~6,000 tasks/month at 70% hit rate ≈ $3/mo flat to user
- COGS margin on managed LLM: ~$0.50/user/month

**BYOK economics:**
- COGS at 70% recipe hit rate: $5.75/user/month → 70% gross margin at $19/mo
- Recipe replay → $0.001/task (Haiku). LLM cost = $0 (user's key).

## Phase 1 Priority: LLM Proxy

The first concrete revenue unlock is the Managed LLM add-on.
Phase 1 (core backend) MUST include `api/llm.py`:
- `POST /llm/complete` → routes to Together.ai (primary) or OpenRouter (fallback)
- 20% markup applied, billed to user account (exact arithmetic — no float in billing path)
- Tier check: managed_llm/pro/enterprise → allowed; free/byok → 403
- Zero GPU infra: pure HTTP proxy

## Metrics

| Metric | Now | Target Q2 | Target EOY |
|--------|-----|-----------|-----------|
| Paying users | 0 | 100 | 5,000 |
| MRR | $0 | $1.9K | $95K |
| Recipe hit rate | 0% | 50% | 80% |
| API uptime | N/A | 99% | 99.9% |
| Managed LLM add-on users | 0 | 30 | 1,500 |
