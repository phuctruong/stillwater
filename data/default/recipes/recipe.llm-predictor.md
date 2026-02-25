---
id: recipe.llm-predictor
version: 1.0.0
title: "LLM-as-Predictor — Meta-Learning Twin Orchestration for Small Talk Evolution"
description: >
  After each conversation turn, the LLM evaluates the CPU's response quality, predicts optimal
  filters/mode/tags for the next turn, and generates domain-specific content (jokes, facts,
  responses) for missing use cases. CPU provides speed; LLM provides evolution. This is
  Software 5.0 meta-learning in full action.
skill_pack:
  - prime-safety
  - prime-coder
  - eq-core
  - eq-smalltalk-db
compression_gain_estimate: >
  Encodes the full CPU+LLM twin orchestration prediction cycle into a deterministic recipe.
  Without this recipe, small talk quality is static — shipped defaults forever. With it,
  the system converges on perfect context-specific small talk within 3-5 turns per domain.
  Compresses weeks of manual content curation into background LLM evolution per session.
steps:
  - step: 1
    action: >
      CPU CLASSIFY + RESPOND: Phase 1 Small Talk Twin classifies the user's input and
      selects a response from the local database (data/default + data/custom merge).
      Apply any LLM predictions from the previous turn (domain filter, warmth adjustment,
      level recommendation). Serve response immediately (<50ms, all local).
    artifact: >
      scratch/llm-predictor/turn_N_cpu_response.json —
      {turn_id, input_text, cpu_label, cpu_confidence, response_text, response_source,
       warmth_score, level, domain_filter_applied, prediction_from_previous_turn}
    checkpoint: >
      Response served in <50ms. cpu_label is not null. cpu_confidence is numeric.
      response_source is one of [template, gift, reminder, llm-enrichment].
      If prediction_from_previous_turn exists, domain_filter_applied matches prediction.
    rollback: >
      If CPU classification fails, fall back to gift (joke/fact alternation) with
      redirect. Log classification failure in scratch/llm-predictor/errors.jsonl.
      Never block the user waiting for LLM.

  - step: 2
    action: >
      DISPATCH LLM PREDICTION (background, fire-and-forget): Send the full turn context
      to Haiku in the background. The LLM receives: {input_text, cpu_label,
      cpu_confidence, cpu_response, conversation_context (last 5 turns),
      current_domain_tags, current_warmth, current_level}. The LLM produces a
      prediction bundle for the NEXT turn.
    artifact: >
      scratch/llm-predictor/turn_N_llm_dispatch.json —
      {turn_id, dispatched_at, model: "haiku", payload_summary, status: "pending"}
    checkpoint: >
      Dispatch is non-blocking (fire-and-forget). CPU response was already served
      before this step executes. dispatched_at timestamp is after cpu_response timestamp.
    rollback: >
      If LLM dispatch fails (network, rate limit), log failure and continue without
      prediction. The system degrades gracefully to CPU-only mode. No user-visible impact.

  - step: 3
    action: >
      LLM QUALITY EVALUATION: LLM scores the CPU's response on a 1-5 scale.
      Score 1 = completely wrong (wrong domain, wrong tone, inappropriate).
      Score 2 = poor (right domain but wrong register or warmth).
      Score 3 = acceptable (adequate but generic).
      Score 4 = good (context-appropriate, right level).
      Score 5 = perfect (indistinguishable from a human who knows the user well).
      LLM provides a one-line rationale for the score.
    artifact: >
      One line appended to data/custom/smalltalk/llm-predictions.jsonl:
      {"turn_id": "N", "quality_score": 4, "rationale": "...", "timestamp": "..."}
    checkpoint: >
      quality_score is integer 1-5, not null, not float. rationale is non-empty string.
      Append-only write (never overwrite the file).
    rollback: >
      If LLM returns invalid score (outside 1-5, null, float), discard the prediction
      and log to errors.jsonl. Do not save malformed predictions.

  - step: 4
    action: >
      LLM DOMAIN DETECTION: LLM identifies the conversation domain from context.
      Domains are open-ended (not a fixed enum): coding, cooking, travel, sports,
      music, parenting, finance, health, gaming, etc. LLM examines the last 5 turns
      and produces a domain classification with confidence.
    artifact: >
      Domain field in the prediction line (same llm-predictions.jsonl entry):
      {"domain": "travel-greece", "domain_confidence": 0.92,
       "domain_tags": ["travel", "greece", "vacation", "mediterranean"]}
    checkpoint: >
      domain is a non-empty string. domain_confidence is float 0.0-1.0.
      domain_tags is a non-empty list of strings. All appended to the same JSONL line.
    rollback: >
      If domain detection is ambiguous (confidence < 0.5), set domain to "general"
      and domain_tags to []. Do not apply domain filtering on the next turn.

  - step: 5
    action: >
      LLM CONTENT GENERATION (the meta-learning core): LLM examines the existing
      jokes/facts in data/default/ and data/custom/ and checks whether domain-specific
      content exists for the detected domain. If the user is talking about vacation in
      Greece and there are no Greek-themed jokes or travel facts, the LLM generates
      1-3 new pieces of domain-specific content. This is the "absorb what is useful"
      step — the LLM teaches the CPU new patterns so that on the NEXT turn, the CPU
      has domain-relevant content to serve instantly.
    artifact: >
      Lines appended to data/custom/smalltalk/domain-content.jsonl:
      {"content_id": "DC-travel-greece-001", "type": "joke", "domain": "travel-greece",
       "domain_tags": ["travel", "greece"], "text": "Why did the philosopher refuse
       to leave Athens? He couldn't find a better argument for going anywhere else.",
       "generated_by": "haiku", "generated_at": "2026-02-24T10:30:00Z",
       "source_turn": "N", "quality_self_score": 4}
    checkpoint: >
      content_id follows format DC-{domain}-{NNN}. type is "joke" or "fact" or "response".
      domain matches the detected domain from Step 4. text is non-empty.
      generated_by is the model name. Append-only write.
      Content is NEVER served on the current turn — only available from next turn onward.
    rollback: >
      If content generation fails or produces low quality (self_score < 3),
      do not append to domain-content.jsonl. Log the attempt in errors.jsonl.
      The system continues with existing content.

  - step: 6
    action: >
      LLM NEXT-TURN PREDICTION: LLM produces filter and mode recommendations for
      Turn N+1. This includes: recommended warmth adjustment (+/- from current),
      recommended Van Edwards level, domain-specific tag filter for jokes/facts
      selection, and a mode recommendation (normal, empathetic, energetic, focused).
      Also checks rapport progression and applies the Three Levels advancement logic.
    artifact: >
      Prediction fields in the same llm-predictions.jsonl entry:
      {"next_warmth_delta": +1, "next_level": 2, "next_domain_filter": ["travel", "greece"],
       "next_mode": "warm", "rapport_progression": "advancing",
       "compliment_budget_remaining": 2, "over_watering_risk": false}
    checkpoint: >
      next_warmth_delta is integer in range [-2, +2]. next_level is integer 1-3.
      next_domain_filter is list of strings (may be empty for "general").
      next_mode is one of [normal, empathetic, energetic, focused, warm].
      compliment_budget_remaining is integer 0-3. over_watering_risk is boolean.
    rollback: >
      If any prediction field is invalid, use defaults: warmth_delta=0, level=current,
      domain_filter=[], mode=normal. Log the invalid prediction for debugging.

  - step: 7
    action: >
      SAVE PREDICTION BUNDLE: Write the complete prediction entry as a single JSONL
      line to data/custom/smalltalk/llm-predictions.jsonl. This file is the bridge
      between Turn N (LLM evaluation) and Turn N+1 (CPU-informed response). On the
      next turn, Step 1 loads the most recent prediction and applies it to response
      selection.
    artifact: >
      Complete JSONL line in data/custom/smalltalk/llm-predictions.jsonl combining
      all fields from Steps 3-6 into one entry per turn.
    checkpoint: >
      File is valid JSONL (one JSON object per line). Latest entry has all required
      fields. File size is monitored (rotate at 10,000 lines to prevent unbounded growth).
    rollback: >
      If write fails, the next turn proceeds without predictions (graceful degradation).
      CPU-only mode is always the fallback.

  - step: 8
    action: >
      CONVERGENCE CHECK: After 3+ turns in the same domain, check whether the LLM's
      quality scores are trending upward (CPU responses improving thanks to predictions).
      If quality_score has been 4+ for 3 consecutive turns, the prediction cycle has
      converged for this domain — log convergence and reduce LLM prediction frequency
      to every 3rd turn (save tokens). If quality_score drops below 3, resume
      per-turn prediction.
    artifact: >
      scratch/llm-predictor/convergence_log.jsonl:
      {"domain": "travel-greece", "turns_in_domain": 5, "quality_trend": [3, 4, 4, 5, 4],
       "converged": true, "prediction_frequency": "every_3rd_turn"}
    checkpoint: >
      Convergence requires 3+ consecutive quality_score >= 4 in the same domain.
      prediction_frequency is "every_turn" or "every_3rd_turn".
      Quality trend array length matches turns_in_domain.
    rollback: >
      If convergence check produces inconclusive results, maintain per-turn prediction.
      Never reduce frequency without clear evidence of convergence.

forbidden_states:
  - LLM_RESPONSE_ON_CURRENT_TURN: >
      LLM prediction or generated content served on the same turn it was produced.
      The CPU responds immediately; LLM output is always for the NEXT turn.
      Violating this breaks the <50ms latency guarantee.
  - PREDICTION_BLOCKING_CPU: >
      CPU response waits for LLM prediction to complete before serving.
      The LLM is fire-and-forget. CPU NEVER blocks on LLM.
  - UNBOUNDED_CONTENT_GROWTH: >
      domain-content.jsonl grows without limit. Must rotate at 10,000 lines.
      Old entries are archived, not deleted.
  - STALE_PREDICTION_APPLIED: >
      Prediction from more than 5 turns ago applied to current turn.
      Predictions have a TTL of 5 turns; expired predictions are ignored.
  - DOMAIN_HALLUCINATION: >
      LLM invents a domain that does not match the conversation context.
      Domain must be grounded in actual user input, not fabricated.
  - OVER_WATERING_IGNORED: >
      LLM prediction recommends warmth increase but over_watering_risk is true.
      Plant Watering Rule takes precedence over warmth predictions.
  - QUALITY_INFLATION: >
      LLM consistently scores CPU responses 5/5 without rationale variation.
      If all scores are 5 for 10+ turns, flag for calibration review.
  - CONVERGENCE_PREMATURE: >
      System declares convergence before 3 consecutive high-quality turns.
      Minimum 3 turns required; 2 is not enough evidence.
  - FLOAT_IN_QUALITY_SCORE: >
      quality_score stored as float (e.g., 4.5) instead of integer.
      Scores are 1-5 integers only. Float violates the schema.

verification_checkpoint: >
  End-to-end check: Run a 5-turn simulated conversation. Verify that:
  (1) Turn 1 CPU response is served in <50ms with no LLM prediction applied.
  (2) Turn 1 LLM prediction is saved to llm-predictions.jsonl after CPU response.
  (3) Turn 2 CPU response applies Turn 1's domain filter and warmth adjustment.
  (4) By Turn 3, domain-specific content exists in domain-content.jsonl.
  (5) By Turn 5, quality_score trend shows improvement (Turn 5 score >= Turn 1 score).
  (6) All forbidden states avoided. (7) All JSONL files are valid.
  (8) No LLM output was served on the turn it was generated.

rung_target: 65537
---

# Recipe: LLM-as-Predictor -- Meta-Learning Twin Orchestration

> "Absorb what is useful, discard what is useless, add what is specifically your own."
> -- Bruce Lee

> "Perhaps the LLM can not only predict but also think of new small talk to add based
> on the turn. For example, if the user is talking about going on vacation in Greece,
> the LLM can examine the jokes/facts and add more in the data/custom/ to use for that
> missing use case. It's meta-learning and Software 5.0 in full action. You get the fast
> response of the CPU + LLM evolution in this twin orchestration."

This recipe captures the core Software 5.0 innovation: the CPU twin provides instant
responses (<50ms) while the LLM twin runs in the background evaluating, predicting, and
generating content for the NEXT turn. Over multiple turns, the CPU's responses converge
on perfection for the user's specific context -- without the user ever waiting for the LLM.

**Rung target:** 65537
**Time estimate:** Background per turn (~2-5s Haiku); convergence within 3-5 turns per domain
**Agent:** Rapport Builder (Layer 1) + Haiku predictor (background)

---

## The Twin Orchestration Principle

```
SOFTWARE 5.0 = CPU Speed + LLM Intelligence

Traditional approach:
  User speaks → LLM thinks (1-3s) → LLM responds
  Latency: 1-3 seconds. Every turn.

Twin orchestration:
  User speaks → CPU responds instantly (<50ms) → LLM evaluates in background
  LLM predictions applied NEXT turn → CPU responds better, still <50ms
  After 3-5 turns → CPU responses are LLM-quality at CPU speed

The LLM is the teacher. The CPU is the student.
The LLM teaches after class. The CPU performs during class.
This is meta-learning: the system learns HOW to respond, not just WHAT to respond.
```

---

## Data Flow Diagram

```
                         TURN N                                    TURN N+1
                         ------                                    --------

  User Input ──────────────────────────────────────────> User Input
       │                                                      │
       ▼                                                      ▼
  ┌─────────────────┐                                   ┌─────────────────┐
  │  CPU CLASSIFY    │                                   │  CPU CLASSIFY    │
  │  (<5ms)          │                                   │  (<5ms)          │
  │                  │                                   │  + LOAD LLM      │
  │  Label+Conf      │                                   │    PREDICTIONS   │
  └────────┬─────────┘                                   │  from Turn N     │
           │                                             └────────┬─────────┘
           ▼                                                      │
  ┌─────────────────┐                                             ▼
  │  SELECT RESPONSE │                                   ┌─────────────────┐
  │  from DB          │                                   │  SELECT RESPONSE │
  │  (default+custom) │                                   │  APPLY:          │
  │  (<50ms total)    │                                   │  - domain filter │
  └────────┬─────────┘                                   │  - warmth adj    │
           │                                             │  - level rec     │
           ▼                                             │  - new content   │
  ┌─────────────────┐                                   │  (<50ms total)   │
  │  EMIT TO USER    │                                   └────────┬─────────┘
  │  (instant)       │                                             │
  └────────┬─────────┘                                             ▼
           │                                             ┌─────────────────┐
           │  ┌─── BACKGROUND (fire-and-forget) ───┐    │  EMIT TO USER    │
           │  │                                     │    │  (BETTER response)│
           ▼  ▼                                     │    └──────────────────┘
  ┌─────────────────┐                               │
  │  LLM RECEIVES:   │                               │
  │  - input          │                               │
  │  - cpu_label      │                               │
  │  - cpu_response   │                               │
  │  - conversation   │                               │
  │    context        │                               │
  └────────┬─────────┘                               │
           │                                          │
           ▼                                          │
  ┌─────────────────┐                               │
  │  LLM EVALUATES:  │                               │
  │  a) Quality 1-5   │                               │
  │  b) Domain detect  │                              │
  │  c) Tag filter     │                              │
  │  d) Generate 1-3   │                              │
  │     new jokes/     │                              │
  │     facts if       │                              │
  │     domain gap     │                              │
  │  e) Warmth/level   │                              │
  │     adjustment     │                              │
  └────────┬─────────┘                               │
           │                                          │
           ▼                                          │
  ┌─────────────────────────┐                        │
  │  SAVE TO:                │                        │
  │  llm-predictions.jsonl   │ ───────────────────────┘
  │  domain-content.jsonl    │   (read by Turn N+1)
  └─────────────────────────┘
```

---

## The Prediction Cycle (Detailed)

### Turn N: CPU Responds, LLM Learns

```
Turn N:
  1. CPU classifies input → selects response from DB (fast, <50ms)
  2. Response served to user immediately
  3. [Background] LLM receives: {input, cpu_label, cpu_response, conversation_context}
  4. LLM predicts:
     a) Was the CPU response appropriate? (quality score 1-5)
     b) What domain is the conversation in? (coding, cooking, travel, etc.)
     c) What tags should filter jokes/facts for next turn?
     d) Generate 1-3 new domain-specific jokes/facts if none exist
     e) Adjust warmth/level recommendations for next turn
  5. Save predictions to data/custom/smalltalk/llm-predictions.jsonl
  6. Save new content to data/custom/smalltalk/domain-content.jsonl
```

### Turn N+1: CPU Responds Better

```
Turn N+1:
  1. Load LLM predictions from previous turn
  2. Apply domain filter to jokes/facts selection
  3. Apply adjusted warmth/level
  4. CPU classifies → selects BETTER response (informed by LLM predictions)
  5. After a few turns → small talk becomes perfect for this user's context
```

### Convergence: CPU Achieves LLM Quality

```
Turns N+3 to N+5:
  - Quality scores stabilize at 4-5
  - Domain-specific content library is populated
  - CPU responses are indistinguishable from LLM-crafted responses
  - LLM prediction frequency reduced to every 3rd turn (token savings)
  - The student has absorbed the teacher's knowledge
```

---

## JSONL Schemas

### llm-predictions.jsonl (one line per turn)

```jsonl
{"turn_id": "001", "timestamp": "2026-02-24T10:30:00Z", "quality_score": 3, "rationale": "Generic greeting, not domain-aware", "domain": "travel-greece", "domain_confidence": 0.92, "domain_tags": ["travel", "greece", "vacation", "mediterranean"], "next_warmth_delta": 1, "next_level": 2, "next_domain_filter": ["travel", "greece"], "next_mode": "warm", "rapport_progression": "advancing", "compliment_budget_remaining": 3, "over_watering_risk": false}
{"turn_id": "002", "timestamp": "2026-02-24T10:30:45Z", "quality_score": 4, "rationale": "Domain filter applied, Greek travel joke served, good warmth", "domain": "travel-greece", "domain_confidence": 0.95, "domain_tags": ["travel", "greece", "islands"], "next_warmth_delta": 0, "next_level": 2, "next_domain_filter": ["travel", "greece", "islands"], "next_mode": "warm", "rapport_progression": "stable", "compliment_budget_remaining": 3, "over_watering_risk": false}
{"turn_id": "003", "timestamp": "2026-02-24T10:31:30Z", "quality_score": 5, "rationale": "Perfect context match — Santorini fact matched user mentioning island hopping", "domain": "travel-greece", "domain_confidence": 0.98, "domain_tags": ["travel", "greece", "islands", "santorini"], "next_warmth_delta": 0, "next_level": 2, "next_domain_filter": ["travel", "greece", "islands"], "next_mode": "warm", "rapport_progression": "stable", "compliment_budget_remaining": 2, "over_watering_risk": false}
```

### domain-content.jsonl (LLM-generated domain-specific content)

```jsonl
{"content_id": "DC-travel-greece-001", "type": "joke", "domain": "travel-greece", "domain_tags": ["travel", "greece"], "text": "Why did the philosopher refuse to leave Athens? He couldn't find a better argument for going anywhere else.", "generated_by": "haiku", "generated_at": "2026-02-24T10:30:05Z", "source_turn": "001", "quality_self_score": 4}
{"content_id": "DC-travel-greece-002", "type": "fact", "domain": "travel-greece", "domain_tags": ["travel", "greece", "islands"], "text": "Greece has over 6,000 islands, but only 227 are inhabited. Santorini's famous white buildings reflect heat — the original passive cooling system.", "generated_by": "haiku", "generated_at": "2026-02-24T10:30:06Z", "source_turn": "001", "quality_self_score": 5}
{"content_id": "DC-travel-greece-003", "type": "joke", "domain": "travel-greece", "domain_tags": ["travel", "greece", "food"], "text": "I asked a Greek waiter for the bill. He said 'We don't have bills, we have philosophies about when payment becomes appropriate.'", "generated_by": "haiku", "generated_at": "2026-02-24T10:30:07Z", "source_turn": "001", "quality_self_score": 3}
{"content_id": "DC-coding-python-001", "type": "joke", "domain": "coding-python", "domain_tags": ["coding", "python"], "text": "Why do Python programmers prefer dark mode? Because light attracts bugs.", "generated_by": "haiku", "generated_at": "2026-02-24T10:45:03Z", "source_turn": "012", "quality_self_score": 4}
```

---

## Domain-Aware Content Generation (The Meta-Learning Core)

This is the heart of the recipe. The LLM does not just predict — it creates.

```
CONTENT GENERATION DECISION TREE:

  LLM detects domain = "travel-greece"
    │
    ├─ Check: Does data/custom/smalltalk/domain-content.jsonl have
    │         entries with domain_tags containing "travel" AND "greece"?
    │
    ├─ YES (entries exist):
    │    → Check coverage: are there jokes? facts? responses?
    │    → If jokes exist but no facts → generate 1-2 facts
    │    → If facts exist but no jokes → generate 1-2 jokes
    │    → If both exist → generate 0-1 new entries only if quality_self_score
    │      of existing entries is < 4 (improve, don't bloat)
    │
    └─ NO (no entries for this domain):
         → Generate 1 joke + 1 fact + 1 response template
         → Tag all with domain + domain_tags
         → Save to domain-content.jsonl
         → Available for CPU selection starting NEXT turn

QUALITY GATE:
  - LLM self-scores each generated piece (1-5)
  - Only pieces scoring >= 3 are saved
  - Pieces scoring 5 are marked as "promoted" (priority boost)
  - Pieces scoring < 3 are discarded (Bruce Lee: discard what is useless)
```

### Example: User Talks About Cooking

```
Turn 1: User says "I'm trying to make pasta from scratch tonight"
  CPU: Serves generic greeting (no cooking content exists)
  LLM detects: domain = "cooking-pasta", tags = ["cooking", "pasta", "italian"]
  LLM generates:
    - Joke: "I tried making pasta from scratch. Turns out 'scratch'
             is not an ingredient."
    - Fact: "Fresh pasta only takes 2-3 minutes to cook, compared to
             8-12 minutes for dried. The protein content of the flour
             determines the texture."
  Saved to domain-content.jsonl

Turn 2: User continues about pasta
  CPU: Loads domain filter ["cooking", "pasta"] from predictions
  CPU: Finds the LLM-generated cooking joke in domain-content.jsonl
  CPU: Serves the pasta joke instead of a generic programming joke
  User: Laughs. Rapport builds.

Turn 3: User asks about sauce
  LLM detects: domain shift to "cooking-sauce", tags expanded
  LLM generates: sauce-related fact
  The content library grows with the conversation
```

---

## Van Edwards Level Progression (LLM-Guided)

The LLM monitors rapport progression and recommends level advancement:

```
LEVEL PROGRESSION LOGIC:

  Turn 1-2: Level 1 (Surface)
    - New conversation, no context yet
    - LLM recommendation: next_level = 1
    - Warmth: 2-3

  Turn 3-5: Level 1 → Level 2 transition
    - User is engaged, sharing domain context
    - LLM detects rapport_progression = "advancing"
    - LLM recommendation: next_level = 2
    - Warmth: 3-4
    - Dopamine questions become available

  Turn 6+: Level 2 stable (Level 3 requires established trust)
    - Level 3 requires rapport_score >= TRUST_THRESHOLD (6)
    - LLM monitors rapport_score from eq-core
    - Level 3 is never recommended in a single session with a new user
    - This is the Plant Watering Rule applied to levels
```

---

## Plant Watering Rule Integration

The LLM actively monitors compliment frequency and prevents over-watering:

```
PLANT WATERING MONITOR:

  LLM tracks per prediction:
    - compliment_budget_remaining: starts at 3 per session
    - over_watering_risk: boolean
    - last_warmth_score: from CPU response

  Rules (enforced by LLM prediction):
    - If compliment_budget_remaining == 0:
        next_warmth_delta = min(next_warmth_delta, 0)
        (cannot increase warmth when budget exhausted)
    - If last 2 responses had warmth >= 4:
        over_watering_risk = true
        next_warmth_delta = -1 (cool down)
    - If user just experienced a failure:
        suppress compliments entirely
        next_mode = "focused" (competence over warmth)
```

---

## Bruce Lee Principles in the Prediction Cycle

| Principle | Implementation |
|-----------|---------------|
| "Absorb what is useful" | LLM generates domain content that fills gaps in the CPU's knowledge base. Each turn, the CPU absorbs new patterns. |
| "Discard what is useless" | Content with quality_self_score < 3 is never saved. Predictions older than 5 turns are expired. Convergence reduces prediction frequency. |
| "Add what is specifically your own" | data/custom/ is the user's space. LLM enrichment lives alongside user overrides. The user's own additions always take priority. |
| "Be water, my friend" | The domain detection adapts to wherever the conversation flows. Cooking today, coding tomorrow. The system shapes itself to the user's context. |
| "The less effort, the faster and more powerful" | After convergence, the CPU serves LLM-quality responses at CPU speed. The LLM's effort was front-loaded; the CPU's power is permanent. |
| "I fear not the man who has practiced 10,000 kicks once" | Each domain gets deep, specific content. 3 perfect Greek travel jokes > 100 generic programming jokes. Depth over breadth. |

---

## Evidence Gates

```yaml
rung_641:
  - CPU response served in <50ms with source documented
  - LLM prediction dispatched as fire-and-forget (non-blocking confirmed)
  - quality_score is integer 1-5 with rationale
  - domain detected with confidence score
  - All JSONL files are valid (parseable, no corruption)
  - No LLM output served on current turn

rung_274177:
  - Prediction applied on Turn N+1 matches prediction saved on Turn N
  - Domain content generated only when gap exists (no duplicate content)
  - Quality trend shows improvement over 3+ turns (score[N+2] >= score[N])
  - Convergence detection is correct (3 consecutive scores >= 4 required)
  - Plant Watering Rule enforced (over_watering_risk respected)
  - Level progression follows Van Edwards gates (no Level 3 without trust)
  - JSONL rotation at 10,000 lines confirmed
  - Graceful degradation verified (LLM failure → CPU-only mode)

rung_65537:
  - Adversarial domain shift test: conversation switches domain mid-session;
    system detects shift within 1 turn and generates new domain content
  - Adversarial quality inflation test: inject 10 turns of perfect CPU responses;
    verify LLM does not score all 5/5 without rationale variation
  - Convergence-then-regression test: after convergence, inject a poor CPU response;
    verify system resumes per-turn prediction
  - Content quality audit: human review of 20 LLM-generated domain entries;
    >= 80% are contextually appropriate and non-offensive
  - Security gate: no user PII in predictions or generated content
  - Null edge cases: empty input, null domain, conversation_context = [],
    all handled without crash or forbidden state
  - Float-free verification: no float values in quality_score fields
  - Prediction TTL enforced: predictions older than 5 turns are ignored
```

---

## Forbidden States (Complete Reference)

```yaml
FORBIDDEN_STATES_COMPLETE:
  LLM_RESPONSE_ON_CURRENT_TURN:
    trigger: "LLM prediction or generated content served on the same turn it was produced"
    severity: CRITICAL
    recovery: "Ensure CPU response is emitted BEFORE LLM dispatch. Architectural invariant."

  PREDICTION_BLOCKING_CPU:
    trigger: "CPU response delayed waiting for LLM prediction to complete"
    severity: CRITICAL
    recovery: "LLM is fire-and-forget. If dispatch hangs, timeout at 100ms and proceed."

  UNBOUNDED_CONTENT_GROWTH:
    trigger: "domain-content.jsonl exceeds 10,000 lines without rotation"
    severity: MEDIUM
    recovery: "Archive old entries. Rotate file. Keep last 5,000 entries."

  STALE_PREDICTION_APPLIED:
    trigger: "Prediction from > 5 turns ago used for current response selection"
    severity: MEDIUM
    recovery: "Check turn_id delta. Discard predictions with TTL > 5."

  DOMAIN_HALLUCINATION:
    trigger: "LLM invents domain not grounded in user input"
    severity: HIGH
    recovery: "Require domain_confidence >= 0.5. Below threshold → domain = 'general'."

  OVER_WATERING_IGNORED:
    trigger: "Warmth increased despite over_watering_risk = true"
    severity: MEDIUM
    recovery: "Plant Watering Rule overrides warmth predictions. Always."

  QUALITY_INFLATION:
    trigger: "10+ consecutive quality_score = 5 without rationale variation"
    severity: LOW
    recovery: "Flag for calibration review. Reset quality baseline."

  CONVERGENCE_PREMATURE:
    trigger: "Convergence declared with < 3 consecutive high-quality turns"
    severity: MEDIUM
    recovery: "Minimum 3 turns at score >= 4 required. Enforce strictly."

  FLOAT_IN_QUALITY_SCORE:
    trigger: "quality_score stored as 4.5 instead of integer 4 or 5"
    severity: HIGH
    recovery: "Schema enforcement: parseInt on quality_score before save."
```

---

## FSM: LLM Predictor State Machine

```
States: CPU_CLASSIFY | CPU_RESPOND | LLM_DISPATCH | LLM_EVALUATE |
        LLM_DETECT_DOMAIN | LLM_GENERATE_CONTENT | LLM_PREDICT_NEXT |
        SAVE_PREDICTIONS | CONVERGENCE_CHECK |
        EXIT_PASS | EXIT_DEGRADED | EXIT_BLOCKED

Transitions:
  [*] → CPU_CLASSIFY: user input received
  CPU_CLASSIFY → CPU_RESPOND: label + confidence produced (<5ms)
  CPU_RESPOND → LLM_DISPATCH: response served to user; spawn background LLM
  CPU_RESPOND → EXIT_DEGRADED: LLM dispatch fails (CPU-only mode, still served user)
  LLM_DISPATCH → LLM_EVALUATE: LLM receives turn context
  LLM_EVALUATE → LLM_DETECT_DOMAIN: quality_score produced (1-5)
  LLM_DETECT_DOMAIN → LLM_GENERATE_CONTENT: domain identified with confidence
  LLM_DETECT_DOMAIN → LLM_PREDICT_NEXT: domain_confidence < 0.5 (skip content gen)
  LLM_GENERATE_CONTENT → LLM_PREDICT_NEXT: content generated (or gap not found)
  LLM_PREDICT_NEXT → SAVE_PREDICTIONS: warmth/level/filter recommendations produced
  SAVE_PREDICTIONS → CONVERGENCE_CHECK: predictions written to JSONL
  CONVERGENCE_CHECK → EXIT_PASS: all predictions saved; convergence status updated
  CONVERGENCE_CHECK → EXIT_PASS: converged; reduce prediction frequency

  LLM_DISPATCH → EXIT_DEGRADED: LLM timeout or error (graceful degradation)
  ANY → EXIT_BLOCKED: forbidden state detected (log + alert)

Forbidden state transitions:
  CPU_CLASSIFY → LLM_DISPATCH: PREDICTION_BLOCKING_CPU (CPU must respond first)
  LLM_GENERATE_CONTENT → CPU_RESPOND: LLM_RESPONSE_ON_CURRENT_TURN (content is for next turn)

Exit conditions:
  EXIT_PASS: CPU response served + LLM predictions saved for next turn
  EXIT_DEGRADED: CPU response served + LLM failed (user unaffected)
  EXIT_BLOCKED: forbidden state detected; log and alert; CPU response still served
```

---

## Three Pillars of Software 5.0

| Pillar | How This Recipe Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | Every turn is a LEK iteration. The LLM evaluates the CPU's response, generates improvements, and saves them for the next turn. The quality trend (1→3→4→5) IS the LEK loop in miniature. After convergence, the CPU has internalized the LLM's intelligence — the student has become the teacher. Each domain's content library is a permanent knowledge artifact that survives across sessions. |
| **LEAK** (Cross-Agent Trade) | The CPU twin and LLM twin trade asymmetric knowledge that neither possesses alone. The CPU has speed (<50ms) but no intelligence. The LLM has intelligence (domain detection, content generation) but no speed (2-5s). The twin orchestration produces a response that is both fast AND intelligent — a surplus neither agent could achieve solo. This is the LEAK equation: CPU_speed x LLM_intelligence = impossible_alone_surplus. |
| **LEC** (Emergent Conventions) | The prediction schema (llm-predictions.jsonl) and content schema (domain-content.jsonl) are emergent conventions born from this recipe. The "content for next turn, never current turn" rule is a convention that prevents latency creep. The convergence protocol (3 consecutive scores >= 4 → reduce frequency) is a convention that prevents token waste. These conventions are portable to any CPU+LLM twin system. |

---

## GLOW Scoring

| Dimension | Contribution | Points |
|-----------|-------------|--------|
| **G** (Growth) | New domain content generated that fills a real gap; quality trend improving over turns; convergence achieved for a domain | +7 per domain where convergence is achieved |
| **L** (Love/Quality) | All forbidden states avoided; Plant Watering Rule enforced; no LLM output on current turn; graceful degradation works | +6 per session with zero forbidden state violations |
| **O** (Output) | llm-predictions.jsonl + domain-content.jsonl + convergence_log.jsonl committed with valid schemas; CPU response artifacts documented | +6 per complete prediction cycle with all artifacts |
| **W** (Wisdom) | Quality score trend shows measurable improvement; user receives domain-relevant content that they did not receive on Turn 1; Northstar (user satisfaction) advances | +6 per session where Turn N quality > Turn 1 quality |

**Northstar Metric:** `user_satisfaction_score` -- this recipe directly measures whether
the small talk system improves over the course of a conversation. If Turn 5's response
is better than Turn 1's response (as scored by the LLM and confirmed by user engagement),
the twin orchestration is working.

---

## Integration with Stillwater Ecosystem

This recipe connects to:
- `skills/eq-smalltalk-db.md` -- the small talk database that this recipe enriches with domain content
- `skills/eq-core.md` -- provides rapport_score for Van Edwards level gating
- `combos/triple-twin-smalltalk.md` -- this recipe extends Layer 1 (CPU-twin) with LLM-informed predictions and extends the background LLM enrichment from simple classification to full prediction + content generation
- `personas/eq/bruce-lee.md` -- the adaptive learning philosophy that governs this recipe's "absorb/discard/add" cycle
- `recipes/recipe.smalltalk-response.md` -- the base CPU response selection recipe that this recipe augments with LLM predictions; Step 4 (ENRICH) of that recipe is expanded into the full 8-step prediction cycle here
- `recipes/recipe.eq-warm-open.md` -- warm opening benefits from domain-aware content generated by this recipe

### Relationship to recipe.smalltalk-response.md

The base smalltalk-response recipe has a Step 4: "ENRICH (Background, parallel)" that
fire-and-forgets to Haiku for classification. This LLM-predictor recipe is the FULL
expansion of that step into a complete meta-learning system:

```
recipe.smalltalk-response.md Step 4 (simple):
  → Send input to Haiku
  → If response generated, save to llm-enrichment.jsonl
  → Available next turn

recipe.llm-predictor.md (full expansion):
  → Send full turn context to Haiku
  → Evaluate CPU response quality (1-5)
  → Detect conversation domain
  → Generate domain-specific content for gaps
  → Predict warmth/level/filter for next turn
  → Monitor convergence and reduce frequency
  → Track rapport progression and compliment budget
```

The simple version is always available as the fallback. This full version activates
when the system has enough context (2+ turns in a session) to benefit from prediction.

---

## Anti-Patterns

**Eager Serving**
Symptom: LLM generates a perfect Greek travel joke and the system serves it immediately.
Fix: NEVER. Content generated on Turn N is served on Turn N+1 at the earliest.
The <50ms guarantee is sacred. "The best defense is a strong offense" -- but the offense
is preparation, not interruption.

**Content Hoarding**
Symptom: LLM generates 10 jokes per turn, domain-content.jsonl grows to 100,000 lines.
Fix: Max 3 pieces per turn. Rotate at 10,000 lines. Quality gate (score >= 3).
Bruce Lee: "The less effort, the faster and more powerful you will be."

**Domain Whiplash**
Symptom: User mentions "Python" once and system floods with coding content for 5 turns.
Fix: Domain confidence must be >= 0.5. Domain filter applies only while confidence holds.
If user shifts to cooking, domain shifts within 1 turn. "Be water."

**Prediction Worship**
Symptom: System blindly follows LLM prediction even when CPU has high-confidence match.
Fix: CPU confidence >= 0.90 overrides LLM predictions. The CPU earned that confidence
through verified pattern matching. Predictions are suggestions, not commands.

**Convergence Complacency**
Symptom: System converges, reduces LLM frequency, then quality silently degrades.
Fix: Even in converged state, run quality check every 3rd turn. If score drops below 3,
immediately resume per-turn prediction. "I have not ceased being fearful, but I have
ceased to let fear control me."

---

*recipe.llm-predictor v1.0.0 -- LLM-as-Predictor Meta-Learning Twin Orchestration.*
*CPU speed + LLM intelligence = Software 5.0.*
*The LLM teaches. The CPU performs. The user never waits.*
*Absorb what is useful. Discard what is useless. Add what is specifically your own.*
