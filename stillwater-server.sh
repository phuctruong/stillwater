#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
HOST="${STILLWATER_HOST:-127.0.0.1}"
START_TIMEOUT="${STILLWATER_START_TIMEOUT:-45}"
PID_DIR="${HOME}/.stillwater/pids"
LOG_DIR="${HOME}/.stillwater/logs"

SERVICES=(
  "admin"
  "cpu-service"
  "evidence-pipeline"
  "oauth3-service"
  "llm-portal"
  "recipe-engine"
  "orchestration-service"
  "swarm-service"
  "tunnel-service"
  "cloud-bridge"
)

service_port() {
  case "$1" in
    admin) echo 8787 ;;
    llm-portal) echo 8788 ;;
    recipe-engine) echo 8789 ;;
    evidence-pipeline) echo 8790 ;;
    oauth3-service) echo 8791 ;;
    cpu-service) echo 8792 ;;
    tunnel-service) echo 8793 ;;
    cloud-bridge) echo 8794 ;;
    orchestration-service) echo 8795 ;;
    swarm-service) echo 8796 ;;
    *) return 1 ;;
  esac
}

pid_file() {
  echo "${PID_DIR}/$1.pid"
}

log_file() {
  echo "${LOG_DIR}/$1.log"
}

is_pid_running() {
  local pid="$1"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

service_health_url() {
  local port
  port="$(service_port "$1")"
  echo "http://${HOST}:${port}/api/health"
}

health_ok() {
  curl -fsS --max-time 2 "$(service_health_url "$1")" >/dev/null 2>&1
}

ensure_dirs() {
  mkdir -p "$PID_DIR" "$LOG_DIR"
}

start_service_process() {
  local service="$1"
  local port
  port="$(service_port "$service")"
  local py_path="${REPO_ROOT}/src/cli/src:${REPO_ROOT}/src:${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
  local lf
  lf="$(log_file "$service")"

  case "$service" in
    admin)
      nohup env PYTHONPATH="$py_path" "$PYTHON" "${REPO_ROOT}/admin/server.py" --host "$HOST" --port "$port" >>"$lf" 2>&1 &
      ;;
    cpu-service)
      nohup env PYTHONPATH="$py_path" "$PYTHON" -m uvicorn admin.services.cpu_service:app --host "$HOST" --port "$port" --log-level warning >>"$lf" 2>&1 &
      ;;
    evidence-pipeline)
      nohup env PYTHONPATH="$py_path" "$PYTHON" -m uvicorn admin.services.evidence_pipeline:app --host "$HOST" --port "$port" --log-level warning >>"$lf" 2>&1 &
      ;;
    oauth3-service)
      nohup env PYTHONPATH="$py_path" "$PYTHON" -m uvicorn admin.services.oauth3_service:app --host "$HOST" --port "$port" --log-level warning >>"$lf" 2>&1 &
      ;;
    llm-portal)
      nohup env PYTHONPATH="$py_path" "$PYTHON" -m uvicorn admin.llm_portal:app --host "$HOST" --port "$port" --log-level warning >>"$lf" 2>&1 &
      ;;
    recipe-engine)
      nohup env PYTHONPATH="$py_path" "$PYTHON" -m uvicorn admin.services.recipe_engine:app --host "$HOST" --port "$port" --log-level warning >>"$lf" 2>&1 &
      ;;
    orchestration-service)
      nohup env PYTHONPATH="$py_path" "$PYTHON" -m uvicorn admin.services.orchestration_service:app --host "$HOST" --port "$port" --log-level warning >>"$lf" 2>&1 &
      ;;
    swarm-service)
      nohup env PYTHONPATH="$py_path" "$PYTHON" -m uvicorn admin.services.swarm_service:app --host "$HOST" --port "$port" --log-level warning >>"$lf" 2>&1 &
      ;;
    tunnel-service)
      nohup env PYTHONPATH="$py_path" "$PYTHON" -m uvicorn admin.services.tunnel_service:app --host "$HOST" --port "$port" --log-level warning >>"$lf" 2>&1 &
      ;;
    cloud-bridge)
      nohup env PYTHONPATH="$py_path" "$PYTHON" -m uvicorn admin.services.cloud_bridge:app --host "$HOST" --port "$port" --log-level warning >>"$lf" 2>&1 &
      ;;
    *)
      echo "Unknown service: $service" >&2
      return 1
      ;;
  esac

  local pid=$!
  echo "$pid" >"$(pid_file "$service")"
}

wait_for_service() {
  local service="$1"
  local waited=0
  while (( waited < START_TIMEOUT )); do
    if health_ok "$service"; then
      return 0
    fi
    sleep 1
    waited=$((waited + 1))
  done
  return 1
}

start_service() {
  local service="$1"
  local pf
  pf="$(pid_file "$service")"

  if health_ok "$service"; then
    printf "%-22s %-6s %s\n" "$service" "$(service_port "$service")" "external-running"
    return 0
  fi

  if [[ -f "$pf" ]]; then
    local existing
    existing="$(cat "$pf" 2>/dev/null || true)"
    if is_pid_running "$existing" && health_ok "$service"; then
      printf "%-22s %-6s %s\n" "$service" "$(service_port "$service")" "already-running"
      return 0
    fi
    rm -f "$pf"
  fi

  start_service_process "$service"
  if wait_for_service "$service"; then
    printf "%-22s %-6s %s\n" "$service" "$(service_port "$service")" "started"
    return 0
  fi

  printf "%-22s %-6s %s\n" "$service" "$(service_port "$service")" "failed"
  tail -n 40 "$(log_file "$service")" || true
  return 1
}

stop_service() {
  local service="$1"
  local pf
  pf="$(pid_file "$service")"

  if [[ ! -f "$pf" ]]; then
    printf "%-22s %-6s %s\n" "$service" "$(service_port "$service")" "not-running"
    return 0
  fi

  local pid
  pid="$(cat "$pf" 2>/dev/null || true)"
  if ! is_pid_running "$pid"; then
    rm -f "$pf"
    printf "%-22s %-6s %s\n" "$service" "$(service_port "$service")" "stale-pid"
    return 0
  fi

  kill -TERM "$pid" 2>/dev/null || true
  local waited=0
  while is_pid_running "$pid" && (( waited < 10 )); do
    sleep 1
    waited=$((waited + 1))
  done
  if is_pid_running "$pid"; then
    kill -9 "$pid" 2>/dev/null || true
  fi
  rm -f "$pf"
  printf "%-22s %-6s %s\n" "$service" "$(service_port "$service")" "stopped"
}

show_status() {
  printf "%-22s %-6s %-10s %-8s %s\n" "SERVICE" "PORT" "PID" "HEALTH" "STATE"
  for service in "${SERVICES[@]}"; do
    local pf
    pf="$(pid_file "$service")"
    local pid="-"
    local state="stopped"
    local health="down"

    if [[ -f "$pf" ]]; then
      pid="$(cat "$pf" 2>/dev/null || true)"
      if is_pid_running "$pid"; then
        state="running"
      else
        state="stale"
      fi
    fi

    if health_ok "$service"; then
      health="ok"
      if [[ "$state" == "stopped" ]]; then
        state="external"
      fi
    fi

    printf "%-22s %-6s %-10s %-8s %s\n" "$service" "$(service_port "$service")" "$pid" "$health" "$state"
  done
}

start_all() {
  ensure_dirs
  printf "%-22s %-6s %s\n" "SERVICE" "PORT" "RESULT"
  for service in "${SERVICES[@]}"; do
    if ! start_service "$service"; then
      echo "ABORT: ${service} failed to start" >&2
      stop_all
      return 1
    fi
  done
  echo ""
  show_status
  echo ""
  echo "Admin UI: http://${HOST}:8787"
}

stop_all() {
  ensure_dirs
  printf "%-22s %-6s %s\n" "SERVICE" "PORT" "RESULT"
  local idx
  for (( idx=${#SERVICES[@]}-1; idx>=0; idx-- )); do
    stop_service "${SERVICES[$idx]}"
  done
}

usage() {
  cat <<USAGE
Usage:
  ./stillwater-server.sh              # start all services
  ./stillwater-server.sh start
  ./stillwater-server.sh --status
  ./stillwater-server.sh --stop
  ./stillwater-server.sh restart
USAGE
}

main() {
  local cmd="${1:-start}"
  case "$cmd" in
    start)
      start_all
      ;;
    --status|status)
      show_status
      ;;
    --stop|stop)
      stop_all
      ;;
    restart)
      stop_all
      start_all
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      usage
      return 1
      ;;
  esac
}

main "$@"
