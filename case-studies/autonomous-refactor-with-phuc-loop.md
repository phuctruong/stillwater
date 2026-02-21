# Autonomous Refactoring Campaign With Phuc-Loop

**Date:** 2026-01-28  
**Stillwater skills loaded:** `phuc-loop v1.0.0`, `prime-coder v2.0.2`, `prime-safety v2.1.0`, `phuc-swarms v1.x`  
**Codebase:** Django REST API, 47 files, ~11,200 lines of Python, legacy auth layer  
**Author:** Tobias Renschler, staff engineer at a mid-stage fintech  
**One-line summary:** Used phuc-loop to run a fully autonomous refactoring campaign over 12 iterations; achieved halting certificate (failing tests = 0) without human intervention between iterations.

---

## 0) Honest executive summary

This is the most technically involved Stillwater workflow I've used. It worked — we got to a halting certificate — but the path had real friction. Iterations 4 and 7 required manual intervention to unstick the loop. The AGENTS.md accumulation was genuinely useful: by iteration 8, the learnings file had enough context that the subagent could avoid failure patterns from earlier iterations.

What convinced me this was worth documenting: on a 47-file codebase, a human doing this refactor would have taken 3-4 days. The autonomous loop finished overnight (wall-clock ~14 hours, most of it waiting between iterations). The diff was clean enough that code review took 90 minutes instead of a full day.

What I'm honest about: "autonomous" means the loop ran without human input between iterations, not that no human was involved. Setup took 3 hours. Two iterations required me to unblock a stuck state. The final output required a human code review before merging.

---

## 1) Context

### 1.1 The problem

We had a Django REST Framework API that had accumulated 18 months of technical debt around authentication. The auth layer was originally written with Django's built-in session auth and later bolted with JWT. The resulting code had:

- Auth logic split across 6 different files with overlapping responsibilities
- 3 different places where user roles were checked, each using different patterns
- Custom middleware that duplicated behavior from DRF's authentication classes
- 14 failing tests (inherited from a previous engineer's partial refactor that was merged without completing)
- 0 tests for the JWT token refresh flow

The goal: refactor the auth layer into a coherent design, make all 14 failing tests pass, add JWT refresh tests, and do not break the 203 passing tests.

### 1.2 Why autonomous loop

I had the refactor scoped and designed (I'm a staff engineer; I knew what needed to happen). What I did not have was the time to execute 47 file changes across multiple sessions while maintaining context. My experience with Claude Code on large refactors was that context drift between sessions caused regressions I'd have to debug.

Phuc-loop's CNF (Context Normal Form) capsule isolation was the specific feature I wanted: each iteration sees a fresh, complete picture of the current state, not a degraded memory of where we started.

### 1.3 Starting state [A]

```
Failing tests: 14
Passing tests: 203
Test coverage: 67% (line)
Files with auth-related code: 6 entangled files
Files to be refactored (scope): 47 (auth + everything that imports auth)
```

---

## 2) Setup

### 2.1 Skills loaded (load order matters)

```
skills/prime-safety.md      # order 1: god-skill, wins all conflicts
skills/prime-coder.md       # order 2: evidence discipline
skills/phuc-swarms.md       # order 3: multi-agent roles (Scout/Solver/Skeptic)
skills/phuc-loop.md         # order 4: loop control
```

Added to CLAUDE.md:

```yaml
phuc_loop_config:
  loop_learnings_file: "AGENTS.md"
  loop_scratch_dir: "scratch/refactor-auth"
  halting_criterion:
    metric: failing_tests
    target: 0
    command: "python -m pytest tests/ -q --tb=no 2>&1 | tail -5"
  divergence_threshold: 3  # iterations without improvement → EXIT_DIVERGED
  max_iterations: 20
  verification_rung_target: 641  # local correctness; no benchmark claim
```

### 2.2 Initial AGENTS.md (seed state)

```markdown
# AGENTS.md — Auth Refactor Loop

## Goal
Refactor Django auth layer (47 files). Halting criterion: failing_tests == 0.
Do not break passing tests (currently 203).

## Constraints
- Lane A: never break a currently-passing test
- Lane A: never remove auth checks without replacing them
- Lane B: prefer minimal diffs per iteration
- Lane C: prioritize files with the highest failing-test correlation first

## Known state (iteration 0)
- Failing: 14 tests in tests/test_auth.py and tests/test_middleware.py
- Root cause hypothesis: auth middleware duplicates DRF authentication class; conflict causes intermittent 403s in tests

## Entanglement map (produced by Scout, iteration 0)
auth/middleware.py imports: utils.auth_helpers, models.user
auth/views.py imports: auth/middleware.py, auth/serializers.py  
auth/serializers.py imports: models.user, utils.jwt_utils
[... 12 more entanglement lines ...]

## Learnings
(empty at start)
```

### 2.3 Halting criterion registration

The phuc-loop skill requires a halting criterion to be declared before the loop starts. This is non-negotiable — the skill emits EXIT_BLOCKED if you try to start without one:

```yaml
halting_criteria:
  primary:
    metric: failing_test_count
    target: 0
    evaluation_command: "python -m pytest tests/ -q --tb=no 2>&1 | grep -E '^[0-9]+ (failed|passed)'"
    halting_certificate_type: EXACT  # residual == 0 → Lane A
  secondary:
    metric: passing_test_count
    constraint: ">= 203"  # never-worse: must not drop passing count
```

---

## 3) What happened (12 iterations)

### 3.1 Iteration 1 — Scout phase

**Subagent role:** Scout  
**Task:** Map all failing tests to their root causes; do not edit code.  
**CNF capsule included:** full repo tree, failing test output, entanglement map

Scout produced a structured root cause analysis:

```
Failing test cluster A (9 tests):
  Root cause: auth/middleware.py:process_request() calls request.user before 
  DRF's authentication classes have run. DRF sets request.user lazily on first
  access through the authentication flow. Middleware access short-circuits this.
  Fix: move middleware user check to process_view() or remove and use DRF permissions.

Failing test cluster B (5 tests):
  Root cause: utils/jwt_utils.py:decode_token() returns None on expired tokens
  instead of raising. Callers in views.py check `if user:` which passes for
  anonymous user objects. Null/zero confusion: None (no token) treated as valid.
  Fix: raise AuthenticationFailed on invalid/expired tokens; never return None.
```

[A] Scout correctly identified both root causes. The Null/zero confusion in cluster B matched the prime-coder Null_vs_Zero_Policy violation pattern exactly.

**AGENTS.md after iteration 1:**
```markdown
## Learnings (iteration 1, Scout phase)

[A] Root cause cluster A: middleware timing bug. process_request() fires before DRF auth.
[A] Root cause cluster B: decode_token() returns None on failure — null/zero confusion.
[C] Priority order: fix cluster B first (smaller change, foundational, cluster A may depend on correct user object)
[B] Entanglement: 11 files import from jwt_utils.py. Changing return contract affects all 11.
[A] CONSTRAINT ADDED: decode_token() must never return None. Must raise or return valid payload.
```

### 3.2 Iterations 2–3 — Cluster B fix

**Subagent role:** Solver (iteration 2), Skeptic (iteration 3)

Iteration 2 solver fixed `jwt_utils.py` and the 11 downstream callers. The change was:

- `decode_token()` now raises `jwt.InvalidTokenError` instead of returning `None`
- All 11 callers updated to catch the exception instead of checking truthiness

[A] After iteration 2: failing tests went from 14 to 7. Passing tests: 205 (net +2, the JWT refresh tests we added along the way).

Iteration 3 skeptic ran the test suite and produced a finding:

```
SKEPTIC FINDING: Two callers were updated but still have implicit None path:
  - auth/views.py:125: token = get_token_from_header(request)
  - The get_token_from_header() helper itself returns None on missing header.
  - This None propagates to decode_token(), which now raises, causing 500 instead of 401.
  Status: REGRESSION (was previously graceful 401, now 500 on missing header)
```

[A] This was a real regression introduced by the iteration 2 solver. The skeptic caught it. The skill's architecture (separate Solver and Skeptic subagents) is what found this.

**AGENTS.md after iteration 3:**
```markdown
## Learnings (iteration 3, Skeptic)

[A] get_token_from_header() still returns None. This is now a live regression.
[A] PATTERN: helpers that return None on missing data will cause regressions when
    callers are updated to not handle None. Fix helpers too, not just callers.
[B] Next solver must audit ALL token extraction helpers, not just decode_token callers.
[C] Consider a policy: any function in auth/ that can return None must be documented
    as "returns Optional" explicitly in type hints, or must raise.
```

### 3.3 Iteration 4 — Stuck state (manual intervention required)

Iteration 4 subagent attempted to fix `get_token_from_header()` but ran into a circular import: the function was in `utils/auth_helpers.py` which imported from `auth/middleware.py` which imported from `utils/auth_helpers.py`.

The subagent correctly identified the circular import and emitted `EXIT_BLOCKED stop_reason=INVARIANT_VIOLATION`. The loop stopped.

**Manual intervention:** I resolved the circular import by extracting the shared constants to a new `auth/constants.py`. This took 20 minutes. I updated AGENTS.md manually:

```markdown
## Learnings (iteration 4, manual unblock)

[A] Circular import: utils/auth_helpers.py <-> auth/middleware.py
[A] Resolution: extracted shared constants to auth/constants.py (new file)
[A] New file added to scope: auth/constants.py
[B] Watch for: any subagent that tries to import auth.middleware from utils/ will hit this again.
```

Then restarted the loop from iteration 5.

[A] Iterations 5-6 resolved cluster B entirely. After iteration 6: failing tests = 5.

### 3.4 Iterations 5–6 — Cluster A begins

After cluster B was resolved, the loop moved to cluster A (middleware timing).

The fix was to remove the custom middleware's user-fetching logic entirely and rely on DRF's `IsAuthenticated` permission class instead. This touched 8 more files.

[A] After iteration 6: failing tests = 5 (unchanged). The middleware fix introduced 5 new failures in tests that were testing the middleware behavior directly — these tests were now testing behavior that had been removed. They needed to be updated to test the DRF permission behavior instead.

**AGENTS.md learning:**
```markdown
[A] ITERATION 6: Removed middleware user-fetch. 5 tests now test deleted behavior.
[A] These tests must be updated to test IsAuthenticated permission class behavior.
[B] Do NOT just delete these tests — they cover real auth scenarios. Rewrite them.
[C] The new test target is: authenticated request passes, unauthenticated request returns 401.
```

### 3.5 Iterations 7–9 — Test rewrites and regression hunting

Iteration 7 rewrote the 5 middleware tests. New failing count: 3.

Iteration 7 also introduced a new failure: a management command (`auth/management/commands/rotate_tokens.py`) imported the old middleware directly and broke. The subagent did not have this file in scope.

**Manual intervention #2:** Added the management command to scope. Updated AGENTS.md. Restarted.

[A] This was the second manual intervention. In retrospect, the initial scope declaration should have used a broader import graph traversal to catch this.

Iterations 8-9 fixed the remaining 3 failures. After iteration 9: failing tests = 0.

### 3.6 Iterations 10–12 — Skeptic sweeps

With failing tests at 0, the loop did not halt immediately. The halting criterion (failing_tests == 0) was met, but the phuc-loop skill requires a halting certificate — a structured document that the criterion was met and a replay confirms it.

Iterations 10 and 11 were Skeptic sweeps:
- Iteration 10: re-ran tests with `--tb=long` to verify no coincidental passes
- Iteration 11: ran the test suite 3 times with different random ordering (`pytest --randomly-seed=X`)

[A] All 3 seeds passed. Passing tests: 210 (was 203 + 7 net new tests added by the refactor).

Iteration 12 produced the halting certificate:

```json
{
  "halting_certificate": "EXACT",
  "lane": "A",
  "metric": "failing_test_count",
  "final_value": 0,
  "target": 0,
  "constraint_met": {
    "passing_tests_never_worse": true,
    "passing_count_before": 203,
    "passing_count_after": 210
  },
  "replay_commands": [
    "python -m pytest tests/ -q --tb=short --randomly-seed=42",
    "python -m pytest tests/ -q --tb=short --randomly-seed=137",
    "python -m pytest tests/ -q --tb=short --randomly-seed=9001"
  ],
  "replay_results": ["210 passed in 23.4s", "210 passed in 22.9s", "210 passed in 23.1s"]
}
```

---

## 4) AGENTS.md — final state (showing accumulation)

The AGENTS.md file grew from 15 lines to 187 lines across 12 iterations. Key sections:

```markdown
# AGENTS.md — Auth Refactor Loop (FINAL, iteration 12)

## Goal [ACHIEVED]
Halting certificate: EXACT, Lane A. failing_tests = 0.

## Constraints
[unchanged from iteration 0]

## Critical Learnings (distilled, lane-typed)

### Lane A (Hard constraints — violations caused regressions)
1. decode_token() must never return None. Raise on failure. [added iteration 1]
2. Helpers that return None propagate through callers. Fix helpers, not just callers. [added iteration 3]
3. Circular imports block fixes. Extract shared constants first. [added iteration 4]
4. Management commands that import internal auth modules are in scope. Always run import graph traversal before declaring scope. [added iteration 8]
5. Never break a test that tests a real auth scenario. Rewrite, don't delete. [added iteration 6]

### Lane B (Strong preferences)
1. Fix null/zero confusion issues before structural issues. They're foundational. [iteration 1]
2. Prefer DRF built-ins over custom middleware where semantically equivalent. [iteration 5]
3. Always add explicit type hints to Optional-returning functions before refactoring callers. [iteration 3]

### Lane C (Heuristics — useful but not binding)
1. Cluster by test file, not by file being edited. Tests co-locate related failures. [iteration 1]
2. When a refactor adds files, add them to scope immediately, not next iteration. [iteration 8]

## Failure patterns avoided (by consulting learnings in later iterations)
- Iteration 9 Solver consulted learnings and pre-checked management commands before editing.
  This avoided a third manual intervention. [A: directly observed in iteration 9 trace]
- Iteration 11 Skeptic consulted learnings and used multi-seed replay (not just single-seed).
  This caught a test that passed with seed=0 but had a timing dependency with seed=137. [A]

## Files changed
47 files touched (as planned). 6 new files created (including auth/constants.py).
Largest single-iteration diff: iteration 5 (22 files). Smallest: iteration 10 (0 files, skeptic only).
```

---

## 5) Results

| Metric | Before | After | Lane |
|---|---|---|---|
| Failing tests | 14 | 0 | [A] |
| Passing tests | 203 | 210 | [A] |
| Iterations to halting certificate | — | 12 | [A] |
| Wall-clock time | — | ~14 hours | [A] |
| Manual interventions | — | 2 | [A] |
| Human code review time | estimated 8h | 1.5h | [B] estimated, 1.5h measured |
| AGENTS.md lines | 15 | 187 | [A] |

[B] Code review was faster because: (1) the diff was 47 files but the AGENTS.md explained every decision with a lane label, so reviewers knew what to trust vs scrutinize; (2) the halting certificate meant reviewers didn't have to manually verify test counts; (3) the skeptic phase had already reviewed the code.

[C] Estimate: for a human doing this refactor solo, 3-4 days of focused work. The autonomous loop converted that to 14 hours of wall clock time plus 3.5 hours of human time (3h setup + 2 manual interventions + 1.5h code review). Total human hours: ~3.5h. Net saving: [C] ~24-30 human-hours.

---

## 6) What didn't work / limitations

### 6.1 Scope declaration is hard to get right

We needed 2 manual interventions because files were out of scope. An import graph traversal at setup time would have caught both. The phuc-loop skill does not automate this — you have to run it yourself or specify scope conservatively (include too much rather than too little).

Lesson: run `python -c "import ast; ..."` import graph tooling before declaring scope.

### 6.2 Iteration 4's circular import stopped the loop

The skill correctly blocked on the circular import (Lane A violation: INVARIANT_VIOLATION). But "correctly blocked" still means a human had to show up and unblock it. If you're hoping for a fully autonomous overnight run with zero human involvement, plan for the possibility of a block.

### 6.3 Wall clock time is long for waiting

14 hours is competitive with a human, but it requires Claude Code to be running the whole time. We used a persistent tmux session. On iteration 6, the session dropped at 2am and we lost the iteration output (the AGENTS.md update was written, but the halting check wasn't saved). We re-ran iteration 6. Lesson: the AGENTS.md is durable state, but iteration artifacts in `scratch/` are ephemeral. Save them explicitly.

### 6.4 AGENTS.md grows; later iterations are slower

By iteration 10, AGENTS.md was 150 lines. The CNF capsule for each iteration includes the full AGENTS.md. This means iteration 10's context was ~3000 tokens heavier than iteration 1's. For a 20-iteration loop on a large codebase, this could become a problem. [C] I don't know what the practical limit is. The skill has a `witness_line_budget` parameter that can truncate, but we didn't hit it in 12 iterations.

### 6.5 What it cannot do

- It cannot make architectural decisions. The circular import was a structural problem that required human judgment to resolve correctly. The skill blocked; it did not guess a fix.
- It cannot evaluate whether a test that it rewrites is semantically equivalent to the original. We had to verify that manually in code review.
- It is not appropriate for greenfield work — it needs existing tests to use as a halting criterion. Without tests, you have no stopping condition.

---

## 7) How to reproduce it

### Prerequisites

```bash
# Stillwater repo checked out, skills in place
# Your project has pytest and a test suite with failing tests
mkdir -p scratch/my-refactor evidence
```

### Step 1: Initialize AGENTS.md

```bash
cat > AGENTS.md << 'EOF'
# AGENTS.md — <Your Refactor Name>

## Goal
<One sentence goal>. Halting criterion: failing_tests == 0.

## Constraints
- Lane A: never break a currently-passing test (count: <N>)
- Lane A: <your hard constraint>
- Lane B: prefer minimal diffs per iteration

## Known state (iteration 0)
- Failing: <count> tests
- Root cause hypothesis: <your hypothesis>

## Learnings
(empty at start)
EOF
```

### Step 2: Configure phuc-loop in CLAUDE.md

```yaml
phuc_loop_config:
  loop_learnings_file: "AGENTS.md"
  loop_scratch_dir: "scratch/my-refactor"
  halting_criterion:
    metric: failing_tests
    target: 0
    command: "python -m pytest tests/ -q --tb=no 2>&1 | tail -3"
  divergence_threshold: 3
  max_iterations: 20
  verification_rung_target: 641
```

### Step 3: Start the loop

In Claude Code:
```
Start the phuc-loop refactoring campaign using AGENTS.md and the config in CLAUDE.md.
Iteration 1 role: Scout. Do not edit code. Map all failing tests to root causes.
Write learnings to AGENTS.md before exiting.
Report: failing test count, Scout findings, AGENTS.md state.
```

### Step 4: Iterate

Each iteration prompt:
```
Start iteration <N> of the phuc-loop campaign.
Read AGENTS.md for current state and learnings.
Current failing test count: <count from iteration N-1 output>.
Role for this iteration: <Solver|Skeptic> (alternate, Skeptic on odd after initial Scout).
Apply learnings to avoid known failure patterns.
Write learnings to AGENTS.md before exiting.
Run halting criterion: python -m pytest tests/ -q --tb=no | tail -3.
If failing_tests == 0, initiate halting certificate protocol.
```

### Step 5: Halting certificate

When failing_tests == 0, the final Skeptic iteration produces the certificate. Save it:
```bash
cp evidence/convergence.json evidence/halting_certificate_FINAL.json
```

### Step 6: Human code review

Review the AGENTS.md learnings to understand what decisions were made and why.
The lane labels tell you what to trust vs verify manually.
