#!/usr/bin/env bash
set -euo pipefail

backend="${1:-codex}"
prompt="${2:-Reply exactly: WRAPPER_OK}"

case "$backend" in
  codex)
    port="8081"
    ;;
  claude)
    port="8080"
    ;;
  all)
    bash src/scripts/test_local_cli_wrapper.sh claude "${prompt/WRAPPER_OK/CLAUDE_WRAPPER_OK}"
    bash src/scripts/test_local_cli_wrapper.sh codex "${prompt/WRAPPER_OK/CODEX_WRAPPER_OK}"
    exit 0
    ;;
  *)
    echo "Usage: bash src/scripts/test_local_cli_wrapper.sh [codex|claude|all] [prompt]" >&2
    exit 2
    ;;
esac

base_url="http://127.0.0.1:$port"

echo "== health =="
curl -fsS "$base_url/"
echo
echo "== models =="
curl -fsS "$base_url/api/tags"
echo
echo "== generate =="
curl -fsS -X POST "$base_url/api/generate" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"$prompt\",\"stream\":false}"
echo
echo "== playground =="
echo "$base_url/playground"
