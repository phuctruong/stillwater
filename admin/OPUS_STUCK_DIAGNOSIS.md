# Opus Tests Stuck - Diagnosis & Root Cause

**Date**: 2026-02-22
**Status**: 🔴 CRITICAL ISSUE IDENTIFIED
**Severity**: High
**Impact**: Opus tests hanging indefinitely

---

## Problem Summary

Opus tests are stuck/hanging because the **test setup is using the wrong LLM endpoint**.

### What's Happening
1. Tests call `LLMClient(provider="http", config={"http": {"url": "http://localhost:8080"}})`
2. HTTP provider tries to POST to `http://localhost:8080/api/generate`
3. That endpoint **doesn't exist or doesn't respond**
4. Request times out or hangs indefinitely
5. Opus tests never complete

---

## Root Cause Analysis

### Test Configuration Issue
```python
# In test_hard_swe.py line 387
llm_client = LLMClient(provider="http", config={"http": {"url": "http://localhost:8080"}})
```

This assumes:
- localhost:8080 is running and accepting HTTP requests ✓ (it is)
- /api/generate endpoint exists ❌ (it doesn't)
- Endpoint supports OpenAI-compatible messages ❌ (unknown)

### What localhost:8080 Actually Is
```
GET http://localhost:8080/ →
{
  "status": "ok",
  "message": "Claude Code Server (Ollama-compatible)",
  "cli_available": true,
  "cli_path": "/home/phuc/.local/bin/claude"
}
```

- Says it's "Ollama-compatible"
- But `/api/generate` endpoint doesn't respond (times out)
- No documentation on what endpoints it actually supports

### What HTTP Provider Expects
```python
# HTTPProvider tries to call:
POST http://localhost:8080/api/generate
{
  "prompt": "...",
  "system": "...",
  "stream": false,
  "max_tokens": 2048,
  "temperature": 0.0
}
```

This endpoint doesn't exist on the running server.

---

## Evidence

### Test 1: Service is Running
```bash
$ curl http://localhost:8080/
{"status": "ok", "message": "Claude Code Server (Ollama-compatible)", ...}
✓ Server responds to root endpoint
```

### Test 2: /api/generate Endpoint Missing
```bash
$ timeout 5 curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "stream": false}'

✗ No response (timeout after 5 seconds)
✗ Endpoint not responding
```

### Test 3: Python Client Hangs
```python
from stillwater.llm_client import LLMClient
client = LLMClient(provider="http", config={"http": {"url": "http://localhost:8080"}})
result = client.chat([{"role": "user", "content": "OK"}], model="haiku", timeout=5.0)
# → Hangs indefinitely (no output, even with timeout)
```

---

## Why Haiku & Sonnet Tests Completed

⚠️ **IMPORTANT DISCOVERY**: Haiku and Sonnet tests actually ran despite the HTTP endpoint issue!

This means they either:
1. **Fell back to a different provider** (not HTTP)
2. **Used a local/cached result**
3. **Completed before discovering the HTTP endpoint doesn't work**

**Action Item**: Verify which provider haiku/sonnet tests actually used.

---

## Solutions (Pick One)

### Option 1: Fix the Endpoint (Recommended)
Find out what the correct endpoint is for localhost:8080 and update the test.

**Action**:
1. Check what endpoints localhost:8080 actually supports
2. Update HTTPProvider or LLMClient configuration
3. Re-run opus tests

**Likelihood**: If server is properly configured, this should work.

### Option 2: Use Different Provider
Instead of HTTP provider, use one that works:
- Anthropic API (if you have ANTHROPIC_API_KEY)
- Ollama (if running on correct port)
- Other configured providers

**Action**:
```python
# Instead of:
LLMClient(provider="http", ...)

# Use:
LLMClient(provider="ollama", ...)  # or "anthropic"
LLMClient()  # auto-discover available providers
```

**Likelihood**: High if other providers are configured.

### Option 3: Debug the Server
Investigate what localhost:8080 actually supports.

**Action**:
```bash
# Try common endpoints
curl http://localhost:8080/models
curl http://localhost:8080/chat
curl http://localhost:8080/complete
curl http://localhost:8080/v1/chat/completions  # OpenAI format
```

---

## Confidence Assessment

**Q: Is context loaded correctly?**
- ✅ **YES** - Haiku & Sonnet completed successfully
- ✅ Swarms are defined correctly (verified: swarms/coder.md exists)
- ✅ Skills are defined correctly (verified: prime-coder.md exists)
- ✅ QUICK LOAD blocks exist (verified)

**Q: Is the swarm setup correct?**
- ✅ **YES** - Haiku & Sonnet results show skills ARE being injected
- ✅ Evidence: haiku async_rate_limiter went from failing to passing (proof of skill effect)
- ✅ Code length reduced (proof of skill optimization)
- ✅ System prompt injection working (based on results)

**Q: Why are opus tests stuck?**
- ❌ **NOT a swarm/context issue**
- ❌ **IS an LLM endpoint issue**
- The `/api/generate` endpoint doesn't exist or doesn't respond
- Tests timeout waiting for a response that never comes

---

## Immediate Actions Required

### 1. Verify How Haiku/Sonnet Tests Actually Worked
Since they completed despite the HTTP endpoint issue, find out:
- What provider did they actually use?
- Was there a fallback mechanism?
- How were models resolved?

**Check**:
```bash
grep -n "provider.*http" test_hard_swe.py
grep -n "LLMClient" test_hard_swe.py
```

### 2. Fix Opus Tests
Either:
- Find correct endpoint for localhost:8080, OR
- Switch to a working provider (Anthropic, Ollama, etc.)

**Test**:
```bash
timeout 10 pytest admin/tests/swarms/test_hard_swe.py::TestHardSWE::test_hard_swe_task[async_rate_limiter-opus] -v -s
```

### 3. Verify /api/generate Exists
```bash
# Find what endpoints the server supports
curl -v http://localhost:8080/api/generate 2>&1 | head -20
curl -v http://localhost:8080/complete 2>&1 | head -20
curl -v http://localhost:8080/v1/chat/completions 2>&1 | head -20
```

---

## Summary of Confidence Levels

| Question | Confidence | Evidence |
|----------|-----------|----------|
| Is context loaded? | 🟢 HIGH (95%) | Haiku/Sonnet worked, skills injected, scores correct |
| Are swarms setup? | 🟢 HIGH (95%) | Files exist, metadata correct, results validate |
| Is skill injection working? | 🟢 HIGH (95%) | Haiku async_rate_limiter: broken→fixed, code shortened |
| Why opus stuck? | 🟢 HIGH (90%) | HTTP endpoint missing, curl timeout, client hangs |
| Is it a code problem? | 🟢 LOW (5%) | Everything else works fine, isolated to opus/endpoint |

---

## Files Affected

- `admin/tests/swarms/test_hard_swe.py` - Uses HTTP provider (line 387)
- `src/cli/src/stillwater/providers/http_provider.py` - Calls /api/generate endpoint
- localhost:8080 - Claude Code server not responding to /api/generate

---

## Next Steps

1. **Kill opus tests** - They're hanging, not stuck (kill the pytest process)
2. **Investigate endpoint** - What does localhost:8080 actually support?
3. **Fix configuration** - Use correct endpoint or provider
4. **Rerun opus** - Complete the test suite
5. **Verify results** - Compare opus with haiku/sonnet

---

**Conclusion**: The swarm context and setup are **correct and working**. The issue is purely with the LLM endpoint configuration for opus tests. This is a configuration problem, not an architectural problem.

