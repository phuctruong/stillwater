# Phase 1A Implementation Guide: Health Checks + Chat
**Coder Dispatch Sheet | Ready to Build**

**Rung Target:** 641 (Local Correctness)
**Time:** 2-3 hours
**Deliverables:** Health checks display + chat works + no wizard UI visible

---

## QUICK REFERENCE: WHAT TO BUILD

### 1. Simplify HTML (30 min)
**File:** `admin/frontend/index.html`

Remove:
```html
<!-- REMOVE THESE SECTIONS -->
<button class="btn-configure" onclick="openLLMWizard()">Configure</button>
<button class="btn-configure" onclick="openSolaceWizard()">Configure</button>

<!-- REMOVE TAB NAVIGATION -->
<div class="tab-navigation">
  <button data-tab="dashboard" onclick="switchTab('dashboard')">Dashboard</button>
  <button data-tab="skills" onclick="switchTab('skills')">Skills</button>
  ...
</div>

<!-- REMOVE TAB PANES FOR DASHBOARD (wizard area) -->
<!-- Keep only Skills, Recipes, Swarms, Personas tabs -->
```

Keep/Modify:
```html
<!-- HEALTH CHECKS SECTION (keep, make expandable) -->
<aside class="status-sidebar">
  <div class="status-card card-llm" id="cardLLM">
    <div class="status-dot llm"></div>
    <div class="status-content">
      <h6>🔌 LLM Portal</h6>
      <p class="status-text" id="llmStatus">Loading...</p>
      <p class="status-detail" id="llmDetail"></p>
      <!-- REMOVE BUTTON, ADD EXPANDABLE PANEL -->
    </div>
  </div>
  <!-- repeat for Solace, Orchestration -->
</aside>

<!-- MAIN CONTENT (keep chat, keep diagram tabs) -->
<main class="main-content">
  <!-- Keep chat interface -->
  <!-- Keep diagram tabs -->
</main>
```

### 2. Create health_routes.py (45 min)
**File:** `admin/backend/health_routes.py`

```python
"""
Health Check Endpoints
Routes for LLM, Solace, and Orchestration status
"""

from fastapi import APIRouter
from pydantic import BaseModel
import yaml
from pathlib import Path

router = APIRouter(prefix="/api", tags=["health"])

# ============================================================================
# PYDANTIC RESPONSE MODELS
# ============================================================================

class LLMHealthResponse(BaseModel):
    online: bool
    default_model: str | None = None
    config_path: str | None = None
    fallback_model: str | None = None
    message: str = ""

class SolaceAGIHealthResponse(BaseModel):
    configured: bool
    api_key_present: bool
    tier: str | None = None
    cloud_sync_enabled: bool = False
    message: str = ""

class OrchestrationHealthResponse(BaseModel):
    loaded: bool
    explorer_model: str | None = None
    builder_model: str | None = None
    arbiter_model: str | None = None
    message: str = ""

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

def get_repo_root() -> Path:
    """Get repository root path"""
    return Path(__file__).resolve().parents[2]

def load_yaml(path: Path) -> dict | None:
    """Load YAML file safely"""
    try:
        if not path.exists():
            return None
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return None

@router.get("/health/llm", response_model=LLMHealthResponse)
async def health_llm() -> LLMHealthResponse:
    """Check LLM Portal status"""
    repo_root = get_repo_root()

    # Check for llm_config.yaml (custom first, then default)
    custom_path = repo_root / "data" / "custom" / "llm_config.yaml"
    default_path = repo_root / "data" / "default" / "llm_config.yaml"

    config = load_yaml(custom_path) or load_yaml(default_path)

    if not config:
        return LLMHealthResponse(
            online=False,
            message="LLM config not found. See docs/CONFIGURE_STILLWATER.md"
        )

    # Extract config values
    default_model = config.get("default_model", "haiku")
    fallback_model = config.get("fallback_model", "sonnet")

    # TODO: Add actual LLM Portal health check (ping localhost:8788)
    # For now, assume online if config exists
    llm_online = True  # Replace with actual health check

    return LLMHealthResponse(
        online=llm_online,
        default_model=default_model,
        fallback_model=fallback_model,
        config_path=str(custom_path if custom_path.exists() else default_path),
        message=f"Ready with {default_model}"
    )

@router.get("/health/solace-agi", response_model=SolaceAGIHealthResponse)
async def health_solace_agi() -> SolaceAGIHealthResponse:
    """Check Solace AGI connection status"""
    repo_root = get_repo_root()

    # Check for solace_agi_config.yaml
    custom_path = repo_root / "data" / "custom" / "solace_agi_config.yaml"
    default_path = repo_root / "data" / "default" / "solace_agi_config.yaml"

    config = load_yaml(custom_path) or load_yaml(default_path)

    if not config:
        return SolaceAGIHealthResponse(
            configured=False,
            api_key_present=False,
            message="Solace AGI not configured. Get API key from solaceagi.com"
        )

    # Check for API key
    api_key = config.get("api_key", "").strip()
    api_key_present = bool(api_key and api_key != "sk_...")

    if not api_key_present:
        return SolaceAGIHealthResponse(
            configured=False,
            api_key_present=False,
            message="API key not configured. Add to data/custom/solace_agi_config.yaml"
        )

    # Extract other config values
    auto_sync = config.get("auto_sync", False)
    tier = config.get("tier", "free")

    # TODO: Verify API key validity with solaceagi.com
    # For now, assume valid if present

    return SolaceAGIHealthResponse(
        configured=True,
        api_key_present=True,
        tier=tier,
        cloud_sync_enabled=auto_sync,
        message=f"Connected ({tier} tier)"
    )

@router.get("/health/orchestration", response_model=OrchestrationHealthResponse)
async def health_orchestration() -> OrchestrationHealthResponse:
    """Check Orchestration Triple Twin status"""
    repo_root = get_repo_root()

    # Check for orchestration.yaml
    custom_path = repo_root / "data" / "custom" / "orchestration.yaml"
    default_path = repo_root / "data" / "default" / "orchestration.yaml"

    config = load_yaml(custom_path) or load_yaml(default_path)

    if not config:
        return OrchestrationHealthResponse(
            loaded=False,
            message="Orchestration config not found"
        )

    # Extract Triple Twin roles
    explorer = config.get("explorer", {})
    builder = config.get("builder", {})
    arbiter = config.get("arbiter", {})

    explorer_model = explorer.get("model", "haiku")
    builder_model = builder.get("model", "sonnet")
    arbiter_model = arbiter.get("model", "sonnet")

    return OrchestrationHealthResponse(
        loaded=True,
        explorer_model=explorer_model,
        builder_model=builder_model,
        arbiter_model=arbiter_model,
        message=f"Loaded: {explorer_model} → {builder_model} → {arbiter_model}"
    )

@router.get("/health/all")
async def health_all():
    """Get all health checks at once"""
    llm = await health_llm()
    solace = await health_solace_agi()
    orch = await health_orchestration()

    return {
        "llm": llm.model_dump(),
        "solace_agi": solace.model_dump(),
        "orchestration": orch.model_dump(),
        "overall": "ok" if all([
            llm.online,
            solace.configured,
            orch.loaded
        ]) else "degraded"
    }
```

### 3. Create health-checker.js (45 min)
**File:** `admin/static/js/health-checker.js`

```javascript
/**
 * Health Checker — Poll and display system status
 * Updates health cards every 5 seconds
 */

class HealthChecker {
    constructor() {
        this.pollInterval = 5000; // 5 seconds
        this.pollTimer = null;
        this.lastStatus = {};
    }

    async start() {
        console.log("🏥 Health checker started");
        this.poll(); // Run immediately
        this.pollTimer = setInterval(() => this.poll(), this.pollInterval);
    }

    stop() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            console.log("🏥 Health checker stopped");
        }
    }

    async poll() {
        try {
            const response = await fetch("/api/health/all");
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            this.updateCards(data);
        } catch (error) {
            console.error("❌ Health check failed:", error);
            this.showError();
        }
    }

    updateCards(data) {
        // Update LLM Card
        this.updateLLMCard(data.llm);

        // Update Solace AGI Card
        this.updateSolaceCard(data.solace_agi);

        // Update Orchestration Card
        this.updateOrchCard(data.orchestration);

        // Store status
        this.lastStatus = data;
    }

    updateLLMCard(llm) {
        const card = document.getElementById("cardLLM");
        const statusDot = card.querySelector(".status-dot");
        const statusText = document.getElementById("llmStatus");
        const statusDetail = document.getElementById("llmDetail");

        if (llm.online) {
            statusDot.className = "status-dot llm online";
            statusText.textContent = `✅ LLM Connected`;
            statusText.style.color = "#2e7d32";

            const model = llm.default_model || "haiku";
            statusDetail.innerHTML = `
                <strong>${model.charAt(0).toUpperCase() + model.slice(1)} ready</strong><br/>
                <small>Portal: localhost:8788</small><br/>
                <button class="btn-hint" onclick="expandHealthPanel('llm')">How to configure →</button>
            `;
        } else {
            statusDot.className = "status-dot llm offline";
            statusText.textContent = `⚠️ LLM Not Ready`;
            statusText.style.color = "#f57c00";
            statusDetail.innerHTML = `
                <small>${llm.message}</small><br/>
                <button class="btn-hint" onclick="expandHealthPanel('llm')">Configure now →</button>
            `;
        }
    }

    updateSolaceCard(solace) {
        const card = document.getElementById("cardSolace");
        const statusDot = card.querySelector(".status-dot");
        const statusText = document.getElementById("solaceStatus");
        const statusDetail = document.getElementById("solaceDetail");

        if (solace.configured) {
            statusDot.className = "status-dot solace online";
            statusText.textContent = `✅ Solace AGI Ready`;
            statusText.style.color = "#2e7d32";

            const tier = solace.tier || "pro";
            statusDetail.innerHTML = `
                <strong>${tier.charAt(0).toUpperCase() + tier.slice(1)} tier</strong><br/>
                <small>Cloud sync: ${solace.cloud_sync_enabled ? 'Enabled' : 'Disabled'}</small><br/>
                <button class="btn-hint" onclick="expandHealthPanel('solace')">Settings →</button>
            `;
        } else {
            statusDot.className = "status-dot solace offline";
            statusText.textContent = `❌ Not Configured`;
            statusText.style.color = "#c62828";
            statusDetail.innerHTML = `
                <small>${solace.message}</small><br/>
                <button class="btn-hint" onclick="expandHealthPanel('solace')">Setup now →</button>
            `;
        }
    }

    updateOrchCard(orch) {
        const card = document.getElementById("cardSkills");
        const statusDot = card.querySelector(".status-dot");
        const statusText = document.getElementById("skillsStatus");
        const statusDetail = document.getElementById("skillsDetail");

        if (orch.loaded) {
            statusDot.className = "status-dot skills online";
            statusText.textContent = `✅ Orchestration Loaded`;
            statusText.style.color = "#2e7d32";

            statusDetail.innerHTML = `
                <strong>Triple Twin Active</strong><br/>
                🔍 ${orch.explorer_model} → 🔨 ${orch.builder_model} → ⚖️ ${orch.arbiter_model}<br/>
                <button class="btn-hint" onclick="expandHealthPanel('orch')">Customize →</button>
            `;
        } else {
            statusDot.className = "status-dot skills offline";
            statusText.textContent = `⚠️ Not Loaded`;
            statusText.style.color = "#f57c00";
            statusDetail.innerHTML = `
                <small>${orch.message}</small><br/>
                <button class="btn-hint" onclick="expandHealthPanel('orch')">Setup →</button>
            `;
        }
    }

    showError() {
        // Show generic error state on all cards
        document.getElementById("llmStatus").textContent = "❌ Error";
        document.getElementById("solaceStatus").textContent = "❌ Error";
        document.getElementById("skillsStatus").textContent = "❌ Error";
    }
}

// Global instance
let healthChecker = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    healthChecker = new HealthChecker();
    healthChecker.start();
});

// Cleanup on page unload
window.addEventListener("beforeunload", () => {
    if (healthChecker) healthChecker.stop();
});

/**
 * Expand health panel with configuration hints
 */
function expandHealthPanel(system) {
    let panel = document.getElementById(`panel-${system}`);

    if (!panel) {
        panel = createHealthPanel(system);
        const card = getCardForSystem(system);
        card.appendChild(panel);
    }

    panel.style.display = panel.style.display === "none" ? "block" : "none";
}

function createHealthPanel(system) {
    const panel = document.createElement("div");
    panel.id = `panel-${system}`;
    panel.className = "health-panel";
    panel.style.display = "none";

    let content = "";
    switch (system) {
        case "llm":
            content = `
                <h6>How to Configure LLM</h6>
                <p><strong>Path:</strong> ~/.stillwater/llm_config.yaml</p>
                <pre><code>default_model: haiku
claude_code_enabled: true
auto_start_wrapper: true</code></pre>
                <p><small>See <a href="docs/CONFIGURE_STILLWATER.md#1-llm-setup" target="_blank">LLM Setup Guide</a></small></p>
            `;
            break;
        case "solace":
            content = `
                <h6>How to Configure Solace AGI</h6>
                <p><strong>Path:</strong> ~/projects/stillwater/data/custom/solace_agi_config.yaml</p>
                <p><strong>Steps:</strong></p>
                <ol>
                    <li>Get API key from <a href="https://solaceagi.com" target="_blank">solaceagi.com</a></li>
                    <li>Create config file with: <code>api_key: "sk_..."</code></li>
                    <li>Restart server: <code>./stillwater-server.sh restart</code></li>
                </ol>
                <p><small>See <a href="docs/CONFIGURE_STILLWATER.md#2-solace-agi-setup" target="_blank">Solace Setup Guide</a></small></p>
            `;
            break;
        case "orch":
            content = `
                <h6>How to Customize Orchestration</h6>
                <p><strong>Path:</strong> ~/projects/stillwater/data/custom/orchestration.yaml</p>
                <p><strong>Current Setup:</strong></p>
                <pre><code>explorer:
  model: haiku
  role: Scout
builder:
  model: sonnet
  role: Coder
arbiter:
  model: sonnet
  role: Skeptic</code></pre>
                <p><small>See <a href="docs/CONFIGURE_STILLWATER.md#3-orchestration-setup" target="_blank">Orchestration Guide</a></small></p>
            `;
            break;
    }

    panel.innerHTML = content;
    return panel;
}

function getCardForSystem(system) {
    const mapping = { "llm": "cardLLM", "solace": "cardSolace", "orch": "cardSkills" };
    return document.getElementById(mapping[system]);
}
```

### 4. Refactor app.css (30 min)
**File:** `admin/frontend/app.css`

Key changes:
```css
/* REMOVE: All wizard/form styles */
/* REMOVE: .wizard-card, .setup-wizards-container, .tab-navigation, etc. */

/* MODIFY: Health panel to be expandable */
.health-panel {
    margin-top: 12px;
    padding: 12px;
    background-color: #f5f5f5;
    border-radius: 4px;
    border-left: 4px solid #2196f3;
    display: none;
}

.health-panel h6 {
    margin: 0 0 8px 0;
    font-size: 14px;
    font-weight: 600;
}

.health-panel p {
    margin: 6px 0;
    font-size: 13px;
}

.health-panel pre {
    background-color: #1e1e1e;
    color: #d4d4d4;
    padding: 8px;
    border-radius: 4px;
    overflow-x: auto;
}

.health-panel code {
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 12px;
}

.btn-hint {
    background: none;
    border: none;
    color: #1976d2;
    cursor: pointer;
    text-decoration: underline;
    font-size: 12px;
    padding: 0;
}

.btn-hint:hover {
    color: #1565c0;
}

/* REMOVE: old wizard-card styles */
/* MODIFY: Make main content more prominent */
```

### 5. Update admin/app.py to register routes (20 min)
**File:** `admin/backend/app.py` (in create_app function)

```python
# Add these imports at top
from admin.backend.health_routes import router as health_router

# In create_app():
app.include_router(health_router)
```

### 6. Update admin/frontend/app.js (20 min)
**File:** `admin/frontend/app.js`

Remove:
```javascript
// DELETE these functions
function openLLMWizard() { ... }
function openSolaceWizard() { ... }
function openSkillsWizard() { ... }
function switchTab(tabName) { ... }
```

Keep all chat and status functions. They still work.

---

## TESTING CHECKLIST (Red → Green)

### 1. Test health endpoints (no UI)
```bash
# Terminal
curl http://localhost:8000/api/health/llm | jq .
curl http://localhost:8000/api/health/solace-agi | jq .
curl http://localhost:8000/api/health/orchestration | jq .
curl http://localhost:8000/api/health/all | jq .

# Expected responses:
# { "online": true, "default_model": "haiku", "config_path": "..." }
# { "configured": true, "api_key_present": true, "tier": "pro" }
# { "loaded": true, "explorer_model": "haiku", "builder_model": "sonnet", ... }
```

### 2. Test in browser
```
1. Load http://localhost:8000 in browser
2. Health cards should show:
   ✅ LLM Connected (with model name)
   ✅ Solace AGI Ready (with tier)
   ✅ Orchestration Loaded (with triple twin)

3. Click each card → expandable panel appears with config hints

4. Chat box should work:
   - Select swarm from dropdown
   - Type command: $ skills list
   - See response

5. No wizard UI visible anywhere

6. Console should have no errors (Ctrl+Shift+J)
```

### 3. Test expandable panels
```
1. Click health card → panel expands
2. Panel shows:
   - File path for configuration
   - Example YAML
   - Link to CONFIGURE_STILLWATER.md

3. Click again → panel collapses

4. All links should be clickable
```

### 4. Test responsive design
```
1. Resize browser to mobile (375px width)
2. Health cards should stack vertically
3. Chat box should be readable
4. No horizontal scrolling
```

---

## SUCCESS CRITERIA (GREEN TESTS)

```
✅ Health Endpoints
  [ ] GET /api/health/llm returns valid JSON
  [ ] GET /api/health/solace-agi returns valid JSON
  [ ] GET /api/health/orchestration returns valid JSON
  [ ] All responses include "message" field

✅ Health Cards in UI
  [ ] All 3 cards visible on page load
  [ ] Status dots show correct color (green = online, red = offline, yellow = degraded)
  [ ] Status text updates correctly
  [ ] Detail text shows relevant info (model name, tier, etc.)

✅ Expandable Panels
  [ ] Click card → panel expands with config hints
  [ ] Click again → panel collapses
  [ ] Panel content is readable
  [ ] Links are clickable

✅ Chat Interface
  [ ] Swarm dropdown populated with 6 roles
  [ ] Chat input works
  [ ] Chat output works
  [ ] Previous functionality preserved

✅ No Wizard UI
  [ ] No "Configure" buttons visible
  [ ] No form inputs visible
  [ ] No wizard steps visible
  [ ] No configuration tabs visible

✅ Code Quality
  [ ] No console errors
  [ ] No broken links
  [ ] No TypeErrors or undefined variables
  [ ] CSS loads correctly
  [ ] JavaScript loads correctly
```

---

## DELIVERABLES (What to Commit)

```
admin/backend/health_routes.py          NEW (~80 lines)
admin/static/js/health-checker.js       NEW (~200 lines)
admin/frontend/index.html               MODIFIED (remove wizard UI)
admin/frontend/app.css                  MODIFIED (remove wizard styles, add panel styles)
admin/frontend/app.js                   MODIFIED (remove wizard functions)
admin/backend/app.py                    MODIFIED (add health_routes import)
```

---

## GOTCHAS & SOLUTIONS

### Gotcha 1: YAML parsing fails
```
Problem: load_yaml() returns None
Solution: Check file path is correct, verify YAML syntax, check file permissions
```

### Gotcha 2: Status cards don't update
```
Problem: healthChecker.poll() doesn't run
Solution: Check DevTools console, verify fetch URL is correct, check CORS
```

### Gotcha 3: Expandable panels don't expand
```
Problem: Click button but panel doesn't show
Solution: Check CSS display property, verify button onclick handler, check element IDs match
```

### Gotcha 4: Config file not found errors
```
Problem: health endpoints return "not configured"
Solution: Create data/custom/[config-name].yaml files or verify data/default/ paths
```

---

## ROLLBACK PLAN (If Something Breaks)

```bash
# If something fails:

1. Restore old files from git:
   git checkout admin/frontend/index.html
   git checkout admin/frontend/app.css
   git checkout admin/frontend/app.js

2. Remove new files:
   rm admin/backend/health_routes.py
   rm admin/static/js/health-checker.js

3. Remove route registration from admin/backend/app.py

4. Restart server: python admin/server.py

5. Test: Load http://localhost:8000 (old UI should work)
```

---

## DONE CRITERIA

When all green tests pass AND no wizard UI is visible:
```
Commit with message:
  "feat: Phase 1A — Health checks + simplified chat interface (no wizards)"

Push to branch:
  git push origin feature/homepage-refactor-phase-1a

Next: Phase 1B (Mermaid diagrams) — separate 2-hour task
```

---

## QUESTIONS FOR CODER

1. **YAML parsing:** Should we handle `.template` files specially?
2. **Health polling:** OK to poll every 5 seconds, or too aggressive?
3. **Error handling:** If LLM Portal is offline, should health check fail or degrade?
4. **Expandable panels:** Should panels auto-close when another card is clicked?

---

## REFERENCES

- Main design: `/home/phuc/projects/stillwater/HOMEPAGE_REFACTOR_RADICAL_SIMPLIFICATION.md`
- Configuration guide (to link from panels): `/home/phuc/projects/stillwater/docs/CONFIGURE_STILLWATER.md`
- Current state: `/home/phuc/projects/stillwater/admin/frontend/index.html` (existing)

