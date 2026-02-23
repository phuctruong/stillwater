# Start All Local Servers

This guide starts both Stillwater Admin and Solaceagi API for local end-to-end testing.

## Quick Start (3 minutes)

### Terminal 1: Stillwater Admin (Port 8000)

```bash
cd /home/phuc/projects/stillwater
./stillwater-server.sh start
# Opens http://localhost:8000 automatically
```

This starts the admin UI with:
- Local data access (jokes, wishes, identity, preferences, profile)
- Firebase auth (if configured)
- API key generation (proxies to cloud by default)
- File editor, LLM operations, CLI runner

### Terminal 2: Solaceagi API (Port 8080)

**Option A: With Docker (Recommended)**

```bash
cd /home/phuc/projects/solaceagi
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
# This starts solace-api on http://localhost:8000 (conflicts with stillwater!)
# So we need to override the port
```

**Option B: Without Docker (Manual Python)**

```bash
cd /home/phuc/projects/solaceagi
python -m venv venv
source venv/bin/activate
pip install -e .
SOLACEAGI_PORT=8080 python -m uvicorn solace.api.main:app --host 127.0.0.1 --port 8080 --reload
```

**Option C: Use Cloud API (No Local Server Needed)**

By default, stillwater-server proxies to `https://www.solaceagi.com`. You don't need to run the solaceagi API locally unless you're developing it.

To use a different cloud URL:

```bash
export SOLACEAGI_API_URL="http://localhost:8080"  # if running locally
export SOLACEAGI_API_URL="https://www.solaceagi.com"  # production (default)
./stillwater-server.sh start
```

---

## Testing Checklist

### 1. Local Data Access (No Auth Required)

```bash
# Terminal 3: Test data endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/data/jokes
curl http://localhost:8000/api/data/settings
curl http://localhost:8000/api/data/learned
```

Expected:
- ✅ Health returns `{"status": "ok", ...}`
- ✅ Jokes returns array of joke objects
- ✅ Settings returns `{"firestore_enabled": false, "api_key_configured": false}`
- ✅ Learned returns empty array `{"learned": []}`

### 2. Verify Data Structure

Check that data/default/ has the new structure:

```bash
ls -la data/default/
# Should show:
# - identity.json
# - preferences.md
# - profile.md
# - jokes.json
# - wishes.md
# - templates/
```

And that skills/, recipes/, combos/ are at repo root (NOT in data/):

```bash
ls -la skills/ recipes/ combos/
# Should all show their respective .md files
```

### 3. Test Local File Editing

In the admin UI at http://localhost:8000:
1. Go to **File Editor** tab
2. Click **Refresh** button
3. Select a file from the list (e.g., `jokes.json`)
4. Edit it (add a new joke)
5. Click **Save**
6. Refresh the page
7. ✅ Your changes should persist

### 4. Test Firebase Auth (If Configured)

In the admin UI at http://localhost:8000:
1. Click **"Login with Google"** button in the header
2. Complete Google auth flow
3. Header should show your email + "Get API Key" button
4. ✅ User is authenticated

### 5. Test API Key Generation

After logging in:
1. Click **"Get API Key"** button
2. Select **"Paid Account"** (MVP: instant generation)
3. Click **"Continue"**
4. View the generated key (starts with `sw_sk_`)
5. Click **"📋 Copy"** button
6. Key is copied to clipboard
7. ✅ API key generation works

### 6. Test API Endpoints with Auth

If you generated an API key or have a Firebase token:

```bash
TOKEN="your-firebase-id-token-or-api-key"

# Get current user (proxies to cloud API)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/auth/user

# List API keys (proxies to cloud API)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/keys/list
```

Expected:
- ✅ Returns user info or error (if cloud API unreachable, returns 503)
- ✅ With invalid token, returns 401 "Unauthorized"

### 7. Test Admin Panels

In the admin UI:
1. **File Editor**: Load default files, edit local files
2. **LLM Operations**: Check provider status (will show: ollama not installed, etc.)
3. **Community Hub**: (stub) Shows empty state
4. **CLI Runner**: Try running a command like "version"
5. **Operations Log**: See all activity logged in real-time

---

## Port Configuration

If ports 8000 or 8080 are already in use:

```bash
# For stillwater admin (use different port)
export STILLWATER_ADMIN_PORT=9000
./stillwater-server.sh start
# Visit http://localhost:9000

# For solaceagi API (if running locally)
SOLACEAGI_PORT=9080 python -m uvicorn solace.api.main:app --host 127.0.0.1 --port 9080 --reload

# Update proxy URL
export SOLACEAGI_API_URL="http://localhost:9080"
./stillwater-server.sh start
```

---

## Troubleshooting

### Port 8000 Already in Use

```bash
# Find what's using port 8000
lsof -i :8000
# or
netstat -tlnp | grep 8000

# Kill the process
kill -9 <PID>

# Or use a different port
export STILLWATER_ADMIN_PORT=8001
./stillwater-server.sh start
```

### "Firebase not initialized" Error

This is expected if you haven't configured Firebase. The admin UI still works for local data access.

To enable Firebase auth, set environment variables:

```bash
export FIREBASE_API_KEY="your-key"
export FIREBASE_AUTH_DOMAIN="your-project.firebaseapp.com"
export FIREBASE_PROJECT_ID="your-project"
# ... etc
./stillwater-server.sh start
```

### Cloud API Returns 503 Error

This happens if:
- Cloud API (solaceagi.com) is down
- You're offline
- SOLACEAGI_API_URL is incorrect

This is **expected and normal** for local testing. The admin UI still works for local data access. Auth endpoints will show 503 errors, which is fine.

### Admin UI Not Opening in Browser

If the browser doesn't auto-open:
```bash
# Manually open
open http://localhost:8000
# or
xdg-open http://localhost:8000
```

---

## What Works Without Cloud API

✅ Local data access (jokes, wishes, identity, preferences, profile)
✅ File editing and saving
✅ Settings configuration
✅ Operations logging
❌ Firebase authentication (requires FIREBASE_* env vars)
❌ API key generation (requires cloud API)
❌ Cloud sync (requires API key + cloud API)

---

## Next Steps After Testing

1. ✅ Verify local data structure is correct
2. ✅ Test local file editing
3. ✅ (Optional) Configure Firebase and test auth
4. ✅ (Optional) Deploy solaceagi-api to Cloud Run
5. ✅ Deploy stillwater-server to Cloud Run (or keep local)
6. ✅ Test end-to-end with cloud API

---

**Status**: Ready for local testing
**Last Updated**: 2026-02-23
