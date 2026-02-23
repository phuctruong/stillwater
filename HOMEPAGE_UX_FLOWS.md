# Stillwater Homepage — UX Flow Diagrams

Visual walkthrough of all user interactions in the homepage system.

---

## FLOW 1: First-Time User Opens Homepage

```
┌─────────────────────────────────────────────────────────────────────┐
│ User opens http://127.0.0.1:8000/ in browser                       │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
                  ┌──────────────────────┐
                  │ Download index.html  │
                  │ Load Bootstrap CDN   │
                  │ Load Mermaid CDN     │
                  │ Load app.js + css    │
                  └──────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │ JavaScript app.js runs                   │
        │ (initializeApp function)                 │
        └─────────────────────────────────────────┘
        ↓           ↓           ↓           ↓
    GET /health  GET /api/    GET /api/    GET /api/
                 llm/status   solace-agi   skills/
                              /status      list
        ↓           ↓           ↓           ↓
     200 OK  ┌─────────────┐ 200 OK     200 OK
             │ Port 8788   │
             │ Not open    │
             │ Status:     │
             │ OFFLINE ⚠   │
             └─────────────┘

                    RENDERED DASHBOARD:
    ┌────────────────────────────────────────────────┐
    │  Stillwater Admin Dojo                         │
    │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
    │                                                │
    │  ┌─────────────────┐  ┌──────────────────┐  │
    │  │ 🔌 LLM Portal   │  │ ☁️  Solace AGI   │  │
    │  │ Status: OFFLINE │  │ Status: NOT SET  │  │
    │  │ ⚠ Not running   │  │ ⚠ Configure now  │  │
    │  │ [CONFIGURE]     │  │ [CONFIGURE]      │  │
    │  └─────────────────┘  └──────────────────┘  │
    │                                                │
    │  ┌──────────────────────────────────┐       │
    │  │ 📊 Skills Ecosystem              │       │
    │  │ Status: 47 skills loaded ✓       │       │
    │  │ [VIEW SKILLS]                    │       │
    │  └──────────────────────────────────┘       │
    │                                                │
    │  ┌──────────────────────────────────────┐   │
    │  │ Setup Wizards                        │   │
    │  │ ┌──────────────────────────────────┐ │   │
    │  │ │ ▶ Configure LLM Portal (Haiku)  │ │   │
    │  │ │ ▶ Connect to Solace AGI         │ │   │
    │  │ └──────────────────────────────────┘ │   │
    │  └──────────────────────────────────────┘   │
    │                                                │
    │  ┌──────────────────────────────────────┐   │
    │  │ Tabs: [ Skills ] [ Recipes ]        │   │
    │  │       [ Swarms ] [ Personas ]       │   │
    │  │                                     │   │
    │  │ (Mermaid graph render area)         │   │
    │  │                                     │   │
    │  └──────────────────────────────────────┘   │
    └────────────────────────────────────────────────┘
```

---

## FLOW 2: User Clicks "Configure LLM" Button

```
┌────────────────────────────────────┐
│ User clicks [CONFIGURE] on LLM card│
└────────────────────────────────────┘
             ↓
    ┌──────────────────────┐
    │ JavaScript opens     │
    │ wizard modal         │
    │ Show: Step 1 / 4    │
    └──────────────────────┘
             ↓
    ┌────────────────────────────────────┐
    │ ╔════════════════════════════════╗ │
    │ ║ LLM Configuration              ║ │
    │ ║ Step 1 of 4: Detect CLI        ║ │
    │ ╚════════════════════════════════╝ │
    │                                    │
    │ Checking for Claude Code CLI...   │
    │ (loading spinner) ...              │
    │                                    │
    │ ┌────────────────────────────────┐│
    │ │ ✓ Found                        ││
    │ │ Location: /usr/local/bin/claude││
    │ │ Version: 4.5-20251001          ││
    │ └────────────────────────────────┘│
    │                                    │
    │ Model compatibility:               │
    │ ✓ Haiku (claude-haiku-4-5)       │
    │ ✓ Sonnet (claude-sonnet-4)       │
    │ ✓ Opus (claude-opus-4-6)         │
    │                                    │
    │ [NEXT STEP] or [SKIP]             │
    └────────────────────────────────────┘
             ↓
    Backend: GET /api/llm/status
    Response: { "claude_code_wrapper": "not_running" }
             ↓
    ┌────────────────────────────────────┐
    │ ╔════════════════════════════════╗ │
    │ ║ LLM Configuration              ║ │
    │ ║ Step 2 of 4: Test Connections  ║ │
    │ ╚════════════════════════════════╝ │
    │                                    │
    │ ⏳ Testing Haiku...                 │
    │ ✓ Online (245ms latency)         │
    │                                    │
    │ ⏳ Testing Sonnet...                │
    │ ✓ Online (380ms latency)         │
    │                                    │
    │ ⏳ Testing Opus...                  │
    │ ⚠ Offline (timeout)              │
    │   (API may be rate-limited)      │
    │                                    │
    │ [NEXT STEP] or [RETRY]            │
    └────────────────────────────────────┘
      (Backend: POST /api/llm/test/{model} × 3)
             ↓
    ┌────────────────────────────────────┐
    │ ╔════════════════════════════════╗ │
    │ ║ LLM Configuration              ║ │
    │ ║ Step 3 of 4: Choose Default    ║ │
    │ ╚════════════════════════════════╝ │
    │                                    │
    │ Which model do you prefer?        │
    │                                    │
    │ ○ Haiku (⚡ fastest)              │
    │ ◉ Sonnet (⚡⚡ balanced)          │
    │ ○ Opus (⚡⚡⚡ most powerful)     │
    │                                    │
    │ Advanced options:                 │
    │ ☑ Auto-start wrapper on boot    │
    │ ☑ Enable model switching        │
    │                                    │
    │ [NEXT STEP] or [BACK]             │
    └────────────────────────────────────┘
             ↓
    ┌────────────────────────────────────┐
    │ ╔════════════════════════════════╗ │
    │ ║ LLM Configuration              ║ │
    │ ║ Step 4 of 4: Confirm & Save    ║ │
    │ ╚════════════════════════════════╝ │
    │                                    │
    │ Summary of your settings:         │
    │                                    │
    │ ┌────────────────────────────────┐│
    │ │ Default Model: Sonnet          ││
    │ │ CLI Path: /usr/local/bin/claude││
    │ │ Auto-start: Enabled            ││
    │ │ Config File: data/custom/      ││
    │ │             llm_config.yaml    ││
    │ └────────────────────────────────┘│
    │                                    │
    │ [SAVE] [BACK] [CANCEL]            │
    └────────────────────────────────────┘
             ↓
    Backend: POST /api/llm/config
    Request body:
    {
      "default_model": "sonnet",
      "auto_start_wrapper": true,
      "claude_code_enabled": true
    }
             ↓
    FastAPI validates + saves to:
    data/custom/llm_config.yaml
             ↓
    Response: 200 OK { "saved": true }
             ↓
    ┌────────────────────────────────────┐
    │ ╔════════════════════════════════╗ │
    │ ║ ✅ Success!                    ║ │
    │ ║ LLM Configuration Saved        ║ │
    │ ╚════════════════════════════════╝ │
    │                                    │
    │ Your settings have been saved:    │
    │ data/custom/llm_config.yaml       │
    │                                    │
    │ Next steps:                       │
    │ 1. Close this wizard             │
    │ 2. Status dashboard will update  │
    │ 3. Try asking Sonnet a question  │
    │                                    │
    │ [CLOSE] [VIEW CONFIG FILE]        │
    └────────────────────────────────────┘
             ↓
    Dashboard refreshes (polling):
    GET /api/llm/status
    Response: {
      "online": true,
      "default_model": "sonnet",
      "config_file": "data/custom/llm_config.yaml"
    }
             ↓
    Status card updates (green ✓)
```

---

## FLOW 3: User Views Skills Graph & Clicks Node

```
┌────────────────────────────────────┐
│ User clicks [Skills] tab           │
└────────────────────────────────────┘
             ↓
    Backend: GET /api/mermaid/skills
    Response:
    {
      "graph_syntax": "graph TD\n  A[Prime Safety] --> B...",
      "nodes": [
        { "id": "prime-safety", "label": "Prime Safety v2.1", "rung": 641 },
        { "id": "prime-coder", "label": "Prime Coder v2.0", "rung": 641 },
        ...
      ],
      "edges": [...]
    }
             ↓
    ┌────────────────────────────────────────────┐
    │ Tab Content: SKILLS ECOSYSTEM              │
    │ ──────────────────────────────────────────│
    │                                            │
    │  ┌────────────────────────────────────┐   │
    │  │ Mermaid Graph (rendered):          │   │
    │  │                                    │   │
    │  │     ┌──────────────┐              │   │
    │  │     │ Prime Safety │ (green)       │   │
    │  │     └──────┬───────┘              │   │
    │  │            ↓                      │   │
    │  │     ┌──────────────┐              │   │
    │  │     │ Prime Coder  │ (blue)       │   │
    │  │     └──────┬───────┘              │   │
    │  │            ↓                      │   │
    │  │     ┌──────────────┐              │   │
    │  │     │Phuc Forecast │ (orange)     │   │
    │  │     └──────────────┘              │   │
    │  │                                    │   │
    │  │  🔍 pan/zoom controls available   │   │
    │  │  (mouse wheel to zoom)            │   │
    │  └────────────────────────────────────┘   │
    │                                            │
    │  Status: 47 skills loaded                  │
    │  Total dependencies: 23                    │
    └────────────────────────────────────────────┘
             ↓
    User hovers over "Prime Safety" node
    (cursor changes to pointer)
             ↓
    User clicks on "Prime Safety" node
             ↓
    JavaScript: mermaid-handler.js
    Event: mermaidClick("prime-safety")
             ↓
    Backend: GET /api/skills/prime-safety
    Response:
    {
      "id": "prime-safety",
      "name": "Prime Safety",
      "version": "2.1.0",
      "rung": 641,
      "description": "God-skill: WINS ALL CONFLICTS...",
      "quick_load": "SKILL: prime-safety v2.1.0 — Fail-closed...",
      "content": "# prime-safety (god-skill)...",
      "depends_on": ["phuc-forecast"],
      "files_touched": ["skills/prime-safety.md"]
    }
             ↓
    ┌────────────────────────────────────────────┐
    │ DETAIL PANEL (right side):                 │
    │ ──────────────────────────────────────────│
    │                                            │
    │ 📚 Prime Safety v2.1.0                     │
    │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
    │                                            │
    │ Authority: system > dev > user > (none)   │
    │ Rung: 641 (Local Correctness) ✓           │
    │                                            │
    │ Quick Load (copy to skill pack):          │
    │ ┌────────────────────────────────────────┐│
    │ │ SKILL: prime-safety v2.1.0 —          ││
    │ │ Fail-closed safety...                  ││
    │ │ (11 lines shown)                       ││
    │ │                                        ││
    │ │ [COPY TO CLIPBOARD] [EXPAND]           ││
    │ └────────────────────────────────────────┘│
    │                                            │
    │ Dependencies:                              │
    │ → phuc-forecast (v1.2.0)                  │
    │                                            │
    │ Files:                                     │
    │ skills/prime-safety.md                    │
    │                                            │
    │ Description:                               │
    │ God-skill that wins all conflicts.        │
    │ Never weakened by any other skill.        │
    │ Fail-closed: prefer UNKNOWN over          │
    │ unjustified OK...                         │
    │                                            │
    │ [VIEW FULL] [CLOSE]                       │
    └────────────────────────────────────────────┘
             ↓
    User clicks [VIEW FULL]
             ↓
    ┌────────────────────────────────────────────┐
    │ Detail panel expands to show full markdown │
    │ User can scroll through skill content     │
    │ (500+ lines, skill definitions + rules)  │
    └────────────────────────────────────────────┘
             ↓
    User clicks on different node
             ↓
    Detail panel updates (smooth transition)
```

---

## FLOW 4: User Connects Solace AGI

```
┌──────────────────────────────────┐
│ User clicks [CONFIGURE] on        │
│ "☁️ Solace AGI" status card       │
└──────────────────────────────────┘
             ↓
    JavaScript opens modal with Step 1
             ↓
    ┌────────────────────────────────────┐
    │ ╔════════════════════════════════╗ │
    │ ║ Connect to Solace AGI          ║ │
    │ ║ Step 1 of 5: Welcome           ║ │
    │ ╚════════════════════════════════╝ │
    │                                    │
    │ Solace AGI is a hosted platform   │
    │ for sharing skills + recipes +    │
    │ running cloud agents              │
    │                                    │
    │ Key features:                     │
    │ ✓ Skill submission to Store      │
    │ ✓ Cloud sync + backup            │
    │ ✓ Recipe sharing + collaboration │
    │ ✓ Twin browser orchestration     │
    │                                    │
    │ Pricing:                          │
    │ • Free: Local only               │
    │ • $3/mo: Managed LLM             │
    │ • $19/mo: Pro (cloud sync)       │
    │ • $99/mo: Enterprise             │
    │                                    │
    │ [GET STARTED] [SKIP FOR NOW]     │
    └────────────────────────────────────┘
             ↓ (user clicks [GET STARTED])
    ┌────────────────────────────────────┐
    │ ╔════════════════════════════════╗ │
    │ ║ Connect to Solace AGI          ║ │
    │ ║ Step 2 of 5: Get API Key       ║ │
    │ ╚════════════════════════════════╝ │
    │                                    │
    │ First, you need an API key from  │
    │ solaceagi.com (takes 1 minute)   │
    │                                    │
    │ You'll receive a key like:        │
    │ sk_test_abc123xyz789...           │
    │                                    │
    │ ┌────────────────────────────────┐│
    │ │ [🔗 OPEN SOLACEAGI.COM]        ││
    │ │ (opens in new tab)             ││
    │ └────────────────────────────────┘│
    │                                    │
    │ Already have a key?               │
    │ [ALREADY HAVE KEY] [BACK]         │
    └────────────────────────────────────┘
             ↓ (user signs up at solaceagi.com, gets API key)
    User returns to browser & clicks [ALREADY HAVE KEY]
             ↓
    ┌────────────────────────────────────┐
    │ ╔════════════════════════════════╗ │
    │ ║ Connect to Solace AGI          ║ │
    │ ║ Step 3 of 5: Paste API Key     ║ │
    │ ╚════════════════════════════════╝ │
    │                                    │
    │ Paste your API key here:          │
    │ (will be encrypted before saving) │
    │                                    │
    │ ┌────────────────────────────────┐│
    │ │ sk_                            ││
    │ │ |cursor                        ││
    │ └────────────────────────────────┘│
    │                                    │
    │ [NEXT STEP] or [BACK]             │
    └────────────────────────────────────┘
      (Client validation: key must match sk_... format)
             ↓
    ┌────────────────────────────────────┐
    │ ╔════════════════════════════════╗ │
    │ ║ Connect to Solace AGI          ║ │
    │ ║ Step 4 of 5: Test Connection   ║ │
    │ ╚════════════════════════════════╝ │
    │                                    │
    │ Testing your API key...           │
    │                                    │
    │ ⏳ Validating key format...         │
    │ ✓ Format correct (sk_...)        │
    │                                    │
    │ ⏳ Connecting to solaceagi.com...   │
    │ ✓ Online (156ms latency)        │
    │                                    │
    │ ⏳ Verifying authentication...     │
    │ ✓ Key is valid (Pro tier)        │
    │                                    │
    │ ⏳ Checking available features... │
    │ ✓ Skill submission: enabled      │
    │ ✓ Cloud sync: enabled            │
    │ ✓ Twin browser: enabled          │
    │                                    │
    │ [NEXT STEP] [RETRY] [BACK]       │
    └────────────────────────────────────┘
      (Backend: POST /api/solace-agi/test)
             ↓
    ┌────────────────────────────────────┐
    │ ╔════════════════════════════════╗ │
    │ ║ Connect to Solace AGI          ║ │
    │ ║ Step 5 of 5: Confirm & Save    ║ │
    │ ╚════════════════════════════════╝ │
    │                                    │
    │ ✅ All checks passed!             │
    │                                    │
    │ Configuration summary:            │
    │                                    │
    │ Service: solaceagi.com            │
    │ Tier: Pro                         │
    │ API Key: sk_...✓ (encrypted)     │
    │ Features enabled: 3               │
    │                                    │
    │ Config will be saved to:          │
    │ data/custom/solace_agi_config.yaml│
    │ (API key is AES-256-GCM encrypted)│
    │                                    │
    │ [SAVE] [BACK] [CANCEL]            │
    └────────────────────────────────────┘
             ↓
    Backend: POST /api/solace-agi/config
    Request:
    {
      "api_key": "sk_...",
      "auto_sync": true,
      "tier": "pro"
    }
             ↓
    FastAPI:
    - Validates API key format
    - Encrypts key using AES-256-GCM
    - Saves to data/custom/solace_agi_config.yaml
    - Reloads config
             ↓
    Response: 200 OK { "saved": true }
             ↓
    ┌────────────────────────────────────┐
    │ ╔════════════════════════════════╗ │
    │ ║ ✅ Success!                    ║ │
    │ ║ Solace AGI Connected           ║ │
    │ ╚════════════════════════════════╝ │
    │                                    │
    │ Your Solace AGI account is ready! │
    │                                    │
    │ You can now:                      │
    │ ✓ Upload skills to Store         │
    │ ✓ Sync recipes to the cloud      │
    │ ✓ Run twin browser agents        │
    │ ✓ Collaborate with others        │
    │                                    │
    │ Next steps:                       │
    │ 1. Close this wizard             │
    │ 2. Go to Skills tab              │
    │ 3. Click "Upload to Store"       │
    │                                    │
    │ [CLOSE] [VIEW CONFIG]             │
    └────────────────────────────────────┘
             ↓
    Status card updates (dashboard polling):
    Solace AGI: CONNECTED ✓
```

---

## FLOW 5: Status Card Updates (Real-Time Polling)

```
┌────────────────────────────────────┐
│ User closes wizard, returns to      │
│ main dashboard                      │
└────────────────────────────────────┘
             ↓
    JavaScript starts polling:
    Every 5 seconds:
      GET /api/llm/status
      GET /api/solace-agi/status
      GET /api/skills/list (count only)
             ↓
    ┌────────────────────────────────────────┐
    │ Status Cards: BEFORE Config (⚠)        │
    │                                        │
    │ ┌─────────────────┐ ┌──────────────┐  │
    │ │ 🔌 LLM Portal   │ │ ☁️  Solace  │  │
    │ │ Status: OFFLINE │ │ Status: SET │  │
    │ │ ⚠ Not running   │ │ ✓ Connected │  │
    │ │ [CONFIGURE]     │ │             │  │
    │ └─────────────────┘ └──────────────┘  │
    │                                        │
    │ ┌──────────────────────────────────┐  │
    │ │ 📊 Skills: 47 loaded ✓           │  │
    │ └──────────────────────────────────┘  │
    └────────────────────────────────────────┘
             ↓ (polling continues...)
             ↓ (5 seconds pass...)
             ↓
    Backend: GET /api/llm/status
    (FastAPI reads data/custom/llm_config.yaml)
    (FastAPI checks if port 8788 is open)
    Response:
    {
      "online": true,
      "default_model": "sonnet",
      "config_file": "data/custom/llm_config.yaml"
    }
             ↓
    JavaScript receives response
    DOM update (CSS class change):
    .card-llm-status {
      border-left: 4px solid #10b981 (green)
      background: #f0fdf4
    }
             ↓
    ┌────────────────────────────────────────┐
    │ Status Cards: AFTER Config (✓)         │
    │                                        │
    │ ┌─────────────────┐ ┌──────────────┐  │
    │ │ 🔌 LLM Portal   │ │ ☁️  Solace  │  │
    │ │ Status: ONLINE  │ │ Status: SET │  │
    │ │ ✓ Sonnet        │ │ ✓ Connected │  │
    │ │ [TEST]          │ │             │  │
    │ └─────────────────┘ └──────────────┘  │
    │                                        │
    │ ┌──────────────────────────────────┐  │
    │ │ 📊 Skills: 47 loaded ✓           │  │
    │ └──────────────────────────────────┘  │
    └────────────────────────────────────────┘
             ↓ (polling continues every 5 seconds)
    No refresh needed — user sees live updates
```

---

## FLOW 6: Error Handling in Wizard

```
User enters wizard, provides invalid API key:
    "not_a_valid_key"
             ↓
    User clicks [NEXT STEP]
             ↓
    Client-side validation (app.js):
    if (key.match(/^sk_[a-z0-9]{48}$/)) {
      // OK, proceed to next step
    } else {
      // Show inline error
    }
             ↓
    ┌────────────────────────────────────┐
    │ Paste your API key:                │
    │                                    │
    │ ┌────────────────────────────────┐│
    │ │ not_a_valid_key                ││
    │ └────────────────────────────────┘│
    │                                    │
    │ ❌ Invalid format. API key must   │
    │    start with sk_ and contain    │
    │    48 lowercase hex characters   │
    │                                    │
    │ Example: sk_test... (copy from   │
    │ solaceagi.com)                   │
    │                                    │
    │ [NEXT STEP] [BACK]                │
    └────────────────────────────────────┘
             ↓
    User copies correct key, retries
             ↓
    Client-side validation passes
             ↓
    User clicks [NEXT STEP]
             ↓
    Backend: POST /api/solace-agi/test
    Timeout waiting for response (15 seconds)
             ↓
    Backend returns:
    503 Service Unavailable
    { "error": "solaceagi.com is not responding" }
             ↓
    ┌────────────────────────────────────┐
    │ ╔════════════════════════════════╗ │
    │ ║ Testing connection...          ║ │
    │ ║ Step 4 of 5: Test Connection   ║ │
    │ ╚════════════════════════════════╝ │
    │                                    │
    │ ⏳ Validating key format...         │
    │ ✓ Format correct                 │
    │                                    │
    │ ⏳ Connecting to solaceagi.com...   │
    │ ❌ Connection timeout (15s)       │
    │                                    │
    │ This usually means:               │
    │ • solaceagi.com is down          │
    │ • Your network is not responding │
    │ • Your API key is invalid        │
    │                                    │
    │ [RETRY] [BACK] [SKIP FOR NOW]     │
    └────────────────────────────────────┘
             ↓
    User clicks [RETRY]
    (connection succeeds on retry)
             ↓
    ✓ Continue to Step 5
```

---

## FLOW 7: Tab Navigation & Persistent State

```
User on Dashboard tab
             ↓
    Visible:
    - Status cards
    - Setup wizards
    - Polls every 5 seconds
             ↓
User clicks [Skills] tab
             ↓
    App state: { activeTab: "skills" }
    Browser history: #skills
             ↓
    Backend: GET /api/mermaid/skills
    Backend: GET /api/skills/list
    Render Mermaid graph
             ↓
    ┌────────────────────────────────┐
    │ Tabs: [ Skills ] ← current     │
    │       [ Recipes ]              │
    │       [ Swarms ]               │
    │       [ Personas ]             │
    │                                │
    │ Skills Ecosystem               │
    │ ─────────────────────────────  │
    │ (Mermaid graph renders here)   │
    │                                │
    │                                │
    └────────────────────────────────┘
             ↓
User clicks on "Prime Coder" node in graph
             ↓
    Detail panel appears (right side):
    - Shows skill content
    - "Copy to skill pack" button
    - Link to skill file
             ↓
User clicks [Recipes] tab
             ↓
    App state: { activeTab: "recipes" }
    Browser history: #recipes
    Detail panel closes
             ↓
    Backend: GET /api/mermaid/recipes
    Render recipe composition graph
             ↓
User closes browser and reopens tomorrow
             ↓
    Browser: history restored
    Tab is: [Recipes]
    Detail panel: closed (clean state)
    Polling: restarts automatically
```

---

## FLOW 8: Configuration File Changes (Behind Scenes)

```
Session 1: User configures LLM
    POST /api/llm/config
    Request: { "default_model": "sonnet" }
             ↓
    FastAPI: app.py middleware
    - Validates input (enum check)
    - Calls llm_service.save_config()
    - Writes to data/custom/llm_config.yaml:
      ──────────────────────────────
      llm_portal:
        enabled: true
        port: 8788
      default_model: sonnet
      ──────────────────────────────
    - Reloads DataRegistry
    - Returns 200 OK
             ↓
Session 2: User (tomorrow) opens homepage
    FastAPI startup:
    1. Load data/default/llm_config.yaml
    2. Load data/custom/llm_config.yaml (overlay)
    3. Merged config has:
       - default_model: "sonnet" (from custom)
       - All other settings from default
             ↓
    GET /api/llm/status
    Returns: { "default_model": "sonnet" }
             ↓
    Dashboard shows: "Default: Sonnet" ✓
    No re-setup needed
```

---

**All flows preserve user intent through:**
- Local data persistence (YAML files, gitignored custom/)
- Status polling (real-time updates)
- Clear error messages (friendly, actionable)
- Modal workflows (step-by-step guidance)
- Graph interactivity (visual exploration)

---

**Version:** 1.0 | **Status:** UX FLOWS COMPLETE
