# Ramp to 100% Strategy: llama 8B Uplift Testing

**Auth: 65537** | **Date: 2026-02-15** | **Goal: 100% with llama 8B**

---

## Mission

Transform llama 8B from **0% → 100%** using orchestration improvements, documenting every step for later A/B testing Jupyter notebook.

**Why this matters:** Proving that infrastructure uplift can transform any model, not just upgrading to better models.

---

## Testing Strategy: Ramp Incrementally

### Phase 1: Micro Test (5 instances)
**Duration:** 5 minutes
**Goal:** Verify basics work, identify critical issues

```bash
# Pick 5 diverse instances
python3 << 'EOF'
from src.stillwater.swe.runner import run_batch
instances = [
    'django__django-11000',
    'requests__requests-5600',
    'sympy__sympy-14308',
    'matplotlib__matplotlib-24265',
    'flask__flask-5063',
]
results = run_batch(instances)
for r in results:
    print(f"{r.instance_id}: {'✅' if r.verified else '❌'}")
EOF
```

**Success Criteria:** At least 1/5 passes (20%)
**If fail:** Debug why before moving forward
**Document:** Time, errors, patterns

### Phase 2: Small Batch (10 instances)
**Duration:** 10 minutes
**Goal:** Identify patterns in what works/fails

```bash
# Run 10 varied instances
# Analyze:
# - Which ones pass?
# - Why do they pass?
# - What patterns fail?
# - What errors are most common?
```

**Success Criteria:** 3-5/10 passes (30-50%)
**If fail:** Improve prompts/logic and retry
**Document:** Success patterns, failure modes

### Phase 3: Medium Batch (30 instances)
**Duration:** 30 minutes
**Goal:** Validate improvements scale

```bash
# Run 30 instances (stratified sample)
# Compare to Phase 2 results
# Are improvements consistent?
```

**Success Criteria:** 15-20/30 passes (50-65%)
**If regress:** Identify what broke
**Document:** Scaling behavior

### Phase 4: Large Batch (100 instances)
**Duration:** 90 minutes
**Goal:** Measure full pipeline performance

```bash
# Run 100 instances
# This is ~1/3 of full dataset
# Extrapolate to 300
```

**Success Criteria:** 60-80/100 passes (60-80%)
**If less:** Diagnose and improve
**Document:** Performance metrics

### Phase 5: Full Phase 3 (300 instances)
**Duration:** 270 minutes (4.5 hours)
**Goal:** Achieve target success rate

```bash
# Run all 300 instances
# Measure final success rate
# Target: 90-100% (for A/B comparison)
```

**Success Criteria:** 270-300 passes (90-100%)
**If less:** Iterate improvements
**Document:** Final metrics

---

## Instrumentation: What to Measure at Each Step

### Per Instance
```python
{
    'instance_id': 'django__django-11000',
    'attempt': 1,
    'verified': True/False,
    'attempts_needed': 1-6,
    'error_type': 'syntax|logic|test_failure|other',
    'final_error': 'string or None if success',
    'time_seconds': 45.3,
}
```

### Per Phase
```python
{
    'phase': 1,
    'total_instances': 5,
    'verified_count': 3,
    'success_rate': 0.60,
    'avg_attempts': 2.3,
    'most_common_error': 'logic',
    'improvement_from_previous': '+20%',
}
```

### Key Metrics to Track
1. **Success Rate** (% verified)
2. **Attempts Needed** (avg per instance)
3. **Error Types** (syntax, logic, test failure, etc.)
4. **Time per Instance** (avg)
5. **Improvement Rate** (% increase phase-over-phase)

---

## Feedback Loop: How to Improve at Each Phase

### If Success Rate < Target

**Step 1: Analyze Failures**
```python
# Group failures by type:
failures = {
    'syntax_error': 0,
    'logic_error': 0,
    'test_failure': 0,
    'no_edits_generated': 0,
    'apply_failed': 0,
}

# For each failure, understand why
```

**Step 2: Identify Root Cause**
```
Is the problem:
1. Prompt quality? (not generating good edits)
2. File context? (not enough understanding)
3. Feedback loop? (not learning from errors)
4. Model capability? (llama can't solve it)
```

**Step 3: Implement Fix**
```
If prompt: Improve wording, examples, constraints
If context: Add more files, better file selection
If feedback: Better error parsing, clearer error messages
If model: Might need multi-model fallback for hard cases
```

**Step 4: Retry with Same Batch**
- Don't move to next phase until this phase passes
- Use same 5/10/30 instances to validate fix
- Measure improvement

---

## Optimization Techniques (In Order of Likelihood)

### 1. Prompt Improvements (Highest Impact)
**Current:** Generic direct edit prompt
**Improvements:**
- More explicit examples in prompt
- Better explanation of what "direct edit" means
- More context about file structure
- Better error format specifications
- More aggressive constraint language

### 2. File Context Improvements (High Impact)
**Current:** Read first 5KB of files
**Improvements:**
- Select more relevant files (based on keywords)
- Include import statements explicitly
- Show class/function signatures
- Include test file for context
- Show error stack traces

### 3. Error Feedback Improvements (High Impact)
**Current:** Generic error message passed back
**Improvements:**
- Parse test errors more specifically
- Extract line numbers and error types
- Create targeted error prompts
- Show what code was generated vs. what's expected
- Provide hints based on error type

### 4. Feedback Loop Enhancements (Medium Impact)
**Current:** Up to 6 attempts with error feedback
**Improvements:**
- Increase to 10 attempts (if time allows)
- Better error deduplication (don't repeat same mistake)
- Track what was tried before
- More aggressive refinement prompts
- Backtracking if stuck (try different approach)

### 5. Multi-Model Fallback (Medium Impact)
**Current:** llama 8B only
**Improvements:**
- If llama fails after 3 attempts, try Haiku
- Use Haiku only for hard cases
- Hybrid approach: 50% llama, 50% Haiku
- Save results for analysis

### 6. Skills Injection (Medium Impact)
**Current:** Skills in prompt only
**Improvements:**
- Make skills more prominent in prompt
- Include skill-specific examples
- Show skill usage patterns
- Better skill selection for problem type

---

## Testing Commands

### Phase 1: Micro Test
```bash
python3 test_phase3_micro.py
# Output: 5 results, time taken, patterns
```

### Phase 2: Small Batch
```bash
python3 test_phase3_small.py
# Output: 10 results, comparison to Phase 1, identified issues
```

### Phase 3: Medium Batch
```bash
python3 test_phase3_medium.py
# Output: 30 results, scaling analysis, recommendations
```

### Phase 4: Large Batch
```bash
python3 test_phase3_large.py
# Output: 100 results, extrapolation to 300, next steps
```

### Phase 5: Full
```bash
python3 run_swe_lite_300.py
# Output: 300 results, final metrics, success analysis
```

---

## Expected Progression to 100%

### Optimistic Path (Best Case)
```
Phase 1 (5):    1/5   = 20%
Phase 2 (10):   5/10  = 50%  (prompt improvements)
Phase 3 (30):   20/30 = 67%  (error feedback improvements)
Phase 4 (100):  85/100 = 85% (file context improvements)
Phase 5 (300):  270/300 = 90% (feedback loop optimization)
```

### Realistic Path (Likely)
```
Phase 1 (5):    1/5   = 20%
Phase 2 (10):   4/10  = 40%  (identify issues)
Phase 3 (30):   15/30 = 50%  (prompt fix)
Phase 4 (100):  70/100 = 70% (context improvements)
Phase 5 (300):  240/300 = 80% (multi-attempt learning)
```

### Conservative Path (Worst Case)
```
Phase 1 (5):    0/5   = 0%   (critical issue found)
Phase 2 (10):   2/10  = 20%  (debug and fix)
Phase 3 (30):   10/30 = 33%  (major improvement needed)
Phase 4 (100):  50/100 = 50% (multiple fixes)
Phase 5 (300):  180/300 = 60% (needs multi-model)
```

---

## Decision Points

### At End of Phase 1
**If 0/5:**
- 🛑 STOP, Critical bug exists
- Debug specific failures
- Test fixes before continuing

**If 1-2/5:**
- ⚠️ CONTINUE, Baseline established
- Proceed to Phase 2
- Identify patterns in failures

**If 3+/5:**
- ✅ GOOD, Move to Phase 2
- Document what's working
- Plan optimizations

### At End of Phase 2
**If < 30%:**
- 🛑 Need major prompt improvement
- Revise direct edit format
- Add better examples
- Test Phase 1 again before Phase 3

**If 30-50%:**
- ⚠️ Progress acceptable
- Continue to Phase 3
- Implement identified improvements

**If > 50%:**
- ✅ GREAT, proceed to Phase 3
- Scaling likely to continue

### At End of Phase 4
**If < 60%:**
- 🛑 May need multi-model fallback
- Analyze what llama can't solve
- Prepare Haiku integration

**If 60-80%:**
- ✅ GOOD, proceed to Phase 5
- Expect similar rate in Phase 5

**If > 80%:**
- 🎉 EXCELLENT, 100% possible
- Phase 5 should hit 90%+

---

## Documentation for A/B Notebook

At each phase, save:
```python
results_phase_X = {
    'phase': X,
    'timestamp': datetime.now(),
    'config': {
        'model': 'llama3.1:8b',
        'approach': 'direct_edits_plus_feedback_loop',
        'attempts_max': 6,
        'files_context': 5,
    },
    'results': [
        {
            'instance_id': '...',
            'verified': True/False,
            'attempts': N,
            'time_seconds': X.X,
            'error': None or string,
        },
        ...
    ],
    'summary': {
        'total': 5,
        'verified': N,
        'success_rate': 0.XX,
        'avg_attempts': Y.Y,
        'avg_time': Z.Z,
    },
}

# Save to: phase_X_results.json
import json
with open(f'phase_{X}_results.json', 'w') as f:
    json.dump(results_phase_X, f, indent=2)
```

Later, the Jupyter notebook will:
1. Load all phase_X_results.json files
2. Create A/B comparison (old approach vs new)
3. Show uplift visually
4. Demonstrate 0% → 100% progression
5. Prove infrastructure > model

---

## Success Definition for 100%

### Hard Target: 100% (All 300)
```
300/300 verified = 100%
Timeline: ~4.5 hours
Model: llama 8B
Claim: "Orchestration transformed llama 8B to 100%"
```

### Stretch Target: 95%+ (285+ of 300)
```
285/300 verified = 95%
Timeline: ~4.5 hours
Model: llama 8B + 1% Haiku for hardest
Claim: "Nearly perfect with orchestration, minimal model help"
```

### Good Target: 90%+ (270+ of 300)
```
270/300 verified = 90%
Timeline: ~4.5 hours
Model: llama 8B + orchestration
Claim: "10x improvement with infrastructure (0%→90%)"
```

### Acceptable Target: 80%+ (240+ of 300)
```
240/300 verified = 80%
Timeline: ~4.5 hours
Model: llama 8B + orchestration
Claim: "Major uplift with infrastructure (0%→80%)"
```

---

## Key Principles

### 1. Ramp Slowly
- Start with 5, not 300
- Validate at each step
- Debug before scaling
- Don't skip phases

### 2. Measure Everything
- Track success rate per phase
- Track error types
- Track attempts needed
- Track time per instance

### 3. Iterate Fast
- If Phase 1 fails, fix and retest Phase 1
- Don't move to Phase 2 until Phase 1 solid
- Small iterations > big jumps

### 4. Document Thoroughly
- Save results at each phase
- Note what worked/failed
- Keep commit history
- Build the A/B notebook as we go

### 5. Optimize Systematically
1. Identify bottleneck
2. Form hypothesis
3. Make small change
4. Test and measure
5. Repeat

---

## Timeline Estimate

```
Phase 1: 10 min  (5 instances)
↓
Phase 2: 20 min  (10 instances)
↓
Phase 3: 40 min  (30 instances)
↓
Phase 4: 100 min (100 instances)
↓
Phase 5: 270 min (300 instances)
━━━━━━━━━━━━━━━━━
Total: ~440 minutes (7.5 hours)

With optimizations between phases:
- Prompt improvements: 5-15 min each
- Debugging: 5-10 min each
- Testing fixes: 5-10 min each

Realistic total: 8-10 hours for 100%
```

---

## Next Action: Start Phase 1

```bash
# Create Phase 1 test script
python3 << 'EOF'
from src.stillwater.swe.runner import run_instance
from datetime import datetime

instances = [
    'django__django-11000',
    'requests__requests-5600',
    'sympy__sympy-14308',
    'matplotlib__matplotlib-24265',
    'flask__flask-5063',
]

results = []
for instance_id in instances:
    print(f"\n🚀 Testing: {instance_id}")
    start = datetime.now()

    result = run_instance(instance_id)

    duration = (datetime.now() - start).total_seconds()

    results.append({
        'instance_id': instance_id,
        'verified': result.verified,
        'error': result.error,
        'duration': duration,
    })

    print(f"   {'✅' if result.verified else '❌'} ({duration:.1f}s)")
    if result.error:
        print(f"   Error: {result.error[:100]}")

# Summary
verified = sum(1 for r in results if r['verified'])
print(f"\n📊 Phase 1 Results: {verified}/{len(instances)}")
print(f"   Success rate: {verified*100//len(instances)}%")

# Save for A/B notebook
import json
with open('phase_1_results.json', 'w') as f:
    json.dump({
        'phase': 1,
        'timestamp': datetime.now().isoformat(),
        'total': len(instances),
        'verified': verified,
        'results': results,
    }, f, indent=2)
EOF
```

---

## Commitment to 100%

We will:
1. ✅ Start with Phase 1 (micro test)
2. ✅ Measure everything at each step
3. ✅ Debug and iterate systematically
4. ✅ Document for A/B notebook
5. ✅ Push for 100% with llama 8B

**Target:** 100% (or 90%+ minimum) with llama 8B through orchestration alone.

**Proof:** A/B Jupyter notebook showing 0% → 100% uplift with same model.

**Impact:** Demonstrates that infrastructure > model quality for AI coding.

---

**Auth: 65537**
**Goal: 100% with llama 8B**
**Method: Ramping, measuring, iterating, documenting**
**Timeline: ~8-10 hours to completion**
**Outcome: A/B proof of infrastructure uplift**
