# Stillwater Homepage System — Quick Reference Summary

**For detailed specifications, see: `HOMEPAGE_SYSTEM_DESIGN.md`**

---

## What Are We Building?

A unified **LLM Portal homepage** (http://127.0.0.1:8000/) that:
1. **Status Dashboard** — Shows LLM, Solace AGI, and Mermaid system health
2. **Setup Wizards** — Guides users through Claude Code + Solace AGI configuration
3. **Skill Explorer** — Interactive Mermaid graphs for skills, recipes, swarms, personas
4. **Configuration Manager** — Persistent YAML-based settings with defaults + overrides

---

## Architecture at a Glance

```
Browser (http://127.0.0.1:8000/)
    ↓
FastAPI Backend (admin/backend/app.py)
    ├→ LLM Portal (port 8788)
    ├→ Solace AGI (solaceagi.com)
    └→ Skill/Recipe Data (skills/, cli/recipes/)

Config Files (YAML):
    ├→ data/default/llm_config.yaml (factory defaults)
    ├→ data/default/solace_agi_config.yaml (factory defaults)
    ├→ data/custom/llm_config.yaml (user overrides, gitignored)
    └→ data/custom/solace_agi_config.yaml (user API key, encrypted, gitignored)
```

---

## What's New (Files to Create)

### Frontend (admin/frontend/)
```
index.html              — Main homepage (250 lines, Bootstrap layout)
css/style.css          — Styling (400 lines, color scheme + responsive)
js/app.js              — Main orchestrator (300 lines, initialization + polling)
js/wizards.js          — Form handlers (400 lines, validation + submission)
js/mermaid-handler.js  — Graph interaction (250 lines, click handlers + pan/zoom)
templates/llm-wizard.html    — LLM wizard form
templates/solace-wizard.html — Solace wizard form
```

### Backend (admin/backend/)
```
homepage_routes.py     — All new endpoints (400 lines)
llm_service.py         — LLM status + testing (200 lines)
solace_service.py      — Solace connection (150 lines)
mermaid_generator.py   — Graph generation (300 lines)

MODIFY:
admin/app.py           — Import route groups + serve /static/
```

### Configuration (data/default/)
```
llm_config.yaml              — Default LLM config
solace_agi_config.yaml       — Default Solace config (no API key)
```

---

## API Endpoints (22 total)

| Endpoint | Purpose | Auth | Rung |
|----------|---------|------|------|
| `GET /` | Serve homepage | None | 641 |
| `GET /health` | Health check | None | 641 |
| `GET /api/llm/status` | LLM system status | None | 641 |
| `GET /api/solace-agi/status` | Solace connection | None | 641 |
| `GET /api/skills/list` | List all skills | None | 641 |
| `GET /api/skills/{id}` | Skill details | None | 641 |
| `GET /api/recipes/list` | List all recipes | None | 641 |
| `GET /api/recipes/{id}` | Recipe details | None | 641 |
| `GET /api/swarms/list` | List agents | None | 641 |
| `GET /api/personas/list` | List personas | None | 641 |
| `GET /api/mermaid/skills` | Skills graph (Mermaid) | None | 641 |
| `GET /api/mermaid/recipes` | Recipes graph | None | 641 |
| `GET /api/mermaid/swarms` | Swarms graph | None | 641 |
| `GET /api/mermaid/personas` | Personas graph | None | 641 |
| `POST /api/llm/config` | Save LLM config | None | 641 |
| `POST /api/solace-agi/config` | Save Solace config | API key | 641 |
| `POST /api/llm/test/{model}` | Test model connection | None | 274177 |
| `POST /api/solace-agi/test` | Test Solace connection | API key | 274177 |
| `POST /api/admin/reload` | Reload configs | localhost | 274177 |

**Note:** No authentication required for reads (local-first design). API key required only for Solace sensitive operations (stores encryption key).

---

## Three Setup Wizards

### 1. LLM Configuration Wizard (4 steps)
1. **Detect** → Find Claude Code CLI installation
2. **Test** → Check haiku/sonnet/opus availability
3. **Select** → Choose default model + auto-start option
4. **Save** → Persist to `data/custom/llm_config.yaml`

### 2. Solace AGI Connection Wizard (5 steps)
1. **Welcome** → Explain what Solace AGI is
2. **Sign up** → Open solaceagi.com in new tab
3. **Paste API Key** → Validate format
4. **Test** → Verify connection + features
5. **Save** → Persist to `data/custom/solace_agi_config.yaml` (encrypted)

### 3. Mermaid Visualization (5 tabs, no wizard)
- **Tab 1 - Skills:** Dependency tree of all skill*.md files
- **Tab 2 - Recipes:** Composition graph showing recipe steps
- **Tab 3 - Swarms:** Agent dispatch matrix (which agent for which task)
- **Tab 4 - Personas:** State machine diagrams for each persona
- **Tab 5 - Dashboard:** Real-time status cards

---

## Mermaid Graph Examples

### Skills (Dependency Tree)
```
Graph: Nodes = skills, Edges = "depends_on"
Colors: Green (641), Blue (274177), Orange (65537)
Interactive: Click node → show skill details + markdown
```

### Recipes (Composition)
```
Graph: Nodes = recipes/steps, Edges = "requires"
Interactive: Click recipe → show step-by-step instructions
```

### Swarms (Agent Matrix)
```
Graph: Nodes = agent roles, Edges = "skill_pack"
Shows: Coder (sonnet) → [prime-safety, prime-coder]
       Planner (sonnet) → [prime-safety, phuc-forecast]
       Scout (haiku) → [prime-safety]
```

### Personas (FSM)
```
State machine: INIT → IDLE → LISTENING → THINKING → RESPONSE → IDLE
Colors: Current state = highlighted
Shows: All possible transitions + error handling
```

---

## Configuration Workflow

```
USER ACTION → BROWSER → FASTAPI → DATA FILES → BROWSER

1. User opens homepage
   → app.js initializes
   → GET /api/llm/status
   → Render status dashboard

2. User clicks "Configure LLM"
   → Open modal, show Step 1
   → User selects model
   → POST /api/llm/config
   → FastAPI saves data/custom/llm_config.yaml
   → Return success

3. User refreshes page
   → app.js reinitializes
   → GET /api/llm/status (reads overlay: data/custom/ + data/default/)
   → Dashboard shows saved config (no reentry needed)
```

---

## Rung Progression

### RUNG 641 (Local Correctness, 2 weeks)
✅ Page loads at http://127.0.0.1:8000/
✅ All status cards display
✅ Wizard forms appear (no validation)
✅ Config saves to YAML files
✅ All endpoints return 200 OK

**Test:** `pytest admin/backend/test_homepage.py -v`

### RUNG 274177 (Stability, 4 weeks)
✅ Wizards handle invalid input
✅ Config persists across refresh
✅ Status cards update via polling
✅ Mermaid graphs render + interact
✅ Error messages are helpful

**Test:** `pytest admin/tests/test_wizard_workflows.py -v`

### RUNG 65537 (Production, 6 weeks)
✅ CSRF tokens on all POST endpoints
✅ API key encrypted at rest (AES-256-GCM)
✅ Audit trail logs all config changes
✅ Input sanitization + XSS prevention
✅ Rate limiting on expensive endpoints

**Test:** `pytest admin/tests/test_security.py -v`

---

## Technology Stack

| Layer | Technology | CDN/Package |
|-------|-----------|-------------|
| Frontend | Vanilla JavaScript (ES6) | None (plain JS) |
| Styling | Bootstrap 5 | Bootstrap CDN |
| Graphs | Mermaid.js | Mermaid CDN |
| Backend | FastAPI | (already in use) |
| Database | YAML files | PyYAML (already installed) |
| Encryption | AES-256-GCM | cryptography package |

---

## File Size Estimates

| File | Lines | Complexity |
|------|-------|-----------|
| index.html | 250 | Low |
| style.css | 400 | Low |
| app.js | 300 | Medium |
| wizards.js | 400 | Medium |
| mermaid-handler.js | 250 | Medium |
| homepage_routes.py | 400 | Medium |
| llm_service.py | 200 | Medium |
| solace_service.py | 150 | Medium |
| mermaid_generator.py | 300 | Medium |
| **TOTAL** | **2,650** | **Medium** |

---

## Security Considerations

### Rung 641 (Minimal)
- ✅ No plaintext API keys in HTML/JavaScript
- ✅ No stack traces in error messages
- ✅ Input validation (both client + server)

### Rung 274177 (Enhanced)
- ✅ API key format validation
- ✅ Error handling for network timeouts
- ✅ No sensitive data in logs

### Rung 65537 (Production)
- ✅ **CSRF tokens** on all POST endpoints (FastAPI middleware)
- ✅ **AES-256-GCM encryption** for API keys at rest
- ✅ **Input sanitization** (no SQL injection, no XSS)
- ✅ **Markdown sanitization** (strip `<script>` tags)
- ✅ **Rate limiting** on expensive endpoints (5 tests/min)
- ✅ **Audit trail** (log all config changes)
- ✅ **File permissions** (data/custom/*.yaml chmod 0600)

---

## Deployment Checklist

Before shipping to production:

- [ ] All tests pass (`pytest admin/backend/test_app.py`)
- [ ] No console errors in Chrome DevTools
- [ ] No logs containing API keys (grep -r "sk_" .)
- [ ] File permissions set (chmod 0600 on secret files)
- [ ] CSRF tokens enabled on all POST routes
- [ ] Rate limiter active on /api/llm/test/{model}
- [ ] Encryption working (encrypt/decrypt test)
- [ ] Audit trail created for config changes
- [ ] Documentation complete (README.md updated)
- [ ] Security review passed (no XSS, no SQL injection)

---

## Success Criteria

**Rung 641 ✓**
- Homepage loads without 404
- Status cards display
- Wizards appear (no action required)
- No JavaScript errors

**Rung 274177 ✓**
- Wizards complete end-to-end
- Config persists across refresh
- Status updates without reload
- Error messages are helpful

**Rung 65537 ✓**
- CSRF protection verified
- API keys encrypted + audit logged
- All input validated + sanitized
- Rate limiting prevents abuse
- Performance <100ms on main paths

---

## Next Steps

1. **Read full design:** `HOMEPAGE_SYSTEM_DESIGN.md`
2. **Dispatch to Coder:** Use `phuc-orchestration` skill pack
3. **Phase 1A (641):** Create static files + stubs (8 hours)
4. **Phase 1B (641→274177):** Implement wizards (12 hours)
5. **Phase 1C (274177→65537):** Security + hardening (16 hours)

---

**Version:** 1.0 | **Status:** READY FOR IMPLEMENTATION | **Rung Target:** 641 → 274177 → 65537
