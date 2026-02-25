# CLI Command Flow

How the Stillwater CLI processes commands from entry point through dispatch to
execution. Based on the `main()` function in `cli.py`, which uses Python's
`argparse` with nested subparsers.

## Top-Level Command Dispatch

```mermaid
flowchart TD
    classDef cmd fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    classDef sub fill:#1a5cb5,color:#fff,stroke:#0f3d80
    classDef gate fill:#b58c1a,color:#fff,stroke:#806000
    classDef io fill:#4a4a4a,color:#fff,stroke:#333

    ENTRY["stillwater [cmd]"]
    PARSER["argparse\nmain(argv)"]
    ROOT["_repo_root()\n4 parents up from cli.py"]

    ENTRY --> PARSER
    PARSER --> ROOT

    PARSER --> PATHS["paths\nPrint key repo paths\n--json flag"]
    PARSER --> PRINT["print\nPrint suggested next steps"]
    PARSER --> INIT["init\nScaffold project templates"]
    PARSER --> LLM["llm\nManage LLM providers"]
    PARSER --> TWIN["twin\nInteractive LLM REPL"]
    PARSER --> SKILLS["skills\nSkill inventory + install"]
    PARSER --> WISH["wish\nWish notebook workflow"]
    PARSER --> STACK["stack\nRun + verify stack workflows"]
    PARSER --> RECIPE["recipe\nRecipe governance"]
    PARSER --> BOOKS["books\nList/show markdown books"]
    PARSER --> PAPERS["papers\nList/show markdown papers"]
    PARSER --> MATH["math-universal\nMath proof workflow"]
    PARSER --> IMO["imo-phuc\nIMO benchmark"]
    PARSER --> IMO_HIST["imo-history\nIMO historical data"]
    PARSER --> OOLONG["oolong\nCounter-bypass workflow"]
    PARSER --> LEARN["learn\nExternalized learning loop"]
    PARSER --> CLEANUP["cleanup\nPhuc cleanup + archive"]
    PARSER --> REPLAY["replay\nReplay stack from manifest"]
    PARSER --> RUN["run\nRun task with skill context"]
    PARSER --> EVIDENCE["evidence\nEvidence dir management"]
    PARSER --> SKILLS_AB_CMD["skills-ab\nA/B benchmark harness"]
    PARSER --> DEMO["demo\nQuick demo (dry-run)"]

    class PATHS,PRINT,INIT,LLM,TWIN,SKILLS,WISH,STACK,RECIPE,BOOKS,PAPERS cmd
    class MATH,IMO,IMO_HIST,OOLONG,LEARN,CLEANUP,REPLAY,RUN,EVIDENCE,SKILLS_AB_CMD,DEMO cmd
```

## LLM Command Subflow

```mermaid
flowchart TD
    classDef sub fill:#1a5cb5,color:#fff,stroke:#0f3d80
    classDef ext fill:#4a4a4a,color:#fff,stroke:#333

    LLM_CMD["stillwater llm [sub]"]
    LLM_CMD --> LLM_STATUS["status\nShow active provider + validation"]
    LLM_CMD --> LLM_PROVIDERS["providers\nList configured providers\nfrom llm_config.yaml"]
    LLM_CMD --> LLM_PROBE["probe-ollama\nProbe candidate Ollama servers\n--urls, --timeout, --json"]
    LLM_CMD --> LLM_MODELS["models\nList models from Ollama endpoint\n--url flag"]
    LLM_CMD --> LLM_SET_PROV["set-provider\nUpdate active provider\nin llm_config.yaml"]
    LLM_CMD --> LLM_SET_OLLAMA["set-ollama\nUpdate ollama url/model\nin llm_config.yaml"]

    class LLM_STATUS,LLM_PROVIDERS,LLM_PROBE,LLM_MODELS,LLM_SET_PROV,LLM_SET_OLLAMA sub
```

## LLM Provider Selection Flow

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    classDef gate fill:#b58c1a,color:#fff,stroke:#806000
    classDef ext fill:#4a4a4a,color:#fff,stroke:#333

    REQUEST["LLM request\n(prompt, model=auto)"]
    REG["provider_registry.py\nPROVIDERS dict"]
    MODEL_MAP["_MODEL_PROVIDER_MAP\nexact model -> provider"]
    OLLAMA_PREFIX["_OLLAMA_PREFIXES check\nllama3, codellama, mistral..."]
    CHEAPEST["get_cheapest_provider()\nfallback selection"]

    REQUEST --> REG
    REG --> MODEL_MAP
    MODEL_MAP -->|"match"| ROUTE_PROVIDER
    MODEL_MAP -->|"no match"| OLLAMA_PREFIX
    OLLAMA_PREFIX -->|"match"| OLLAMA_PROV["ollama\nlocalhost:11434"]
    OLLAMA_PREFIX -->|"no match"| CHEAPEST

    subgraph ROUTE_PROVIDER ["Route to Provider"]
        ANTHROPIC["anthropic\nhttps://api.anthropic.com/v1\nANTHROPIC_API_KEY env"]
        OPENAI["openai\nhttps://api.openai.com/v1\nOPENAI_API_KEY env"]
        TOGETHER["together\nhttps://api.together.xyz/v1\nTOGETHER_API_KEY env"]
        OPENROUTER["openrouter\nhttps://openrouter.ai/api/v1\nOPENROUTER_API_KEY env"]
    end

    CHEAPEST --> ROUTE_PROVIDER

    subgraph CALL_LOG ["Post-call logging"]
        USAGE_TRACK["usage_tracker.py\nToken cost (int, never float)\nRecipe cache hit flag\nSW5.0 40% iteration savings"]
        LOG_FILE["~/.stillwater/llm_calls.jsonl\nts, provider, model\nprompt_chars, response_chars\nlatency_ms, input_tokens\noutput_tokens, cost_hundredths_cent"]
    end

    ROUTE_PROVIDER --> CALL_LOG
    OLLAMA_PROV --> CALL_LOG
    USAGE_TRACK --> LOG_FILE

    class REQUEST active
    class MODEL_MAP,OLLAMA_PREFIX gate
    class ANTHROPIC,OPENAI,TOGETHER,OPENROUTER,OLLAMA_PROV ext
    class USAGE_TRACK,LOG_FILE active
```

## Skills Load Flow

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff,stroke:#1a5c1a

    SKILL_DIRS["_kernel_paths(root)\nSkill directory resolution"]
    ROOT_SKILLS["skills/ (root)"]
    CLI_SKILLS["src/cli/skills/"]
    CLI_SW_SKILLS["src/cli/skills/stillwater/"]
    EXT_SKILLS["extensions/skills/ (if ext_root exists)"]
    ENV_SKILLS["STILLWATER_SKILL_DIRS env var"]
    CFG_SKILLS["kernel_config.yaml: skill_dirs"]

    SKILL_DIRS --> ROOT_SKILLS
    SKILL_DIRS --> CLI_SKILLS
    SKILL_DIRS --> CLI_SW_SKILLS
    SKILL_DIRS --> EXT_SKILLS
    SKILL_DIRS --> ENV_SKILLS
    SKILL_DIRS --> CFG_SKILLS

    DEDUP["_dedupe_keep_order()\nfirst-wins deduplication"]
    ROOT_SKILLS & CLI_SKILLS & CLI_SW_SKILLS & EXT_SKILLS & ENV_SKILLS & CFG_SKILLS --> DEDUP

    RESOLVED["Resolved skill file paths\n(source, Path) tuples"]
    DEDUP --> RESOLVED

    class SKILL_DIRS,DEDUP,RESOLVED active
```

## Source Files

- `src/cli/src/stillwater/cli.py` — `main()` function, all `sub.add_parser()` calls (lines 5268–5822)
- `src/cli/src/stillwater/llm_client.py` — `LLMClient`, `_log_call()`, `get_call_history()`
- `src/cli/src/stillwater/provider_registry.py` — `PROVIDERS` dict, `_MODEL_PROVIDER_MAP`, `_OLLAMA_PREFIXES`
- `src/cli/src/stillwater/usage_tracker.py` — `SessionUsageTracker`, `SW5_ITERATION_REDUCTION_PCT=40`
- `src/cli/src/stillwater/session_manager.py` — `Session` dataclass, TTL=86400s
- `src/cli/src/stillwater/llm_cli_support.py` — Ollama probing helpers

## Coverage

- All top-level CLI commands extracted from `argparse` subparser definitions
- LLM subcommand breakdown (`status`, `providers`, `probe-ollama`, `models`, `set-provider`, `set-ollama`)
- LLM provider selection: model map lookup -> Ollama prefix match -> cheapest fallback
- Post-call logging: cost in integer hundredths-of-a-cent, JSONL call log
- Skill directory resolution with priority order and deduplication
