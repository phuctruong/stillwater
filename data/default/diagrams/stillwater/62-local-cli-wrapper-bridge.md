# 62. Local CLI Wrapper Bridge

**Purpose:** Show how Stillwater can expose local development CLIs as stable HTTP webservices, with Codex and Claude wrappers sharing the same operational shape.

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    classDef portal fill:#1a5cb5,color:#fff,stroke:#0f3d80
    classDef gate fill:#b58c1a,color:#fff,stroke:#806000
    classDef external fill:#4a4a4a,color:#fff,stroke:#333

    USER["Browser / Notebook / Test Script"]
    PLAY["/playground<br/>manual test page"]
    API["/api/generate<br/>Ollama-compatible JSON"]
    SCRIPTS["src/scripts/start|stop|test_local_cli_wrapper.sh"]

    subgraph WRAPPERS["Local CLI Wrapper Webservices"]
        CLAUDE["claude_code_wrapper.py :8080"]
        CODEX["codex_cli_wrapper.py :8081"]
    end

    subgraph SAFETY["Isolation Rules"]
        SCRATCH["scratch/ wrapper working dir"]
        CLEAN["strip session env vars"]
        PID["pid + log files in scratch/wrapper-services"]
    end

    subgraph CLIS["Local Development CLIs"]
        CLAUDECLI["claude -p"]
        CODEXCLI["codex exec"]
    end

    subgraph STILLWATER["Stillwater Wiring"]
        HTTPP["HTTPProvider / CodexWrapperProvider"]
        CFG["llm_config.yaml<br/>provider switch"]
        TESTS["pytest unit tests"]
    end

    USER --> PLAY
    USER --> API
    USER --> SCRIPTS
    PLAY --> CODEX
    API --> CLAUDE
    API --> CODEX
    SCRIPTS --> CLAUDE
    SCRIPTS --> CODEX
    CLAUDE --> SCRATCH
    CODEX --> SCRATCH
    CLAUDE --> CLEAN
    CODEX --> CLEAN
    CLAUDE --> PID
    CODEX --> PID
    CLAUDE --> CLAUDECLI
    CODEX --> CODEXCLI
    CODEX --> HTTPP
    CODEX --> CFG
    CODEX --> TESTS

    class USER,PLAY,API,SCRIPTS portal
    class CLAUDE,CODEX,SCRATCH,CLEAN,PID active
    class HTTPP,CFG,TESTS gate
    class CLAUDECLI,CODEXCLI external
```

## Contract

- Webservice: `GET /`, `GET /api/tags`, `GET /playground`, `POST /api/generate`
- Evidence: unit tests validate handler behavior, CLI error handling, and provider wiring
- Operations: start/stop/test scripts manage pid files and surface playground URLs
