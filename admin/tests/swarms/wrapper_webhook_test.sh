#!/bin/bash
################################################################################
# wrapper_webhook_test.sh — Test Claude Code Wrapper with Portal Webhook
#
# Flow:
# 1. Call Claude Code Wrapper on port 8080
# 2. Get response
# 3. Send result to Portal v3 webhook on port 8788
################################################################################

REQUEST_ID="$(date +%s)-wrapper-test"
WRAPPER_URL="http://127.0.0.1:8080/api/generate"
PORTAL_WEBHOOK_URL="http://localhost:8788/v1/webhook/result"
START_TIME=$(date +%s%N)

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting wrapper webhook test..."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Request ID: $REQUEST_ID"
echo ""

# Call wrapper and capture response
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Calling wrapper at $WRAPPER_URL"
WRAPPER_RESPONSE=$(curl -s -X POST "$WRAPPER_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku",
    "prompt": "hello",
    "stream": false
  }' \
  --max-time 30)

WRAPPER_EXIT=$?
END_TIME=$(date +%s%N)
LATENCY_MS=$(( (END_TIME - START_TIME) / 1000000 ))

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Wrapper response received (exit: $WRAPPER_EXIT, latency: ${LATENCY_MS}ms)"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Response: $WRAPPER_RESPONSE"
echo ""

# Determine status
if [ $WRAPPER_EXIT -eq 0 ]; then
  STATUS="success"
  ERROR=""
else
  STATUS="error"
  ERROR="Exit code $WRAPPER_EXIT"
fi

# Build webhook payload
WEBHOOK_PAYLOAD=$(cat <<EOF
{
  "request_id": "$REQUEST_ID",
  "source": "wrapper",
  "status": "$STATUS",
  "response": $WRAPPER_RESPONSE,
  "error": "$ERROR",
  "latency_ms": $LATENCY_MS,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
)

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sending result to Portal webhook at $PORTAL_WEBHOOK_URL"

# Send webhook result to Portal
WEBHOOK_RESPONSE=$(curl -s -X POST "$PORTAL_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$WEBHOOK_PAYLOAD")

WEBHOOK_EXIT=$?
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Webhook response (exit: $WEBHOOK_EXIT): $WEBHOOK_RESPONSE"
echo ""

if [ $WEBHOOK_EXIT -eq 0 ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ SUCCESS - Result sent to Portal"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ FAILED - Webhook POST failed"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] To retrieve results, run:"
echo "  curl http://localhost:8788/v1/webhook/results/$REQUEST_ID"
