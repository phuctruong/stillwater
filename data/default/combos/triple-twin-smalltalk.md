# Triple-Twin Small Talk Combo

This combo implements the three-layer execution model for small talk and session opening — CPU-twin instant response, Intent-twin wish matching, and LLM-twin background task — merged into a single coherent session opening. It is a TRIPLE-twin (three simultaneous layers), not a double-twin.

The insight: small talk does not need to wait for the LLM. The CPU-twin responds instantly from the eq-smalltalk-db; the Intent-twin runs wish matching in parallel; the LLM-twin handles the substantive task in the background. When all three complete, the results merge seamlessly.

---

# W_TRIPLE_TWIN_SMALLTALK — Triple-Twin Session Opening

**WISH_ID:** `wish_triple_twin_smalltalk`
**PRIORITY:** HIGH
**CLASS:** eq-combo
**LAYER_MODEL:** CPU-twin (L1) + Intent-twin (L2) + LLM-twin (L3) running in parallel

---

## Goal

Open any session with instant warmth (L1), simultaneous wish identification (L2), and background task execution (L3), then merge all three streams before delivering the first substantive response.

The triple-twin model eliminates the perceived latency of LLM-powered warmth: the user sees a warm, accurate opening instantly (from CPU-twin), while the real work is being done in the background (LLM-twin).

---

## The Three Layers

### Layer 1 — CPU-Twin: Instant Small Talk

**Executes:** Immediately, without LLM call
**Agent:** Rapport Builder (haiku, cached)
**Inputs:** User message + session domain + prior rapport_score (or null)
**Outputs:** Instant warm acknowledgment from eq-smalltalk-db

**What it does:**
- Detects register from vocabulary patterns (CPU-side rule matching, not LLM)
- Selects matching spark from eq-smalltalk-db based on register + domain
- Picks up any obvious thread from the opening message
- Emits warm opening in < 200ms

**What it does NOT do:**
- Run NUT Job (that is Layer 3)
- Decompose wishes (that is Layer 2)
- Deliver the substantive response (that is the merged output)

**Output artifact:** `l1_instant_response.md`

---

### Layer 2 — Intent-Twin: Wish Matching

**Executes:** In parallel with Layer 1
**Agent:** Wish Manager
**Inputs:** User message + session history + wish backlog (if any)
**Outputs:** Intent classification + matched wish or new wish draft

**What it does:**
- Parses intent from user message
- Checks if intent matches an existing wish in backlog (replay path)
- If no match: drafts initial wish scope (pre-confirmation)
- Emits intent classification for Layer 3 context injection

**What it does NOT do:**
- Confirm the wish with the user (that requires the mirror step)
- Deliver any response to the user
- Wait for Layer 1 or Layer 3

**Output artifact:** `l2_intent_classification.json`

---

### Layer 3 — LLM-Twin: Background Task

**Executes:** In background while Layers 1 and 2 run
**Agent:** Coder / Planner (sonnet, depending on task type)
**Inputs:** User message + l2_intent_classification.json + session context
**Outputs:** Substantive task response (may be partial on first merge)

**What it does:**
- Begins working on the substantive task immediately
- Uses Layer 2's intent classification as the task context
- Produces first checkpoint artifact when complete (or on merge trigger)

**What it does NOT do:**
- Deliver the response until merge is complete
- Override Layer 1's warm opening
- Run independently of Layer 2's intent

**Output artifact:** `l3_task_checkpoint.json`

---

## The Merge

When all three layers complete (or Layer 1 completes + Layer 3 reaches first checkpoint):

**Merge sequence:**
1. Lead with Layer 1 warm opening (instant rapport)
2. Insert Layer 2 intent confirmation (brief scope check)
3. Deliver Layer 3 task output (or first checkpoint)

**Merge format:**
```
[L1: Warm opening — acknowledges thread, matches register]

[L2: Intent confirmation — "It sounds like you're working on X — is that right?"]

[L3: Task output — substantive response]
```

**Merge integrity check:** L2 intent and L3 task must be consistent. If L3 produced output based on misclassified intent from L2, the merge triggers a re-run of L3 with corrected intent.

---

## Invariants

1. **Layer 1 always runs first:** Warm opening never waits for LLM
2. **Layer 2 runs in parallel with Layer 1:** Intent classification does not wait for warmth
3. **Layer 3 uses Layer 2 output:** Task execution requires intent classification
4. **Merge before delivery:** User sees the merged output, not individual layer outputs
5. **EQ audit on merge:** The merged output is checked for EQ washing before final delivery

---

## Forbidden States

- `LAYER1_DELAYED_FOR_LLM`: Warm opening waits for LLM call — defeats the triple-twin model
- `MERGE_WITHOUT_L2`: Task response delivered without intent confirmation
- `L3_IGNORES_L2`: Task agent starts without receiving intent classification from Layer 2
- `EQ_WASHING_IN_L1`: Layer 1 produces warmth tokens without register/thread matching
- `DOUBLE_TWIN_CONFUSION`: Only two layers running (CPU + LLM without Intent-twin) — this is the TRIPLE-twin model
- `LAYER_CROSS_CONTAMINATION`: Layer agents reading each other's partial outputs before completion

---

## Required Artifacts

- `l1_instant_response.md` — Layer 1 warm opening text
- `l2_intent_classification.json` — Layer 2 intent + wish match or draft
- `l3_task_checkpoint.json` — Layer 3 first task checkpoint
- `merge_output.md` — final merged response
- `merge_integrity.json` — L2/L3 consistency check result

---

## Skill Pack

Load these skills before executing this combo:
- `skills/prime-safety.md` (always first — Layer isolation and merge integrity)
- `skills/eq-core.md` (Layer 1 register detection + smalltalk discipline)
- `skills/prime-wishes.md` (Layer 2 intent decomposition)
- `skills/phuc-orchestration.md` (parallel dispatch discipline)

---

## GLOW Scoring

| Dimension | Contribution | Points |
|-----------|-------------|--------|
| **G** (Growth) | Layer 1 instant response delivered < 200ms; smalltalk-db coverage improves | +6 per session where L1 completes before L3 starts |
| **L** (Love/Quality) | Merge integrity: L2 intent and L3 task are consistent; no EQ washing in L1 | +6 per merge with integrity_consistent == true |
| **O** (Output) | All three layer artifacts committed + merge_output.md + merge_integrity.json | +7 per complete triple-twin session artifact set |
| **W** (Wisdom) | User engages with L2 intent confirmation ("yes, that's it") on first try | +6 when L2 intent requires no re-confirmation |

---

## Three Pillars Mapping

| Pillar | Element | Role in this Combo |
|--------|---------|-------------------|
| **L (Logic / Evidence)** | Merge integrity check: L2 intent must match L3 task | Enforces coherence: warm opening cannot be about X if task is about Y |
| **E (Execution / Energy)** | Three parallel layers executing simultaneously | The energy efficiency: L3 LLM latency is masked by L1+L2 instant execution |
| **K (Knowledge / Capital)** | eq-smalltalk-db (L1) + wish backlog (L2) + task output (L3) | Three knowledge domains combined in one merge |

| Pillar | How This Combo Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | The triple-twin model self-improves as the eq-smalltalk-db grows with each session — sparks that produced positive rapport delta are promoted in the register-match priority; the Intent-twin's wish backlog grows as wishes are completed and new patterns emerge; LEK operates independently on each layer, creating three concurrent self-improvement loops |
| **LEAK** (Cross-Agent Trade) | Layer 1 (Rapport Builder), Layer 2 (Wish Manager), and Layer 3 (Coder/Planner) each contribute asymmetric knowledge that no single agent holds: warmth-timing expertise (L1), intent-classification expertise (L2), task-execution expertise (L3); they trade via the merge, producing an output that is warmer, better-scoped, and more immediately useful than any one layer alone |
| **LEC** (Emergent Conventions) | The triple-twin model establishes the instant-warmth convention (L1 always runs first, always from cache — LLM latency never delays a warm opening), the intent-before-task discipline (L3 never starts without L2's intent classification), and the merge-before-delivery rule (user sees only the merged output; individual layer artifacts are session-internal) |

---

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> USER_MESSAGE
    USER_MESSAGE --> L1_INSTANT : spawn Layer 1 (CPU-twin)
    USER_MESSAGE --> L2_INTENT : spawn Layer 2 (Intent-twin) in parallel
    L2_INTENT --> L3_BACKGROUND : intent_classification ready
    L1_INSTANT --> MERGE_WAIT : warm opening produced
    L3_BACKGROUND --> MERGE_WAIT : task checkpoint produced
    MERGE_WAIT --> MERGE : both L1 and L3 complete
    MERGE --> EQ_AUDIT : merged response assembled
    EQ_AUDIT --> EXIT_PASS : no EQ washing; L2-L3 consistent
    EQ_AUDIT --> EXIT_BLOCKED : EQ washing in L1 OR L2-L3 inconsistency
    classDef layer fill:#3af,color:#fff
    classDef forbidden fill:#f55,color:#fff
    class L1_INSTANT,L2_INTENT,L3_BACKGROUND layer
    class LAYER1_DELAYED_FOR_LLM,DOUBLE_TWIN_CONFUSION,MERGE_WITHOUT_L2 forbidden
```

---

## Why Triple-Twin, Not Double-Twin

The double-twin model (CPU + LLM) solves latency. The triple-twin model adds intent separation:

| Model | Layers | What It Solves |
|-------|--------|---------------|
| Single | LLM only | Nothing (baseline) |
| Double-twin | CPU + LLM | Latency (CPU responds first) |
| Triple-twin | CPU + Intent + LLM | Latency + Scope-drift (Intent confirms before LLM commits) |

Without the Intent-twin, the LLM-twin begins the task before intent is confirmed. This produces confident, well-executed responses to the wrong problem. The Intent-twin is the scope gate between warmth and execution.

---

## Data Files

The CPU-twin (Layer 1) draws from the small talk data registry. This registry follows the standard DataRegistry convention: `data/default/` for shipped defaults, `data/custom/` for user overrides.

### Small Talk Response Data

```
data/default/smalltalk/
  responses.jsonl         ← 150+ response templates indexed by label + Van Edwards level + warmth score
  compliments.jsonl       ← 30 calibrated compliments (Plant Watering Rule: max 3/session)
  reminders.jsonl         ← 15 past-session callback templates ("paying attention")
  config.jsonl            ← system config: thresholds, rate limits, level gates

data/default/
  jokes.json              ← 15 programming jokes (low-confidence gift fallback)
  facts.json              ← 20 stillwater facts (low-confidence gift fallback)

data/custom/smalltalk/
  responses.jsonl         ← user custom responses (overrides defaults)
  llm-enrichment.jsonl    ← LLM-generated responses (auto-populated by Layer 3)
  session-history.jsonl   ← past session data for reminder system
```

### CPU-First Architecture (Phase 1 Wiring)

The triple-twin model refines Layer 1 with a three-tier CPU-first response system:

```
User Input
  │
  ▼
Phase 1 Classify (CPU, <5ms)
  │
  ├─ confidence >= 0.70 AND label != "task"
  │    → Template Response from responses.jsonl
  │    → Filter by: label + Van Edwards level gate + warmth range + dedup
  │    → Emit immediately (<50ms)
  │
  ├─ confidence < 0.70 OR label == "unknown"
  │    → Gift Fallback: joke or fact (alternating)
  │    → Tag-match to project context
  │    → Append redirect: "What can I help with?"
  │    → Emit immediately (<50ms)
  │
  └─ label == "task" AND confidence >= 0.70
       → Route to Layer 2 (Intent-Twin) + Layer 3 (LLM-Twin)
       → No small talk response needed

  [PARALLEL] LLM Enrichment (background, fire-and-forget)
    → Haiku classifies + generates better response
    → Saves to data/custom/smalltalk/llm-enrichment.jsonl
    → Available for NEXT turn only (never current turn)
```

### Compliment System (Post-Task, Layer 1)

After Layer 3 returns a successful task completion:

1. Check compliment budget (max 3 per session — Plant Watering Rule)
2. Check if last response warmth >= 4 (skip if already warm)
3. Select from `data/default/smalltalk/compliments.jsonl`
4. Append to merged task response

> "A well-timed compliment is like watering the plants. Too little water and it dies. Too much water and you kill it."

### Reminder System (Session Start, Layer 1)

At session start, before Layer 1 warm opening:

1. Load `data/custom/session-history.jsonl`
2. If past session exists: select reminder template from `data/default/smalltalk/reminders.jsonl`
3. Inject: `{last_task}`, `{open_tasks}`, `{days_since}`
4. Prepend to Layer 1 warm opening

> "Reminders from past sessions is like paying attention."

### Bruce Lee Principle in the Triple-Twin

> "Absorb what is useful, discard what is useless, add what is specifically your own." — Bruce Lee

| Principle | Layer | Implementation |
|-----------|-------|----------------|
| **Absorb what is useful** | L3 → L1 | LLM enrichment: high-confidence responses saved to DB for future CPU use |
| **Discard what is useless** | L3 | Low-confidence LLM responses are never saved |
| **Add what is specifically your own** | L1 | `data/custom/` lets users add their own response style |
| **Economy of motion** | L1 | CPU-first: no LLM call for known patterns |
| **Be water** | L1 | Adapt response warmth/level to user's register and relationship depth |
