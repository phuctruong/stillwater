# Stillwater Homepage — Mermaid-Interactive First Design

**Philosophy**: Let Mermaid diagrams drive the UX. Users click nodes to explore and configure.

**Status**: 🎯 Rung 641 Ready
**Date**: 2026-02-23

---

## Homepage Layout (Simple)

```
┌─────────────────────────────────────────────────┐
│ 🥋 Stillwater Software 5.0 Dojo                │
│ Linux for AI: Teach your AI Kung-fu             │
└─────────────────────────────────────────────────┘

┌─ Mermaid Orchestration Diagram ─────────────────┐
│                                                 │
│  [Explorer] ─────→ [Builder] ─────→ [Arbiter]  │
│   (haiku)          (sonnet)         (sonnet)    │
│   Hover: Info      Click: Drill     Click: Go   │
│                                                 │
│  Each node shows:                              │
│  - Role name + model                           │
│  - Status indicator                            │
│  - Hover tooltip with details                  │
│  - Click to view node details below            │
│                                                 │
└─────────────────────────────────────────────────┘

┌─ Node Details Panel ────────────────────────────┐
│ (Shown when node clicked in diagram)            │
│                                                 │
│ Explorer (Scout/Haiku)                         │
│ ════════════════════════════════════════       │
│ Type: CPU Webservice                           │
│ Model: haiku                                   │
│ Responsibility: Research, exploration          │
│                                                 │
│ [Show Algorithm Diagram]  [Test Examples]      │
│ [VSCode: Open config]     [Cute image]         │
│                                                 │
└─────────────────────────────────────────────────┘

┌─ CLI Chat (Anchored Bottom) ────────────────────┐
│ Swarm: [Orchestration ▼]                       │
│ Input: $ ___________________________            │
│ Output: [Terminal display]                     │
│ [Send] [Clear]                                 │
└─────────────────────────────────────────────────┘
```

---

## User Interactions

### 1. Initial Load
- Fetch `/api/orchestration/mermaid` → Get Mermaid syntax for current setup
- Render diagram with 3 nodes (Explorer, Builder, Arbiter)
- Display default node details (Explorer)
- CLI defaults to "Orchestration" swarm

### 2. Hover on Node
- Show tooltip:
  ```
  Explorer
  Scout / Haiku
  Research & discovery
  Status: Ready
  ```
- Highlight node in diagram

### 3. Click on Node
- Expand "Node Details Panel" below diagram
- Show different content based on node type:

#### If CPU Node (Explorer):
```
┌─ Explorer Details ──────────────┐
│ Type: CPU Webservice            │
│ Model: haiku                    │
│ Role: Scout (research)          │
│                                 │
│ Algorithm (Mermaid Diagram):    │
│ [Show CPU algorithm flow]       │
│                                 │
│ Code Location:                  │
│ - swarms/scout.md (persona)     │
│ - skills/prime-safety.md        │
│ - skills/phuc-forecast.md       │
│                                 │
│ [Open in VSCode] 🔧             │
│ $ code swarms/scout.md          │
│                                 │
│ Try These Examples:             │
│ $ curl /api/scout/execute       │
│   {"task": "research X"}        │
│                                 │
│ 🥋 [cute droplet image]         │
└─────────────────────────────────┘
```

#### If Swarm Node (Builder/Arbiter):
```
┌─ Builder Details ───────────────┐
│ Type: Swarm Webservice          │
│ Model: sonnet                   │
│ Role: Coder (implement)         │
│                                 │
│ Configuration:                  │
│ Model: sonnet                   │
│ Skills:                         │
│ - prime-safety                  │
│ - prime-coder                   │
│                                 │
│ [Open in VSCode] 🔧             │
│ $ code data/custom/orchestration.yaml
│                                 │
│ Try These Examples:             │
│ $ curl /api/coder/execute       │
│   {"task": "fix null check"}    │
│                                 │
│ 🥋 [cute droplet image]         │
└─────────────────────────────────┘
```

### 4. Click "Open in VSCode"
- Backend runs: `subprocess.Popen(["code", filename])`
- Opens VSCode with the config/swarm file
- User can edit directly
- On save, restart server to apply

### 5. CLI Swarm Selector
- Dropdown: [Orchestration ▼] shows:
  - Orchestration (default)
  - Explorer (scout)
  - Builder (coder)
  - Arbiter (skeptic)
- Selecting changes chat context
- Selected node highlighted in diagram above

---

## API Endpoints Required

### Mermaid & Status
```
GET /api/orchestration/mermaid
  Returns: Mermaid syntax for current orchestration
  Example: 
  ```
  graph LR
    A["Explorer<br/>haiku"]-->B["Builder<br/>sonnet"]-->C["Arbiter<br/>sonnet"]
  ```

GET /api/orchestration/node/{node_id}
  Returns: Details for clicked node
  {
    "name": "Explorer",
    "role": "scout",
    "model": "haiku",
    "type": "CPU",  // or "Swarm"
    "description": "Research & discovery",
    "config_path": "swarms/scout.md",
    "algorithm": "{mermaid syntax for algorithm}",
    "examples": ["command1", "command2"]
  }
```

### VSCode Integration
```
POST /api/vscode/open
  Request: {"file": "swarms/scout.md"}
  Action: Runs `code swarms/scout.md`
  Returns: {"success": true}
```

### CLI Execution (Already exists)
```
POST /api/cli/execute
  Request: {"command": "skills list"}
  Returns: JSON with output
```

---

## Files to Create

### New (Focused)
```
admin/static/
├── js/
│   ├── mermaid-interactive.js (new - 300 lines)
│   │   - Load diagram
│   │   - Handle hover/click
│   │   - Update node details
│   │   - CLI swarm selector
│   │
│   └── cli-chat.js (existing - keep as-is)
│
├── css/
│   ├── mermaid-interactive.css (new - 150 lines)
│   │   - Diagram styling
│   │   - Hover effects
│   │   - Node details panel
│   │
│   └── cli-chat.css (existing - keep as-is)
│
└── index.html (update - simple structure)
    └── 3 sections: Diagram, Details, Chat

admin/backend/
├── mermaid_routes.py (new - 80 lines)
│   - GET /api/orchestration/mermaid
│   - GET /api/orchestration/node/{id}
│
├── vscode_routes.py (new - 30 lines)
│   - POST /api/vscode/open
│
└── app.py (update - add route imports)
```

### To Delete (Move to scratch/)
```
All old design docs (already moved)
admin/frontend/js/wizards.js
admin/frontend/js/mermaid-handler.js
admin/frontend/templates/*
```

---

## Implementation Plan

### Phase 1: Mermaid Interactive (3 hours)
1. Update index.html (simple 3-section layout)
2. Create mermaid_routes.py (orchestration + node details)
3. Create mermaid-interactive.js (diagram + hover/click)
4. Create mermaid-interactive.css (styling)
5. Test: Click each node, see details panel

### Phase 2: VSCode Integration (1 hour)
1. Create vscode_routes.py
2. Add "Open in VSCode" button to details panel
3. Test: Click button → VSCode opens

### Phase 3: Refinement (1 hour)
1. Polish UI (spacing, colors, animations)
2. Add cute images to details panels
3. Final testing

**Total: 5 hours to Phase 1 working**

---

## Key Principles

✅ **Mermaid-First**: Diagrams are primary UI, not afterthought
✅ **Interactive**: Click to drill, not separate pages
✅ **Transparent**: See code, config, algorithms
✅ **Simple**: One page, three sections
✅ **Webservice-First**: All logic in APIs
✅ **Self-Hosting**: VSCode integration for power users

---

## Success Criteria (Rung 641)

✅ Homepage loads with diagram visible
✅ Hover shows tooltips
✅ Click shows node details (no errors)
✅ CLI swarm selector works
✅ Chat displays output
✅ No JavaScript console errors
✅ All mermaid diagrams render

---

**Next**: Dispatch Phase 1 to Coder agent with mermaid_routes.py template.

