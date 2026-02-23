# REVISED: Stillwater Homepage System — Rails Philosophy Edition

## Key Corrections from Prior Design

### ✅ Architecture Corrections Applied
1. **NO direct Firestore**: Always via solaceagi.com API + API key
2. **CLI as glue wrapper**: Connects webservices, no deep work
3. **Convention-over-Configuration**: 80% convention, 20% configuration (Rails/Next.js style)
4. **Orchestration is ripple-able**: Users can override defaults without complex UX
5. **Homepage needs CLI chat**: Users talk to stillwater CLI from homepage
6. **Orchestration settings tab**: Show/customize Triple Twin orchestration

## Revised Major Components

### MAJOR ITEM 1: LLM Configuration (Unchanged)
- Claude Code wrapper (haiku/sonnet/opus)
- Default config in data/default/llm_config.yaml
- User overrides in data/custom/llm_config.yaml

### MAJOR ITEM 2: Solace AGI Connection (Unchanged)
- API key only
- All Firestore work happens at solaceagi.com (not here)
- Connection via API calls with auth header

### MAJOR ITEM 3: CLI Chat Interface (NEW)
- **Purpose**: Talk to stillwater CLI from browser
- **How it works**: 
  - Browser sends command to `/api/cli/execute`
  - Backend runs: `python -m stillwater.cli <command>` with args
  - Returns output as JSON
  - Streams responses for long-running commands
- **Example commands from UI**:
  - `stillwater skills list` → show all skills
  - `stillwater recipes list` → show recipes
  - `stillwater swarms available` → show agents
  - `stillwater orchestration show` → show current flow
  - Custom commands user types in chat box

### MAJOR ITEM 4: Orchestration Settings Tab (NEW)
- **Convention Model**: Triple Twin (default setup)
  - Explorer Twin (scout/research)
  - Builder Twin (coder/builder)
  - Arbiter Twin (skeptic/judge)
- **Display**: Mermaid graph showing roles + flow
- **Ripple**: Users can override:
  - Default model per role (haiku/sonnet/opus)
  - Priorities (which twin decides conflicts)
  - Custom roles added to data/custom/orchestration.yaml
- **Philosophy**: 80% convention (default Triple Twin works out of box)
  - 20% configuration (users can customize if needed)
  - NOT complex setup wizard - just show current + edit button

### MAJOR ITEM 5: Skills/Recipes/Swarms/Personas (Phase 1B)
- Read from files + display as Mermaid graphs
- Interactive node clicking
- View source, usage stats, dependencies
- This is Phase 1B work (after Phase 1A CLI chat + orchestration)

## Homepage Layout (Revised)

```
┌─────────────────────────────────────────┐
│  Stillwater — LLM Portal                 │
│  Triple Twin Orchestration Hub           │
└─────────────────────────────────────────┘

┌─ Status Dashboard ──────────────────────┐
│                                         │
│  ✅ LLM Ready (haiku)    🟡 Solace AGI   │  ✅ Orchestration
│  │ Configured                 │ Add key   │  │ Triple Twin active
│                                         │
└─────────────────────────────────────────┘

┌─ Main Content Area ─────────────────────┐
│                                         │
│  [CLI Chat]  [Orchestration]  [Skills] │  ← Tabs
│                                         │
│  CLI Chat Tab:                          │
│  ├─ Input: $ stillwater [command]      │
│  ├─ Output: JSON response               │
│  └─ History of recent commands          │
│                                         │
│  Orchestration Tab:                     │
│  ├─ Mermaid graph: Explorer→Builder→   │
│  │                    Arbiter flow      │
│  ├─ Current roles: haiku/sonnet/opus    │
│  ├─ Edit button: ripple custom settings │
│  └─ Show: conflicts, priorities         │
│                                         │
│  Skills Tab:                            │
│  ├─ Mermaid graph: skill dependencies   │
│  └─ (Phase 1B)                          │
│                                         │
└─────────────────────────────────────────┘

┌─ Footer ────────────────────────────────┐
│ Powered by Stillwater OS | Conv-over-Config │
└─────────────────────────────────────────┘
```

## Implementation Phases (Revised)

### Phase 1A: CLI Chat (Week 1 - 3 hours)
- Implement `/api/cli/execute` endpoint (runs `stillwater cli` command)
- HTML form: input field + send button
- Display output in scrollable div
- Basic command history

### Phase 1B: Orchestration Settings (Week 1 - 2 hours)
- Create `data/default/orchestration.yaml` (Triple Twin defaults)
- Render Mermaid graph of orchestration flow
- "Edit" button opens simple form to override roles/models
- Save to `data/custom/orchestration.yaml`

### Phase 1C: Skills/Recipes Tabs (Week 2 - 3 hours)
- Read from files and generate Mermaid graphs
- Node clicking shows details
- (Same as original design)

### Phase 1D: Security + Polish (Week 2 - 2 hours)
- Input validation on CLI commands (allowlist safe commands)
- API key encryption
- Audit logging for commands run

## API Endpoints (Revised)

**Core (unchanged)**:
- `GET /api/llm/status`
- `POST /api/llm/config`
- `GET /api/solace-agi/status`
- `POST /api/solace-agi/config`

**NEW: CLI Execution**:
- `POST /api/cli/execute`
  - Body: `{ "command": "skills list", "args": [...] }`
  - Returns: `{ "output": "...", "status": 0, "duration_ms": 123 }`

**NEW: Orchestration**:
- `GET /api/orchestration/status`
  - Returns current orchestration config + available twins
- `POST /api/orchestration/config`
  - Updates orchestration settings

**NEW: Mermaid Graphs**:
- `GET /api/mermaid/orchestration` → Returns Mermaid syntax for Triple Twin
- (Phase 1C) `GET /api/mermaid/skills` → Skill dependency graph
- (Phase 1C) `GET /api/mermaid/recipes` → Recipe composition graph

## Configuration Files (Revised)

**data/default/orchestration.yaml** (NEW):
```yaml
# Triple Twin Orchestration (Convention Over Configuration)
# This is the DEFAULT - users rarely need to change it

orchestration:
  name: "Triple Twin"
  description: "Explorer (scout) → Builder (coder) → Arbiter (skeptic)"
  
  twins:
    explorer:
      role: "scout"
      model: "haiku"
      responsibility: "Research, exploration, discovery"
      tools: ["web_search", "grep", "glob"]
    
    builder:
      role: "coder"
      model: "sonnet"
      responsibility: "Implementation, coding, building"
      tools: ["file_edit", "bash", "test_run"]
    
    arbiter:
      role: "skeptic"
      model: "sonnet"
      responsibility: "Verification, review, conflict resolution"
      tools: ["analysis", "comparison", "quality_check"]
  
  flow:
    - "explorer: research & discover"
    - "builder: implement based on findings"
    - "arbiter: verify & review"
    - "conflict_decision: arbiter wins on technical decisions"
  
  priorities:
    - "Safety always first (prime-safety skill)"
    - "Correctness over speed"
    - "Evidence over hopes"
```

**data/custom/orchestration.yaml** (USER OVERRIDE):
```yaml
# User customization (optional)
# Only add here if you want to override defaults

orchestration:
  twins:
    builder:
      model: "opus"  # Use bigger model instead of sonnet
    
    custom_twin:  # Add custom role
      role: "mathematician"
      model: "opus"
      responsibility: "Complex math and proofs"
```

## Phase 1A Implementation (Hours 1-3)

### File: admin/frontend/js/cli-chat.js (NEW)
```javascript
// CLI Chat Interface
// Users type: $ stillwater skills list
// Browser sends to /api/cli/execute
// Display output in chat window
```

### File: admin/backend/app.py (ADD ROUTE)
```python
@app.post("/api/cli/execute")
async def execute_cli_command(request: dict):
    """Execute stillwater CLI command from browser"""
    command = request.get("command", "")
    # Run: python -m stillwater.cli <command>
    # Return output as JSON
```

### File: admin/frontend/html (ADD TAB)
```html
<div class="tab-pane" id="cli-chat">
  <h3>Stillwater CLI Chat</h3>
  <div id="cli-output"></div>
  <input type="text" placeholder="$ stillwater ..." id="cli-input">
  <button onclick="executeCLI()">Send</button>
</div>
```

## Rails Philosophy Applied

1. **Convention**: Triple Twin is the default (works out of box)
2. **Configuration**: Users only override if needed (data/custom/)
3. **Simple UX**: One "Edit" button, not 10-step wizard
4. **Composable**: CLI commands + Mermaid graphs + settings tabs
5. **DRY**: Don't repeat UI for each command type
6. **Fat Models**: Backend does all work (CLI execution, Mermaid gen)
7. **Thin Views**: Frontend just displays + sends user input

## Success Criteria (Rung 641)

✅ Homepage loads at / with all tabs visible
✅ CLI Chat tab: Users can type `stillwater skills list` and see output
✅ Orchestration tab: Mermaid graph shows Triple Twin flow
✅ Edit button opens form to customize model/roles
✅ Configuration persists to data/custom/orchestration.yaml
✅ No 404 errors, no JavaScript console errors
✅ All API endpoints return proper JSON

---

**Next Steps**: Dispatch Phase 1A CLI Chat implementation to Coder agent
