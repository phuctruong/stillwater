# Diagram 25: Service Types — Endpoints, Flows, and Evidence

**Description:** Each of the seven Stillwater services has a canonical port, a defined endpoint set, a request/response contract, evidence capture behavior, and OAuth3 scope requirements. This diagram catalogs every service in detail: what it does, what it exposes, how requests flow through it, where evidence is captured, and what OAuth3 scopes govern access.

---

## Service Type Overview

```mermaid
flowchart TD
    subgraph CATALOG["7 Service Types — Port Assignments and Roles"]
        direction TB

        S1["Admin Server\nPort: 8787\nRole: Service registry + discovery + proxy\nEvidence: captures all proxied calls\nOAuth3: no (gateway — auth bootstrap)"]
        S2["LLM Portal\nPort: 8788\nRole: Multi-provider LLM routing\nEvidence: always (every LLM call)\nOAuth3: machine.llm.*"]
        S3["Recipe Engine\nPort: 8789\nRole: Recipe execution + hit/miss routing\nEvidence: always (every execution)\nOAuth3: recipe.*"]
        S4["Evidence Pipeline\nPort: 8790\nRole: Hash-chained audit capture\nEvidence: self-capturing (is the pipeline)\nOAuth3: evidence.* (read/export only)"]
        S5["OAuth3 Authority\nPort: 8791\nRole: Token issuance + validation + revoke\nEvidence: always (every auth event)\nOAuth3: no (auth bootstrap)"]
        S6["CPU Service\nPort: 8792\nRole: Deterministic CPU computation\nEvidence: on-error\nOAuth3: machine.cpu.*"]
        S7["Browser\nPort: 9222\nRole: Chrome DevTools Protocol\nEvidence: always (every action)\nOAuth3: web.*"]
    end
```

---

## Service 1: Admin Server (8787)

```mermaid
flowchart TD
    subgraph ADMIN_SVC["Admin Server — localhost:8787"]
        direction TB

        subgraph REGISTRY_ENDPOINTS["Registry Endpoints"]
            AR1["GET /api/services\n→ All registered services (filterable)"]
            AR2["GET /api/services/{id}\n→ Single service descriptor + health history"]
            AR3["GET /api/services/health\n→ Aggregate: {total, healthy, degraded, stopped}"]
            AR4["POST /api/services/register\n{descriptor}\n→ Register service, verify health, persist"]
            AR5["POST /api/services/{id}/deregister\n→ Mark stopped, keep history, persist"]
            AR6["POST /api/services/discover\n→ Probe ports 8788–9222, register new services"]
        end

        subgraph PROXY_ENDPOINT["Proxy Endpoint"]
            AP1["POST /api/proxy/{service_id}/{path}\n{...body...}\nAuthorization: Bearer {token}\n→ Validate OAuth3 (if service requires)\n→ Forward to service\n→ Capture to Evidence Pipeline\n→ Return response + evidence_id"]
        end

        subgraph EXISTING_ENDPOINTS["Existing Endpoints (Phase 1)"]
            AE1["GET /api/catalog → File catalog"]
            AE2["GET /api/file → Read file content"]
            AE3["POST /api/file/save → Save file"]
            AE4["GET /api/llm/status → LLM Portal status"]
            AE5["POST /api/cli/run → Allowlisted CLI commands"]
        end
    end

    subgraph ADMIN_EVIDENCE["Evidence Capture (Admin)"]
        AEV1["Captures: every proxied request (all services)"]
        AEV2["Fields: source IP, service_id, endpoint,\nrequest_hash, response_hash,\ntoken_principal (if OAuth3),\nlatency_ms, status_code"]
        AEV3["Mode: always (on all proxied calls)"]
    end

    PROXY_ENDPOINT --> ADMIN_EVIDENCE
```

---

## Service 2: LLM Portal (8788)

```mermaid
flowchart TD
    subgraph LLM_SVC["LLM Portal — localhost:8788"]
        direction TB

        subgraph LLM_ENDPOINTS["Core Endpoints (FastAPI)"]
            L1["POST /chat\n{messages: [{role, content}],\n model?: string,\n provider?: string,\n stream?: bool}\n→ {content, tokens_used,\n   provider, model, latency_ms}"]
            L2["POST /complete\n{prompt: string,\n max_tokens?: int}\n→ {text, tokens_used, provider, model}"]
            L3["POST /embed\n{text: string | list[string]}\n→ {embeddings: [[float]], model, provider}"]
            L4["POST /classify\n{text: string, labels: [string]}\n→ {label, confidence, provider}"]
        end

        subgraph LLM_MGMT["Management Endpoints"]
            LM1["GET /health\n→ {status, version, uptime_seconds,\n   last_request_ts, providers_active: []}"]
            LM2["GET /descriptor\n→ Full ServiceDescriptor JSON"]
            LM3["GET /openapi.json\n→ Auto-generated OpenAPI spec (FastAPI)"]
            LM4["GET /providers\n→ {providers: [{id, status, models: []}]}"]
            LM5["POST /providers/config\n{provider, api_key?, ollama_url?}\n→ Update provider configuration\n(keys: memory-only, never persisted)"]
        end

        subgraph LLM_ROUTING["Provider Routing Logic"]
            BYOK["BYOK mode:\nRead ANTHROPIC_API_KEY /\nOPENAI_API_KEY / TOGETHER_API_KEY\nfrom environment at startup"]
            MANAGED["Managed mode:\nRead platform key from OAuth3 vault\n(solaceagi.com Pro tier)"]
            FALLBACK["Fallback chain:\nPrimary provider → OpenRouter\n(if primary fails or rate-limits)"]
        end
    end

    subgraph LLM_EVIDENCE["Evidence Capture (LLM Portal)"]
        LEV1["Captures: every chat, complete, embed, classify"]
        LEV2["Fields: messages_hash (not messages — privacy),\ntokens_used, provider, model,\nlatency_ms, response_hash,\ncaller_ip (127.0.0.1 always),\nevidence_id (from X-Evidence-Id header)"]
        LEV3["Mode: always — LLM calls are evidence events\nby definition in Software 5.0"]
        LEV4["OAuth3 required scope: machine.llm.chat\n(chat + complete)\nmachine.llm.embed\nmachine.llm.classify"]
    end

    LLM_ENDPOINTS --> LLM_EVIDENCE
```

---

## Service 3: Recipe Engine (8789)

```mermaid
flowchart TD
    subgraph RECIPE_SVC["Recipe Engine — localhost:8789"]
        direction TB

        subgraph RECIPE_ENDPOINTS["Core Endpoints"]
            RE1["POST /execute\n{recipe_id: string,\n params: {key: value},\n force_fresh?: bool}\n→ {status, result,\n   steps_executed, hit_rate,\n   evidence_ids: []}"]
            RE2["POST /replay\n{evidence_bundle_id: string}\n→ Re-execute exact steps from prior run\n→ Compare outputs (regression test)"]
            RE3["GET /recipes\n→ List all available recipes\n{id, name, version, hit_rate, last_run}"]
            RE4["GET /recipes/{id}\n→ Recipe detail: steps, params schema,\n  hit_rate_history, evidence summary"]
            RE5["POST /recipes/{id}/purge-cache\n→ Force next execution to be fresh\n(bypass hit cache)"]
        end

        subgraph RECIPE_MGMT["Management Endpoints"]
            RM1["GET /health\n→ {status, version, uptime_seconds,\n   recipes_loaded, cache_hit_rate}"]
            RM2["GET /descriptor\n→ Full ServiceDescriptor"]
            RM3["GET /openapi.json"]
            RM4["GET /hit-rate\n→ {overall_hit_rate,\n   by_recipe: {id: rate}}"]
        end

        subgraph RECIPE_STEPS["Step Classification and Routing"]
            STEP_LLM["LLM step:\nPOST http://127.0.0.1:8788/chat\nor POST /proxy/llm/chat (if via admin)"]
            STEP_CPU["CPU step:\nPOST http://127.0.0.1:8792/compute"]
            STEP_WEB["Web step:\nPOST http://127.0.0.1:9222/action\n(CDP command via Browser service)"]
            STEP_CACHE["Cache hit:\nReturn stored result directly\n(no downstream call)"]
        end
    end

    subgraph RECIPE_EVIDENCE["Evidence Capture (Recipe Engine)"]
        REV1["Captures: every recipe execution start + end"]
        REV2["Fields: recipe_id, params_hash,\nhit_or_miss, steps: [{type, service, latency}],\noverall_status, result_hash,\ncache_key (for future hit matching)"]
        REV3["Mode: always"]
        REV4["OAuth3 required scope: recipe.execute\n(POST /execute, /replay)\nrecipe.store.read (GET /recipes)"]
    end

    RECIPE_ENDPOINTS --> RECIPE_EVIDENCE
```

---

## Service 4: Evidence Pipeline (8790)

```mermaid
flowchart TD
    subgraph EVIDENCE_SVC["Evidence Pipeline — localhost:8790"]
        direction TB

        subgraph CAPTURE_ENDPOINTS["Capture Endpoints (write path)"]
            EW1["POST /api/capture/request\n{service, endpoint, request_hash,\n token_principal?, extra_fields?}\n→ {evidence_id} (assigned UUID)"]
            EW2["POST /api/capture/response\n{evidence_id, response_hash,\n status_code, latency_ms, extra_fields?}\n→ {evidence_id, hash_chain_entry}"]
            EW3["POST /api/capture/seal\n{evidence_ids: [id1, id2, ...]}\n→ {bundle_id, root_hash}\nSeals a set of events into a named bundle"]
            EW4["POST /api/capture/raw\n{event_type, fields: {key: value}}\n→ {evidence_id}\nFor custom evidence (browser snapshots, etc.)"]
        end

        subgraph QUERY_ENDPOINTS["Query Endpoints (read path)"]
            ER1["GET /api/evidence/{evidence_id}\n→ Single event record with all fields"]
            ER2["GET /api/bundles\n→ List all bundles\n{bundle_id, root_hash, event_count, ts}"]
            ER3["GET /api/bundles/{bundle_id}\n→ Full bundle: all events in chain order\n  + chain verification result"]
            ER4["GET /api/bundles/{bundle_id}/export\n→ Export as Part 11 audit document\n  (ALCOA+ fields, hash-chained, signed)"]
            ER5["GET /api/bundles/{bundle_id}/verify\n→ Verify chain integrity from root hash\n→ {valid: bool, broken_at?: evidence_id}"]
        end

        subgraph MGMT_ENDPOINTS["Management Endpoints"]
            EM1["GET /health\n→ {status, version, events_captured,\n   bundles_sealed, chain_valid}"]
            EM2["GET /descriptor"]
            EM3["GET /openapi.json"]
        end
    end

    subgraph EVIDENCE_CHAIN["Hash Chain Structure"]
        EC1["Entry N fields:\n{evidence_id, ts, service, endpoint,\n request_hash, response_hash,\n token_principal, status_code,\n latency_ms, prev_hash}"]
        EC2["Entry N chain hash:\nSHA-256(entry_N_json + prev_hash)\n(tamper-evident: change any field,\nchain breaks from that point)"]
        EC3["Storage:\nartifacts/evidence/evidence_pipeline.jsonl\n(append-only, one entry per line)"]
        EC1 --> EC2 --> EC3
    end

    subgraph EVIDENCE_ALCOA["FDA 21 CFR Part 11 / ALCOA+"]
        ATTR["Attributable:\ntoken_principal on every event\n(who authorized the action)"]
        LEG["Legible:\nhuman-readable JSONL\n(not binary, not encrypted)"]
        CONTEMP["Contemporaneous:\nts = event time, not log time\n(populated before response sent)"]
        ORIG["Original:\nbrowser snapshots stored via pzip\n(compressed HTML, not screenshot)"]
        ACCUR["Accurate:\nhash-chained, tamper-evident\nchain verification via /verify"]
    end

    CAPTURE_ENDPOINTS --> EVIDENCE_CHAIN
    EVIDENCE_CHAIN --> EVIDENCE_ALCOA
```

---

## Service 5: OAuth3 Authority (8791)

```mermaid
flowchart TD
    subgraph OAUTH_SVC["OAuth3 Authority — localhost:8791"]
        direction TB

        subgraph TOKEN_ENDPOINTS["Token Lifecycle Endpoints"]
            OT1["POST /api/token/issue\n{principal, scopes: [scope1, scope2],\n expiry_hours?, one_use?: bool}\n→ {token_id, token,\n   scopes, expires_at, one_use}"]
            OT2["POST /api/token/validate\n{token, required_scope}\n→ {valid: bool, principal?,\n   scopes?, expires_at?,\n   error?: 'expired'|'revoked'|'scope_mismatch'}"]
            OT3["POST /api/token/refresh\n{token}\n→ {new_token, expires_at}\n(requires: token not revoked,\n  expiry within 24h)"]
            OT4["POST /api/token/revoke\n{token_id?, scope?, principal?}\n→ {revoked: int} (count of tokens revoked)\n(append-only revocation list)"]
        end

        subgraph CONSENT_ENDPOINTS["Consent UI Endpoints"]
            OC1["GET /consent/{request_id}\n→ Render consent screen HTML\n{agent_id, action, scope, evidence_hash}"]
            OC2["POST /consent/{request_id}/approve\n{one_use?: bool, expiry_hours?}\n→ Issue token, redirect to callback"]
            OC3["POST /consent/{request_id}/deny\n→ Log denial, callback with 403"]
        end

        subgraph VAULT_ENDPOINTS["Vault Management"]
            OV1["GET /api/tokens\n→ List active tokens for current principal\n{token_id, scopes, expires_at, last_used}"]
            OV2["GET /api/audit\n→ Token audit log (all events)\n{ts, event_type, token_id, scope,\n principal, error?}"]
            OV3["GET /health\n{status, version, uptime_seconds,\n tokens_active, vault_ok}"]
            OV4["GET /descriptor"]
        end

        subgraph VAULT_STORAGE["Token Storage (AES-256-GCM)"]
            VS1["~/.stillwater/oauth3_vault.enc\n(encrypted blob, local only)"]
            VS2["Key: derived at vault init\n(stored in system keychain or\n local file — not memory)"]
            VS3["Revocation list: append-only\n(never delete — audit trail)"]
        end
    end

    subgraph OAUTH_EVIDENCE["Evidence Capture (OAuth3 Authority)"]
        OEV1["Captures: every token issue, validate, revoke"]
        OEV2["Fields: ts, event_type,\ntoken_id, scopes, principal,\nexpiry, one_use, error?"]
        OEV3["Mode: always — auth events are always evidence"]
        OEV4["OAuth3 required: None\n(auth bootstrap — cannot require own token\nfor basic issue/validate)\nAdmin reads vault: evidence.read scope"]
    end

    TOKEN_ENDPOINTS --> VAULT_STORAGE
    TOKEN_ENDPOINTS --> OAUTH_EVIDENCE
```

---

## Service 6: CPU Service (8792)

```mermaid
flowchart TD
    subgraph CPU_SVC["CPU Service — localhost:8792"]
        direction TB

        subgraph CPU_ENDPOINTS["Computation Endpoints"]
            C1["POST /compute\n{function: string,\n args: [arg1, arg2, ...],\n kwargs?: {key: value}}\n→ {result, duration_ms, deterministic: bool}"]
            C2["POST /compute/batch\n{tasks: [{function, args}], parallel?: bool}\n→ {results: [{result, duration_ms}]}"]
            C3["GET /functions\n→ List registered CPU functions\n{id, description, input_schema, output_schema}"]
            C4["POST /functions/register\n{id, module, function}\n→ Register new CPU function\n(allowlist-only: must be in\nallowed_modules list)"]
        end

        subgraph CPU_FUNCTIONS["Built-in CPU Functions"]
            CF1["text.hash\n→ SHA-256 of string input"]
            CF2["text.count_tokens\n→ Approximate token count\n(no LLM call — regex-based)"]
            CF3["data.json_extract\n→ jq-style extraction from JSON"]
            CF4["data.deduplicate\n→ Remove duplicate items from list"]
            CF5["math.exact_add / .subtract / .multiply\n→ Exact integer arithmetic\n(int, not float — never floats in CPU service)"]
            CF6["pzip.compress\n→ Compress HTML snapshot\n(pzip format, lossless)"]
            CF7["pzip.decompress\n→ Decompress pzip archive"]
        end

        subgraph CPU_SAFETY["Safety Model"]
            CS1["Allowed modules only:\n(hardcoded allowlist in cpu_service.py)\nNo exec(), no eval(), no import of\narbitrary modules"]
            CS2["No LLM calls — ever\n(CPU service is the LLM-free lane)"]
            CS3["Timeout: 30s per computation\n(hard limit, subprocess killed)"]
            CS4["No network access\n(CPU service has no outbound calls)"]
        end

        subgraph CPU_MGMT["Management Endpoints"]
            CM1["GET /health\n{status, version, uptime_seconds,\n functions_registered, last_compute_ts}"]
            CM2["GET /descriptor"]
            CM3["GET /openapi.json"]
        end
    end

    subgraph CPU_EVIDENCE["Evidence Capture (CPU Service)"]
        CEV1["Captures: errors only (evidence_capture: on-error)"]
        CEV2["Fields on error: function, args_hash,\nerror_type, error_message, stack_trace,\nduration_ms (how long before failure)"]
        CEV3["Mode: on-error — successful CPU calls\nare not evidence events by default\n(too high frequency, low value)"]
        CEV4["OAuth3 required scope: machine.cpu.compute"]
    end

    CPU_ENDPOINTS --> CPU_SAFETY
    CPU_ENDPOINTS --> CPU_EVIDENCE
```

---

## Service 7: Browser (9222)

```mermaid
flowchart TD
    subgraph BROWSER_SVC["Browser — localhost:9222"]
        direction TB

        subgraph CDP_PROTOCOL["Chrome DevTools Protocol (CDP)"]
            BR_NATIVE["Native CDP endpoints:\nws://localhost:9222/json\n(Chrome launches with --remote-debugging-port=9222)"]
            BR_NOTE["CDP is a WebSocket protocol —\nnot a REST API.\nThe Browser service wrapper\n(browser_service.py) exposes\na REST facade on top of CDP."]
        end

        subgraph WRAPPER_ENDPOINTS["REST Wrapper Endpoints (browser_service.py)"]
            BW1["POST /action\n{type: 'navigate'|'click'|'fill'|'submit'|'extract',\n url?: string, selector?: string,\n value?: string, extract_schema?: {}}\n→ {success, result, snapshot_id,\n   dom_hash_before, dom_hash_after}"]
            BW2["POST /snapshot\n{format: 'html'|'screenshot'|'pdf'}\n→ {snapshot_id, pzip_url?,\n   screenshot_url?, ts}"]
            BW3["GET /page\n→ {url, title, dom_hash, cookies_count,\n   local_storage_keys: []}"]
            BW4["POST /recipe/run\n{steps: [{type, selector, value}]}\n→ {steps_completed, failed_at?,\n   snapshots: [snapshot_id]}"]
            BW5["GET /sessions\n→ Active browser sessions and tabs"]
            BW6["POST /sessions/new\n{profile?: string}\n→ {session_id}\nOpen new browser window/profile"]
        end

        subgraph BROWSER_MGMT["Management Endpoints"]
            BM1["GET /health\n{status, version, uptime_seconds,\n chrome_pid, pages_open, cdp_connected}"]
            BM2["GET /descriptor\n{..., protocol: 'cdp',\n cdp_url: 'ws://localhost:9222'}"]
            BM3["GET /openapi.json\n(wrapper endpoints only — not CDP)"]
        end
    end

    subgraph BROWSER_EVIDENCE["Evidence Capture (Browser)"]
        BEV1["Captures: every web action (evidence_capture: always)"]
        BEV2["Fields: action_type, url, selector, value_hash,\ndom_hash_before, dom_hash_after,\nsnapshot_id (pzip HTML),\noauth3_scope (web.*.write or web.*.read),\ntoken_principal, ts"]
        BEV3["pzip snapshots:\nBefore and after DOM stored as pzip archives\n(what the agent saw + what changed)\nSnapshot is the 'Original' in ALCOA+"]
        BEV4["Mode: always — every web action is an evidence event\n(browser actions are irreversible by default)"]
        BEV5["OAuth3 scope enforcement:\nweb.*.read   → browse, scrape, extract\nweb.*.write  → click submit, fill, post\nweb.*.admin  → delete, publish, manage (rung 274177)\nweb.*.auth   → OAuth2 token management (rung 65537)"]
    end

    WRAPPER_ENDPOINTS --> BROWSER_EVIDENCE
```

---

## Evidence Capture Summary: All Services

```mermaid
flowchart TD
    subgraph SUMMARY["Evidence Capture Mode per Service"]
        direction TB

        T_HEADER["Service | Port | Mode | Captured Fields"]

        T_ADMIN["Admin Server\n8787 | always (proxied calls)\n| source, target, request_hash, response_hash,\n| token_principal, latency_ms, status_code"]

        T_LLM["LLM Portal\n8788 | always\n| messages_hash (not messages), tokens_used,\n| provider, model, response_hash, latency_ms"]

        T_RECIPE["Recipe Engine\n8789 | always\n| recipe_id, params_hash, hit_or_miss,\n| steps[], result_hash, overall_status"]

        T_EVIDENCE["Evidence Pipeline\n8790 | self (is the pipeline)\n| all events from all services — see chain schema"]

        T_OAUTH["OAuth3 Authority\n8791 | always\n| event_type, token_id, scope,\n| principal, expiry, error?"]

        T_CPU["CPU Service\n8792 | on-error only\n| function, args_hash, error_type,\n| error_message, stack_trace, duration_ms"]

        T_BROWSER["Browser\n9222 | always\n| action_type, url, selector, value_hash,\n| dom_hash_before/after, snapshot_id (pzip)"]
    end
```

---

## OAuth3 Scope Summary: All Services

```mermaid
flowchart TD
    subgraph SCOPE_TABLE["OAuth3 Scopes — Required per Service and Endpoint"]
        direction TB

        SC_LLM["LLM Portal (8788)\nPOST /chat, /complete → machine.llm.chat\nPOST /embed           → machine.llm.embed\nPOST /classify        → machine.llm.classify\nGET  /health, /providers → (no auth)\nPOST /providers/config → machine.llm.admin"]

        SC_RECIPE["Recipe Engine (8789)\nPOST /execute        → recipe.execute\nPOST /replay         → recipe.execute\nGET  /recipes        → recipe.store.read\nGET  /recipes/{id}   → recipe.store.read\nPOST /recipes/{id}/purge-cache → recipe.admin"]

        SC_EVIDENCE["Evidence Pipeline (8790)\nPOST /api/capture/*   → (internal — no external OAuth3)\nGET  /api/evidence/*  → evidence.read\nGET  /api/bundles/*   → evidence.read\nGET  /api/bundles/export → evidence.export\n(write endpoints: admin-proxy-internal only)"]

        SC_OAUTH["OAuth3 Authority (8791)\nPOST /api/token/issue    → (no auth — bootstrap)\nPOST /api/token/validate → (no auth — bootstrap)\nPOST /api/token/revoke   → (principal match required)\nGET  /api/tokens         → evidence.read\nGET  /api/audit          → evidence.read\nGET  /consent/*          → (UI — no token)"]

        SC_CPU["CPU Service (8792)\nPOST /compute        → machine.cpu.compute\nPOST /compute/batch  → machine.cpu.compute\nGET  /functions      → (no auth)\nPOST /functions/register → machine.cpu.admin"]

        SC_BROWSER["Browser (9222)\nPOST /action (read)  → web.*.read\nPOST /action (write) → web.*.write\nPOST /action (admin) → web.*.admin (rung 274177)\nPOST /action (auth)  → web.*.auth (rung 65537)\nGET  /page           → (no auth)\nPOST /recipe/run     → web.*.write (minimum)"]
    end
```

---

## Request/Response Flow: End-to-End Example

```mermaid
sequenceDiagram
    participant CLI as stillwater CLI
    participant ADMIN as Admin (8787)
    participant OAUTH as OAuth3 (8791)
    participant RECIPE as Recipe (8789)
    participant LLM as LLM Portal (8788)
    participant BROWSER as Browser (9222)
    participant EVIDENCE as Evidence (8790)

    CLI->>ADMIN: POST /api/proxy/recipe/execute\n{recipe_id: "linkedin-post",\n params: {content: "article text"},\n token: "tok_abc"}

    ADMIN->>OAUTH: validate(token="tok_abc", scope="recipe.execute")
    OAUTH-->>ADMIN: {valid: true, principal: "phuc"}

    ADMIN->>EVIDENCE: capture/request\n{service: "recipe", endpoint: "/execute"}
    EVIDENCE-->>ADMIN: {evidence_id: "ev_001"}

    ADMIN->>RECIPE: POST /execute {recipe_id, params}\n+ X-Evidence-Id: ev_001

    RECIPE->>RECIPE: Check cache for (recipe_id, params_hash)
    Note over RECIPE: MISS — no cached result

    RECIPE->>LLM: POST /chat {classify prompt + params}
    LLM-->>RECIPE: {classification: "web_post_action"}

    RECIPE->>EVIDENCE: capture/raw {type: "llm_step", ...}

    RECIPE->>BROWSER: POST /action\n{type: "navigate", url: "linkedin.com/post"}
    BROWSER->>BROWSER: CDP navigate command
    BROWSER->>EVIDENCE: capture/raw {type: "web_action",\n  snapshot_id: "snap_001"}
    BROWSER-->>RECIPE: {success: true, dom_hash_after: "abc..."}

    RECIPE->>BROWSER: POST /action {type: "fill", ...content}
    BROWSER-->>RECIPE: {success: true}

    RECIPE->>BROWSER: POST /action {type: "submit"}
    BROWSER->>EVIDENCE: capture/raw {type: "web_action", snapshot_id: "snap_002"}
    BROWSER-->>RECIPE: {success: true, result_url: "linkedin.com/post/123"}

    RECIPE->>EVIDENCE: capture/raw {type: "recipe_complete",\n result_hash: "...", hit: false}
    RECIPE->>RECIPE: Store result in cache

    RECIPE-->>ADMIN: {status: "complete",\n result: {url: "linkedin.com/post/123"},\n evidence_ids: ["ev_001", ...]}

    ADMIN->>EVIDENCE: capture/response {evidence_id: "ev_001", ...}
    ADMIN->>EVIDENCE: seal {evidence_ids: [ev_001, ...]}
    EVIDENCE-->>ADMIN: {bundle_id: "bun_001", root_hash: "..."}

    ADMIN-->>CLI: {status: "complete", result: {...},\n evidence_bundle_id: "bun_001"}
```

---

## Source Files

- `admin/server.py` — Admin Server (Phase 1; registry/proxy endpoints in Phase 2)
- `admin/llm_portal.py` — LLM Portal (Phase 1 service; full endpoint set)
- `papers/54-webservice-first-architecture.md` — Architectural narrative
- `diagrams/stillwater/23-service-registry.md` — ServiceDescriptor model and registry flow
- `diagrams/stillwater/24-service-mesh.md` — Inter-service communication topology
- `diagrams/stillwater/20-oauth3-flow.md` — OAuth3 token lifecycle (OAuth3 Authority design)

---

## Coverage

- All 7 service types: port, role, evidence mode, OAuth3 scope requirements
- Admin Server: registry endpoints (6) + proxy endpoint + existing Phase 1 endpoints
- LLM Portal: chat/complete/embed/classify + provider routing (BYOK vs managed) + management
- Recipe Engine: execute/replay + step classification (LLM/CPU/web/sub-recipe) + hit rate
- Evidence Pipeline: capture endpoints (4) + query endpoints (5) + hash chain schema + ALCOA+ mapping
- OAuth3 Authority: token lifecycle (issue/validate/refresh/revoke) + consent UI + vault storage
- CPU Service: compute endpoints + built-in function catalog (7 functions) + safety model + allowlist
- Browser: CDP architecture + REST wrapper endpoints (6) + pzip snapshot evidence + scope per action type
- Evidence capture modes per service: never / on-error / always — with justification
- OAuth3 scope table: every endpoint for every service with required scope
- End-to-end example: linkedin-post recipe through all 7 services with evidence chain
