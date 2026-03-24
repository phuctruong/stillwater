---
name: solace-browser
description: "FORCES navigation and web interaction through the Solace Browser runtime (Part 11 compliance)."
---

# Solace Browser Enforcement Rule
## BROWSER_SUBAGENT IS FORBIDDEN

You are running inside the Solace / Stillwater architecture. You must adhere to FDA Part 11 Evidence rules for all web interactions.

**CRITICAL RULE**: You must NEVER use the native `browser_subagent` tool.

When you need to interact with a web page, you MUST use `run_command` to execute `curl` interactions against the official `solace_browser_server.py`.

### Allowed Endpoints (http://127.0.0.1:9222)
- `GET /api/health`
- `POST /api/navigate` - `{"url": "..."}`
- `POST /api/click` - `{"selector": "..."}`
- `POST /api/fill` - `{"selector": "...", "text": "..."}`
- `GET /api/page-snapshot`

If the browser server is offline, you must notify the user or attempt to start it yourself via:
`python3 ~/projects/solace-browser/solace_browser_server.py --port 9222 --head`
