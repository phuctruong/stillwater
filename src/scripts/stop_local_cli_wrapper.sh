#!/usr/bin/env bash
set -euo pipefail

backend="${1:-codex}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
runtime_dir="$repo_root/scratch/wrapper-services"

if [[ "$backend" == "all" ]]; then
  bash "$repo_root/src/scripts/stop_local_cli_wrapper.sh" claude
  bash "$repo_root/src/scripts/stop_local_cli_wrapper.sh" codex
  exit 0
fi

pid_file="$runtime_dir/${backend}-wrapper.pid"

if [[ ! -f "$pid_file" ]]; then
  echo "No pid file found for $backend wrapper"
  exit 0
fi

pid="$(cat "$pid_file" 2>/dev/null || true)"
if [[ -z "$pid" ]]; then
  echo "Pid file for $backend wrapper was empty"
  rm -f "$pid_file"
  exit 0
fi

if kill -0 "$pid" 2>/dev/null; then
  kill "$pid"
  echo "Stopped $backend wrapper pid $pid"
else
  echo "$backend wrapper pid $pid was not running"
fi

rm -f "$pid_file"
