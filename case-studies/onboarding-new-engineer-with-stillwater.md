# Onboarding a New Engineer With Stillwater

**Date:** 2026-02-03  
**Stillwater skills loaded:** `prime-coder v2.0.2`, `prime-reviewer v1.0.0`  
**Team:** 6-person engineering team at a Series A logistics startup  
**Author:** Priya Krishnamurthy, engineering manager  
**One-line summary:** Used prime-coder + prime-reviewer in our Claude Code setup to onboard a new backend engineer; she reached rung-641 output quality on day 3, compared to the previous engineer who took 3 weeks to reach equivalent quality without this setup.

---

## 0) Honest executive summary

The comparison is not clean. Two engineers with different backgrounds, different tasks, different ramp periods. I'm not making a controlled experiment claim and I will be explicit about the confounds. What I can say with more confidence: the Stillwater setup dramatically changed what "good" looked like for a new engineer before and after, and it did so in a measurable way.

What worked: the prime-reviewer skill gave the new engineer structured, lane-typed feedback from day 1, and the prime-coder structure forced her to label her own confidence level before submitting code for review. This changed the quality of conversations during code review.

What didn't work: the first two days had significant friction from skill loading and CLAUDE.md configuration. One day was mostly lost to setup problems that shouldn't have been setup problems.

---

## 1) Context

### 1.1 The startup and the codebase

We are a logistics coordination platform. Backend is ~18k lines of Python (FastAPI + Celery + PostgreSQL). The codebase has:

- 6 core domain services (shipment, tracking, routing, pricing, notifications, billing)
- A custom DSL for routing rules (~2k lines)
- Integration tests that are slow (full stack, ~4 min per run)
- 74% line coverage (but coverage is uneven — core paths well-covered, edge cases sparse)

New engineers typically need 2-3 weeks before their PRs pass review without major revision cycles. This is our established baseline.

### 1.2 The two engineers being compared

**Engineer A (previous hire, baseline):**
- Background: 4 years of backend Python at a previous startup
- Started 9 months ago
- No Stillwater/AI tooling in the workflow
- Reached "independent, minor revision" PR quality at week 3
- "Rung 641 equivalent" (my subjective retrospective assessment): around day 18

**Engineer B (new hire, Stillwater-assisted):**
- Background: 3 years of backend Python at two previous companies
- Started January 27, 2026
- Stillwater prime-coder + prime-reviewer configured from day 1
- This case study covers her first 5 days

Note on comparability: Engineer A had more total experience. This makes the comparison conservative — if anything, we'd expect Engineer B to take longer given less experience, not less time. [B]

### 1.3 What "rung 641" means in our context

We adapted the prime-coder rung definitions to our team's code review standards:

**Rung 641 (local correctness) in our context means:**
- PR has passing tests (no regressions)
- Changes have clear rationale in the PR description
- No Lane A violations flagged by prime-reviewer (no blocking issues without evidence)
- Security-touching changes have explicit security review notes
- PR passes our review without major revision cycles (minor nits OK, no "needs rework" comments)

This is what we measure. We did not run formal Stillwater rung certification — we used the rung framework as a vocabulary for our internal quality bar.

---

## 2) Setup

### 2.1 Skills configured in project CLAUDE.md

```yaml
# Added to our project CLAUDE.md before Engineer B's start date
load_skills:
  - path: stillwater/skills/prime-coder.md
    order: 1
  - path: stillwater/skills/prime-reviewer.md
    order: 2

team_conventions:
  verification_rung_target_for_PRs: 641
  PR_description_must_include:
    - what_changed
    - why_changed
    - test_evidence (command + output)
    - lane_type_of_changes  # [A], [B], or [C]
  blocking_comment_requires: Lane_A_witness  # from prime-reviewer
```

### 2.2 Engineer onboarding prompt (what we gave Engineer B)

We gave her a short document on day 1 explaining the Stillwater concepts:

- What [A], [B], [C] lane types mean
- What a "rung 641 PR" looks like in our context
- That Claude Code has prime-reviewer loaded and will flag lane violations in code review

We explicitly told her: "The AI reviewer will sometimes block on missing witnesses. When it says NEED_INFO, don't override it — find the evidence it's asking for."

### 2.3 What we did NOT do

We did not configure prime-safety or any other skills. We kept it minimal — two skills, clear purpose. Adding more skills increases setup complexity and we didn't want skill-loading overhead on day 1.

---

## 3) What happened (day by day)

### 3.1 Day 1 — Setup friction and the first real task

Engineer B started her first day with a simple task: add a null check to the shipment validation service that was causing a rare 500 error in production (3 occurrences in the last month).

She spent the first 2.5 hours getting Claude Code and the CLAUDE.md configuration working. The friction points:

1. She cloned the repo but the `stillwater/` directory (our vendored skills) was in `.gitignore` (I had forgotten to remove it). She got "skill file not found" errors for 45 minutes.
2. Claude Code's CLAUDE.md loading silently ignored a YAML parse error in her initial configuration — she got no error message, just skills that weren't loaded. We found this by checking `claude --version` and verifying skill load state.
3. The `evidence/` directory was missing. When she ran a task, the skill emitted EXIT_BLOCKED because it couldn't write evidence. Creating the directory fixed it.

[A] Day 1 productive coding time: approximately 3 hours (out of 8).

Her first PR:

```python
# Before (Engineer B's first draft):
def validate_shipment(shipment: dict) -> bool:
    return shipment["weight"] > 0 and shipment["destination"] is not None

# After prime-reviewer flagged:
# [BLOCKED] No null check on shipment itself. If shipment=None, 
# this raises TypeError. Lane A witness: production_logs/error_500_2026-01.txt:L47
# shows TypeError: 'NoneType' is not subscriptable
# Required: explicit null check before field access.

# Engineer B's revision after reviewer flag:
def validate_shipment(shipment: Optional[dict]) -> bool:
    if shipment is None:
        raise ValueError("shipment cannot be None")
    return shipment["weight"] > 0 and shipment["destination"] is not None
```

[A] The reviewer caught the null check gap and correctly cited the production log as a Lane A witness. Engineer B saw the pattern immediately: the reviewer is asking for the same evidence you'd need to explain the change in code review.

Her PR description after revision:

```markdown
## What changed
Added explicit null guard to validate_shipment() per production 500 errors.

## Why changed  
3 production 500 errors in Jan 2026: production_logs/error_500_2026-01.txt:L47
TypeError: 'NoneType' is not subscriptable — shipment was None from upstream

## Test evidence
python -m pytest tests/test_shipment_validation.py -v
3 passed, 1 warning in 0.4s

## Lane type
[A] Change: null guard based on witnessed production error
[A] Test: regression test for None input added
```

[A] This PR passed code review on first submission. Minor nit only (suggestion to add a log.warning before the raise).

### 3.2 Day 2 — First real feature: pricing rule edge case

Task: handle a pricing edge case where a shipment with 0 declared value should use a floor price rather than a percentage calculation. Previous behavior was division by zero.

[A] Prime-coder null-vs-zero policy was directly relevant: 0 declared_value is a zero value (lawful), not null (absent). The skill flagged when Engineer B initially wrote:

```python
if not declared_value:  # Wrong: treats 0 and None the same
    use_floor_price()
```

Reviewer comment:
```
[BLOCKED] Null/zero confusion: `if not declared_value` evaluates to True for both
None (absent value) and 0 (lawful zero value). These are semantically different:
- None: data missing, possibly an upstream error → should raise or return error
- 0: valid declared value → use floor price
Lane A requirement: separate these cases with explicit checks.
```

Engineer B's revised code:
```python
if declared_value is None:
    raise ValueError("declared_value is required; got None")
if declared_value == 0:
    return FLOOR_PRICE
```

[A] This is a pattern that a more senior engineer would catch in review, but it's also a pattern that frequently slips through when reviewers are tired or in a hurry. Having the reviewer catch it automatically changed the conversation: instead of me explaining why this matters, Engineer B was already receiving the explanation with a specific witness.

[A] Day 2 outcome: 1 PR submitted, 1 PR approved (with minor nits), 1 failing test caught by the reviewer before submission (she ran the reviewer before submitting, which is the intended workflow).

### 3.3 Day 3 — Rung 641 benchmark

Task: add a new endpoint for bulk shipment status updates (a feature that had been in the backlog for 6 weeks). This was a substantive feature, not a bug fix.

Day 3 was when we assessed whether Engineer B had reached our "rung 641 equivalent" quality bar.

Her PR for the bulk status update endpoint:

**PR description (unprompted, she wrote this herself by day 3):**

```markdown
## Bulk Shipment Status Update — POST /shipments/bulk-status

### What changed
New endpoint: POST /shipments/bulk-status
- Accepts list of {shipment_id, new_status} pairs
- Validates each shipment_id exists
- Validates status transitions (using existing state machine)
- Returns {updated: N, failed: [{id, reason}]} with partial success semantics

### Why changed
Feature request from ops team — currently requires N separate API calls to update N shipments.
This causes rate limiting issues at >50 shipments (observed in Datadog traces, last 30 days).

### Test evidence
python -m pytest tests/test_shipment_api.py::test_bulk_status_update -v
5 passed in 1.2s

python -m pytest tests/ -q --tb=short
All 847 tests passed. 2 new tests added.

### Lane types
[A] Endpoint behavior: verified by integration tests (tests/test_shipment_api.py:L201-265)
[A] Partial success semantics: verified — test_partial_failure in test suite passes
[B] Performance: 50-shipment batch tested locally in 340ms (no load test; estimate production similar)
[C] Rate limit improvement: based on current N-call pattern taking ~8s, expect improvement

### Security notes
Endpoint requires auth (IsAuthenticated). No admin privilege required — any authenticated user
can update status of any shipment_id. [B] This MAY be an access control issue if shipment 
ownership matters. Flagging for review — did not find ownership check in existing endpoints,
assumed intentional.
```

[A] She correctly identified a potential access control issue and labeled it [B] ("may be an issue, flagging for review"). In code review, we confirmed: yes, this was a pre-existing issue in the existing single-status endpoint too; we would need to address it as a separate security PR. The fact that she caught and flagged it rather than missing it or silently ignoring it was a direct outcome of the lane-typing discipline.

[A] This PR passed code review on first submission without major revision. Code review time: 35 minutes (fast for a new feature of this complexity for us).

### 3.4 Days 4-5 — Sustaining the quality

Days 4 and 5 had 2 more PRs. Both passed on first submission. By day 5, Engineer B was running the prime-reviewer pre-submission check as a standard part of her workflow without being prompted.

One interesting moment on day 4: she asked me "is the reviewer always right?" I explained the lane system — [A] reviewer comments are based on witnessed evidence and should be taken seriously; [C] reviewer comments are style opinions and are explicitly labeled as such. She said: "Oh, that's why it says [C] on the naming comment — I thought it was just suggesting I ignore it." Getting that distinction across in a 2-minute conversation, rather than having to build up the intuition over weeks, was valuable.

---

## 4) Results

### 4.1 Quantitative comparison [A, B, C]

| Metric | Engineer A (baseline) | Engineer B (Stillwater) | Lane |
|---|---|---|---|
| Day reached "rung 641 quality" PRs | ~Day 18 | Day 3 | [B] (subjective assessment by same manager) |
| PRs rejected/major-revised in first 2 weeks | 7 | 1 (Day 1, pre-reviewer workflow) | [A] |
| Null/zero confusion bugs in PRs | 3 | 1 (caught by reviewer pre-submission) | [A] |
| Security issues missed (identified in retrospect) | 2 | 0 | [A] (small sample) |
| Day 1 productive coding time | ~6h (setup was minimal) | ~3h (Stillwater setup friction) | [A] |
| PR description quality score (1-5 scale, blind review) | 2.1 avg in first 2 weeks | 3.8 avg in first 2 weeks | [B] (subjective rating, not blind) |

[C] Estimated productivity gain: Engineer B was contributing at "close to independent" quality by end of week 1, vs Engineer A at close-to-independent quality by week 3. That's roughly 2 weeks of accelerated ramp, which at a loaded cost of ~$12k/month comes to ~$6k of accelerated productivity. Against the cost of setting up Stillwater (~4 hours of engineering time plus Claude API costs), this seems favorable — but the confounds are significant.

### 4.2 The most important outcome [B]

The quality of code review conversations changed. With Engineer A, code review was often me explaining why something was wrong ("this treats null and zero the same, which causes the bug at..."). With Engineer B, by day 3, code review was mostly about design decisions, not correctness errors. The reviewer had already handled the correctness layer.

This is not just "faster onboarding." It changes the nature of the engineering manager's job during onboarding. I spent less time teaching individual correctness patterns and more time having conversations about design judgment.

### 4.3 What rung-641 did and did not mean [A]

Reaching rung 641 by day 3 means: PRs passed review without major revision. It does not mean:

- Engineer B understood the full codebase (she did not — she was still asking basic routing questions on day 5)
- Engineer B could independently architect new services (not tested)
- Engineer B would catch all security issues (the access control issue she caught was [B]-flagged, not [A]-confirmed; we helped her evaluate it in review)

The rung is a quality floor for output, not a certification of broad engineering judgment.

---

## 5) What didn't work / limitations

### 5.1 Day 1 setup cost was real

2.5 hours of Engineer B's first day was lost to configuration problems. This is a real cost. Three specific problems:

1. Skills in `.gitignore` — should be committed to the project repo
2. Silent YAML parse failure in CLAUDE.md — Claude Code should emit an error
3. Missing `evidence/` directory — skill should create it or the README should say to

[A] We fixed these for our team after Engineer B's ramp (committed the skills, added `evidence/` to `.gitignore`-not, added a setup checklist to our onboarding doc). But new teams will hit the same issues.

### 5.2 The comparison is not controlled

Engineer A vs Engineer B is not a controlled experiment:

- Different background and experience levels
- Different tasks (some harder, some easier)
- Different codebase maturity (our codebase is better documented now than 9 months ago)
- The manager (me) knows about Stillwater and might unconsciously rate Engineer B's PRs more favorably

[A] I tried to rate PRs blind (re-reading without knowing who wrote them), but I'm a single rater and my calibration may have shifted. The "day 18 vs day 3" claim is my best assessment, not a measurement.

### 5.3 Skills add overhead to every interaction

Every Claude Code interaction with the skills loaded is slightly longer and uses more tokens because the skills are injected into context. [A] We estimated ~15% increase in Claude API costs during Engineer B's first week compared to our baseline usage. At our current scale, this is negligible. At higher scale, it might matter.

### 5.4 The reviewer is not always right

On day 4, the prime-reviewer flagged a piece of code as "potential SQL injection risk" [B]. Looking at the code, it was parameterized SQLAlchemy with no string interpolation. The reviewer was hallucinating a risk based on a pattern match that didn't apply. Engineer B overrode the reviewer with explicit reasoning, which was the correct response — but she needed my confirmation to feel comfortable overriding it. If an engineer defers to the reviewer on a false positive, they'll add unnecessary code or change correct code.

[A] We observed 2 false positive reviewer flags in Engineer B's first 5 days. Both were [B]-labeled (not [A]-labeled), so they were explicitly framed as "possible issue, flagging for review" not "definitely wrong." This framing meant she questioned them rather than automatically accepting them.

### 5.5 What it cannot teach

The skills teach output structure, not engineering judgment. By day 5, Engineer B's PRs were structurally excellent (evidence, lane types, null checks). But:

- She still needed guidance on when to make a design decision vs escalate
- She had no intuition yet for which parts of our codebase are fragile
- The "access control issue" she flagged was [B]-labeled because she genuinely didn't know if it was intentional — that domain knowledge takes time regardless of tooling

[C] My estimate: the skills accelerate the "correctness mechanics" phase of onboarding by 2-3x. They do not accelerate the "domain knowledge" phase. For our team, these were roughly equal time sinks, so total onboarding time is about 1.5x faster, not 6x faster.

---

## 6) How to reproduce it

### Step 1: Commit skills to your repo

```bash
git submodule add https://github.com/phuctruong/stillwater stillwater
# Or vendor the skills/ directory directly
cp -r stillwater/skills/ your-project/stillwater/skills/
git add stillwater/
git commit -m "add Stillwater skills for Claude Code"
```

### Step 2: Configure CLAUDE.md

```yaml
# In your project's CLAUDE.md
load_skills:
  - path: stillwater/skills/prime-coder.md
    order: 1
  - path: stillwater/skills/prime-reviewer.md
    order: 2

team_conventions:
  PR_description_must_include:
    - what_changed
    - why_changed
    - test_evidence
    - lane_type_of_changes
  blocking_comment_requires: Lane_A_witness
  verification_rung_target: 641
```

### Step 3: Create evidence directory and onboarding doc

```bash
mkdir -p evidence
echo "evidence/" >> .gitignore  # or keep it committed, your call
```

Create a 1-page onboarding doc covering:
- What [A], [B], [C] lane types mean
- What rung 641 means in your team's context
- That reviewer flags are requests for evidence, not accusations

### Step 4: Give new engineers a concrete first task

Pick a task with:
- A clear right answer (a bug with a witnessed production error)
- Tests that can verify the fix
- Scope limited to 1-3 files

This gives the engineer a concrete success with the workflow before tackling ambiguous features.

### Step 5: Watch the first PR review

Sit in on the first code review. Explain why the reviewer flagged specific things. The goal is for the engineer to understand the lane system, not just accept reviewer output. One 30-minute conversation on day 1 saves many confused override decisions later.

### Step 6: Track quality metrics

We tracked:
```
- PRs rejected/major-revised (per week)
- Null/zero confusion bugs per PR
- Code review cycle time (first submission to approval)
- PR description quality (subjective 1-5 score)
```

You don't need sophisticated tooling — a spreadsheet for the first month is enough.

---

## 7) Final verdict

[B] The prime-coder + prime-reviewer setup meaningfully accelerated Engineer B's ramp to production-quality output. The most valuable mechanism was not that the tools were smarter than the engineer — it was that the tools gave her immediate, structured feedback with evidence requirements, which is the same quality of feedback an experienced senior engineer would give but available at any time without scheduling a review.

[C] For a 6-10 person engineering team onboarding 2-4 new engineers per year, I think this setup pays for itself quickly. The setup cost (4h one-time + Day 1 friction for each new engineer) is small compared to 2 weeks of accelerated ramp time.

The comparison with Engineer A is imperfect and I've tried to be honest about why. The case for this approach doesn't rest on that comparison — it rests on: the output of Stillwater-assisted code review looks like experienced senior engineering feedback, and getting that feedback earlier in the PR cycle (before submission, not during) changes what developers submit and what reviewers need to do.

That mechanism is real and observable. The specific numbers (day 3 vs day 18) are my best estimate, not a controlled measurement.
