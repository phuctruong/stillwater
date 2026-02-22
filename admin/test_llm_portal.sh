#!/bin/bash
################################################################################
# test_llm_portal.sh — Test LLM Portal v3 Swarm Execution
#
# Simple script to test Portal v3 swarm + prompt combinations
#
# Usage:
#   ./admin/test_llm_portal.sh [OPTIONS]
#
# Required:
#   --swarm SWARM_TYPE        Swarm to execute (e.g., coder, mathematician)
#   --prompt PROMPT_TEXT      Task/prompt for the swarm
#
# Optional:
#   --model MODEL             LLM model: haiku, sonnet, opus (default: haiku)
#   --max-tokens INT          Maximum tokens (default: 2048)
#   --temp FLOAT              Temperature (default: 0.0)
#   --endpoint URL            Portal endpoint (default: http://localhost:8788)
#   --help                    Show this help message
#
# Examples:
#   # Simple test with defaults (haiku model)
#   ./admin/test_llm_portal.sh --swarm coder --prompt "Write a sum function"
#
#   # Test with sonnet model
#   ./admin/test_llm_portal.sh \
#     --swarm coder \
#     --prompt "Implement LRU Cache with O(1) operations" \
#     --model sonnet
#
#   # Test mathematician swarm
#   ./admin/test_llm_portal.sh \
#     --swarm mathematician \
#     --prompt "Prove that sqrt(2) is irrational" \
#     --model opus
#
#   # Custom settings
#   ./admin/test_llm_portal.sh \
#     --swarm coder \
#     --prompt "Write a binary search implementation" \
#     --model sonnet \
#     --max-tokens 1024 \
#     --temp 0.7
#
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
ENDPOINT="http://localhost:8788"
MODEL="haiku"
MAX_TOKENS="2048"
TEMPERATURE="0.0"
SWARM=""
PROMPT=""

# Ensure logs directory exists
mkdir -p "$(dirname "$0")/logs"
LOG_DIR="$(dirname "$0")/logs"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --swarm)
      SWARM="$2"
      shift 2
      ;;
    --prompt)
      PROMPT="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --max-tokens)
      MAX_TOKENS="$2"
      shift 2
      ;;
    --temp)
      TEMPERATURE="$2"
      shift 2
      ;;
    --endpoint)
      ENDPOINT="$2"
      shift 2
      ;;
    --help|-h)
      grep "^#" "$0" | grep -v "^#!/bin/bash" | sed 's/^# //'
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Validate required parameters
if [[ -z "$SWARM" ]]; then
  echo -e "${RED}Error: --swarm is required${NC}"
  exit 1
fi

if [[ -z "$PROMPT" ]]; then
  echo -e "${RED}Error: --prompt is required${NC}"
  exit 1
fi

# Build request
REQUEST=$(cat <<EOF
{
  "swarm_type": "$SWARM",
  "prompt": "$PROMPT",
  "model": "$MODEL",
  "max_tokens": $MAX_TOKENS,
  "temperature": $TEMPERATURE
}
EOF
)

# Save input to log
cat > "$LOG_DIR/test_swarm_input.md" <<EOF
# Swarm Execution Test - Input

**Timestamp:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')

## Parameters

- **Endpoint:** \`$ENDPOINT/v1/swarm/execute\`
- **Swarm Type:** \`$SWARM\`
- **Model:** \`$MODEL\`
- **Max Tokens:** \`$MAX_TOKENS\`
- **Temperature:** \`$TEMPERATURE\`

## Prompt

\`\`\`
$PROMPT
\`\`\`

## Request JSON

\`\`\`json
$(echo "$REQUEST" | python3 -m json.tool)
\`\`\`
EOF

# Print header
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Stillwater LLM Portal v3 - Swarm Execution Test${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Endpoint:${NC}   $ENDPOINT/v1/swarm/execute"
echo -e "${YELLOW}Swarm:${NC}      $SWARM"
echo -e "${YELLOW}Model:${NC}      $MODEL"
echo -e "${YELLOW}Max Tokens:${NC}  $MAX_TOKENS"
echo -e "${YELLOW}Temp:${NC}       $TEMPERATURE"
echo ""
echo -e "${YELLOW}Prompt:${NC}"
echo "  $PROMPT"
echo ""
echo -e "${BLUE}Sending request...${NC}"
echo ""

# Time the request
START_TIME=$(date +%s%N)

# Make the request
RESPONSE=$(curl -s -X POST "$ENDPOINT/v1/swarm/execute" \
  -H "Content-Type: application/json" \
  -d "$REQUEST")

END_TIME=$(date +%s%N)
ELAPSED_MS=$(( (END_TIME - START_TIME) / 1000000 ))

# Check if response is valid JSON
if ! echo "$RESPONSE" | python3 -m json.tool > /dev/null 2>&1; then
  echo -e "${RED}✗ ERROR: Invalid JSON response${NC}"
  echo "$RESPONSE"
  exit 1
fi

# Parse response
RESPONSE_JSON=$(echo "$RESPONSE" | python3 -m json.tool)

# Extract fields
SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "false")
RESPONSE_TEXT=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('response', ''))" 2>/dev/null || echo "")
RESPONSE_MODEL=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('model', ''))" 2>/dev/null || echo "")
ERROR=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('error', ''))" 2>/dev/null || echo "")

# Save output to log
cat > "$LOG_DIR/test_swarm_output.md" <<EOF
# Swarm Execution Test - Output

**Timestamp:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')

## Summary

- **Success:** \`$SUCCESS\`
- **Model:** \`$RESPONSE_MODEL\`
- **Elapsed Time:** \`${ELAPSED_MS}ms\`

EOF

if [[ "$SUCCESS" == "True" ]] || [[ "$SUCCESS" == "true" ]]; then
  cat >> "$LOG_DIR/test_swarm_output.md" <<EOF

## Response

\`\`\`
$RESPONSE_TEXT
\`\`\`

EOF
else
  cat >> "$LOG_DIR/test_swarm_output.md" <<EOF

## Error

\`\`\`
$ERROR
\`\`\`

EOF
fi

cat >> "$LOG_DIR/test_swarm_output.md" <<EOF

## Full Response JSON

\`\`\`json
$RESPONSE_JSON
\`\`\`
EOF

# Print results
if [[ "$SUCCESS" == "True" ]] || [[ "$SUCCESS" == "true" ]]; then
  echo -e "${GREEN}✓ Success${NC}"
else
  echo -e "${RED}✗ Failed${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Elapsed Time:${NC} ${ELAPSED_MS}ms"
echo -e "${GREEN}Model:${NC}       $RESPONSE_MODEL"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

if [[ "$SUCCESS" == "True" ]] || [[ "$SUCCESS" == "true" ]]; then
  echo -e "${BLUE}Response:${NC}"
  echo ""
  echo "$RESPONSE_TEXT"
  echo ""
else
  echo -e "${RED}Error:${NC}"
  echo ""
  echo "$ERROR"
  echo ""
fi

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}📝 Input log:${NC}  $LOG_DIR/test_swarm_input.md"
echo -e "${YELLOW}📝 Output log:${NC} $LOG_DIR/test_swarm_output.md"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
