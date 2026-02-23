# Stillwater Homepage — Implementation Checklist

**Use this document to track progress as you build the homepage system.**

---

## PHASE 1A: Core Homepage (Rung 641) — ~8 hours

### 1A.1 Static Files & Setup

- [ ] Create directory: `admin/frontend/`
- [ ] Create directory: `admin/frontend/css/`
- [ ] Create directory: `admin/frontend/js/`
- [ ] Create directory: `admin/frontend/templates/`
- [ ] Verify `data/default/` directory exists
- [ ] Verify `skills/` directory exists
- [ ] Verify `cli/recipes/` directory exists

### 1A.2 Configuration Files

- [ ] Create `data/default/llm_config.yaml`
  - [ ] Include factory defaults for Claude Code wrapper
  - [ ] Include model availability flags
  - [ ] Include port numbers + timeouts
  - [ ] Test: YAML syntax is valid (no parse errors)

- [ ] Create `data/default/solace_agi_config.yaml`
  - [ ] Include factory defaults (service disabled)
  - [ ] Include auth configuration (no API key)
  - [ ] Include feature flags
  - [ ] Test: YAML syntax is valid

### 1A.3 Frontend HTML (admin/frontend/index.html)

- [ ] Create base HTML5 document
- [ ] Add Bootstrap 5 CDN link
- [ ] Add Mermaid.js CDN link
- [ ] Create topbar section (logo + header)
  - [ ] Branding: "Stillwater Admin Dojo"
  - [ ] Status indicator (server clock)
  - [ ] Quick link buttons

- [ ] Create main layout (2 columns):
  - [ ] Left sidebar (25%, status cards)
  - [ ] Right main area (75%, content)

- [ ] Create 3 status cards:
  - [ ] LLM Portal card (placeholder)
  - [ ] Solace AGI card (placeholder)
  - [ ] Skills Ecosystem card (placeholder)
  - [ ] Each card has [CONFIGURE] button

- [ ] Create tab navigation bar:
  - [ ] Tab 1: Dashboard (default)
  - [ ] Tab 2: Skills
  - [ ] Tab 3: Recipes
  - [ ] Tab 4: Swarms
  - [ ] Tab 5: Personas

- [ ] Create tab pane containers:
  - [ ] `#tab-dashboard` - Setup wizards area
  - [ ] `#tab-skills` - Mermaid graph area
  - [ ] `#tab-recipes` - Mermaid graph area
  - [ ] `#tab-swarms` - Mermaid graph area
  - [ ] `#tab-personas` - Mermaid graph area

- [ ] Create placeholder wizard sections:
  - [ ] LLM configuration form (div)
  - [ ] Solace AGI configuration form (div)
  - [ ] No form logic yet (just HTML)

- [ ] Add script tags:
  - [ ] `<script src="/static/app.js"></script>`
  - [ ] `<script src="/static/wizards.js"></script>`
  - [ ] `<script src="/static/mermaid-handler.js"></script>`

- [ ] Test: Open `http://127.0.0.1:8000/` → page loads (no 404)
- [ ] Test: Inspect element → no broken links
- [ ] Test: Browser console → no errors

### 1A.4 Frontend CSS (admin/frontend/css/app.css)

- [ ] Create base stylesheet
- [ ] Define color palette:
  - [ ] Primary: #2563eb (Stillwater blue)
  - [ ] Success: #10b981 (green — online)
  - [ ] Warning: #f59e0b (amber — needs setup)
  - [ ] Error: #ef4444 (red — offline)

- [ ] Style topbar:
  - [ ] Fixed position, 60px height
  - [ ] Background color + logo
  - [ ] Status indicator styling

- [ ] Style main layout:
  - [ ] Sidebar: 300px fixed, scrollable
  - [ ] Main area: flexible, responsive

- [ ] Style status cards:
  - [ ] 250px min-width
  - [ ] Border-left 4px colored
  - [ ] Padding 20px
  - [ ] Shadow + hover effect
  - [ ] Status indicator (green/amber/red dot)

- [ ] Style tabs:
  - [ ] Horizontal nav bar
  - [ ] Underline on active tab
  - [ ] Hover effect

- [ ] Style forms (placeholder):
  - [ ] Input fields: 100% width, padding 10px
  - [ ] Buttons: 8px padding, 4px border-radius
  - [ ] Button hover state

- [ ] Style Mermaid containers:
  - [ ] `#mermaid-skills`, etc. — min 500px height
  - [ ] White background
  - [ ] Light gray border
  - [ ] Padding 20px

- [ ] Test: Page renders responsive (desktop + mobile)
- [ ] Test: All text readable (contrast check)
- [ ] Test: No layout shifts on tab switch

### 1A.5 Frontend JavaScript (admin/frontend/js/app.js)

- [ ] Create app.js with initialization logic
- [ ] Function: `initializeApp()`
  - [ ] Call `checkServerHealth()`
  - [ ] Call `fetchSystemStatus()`
  - [ ] Call `setupTabNavigation()`
  - [ ] Call `startPolling()`

- [ ] Function: `checkServerHealth()`
  - [ ] `GET /health`
  - [ ] Display server status in topbar
  - [ ] Handle timeout (show "Server offline" warning)

- [ ] Function: `fetchSystemStatus()`
  - [ ] `GET /api/llm/status`
  - [ ] `GET /api/solace-agi/status`
  - [ ] `GET /api/skills/list`
  - [ ] Update all 3 status cards with response data

- [ ] Function: `renderStatusDashboard(data)`
  - [ ] Populate LLM card: status, default_model, [CONFIGURE] button
  - [ ] Populate Solace card: status, tier, [CONFIGURE] button
  - [ ] Populate Skills card: count of skills loaded

- [ ] Function: `setupTabNavigation()`
  - [ ] Tab click handlers
  - [ ] Show/hide tab panes
  - [ ] Save active tab to localStorage
  - [ ] Restore tab on page reload

- [ ] Function: `startPolling()`
  - [ ] Set interval 5 seconds
  - [ ] Call `fetchSystemStatus()` in loop
  - [ ] Stop polling if user tabs away (use `visibilitychange` event)

- [ ] Function: `updateStatusCard(cardId, data)`
  - [ ] Animate color change (green/amber/red)
  - [ ] Update text content
  - [ ] Show loading indicator during fetch

- [ ] On page load:
  - [ ] Execute `initializeApp()`
  - [ ] Show loading spinner until data arrives

- [ ] Error handling:
  - [ ] Network error → show "Could not reach server"
  - [ ] Timeout error → show "Request timed out"
  - [ ] Missing data → show placeholder text

- [ ] Test: `console.log(initializeApp)` → function exists
- [ ] Test: Server responds to `/health` → status updates
- [ ] Test: Tab switching works (no page reload)
- [ ] Test: Polling continues (every 5 seconds)

### 1A.6 Frontend JavaScript Stubs (admin/frontend/js/wizards.js)

- [ ] Create wizards.js
- [ ] Create placeholder `LLMConfigWizard` class
  - [ ] Methods: `step1()`, `step2()`, `step3()`, `step4()`
  - [ ] Methods: `validate()`, `submit()` (no-op for now)
  - [ ] Return console.log("Wizard called") (testing only)

- [ ] Create placeholder `SolaceAGIWizard` class
  - [ ] Methods: `step1()`, `step2()`, `step3()`, `step4()`, `step5()`
  - [ ] Methods: `validate()`, `submit()` (no-op for now)

- [ ] Wire up wizard buttons:
  - [ ] Click event listeners for [CONFIGURE] buttons
  - [ ] Open modal on click
  - [ ] Show Step 1 (placeholder)

- [ ] Test: Click [CONFIGURE] button → modal opens with Step 1 HTML

### 1A.7 Frontend JavaScript Stubs (admin/frontend/js/mermaid-handler.js)

- [ ] Create mermaid-handler.js
- [ ] Function: `initMermaidGraphs()`
  - [ ] Initialize Mermaid.js from CDN
  - [ ] Set config: theme, security level, etc.

- [ ] Function: `renderSkillsGraph(graphData)`
  - [ ] Take Mermaid syntax from API response
  - [ ] Render into `#mermaid-skills` container
  - [ ] Test: console.log(graphData) (verify data arrives)

- [ ] Function: `registerMermaidClickHandlers()`
  - [ ] No-op for now (just placeholder)

- [ ] On page load:
  - [ ] Call `initMermaidGraphs()`
  - [ ] Mermaid library ready

- [ ] Test: Mermaid CDN loads (check Network tab)
- [ ] Test: No Mermaid errors in console

### 1A.8 Backend Routes (admin/backend/homepage_routes.py)

- [ ] Create `homepage_routes.py`
- [ ] Import necessary FastAPI, Pydantic, etc.

- [ ] Endpoint: `GET /` (serve homepage)
  - [ ] Return `FileResponse("admin/frontend/index.html")`
  - [ ] Set correct MIME type
  - [ ] Test: `curl http://127.0.0.1:8000/ | head -20`

- [ ] Endpoint: `GET /static/{filepath}` (serve CSS/JS)
  - [ ] Use FastAPI StaticFiles mount
  - [ ] Point to `admin/frontend/`
  - [ ] Test: `curl http://127.0.0.1:8000/static/app.js | head -5`

- [ ] Endpoint: `GET /api/llm/status` (stub)
  - [ ] Return: `{ "online": false, "available_models": [], ... }`
  - [ ] Test: `curl http://127.0.0.1:8000/api/llm/status`

- [ ] Endpoint: `GET /api/solace-agi/status` (stub)
  - [ ] Return: `{ "configured": false, "api_key_valid": false, ... }`
  - [ ] Test: `curl http://127.0.0.1:8000/api/solace-agi/status`

- [ ] Endpoint: `GET /api/skills/list` (stub)
  - [ ] Return: `{ "count": 0, "skills": [] }`
  - [ ] Test: `curl http://127.0.0.1:8000/api/skills/list`

- [ ] Endpoint: `GET /api/recipes/list` (stub)
  - [ ] Return: `{ "count": 0, "recipes": [] }`

- [ ] Endpoint: `GET /api/swarms/list` (stub)
  - [ ] Return: `{ "count": 0, "agents": [] }`

- [ ] Endpoint: `GET /api/personas/list` (stub)
  - [ ] Return: `{ "count": 0, "personas": [] }`

- [ ] Endpoint: `GET /api/mermaid/skills` (stub)
  - [ ] Return: `{ "graph_syntax": "graph TD\n A[Placeholder]", "nodes": [], "edges": [] }`

- [ ] Endpoint: `GET /api/mermaid/recipes` (stub)
- [ ] Endpoint: `GET /api/mermaid/swarms` (stub)
- [ ] Endpoint: `GET /api/mermaid/personas` (stub)

- [ ] Endpoint: `POST /api/llm/config` (stub)
  - [ ] Accept JSON body
  - [ ] Return: `{ "saved": true, "config_path": "..." }`
  - [ ] Test: `curl -X POST http://127.0.0.1:8000/api/llm/config -H "Content-Type: application/json" -d '{"default_model":"haiku"}'`

- [ ] Endpoint: `POST /api/solace-agi/config` (stub)
  - [ ] Accept JSON body with API key
  - [ ] Return: `{ "saved": true }`

### 1A.9 Backend Module Updates (admin/app.py)

- [ ] Import new route module: `from admin.backend.homepage_routes import router as homepage_router`
- [ ] Mount static files: `app.mount("/static", StaticFiles(...), name="static")`
- [ ] Include router: `app.include_router(homepage_router)`
- [ ] Update CORS if needed to allow localhost requests
- [ ] Test: `python -m admin.app` → server starts without errors

### 1A.10 Testing (Rung 641)

**Unit Tests:**
- [ ] Test: `admin/frontend/index.html` is valid HTML (w3c validator)
- [ ] Test: `admin/frontend/css/app.css` is valid CSS (no parse errors)
- [ ] Test: `admin/frontend/js/app.js` loads without syntax errors
- [ ] Test: `admin/backend/homepage_routes.py` imports without errors

**Integration Tests:**
- [ ] Test: `GET http://127.0.0.1:8000/` → 200 OK, HTML returned
- [ ] Test: `GET http://127.0.0.1:8000/static/app.js` → 200 OK, JS returned
- [ ] Test: `GET http://127.0.0.1:8000/static/app.css` → 200 OK, CSS returned
- [ ] Test: `GET http://127.0.0.1:8000/health` → 200 OK
- [ ] Test: `GET http://127.0.0.1:8000/api/llm/status` → 200 OK, JSON returned
- [ ] Test: All 14 endpoints return 200 OK (no errors)

**Browser Tests (Manual):**
- [ ] Open `http://127.0.0.1:8000/` in Chrome
- [ ] Inspect element → no red 404 errors in Console
- [ ] Check Network tab → all files load (200 OK)
- [ ] Check that page is responsive (inspect responsive mode)
- [ ] Check that tabs exist and switch
- [ ] Check that status cards display (even if empty)

### 1A.11 Rung 641 Verification

```
CHECKLIST: All items below must pass

Functionality:
☐ Homepage loads at http://127.0.0.1:8000/ (no 404)
☐ Page contains 3 status cards (LLM, Solace, Skills)
☐ Cards display placeholder status (even if no config)
☐ Dashboard tab is default
☐ Other 4 tabs exist and are clickable
☐ All 19 endpoints return HTTP 200
☐ /api/*/list endpoints return empty arrays (not errors)
☐ /api/mermaid/* endpoints return Mermaid syntax

Data Structure:
☐ data/default/llm_config.yaml exists + is valid YAML
☐ data/default/solace_agi_config.yaml exists + is valid YAML
☐ Endpoints return JSON with expected fields
☐ No missing required fields

Error Handling:
☐ Missing data → graceful fallback (not crash)
☐ Endpoint timeout → shows message (not hang)
☐ Invalid JSON request → 400 error

Security (Rung 641 baseline):
☐ No API keys in HTML source code
☐ No secrets in API responses
☐ No stack traces in error messages

Performance:
☐ Page loads in <3 seconds (cold start)
☐ Status polling doesn't block UI
☐ Tabs switch instantly (no lag)

Code Quality:
☐ Zero JavaScript syntax errors (DevTools console)
☐ Zero Python import errors
☐ All filenames follow convention (app.js, llm_service.py)
☐ File structure matches HOMEPAGE_SYSTEM_DESIGN.md

Documentation:
☐ Functions have docstrings (Python)
☐ Complex code sections have comments
☐ No hardcoded magic numbers
```

---

## PHASE 1B: Mermaid Integration (Rung 641→274177) — ~6 hours

### 1B.1 Implement Graph Generation (llm_service.py, solace_service.py, mermaid_generator.py)

- [ ] Create `admin/backend/llm_service.py`
- [ ] Create `admin/backend/solace_service.py`
- [ ] Create `admin/backend/mermaid_generator.py`

### 1B.2 Populate Data Reading

- [ ] Walk `skills/` directory, parse skill*.md files
- [ ] Extract: id, name, version, rung, dependencies
- [ ] Walk `cli/recipes/` directory, parse recipe*.md files
- [ ] Extract: id, name, version, skills_required
- [ ] Walk `admin/orchestration/` or similar for swarms
- [ ] Parse swarm agent roles + skill packs

### 1B.3 Mermaid Graph Generation

- [ ] Generate Mermaid syntax for skill dependency graph
  - [ ] Nodes: skill boxes with version + rung
  - [ ] Edges: "depends_on" relationships
  - [ ] Colors: green (641), blue (274177), orange (65537)

- [ ] Generate Mermaid syntax for recipe graph
- [ ] Generate Mermaid syntax for swarm matrix
- [ ] Generate Mermaid syntax for persona FSMs

### 1B.4 Test Mermaid Rendering

- [ ] Visit http://127.0.0.1:8000/#skills
- [ ] Graph renders (no Mermaid errors)
- [ ] Nodes have correct colors + labels
- [ ] Edges connect nodes correctly

---

## PHASE 1C: Wizard Interactivity (Rung 274177) — ~12 hours

### 1C.1 LLM Wizard Implementation

- [ ] Implement `LLMConfigWizard.step1()` - Detect Claude CLI
- [ ] Implement `LLMConfigWizard.step2()` - Test connections
- [ ] Implement `LLMConfigWizard.step3()` - Select model
- [ ] Implement `LLMConfigWizard.step4()` - Confirm + save
- [ ] Implement `LLMConfigWizard.validate()` - Input validation
- [ ] Implement `LLMConfigWizard.submit()` - POST /api/llm/config

### 1C.2 Solace AGI Wizard Implementation

- [ ] Implement all 5 steps (same pattern as LLM)
- [ ] Validate API key format (client + server)
- [ ] Test connection (`POST /api/solace-agi/test`)
- [ ] Encrypt API key before saving

### 1C.3 Backend Config Save

- [ ] Implement `POST /api/llm/config` handler
  - [ ] Validate input (enum check for model)
  - [ ] Write to `data/custom/llm_config.yaml`
  - [ ] Reload DataRegistry
  - [ ] Return 200 OK

- [ ] Implement `POST /api/solace-agi/config` handler
  - [ ] Validate API key format
  - [ ] Encrypt key using AES-256-GCM
  - [ ] Write to `data/custom/solace_agi_config.yaml`
  - [ ] Return 200 OK

### 1C.4 Status Polling Enhancement

- [ ] Implement actual LLM status detection
  - [ ] Try to connect to port 8788
  - [ ] Check if Claude Code CLI is installed
  - [ ] Return real status (not stub)

- [ ] Implement Solace AGI status detection
  - [ ] Read from `data/custom/solace_agi_config.yaml`
  - [ ] Check API key exists + is valid format
  - [ ] Return configured/unconfigured status

### 1C.5 Mermaid Interactivity

- [ ] Register click handlers on Mermaid nodes
- [ ] Implement detail panel show/hide
- [ ] Fetch skill details on node click
- [ ] Render skill markdown in detail panel

### 1C.6 Testing (Rung 274177)

- [ ] Test: Complete LLM wizard end-to-end
- [ ] Test: Config saves to YAML file
- [ ] Test: Page refresh shows saved config
- [ ] Test: Invalid input rejected with error
- [ ] Test: Status card updates after save
- [ ] Test: Solace wizard handles timeout gracefully

---

## PHASE 1D: Production Hardening (Rung 65537) — ~16 hours

### 1D.1 Security

- [ ] Add CSRF token generation + validation
- [ ] Implement AES-256-GCM encryption for API keys
- [ ] Sanitize all user input (no SQL injection, no XSS)
- [ ] Sanitize markdown before rendering (no `<script>` tags)

### 1D.2 Error Handling

- [ ] Add retry logic for network timeouts
- [ ] Implement exponential backoff for failed requests
- [ ] Add user-friendly error messages

### 1D.3 Performance

- [ ] Cache Mermaid graphs (5 minute TTL)
- [ ] Cache skill list (10 minute TTL)
- [ ] Lazy-load detail panels (don't fetch until clicked)
- [ ] Profile page load time, optimize bottlenecks

### 1D.4 Audit Trail

- [ ] Log all config changes with timestamp
- [ ] Store audit log in `data/audit/` (local only)
- [ ] Show audit log in admin UI

### 1D.5 Testing (Rung 65537)

- [ ] Run OWASP ZAP security scan
- [ ] Test SQL injection attempts (all should fail)
- [ ] Test XSS injection attempts (all should fail)
- [ ] Test CSRF attacks (all should fail)
- [ ] Verify API key encryption (decrypt + verify)
- [ ] Check audit log (all changes logged)

### 1D.6 Documentation

- [ ] Write README.md for admin/frontend/
- [ ] Add inline comments to all new functions
- [ ] Document API endpoints (FastAPI docs)
- [ ] Update data/README.md with config instructions

---

## PR CHECKPOINTS

### PR 1: Phase 1A (Rung 641)
- [ ] All files created + pass basic tests
- [ ] CI tests pass (pytest)
- [ ] No console errors
- [ ] PR title: "feat: Stillwater homepage Phase 1A (core layout, 641)"

### PR 2: Phase 1B (Rung 641→274177 - Mermaid)
- [ ] Mermaid graphs render correctly
- [ ] All graph types tested (skills, recipes, swarms, personas)
- [ ] PR title: "feat: Stillwater homepage Phase 1B (Mermaid graphs)"

### PR 3: Phase 1C (Rung 274177 - Wizards)
- [ ] Wizards complete end-to-end
- [ ] Config persists across refresh
- [ ] Error handling tested
- [ ] PR title: "feat: Stillwater homepage Phase 1C (wizard workflows, 274177)"

### PR 4: Phase 1D (Rung 65537 - Production)
- [ ] Security measures implemented + tested
- [ ] Audit trail working
- [ ] Performance optimized
- [ ] Full documentation
- [ ] PR title: "feat: Stillwater homepage Phase 1D (production hardening, 65537)"

---

## SIGN-OFF CHECKLIST

Before marking **COMPLETE**:

**Code Review:**
- [ ] Another developer reviewed all code
- [ ] No critical issues found
- [ ] Code style consistent with rest of project

**Testing:**
- [ ] All unit tests pass (`pytest admin/ -v`)
- [ ] All integration tests pass
- [ ] Manual QA: all flows tested in browser
- [ ] Browser compatibility: Chrome, Firefox, Safari

**Performance:**
- [ ] Page load time <3 seconds (cold start)
- [ ] Status polling doesn't cause memory leak
- [ ] Large graphs (100+ nodes) render in <2 seconds

**Security:**
- [ ] No secrets in code or logs
- [ ] API keys encrypted at rest
- [ ] CSRF protection enabled
- [ ] Input validation + sanitization passed
- [ ] Penetration testing passed (or scheduled)

**Documentation:**
- [ ] README.md complete
- [ ] API docs generated (FastAPI docs)
- [ ] UX flows documented
- [ ] Troubleshooting guide written

**Deployment:**
- [ ] Deployed to staging
- [ ] Tested in staging environment
- [ ] Ready for production merge

**User Communication:**
- [ ] Release notes written
- [ ] Users notified of new features
- [ ] Support team trained on new UI

---

**Version:** 1.0 | **Status:** READY FOR TEAM ASSIGNMENT
