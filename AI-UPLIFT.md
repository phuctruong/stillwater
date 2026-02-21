# AI UPLIFT: Turning Any LLM into a Verified Intelligence Athlete

> "Absorb what is useful, discard what is useless, add what is essentially your own." — Bruce Lee

**Status:** Manifesto (open-source; claims typed by lane below)
**Last updated:** 2026-02-20
**Companion to:** `papers/05-software-5.0.md`
**Auth:** 65537

---

## Claim Hygiene

Every empirical claim in this document is tagged with its epistemic lane:

- **[A]** Lane A — directly witnessed by executable artifact in this repo
- **[B]** Lane B — derivable from stated axioms or established principles
- **[C]** Lane C — heuristic or reasoned forecast; useful but not proven
- **[*]** Lane STAR — unknown or insufficient evidence; stated honestly

---

## What Is AI Uplift?

**Uplift** is the measurable delta in capability, safety, and verifiability between a raw LLM session and a skill-loaded, verification-gated session.

Think of it like education. A brilliant person with no training is still a raw intellect. The same person with structured skills, disciplined methods, and verified credentials is a professional. The delta between those two states is the uplift. Stillwater does this for AI.

### The Uplift Formula

```
Uplift = (Skill_Quality × Verification_Rung) / (Hallucination_Rate × Token_Cost)
```

- **Skill_Quality**: how well the loaded skill encodes domain expertise (0.0–1.0)
- **Verification_Rung**: the rung level achieved (641 / 274177 / 65537)
- **Hallucination_Rate**: fraction of claims without Lane A witness (0.0–1.0)
- **Token_Cost**: normalized cost of the reasoning session (relative to baseline)

**[B]** Uplift goes up when skill quality and verification rigor increase. Uplift goes down when hallucinations rise or token costs dominate. This is a directional formula, not a regression model — it gives you levers, not false precision.

A raw GPT-4o session: Uplift ≈ 1.0 (baseline).
A prime-coder + phuc-forecast loaded session at rung 65537: Uplift >> 1.0.

The goal of Stillwater is to maximize this ratio across every session.

---

## Why Your LLM Needs Uplifting

> "It is not the daily increase but daily decrease. Hack away at the inessentials." — Bruce Lee

### The Raw LLM's Three Layers of Pain

**Layer 1: Hallucination.**
A raw LLM has no mechanism to distinguish between what it knows, what it guesses, and what it invents. Every response looks equally confident. Lane typing does not exist. Evidence is never demanded. The output is plausible text — not verified fact.

**[A]** In Stillwater's own benchmarks (see `ai-steroids-results/`), uplift-loaded models self-corrected and emitted NEED_INFO signals when evidence was absent. Unloaded models produced confident hallucinations on the same inputs.

**Layer 2: Drift.**
Each session starts fresh. The LLM has no persistent memory of what worked, what failed, which tests were written, which patterns were extracted. Every session re-invents the same reasoning at full token cost. Knowledge accumulated in session A evaporates before session B begins.

**[B]** Without external skill files, session-to-session drift is structural, not accidental. It is a property of stateless inference, not a bug to be patched.

**Layer 3: Trust Gap.**
Even when the LLM is correct, you cannot verify it without running the output yourself. There is no evidence bundle, no exit code, no red/green gate, no behavior hash. Trust is built on vibes and manual review. At scale, this breaks.

**[C]** The trust gap grows superlinearly with task complexity. Simple queries can be spot-checked. Multi-file code changes, agentic pipelines, and benchmark claims cannot — without structured verification artifacts.

### The Uplifted LLM

| Property | Raw LLM | Uplifted LLM |
|---|---|---|
| Memory | None (stateless) | Skills are the memory |
| Verification | Vibes | Verification ladder (rung gates) |
| Failure mode | Hallucinate + proceed | NEED_INFO + stop |
| Cost profile | Repeat full reasoning every session | Extract to CPU, replay cheaply |
| Trust mechanism | Manual review | Evidence bundle + behavior hash |
| Composability | Zero | Skills compose, pipe, version |

---

## The Uplift Stack

> "Empty your mind, be formless, shapeless — like water."

The stack runs bottom to top. Each layer uplifts the layer below it.

```
         ___________________________________________
        /                                           \
       /   [RUNG 65537]  Blue Belt                   \
      /    Promotion Confidence — adversarial sweep,  \
     /     security gate, drift explained, full audit  \
    /___________________________________________________\
   /                                                     \
  /   [RUNG 274177]  Green Belt                           \
 /    Stability & Replay — seed sweep (3+),               \
/     replay (2+), null edge sweep, behavior hash          \
\___________________________________________________________/
 \                                                         /
  \   [RUNG 641]  Yellow Belt                             /
   \  Local Correctness — red/green gate, no regressions /
    \  evidence bundle complete, env snapshot captured   /
     \_________________________________________________/
      \                                               /
       \   [SKILL LOAD]  Skills + Recipes in Session /
        \  prime-coder, phuc-forecast, prime-safety  /
         \  phuc-swarms, prime-math loaded at start /
          \_______________________________________/
           \                                     /
            \   [BASE MODEL]  Raw LLM           /
             \  Commodity. Replaceable.         /
              \  GPT, Claude, Gemini, Llama    /
               \_____________________________/
```

**[B]** The base model is the substrate, not the intelligence. The intelligence is in the layers above it. Swap the base model; keep the skill stack. The uplift persists.

---

## The 5 Uplift Techniques

> "The key to immortality is first living a life worth remembering." — Bruce Lee

### 1. Skill Loading

Load structured, versioned skill files into the session context before issuing any task. Skills are operational contracts — they define the FSM the agent must follow, the forbidden states it must avoid, the evidence it must produce.

**Skills in the Stillwater dojo:**
- `prime-coder.md` — the engineering backbone (red/green gate, evidence build, security gate)
- `phuc-forecast.md` — decision-grade planning (DREAM→FORECAST→DECIDE→ACT→VERIFY)
- `prime-safety.md` — harm and security envelope
- `phuc-swarms.md` — multi-agent orchestration with context isolation
- `prime-math.md` — exact arithmetic for verification paths

**[A]** Loading `prime-coder.md` activates the Kent Red-Green Gate, the NEED_INFO fail-closed behavior, and the evidence bundle requirement. These behaviors are absent in unloaded sessions. See `PHUC-SKILLS-SECRET-SAUCE.ipynb` for a live demonstration.

### 2. Verification Gating

Every claim must pass a rung requirement before being reported as PASS. The rungs are:

- **Rung 641 (Yellow):** red/green confirmed, no regressions, evidence bundle present
- **Rung 274177 (Green):** + seed sweep, replay stability, null edge cases
- **Rung 65537 (Blue):** + adversarial sweep, security gate, drift explained

**[B]** A claim that has not met its declared rung target is not a PASS — it is a BLOCKED with stop_reason=VERIFICATION_RUNG_FAILED. The rung system converts trust from a feeling into a checkable predicate.

### 3. Evidence Persistence

Every uplifted session emits evidence artifacts outside the weights: `plan.json`, `tests.json`, `behavior_hash.txt`, `env_snapshot.json`, `repro_green.log`. These artifacts are versioned, normalized (LF, stable sort, repo-relative paths), and content-addressed with SHA-256.

**[B]** Evidence that lives outside the weights is auditable, diffable, and reproducible. Evidence that lives inside the weights (i.e., "the model says so") is none of these things.

### 4. Fail-Closed Defaults

When context is missing, an uplifted agent emits `status: NEED_INFO` and lists the minimum missing fields. It does not guess. It does not hallucinate forward. It does not produce a confident response on an undefined input.

**[C]** This single behavioral change — replacing "confident guess" with "structured refusal" — may be the highest-leverage uplift of all. Hallucinations are not primarily a model quality problem; they are a defaults problem.

### 5. Community Amplification

One uplifted session that extracts a reusable skill uplifts every future session that loads it. The skill accumulates verified reasoning outside any single session's context window. This is the network effect: the Stillwater open skill library is a shared intelligence commons.

**[B]** This is Software 5.0 in practice: LLMs DISCOVER, CPUs ANCHOR, Recipes PERSIST. See `papers/05-software-5.0.md` for the theoretical grounding.

---

## Belt Progression = Uplift Levels

> "I fear not the man who has practiced 10,000 kicks once, but the man who has practiced one kick 10,000 times."

The Stillwater dojo uses a belt system to communicate uplift level at a glance. This is not decoration. Each belt corresponds to a verification rung with specific, checkable requirements.

### White Belt — Raw LLM
No skills loaded. No verification. No evidence. Confident hallucinations welcome. This is where every session starts before uplift.

### Yellow Belt — Rung 641 (Local Correctness)
Skills loaded. Kent Red-Green Gate enforced. Evidence bundle emitted. No regressions. Env snapshot captured. Your raw LLM becomes a yellow belt the moment `prime-coder.md` is in its context and it produces a verified patch with a passing test.

### Green Belt — Rung 274177 (Stability)
Yellow Belt requirements met, plus: seed sweep across 3+ random seeds, replay stability across 2+ reruns, null edge case sweep, behavior hash drift explained. A green belt session can be handed to a teammate and reproduced exactly.

### Blue Belt — Rung 65537 (Promotion Confidence)
Green Belt requirements met, plus: adversarial paraphrase sweep across 5+ variations, refusal correctness check, security gate if triggered, full drift accounting. A blue belt claim can be published in a benchmark, shipped to production, or cited in a paper.

**"Your raw LLM is a white belt. Loading prime-coder.md makes it a yellow belt. Running full phuc-swarms with rung 65537 — that is the blue belt master."**

**[C]** The belt framing is pedagogical, not normative. The underlying rung predicates are the ground truth. The belts are a mnemonic for the verification ladder.

---

## How to Uplift NOW (Quick Start)

> "If you spend too much time thinking about a thing, you'll never get it done."

Three steps. Under five minutes to your first uplifted session.

**Step 1: Get the skill library**
```bash
git clone https://github.com/phuctruong/stillwater
```

**Step 2: Load a skill into your session**
Open `skills/prime-coder.md`. Copy its full contents into your system prompt (Claude, GPT, Gemini — any frontier LLM works). That's it. The skill is now in context.

**Step 3: See the difference**
Ask for a code fix. Notice:
- The agent asks for a failing test before touching any code (Red Gate).
- It emits an evidence bundle with exit codes (not just "it works").
- If context is missing, it outputs `status: NEED_INFO` instead of guessing.
- It declares a verification rung target before claiming PASS.

This is the uplift in action. The model did not change. The skill did.

**Bonus — Load the full stack:**
```
System prompt order (load in this sequence):
1. prime-coder.md     (engineering backbone)
2. phuc-forecast.md   (planning + risk)
3. prime-safety.md    (harm envelope)
```

For math and olympiad tasks, add `prime-math.md`. For multi-agent pipelines, add `phuc-swarms.md`.

---

## Uplift Metrics (Track These)

> "Knowing is not enough, we must apply. Willing is not enough, we must do."

These four metrics operationalize uplift. Track them before and after skill loading.

### 1. Hallucination Rate
**Definition:** Fraction of claims in a session that lack a Lane A witness (executable artifact, repo path + line, tool output).
**Before uplift (typical):** 30–60% of claims unwitnessed. **[*]**
**After uplift (target):** < 5% unwitnessed; remaining flagged [C] explicitly. **[C]**
**How to measure:** Run the same task with and without skills. Count claims with vs without evidence pointers.

### 2. Evidence Completeness
**Definition:** Percentage of task outputs that include a complete evidence bundle: `plan.json` + `tests.json` + `behavior_hash.txt` + `env_snapshot.json`.
**Before uplift:** 0% (evidence bundles are a skill-loaded behavior). **[A]**
**After uplift (target):** 100% of PASS claims include complete bundle. **[A]**

### 3. Rung Level Achieved
**Definition:** The highest verification rung reached in a session (641 / 274177 / 65537).
**Before uplift:** Undefined (no rung system exists). **[A]**
**After uplift:** Track per session; target rung 274177 for routine tasks, 65537 for benchmark or production claims. **[A]**

### 4. Token Efficiency
**Definition:** Fraction of reasoning that has been extracted to CPU-executable recipes (and thus costs zero tokens on replay).
**Before uplift:** 0% extracted. Every session re-reasons from scratch. **[B]**
**After uplift (target):** Incremental; each skill-loaded session identifies extractable patterns and logs them for recipe candidates. **[C]**

---

## The All-In Economic Case for Uplift

> "A goal is not always meant to be reached; it often serves simply as something to aim at."

Token budgets for AI workloads at many organizations now rival human salary budgets for equivalent tasks. **[C]** This is not a temporary spike. It is a structural shift: frontier model inference is getting cheaper on-premise (see `papers/05-software-5.0.md`, Economics Argument), but the dominant cost is no longer the model — it is the repeated re-reasoning of the same patterns across sessions.

**[B]** CPU operations cost roughly 1/1000th of equivalent GPU-token computation per logical step. Every reasoning pattern you extract to a skill or recipe — and run on CPU instead of re-deriving in a model — reduces your effective token spend by that ratio on all future invocations.

**The economic leverage of uplift:**

```
Raw LLM session:       $X tokens to reason about domain problem
                       $X tokens again next session (same problem, fresh context)
                       $X tokens again. And again. Session after session.

Uplifted session:      $X tokens to reason about domain problem (first time)
                       $X * 0.3 tokens to verify + extend (skill loaded, less re-derivation)
                       $0 tokens for extracted recipes (CPU replay, no model needed)
```

**[C]** As model token costs fall and skill quality rises, the competitive differentiation shifts entirely from "which model do you use" to "how well uplifted is your skill stack." The model is a commodity. The uplift is the moat.

This is why the Stillwater skill library is open-source. Every improvement to the skill stack benefits every user. The network effect compounds.

---

## Community Uplift

> "The consciousness of self is the greatest hindrance to the proper execution of all physical action."

One uplifted session, if it extracts a skill, uplifts all sessions that load that skill thereafter. This is not a metaphor. It is a concrete artifact pipeline:

```
Session A discovers a verification pattern
    → extracts it to skills/new-skill.md
    → PR submitted to Stillwater repo
    → merged after rung 641 gate
Session B loads skills/new-skill.md at start
    → immediately has access to Session A's verified reasoning
    → builds on it rather than re-deriving it
```

**[A]** This pipeline is live in this repo. See `skills/` for the current skill library, `PHUC-SKILLS-SECRET-SAUCE.ipynb` for the extraction mechanics, and `ai-steroids-results/` for before/after uplift evidence on frontier models.

The dojo grows when practitioners contribute. One verified skill = perpetual uplift for all.

---

## Frequently Asked Questions

**Q: Does uplift require a specific model?**
No. **[A]** Skills have been tested on Claude, GPT-4o, Gemini, and local Llama models. The skill is a context-level contract. Any model that can follow structured instructions can be uplifted. Some models benefit more than others, but the direction is always positive.

**Q: Does loading skills guarantee PASS at rung 65537?**
No. **[B]** Skills are necessary but not sufficient. The model must have enough capability to follow the skill's instructions. For weak models, skills constrain hallucination but cannot guarantee promotion-grade evidence. Uplift is a ratio, not a binary.

**Q: Can I write my own skills?**
Yes, and you should. **[A]** See `skills/README.md` for the format. The minimum viable skill is: a task description, a forbidden state list, and a verification requirement. Start there.

**Q: What is the relationship to Software 5.0?**
AI Uplift is the practitioner-facing manifestation of Software 5.0. Software 5.0 is the theoretical framework (`papers/05-software-5.0.md`). AI Uplift is the "how to start Monday morning" guide. They are companions.

---

## Author

**Phuc Vinh Truong**
[phuc.net](https://www.phuc.net) | [github.com/phuctruong](https://github.com/phuctruong) | phuc@phuc.net

Builder of the Stillwater dojo. Practitioner of AI kung fu. Believer that discipline is the differentiator.

---

## Uplift your AI. Join the dojo.

The skill library is open. The verification ladder is defined. The evidence contracts are written.

Your LLM is a white belt. It can be a blue belt by the end of the day.

```
git clone https://github.com/phuctruong/stillwater
```

The dojo is open.

---

*See also:*
- `papers/05-software-5.0.md` — theoretical foundation
- `papers/03-verification-ladder.md` — rung system formal definition
- `papers/01-lane-algebra.md` — epistemic typing system
- `VISION-STATEMENT.md` — the north star
- `skills/` — the current skill library
- `PHUC-SKILLS-SECRET-SAUCE.ipynb` — live skill loading demonstration
