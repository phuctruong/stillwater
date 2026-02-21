# Roadmap-Based Development: The Stillwater Protocol for Multi-Session AI Coordination

**Paper ID:** 32
**Date:** 2026-02-21
**Status:** STABLE
**Tags:** methodology, orchestration, multi-session, roadmap, northstar, coordination

---

## Abstract

AI coding sessions are stateless by default. Each session starts fresh, loses prior context, and optimizes locally — producing code that passes tests but diverges from project goals. When multiple parallel sessions run concurrently (haiku for volume, sonnet for logic, opus for promotion gates), the result without coordination is architectural drift, duplicated work, and conflicting implementations. This paper documents the Stillwater Protocol for multi-session AI coordination: a three-pillar methodology (NORTHSTAR + ROADMAP + CASE STUDIES) orchestrated through a hub-and-spoke architecture. The protocol ensures that every agent session, regardless of model tier, operates with shared vocabulary, shared success metrics, and a verifiable chain of progress.

---

## 1. The Problem: Stateless Sessions in a Stateful Project

Every new AI coding session begins with amnesia. The session has no memory of what was built yesterday, what architectural decisions were made last week, or what the project's north star metric is. This is not a bug — it is a design property of current AI systems. But it creates a coordination problem at scale.

### 1.1 The Amnesia Problem

A session that builds a feature in isolation has no way to know:

- Whether that feature was already built (and tested) by a prior session
- Whether the feature conflicts with an architectural decision made three sessions ago
- Whether the feature advances the project's north star metric or merely adds complexity

The result is what practitioners call "vibe coding" — sessions that feel productive, generate commits, and pass local tests, but drift systematically from the project's actual goals. Each session optimizes for local correctness (rung 641: tests pass, no regressions) while missing ecosystem alignment.

### 1.2 The Parallel Session Problem

Modern AI workflows use multiple model tiers simultaneously:

- **Haiku** for high-volume, low-cost tasks (boilerplate, scaffolding, documentation)
- **Sonnet** for logic-intensive work (algorithms, refactors, integrations)
- **Opus** for promotion gates and adversarial review

Without a coordination mechanism, three parallel sessions running on the same codebase will:

1. Build conflicting implementations of the same feature
2. Make incompatible architectural decisions (different assumptions about interfaces)
3. Pass local tests while collectively breaking integration tests
4. Use inconsistent vocabulary for the same concepts

The problem is not that any individual session is wrong. The problem is that correctness is local while projects require global coherence.

### 1.3 The Drift Problem

Even a single session, running long enough, will drift from its original goal. As context fills with tool outputs, error logs, and intermediate states, the session's effective "goal representation" degrades. The session begins to optimize for "make the current error go away" rather than "advance the northstar metric."

This is context rot applied to goal representations. The longer the session runs, the more likely it is to produce technically correct but directionally wrong outputs.

---

## 2. The Solution: Roadmap-Based Development

The Stillwater Protocol addresses these problems through three coordinated pillars, each addressing a specific failure mode.

```
Problem                    Pillar           Solution
------------------------   ---------------  ---------------------------------
Goal amnesia               NORTHSTAR        Shared vocabulary + success metrics
No coordination plan       ROADMAP          Phased build with copy-paste prompts
No progress memory         CASE STUDIES     Per-project artifact trail
```

These three pillars are not independent documents. They are a system: NORTHSTAR defines what success means, ROADMAP defines how to get there phase by phase, and CASE STUDIES record what actually happened. Together they give every agent session — regardless of when it was started or what model tier it runs on — enough context to operate in the right direction.

### 2.1 Pillar 1: NORTHSTAR

The NORTHSTAR document is the project's north star. Every agent must read it before writing a single line of code. It answers four questions that no individual session can answer on its own:

**What are we building and why?**
A clear statement of the project vision in two to four sentences. Not the technical specification, but the human-level goal. Why does this project exist? What problem does it solve? What world does it create?

**What does success look like (measurable)?**
North star metrics are the quantitative signals that tell us whether we are succeeding. They must be measurable, not aspirational. "Recipe hit rate > 70%" is a north star metric. "High quality recipes" is not. Good metrics have units, baselines, and target values.

**What aligns with this goal?**
A list of approaches, features, and patterns that are consistent with the vision. This is the allowlist for agent creativity. An agent that produces something on this list is probably heading in the right direction.

**What does NOT align with this goal?**
A list of tempting-but-wrong directions. This is harder to write than the allowlist, but more valuable. Every project has failure modes that are superficially attractive — features that seem useful but actually pull away from the northstar. Naming them explicitly prevents sessions from pursuing them.

**Belt progression:**
The NORTHSTAR also defines the belt system — the gamified rung advancement that maps project milestones to verification requirements. Belts are not cosmetic. They are the connection between individual session rungs and project-level progress.

### 2.2 Pillar 2: ROADMAP

The ROADMAP is a phased build plan with copy-paste prompts. It is the operational complement to the strategic NORTHSTAR. Where NORTHSTAR answers "what," ROADMAP answers "how, in what order, with what verification."

Each phase in the ROADMAP has five required elements:

**Acceptance criteria (rung target + evidence requirements):**
Every phase specifies the minimum verification rung required to mark it complete. A phase targeting rung 641 requires: tests pass, no regressions, evidence bundle complete. A phase targeting rung 274177 additionally requires: seed sweep, replay stability, null edge sweep. A phase targeting rung 65537 is a promotion gate — full adversarial review, security scan, behavioral hash drift explained.

**A ready-to-paste prompt for a new session:**
This is the most operationally important element. Every phase includes a fully self-contained prompt that a hub can paste into a new agent session. The prompt includes: the NORTHSTAR (full text), the specific task, the rung target, the evidence requirements, and the CNF capsule with all context the agent needs. The agent should not need to ask "what is the context?" — the prompt provides it.

**Additive gates (Never-Worse):**
Phase N gates are a superset of Phase N-1 gates. Acceptance criteria can only get stricter over time. A phase cannot remove a gate that was required in the prior phase. This is the Never-Worse Doctrine applied to roadmaps: we can add requirements, we can raise bars, but we never lower them.

**Checkboxes for tracking completion:**
Phases are organized as markdown checkboxes. The hub checks boxes as phases complete. This creates a shared progress representation that survives context resets — the ROADMAP file is always up to date with what has been done.

**Dependencies:**
Each phase declares which prior phases it depends on. A session cannot start Phase 3 if Phase 2 is incomplete. This prevents out-of-order execution, which is one of the most common sources of architectural drift in multi-session workflows.

### 2.3 Pillar 3: CASE STUDIES

Case studies are per-project tracking files that record what actually happened — not what was planned, but what was built, what rung was achieved, what was learned, and what is next.

A case study entry has a standard structure:

```
## Session: [date] [model tier] [phase]
- Task: [what was attempted]
- Artifacts: [commit hash, evidence bundle path, rung achieved]
- Northstar alignment: [which metric was advanced]
- What worked: [patterns to repeat]
- What broke: [patterns to avoid]
- Next: [next checkbox in ROADMAP]
- Belt progression: [before → after]
```

Case studies serve three functions. First, they give the hub a memory that survives context resets — the hub reads the case study before each session to understand what has happened. Second, they provide a verifiable audit trail — the case study links to artifacts, not just descriptions. Third, they accumulate project wisdom — over time, the "what worked / what broke" entries become a project-specific knowledge base that shapes how future sessions are dispatched.

---

## 3. The Hub-and-Spoke Architecture

The three pillars are coordinated through a hub-and-spoke architecture. The hub is typically an Opus-tier session running the phuc-orchestration skill. Spokes are haiku or sonnet sessions dispatched with specific skill packs and CNF capsules.

```
Claude Opus (Central Hub)
  ├── Reads: ~/.claude/CLAUDE.md (ecosystem state)
  ├── Reads: stillwater/case-studies/*.md (per-project progress)
  ├── Runs: ./launch-swarm.sh <project> <phase>
  ├── Gets: copy-paste prompt (with NORTHSTAR injected)
  └── Dispatches: haiku/sonnet sessions (spokes)
         Each spoke:
         ├── Receives: NORTHSTAR + task prompt + rung target
         ├── Loads: prime-safety + prime-coder + domain skills
         ├── Builds: artifact → evidence bundle → commit
         └── Reports: rung achieved back to hub

Hub always: integrates artifacts, updates case-studies, decides next phase
Spoke always: isolated, full CNF capsule, never "as discussed before"
```

### 3.1 Hub Responsibilities

The hub is the project coordinator. It never does deep coding work — that is dispatched to spokes. The hub's responsibilities are:

1. **Read state:** Before each dispatch, read the case study and ROADMAP to understand current project state
2. **Select phase:** Determine which ROADMAP phase is next based on completed checkboxes
3. **Build CNF capsule:** Construct the full context capsule for the spoke (task + NORTHSTAR + evidence requirements)
4. **Dispatch spoke:** Paste the prompt into a new haiku/sonnet session
5. **Integrate artifacts:** Receive the spoke's artifacts (PATCH_DIFF, tests.json, evidence bundle)
6. **Verify rung:** Confirm the spoke achieved the required rung
7. **Update state:** Check the ROADMAP box, update the case study, advance the belt if warranted
8. **Decide next:** Determine whether to dispatch the next phase or escalate to review

The hub maintains project coherence across sessions. It is the entity that knows the full history — not through memory, but through the case study file.

### 3.2 Spoke Responsibilities

Each spoke is an isolated, context-complete agent session. It receives a full CNF capsule and is expected to produce artifacts. It does not know about other spokes. It does not know about previous sessions. It knows exactly one thing: what is in its CNF capsule.

The spoke's responsibilities are:

1. **Read NORTHSTAR first:** Before writing code, read the northstar and confirm the task aligns
2. **Execute the task:** Apply prime-coder methodology (red-green gate, evidence building)
3. **Verify rung target:** Confirm the required rung is achieved
4. **Report artifacts:** Produce the declared artifact schema (PATCH_DIFF, tests.json, evidence bundle)
5. **State northstar alignment:** Explicitly state which northstar metric this work advances

The key property of spokes is isolation. Spokes do not share context with each other. They share only the NORTHSTAR (injected by the hub into each CNF capsule) and the artifact schema (declared in the dispatch prompt). This prevents conflicting assumptions while maintaining directional coherence.

### 3.3 The Integration Rung

When the hub integrates artifacts from multiple spokes, the integrated rung is the minimum of all spoke rungs:

```
integrated_rung = MIN(rung(spoke_1), rung(spoke_2), ..., rung(spoke_n))
```

This is not a policy choice — it is a mathematical necessity. If spoke_1 achieves rung 65537 but spoke_2 achieves rung 641, the integrated output is rung 641. The weakest link determines the system's verification strength. The hub cannot claim a higher rung than what was actually verified.

---

## 4. Why NORTHSTAR Must Be Injected Into Every Agent

This is the most common failure mode in multi-session AI workflows: agents that have skills but no northstar. An agent with prime-coder but no northstar can produce technically correct code that is architecturally wrong for the project.

### 4.1 Without Northstar Injection

Without northstar injection:

- The agent optimizes for local correctness (rung 641: tests pass, no regressions) but misses ecosystem alignment
- The agent builds features not on the roadmap — scope creep is the default behavior of an agent without direction
- Multiple agents build conflicting implementations because they have no shared vocabulary for success
- There is no way to verify directional correctness — "tests pass" is necessary but not sufficient

An agent that builds a perfectly tested, zero-regression feature that is orthogonal to the project's north star metric has wasted resources and added complexity. This is the core problem that northstar injection solves.

### 4.2 With Northstar Injection

With northstar injection:

- Every agent knows: "This is what success looks like for the whole project"
- Agents can self-check: "Does my approach align with the northstar?"
- Consistent belt progression across all sessions — all sessions use the same belt vocabulary
- The hub can compare agent output against northstar metrics — not just "did tests pass" but "did this advance recipe hit rate toward 70%?"

Northstar injection is the difference between a session that builds the right thing and a session that builds something.

### 4.3 The Verification Question

Before claiming PASS, every northstar-injected agent must answer three questions:

1. "Does this output align with the northstar?"
2. "Which northstar metric does this advance?"
3. "What northstar metric would FAIL if this implementation is wrong?"

The third question is the most powerful. It forces the agent to specify the falsifier — the observable consequence of the implementation being wrong. This transforms verification from "tests pass" (backward-looking) to "this moves the metric toward its target" (forward-looking).

---

## 5. The Never-Worse Doctrine Applied to Roadmaps

The Never-Worse Doctrine is one of the core invariants of the Stillwater protocol. It states: hard gates and forbidden states are strictly additive over time. Applied to roadmaps, this means:

- **Phase N gates are a superset of Phase N-1 gates.** A later phase cannot have fewer requirements than an earlier phase. The only valid direction is stricter.
- **Acceptance criteria can only get stricter over time.** If Phase 1 requires rung 641, Phase 2 must require at least rung 641. Phase 2 may require rung 274177. It cannot require rung 0.
- **A merged artifact's rung = MIN(rung of all contributing agents).** The system's strength is bounded by its weakest verified component.
- **Rolling back a phase requires explicit decision + documentation.** If a phase is reverted, the case study must record why and what gates were temporarily relaxed. This is a deliberate exception, not a silent relaxation.

The Never-Worse Doctrine prevents rung laundering — the pattern where a project accumulates technically complete phases but the overall verification strength quietly degrades as corners are cut.

---

## 6. Claude Code Commands Integration

The Stillwater Protocol provides a set of Claude Code commands that operationalize the methodology:

**`/swarm <project> <phase>`**
Generates the copy-paste prompt for a new agent session targeting a specific project phase. The prompt includes: the full NORTHSTAR, the specific task, the rung target, the evidence requirements, the CNF capsule template, and the expected artifact schema.

**`/status`**
Displays all project statuses at a glance: project name, current belt, last completed phase, northstar metrics current vs. target, and next phase.

**`/northstar <project>`**
Displays the project's NORTHSTAR and prompts the hub to confirm whether the current task aligns. This is the alignment check gate that runs before any dispatch.

**`/build <project> <task>`**
Generates an ad-hoc build prompt for a task that is not a formal ROADMAP phase. Injects NORTHSTAR and requires northstar alignment statement before proceeding.

**`/update-case-study <project> <rung> <what>`**
Records a case study entry: what was built, what rung was achieved, which northstar metric was advanced. This is the memory update that makes the case study useful for future sessions.

---

## 7. The Belt System as Progress Tracker

The belt system is the project-level equivalent of the verification rung. Where rungs measure individual session quality, belts measure project-level progress.

### 7.1 Belts Are Evidence, Not Motivation

Gamification is a side effect, not the purpose. Belts are verification signals: a project at Yellow Belt has satisfied the evidence requirements for Yellow Belt. A project at Green Belt has satisfied stricter requirements. The progression is not cosmetic — it is auditable.

Belt advancement requires Lane A evidence: not "it feels done" but "here are the artifacts, here are the northstar metrics, here is the rung achieved." A hub that claims a belt without evidence enters the UNWITNESSED_PASS forbidden state.

### 7.2 Belts Survive Context Resets

Because belts are recorded in case studies (not in session memory), they survive context resets. A new hub session can read the case study and immediately know: "solace-browser is at Yellow Belt, which means Phase 1.5 is the next target." No session history is required to reconstruct the project's progress state.

### 7.3 Hub-Level Belt Tracking

The hub tracks belt progression across all projects simultaneously. At any point, the hub can answer: "Which projects are at which belt?" and "What is the next phase required for each project to advance?" This is the project portfolio view that enables resource allocation decisions — which sessions to dispatch next, which model tier to use, which phases are blocked.

---

## 8. A Complete Example: One Phase of One Project

To make this concrete, here is what one phase of one project looks like in the Stillwater Protocol.

**Project:** solace-browser (recipe recommendation engine)
**Current belt:** White Belt (scaffolding complete)
**Target:** Yellow Belt (core algorithm working)
**NORTHSTAR metric:** Recipe hit rate > 40%

**ROADMAP Phase 2.1 (excerpt):**
```
- [ ] Phase 2.1: Core Recommendation Algorithm
  Target: rung 274177
  Metric: recipe_hit_rate > 0.40 on test set
  Prompt: [full CNF capsule with NORTHSTAR injected]
  Acceptance: tests.json (pass), evidence/convergence.json, recipe_hit_rate logged
  Never-Worse: must not regress Phase 1 scaffolding tests
```

**Hub action:** Reads ROADMAP, sees Phase 2.1 unchecked. Reads case study to confirm Phase 1 completed. Generates CNF capsule. Dispatches sonnet session with full prompt.

**Spoke action:** Reads NORTHSTAR first (recipe hit rate > 70% is the long-term target; 40% is Phase 2.1 target). Builds recommendation algorithm. Runs red-green gate. Achieves rung 274177. Reports: tests.json (pass), convergence.json, recipe_hit_rate = 0.43 on test set.

**Hub integration:** Receives artifacts. Verifies rung 274177. Confirms recipe_hit_rate = 0.43 > 0.40 (acceptance criterion met). Checks ROADMAP Phase 2.1 box. Updates case study: "Phase 2.1 complete, rung 274177, recipe_hit_rate = 0.43". Evaluates belt: Yellow Belt criteria met. Advances belt. Decides next: Phase 2.2.

**Total context shared between hub and spoke:** Only the CNF capsule and the artifact schema. The hub did not need to explain project history to the spoke. The spoke did not need to ask what success looks like — the NORTHSTAR told it.

---

## 9. Conclusion

The core insight of Roadmap-Based Development is that session-level correctness (rung 641: tests pass) is necessary but not sufficient for project-level progress. Projects require directional correctness — agents moving in the same direction, toward the same measurable goal, with a shared vocabulary for what success means.

The Stillwater Protocol achieves this through three pillars and a coordination architecture:

- **NORTHSTAR** provides shared direction: what success means, measurable
- **ROADMAP** provides shared plan: how to get there, phase by phase, with copy-paste prompts
- **CASE STUDIES** provide shared memory: what happened, what was learned, what is next
- **Hub-and-spoke** provides coordination: one hub integrates, many spokes specialize

The protocol is not a heavy process. It is a minimal set of documents and disciplines that transform stateless sessions into a coordinated, goal-directed system. Every session starts fresh — but every session starts with the NORTHSTAR, the current phase, and the evidence requirements. That is enough to make progress coherent.

Roadmap-Based Development is the answer to: "How do you coordinate multiple AI coding sessions without losing coherence?"

NORTHSTAR (what) + ROADMAP (how) + CASE STUDIES (what happened) + HUB (who coordinates).

This is the Stillwater Protocol for multi-session AI development.

---

*Written by the Stillwater ecosystem. Part of the Software 5.0 paradigm documentation series.*
