# Swarms A|B Testing Guide

Auth: 65537 | Version: 2.0.0

## Overview

A|B testing in Stillwater swarms means testing swarms with different inputs/conditions to understand their behavior and effectiveness.

---

## Testing Approaches

### 1. **Prompt Variant A|B** (Current Implementation)

**What it tests:**
- Same swarm with different prompt types
- Factual prompts (A) vs domain-specific prompts (B)

**Example:**
```
Swarm: coder
Model: haiku
Temperature: 0.0

Variant A: "What is the capital of France?"
Variant B: "Design a REST API endpoint for user registration"
```

**Metrics Captured:**
- Response length (characters)
- Latency (milliseconds)
- Response presence (not empty)
- Quality score (heuristic)

**What it tells you:**
- Can the swarm handle both simple and complex prompts?
- Does domain-specific context improve responses?
- Are responses reasonable length?

**Current test output:**
```
✓ coder (a): 156 chars, 2345ms
✓ coder (b): 234 chars, 3121ms
```

---

### 2. **Persona Variant A|B** (Improved)

**What it tests:**
- Same swarm WITH persona vs WITHOUT persona

**Example:**
```
Swarm: coder
Prompt: "What is the capital of France?"

Variant A (with persona):
  Skills: prime-safety, prime-coder, persona-engine
  Persona: Donald Knuth

Variant B (without persona):
  Skills: prime-safety, prime-coder
  (no persona)
```

**Metrics:**
- Response length delta
- Consistency score (similarity between A & B)
- Quality impact of persona

**What it tells you:**
- Does the persona actually change the response?
- Does persona improve or degrade response quality?
- Is the persona's influence noticeable?

**Sample output:**
```
coder - Persona Impact:
  With persona:     234 chars
  Without persona:  198 chars
  Similarity:       0.65 (65% similar)
  → Persona adds ~36 chars of differentiation
```

---

### 3. **Temperature Variant A|B** (Consistency Test)

**What it tests:**
- Deterministic (temperature=0) vs creative (temperature=0.5)

**Example:**
```
Swarm: coder
Prompt: "What is the capital of France?"

Variant A: temperature=0.0
  → Should be deterministic (same prompt = same response)

Variant B: temperature=0.5
  → Should be more creative/variable
```

**Metrics:**
- Consistency score (Levenshtein similarity)
- Response length variance
- Latency variance

**What it tells you:**
- Is temperature=0 truly deterministic?
- How much does temperature affect output?
- Is the swarm predictable?

**Sample output:**
```
coder - Temperature Consistency:
  Temperature=0:    234 chars
  Temperature=0.5:  267 chars
  Consistency:      0.78 (78% similar)
  → Temperature=0 is fairly deterministic (>0.7 = good)
```

---

### 4. **Skill Subset A|B** (Potential Future)

**What it would test:**
- Full skill pack vs minimal skill pack

**Example:**
```
Swarm: coder

Variant A (full):
  Skills: prime-safety, prime-coder, persona-engine

Variant B (minimal):
  Skills: prime-safety only
```

**Metrics:**
- Quality impact per skill
- Latency impact per skill
- Necessity analysis (which skills matter most?)

**What it tells you:**
- Which skills are essential?
- Which skills provide marginal value?
- Can we optimize for faster response?

---

## Quality Scoring

The improved tests use a heuristic quality score (0-1):

```python
def calculate_quality_score(response: str) -> float:
    score = 0.0

    # Length score (optimal 100-500 chars)
    if 100 <= length <= 500:
        score += 0.3

    # Structure (has paragraphs, lists, code)
    if "\n" in response:
        score += 0.15
    if "```" in response or "- " in response:
        score += 0.15

    # No error keywords
    if "error" not in response.lower():
        score += 0.2

    # Complete sentences
    if response.endswith((".","!","?")) or response.endswith(")"):
        score += 0.15

    return min(1.0, score)
```

**Scoring breakdown:**
- 0.0-0.3: Poor (empty, error, nonsense)
- 0.3-0.6: Fair (some structure, but incomplete)
- 0.6-0.8: Good (well-formed, reasonable)
- 0.8-1.0: Excellent (complete, well-structured)

---

## Consistency Scoring

For temperature tests, we use word-level similarity:

```python
def consistency_score(response_a: str, response_b: str) -> float:
    a_words = set(response_a.lower().split())
    b_words = set(response_b.lower().split())

    intersection = len(a_words & b_words)
    union = len(a_words | b_words)

    return intersection / union  # Jaccard similarity
```

**Interpretation:**
- 1.0 = Identical responses (perfectly deterministic)
- 0.7-1.0 = High consistency (good for temperature=0)
- 0.5-0.7 = Moderate consistency (expected at temperature=0.5)
- <0.5 = Low consistency (responses very different)

---

## Test Files

### Basic Testing (Current)
**File**: `test_swarms.py`

**Coverage:**
- 34 swarms × 2 prompt variants = 68 tests
- Metadata validation (100+ tests)
- Simple quality checks

**Run:**
```bash
pytest admin/tests/swarms/test_swarms.py -v
```

### Improved A|B Testing (New)
**File**: `test_swarms_improved.py`

**Coverage:**
- Prompt variants (all 34 swarms)
- Temperature consistency (first 5 swarms)
- Persona impact (first 3 swarms)
- Quality metrics on all tests

**Run:**
```bash
pytest admin/tests/swarms/test_swarms_improved.py -v -s
```

---

## Example Output

### Prompt Variant Test
```
coder - Prompt Variants:
  A (factual):      156 chars, 2345ms, quality=0.72
  B (domain):       234 chars, 3121ms, quality=0.85
  Length delta:     +78 chars
  Latency delta:    +776ms
  Winner:           B (longer + higher quality)
```

### Persona Impact Test
```
coder - Persona Impact:
  With persona:     234 chars
  Without persona:  198 chars
  Similarity:       0.65 (65% similar)
  → Persona adds style differentiation
```

### Temperature Consistency Test
```
coder - Temperature Consistency:
  Temperature=0:    234 chars
  Temperature=0.5:  267 chars
  Consistency:      0.78 (78% similar)
  ✓ Good determinism at temperature=0 (>0.7)
```

---

## What to Look For

### Green Signals ✅
- Quality scores 0.7+
- Prompt B longer than A (domain context expands response)
- Consistency >0.7 for temperature=0 tests
- Persona adds 30-100 chars of differentiation

### Yellow Signals ⚠️
- Quality scores 0.5-0.7 (fair but not great)
- Prompt B shorter than A (swarm might not handle complexity well)
- Consistency 0.5-0.7 for temperature=0 (less deterministic than expected)
- Persona adds <20 chars (minimal impact)

### Red Signals 🔴
- Quality scores <0.5 (poor output)
- Both variants return error messages
- Consistency <0.3 for temperature=0 (not deterministic at all)
- Persona removes quality (similarity close to 1.0 but worse quality)

---

## Extending A|B Tests

### Add New Prompt Variants
```python
PROMPTS = {
    "a": "What is the capital of France?",
    "b": "Design a REST API endpoint...",
    "c": "Write Python code for...",  # New variant
    "d": "Explain quantum computing...", # New variant
}
```

### Add New Quality Metrics
```python
def calculate_quality_score(response: str) -> float:
    score = 0.0

    # Existing metrics...

    # Add new metric: code blocks
    if "```python" in response:
        score += 0.1

    # Add new metric: clarity/readability
    avg_line_length = sum(len(l) for l in response.split("\n")) / max(1, len(response.split("\n")))
    if 30 <= avg_line_length <= 80:
        score += 0.1

    return min(1.0, score)
```

### Add New Consistency Tests
```python
class TestSkillSubsetImpact:
    """Test full skill pack vs minimal."""

    def test_skill_impact(self, swarm_name, llm_client):
        # Variant A: all skills
        # Variant B: prime-safety only
        # Compare quality, latency, length
```

---

## Best Practices

1. **Keep prompts realistic**: Use prompts that actual users would ask
2. **Test in isolation**: One variable at a time (prompt, temperature, persona)
3. **Measure consistently**: Same max_tokens, same model (haiku), same timeout
4. **Look at patterns**: Single test means little; run full suite for trends
5. **Document findings**: Note when a swarm surprises you

---

## Running Full A|B Suite

```bash
# Run all prompt variant tests
pytest test_swarms_improved.py::TestPromptVariants -v

# Run all temperature consistency tests
pytest test_swarms_improved.py::TestTemperatureConsistency -v

# Run all persona impact tests
pytest test_swarms_improved.py::TestPersonaImpact -v

# Run everything with output
pytest test_swarms_improved.py -v -s --tb=short
```

---

## Interpreting Results

**Q: Why is Prompt B longer?**
A: Domain-specific context typically generates longer responses. This is expected and good.

**Q: Why is consistency <0.7 for temperature=0?**
A: Possible issues:
- LLM is not fully deterministic (haiku behavior variance)
- Skill pack has non-deterministic elements
- Persona is adding variability
- Network/timing issues

**Q: Why does persona hurt quality?**
A: Sometimes personas are too specific and constrain responses unnaturally.

**Q: Should I run tests at higher temperatures?**
A: Not for unit tests. Use temperature=0 for determinism. Higher temps = integration tests.

---

## See Also
- `test_swarms.py` - Basic unit tests
- `test_swarms_improved.py` - Advanced A|B tests
- `run_tests.sh` - Test runner script
