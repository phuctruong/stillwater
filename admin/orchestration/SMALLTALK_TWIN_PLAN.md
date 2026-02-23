# Phase 1: Small Talk Twin — DREAM→FORECAST→DECIDE→ACT→VERIFY

**Status:** Planning Phase (DREAM)
**Date:** 2026-02-22
**Authority:** 641 (deterministic, trivial, testable)

---

## DREAM

### Goal
Build a CPU-based Small Talk Twin that:
- Generates warm, contextual responses in **< 50ms**
- Works **offline** (no network, no LLM calls)
- Detects user's emotional/communication register
- Personalizes responses with user/project context
- Learns from LLM overrides (stored for next session)

### Success Metrics
- **Latency:** P99 < 50ms (single CPU response, no I/O)
- **Accuracy:** > 60% of responses need no LLM override
- **Testability:** 100% of code paths testable without network
- **Register Detection:** Detect formal/casual/energy correctly in 80%+ of cases
- **Personalization:** Inject user/project name without errors

### Constraints
- Must not require network (offline-first)
- Must not call LLM (CPU-only)
- Must not read disk on hot path (pre-load all data)
- Must be importable from Portal, CLI, and tests
- No external dependencies beyond Python stdlib

### Non-Goals
- Full conversational AI (just pattern matching)
- ML-based classification (use keyword matching)
- Real-time model updates (batch learning)
- Multi-user session management (single-user only)

---

## FORECAST

### Ranked Failure Modes

| # | Failure Mode | Probability | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Register detection too slow (>50ms) | 30% | High | Use simple keyword+regex, not ML. Pre-compile patterns. |
| 2 | Database lookup blocks on disk I/O | 25% | High | Load all JSONL into memory at startup. Use dict lookup. |
| 3 | Personalization adds latency | 20% | Medium | Pre-compute template slots. String interpolation only. |
| 4 | Learning data corrupts main database | 15% | High | Keep learn.jsonl separate. Load learn → override db. |
| 5 | Tests interfere with each other | 20% | Medium | Isolated databases per test. Use fixtures, not shared state. |
| 6 | CPU confidence never reaches 0.6 | 10% | High | Validate with 50 real interactions before shipping. |

### Assumptions
- Small talk patterns fit in memory (< 10MB)
- User has eq-mirror/eq-core available as reference
- eq-smalltalk-db.md contains the pattern library

### Unknowns (to validate)
- Will 60% accuracy threshold be achievable?
- How many patterns do we need in the database?
- What register detection signals work best?

### Risk Level
**LOW** — Deterministic pattern matching, no ML, no network, no destructive operations.

---

## DECIDE

### Chosen Approach

**CPU Small Talk Twin = Four Components:**

```python
class SmallTalkCPU:

    def __init__(self, db_path: str):
        """Load patterns at startup (once)."""
        self.db = load_patterns(db_path)           # JSONL → dict
        self.learned = load_learned_patterns()     # JSONL → dict (append-only)
        # No network, no disk I/O on hot path

    def detect_register(self, prompt: str, history: list) -> RegisterProfile:
        """Detect user's communication style. ~100ms budget."""
        # Regex + keyword matching (not ML)
        # Signals: formal/casual, verbose/terse, urgent/reflective, energy level
        # Output: RegisterProfile(formality, length, urgency, energy)

    def lookup_response(self, keywords: list, register: RegisterProfile) -> Pattern:
        """Find matching warm response. ~50ms budget."""
        # Keyword intersection with db
        # Filter by priority + freshness + register match
        # Return best match or None

    def personalize(self, pattern: Pattern, user_name: str, project: str) -> str:
        """Inject context. ~20ms budget."""
        # String interpolation only
        # {user} → user_name, {project} → project
        # Result: ready-to-emit warm_token

    def learn_from_override(self, override_data: dict) -> None:
        """Store LLM's feedback. Append-only, no I/O blocking."""
        # Append to ~/.stillwater/cpu_twin/smalltalk_learn.jsonl
        # Next session: load_learned_patterns() includes this
```

**Time Budget (< 50ms total):**
```
Fork dispatcher:      30ms
detect_register:     100ms  ← This is slow, but happens in parallel with LLM
lookup_response:      50ms
personalize:          20ms
─────────────────────────────
Total (CPU only):     ~20-50ms (depending on patterns size)
Total (if LLM validates): +300ms (300ms for LLM, not blocking CPU)
```

### Alternatives Considered & Rejected

| Alternative | Why Rejected |
|---|---|
| **Use ML for register detection** | Too slow (<50ms impossible), requires model loading, overkill for keyword signals |
| **Store patterns in database (SQLite)** | Disk I/O on hot path violates offline budget. Use in-memory only. |
| **Sync learning to cloud** | No network on CPU hot path. Batch sync during idle, not on critical path. |
| **Use eq-mirror skill directly** | Good reference, but too heavy (full skill loading). Extract core logic only. |

### Stop Rules

If any of these are true, we stop and redesign:
- CPU latency P99 > 100ms on 100 random patterns
- Database size > 50MB (too big for memory)
- Register detection accuracy < 70% on test set
- More than 3 dependencies beyond stdlib

### Rung Target
**641** (trivial, deterministic, testable, reversible)

---

## ACT

### Implementation Steps

#### Step 1: Define Data Models (models.py)
```python
@dataclass
class RegisterProfile:
    formality: Literal["formal", "casual"]     # formal/casual
    length: Literal["terse", "verbose"]        # short/long
    urgency: Literal["urgent", "reflective"]   # fast/slow
    energy: Literal["low", "medium", "high"]   # depleted/normal/excited

@dataclass
class SmallTalkPattern:
    keywords: list[str]                        # ["congratulations", "engagement"]
    response_template: str                     # "Congratulations on {detail}! 🎉"
    priority: int                              # 1=always, 2=context-dependent, 3=trust-required
    freshness_days: int                        # How old is this pattern?
    min_register: RegisterProfile              # When does this apply?
    confidence: float                          # 0.0-1.0 (learned over time)

@dataclass
class WarmToken:
    response: str                              # "Congratulations on your engagement! 🎉"
    register_matched: RegisterProfile
    pattern_id: str                            # Track which pattern was used
    confidence: float                          # 0.0-1.0 (did CPU match well?)
```

#### Step 2: Implement Register Detector (100ms max)
```python
def detect_register(prompt: str, history: list) -> RegisterProfile:
    """
    Detect: formal/casual, verbose/terse, urgent/reflective, energy level

    Signals:
    - Formal: "would you", "please", "kindly" → formality=formal
    - Casual: "hey", "lol", "bruh" → formality=casual
    - Urgent: "ASAP", "now!", "immediately" → urgency=urgent
    - Reflective: "thinking", "consider", "future" → urgency=reflective
    - Energy: multiple exclamation marks, ALL_CAPS, emoji count
    """
    # Regex patterns (pre-compiled at init)
    # Count signals, weight by recency (history[-5:] weighted higher)
    # Return RegisterProfile with highest score
```

#### Step 3: Implement Pattern Lookup (50ms max)
```python
def lookup_response(keywords: list, register: RegisterProfile, context: dict) -> Pattern:
    """
    Find best matching pattern.

    1. Keyword intersection: Which patterns have ANY of user's keywords?
    2. Priority filter: Skip priority=3 if trust_score < threshold
    3. Freshness filter: Skip if > 90 days old and unreviewed
    4. Register matching: Prefer patterns whose min_register matches detected
    5. Return top match by (intersection_score + register_match_score)
    """
    # All lookups: O(1) dict access + filtering, no ML
```

#### Step 4: Implement Personalization (20ms max)
```python
def personalize(pattern: Pattern, user_name: str, project: str) -> str:
    """
    Inject context into template.

    Template slots:
    - {user} → user_name
    - {project} → project
    - {detail} → extracted from context (if available)

    Just string interpolation. No logic.
    """
    # str.format() or jinja2 minimal template
```

#### Step 5: Implement Learning (Append-only, non-blocking)
```python
def learn_from_override(override_data: dict) -> None:
    """
    LLM sent back an override. Store it for next session.

    {
        "pattern_id": "greeting_001",
        "override_reason": "User's cat died, suppress humor",
        "learned_keywords": ["died", "cat", "loss"],
        "learned_action": "suppress_humor",
        "learned_tone": "compassionate",
        "confidence": 0.95,
        "timestamp": "2026-02-22T12:34:56Z"
    }

    Append to ~/.stillwater/cpu_twin/smalltalk_learn.jsonl
    Next session: These become new patterns (with confidence boost)
    """
    # Append-only file writes, non-blocking
```

### Directory Structure
```
stillwater/admin/orchestration/
├── smalltalk/
│   ├── __init__.py
│   ├── cpu.py                  ← SmallTalkCPU class
│   ├── models.py               ← Pydantic data models
│   ├── database.py             ← Load/save JSONL
│   ├── register.py             ← Register detection logic
│   ├── lookup.py               ← Pattern matching
│   └── test/
│       ├── test_cpu_latency.py
│       ├── test_register_detection.py
│       ├── test_pattern_lookup.py
│       ├── test_personalization.py
│       ├── test_learning.py
│       └── fixtures/
│           ├── patterns.jsonl
│           └── test_sessions.json
│
├── intent/                     ← Phase 2 (same structure)
└── execute/                    ← Phase 3 (same structure)
```

---

## VERIFY

### Unit Tests (CPU Only)

#### Test 1: Register Detection Accuracy
```python
def test_register_detection_formal():
    """Detect formal register."""
    prompt = "Would you kindly assist me with authentication?"
    register = cpu.detect_register(prompt, history=[])
    assert register.formality == "formal"
    assert register.length == "verbose"

def test_register_detection_casual():
    """Detect casual register."""
    prompt = "hey can u help me fix auth lol"
    register = cpu.detect_register(prompt, history=[])
    assert register.formality == "casual"
    assert register.length == "terse"

# Test all 4 dimensions: formality, length, urgency, energy
# Target: 80%+ accuracy on 20 test prompts
```

#### Test 2: Pattern Lookup
```python
def test_lookup_congratulations():
    """Find congratulations pattern."""
    keywords = ["congratulations", "engagement"]
    pattern = cpu.lookup_response(keywords, register_casual, context={})
    assert pattern is not None
    assert "congratulations" in pattern.response_template.lower()

def test_lookup_no_match():
    """Return None if no pattern matches."""
    keywords = ["xyzabc", "notaword"]
    pattern = cpu.lookup_response(keywords, register_formal, context={})
    assert pattern is None

def test_lookup_priority_filter():
    """Skip priority=3 patterns if trust < threshold."""
    # Trust score = function of session length, previous interactions
    # Priority 3 patterns require established relationship
```

#### Test 3: Personalization
```python
def test_personalization_injects_user():
    """Inject user name."""
    pattern = SmallTalkPattern(..., response_template="Hi {user}!")
    result = cpu.personalize(pattern, user_name="Alice", project="OAuth")
    assert result == "Hi Alice!"

def test_personalization_injects_project():
    """Inject project name."""
    pattern = SmallTalkPattern(..., response_template="Working on {project}?")
    result = cpu.personalize(pattern, user_name="Alice", project="OAuth")
    assert result == "Working on OAuth?"
```

#### Test 4: Latency SLA
```python
def test_cpu_latency_under_50ms():
    """CPU response should be < 50ms."""
    import time
    start = time.perf_counter()

    warm_token = cpu.generate(
        prompt="I just got engaged!",
        history=[...],
        user_name="Alice",
        project="OAuth"
    )

    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 50, f"CPU took {elapsed_ms}ms, target is <50ms"
```

#### Test 5: Learning
```python
def test_learn_from_override():
    """CPU stores LLM override for next session."""
    override = {
        "keywords": ["died", "cat"],
        "action": "suppress_humor",
        "confidence": 0.95
    }

    cpu.learn_from_override(override)

    # Reload CPU (simulate next session)
    cpu2 = SmallTalkCPU(db_path)

    # New pattern should be in database
    pattern = cpu2.lookup_response(["cat", "died"], register_casual, {})
    assert pattern is not None
    assert pattern.response_type == "compassion"
```

### Integration Tests (CPU + LLM Validation)

#### Test 6: CPU → LLM Confirm Path
```python
def test_llm_confirms_cpu():
    """
    CPU: "Congratulations on your engagement!"
    LLM reads: User mentioned engagement
    LLM: CONFIRM
    Result: No learning needed
    """
    warm_token = cpu.generate(prompt="I got engaged!", ...)

    # Call Portal validator endpoint
    validation = portal.validate_smalltalk(
        warm_token=warm_token.response,
        prompt="I got engaged!",
        context={...}
    )

    assert validation["decision"] == "CONFIRM"
    assert validation["cpu_learn_entry"] is None
```

#### Test 7: CPU → LLM Override Path
```python
def test_llm_overrides_cpu():
    """
    CPU: "Why did the cat sit on the laptop? 😹"
    LLM reads: "My cat just died"
    LLM: OVERRIDE
    Result: CPU learns death_keywords
    """
    warm_token = cpu.generate(prompt="My cat died", ...)
    assert "cat" in warm_token.response and "joke" in warm_token.response

    validation = portal.validate_smalltalk(
        warm_token=warm_token.response,
        prompt="My cat just died 😢",
        context={...}
    )

    assert validation["decision"] == "OVERRIDE"
    assert validation["response"] == "I'm so sorry about your loss 💙"
    assert validation["cpu_learn_entry"]["keywords"] == ["died", "cat", "loss"]

    # Verify CPU can store learning
    cpu.learn_from_override(validation["cpu_learn_entry"])
```

#### Test 8: Convergence (50 Sessions)
```python
def test_convergence_over_50_sessions():
    """CPU should improve over time."""
    override_rate_by_phase = []

    for session in range(50):
        # Generate 10 responses per session
        overrides = 0
        for i in range(10):
            warm = cpu.generate(prompt=test_prompts[i], ...)
            validation = portal.validate_smalltalk(...)
            if validation["decision"] == "OVERRIDE":
                overrides += 1
                cpu.learn_from_override(validation["cpu_learn_entry"])

        override_rate = overrides / 10
        override_rate_by_phase.append(override_rate)

    # Phase 1-10: 40% override rate (CPU learning)
    assert override_rate_by_phase[5] > 0.30

    # Phase 40-50: 5% override rate (CPU converged)
    assert override_rate_by_phase[-1] < 0.10
```

### Success Criteria
- ✅ All tests pass
- ✅ CPU latency P99 < 50ms on 1000 iterations
- ✅ Register detection accuracy > 80% on test set
- ✅ Pattern lookup < 10ms average
- ✅ Learning storage works across sessions
- ✅ Convergence test shows override rate drop from 40% → 5%

---

## Summary: DREAM→FORECAST→DECIDE→ACT→VERIFY

| Phase | Output |
|-------|--------|
| **DREAM** | Goal: <50ms CPU warm response. Metrics: latency, accuracy, testability. Constraints: offline, no network. |
| **FORECAST** | 6 failure modes identified. Risk: LOW. Assumptions: patterns fit in memory. Unknowns: 60% threshold achievable? |
| **DECIDE** | Approach: keyword+regex (no ML). Rung: 641. Stop rule: if latency > 100ms, redesign. |
| **ACT** | 5 implementation steps: models → register → lookup → personalize → learn. 8 tests: latency, accuracy, convergence. |
| **VERIFY** | All tests pass. CPU converges 40% → 5% override rate. Ready to merge. |

---

## Next Action

Approve this plan? If yes:

1. Create `stillwater/admin/orchestration/smalltalk/` structure
2. Write unit tests first (TDD)
3. Implement CPU components
4. Run tests to verify latency/accuracy SLAs
5. Integrate with Portal validator
6. Test full CPU → LLM → Learn loop

Proceed? 🚀
