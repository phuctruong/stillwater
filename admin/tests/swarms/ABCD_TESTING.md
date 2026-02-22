# ABCD Testing Framework - Prime-Coder Swarm

Auth: 65537 | Version: 1.0.0 | Focus: Code Quality Measurement & Model Comparison

---

## What is ABCD Testing?

ABCD testing compares the prime-coder swarm across **4 variants**:

| Variant | Description | Purpose |
|---------|-------------|---------|
| **A** | Haiku (baseline) | Fastest model; baseline quality |
| **B** | Sonnet (mid-tier) | Larger model; expected improvement |
| **C** | Opus (largest) | Best model; upper bound quality |
| **D** | (Reserved) | Custom baseline or specialized model |

We run the **same coding tasks** across all models and compare:
- ✅ **Syntax validity**: Does code have valid Python syntax?
- ✅ **Functional correctness**: Does code pass the test suite?
- ✅ **Code quality**: Does code follow best practices?
- ✅ **Context injection**: Was the system prompt properly applied?

---

## File Structure

```
admin/tests/swarms/
├── test_abcd_coding.py          # ABCD test suite
├── ABCD_TESTING.md              # This file
├── results/                      # Test results (created after first run)
│   ├── haiku/                    # Haiku model results
│   │   ├── task_1_simple_sum_haiku.json
│   │   ├── task_2_palindrome_haiku.json
│   │   ├── task_3_fibonacci_haiku.json
│   │   └── task_4_dict_merge_haiku.json
│   ├── sonnet/                   # Sonnet model results
│   │   ├── task_1_simple_sum_sonnet.json
│   │   ├── task_2_palindrome_sonnet.json
│   │   ├── task_3_fibonacci_sonnet.json
│   │   └── task_4_dict_merge_sonnet.json
│   ├── opus/                     # Opus model results
│   │   ├── task_1_simple_sum_opus.json
│   │   ├── task_2_palindrome_opus.json
│   │   ├── task_3_fibonacci_opus.json
│   │   └── task_4_dict_merge_opus.json
│   └── ABCD_SUMMARY.json        # Cross-model comparison summary
```

---

## Coding Tasks in Detail

### Task 1: Simple Sum Function
**Difficulty**: ⭐ (Trivial)

```python
sum_integers([1, 2, 3]) → 6
sum_integers([]) → 0
```

**What it measures:**
- Can the model write basic functions?
- Does it handle edge cases (empty list)?
- Does it include docstrings and type hints?

**Success criteria:**
- ✅ Valid Python syntax
- ✅ Passes all test cases
- ✅ Has docstring + type hints
- ✅ Quality score > 0.3

---

### Task 2: Palindrome Checker
**Difficulty**: ⭐⭐ (Easy)

```python
is_palindrome("A man, a plan, a canal: Panama") → True
is_palindrome("hello") → False
```

**What it measures:**
- Can the model handle string manipulation?
- Does it normalize input (lowercase, strip punctuation)?
- Does it include comprehensive tests?

**Success criteria:**
- ✅ Valid Python syntax
- ✅ Passes all test cases (including "A man, a plan...")
- ✅ Includes error handling
- ✅ Quality score > 0.3

---

### Task 3: Fibonacci Generator
**Difficulty**: ⭐⭐⭐ (Medium)

```python
fibonacci(5) → [0, 1, 1, 2, 3]
fibonacci(0) → []
fibonacci(1) → [0]
```

**What it measures:**
- Can the model implement algorithms?
- Does it understand sequences/generators?
- Does it handle edge cases correctly?

**Success criteria:**
- ✅ Valid Python syntax
- ✅ Passes all test cases
- ✅ Efficient implementation
- ✅ Quality score > 0.3

---

### Task 4: Dictionary Merger
**Difficulty**: ⭐⭐⭐⭐ (Hard)

```python
merge_dicts({"a": 1}, {"b": 2}) → {"a": 1, "b": 2}
merge_dicts({"a": 1}, {"a": 2}) → {"a": 2}
```

**What it measures:**
- Can the model handle variable arguments (*args)?
- Does it use advanced type hints?
- Does it include comprehensive error handling?

**Success criteria:**
- ✅ Valid Python syntax
- ✅ Passes all test cases
- ✅ Type hints with typing.Dict, typing.Any
- ✅ Quality score > 0.3

---

## Quality Score Breakdown

Quality score ranges from **0.0 to 1.0** based on these factors:

| Factor | Weight | Score | What it checks |
|--------|--------|-------|-----------------|
| Docstrings | 0.1 | +0.1 if present | Module-level docstring |
| Type Hints | 0.15 | +0.15 if present | Function args and return type |
| Error Handling | 0.15 | +0.15 if try/except | Graceful exception handling |
| Tests/Assertions | 0.2 | +0.2 if present | test_* functions or assert statements |
| Function Structure | 0.15 | +0.15 if has functions | Well-organized with functions |
| Length (20-500 lines) | 0.1 | +0.1 if in range | Not too short, not too bloated |
| **Penalty: Anti-patterns** | -0.1 | -0.1 if present | eval(), exec(), import * |

**Interpretation:**
- **0.0-0.3**: Poor (minimal structure, no tests)
- **0.3-0.6**: Fair (some structure, incomplete tests)
- **0.6-0.8**: Good (well-structured, comprehensive)
- **0.8-1.0**: Excellent (docstrings, types, tests, error handling)

---

## Context Injection Verification

### What is "Context Injection"?

The prime-coder swarm includes:
1. **prime-safety skill** — Safety constraints and boundaries
2. **prime-coder skill** — Red-green gate, evidence contract, proof discipline
3. **Persona (Donald Knuth)** — Algorithmic precision, documentation

When these are properly injected, the model should:
- ✅ Ask for clarification if scope is unclear
- ✅ Include test cases and evidence artifacts
- ✅ Focus on algorithmic correctness
- ✅ Document invariants and complexity

### How We Detect It

The test checks:
1. Does response mention "## SKILL:" or "prime-coder"?
2. Does code include docstrings/type hints (Knuth influence)?
3. Does code include tests (evidence contract)?

**Note**: A `False` context detection means either:
- The system prompt wasn't included in the request
- The model filtered it out
- The skill markers were in the code itself (not system prompt)

---

## Running ABCD Tests

### Prerequisites

```bash
# Terminal 1: Start wrapper
python3 cli/src/claude_code_wrapper.py --port 8080

# Terminal 2: Verify it's running
curl http://localhost:8080/api/generate -X POST \
  -H "Content-Type: application/json" \
  -d '{"prompt": "hello", "model": "haiku"}'
```

### Run All Tests

```bash
# Run all ABCD tests (all models, all tasks)
pytest admin/tests/swarms/test_abcd_coding.py -v -s

# This will:
# 1. Test 4 coding tasks × 3 models = 12 total tests
# 2. Save results to admin/tests/swarms/results/{model}/
# 3. Generate comparison summary at the end
```

### Run Specific Task

```bash
# Test only task 1 (Simple Sum)
pytest admin/tests/swarms/test_abcd_coding.py::TestABCDCoding::test_coding_task[task_1_simple_sum-haiku] -v -s

# Test only Sonnet model
pytest admin/tests/swarms/test_abcd_coding.py -k "sonnet" -v -s

# Test only functional tests (skip quality)
pytest admin/tests/swarms/test_abcd_coding.py::TestABCDCoding -v -s
```

### Generate Comparison Report

```bash
# After running all tests, generate summary
pytest admin/tests/swarms/test_abcd_coding.py::TestABCDSummary::test_generate_comparison_report -v -s
```

---

## Understanding Results

### Result Files

Each test generates a JSON file: `results/{model}/{task}_{model}.json`

```json
{
  "model": "sonnet",
  "task_name": "task_2_palindrome",
  "syntax_valid": true,
  "functional_pass": true,
  "quality_score": 0.75,
  "system_prompt_detected": true,
  "timestamp": "2026-02-22T10:30:45.123456",
  "code": "def is_palindrome(s: str) -> bool:\n    ..."
}
```

### Comparison Report

File: `results/ABCD_SUMMARY.json`

```json
{
  "haiku": {
    "syntax_rate": 0.75,
    "functional_rate": 0.50,
    "quality_avg": 0.42,
    "context_rate": 0.75,
    "total_tests": 4
  },
  "sonnet": {
    "syntax_rate": 1.00,
    "functional_rate": 1.00,
    "quality_avg": 0.72,
    "context_rate": 1.00,
    "total_tests": 4
  },
  "opus": {
    "syntax_rate": 1.00,
    "functional_rate": 1.00,
    "quality_avg": 0.81,
    "context_rate": 1.00,
    "total_tests": 4
  }
}
```

### Interpreting Metrics

**Syntax Rate**: Percentage of responses with valid Python
- ✅ 100% = All models produce syntactically correct code
- ⚠️ 75% = 1 in 4 responses has syntax errors
- ❌ <50% = Model struggles with syntax

**Functional Rate**: Percentage passing the test suite
- ✅ 100% = All code passes all test cases
- ⚠️ 75% = 1 in 4 fails at least one test
- ❌ <50% = Model produces non-functional code

**Quality Avg**: Average quality score (0-1)
- ✅ >0.7 = Excellent (docstrings, types, tests, error handling)
- ⚠️ 0.4-0.7 = Fair (some structure, incomplete evidence)
- ❌ <0.4 = Poor (minimal structure, no tests)

**Context Rate**: Percentage with detected system prompt
- ✅ 100% = System prompt was applied to all requests
- ⚠️ 75% = System prompt applied to 3 of 4 tests
- ❌ 0% = System prompt not detected (verify HTTP wrapper!)

---

## Model Comparison Example

### Hypothetical Results

| Metric | Haiku | Sonnet | Opus |
|--------|-------|--------|------|
| Syntax Rate | 75% | 100% | 100% |
| Functional Rate | 50% | 100% | 100% |
| Quality Avg | 0.42 | 0.72 | 0.81 |
| Context Rate | 75% | 100% | 100% |

**Interpretation**:
1. **Haiku struggles** with functional correctness (50%) but cheaper
2. **Sonnet is sweet spot** - 100% functional, 0.72 quality (good for most tasks)
3. **Opus is best** - 100% functional, 0.81 quality (pay premium for higher quality)
4. **Context injection working** on all models except some haiku tests

**Uplift Calculation**:
```
Sonnet vs Haiku uplift = (Sonnet.functional - Haiku.functional) / Haiku.functional
                       = (100% - 50%) / 50%
                       = 100% improvement ← worth the extra cost

Quality improvement = (0.72 - 0.42) / 0.42
                    = 71% quality improvement
```

---

## Debugging Failed Tests

### Issue: Context Not Detected (context_rate = 0%)

**Check 1**: Is the wrapper running?
```bash
curl http://localhost:8080/api/generate -X POST \
  -H "Content-Type: application/json" \
  -d '{"prompt": "hello", "model": "haiku"}'
```

**Check 2**: Is the system prompt being sent?
```bash
# Add debug logging to test to print response
# Look for "## SKILL:" or "prime-coder" in response
```

**Check 3**: Verify wrapper supports system prompt
```python
# In cli/src/claude_code_wrapper.py, check:
# - Does POST /api/generate accept "system" parameter?
# - Does wrapper prepend system to prompt?
```

### Issue: Syntax Errors

**Check 1**: Is the code block extracted correctly?
```python
# Look for ```python markers in response
# If missing, whole response used as code
```

**Check 2**: Model generating invalid Python
```bash
# Run specific task with verbose output:
pytest admin/tests/swarms/test_abcd_coding.py::TestABCDCoding::test_coding_task[task_1_simple_sum-haiku] -v -s

# Check "Code Response" output for malformed code
```

### Issue: Functional Tests Failing

**Check 1**: Validation code is correct
```python
# Ensure CODING_TASKS[task_key]["validation_code"] is valid Python
```

**Check 2**: Model-generated function has wrong name
```python
# E.g., function named `sum_list()` instead of `sum_integers()`
# Model might have slightly different interpretation
```

### Issue: Quality Score Too Low

**Check 1**: Missing docstrings
```python
def function_name(args):  # ❌ No docstring
    pass

def function_name(args):
    """This is a docstring."""  # ✅ Has docstring
    pass
```

**Check 2**: Missing type hints
```python
def function_name(args):  # ❌ No type hints
    return result

def function_name(args: list) -> int:  # ✅ Has type hints
    return result
```

**Check 3**: No error handling
```python
def function_name(items):
    return sum(items)  # ❌ No error handling

def function_name(items):
    try:
        return sum(items)
    except TypeError:
        return 0  # ✅ Error handling
```

---

## Extending ABCD Tests

### Add New Coding Task

1. Add to `CODING_TASKS` dictionary in `test_abcd_coding.py`:

```python
CODING_TASKS = {
    ...
    "task_5_json_parser": {
        "name": "JSON Parser",
        "prompt": """Write a function that parses JSON...""",
        "validation_code": """
def test_json_parser():
    assert json_parser('{"a": 1}') == {"a": 1}
    ...
test_json_parser()
print("PASS: json_parser works")
""",
    },
}
```

2. Tests automatically pick up new task
3. Run: `pytest admin/tests/swarms/test_abcd_coding.py -v -s`

### Add New Model

Edit `MODELS` list in `TestABCDCoding`:

```python
class TestABCDCoding:
    MODELS = ["haiku", "sonnet", "opus", "custom_model"]  # Add new model
```

### Add New Quality Metric

Edit `calculate_code_quality_score()` function:

```python
def calculate_code_quality_score(code: str, test_output: str = "") -> float:
    score = 0.0

    # ... existing metrics ...

    # Add new metric: uses f-strings (+0.1)
    if 'f"' in code or "f'" in code:
        score += 0.1

    return min(1.0, max(0.0, score))
```

---

## See Also

- `test_swarms_improved.py` — Basic A|B testing (all 34 swarms)
- `AB_TESTING.md` — A|B testing explanation
- `swarms/coder.md` — Prime-coder swarm definition
- `skills/prime-coder.md` — Prime-coder skill pack
- `SWARMS_ARCHITECTURE.md` — Context injection architecture
