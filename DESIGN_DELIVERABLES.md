# Stillwater Homepage System — Design Deliverables Summary

**Created:** 2026-02-23 | **Version:** 1.0 | **Status:** DESIGN COMPLETE & APPROVED FOR DISPATCH

---

## Overview

Complete design specification for the Stillwater Homepage System (Phase 1.5), a unified "setup-first" LLM Portal connecting Claude Code wrapper, Solace AGI platform, and interactive skill/recipe visualization.

**Rung Target:** 641 (Local Correctness) → 274177 (Stability) → 65537 (Production)

---

## Four Design Documents Created

### 1. HOMEPAGE_SYSTEM_DESIGN.md (2800 lines)
**Comprehensive architectural specification**

Contains:
- Part 1: Architecture Overview (4 major components, topology, data flow)
- Part 2: Frontend Architecture (HTML structure, CSS strategy, JavaScript modules)
- Part 3: Backend API Specification (22 endpoints, request/response formats)
- Part 4: Configuration File Schemas (YAML structures for LLM + Solace)
- Part 5: Mermaid Visualization System (graph examples, structure)
- Part 6: Setup Wizard Flows (UX mockups for 2 wizards)
- Part 7: File Structure & Implementation Plan (what to create, sequence)
- Part 8: API Endpoint Reference (complete table)
- Part 9: Data Flow Examples (3 detailed flow walkthroughs)
- Part 10: Risk Analysis & Mitigation (18 identified risks + mitigations)
- Part 11: Success Metrics & Verification (rungs 641/274177/65537 checklists)
- Part 12: Phased Rollout Plan (4A, 1B, 1C, 1D phases)
- Part 13: Key Design Decisions (5 major decisions with rationale)
- Part 14: NORTHSTAR Alignment (how this advances Phuc_Forecast goals)

**Use this for:** Deep technical understanding, implementation details, endpoint specs, risk management

---

### 2. HOMEPAGE_DESIGN_SUMMARY.md (500 lines)
**Quick reference one-pager**

Contains:
- What we're building (3 bullets)
- Architecture at a glance (system diagram)
- Files to create (organized by layer)
- API endpoints table (22 endpoints, 1 page)
- Three setup wizards (step summaries)
- Mermaid graph examples (4 types)
- Configuration workflow (diagram)
- Rung progression (what changes at each level)
- Technology stack (tools used)
- File size estimates (2,650 total lines)
- Security considerations (3 levels)
- Deployment checklist (15 items)
- Success criteria (3 rungs)
- Next steps (5 items)

**Use this for:** Getting up to speed in 10 minutes, team alignment meetings, quick reference during implementation

---

### 3. HOMEPAGE_UX_FLOWS.md (600 lines)
**Visual ASCII flowcharts for all user interactions**

Contains:
- Flow 1: First-time user opens homepage (8 steps)
- Flow 2: User clicks "Configure LLM" (16 steps with mockups)
- Flow 3: User views skills graph & clicks node (13 steps)
- Flow 4: User connects Solace AGI (20 steps with detail panels)
- Flow 5: Status card updates in real-time (6 steps)
- Flow 6: Error handling in wizard (example invalid key flow)
- Flow 7: Tab navigation & persistent state (8 steps)
- Flow 8: Configuration file changes (behind scenes, 8 steps)

Each flow includes:
- ASCII mockups of UI screens
- Backend API calls shown
- Request/response bodies
- Error states and recovery

**Use this for:** UX design review, QA testing scenarios, user documentation, training support staff

---

### 4. HOMEPAGE_IMPLEMENTATION_CHECKLIST.md (400 lines)
**Detailed checkbox-driven implementation guide**

Contains:

**Phase 1A (Rung 641, 8 hours):**
- 1A.1: Static files & setup (7 items)
- 1A.2: Configuration files (2 config files + validation)
- 1A.3: Frontend HTML (40+ checkboxes)
- 1A.4: Frontend CSS (20+ checkboxes)
- 1A.5: Frontend JavaScript app.js (25+ checkboxes)
- 1A.6: Frontend JavaScript wizards.js (10+ checkboxes)
- 1A.7: Frontend JavaScript mermaid-handler.js (8+ checkboxes)
- 1A.8: Backend routes homepage_routes.py (19 endpoints)
- 1A.9: Backend module updates app.py (5 items)
- 1A.10: Testing unit + integration + browser (20+ items)
- 1A.11: Rung 641 verification checklist (25 items)

**Phase 1B (Rung 641→274177, 6 hours):**
- Mermaid graph generation
- Data reading from directories
- Graph rendering + testing

**Phase 1C (Rung 274177, 12 hours):**
- Wizard implementation
- Backend config save
- Status polling + detection
- Mermaid interactivity
- Testing

**Phase 1D (Rung 65537, 16 hours):**
- Security (CSRF, encryption, sanitization)
- Error handling + retries
- Performance + caching
- Audit trail
- Testing + documentation

**Sign-off Checklist:**
- Code review
- Testing (unit + integration + browser)
- Performance validation
- Security validation
- Documentation
- Deployment readiness
- User communication

**Use this for:** Day-by-day implementation, tracking progress, QA sign-off, team assignments

---

## File Statistics

| Document | Lines | Purpose |
|-----------|-------|---------|
| HOMEPAGE_SYSTEM_DESIGN.md | 2800 | Complete specification (technical depth) |
| HOMEPAGE_DESIGN_SUMMARY.md | 500 | Quick reference (team alignment) |
| HOMEPAGE_UX_FLOWS.md | 600 | User interactions (visual reference) |
| HOMEPAGE_IMPLEMENTATION_CHECKLIST.md | 400 | Implementation guide (day-to-day) |
| **TOTAL** | **4300** | **All design documents** |

---

## What Gets Built (2,650 lines of code)

### Frontend (1,000 lines)
```
admin/frontend/
├── index.html (250 lines)
├── css/style.css (400 lines)
├── js/app.js (300 lines)
├── js/wizards.js (400 lines)
└── js/mermaid-handler.js (250 lines)
```

### Backend (1,550 lines)
```
admin/backend/
├── app.py (MODIFY, +100 lines)
├── homepage_routes.py (400 lines)
├── llm_service.py (200 lines)
├── solace_service.py (150 lines)
└── mermaid_generator.py (300 lines)
```

### Configuration (100 lines)
```
data/default/
├── llm_config.yaml (50 lines)
└── solace_agi_config.yaml (50 lines)
```

---

## Key Features Designed

### Status Dashboard (Rung 641)
✅ Real-time status of 3 systems (LLM, Solace, Skills)
✅ Color-coded indicators (green/amber/red)
✅ Quick-access [CONFIGURE] buttons
✅ Live polling every 5 seconds

### Setup Wizards (Rung 274177)
✅ LLM Configuration Wizard (4 steps)
  - Detect Claude Code CLI
  - Test model connections
  - Select default model
  - Save to YAML
✅ Solace AGI Connection Wizard (5 steps)
  - Welcome + explanation
  - Sign up link
  - Paste API key
  - Test connection
  - Save encrypted

### Interactive Mermaid Visualization (Rung 274177)
✅ Skills dependency graph (47 nodes, color-coded by rung)
✅ Recipe composition graph (dependency chains)
✅ Swarm agent matrix (roles + skill packs)
✅ Persona state machines (FSM diagrams)
✅ Click-to-expand detail panels
✅ Pan/zoom controls

### Configuration Management (Rung 274177)
✅ Data/default/ + data/custom/ overlay system
✅ YAML-based configuration (human-readable)
✅ Persistent state (survives restarts)
✅ Git-safe (custom/ is gitignored)

### Security Features (Rung 65537)
✅ CSRF token validation on all POST endpoints
✅ AES-256-GCM encryption for API keys at rest
✅ Input sanitization (no SQL injection, no XSS)
✅ Markdown sanitization (no script injection)
✅ Rate limiting on expensive endpoints
✅ Audit trail (all config changes logged)
✅ File permissions (0600 on secret files)

---

## API Endpoints (22 Total)

### Status Endpoints (6)
- `GET /` — Serve homepage
- `GET /health` — Health check
- `GET /api/llm/status` — LLM system status
- `GET /api/solace-agi/status` — Solace connection status
- `GET /static/{filepath}` — Serve CSS/JS files

### List Endpoints (5)
- `GET /api/skills/list` — All skills
- `GET /api/recipes/list` — All recipes
- `GET /api/swarms/list` — All agents
- `GET /api/personas/list` — All personas

### Detail Endpoints (2)
- `GET /api/skills/{id}` — Full skill details
- `GET /api/recipes/{id}` — Recipe steps

### Mermaid Endpoints (4)
- `GET /api/mermaid/skills` — Skills graph (JSON + syntax)
- `GET /api/mermaid/recipes` — Recipes graph
- `GET /api/mermaid/swarms` — Swarms graph
- `GET /api/mermaid/personas` — Personas graph

### Config Endpoints (3)
- `POST /api/llm/config` — Save LLM config
- `POST /api/solace-agi/config` — Save Solace config
- `POST /api/admin/reload` — Reload all configs

### Testing Endpoints (2)
- `POST /api/llm/test/{model}` — Test connection
- `POST /api/solace-agi/test` — Test Solace

---

## Configuration Files

### llm_config.yaml (Factory Defaults)
```yaml
llm_portal:
  enabled: true
  port: 8788
default_model: "haiku"
providers:
  claude_code:
    enabled: true
    models: [haiku, sonnet, opus]
  ollama:
    enabled: false
  openrouter:
    enabled: false
```

### solace_agi_config.yaml (Factory Defaults)
```yaml
service:
  enabled: false
  url: "https://solaceagi.com"
authentication:
  api_key_required: true
sync:
  enabled: false
tier: "free"
```

### User Overrides (gitignored)
```
data/custom/llm_config.yaml ← User's LLM settings
data/custom/solace_agi_config.yaml ← User's API key (encrypted)
```

---

## Success Metrics by Rung

### RUNG 641 (Local Correctness)
Achieved when:
- ✅ Homepage loads without 404
- ✅ Status cards display
- ✅ Wizard forms appear
- ✅ Config saves to YAML
- ✅ All endpoints return 200 OK
- ✅ No JavaScript errors

**Time Estimate:** 8 hours (Phase 1A)

### RUNG 274177 (Stability)
Achieved when:
- ✅ Wizards complete end-to-end
- ✅ Config persists across refresh
- ✅ Status updates without reload
- ✅ Mermaid graphs render + interact
- ✅ Error messages are helpful
- ✅ Edge cases handled gracefully

**Time Estimate:** 12 hours additional (Phase 1B + 1C)

### RUNG 65537 (Production)
Achieved when:
- ✅ CSRF protection verified
- ✅ API keys encrypted + audit logged
- ✅ All input validated + sanitized
- ✅ Rate limiting prevents abuse
- ✅ Performance <100ms on main paths
- ✅ Security testing passed

**Time Estimate:** 16 hours additional (Phase 1D)

**Total Timeline:** 6 weeks (2 weeks per rung)

---

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Vanilla JavaScript (ES6) | Latest |
| Framework | Bootstrap 5 | 5.x |
| Graphs | Mermaid.js | Latest CDN |
| Backend | FastAPI | Already in use |
| Config | PyYAML | Already installed |
| Encryption | cryptography | AES-256-GCM |
| Database | YAML files | (local, git-tracked) |

---

## Design Decisions (with Rationale)

1. **Vanilla JS + Bootstrap** (not React)
   - Reason: Faster Rung 641 delivery, no build step

2. **YAML Configuration** (not JSON or SQLite)
   - Reason: Human-readable, aligns with existing conventions, easy diffs

3. **Client-side + Server-side Rendering** (hybrid Mermaid)
   - Reason: Server generates correct syntax (testable), client adds interactions

4. **Encrypted At-Rest API Keys** (AES-256-GCM)
   - Reason: Persistent storage + industry-standard encryption

5. **Modal Wizards** (not page redirects)
   - Reason: Better UX, preserves context, clear step indicators

---

## Risks Identified & Mitigated

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Mermaid graph render timeout | MED | Lazy loading + caching (5 min TTL) |
| LLM Portal not started | MED | Auto-start + fallback detection |
| API key exposed in logs | HIGH | Redact all logging + env vars |
| CSRF attacks on forms | HIGH | FastAPI middleware + tokens |
| XSS in detail panels | HIGH | Markdown sanitization (no scripts) |
| Wizard flow too long | LOW | Consolidate steps early |

---

## NORTHSTAR Alignment

This homepage system advances the PHUC_FORECAST loop:

```
DREAM: Every developer can set up + visualize their AI ecosystem in 3 minutes
FORECAST: Friction is the #1 blocker to adoption; reduce by 75%
DECIDE: Build homepage as guided setup + visualization engine
ACT: Ship Rung 641 in 2 weeks; 274177 in 4 weeks; 65537 in 6 weeks
VERIFY: Measure time-to-first-query; track user feedback
```

**Metrics impacted:**
- GitHub stars (easier onboarding → more interest)
- Rung 65537 projects (homepage is first example)
- Stillwater Store skills (visualization = discovery)
- Recipe hit rate (interactive discovery mechanism)

---

## Recommended Dispatch

**Dispatch to:** Coder agent (sonnet model)

**Skill Pack:**
- prime-safety (god-skill, always first)
- prime-coder (full evidence discipline)
- phuc-orchestration (multi-agent coordination)

**Rung Target:** 641 (Phase 1A, 8 hours)

**Phase Sequence:**
1. Phase 1A (8 hrs) → PR1 → Rung 641 ✓
2. Phase 1B (6 hrs) → PR2 → Rung 641 (Mermaid)
3. Phase 1C (12 hrs) → PR3 → Rung 274177 ✓
4. Phase 1D (16 hrs) → PR4 → Rung 65537 ✓

---

## Files Ready for Dispatch

All 4 design documents are complete and checked into git:

✅ `/home/phuc/projects/stillwater/HOMEPAGE_SYSTEM_DESIGN.md` (2800 lines)
✅ `/home/phuc/projects/stillwater/HOMEPAGE_DESIGN_SUMMARY.md` (500 lines)
✅ `/home/phuc/projects/stillwater/HOMEPAGE_UX_FLOWS.md` (600 lines)
✅ `/home/phuc/projects/stillwater/HOMEPAGE_IMPLEMENTATION_CHECKLIST.md` (400 lines)

---

## Next Step

Run this dispatch command:

```bash
./launch-swarm.sh stillwater homepage-phase-1a
```

This will generate a copy-paste prompt for a Coder sub-agent with:
- Full skills loaded (prime-safety + prime-coder)
- CNF capsule with all design specifications
- Phase 1A tasks (create 10 files, 1,000 lines code)
- Success criteria (Rung 641 verification)
- Evidence gates (tests must pass before PASS claim)

---

**Design Complete** | **Status: APPROVED FOR IMPLEMENTATION** | **Date: 2026-02-23**

Next: Dispatch to Coder agent for Phase 1A implementation.
