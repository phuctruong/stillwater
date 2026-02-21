---
skill_id: prime-llm-portal
version: 1.0.0
author: solaceagi
authority: 65537
status: STABLE
tags: [llm, portal, proxy, openai, ollama, routing, standard-library]
---

# prime-llm-portal — Stillwater LLM Portal Skill

> "Be water, my friend. Flow to any LLM." — adapted from Bruce Lee

## Purpose

The Stillwater LLM Portal is the universal LLM access layer for all Solace projects.
It provides:
1. **OpenAI-compatible proxy** on port 8788 (routes to any configured provider)
2. **Web UI** at http://localhost:8788 (configure, test, view call history)
3. **Python standard library** (`from stillwater.llm_client import llm_call`)
4. **Call logging** to `~/.stillwater/llm_calls.jsonl` (every call logged)

---

## Quick Load (orientation)

```yaml
SKILL: prime-llm-portal v1.0.0
PURPOSE: Universal LLM proxy + web UI + standard library for all Solace projects
PORTAL URL: http://localhost:8788 (start: bash admin/start-llm-portal.sh)
IMPORT: from stillwater.llm_client import llm_call, llm_chat, LLMClient
OFFLINE: llm_call("test", provider="offline")  # instant, no network
PROVIDERS: offline | claude-code (localhost:8080) | ollama (remote) | claude | openai | openrouter | gemini | togetherai
CONFIG: llm_config.yaml (repo root) — change "provider:" to switch
LOG: ~/.stillwater/llm_calls.jsonl — every call logged with ts/provider/model/latency_ms
PORTS: 8787=admin | 8788=llm-portal | 8080=claude-code-wrapper | 11434=ollama
```

---

## Service Management

```bash
# Start portal (background mode)
bash admin/start-llm-portal.sh

# Start in dev mode (auto-reload)
bash admin/start-llm-portal.sh --dev

# Stop
bash admin/stop-llm-portal.sh

# Restart
bash admin/restart-llm-portal.sh

# Status + last 20 log lines
bash admin/llm-portal-status.sh

# Health check
curl http://localhost:8788/api/health

# List all providers
curl http://localhost:8788/api/providers

# Switch provider
curl -X POST http://localhost:8788/api/providers/switch \
  -H "Content-Type: application/json" \
  --data-raw '{"provider": "ollama"}'

# OpenAI-compatible chat
curl -X POST http://localhost:8788/v1/chat/completions \
  -H "Content-Type: application/json" \
  --data-raw '{"model": "offline", "messages": [{"role": "user", "content": "hello"}]}'
```

---

## Python Standard Library

### Installation

The `stillwater` package is already installed (editable mode from repo root):
```bash
pip install -e /path/to/stillwater  # if needed
```

### Usage

```python
from stillwater.llm_client import llm_call, llm_chat, LLMClient, get_call_history

# ── One-liner (active provider from llm_config.yaml) ──────────────────────
answer = llm_call("What is 2+2?")

# ── Provider override ──────────────────────────────────────────────────────
answer = llm_call("ping", provider="offline")          # instant, no network
answer = llm_call("hi", provider="ollama")              # remote Ollama
answer = llm_call("hi", provider="claude")              # Anthropic API direct
answer = llm_call("hi", provider="claude-code")         # local Claude CLI

# ── Model override ─────────────────────────────────────────────────────────
answer = llm_call("hi", provider="ollama", model="llama3.1:8b")
answer = llm_call("hi", provider="claude", model="claude-opus-4-6")

# ── System prompt ──────────────────────────────────────────────────────────
answer = llm_call("What is your job?", system="You are a code reviewer.")

# ── Chat format (OpenAI messages) ──────────────────────────────────────────
response = llm_chat([
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "What can you do?"},
], provider="offline")

# ── Full client (test connection) ──────────────────────────────────────────
client = LLMClient(provider="ollama")
ok, latency_ms, error = client.test_connection()
if ok:
    print(f"Ollama reachable in {latency_ms}ms")
    response = client.call("Summarize this", system="Be concise")

# ── Call history ───────────────────────────────────────────────────────────
history = get_call_history(n=20)
for entry in history:
    print(f"{entry['ts']} | {entry['provider']} | {entry['latency_ms']}ms | {entry.get('error','ok')}")
```

### Error Handling

```python
from stillwater.llm_client import llm_call, LLMClient

# llm_call raises RuntimeError on failure
try:
    answer = llm_call("hello", provider="ollama")
except RuntimeError as e:
    print(f"LLM call failed: {e}")
    # Fallback to offline
    answer = llm_call("hello", provider="offline")

# test_connection() never raises — returns (ok, latency_ms, error)
client = LLMClient(provider="claude")
ok, ms, err = client.test_connection()
if not ok:
    print(f"Claude API unavailable: {err}")
```

---

## Configuring Providers

Edit `llm_config.yaml` in the repo root. Change `provider:` to switch active:

```yaml
provider: "claude-code"     # <- change this to switch active provider

claude-code:                # Local Claude CLI wrapper
  type: "http"
  url: "http://localhost:8080"
  model: "claude-haiku-4-5-20251001"
  requires_api_key: false

ollama:                     # Remote Ollama server
  type: "http"
  url: "http://192.168.68.100:11434"
  model: "llama3.1:8b"
  requires_api_key: false

claude:                     # Anthropic API direct
  type: "api"
  url: "https://api.anthropic.com/v1"
  model: "claude-haiku-4-5-20251001"
  environment_variables: ["ANTHROPIC_API_KEY"]

openai:                     # OpenAI API
  type: "api"
  url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  environment_variables: ["OPENAI_API_KEY"]

offline:                    # No network — deterministic, instant
  type: "offline"
  requires_api_key: false
```

---

## Provider Routing Logic

| Provider type | URL pattern | API called |
|---|---|---|
| `offline` | any | Returns `[offline: {prompt}]` immediately |
| `http` | `localhost` or `127.0.0.1` | `POST /api/generate` (Ollama-compat, for claude_code_wrapper) |
| `http` | other | `POST /api/chat` (Ollama chat API) |
| `api` | `api.anthropic.com` | Anthropic SDK `messages.create()` |
| `api` | other | `POST {url}/chat/completions` (OpenAI-compat) |

---

## Call Logging Schema

Every call writes one JSON line to `~/.stillwater/llm_calls.jsonl`:

```json
{
  "ts": "2026-02-21T12:00:00Z",
  "provider": "ollama",
  "model": "llama3.1:8b",
  "prompt_chars": 42,
  "response_chars": 120,
  "latency_ms": 830,
  "error": null
}
```

`error` is `null` on success, or the exception string on failure.

---

## Tests

```bash
# Run all portal tests (offline provider — no network needed)
cd /path/to/stillwater
pytest admin/test_llm_portal.py -v -p no:httpbin

# Expected: 17/17 passed
```

Test coverage:
- Health endpoint
- Provider listing (≥7 providers)
- Provider switching (offline ✓, invalid → 400)
- OpenAI-compat completions (offline provider)
- Response shape validation (id, object, choices, usage)
- Call logging (history grows after call)
- `llm_call()` / `llm_chat()` / `LLMClient` unit tests

---

## Architecture

```
Any Python code / script / notebook / batch job
  └── from stillwater.llm_client import llm_call
          └── reads llm_config.yaml
                  └── routes to provider
                          └── logs to ~/.stillwater/llm_calls.jsonl

Browser / CLI / OpenAI SDK
  └── POST http://localhost:8788/v1/chat/completions
          └── admin/llm_portal.py (FastAPI)
                  └── LLMClient (stillwater.llm_client)
                          └── same routing + logging
```

---

## Gamification: Provider Levels

| Level | Provider | XP | Skill |
|-------|----------|-----|-------|
| White | offline | 0 | Import works |
| Yellow | claude-code | 100 | Claude CLI connected |
| Orange | ollama | 300 | Local model running |
| Green | claude API | 500 | Anthropic key configured |
| Blue | multi-provider | 1000 | Routing tested |
| Black | custom provider | 3000 | New provider added to config |
