# Webservice-First Architecture

**Status**: Ready for Production (Rung 641)
**Date**: 2026-02-23
**Architecture**: Webservice-first, OAuth3-ready, Software 5.0 ready

---

## Overview

Both **Stillwater** and **Solace Browser** follow a **webservice-first architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│              Webservice Layer (REST API)                    │
│  Port 8000 (Stillwater) / Port 9223 (Solace Browser)      │
├─────────────────────────────────────────────────────────────┤
│ • Data access (file-based + cloud-optional)                │
│ • OAuth3 authentication + token management                  │
│ • Session persistence (cookies + localStorage)              │
│ • Evidence bundling + audit trails                          │
│ • Recipe execution + verification ladder                    │
└─────────────────────────────────────────────────────────────┘
          ↑
          │ REST API calls
          │
┌─────────────────────────────────────────────────────────────┐
│          Control Surfaces (Clients)                          │
├─────────────────────────────────────────────────────────────┤
│ • CLI (stillwater-server.sh / solace-browser-server.sh)    │
│ • Python API (HttpX clients)                                │
│ • Browser UI (localhost:8000 / localhost:9223)              │
│ • Cloud tunnel (solaceagi.com → local server)               │
│ • Phuc Swarms (AI agents calling via REST)                  │
└─────────────────────────────────────────────────────────────┘
```

**Key Principle**: The webservice is the primary interface. Everything else (UI, CLI, agents) communicates via REST API.

---

## The Two Webservices

### 1. Stillwater Admin Backend

**Purpose**: Data access + verification framework
**Port**: 8000
**Tech**: FastAPI (async Python)
**Data**: data/default/, data/custom/
**Management**: `./stillwater-server.sh`

**What it serves**:
- User data (identity, preferences, profile, orchestration, facts, jokes, wishes)
- File editing capabilities (read/write/list files)
- API key generation + management
- Firebase authentication (optional)
- Cloud sync (optional Firestore)

**Key principle**: Local-first, cloud-optional. Everything works offline.

### 2. Solace Browser Webservice

**Purpose**: Browser automation + OAuth3 control
**Port**: 9223
**Tech**: FastAPI + Playwright (async Python)
**Session**: artifacts/solace_session.json (persistent)
**Management**: `./solace-browser-server.sh`

**What it serves**:
- Browser navigation (GET /navigate)
- Page interaction (click, fill, keyboard)
- Snapshots (ARIA tree + DOM + console)
- Screenshots (visual capture)
- OAuth3 session management (6+ providers)
- Recipe execution framework

**Key principle**: Persistent session. Login once, script forever.

---

## Management Scripts

Both scripts follow the same pattern for consistency.

### Stillwater Server Management

```bash
cd /home/phuc/projects/stillwater

# Start server (opens admin UI at localhost:8000)
./stillwater-server.sh start

# Check status
./stillwater-server.sh status

# Monitor logs
./stillwater-server.sh tail

# Run health checks
./stillwater-server.sh test

# Restart (useful for clean session)
./stillwater-server.sh restart

# Stop server
./stillwater-server.sh stop
```

### Solace Browser Server Management

```bash
cd /home/phuc/projects/solace-browser

# Start in HEADED mode (shows browser window)
./solace-browser-server.sh start

# Start in HEADLESS mode (for Cloud Run)
./solace-browser-server.sh start --headless

# Or via environment variable
SOLACE_HEADLESS=true ./solace-browser-server.sh start

# Check status
./solace-browser-server.sh status

# View session info
./solace-browser-server.sh session

# Monitor logs
./solace-browser-server.sh tail

# Run health checks
./solace-browser-server.sh test

# Stop server
./solace-browser-server.sh stop
```

---

## Software 5.0: Webservice-First Development

### Why Webservice-First?

1. **CLI Independence** → Script doesn't care about implementation (Python/Node/Go)
2. **Multi-Client** → Same server serves web UI, CLI, agents, cloud
3. **Evidence Trail** → All API calls logged for audit trails (Part 11)
4. **Test-Friendly** → Can test API without launching full app
5. **Cloud-Ready** → Deploy same service headless to Cloud Run
6. **Deterministic** → Same API request → same response (reproducible)

### Example: Three Ways to Use Stillwater

**Way 1: Web Browser**
```
Open browser → http://127.0.0.1:8000
Click buttons in admin UI
```

**Way 2: CLI (curl)**
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/data/facts | jq
```

**Way 3: Python Script**
```python
import httpx

async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
    resp = await client.get("/api/data/facts")
    print(resp.json())
```

**Way 4: Phuc Swarm (AI Agent)**
```python
# Agent code (inside phuc-swarm)
await http_client.get("/api/data/orchestration")
# Reads orchestration workflow, validates phase thresholds
```

All four ways work identically. The webservice is the source of truth.

---

## API Design Principles

### 1. REST Convention
```
GET  /api/data/facts              → Retrieve facts
POST /api/data/jokes              → Add joke
GET  /api/oauth3/providers        → List OAuth3 providers
POST /api/oauth3/login            → Start OAuth3 flow
```

### 2. Deterministic Responses
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2026-02-23T15:30:00Z",
  "request_id": "req_abc123"
}
```

### 3. Error Convention
```json
{
  "success": false,
  "error": "Invalid OAuth3 provider",
  "code": "INVALID_PROVIDER",
  "request_id": "req_abc123"
}
```

### 4. Idempotent Operations
```bash
# Same request always produces same result
curl -X POST /api/oauth3/login -d '{"provider": "gmail"}'
curl -X POST /api/oauth3/login -d '{"provider": "gmail"}'  # Same result
```

---

## Environment Variables

### Stillwater

```bash
STILLWATER_ADMIN_PORT=8000        # Which port to listen on
STILLWATER_ADMIN_HOST=127.0.0.1   # Which host to bind to
```

### Solace Browser

```bash
SOLACE_PORT=9223                    # API port
SOLACE_HOST=127.0.0.1              # API host
SOLACE_HEADLESS=false              # Show browser window (false) or run headless (true)
SOLACE_SESSION_FILE=artifacts/solace_session.json  # Where to persist session
SOLACE_USER_DATA_DIR=~/.solace-browser/profile     # Chrome profile directory
SOLACE_AUTOSAVE_SECONDS=60         # Auto-save session interval (seconds)
```

---

## Session Persistence

### Stillwater

**Data Storage**:
- `data/default/` → Git-tracked, user-customizable templates
- `data/custom/` → Gitignored overrides (per-user customization)
- `data/settings.md` → API key + sync settings

**No session state** (stateless design)
- Each API call reads from disk
- No in-memory state to lose
- Cloud-friendly (scales horizontally)

### Solace Browser

**Session Storage**:
- `artifacts/solace_session.json` → Cookies + localStorage (encrypted)
- Persists across browser restarts
- Can be uploaded to solaceagi.com for cloud sync

**Persistent Browser Context**:
```python
# Browser runs headless in background
# Playwright maintains persistent_context
# All cookies/localStorage preserved
await context.storage_state(path="artifacts/solace_session.json")
```

**Multi-Device Sync**:
```
Local Session             Cloud Session
    ↓                         ↓
solace_session.json ←→ solaceagi.com (AES-256-GCM)
                        ↓
                    Cloud Browser (24/7 headless)
```

---

## Verification Ladder Integration

Both webservices implement the **rung system**:

```
RUNG 641   → Local correctness
            Examples:
            - GET /api/data/facts returns valid JSON ✓
            - OAuth3 login flow completes ✓
            - Session persists after restart ✓

RUNG 274177 → Stability (edge cases, replay)
            Examples:
            - Same login flow succeeds 100x ✓
            - Token refresh handles expiry ✓
            - Network errors handled gracefully ✓

RUNG 65537  → Production (security, audit, load)
            Examples:
            - API key hash never logged ✓
            - Audit trail tamper-evident (hash-chained) ✓
            - Handles 1000 concurrent requests ✓
```

---

## Cloud Deployment

Both services deploy to **Cloud Run** (same container image):

```bash
# Build Docker image
docker build -t stillwater-admin .

# Deploy to Cloud Run (auto-scales)
gcloud run deploy stillwater-admin \
  --image=stillwater-admin \
  --platform=managed \
  --region=us-central1 \
  --memory=1Gi \
  --timeout=300
```

**For Solace Browser (headless)**:
```bash
SOLACE_HEADLESS=true gcloud run deploy solace-browser \
  --image=solace-browser \
  --platform=managed \
  --region=us-central1 \
  --memory=2Gi \
  --timeout=600
```

---

## Checklist: Running Both Services

### Local Development (Headed Mode)

```bash
# Terminal 1: Start Stillwater
cd ~/projects/stillwater
./stillwater-server.sh start
# Opens http://127.0.0.1:8000

# Terminal 2: Start Solace Browser
cd ~/projects/solace-browser
./solace-browser-server.sh start
# Opens http://127.0.0.1:9223
# Shows real browser window

# Terminal 3: Test APIs
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:9223/health

# Terminal 4: Run Phuc Swarms
# Agents can now call both webservices
```

### Cloud Deployment (Headless Mode)

```bash
# Deploy Stillwater to Cloud Run
gcloud run deploy stillwater \
  --source=./projects/stillwater \
  --region=us-central1

# Deploy Solace Browser (headless)
gcloud run deploy solace-browser \
  --source=./projects/solace-browser \
  --region=us-central1 \
  --set-env-vars SOLACE_HEADLESS=true

# Test from CLI
curl https://stillwater-abc123.run.app/health
curl https://solace-browser-xyz789.run.app/health
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start Stillwater | `cd stillwater && ./stillwater-server.sh start` |
| Start Solace Browser (headed) | `cd solace-browser && ./solace-browser-server.sh start` |
| Start Solace Browser (headless) | `SOLACE_HEADLESS=true ./solace-browser-server.sh start` |
| Check Stillwater | `curl http://127.0.0.1:8000/health` |
| Check Solace Browser | `curl http://127.0.0.1:9223/health` |
| View Stillwater logs | `cd stillwater && ./stillwater-server.sh tail` |
| View Solace Browser logs | `cd solace-browser && ./solace-browser-server.sh tail` |
| Restart Stillwater | `cd stillwater && ./stillwater-server.sh restart` |
| Restart Solace Browser | `cd solace-browser && ./solace-browser-server.sh restart` |
| Test both servers | See "Testing" section below |

---

## Testing

### Test Stillwater

```bash
cd ~/projects/stillwater
./stillwater-server.sh test

# Expected output:
# ✓ Health check passed
# ✓ Config endpoint working
# ✓ /api/data/facts working
# ✓ /api/data/jokes working
# ... etc
```

### Test Solace Browser

```bash
cd ~/projects/solace-browser
./solace-browser-server.sh test

# Expected output:
# ✓ Health check passed
# ✓ Status endpoint working
```

### Test Full Integration

```bash
# 1. Start both servers
cd ~/projects/stillwater && ./stillwater-server.sh start &
cd ~/projects/solace-browser && ./solace-browser-server.sh start &

# 2. Run pytest test suite
pytest tests/test_stillwater_qa.py -v

# 3. Check results
# ✓ 13/13 tests passing
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
STILLWATER_ADMIN_PORT=8001 ./stillwater-server.sh start
```

### Server Won't Start

```bash
# Check logs
./stillwater-server.sh log

# Try starting manually to see error
python -m uvicorn admin.backend.app:app --host 127.0.0.1 --port 8000

# Check Python path
echo $PYTHONPATH
```

### Browser Won't Connect

```bash
# Verify server is running
./solace-browser-server.sh status

# Check health endpoint
curl http://127.0.0.1:9223/health

# View browser logs
./solace-browser-server.sh tail
```

---

## Architecture Decisions (Why This Way?)

### Why REST API?
- **Cloud-ready** → Same service runs headless on Cloud Run
- **Testable** → Can test without launching full UI
- **Language-neutral** → Works with any programming language
- **Auditable** → All requests logged for compliance

### Why Local-First (Stillwater)?
- **Privacy** → Data never leaves user's machine
- **Speed** → No network latency
- **Offline** → Works without internet
- **Git-friendly** → Easy version control

### Why Persistent Sessions (Solace Browser)?
- **Efficiency** → Login once, script many times
- **Reliability** → Session survives browser restarts
- **Scale** → Can run 100 scripts against 1 session
- **Cost** → Fewer logins = fewer CAPTCHA challenges

### Why Webservice-First?
- **Separation of concerns** → Server logic separate from UI
- **Multiple clients** → Web, CLI, agents all use same API
- **Evidence trails** → All API calls logged (Part 11)
- **Reproducibility** → Same request = same result (deterministic)

---

## Next Steps

1. ✅ Both webservices have management scripts
2. ✅ Both follow same pattern (start|stop|restart|status|tail|log|test)
3. 🎯 Add OAuth3 homepage to Solace Browser (see docs/ARCHITECTURE_OAUTH3_HOMEPAGE.md)
4. 🎯 Integrate recipe execution framework
5. 🎯 Deploy to solaceagi.com (Cloud Run)
6. 🎯 Enable Firestore sync (optional cloud backup)

---

## Key Files

| File | Purpose |
|------|---------|
| `stillwater-server.sh` | Manage Stillwater webservice |
| `solace-browser-server.sh` | Manage Solace Browser webservice |
| `admin/backend/app.py` | Stillwater FastAPI app |
| `solace_browser_server.py` | Solace Browser FastAPI app |
| `NORTHSTAR.md` | Project vision + metrics |
| `WEBSERVICE_ARCHITECTURE.md` | This file |
| `docs/ARCHITECTURE_OAUTH3_HOMEPAGE.md` | OAuth3 API design |

---

**Status**: ✅ READY FOR PRODUCTION (Rung 641)
**Last Updated**: 2026-02-23
**Next**: Deploy to Cloud Run and enable multi-OAuth3 homepage
