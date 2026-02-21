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
