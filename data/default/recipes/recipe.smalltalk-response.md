---
id: recipe-smalltalk-response-v1
type: recipe
name: "Small Talk Response Selection"
phase: 1
triggers: ["non-task classification", "low confidence", "session start"]
inputs: ["phase1_label", "phase1_confidence", "session_history"]
outputs: ["response_text", "response_source", "warmth_score"]
latency: "<50ms (all local)"
---

# Recipe: Small Talk Response Selection

## Purpose
Select the best response for non-task Phase 1 classifications using CPU-first architecture.

## Steps

### Step 1: CLASSIFY (CPU)
- Phase 1 Small Talk Twin classifies input
- Output: label + confidence

### Step 2: GATE (Decision)
```
IF label == "task" AND confidence >= 0.70:
    -> Route to Phase 2 (no response needed)

IF label != "task" AND confidence >= 0.70:
    -> Step 3A: HIGH CONFIDENCE PATH

IF confidence < 0.70 OR label == "unknown":
    -> Step 3B: LOW CONFIDENCE PATH
```

### Step 3A: HIGH CONFIDENCE -- Template Response
1. Load responses from `data/default/smalltalk/responses.jsonl`
2. Override with `data/custom/smalltalk/responses.jsonl` (if exists)
3. Filter by: label match + level gate + warmth range + not-used-this-session
4. Select best match (highest confidence, then random for variety)
5. Personalize: inject {user_name}, {project_name}, {last_task}
6. Return immediately

### Step 3B: LOW CONFIDENCE -- Gift Fallback
1. Check alternation: was last gift a joke or fact?
2. Load from `data/default/jokes.json` or `data/default/facts.json`
3. Override with custom versions (if exist)
4. Tag-match: prefer gifts matching project context
5. Append redirect: "What can I help with?"
6. Return immediately

### Step 4: ENRICH (Background, parallel)
- Fire-and-forget: send input to Haiku for classification
- If Haiku returns non-task label with response:
  - Append to `data/custom/smalltalk/llm-enrichment.jsonl`
  - This response is available for NEXT turn only

### Step 5: COMPLIMENT CHECK (Post-task)
After any task completion (Phase 3 returns success):
1. Check compliment budget (max 3 per session)
2. Check if last response was already warm (warmth >= 4)
3. If budget available and not over-watered:
   - Select from `data/default/smalltalk/compliments.jsonl`
   - Append to task response
4. Log compliment usage

### Step 6: REMINDER CHECK (Session start)
At session start only:
1. Load `data/custom/session-history.jsonl`
2. If past session exists:
   - Select reminder template from `data/default/smalltalk/reminders.jsonl`
   - Inject: {last_task}, {open_tasks}, {days_since}
   - Prepend to first response

## Data Flow
```
data/default/smalltalk/     <- shipped templates (pip install)
  responses.jsonl           <- 150+ response templates by label
  compliments.jsonl         <- 30 calibrated compliments
  reminders.jsonl           <- 15 past-session callbacks
  config.jsonl              <- system configuration

data/default/jokes.json     <- 15 programming jokes
data/default/facts.json     <- 20 stillwater facts

data/custom/smalltalk/      <- user overrides + LLM enrichment
  responses.jsonl           <- user custom responses (overrides default)
  llm-enrichment.jsonl      <- LLM-generated responses (auto-populated)
  session-history.jsonl     <- past session data for reminders
```

## Van Edwards Three Levels
| Level | When | Warmth Range | Example |
|-------|------|-------------|---------|
| 1 (Surface) | Default, new users | 1-3 | "Hey! What are you working on?" |
| 2 (Dopamine) | Returning users, some context | 2-4 | "Welcome back. Pick up where you left off?" |
| 3 (Connection) | Long relationship, high GLOW | 3-5 | "You're on fire today. Don't stop now." |

## Bruce Lee Principle
> "Absorb what is useful, discard what is useless, add what is specifically your own."

- **Absorb**: CPU absorbs high-confidence LLM responses into the DB
- **Discard**: Low-confidence responses are never saved
- **Add your own**: data/custom/ lets users add their own style

## Compliment Calibration (The Plant Watering Rule)

> "A well-timed compliment is like watering the plants. Too little water and it dies. Too much water and you kill it."

| Rule | Threshold |
|------|-----------|
| Max compliments per session | 3 |
| Only after | Task completion or achievement |
| Never after | Failure (that is patronizing) |
| Normal completions | Warmth 3-4 |
| Difficult tasks | Warmth 5 (only when demonstrably hard) |
| Skip if | Last response warmth >= 4 (over-watering) |

## Reminder System (The Paying Attention Rule)

> "Reminders from past sessions is like paying attention."

| Rule | Detail |
|------|--------|
| When | Session start only |
| Source | `data/custom/session-history.jsonl` |
| Templates | `data/default/smalltalk/reminders.jsonl` |
| Tokens | {last_task}, {open_tasks}, {days_since} |
| Frequency | Max 1 per session start |
| Requirement | Must reference specific past work, never generic |

## Evidence Gates

```yaml
rung_641:
  - Phase 1 label + confidence logged
  - Response source documented (template / gift / reminder)
  - Warmth score recorded
  - Latency < 50ms confirmed

rung_274177:
  - Level gate correctly applied (Van Edwards level matches relationship depth)
  - Dedup confirmed (no repeat response in session)
  - Compliment budget tracked
  - LLM enrichment fire-and-forget confirmed (not blocking)

rung_65537:
  - Full data flow audited (default -> custom override -> LLM enrichment)
  - Plant Watering Rule verified (no over-complimenting)
  - Reminder specificity verified (references actual past work)
  - Gift alternation confirmed (joke -> fact -> joke)
  - All forbidden states avoided
```

## Forbidden States

- `TEMPLATE_SERVED_WITH_LOW_CONFIDENCE`: Template response served when confidence < 0.70
- `LLM_RESPONSE_ON_CURRENT_TURN`: LLM enrichment served immediately instead of saved for next turn
- `OVER_WATERING`: More than 3 compliments in a session or compliment after warm response
- `COMPLIMENT_AFTER_FAILURE`: Compliment served after task failure
- `GENERIC_REMINDER`: Reminder that does not reference specific past work
- `GIFT_TYPE_REPEATED`: Two jokes or two facts in a row without alternation
- `LEVEL_GATE_VIOLATED`: Level 3 response served to new user without established trust
