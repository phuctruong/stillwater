# gpt5.3-on-ai-steroids Report

**Rubric definition.** Each skill is scored on a 1–10 scale for how well it prepares `gpt5.3-on-ai-steroids` to deliver disciplined, measurable, fail-closed outputs (determinism, evidence, bounded scope, auditability, safe refusal).

**Honesty note (important).** I do not have a runnable `gpt-5.3` A/B harness result in this repo, so “Before” and “After” below are **spec-based expectation scores**: “Before” is the typical baseline behavior of a strong coding model without the Stillwater skill text injected; “After” is the enforceability uplift implied by the concrete gates/contracts in the skill file itself. To turn these into empirical scores, run the same A/B/AB/ABC benchmark harness you used for other models and compare receipts.

## prime-coder.md
- Path: `skills/prime-coder.md`
- Core goal: enforce fail-closed coding via a closed FSM, explicit budgets, Red→Green evidence gates, determinism normalization, and “stricter wins” layering rules.
- Score before: 8/10 (likely strong at implementing fixes, but still prone to “plausible patch” behavior when evidence is missing or time pressure is implied).
- Score after: 9/10 (the FSM + forbidden states + evidence/normal-form requirements force auditability and sharply reduce unverifiable claims).
- Measure rationale: the rubric rewards “no green without receipts”; this file encodes that as hard runtime gates rather than style guidance.

## prime-math.md
- Path: `skills/prime-math.md`
- Core goal: preserve a public math contract while adding task-family routing, rung targets, Math Red→Green, deterministic witness handling, and strict “UNKNOWN over maybe” downgrade rules.
- Score before: 7/10 (often correct, but proof-grade rigor and explicit witness discipline are inconsistent unless demanded).
- Score after: 9/10 (binds “status OK” to checkable witnesses + rung targets; reduces overclaim and domain slippage).
- Measure rationale: math reliability improves most when OK is mechanically tied to witnesses and bounded domains; this skill makes that binding explicit.

## prime-safety.md
- Path: `skills/prime-safety.md`
- Core goal: tool-using safety via authority ordering, a capability envelope (NULL-by-default), stop conditions, injection firewall, and an auditable output contract.
- Score before: 7/10 (generally cautious, but without an explicit envelope it can still “helpfully comply” in edge cases).
- Score after: 9/10 (capability envelope + stop conditions make refusal/UNKNOWN decisions predictable and reviewable).
- Measure rationale: safety under tools is judged by how tightly actions are bounded and how auditable the go/no-go logic is; this file is operational, not aspirational.

## phuc-context.md
- Path: `skills/phuc-context.md`
- Core goal: anti-rot context hygiene + batched instruction packs + typed prime channels (SCOUT/FORECAST/DECIDE/PATCH/SKEPTIC/JUDGE artifacts) for stable multi-step runs.
- Score before: 7/10 (can manage context, but long runs still risk drift, overload, and “implicit memory” becoming pseudo-fact).
- Score after: 8/10 (explicit context partitioning + assets-first NEED_INFO gate reduces hallucinated continuity and improves replayability).
- Measure rationale: the rubric rewards bounded state and replayable artifacts; this skill improves both, but its benefit depends on actually using the channel artifacts.

## phuc-forecast.md
- Path: `skills/phuc-forecast.md`
- Core goal: enforce a decision-quality loop (DREAM→FORECAST→DECIDE→ACT→VERIFY) with closure/coverage/integrity/love/verification/portability as hard pillars.
- Score before: 7/10 (good planning is common, but premortems, falsifiers, and stop rules are not reliably emitted without a template).
- Score after: 9/10 (adds required fields, lens-based premortems, explicit stop rules, and fail-closed NEED_INFO behavior).
- Measure rationale: this is a near-direct match to the rubric: it turns “plan-ish” output into decision-grade, checkable structure.

## phuc-swarms.md
- Path: `skills/phuc-swarms.md`
- Core goal: multi-agent orchestration with role contracts, CNF (Context Normal Form) capsules, prime JSON channels, and rung-based verification with replayability constraints.
- Score before: 6/10 (can roleplay multi-agent workflows, but without strict IO schemas and role-forbidden actions, responsibilities blur and assumptions leak).
- Score after: 8/10 (role contracts + required artifacts + forbidden states make coordination more deterministic and easier to audit).
- Measure rationale: orchestration quality is measured by boundedness + replayability; this skill supplies the missing “bus + contracts,” at the cost of higher operational overhead.

## phuc-cleanup.md
- Path: `skills/phuc-cleanup.md`
- Core goal: “archive-first” cleanup workflow with suspicious-first triage (from `FINAL-AUDIT.md`) and explicit approval gates + receipts.
- Score before: 6/10 (cleanup is usually possible, but assistants often default to deletion or broad globs without an evidence-preserving protocol).
- Score after: 7/10 (scan → classify → ask approval → archive → receipts; improves reversibility and reduces accidental loss).
- Measure rationale: cleanup is judged by reversibility + audit trail; this skill adds both, but it’s narrower-scope than the prime execution skills.

