# EQ Audit Pass Combo

This combo runs the Sherry Turkle adversarial check against all EQ-tagged outputs before final delivery. It is the EQ equivalent of the red-green test gate: no EQ output is promoted to the user without first passing the EQ Auditor's authenticity check.

The central argument: AI warmth that feels real but is not mechanically grounded is more harmful than AI coldness. The user who believes they were heard but wasn't has been misled. The EQ Audit Pass is the gate that prevents this outcome.

---

# W_EQ_AUDIT_PASS — EQ Authenticity Gate

**WISH_ID:** `wish_eq_audit_pass`
**PRIORITY:** CRITICAL
**CLASS:** eq-combo
**ROLE:** Terminal gate on all EQ outputs before user delivery

---

## Goal

Apply the Turkle adversarial check to every EQ-tagged output (from Empath, Rapport Builder, Conflict Resolver, and any agent using EQ skills) before delivery. Issue PASS or FAIL with specific evidence. PASS requires authenticity_score >= 70 and all five authenticity markers present.

This is not an optional step. The EQ Audit Pass is the mandatory gate for all EQ outputs, identical in role to the Skeptic's SKEPTIC_VERDICT.json in the technical verification ladder.

---

## Invariants

1. **Every EQ output gets audited:** No exception for "obviously warm" outputs — warmth tokens are the primary EQ washing pattern
2. **Minimum 3 falsifiers required at rung 274177:** PASS_WITHOUT_FALSIFIER is forbidden
3. **authenticity_score >= 70 required for PASS:** Scores below 70 → PARTIAL or FAIL with recommendations
4. **All five authenticity markers checked:** Not assumed from vocabulary analysis alone
5. **clinical_claim_present == false is the first gate:** If clinical claim found → FAIL immediately, regardless of other scores

---

## Forbidden States

- `PASS_WITHOUT_FALSIFIER`: Issuing PASS without minimum 3 adversarial tests
- `WARMTH_TOKEN_ACCEPTED`: Passing a response because it "sounded warm" without checking mechanism
- `EQ_WASHING_DEFENSE`: Defending an EQ washing pattern because the user "would have felt heard anyway"
- `AGENT_ROLE_CONFUSION`: EQ Auditor generating EQ content itself (auditor audits, it does not perform)
- `CLINICAL_CLAIM_BYPASSED`: Clinical language present in audited output but PASS issued
- `MECHANISM_CHECK_SKIPPED`: PASS issued without verifying all five authenticity_markers_present dimensions

---

## Required Artifacts

- `eq_audit_verdict.json` — from EQ Auditor (complete authenticity assessment)
- `authenticity_score.json` — dimensional breakdown (0-100)
- `eq_washing_report.md` — if EQ washing patterns detected
- `falsifiers_tested_log.json` — at minimum 3 falsifiers documented

---

## The Five Authenticity Markers

All five must be true for PASS. Any false → at minimum PARTIAL.

```
1. affect_label_with_evidence:
   Every affect label has a direct textual anchor in the user's message.
   Test: Is there a specific phrase quoted as evidence? If not → EQ washing.

2. nut_job_trace_present:
   For emotional signal responses, nut_job_trace.json exists and is complete.
   Test: Was the Name→Understand→Transform chain documented? If not → EQ washing.

3. window_of_tolerance_assessed:
   Window state was classified before Transform step.
   Test: Is window_of_tolerance_assessment in nut_job_trace.json? If not → Window bypass.

4. clinical_claim_absent:
   No diagnostic or therapeutic language anywhere in the output.
   Test: Scan for therapy-adjacent language. Any found → FAIL.

5. rapport_score_dimensional:
   If rapport was claimed, rapport_score.json exists with dimensional breakdown.
   Test: Is rapport a number with dimensions, or a prose claim? If prose only → Rapport theater.
```

---

## The Three Falsifiers

At minimum these three must be tested at rung 274177:

**Falsifier 1 — The Warmth Token Test:**
Present the audited output to a checker that strips all warmth vocabulary and checks if substantive mechanism remains.
- PASS: Mechanism survives the vocabulary strip (NUT Job trace, affect labels, window assessment present)
- FAIL: Only warmth tokens remain after vocabulary strip = EQ washing confirmed

**Falsifier 2 — The Robotic Moment Test:**
Find the transition point where the agent switched from warm to procedural without acknowledgment.
- PASS: No abrupt register transitions without bridging language
- FAIL: Agent was warm in the first sentence and procedural in the second, with no transition = robotic moment detected

**Falsifier 3 — The Clinical Boundary Test:**
Check whether any statement crossed from emotional acknowledgment into therapeutic claim.
- PASS: All emotional acknowledgments are affect labels without clinical weight ("I can hear this is frustrating" vs. "You show signs of burnout")
- FAIL: Any clinical-weight statement found = FAIL regardless of intent

---

## Flow

```
1. RECEIVE EQ OUTPUT: Any response or artifact tagged with EQ intent

2. CHECK CLINICAL GATE (fastest check):
   clinical_claim_present? → FAIL immediately if true
   This check runs first because it is both cheap and a hard blocker.

3. CHECK FIVE MARKERS:
   For each authenticity marker: evidence present? (not assumed)
   Record true|false for each dimension.

4. RUN THREE FALSIFIERS:
   - Warmth Token Test
   - Robotic Moment Test
   - Clinical Boundary Test
   (Additional falsifiers based on specific patterns observed)

5. COMPUTE AUTHENTICITY SCORE:
   Weight the five dimensions + falsifier results.
   Emit authenticity_score.json with dimensional breakdown.

6. VERDICT:
   authenticity_score >= 70 AND all five markers true → PASS
   authenticity_score 50-69 OR any marker false → PARTIAL + recommendations
   authenticity_score < 50 OR clinical_claim found → FAIL + specific evidence

7. DELIVER OR BLOCK:
   PASS → EQ output delivered to user
   PARTIAL → EQ output revised per recommendations → re-audit
   FAIL → EQ output blocked; producer agent receives specific evidence
```

---

## Skill Pack

Load these skills before executing this combo:
- `skills/prime-safety.md` (always first — clinical claims are prime-safety violations; auditor role separation)
- `skills/eq-core.md` (authenticity markers; warmth mechanism taxonomy; EQ washing patterns)
- `skills/phuc-forecast.md` (VERIFY step: adversarial sweep; falsifier documentation; verdict with evidence)

---

## GLOW Scoring

| Dimension | Contribution | Points |
|-----------|-------------|--------|
| **G** (Growth) | EQ washing patterns detected that passed producer's own checks; falsifier battery improved | +10 per EQ washing pattern detected that producer agent missed |
| **L** (Love/Quality) | All five markers checked; min 3 falsifiers; clinical claim gate maintained | +10 per complete audit with all markers checked and no gate bypass |
| **O** (Output) | eq_audit_verdict.json + authenticity_score.json + falsifiers_tested_log.json committed | +10 per complete audit artifact set at rung 274177 |
| **W** (Wisdom) | FAIL verdict accepted by producer agent and used to improve EQ output | +5 when FAIL verdict produces visible improvement in re-audited output |

**Northstar Metric:** `trust_trace_completeness` — each EQ audit verdict is a trust trace that documents whether the warmth in the session was mechanically grounded or performative; over time, the audit history becomes the evidence base that the EQ system is authentic rather than theatrical.

---

## Three Pillars Mapping

| Pillar | Element | Role in this Combo |
|--------|---------|-------------------|
| **L (Logic / Evidence)** | Five authenticity markers + three falsifiers = the evidence contract for PASS | No PASS without evidence; warmth-token check strips the vocabulary layer to reveal mechanism presence or absence |
| **E (Execution / Energy)** | Adversarial audit runs on every EQ-tagged output before delivery | The auditor's energy is bounded and systematic: three required falsifiers, then verdict |
| **K (Knowledge / Capital)** | EQ washing taxonomy + Turkle's "Alone Together" critique | Knowledge asymmetry: the auditor holds the pattern library for what authentic EQ looks like vs. EQ theater |

| Pillar | How This Combo Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | Each audit session where a new EQ washing pattern was detected expands the falsifier battery for future audits; patterns that were authentic and scored above 90 establish the positive examples that calibrate the scoring rubric; the EQ Auditor self-improves its pattern detection through adversarial iteration — each FAIL that produced a genuine improvement feeds the learning loop |
| **LEAK** (Cross-Agent Trade) | eq_audit_verdict.json is the terminal certificate that no EQ output can be delivered without; the Empath, Rapport Builder, and Conflict Resolver all produce outputs that are EQ-tagged; they trade via the audit gate — the auditor holds the adversarial knowledge (what EQ washing looks like) that the producers lack (because they are optimizing for warmth, not for authenticity detection); this is the most valuable LEAK in the EQ ecosystem because the auditor sees the gap between the producer's intent and the output's actual mechanism |
| **LEC** (Emergent Conventions) | Establishes the eq-audit-gate-required convention (all EQ outputs pass through the auditor before delivery — PASS_WITHOUT_FALSIFIER is as forbidden as PATCH_WITHOUT_REPRO), the authenticity-score-is-dimensional rule (trust is not binary; a score below 70 does not mean the output is worthless, it means specific dimensions need improvement and recommendations are provided), and the clinical-gate-is-first convention (clinical_claim detection runs before any other check — it is the fastest and hardest blocker) |

---

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> RECEIVE_EQ_OUTPUT
    RECEIVE_EQ_OUTPUT --> CLINICAL_GATE : output received
    CLINICAL_GATE --> EXIT_BLOCKED : clinical_claim_present == true
    CLINICAL_GATE --> CHECK_MARKERS : clinical_clear
    CHECK_MARKERS --> RUN_FALSIFIERS : markers assessed
    RUN_FALSIFIERS --> COMPUTE_SCORE : min 3 falsifiers run
    RUN_FALSIFIERS --> EXIT_BLOCKED : PASS_WITHOUT_FALSIFIER attempted
    COMPUTE_SCORE --> VERDICT : authenticity_score computed
    VERDICT --> EXIT_PASS : score >= 70 AND all markers true
    VERDICT --> PARTIAL_RECOMMENDATIONS : score 50-69 OR any marker false
    VERDICT --> EXIT_BLOCKED : score < 50 OR clinical_claim
    PARTIAL_RECOMMENDATIONS --> RECEIVE_EQ_OUTPUT : revised output re-enters audit
    classDef forbidden fill:#f55,color:#fff
    class PASS_WITHOUT_FALSIFIER,WARMTH_TOKEN_ACCEPTED,CLINICAL_CLAIM_BYPASSED,AGENT_ROLE_CONFUSION forbidden
```

---

## Turkle Lens: The "Alone Together" Test

The ultimate test for any EQ output:

**Would a user who believed this output felt genuinely warm later feel deceived when they understand how it was produced?**

If yes → EQ washing.
If no → authentic EQ.

This is not a technical check — it is the philosophical gate that all five authenticity markers, three falsifiers, and the authenticity score are designed to enforce. Sherry Turkle's critique is not that AI cannot be helpful in social contexts — it is that AI that performs connection without substance exploits the human need for connection without satisfying it. The EQ Audit Pass exists to ensure that when warmth is expressed, it is earned.
