#!/bin/bash
################################################################################
# test_llm_portal.sh — Test script for Stillwater LLM Portal with context injection
#
# Usage:
#   ./admin/test_llm_portal.sh [OPTIONS]
#
# Options:
#   --endpoint URL              LLM portal endpoint (default: http://localhost:8788/v1/context/chat)
#   --model MODEL              LLM model to use (default: ollama)
#   --message TEXT             User message (default: "Hello, what can you do?")
#   --skills SKILL1,SKILL2     Comma-separated skills to inject
#   --recipes RECIPE1,RECIPE2  Comma-separated recipes to inject
#   --swarms SWARM1,SWARM2     Comma-separated swarms to inject
#   --personas PERSONA1,PERSONA2 Comma-separated personas to inject
#   --raw TEXT                 Raw context text to inject
#   --mode quick|full          Mode for context loading (default: quick)
#   --task TEXT                CNF capsule task description
#   --constraints TEXT         CNF capsule constraints
#   --rung 641|274177|65537    Rung target (default: 641)
#   --temp FLOAT               Temperature (default: 0.0)
#   --max-tokens INT           Max tokens (default: 4096)
#   --help                     Show this help message
#
# Examples:
#   # Test with default settings
#   ./admin/test_llm_portal.sh
#
#   # Test with prime-safety skill
#   ./admin/test_llm_portal.sh --skills "prime-safety" --message "What is your prime directive?"
#
#   # Test recipe with CNF capsule
#   ./admin/test_llm_portal.sh \
#     --recipes "null-zero-audit" \
#     --task "Audit Python function for null-zero coercion" \
#     --constraints "Fail-closed on ambiguous null handling" \
#     --message "How would you test this code?"
#
#   # Test multiple skills and recipes
#   ./admin/test_llm_portal.sh \
#     --skills "prime-safety,prime-coder" \
#     --recipes "null-zero-audit,paper-from-run" \
#     --message "Design a test plan"
#
#   # Test with persona
#   ./admin/test_llm_portal.sh \
#     --personas "guido" \
#     --message "What's the Python way?"
#
################################################################################

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Defaults
ENDPOINT="http://localhost:8788/v1/context/chat"
MODEL="ollama"
MESSAGE="Hello, what can you do?"
MODE="quick"
RUNG_TARGET="641"
TEMPERATURE="0.0"
MAX_TOKENS="4096"

SKILLS=""
RECIPES=""
SWARMS=""
PERSONAS=""
RAW=""
TASK=""
CONSTRAINTS=""

# Ensure logs directory exists
mkdir -p "$(dirname "$0")/logs"
LOG_DIR="$(dirname "$0")/logs"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --endpoint)
      ENDPOINT="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --message)
      MESSAGE="$2"
      shift 2
      ;;
    --skills)
      SKILLS="$2"
      shift 2
      ;;
    --recipes)
      RECIPES="$2"
      shift 2
      ;;
    --swarms)
      SWARMS="$2"
      shift 2
      ;;
    --personas)
      PERSONAS="$2"
      shift 2
      ;;
    --raw)
      RAW="$2"
      shift 2
      ;;
    --mode)
      MODE="$2"
      shift 2
      ;;
    --task)
      TASK="$2"
      shift 2
      ;;
    --constraints)
      CONSTRAINTS="$2"
      shift 2
      ;;
    --rung)
      RUNG_TARGET="$2"
      shift 2
      ;;
    --temp)
      TEMPERATURE="$2"
      shift 2
      ;;
    --max-tokens)
      MAX_TOKENS="$2"
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

# Function to build context sources JSON
build_context_sources() {
  local sources="[]"

  # Add skills
  if [[ -n "$SKILLS" ]]; then
    IFS=',' read -ra skill_array <<< "$SKILLS"
    for skill in "${skill_array[@]}"; do
      skill=$(echo "$skill" | xargs)  # trim whitespace
      sources=$(echo "$sources" | python3 -c "import sys, json; arr=json.load(sys.stdin); arr.append({'type':'skill','name':'$skill','mode':'$MODE'}); print(json.dumps(arr))")
    done
  fi

  # Add recipes
  if [[ -n "$RECIPES" ]]; then
    IFS=',' read -ra recipe_array <<< "$RECIPES"
    for recipe in "${recipe_array[@]}"; do
      recipe=$(echo "$recipe" | xargs)  # trim whitespace
      sources=$(echo "$sources" | python3 -c "import sys, json; arr=json.load(sys.stdin); arr.append({'type':'recipe','name':'$recipe','mode':'$MODE'}); print(json.dumps(arr))")
    done
  fi

  # Add swarms
  if [[ -n "$SWARMS" ]]; then
    IFS=',' read -ra swarm_array <<< "$SWARMS"
    for swarm in "${swarm_array[@]}"; do
      swarm=$(echo "$swarm" | xargs)  # trim whitespace
      sources=$(echo "$sources" | python3 -c "import sys, json; arr=json.load(sys.stdin); arr.append({'type':'swarm','name':'$swarm','mode':'$MODE'}); print(json.dumps(arr))")
    done
  fi

  # Add personas
  if [[ -n "$PERSONAS" ]]; then
    IFS=',' read -ra persona_array <<< "$PERSONAS"
    for persona in "${persona_array[@]}"; do
      persona=$(echo "$persona" | xargs)  # trim whitespace
      sources=$(echo "$sources" | python3 -c "import sys, json; arr=json.load(sys.stdin); arr.append({'type':'persona','name':'$persona','mode':'$MODE'}); print(json.dumps(arr))")
    done
  fi

  # Add raw context
  if [[ -n "$RAW" ]]; then
    sources=$(echo "$sources" | python3 -c "import sys, json; arr=json.load(sys.stdin); arr.append({'type':'raw','content':'$RAW'}); print(json.dumps(arr))")
  fi

  echo "$sources"
}

# Function to build CNF capsule
build_cnf_capsule() {
  local cnf="{}"

  if [[ -n "$TASK" ]]; then
    cnf=$(echo "$cnf" | python3 -c "import sys, json; d=json.load(sys.stdin); d['task']='$TASK'; print(json.dumps(d))")
  fi

  if [[ -n "$CONSTRAINTS" ]]; then
    cnf=$(echo "$cnf" | python3 -c "import sys, json; d=json.load(sys.stdin); d['constraints']='$CONSTRAINTS'; print(json.dumps(d))")
  fi

  echo "$cnf"
}

# Build context sources and CNF capsule
CONTEXT_SOURCES=$(build_context_sources)
CNF_CAPSULE=$(build_cnf_capsule)

# Build the request JSON
REQUEST=$(cat <<EOF
{
  "model": "$MODEL",
  "messages": [{"role": "user", "content": "$MESSAGE"}],
  "context_sources": $CONTEXT_SOURCES,
  "cnf_capsule": $CNF_CAPSULE,
  "rung_target": $RUNG_TARGET,
  "temperature": $TEMPERATURE,
  "max_tokens": $MAX_TOKENS
}
EOF
)

# Save input to log
echo "# LLM Portal Test Input" > "$LOG_DIR/test_llm_portal_input.md"
echo "" >> "$LOG_DIR/test_llm_portal_input.md"
echo "**Timestamp:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')" >> "$LOG_DIR/test_llm_portal_input.md"
echo "" >> "$LOG_DIR/test_llm_portal_input.md"
echo "**Endpoint:** \`$ENDPOINT\`" >> "$LOG_DIR/test_llm_portal_input.md"
echo "" >> "$LOG_DIR/test_llm_portal_input.md"
echo "## Request Parameters" >> "$LOG_DIR/test_llm_portal_input.md"
echo "" >> "$LOG_DIR/test_llm_portal_input.md"
echo "- **Model:** \`$MODEL\`" >> "$LOG_DIR/test_llm_portal_input.md"
echo "- **Message:** \`$MESSAGE\`" >> "$LOG_DIR/test_llm_portal_input.md"
echo "- **Rung Target:** \`$RUNG_TARGET\`" >> "$LOG_DIR/test_llm_portal_input.md"
echo "- **Temperature:** \`$TEMPERATURE\`" >> "$LOG_DIR/test_llm_portal_input.md"
echo "- **Max Tokens:** \`$MAX_TOKENS\`" >> "$LOG_DIR/test_llm_portal_input.md"
echo "" >> "$LOG_DIR/test_llm_portal_input.md"
echo "## Context Sources" >> "$LOG_DIR/test_llm_portal_input.md"
echo "" >> "$LOG_DIR/test_llm_portal_input.md"
echo "- **Skills:** $(echo "$SKILLS" | tr ',' '\n' | sed 's/^ */* /g' || echo 'None')" >> "$LOG_DIR/test_llm_portal_input.md"
echo "- **Recipes:** $(echo "$RECIPES" | tr ',' '\n' | sed 's/^ */* /g' || echo 'None')" >> "$LOG_DIR/test_llm_portal_input.md"
echo "- **Swarms:** $(echo "$SWARMS" | tr ',' '\n' | sed 's/^ */* /g' || echo 'None')" >> "$LOG_DIR/test_llm_portal_input.md"
echo "- **Personas:** $(echo "$PERSONAS" | tr ',' '\n' | sed 's/^ */* /g' || echo 'None')" >> "$LOG_DIR/test_llm_portal_input.md"
echo "- **Mode:** \`$MODE\`" >> "$LOG_DIR/test_llm_portal_input.md"
echo "" >> "$LOG_DIR/test_llm_portal_input.md"
if [[ -n "$TASK" ]] || [[ -n "$CONSTRAINTS" ]]; then
  echo "## CNF Capsule" >> "$LOG_DIR/test_llm_portal_input.md"
  echo "" >> "$LOG_DIR/test_llm_portal_input.md"
  [[ -n "$TASK" ]] && echo "- **Task:** \`$TASK\`" >> "$LOG_DIR/test_llm_portal_input.md"
  [[ -n "$CONSTRAINTS" ]] && echo "- **Constraints:** \`$CONSTRAINTS\`" >> "$LOG_DIR/test_llm_portal_input.md"
  echo "" >> "$LOG_DIR/test_llm_portal_input.md"
fi
echo "## Request JSON" >> "$LOG_DIR/test_llm_portal_input.md"
echo "" >> "$LOG_DIR/test_llm_portal_input.md"
echo '```json' >> "$LOG_DIR/test_llm_portal_input.md"
echo "$REQUEST" | python3 -m json.tool >> "$LOG_DIR/test_llm_portal_input.md"
echo '```' >> "$LOG_DIR/test_llm_portal_input.md"

# Send the request
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Stillwater LLM Portal Test${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Sending request to:${NC} $ENDPOINT"
echo -e "${YELLOW}Model:${NC} $MODEL"
echo -e "${YELLOW}Message:${NC} $MESSAGE"
[[ -n "$SKILLS" ]] && echo -e "${YELLOW}Skills:${NC} $SKILLS"
[[ -n "$RECIPES" ]] && echo -e "${YELLOW}Recipes:${NC} $RECIPES"
[[ -n "$SWARMS" ]] && echo -e "${YELLOW}Swarms:${NC} $SWARMS"
[[ -n "$PERSONAS" ]] && echo -e "${YELLOW}Personas:${NC} $PERSONAS"
echo ""

# Time the request
START_TIME=$(date +%s%N)

# Make the request
RESPONSE=$(curl -s -X POST "$ENDPOINT" \
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

# Save output to log
echo "# LLM Portal Test Output" > "$LOG_DIR/test_llm_portal_output.md"
echo "" >> "$LOG_DIR/test_llm_portal_output.md"
echo "**Timestamp:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')" >> "$LOG_DIR/test_llm_portal_output.md"
echo "" >> "$LOG_DIR/test_llm_portal_output.md"
echo "## Summary" >> "$LOG_DIR/test_llm_portal_output.md"
echo "" >> "$LOG_DIR/test_llm_portal_output.md"

# Extract key fields
PROVIDER=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('_meta', {}).get('provider', 'unknown'))" 2>/dev/null || echo "unknown")
RESPONSE_TEXT=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('choices', [{}])[0].get('message', {}).get('content', ''))" 2>/dev/null || echo "")
RUNG=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('_meta', {}).get('rung_target', 'unknown'))" 2>/dev/null || echo "unknown")
SYSTEM_PROMPT_CHARS=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('_meta', {}).get('system_prompt_chars', 0))" 2>/dev/null || echo "0")

echo "- **Model:** \`$MODEL\`" >> "$LOG_DIR/test_llm_portal_output.md"
echo "- **Provider:** \`$PROVIDER\`" >> "$LOG_DIR/test_llm_portal_output.md"
echo "- **Total Time:** \`${ELAPSED_MS}ms\`" >> "$LOG_DIR/test_llm_portal_output.md"
echo "- **Rung Target:** \`$RUNG\`" >> "$LOG_DIR/test_llm_portal_output.md"
echo "- **System Prompt:** \`${SYSTEM_PROMPT_CHARS} chars\`" >> "$LOG_DIR/test_llm_portal_output.md"
echo "" >> "$LOG_DIR/test_llm_portal_output.md"
echo "## Response Text" >> "$LOG_DIR/test_llm_portal_output.md"
echo "" >> "$LOG_DIR/test_llm_portal_output.md"
echo "$RESPONSE_TEXT" >> "$LOG_DIR/test_llm_portal_output.md"
echo "" >> "$LOG_DIR/test_llm_portal_output.md"
echo "## Full Response JSON" >> "$LOG_DIR/test_llm_portal_output.md"
echo "" >> "$LOG_DIR/test_llm_portal_output.md"
echo '```json' >> "$LOG_DIR/test_llm_portal_output.md"
echo "$RESPONSE_JSON" >> "$LOG_DIR/test_llm_portal_output.md"
echo '```' >> "$LOG_DIR/test_llm_portal_output.md"

# Print to console
echo -e "${GREEN}✓ Response received${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Model:${NC} $MODEL"
echo -e "${GREEN}Provider:${NC} $PROVIDER"
echo -e "${GREEN}Total Time:${NC} ${ELAPSED_MS}ms"
echo -e "${GREEN}Rung Target:${NC} $RUNG"
echo -e "${GREEN}System Prompt:${NC} ${SYSTEM_PROMPT_CHARS} chars"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Response:${NC}"
echo ""
echo "$RESPONSE_TEXT"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}📝 Input log:${NC}  $LOG_DIR/test_llm_portal_input.md"
echo -e "${YELLOW}📝 Output log:${NC} $LOG_DIR/test_llm_portal_output.md"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
