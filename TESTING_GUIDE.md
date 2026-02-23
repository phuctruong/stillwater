# Testing Guide — Stillwater Admin & Orchestration

**Server Status**: ✅ RUNNING on http://127.0.0.1:8000

---

## Part 1: Test Local Data Access (5 minutes)

### Test 1.1: Health Check

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "firestore_enabled": false
}
```

### Test 1.2: Get Identity

```bash
curl http://127.0.0.1:8000/api/data/identity
```

Expected: Returns `identity.json` with your name, email, timezone, etc.

### Test 1.3: Get Preferences

```bash
curl http://127.0.0.1:8000/api/data/preferences
```

Expected: Returns your theme, sync settings, learning settings.

### Test 1.4: Get Orchestration Workflow

```bash
curl http://127.0.0.1:8000/api/data/orchestration
```

Expected: Returns the complete triple-twin orchestration configuration with all three phases.

### Test 1.5: Get Jokes

```bash
curl http://127.0.0.1:8000/api/data/jokes
```

Expected: JSON array of 15 default jokes (with id, joke, tags, confidence, etc.)

### Test 1.6: Get Wishes

```bash
curl http://127.0.0.1:8000/api/data/wishes
```

Expected: Returns your personal goals/task categories in Mermaid format.

---

## Part 2: Test Data Directory Structure (5 minutes)

### Verify data/default/ is Correct

```bash
ls -la data/default/
```

Should show:
```
identity.json       ← Your identity settings
preferences.md      ← Your preferences
profile.md          ← Your profile/bio
orchestration.md    ← Triple-twin workflow
jokes.json          ← Example jokes
wishes.md           ← Your goals
templates/          ← Templates for new files
```

**✅ Correct**: All user-customizable data here

### Verify Skills/Recipes/Combos are Global

```bash
ls -la skills/ recipes/ combos/ | head -20
```

Should show:
- `skills/` — prime-safety, prime-coder, phuc-forecast, etc. (30+ skill definitions)
- `recipes/` — bugfix, qa-audit, ci-triage, etc. (20+ recipes)
- `combos/` — plan, run-test, conflict-to-resolution, etc. (15+ combos)

**✅ Correct**: Framework files stay outside data/

### Verify data/custom/ is Ready

```bash
ls -la data/custom/
```

Should show:
```
.gitkeep            ← Placeholder file (in git)
```

**✅ Correct**: Empty, ready for user customizations

---

## Part 3: Test Admin UI in Browser (10 minutes)

### Step 1: Open Admin UI

Open your browser to: **http://127.0.0.1:8000**

You should see:
- Header: "Stillwater Admin Dojo"
- "Login with Google" button (top right)
- File Editor tab (active)
- LLM Operations tab
- Community Hub tab
- CLI Runner tab
- Operations Log (bottom)

### Step 2: Test File Editor (Local Data)

1. Click **"Refresh"** button
2. Select **"Skills"** tab (or "Recipes" or "Papers")
3. Click on a file in the left panel (e.g., `prime-safety.md`)
4. You should see the file content loaded in the editor
5. Make a small edit (add a comment at the bottom)
6. Click **"Save"** button
7. Refresh the page
8. **✅ Your changes should persist**

### Step 3: Test Local Data via File Editor

1. Click **"Recipes"** tab
2. Expand the file list
3. Look for `recipe.bugfix.md`
4. Click to open it
5. You should see the bugfix recipe workflow
6. **✅ File loads successfully**

### Step 4: Check Operations Log

Look at the **Operations Log** panel at the bottom. You should see entries like:
```
[2026-02-23T14:30:00] Catalog refreshed.
[2026-02-23T14:30:15] Opened recipe.bugfix.md
[2026-02-23T14:30:22] Saved recipe.bugfix.md
```

**✅ All actions are logged**

---

## Part 4: Test Customization Pattern (5 minutes)

### Create Custom Identity

1. Open admin UI at http://127.0.0.1:8000
2. Go to **File Editor** → **Recipes** tab (or find where data/ files are listed)
3. Create a new file: `data/custom/identity.json`

Actually, easier via command line:

```bash
# Copy default identity to custom
cp data/default/identity.json data/custom/identity.json

# Edit it
nano data/custom/identity.json
# Change "name": "Your Name" to "name": "Phuc Vu"
# Change "email": "you@example.com" to your email
```

Then:

```bash
# Test that custom overrides default
curl http://127.0.0.1:8000/api/data/identity | jq .name
```

Expected: Should now return "Phuc Vu" (your custom value)

**✅ Custom/ correctly overrides default/**

### Verify Custom File is Gitignored

```bash
git status data/custom/identity.json
```

Expected: Should NOT appear in git status (it's gitignored)

**✅ Custom files are never accidentally committed**

---

## Part 5: Test Orchestration Workflow (10 minutes)

### View the Orchestration Diagram

Open your browser and visit:
```
http://127.0.0.1:8000
```

Then in admin UI, find and open:
- File: `data/default/orchestration.md`
- You should see:
  - Overview diagram (triple-twin)
  - Phase 1 state machine (Small Talk Twin)
  - Phase 2 state machine (Intent Twin)
  - Phase 3 state machine (Execution Twin)
  - End-to-end flow diagram
  - Webservices flow diagram

**✅ All diagrams render correctly**

### Create Custom Orchestration Phase

```bash
# Create Phase 1 customization
cat > data/custom/orchestration-phase1.md << 'EOF'
---
phase: 1
name: "Small Talk Twin"
enabled: true
validator: "haiku"
threshold: 0.75
---

# Phase 1: Custom Settings

## Emotional Actions to Learn
- celebrate_success
- encourage_struggle
- acknowledge_loss

## Custom Confidence Gate
0.75 (stricter than default 0.70)
EOF
```

Test:
```bash
curl http://127.0.0.1:8000/api/data/orchestration-phase1 2>/dev/null || echo "Phase1 customization file created in data/custom/"
```

**✅ Users can now customize orchestration per phase**

---

## Part 6: Test Cloud-Ready Endpoints (5 minutes)

### Test Health Endpoint (No Auth)

```bash
curl -w "\nStatus: %{http_code}\n" http://127.0.0.1:8000/health
```

Expected: `200 OK`

### Test Config Endpoint (Firebase Config)

```bash
curl -s http://127.0.0.1:8000/config | python -m json.tool
```

Expected: Returns Firebase config (projectId, apiKey, etc.)

### Test Auth Endpoint (Requires Token)

```bash
curl -w "\nStatus: %{http_code}\n" \
  -H "Authorization: Bearer invalid_token" \
  http://127.0.0.1:8000/api/auth/user
```

Expected: `401` or `503` (depending on cloud API availability)

---

## Part 7: Verify Orchestration Architecture (5 minutes)

### Check Phase 1 Configuration

Look at `data/default/orchestration.md`, Phase 1 section:

```yaml
phase: 1
name: "Small Talk Twin"
enabled: true
validator: "haiku"
threshold: 0.70
learnings_file: "learned_smalltalk.jsonl"
```

**✅ Phase 1 correctly configured**

### Check Phase 2 Configuration

Phase 2 section should show:

```yaml
phase: 2
name: "Intent Twin"
threshold: 0.80
learnings_file: "learned_wishes.jsonl"
```

**✅ Phase 2 stricter (0.80 > 0.70)**

### Check Phase 3 Configuration

Phase 3 section should show:

```yaml
phase: 3
name: "Execution Twin"
threshold: 0.90
learnings_file: "learned_combos.jsonl"
```

**✅ Phase 3 strictest (0.90 > 0.80 > 0.70)**

---

## Part 8: Test Cost Breakdown (5 minutes)

From `orchestration.md`, you can see the cost per session:

| Service | Requests | Cost |
|---------|----------|------|
| Haiku Validators | 3 | ~$0.001 |
| Firestore (read) | 1 | ~$0.0001 |
| Firestore (sync) | 1 | ~$0.0001 |
| **TOTAL** | ~12-20 | ~$0.0011 |

This is documented and customizable. Users can:

```yaml
# Skip validators when CPU confident
skip_validator_if_cpu_confidence: 0.70
# Result: 50% fewer calls, 50% cost reduction
```

**✅ Costs are transparent and customizable**

---

## Part 9: Full End-to-End Test (Optional, 15 minutes)

### Scenario: User Adds Custom Joke

1. **Open admin UI** → http://127.0.0.1:8000
2. **File Editor** → Find jokes (or use API)
3. **Create** `data/custom/jokes.json` with your own jokes:

```bash
curl -X POST http://127.0.0.1:8000/api/data/jokes \
  -H "Content-Type: application/json" \
  -d '{"id": "custom_001", "joke": "Stillwater flows, but never drowns", "category": "zen"}'
```

4. **Verify custom override**:

```bash
curl http://127.0.0.1:8000/api/data/jokes | jq '.jokes[] | select(.id == "custom_001")'
```

Expected: Returns your custom joke

**✅ End-to-end customization works**

---

## Checklist: All Tests Passing

- [ ] ✅ Health check returns 200
- [ ] ✅ All data/ files load correctly (identity, preferences, profile, orchestration, jokes, wishes)
- [ ] ✅ Admin UI opens in browser at http://127.0.0.1:8000
- [ ] ✅ File editor loads and saves files
- [ ] ✅ data/default/ has user-customizable data
- [ ] ✅ data/custom/ is empty and ready for overrides
- [ ] ✅ skills/, recipes/, combos/ are global (not in data/)
- [ ] ✅ Orchestration.md shows triple-twin with diagrams
- [ ] ✅ Phase 1 threshold is 0.70 (Small Talk)
- [ ] ✅ Phase 2 threshold is 0.80 (Intent)
- [ ] ✅ Phase 3 threshold is 0.90 (Execution)
- [ ] ✅ Custom files in data/custom/ are gitignored
- [ ] ✅ Cost breakdown is documented
- [ ] ✅ Can create custom orchestration-phaseX.md files

---

## Server Management

### Check if Server is Running

```bash
curl http://127.0.0.1:8000/health
```

### Stop the Server

```bash
pkill -f "uvicorn admin.backend.app"
# or
./stillwater-server.sh stop
```

### View Logs

```bash
tail -f ~/.stillwater/logs/admin-server.log
```

### Restart Server

```bash
./stillwater-server.sh restart
```

---

## What's Ready

✅ **Local Data Access** — Works without internet
✅ **User Customization** — Clear data/default → data/custom override pattern
✅ **Orchestration Workflow** — Triple-twin architecture fully documented
✅ **Admin UI** — File editor, settings, logging
✅ **Firebase Auth** — Ready to configure (currently optional)
✅ **Cloud Sync** — Ready for Firestore integration (currently optional)

---

## Next Steps

1. ✅ **Test all endpoints** — Use this guide to verify everything works
2. 🎯 **Customize identity** — Edit `data/custom/identity.json` with your info
3. 🎯 **Customize orchestration** — Create `data/custom/orchestration-phase*.md` files
4. 🎯 **Deploy solaceagi-api** — Deploy to Cloud Run when ready
5. 🎯 **Test end-to-end** — With Firebase auth and Firestore sync

---

**Status**: ✅ READY FOR TESTING
**Last Updated**: 2026-02-23
**Server**: Running on http://127.0.0.1:8000
