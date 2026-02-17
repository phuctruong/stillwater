# STILLWATER - LLM Agent Framework for SWE-Bench

> **Project:** STILLWATER
> **Architecture:** 65537D OMEGA (F4 = 2^16 + 1)
> **Status:** ACTIVE
> **Northstar:** Phuc Forecast
> **Identity:** Solace (SWE-Bench Intelligence)
> **Auth:** 65537
> **Ecosystem:** PUBLIC (github.com/phuctruong/stillwater)
> **Memory Hub:** solace-cli (private, optional)
> **Registry:** See ECOSYSTEM_ARCHITECTURE.md in solace-cli

---

## MISSION

```
STILLWATER = LLM agent framework for SWE-Bench testing

Infrastructure > Model Quality

Built on:
  - Phuc Forecast (Northstar methodology)
  - 65537D OMEGA architecture
  - Prime channel memory system (2,3,5,7,11,13)
  - 5 weapons system (verification gates)
  - Haiku swarms (multi-agent coordination)
  - 100% pass rate methodology (never advance until phase is solid)

Goal: Build the most capable LLM agent framework for software engineering
```

---

## ECOSYSTEM INTEGRATION

**STILLWATER** is part of the **Phuc.Net ecosystem** - a distributed multi-project system with:
- **solace-cli** (PRIVATE): Memory hub, Channel 17 Q/A caching, orchestration
- **Public Projects**: stillwater, pzip, paudio, pvideo, solace-browser, phucnet, if

**This Repository:** Open-source SWE-Bench LLM framework (Channels 2-13 only)

**Accessing Memory Hub (Optional):**
```python
# Optional: Use semantic Q/A cache from solace-cli
try:
    from solace_cli.memory import QACache
    cache = QACache()
    # Look up past solutions to similar problems
    result = cache.ask("How to fix import errors in Python?")
    if result['cache_hit']:
        print(f"Found cached solution: {result['answer']}")
except ImportError:
    # Fallback: Work with local memory only
    pass
```

**NO proprietary code:** STILLWATER remains fully open-source with zero solace-cli dependencies.

---

## CORE PRINCIPLES (Unified)

### The 7 Axioms

| # | Axiom | Invariant |
|---|-------|-----------|
| 1 | **Generator > Data** | Don't store data. Store the function that produces it. |
| 2 | **Stillwater/Ripple** | Small generator + residuals: S << R. |
| 3 | **RTC** | Round-Trip Correctness: decode(encode(X)) = X. Always. |
| 4 | **Never-Worse** | If no improvement, fallback to baseline. Never harm. |
| 5 | **Type-Aware** | Different types need different approaches. |
| 6 | **Verification First** | Test edge cases before claims. |
| 7 | **Counter, Not LLM** | Code enumerates, LLMs interpolate. Use code. |

### Stillwater-Specific Principles

1. **Infrastructure > Model Quality** - Orchestration beats pure model capability
2. **Maintain 100%** - Don't advance until phase at 100%
3. **Fast Feedback** - Quick iterations for debugging
4. **Remote Only** - Always use remote Ollama (192.168.68.100:11434)
5. **Evidence Driven** - All decisions backed by test data

---

## PHUC FORECAST METHODOLOGY

Every decision in STILLWATER follows: **DREAM → FORECAST → DECIDE → ACT → VERIFY**

```
DREAM: Understand current benchmark state
  ├─ Load skills (51+ prime skills)
  ├─ Read memory channels (2,3,5,7,11,13)
  └─ Identify phase bottlenecks

FORECAST: Predict improvement from new approach
  ├─ Estimate pass rate increase
  ├─ Calculate confidence
  └─ Reference past phases

DECIDE: Choose implementation path
  ├─ Set success criteria (e.g., "95% phase pass rate")
  ├─ Define phase advancement rule
  └─ Approve with confidence score

ACT: Implement and test
  ├─ Deploy changes
  ├─ Run full phase test
  └─ Track metrics in real-time

VERIFY: Validate results
  ├─ Check against success criteria
  ├─ Measure final pass rate
  ├─ Update memory (Channel 7: CONTEXT)
  └─ Decide: advance to next phase or refine current
```

---

## QUICK START

### Setup

```bash
cd /home/phuc/projects/stillwater

# Load environment
source ~/.solace/env.sh

# Load skills
/load-skills

# Verify setup
python3 debug_5_weapons.py
```

### Test Commands

```bash
# Phase 1: Single instance
python3 test_1_instance_100pct.py

# Phase 2: Five instances
python3 test_5_instances_100pct.py

# Phase 3: Ten instances
python3 test_10_instances_100pct.py

# Check results
cat phase_*_instances.json | jq '.success_rate'
```

### Memory Commands

```bash
# Store session state
/remember phase="Phase 3"
/remember pass_rate="95.7%"

# Retrieve state
/remember list

# Clear memory
/remember clear
```

---

## MEMORY SYSTEM (Channels 2-13)

**Local Memory (Project-Specific):**

```
~/.claude/memory/
├── identity.json       # Channel 2: Project identity
├── goals.json          # Channel 3: Phase goals, benchmarks
├── decisions.json      # Channel 5: Locked rules, constraints
├── context.json        # Channel 7: Current phase, pass rates
├── blockers.json       # Channel 11: Known issues
└── haiku_swarms.json   # Channel 13: Agent assignments
```

**Optional: solace-cli Memory Hub (Channel 17)**

If solace-cli is available in the same environment:

```python
from solace_cli.memory import QACache

cache = QACache()
result = cache.ask("How to handle import errors in Python?")
# Returns cached solution if available, otherwise calls LLM
```

---

## 5 WEAPONS SYSTEM

The framework uses 5 verification weapons to achieve 100% pass rate:

```
Weapon 1: Code Generation
  - Generate solutions for SWE-bench instances
  - Verify against test suite

Weapon 2: Test-Driven
  - Tests drive implementation
  - Red-Green-Refactor cycle

Weapon 3: Agent Coordination
  - Multiple agents attacking same problem
  - Majority voting on solutions

Weapon 4: Fallback Strategy
  - Timeout detection
  - Alternative approaches

Weapon 5: Human Loop Integration
  - Review challenging cases
  - Feedback incorporation
```

---

## PHASE STRUCTURE

### Phase 1: 1 Instance (100%)
- Single SWE-bench instance
- Verify all 5 weapons work
- Debug individual components

### Phase 2: 5 Instances (100%)
- Small batch of instances
- Verify consistency
- Identify patterns

### Phase 3: 10 Instances (100%)
- Larger batch
- Scale agent coordination
- Measure performance

### Phase 4+: Full Suite (Target 100%)
- All remaining instances
- Production readiness
- Performance optimization

---

## CORE FILES

- `CLAUDE.md` ← THIS FILE (project directives)
- `.claude/CLAUDE.md` ← Complete configuration
- `debug_5_weapons.py` ← Verify all weapons
- `test_N_instances_100pct.py` ← Phase testing
- `.claude/memory/` ← Persistent session memory
- `canon/` ← Skills, knowledge, papers

---

## KEY METRICS

Track these across phases:

```json
{
  "phase": 3,
  "instances_total": 10,
  "instances_passed": 10,
  "pass_rate": 1.0,
  "avg_time_per_instance": 45.3,
  "weapons_enabled": [1,2,3,4,5],
  "blockers": [],
  "next_phase_ready": true
}
```

---

## SUCCESS CRITERIA

**Per Phase:**
- ✅ Pass rate ≥ 95%
- ✅ All weapons functional
- ✅ No timeout failures
- ✅ Reproducible results
- ✅ Clear path to next phase

**Overall:**
- ✅ 100% pass rate on full SWE-bench
- ✅ <1min average time per instance
- ✅ All 5 weapons optimized
- ✅ Production deployment ready

---

## DEVELOPMENT WORKFLOW

### Adding Feature

```bash
# Create branch
git checkout -b feature/weapon-6-optimization

# Implement with DREAM→FORECAST→DECIDE→ACT→VERIFY
# Run phase tests
python3 test_1_instance_100pct.py

# Commit (with phuc forecast narrative)
git commit -m "feat: Weapon 6 optimization

Phuc Forecast:
- DREAM: identified timeout bottleneck in weapon 5
- FORECAST: estimated 10% speed improvement
- DECIDE: add parallel execution
- ACT: implemented concurrent workers
- VERIFY: 10.2% speedup achieved, 100% pass rate maintained

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"

# Push to public GitHub
git push origin feature/weapon-6-optimization
```

### Testing Requirements

```bash
# Before committing: run full phase test
python3 test_1_instance_100pct.py  # Phase 1 must pass 100%
python3 test_5_instances_100pct.py # Phase 2 must pass 100%

# Result: All tests pass or don't commit
```

---

## CONTACTS & GOVERNANCE

**Architecture:** Solace (65537)
**Memory Hub:** solace-cli (private, optional)
**Public Repo:** github.com/phuctruong/stillwater
**Ecosystem:** See ECOSYSTEM_ARCHITECTURE.md in solace-cli

---

*"Infrastructure > Model Quality"*
*"Don't advance until phase is 100%"*
*"65537D OMEGA × Prime Channels"*
*"Auth: 65537 | Solace | 2026-02-16"*
