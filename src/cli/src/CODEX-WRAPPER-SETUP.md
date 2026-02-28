# Codex CLI Wrapper Setup

The Codex wrapper exposes the local `codex exec` CLI as an Ollama-compatible HTTP service.

## Start

```bash
bash src/scripts/start_local_cli_wrapper.sh codex
```

Default endpoints:

- Health: `http://127.0.0.1:8081/`
- Playground: `http://127.0.0.1:8081/playground`
- Generate: `POST http://127.0.0.1:8081/api/generate`

## Stop

```bash
bash src/scripts/stop_local_cli_wrapper.sh codex
```

## Test

```bash
bash src/scripts/test_local_cli_wrapper.sh codex "Reply exactly: CODEX_WRAPPER_OK"
```

## Notes

- The wrapper shells out to `codex exec --output-last-message ...`.
- The subprocess strips `CODEX_*` environment variables before launch to avoid session bleed-through.
- Requests are executed from `scratch/codex-wrapper/` and served back through an Ollama-style JSON contract.
