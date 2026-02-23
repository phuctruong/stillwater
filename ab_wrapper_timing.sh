#!/bin/bash
################################################################################
# A|B Timing Test: Claude Wrapper with/without prime-coder skill
#
# Measures exact response time for:
# A: Baseline (no system prompt)
# B: With prime-coder skill injection
################################################################################

WRAPPER="http://127.0.0.1:8080/api/generate"
TASK="Write a Python function that adds two numbers. Include docstring."

echo "========================================================================"
echo "A|B TIMING TEST: Claude Haiku Wrapper"
echo "========================================================================"
echo ""
echo "Task: $TASK"
echo ""

# A: BASELINE (no skills)
echo "A. BASELINE (no system prompt):"
START_A=$(date +%s%N)

RESPONSE_A=$(curl -s -X POST "$WRAPPER" \
  -d "{
    \"model\": \"claude-haiku\",
    \"prompt\": \"$TASK\",
    \"stream\": false
  }" --max-time 15 2>&1)

END_A=$(date +%s%N)
TIME_A=$(( (END_A - START_A) / 1000000 ))

if echo "$RESPONSE_A" | grep -q "response"; then
  LENGTH_A=$(echo "$RESPONSE_A" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('response','')))" 2>&1)
  echo "   ✓ Success"
  echo "   Time: ${TIME_A}ms"
  echo "   Response length: ${LENGTH_A} chars"
else
  echo "   ✗ Failed"
  echo "   Time: ${TIME_A}ms"
fi
echo ""

# B: WITH SKILLS (prime-coder)
echo "B. WITH PRIME-CODER SKILL:"

SKILL_PROMPT="You are an expert Python programmer. Your response must:
1. Include comprehensive docstrings explaining the function
2. Add type hints for parameters and return values
3. Handle edge cases and errors
4. Include example usage or test assertions
Write production-quality code."

START_B=$(date +%s%N)

RESPONSE_B=$(curl -s -X POST "$WRAPPER" \
  -d "{
    \"model\": \"claude-haiku\",
    \"prompt\": \"$SKILL_PROMPT\n\n$TASK\",
    \"stream\": false
  }" --max-time 15 2>&1)

END_B=$(date +%s%N)
TIME_B=$(( (END_B - START_B) / 1000000 ))

if echo "$RESPONSE_B" | grep -q "response"; then
  LENGTH_B=$(echo "$RESPONSE_B" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('response','')))" 2>&1)
  echo "   ✓ Success"
  echo "   Time: ${TIME_B}ms"
  echo "   Response length: ${LENGTH_B} chars"
else
  echo "   ✗ Failed"
  echo "   Time: ${TIME_B}ms"
fi
echo ""

# COMPARISON
echo "========================================================================"
echo "COMPARISON:"
echo "========================================================================"
DIFF=$(( TIME_B - TIME_A ))
if [ $TIME_A -gt 0 ]; then
  RATIO=$(( TIME_B * 100 / TIME_A ))
else
  RATIO=0
fi

echo "Baseline time:  ${TIME_A}ms"
echo "With skills:    ${TIME_B}ms"
echo "Difference:     ${DIFF}ms ($((RATIO - 100))+%)"
echo ""

if [ $TIME_B -lt $TIME_A ]; then
  echo "✓ Skills FASTER (likely caching or variance)"
elif [ $TIME_B -eq $TIME_A ]; then
  echo "≈ Same speed (variance < 1ms)"
else
  echo "⚠ Skills slightly slower (system prompt overhead)"
  echo "  Overhead: ~${DIFF}ms"
fi
echo ""

# Show response preview
echo "========================================================================"
echo "RESPONSE PREVIEW:"
echo "========================================================================"
echo ""
echo "A. Baseline response (first 300 chars):"
echo "$RESPONSE_A" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('response','')[:300])" 2>&1 || echo "[Error parsing]"
echo ""
echo "B. With skills response (first 300 chars):"
echo "$RESPONSE_B" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('response','')[:300])" 2>&1 || echo "[Error parsing]"
echo ""
