# Phase 1 Small Talk -- Test Results Summary

**Date**: 2026-02-24
**Engine**: TripleTwinEngine (CPU-only, no LLM)
**Threshold**: 0.70
**Seeds**: 49 keywords (43 task + 6 non-task) in `data/default/seeds/small-talk-seeds.jsonl`
**Confidence formula**: `1 - 1/(1 + 0.3 * count)` -- all seeds have count=25 -> conf=0.8824
**Responses DB**: `data/default/smalltalk/responses.jsonl` + `jokes.json` + `facts.json`
**Simulation file**: `simulation-run-2026-02-24.jsonl` (40 entries)

---

## Results Overview

| Category         | Total | CPU Match | Low-Conf Fallback | Phase 2 Route | Verdict Breakdown                    |
|------------------|-------|-----------|--------------------|---------------|--------------------------------------|
| Greeting         | 8     | 2         | 6                  | 0             | 2 PASS, 2 FAIL-GAP, 4 PASS-EDGE     |
| Gratitude        | 5     | 1         | 4                  | 0             | 1 PASS, 2 FAIL-GAP, 2 PASS-EDGE     |
| Task             | 5     | 5         | 0                  | 5             | 5 PASS                               |
| Emotional+       | 5     | 1         | 4                  | 0             | 1 PASS, 2 FAIL-GAP, 2 PASS-EDGE     |
| Emotional-       | 5     | 1         | 4                  | 1             | 1 FAIL-GAP, 4 PASS-EDGE             |
| Humor            | 4     | 1         | 3                  | 0             | 1 PASS, 3 FAIL-GAP                   |
| Mixed (bugs)     | 4     | 4         | 0                  | 0             | 4 FAIL-BUG                           |
| Edge cases       | 4     | 0         | 4                  | 0             | 4 PASS-EDGE                          |
| **Total**        | **40**| **15**    | **25**             | **6**         | **10 PASS, 10 FAIL-GAP, 4 FAIL-BUG, 16 PASS-EDGE** |

### Verdict Legend

| Verdict    | Meaning                                                                          |
|------------|----------------------------------------------------------------------------------|
| PASS       | Correct classification, correct routing, no issues                               |
| PASS-EDGE  | Correct for the engine's current design, but input is an edge case               |
| FAIL-GAP   | Incorrect due to missing seeds (coverage gap in `small-talk-seeds.jsonl`)        |
| FAIL-BUG   | Incorrect due to `BUG-P1-001` first-keyword-wins tie-break behavior              |

---

## Architecture Diagram

```
User Input
  |
  v
[Phase 1: Small Talk Twin]
  |
  +-- Keyword Extraction
  |     +-- text.lower()
  |     +-- regex [a-z]+ splits on non-alpha
  |     +-- filter: remove 89 stop words
  |     +-- filter: remove words with len < 3
  |     +-- deduplicate (preserve order)
  |
  +-- CPU Prediction (CPULearner.predict)
  |     +-- iterate keywords in extraction order
  |     +-- lookup each in seeds/learned patterns
  |     +-- track best_label = first keyword with highest confidence
  |     +-- BUG: equal-confidence keywords do NOT update best_label
  |
  +-- Confidence Gate (threshold = 0.70)
  |
  +-- CPU Match (confidence >= 0.70)
  |     +-- label = task --> Continue to Phase 2 (intent twin)
  |     +-- label = non-task --> Select response from smalltalk/responses.jsonl
  |           +-- Return warm_token immediately
  |           +-- No LLM cost
  |
  +-- Low Confidence (confidence < 0.70 or 0.0)
  |     +-- Serve joke from jokes.json   <-- "gifts that uplift"
  |     +-- OR serve fact from facts.json
  |     +-- OR serve heuristic response from responses.jsonl
  |     +-- Return immediately (still CPU, no LLM)
  |
  +-- [Background: LLM Enrichment] (not active in this simulation)
        +-- LLM (Haiku) classifies in parallel
        +-- Generates improved response
        +-- Saves to learned_small_talk.jsonl for NEXT turn (not current)
        +-- LEAK protocol: LLM teaches CPU new patterns
```

---

## Key Insights

### 1. Seed Coverage is Narrow (6 non-task seeds for 8 labels)

The seed file has **49 keywords** but **43 are task-related**. Only 6 non-task seeds exist:
- `hello` (greeting)
- `thanks` (gratitude)
- `happy` (emotional_positive)
- `sad` (emotional_negative)
- `joke` (humor)
- `weather` (small_talk)

This means common variations like "hey", "morning", "thank", "awesome", "frustrated", "lol", "haha", "funny" all fall to unknown (conf=0.0). The cpu-node doc (`small-talk.md`) lists these words in keyword groups, but they were never added to the JSONL seed file.

**Impact**: 10 of 40 inputs (25%) are FAIL-GAP due to missing seeds.

### 2. Task Classification is Robust

All 5 pure task inputs were correctly classified and routed to Phase 2. Task seeds cover the most important verbs: fix, deploy, write, refactor, test, build, create, add, help, review, etc. The task pipeline works well for single-intent inputs.

### 3. Edge Cases Degrade Gracefully

All 4 edge cases (empty string, all stop words, numeric, punctuation) correctly fall to unknown with conf=0.0. No crashes, no errors. The regex `[a-z]+` and stop word filter handle degenerate inputs cleanly.

### 4. First-Keyword-Wins Bug Affects Multi-Intent Inputs

The `CPULearner.predict()` method has a critical bug (BUG-P1-001) where equal-confidence keywords do not update `best_label`. Since all seeds share count=25 / conf=0.8824, the first keyword in extraction order always wins. This causes 4 FAIL-BUG results where task intents are lost.

### 5. "help" is Classified as Task (Semantic Mismatch)

Input "help!!!" routes to Phase 2 as a task because "help" has a task seed. But emotionally, "help!!!" is a distress call that should receive an empathetic response before routing. This is a semantic gap in the label taxonomy.

### 6. Apostrophe Splitting Creates Unexpected Tokens

"doesn't" becomes ["doesn", "t"] because regex `[a-z]+` splits on the apostrophe. "I'm" becomes ["i", "m"]. The contraction handling is a known limitation of the simple regex tokenizer.

---

## Known Bugs Demonstrated

### BUG-P1-001: First-Keyword-Wins Tie-Break

**Affected**: sim_033, sim_034, sim_035, sim_036 (4 inputs)

**Root cause**: In `CPULearner.predict()`, the iteration loop:
```python
for kw in keywords:
    if conf > best_conf:
        best_conf = conf
        best_label = self._patterns[kw]["label"]
    elif conf == best_conf and best_label is not None:
        matched.append(kw)  # appends but does NOT update best_label
```

When two keywords have equal confidence (which is always the case with count=25 seeds), the first one encountered sets `best_label` permanently. Subsequent equal-confidence keywords are added to `matched[]` but the label never changes.

**Impact**: HIGH -- any multi-intent message starting with politeness (greeting, thanks, joke) will swallow the task intent. The task never reaches Phase 2.

**Recommended fixes** (in priority order):
1. **Task-priority override**: If ANY keyword maps to `task`, classify as `task` regardless of order
2. **Label vote counting**: Count keywords per label, majority wins
3. **Multi-label output**: Return all detected labels, let the pipeline decide routing
4. **Weighted priority map**: `task > greeting > gratitude > humor > small_talk > unknown`

### Coverage Gaps in Seeds

**Affected**: sim_003, sim_005, sim_010, sim_012, sim_020, sim_022, sim_024, sim_030, sim_031, sim_032 (10 inputs, 25% of total)

**Root cause**: The `small-talk-seeds.jsonl` only contains 6 non-task keywords, but the `small-talk.md` cpu-node documentation lists 30+ keywords across 9 label groups. The following keywords are documented but not seeded:

| Label              | Documented Keywords                                      | Seeded |
|--------------------|----------------------------------------------------------|--------|
| greeting           | hello, hi, hey, greetings, morning, evening              | hello  |
| gratitude          | thanks, thank, appreciate, grateful                      | thanks |
| emotional_positive | happy, excited, great, awesome, amazing, wonderful       | happy  |
| emotional_negative | sad, frustrated, angry, upset, annoyed, disappointed     | sad    |
| humor              | joke, funny, lol, haha, laugh, humor                     | joke   |
| small_talk         | weather, weekend, coffee, lunch, movie, music            | weather|

**Missing seed count**: ~24 keywords documented but not in JSONL.

---

## Fallback System Performance

When the CPU has no match (conf=0.0), the fallback system activates:

| Fallback Source                          | Count | Purpose                                      |
|------------------------------------------|-------|----------------------------------------------|
| `data/default/smalltalk/responses.jsonl` | 22    | Heuristic responses (emotion, presence, etc.)|
| `data/default/jokes.json`               | 2     | Gift-that-uplifts for unknown/low-conf input |
| `data/default/facts.json`               | 1     | Educational nugget for unknown input         |
| **Total fallback**                       | **25**| **62.5% of all inputs**                      |

The fallback system ensures no input goes unanswered, even when the CPU has zero confidence. The jokes and facts serve as "gifts that uplift" -- the user gets something useful even when classification fails.

---

## Summary Statistics

```
Total inputs tested:           40
CPU confident matches:         15  (37.5%)
Low-confidence fallbacks:      25  (62.5%)
Routed to Phase 2 (task):      6  (15.0%)
Handled at Phase 1:           34  (85.0%)
LLM calls:                     0  (0.0%)
Correct (PASS + PASS-EDGE):   26  (65.0%)
Coverage gaps (FAIL-GAP):     10  (25.0%)
Bug-caused failures:           4  (10.0%)
```

### By Handler

```
cpu (confident):       15 inputs  (37.5%)
cpu_fallback (low):    25 inputs  (62.5%)
llm:                    0 inputs  ( 0.0%)
```

### Token Cost

```
LLM tokens used:    0
CPU operations:    40
Estimated cost:    $0.00
```

Phase 1 small talk is entirely CPU-driven in this simulation. Zero LLM calls. The LEAK protocol (LLM teaching CPU) would activate on subsequent turns when the LLM enrichment background process runs, but that is not tested in this CPU-only simulation.

---

## Recommendations

1. **Add missing seeds**: Expand `small-talk-seeds.jsonl` with the ~24 keywords documented in `small-talk.md` but not seeded. This would increase CPU match rate from 35% to an estimated 70%+.

2. **Fix BUG-P1-001**: Implement task-priority override in `CPULearner.predict()` so that task intents are never swallowed by politeness prefixes.

3. **Add abbreviation map**: Map common abbreviations (thx->thanks, ty->thanks, lol->joke, plz->please, halp->help) to their seed equivalents before lookup.

4. **Add contraction handling**: Pre-process contractions (doesn't->does not, I'm->I am) before regex tokenization to avoid unexpected splits.

5. **Semantic "help" disambiguation**: Add a heuristic that distinguishes "help me with X" (task) from "help!!!" (distress). Possible approach: if "help" is the only keyword and input has exclamation marks, classify as emotional_negative first.

---

## Files in This Test Suite

| File | Purpose |
|------|---------|
| `simulation-run-2026-02-24.jsonl` | Full 40-input simulation trace (machine-readable) |
| `summary.md` | This file -- human-readable analysis |
| `custom-jokes-test.jsonl` | 10 custom jokes for fallback system testing |
| `custom-facts-test.jsonl` | 10 custom facts for fallback system testing |
