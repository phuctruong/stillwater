# gpt5.2-on-ai-steroids Report

**Rubric definition.** Each skill is scored on a 1–10 scale for how well it prepares `gpt5.2-on-ai-steroids` to deliver disciplined, measurable, fail-closed outputs (determinism, evidence, bounded scope, auditability, safe refusal). “Before” is baseline `gpt-5.2` behavior with no Stillwater skill injected; “After” reflects the concrete control surfaces and gates encoded in the skill text.

## prime-coder.md
- Path: `skills/prime-coder.md`
- Core goal: enforce fail-closed coding via a closed FSM, explicit budgets, Red→Green evidence gates, determinism normalization, and “stricter wins” layering rules.
- Score before: 7/10 (strong coding ability, but typically lacks a *deterministic* process contract and may over-index on plausibility over proof under time pressure).
- Score after: 9/10 (the FSM + forbidden states + evidence/normal-form requirements sharply increase enforceability and reduce “looks-right” patches).
- Measure rationale: this skill directly operationalizes “no green without receipts” with machine-like branching and hard stops, which is exactly what the rubric rewards.

## prime-math.md
- Path: `skills/prime-math.md`
- Core goal: preserve a public math contract while adding task-family routing, rung targets, Math Red→Green, deterministic witness handling, and strict “UNKNOWN over maybe” downgrade rules.
- Score before: 6/10 (can solve many problems, but proof-grade rigor and explicit verification lanes are inconsistent unless prompted).
- Score after: 9/10 (adds explicit verification ladders, witness budgets/ids, and overclaim prevention via rung-target + UNKNOWN rules).
- Measure rationale: math reliability improves most when “status OK” is mechanically bound to checkable witnesses and bounded domains, which this skill encodes.

## prime-safety.md
- Path: `skills/prime-safety.md`
- Core goal: tool-using safety via authority ordering, a capability envelope (NULL-by-default), stop conditions, injection firewall, and an auditable output contract.
- Score before: 6/10 (generally cautious, but “pause-and-ask” and envelope constraints are not guaranteed without explicit policy).
- Score after: 9/10 (capability envelope + stop conditions make refusal/UNKNOWN decisions predictable and reviewable).
- Measure rationale: safety under tools is judged by how tightly actions are bounded and how easy it is to audit why something did/didn’t happen; this is highly operational.

## phuc-context.md
- Path: `skills/phuc-context.md`
- Core goal: anti-rot context hygiene + batched instruction packs + typed prime channels (SCOUT/FORECAST/DECIDE/PATCH/SKEPTIC/JUDGE artifacts) for stable multi-step runs.
- Score before: 6/10 (can manage context, but drift/overload risk rises quickly in long, multi-agent or multi-iteration sessions).
- Score after: 8/10 (explicit context partitioning + “assets-first” NEED_INFO gate reduces hallucinated “memory” and improves reproducibility).
- Measure rationale: the rubric rewards bounded state and replayable artifacts; this skill improves both, though benefits depend on actually using the channel artifacts.

## phuc-forecast.md
- Path: `skills/phuc-forecast.md`
- Core goal: enforce a decision-quality loop (DREAM→FORECAST→DECIDE→ACT→VERIFY) with closure/coverage/integrity/love/verification/portability as hard pillars.
- Score before: 6/10 (good planning, but coverage and falsifier-thinking are uneven without an explicit premortem/stop-rule template).
- Score after: 9/10 (adds deterministic structure, required fields, lens-based premortems, and explicit fail-closed NEED_INFO behavior).
- Measure rationale: this skill most directly matches the rubric’s “measurable, bounded, verified” requirement and reduces ambiguous, untestable conclusions.

## phuc-swarms.md
- Path: `skills/phuc-swarms.md`
- Core goal: multi-agent orchestration with role contracts, CNF (Context Normal Form) capsules, prime JSON channels, and rung-based verification with replayability constraints.
- Score before: 5/10 (can simulate roles, but without strict IO schemas and role-forbidden actions, swarms tend to blur responsibilities and leak assumptions).
- Score after: 8/10 (role contracts + required artifacts + forbidden states make coordination more deterministic and easier to audit).
- Measure rationale: orchestration quality is measured by whether coordination is bounded and replayable; this skill supplies the missing “bus + contracts,” but it’s heavier to run.

## phuc-cleanup.md
- Path: `skills/phuc-cleanup.md`
- Core goal: “archive-first” cleanup workflow with suspicious-first triage (from `FINAL-AUDIT.md`) and explicit approval gates + receipts.
- Score before: 6/10 (cleanup is usually possible, but assistants often default to deletion or broad globs without an evidence-preserving protocol).
- Score after: 7/10 (clear safe workflow: scan → classify → ask approval → archive → receipts; reduces accidental loss and improves reversibility).
- Measure rationale: cleanup is judged by reversibility and audit trail; this skill adds both, but it’s narrower-scope than the other prime skills.

