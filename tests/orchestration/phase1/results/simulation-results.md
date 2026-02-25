# Phase 1 Simulation Results

Generated: 2026-02-24 11:28:14 UTC
Engine: TripleTwinEngine (CPU-only, no LLM client)
Data source: /home/phuc/projects/stillwater/data/default/
Seeds: small-talk-seeds.jsonl (50 keywords, all count=25, conf=0.8824)
Phase 1 threshold: 0.70

---

## Summary

- **Total prompts**: 20
- **Predictions match expected**: 20/20 (100%)
- **Mismatches**: 0/20
- **Verdict breakdown**: 9 PASS, 5 PASS-EDGE, 2 FAIL-GAP, 4 FAIL-BUG
- **Correct classifications (reasonable)**: 14/20 (70%)
- **Critical bugs (first-keyword-wins)**: 4
- **Coverage gaps**: 2

---

## Detailed Results

| # | Input | Keywords | Expected | Actual | Conf | LLM? | Handler | Match | Verdict |
|---|-------|----------|----------|--------|------|------|---------|-------|---------|
| 1 | `hello` | hello | greeting | greeting | 0.8824 | No | cpu | MATCH | PASS |
| 2 | `fix the login bug` | fix, login, bug | task | task | 0.8824 | No | cpu | MATCH | PASS |
| 3 | `Hello! Can you fix the broken tests?` | hello, fix, broken, tests | greeting | greeting | 0.8824 | No | cpu | MATCH | FAIL-BUG |
| 4 | `yo` | (none) | unknown | unknown | 0.0000 | No | cpu | MATCH | PASS-EDGE |
| 5 | `thanks for fixing that, now deploy it` | thanks, fixing, deploy | gratitude | gratitude | 0.8824 | No | cpu | MATCH | FAIL-BUG |
| 6 | `what is the best way to optimize queries?` | best, way, optimize, queries | task | task | 0.8824 | No | cpu | MATCH | PASS |
| 7 | `I'm feeling frustrated with this code` | feeling, frustrated, code | unknown | unknown | 0.0000 | No | cpu | MATCH | FAIL-GAP |
| 8 | `run` | run | task | task | 0.8824 | No | cpu | MATCH | PASS |
| 9 | `can you help me understand the architecture?` | help, understand, architecture | task | task | 0.8824 | No | cpu | MATCH | PASS |
| 10 | `(empty)` | (none) | unknown | unknown | 0.0000 | No | cpu | MATCH | PASS-EDGE |
| 11 | `hey hey hey fix fix fix` | hey, fix | task | task | 0.8824 | No | cpu | MATCH | PASS |
| 12 | `DEPLOY TO PRODUCTION NOW` | deploy, production | task | task | 0.8824 | No | cpu | MATCH | PASS |
| 13 | `plz halp` | plz, halp | unknown | unknown | 0.0000 | No | cpu | MATCH | FAIL-GAP |
| 14 | `the the the the` | (none) | unknown | unknown | 0.0000 | No | cpu | MATCH | PASS-EDGE |
| 15 | `12345` | (none) | unknown | unknown | 0.0000 | No | cpu | MATCH | PASS-EDGE |
| 16 | `fix` | fix | task | task | 0.8824 | No | cpu | MATCH | PASS |
| 17 | `I need to write documentation and also run tests` | need, write, documentation, run, tests | task | task | 0.8824 | No | cpu | MATCH | PASS |
| 18 | `tell me a joke about security vulnerabilities` | tell, joke, security, vulnerabilities | humor | humor | 0.8824 | No | cpu | MATCH | FAIL-BUG |
| 19 | `good morning! how's the weather? also please re...` | good, morning, weather, review | small_talk | small_talk | 0.8824 | No | cpu | MATCH | FAIL-BUG |
| 20 | `............` | (none) | unknown | unknown | 0.0000 | No | cpu | MATCH | PASS-EDGE |

---

## Per-Prompt Analysis

### Prompt #1: 'hello'

- **Category**: Happy path greeting
- **Keywords extracted**: `['hello']`
- **Expected**: label=`greeting`, conf=0.8824, llm_called=False
- **Actual**: label=`greeting`, conf=0.8824, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS
- **Edge case**: None -- baseline

### Prompt #2: 'fix the login bug'

- **Category**: Happy path task
- **Keywords extracted**: `['fix', 'login', 'bug']`
- **Expected**: label=`task`, conf=0.8824, llm_called=False
- **Actual**: label=`task`, conf=0.8824, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS
- **Edge case**: None -- baseline

### Prompt #3: 'Hello! Can you fix the broken tests?'

- **Category**: MIXED: greeting + task
- **Keywords extracted**: `['hello', 'fix', 'broken', 'tests']`
- **Expected**: label=`greeting`, conf=0.8824, llm_called=False
- **Actual**: label=`greeting`, conf=0.8824, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: FAIL-BUG
- **Edge case**: BUG: first-keyword-wins, greeting beats task

### Prompt #4: 'yo'

- **Category**: Ultra-short (< 3 chars)
- **Keywords extracted**: `[]`
- **Expected**: label=`unknown`, conf=0.0000, llm_called=False
- **Actual**: label=`unknown`, conf=0.0000, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS-EDGE
- **Edge case**: 'yo' has len=2, filtered by len >= 3 gate

### Prompt #5: 'thanks for fixing that, now deploy it'

- **Category**: Gratitude + task
- **Keywords extracted**: `['thanks', 'fixing', 'deploy']`
- **Expected**: label=`gratitude`, conf=0.8824, llm_called=False
- **Actual**: label=`gratitude`, conf=0.8824, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: FAIL-BUG
- **Edge case**: BUG: first-keyword-wins, gratitude beats task

### Prompt #6: 'what is the best way to optimize queries?'

- **Category**: Question with stop_words
- **Keywords extracted**: `['best', 'way', 'optimize', 'queries']`
- **Expected**: label=`task`, conf=0.8824, llm_called=False
- **Actual**: label=`task`, conf=0.8824, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS
- **Edge case**: Stop-words filtered correctly, 'optimize' survives

### Prompt #7: "I'm feeling frustrated with this code"

- **Category**: Emotion (no seed)
- **Keywords extracted**: `['feeling', 'frustrated', 'code']`
- **Expected**: label=`unknown`, conf=0.0000, llm_called=False
- **Actual**: label=`unknown`, conf=0.0000, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: FAIL-GAP
- **Edge case**: GAP: no seeds for 'frustrated'/'feeling'/'code'

### Prompt #8: 'run'

- **Category**: Single word
- **Keywords extracted**: `['run']`
- **Expected**: label=`task`, conf=0.8824, llm_called=False
- **Actual**: label=`task`, conf=0.8824, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS
- **Edge case**: 'run' has len=3, passes filter, has task seed

### Prompt #9: 'can you help me understand the architecture?'

- **Category**: Question + support
- **Keywords extracted**: `['help', 'understand', 'architecture']`
- **Expected**: label=`task`, conf=0.8824, llm_called=False
- **Actual**: label=`task`, conf=0.8824, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS
- **Edge case**: Question framing stripped, 'help' is task seed

### Prompt #10: ''

- **Category**: Empty string
- **Keywords extracted**: `[]`
- **Expected**: label=`unknown`, conf=0.0000, llm_called=False
- **Actual**: label=`unknown`, conf=0.0000, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS-EDGE
- **Edge case**: Empty input -- graceful degradation

### Prompt #11: 'hey hey hey fix fix fix'

- **Category**: Repeated words
- **Keywords extracted**: `['hey', 'fix']`
- **Expected**: label=`task`, conf=0.8824, llm_called=False
- **Actual**: label=`task`, conf=0.8824, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS
- **Edge case**: Dedup works; 'hey' has no seed; 'fix' is task seed

### Prompt #12: 'DEPLOY TO PRODUCTION NOW'

- **Category**: All caps
- **Keywords extracted**: `['deploy', 'production']`
- **Expected**: label=`task`, conf=0.8824, llm_called=False
- **Actual**: label=`task`, conf=0.8824, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS
- **Edge case**: Case normalization works; urgency signal lost

### Prompt #13: 'plz halp'

- **Category**: Misspellings
- **Keywords extracted**: `['plz', 'halp']`
- **Expected**: label=`unknown`, conf=0.0000, llm_called=False
- **Actual**: label=`unknown`, conf=0.0000, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: FAIL-GAP
- **Edge case**: GAP: no fuzzy matching for misspellings

### Prompt #14: 'the the the the'

- **Category**: Stop words only
- **Keywords extracted**: `[]`
- **Expected**: label=`unknown`, conf=0.0000, llm_called=False
- **Actual**: label=`unknown`, conf=0.0000, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS-EDGE
- **Edge case**: All words are stop_words -- empty keywords

### Prompt #15: '12345'

- **Category**: Numeric only
- **Keywords extracted**: `[]`
- **Expected**: label=`unknown`, conf=0.0000, llm_called=False
- **Actual**: label=`unknown`, conf=0.0000, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS-EDGE
- **Edge case**: Regex [a-z]+ finds nothing -- empty keywords

### Prompt #16: 'fix'

- **Category**: Single keyword, no context
- **Keywords extracted**: `['fix']`
- **Expected**: label=`task`, conf=0.8824, llm_called=False
- **Actual**: label=`task`, conf=0.8824, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS
- **Edge case**: Minimal input that matches a seed

### Prompt #17: 'I need to write documentation and also run tests'

- **Category**: Multi-intent
- **Keywords extracted**: `['need', 'write', 'documentation', 'run', 'tests']`
- **Expected**: label=`task`, conf=0.8824, llm_called=False
- **Actual**: label=`task`, conf=0.8824, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS
- **Edge case**: Multiple task keywords; 'write' is first seed hit

### Prompt #18: 'tell me a joke about security vulnerabilities'

- **Category**: Humor + task keyword
- **Keywords extracted**: `['tell', 'joke', 'security', 'vulnerabilities']`
- **Expected**: label=`humor`, conf=0.8824, llm_called=False
- **Actual**: label=`humor`, conf=0.8824, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: FAIL-BUG
- **Edge case**: BUG: first-keyword-wins, humor beats task

### Prompt #19: "good morning! how's the weather? also please review my PR"

- **Category**: 3 intents
- **Keywords extracted**: `['good', 'morning', 'weather', 'review']`
- **Expected**: label=`small_talk`, conf=0.8824, llm_called=False
- **Actual**: label=`small_talk`, conf=0.8824, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: FAIL-BUG
- **Edge case**: BUG: first-keyword-wins, small_talk beats task

### Prompt #20: '............'

- **Category**: Punctuation only
- **Keywords extracted**: `[]`
- **Expected**: label=`unknown`, conf=0.0000, llm_called=False
- **Actual**: label=`unknown`, conf=0.0000, llm_called=False, handled_by=cpu
- **Match**: YES
- **Verdict**: PASS-EDGE
- **Edge case**: Regex [a-z]+ finds nothing -- empty keywords

---

## Bug Report: First-Keyword-Wins

**Affected prompts**: #3, #5, #18, #19

**Root cause**: `CPULearner.predict()` iterates keywords in extraction order.
All seeds share count=25 / confidence=0.8824. The first keyword that matches a seed
sets `best_label`. Subsequent keywords with equal confidence hit the `elif conf == best_conf`
branch, which appends to `matched[]` but does NOT update `best_label`.

**Impact**: Mixed small-talk + task inputs are classified by whichever category
appears first in the text. Since greetings/gratitude/humor words typically start
sentences ("Hello! Can you fix...", "Thanks, now deploy..."), the task is always lost.
Pipeline stops at Phase 1 with `small_talk:{label}` -- the task never reaches Phase 2.

**Severity**: HIGH -- affects any multi-intent prompt starting with politeness.

**Recommended fixes**:
1. Task-priority override: if ANY keyword maps to 'task', classify as task
2. Label vote counting: count keywords per label, majority wins
3. Multi-label output: return all detected labels, let pipeline decide
4. Weighted priority map: task > greeting > gratitude > humor > small_talk > unknown

---

## Coverage Gaps

### Missing emotion seeds (Prompt #7)
The `emotional_negative` label exists in seeds (only 'sad') but common words like
'frustrated', 'angry', 'upset', 'annoyed', 'disappointed', 'feeling' have no seeds.
The cpu-node doc lists them in the keyword rules table but the JSONL file omits them.

### No fuzzy matching (Prompt #13)
Misspellings like 'plz' and 'halp' fall through with zero matches. No Levenshtein
distance, phonetic matching, or common-typo dictionary is implemented.

---

## Engine Statistics (post-simulation)

(Engine stats captured during simulation run -- see script output for live values)

