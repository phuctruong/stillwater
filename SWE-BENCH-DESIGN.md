# SWE-bench Strategy: Verification Gates for Perfect Patches

> **Channeling**: Phuc Forecast + 65537 Experts + Max Love + God + Greg Isenberg + Top AI Podcasters

## 🎯 The Thesis (Greg Isenberg's Framing)

**"We're the only ones who REFUSE to ship bad code."**

Every other AI coding assistant generates patches and hopes they work.
We **mathematically verify** patches before they touch your codebase.

**The hook**: "What if your AI couldn't push broken code?"

---

## 🔥 The Problem (Phuc Forecast Analysis)

**Current state-of-the-art** (OpenAI Devin, Cursor, Copilot):
- Generate patches
- Hope they work
- Pray tests pass
- Ship and pray 🙏

**Result**: ~50% success rate on SWE-bench (GPT-4)

**Why they fail**:
1. No verification before applying patch
2. No rollback if tests fail
3. No state machine validation
4. No proof certificate

---

## ⚡ The Solution (65537 Expert Council)

### Red-Green Gate Protocol

**Three-stage verification** inspired by TDD:

```
Stage 1: PRE-CHECK (Red Gate)
├─ Run existing tests BEFORE patch
├─ Establish baseline (which tests pass)
└─ GATE: If tests fail → environment broken, abort

Stage 2: PATCH (Green Attempt)
├─ Apply candidate patch
├─ Run existing tests AGAIN
└─ GATE: If tests regress → reject patch

Stage 3: VERIFY (God Approval)
├─ Check patch determinism (same input → same patch)
├─ Generate proof certificate
└─ GATE: If non-deterministic → reject
```

**Critical insight**: We catch bad patches BEFORE they enter the codebase.

---

## 🏗️ Architecture (God's Blueprint)

```
┌──────────────────────────────────────────────────────┐
│ SWE-bench Instance                                   │
│ ├─ problem_statement                                 │
│ ├─ repo (git clone)                                  │
│ ├─ base_commit                                       │
│ ├─ test_patch (how to run tests)                    │
│ └─ gold_patch (ground truth - not shown to model)   │
└──────────────────────────────────────────────────────┘
           ↓
┌──────────────────────────────────────────────────────┐
│ STAGE 1: Environment Setup + Red Gate               │
│ ├─ Clone repo at base_commit                        │
│ ├─ Apply test_patch (sets up test environment)      │
│ ├─ Run tests → capture PASSING_BASELINE             │
│ └─ GATE: If fail → instance broken, skip            │
└──────────────────────────────────────────────────────┘
           ↓
┌──────────────────────────────────────────────────────┐
│ STAGE 2: Patch Generation (LLM)                     │
│ ├─ Load problem_statement                           │
│ ├─ Explore codebase (grep, read, understand)        │
│ ├─ Generate candidate patch (unified diff)          │
│ └─ OUTPUT: model_patch (our solution)               │
└──────────────────────────────────────────────────────┘
           ↓
┌──────────────────────────────────────────────────────┐
│ STAGE 3: Green Gate (Verification)                  │
│ ├─ Apply model_patch to repo                        │
│ ├─ Run tests → capture PASSING_WITH_PATCH           │
│ ├─ Compare: PASSING_WITH_PATCH >= PASSING_BASELINE  │
│ └─ GATE: If tests regress → REJECT                  │
└──────────────────────────────────────────────────────┘
           ↓
┌──────────────────────────────────────────────────────┐
│ STAGE 4: Determinism Check                          │
│ ├─ Run same instance 3x → must produce same patch   │
│ ├─ SHA256(patch_1) == SHA256(patch_2) == ...        │
│ └─ GATE: If different → non-deterministic, warn     │
└──────────────────────────────────────────────────────┘
           ↓
┌──────────────────────────────────────────────────────┐
│ STAGE 5: Certificate Generation                     │
│ ├─ Baseline tests: [test1, test2, ...]  (PASSING)   │
│ ├─ After patch: [test1, test2, test3]   (PASSING)   │
│ ├─ New tests fixed: [test3]                         │
│ ├─ Regressions: []                                   │
│ └─ Status: VERIFIED ✅                               │
└──────────────────────────────────────────────────────┘
```

---

## 📊 Success Metrics (Forecast-Driven)

### Primary Metric: **Verified Accuracy**
- % of patches that pass verification gates
- % of patches that fix the issue WITHOUT breaking tests
- % of patches that are deterministic

### Secondary Metrics:
- Execution time per instance
- Patch generation latency
- Test suite run time

### Comparison Baseline:
| Approach | Accuracy | Verification | Deterministic |
|----------|----------|--------------|---------------|
| GPT-4 (raw) | ~50% | ❌ No | ❌ No |
| Devin | ~45% | ❌ No | ❌ No |
| **Stillwater** | **TBD** | ✅ Red-Green | ✅ Yes |

**Target**: 85%+ accuracy with 100% verification

---

## 🎬 Demo Flow (Podcast-Ready)

**The 60-second pitch**:

1. **Show the problem** (15s)
   ```
   "SWE-bench: 300 real GitHub issues. Fix the bug. Pass the tests."
   "GPT-4: 50% accuracy. Half the patches break things."
   ```

2. **Show our gates** (20s)
   ```
   "We run THREE gates before accepting a patch:
    1. Red: Tests must pass BEFORE patch
    2. Green: Tests must pass AFTER patch
    3. God: Patch must be deterministic"
   ```

3. **Show the result** (15s)
   ```
   "Result: VERIFIED patch with proof certificate.
    Tests before: [✓ test_foo, ✓ test_bar]
    Tests after:  [✓ test_foo, ✓ test_bar, ✓ test_baz]
    Regressions: ZERO"
   ```

4. **The kicker** (10s)
   ```
   "We're the only AI that REFUSES to ship broken code.
    Certificate included. Math-verified. Zero regressions."
   ```

**Viral potential**: Side-by-side comparison video
"GPT-4 breaks your tests. Stillwater doesn't. Here's why."

---

## 🔧 Implementation Plan (Ship Fast Strategy)

### Phase 1: Minimal Harness (Week 1)
- [ ] SWE-bench dataset loader
- [ ] Docker container setup (or local git clone)
- [ ] Red Gate: Run tests, capture baseline
- [ ] Patch applicator
- [ ] Green Gate: Run tests, verify no regression

**Goal**: Run 1 instance end-to-end with manual patch

### Phase 2: LLM Integration (Week 2)
- [ ] Problem statement → LLM prompt
- [ ] Codebase exploration (grep, read files)
- [ ] Patch generation (unified diff format)
- [ ] Integration with gates

**Goal**: Generate patches automatically

### Phase 3: Verification + Cert (Week 3)
- [ ] Determinism check (3x same instance)
- [ ] Certificate generation (JSON format)
- [ ] Proof hashing (SHA256 artifacts)

**Goal**: Math-verified patches with certificates

### Phase 4: Scale to 300 (Week 4)
- [ ] Batch runner (process all 300 instances)
- [ ] Progress tracking (resume on failure)
- [ ] Result aggregation
- [ ] Leaderboard comparison

**Goal**: Full benchmark run, publish results

---

## 🧠 Key Innovations (What Makes This Different)

### 1. **Red-Green Protocol**
Borrowed from TDD, applied to AI code generation.

**Before Stillwater**: Generate patch → cross fingers
**After Stillwater**: Verify environment → generate patch → verify patch → ship

### 2. **State Machine Validation**
Patches must transition from:
```
State: Tests Passing (baseline)
  ↓ (apply patch)
State: Tests Passing (with fix)
```

Invalid transitions:
```
Tests Passing → Tests Failing  (REJECT - regression)
Tests Failing → Tests Failing  (REJECT - didn't fix)
```

### 3. **Proof Certificates**
Every accepted patch comes with:
```json
{
  "instance_id": "django__django-12345",
  "baseline_passing": ["test_foo", "test_bar"],
  "after_patch_passing": ["test_foo", "test_bar", "test_baz"],
  "regressions": [],
  "new_fixes": ["test_baz"],
  "determinism_verified": true,
  "patch_hash": "sha256:abc123...",
  "status": "VERIFIED"
}
```

### 4. **Deterministic Generation**
Same input → same patch (mathematically provable)

**How**: Use temperature=0, seed, and verify 3x

---

## 💡 Pro Tips from 65537 Experts

### Tip #1: **Filter instances by test infrastructure**
Some SWE-bench instances have flaky tests or broken Docker images.

**Strategy**: Pre-validate the "hardest 10" + 118 infrastructure-resilient instances
**Why**: Focus on clean signal, not test flakiness

### Tip #2: **Use git worktrees for isolation**
Don't pollute main repo with patches.

```bash
git worktree add /tmp/sweb-instance-123 base_commit
# Work in isolated worktree
git worktree remove /tmp/sweb-instance-123
```

### Tip #3: **Cache test results**
Running tests is slow. Cache baseline results per instance.

```
baseline_cache/
  ├─ django__django-12345.json  (passing tests)
  ├─ requests__requests-5678.json
  └─ ...
```

### Tip #4: **Parallel execution**
Run multiple instances in parallel (different Docker containers).

**BUT**: Gate evaluation must be sequential per instance.

### Tip #5: **Fail fast**
If Red Gate fails (baseline tests broken), skip instance immediately.

**Why**: No point generating patches for broken environments.

---

## 📚 File Structure

```
src/stillwater/swe/
├─ __init__.py
├─ loader.py           # Load SWE-bench dataset
├─ environment.py      # Setup git repo, apply test_patch
├─ gates.py            # Red/Green/God gate logic
├─ patch_generator.py  # LLM → unified diff
├─ verifier.py         # Determinism checks
├─ certificate.py      # Generate proof certificates
└─ runner.py           # Batch orchestration

tests/
└─ test_swe.py         # Unit tests for SWE harness
```

---

## 🎯 Success Criteria (Max Love for Users)

### User Experience Goals:
1. **One command to run**: `stillwater bench swe`
2. **Clear output**: Progress bar, real-time status
3. **Proof certificates**: Every patch comes with verification
4. **Resume on failure**: Don't lose progress
5. **Explainable rejections**: "Patch rejected: test_foo regressed"

### Developer Experience Goals:
1. **Extensible gates**: Easy to add new verification rules
2. **Pluggable LLM**: Works with any model (Ollama, OpenAI, etc.)
3. **Local-first**: No cloud dependencies
4. **Deterministic**: Same input → same result

---

## 🚀 Go-to-Market (Isenberg Strategy)

### Phase 1: Proof of Concept
- Run "hardest 10" instances
- Show 100% verification (even if patches fail, gates work)
- Blog post: "How We Prevent Broken Code"

### Phase 2: Benchmark Run
- Full 300-instance evaluation
- Compare to GPT-4 baseline
- Leaderboard submission

### Phase 3: Viral Content
- YouTube video: Side-by-side comparison
- Twitter thread: "Thread: How AI breaks your tests (and how we don't)"
- Podcast tour: Lex Fridman, Dwarkesh, Latent Space

### Key Message:
> "We're not the fastest. We're not the cheapest.
> We're the only ones who mathematically prove our patches work."

---

## 🏁 Next Actions (Ship Fast)

**This week**:
1. Create `src/stillwater/swe/` directory
2. Implement dataset loader
3. Implement Red Gate (baseline test runner)
4. Test on 1 instance manually

**Next week**:
2. Add LLM patch generation
3. Implement Green Gate
4. Run on "hardest 10"

**Week 3**:
5. Add determinism checks
6. Generate certificates
7. Write documentation

**Week 4**:
8. Scale to 300 instances
9. Publish results
10. Launch 🚀

---

## 📖 Philosophy (God's Perspective)

**Perfect code** is:
1. **Deterministic**: Same input → same output
2. **Verified**: Mathematically proven correct
3. **Reversible**: Can rollback on failure
4. **Certified**: Comes with proof

**Stillwater doesn't guess. It proves.**

---

**Auth: 65537**
**Version: 1.0.0**
**Status: DESIGN COMPLETE → Ready for implementation**

---
