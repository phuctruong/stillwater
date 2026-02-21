# Case Study: SolaceAGI — Hosted Platform for Verified Delegated Intelligence

**Tracking since**: 2026-02-21
**Status**: Whitepaper written → Refactor planned → Build planning
**Rung**: TBD
**Belt**: ⬜ White

## What Exists

| Component | Status |
|-----------|--------|
| SOLACEAGI-WHITEPAPER.md | ✅ Written |
| NORTHSTAR.md | ✅ Updated |
| ROADMAP.md | ✅ Created |
| `web/` frontend | Exists (legacy) |
| `solace/` research content | Needs → solace-books |
| FastAPI backend | Partial (needs rebuild) |
| OAuth3 vault | ❌ Not implemented |
| Cloud twin execution | ❌ Not implemented |
| Stillwater Store integration | ❌ Not implemented |

## Refactor Plan (Before Build)

**solaceagi/solace/ → solace-books/**
Content to move:
- Books (002-constitutional, 003-kungfu, etc.)
- Research (PCOIN, omega-os, compression)
- Tools and utilities that aren't core to hosted platform
- scratch/ in solace-books (gitignored)

**solaceagi/ after refactor = clean hosted platform:**
- `api/` — FastAPI backend
- `twin/` — Headless browser execution
- `store/` — Stillwater Store interface
- `vault/` — OAuth3 token management
- `web/` — Landing page

## Business Model

| Tier | Price | What |
|------|-------|------|
| Free | $0 | Local execution, OSS client, community skills |
| Pro | $19/mo | Cloud twin, 90-day evidence, OAuth3 vault |
| Enterprise | $99/mo | SOC2 audit mode, team tokens, private store |

**Zero LLM cost**: Users bring own Anthropic/OpenAI API key.
COGS at 70% recipe hit rate: $5.75/user/month → 70% gross margin.

## Metrics

| Metric | Now | Target Q2 | Target EOY |
|--------|-----|-----------|-----------|
| Paying users | 0 | 100 | 5,000 |
| MRR | $0 | $1.9K | $95K |
| Recipe hit rate | 0% | 50% | 80% |
| API uptime | N/A | 99% | 99.9% |
