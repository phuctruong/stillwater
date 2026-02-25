# Real LLM Testing Plan — Phase 1

## Why Real LLM Testing

Current tests only verify the CPU path. When CPU confidence < 0.70 (Phase 1 threshold), the LLM fallback triggers. We have NEVER tested this with a real LLM — only mocked responses.

## What to Test

### Test 1: LLM fallback triggers correctly
```
Input: "plz halp" (misspelled, no matching seeds)
Expected: CPU returns ("unknown", 0.0) → LLM fallback called
Verify: LLM returns a valid label (task, greeting, etc.)
```

### Test 2: LLM classification accuracy
```
Inputs that CPU can't handle (no seeds):
  "plz halp" → should be: task/support
  "yo" → should be: greeting
  "what should I do about this error?" → should be: task
  "merci beaucoup" → should be: gratitude (non-English)
  "lgtm ship it" → should be: task
```

### Test 3: LLM latency measurement
```
For each LLM call, measure:
  - Time to first token
  - Total completion time
  - Compare: CPU ~0ms vs LLM ~500-2000ms
```

### Test 4: LLM cost tracking
```
For each LLM call, log:
  - Model used (haiku vs sonnet)
  - Input tokens
  - Output tokens
  - Cost estimate ($0.00025/1K input, $0.00125/1K output for haiku)
```

### Test 5: LLM learns from fallback
```
After LLM classifies "plz halp" → task:
  1. System should LEARN this pattern
  2. Next time "plz halp" appears → CPU handles it (no LLM needed)
  3. Verify: second call uses CPU path, not LLM
```

## Requirements

1. **API key**: Need real Anthropic API key (ANTHROPIC_API_KEY env var)
2. **Model**: haiku for Phase 1 (fast + cheap for classification)
3. **Rate limiting**: max 10 LLM calls per test run
4. **Cost budget**: < $0.01 per test run

## Test Script Location

`tests/orchestration/phase1/test-cases/test_llm_fallback.py`

```python
# Pseudocode — requires real API key
import os
import time
from stillwater.triple_twin import TripleTwinEngine
from stillwater.data_registry import DataRegistry

# Skip if no API key
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    print("SKIP: No ANTHROPIC_API_KEY set. Real LLM tests require API key.")
    exit(0)

reg = DataRegistry()
engine = TripleTwinEngine(registry=reg, llm_api_key=API_KEY)

# Test prompts that CPU can't handle
LLM_TEST_PROMPTS = [
    ("plz halp", "task"),
    ("yo", "greeting"),
    ("what should I do about this error?", "task"),
    ("merci beaucoup", "gratitude"),
    ("lgtm ship it", "task"),
]

for text, expected in LLM_TEST_PROMPTS:
    start = time.time()
    result = engine.process(text)
    elapsed = time.time() - start

    print(f"Input: {text!r}")
    print(f"  Label: {result.phase1.label}")
    print(f"  Confidence: {result.phase1.confidence:.3f}")
    print(f"  LLM called: {result.phase1.llm_used}")
    print(f"  Time: {elapsed:.3f}s")
    print(f"  Expected: {expected}")
    print(f"  PASS: {result.phase1.label == expected}")
    print()
```

## When to Run

- NOT in CI (requires API key, costs money)
- Run manually before major releases
- Run after changing LLM prompt template
- Run after adding new Phase 1 labels

## Integration with stillwater

Stillwater currently uses mock LLM in tests. The real LLM integration depends on:
1. `TripleTwinEngine` accepting an `llm_api_key` parameter
2. The LLM prompt template for Phase 1 classification
3. Response parsing (LLM returns label string)

Currently the LLM path in `triple_twin.py` is likely a stub/mock. This test plan identifies what needs to be implemented for real LLM fallback to work.
