# Stillwater System Architecture

High-level view of all major components and their relationships within the
Stillwater OS. Stillwater is a Software 5.0 verification framework: skills,
swarms, evidence, and a governed store are first-class citizens.

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    classDef portal fill:#1a5cb5,color:#fff,stroke:#0f3d80
    classDef gate fill:#b58c1a,color:#fff,stroke:#806000
    classDef store fill:#7a2d7a,color:#fff,stroke:#5c1a5c
    classDef external fill:#4a4a4a,color:#fff,stroke:#333

    USER["User / Agent"]

    subgraph CLI ["stillwater CLI  (src/cli/src/stillwater/)"]
        CLI_MAIN["cli.py\nargparse entry point"]
        LLM_CLIENT["llm_client.py\nUniversal LLM Client v2.0"]
        SESSION_MGR["session_manager.py\nSession TTL + skill packs"]
        USAGE["usage_tracker.py\nToken cost (int arithmetic)"]
        SKILLS_AB["skills_ab.py\nA/B benchmark harness"]
        PROVIDER_REG["provider_registry.py\nProvider routing table"]
        PROVIDERS["providers/\nanthropicprovider\nopenai_provider\nollama_provider\ntogether_provider\nopenrouter_provider"]
    end

    subgraph ADMIN ["Admin Layer  (admin/)"]
        ADMIN_SRV["server.py\nHTTP admin server\npath-traversal guard\nCLI allowlist"]
        LLM_PORTAL["llm_portal.py\nOpenAI-compat proxy\nPort 8788\nAES-256-GCM key store"]
        ADMIN_SESSION["session_manager.py\nAdmin session manager"]
    end

    subgraph STORE ["Stillwater Store  (src/store/)"]
        STORE_API["FastAPI endpoints\nPOST /store/submit\nGET /store/skills\nPOST /store/install"]
        STORE_MODELS["models.py\nAPIKey, SkillSubmission\nReviewRecord, SkillListing\nInstallRequest"]
        STORE_DB["db.py\nIn-memory singleton\nJSON-file persistence\napikeys.json + skills.json"]
        STORE_AUTH["auth.py\nsw_sk_ key format\nHMAC-SHA256 validation\nRate limit 10/24h\nReputation scoring"]
        RUNG_VAL["rung_validator.py\nEvidence bundle gate\nplan.json + tests.json\nbehavior_hash.txt\n3-seed consensus"]
    end

    subgraph SKILLS_LAYER ["Skill + Swarm Library"]
        SKILLS["skills/ (40+ files)\nprime-safety\nprime-coder\nphuc-orchestration\nphuc-forecast\n..."]
        SWARMS["swarms/ (27 files)\ncoder, planner\nskeptic, scout\nmathematician\nnorthstar-navigator\n..."]
        COMBOS["combos/ (12 files)\nbugfix, plan\nrun-test, qa-audit\n..."]
    end

    subgraph EVIDENCE ["Evidence + Artifacts"]
        ARTIFACTS["artifacts/\nwishes/\nruns/\ntwin/\nadmin/"]
        EVIDENCE_DIR["evidence/\nplan.json\ntests.json\nbehavior_hash.txt\nsecurity_scan.json"]
        LOG["~/.stillwater/\nllm_calls.jsonl"]
    end

    subgraph PROVIDERS_EXT ["External LLM Providers"]
        ANTHROPIC["Anthropic API\nclaude-opus-4-6\nclaude-sonnet-4-6\nclaude-haiku-4-5"]
        OPENAI["OpenAI API\ngpt-4o, gpt-4o-mini"]
        OLLAMA["Ollama (local)\nlocalhost:11434"]
        TOGETHER["Together.ai\nLlama-3.3-70B"]
        OPENROUTER["OpenRouter\nmulti-vendor"]
    end

    USER --> CLI_MAIN
    CLI_MAIN --> LLM_CLIENT
    CLI_MAIN --> SESSION_MGR
    CLI_MAIN --> SKILLS_AB
    LLM_CLIENT --> USAGE
    LLM_CLIENT --> PROVIDER_REG
    PROVIDER_REG --> PROVIDERS
    PROVIDERS --> ANTHROPIC & OPENAI & OLLAMA & TOGETHER & OPENROUTER

    CLI_MAIN --> ADMIN_SRV
    ADMIN_SRV --> LLM_PORTAL
    LLM_PORTAL --> ADMIN_SESSION
    LLM_PORTAL --> LLM_CLIENT

    CLI_MAIN --> STORE_API
    STORE_API --> STORE_AUTH
    STORE_API --> STORE_MODELS
    STORE_API --> STORE_DB
    STORE_AUTH --> STORE_DB
    STORE_API --> RUNG_VAL
    RUNG_VAL --> EVIDENCE_DIR

    CLI_MAIN --> SKILLS
    CLI_MAIN --> SWARMS
    CLI_MAIN --> COMBOS

    LLM_CLIENT --> LOG
    USAGE --> LOG
    CLI_MAIN --> ARTIFACTS
    RUNG_VAL --> EVIDENCE_DIR

    class CLI_MAIN,LLM_CLIENT,SESSION_MGR,USAGE,SKILLS_AB,PROVIDER_REG,PROVIDERS active
    class LLM_PORTAL,ADMIN_SRV,ADMIN_SESSION portal
    class RUNG_VAL,STORE_AUTH gate
    class STORE_API,STORE_MODELS,STORE_DB,STORE_AUTH store
    class ANTHROPIC,OPENAI,OLLAMA,TOGETHER,OPENROUTER external
```

## Source Files

- `src/cli/src/stillwater/cli.py` — main CLI entry point, command dispatch
- `src/cli/src/stillwater/llm_client.py` — universal LLM client, call logging
- `src/cli/src/stillwater/session_manager.py` — session lifecycle
- `src/cli/src/stillwater/usage_tracker.py` — cost tracking
- `src/cli/src/stillwater/skills_ab.py` — A/B benchmark harness
- `src/cli/src/stillwater/provider_registry.py` — provider routing table
- `src/cli/src/stillwater/providers/` — individual provider implementations
- `admin/server.py` — HTTP admin server with security guards
- `admin/llm_portal.py` — LLM portal, OpenAI-compat proxy
- `src/store/models.py` — Pydantic data models
- `src/store/db.py` — in-memory store with JSON persistence
- `src/store/auth.py` — API key generation, HMAC validation, rate limiting
- `src/store/rung_validator.py` — evidence bundle validation

## Coverage

- All major subsystems: CLI, Admin, Store, Skills, Swarms, Evidence
- LLM provider routing from CLI through provider registry to external APIs
- Store authentication and rung validation gates
- Call logging path to `~/.stillwater/llm_calls.jsonl`
- Color code: green = active CLI components, blue = portal/admin, yellow = gates, purple = store
