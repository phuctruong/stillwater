# Diagram 16: Admin Server Endpoints and Security Model

**Description:** The Stillwater Admin Server (`admin/server.py`) is a Python `ThreadingHTTPServer` running on `localhost:8787`. It provides a web UI for editing skills, recipes, and swarms within the repo, as well as LLM configuration, community linking, and safe CLI execution. All file operations enforce path traversal prevention, an allowed-directory allowlist, and a write-suffix whitelist. CLI execution uses a strict command allowlist.

---

## All HTTP Endpoints

```mermaid
flowchart TD
    subgraph SERVER["Admin Server — admin/server.py\nlocalhost:8787"]
        direction TB

        subgraph GET_ROUTES["GET Routes"]
            G1["GET /\n→ Serve admin/static/index.html"]
            G2["GET /static/{file}\n→ Serve static assets\n(path traversal guarded)"]
            G3["GET /api/catalog\n→ List all skills/recipes/swarms/papers\n(grouped by CATALOG_GROUPS)"]
            G4["GET /api/file?path=...\n→ Read file content + SHA-256\n(allowed paths only)"]
            G5["GET /api/llm/status\n→ Active provider, Ollama probe, models list"]
            G6["GET /api/community/status\n→ Linked email, sync event count"]
            G7["GET /api/cli/commands\n→ List SAFE_CLI_COMMANDS keys"]
        end

        subgraph POST_ROUTES["POST Routes (JSON body)"]
            P1["POST /api/file/save\n{path, content}\n→ Save file (allowed paths + suffix check)"]
            P2["POST /api/file/create\n{group, filename}\n→ Create new file from template\n(CATALOG_GROUPS template)"]
            P3["POST /api/llm/config\n{provider, ollama_url, ollama_model}\n→ Update llm_config.yaml"]
            P4["POST /api/system/install-ollama\n{sudo_password}\n→ Run Ollama install script"]
            P5["POST /api/ollama/pull\n{model, ollama_url}\n→ ollama pull {model}"]
            P6["POST /api/community/link\n{email}\n→ Mock magic link (stub)"]
            P7["POST /api/community/sync\n{direction}\n→ Upload skills/recipes, fetch remote"]
            P8["POST /api/cli/run\n{command}\n→ Run allowlisted CLI command"]
        end
    end
```

---

## Path Traversal Prevention

```mermaid
flowchart TD
    INPUT["Client sends path string\n(e.g. '../../etc/passwd'\nor 'skills/my-skill.md')"]

    INPUT --> RESOLVE["_safe_resolve_repo_path(raw)\n= (REPO_ROOT / raw).resolve()"]
    RESOLVE --> CHECK_REPO{"Does resolved path\nstart with REPO_ROOT?"}
    CHECK_REPO -->|"No — path escapes repo"| ERR400["400 Bad Request\n'path escapes repo'"]
    CHECK_REPO -->|"Yes"| CHECK_ALLOWED["_is_allowed_edit_path(path)"]

    subgraph ALLOWED_CHECK["_is_allowed_edit_path()"]
        SUFFIX["Check suffix in\nALLOWED_WRITE_SUFFIXES\n(.md .txt .yaml .yml .json)"]
        SUFFIX -->|"No"| DENY["Return False\n(executables, .py, .sh blocked)"]
        SUFFIX -->|"Yes"| SCAN["Scan _allowed_paths():\n  - All CATALOG_GROUPS dirs\n  - EXTRA_EDITABLE_FILES list"]
        SCAN -->|"Path in allowlist"| ALLOW["Return True"]
        SCAN -->|"Not in allowlist"| DENY
    end

    CHECK_ALLOWED --> ALLOWED_CHECK
    ALLOW --> READ_WRITE["Perform read/write operation"]
    DENY --> ERR400_2["400 PermissionError response"]

    subgraph SAFE_SUFFIXES["ALLOWED_WRITE_SUFFIXES"]
        S1[".md"]
        S2[".txt"]
        S3[".yaml"]
        S4[".yml"]
        S5[".json"]
    end

    subgraph BLOCKED["Implicitly blocked (no suffix match)"]
        B1[".py — no Python execution via UI"]
        B2[".sh — no shell script writes"]
        B3[".exe / .bin — no executables"]
        B4["Any other extension"]
    end
```

---

## CLI Command Allowlist Enforcement

```mermaid
flowchart TD
    REQ["POST /api/cli/run\n{command: 'doctor'}"]
    REQ --> LOOKUP{"command in\nSAFE_CLI_COMMANDS?"}

    subgraph ALLOWLIST["SAFE_CLI_COMMANDS (hardcoded dict)"]
        C1["'version'\n→ ['python', '-m', 'stillwater', '--version']"]
        C2["'doctor'\n→ ['python', '-m', 'stillwater', 'doctor']"]
        C3["'llm-status'\n→ ['python', '-m', 'stillwater', 'llm', 'status']"]
    end

    LOOKUP -->|"Yes"| GET_CMD["Look up exact command list\nfrom SAFE_CLI_COMMANDS"]
    LOOKUP -->|"No"| ERR["ValueError:\n'command not allowed'\nReturns 400"]

    GET_CMD --> SETENV["Set PYTHONPATH=src/cli/src\nin subprocess env"]
    SETENV --> RUN["subprocess.run(\ncmd, cwd=REPO_ROOT,\ncapture_output=True,\ntimeout=30s)"]
    RUN --> RESULT["Return: {command, cmd, returncode,\nstdout (last 5000 chars),\nstderr (last 5000 chars), ok}"]

    style ALLOWLIST text-align:left
    style C1 text-align:left
    style C2 text-align:left
    style C3 text-align:left
```

---

## File Operations Security Model

```mermaid
flowchart TD
    subgraph READ_OP["Read: GET /api/file?path=..."]
        R1["_safe_resolve_repo_path(path)"] --> R2["Path escapes repo? → 400"]
        R2 --> R3["_is_allowed_edit_path()? → 400 if not"]
        R3 --> R4["Read file text + compute SHA-256"]
        R4 --> R5["Return {path, content, size, sha256}"]
    end

    subgraph SAVE_OP["Save: POST /api/file/save"]
        S1["_safe_resolve_repo_path(path)"] --> S2["_is_allowed_edit_path()? → 400 if not"]
        S2 --> S3["len(content.encode()) > 2MB? → 400 if too large"]
        S3 --> S4["path.parent.mkdir(parents=True)"]
        S4 --> S5["path.write_text(content)"]
        S5 --> S6["Return _file_payload() with new SHA-256"]
    end

    subgraph CREATE_OP["Create: POST /api/file/create"]
        C1["Validate filename\nmatches [A-Za-z0-9._-]+"] --> C2["Look up group_id\nin CATALOG_GROUPS"]
        C2 --> C3["Compute target path\nin group['dirs'][0]"]
        C3 --> C4["_is_allowed_edit_path()? → 400 if not"]
        C4 --> C5["target.exists()? → 409 FileExistsError"]
        C5 --> C6["Write group template\ncreate_template string"]
        C6 --> C7["Return {path, created: True}"]
    end

    subgraph STATIC_OP["Static: GET /static/{file}"]
        T1["Resolve path under\nadmin/static/"] --> T2["Path within admin/static/?\n(startswith check)"]
        T2 -->|"No"| T3["404 not found"]
        T2 -->|"Yes"| T4["Serve file bytes\nwith guessed MIME type"]
    end
```

---

## Catalog Groups (Editable Content Registry)

```mermaid
flowchart LR
    CATALOG["CATALOG_GROUPS\n(server.py)"]

    CATALOG --> G1["root_skills\n→ skills/*.md"]
    CATALOG --> G2["swarms\n→ swarms/*.md"]
    CATALOG --> G3["root_recipes\n→ recipes/*.md"]
    CATALOG --> G4["papers\n→ papers/*.md"]
    CATALOG --> G5["community\n→ community/*.md"]
    CATALOG --> G6["recipes\n→ src/cli/recipes/*.md\n   src/cli/extensions/recipes/*.md"]
    CATALOG --> G7["skills\n→ src/cli/extensions/skills/*.md"]
    CATALOG --> G8["personas\n→ src/cli/extensions/personas/*.md"]
    CATALOG --> G9["identity\n→ src/cli/identity/*.md\n   src/cli/extensions/identity/*.md"]
    CATALOG --> G10["settings\n→ src/cli/settings/*.md"]

    EXTRA["EXTRA_EDITABLE_FILES\n(not in catalog groups)"]
    EXTRA --> E1["llm_config.yaml"]
    EXTRA --> E2["src/cli/extensions/splash.txt"]
    EXTRA --> E3["CLAUDE.md"]
    EXTRA --> E4["admin/README.md"]
```

---

## Community Link Flow

```mermaid
sequenceDiagram
    participant UI as Admin UI
    participant SERVER as Admin Server
    participant FS as artifacts/admin/

    UI->>SERVER: POST /api/community/link {email: "user@example.com"}
    SERVER->>SERVER: Validate email regex [^@\s]+@[^@\s]+\.[^@\s]+
    SERVER->>SERVER: secrets.token_urlsafe(24) → magic token
    SERVER->>SERVER: secrets.token_hex(16) → mock api_key
    SERVER->>FS: _write_json(community_link.json, payload)
    SERVER-->>UI: {email, status:"magic_link_sent_mock", login_link_stub, api_key, note}

    UI->>SERVER: POST /api/community/sync {direction: "both"}
    SERVER->>SERVER: Count src/cli/recipes/*.md + skills/*.md
    SERVER->>FS: _append_jsonl(community_sync.jsonl, row)
    SERVER-->>UI: {timestamp, direction, uploaded:{recipes,skills}, remote_available:[], status:"mock_sync_complete"}

    Note over SERVER,FS: Stub flow — real email delivery and<br/>API auth will be wired in a future phase
```

---

## Source Files

- `admin/server.py` — ThreadingHTTPServer, AdminHandler, all endpoint logic
- `admin/server.py` — `_safe_resolve_repo_path`, `_is_allowed_edit_path`, `ALLOWED_WRITE_SUFFIXES`
- `admin/server.py` — `SAFE_CLI_COMMANDS`, `_run_cli_command`, `CATALOG_GROUPS`, `EXTRA_EDITABLE_FILES`
- `admin/server.py` — `_community_link`, `_community_sync`, `_llm_status`, `_update_llm_config`

---

## Coverage

- All 15 HTTP endpoints (7 GET + 8 POST) with their exact path strings
- Path traversal prevention: `_safe_resolve_repo_path` + `_is_allowed_edit_path`
- Write suffix whitelist (`.md .txt .yaml .yml .json` — executables blocked)
- CLI command allowlist (`version`, `doctor`, `llm-status` only)
- CATALOG_GROUPS: 10 content groups covering all editable repo directories
- EXTRA_EDITABLE_FILES: 4 specific files outside catalog groups
- File size limit (2 MB) and filename character validation (`[A-Za-z0-9._-]+`)
- Static file serving with path containment check
- Community link stub flow (magic link + sync)
- Subprocess execution: cwd=REPO_ROOT, PYTHONPATH=src/cli/src, timeout=30s
