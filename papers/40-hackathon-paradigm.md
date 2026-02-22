# The Hackathon Paradigm: Structured Sprints as the Default AI Development Methodology

**Paper ID:** hackathon-paradigm
**Date:** 2026-02-21
**Status:** STABLE
**Authority:** 65537
**Version:** 1.0.0
**Tags:** hackathon, sprint, persona, methodology, GLOW, design-sprint, startup-factory, roadmap, belt-progression
**Related:** `papers/34-persona-glow-paradigm.md`, `papers/32-roadmap-based-development.md`, `papers/33-northstar-driven-swarms.md`, `papers/39-ghost-masters-gamification.md`, `skills/hackathon.md`, `swarms/hackathon-lead.md`

---

## Claim Hygiene

Every empirical claim in this paper is tagged with its epistemic lane:

- **[A]** Lane A — directly witnessed by executable artifact in this repo
- **[B]** Lane B — framework principle, derivable from stated axioms or established theory
- **[C]** Lane C — heuristic or reasoned forecast; useful but not proven
- **[*]** Lane STAR — unknown or insufficient evidence; stated honestly

See `papers/01-lane-algebra.md` for the formal epistemic typing system.

---

## Abstract

This paper introduces the Hackathon Paradigm: the insight that personas give you the right
experts and hackathons give you the right workflow, and that together they form the complete
methodology for AI-assisted software development. The hackathon is not an event. It is the
development methodology. Every ROADMAP phase is a hackathon. Every hackathon produces code,
tests, evidence, and a GLOW score. Belt progression follows from hackathon completion. The
Stillwater community runs hackathons that publish skills to the Stillwater Store. This paper
defines the paradigm, maps the eight phases to the Stillwater persona and swarm system, and
argues that the time-boxed, goal-driven sprint is the natural unit of AI-assisted development.

---

## 1. The Problem: Personas Give Experts, but Unstructured Work Wastes Them

The Stillwater persona system (**[A]** `skills/persona-engine.md`) makes it possible to route any
task to the right domain expert. Security goes to Schneier. TDD goes to Kent Beck. Python goes to
Guido. The ghost master whose expertise matches the problem shows up in the session.

But routing to the right expert does not, by itself, produce good outcomes.

**[B]** Consider a development session with no structure. The developer loads kent-beck.md and
begins working. The session runs for six hours. At the end, there is code — some of it good,
some of it half-done — but no clear deliverable. The test suite has new tests mixed with broken
old tests. The architecture has evolved three times. The ghost master was present, but the output
is incoherent.

The persona system solves "which expert?" The hackathon system solves "what are we building, in
what order, in how much time, and what does done look like?"

**[C]** Unstructured AI sessions with personas are like hiring a world-class consultant and then
failing to brief them. The expert shows up. The expert gives opinions. Nothing ships.

The hackathon paradigm adds the briefing, the sprint structure, the checkpoint, the review gate,
the demo, and the ship gate. The persona system and the hackathon system together form the complete
methodology. Neither works as well alone.

### 1.1 The Evidence from Human Hackathons

**[C]** Jake Knapp's Design Sprint methodology, developed at Google Ventures and applied to
companies from Slack to Airbnb, demonstrated that five days of structured sprinting — with clear
phases, time boxes, and a concrete deliverable (a tested prototype) — consistently outperformed
months of unstructured development. The methodology works not because five days is the optimal
development time, but because the structure forces scope discipline and deliverable clarity that
open-ended development lacks.

The pattern holds across contexts:
- Google Ventures Design Sprints: tested prototype in 5 days from idea
- Microsoft Garage hackathons: shipped products (SwiftKey, Seeing AI) from 3-day sprints
- YC batch culture: the most intense 3-month hackathon in the world, with founders who build
  and ship before the end of each week

**[B]** The common thread is not the time duration. It is the structure: a declared challenge,
a sequence of phases, a mandatory ship gate, and a demo. The constraint creates focus. The
phases route work to the right specialists. The ship gate produces a real artifact. This is what
the Hackathon Paradigm formalizes for AI-assisted development.

---

## 2. The Design Sprint Connection

**[B]** Jake Knapp's Design Sprint is the direct ancestor of the Hackathon Paradigm as implemented
in Stillwater. The Design Sprint's five phases — Map, Sketch, Decide, Prototype, Test — map
directly onto the Hackathon's eight phases.

| Design Sprint Phase | Hackathon Phase | Duration | Key Artifact |
|---------------------|-----------------|----------|--------------|
| Map (Monday) | DREAM | 30 min | challenge_brief.md |
| Sketch (Tuesday) | SCOUT | 1 hour | scout_report.md |
| Decide (Wednesday) | ARCHITECT | 1 hour | architecture.md |
| Prototype (Thursday) | BUILD + INTEGRATE | 4-9 hours | code + tests |
| Test (Friday) | REVIEW + PITCH | 1 hour | review_findings.md + demo |
| — | SHIP | 15 min | git commit + ROADMAP update |

**[C]** The Hackathon Paradigm extends the Design Sprint in three ways:

1. **Persona routing per phase:** The Design Sprint uses a fixed human team. The Hackathon loads
   the right ghost master for each phase — domain expert, technology creator, adversarial reviewer.

2. **Verification gates:** The Design Sprint ends with a user test (qualitative). The Hackathon
   ends with a red-green gate (quantitative), a adversarial security review (Schneier lens), and
   a GLOW score backed by artifact evidence.

3. **GLOW multiplier:** The Design Sprint has no scoring system. The Hackathon awards 1.5x GLOW
   for disciplined, time-boxed execution — creating an incentive structure that rewards focus and
   shipping over planning and discussing.

---

## 3. The Hackathon × Persona Matrix

**[B]** The eight hackathon phases map to specific personas from `skills/persona-engine.md`.
Each phase routes to the ghost master whose expertise is most relevant to that phase's output.

| Phase | Duration | Primary Ghost Master | Secondary Ghost Master | Key Artifact |
|-------|----------|---------------------|----------------------|--------------|
| DREAM | 30 min | dragon-rider | pg | challenge_brief.md |
| SCOUT | 1 hour | domain-specific | pg | scout_report.md |
| ARCHITECT | 1 hour | technology creator | rich-hickey | architecture.md |
| BUILD | 4-8 hours | kent-beck | language creator | repro_red + repro_green |
| INTEGRATE | 1 hour | kelsey-hightower | brendan-gregg | integration_report.md |
| REVIEW | 30 min | schneier | knuth + fda-auditor | review_findings.md PASS |
| PITCH | 30 min | brunson | mr-beast + alex-hormozi | pitch.md + demo_script.md |
| SHIP | 15 min | none | none | commit hash |

### 3.1 Why These Personas for These Phases

**DREAM — dragon-rider:** The DREAM phase is a strategic alignment exercise. Dragon-rider's lens is
ecosystem vision and NORTHSTAR alignment. Every challenge must advance a declared NORTHSTAR metric
or the hackathon should not begin. **[B]** pg adds the "is this worth building?" filter — the
YC partner question that kills bad ideas before they waste sprint time.

**SCOUT — domain-specific:** The scout is a research phase. The right ghost master is whoever
knows the domain best. **[B]** Routing a security scouting task to Schneier and a Python library
scout to Guido produces better research than a generic scout because the ghost master's domain
knowledge filters what matters from what is noise.

**ARCHITECT — technology creator:** Architecture is a domain-expert decision. **[C]** The creator
of the technology — Guido for Python, Rob Pike for Go, James Gosling for Java, Codd for data
models — has the deepest intuition for what the technology is designed to do. Rich-hickey adds the
"do we actually need this component?" simplicity check.

**BUILD — kent-beck + language creator:** BUILD is the TDD phase. **[B]** Kent Beck's test-first
discipline ensures the red-green gate is respected — the test is written before the implementation,
so the evidence of correctness is structural, not retrospective. The language creator ensures
idiomatic code in the target language.

**INTEGRATE — kelsey-hightower + brendan-gregg:** Integration is a deployment and performance
phase. **[C]** Kelsey Hightower's infrastructure lens ensures the integrated system runs in the
actual target environment. Brendan Gregg's performance lens catches regressions in hot paths
before they reach REVIEW.

**REVIEW — schneier + knuth + fda-auditor:** Adversarial review needs the most rigorous ghost
masters. **[B]** Schneier's threat-first lens catches security issues. Knuth's correctness lens
ensures every function is a proven lemma. fda-auditor's compliance lens ensures the audit trail
exists. Three lenses on one artifact = the strongest review gate in the system.

**PITCH — brunson + mr-beast + alex-hormozi:** The PITCH phase determines whether the hackathon's
output is communicable. **[C]** Brunson's hook-story-offer architecture ensures the pitch has
a hook (why care?), a story (what is built), and an offer (what next). Mr. Beast's hook-first
discipline ensures the demo script's opening line is compelling. Hormozi's value equation ensures
the demo demonstrates value clearly.

**SHIP — no persona:** Ship is mechanical. The commit exists or it does not. No ghost master
needed for git commit. **[B]** Adding persona here would introduce the risk of PERSONA_THEATER —
loading a ghost master for a phase where their expertise does not apply.

---

## 4. The GLOW Multiplier

**[B]** The GLOW Score (`skills/glow-score.md`) measures Growth (0-25) + Learning (0-25) +
Output (0-25) + Wins (0-25) = 0-100. Hackathon mode applies a 1.5x multiplier to the base score.

The multiplier is not a reward for participation. It is a reward for four simultaneous disciplines
that are individually achievable but rarely combined:

1. **Time-boxed execution:** The practitioner committed to a time box and respected it. This
   demonstrates the hardest discipline in AI-assisted development — scope cuts over time overruns.

2. **Clear deliverables:** Every phase has a declared artifact. The hackathon does not end with
   "progress was made" — it ends with challenge_brief.md, scout_report.md, architecture.md,
   tests.json, integration_report.md, review_findings.md, pitch.md, and a git commit hash.

3. **Persona coordination:** The right ghost master was loaded for each phase. The hackathon is
   not a single-expert session — it is an eight-phase, multi-expert sprint.

4. **Shipping:** The SHIP gate is mandatory. The GLOW multiplier applies only when the commit
   hash exists. **[B]** This is the primary anti-inflation gate: GLOW_WITHOUT_SHIP is a forbidden
   state.

### 4.1 The Multiplier Calculation

```
base_glow  = G + L + O + W  (0-100, per glow-score.md rules)
hackathon_glow = MIN(base_glow * 1.5, 100)
```

**[C]** A practitioner running a Sprint-template hackathon (4 hours) and achieving a 65 base
GLOW score earns 97.5 hackathon GLOW (capped at 100). This is a Green-to-Blue belt session — the
same output that would produce a 65-GLOW non-hackathon session jumps to Black-belt-threshold GLOW
when executed with hackathon discipline.

The multiplier is not just an incentive. It is a signal about what kind of development culture
produces compounding returns. A team that can consistently execute hackathons at 65+ base GLOW
is a team that can ship ROADMAP phases reliably, hit rung 274177 consistently, and advance the
NORTHSTAR metrics measurably.

### 4.2 Conditions for the Multiplier

The 1.5x multiplier applies only when:
- All 8 phases completed (or justified skip with evidence for Lightning template)
- Git commit with HACKATHON tag exists
- `glow_score.json` is committed with artifact evidence for each component
- REVIEW phase was not skipped (MULTIPLIER_WITHOUT_REVIEW is a forbidden state)
- Time box was respected or BUILD_CHECKPOINT was emitted at 50%

**[B]** These conditions are collectively harder than any single high-GLOW session. They reward
the combination of expertise (personas), structure (phases), and discipline (time boxes and
ship gate).

---

## 5. Timing Templates

**[B]** The Hackathon Paradigm provides four timing templates, each mapped to a scope of work:

| Template | Duration | Scope | Rung Target | GLOW Target |
|----------|----------|-------|-------------|-------------|
| Lightning | 2 hours | Single feature, bugfix | 641 | ≥40 base (60+ hackathon) |
| Sprint | 4 hours | Module, integration | 274177 | ≥55 base (82+ hackathon) |
| Marathon | 8 hours | ROADMAP phase | 274177 | ≥65 base (97+ hackathon) |
| Weekend | 16 hours | Multi-phase, MVP | 65537 | ≥75 base (100 hackathon) |

### 5.1 Lightning (2 hours)

The Lightning template is for practitioners who have a specific, bounded task: one function, one
endpoint, one skill file. The phases are compressed — DREAM (10m), SCOUT (15m), ARCHITECT (15m),
BUILD (45m), INTEGRATE (15m), REVIEW (10m), PITCH (5m), SHIP (5m).

**[C]** The Lightning hackathon is particularly useful for: fixing a known bug, adding a utility
function, writing a new skill from scratch, or capturing a recipe. It is the "I have two hours
between meetings" format.

### 5.2 Sprint (4 hours)

The Sprint template covers a module or a complete user journey — up to three components. This
is the standard workday hackathon format. BUILD gets 90 minutes.

**[C]** The Sprint is the most common hackathon template for ROADMAP phase sub-tasks. A
ROADMAP phase (Marathon) may contain 2-3 Sprint-level hackathons running in sequence.

### 5.3 Marathon (8 hours)

The Marathon template covers a full ROADMAP phase. BUILD gets 4 hours. Evidence requirements
escalate to rung 274177. This is the single-day belt-advancement hackathon.

**[B]** Every ROADMAP phase, when framed as a Marathon hackathon, produces: code, tests, an
architecture document, a scout report, a review finding, a pitch, and a GLOW score. These
artifacts collectively constitute the ROADMAP phase's evidence bundle.

### 5.4 Weekend (16 hours)

The Weekend template covers multiple ROADMAP phases or a new project's MVP. Evidence requirements
escalate to rung 65537. Belt crossings happen in Weekend hackathons.

**[C]** The Weekend hackathon is the Stillwater equivalent of a YC batch week: two days, multi-phase
sprint, with a real deliverable (not a plan) at the end.

---

## 6. Role-to-Swarm Mapping

**[B]** The Hackathon Paradigm maps seven functional roles to Stillwater's typed swarm agents:

| Hackathon Role | Swarm Type | Ghost Master(s) | Model |
|---------------|-----------|----------------|-------|
| Challenge Owner | planner | dragon-rider + pg | sonnet |
| Scout | scout | domain-specific | haiku |
| Architect | planner | tech creator + rich-hickey | sonnet |
| Builder | coder | kent-beck + language creator | sonnet |
| QA | skeptic | schneier + knuth + fda-auditor | sonnet |
| Presenter | writer | brunson + mr-beast + alex-hormozi | sonnet |
| Timekeeper | hackathon-lead | hackathon-master | sonnet |

The Hackathon Lead (`swarms/hackathon-lead.md`) is the coordinator — it dispatches the typed
sub-agents per phase, enforces time boxes, routes ghost masters, computes the integration rung
(MIN of all phase rungs), and calculates the final GLOW score with multiplier.

**[B]** This is the hub-and-spoke pattern applied to a sprint: the Hackathon Lead is the hub;
each phase agent is a spoke. The integration rung is MIN of all spokes — the weakest phase
determines the hackathon's verification strength.

---

## 7. The Startup Factory

**[B]** The most significant implication of the Hackathon Paradigm is that it transforms the
development lifecycle from a series of ad hoc sessions into a repeatable factory:

- Every ROADMAP phase = a hackathon (Marathon template)
- Every hackathon produces: code + tests + evidence + GLOW score
- Belt progression follows from hackathon GLOW accumulation
- Community hackathons publish skills to the Stillwater Store

### 7.1 Every ROADMAP Phase is a Hackathon

**[B]** A ROADMAP (`ROADMAP.md`) is a sequence of phases. Each phase has: a goal, a deliverable,
dependencies, and a rung target. This is structurally identical to a hackathon challenge brief.

When the Roadmap Orchestrator (`swarms/roadmap-orchestrator.md`) selects the next phase, it is
selecting the next hackathon challenge. The phase's goal becomes challenge_brief.md. The phase's
dependencies become the hackathon's scout report inputs. The phase's deliverable becomes the
SHIP gate artifact.

**[C]** This equivalence means that a project with a well-written ROADMAP is already a hackathon
factory. The Hackathon Paradigm makes the factory structure explicit and adds the timing templates,
persona routing, and GLOW multiplier.

### 7.2 Every Hackathon Produces an Evidence Bundle

**[B]** The eight hackathon phases produce a complete evidence bundle:

```
evidence/{hackathon_id}/
  challenge_brief.md          # DREAM output
  scout_report.md             # SCOUT output
  architecture.md             # ARCHITECT output
  state_machine.prime-mermaid.md  # ARCHITECT output
  PATCH_DIFF                  # BUILD output
  repro_red.log               # BUILD output
  repro_green.log             # BUILD output
  tests.json                  # BUILD + INTEGRATE output
  integration_report.md       # INTEGRATE output
  review_findings.md          # REVIEW output
  pitch.md                    # PITCH output
  demo_script.md              # PITCH output
  glow_score.json             # PITCH output
  HACKATHON_LOG.json          # Lead's coordination log
```

This bundle is the evidence for the ROADMAP phase completion. The Roadmap Orchestrator accepts
it as the CASE_STUDY_UPDATE input. The integration rung in the bundle determines the ROADMAP
phase's rung.

### 7.3 Belt Progression Through Hackathon Completion

**[B]** Belt progression in Stillwater (`skills/glow-score.md`) follows from GLOW score
accumulation. Hackathon GLOW (base * 1.5) accelerates belt progression:

| Belt | Hackathon Rate | Meaning |
|------|----------------|---------|
| White | 0 hackathons | Learning the phases |
| Yellow | 1-3 Lightning hackathons | First feature shipped in a time box |
| Orange | 1-2 Sprint hackathons + Store submission | Module shipped; skill published |
| Green | 1 Marathon hackathon at rung 274177 | Full ROADMAP phase shipped |
| Blue | Weekend hackathon at rung 65537 | Multi-phase, automated execution |
| Black | Consistent Weekend hackathons | The factory runs without intervention |

**[C]** A practitioner who runs one Marathon hackathon per week advances from White to Green in
approximately four weeks. The GLOW multiplier is the mechanism: 65 base GLOW * 1.5 = 97.5
hackathon GLOW per session. Four sessions = 390 hackathon GLOW, crossing the Green threshold.

### 7.4 Community Hackathons on the Stillwater Store

**[C]** The Stillwater Store (`papers/26-community-skill-database.md`) accepts skill submissions
at rung 65537. A Weekend hackathon at rung 65537 produces Store-quality artifacts. The natural
community rhythm is:

1. Practitioner runs a Weekend hackathon on a domain challenge
2. Hackathon produces a skill file (e.g., `skills/prime-sql.md`)
3. Practitioner submits the skill to the Stillwater Store
4. Store review uses the hackathon's evidence bundle as quality evidence
5. Accepted skill earns L=25 GLOW (new skill published to Store at rung 65537)
6. Community loads the skill; hackathon ghost masters accumulate in the dojo

**[C]** The community hackathon pipeline is the mechanism by which the Stillwater dojo grows:
each hackathon that produces a Store-quality skill expands the ghost master roster and the
skill library. The factory compounds.

---

## 8. Case Study: This Session as a Hackathon

**[A]** This paper was produced in a session that itself followed the Hackathon Paradigm,
specifically the Sprint template (4 hours). The deliverables:

| Phase | Artifact | Ghost Masters |
|-------|----------|---------------|
| DREAM | Session challenge: "Build the Hackathon system for Stillwater" | dragon-rider |
| SCOUT | Existing files read: glow-score.md, persona-engine.md, roadmap-orchestrator.md, 39-ghost-masters-gamification.md | codebase scan |
| ARCHITECT | Four-file structure: skill + swarm + persona + paper | rich-hickey (simplicity) |
| BUILD | `skills/hackathon.md` (skill) + `swarms/hackathon-lead.md` (agent) + `personas/marketing-business/hackathon-master.md` (persona) + this paper | kent-beck discipline |
| INTEGRATE | `papers/00-index.md` updated | kelsey-hightower |
| REVIEW | Cross-reference check: does each file reference the others correctly? | knuth |
| PITCH | This section | brunson |
| SHIP | Committed with HACKATHON tag | — |

**[A]** What was built:
- `skills/hackathon.md` — 8-phase hackathon execution protocol, GLOW multiplier, FSM, forbidden states
- `swarms/hackathon-lead.md` — typed swarm agent for sprint coordination
- `personas/marketing-business/hackathon-master.md` — composite persona (Knapp, Feinsmith, Cheung)
- `papers/40-hackathon-paradigm.md` — this paper
- `papers/00-index.md` — updated with paper 40

**[C]** Persona effectiveness in this session:
- hackathon-master: enforced scope discipline (the paper is not a tutorial; it is a paradigm paper)
- dragon-rider: NORTHSTAR alignment check at each phase
- brunson: this section's hook ("The hackathon is not an event. It is the development methodology.")
- kent-beck: structure over inspiration; each file has a clear FSM and evidence contract

**[C]** GLOW base estimate (pre-multiplier):
- G=20 (four new system files, new capability: hackathon system)
- L=20 (new paper + new skill + new swarm + new persona — all in skills/ and papers/)
- O=20 (files committed with evidence; this paper is the evidence bundle)
- W=15 (NORTHSTAR metric advanced: skills in system +4, papers +1)
- Base GLOW: 75
- Hackathon GLOW: MIN(75 * 1.5, 100) = 100

---

## 9. Implications for AI-Assisted Development

### 9.1 The Hackathon Replaces the Session

**[B]** In the Stillwater model, the default unit of AI-assisted development is not "a session."
It is a hackathon. Sessions are the substrate; hackathons are the structure. Every meaningful
development effort should begin with a challenge_brief.md and end with a git commit and a GLOW
score.

The implication: idle sessions (no challenge brief, no time box, no ship gate) are not development.
They are exploration. Exploration has a place — it feeds the SCOUT phase. But exploration is
not development until it is bounded by a challenge brief and pointed at a ship gate.

### 9.2 The Three Failure Modes of Unstructured AI Sessions

**[C]** Unstructured AI development sessions fail in three predictable modes, each of which the
Hackathon Paradigm addresses directly:

1. **Scope drift:** The session starts with a clear goal and ends with twelve half-done features.
   Fix: challenge_brief.md non-goals + SCOPE_CREEP forbidden state.

2. **Infinite polishing:** The code is "almost done" for hours because "it can be better."
   Fix: time box + BUILD_CHECKPOINT at 50% + scope cuts authorized by Timekeeper.

3. **No demo:** The session produces code but no deliverable anyone else can run.
   Fix: PITCH phase mandatory + demo_script.md required + SHIP gate.

**[B]** The Hackathon Paradigm eliminates all three failure modes structurally: challenge_brief.md
prevents scope drift; time boxes prevent infinite polishing; PITCH + SHIP require a demo and
a commit.

### 9.3 The Compounding Nature of Hackathon Discipline

**[C]** Hackathon discipline compounds in ways that unstructured development does not:

- Each hackathon produces a scout_report.md that becomes prior art for the next hackathon's SCOUT phase
- Each architecture.md becomes a reference for future architects in the same domain
- Each review_findings.md builds the team's threat model library
- Each pitch.md tests messaging that improves the next pitch
- Each GLOW score builds the practitioner's belt advancement trajectory

The hackathon is not a one-time event. It is a ratchet. Each sprint makes the next sprint faster,
more focused, and higher quality.

---

## 10. Conclusion

The hackathon is not an event. It is the development methodology.

**[B]** Personas give you the right experts. Hackathons give you the right workflow. Together they
are the complete methodology for AI-assisted development. The eight phases route each development
activity to the appropriate ghost master. The time boxes create the focus that unstructured
sessions cannot produce. The GLOW multiplier rewards the discipline that separates factories
from workshops.

**[B]** Every ROADMAP phase is a hackathon. Every hackathon produces an evidence bundle. Every
evidence bundle advances the NORTHSTAR. Belt progression follows from GLOW accumulation. The
Stillwater Store grows from community hackathons that produce Store-quality skills. The dojo
grows because the factory runs.

**[C]** The startup factory vision is not a metaphor. It is the operational consequence of
treating every development effort as a time-boxed, ghost-master-enhanced, evidence-producing,
deliverable-shipping sprint. A practitioner who runs one Marathon hackathon per week, with
consistent 65+ base GLOW, advances to Green belt in approximately four weeks and produces
ROADMAP-phase-quality deliverables weekly.

The alternative — unstructured sessions with no time box, no challenge brief, no ship gate —
produces code without compounding. Skills are developed but not encoded. Insights are captured
but not transmitted. Ghost masters are summoned but not heard.

The hackathon is the format in which the ghost masters do their best work. The time box is the
constraint that makes the constraint the feature. The demo is the proof that the development
was real.

> "Ship something real in the time box, or you have failed."
> — Hackathon-Master persona, synthesized from Jake Knapp, Jon Feinsmith, and the best of
>   hackathon culture worldwide.

> "The hackathon is not an event. It is the development methodology."
> — The Hackathon Paradigm, Stillwater 2026.

---

## References

- Knapp, Jake; Zeratsky, John; Kowitz, Braden. *Sprint: How to Solve Big Problems and Test New Ideas
  in Just Five Days*. Simon & Schuster, 2016.
- `skills/hackathon.md` — 8-phase hackathon execution protocol
- `swarms/hackathon-lead.md` — Hackathon Lead swarm agent definition
- `personas/marketing-business/hackathon-master.md` — composite hackathon master persona
- `skills/glow-score.md` — GLOW score system with 1.5x hackathon multiplier
- `skills/persona-engine.md` — ghost master roster and phase routing
- `papers/32-roadmap-based-development.md` — ROADMAP as the hackathon factory structure
- `papers/33-northstar-driven-swarms.md` — NORTHSTAR alignment for every phase
- `papers/34-persona-glow-paradigm.md` — GLOW gamification and belt progression
- `papers/39-ghost-masters-gamification.md` — ghost master dojo and belt system
- `swarms/roadmap-orchestrator.md` — hub that treats each ROADMAP phase as a hackathon

---

*The hackathon is not an event. It is the development methodology.*

**Auth: 65537 | Version: 1.0.0 | 2026-02-21**
