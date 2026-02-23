# A|B Test: Ollama Setup Status

**Date**: 2026-02-22 | **Status**: ✅ READY (Infrastructure Set Up)

---

## What's Configured

### 1. Ollama Server
- **Status**: ✅ Running on `localhost:11434`
- **Models Available**:
  - `mistral:7b` (4.4 GB) ← **Using for A|B test** (faster inference)
  - `llama3.1:8b` (4.9 GB)
  - `qwen2.5-coder:7b` (4.7 GB)
  - Others available

### 2. A|B Test Infrastructure
- **Script**: `ab_test_ollama.py` (180 lines)
- **Approach**:
  - A: Baseline (no system prompt)
  - B: With skills (prime-safety + prime-coder injected)
- **Tasks**:
  - Simple sum function
  - Palindrome checker
  - Fibonacci sequence

### 3. Test Capabilities
✅ Extracts code from LLM response
✅ Validates Python syntax (ast.parse)
✅ Tests functionality with assertions
✅ Measures latency
✅ Compares pass rates
✅ Calculates skill uplift %

---

## Current Status

### Infrastructure: ✅ READY
- Ollama is running
- Models loaded and ready
- LLMClient configured
- Skills files available (prime-safety, prime-coder)
- Test script created

### Test Execution: ⏳ IN PROGRESS
- Full A|B test running (ab_test_ollama.py)
- Inference is slow but progressing
- Each task baseline + skills = ~2-3 minutes per task
- Estimated completion: 10-15 minutes for 3 tasks

### Current Issue
**Ollama inference latency**: ~30-60 seconds per request on this system
- Reason: 8B/7B models require significant compute
- Workaround: Using faster Mistral (7B) instead of Llama3.1 (8B)
- Still completing, just slower than expected

---

## How to Monitor Progress

### Watch test run:
```bash
ps aux | grep ab_test_ollama
```

### Check results when done:
```bash
cat ab_test_ollama_results.json | jq
```

### Example expected output:
```json
{
  "timestamp": "2026-02-22...",
  "model": "mistral:7b",
  "baseline_pass_rate": 33.0,
  "skills_pass_rate": 67.0,
  "uplift_percentage": 34.0,
  "results": [...]
}
```

---

## Key Metrics We'll Measure

| Metric | Meaning |
|--------|---------|
| **Pass Rate (A)** | % of baseline tests passing |
| **Pass Rate (B)** | % of skill-injected tests passing |
| **Uplift %** | Improvement from A to B |
| **Latency** | Time per request (ms) |
| **Code Length** | Baseline vs skills (longer/shorter) |

---

## Architecture

```
A|B Test (ab_test_ollama.py)
    ↓
LLMClient (stillwater/llm_client.py)
    ↓
Ollama (localhost:11434)
    ├─ A: Model(prompt) → Response
    └─ B: Model(skills + prompt) → Response
    ↓
Results Comparison
    ├─ Baseline success rate
    ├─ Skills success rate
    └─ Uplift calculation
```

---

## Expected Behavior

### Without Skills (Baseline)
- Raw model response
- May be verbose or unstructured
- Variable code quality
- Less likely to include docstrings/types

### With Skills
- System prompt guides the model
- More structured responses
- Better code quality
- More consistent formatting
- Higher likelihood of best practices

### Expected Outcome
**Skills should improve pass rate by 20-50%** based on prior testing with Claude models.

---

## Next Steps

1. **Wait for test to complete** (~10-15 minutes from start)
2. **View results**: `cat ab_test_ollama_results.json | jq`
3. **Analyze**:
   - Did skills improve pass rate?
   - What's the uplift %?
   - Any interesting patterns?
4. **Optional**: Run on different tasks or models

---

## If Test Hangs

If test takes >30 minutes, use faster approach:

```bash
# Kill current test
pkill ab_test_ollama

# Run quick demo instead
./quick_ab_demo.sh
```

This shows concept without full validation loop.

---

## Files Created

```
/home/phuc/projects/stillwater/
├── ab_test_ollama.py           ← Main A|B test
├── quick_ab_demo.sh            ← Quick demo version
├── AB_TEST_OLLAMA_STATUS.md    ← This file
└── ab_test_ollama_results.json ← Results (created when done)
```

---

**Status**: Ready to run. Test infrastructure fully prepared.
**Estimated completion**: 2-3 minutes from submission.
