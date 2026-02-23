# LLM Validators Design Specification
## Phase 1/2/3 Feedback Loop Implementation

**Status:** DESIGN APPROVED (Question-Based Discovery Complete)
**Date:** 2026-02-23
**Rung Target:** 641 (deterministic, testable, offline-first)
**SW5.0 Compliance:** LEAK (Asymmetric Knowledge Transfer) + PORTAL (Boundary Crossing)

---

## Executive Summary

Three Haiku validators (Phase 1/2/3) implement the CPU-LLM feedback loop:
- **Phase 1:** Small Talk Twin — warm_token validation → smalltalk_learn.jsonl
- **Phase 2:** Intent Twin — IntentMatch validation → learned_wishes.jsonl
- **Phase 3:** Execution Twin — ExecutionMatch validation → learned_combos.jsonl

Each validator implements:
1. **HANDSHAKE** — Bayesian alignment check (confidence > phase_threshold)
2. **PORTAL** — Append to learned_*.jsonl at session boundary
3. **SUBSTRATE** — Shared JSONL schema (keywords, action, confidence, timestamp)

---

## Architecture Decisions (Q-001 through Q-020)

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| Q-001 | Storage | Hybrid: Local + GCS sync | Works offline (low latency), persists to cloud (durable) |
| Q-002 | Multi-user | Hybrid: Shared + private | High-confidence patterns globally, user-specific overrides private |
| Q-004 | CLI sync | Opt-in | Users choose to sync `stillwater auth login` |
| Q-009 | Conflict merge | Last-write-wins | Timestamp-based, deterministic, simple |
| Q-005 | Visibility | CLI admin + solaceagi.com settings | Power users: CLI; casual users: web dashboard |
| Q-006 | Audit trail | Store validator source + date | Transparency: users see WHEN/HOW learned |
| Q-015 | Thresholds | Per-phase gates | small-talk=0.70, intent=0.80, execute=0.90 |
| Q-016 | Cost control | Validate only if CPU confidence < 0.5 | Skip expensive haiku when CPU confident |
| Q-007 | Diagrams | State machine: CPU → LLM → Learn | Visualize feedback loop for users |
| Q-018 | Verification | Convergence + pattern growth + A/B test | Comprehensive LEAK validation |

---

## Architecture Diagram (Prime Mermaid)

```
state "Phase N Workflow" as PHASE {
  [*] --> CPU_DECIDE
  CPU_DECIDE --> EMIT_TOKEN
  EMIT_TOKEN --> LLM_VALIDATOR

  LLM_VALIDATOR --> CONFIDENCE_CHECK{confidence > phase_threshold?}
  CONFIDENCE_CHECK -->|YES| PORTAL_WRITE["Write to learned_*.jsonl"]
  CONFIDENCE_CHECK -->|NO| SKIP_LEARN["No learning signal"]

  PORTAL_WRITE --> MERGE_SIGNAL["Next startup: CPU loads + merges"]
  SKIP_LEARN --> MERGE_SIGNAL
  MERGE_SIGNAL --> [*]
}

state "Storage Topology" as STORAGE {
  LOCAL["Local (~/.stillwater/)"] --> GCS["Google Cloud Storage"]
  GCS --> SYNC["Sync background job"]
  SYNC --> CONFLICT["Conflict: last-write-wins"]
}

state "Learning Layer" as LEARNING {
  SHARED["Shared: High-confidence (>0.85)"]
  PRIVATE["Private: User-specific (<0.85)"]
  SHARED --> PRIVATE: "User's confidence < global = override"
}
```

---

## Validator Specifications

### Phase 1: Small Talk Twin Validator

**Input:**
```python
{
  "warm_token": WarmToken,           # CPU's response (source=cpu_glow|cpu_repo|queue_hit)
  "prompt": str,                      # User's original message
  "session_context": dict,            # (user_id, session_id, project, etc)
  "full_history": list                # Prior messages in session
}
```

**HANDSHAKE (Bayesian Alignment):**
- Read full context: "Does warm_token fit this situation?"
- Confidence scoring: 0.0 (definitely override) to 1.0 (definitely correct)
- Gate: If confidence <= 0.70, do NOT learn (too weak signal)

**Decision Logic:**
```python
if warm_token.source == "queue_hit":
  decision = "CONFIRM"
  learn_entry = None

elif llm_confidence_override > 0.70:
  if llm_override_differs_from_warm_token:
    decision = "OVERRIDE"
    learned = {
      "keywords": extract_emotional_keywords(full_context),
      "action": infer_action(llm_response),  # suppress_humor | show_sympathy | celebrate | etc
      "tone": infer_tone(llm_response),
      "confidence": llm_confidence_override,
      "source": "phase1_validator",
      "timestamp": now()
    }
  else:
    decision = "AUGMENT"
    learned = enhance_with_details(...)

else:
  decision = "CONFIRM"
  learn_entry = None
```

**Output:**
```python
{
  "decision": "CONFIRM|OVERRIDE|AUGMENT",
  "response": str,                    # CPU's or LLM's response
  "learn_entry": dict | None,        # For appending to smalltalk_learn.jsonl
  "confidence": float                 # 0.0-1.0
}
```

**Storage (PORTAL):**
- Append to: `~/.stillwater/orchestration/smalltalk/smalltalk_learn.jsonl`
- Format: One JSON line per entry
- Merging: At next CPU startup, load + filter by confidence > 0.70

---

### Phase 2: Intent Twin Validator

**Input:**
```python
{
  "intent_match": IntentMatch,       # CPU's wish match (or None if no match)
  "prompt": str,
  "session_context": dict,
  "extracted_keywords": list         # From CPU's extraction
}
```

**HANDSHAKE:**
- Read full prompt: "Does wish_id match the user's actual intent?"
- If CPU matched: Confirm or override the wish_id
- If CPU missed: Figure out what wish they need

**Decision Logic:**
```python
if intent_match is None:
  # CPU couldn't find a wish
  decision = "FIGURE_OUT"
  llm_wish = infer_wish_from_context(prompt, full_history)
  learned = {
    "keywords": extracted_keywords + llm_discovered_keywords,
    "wish_id": llm_wish.id,
    "skill_pack_hint": llm_wish.skill_pack_hint,
    "confidence": llm_confidence,
    "source": "phase2_validator",
    "timestamp": now()
  }

elif llm_confidence_override > 0.80:
  if llm_wish_differs_from_cpu_match:
    decision = "OVERRIDE"
    learned = new_wish_mapping(...)
  else:
    decision = "CONFIRM"
    learned = None

else:
  decision = "CONFIRM"
  learned = None
```

**Storage (PORTAL):**
- Append to: `~/.stillwater/orchestration/intent/learned_wishes.jsonl`
- Merging: At startup, rebuild keyword_index from main wishes + learned entries

---

### Phase 3: Execution Twin Validator

**Input:**
```python
{
  "execution_match": ExecutionMatch,  # CPU's combo match (or None)
  "wish_id": str,
  "session_context": dict
}
```

**HANDSHAKE:**
- "Is this swarm+recipe right for this wish?"
- If CPU matched: Confirm
- If CPU missed: Figure out swarm+recipe needed

**Decision Logic:**
```python
if execution_match is None:
  decision = "FIGURE_OUT"
  llm_swarm = infer_swarm_from_wish(wish_id, session_context)
  learned = {
    "wish_id": wish_id,
    "swarm": llm_swarm.name,
    "recipe": llm_swarm.recipe,        # ["prime-safety", "skill1", "skill2"]
    "confidence": llm_confidence,
    "source": "phase3_validator",
    "timestamp": now()
  }

elif llm_confidence_override > 0.90:
  if llm_combo_differs:
    decision = "OVERRIDE"
    learned = new_combo(...)
  else:
    decision = "CONFIRM"
    learned = None

else:
  decision = "CONFIRM"
  learned = None
```

**Storage (PORTAL):**
- Append to: `~/.stillwater/orchestration/execute/learned_combos.jsonl`
- Merging: At startup, merge (higher confidence overrides)

---

## Cost Control Strategy (Q-016)

**Rate Limiting Rule:**
```python
# Skip expensive haiku validator if CPU is already confident
if cpu_phase_match.confidence > 0.50:
  # CPU confident: ~50% probability skip validator
  skip_with_probability(0.5)  # Save 50% of validator calls
else:
  # CPU uncertain: always validate (need LLM guidance)
  run_validator()
```

**Expected Cost Impact:**
- Without rate limit: 1 haiku per request = ~$0.001 per request
- With rate limit: ~0.5 haiku per request = ~$0.0005 per request
- **50% cost reduction while maintaining learning signal**

---

## Hybrid Storage: Local + GCS Sync

### Local Side (CLI)
```
~/.stillwater/orchestration/
├── smalltalk/smalltalk_learn.jsonl
├── intent/learned_wishes.jsonl
└── execute/learned_combos.jsonl
```

### Cloud Side (solaceagi.com)
```
GCS: gs://solaceagi-learning/{user_id}/
├── smalltalk_learn.jsonl
├── learned_wishes.jsonl
└── learned_combos.jsonl
```

### Sync Strategy
```
Local writes → GCS (background, non-blocking)
Cloud writes → Local on next session start (or on-demand)
Conflict → last-write-wins (timestamp)
Offline → No GCS writes; continue locally. Merge on reconnect.
```

---

## Multi-User Learning: Shared + Private Layers

### Shared Layer (Global)
```jsonl
// In solaceagi.com GCS, public to all users
// Only high-confidence patterns (confidence > 0.85)
{"keywords": ["died", "lost"], "action": "suppress_humor", "confidence": 0.95}
```

### Private Layer (Per-User)
```jsonl
// In user's ~/.stillwater/, user-specific
// Lower-confidence overrides (confidence <= 0.85)
{"keywords": ["project-xyz-failed"], "action": "encourage", "confidence": 0.60}
```

### Merge at Startup
```python
# 1. Load shared patterns (confidence > 0.85)
shared_patterns = load_gcs_shared_layer()

# 2. Load user's private overrides
private_patterns = load_local_learned()

# 3. Merge: private overrides shared on conflict
merged = {**shared_patterns, **private_patterns}

# 4. Gate: only use if confidence > phase_threshold
learned_rules = {k: v for k, v in merged.items() if v["confidence"] > THRESHOLD}
```

---

## Verification Strategy (Q-018, Q-020)

### Test 1: Convergence (50 Sessions)
```python
# Session 1-50: Measure CPU accuracy over time
accuracy_by_session = []
for session in range(1, 51):
    warm = cpu.generate(...)
    llm_validation = validator.check(warm)
    override_rate = (llm_validation.decision == "OVERRIDE") / 10
    accuracy_by_session.append(1.0 - override_rate)

# Check convergence: should improve from ~0.60 to ~0.80+
assert accuracy_by_session[5] > 0.60   # Early sessions
assert accuracy_by_session[-1] > 0.80  # Later sessions
print(f"Convergence: {accuracy_by_session[5]:.2f} → {accuracy_by_session[-1]:.2f}")
```

### Test 2: Learned Patterns Growth
```python
# Measure: How many unique patterns learned?
# Measure: Are patterns reused (same keywords, different sessions)?
unique_keywords = set()
pattern_reuse_count = 0

for entry in load_jsonl("learned_wishes.jsonl"):
    keywords = tuple(sorted(entry["keywords"]))
    if keywords in seen_keywords:
        pattern_reuse_count += 1
    seen_keywords.add(keywords)

print(f"Unique patterns: {len(unique_keywords)}")
print(f"Pattern reuse: {pattern_reuse_count}% (target > 30%)")
```

### Test 3: A/B Test (Learned vs Non-Learned)
```python
# Run identical prompt through CPU with + without learned entries
identical_prompts = ["I got promoted!", "My project failed", "Can you help?"]

for prompt in identical_prompts:
    cpu_no_learned = SmallTalkCPU(use_learned=False)
    cpu_with_learned = SmallTalkCPU(use_learned=True)

    token1 = cpu_no_learned.generate(prompt)
    token2 = cpu_with_learned.generate(prompt)

    diff = levenshtein_distance(token1.response, token2.response)
    print(f"Prompt: '{prompt}' → Difference: {diff} chars")
```

---

## CLI User Visibility (Q-005, Q-006)

### Local Learned Admin
```bash
# View learned entries
$ stillwater admin learned list --phase smalltalk
Keywords: died, lost, passed
Action: suppress_humor
Tone: compassionate
Confidence: 0.95
Source: phase1_validator
Learned: 2026-02-23T12:34:56Z

# Delete a learned entry if it's causing bad behavior
$ stillwater admin learned delete --phase smalltalk --keywords "died,lost"

# Export for backup
$ stillwater admin learned export --output my_learned.jsonl
```

### solaceagi.com Dashboard
```
Settings → Learning
├─ Shared Patterns (Read-only)
│  └─ 47 high-confidence global patterns
├─ Your Overrides (Editable)
│  └─ 12 private patterns
│     - suppress_humor on death keywords (0.95)
│     - encourage on project-xyz-fail (0.60)
│     [Delete] [Adjust Confidence]
└─ Statistics
   └─ Override rate: 15% (down from 40% at start)
      Accuracy trending: 60% → 78%
```

---

## Implementation Roadmap (MVP Scope)

### Phase A: Core Architecture (Week 1)
- [ ] Define Haiku validator skeleton (3 phases)
- [ ] Implement learned_*.jsonl append logic
- [ ] Implement CPU merge logic at startup
- [ ] Implement confidence gating (phase-specific thresholds)

### Phase B: Storage + Sync (Week 2)
- [ ] Local learned_*.jsonl files
- [ ] GCS upload job (background, non-blocking)
- [ ] Last-write-wins conflict resolution
- [ ] Opt-in CLI sync to solaceagi.com

### Phase C: Testing (Week 3)
- [ ] 50-session convergence test
- [ ] Pattern growth measurement
- [ ] A/B test (learned vs non-learned)
- [ ] Cost tracking (validator calls/skipped)

### Phase D: Observability (Week 4)
- [ ] CLI admin commands (list, delete, export)
- [ ] solaceagi.com API endpoints (/api/v1/learned/*)
- [ ] Metrics dashboard (override rate, accuracy trend)

---

## Success Criteria (Rung 641)

- ✓ All three validators implement HANDSHAKE + PORTAL + SUBSTRATE
- ✓ learned_*.jsonl files append without locking
- ✓ CPU merges at startup with confidence filtering
- ✓ Convergence test: accuracy 60% → 80%+ in 50 sessions
- ✓ Cost reduction: 50% fewer haiku calls via confidence gating
- ✓ No network on CPU hot path (all merge logic offline)
- ✓ Deterministic: learned entries reproducible, no randomness

---

## References

- Paper #51: CPU-LLM Twin Feedback Loop Architecture
- Paper #49: Three Pillars (LEK/LEAK/LEC)
- Paper #44: Questions as External Weights
- phuc-leak.md: LEAK (Asymmetric Knowledge Transfer)
- phuc-portals.md: PORTAL Protocol (HANDSHAKE/TEMPERATURE/SUBSTRATE)
- phuc-qa.md: Four-Phase QA Discipline
- prime-mermaid.md: State machine diagrams

---

**Status:** APPROVED FOR IMPLEMENTATION
**Rung Target:** 641 ✓
**Next Action:** Build Phase A (Haiku validators skeleton)
