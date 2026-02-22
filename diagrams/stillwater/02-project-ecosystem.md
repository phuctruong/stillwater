# 9-Project Ecosystem

The Phuc Ecosystem consists of 9 interdependent projects converging on
`solaceagi.com`. Stillwater is the central verification OS that all other
projects depend on for skill governance and evidence discipline.

```mermaid
flowchart LR
    classDef oss fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    classDef private fill:#5a5a5a,color:#fff,stroke:#333
    classDef paid fill:#b58c1a,color:#fff,stroke:#806000
    classDef hub fill:#7a2d7a,color:#fff,stroke:#5c1a5c

    subgraph OSS ["Public / Open Source"]
        SW["stillwater\nVerification OS\nskills + swarms\nStore governance\nrung ladder"]
        SW_CLI["stillwater/cli\nBase CLI (OSS)\nllm_client\nprovider_registry\nsession_manager"]
        STORE["stillwater store\nSkill publishing\nRung-gated review\nAPI: sw_sk_ keys"]
        SB["solace-browser\nOAuth3 reference impl\nTwin browser\nPM triplets + recipes"]
        PAUDIO["paudio\nDeterministic TTS\nVoice Arena\npaudio-compute\npaudio-judge\npaudio-karaoke\npaudio-stt"]
        PHUCNET["phucnet\nphuc.net\nArticles + books\nIF Theory essays"]
        IF["if\nIF Theory physics\nMersenne Tower Theorem\nPrime Field Theory"]
        PZIP["pzip\nUniversal compression\nGAR 66:1 ratio\n$0.00032/user/mo"]
    end

    subgraph PRIVATE ["Private"]
        SCLI["solace-cli\nExtends stillwater/cli\nOAuth3 vault\nAES-256-GCM tokens\nTwin orchestration\nCloud backend"]
        PVIDEO["pvideo\nIF Theory engine\nPhysics video/avatar\nSecret sauce"]
        MKTG["solace-marketing\nStrategy v3.0\nGTM + content"]
    end

    subgraph PAID_LAYER ["Hosted Platform"]
        SOLACE["solaceagi.com\nIntegration layer\nBYOK + Managed LLM\nOAuth3 vault\nAvatar system\n$3/mo LLM tier\n$19/mo Pro\n$99/mo Enterprise"]
    end

    %% stillwater relationships
    SW --> SW_CLI
    SW --> STORE
    SW_CLI --> SCLI
    SW --> SB
    SW --> PAUDIO
    SW --> PVIDEO

    %% ecosystem convergence
    SCLI --> SOLACE
    SB --> SOLACE
    PAUDIO --> SOLACE
    PVIDEO --> SOLACE
    IF --> PVIDEO
    IF --> PZIP

    %% avatar system
    PAUDIO -.->|"voice"| SOLACE
    PVIDEO -.->|"visual"| SOLACE

    %% marketing
    MKTG --> SOLACE

    %% phucnet feeds content
    PHUCNET -.->|"articles"| SOLACE

    class SW,SW_CLI,STORE,SB,PAUDIO,PHUCNET,IF,PZIP oss
    class SCLI,PVIDEO,MKTG private
    class SOLACE paid
```

### Data Flow Detail

```mermaid
flowchart LR
    classDef oss fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    classDef private fill:#5a5a5a,color:#fff,stroke:#333
    classDef paid fill:#b58c1a,color:#fff,stroke:#806000

    USER["User"]

    subgraph BYOK ["BYOK Path (free)"]
        SW_CLI2["stillwater/cli\n(OSS)"]
        ANTHRO["Anthropic/OpenAI\n(user's own key)"]
    end

    subgraph MANAGED ["Managed LLM Path (+$3/mo)"]
        SCLI2["solace-cli\n(private extension)"]
        TOGETHER["Together.ai\nLlama-3.3-70B\n$0.59/M tokens"]
        OPENROUTER["OpenRouter\nfallback"]
    end

    subgraph STORE2 ["Stillwater Store"]
        SUBMIT["POST /store/submit\nsw_sk_ auth\nrung validation"]
        REVIEW["Review\npending -> accepted\n-> rejected"]
        PUBLISH["Published skills\nGET /store/skills"]
    end

    USER --> SW_CLI2
    SW_CLI2 --> ANTHRO
    USER --> SCLI2
    SCLI2 --> TOGETHER
    SCLI2 --> OPENROUTER

    SW_CLI2 --> SUBMIT
    SUBMIT --> REVIEW
    REVIEW --> PUBLISH
    PUBLISH --> SW_CLI2

    class SW_CLI2 oss
    class SCLI2,TOGETHER,OPENROUTER private
    class SUBMIT,REVIEW,PUBLISH paid
```

## Source Files

- `/home/phuc/projects/stillwater/CLAUDE.md` — 9-project architecture description
- `/home/phuc/.claude/CLAUDE.md` — ecosystem hub memory, pricing tiers, project locations
- `store/auth.py` — `sw_sk_` key format, HMAC validation
- `admin/llm_portal.py` — LLM provider routing documentation
- `cli/src/stillwater/provider_registry.py` — Together.ai, OpenRouter, Anthropic, OpenAI providers

## Coverage

- All 9 projects in the ecosystem with OSS/private color coding
- Data flow from stillwater CLI through managed LLM providers
- Avatar system convergence: paudio (voice) + pvideo (visual) at solaceagi.com
- Stillwater Store submission and review lifecycle
- Pricing tiers: BYOK (free) vs managed LLM (+$3/mo) vs Pro ($19/mo)
- IF Theory as physics substrate flowing into pvideo and pzip
