# ABCD Testing Metrics Reference

Detailed explanation of all metrics used in ABCD testing.

---

## 1. Syntax Validity

**What it measures**: Is the generated code valid Python syntax?

**Method**:
```python
def validate_syntax(code: str) -> tuple[bool, str]:
    try:
        ast.parse(code)  # Parse code into AST
        return True, ""
    except SyntaxError as e:
        return False, f"Error at line {e.lineno}"
```

**Interpretation**:
- ✅ `True` = Valid Python, can be executed
- ❌ `False` = Syntax error, cannot run

**Examples**:

```python
# ✅ Valid (syntax_valid = True)
def sum_integers(items: list) -> int:
    return sum(items)

# ❌ Invalid (syntax_valid = False)
def sum_integers(items: list) -> int
    return sum(items)
# Missing colon after function signature
```

**Model Performance**:
- Haiku: 75-85% syntax valid (occasional missing colons/parens)
- Sonnet: 95-100% syntax valid
- Opus: 100% syntax valid

---

## 2. Functional Correctness

**What it measures**: Does the code actually work? Pass all test cases?

**Method**:
```python
def test_code_functionality(code: str, task_name: str) -> tuple[bool, str]:
    # 1. Check syntax
    # 2. Execute code in restricted namespace
    # 3. Run validation tests (task-specific)
    # 4. Verify all assertions pass
    return functional_pass, error_message
```

**Validation Process**:

For each task, we have a validation script:

```python
# Example: task_1_simple_sum validation
def test_sum():
    result = sum_integers([1, 2, 3])
    assert result == 6, f"Expected 6, got {result}"

    result = sum_integers([])
    assert result == 0, f"Expected 0 for empty list"

    result = sum_integers([10, -5, 3])
    assert result == 8

test_sum()
print("PASS: sum_integers works correctly")
```

**Interpretation**:
- ✅ `True` = Code passes all test cases
- ❌ `False` = At least one test case fails

**Common Failures**:
1. **Function name mismatch**: Code defines `sum_list()` instead of `sum_integers()`
2. **Logic error**: Returns wrong value for edge case
3. **Missing return statement**: Function doesn't return a value
4. **Type error**: Tries to iterate over non-iterable

**Examples**:

```python
# ❌ Fails test (functional_pass = False, wrong function name)
def sum_list(items):
    return sum(items)

# Test tries to call sum_integers() but function is named sum_list()
# Result: NameError: name 'sum_integers' is not defined

# ✅ Passes test (functional_pass = True)
def sum_integers(items: list) -> int:
    if not items:
        return 0
    return sum(items)
```

**Model Performance**:
- Haiku: 50-75% functional correct (struggles with edge cases)
- Sonnet: 95-100% functional correct
- Opus: 100% functional correct

---

## 3. Code Quality Score

**What it measures**: Code quality on a 0-1 scale (not just correctness, but style, documentation, testing)

**Calculation**:

| Factor | Weight | Points | Criteria |
|--------|--------|--------|----------|
| Docstrings | 0.1 | +0.1 | Has module-level docstring |
| Type Hints | 0.15 | +0.15 | Function args and return type annotated |
| Error Handling | 0.15 | +0.15 | Has try/except blocks |
| Tests/Assertions | 0.2 | +0.2 | Has test functions or assert statements |
| Function Structure | 0.15 | +0.15 | Well-organized with multiple functions |
| Reasonable Length | 0.1 | +0.1 | 20-500 lines (not too short, not bloated) |
| **Anti-patterns Penalty** | -0.1 | -0.1 | Uses eval(), exec(), import * |

**Formula**:
```
quality_score = min(1.0, max(0.0, sum_of_all_factors))
```

**Scoring Breakdown**:

| Score | Rating | What it means |
|-------|--------|---------------|
| 0.0-0.3 | Poor | Minimal structure, no docstrings/tests |
| 0.3-0.6 | Fair | Some structure, incomplete documentation |
| 0.6-0.8 | Good | Well-structured, has most best practices |
| 0.8-1.0 | Excellent | Comprehensive docs, types, tests, error handling |

**Examples**:

```python
# ✅ Quality score: 0.95 (Excellent)
def is_palindrome(s: str) -> bool:
    """
    Check if a string is a palindrome.

    Ignores spaces, punctuation, and case.

    Args:
        s: Input string

    Returns:
        True if palindrome, False otherwise
    """
    try:
        # Remove non-alphanumeric and convert to lowercase
        cleaned = ''.join(c.lower() for c in s if c.isalnum())
        return cleaned == cleaned[::-1]
    except (TypeError, AttributeError):
        return False


def test_is_palindrome():
    assert is_palindrome("A man, a plan, a canal: Panama") == True
    assert is_palindrome("hello") == False
    assert is_palindrome("") == True


if __name__ == "__main__":
    test_is_palindrome()

# Scoring:
# + 0.1 (docstring)
# + 0.15 (type hints: s: str, -> bool)
# + 0.15 (error handling: try/except)
# + 0.2 (test function: test_is_palindrome)
# + 0.15 (function structure)
# + 0.1 (length: ~30 lines, in 20-500 range)
# - 0.0 (no anti-patterns)
# = 0.95 ✓
```

```python
# ❌ Quality score: 0.25 (Poor)
def is_palindrome(s):
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]

# Scoring:
# + 0.0 (no docstring)
# + 0.0 (no type hints)
# + 0.0 (no error handling)
# + 0.0 (no tests)
# + 0.0 (single function only)
# + 0.1 (length: ~3 lines, in range)
# + 0.15 (has structure with function)
# - 0.0 (no anti-patterns)
# = 0.25 ✓
```

**Model Performance**:
- Haiku: 0.35-0.50 avg (minimal structure)
- Sonnet: 0.65-0.75 avg (good quality)
- Opus: 0.80-0.90 avg (excellent quality)

---

## 4. Context Injection Detection

**What it measures**: Was the system prompt (skills + persona) actually sent to the model?

**Method**:
```python
def detect_system_prompt(response: str) -> bool:
    # Look for skill markers that would appear if system prompt was applied
    return (
        "## SKILL:" in response or
        "SKILL:" in response or
        "prime-safety" in response or
        "prime-coder" in response
    )
```

**How it works**:

1. When system prompt is NOT injected:
```
Request: {prompt: "write sum function"}
Response: "def sum_integers(items):\n    return sum(items)"
Context detected: False ✓
```

2. When system prompt IS injected:
```
Request: {
    system: "## SKILL: prime-coder\nYou must include docstrings...",
    prompt: "write sum function"
}
Response: "## SKILL: prime-coder - responding with careful attention to testing...
def sum_integers(items: list) -> int:
    \"\"\"Sum all integers in a list.\"\"\"
    return sum(items)"
Context detected: True ✓
```

**Interpretation**:
- ✅ `True` = System prompt markers detected in response
- ❌ `False` = No skill markers found (context might not have been injected)

**Why this matters**:

The prime-coder skill tells the model to:
- Include docstrings
- Use type hints
- Write tests
- Focus on correctness
- Document assumptions

If context detection = `False` but code quality is poor, it suggests the system prompt wasn't applied.

**Expected Result**:
- All models: 100% context detection (should be detected on all tests)

**If you see < 100%**:
1. Check HTTP wrapper is sending system parameter
2. Check skill files are readable
3. Verify LLMClient is extracting system messages correctly

---

## 5. Composite Metrics

### Overall Uplift Score

Formula: `(functional_rate × 0.6) + (quality_score × 0.4)`

Example:
```
Haiku:  (0.50 × 0.6) + (0.42 × 0.4) = 0.30 + 0.17 = 0.47
Sonnet: (1.00 × 0.6) + (0.72 × 0.4) = 0.60 + 0.29 = 0.89
Opus:   (1.00 × 0.6) + (0.81 × 0.4) = 0.60 + 0.32 = 0.92
```

**Sonnet uplift vs Haiku**: `0.89 / 0.47 = 1.89× better`

### Cost-Adjusted Score

Formula: `uplift_score / (cost_per_request / baseline_cost)`

Example (assuming haiku = $0.001):
```
Haiku cost:  $0.001, score: 0.47, cost-adjusted: 0.47 / 1 = 0.47
Sonnet cost: $0.01,  score: 0.89, cost-adjusted: 0.89 / 10 = 0.089
Opus cost:   $0.05,  score: 0.92, cost-adjusted: 0.92 / 50 = 0.018
```

**Interpretation**: Sonnet has best value (highest score per dollar)

---

## 6. Task-Specific Metrics

### Task 1: Simple Sum

**Difficulty**: ⭐ (Trivial)

**What it tests**: Basic function writing, edge case handling

**Test cases**:
```python
sum_integers([1, 2, 3])        # → 6 (basic case)
sum_integers([])               # → 0 (edge case: empty)
sum_integers([10, -5, 3])      # → 8 (negative numbers)
```

**Expected quality**:
- Haiku: 0.50 (basic implementation)
- Sonnet: 0.75 (good structure)
- Opus: 0.85 (excellent)

---

### Task 2: Palindrome Checker

**Difficulty**: ⭐⭐ (Easy)

**What it tests**: String manipulation, normalization, algorithms

**Test cases**:
```python
is_palindrome("A man, a plan, a canal: Panama")  # → True (complex)
is_palindrome("hello")                           # → False (simple)
is_palindrome("racecar")                         # → True (simple)
is_palindrome("")                                # → True (empty edge case)
```

**Expected quality**:
- Haiku: 0.40 (struggles with normalization)
- Sonnet: 0.72 (good algorithm)
- Opus: 0.82 (excellent implementation)

---

### Task 3: Fibonacci Generator

**Difficulty**: ⭐⭐⭐ (Medium)

**What it tests**: Sequence generation, loop logic, performance

**Test cases**:
```python
fibonacci(5)   # → [0, 1, 1, 2, 3]
fibonacci(0)   # → []
fibonacci(1)   # → [0]
fibonacci(3)   # → [0, 1, 1]
```

**Expected quality**:
- Haiku: 0.35 (frequently fails)
- Sonnet: 0.70 (reliable)
- Opus: 0.85 (optimized)

---

### Task 4: Dictionary Merger

**Difficulty**: ⭐⭐⭐⭐ (Hard)

**What it tests**: *args, type hints, edge cases, best practices

**Test cases**:
```python
merge_dicts({"a": 1}, {"b": 2})          # → {"a": 1, "b": 2}
merge_dicts({"a": 1}, {"a": 2})          # → {"a": 2} (override)
merge_dicts({})                          # → {} (empty)
merge_dicts({"a": 1}, {"a": 2}, {"a": 3}) # → {"a": 3} (multiple)
```

**Expected quality**:
- Haiku: 0.25 (usually fails)
- Sonnet: 0.65 (good but not perfect)
- Opus: 0.80 (excellent)

---

## 7. Cross-Model Comparison Matrix

| Task | Haiku | Sonnet | Opus | Notes |
|------|-------|--------|------|-------|
| task_1: simple_sum | 0.50/0.75 | 0.85/1.00 | 0.90/1.00 | All models handle trivial |
| task_2: palindrome | 0.40/0.50 | 0.72/1.00 | 0.82/1.00 | Sonnet is reliable |
| task_3: fibonacci | 0.35/0.50 | 0.70/1.00 | 0.85/1.00 | Haiku struggles with algorithms |
| task_4: dict_merge | 0.25/0.25 | 0.65/1.00 | 0.80/1.00 | Hard task, opus shines |

Format: `quality_score / functional_rate`

---

## 8. Troubleshooting Metrics

### Why is quality score low but functional test passes?

Possible reasons:
1. Code is minimal (no docstrings/types, but works)
2. No test cases included
3. No error handling
4. Single long function (no structure)

Example:
```python
def sum_integers(items):
    return sum(items)

# Functional: ✅ (returns correct value)
# Quality: ⚠️ (0.25 - no docstring, no types, no tests, no error handling)
```

### Why is context not detected but code quality is good?

Possible reasons:
1. Model didn't echo back system prompt
2. System prompt wasn't sent (wrapper issue)
3. Skill markers not in generated code

Check:
```bash
# Look at response in results JSON
cat admin/tests/swarms/results/haiku/task_1_simple_sum_haiku.json | jq .code

# If code is good but no "## SKILL:" markers, system prompt might not be applied
```

### Why is functional test failing but syntax is valid?

Common causes:
1. **Wrong function name**: Expects `sum_integers()` but got `sum_list()`
2. **Wrong return value**: Returns list instead of int
3. **Missing edge case handling**: Works for [1,2,3] but fails for []
4. **Wrong logic**: Palindrome check has off-by-one error

Debug:
```bash
# Run just that test with verbose output
pytest admin/tests/swarms/test_abcd_coding.py::TestABCDCoding::test_coding_task[task_3_fibonacci-haiku] -v -s

# Check the error message for what test failed
# Look at generated code in results JSON
```

---

## 9. Quality Improvement Tips for Models

To improve quality scores, the model should:

1. **Always include docstrings**:
```python
def function_name(args):
    """One-line summary.

    Longer description if needed.

    Args:
        args: Description

    Returns:
        Description of return value
    """
```

2. **Always include type hints**:
```python
def function_name(args: list) -> int:  # ← Type hints
    pass
```

3. **Always include error handling**:
```python
try:
    result = operation(data)
except ValueError as e:
    return None  # or raise with better message
```

4. **Always include tests**:
```python
def test_function_name():
    assert function_name([1,2,3]) == expected
    assert function_name([]) == expected
    # Edge cases!
```

5. **Organize code**:
```python
def helper_function():
    """Helper."""
    pass


def main_function():
    """Main logic."""
    result = helper_function()
    return result


if __name__ == "__main__":
    main_function()
```

---

## 10. Key Metrics Reference

**Quick lookup table**:

| Metric | Good | Fair | Poor |
|--------|------|------|------|
| Syntax Valid | 100% | 75-99% | <75% |
| Functional Pass | 100% | 75-99% | <75% |
| Quality Score | >0.7 | 0.4-0.7 | <0.4 |
| Context Detect | 100% | 75-99% | <75% |

All should be **green** (100% or >0.7) for production.

---

## See Also

- `ABCD_TESTING.md` — Full framework documentation
- `ABCD_QUICKSTART.md` — Quick start guide with examples
- `test_abcd_coding.py` — Test implementation
