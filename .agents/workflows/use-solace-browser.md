---
description: How to interact with webpages using the compliant Solace Browser.
---

# Workflow: Compliant Web Navigation 

1. Check if the Solace Browser is running.
// turbo
`curl -fsS http://127.0.0.1:9222/api/health`

2. If not running, start the server in the background:
// turbo
`python3 ~/projects/solace-browser/solace_browser_server.py --port 9222 --head &`

3. To navigate:
`curl -X POST http://127.0.0.1:9222/api/navigate -H "Content-Type: application/json" -d '{"url": "<YOUR_URL>"}'`

4. To grab the DOM snapshot:
`curl -s http://127.0.0.1:9222/api/dom-snapshot`
