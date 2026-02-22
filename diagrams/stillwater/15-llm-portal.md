# Diagram 15: LLM Portal Architecture

**Description:** The Stillwater LLM Portal (`admin/llm_portal.py`) is a FastAPI-based web application running on `localhost:8788`. It exposes an OpenAI-compatible proxy interface for all configured LLM providers and includes a dark-theme web UI for interactive testing. The universal LLM client (`cli/src/stillwater/llm_client.py`) abstracts all provider differences behind a single API.

---

## Architecture Overview

```mermaid
flowchart TD
    subgraph UI["Web UI (localhost:8788)"]
        BROWSER["Dark-theme HTML UI\n(embedded, no CDN)"]
    end

    subgraph PORTAL["FastAPI App — admin/llm_portal.py"]
        direction TB
        H_ROOT["GET / → Web UI"]
        H_HEALTH["GET /api/health"]
        H_PROVIDERS["GET /api/providers\n(reachability + auth status)"]
        H_SWITCH["POST /api/providers/switch"]
        H_AUTH["POST /api/providers/auth\n(AES-256-GCM key store)"]
        H_HISTORY["GET /api/history\n(~/.stillwater/llm_calls.jsonl)"]
        H_CHAT["POST /v1/chat/completions\n(OpenAI-compatible proxy)"]
        H_MODELS["GET /v1/models"]
    end

    subgraph SESSION["SessionManager (Phase 3)"]
        AES["AES-256-GCM\n256-bit key, 96-bit nonce"]
        MEMSTORE["In-memory encrypted store\n(never written to disk)"]
        AES --> MEMSTORE
    end

    subgraph CONFIG["LLMConfigManager"]
        ACTIVE["Active provider\n(in-session switching)"]
        CFGYAML["llm_config.yaml"]
        CFGYAML --> ACTIVE
    end

    subgraph CLIENT["LLMClient — llm_client.py"]
        RESOLVE["_resolve_provider()\nPriority: explicit → default → cheapest"]
        COMPLETE["complete() / chat()"]
        LOG["_log_call()\n~/.stillwater/llm_calls.jsonl"]
        CALLBACKS["_fire_callbacks()\ntip_callback + usage_tracker"]
        RESOLVE --> COMPLETE --> LOG
        COMPLETE --> CALLBACKS
    end

    subgraph REGISTRY["Provider Registry — providers/__init__.py"]
        PRIORITY["PROVIDER_PRIORITY:\n1. ollama (free)\n2. together ($0.59/M)\n3. openai\n4. openrouter\n5. anthropic"]
        GET_P["get_provider(name)"]
        LIST_P["list_available_providers()"]
        CHEAPEST["get_cheapest_provider()"]
        PRIORITY --> LIST_P --> CHEAPEST
        GET_P --> LIST_P
    end

    subgraph PROVIDERS["Provider Backends"]
        OLLAMA["OllamaProvider\nlocalhost:11434 (or OLLAMA_URL)\nModels: llama3.1:8b/70b, codellama, mistral\nNo API key required"]
        TOGETHER["TogetherProvider\napi.together.xyz/v1\nModels: Llama-3.3-70B, Llama-3.1-8B\nTOGETHER_API_KEY"]
        OPENAI["OpenAIProvider\napi.openai.com/v1\nModels: gpt-4o, gpt-4o-mini\nOPENAI_API_KEY"]
        OPENROUTER["OpenRouterProvider\nopenrouter.ai/api/v1\nModels: claude-3-haiku, gpt-4o-mini, llama-3.3-70b\nOPENROUTER_API_KEY"]
        ANTHROPIC["AnthropicProvider\napi.anthropic.com/v1\nModels: claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5\nANTHROPIC_API_KEY"]
        OFFLINE["Offline Mode\nEcho response, no network\nWorks immediately, zero cost"]
    end

    BROWSER -->|"fetch /api/*"| PORTAL
    H_AUTH --> SESSION
    H_SWITCH --> CONFIG
    H_PROVIDERS --> CONFIG
    H_PROVIDERS --> SESSION
    H_CHAT --> CLIENT
    H_HISTORY -->|"read JSONL"| LOG
    CLIENT --> REGISTRY
    REGISTRY --> GET_P
    GET_P --> OLLAMA & TOGETHER & OPENAI & OPENROUTER & ANTHROPIC & OFFLINE
```

---

## Provider Selection and Fallback Chain

```mermaid
flowchart LR
    REQ["Client Request\nprovider=auto or explicit"]

    REQ --> CHECK_EXPLICIT{"Explicit\nprovider?"}
    CHECK_EXPLICIT -->|"Yes"| USE_EXPLICIT["Use specified provider"]
    CHECK_EXPLICIT -->|"No"| CHECK_DEFAULT{"Default\nset in constructor?"}

    CHECK_DEFAULT -->|"Yes"| USE_DEFAULT["Use constructor default"]
    CHECK_DEFAULT -->|"No"| AUTO["Auto-select cheapest"]

    AUTO --> P1{"ollama\navailable?"}
    P1 -->|"Yes"| USE_OLLAMA["Use ollama\n(free, local)"]
    P1 -->|"No"| P2{"together\navailable?"}
    P2 -->|"Yes"| USE_TOGETHER["Use together\n($0.59/M tokens)"]
    P2 -->|"No"| P3{"openai\navailable?"}
    P3 -->|"Yes"| USE_OPENAI["Use openai\n(gpt-4o-mini $0.15/M)"]
    P3 -->|"No"| P4{"openrouter\navailable?"}
    P4 -->|"Yes"| USE_OPENROUTER["Use openrouter\n(variable)"]
    P4 -->|"No"| P5{"anthropic\navailable?"}
    P5 -->|"Yes"| USE_ANTHROPIC["Use anthropic\n(haiku $0.80/M)"]
    P5 -->|"No"| OFFLINE_FB["offline mode\n(echo, no network)"]

    USE_EXPLICIT & USE_DEFAULT & USE_OLLAMA & USE_TOGETHER & USE_OPENAI & USE_OPENROUTER & USE_ANTHROPIC & OFFLINE_FB --> CALL["Execute LLM call"]
    CALL --> LOG2["Log to\n~/.stillwater/llm_calls.jsonl"]
    LOG2 --> RESP["Return LLMResponse\n(text, tokens, cost, latency)"]
```

---

## Call Sequence: Client to Provider

```mermaid
sequenceDiagram
    participant APP as Application Code
    participant CLIENT as LLMClient
    participant REGISTRY as ProviderRegistry
    participant PROVIDER as LLMProvider (e.g. Anthropic)
    participant LOG as llm_calls.jsonl

    APP->>CLIENT: llm_call("What is 2+2?", provider="anthropic")
    CLIENT->>CLIENT: _resolve_provider("anthropic")
    CLIENT->>REGISTRY: get_provider("anthropic")
    REGISTRY-->>CLIENT: AnthropicProvider instance

    CLIENT->>PROVIDER: chat([{role:"user", content:"What is 2+2?"}])
    PROVIDER->>PROVIDER: Build HTTP request (stdlib urllib only)
    PROVIDER->>+PROVIDER: POST https://api.anthropic.com/v1/messages
    PROVIDER-->>-PROVIDER: HTTP 200 + JSON response

    PROVIDER-->>CLIENT: LLMResponse(text, model, tokens, cost_hundredths_cent, latency_ms)

    CLIENT->>LOG: _log_call(provider, model, chars, latency, tokens, cost)
    CLIENT->>APP: LLMResponse (or .text for llm_call())

    Note over CLIENT,LOG: Thread-safe with _log_lock<br/>Cost in exact int (hundredths of cent, never float)
```

---

## API Key Security Flow (Phase 3)

```mermaid
sequenceDiagram
    participant USER as Browser / User
    participant PORTAL as LLM Portal FastAPI
    participant SESSION as SessionManager
    participant AES as AES-256-GCM

    USER->>PORTAL: POST /api/providers/auth {provider:"openai", api_key:"sk-..."}
    PORTAL->>PORTAL: Validate provider exists in config
    PORTAL->>PORTAL: Validate api_key non-empty (null != empty)
    PORTAL->>SESSION: session.store_key("openai", "sk-...")
    SESSION->>AES: _aes_encrypt(32-byte key, plaintext)
    AES->>AES: Generate fresh 12-byte random nonce
    AES-->>SESSION: nonce + ciphertext (bytes)
    SESSION->>SESSION: Store in _encrypted_keys dict (memory only)
    SESSION-->>PORTAL: stored
    PORTAL-->>USER: {"status": "authenticated", "provider": "openai"}

    Note over SESSION: Key never written to disk<br/>Never appears in repr/str/logs<br/>Wiped on process exit

    USER->>PORTAL: POST /v1/chat/completions {...}
    PORTAL->>SESSION: session.get_key("openai")
    SESSION->>AES: _aes_decrypt(blob)
    AES-->>SESSION: plaintext api_key
    SESSION-->>PORTAL: "sk-..."
    PORTAL->>PORTAL: Inject key into HTTP headers
    Note over PORTAL: Key in memory only during request<br/>Never logged
```

---

## Call Logging Structure

```mermaid
flowchart TD
    CALL["LLM call completes (or errors)"]
    CALL --> LOGFN["_log_call(provider, model,\nprompt_chars, response_chars,\nlatency_ms, input_tokens,\noutput_tokens, cost_hundredths_cent,\nrequest_id, error)"]

    LOGFN --> LOCK["Acquire _log_lock\n(threading.Lock)"]
    LOCK --> WRITE["Append JSON line to\n~/.stillwater/llm_calls.jsonl"]
    LOCK --> UNLOCK["Release lock"]

    WRITE --> FIELDS["Fields per entry:\n- ts: ISO 8601 UTC timestamp\n- provider: string\n- model: string\n- prompt_chars: int\n- response_chars: int\n- latency_ms: int\n- input_tokens: int\n- output_tokens: int\n- cost_hundredths_cent: int (never float)\n- request_id: string\n- error: string or null"]

    WRITE --> READ["GET /api/history?n=50\nreturns last N entries\n(max 500) + total count"]

    style FIELDS text-align:left
```

---

## Source Files

- `admin/llm_portal.py` — FastAPI app, routes, session manager, HTML UI
- `admin/session_manager.py` — AES-256-GCM in-memory key storage
- `cli/src/stillwater/llm_client.py` — Universal LLMClient, llm_call, llm_chat, _log_call
- `cli/src/stillwater/provider_registry.py` — High-level PROVIDERS dict, routing table
- `cli/src/stillwater/providers/__init__.py` — Provider class registry, PROVIDER_PRIORITY, list_available_providers
- `cli/src/stillwater/providers/anthropic_provider.py` — Anthropic backend
- `cli/src/stillwater/providers/openai_provider.py` — OpenAI backend
- `cli/src/stillwater/providers/together_provider.py` — Together.ai backend
- `cli/src/stillwater/providers/openrouter_provider.py` — OpenRouter backend
- `cli/src/stillwater/providers/ollama_provider.py` — Local Ollama backend

---

## Coverage

- All 5 provider backends (anthropic, openai, together, openrouter, ollama) + offline mode
- Provider priority/fallback chain (cheapest-first auto-selection)
- All 8 HTTP routes on the LLM Portal (GET /, /api/health, /api/providers, GET /v1/models; POST /api/providers/switch, /api/providers/auth, /api/history, /v1/chat/completions)
- Phase 3 AES-256-GCM session key storage (memory-only, never persisted)
- Call logging to `~/.stillwater/llm_calls.jsonl` (thread-safe, exact int cost arithmetic)
- Provider resolution priority: explicit > constructor default > auto (cheapest available)
- LLMClient v1.x backward compatibility (llm_call, llm_chat, .call())
- Cost tracking in hundredths of a cent (int arithmetic, never float)
