# Claude Code Wrapper Setup Guide

**Auth: 65537** | **Status: Experimental**

---

## Quick Start

```bash
# Terminal 1: Start wrapper (once, keeps running)
cd /path/to/stillwater
python3 src/claude_code_wrapper.py --port 8080 &

# Terminal 2: Run notebook (in Claude Code)
# Then open and run: HOW-TO-CRUSH-SWE-BENCHMARK.ipynb
```

Tip: if you're already inside the repo, you can also do:
```bash
cd "$(git rev-parse --show-toplevel)"
```

---

## What is the Wrapper?

The Claude Code wrapper is an **independent HTTP server** that:
- Runs on `http://localhost:8080`
- Provides an Ollama-compatible API (`/api/generate` endpoint)
- Internally calls the Claude CLI for LLM requests
- Supports all models: Haiku, Sonnet, Opus

---

## Why Do We Need It?

### The Problem
The Claude CLI (`claude -p "prompt"`) fails inside Claude Code with:
```
Error: Cannot be launched inside another Claude Code session
```

This is because the CLI checks the process tree (PPID) to prevent nested sessions.

### The Solution
```
┌─ Claude Code Session (inside)
│  └─ Notebook
│     └─ HTTP call to localhost:8080
│
└─ Wrapper (independent process, outside)
   └─ Calls Claude CLI (clean process tree)
      └─ No nested session error!
```

The wrapper runs as a **separate process**, so when it calls the CLI, there's no nested session conflict.

---

## Which Wrapper File to Use?

### ✅ Correct: `src/claude_code_wrapper.py`
- **Uses:** Claude CLI internally
- **Supports:** All models (Haiku, Sonnet, Opus)
- **Size:** 17 KB
- **Status:** Production ready

```bash
python3 src/claude_code_wrapper.py --port 8080 &
```

### ❌ Don't Use: `src/claude_code_wrapper_ollama.py`
- **Uses:** Ollama directly (not CLI)
- **Supports:** Only Ollama models
- **Limitation:** No Haiku support
- **Status:** Alternative only

---

## Setup Steps

### Step 1: Start the Wrapper

In a **separate terminal** (Terminal 1):

```bash
cd /path/to/stillwater
python3 src/claude_code_wrapper.py --port 8080 &
```

**Expected output:**
```
================================================================================
CLAUDE CODE SERVER (Ollama-compatible)
================================================================================

✅ Server running at: http://127.0.0.1:8080
   CLI available: Yes
   CLI path: /path/to/claude

📝 Test with curl:
   curl http://127.0.0.1:8080/

⌨️  Press Ctrl+C to stop

================================================================================
```

### Step 2: Verify It's Running

In a **different terminal** (Terminal 2):

```bash
curl http://localhost:8080/
```

**Expected response:**
```json
{
  "status": "ok",
  "message": "Claude Code Server (Ollama-compatible)",
  "cli_available": true,
  "cli_path": "/path/to/claude"
}
```

### Step 3: Run the Notebook

In **Claude Code**, open and run:
```
HOW-TO-CRUSH-SWE-BENCHMARK.ipynb
```

The notebook will automatically detect the wrapper and use it for all LLM calls.

---

## Troubleshooting

### Q: "Connection refused" error

**Problem:** Wrapper is not running

**Solution:**
```bash
# Start wrapper in separate terminal
python3 src/claude_code_wrapper.py --port 8080 &
```

### Q: "Port 8080 already in use"

**Problem:** Another process is using port 8080

**Solution:**
```bash
# Find process using port 8080
lsof -i :8080

# Kill it
kill -9 <PID>

# Then start wrapper again
python3 src/claude_code_wrapper.py --port 8080 &
```

### Q: "CLI not available" message

**Problem:** Claude CLI not installed or not in PATH

**Solution:**
```bash
# Check if Claude is installed
which claude

# If not, install:
pip install claude-code

# Or ensure it's in PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Q: "Nested session error" still happens

**Problem:** Using wrong wrapper file

**Solution:**
```bash
# Make sure you're using the CORRECT wrapper:
✅ python3 src/claude_code_wrapper.py --port 8080

# NOT:
❌ python3 src/claude_code_wrapper_ollama.py
```

---

## How the Notebook Uses the Wrapper

### Architecture
```
Notebook (Cell 0-10)
  ↓
Cell 6: swe_solver_real.py subprocess
  ↓
Solver internally imports claude_code_wrapper
  ↓
Wrapper.query() method
  ↓
HTTP POST to http://localhost:8080/api/generate
  ↓
Wrapper (independent process)
  ↓
Claude CLI subprocess (clean process tree)
  ↓
Haiku LLM
  ↓
Response back to notebook
```

### What the Notebook Does

1. **Cell 0:** Validates wrapper is running at `http://localhost:8080`
2. **Cell 1-4:** Loads real SWE-bench instances
3. **Cell 5-6:** Initializes solver
4. **Cell 7-8:** Calls solver on each instance
   - Solver → uses wrapper → returns patch
5. **Cell 9-10:** Displays results and QA validation

---

## Performance Tips

### Wrapper Keeps Running
The wrapper keeps running in the background and can handle multiple requests:

```bash
# Start wrapper once
python3 src/claude_code_wrapper.py --port 8080 &

# Use it from notebook
# Can process 100+ instances without restarting wrapper
```

### Check Wrapper Health Anytime

```bash
# In notebook or terminal
curl http://localhost:8080/
```

### Stop the Wrapper

```bash
# When done (optional)
pkill -f "claude_code_wrapper.py"

# Or: kill <PID>
```

---

## Environment Variables

The wrapper respects these environment variables:

```bash
# Set LLM model (optional)
export CLAUDE_CODE_MODEL="claude-haiku-4-5-20251001"

# Set port (optional, default 8080)
export CLAUDE_CODE_PORT="8080"

# Enable debug logging
export DEBUG="true"
```

---

## Summary

| Item | Details |
|------|---------|
| **Correct Wrapper** | `src/claude_code_wrapper.py` |
| **Wrong Wrapper** | `src/claude_code_wrapper_ollama.py` |
| **Start Command** | `python3 src/claude_code_wrapper.py --port 8080 &` |
| **Endpoint** | `http://localhost:8080` |
| **API** | POST `/api/generate` (Ollama-compatible) |
| **Status** | Experimental |

---

**Key Points:**
- ✅ Start wrapper BEFORE running notebook
- ✅ Use `src/claude_code_wrapper.py` (not ollama version)
- ✅ Wrapper runs as independent process (avoids nested session errors)
- ✅ Notebook calls wrapper via HTTP (no subprocess issues)
- ✅ Supports all models: Haiku, Sonnet, Opus
