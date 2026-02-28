# Local CLI Wrapper Setup

## Purpose

Run local Claude Code and Codex CLI backends as HTTP webservices so Stillwater, Solace Browser, and SolaceAGI can use a stable localhost contract.

## Live Ports

On this machine:

- Codex wrapper: `http://127.0.0.1:8081`
- Claude wrapper: `http://127.0.0.1:8082`

`8082` is used for Claude because `127.0.0.1:8080` is already bound by another local service.

## Playground URLs

- Codex: `http://127.0.0.1:8081/playground`
- Claude: `http://127.0.0.1:8082/playground`

Each playground links to the other wrapper.

## Webservice Contract

Both wrappers expose:

- `GET /` — health JSON
- `GET /api/tags` — model list
- `GET /playground` — browser test page
- `POST /api/generate` — Ollama-compatible generate API

## Startup

Start both wrappers on the same localhost machine:

```bash
bash src/scripts/start_local_cli_wrapper.sh all
```

Stop both:

```bash
bash src/scripts/stop_local_cli_wrapper.sh all
```

Smoke test both:

```bash
bash src/scripts/test_local_cli_wrapper.sh all
```

## Browser / AGI Usage

Point local consumers at the wrapper URLs:

- Codex-oriented local backend: `http://127.0.0.1:8081`
- Claude-oriented local backend: `http://127.0.0.1:8082`

This keeps Browser/AGI on a webservice boundary instead of a direct subprocess boundary.

## Related Files

- `src/cli/src/codex_cli_wrapper.py`
- `src/cli/src/claude_code_wrapper.py`
- `src/scripts/start_local_cli_wrapper.sh`
- `src/scripts/stop_local_cli_wrapper.sh`
- `src/scripts/test_local_cli_wrapper.sh`
- `data/default/diagrams/stillwater/62-local-cli-wrapper-bridge.md`
