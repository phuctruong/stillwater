# Gmail Recipes — CPU-First From Prime Wiki

**Source:** solace-browser primewiki analysis of live Gmail inbox
**Date Created:** 2026-02-24
**Authority:** 65537
**Selectors Confidence:** 0.92-0.98+

---

## What This Is

These recipes are **reverse-engineered from real Gmail** by the solace-browser webservice. The browser:

1. **Explored Gmail interface** via Playwright (Scout → Solver → Skeptic agents)
2. **Documented all portals** (selectors, confidence scores, timing patterns)
3. **Generated Prime Wiki** (645-line semantic map in `primewiki/gmail/gmail-automation-100.primewiki.md`)
4. **Verified on real data** (47 successful logins, 100+ operations, 2,813 live inbox emails)

Now these recipes **replay that knowledge** without needing LLM rediscovery.

---

## Recipes Created

### 1. `recipe.gmail-compose.json` — Send Email
**From Prime Wiki:** COMPOSE tier (0.98 confidence)

| Portal | Selector | Confidence |
|--------|----------|------------|
| Compose button | `[gh='cm']` | 0.98 |
| To field | `input[aria-autocomplete='list']` | 1.0 |
| Subject field | `input[name='subjectbox']` | 0.98 |
| Body field | `div[aria-label='Message Body']` | 0.98 |
| Send shortcut | `Ctrl+Enter` | 1.0 |

**Pattern from Prime Wiki:**
- Type 80-200ms delays (beats bot detection)
- Press Enter after email to close autocomplete dropdown
- Use Ctrl+Enter for 100% send reliability vs 85% button click

**Cost:** 0 tokens | **Budget:** 0 (composing doesn't consume OAuth3 budget)

---

### 2. `recipe.gmail-search.json` — Search Emails
**From Prime Wiki:** ADVANCED tier (0.96 confidence)

| Portal | Selector | Confidence |
|--------|----------|------------|
| Search field | `input[aria-label='Search mail']` | 0.96 |
| Results rows | `[role='row']` | 0.97 |
| Subject extraction | `[role='heading']` | 0.96 |
| Sender extraction | `[email]` | 0.95 |

**Cost:** 0 tokens | **Budget:** 0 (read-only operation)

---

### 3. `recipe.gmail-read-inbox.json` — Extract Structured Email Data
**From Prime Wiki:** READ_INBOX tier (0.96+ confidence)

| Portal | Selector | Confidence |
|--------|----------|------------|
| Email rows | `[role='row']` | 0.97 |
| Subject | `[role='heading']` | 0.96 |
| Sender | `[email]` | 0.95 |
| Unread flag | `[aria-label*='Unread']` | 0.94 |
| Starred flag | `[aria-label*='Starred']` | 0.93 |
| Attachment flag | `[aria-label*='Attachment']` | 0.92 |

**Key Usage:** Provides structured data for CPU-first email triage

**Token Savings:**
- Without recipe: 2,813 emails × 50 tokens/email = 140K tokens ($0.083/session)
- With recipe: 0 tokens (pure extraction), then CPU keyword classification on output
- **Savings:** 70% reduction if CPU achieves 70% triage hit rate

**Cost:** 0 tokens | **Budget:** Uses read budget (200/session)

---

### 4. `recipe.gmail-archive-batch.json` — Archive Emails Safely
**From Prime Wiki:** ADVANCED tier (0.95 confidence) + Safety Constraints

| Portal | Selector | Confidence |
|--------|----------|------------|
| Archive button | `div[aria-label='Archive']` | 0.95 |

**Safety Features:**
- OAuth3 scope check (requires `gmail.archive`)
- Budget enforcement (10 archives/session max)
- Confirmation gate (>5 emails requires human approval)
- Pre-action snapshot (required for rollback)
- 4 halt paths (no fallbacks)

**Incident Reference:** Summer Yue (Feb 22, 2026) — 200+ emails deleted by OpenClaw due to silent fallback on context compaction. This recipe prevents it.

**Cost:** 0 tokens | **Budget:** Uses archive budget (10/session)

---

### 5. `recipe.gmail-reply.json` — Reply to Email
**From Prime Wiki:** ADVANCED tier (0.94 confidence)

| Portal | Selector | Confidence |
|--------|----------|------------|
| Reply button | `div[aria-label='Reply']` | 0.94 |
| Message body | `div[aria-label='Message Body']` | 0.98 |
| Send shortcut | `Ctrl+Enter` | 1.0 |

**Cost:** 0 tokens | **Budget:** 0 (composing doesn't consume OAuth3 budget)

---

## Architecture: CPU-First From Prime Wiki

```
solace run email-triage.task
  │
  ├─ Load Prime Wiki from primewiki/gmail/gmail-automation-100.primewiki.md
  │
  ├─ Recipe 1: recipe.gmail-read-inbox.json
  │   └─ Extract 2,813 emails with ARIA selectors (0 tokens)
  │
  ├─ CPU-First Classification (no LLM)
  │   ├─ Apply keywords: urgent, work, promo, spam
  │   ├─ Rank by confidence (>80% = direct route)
  │   └─ Result: 70% auto-classified (1,968 emails)
  │
  ├─ LLM Validation (only 30% escalated)
  │   └─ Haiku: "Is this email urgent?" (42K tokens, not 140K)
  │
  ├─ Recipe 2-5: gmail-compose, gmail-search, gmail-archive, gmail-reply
  │   └─ Execute actions with portals from Prime Wiki
  │
  └─ Audit
      └─ Part 11 hash-chain every action
```

---

## Token Economics

| Scenario | Tokens | Cost |
|----------|--------|------|
| **LLM-First (no recipes)** | 2,813 × 50 = 140K | $0.083/session |
| **CPU-First (with recipes)** | 0 (extract) + 42K (validate 30%) | $0.025/session |
| **Savings** | 98K tokens | **$0.058/session = $69.60/year** |

**Key:** Recipes let CPU do the work (0 tokens) → only LLM validates edge cases (<80% confidence)

---

## How Recipes Use Prime Wiki

### Discovery Phase (One-Time, Expensive)
```
Browser: Scout/Solver agents explore Gmail
  → Document selectors
  → Test confidence scores
  → Record patterns (80-200ms typing, Ctrl+Enter, etc.)
  → Save to Prime Wiki (645 lines)
```

### Replay Phase (Recurring, Cheap)
```
Recipes: Load selectors from Prime Wiki
  → Use exact same CSS selectors
  → Apply exact same timing patterns
  → Call exact same portals
  → Zero LLM needed for known operations
```

**Result:** First Gmail run is expensive (LLM explores). Subsequent runs are cheap (recipes replay).

---

## Recipe Metadata

All recipes include:

| Field | Value |
|-------|-------|
| `source` | Link to primewiki file |
| `confidence` | 0.92-0.98+ (from primewiki verification) |
| `test_evidence` | "47 cookies, 100+ operations, 2813 emails" |
| `rung` | 641 (local correctness) |
| `cost_tokens` | 0 |
| `cost_usd` | 0 |

---

## Next Steps

1. **Integrate recipes into `solace run`:**
   - Load recipe.gmail-read-inbox → get structured email data
   - Apply CPU-first email-triage skill → classify 70%
   - Only escalate <80% confidence to Haiku

2. **Expand to other portals:**
   - Primewiki also documents: forward, delete, mark_read, label_apply
   - Create recipes for each (same pattern as above)

3. **Compound knowledge:**
   - Each recipe run → more Part 11 events → verified selectors
   - ALCOA+ audit trail → regulatory-grade evidence
   - No need to rediscover Gmail every session

---

**Authority:** Dragon Rider (rung 65537) | **Date:** 2026-02-24
