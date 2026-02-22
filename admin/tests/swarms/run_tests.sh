#!/bin/bash
# Swarms Unit Test Runner
# Auth: 65537 | Version: 1.0.0
#
# Usage:
#   ./run_tests.sh                              # Run all tests
#   ./run_tests.sh metadata                     # Run metadata tests only
#   ./run_tests.sh invocation                   # Run invocation tests only
#   ./run_tests.sh coder                        # Run tests for coder swarm
#   ./run_tests.sh -v                           # Verbose output
#   ./run_tests.sh --setup                      # Start wrapper + portal

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
WRAPPER_PORT=8080
PORTAL_PORT=8788

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
  echo -e "${GREEN}=== $1 ===${NC}"
}

print_error() {
  echo -e "${RED}ERROR: $1${NC}" >&2
}

print_warning() {
  echo -e "${YELLOW}WARNING: $1${NC}"
}

# Check if services are running
check_services() {
  if ! lsof -i :$WRAPPER_PORT >/dev/null 2>&1; then
    print_error "Claude Code wrapper not running on port $WRAPPER_PORT"
    echo "Start it with: python3 cli/src/claude_code_wrapper.py --port $WRAPPER_PORT"
    return 1
  fi

  if ! lsof -i :$PORTAL_PORT >/dev/null 2>&1; then
    print_error "LLM Portal not running on port $PORTAL_PORT"
    echo "Start it with: python3 admin/llm_portal_swarms.py"
    return 1
  fi

  return 0
}

# Start services
start_services() {
  print_header "Starting Services"

  if lsof -i :$WRAPPER_PORT >/dev/null 2>&1; then
    echo "Wrapper already running on port $WRAPPER_PORT"
  else
    echo "Starting Claude Code wrapper on port $WRAPPER_PORT..."
    cd "$PROJECT_ROOT"
    python3 cli/src/claude_code_wrapper.py --port $WRAPPER_PORT > /tmp/wrapper.log 2>&1 &
    sleep 2
  fi

  if lsof -i :$PORTAL_PORT >/dev/null 2>&1; then
    echo "Portal already running on port $PORTAL_PORT"
  else
    echo "Starting LLM Portal on port $PORTAL_PORT..."
    cd "$PROJECT_ROOT"
    python3 admin/llm_portal_swarms.py > /tmp/portal.log 2>&1 &
    sleep 2
  fi

  if check_services; then
    echo -e "${GREEN}✓ Services running${NC}"
  else
    print_error "Failed to start services"
    return 1
  fi
}

# Run tests
run_tests() {
  local filter="$1"

  cd "$PROJECT_ROOT"

  # Build pytest command
  local cmd="pytest admin/tests/swarms/test_swarms.py -v --tb=short"

  if [ -n "$filter" ]; then
    cmd="$cmd -k '$filter'"
  fi

  echo -e "${GREEN}Running: $cmd${NC}\n"
  eval "$cmd"
}

# Main
main() {
  local setup=0
  local filter=""
  local verbose=0

  while [[ $# -gt 0 ]]; do
    case $1 in
      --setup)
        setup=1
        shift
        ;;
      -v)
        verbose=1
        shift
        ;;
      *)
        filter="$1"
        shift
        ;;
    esac
  done

  # Start services if needed
  if [ $setup -eq 1 ]; then
    start_services || exit 1
  else
    if ! check_services; then
      print_error "Services not running. Use --setup to start them."
      exit 1
    fi
  fi

  print_header "Running Swarms Tests"
  echo "Filter: ${filter:-'(all tests)'}"
  echo ""

  run_tests "$filter"
}

main "$@"
