# Stillwater Admin UI — Local Testing Guide

## Overview

The Stillwater Admin UI is a FastAPI backend that serves:
1. **Local data access** — no auth required (edit jokes, wishes, combos locally)
2. **Cloud sync** — auth required (connect to solaceagi.com, get API keys)
3. **LLM operations** — Ollama/provider configuration
4. **Static web UI** — HTML + JavaScript with Firebase auth

## Quick Start (Local Dev)

### Prerequisites

- Python 3.10+
- FastAPI + uvicorn installed (in `admin/backend/requirements.txt`)
- Firebase account (for testing auth; optional for local data access)

### Step 1: Install Dependencies

```bash
pip install -r admin/backend/requirements.txt
```

### Step 2: Start the Admin Backend

```bash
./stillwater-server.sh start
```

This command:
- Starts the FastAPI server on `http://127.0.0.1:8000`
- Opens your browser automatically to the admin UI
- Creates a PID file at `~/.stillwater/admin.pid`
- Logs to `~/.stillwater/logs/admin-YYYYMMDD.log`

### Step 3: Access the Admin UI

Open `http://localhost:8000` in your browser. You should see:

1. **Header**: "Stillwater Admin Dojo" with "Login with Google" button
2. **File Editor**: Edit skills, recipes, papers
3. **LLM Operations**: Configure Ollama/providers
4. **Community Hub**: (stub) Prepare for skill marketplace
5. **CLI Runner**: Execute allowlisted CLI commands
6. **Operations Log**: Real-time activity log

### Step 4: Test Local Data Access

Without logging in, you can:

1. Go to **File Editor** tab
2. Click "Refresh" button
3. View and edit files in `data/default/` and `data/custom/`
4. Add jokes, wishes, or combos
5. Changes are saved locally to `data/custom/`

**Example**: Add a joke via API:
```bash
curl -X POST http://localhost:8000/api/data/jokes \
  -H "Content-Type: application/json" \
  -d '{"id": "test_001", "joke": "Test joke", "category": "test"}'
```

## Firebase Authentication (Optional for MVP)

### Prerequisites

You need a Firebase project configured. For MVP testing, we assume paid accounts.

### Environment Variables

```bash
# Optional: override default Firebase config
export FIREBASE_API_KEY="your-api-key"
export FIREBASE_AUTH_DOMAIN="your-project.firebaseapp.com"
export FIREBASE_PROJECT_ID="your-project"
export FIREBASE_STORAGE_BUCKET="your-project.appspot.com"
export FIREBASE_MESSAGING_SENDER_ID="your-sender-id"
export FIREBASE_APP_ID="your-app-id"

# Cloud API URL (for proxy calls)
export SOLACEAGI_API_URL="http://localhost:8080"  # local dev
# or
export SOLACEAGI_API_URL="https://www.solaceagi.com"  # production
```

### Test Login Flow

1. Click **"Login with Google"** in the header
2. Choose between Google and GitHub login options
3. After successful login, header shows your email + "Get API Key" button
4. Click **"Get API Key"** to start the verification flow

### Test API Key Generation (MVP Mode)

For MVP, users don't need actual verification:

1. After login, click **"Get API Key"**
2. Select **"Paid Account (Recommended)"**
3. Click **"Continue"**
4. The system generates an API key immediately
5. Copy the key and save it to your local `data/settings.md`:

```yaml
---
api_key: sw_sk_your_generated_key_here
firestore_enabled: true
sync_interval_seconds: 300
---
```

### Test Verification Stubs (Optional)

The UI has stubs for social media and follow verification:

1. Click **"Get API Key"**
2. Select **"Social Post"** option
3. Enter a public URL where you posted something
4. Click **"Verify Post"** (returns pending_review for MVP)

Or:

1. Select **"Social Follow"** option
2. Click **"Verify"** (returns pending_review for MVP)

## Testing API Endpoints

### Local Data (No Auth)

```bash
# Get jokes
curl http://localhost:8000/api/data/jokes

# Get settings
curl http://localhost:8000/api/data/settings

# Get learned entries
curl http://localhost:8000/api/data/learned

# Add a joke
curl -X POST http://localhost:8000/api/data/jokes \
  -H "Content-Type: application/json" \
  -d '{"id": "test_1", "joke": "test", "category": "test"}'
```

### Cloud APIs (Auth Required)

These endpoints require a valid Firebase ID token as Bearer token:

```bash
# Get current user
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/auth/user

# Generate API key (proxies to cloud)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/keys/generate

# List API keys (proxies to cloud)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/keys/list

# Verify social post
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://twitter.com/..."}' \
  http://localhost:8000/api/verify/social
```

## Server Management

```bash
# Start server
./stillwater-server.sh start

# Stop server
./stillwater-server.sh stop

# Restart server
./stillwater-server.sh restart

# Check status
./stillwater-server.sh status

# View logs (today)
./stillwater-server.sh log

# Tail logs in real-time
./stillwater-server.sh tail
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
export STILLWATER_ADMIN_PORT=8001
./stillwater-server.sh start
# Visit http://localhost:8001
```

### Browser Won't Open

If the browser doesn't auto-open on Linux:

```bash
# Manually open in your browser
open http://localhost:8000
# or
xdg-open http://localhost:8000
```

### Firebase Config Not Found

The backend will try to load Firebase config from environment variables. If not set, it uses defaults. For a real Firebase project:

1. Create a Firebase project at https://firebase.google.com
2. Enable Google & GitHub authentication
3. Copy your config to environment variables
4. Restart the server

### Cloud API Errors (503)

If you see 503 errors:

- Cloud API is unreachable (check `SOLACEAGI_API_URL`)
- For local-only testing, skip auth endpoints
- Local data endpoints work without the cloud API

## Architecture

```
admin/backend/app.py              ← FastAPI server
  ├── GET /health                 ← Server health check
  ├── GET /config                 ← Firebase config for frontend
  ├── GET /api/data/*             ← Local data access (no auth)
  ├── POST /api/data/*            ← Local data write (no auth)
  ├── GET|POST /api/auth/*        ← Firebase auth proxy
  ├── GET|POST /api/verify/*      ← Verification proxy
  ├── GET|POST /api/keys/*        ← API key management proxy
  └── GET /                       ← Serve index.html

admin/static/
  ├── index.html                  ← Main UI
  ├── app.js                      ← Firebase auth + API logic
  ├── app.css                     ← Styling
  └── *.svg                       ← Background/decorative assets

stillwater-server.sh              ← Server lifecycle management
```

## Next Steps

1. **Test Local Data**: Add/edit jokes, wishes via the UI
2. **Test Firebase Auth**: Login with Google/GitHub (if Firebase configured)
3. **Test API Keys**: Generate a key and save to `data/settings.md`
4. **Test Sync**: Run `stillwater sync pull` to download cloud data
5. **Deploy**: When ready, push solaceagi API to Cloud Run

## Testing Checklist

- [ ] Server starts with `./stillwater-server.sh start`
- [ ] Admin UI loads at http://localhost:8000
- [ ] Can edit local files without auth
- [ ] Firebase login works (if configured)
- [ ] Can generate API keys after login
- [ ] API key displays once, can copy to clipboard
- [ ] Settings load from `data/settings.md`
- [ ] Data persists after page refresh
- [ ] Server stops cleanly with `./stillwater-server.sh stop`

---

**Status**: ✅ Frontend UI complete with Firebase auth + API key generation
**Next**: Deploy solaceagi-api to Cloud Run, then test end-to-end
