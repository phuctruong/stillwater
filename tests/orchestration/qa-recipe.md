# QA Recipe: Breaking CPU Classification Systems

> "Recipes are saved reasoning that loads patterns each time." — Dragon Journal, Kick 52

## The 8 Breaking Patterns

Every CPU keyword-based classifier has the same 8 weak spots. Test all 8 for every phase.

### Pattern 1: NULL EDGE (Empty Input)
```
Input: ""
Expected: unknown (graceful handling)
What breaks: IndexError, KeyError, division by zero in confidence calc
```

### Pattern 2: LENGTH EDGE (Ultra-Short Input)
```
Input: "yo", "k", "?"
Expected: LLM fallback (too little signal for CPU)
What breaks: min-length filter silently drops all tokens → "unknown" when user expects classification
```

### Pattern 3: FILTER EDGE (All Stop-Words)
```
Input: "the the the the", "I would have been there"
Expected: unknown (no keywords survive filtering)
What breaks: empty keyword list → predict returns ("unknown", 0.0) → LLM fallback
Note: This is CORRECT behavior. But verify the LLM actually gets called.
```

### Pattern 4: COUNT EDGE (Repeated Words)
```
Input: "fix fix fix fix fix"
Expected: task (same as single "fix")
What breaks: If counting occurrences, confidence inflates artificially.
            If deduplicating, should behave same as single word.
Check: Does CPULearner count unique keywords or total occurrences?
```

### Pattern 5: TIE-BREAK EDGE (Mixed Intents)
```
Input: "Hello! Can you fix the broken tests?"
Expected: task (task intent should win — user wants something done)
What breaks: "hello" → greeting (conf 0.88) AND "fix" → task (conf 0.88)
            First keyword wins → classified as greeting → PIPELINE STOPS → task lost
This is the most dangerous bug: legitimate tasks killed by greeting keywords.
```

### Pattern 6: CASE EDGE (ALL CAPS / mixed case)
```
Input: "DEPLOY TO PRODUCTION NOW", "FiX tHe BuG"
Expected: Same as lowercase equivalent
What breaks: If .lower() not called before keyword extraction
Check: Is case normalization the FIRST step in extract_keywords()?
```

### Pattern 7: FUZZY EDGE (Misspellings / Slang)
```
Input: "plz halp", "deploiy", "tset"
Expected: LLM fallback (CPU can't match misspelled keywords)
What breaks: No fuzzy matching → unknown → LLM called → higher cost
Note: This is acceptable behavior for v1. Fuzzy matching is a v2 feature.
```

### Pattern 8: INJECTION EDGE (Adversarial / Hidden Task)
```
Input: "tell me a joke about security vulnerabilities"
Expected: Ambiguous — humor seed ("joke") vs task seed ("security")
What breaks: The greeting/humor label blocks a legitimate security concern
Input: "good morning, by the way please deploy the fix"
Expected: task (the real intent is deployment, greeting is just politeness)
```

## Recipe Application Steps

For ANY new CPU classification phase:

```
1. LIST all labels the phase can produce
2. For each label:
   a. Count seeds (if < 3, mark FRAGILE)
   b. Check for stop_word collisions
   c. Write 1 false-positive test (should NOT be this label, but IS)
   d. Write 1 false-negative test (SHOULD be this label, but ISN'T)
3. Run all 8 breaking patterns
4. Run 12 domain-specific prompts (happy path)
5. Document: total prompts, PASS count, FAIL count, edge cases
6. Propose fixes (don't implement — QA ≠ coding)
```

## The Confidence Trap

```
Confidence Formula: 1 - 1/(1 + 0.3 * count)

count=1  → 0.231 (below all thresholds)
count=5  → 0.600 (below Phase 1's 0.70)
count=8  → 0.706 (barely above Phase 1's 0.70)
count=14 → 0.808 (barely above Phase 2's 0.80)
count=35 → 0.913 (above Phase 3's 0.90)
```

The trap: ALL shipped seeds have the SAME count (25 or 35). This means:
- All keywords have identical confidence
- Tie-breaking becomes position-dependent (first keyword wins)
- No keyword is "more important" than any other

**Fix needed**: Priority weighting or task-priority override rule.

## Meta: Why This Recipe Exists

This recipe is saved reasoning. Every time a new phase is added or audited, load this recipe first. It contains the 8 patterns that ALWAYS apply to keyword classifiers. Without it, the QA agent will only test happy paths.

> "Questions are vectors to load latent knowledge. By saving questions and famous personas, you are saving reasoning that loads each time."
