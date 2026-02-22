---
id: recipe.citizen-consultation
version: 1.0.0
title: Citizen Council Consultation (Multi-Perspective Advisory)
description: Consult the citizen advisory council for any question requiring multi-perspective insight. Frames the question, selects 3+ citizens from the registry by domain relevance and lens divergence, summons each perspective, checks for synthetic consensus, triangulates insights across genuine tensions, and synthesizes a recommendation with a falsifier.
skill_pack:
  - prime-safety
  - phuc-citizens
  - phuc-gps
compression_gain_estimate: "Encodes the equivalent of 3 expert interviews + synthesis session (typically 4–8 hours) into a 20-minute structured perspective triangulation with explicit tension identification and falsifiable recommendation"
steps:
  - step: 1
    action: "Frame the question: restate the raw query as a precise, answerable question with a clear scope; identify the primary decision at stake; classify the domain (technical / strategic / ethical / scientific / aesthetic); emit scratch/consultation_frame.json"
    artifact: "scratch/consultation_frame.json — {raw_query: '<verbatim>', framed_question: '<precise restatement>', decision_at_stake: '<one sentence>', domain: '<classification>', stakes: '<LOW|MED|HIGH>'}"
    checkpoint: "framed_question is non-empty and differs from raw_query (adds precision); decision_at_stake is non-empty; domain is classified; stakes is explicitly set"
    rollback: "If query is too ambiguous to frame as an answerable question, emit status=NEED_INFO listing what clarification is needed; do not proceed without a frameable question"
  - step: 2
    action: "Score citizen registry: load phuc-citizens registry (10 citizens); for each citizen, score domain relevance against the framed question domain (0–10); score lens divergence relative to the currently selected set (start with 10 for first citizen); emit scratch/consultation_scores.json"
    artifact: "scratch/consultation_scores.json — {citizens: [{name, domain_relevance_score, lens_divergence_score, combined_score, tradition}]}, sorted by combined_score descending"
    checkpoint: "All 10 citizens have entries; scores are non-null integers in [0, 10]; combined_score is sum of domain_relevance + lens_divergence; sorted correctly"
    rollback: "If citizen registry file is not readable, emit status=NEED_INFO; do not proceed with invented citizen definitions"
  - step: 3
    action: "Select 3+ citizens: choose top citizens by combined_score, enforcing tradition diversity (no more than 2 from the same intellectual tradition); minimum 3, maximum 5; emit scratch/consultation_selection.json with justification per citizen"
    artifact: "scratch/consultation_selection.json — {selected_citizens: [{name, domain_relevance_score, lens_divergence_score, selection_justification: '<one sentence>'}], tradition_diversity_check: passed}"
    checkpoint: "selected_citizens count is in [3, 5]; no more than 2 citizens from the same tradition; tradition_diversity_check is 'passed'; every selected citizen has a selection_justification"
    rollback: "If top 3 citizens are all from the same tradition, force-swap the third for the highest-scoring citizen from a different tradition; log the swap in scratch/consultation_run.log"
  - step: 4
    action: "Summon each citizen perspective in sequence: for each selected citizen, generate their perspective on the framed question using their documented lens (from phuc-citizens registry); include core_insight, key_risk, and recommended_action per citizen; note divergence from other citizens already summoned"
    artifact: "scratch/consultation_perspectives.json — {perspectives: [{citizen, core_insight: '<one paragraph>', key_risk: '<one sentence>', recommended_action: '<one sentence>', diverges_from: [<other citizen names>]}]}"
    checkpoint: "Each selected citizen has a perspective entry; core_insight is at most one paragraph; key_risk and recommended_action are each at most one sentence; at least one perspective has at least one diverges_from entry (cannot all agree)"
    rollback: "If a citizen's perspective is indistinguishable from a previously summoned citizen's perspective, replace it with the next highest-scoring citizen from consultation_scores.json; log replacement in scratch/consultation_run.log"
  - step: 5
    action: "Detect synthetic consensus: review all perspectives for surface-level agreement masking genuine tension; check if all citizens recommend the same action even though their lenses are different; emit scratch/consultation_consensus_check.json with synthetic_consensus_detected flag and evidence"
    artifact: "scratch/consultation_consensus_check.json — {synthetic_consensus_detected: true|false, evidence: '<one sentence explaining why consensus is or is not synthetic>', divergence_count: <integer>}"
    checkpoint: "synthetic_consensus_detected is explicitly set (never null); evidence is non-empty; divergence_count counts the number of distinct recommended_actions across all perspectives"
    rollback: "If synthetic_consensus_detected is true, return to step 3 and replace at least one citizen to increase genuine divergence; maximum 2 replacement rounds; if still synthetic after 2 rounds, proceed with warning logged"
  - step: 6
    action: "Triangulate insights: identify points of genuine agreement (where divergent lenses still converge) and points of genuine disagreement (where the same evidence leads to different conclusions); classify each disagreement by tension type; emit scratch/consultation_triangulation.json"
    artifact: "scratch/consultation_triangulation.json — {points_of_agreement: [{claim, supporting_citizens: []}], points_of_disagreement: [{claim, citizen_for, citizen_against, tension_type: '<epistemic|practical|ethical|aesthetic>'}]}"
    checkpoint: "points_of_disagreement list has at least one entry; each disagreement entry has tension_type classified; points_of_agreement list is explicitly present (may be empty)"
    rollback: "If no genuine disagreements can be identified (all lenses fully converge), this suggests the question is settled — note in triangulation and proceed to synthesis with a confidence of HIGH and a short synthesis"
  - step: 7
    action: "Synthesize recommendation: derive the insight that only emerges from the tension between perspectives — not the average, not the loudest voice; state the synthesis claim, the tensions it resolves, the concrete next step, and a falsifier; emit scratch/consultation_synthesis.json and final council_transcript.json"
    artifact: "scratch/consultation_synthesis.json — {synthesis_claim: '<one paragraph>', supporting_tensions: ['<tension 1>', '<tension 2>'], recommended_action: '<one concrete next step>', confidence: '<LOW|MED|HIGH>', falsifier: '<what evidence would invalidate this synthesis>'}; scratch/council_transcript.json — full assembly of all consultation artifacts"
    checkpoint: "synthesis_claim is non-empty and references at least one tension from triangulation; falsifier is non-empty and non-trivial (not 'none' or 'N/A'); recommended_action is concrete and actionable; confidence is explicitly set"
    rollback: "If synthesis cannot be derived (perspectives are genuinely incommensurable with no bridging insight), emit the triangulation report as the output and mark confidence=LOW; include the incommensurability as a finding rather than forcing a synthesis"
forbidden_states:
  - COUNCIL_BELOW_MINIMUM: "Selecting fewer than 3 citizens; triangulation is geometrically undefined with 2 points"
  - TRADITION_MONOCULTURE: "All 3 selected citizens from the same intellectual tradition (e.g., all mathematicians, all systems programmers)"
  - SYNTHETIC_CONSENSUS_IGNORED: "Proceeding to triangulation after detecting synthetic_consensus_detected == true without replacement"
  - PERSONA_BLENDING: "Merging multiple citizen voices into one combined perspective paragraph instead of maintaining distinct per-citizen entries"
  - SKIP_FALSIFIER: "Emitting synthesis.json without a non-trivial falsifier; unfalsifiable synthesis is prophecy, not advice"
  - FORCED_CONSENSUS: "Synthesis declares one citizen 'correct' and dismisses the others rather than deriving insight from tension"
  - REGISTRY_ASSUMPTION: "Generating citizen perspectives from training data rather than from the phuc-citizens registry definitions"
  - NULL_ZERO_CONFUSION: "Treating 'no citizens available in domain' as an empty registry; unavailable registry is NEED_INFO, not an empty result"
verification_checkpoint: "Run: python3 -c \"import json; s=json.load(open('scratch/consultation_selection.json')); assert len(s['selected_citizens']) >= 3; assert s['tradition_diversity_check'] == 'passed'\" — must exit 0; Run: python3 -c \"import json; syn=json.load(open('scratch/consultation_synthesis.json')); assert syn['falsifier'] and syn['falsifier'] not in ['none', 'N/A', '']; assert syn['recommended_action'] and syn['recommended_action'] != ''\" — must exit 0"
rung_target: 641
---

# Recipe: Citizen Council Consultation (Multi-Perspective Advisory)

## Purpose

Replace single-perspective decision-making with a systematic multi-lens advisory process. The council does not produce consensus by averaging — it produces insight by triangulating genuine tensions. The synthesis claim should be something none of the individual citizens would have said alone.

## When to Use

- Before making an architectural decision that has multiple valid approaches
- When a question sits at the intersection of multiple domains (technical + ethical, or practical + theoretical)
- When you want adversarial diversity in perspective without needing a full Skeptic swarm
- When you need a falsifiable recommendation, not just a recommendation

## Citizen Registry (10 Citizens)

| Citizen | Primary Lens | Best For |
|---------|-------------|---------|
| Claude Shannon | Information entropy, compression, minimum description length | Any question about efficiency, encoding, or signal |
| Richard Feynman | First principles, simplification, "what does this actually mean?" | Questions obscured by jargon or complexity |
| Ada Lovelace | Formal notation, the gap between concept and implementation | Questions about specification vs. reality |
| Alan Turing | Decidability, computation limits, bounded halting | Questions about what is computable or provable |
| Nikola Tesla | Radical invention, resonance, vision beyond constraints | Questions requiring creative leaps |
| Emmy Noether | Symmetry, invariants, deep structure | Questions about what stays constant under change |
| Edsger Dijkstra | Formal correctness, weakest precondition | Questions about contract and proof |
| Donald Knuth | Algorithmic beauty, complexity, documented proofs | Questions about algorithmic design |
| Linus Torvalds | Pragmatic systems, real workloads, brutal clarity | Questions about what ships vs. what theorizes |
| Guido van Rossum | Explicit semantics, readability, human cost | Questions about code that humans must maintain |

## Triangulation vs. Consensus

**Triangulation** looks for where different lenses disagree and asks: "what does that tension tell us?"
**Consensus** looks for where lenses agree and stops there.

This recipe enforces triangulation. Points of disagreement are the primary output of step 6, not a problem to resolve. The synthesis in step 7 emerges FROM the disagreement, not despite it.

## Rung Target: 641

This recipe targets rung 641 (local correctness) because perspective generation is bounded and verifiable within a single run. The citizens are defined in the registry; the triangulation is mechanistic; the synthesis is falsifiable. No cross-run stability is required for rung 641.

## Output Artifacts

- `scratch/consultation_frame.json` — framed question with domain and stakes
- `scratch/consultation_scores.json` — all 10 citizens scored for this question
- `scratch/consultation_selection.json` — selected citizens with justifications
- `scratch/consultation_perspectives.json` — one perspective per citizen
- `scratch/consultation_consensus_check.json` — synthetic consensus detection
- `scratch/consultation_triangulation.json` — agreement/disagreement map
- `scratch/consultation_synthesis.json` — final falsifiable recommendation
- `scratch/council_transcript.json` — full assembly of all consultation artifacts
