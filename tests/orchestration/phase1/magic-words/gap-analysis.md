# Phase 1 Magic Word Gap Analysis

**Date:** 2026-02-24
**Source code:** `src/cli/src/stillwater/cpu_learner.py` (CPULearner)
**Seed file:** `data/default/seeds/small-talk-seeds.jsonl` (49 seeds)
**Rung target:** 65537

---

## Section 1: Stop Words vs Seed Keywords

### CPULearner Stop Words (88 words)

The stop words are defined as a **set** (O(1) lookup) in `extract_keywords()` at lines 77-89 of `cpu_learner.py`:

```
a, an, the, is, it, in, on, at, to, for, of, and, or, but, not, with, by, from, as,
i, you, we, they, he, she, this, that, be, are, was, were, has, have, had, do, does, did,
will, would, can, could, should, may, might, me, my, your, our, their, its, if, so,
all, any, some, no, yes, just, like, about, what, how, when, where, why, who, which,
there, here, up, out, into, then, than, now, also, very, more, most, really, please,
im, ive, dont, cant, wont, isnt, wasnt
```

### Seed Keywords (49 keywords)

From `data/default/seeds/small-talk-seeds.jsonl`:

```
hello, thanks, happy, sad, joke, weather, fix, bug, deploy, test, add, create, feature,
security, optimize, performance, docs, refactor, plan, debug, review, research, help,
design, audit, integrate, browse, scrape, email, notify, data, analytics, pipeline,
content, article, blog, proof, theorem, calculate, ship, build, implement, write, run,
update, configure, send, process, prove
```

### Direct Collisions: ZERO

No seed keyword exactly matches any stop word. All 49 seeds survive stop-word filtering.

### Near-Miss Analysis

The following seed keywords are **close** to stop words or share roots with common stop words. While they survive filtering, they are ambiguity risks:

| Seed Keyword | Similar Stop Word / Risk | Risk Level |
|---|---|---|
| `add` | Common non-task usage: "I would add that..." | MEDIUM |
| `run` | Short, ambiguous: "in the long run" | MEDIUM |
| `help` | IntentCPU (Phase 2) DOES stop this word | HIGH |
| `send` | Short, could appear in non-task: "it sends a message" | LOW |
| `plan` | Could be reflective: "I plan to..." | LOW |
| `data` | Appears in non-task: "data shows that..." | MEDIUM |
| `process` | Noun vs verb ambiguity: "the process" vs "process data" | MEDIUM |
| `build` | Could be metaphorical: "build on that idea" | LOW |
| `write` | Could be non-task: "as I write this..." | LOW |
| `content` | Could be adjective: "I'm content with..." | MEDIUM |
| `ship` | Could be noun: "a ship at sea" | LOW |
| `update` | Could be noun: "give me an update" (still task-adjacent) | LOW |

### Cross-System Stop Word Conflict (CRITICAL)

**CPULearner** (Phase 1) and **IntentCPU** (Phase 2) use DIFFERENT stop word sets.

IntentCPU adds these words that CPULearner does NOT stop:

```
help, make, get, set, use, want, need, like, well, hi, hey, ok, okay,
between, into, through, during, before, after, above, below, down, off,
over, under, again, once, both, either, neither, own, same, too, am,
each, few, other, such, using, used
```

**Impact:** The seed keyword `help` is a valid trigger in CPULearner Phase 1 but is **stopped** by IntentCPU Phase 2. Any learned pattern relying on `help` will work in Phase 1 but silently fail in Phase 2. This is an architectural inconsistency.

### Length Filter (>= 3 characters)

All 49 seed keywords have length >= 3. The shortest seeds are:

| Keyword | Length | Risk |
|---|---|---|
| `fix` | 3 | Survives. Exact match required. |
| `bug` | 3 | Survives. Exact match required. |
| `run` | 3 | Survives. Exact match required. |
| `add` | 3 | Survives. Exact match required. |
| `sad` | 3 | Survives. Exact match required. |

No seed is at risk of the length filter.

---

## Section 2: Seed Coverage Matrix

### Label Distribution

| Label | Seed Count | Keywords | Health |
|---|---|---|---|
| `task` | 43 | fix, bug, deploy, test, add, create, feature, security, optimize, performance, docs, refactor, plan, debug, review, research, help, design, audit, integrate, browse, scrape, email, notify, data, analytics, pipeline, content, article, blog, proof, theorem, calculate, ship, build, implement, write, run, update, configure, send, process, prove | **OVER-REPRESENTED** |
| `greeting` | 1 | hello | **FRAGILE** |
| `gratitude` | 1 | thanks | **FRAGILE** |
| `emotional_positive` | 1 | happy | **FRAGILE** |
| `emotional_negative` | 1 | sad | **FRAGILE** |
| `humor` | 1 | joke | **FRAGILE** |
| `small_talk` | 1 | weather | **FRAGILE** |

### Health Ratings

- **DEAD** (0 seeds): None.
- **FRAGILE** (1-2 seeds): `greeting`, `gratitude`, `emotional_positive`, `emotional_negative`, `humor`, `small_talk` -- **ALL non-task labels are FRAGILE**.
- **OK** (3-5 seeds): None.
- **OVER-REPRESENTED** (>10 seeds): `task` with **43 seeds** (87.8% of all seeds).

### Diagnosis

The seed distribution is severely imbalanced:

1. **Task dominance**: 43 out of 49 seeds (87.8%) map to `task`. This creates a strong bias toward classifying any input with a recognizable keyword as a task.

2. **Non-task fragility**: Every non-task label has exactly ONE keyword. If that single keyword fails to match (e.g., user says "hi" instead of "hello", or "funny" instead of "joke"), the label has ZERO coverage and the system either misclassifies or falls through to LLM.

3. **Missing common synonyms**:
   - `greeting`: Missing `hi`, `hey`, `howdy`, `greetings`, `morning`, `afternoon`, `evening`, `goodnight`, `goodbye`, `bye`, `welcome`, `sup`, `yo`
   - `gratitude`: Missing `thank`, `grateful`, `appreciate`, `appreciated`, `cheers`, `thx`, `kudos`
   - `emotional_positive`: Missing `great`, `awesome`, `excellent`, `wonderful`, `fantastic`, `love`, `excited`, `amazing`, `glad`, `pleased`, `proud`
   - `emotional_negative`: Missing `angry`, `frustrated`, `upset`, `disappointed`, `annoyed`, `worried`, `stressed`, `tired`, `exhausted`, `confused`, `overwhelmed`
   - `humor`: Missing `funny`, `humor`, `laugh`, `hilarious`, `comedy`, `pun`, `meme`, `lol`
   - `small_talk`: Missing `weekend`, `holiday`, `vacation`, `coffee`, `lunch`, `morning`, `evening`, `traffic`, `commute`, `sleep`, `food`, `music`, `movie`, `sports`, `news`

4. **Missing labels entirely**:
   - `question` / `clarification`: "What does X mean?", "Can you explain Y?"
   - `feedback`: "Great job", "This could be better"
   - `status_check`: "What's the progress?", "How far along?"
   - `abort` / `cancel`: "Stop", "Never mind", "Cancel that"

5. **No stemming**: The word `tests` does not match the seed `test`. Similarly, `deploying`, `deployed`, `fixes`, `fixing`, `creates`, `creating`, etc. all fail to match their root seeds. This dramatically reduces effective coverage.

### Effective Coverage Estimate

Given no stemming and single-keyword fragility:
- **Task hit rate**: Moderate. 43 seeds cover the most common task verbs, but plural/gerund forms miss.
- **Non-task hit rate**: Very low. Only exact matches of 6 specific words trigger non-task labels.
- **Overall CPU hit rate estimate**: ~40-60% of real-world inputs (heavily dependent on how users phrase things).

---

## Section 3: Tie-Breaking Analysis

### The Algorithm (from `predict()` in `cpu_learner.py`, lines 178-206)

```python
def predict(self, text: str) -> tuple:
    keywords = self.extract_keywords(text)

    best_label = None
    best_conf = 0.0
    matched = []

    for kw in keywords:
        if kw not in self._patterns:
            continue
        conf = self.confidence(kw)
        if conf > best_conf:           # STRICTLY greater
            best_conf = conf
            best_label = self._patterns[kw]["label"]
            matched = [kw]
        elif conf == best_conf and best_label is not None:
            matched.append(kw)         # Append but do NOT change label

    return best_label, best_conf, matched
```

### Tie-Breaking Rules

1. **Strictly greater confidence wins**: When a new keyword has higher confidence than the current best, it takes over completely (new label, new matched list).

2. **On exact tie**: The keyword is appended to `matched`, but the label is **NOT updated**. The label from the **first keyword encountered** (in extraction order) persists.

3. **Extraction order = input text order**: `extract_keywords()` preserves the order words appear in the input text (after lowercasing and deduplication).

### Consequence: Position-Dependent Classification

With the default seed file, ALL seeds have identical count=25 and confidence=0.8824. This means **every seed keyword ties with every other seed keyword**. The winner is determined entirely by **position in the input text**.

| Input | Extracted Keywords | First Match | Label | Correct? |
|---|---|---|---|---|
| `"hello deploy"` | [hello, deploy] | hello (greeting) | `greeting` | NO - user wants to deploy |
| `"deploy hello"` | [deploy, hello] | deploy (task) | `task` | YES |
| `"hello fix the bug"` | [hello, fix, bug] | hello (greeting) | `greeting` | NO - user wants a bugfix |
| `"fix the bug hello"` | [fix, bug, hello] | fix (task) | `task` | YES |
| `"thanks for the help"` | [thanks, help] | thanks (gratitude) | `gratitude` | MAYBE - could be a request for more help |
| `"help me say thanks"` | [help, thanks] | help (task) | `task` | MAYBE - could be gratitude |

### The Core Bug

**There is no majority-vote or weighted-vote mechanism.** When three task keywords and one greeting keyword tie on confidence, the greeting keyword wins if it appears first in the text. The system does not count that 3 keywords say "task" and only 1 says "greeting."

Example: `"Hello, please deploy the build and configure the server"`
- Keywords: [hello, deploy, build, configure, server]
- Matches: hello->greeting, deploy->task, build->task, configure->task
- First match: hello (greeting, 0.8824)
- Ties: deploy (task, 0.8824), build (task, 0.8824), configure (task, 0.8824)
- **Result: label=greeting, matched=[hello, deploy, build, configure]**
- Three task keywords are overruled by one greeting keyword due to position.

### Suggested Fix: Majority-Vote Tie-Breaking

When confidence ties exist, count keywords per label and pick the label with the most votes:

```python
# After the main loop, if ties exist:
if len(matched) > 1:
    from collections import Counter
    label_votes = Counter()
    for kw in matched:
        label_votes[self._patterns[kw]["label"]] += 1
    best_label = label_votes.most_common(1)[0][0]
```

---

## Section 4: Proposed Fixes

### Fix 1: Add Synonym Seeds for Non-Task Labels (CRITICAL)

The most urgent fix. Add seeds to bring non-task labels from FRAGILE to OK status.

**greeting** (add 6 seeds):
```jsonl
{"keyword": "hey", "label": "greeting", "count": 25, "confidence": 0.8824, "examples": ["hey there", "hey!"], "phase": "phase1"}
{"keyword": "greetings", "label": "greeting", "count": 25, "confidence": 0.8824, "examples": ["greetings everyone", "greetings!"], "phase": "phase1"}
{"keyword": "morning", "label": "greeting", "count": 20, "confidence": 0.8571, "examples": ["good morning", "morning!"], "phase": "phase1"}
{"keyword": "evening", "label": "greeting", "count": 20, "confidence": 0.8571, "examples": ["good evening", "evening!"], "phase": "phase1"}
{"keyword": "goodbye", "label": "greeting", "count": 20, "confidence": 0.8571, "examples": ["goodbye!", "goodbye and thanks"], "phase": "phase1"}
{"keyword": "welcome", "label": "greeting", "count": 20, "confidence": 0.8571, "examples": ["welcome aboard", "you're welcome"], "phase": "phase1"}
```

**gratitude** (add 4 seeds):
```jsonl
{"keyword": "thank", "label": "gratitude", "count": 25, "confidence": 0.8824, "examples": ["thank you", "thank you so much"], "phase": "phase1"}
{"keyword": "grateful", "label": "gratitude", "count": 20, "confidence": 0.8571, "examples": ["I'm grateful", "so grateful"], "phase": "phase1"}
{"keyword": "appreciate", "label": "gratitude", "count": 20, "confidence": 0.8571, "examples": ["I appreciate it", "really appreciate"], "phase": "phase1"}
{"keyword": "cheers", "label": "gratitude", "count": 20, "confidence": 0.8571, "examples": ["cheers!", "cheers mate"], "phase": "phase1"}
```

**emotional_positive** (add 5 seeds):
```jsonl
{"keyword": "great", "label": "emotional_positive", "count": 20, "confidence": 0.8571, "examples": ["that's great!", "great work"], "phase": "phase1"}
{"keyword": "awesome", "label": "emotional_positive", "count": 20, "confidence": 0.8571, "examples": ["awesome!", "that's awesome"], "phase": "phase1"}
{"keyword": "excited", "label": "emotional_positive", "count": 20, "confidence": 0.8571, "examples": ["I'm excited", "so excited"], "phase": "phase1"}
{"keyword": "love", "label": "emotional_positive", "count": 20, "confidence": 0.8571, "examples": ["I love this", "love it"], "phase": "phase1"}
{"keyword": "amazing", "label": "emotional_positive", "count": 20, "confidence": 0.8571, "examples": ["amazing work", "that's amazing"], "phase": "phase1"}
```

**emotional_negative** (add 4 seeds):
```jsonl
{"keyword": "frustrated", "label": "emotional_negative", "count": 20, "confidence": 0.8571, "examples": ["I'm frustrated", "so frustrated"], "phase": "phase1"}
{"keyword": "stressed", "label": "emotional_negative", "count": 20, "confidence": 0.8571, "examples": ["feeling stressed", "very stressed"], "phase": "phase1"}
{"keyword": "worried", "label": "emotional_negative", "count": 20, "confidence": 0.8571, "examples": ["I'm worried", "worried about this"], "phase": "phase1"}
{"keyword": "disappointed", "label": "emotional_negative", "count": 20, "confidence": 0.8571, "examples": ["I'm disappointed", "disappointed with"], "phase": "phase1"}
```

**humor** (add 3 seeds):
```jsonl
{"keyword": "funny", "label": "humor", "count": 20, "confidence": 0.8571, "examples": ["that's funny", "funny story"], "phase": "phase1"}
{"keyword": "laugh", "label": "humor", "count": 20, "confidence": 0.8571, "examples": ["made me laugh", "laughing"], "phase": "phase1"}
{"keyword": "hilarious", "label": "humor", "count": 20, "confidence": 0.8571, "examples": ["that's hilarious", "hilarious bug"], "phase": "phase1"}
```

**small_talk** (add 4 seeds):
```jsonl
{"keyword": "weekend", "label": "small_talk", "count": 20, "confidence": 0.8571, "examples": ["how was your weekend", "this weekend"], "phase": "phase1"}
{"keyword": "coffee", "label": "small_talk", "count": 20, "confidence": 0.8571, "examples": ["need coffee", "coffee break"], "phase": "phase1"}
{"keyword": "holiday", "label": "small_talk", "count": 20, "confidence": 0.8571, "examples": ["happy holidays", "on holiday"], "phase": "phase1"}
{"keyword": "lunch", "label": "small_talk", "count": 20, "confidence": 0.8571, "examples": ["lunch break", "had lunch?"], "phase": "phase1"}
```

### Fix 2: Implement Majority-Vote Tie-Breaking (CRITICAL)

Replace position-dependent tie-breaking with vote counting. In `predict()`:

```python
# After the main keyword loop:
if len(matched) > 1:
    from collections import Counter
    label_votes = Counter(
        self._patterns[kw]["label"] for kw in matched
        if kw in self._patterns
    )
    if label_votes:
        best_label = label_votes.most_common(1)[0][0]
```

This ensures that `"Hello, please deploy the build and configure"` classifies as `task` (3 votes) instead of `greeting` (1 vote).

### Fix 3: Harmonize Stop Word Lists (HIGH)

Create a shared stop word module used by both `CPULearner` and `IntentCPU`:

```python
# stillwater/stop_words.py
STOP_WORDS: frozenset = frozenset({
    # ... single canonical list ...
})
```

Both `CPULearner.extract_keywords()` and `IntentCPU.extract_tokens()` import from this shared module. This prevents the current situation where `help` is a valid seed in Phase 1 but a stop word in Phase 2.

### Fix 4: Add Basic Stemming (MEDIUM)

Add suffix stripping to `extract_keywords()` to catch common morphological variants:

```python
def _stem(word: str) -> str:
    """Minimal rule-based stemmer (no external deps)."""
    for suffix in ("ing", "tion", "ment", "ness", "able", "ible", "ous", "ive", "ful", "less", "ed", "er", "es", "ly", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[:-len(suffix)]
    return word
```

This would allow `tests` to match `test`, `deploying` to match `deploy`, `creating` to match `creat` (close enough for seed lookup if we also stem the seeds).

**Caution**: Stemming can cause false matches. A minimal approach (just strip trailing `s`, `ed`, `ing` when the root is >= 3 chars) is safer than a full Porter stemmer.

### Fix 5: Add Input Length Guard (MEDIUM)

Protect against DoS via extremely long input:

```python
MAX_INPUT_LENGTH = 10_000  # characters

@staticmethod
def extract_keywords(text: str) -> list:
    if len(text) > MAX_INPUT_LENGTH:
        text = text[:MAX_INPUT_LENGTH]
    # ... rest of method ...
```

### Fix 6: Add Type Guard to predict() (LOW)

```python
def predict(self, text: str) -> tuple:
    if not isinstance(text, str):
        return None, 0.0, []
    # ... rest of method ...
```

### Fix 7: Differentiate Seed Confidence (LOW)

Instead of uniform count=25 for all seeds, assign confidence based on keyword specificity:

- **High-specificity task keywords** (count=30): `deploy`, `refactor`, `optimize`, `debug`, `integrate`, `configure`, `implement`, `audit`, `scrape`
- **Medium-specificity keywords** (count=25): `fix`, `bug`, `test`, `create`, `feature`, `security`, `performance`, `docs`, `review`, `research`, `design`, `browse`, `email`, `notify`, `analytics`, `pipeline`, `article`, `blog`, `proof`, `theorem`, `calculate`, `prove`
- **Low-specificity / ambiguous keywords** (count=15): `add`, `run`, `write`, `update`, `send`, `process`, `data`, `content`, `build`, `ship`, `plan`, `help`

This breaks the universal tie and gives high-specificity task keywords natural priority over ambiguous ones and over non-task labels.

---

## Summary of Findings

| Finding | Severity | Fix | Effort |
|---|---|---|---|
| All non-task labels FRAGILE (1 seed each) | CRITICAL | Add synonym seeds | Low |
| Position-dependent tie-breaking bug | CRITICAL | Majority-vote tie-breaking | Low |
| Cross-system stop word inconsistency | HIGH | Shared stop word module | Medium |
| No stemming (plurals/gerunds miss) | HIGH | Minimal suffix stripping | Medium |
| No input length guard | MEDIUM | Max length truncation | Low |
| No type guard on predict() | LOW | isinstance check | Low |
| Uniform seed confidence | LOW | Differentiated counts | Low |
| Missing labels (question, cancel, status) | MEDIUM | Add new label seeds | Low |
| No negative evidence mechanism | MEDIUM | Phase 2 feature | High |
| No property-based tests | MEDIUM | Add hypothesis tests | Medium |
