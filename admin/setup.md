# Stillwater Admin — Setup Guide

## System Requirements

- **Python 3.9+** (stdlib only; no mandatory pip dependencies)
- A terminal and a web browser
- Git (to clone the repo)

No virtual environment required for basic operation. The admin server uses Python's built-in `http.server` and `json` modules.

---

## Quick Start

Three commands. That's it.

```bash
# 1. Absorb — clone the repo
git clone https://github.com/phuctruong/stillwater.git
cd stillwater

# 2. Discard nothing — run the admin server (no install needed)
python admin/server.py

# 3. Add what you want — open the admin UI
# Browser opens automatically, or navigate to:
# http://127.0.0.1:8787
```

Bruce Lee principle in action:

- **Absorb** what is useful: clone and run.
- **Discard** what is not: nothing is required by default.
- **Add** what is essentially your own: install extras only for the features you need.
- **Verify**: open the browser, see the admin UI. If it loads, you're done.

---

## Optional: Install requests (for Ollama model listing)

The `requests` library unlocks live Ollama model listing and community sync features.

```bash
pip install -r admin/requirements.txt
```

Without it, Ollama model listing falls back to a cached/stub response and community sync is disabled. All other features work with stdlib alone.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `STILLWATER_ADMIN_HOST` | `127.0.0.1` | Host to bind the admin server |
| `STILLWATER_ADMIN_PORT` | `8787` | Port to bind the admin server |

Example — run on a different port:

```bash
STILLWATER_ADMIN_PORT=9000 python admin/server.py
```

Example — use the start script (handles PYTHONPATH and browser open):

```bash
# From repo root:
bash admin/start-admin.sh

# Or from inside admin/:
cd admin && bash start-admin.sh
```

---

## LLM Portal (port 8788)

The **Stillwater LLM Portal** is a separate service: an OpenAI-compatible proxy + web UI for configuring and testing any LLM provider.

```bash
# Start LLM Portal
bash admin/start-llm-portal.sh

# Open in browser
open http://localhost:8788

# Dev mode (auto-reload)
bash admin/start-llm-portal.sh --dev

# Stop
bash admin/stop-llm-portal.sh

# Status
bash admin/llm-portal-status.sh
```

**Requirements:** `pip install "fastapi[standard]" uvicorn httpx`

### LLM Portal endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Web UI (dark theme, provider cards, chat test, call log) |
| `GET /api/health` | Health check + active provider |
| `GET /api/providers` | All configured providers + reachability |
| `POST /api/providers/switch` | Switch active provider (session-local) |
| `GET /api/history` | Call history from `~/.stillwater/llm_calls.jsonl` |
| `POST /v1/chat/completions` | OpenAI-compatible proxy |
| `GET /v1/models` | Model listing |

### Universal LLM Client

All Python code across all projects can use the standard library:

```python
from stillwater.llm_client import llm_call, llm_chat, LLMClient

# One-liner (uses active provider from llm_config.yaml)
answer = llm_call("What is 2+2?")

# With provider override
answer = llm_call("ping", provider="offline")   # instant, no network
answer = llm_call("explain this", provider="ollama", model="llama3.1:8b")

# Chat format (OpenAI messages)
response = llm_chat([
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"},
])

# Call history
from stillwater.llm_client import get_call_history
history = get_call_history(n=20)  # reads ~/.stillwater/llm_calls.jsonl
```

### Configure LLM Provider

Edit `llm_config.yaml` in the repo root:
```yaml
provider: "claude-code"   # currently active

claude-code:              # local Claude CLI wrapper (port 8080)
  url: "http://localhost:8080"
ollama:                   # remote Ollama
  url: "http://192.168.68.100:11434"
claude:                   # Anthropic API direct
  url: "https://api.anthropic.com/v1"
```

---

## Security Notes

- **Localhost only by default.** The server binds to `127.0.0.1`. Do not expose it to a network interface without understanding the risks.
- **Edit restrictions.** File writes are restricted to curated Stillwater config and content paths (`skills/`, `cli/`, `llm_config.yaml`, etc.). Arbitrary filesystem writes are not permitted.
- **No credential storage.** The admin UI does not store API keys, passwords, or tokens in any persistent file. Community magic-link stubs are local only.
- **Sudo actions.** The "Install Ollama" button runs `sudo` commands on your machine. Only use this on trusted, local machines.

---

## Troubleshooting

### Port already in use

```
OSError: [Errno 98] Address already in use
```

Find and stop the process using the port:

```bash
lsof -i :8787
kill <PID>
```

Or run on a different port:

```bash
STILLWATER_ADMIN_PORT=8788 python admin/server.py
```

### Python not found / wrong version

```bash
python3 --version   # should be 3.9+
python3 admin/server.py
```

If your system defaults to Python 2, use `python3` explicitly.

### Module not found errors (ImportError)

The admin server imports from `cli/src` for some features. Set PYTHONPATH from the repo root:

```bash
PYTHONPATH=cli/src python admin/server.py
```

Or use the start script which sets this automatically:

```bash
bash admin/start-admin.sh
```

### Browser does not open automatically

Navigate manually to: `http://127.0.0.1:8787`

The auto-open uses `xdg-open` (Linux) or `open` (macOS). If neither is available, the server still runs — just open the URL yourself.
