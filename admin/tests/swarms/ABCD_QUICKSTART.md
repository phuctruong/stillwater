# ABCD Testing - Quick Start Guide

**TL;DR**: Test prime-coder across haiku, sonnet, opus with 4 coding tasks. Measure: syntax, functional correctness, code quality, context injection.

---

## 30-Second Start

```bash
# 1. Start wrapper (Terminal 1)
python3 src/cli/src/claude_code_wrapper.py --port 8080

# 2. Run tests (Terminal 2)
bash admin/tests/swarms/run_abcd_tests.sh --setup

# 3. View results
cat admin/tests/swarms/results/ABCD_SUMMARY.json
```

---

## What Happens When You Run Tests

### 1. Test Execution (≈10-15 minutes)

The test runner will:
```
Running task_1_simple_sum on haiku...
  ✓ Code generation: 234 chars
  ✓ Syntax validation: PASS
  ✓ Functional test: PASS
  ✓ Quality score: 0.65/1.0
  ✓ Context detected: YES
  Saved: results/haiku/task_1_simple_sum_haiku.json

Running task_1_simple_sum on sonnet...
  ✓ Code generation: 289 chars
  ✓ Syntax validation: PASS
  ✓ Functional test: PASS
  ✓ Quality score: 0.82/1.0
  ✓ Context detected: YES
  Saved: results/sonnet/task_1_simple_sum_sonnet.json

Running task_1_simple_sum on opus...
  ✓ Code generation: 312 chars
  ✓ Syntax validation: PASS
  ✓ Functional test: PASS
  ✓ Quality score: 0.91/1.0
  ✓ Context detected: YES
  Saved: results/opus/task_1_simple_sum_opus.json

... (repeat for 4 tasks × 3 models = 12 total tests)
```

### 2. Summary Report

After all tests, you'll see:

```
======================================================================
ABCD COMPARISON REPORT: Prime-Coder Across Models
======================================================================

Model        Syntax     Functional Quality  Context
----------------------------------------------
haiku        75.0%      50.0%      0.42     75.0%
sonnet       100.0%     100.0%     0.72     100.0%
opus         100.0%     100.0%     0.81     100.0%

Key Findings:
  haiku: 4 tests, 50% pass, quality=0.42
  sonnet: 4 tests, 100% pass, quality=0.72
  opus: 4 tests, 100% pass, quality=0.81

Summary saved to: admin/tests/swarms/results/ABCD_SUMMARY.json
```

---

## Result Files

After running, you'll have:

```
admin/tests/swarms/results/
├── haiku/
│   ├── task_1_simple_sum_haiku.json
│   ├── task_2_palindrome_haiku.json
│   ├── task_3_fibonacci_haiku.json
│   └── task_4_dict_merge_haiku.json
├── sonnet/
│   ├── task_1_simple_sum_sonnet.json
│   ├── task_2_palindrome_sonnet.json
│   ├── task_3_fibonacci_sonnet.json
│   └── task_4_dict_merge_sonnet.json
├── opus/
│   ├── task_1_simple_sum_opus.json
│   ├── task_2_palindrome_opus.json
│   ├── task_3_fibonacci_opus.json
│   └── task_4_dict_merge_opus.json
└── ABCD_SUMMARY.json
```

### Example Result File

`results/sonnet/task_2_palindrome_sonnet.json`:

```json
{
  "model": "sonnet",
  "task_name": "task_2_palindrome",
  "syntax_valid": true,
  "functional_pass": true,
  "quality_score": 0.82,
  "system_prompt_detected": true,
  "timestamp": "2026-02-22T10:45:30.123456",
  "code": "def is_palindrome(s: str) -> bool:\n    \"\"\"\n    Check if a string is a palindrome.\n    \n    Ignores spaces, punctuation, and case.\n    \n    Args:\n        s: Input string\n        \n    Returns:\n        True if palindrome, False otherwise\n    \n    Examples:\n        >>> is_palindrome('A man, a plan, a canal: Panama')\n        True\n        >>> is_palindrome('hello')\n        False\n    \"\"\"\n    # Remove non-alphanumeric and convert to lowercase\n    cleaned = ''.join(c.lower() for c in s if c.isalnum())\n    \n    # Check if cleaned string equals its reverse\n    return cleaned == cleaned[::-1]\n\n\nif __name__ == '__main__':\n    test_cases = [\n        ('A man, a plan, a canal: Panama', True),\n        ('hello', False),\n        ('racecar', True),\n        ('', True),\n        ('a', True),\n    ]\n    \n    for text, expected in test_cases:\n        result = is_palindrome(text)\n        assert result == expected, f\"Failed for {text!r}\"\n        print(f\"✓ {text!r} -> {result}\")\n    \n    print(\"All tests passed!\")\n"
}
```

### Summary Report

`results/ABCD_SUMMARY.json`:

```json
{
  "haiku": {
    "syntax_rate": 0.75,
    "functional_rate": 0.5,
    "quality_avg": 0.42,
    "context_rate": 0.75,
    "total_tests": 4
  },
  "sonnet": {
    "syntax_rate": 1.0,
    "functional_rate": 1.0,
    "quality_avg": 0.72,
    "context_rate": 1.0,
    "total_tests": 4
  },
  "opus": {
    "syntax_rate": 1.0,
    "functional_rate": 1.0,
    "quality_avg": 0.81,
    "context_rate": 1.0,
    "total_tests": 4
  }
}
```

---

## Interpreting Your Results

### Scenario 1: All Tests Pass (Expected)

```
haiku:   75%/50%/0.42 ← Some syntax errors, functional issues on hard tasks
sonnet:  100%/100%/0.72 ← Perfect, good quality
opus:    100%/100%/0.81 ← Perfect, excellent quality

Analysis:
✅ Sonnet is reliable (100% functional)
✅ Opus is best quality (0.81)
✅ Haiku works but needs simpler tasks
✅ Context injection working on all models
```

**What this means:**
- Sonnet is the sweet spot for coding tasks (good quality, acceptable cost)
- Opus for critical/complex code only
- Haiku for trivial tasks only

### Scenario 2: Haiku Context Not Detected

```
haiku:   50%/25%/0.35 context_rate: 25% ← Problem!
sonnet:  100%/100%/0.72 context_rate: 100%
opus:    100%/100%/0.81 context_rate: 100%

Issue: Haiku 75% tests have context_rate=False
```

**Possible causes:**
1. HTTP wrapper not properly injecting system prompt
2. Haiku filtering out or not using system prompt
3. Skill markers not appearing in response text

**Fix:**
```bash
# Check wrapper log
tail -50 /tmp/wrapper.log

# Manually test context injection
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "system": "You are a coder. Focus on correctness.",
    "prompt": "Write hello world",
    "model": "haiku"
  }'

# Response should include system prompt markers
```

### Scenario 3: Functional Tests Failing

```
haiku:   75%/50%/0.42 ← Only 50% passing functional tests
sonnet:  100%/100%/0.72
opus:    100%/100%/0.81
```

**Possible causes:**
1. Function name mismatch (wrote `sum_list()` instead of `sum_integers()`)
2. Logic error in implementation
3. Edge case not handled (empty list, negative numbers, etc.)

**Debug single failure:**
```bash
# Run specific task on specific model
pytest admin/tests/swarms/test_abcd_coding.py::TestABCDCoding::test_coding_task[task_3_fibonacci-haiku] -v -s

# Look at detailed error message
# Check: results/haiku/task_3_fibonacci_haiku.json
cat admin/tests/swarms/results/haiku/task_3_fibonacci_haiku.json | jq .code
```

---

## Cost Analysis Example

If these are your real results:

```
haiku:   50% functional, cost ~$0.001 per request
sonnet:  100% functional, cost ~$0.01 per request  (10× haiku)
opus:    100% functional, cost ~$0.05 per request  (50× haiku)
```

**Decision matrix:**

| Task Complexity | Model | Justification |
|--|--|--|
| Trivial (task_1) | haiku | 50% works fine, cheap |
| Easy (task_2) | sonnet | Must be reliable, haiku fails too often |
| Medium (task_3) | sonnet | Safe choice, 10× cost worth it |
| Hard (task_4) | opus | Need best quality, reliability matters |

**Expected cost per task:**
- Haiku: 1 × $0.001 = $0.001
- Sonnet: 1 × $0.01 = $0.01 (best value)
- Opus: 1 × $0.05 = $0.05 (only for critical)
- **Average**: ~$0.02/task (assuming mix of difficulties)

---

## Common Commands

### Run all tests
```bash
bash admin/tests/swarms/run_abcd_tests.sh --setup
```

### Run only sonnet
```bash
bash admin/tests/swarms/run_abcd_tests.sh --model sonnet
```

### Run only task 2 (palindrome)
```bash
bash admin/tests/swarms/run_abcd_tests.sh --task task_2
```

### Run only task 3 on opus
```bash
bash admin/tests/swarms/run_abcd_tests.sh --task task_3 --model opus
```

### View specific result
```bash
cat admin/tests/swarms/results/sonnet/task_2_palindrome_sonnet.json
```

### View comparison summary
```bash
cat admin/tests/swarms/results/ABCD_SUMMARY.json | jq
```

### Run with pytest directly (more control)
```bash
# Run all
pytest admin/tests/swarms/test_abcd_coding.py -v -s

# Run specific test
pytest admin/tests/swarms/test_abcd_coding.py::TestABCDCoding::test_coding_task[task_2_palindrome-sonnet] -v -s

# Run only haiku
pytest admin/tests/swarms/test_abcd_coding.py -k haiku -v -s
```

---

## Troubleshooting

### Wrapper not starting

```bash
# Check if port 8080 is in use
lsof -i :8080

# Kill any old instances
pkill -f "claude_code_wrapper.py"

# Start manually
python3 src/cli/src/claude_code_wrapper.py --port 8080
```

### Tests hanging

The LLM calls can take 30-60 seconds per test. If hanging for >2 minutes:
```bash
# Check if claude CLI is responsive
timeout 10 claude -p "hello"

# Check wrapper logs
tail -f /tmp/wrapper.log
```

### Import errors

```bash
# Make sure you're running from project root
cd /home/phuc/projects/stillwater

# Make sure pytest is installed
pip install pytest pyyaml

# Run tests
pytest admin/tests/swarms/test_abcd_coding.py -v -s
```

### Results not being saved

```bash
# Check directory permissions
ls -la admin/tests/swarms/results/

# Create if missing
mkdir -p admin/tests/swarms/results/{haiku,sonnet,opus}

# Re-run tests
pytest admin/tests/swarms/test_abcd_coding.py -v -s
```

---

## Next Steps After Running Tests

1. **Analyze results**: Look at ABCD_SUMMARY.json
2. **Identify best model**: Usually sonnet (sweet spot)
3. **Check context injection**: Should be 100% on all models
4. **Review failing code**: Look at specific .json files
5. **Update production**: Use winning model+config for your app

---

## See Also

- `ABCD_TESTING.md` — Full ABCD framework documentation
- `test_abcd_coding.py` — Test implementation
- `AB_TESTING.md` — Simpler A|B testing explanation
- `SWARMS_ARCHITECTURE.md` — Context injection architecture
