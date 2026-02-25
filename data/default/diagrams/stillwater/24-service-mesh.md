# Diagram 24: Service Mesh — Inter-Service Communication

**Description:** The Stillwater service mesh connects seven services (Admin, LLM Portal, Recipe Engine, Evidence Pipeline, OAuth3 Authority, CPU Service, Browser) through a hub-and-spoke topology centered on the Admin Server (8787). All external-facing calls route through the admin proxy. Services can also call each other directly for performance-critical paths, but all such direct calls are captured by the Evidence Pipeline. OAuth3 Authority enforces scope requirements on every call that the admin proxy routes.

---

## Full Service Mesh: All 7 Services and Connections

```mermaid
flowchart TD
    subgraph EXTERNAL["External Callers"]
        CLI["stillwater CLI\n(thin HTTP client)"]
        BROWSER_EXT["Browser Extension\n(solace-browser)"]
        REMOTE["Remote Client\n(via tunnel: solaceagi.com)"]
    end

    subgraph MESH["Service Mesh — localhost:8787–9222"]
        direction TB

        ADMIN["Admin Server\nlocalhost:8787\nService registry + proxy\nOAuth3 header injection\nEvidence capture routing"]

        LLM["LLM Portal\nlocalhost:8788\nMulti-provider LLM\nBYOK + managed"]

        RECIPE["Recipe Engine\nlocalhost:8789\nRecipe execution\nStep routing + replay\nHit rate tracking"]

        EVIDENCE["Evidence Pipeline\nlocalhost:8790\nHash-chained JSONL\nTamper-evident audit\nPart 11 capture"]

        OAUTH["OAuth3 Authority\nlocalhost:8791\nToken issuance\nScope validation\nRevocation"]

        CPU["CPU Service\nlocalhost:8792\nDeterministic computation\nExact arithmetic\nNo LLM calls"]

        BROWSER["Browser\nlocalhost:9222\nChrome DevTools Protocol\nWeb automation\nSnapshot capture"]
    end

    subgraph PERSISTENCE["Persistence Layer"]
        REG_JSON["artifacts/admin/\nservice_registry.json"]
        EV_JSONL["artifacts/evidence/\nevidence_pipeline.jsonl"]
        OAUTH_STORE["~/.stillwater/\noauth3_vault.enc\n(AES-256-GCM)"]
    end

    CLI & BROWSER_EXT & REMOTE --> ADMIN

    ADMIN -->|"proxy + OAuth3 check"| LLM & RECIPE & EVIDENCE & OAUTH & CPU & BROWSER
    ADMIN --> REG_JSON

    RECIPE -->|"direct: LLM call"| LLM
    RECIPE -->|"direct: CPU step"| CPU
    RECIPE -->|"direct: web step"| BROWSER
    RECIPE -->|"capture: every step"| EVIDENCE

    LLM -->|"capture: every call"| EVIDENCE
    CPU -->|"capture: on-error only"| EVIDENCE
    BROWSER -->|"capture: every action"| BROWSER
    BROWSER -->|"snapshot + evidence"| EVIDENCE

    OAUTH -->|"persist tokens"| OAUTH_STORE
    EVIDENCE --> EV_JSONL

    style ADMIN fill:#1a3a2a,stroke:#3fb950
    style OAUTH fill:#2a1a3a,stroke:#a371f7
    style EVIDENCE fill:#1a2a3a,stroke:#58a6ff
```

---

## CLI → Admin → Service Routing

```mermaid
sequenceDiagram
    participant CLI as stillwater CLI
    participant ADMIN as Admin Server (8787)
    participant OAUTH as OAuth3 Authority (8791)
    participant RECIPE as Recipe Engine (8789)
    participant EVIDENCE as Evidence Pipeline (8790)

    CLI->>ADMIN: POST /api/proxy/recipe/execute\n{recipe_id, params, oauth3_token}
    ADMIN->>ADMIN: Lookup "recipe" in registry\n→ port 8789, oauth3_required: true

    ADMIN->>OAUTH: POST /api/token/validate\n{token, required_scope: "recipe.execute"}
    OAUTH-->>ADMIN: {valid: true, principal: "phuc", scopes: [...], expires: "..."}

    ADMIN->>EVIDENCE: POST /api/capture/request\n{service: "recipe", endpoint: "/execute",\n request_hash: SHA256(body), token_principal: "phuc"}
    EVIDENCE-->>ADMIN: {evidence_id: "ev_abc123"}

    ADMIN->>RECIPE: POST /execute\n{recipe_id, params}\n+ headers: X-Evidence-Id: ev_abc123\n            X-OAuth3-Principal: phuc\n            X-Request-Ts: ISO8601

    RECIPE-->>ADMIN: {status: "complete", result: {...}, steps_executed: 5}

    ADMIN->>EVIDENCE: POST /api/capture/response\n{evidence_id: "ev_abc123",\n response_hash: SHA256(body),\n status: "complete"}
    EVIDENCE-->>ADMIN: {evidence_id: "ev_abc123", sealed: true}

    ADMIN-->>CLI: {status: "complete", result: {...},\n evidence_id: "ev_abc123"}
```

---

## Browser → Admin → LLM Routing

```mermaid
sequenceDiagram
    participant BEXT as Browser Extension
    participant ADMIN as Admin Server (8787)
    participant OAUTH as OAuth3 Authority (8791)
    participant LLM as LLM Portal (8788)
    participant EVIDENCE as Evidence Pipeline (8790)

    BEXT->>ADMIN: POST /api/proxy/llm/chat\n{messages: [...], oauth3_token}
    ADMIN->>ADMIN: Lookup "llm" in registry\n→ port 8788, oauth3_required: true,\n  evidence_capture: "always"

    ADMIN->>OAUTH: POST /api/token/validate\n{token, required_scope: "machine.llm.chat"}
    OAUTH-->>ADMIN: {valid: true, principal: "phuc"}

    ADMIN->>EVIDENCE: POST /api/capture/request\n{service: "llm", endpoint: "/chat",\n request_hash: SHA256(messages),\n token_principal: "phuc",\n model_hint: "llama-3.3-70b"}
    EVIDENCE-->>ADMIN: {evidence_id: "ev_def456"}

    ADMIN->>LLM: POST /chat\n{messages: [...]}\n+ X-Evidence-Id: ev_def456\n  X-Provider-Hint: "managed"\n  X-OAuth3-Principal: phuc

    LLM->>LLM: Route to provider\n(BYOK: user key | Managed: platform key)
    LLM-->>ADMIN: {content: "...", tokens_used: 847,\n provider: "llama", model: "llama-3.3-70b-instruct"}

    ADMIN->>EVIDENCE: POST /api/capture/response\n{evidence_id: "ev_def456",\n tokens_used: 847,\n response_hash: SHA256(content)}
    EVIDENCE-->>ADMIN: {sealed: true}

    ADMIN-->>BEXT: {content: "...", evidence_id: "ev_def456"}
```

---

## Recipe Engine → LLM + Browser + CPU Routing

```mermaid
flowchart TD
    subgraph RECIPE_EXECUTION["Recipe Engine Step Routing"]
        direction TB

        TASK["Incoming task:\n{recipe_id, params}"]
        TASK --> REPLAY{"Recipe hit?\n(cached result\nfor these params?)"}

        REPLAY -->|"HIT (70% target)"| CACHED["Return cached result\nNo LLM call\nEvidence: cache-hit record"]
        REPLAY -->|"MISS"| CLASSIFY["LLM step:\nClassify task intent\nPOST /proxy/llm/chat\n{messages: classify_prompt + params}"]

        CLASSIFY --> ROUTE{"Step type?"}

        ROUTE -->|"web action"| WEB["Browser step:\nPOST /proxy/browser/action\n{action, selector, url}\nOAuth3 scope: web.*.write\nEvidence: CDP snapshot"]

        ROUTE -->|"computation"| CPU_STEP["CPU step:\nPOST /proxy/cpu/compute\n{function, args}\nOAuth3 scope: machine.cpu\nEvidence: on-error only"]

        ROUTE -->|"LLM reasoning"| LLM_STEP["LLM step:\nPOST /proxy/llm/chat\n{messages: reasoning_prompt}\nOAuth3 scope: machine.llm.chat\nEvidence: always"]

        ROUTE -->|"sub-recipe"| SUB_RECIPE["Sub-recipe:\nPOST /proxy/recipe/execute\n{recipe_id: sub_id, params}\nRecurse into Recipe Engine\nEvidence: nested bundle"]

        WEB & CPU_STEP & LLM_STEP & SUB_RECIPE --> COLLECT["Collect step results\n+ evidence IDs"]
        COLLECT --> ASSEMBLE["Assemble final result\nBundle all evidence IDs\nCompute overall status"]
        ASSEMBLE --> CACHE_STORE["Store result in\nrecipe cache\n(for future hits)"]
        CACHE_STORE --> RETURN["Return to caller:\n{result, evidence_ids: [...], hit_rate_updated: true}"]
    end

    CACHED & RETURN --> END["Response to admin proxy"]
```

---

## Evidence Pipeline: Captures from All Services

```mermaid
flowchart TD
    subgraph EVIDENCE_SOURCES["Evidence Sources — All Services"]
        LLM_EV["LLM Portal\nevidence_capture: always\n→ every chat, embed, classify call\n→ tokens_used, provider, model, latency"]
        RECIPE_EV["Recipe Engine\nevidence_capture: always\n→ every recipe execution start/end\n→ hit/miss, steps, sub-recipes"]
        OAUTH_EV["OAuth3 Authority\nevidence_capture: always\n→ every issue, validate, revoke\n→ principal, scope, expiry"]
        CPU_EV["CPU Service\nevidence_capture: on-error\n→ only failed computations\n→ input, error, stack trace"]
        BROWSER_EV["Browser\nevidence_capture: always\n→ every web action\n→ CDP snapshot (pzip compressed)\n→ selector, before/after DOM hash"]
        ADMIN_EV["Admin Proxy\nevidence_capture: always\n→ every proxied request/response\n→ source, target service, latency"]
    end

    subgraph EVIDENCE_PIPELINE["Evidence Pipeline (8790)"]
        direction TB
        INGEST["POST /api/capture/request\nPOST /api/capture/response\n→ Receive structured evidence events"]
        HASH["Compute SHA-256\nfor request + response payloads"]
        CHAIN["Hash-chain entry:\nentry_hash = SHA256(entry + prev_hash)\n(tamper-evident append-only)"]
        APPEND["Append to\nartifacts/evidence/evidence_pipeline.jsonl"]
        SEAL["POST /api/capture/seal\n→ Finalize evidence bundle\n→ Issue bundle_id with root hash"]
    end

    subgraph QUERY["Evidence Query API"]
        Q1["GET /api/evidence/{evidence_id}\n→ Single event record"]
        Q2["GET /api/bundles/{bundle_id}\n→ Full bundle with chain verification"]
        Q3["GET /api/bundles/{bundle_id}/export\n→ Export for Part 11 audit\n   (structured JSON with ALCOA+ fields)"]
    end

    LLM_EV & RECIPE_EV & OAUTH_EV & CPU_EV & BROWSER_EV & ADMIN_EV --> INGEST
    INGEST --> HASH --> CHAIN --> APPEND --> SEAL
    SEAL --> QUERY
```

---

## OAuth3 Enforcement: All Services

```mermaid
flowchart TD
    subgraph ENFORCEMENT_MODEL["OAuth3 Enforcement on All Services"]
        direction TB

        REQUEST["Incoming request to\nAdmin Proxy\n(any service, any endpoint)"]

        REQUEST --> CHECK_DESCRIPTOR{"Service has\noauth3_required: true?"}
        CHECK_DESCRIPTOR -->|"No — pass through"| FORWARD_DIRECT["Forward to service\n(no token check)"]

        CHECK_DESCRIPTOR -->|"Yes"| EXTRACT_TOKEN["Extract token from\nAuthorization: Bearer {token}\nor X-OAuth3-Token: {token}"]

        EXTRACT_TOKEN --> HAS_TOKEN{"Token present?"}
        HAS_TOKEN -->|"No"| REJECT_401["Return 401\n{error: 'missing_token',\n required_scope: '...',\n service: service_id}"]

        HAS_TOKEN -->|"Yes"| VALIDATE["POST /api/token/validate\n{token, required_scope}\nto OAuth3 Authority (8791)"]

        VALIDATE --> VALID{"Valid?"}
        VALID -->|"No — expired"| REJECT_401_EXP["Return 401\n{error: 'token_expired',\n refresh_hint: '/api/token/refresh'}"]
        VALID -->|"No — wrong scope"| REJECT_403["Return 403\n{error: 'insufficient_scope',\n granted: [...],\n required: '...'}"]
        VALID -->|"No — revoked"| REJECT_401_REV["Return 401\n{error: 'token_revoked',\n revoked_at: ISO8601}"]
        VALID -->|"Yes"| INJECT["Inject headers:\nX-OAuth3-Principal: {principal}\nX-OAuth3-Scope: {scope}\nX-OAuth3-Token-Id: {token_id}"]

        INJECT --> FORWARD_AUTH["Forward to service\nwith injected headers"]
        FORWARD_DIRECT & FORWARD_AUTH --> EVIDENCE_CAPTURE["Evidence Pipeline\ncaptures request + response\n(if service.evidence_capture != 'never')"]
    end

    subgraph SCOPE_MAP["Service → Required OAuth3 Scope"]
        S_LLM["LLM Portal → machine.llm.chat\n          machine.llm.embed\n          machine.llm.classify"]
        S_RECIPE["Recipe Engine → recipe.execute\n              recipe.replay\n              recipe.store.read"]
        S_EVIDENCE["Evidence Pipeline → evidence.read\n                   evidence.export\n(write: internal only — no scope)"]
        S_OAUTH["OAuth3 Authority → No OAuth3\n(auth bootstrap — cannot require own token)"]
        S_CPU["CPU Service → machine.cpu.compute"]
        S_BROWSER["Browser → web.*.read\n          web.*.write\n          web.*.admin (destructive)"]
    end
```

---

## Tunnel: Services Exposed to solaceagi.com

```mermaid
flowchart LR
    subgraph LOCAL["Local Service Mesh (localhost)"]
        L_ADMIN["Admin (8787)"]
        L_LLM["LLM Portal (8788)"]
        L_RECIPE["Recipe Engine (8789)"]
        L_EVIDENCE["Evidence Pipeline (8790)"]
        L_OAUTH["OAuth3 Authority (8791)"]
        L_CPU["CPU Service (8792)"]
        L_BROWSER["Browser (9222)"]
    end

    subgraph TUNNEL["Tunnel Service\n(solace-cli PRIVATE)"]
        T_AGENT["Tunnel agent\n(opens outbound WS to solaceagi.com)\nUser selects which services to expose"]
    end

    subgraph CLOUD["solaceagi.com"]
        C_RELAY["Tunnel relay\n(assigns tunnel_id per user)"]
        C_PLATFORM["Platform services\n(OAuth3 vault sync, evidence archive,\nmanaged LLM, cloud twin)"]
        C_CLIENT["Remote clients\n(browser extension, CLI, API)"]
    end

    L_ADMIN & L_LLM & L_RECIPE --> TUNNEL
    TUNNEL --> C_RELAY
    C_RELAY --> C_PLATFORM
    C_CLIENT -->|"tunnel_id/llm/...\ntunnel_id/recipe/...\ntunnel_id/admin/..."| C_RELAY
    C_RELAY -->|"route through tunnel"| L_ADMIN & L_LLM & L_RECIPE

    note["Tunnel is per-service:\nUser can expose LLM but not Evidence\nAdmin proxy enforces same OAuth3\ngates on tunneled requests"]
```

---

## Source Files

- `admin/server.py` — Admin Server (Phase 1; proxy and registry endpoints added in Phase 2)
- `admin/llm_portal.py` — LLM Portal (Phase 1; first service to join mesh)
- `papers/54-webservice-first-architecture.md` — Full architectural narrative
- `data/default/diagrams/stillwater/23-service-registry.md` — Service registry detail
- `data/default/diagrams/stillwater/25-service-types.md` — Per-service endpoint catalog
- `data/default/diagrams/stillwater/20-oauth3-flow.md` — OAuth3 token lifecycle

---

## Coverage

- Full 7-service topology (Admin, LLM, Recipe, Evidence, OAuth3, CPU, Browser)
- CLI → admin → service routing with OAuth3 validation and evidence capture
- Browser extension → admin → LLM routing with provider selection
- Recipe Engine step routing: hit/miss, web/CPU/LLM/sub-recipe classification
- Evidence Pipeline: all 6 capture sources, hash-chaining, bundle sealing
- OAuth3 enforcement flow: token extraction, validation, scope check, header injection
- Per-service OAuth3 scope requirements table
- Tunnel architecture: local → outbound WS → solaceagi.com relay → remote clients
- Error cases: missing token (401), expired (401), wrong scope (403), revoked (401)
- Evidence capture modes: never, on-error, always — per service
