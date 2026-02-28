# Stillwater Source Diagrams

This directory is a source-level entry point for current diagram/setup notes.

Canonical architecture diagrams still live under:

- `data/default/diagrams/`

Wrapper setup for local development:

- `src/diagrams/local-cli-wrapper-setup.md`
- `data/default/diagrams/stillwater/62-local-cli-wrapper-bridge.md`

Current local wrapper ports:

- Claude wrapper: `127.0.0.1:8082` on this machine because `8080` is already occupied
- Codex wrapper: `127.0.0.1:8081`

Launcher commands:

```bash
bash src/scripts/start_local_cli_wrapper.sh all
bash src/scripts/stop_local_cli_wrapper.sh all
```
