# Diagram 22: Deployment Architecture

**Description:** Stillwater has three deployment surfaces: local development (the OSS repo), local admin services (Admin Server on 8787 and LLM Portal on 8788), and the hosted solaceagi.com platform (nginx + uvicorn + FastAPI). The Admin Server and LLM Portal are designed for localhost-only use; solaceagi.com is the production cloud deployment. This diagram covers all three surfaces, the development → QA → production pipeline, and how the 9-project ecosystem integrates at deployment time.

---

## Local Development Setup

```mermaid
flowchart TD
    subgraph LOCAL_DEV["Local Development — /home/phuc/projects/stillwater/"]
        direction TB

        subgraph REPO["Repo Structure"]
            CLI_PKG["cli/ — stillwater package\n(pip install -e cli/)"]
            ADMIN_PKG["admin/ — admin server + LLM portal\n(uvicorn admin.llm_portal:app)"]
            SKILLS["skills/ — prime-safety, prime-coder, etc."]
            SWARMS["swarms/ — agent type definitions"]
            RECIPES["recipes/ + cli/recipes/ — automation recipes"]
            PAPERS["papers/ — technical papers"]
            DIAGRAMS["diagrams/ — mermaid diagram files"]
            COMBOS["combos/ — WISH+RECIPE pairs"]
            TESTS["tests/ — pytest test suite"]
        end

        subgraph SERVICES["Local Services"]
            ADMIN_SVC["Admin Server\nlocalhost:8787\nbash admin/start-admin.sh\n(ThreadingHTTPServer)"]
            PORTAL_SVC["LLM Portal\nlocalhost:8788\nbash admin/start-llm-portal.sh\n(uvicorn FastAPI)"]
        end

        subgraph LLM_CONFIG["LLM Configuration"]
            CONFIG_YAML["llm_config.yaml\n(active provider, ollama URL, model)"]
            OLLAMA["Ollama (optional)\n192.168.68.100:11434 (LAN)\nor localhost:11434\nor OLLAMA_URL env var"]
            ENV_KEYS["Environment variables:\nANTHROPIC_API_KEY\nOPENAI_API_KEY\nTOGETHER_API_KEY\nOPENROUTER_API_KEY"]
        end

        CLI_PKG --> ADMIN_SVC & PORTAL_SVC
        CONFIG_YAML --> ADMIN_SVC & PORTAL_SVC
        ENV_KEYS --> PORTAL_SVC
        OLLAMA --> PORTAL_SVC
    end

    subgraph LOG_DIR["Log Directory (~/.stillwater/)"]
        LLM_LOG["llm_calls.jsonl\n(all LLM calls, thread-safe append)"]
        SESSION_STATE["(no persistent session state —\nkeys are memory-only in LLM Portal)"]
    end

    PORTAL_SVC --> LLM_LOG
```

---

## Admin Services Startup Sequence

```mermaid
sequenceDiagram
    participant DEV as Developer
    participant BASH as bash scripts
    participant ADMIN as Admin Server (8787)
    participant PORTAL as LLM Portal (8788)
    participant BROWSER as Browser

    DEV->>BASH: bash admin/start-admin.sh
    BASH->>BASH: Check Python + deps
    BASH->>ADMIN: python admin/server.py --host 127.0.0.1 --port 8787 --open
    ADMIN->>ADMIN: Resolve REPO_ROOT (2 parents up from admin/)
    ADMIN->>ADMIN: Build CATALOG from CATALOG_GROUPS
    ADMIN->>BROWSER: Open http://127.0.0.1:8787 (if --open)
    ADMIN-->>DEV: [admin] serving: http://127.0.0.1:8787

    DEV->>BASH: bash admin/start-llm-portal.sh
    BASH->>PORTAL: uvicorn admin.llm_portal:app --host 0.0.0.0 --port 8788
    PORTAL->>PORTAL: Load LLMConfigManager (llm_config.yaml)
    PORTAL->>PORTAL: Init SessionManager (AES-256-GCM)
    PORTAL->>PORTAL: Register FastAPI routes
    PORTAL-->>DEV: INFO: Uvicorn running on http://0.0.0.0:8788

    DEV->>BROWSER: http://localhost:8788
    BROWSER->>PORTAL: GET /
    PORTAL-->>BROWSER: Dark-theme HTML UI (embedded, no CDN)
    BROWSER->>PORTAL: GET /api/providers
    PORTAL->>PORTAL: Probe localhost providers (2s timeout)
    PORTAL-->>BROWSER: {providers: [...], active: "ollama"}
```

---

## Development → QA → Production Pipeline

```mermaid
flowchart LR
    subgraph DEV_ENV["Development\n(local machine)"]
        DEV1["Edit skills/recipes/code\n(Admin UI or direct edit)"]
        DEV2["Run pytest tests\n(tests/ directory)"]
        DEV3["Achieve rung 641\n(red/green + evidence bundle)"]
        DEV4["LLM Portal: test\nprovider routing"]
        DEV1 --> DEV2 --> DEV3 --> DEV4
    end

    subgraph QA_ENV["QA — Rung Ladder"]
        QA1["Rung 641 PASS\n(local correctness)"]
        QA2["Rung 274177 PASS\n(seed sweep + replay)"]
        QA3["Rung 65537 PASS\n(adversarial + security)"]
        QA4["Evidence bundle:\ntests.json + plan.json\nrepro_red.log + repro_green.log\nbehavioral_hash.json"]
        QA1 --> QA2 --> QA3 --> QA4
    end

    subgraph STORE["Stillwater Store\n(community review)"]
        ST1["Submit PR + evidence bundle"]
        ST2["Automated rung gate check"]
        ST3["Community review\n(peer verification)"]
        ST4["Published skill/recipe"]
        ST1 --> ST2 --> ST3 --> ST4
    end

    subgraph PROD_ENV["Production\n(solaceagi.com)"]
        PR1["solaceagi.com\nnginx + uvicorn\nFastAPI backend"]
        PR2["Managed LLM proxy\n(Together.ai / OpenRouter)"]
        PR3["OAuth3 vault\n(cloud-backed AES-256-GCM)"]
        PR4["Cloud twin\n(solace-browser + solace-cli)"]
        PR5["24/7 automated execution\n(Blue Belt territory)"]
        PR1 --> PR2 & PR3 & PR4 --> PR5
    end

    DEV_ENV -->|"tests pass\nrung 641"| QA_ENV
    QA_ENV -->|"rung 65537 achieved\nevidence bundle"| STORE
    STORE -->|"published skill\npulled by platform"| PROD_ENV
```

---

## solaceagi.com Deployment Architecture

```mermaid
flowchart TD
    subgraph INTERNET["Internet"]
        USERS["Users\n(browser, CLI, API clients)"]
    end

    subgraph CLOUD["solaceagi.com Cloud"]
        NGINX["nginx\n- TLS termination (Let's Encrypt)\n- Static file serving\n- Reverse proxy to uvicorn"]

        subgraph UVICORN["uvicorn (FastAPI)"]
            API_BACKEND["FastAPI backend (solace-cli PRIVATE)\n- Auth + tier check\n- Managed LLM proxy\n- OAuth3 vault API\n- Cloud twin orchestration"]
        end

        subgraph LLM_PROXY["Managed LLM Proxy"]
            TOGETHER_PROXY["Together.ai proxy\n(Llama 3.3 70B, $0.59/M)"]
            OPENROUTER_PROXY["OpenRouter fallback\n(Claude, GPT-4, Mixtral)"]
        end

        subgraph TWIN_SVC["Cloud Twin Service"]
            SOLACE_BROWSER["solace-browser instance\n(per-user cloud twin)"]
            OAUTH3_VAULT["OAuth3 vault\n(cloud-backed, AES-256-GCM)"]
        end

        subgraph DB_LAYER["Persistence"]
            USER_DB["User DB\n(tier, subscription, email)"]
            EVIDENCE_DB["Evidence store\n(90-day audit trail, hash-chained)"]
            CALL_LOG["LLM call log\n(per-user, cost tracking)"]
        end

        subgraph STRIPE_INT["Billing"]
            STRIPE_WEBHOOK["Stripe webhook handler\n(/webhook endpoint)"]
            STRIPE_CHECKOUT["Stripe checkout sessions"]
        end
    end

    subgraph OSS_CLI["User Local (OSS)"]
        SW_CLI["stillwater/cli\n(pip install, free)"]
        LOCAL_PORTAL["LLM Portal\n(localhost:8788)"]
        LOCAL_ADMIN["Admin Server\n(localhost:8787)"]
    end

    USERS -->|"HTTPS"| NGINX
    NGINX --> UVICORN
    API_BACKEND --> LLM_PROXY & TWIN_SVC & DB_LAYER & STRIPE_INT
    OSS_CLI <-->|"optional cloud sync\n(Pro/Enterprise tier)"| API_BACKEND

    style NGINX fill:#1a2a3a,stroke:#58a6ff
    style UVICORN fill:#1a3a2a,stroke:#3fb950
    style LLM_PROXY fill:#2a1a3a,stroke:#a371f7
```

---

## Multi-Project Deployment Integration

```mermaid
flowchart TD
    subgraph STILLWATER_DEPLOY["stillwater (OSS)\nDeployed: everywhere (local + cloud)"]
        SW1["stillwater/cli → pip install\n(any developer machine)"]
        SW2["Admin Server → localhost:8787"]
        SW3["LLM Portal → localhost:8788"]
        SW4["Skill Store → GitHub + stillwater community"]
    end

    subgraph SOLACE_BROWSER_DEPLOY["solace-browser (OSS)\nDeployed: developer machines + solaceagi.com cloud"]
        SB1["Local: python -m solace_browser\n(developer machine)"]
        SB2["Cloud: per-user twin instance\n(solaceagi.com Pro tier)"]
        SB3["OAuth3 consent UI\n(embedded in browser)"]
    end

    subgraph PAUDIO_DEPLOY["paudio (OSS)\nDeployed: community volunteer compute"]
        PA1["paudio-compute: CPU-only nodes\n(volunteer network, deterministic)"]
        PA2["paudio API: solaceagi.com/api/v1/tts\n(hosted endpoint)"]
        PA3["Voice Arena: gamified evaluation\n(community judgment)"]
    end

    subgraph SOLACEAGI_DEPLOY["solaceagi.com (PAID)\nDeployed: cloud (nginx + uvicorn)"]
        SAG1["API backend (solace-cli PRIVATE)"]
        SAG2["LLM proxy (Together.ai + OpenRouter)"]
        SAG3["Avatar: paudio (voice) + pvideo (visual)"]
        SAG4["OAuth3 cloud vault"]
        SAG5["Stillwater evidence store (90 days)"]
    end

    subgraph PVIDEO_DEPLOY["pvideo (PRIVATE)\nDeployed: solaceagi.com only"]
        PV1["IF Theory physics engine\n(secret sauce)"]
        PV2["Avatar visual system\n(Phase 1: cartoon Q2 2026)"]
    end

    SW1 & SB1 -->|"skills + evidence"| SAG1
    PA2 --> SAG3
    PV2 --> SAG3
    SAG1 --> STILLWATER_DEPLOY

    style PVIDEO_DEPLOY fill:#2a1a1a,stroke:#f85149
    style SOLACEAGI_DEPLOY fill:#1a2a3a,stroke:#58a6ff
```

---

## LLM Portal Startup and Shutdown

```mermaid
flowchart TD
    subgraph START["Start LLM Portal"]
        SL1["bash admin/start-llm-portal.sh"]
        SL2["cd to repo root"]
        SL3["pip install -r admin/requirements.txt\n(fastapi, uvicorn, httpx, cryptography)"]
        SL4["uvicorn admin.llm_portal:app\n--host 0.0.0.0 --port 8788\n--reload (dev mode)"]
        SL5["FastAPI init:\n- Load LLMConfigManager (llm_config.yaml)\n- Init SessionManager (random AES key)\n- Register all routes"]
        SL1 --> SL2 --> SL3 --> SL4 --> SL5
    end

    subgraph RUNNING["Running State"]
        RN1["Accept connections on 0.0.0.0:8788"]
        RN2["Provider probe on /api/providers\n(localhost providers only, 2s timeout)"]
        RN3["History refresh every 10s\n(browser-side, not server push)"]
    end

    subgraph STOP["Stop LLM Portal"]
        SP1["bash admin/stop-llm-portal.sh\n(or Ctrl+C)"]
        SP2["SessionManager garbage collected"]
        SP3["AES key destroyed (in-memory only)\nAll encrypted API keys wiped"]
        SP4["No persistent state written\n(keys were never on disk)"]
        SP1 --> SP2 --> SP3 --> SP4
    end

    START --> RUNNING --> STOP
```

---

## Source Files

- `admin/server.py` — ThreadingHTTPServer, startup, REPO_ROOT resolution, --host/--port
- `admin/llm_portal.py` — FastAPI app, uvicorn entry point, SessionManager init
- `admin/start-admin.sh` — Admin server startup script
- `admin/start-llm-portal.sh` — LLM Portal startup script
- `admin/stop-llm-portal.sh` — LLM Portal stop script
- `admin/llm-portal-status.sh` — LLM Portal status check
- `admin/requirements.txt` — FastAPI, uvicorn, httpx, cryptography dependencies
- `admin/session_manager.py` — AES-256-GCM session key storage (memory-only)
- `/home/phuc/.claude/CLAUDE.md` — LLM Portal URL, provider list, solaceagi.com deployment

---

## Coverage

- Local development setup: repo structure, service startup, LLM config
- Admin Server (8787): ThreadingHTTPServer, startup, REPO_ROOT resolution
- LLM Portal (8788): uvicorn FastAPI, startup/shutdown, session key lifecycle
- Admin service startup sequence (step-by-step with commands)
- Development → QA → Production pipeline with rung gates
- solaceagi.com cloud deployment: nginx + uvicorn + FastAPI + LLM proxy + vault
- Multi-project deployment: how stillwater, solace-browser, paudio, pvideo converge at solaceagi.com
- LLM Portal startup/shutdown: AES key lifecycle (created at start, wiped at stop)
- Avatar system deployment phases (Q2-Q4 2026)
