# Stillwater Homepage — Multi-Page Architecture with DataTables + AmCharts

**Philosophy**: Simple pages, not tabs. Each page shows chat + reports + tables + diagrams in a single column, scrollable.

**Status**: 🎯 Rung 641 Ready
**Date**: 2026-02-23

---

## Pages (5 Total)

Each page has the same structure top-to-bottom:
1. **Chat Box** (at top) — Contextual for that page's mode
2. **AmCharts Report** — Metrics relevant to page (2-3 columns)
3. **DataTable** — Info table (2-3 columns) with sorting/filtering
4. **Mermaid Diagram** — Full-width diagram specific to page
5. **Instructions** — How to customize + VSCode links (cute droplet-kungfu logo)

### Page 1: Orchestration (Home/Default)
- **Chat**: "Ask orchestration questions or run commands"
- **Report**: Rung ladder progress, verification flow, recent tasks
- **DataTable**: Triple Twin status (Explorer, Builder, Arbiter - model, status, last run)
- **Mermaid**: Full Triple Twin diagram with detailed node info
- **Instructions**: "Click a node to configure. Open in VSCode: [Button with logo]"

### Page 2: Swarms Nodes
- **Chat**: "Ask a swarm to do something (coder, planner, skeptic, scout)"
- **Report**: Swarm success rate (%) by type, tokens used, cost, average latency
- **DataTable**: Swarm types (name, model, skills, recent results)
- **Mermaid**: Swarm dispatch diagram (when you ask → which swarm runs → output)
- **Instructions**: "Configure swarms in data/custom/orchestration.yaml"

### Page 3: CPU Nodes
- **Chat**: "Ask about algorithm performance, optimization ideas"
- **Report**: Algorithm latency (ms), throughput, error rate, memory usage
- **DataTable**: CPU algorithms (name, complexity, recent executions, avg time)
- **Mermaid**: Algorithm flowcharts (each CPU algo shown)
- **Instructions**: "Optimize algorithms in swarms/ or cli/src/"

### Page 4: LLM Settings
- **Chat**: "Ask to test a model, switch providers, configure"
- **Report**: Token usage ($), cost/day, model performance (accuracy %), uptime
- **DataTable**: Available models (model name, provider, tokens cost, active/inactive)
- **Mermaid**: LLM routing strategy (which model for which task)
- **Instructions**: "Edit llm_config.yaml to change providers and models"

### Page 5: Solace AGI Sync
- **Chat**: "Ask to sync data, check status, manage cloud"
- **Report**: Sync status (% complete), data uploaded (GB), firestore health, uptime
- **DataTable**: Sync logs (timestamp, action, status, bytes transferred)
- **Mermaid**: Sync flow diagram (local → API → firestore)
- **Instructions**: "Enable Firestore sync in data/custom/settings.md with API key"

---

## Frontend Architecture

### Libraries to Install
```html
<!-- DataTables: https://cdn.datatables.net/ -->
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css" />
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>

<!-- AmCharts: https://www.amcharts.com/ -->
<link rel="stylesheet" href="https://www.amcharts.com/lib/4/themes/animated.css" />
<script src="https://www.amcharts.com/lib/4/core.min.js"></script>
<script src="https://www.amcharts.com/lib/4/charts.min.js"></script>
<script src="https://www.amcharts.com/lib/4/themes/animated.js"></script>

<!-- Mermaid: Already loaded -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
```

### Navigation
- **Header Navigation**: Simple links to each page
  ```
  [Home] [Swarms] [CPU] [LLM] [Sync]
  ```
- **Full-Width Single Column** layout except:
  - Reports section: 2-3 columns (side-by-side charts)
  - DataTables: Can expand to 2-3 columns if needed
- **Responsive**: Mobile collapses to 1 column

### Page Structure (Each Page)
```
┌─────────────────────────────────────────┐
│ Header Navigation                       │
│ [Home] [Swarms] [CPU] [LLM] [Sync]     │
└─────────────────────────────────────────┘

┌─ Chat Box (Full Width) ─────────────────┐
│ Swarm: [Orchestration ▼]                │
│ Input: $ _________________________      │
│ Output: [Terminal]                      │
│ [Send] [Clear]                          │
└─────────────────────────────────────────┘

┌─ AmCharts Reports (2-3 Columns) ────────┐
│ [Chart 1]      [Chart 2]      [Chart 3] │
│ Metric A       Metric B       Metric C  │
└─────────────────────────────────────────┘

┌─ DataTable (2-3 Columns) ──────────────┐
│ [Table with sorting/filtering]          │
│ [Column 1] [Column 2] [Column 3]       │
└─────────────────────────────────────────┘

┌─ Mermaid Diagram (Full Width) ──────────┐
│ [Full-width diagram]                    │
└─────────────────────────────────────────┘

┌─ Instructions (Full Width) ─────────────┐
│ "How to customize this page:"           │
│ 1. Edit file: [VSCode link] 🥋          │
│ 2. Run command: $ ...                   │
│ [More help links]                       │
└─────────────────────────────────────────┘
```

---

## Backend Routes

### New Routes to Add

```python
# Navigation + Page Data
GET /api/pages
  Returns: {"pages": ["orchestration", "swarms", "cpu", "llm", "sync"]}

GET /api/page/{page_name}/data
  Returns: {
    "title": "Orchestration",
    "chat_prompt": "Ask orchestration...",
    "report_config": {...},  # AmCharts config
    "table_config": {...},   # DataTables config
    "diagram_mermaid": "...", # Mermaid syntax
    "instructions": [...]     # Help items
  }

# Reports Data
GET /api/page/{page_name}/metrics
  Returns: Current metrics for AmCharts (tokens, rung progress, etc)

# Instructions with VSCode links
POST /api/vscode/open
  Request: {"file": "data/custom/orchestration.yaml"}
  Returns: {"success": true}
```

---

## Files to Create/Modify

### New Files
```
admin/static/
├── js/
│   ├── pages.js (300 lines)
│   │   - Load page on navigation click
│   │   - Initialize DataTables
│   │   - Initialize AmCharts
│   │   - Render Mermaid diagrams
│   │   - Handle VSCode buttons
│   │
│   └── page-config.js (200 lines)
│       - Page definitions (title, routes, widgets)
│
├── css/
│   ├── pages.css (250 lines)
│   │   - Multi-column layout
│   │   - Chart styling
│   │   - Table styling
│   │   - Full-width sections
│   │   - Responsive design
│   │
│   └── responsive.css (100 lines)
│       - Mobile breakpoints
│
└── index-new.html (150 lines)
    - Simple header navigation
    - Main content area (dynamic)
    - Script imports
```

### Backend Routes
```
admin/backend/
├── pages_routes.py (200 lines)
│   - GET /api/pages
│   - GET /api/page/{name}/data
│   - GET /api/page/{name}/metrics
│   - POST /api/vscode/open
│
└── app.py (modified)
    - Import pages_routes
    - Register routes
```

---

## Implementation Plan

### Phase 2A: Libraries + Navigation (2 hours)
1. Update index.html with DataTables + AmCharts CDN links
2. Create header navigation (5 page links)
3. Create pages.js with page router
4. Create pages.css with multi-column layout
5. Test: Click each page link, page content changes

### Phase 2B: Backend Routes (1 hour)
1. Create pages_routes.py
2. Add GET /api/pages endpoint
3. Add GET /api/page/{name}/data endpoint
4. Add GET /api/page/{name}/metrics endpoint
5. Test: Fetch page data for each page

### Phase 2C: Page Content (3 hours)
1. Create sample data for each page
2. Initialize DataTables on each page
3. Initialize AmCharts reports on each page
4. Render Mermaid diagrams
5. Add instructions + VSCode buttons
6. Test: All pages load, tables sort, charts animate

### Phase 2D: VSCode Integration (1 hour)
1. Add vscode_routes.py with POST /api/vscode/open
2. Add VSCode buttons to each page
3. Test: Click button → opens VSCode with file

**Total: 7 hours**

---

## Sample AmCharts Reports per Page

### Orchestration Page
- **Rung Progress Bar**: 0→641→274177→65537 (current position)
- **Recent Tasks**: Line chart (tasks/day over time)
- **Verification Flow**: Pie chart (% of tasks in each rung)

### Swarms Page
- **Swarm Success Rates**: Column chart (haiku/sonnet/opus success %)
- **Token Usage**: Area chart (tokens/day by swarm)
- **Cost Breakdown**: Donut chart ($ by provider)

### CPU Page
- **Algorithm Performance**: Line chart (latency ms over time)
- **Throughput**: Column chart (requests/sec)
- **Resource Usage**: Gauge (CPU %, Memory %)

### LLM Page
- **Token Cost**: Line chart ($, cumulative)
- **Model Comparison**: Column chart (cost per task by model)
- **Uptime**: Gauge (% availability)

### Sync Page
- **Sync Status**: Gauge (% complete)
- **Data Volume**: Area chart (GB synced over time)
- **Firestore Health**: Status indicator + latency

---

## Success Criteria (Rung 641)

✅ 5 pages accessible via navigation
✅ Each page loads without errors
✅ Chat box works on each page
✅ DataTables display + sort/filter working
✅ AmCharts render without errors
✅ Mermaid diagrams render full-width
✅ VSCode buttons open files
✅ Instructions visible and helpful
✅ No console errors on any page
✅ Responsive layout (mobile-friendly)

---

**Next**: Dispatch Phase 2A-D to Coder agent for implementation.
