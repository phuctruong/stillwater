# Stillwater Admin System Architecture

## System Overview

The Stillwater Admin System is a multi-page web dashboard (running on port 8787) that provides:
1. Catalog management (skills, swarms, recipes, papers, community docs)
2. File editing (safe repo-wide text editing)
3. LLM configuration (Ollama setup, model selection, provider management)
4. Service registry (auto-discovery, health checking, service coordination)
5. CLI integration (safe allowlisted command execution)
6. Community linking (email-based auth, skill/recipe sync)

## High-Level Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend (Port 8787)"]
        UI["Web UI<br/>index.html"]
        Pages["5 Frontend Pages:<br/>- Orchestration<br/>- LLM Settings<br/>- Services<br/>- CPU Chat<br/>- Community"]
    end

    subgraph AdminServer["Admin Server (server.py)"]
        Handler["AdminHandler<br/>HTTP Request Router"]
        Catalog["_catalog()<br/>File Indexing"]
        FileOps["_file_payload()<br/>_save_file()<br/>_create_file()"]
        LLMOps["_llm_status()<br/>_update_llm_config()"]
        Community["_community_status()<br/>_community_link()<br/>_community_sync()"]
        CLI["_run_cli_command()"]
        SysOps["_install_ollama()<br/>_pull_ollama_model()"]
    end

    subgraph ServiceRegistry["Service Registry (registry.py)"]
        Registry["ServiceRegistry<br/>register()<br/>deregister()<br/>get()<br/>list_all()"]
        HealthCheck["health_check()"]
        Discovery["discover()"]
        Persistence["save()<br/>load()"]
    end

    subgraph Backends["External Services"]
        Ollama["Ollama<br/>Local LLM"]
        LLMPortal["LLM Portal :8788"]
        RecipeEngine["Recipe Engine :8789"]
        Evidence["Evidence Pipeline :8790"]
        OAuth3["OAuth3 Authority :8791"]
        CPUService["CPU Service :8792"]
        Browser["Browser DevTools :9222"]
    end

    UI --> Pages
    Pages -->|HTTP Requests| Handler

    Handler -->|Catalog Routes| Catalog
    Handler -->|File Routes| FileOps
    Handler -->|LLM Routes| LLMOps
    Handler -->|Community Routes| Community
    Handler -->|CLI Routes| CLI
    Handler -->|System Routes| SysOps
    Handler -->|Service Routes| Registry

    Registry --> HealthCheck
    Registry --> Discovery
    Registry --> Persistence

    Catalog --> FileOps
    LLMOps --> Ollama
    Discovery -->|Port Scan 8787-8792, 9222| Backends
    HealthCheck -->|HTTP Health Check| Backends
```

## Frontend Pages and API Integration

```mermaid
graph LR
    subgraph Pages["Frontend Pages"]
        Orch["Orchestration Page"]
        LLM["LLM Settings Page"]
        Svc["Services Page"]
        CPU["CPU Chat Page"]
        Comm["Community Page"]
    end

    subgraph CatalogAPI["Catalog API"]
        CatGet["/api/catalog<br/>GET"]
        FileGet["/api/file<br/>GET"]
        FileSave["/api/file/save<br/>POST"]
        FileCreate["/api/file/create<br/>POST"]
    end

    subgraph LLMAPI["LLM API"]
        LLMStatus["/api/llm/status<br/>GET"]
        LLMConfig["/api/llm/config<br/>POST"]
        OllamaInstall["/api/system/install-ollama<br/>POST"]
        OllamaPull["/api/ollama/pull<br/>POST"]
    end

    subgraph ServiceAPI["Service API"]
        SvcList["/api/services<br/>GET"]
        SvcRegister["/api/services/register<br/>POST"]
        SvcDeregister["/api/services/deregister<br/>POST"]
        SvcHealth["/api/services/{id}/health<br/>GET"]
        SvcDiscover["/api/services/discover<br/>POST"]
    end

    subgraph CLIAPI["CLI API"]
        CLIRun["/api/cli/run<br/>POST"]
        CLICmds["/api/cli/commands<br/>GET"]
    end

    subgraph CommunityAPI["Community API"]
        CommStatus["/api/community/status<br/>GET"]
        CommLink["/api/community/link<br/>POST"]
        CommSync["/api/community/sync<br/>POST"]
    end

    Orch --> CatGet
    Orch --> FileGet
    Orch --> FileSave
    Orch --> FileCreate
    Orch --> CLICmds

    LLM --> LLMStatus
    LLM --> LLMConfig
    LLM --> OllamaInstall
    LLM --> OllamaPull

    Svc --> SvcList
    Svc --> SvcRegister
    Svc --> SvcDeregister
    Svc --> SvcHealth
    Svc --> SvcDiscover

    CPU --> CLIRun
    CPU --> CLICmds

    Comm --> CommStatus
    Comm --> CommLink
    Comm --> CommSync
```

## Data Flow: Orchestration Page (Catalog Editing)

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant AdminServer
    participant FileSystem
    participant LLMPortal

    User->>Browser: Load Orchestration Page
    Browser->>AdminServer: GET /api/catalog
    AdminServer->>FileSystem: Scan CATALOG_GROUPS dirs
    FileSystem-->>AdminServer: Return file list
    AdminServer-->>Browser: {"ok":true,"groups":[...],"extras":[...]}
    Browser->>Browser: Render file tree

    User->>Browser: Click file to edit
    Browser->>AdminServer: GET /api/file?path=skills/example.md
    AdminServer->>FileSystem: Read file content
    FileSystem-->>AdminServer: File content + SHA256
    AdminServer-->>Browser: {"ok":true,"content":"...","sha256":"..."}
    Browser->>Browser: Display file in editor

    User->>Browser: Edit & Save
    Browser->>AdminServer: POST /api/file/save
    AdminServer->>AdminServer: Verify safe path (in ALLOWED_PATHS)
    AdminServer->>FileSystem: Write content
    FileSystem-->>AdminServer: OK
    AdminServer-->>Browser: {"ok":true,"sha256":"..."}
    Browser->>Browser: Update UI, show success

    User->>Browser: Create new file
    Browser->>AdminServer: POST /api/file/create<br/>{group:"skills",filename:"new-skill.md"}
    AdminServer->>FileSystem: Create template file
    FileSystem-->>AdminServer: Path created
    AdminServer-->>Browser: {"ok":true,"path":"skills/new-skill.md"}
```

## Data Flow: LLM Configuration

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant AdminServer
    participant Ollama
    participant LLMConfigManager

    User->>Browser: Load LLM Settings Page
    Browser->>AdminServer: GET /api/llm/status
    AdminServer->>LLMConfigManager: get_llm_config()
    LLMConfigManager-->>AdminServer: Provider, model, URL
    AdminServer->>Ollama: Probe available Ollama instances
    Ollama-->>AdminServer: Health status, latency
    AdminServer->>Ollama: GET /api/tags
    Ollama-->>AdminServer: {"models":[...]}
    AdminServer-->>Browser: Status with all models
    Browser->>Browser: Render LLM page

    User->>Browser: Select provider & model
    Browser->>AdminServer: POST /api/llm/config
    AdminServer->>LLMConfigManager: update_llm_config_file()
    LLMConfigManager-->>AdminServer: New config
    AdminServer->>AdminServer: Call _llm_status() again
    AdminServer-->>Browser: Updated status

    User->>Browser: Install Ollama (if needed)
    Browser->>AdminServer: POST /api/system/install-ollama<br/>{sudo_password:"..."}
    AdminServer->>AdminServer: Run sudo bash -c "curl ... | sh"
    AdminServer-->>Browser: {"ok":true,"message":"Installed"}

    User->>Browser: Pull a model
    Browser->>AdminServer: POST /api/ollama/pull<br/>{model:"llama2",ollama_url:"..."}
    AdminServer->>Ollama: ollama pull llama2
    Ollama-->>AdminServer: Download progress...
    AdminServer-->>Browser: {"ok":true,"message":"Model pulled"}
```

## Data Flow: Service Registry Discovery

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant AdminServer
    participant ServiceRegistry
    participant KnownServices

    User->>Browser: Load Services Page
    Browser->>AdminServer: POST /api/services/discover
    AdminServer->>ServiceRegistry: discover()
    ServiceRegistry->>ServiceRegistry: Iterate KNOWN_PORTS

    par Port Scanning
        ServiceRegistry->>KnownServices: HTTP GET :8787/api/health
        ServiceRegistry->>KnownServices: HTTP GET :8788/api/health
        ServiceRegistry->>KnownServices: HTTP GET :8789/api/health
        ServiceRegistry->>KnownServices: HTTP GET :8790/api/health
        ServiceRegistry->>KnownServices: HTTP GET :8791/api/health
        ServiceRegistry->>KnownServices: HTTP GET :8792/api/health
        ServiceRegistry->>KnownServices: HTTP GET :9222/api/health
    end

    KnownServices-->>ServiceRegistry: Online/Offline status
    ServiceRegistry->>ServiceRegistry: Register discovered services
    ServiceRegistry-->>AdminServer: {"ok":true,"discovery":{...}}
    AdminServer-->>Browser: Service list

    Browser->>Browser: Display services
    User->>Browser: Refresh health status
    Browser->>AdminServer: GET /api/services/{service_id}/health
    AdminServer->>ServiceRegistry: health_check(service_id)
    ServiceRegistry->>KnownServices: HTTP GET {health_endpoint}
    KnownServices-->>ServiceRegistry: Health details + latency_ms
    ServiceRegistry-->>AdminServer: Health object
    AdminServer-->>Browser: {"ok":true,"health":{...}}
```

## Data Flow: Community Linking & Sync

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant AdminServer
    participant FileSystem
    participant CommunityHub

    User->>Browser: Load Community Page
    Browser->>AdminServer: GET /api/community/status
    AdminServer->>FileSystem: Read COMMUNITY_LINK_FILE
    FileSystem-->>AdminServer: Link status (or empty)
    AdminServer->>FileSystem: Count COMMUNITY_SYNC_LOG lines
    FileSystem-->>AdminServer: Sync event count
    AdminServer-->>Browser: {"ok":true,"community":{linked:bool,email:"..."}}

    User->>Browser: Enter email + click "Link"
    Browser->>AdminServer: POST /api/community/link<br/>{email:"user@example.com"}
    AdminServer->>FileSystem: Generate magic token
    AdminServer->>FileSystem: Write COMMUNITY_LINK_FILE
    AdminServer-->>Browser: {"ok":true,"link":{email:"...",login_link_stub:"..."}}
    Browser->>Browser: Show magic link

    User->>Browser: Click "Sync"
    Browser->>AdminServer: POST /api/community/sync<br/>{direction:"both"}
    AdminServer->>FileSystem: Scan cli/recipes, recipes, skills
    FileSystem-->>AdminServer: File counts
    AdminServer->>FileSystem: Append sync event to COMMUNITY_SYNC_LOG
    AdminServer-->>Browser: {"ok":true,"sync":{uploaded:{...},remote_available:[...]}}
    Browser->>Browser: Display sync results
```

## Data Flow: CLI Integration

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant AdminServer
    participant CLI

    User->>Browser: Load page (Swarm Chat, CPU, or Orchestration)
    Browser->>AdminServer: GET /api/cli/commands
    AdminServer-->>Browser: ["version","doctor","llm-status"]
    Browser->>Browser: Render available commands

    User->>Browser: Type command (e.g., "doctor") + Send
    Browser->>AdminServer: POST /api/cli/run<br/>{command:"doctor"}
    AdminServer->>AdminServer: Check SAFE_CLI_COMMANDS whitelist
    AdminServer->>CLI: Run: python -m stillwater doctor
    CLI-->>AdminServer: stdout, stderr, returncode
    AdminServer-->>Browser: {"ok":true,"result":{...}}
    Browser->>Browser: Display output in chat interface
```

## Data Flow: File Operations

```mermaid
sequenceDiagram
    participant Browser
    participant AdminServer
    participant Security
    participant FileSystem

    Browser->>AdminServer: GET /api/file?path=skills/example.md
    AdminServer->>Security: _safe_resolve_repo_path()
    Security->>Security: Check path doesn't escape REPO_ROOT
    Security-->>AdminServer: Resolved path
    AdminServer->>Security: _is_allowed_edit_path()
    Security->>Security: Check suffix in ALLOWED_WRITE_SUFFIXES
    Security->>Security: Check resolved path in ALLOWED_PATHS
    Security-->>AdminServer: Permission allowed
    AdminServer->>FileSystem: Read content
    FileSystem-->>AdminServer: File bytes
    AdminServer->>AdminServer: Compute SHA256
    AdminServer-->>Browser: {"ok":true,"content":"...","sha256":"..."}
```

## Service Registry: Known Ports & Types

```
Port 8787 → admin (CUSTOM) — Stillwater Admin
Port 8788 → llm-portal (LLM) — LLM Portal (Ollama/Claude/OpenAI routing)
Port 8789 → recipe-engine (RECIPE) — Recipe Engine
Port 8790 → evidence-pipeline (EVIDENCE) — Evidence Pipeline
Port 8791 → oauth3-authority (OAUTH3) — OAuth3 Authority
Port 8792 → cpu-service (CPU) — CPU Service
Port 9222 → browser (BROWSER) — Solace Browser DevTools
```

## Catalog Groups

```
Root:
  - skills/                    → Skills (*.md)
  - swarms/                    → Swarm Agents (*.md)
  - recipes/                   → Recipes (*.md)
  - papers/                    → Papers (*.md)
  - community/                 → Community Docs (*.md)

CLI Extensions:
  - cli/recipes/               → CLI Recipes (*.md)
  - cli/extensions/skills/     → CLI Skills (*.md)
  - cli/extensions/personas/   → Personas (*.md)
  - cli/identity/              → Identity Notes (*.md)
  - cli/extensions/identity/   → Extended Identity (*.md)
  - cli/settings/              → Settings (*.md)

Editable Files (Extra):
  - llm_config.yaml
  - cli/extensions/splash.txt
  - CLAUDE.md
  - admin/README.md
```

## Frontend Page Mapping

| Page | Tab | API Endpoints Used | Purpose |
|------|-----|-------------------|---------|
| Orchestration | Default | /api/catalog, /api/file, /api/file/save, /api/file/create, /api/cli/commands | Browse & edit repo files (skills, recipes, etc.) |
| LLM Settings | llm-tab | /api/llm/status, /api/llm/config, /api/system/install-ollama, /api/ollama/pull | Configure LLM provider, manage Ollama |
| Services | services-tab | /api/services, /api/services/discover, /api/services/{id}/health, /api/services/register, /api/services/deregister | Auto-discover & monitor services |
| CPU Chat | cpu-tab | /api/cli/run, /api/cli/commands | Run CLI commands in chat interface |
| Community | sync-tab | /api/community/status, /api/community/link, /api/community/sync | Link to community, sync skills/recipes |

## Error Handling

All endpoints return:
```json
{
  "ok": true|false,
  "error": "error message if ok=false",
  ...response_fields
}
```

Common error cases:
- **400 Bad Request**: Invalid JSON payload, validation errors
- **404 Not Found**: File/service not found, unknown path
- **500 Internal Server Error**: System error (Ollama install fails, etc.)

## Security Boundaries

1. **File Operations**: Only paths in ALLOWED_PATHS (catalog dirs + EXTRA_EDITABLE_FILES) with safe suffixes (.md, .txt, .yaml, .yml, .json)
2. **Path Traversal**: _safe_resolve_repo_path() prevents "../" escapes
3. **CLI Commands**: Only SAFE_CLI_COMMANDS whitelist allowed (version, doctor, llm-status)
4. **Service Registry**: HTTP-only health checks (no arbitrary network calls)
5. **Filesize Limit**: Max 2MB per file write
