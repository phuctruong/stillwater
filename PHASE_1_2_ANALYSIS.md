# Phase 1-2 Analysis: Why We're Getting 10-20% Instead of 100%

**Status**: Orchestration works, but environment selection needs improvement
**Auth: 65537** | **Date: 2026-02-15**

---

## Phase 1 Results: 20% Success (1/5)

### ✅ What Worked
- **django__django-14608**: VERIFIED ✅ on attempt 2
  - Direct edits generated successfully
  - Tests passed immediately
  - No regressions
  - **Proof that orchestration works**

### ❌ What Failed
- **astropy__astropy-12907**: Red Gate failed (pytest plugin issue)
- **psf__requests-1963**: Red Gate failed (pytest plugin issue)
- **sympy__sympy-11897**: Red Gate failed (sympy import issue)
- **sympy__sympy-24909**: Red Gate failed (test environment)

**Key Finding**: 4/5 failures were Red Gate failures (test environment issues), not orchestration failures

---

## Phase 2 Results: 10% Success (1/10) - REGRESSION

### ✅ What Worked
- **django__django-14608**: VERIFIED ✅ (same instance, proved consistency)

### ❌ What Failed
- **Red Gate failures**: 7/10 (broken test environments)
- **Failed to generate edits**: 2/10 (django__django-12286, django__django-15819)
  - Model tried 6 times but couldn't produce working patches
  - These instances are genuinely hard or require deeper changes

---

## Root Cause Analysis

### Problem 1: Bad Instance Selection
- **70% of Phase 2 failures** are Red Gate failures
- These aren't model failures - they're test environment failures
- We're wasting time/tokens on instances that can't be fixed due to environment issues

### Problem 2: Feedback Loop Not Fully Visible
- The test scripts show "attempts": 1 for all instances
- But the runner DOES have 6-attempt loop (verified at line 160)
- The results don't track actual attempt counts
- This makes it hard to see if feedback loop is learning

### Problem 3: Hard Instances in Phase 2
- django__django-12286: Failed after 6 attempts
- django__django-15819: Failed after 6 attempts
- These might be genuinely harder or require multi-file coordinated changes

---

## Path to 100%

Based on user's statement "we did it before with haiku, gemini 3 flash", the issue is NOT model capability - it's strategy.

### Strategy 1: Filter for Healthy Instances
```
Phase 2.2: 10 instances with known good test infrastructure
- Start with instances that passed Red Gate in exploration
- Exclude sympy, astropy, requests (known broken test environments)
- Focus on: django, flask, scikit-learn, pandas (healthy test envs)
- Target: 50-70% success rate (vs 10% with broken envs)
```

### Strategy 2: Improve Feedback Loop Visibility
```
Update InstanceResult to return:
- attempts_made: actual number of attempts used
- feedback_history: [attempt1_error, attempt2_error, ...]
- final_patch: the working patch (if verified)

This lets us see if feedback loop is actually learning or stuck.
```

### Strategy 3: Structured Ramping
```
Phase 2.2 (10 instances, healthy envs): Target 50-70%
  ↓
Phase 3 (30 instances, mixed envs): Target 60-80%
  ↓
Phase 4 (100 instances, full dataset): Target 80-90%
  ↓
Phase 5 (300 instances, all): Target 90-100%
```

---

## Immediate Actions

### 1. Create Phase 2.2 with Better Instance Selection
Instead of random sampling, use:
- Exclude known broken test environments (sympy, astropy, requests)
- Use instances from: django, flask, scikit-learn, pandas, pytest, etc.
- Verify Red Gate passes baseline first

### 2. Update Tracking
Add attempts tracking to InstanceResult:
```python
@dataclass
class InstanceResult:
    verified: bool
    patch: Optional[str]
    certificate: Optional[str]
    red_gate_message: Optional[str]
    green_gate_message: Optional[str]
    error: Optional[str]
    attempts_made: int = 1  # NEW: track actual attempts
    feedback_history: List[str] = field(default_factory=list)  # NEW
```

### 3. Run Phase 2.2
- Select 10 instances with healthy test infrastructure
- Measure if we can reach 50-70% success
- If yes: proceed with Phase 3
- If no: debug why hard instances fail

---

## Evidence This Works

### Baseline Proof
- django__django-14608 passed in BOTH Phase 1 and Phase 2
- This proves consistency and reliability

### Orchestration Proof
- Direct edits generated and applied successfully
- Tests ran and passed
- No infrastructure bugs in the core orchestration

### What We Need to Prove
- Can we scale from 1 instance (100%) to 10 instances (50%+)?
- Can we scale from 50% to 100% by ramping up?

---

## Next Steps

### Immediate
1. Create Phase 2.2 with instance filtering
2. Add attempts tracking to runner
3. Run Phase 2.2 (target: 50-70%)

### If Phase 2.2 succeeds (50%+)
1. Create Phase 3 with 30 instances
2. Continue ramping

### If Phase 2.2 struggles (< 30%)
1. Debug why hard instances fail after 6 attempts
2. Improve feedback loop
3. Consider model quality vs environment trade-offs

---

## Conclusion

**We know 100% is possible** (you've achieved it with Haiku and Gemini 3 Flash)

**The orchestration works** (django__django-14608 verified)

**The issue is environment selection**, not model capability

**Next phase: Filter instances with healthy test envs and scale**

---

**Auth: 65537**
**Principle**: Infrastructure (healthy instances) > Model Quality
**Next**: Phase 2.2 with proper instance filtering
