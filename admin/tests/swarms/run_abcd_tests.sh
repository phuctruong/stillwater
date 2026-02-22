#!/bin/bash
#
# ABCD Test Runner for Prime-Coder Swarm
# Usage: bash run_abcd_tests.sh [--setup] [--model MODEL] [--task TASK]
#

set -e

# Find project root by looking for cli/src/claude_code_wrapper.py
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Try different path levels to find project root
for i in 1 2 3 4 5; do
    TEST_ROOT="$SCRIPT_DIR"
    for j in $(seq 1 $i); do
        TEST_ROOT="$(cd "$TEST_ROOT/.." && pwd)"
    done
    if [ -f "$TEST_ROOT/cli/src/claude_code_wrapper.py" ]; then
        PROJECT_ROOT="$TEST_ROOT"
        break
    fi
done

if [ -z "$PROJECT_ROOT" ]; then
    echo "ERROR: Could not find project root (cli/src/claude_code_wrapper.py not found)"
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
SETUP=false
MODEL=""
TASK=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --setup)
            SETUP=true
            shift
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --task)
            TASK="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ============================================================
# Functions
# ============================================================

check_wrapper() {
    echo -e "${YELLOW}[CHECK]${NC} Looking for claude code wrapper on port 8080..."
    if curl -s http://localhost:8080/api/generate -X POST \
        -H "Content-Type: application/json" \
        -d '{"prompt": "test", "model": "haiku"}' > /dev/null 2>&1; then
        echo -e "${GREEN}[OK]${NC} Wrapper is running"
        return 0
    else
        echo -e "${RED}[ERROR]${NC} Wrapper not found on port 8080"
        return 1
    fi
}

start_wrapper() {
    echo -e "${YELLOW}[START]${NC} Starting claude code wrapper..."

    # Check if already running
    if check_wrapper; then
        echo -e "${GREEN}[OK]${NC} Wrapper already running"
        return 0
    fi

    # Kill any old instances
    pkill -f "claude_code_wrapper.py" 2>/dev/null || true
    sleep 1

    # Start wrapper in background (use absolute path)
    python3 "$PROJECT_ROOT/cli/src/claude_code_wrapper.py" --port 8080 > /tmp/wrapper.log 2>&1 &
    WRAPPER_PID=$!
    echo "Wrapper PID: $WRAPPER_PID"

    # Wait for startup
    sleep 3

    # Verify
    if check_wrapper; then
        echo -e "${GREEN}[OK]${NC} Wrapper started successfully"
        return 0
    else
        echo -e "${RED}[ERROR]${NC} Failed to start wrapper"
        echo "Check: tail -50 /tmp/wrapper.log"
        return 1
    fi
}

run_all_tests() {
    echo -e "${YELLOW}[TEST]${NC} Running all ABCD tests (all models, all tasks)..."

    pytest "$PROJECT_ROOT/admin/tests/swarms/test_abcd_coding.py::TestABCDCoding" -v -s \
        --tb=short 2>&1 | tee /tmp/abcd_test_run.log

    echo ""
    echo -e "${YELLOW}[SUMMARY]${NC} Generating comparison report..."
    pytest "$PROJECT_ROOT/admin/tests/swarms/test_abcd_coding.py::TestABCDSummary" -v -s
}

run_model_tests() {
    echo -e "${YELLOW}[TEST]${NC} Running ABCD tests for model: $MODEL..."

    pytest "$PROJECT_ROOT/admin/tests/swarms/test_abcd_coding.py::TestABCDCoding" -k "$MODEL" \
        -v -s --tb=short 2>&1 | tee /tmp/abcd_test_${MODEL}.log
}

run_task_tests() {
    echo -e "${YELLOW}[TEST]${NC} Running ABCD tests for task: $TASK..."

    pytest "$PROJECT_ROOT/admin/tests/swarms/test_abcd_coding.py::TestABCDCoding" -k "$TASK" \
        -v -s --tb=short 2>&1 | tee /tmp/abcd_test_${TASK}.log
}

show_results() {
    echo ""
    echo -e "${GREEN}[RESULTS]${NC} Test results saved to:"
    ls -la "$SCRIPT_DIR/results/" 2>/dev/null || echo "  (no results yet)"

    echo ""
    echo -e "${GREEN}[SUMMARY]${NC} Comparison report:"
    cat "$SCRIPT_DIR/results/ABCD_SUMMARY.json" 2>/dev/null || echo "  (run tests first)"
}

show_usage() {
    cat << 'EOF'
ABCD Test Runner for Prime-Coder Swarm

Usage:
    bash run_abcd_tests.sh [OPTIONS]

Options:
    --setup         Start wrapper and run all tests
    --model MODEL   Run tests for specific model (haiku, sonnet, opus)
    --task TASK     Run tests for specific task (task_1_simple_sum, etc.)

Examples:
    # Run all tests (with wrapper startup)
    bash run_abcd_tests.sh --setup

    # Run all tests (wrapper already running)
    bash run_abcd_tests.sh

    # Run only sonnet tests
    bash run_abcd_tests.sh --model sonnet

    # Run only task 1
    bash run_abcd_tests.sh --task task_1

    # Run only task 2 on opus
    bash run_abcd_tests.sh --task task_2 --model opus

Tasks:
    - task_1_simple_sum    (⭐ Trivial)
    - task_2_palindrome    (⭐⭐ Easy)
    - task_3_fibonacci     (⭐⭐⭐ Medium)
    - task_4_dict_merge    (⭐⭐⭐⭐ Hard)

Models:
    - haiku        (fastest baseline)
    - sonnet       (mid-tier)
    - opus         (largest/best)

Results:
    Results saved to: admin/tests/swarms/results/{model}/{task}_{model}.json
    Summary report:  admin/tests/swarms/results/ABCD_SUMMARY.json

EOF
}

# ============================================================
# Main
# ============================================================

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║     ABCD Testing Framework - Prime-Coder Swarm       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Show usage if no args
if [ "$SETUP" = false ] && [ -z "$MODEL" ] && [ -z "$TASK" ]; then
    show_usage
    exit 0
fi

# Setup: start wrapper
if [ "$SETUP" = true ]; then
    echo -e "${YELLOW}[SETUP]${NC} Starting ABCD test suite..."
    start_wrapper || exit 1
fi

# Check wrapper is running
if ! check_wrapper; then
    echo ""
    echo -e "${YELLOW}[TIP]${NC} Start wrapper with:"
    echo "  python3 cli/src/claude_code_wrapper.py --port 8080"
    echo ""
    echo "Or use: bash run_abcd_tests.sh --setup"
    exit 1
fi

# Run tests based on filters
if [ -z "$MODEL" ] && [ -z "$TASK" ]; then
    # No filters: run all
    run_all_tests
elif [ -n "$MODEL" ] && [ -z "$TASK" ]; then
    # Model filter only
    run_model_tests
elif [ -z "$MODEL" ] && [ -n "$TASK" ]; then
    # Task filter only
    run_task_tests
else
    # Both filters
    echo -e "${YELLOW}[TEST]${NC} Running ABCD tests for task: $TASK, model: $MODEL..."
    pytest "$PROJECT_ROOT/admin/tests/swarms/test_abcd_coding.py::TestABCDCoding" \
        -k "$TASK and $MODEL" -v -s --tb=short
fi

# Show results
show_results

echo ""
echo -e "${GREEN}[DONE]${NC} Test run complete"
echo ""
