# Stillwater Admin API Contracts

## Overview

All endpoints return JSON responses with an `"ok"` field indicating success (true) or failure (false).

Base URL: `http://127.0.0.1:8787`

## Catalog API

### GET /api/catalog

Fetch the complete catalog structure with all discoverable files grouped by category.

**Method**: GET

**Query Parameters**: None

**Request Body**: None

**Response (200 OK)**:
```json
{
  "ok": true,
  "groups": [
    {
      "id": "root_skills",
      "title": "Skills",
      "files": [
        {
          "path": "skills/prime-safety.md",
          "name": "prime-safety.md",
          "group": "root_skills",
          "dir": "skills"
        }
      ],
      "count": 15
    }
  ],
  "extras": [
    {
      "path": "llm_config.yaml",
      "name": "llm_config.yaml",
      "group": "extras",
      "dir": "."
    }
  ]
}
```

**Catalog Groups**:
- `root_skills` → Skills directory
- `swarms` → Swarm agents directory
- `root_recipes` → Root recipes directory
- `papers` → Papers directory
- `community` → Community docs directory
- `recipes` → CLI recipes directory
- `skills` → CLI extensions skills directory
- `personas` → Personas directory
- `identity` → Identity notes directory
- `settings` → Settings directory

---

## File API

### GET /api/file

Fetch a single file's content, size, and SHA256 hash.

**Method**: GET

**Query Parameters**:
- `path` (required): Relative path to file (e.g., `skills/prime-safety.md`)

**Request Body**: None

**Response (200 OK)**:
```json
{
  "ok": true,
  "path": "skills/prime-safety.md",
  "content": "# Prime Safety\n\nFail-closed safety...",
  "size": 12456,
  "sha256": "abc123def456..."
}
```

**Errors**:
- **400**: File not found or path not allowed
  ```json
  { "ok": false, "error": "FileNotFoundError: skills/nonexistent.md" }
  ```
- **400**: Permission denied (outside ALLOWED_PATHS)
  ```json
  { "ok": false, "error": "PermissionError: /etc/passwd" }
  ```

---

### POST /api/file/save

Save file content to disk. File must be in an allowed path and have a safe suffix.

**Method**: POST

**Request Body**:
```json
{
  "path": "skills/new-skill.md",
  "content": "# New Skill\n\nDescription..."
}
```

**Response (200 OK)**:
```json
{
  "ok": true,
  "path": "skills/new-skill.md",
  "content": "# New Skill\n\nDescription...",
  "size": 1024,
  "sha256": "def789ghi012..."
}
```

**Constraints**:
- `path` must resolve to a safe location (within REPO_ROOT, in ALLOWED_PATHS)
- File suffix must be in ALLOWED_WRITE_SUFFIXES: .md, .txt, .yaml, .yml, .json
- File size must be ≤ 2,000,000 bytes

**Errors**:
- **400**: Invalid path or suffix
  ```json
  { "ok": false, "error": "PermissionError: /home/user/secrets.txt" }
  ```
- **400**: File too large
  ```json
  { "ok": false, "error": "ValueError: file too large" }
  ```

---

### POST /api/file/create

Create a new file in a catalog group with template content.

**Method**: POST

**Request Body**:
```json
{
  "group": "root_skills",
  "filename": "my-skill"
}
```

**Response (200 OK)**:
```json
{
  "ok": true,
  "path": "skills/my-skill.md",
  "created": true
}
```

**Behavior**:
- If `filename` has no extension, `.md` is appended
- Template content is inserted based on the group's `create_template`
- If directory doesn't exist, it is created

**Errors**:
- **400**: Invalid filename format (must match `[A-Za-z0-9._-]+`)
  ```json
  { "ok": false, "error": "ValueError: filename must match [A-Za-z0-9._-]+" }
  ```
- **400**: Unknown group ID
  ```json
  { "ok": false, "error": "ValueError: unknown group: invalid_group" }
  ```
- **400**: File already exists
  ```json
  { "ok": false, "error": "FileExistsError: my-skill.md" }
  ```

---

## LLM API

### GET /api/llm/status

Fetch current LLM configuration status, available Ollama instances, and models.

**Method**: GET

**Query Parameters**: None

**Request Body**: None

**Response (200 OK)**:
```json
{
  "ok": true,
  "status": {
    "provider": "ollama",
    "provider_name": "Ollama (Local)",
    "provider_url": "http://127.0.0.1:11434",
    "provider_model": "llama2",
    "setup_ok": true,
    "setup_msg": "Valid configuration",
    "probes": [
      {
        "url": "http://127.0.0.1:11434",
        "latency_ms": 2.5,
        "status": "online"
      }
    ],
    "preferred_ollama_url": "http://127.0.0.1:11434",
    "models": [
      "llama2",
      "mistral",
      "neural-chat"
    ],
    "ollama_installed": true
  }
}
```

**Fields**:
- `provider`: Active provider name (empty if unconfigured)
- `provider_name`: Human-readable provider name
- `provider_url`: Provider endpoint URL
- `provider_model`: Selected model name
- `setup_ok`: Configuration is valid
- `setup_msg`: Status message or error details
- `probes`: List of discovered Ollama instances with latency
- `preferred_ollama_url`: Best Ollama instance found
- `models`: Available models on preferred instance
- `ollama_installed`: Ollama binary is in PATH

---

### POST /api/llm/config

Update LLM provider configuration.

**Method**: POST

**Request Body**:
```json
{
  "provider": "ollama",
  "ollama_url": "http://127.0.0.1:11434",
  "ollama_model": "llama2"
}
```

**Response (200 OK)**:
```json
{
  "ok": true,
  "status": {
    "provider": "ollama",
    "provider_name": "Ollama (Local)",
    "provider_url": "http://127.0.0.1:11434",
    "provider_model": "llama2",
    "setup_ok": true,
    "setup_msg": "Valid configuration",
    ...
  }
}
```

**Behavior**:
- Updates `llm_config.yaml` in REPO_ROOT
- Empty strings (`""`) clear the field to None
- Returns updated status immediately

**Errors**:
- **400**: llm_config_manager unavailable
  ```json
  { "ok": false, "error": "RuntimeError: llm config helper unavailable" }
  ```

---

### POST /api/system/install-ollama

Install Ollama system-wide using `curl ... | sh` and sudo.

**Method**: POST

**Request Body**:
```json
{
  "sudo_password": "user_password"
}
```

**Response (200 OK)**:
```json
{
  "ok": true,
  "changed": true,
  "message": "Ollama install completed.",
  "returncode": 0,
  "stdout": "...installation output...",
  "stderr": ""
}
```

**Response (500) - Install Failed**:
```json
{
  "ok": false,
  "changed": false,
  "message": "Ollama install failed.",
  "returncode": 1,
  "stdout": "...output...",
  "stderr": "...error..."
}
```

**Behavior**:
- If Ollama is already installed, returns immediately with `changed: false`
- Platform-aware: uses correct installer for Ubuntu/Debian, macOS, etc.
- Runs with `sudo -S` to read password from stdin

**Errors**:
- **400**: No sudo password provided
  ```json
  { "ok": false, "error": "ValueError: sudo password is required" }
  ```

---

### POST /api/ollama/pull

Pull a model from Ollama repository.

**Method**: POST

**Request Body**:
```json
{
  "model": "llama2",
  "ollama_url": "http://127.0.0.1:11434"
}
```

**Response (200 OK)**:
```json
{
  "ok": true,
  "message": "model pull completed",
  "returncode": 0,
  "stdout": "pulling manifest...",
  "stderr": ""
}
```

**Response (500) - Pull Failed**:
```json
{
  "ok": false,
  "message": "model pull failed",
  "returncode": 1,
  "stdout": "...output...",
  "stderr": "...error..."
}
```

**Behavior**:
- Runs `ollama pull <model>` on the system
- Sets `OLLAMA_HOST` env var if `ollama_url` is provided
- Timeout: 3600 seconds (1 hour)

**Errors**:
- **400**: Model name not provided
  ```json
  { "ok": false, "error": "ValueError: model is required" }
  ```
- **400**: Ollama binary not installed
  ```json
  { "ok": false, "error": "RuntimeError: ollama binary is not installed" }
  ```

---

## Service Registry API

### GET /api/services

List all registered services.

**Method**: GET

**Query Parameters**: None

**Request Body**: None

**Response (200 OK)**:
```json
{
  "ok": true,
  "services": [
    {
      "service_id": "llm-portal",
      "service_type": "LLM",
      "name": "LLM Portal",
      "version": "1.0.0",
      "host": "127.0.0.1",
      "port": 8788,
      "health_endpoint": "/api/health",
      "openapi_endpoint": "/openapi.json",
      "oauth3_scopes": [],
      "evidence_capture": false,
      "metadata": {},
      "status": "ONLINE",
      "last_health_check": "2026-02-23T10:30:00Z"
    }
  ]
}
```

**Service Types**: CUSTOM, LLM, RECIPE, EVIDENCE, OAUTH3, CPU, BROWSER

---

### POST /api/services/register

Register a new service manually.

**Method**: POST

**Request Body**:
```json
{
  "service_id": "my-service",
  "service_type": "CUSTOM",
  "name": "My Service",
  "version": "1.0.0",
  "host": "127.0.0.1",
  "port": 9999,
  "health_endpoint": "/api/health",
  "openapi_endpoint": "/openapi.json",
  "oauth3_scopes": [],
  "evidence_capture": false,
  "metadata": {}
}
```

**Response (200 OK)**:
```json
{
  "ok": true,
  "service": {
    "service_id": "my-service",
    "service_type": "CUSTOM",
    "name": "My Service",
    "version": "1.0.0",
    "host": "127.0.0.1",
    "port": 9999,
    "health_endpoint": "/api/health",
    "openapi_endpoint": "/openapi.json",
    "oauth3_scopes": [],
    "evidence_capture": false,
    "metadata": {},
    "status": "STARTING",
    "last_health_check": null
  }
}
```

**Errors**:
- **400**: Invalid service data (validation error)

---

### POST /api/services/deregister

Unregister a service.

**Method**: POST

**Request Body**:
```json
{
  "service_id": "my-service"
}
```

**Response (200 OK)**:
```json
{
  "ok": true
}
```

---

### GET /api/services/{service_id}

Get a single service descriptor.

**Method**: GET

**Query Parameters**: None

**Request Body**: None

**Response (200 OK)**:
```json
{
  "ok": true,
  "service": {
    "service_id": "llm-portal",
    "service_type": "LLM",
    "name": "LLM Portal",
    "version": "1.0.0",
    "host": "127.0.0.1",
    "port": 8788,
    "health_endpoint": "/api/health",
    "openapi_endpoint": "/openapi.json",
    "oauth3_scopes": [],
    "evidence_capture": false,
    "metadata": {},
    "status": "ONLINE",
    "last_health_check": "2026-02-23T10:30:00Z"
  }
}
```

**Errors**:
- **404**: Service not found
  ```json
  { "ok": false, "error": "service not found" }
  ```

---

### GET /api/services/{service_id}/health

Check the health of a specific service.

**Method**: GET

**Query Parameters**: None

**Request Body**: None

**Response (200 OK)**:
```json
{
  "ok": true,
  "health": {
    "service_id": "llm-portal",
    "status": "ONLINE",
    "latency_ms": 2.5,
    "details": {
      "uptime": "3600s",
      "version": "1.0.0"
    },
    "last_check": "2026-02-23T10:30:00Z"
  }
}
```

**Response (200) - Service Offline**:
```json
{
  "ok": true,
  "health": {
    "service_id": "llm-portal",
    "status": "OFFLINE",
    "latency_ms": 2500.0,
    "details": {
      "error": "Connection refused"
    },
    "last_check": "2026-02-23T10:30:00Z"
  }
}
```

**Statuses**: STARTING, ONLINE, OFFLINE

---

### POST /api/services/discover

Auto-discover services on known ports (8787-8792, 9222).

**Method**: POST

**Query Parameters**: None

**Request Body**: {} (empty object)

**Response (200 OK)**:
```json
{
  "ok": true,
  "discovery": {
    "discovered": [
      {
        "service_id": "llm-portal",
        "service_type": "LLM",
        "name": "LLM Portal",
        "version": "1.0.0",
        "host": "127.0.0.1",
        "port": 8788,
        "health_endpoint": "/api/health",
        "openapi_endpoint": "/openapi.json",
        "oauth3_scopes": [],
        "evidence_capture": false,
        "metadata": {},
        "status": "ONLINE",
        "last_health_check": "2026-02-23T10:30:00Z"
      }
    ],
    "failed_ports": [9222],
    "scan_duration_ms": 7500.0
  }
}
```

**Behavior**:
- Scans all KNOWN_PORTS in parallel
- Skips ports with already-registered services
- Timeout per port: 1 second
- New discoveries are auto-registered with ONLINE status

**Known Ports**:
- 8787 → admin (Stillwater Admin)
- 8788 → llm-portal (LLM Portal)
- 8789 → recipe-engine (Recipe Engine)
- 8790 → evidence-pipeline (Evidence Pipeline)
- 8791 → oauth3-authority (OAuth3 Authority)
- 8792 → cpu-service (CPU Service)
- 9222 → browser (Solace Browser)

---

## CLI API

### GET /api/cli/commands

List available allowlisted CLI commands.

**Method**: GET

**Query Parameters**: None

**Request Body**: None

**Response (200 OK)**:
```json
{
  "ok": true,
  "commands": [
    "version",
    "doctor",
    "llm-status"
  ]
}
```

---

### POST /api/cli/run

Execute a safe, allowlisted CLI command.

**Method**: POST

**Request Body**:
```json
{
  "command": "version"
}
```

**Response (200 OK)**:
```json
{
  "ok": true,
  "result": {
    "command": "version",
    "cmd": ["python", "-m", "stillwater", "--version"],
    "returncode": 0,
    "stdout": "stillwater 1.4.0\n",
    "stderr": "",
    "ok": true
  }
}
```

**Response (400) - Command Not Allowed**:
```json
{
  "ok": false,
  "error": "ValueError: command not allowed: 'rm'. Allowed: ['version', 'doctor', 'llm-status']"
}
```

**Allowlisted Commands**:
- `version` → `python -m stillwater --version`
- `doctor` → `python -m stillwater doctor`
- `llm-status` → `python -m stillwater llm status`

**Behavior**:
- Only commands in SAFE_CLI_COMMANDS are allowed
- Timeout: 30 seconds
- Working directory: REPO_ROOT
- stdout/stderr capped at 5000 characters

---

## Community API

### GET /api/community/status

Fetch community linking status and sync history.

**Method**: GET

**Query Parameters**: None

**Request Body**: None

**Response (200 OK - Not Linked)**:
```json
{
  "ok": true,
  "community": {
    "linked": false,
    "email": "",
    "api_key": "",
    "link_status": "not_linked",
    "login_link_stub": "",
    "sync_events": 0
  }
}
```

**Response (200 OK - Linked)**:
```json
{
  "ok": true,
  "community": {
    "linked": true,
    "email": "user@example.com",
    "api_key": "sw_live_mock_abc123def456...",
    "link_status": "magic_link_sent_mock",
    "login_link_stub": "https://community.stillwater.local/magic?token=xyz789",
    "sync_events": 3
  }
}
```

**Data Stored In**:
- Link info: `~/.stillwater/artifacts/admin/community_link.json`
- Sync log: `~/.stillwater/artifacts/admin/community_sync.jsonl` (one JSON per line)

---

### POST /api/community/link

Link a local stillwater instance to the community by email.

**Method**: POST

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK)**:
```json
{
  "ok": true,
  "link": {
    "email": "user@example.com",
    "status": "magic_link_sent_mock",
    "requested_at_utc": "2026-02-23T10:30:00Z",
    "login_link_stub": "https://community.stillwater.local/magic?token=abc123def456...",
    "api_key": "sw_live_mock_abc123def456...",
    "note": "Stub flow only. Real email delivery/API auth will be wired later."
  }
}
```

**Behavior**:
- Validates email format
- Generates random magic token and API key
- Stores in COMMUNITY_LINK_FILE
- **Note**: Currently a mock implementation; real email/auth flow pending

**Errors**:
- **400**: Invalid email format
  ```json
  { "ok": false, "error": "ValueError: valid email required" }
  ```

---

### POST /api/community/sync

Synchronize skills and recipes with the community hub.

**Method**: POST

**Request Body**:
```json
{
  "direction": "both"
}
```

**Response (200 OK)**:
```json
{
  "ok": true,
  "sync": {
    "timestamp_utc": "2026-02-23T10:30:00Z",
    "direction": "both",
    "uploaded": {
      "recipes": 10,
      "cli_recipes": 5,
      "root_recipes": 5,
      "skills": 20
    },
    "remote_available": [
      "recipe.counter_bypass_v2.prime-mermaid.md",
      "skill.prime-math-proofs.md",
      "persona.scope-police-plus.md"
    ],
    "status": "mock_sync_complete"
  }
}
```

**Direction Options**:
- `"up"` → Upload local skills/recipes only
- `"down"` → Download from community (stub)
- `"both"` → Bidirectional sync (stub)

**Behavior**:
- Counts files in cli/recipes, recipes/, and skills/
- Appends sync event to COMMUNITY_SYNC_LOG
- **Note**: Currently a mock implementation; real upload/download pending

---

## Error Response Format

All error responses follow this format:

```json
{
  "ok": false,
  "error": "error message describing what went wrong"
}
```

**HTTP Status Codes**:
- **200 OK**: Successful request
- **400 Bad Request**: Invalid input, validation error, permission denied
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: System error, subprocess failure

---

## Common Patterns

### Authentication
Currently no authentication. Access control is file-system based (ALLOWED_PATHS).

### Rate Limiting
No rate limiting implemented.

### Pagination
Not applicable. Endpoints return complete results.

### Caching
Responses are not cached. Each request fetches fresh data.

### Versioning
API version in response headers would be `StillwaterAdmin/0.2`.

---

## Examples

### Example 1: Edit a skill file

```bash
# Get current content
curl http://127.0.0.1:8787/api/file?path=skills/prime-safety.md

# Modify and save
curl -X POST http://127.0.0.1:8787/api/file/save \
  -H "Content-Type: application/json" \
  -d '{
    "path": "skills/prime-safety.md",
    "content": "# Updated Prime Safety\n\nNew content..."
  }'
```

### Example 2: Discover services and check health

```bash
# Discover services on known ports
curl -X POST http://127.0.0.1:8787/api/services/discover \
  -H "Content-Type: application/json" \
  -d '{}'

# Check health of LLM portal
curl http://127.0.0.1:8787/api/services/llm-portal/health
```

### Example 3: Configure LLM and pull a model

```bash
# Update LLM config
curl -X POST http://127.0.0.1:8787/api/llm/config \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "ollama",
    "ollama_url": "http://127.0.0.1:11434",
    "ollama_model": "llama2"
  }'

# Pull a model
curl -X POST http://127.0.0.1:8787/api/ollama/pull \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral",
    "ollama_url": "http://127.0.0.1:11434"
  }'
```

### Example 4: Run a CLI command

```bash
# Get available commands
curl http://127.0.0.1:8787/api/cli/commands

# Run a command
curl -X POST http://127.0.0.1:8787/api/cli/run \
  -H "Content-Type: application/json" \
  -d '{"command": "version"}'
```

### Example 5: Link and sync with community

```bash
# Link to community
curl -X POST http://127.0.0.1:8787/api/community/link \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Check status
curl http://127.0.0.1:8787/api/community/status

# Sync with community
curl -X POST http://127.0.0.1:8787/api/community/sync \
  -H "Content-Type: application/json" \
  -d '{"direction": "both"}'
```
