# Stillwater Admin Dojo

Web UI for configuring Stillwater without editing files by hand.

## Features

### 1. Browse and edit

- `skills/` — individual skill files
- `cli/recipes/` and `cli/extensions/recipes/` — command recipes
- `cli/extensions/personas/` — persona definitions
- `cli/identity/` — identity config
- `cli/settings/` — settings files
- `llm_config.yaml` — LLM provider and model config

### 2. Catalog groups

Browse and manage Stillwater content by category:

- **Skills** — reusable skill files from `skills/`
- **Swarms** — multi-agent orchestration configs
- **Recipes** — CLI command recipes and extensions
- **Papers** — research papers and writing from `papers/`
- **Community Docs** — synced community content and shared configs

### 3. CLI Runner

Run `stillwater` commands from the web UI without leaving the browser.

- Allowlisted commands only (safe subset of the CLI)
- Output displayed inline in the UI
- Useful for: running skills, testing recipes, checking diagnostics

### 4. LLM / Ollama control

- Provider, URL, and model edits
- Live Ollama probe + model list (requires `requests`; see [setup.md](setup.md))
- Install Ollama button (sudo required)
- Pull local models

### 5. Community hub

- Magic-link + API key stub (email input)
- Recipe/skill sync mock with audit log

---

## Run

From repo root:

```bash
# Recommended: use the start script (sets PYTHONPATH, opens browser)
bash admin/start-admin.sh

# Or directly:
python admin/server.py --host 127.0.0.1 --port 8787 --open
```

From inside `admin/`:

```bash
cd admin && python server.py
# or
cd admin && bash start-admin.sh
```

For full setup instructions (environment variables, optional dependencies, troubleshooting):

```bash
cat admin/setup.md
# or see: admin/setup.md
```

---

## Security Notes

- Editing is restricted to curated Stillwater config/content paths.
- Install action executes `sudo` commands on your machine; use only on trusted hosts.
- Community link/sync is currently a local stub stored in `artifacts/admin/`.
- Server binds to `127.0.0.1` by default (localhost only).

---

## Bruce Lee Principle

> "Absorb what is useful. Discard what is not. Add what is essentially your own."

- **Absorb**: clone and run — no install required.
- **Discard**: nothing mandatory; skip pip entirely for basic use.
- **Add**: `pip install -r admin/requirements.txt` for Ollama model listing and community sync.
- **Verify**: open browser at `http://127.0.0.1:8787`, see the dojo.
