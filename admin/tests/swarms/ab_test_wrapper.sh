#!/bin/bash
################################################################################
# A|B Test: Claude Code Wrapper with/without Skills
#
# Tests if skills help using the working Claude Code wrapper on port 8080
################################################################################

echo "========================================================================"
echo "A|B Test: Claude Code Wrapper with/without Skills"
echo "========================================================================"
echo ""
echo "Model: Claude (via wrapper on port 8080)"
echo "Method: System prompt injection"
echo ""

TASK="Write a Python function that adds two numbers"

echo "Task: $TASK"
echo ""

# Helper function to test response
test_response() {
  local label="$1"
  local prompt="$2"

  echo "$label:"
  echo "---"

  START=$(date +%s%N)

  RESPONSE=$(curl -s -X POST http://127.0.0.1:8080/api/generate \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"claude-haiku\",
      \"prompt\": \"$prompt\",
      \"stream\": false
    }" --max-time 10 2>&1)

  END=$(date +%s%N)
  LATENCY=$(( (END - START) / 1000000 ))

  if echo "$RESPONSE" | grep -q "response"; then
    echo "✓ Success ($LATENCY ms)"
    echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print('Length:', len(d.get('response', '')))" 2>&1
  else
    echo "✗ Failed or no response"
  fi
  echo ""
}

# A: Baseline (no system prompt)
test_response "A. BASELINE (no skills)" "$TASK"

# B: With skills (expert system prompt)
SKILL_PROMPT="You are an expert Python programmer. Write clean, well-documented code with docstrings, type hints, and error handling."

test_response "B. WITH SKILLS (expert system prompt)" "$SKILL_PROMPT\n\n$TASK"

echo "========================================================================"
echo "Observations:"
echo "- Baseline: Raw response from Claude"
echo "- With Skills: Response guided by expert system prompt"
echo "- Expected: Skills version has better structure/documentation"
echo "========================================================================"
