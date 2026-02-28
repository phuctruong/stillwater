#!/usr/bin/env bash
set -euo pipefail

backend="${1:-codex}"
requested_port="${2:-}"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
runtime_dir="$repo_root/scratch/wrapper-services"
mkdir -p "$runtime_dir"

is_port_free() {
  local port="$1"
  python3 -c 'import socket, sys; s = socket.socket(); rc = s.connect_ex(("127.0.0.1", int(sys.argv[1]))); s.close(); raise SystemExit(0 if rc != 0 else 1)' "$port"
}

start_wrapper() {
  local target_backend="$1"
  local target_port="$2"
  shift 2
  local env_args=("$@")
  local target_module=""

  case "$target_backend" in
    codex)
      target_module="$repo_root/src/cli/src/codex_cli_wrapper.py"
      ;;
    claude)
      target_module="$repo_root/src/cli/src/claude_code_wrapper.py"
      ;;
    *)
      echo "Unknown backend: $target_backend" >&2
      exit 2
      ;;
  esac

  local target_pid_file="$runtime_dir/${target_backend}-wrapper.pid"
  local target_log_file="$runtime_dir/${target_backend}-wrapper.log"

  if [[ -f "$target_pid_file" ]]; then
    local existing_pid
    existing_pid="$(cat "$target_pid_file" 2>/dev/null || true)"
    if [[ -n "$existing_pid" ]] && kill -0 "$existing_pid" 2>/dev/null; then
      echo "$target_backend wrapper already running with pid $existing_pid"
      echo "Log: $target_log_file"
      return 0
    fi
    rm -f "$target_pid_file"
  fi

  nohup env "${env_args[@]}" python3 "$target_module" --host 127.0.0.1 --port "$target_port" >"$target_log_file" 2>&1 &
  local wrapper_pid="$!"
  echo "$wrapper_pid" > "$target_pid_file"

  sleep 1
  if ! kill -0 "$wrapper_pid" 2>/dev/null; then
    echo "Failed to start $target_backend wrapper. Log follows:" >&2
    cat "$target_log_file" >&2
    exit 1
  fi

  echo "Started $target_backend wrapper"
  echo "PID: $wrapper_pid"
  echo "Health: http://127.0.0.1:$target_port/"
  echo "Playground: http://127.0.0.1:$target_port/playground"
  echo "Log: $target_log_file"
}

case "$backend" in
  codex)
    default_port="8081"
    ;;
  claude)
    default_port="8080"
    ;;
  all)
    claude_port="${requested_port:-8080}"
    codex_port="8081"
    if ! is_port_free "$claude_port"; then
      claude_port="8082"
    fi
    if ! is_port_free "$codex_port"; then
      codex_port="8083"
    fi
    start_wrapper claude "$claude_port" "CODEX_WRAPPER_URL=http://127.0.0.1:$codex_port"
    start_wrapper codex "$codex_port" "CLAUDE_CODE_URL=http://127.0.0.1:$claude_port"
    echo "Both wrappers are available on the same localhost machine:"
    echo "  Claude: http://127.0.0.1:$claude_port/playground"
    echo "  Codex:  http://127.0.0.1:$codex_port/playground"
    exit 0
    ;;
  *)
    echo "Usage: bash src/scripts/start_local_cli_wrapper.sh [codex|claude|all] [port]" >&2
    exit 2
    ;;
esac

port="${requested_port:-$default_port}"
start_wrapper "$backend" "$port"
