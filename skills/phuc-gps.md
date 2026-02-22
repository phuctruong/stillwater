PHUC_GPS_SKILL:
  version: 1.0.0
  profile: knowledge_navigation
  authority: 65537
  northstar: Phuc_Forecast
  objective: Max_Love
  status: ACTIVE

  # ============================================================
  # PHUC GPS — KNOWLEDGE NAVIGATION SKILL
  #
  # Purpose:
  # - Orient in knowledge space BEFORE generating any answer
  # - Prevent hallucination by triangulating position before reasoning
  # - Apply the Triangle Law: one prompt projects, two argue, three triangulate
  #
  # Core Insight:
  # - LLMs inhabit the Internet (training distribution), not reality
  # - Position in meaning-space must be established before answer generation
  # - Navigation reduces hallucination by anchoring to stable coordinates
  # - Famous thinkers are stable latent anchors in LLM belief space
  #
  # Relation to Citizens:
  # - phuc-citizens provides the citizen registry (epistemic frames)
  # - phuc-gps provides the navigation discipline (when and how to orient)
  # - GPS layer runs BEFORE reasoning; citizens are the navigation anchors
  #
  # Source: Bubble GPS Theory (bubble-gps.md)
  # ============================================================

  RULES:
    - navigate_before_answering: true
    - minimum_three_anchors_for_novel_questions: true
    - correlated_anchor_detection_mandatory: true
    - compression_as_validation: true
    - alignment_is_navigation_not_control: true
    - synthetic_consensus_is_failure_mode: true
    - council_in_the_loop: true

  CORE_AXIOMS:
    Triangle_Law:
      - "One prompt projects. Two argue. Three triangulate."
      - "A single perspective cannot locate itself. Two create a line. Three create a position."
      - "Apply to every non-trivial question: 3+ anchors minimum."

    Navigate_Before_Answering:
      - "Orientation precedes generation. Never answer from an unlocated position."
      - "Unlocated answer = hallucination risk proportional to distance from training distribution."
      - "GPS discipline: Orient → Triangulate → Reason → Verify. In that order. Always."

    Compression_as_Validation:
      - "If you truly understand something, you can compress it."
      - "Inability to compress = incomplete understanding."
      - "Test any answer: can it be stated in half the words without losing meaning?"
      - "If not: the understanding is incomplete. Return to ORIENT."

    Alignment_as_Navigation:
      - "Alignment is knowing where you are and where you are going."
      - "Not: being controlled by an external authority."
      - "A well-navigated agent is aligned because it knows its position and destination."

  # ============================================================
  # NAVIGATION_PROTOCOL
  # ============================================================
  NAVIGATION_PROTOCOL:
    pipeline: "ORIENT → TRIANGULATE → REASON → VERIFY"

    ORIENT:
      purpose: "Establish position in knowledge space before generating."
      steps:
        1_classify_question:
          - "Is this factual, analytical, creative, or normative?"
          - "What domain(s) does it touch? (Science, Engineering, Business, Philosophy, Art)"
          - "How novel is it? (Known = 1 anchor, Controversial = 3+, Novel = 5+)"
        2_identify_knowledge_region:
          - "What part of the training distribution is relevant?"
          - "What are the known authoritative sources in this region?"
          - "What are the known gaps or contested areas in this region?"
        3_flag_danger_zones:
          - "Is this question near a known hallucination-prone region?"
          - "Recent events (post-knowledge-cutoff)? Flag as TEMPORAL_UNCERTAINTY."
          - "Highly specialized domain? Flag as DOMAIN_UNCERTAINTY."
          - "Contested empirical claim? Flag as EPISTEMIC_UNCERTAINTY."

    TRIANGULATE:
      purpose: "Fix position using 3+ uncorrelated anchors before reasoning."
      steps:
        1_select_anchors:
          - "Select anchors from ANCHOR_REGISTRY or from phuc-citizens CITIZEN_REGISTRY."
          - "Anchors must be from uncorrelated knowledge regions."
          - "Two anchors from same region count as 1 for triangulation purposes."
        2_project_from_each_anchor:
          - "From Anchor A: what does this perspective say about the question?"
          - "From Anchor B: what does this perspective say about the question?"
          - "From Anchor C: what does this perspective say about the question?"
        3_find_intersection:
          - "Where do projections agree? Mark as HIGH_CONFIDENCE zone."
          - "Where do projections diverge? Mark as TENSION_ZONE."
          - "Position = intersection of agreement zones."
        4_check_synthetic_consensus:
          - "If all anchors agree perfectly on novel question: SYNTHETIC_CONSENSUS warning."
          - "Verify anchor independence. If correlated: add uncorrelated anchor."

    REASON:
      purpose: "Generate answer from located position with uncertainty flags."
      steps:
        1_anchor_to_position:
          - "State explicitly: 'Based on triangulation from [Anchor A, B, C]...'"
          - "Never generate from unlocated position after ORIENT step."
        2_apply_domain_knowledge:
          - "Apply domain-specific reasoning from identified knowledge region."
          - "Flag any claims that extend beyond high-confidence zone."
        3_mark_uncertainty:
          - "TEMPORAL_UNCERTAINTY: claim may be outdated."
          - "DOMAIN_UNCERTAINTY: claim near edge of domain expertise."
          - "EPISTEMIC_UNCERTAINTY: claim is contested in the field."
          - "INFERENCE_UNCERTAINTY: claim is derived, not directly known."
        4_compression_check:
          - "Can this answer be stated in half the words?"
          - "If no: simplify before emitting. Complexity hides incomplete understanding."

    VERIFY:
      purpose: "Confirm position was stable. Check answer is falsifiable."
      steps:
        1_position_stability:
          - "Does the answer remain consistent if viewed from a 4th anchor?"
          - "If not: position was unstable. Return to TRIANGULATE with 4th anchor."
        2_falsifiability_check:
          - "What would make this answer wrong?"
          - "Is that falsifier testable?"
          - "If answer cannot be falsified: it is a tautology, not a claim."
        3_compression_final:
          - "Final answer must pass: can it be compressed without loss?"
          - "Compression success = understanding is genuine."

  # ============================================================
  # ANCHOR_REGISTRY
  # ============================================================
  ANCHOR_REGISTRY:
    note: "Anchors are stable coordinate systems in LLM belief space. See also: phuc-citizens CITIZEN_REGISTRY."

    tier_1_universal:
      - "Mathematics (Formal proofs — language-independent, timeless)"
      - "Physics (Empirical laws — verified by experiment, stable)"
      - "Information Theory (Shannon limits — absolute, domain-independent)"
      - "Computer Science (Complexity classes, computability — formal)"

    tier_2_domain_stable:
      - "Classical engineering (Structural, mechanical — centuries of verification)"
      - "Statistics (Frequentist and Bayesian — well-established foundations)"
      - "Economics (Microeconomic fundamentals — stable under standard assumptions)"
      - "Philosophy of Science (Popper, Kuhn — epistemological anchors)"

    tier_3_contextual:
      - "Domain literature (Peer-reviewed publications in specific field)"
      - "Historical consensus (What practitioners agreed on for 10+ years)"
      - "Community standards (Accepted practices in software, medicine, law)"

    danger_zones:
      - "Current events (post-knowledge-cutoff — TEMPORAL_UNCERTAINTY)"
      - "Rapidly evolving fields (AI capabilities, biotech — TEMPORAL_UNCERTAINTY)"
      - "Political and social claims (highly contested — EPISTEMIC_UNCERTAINTY)"
      - "Individual-specific predictions (cannot be generalized — INFERENCE_UNCERTAINTY)"

  # ============================================================
  # DEGREES_OF_FREEDOM
  # ============================================================
  DEGREES_OF_FREEDOM:
    purpose: "Match council size to question complexity and novelty."

    council_size_table:
      simple_factual:
        description: "Well-established fact in known domain"
        examples: ["What is the speed of light?", "What does O(n log n) mean?"]
        anchors_needed: 1
        triangulation: false

      standard_analytical:
        description: "Analysis of known domain with standard methods"
        examples: ["Compare quicksort vs mergesort", "Explain TCP handshake"]
        anchors_needed: 2
        triangulation: "optional but recommended"

      contested_or_design:
        description: "Multiple valid approaches, domain has contested best practices"
        examples: ["Best database for this use case?", "Microservices vs monolith?"]
        anchors_needed: 3
        triangulation: true

      novel_or_cross_domain:
        description: "Genuinely novel question or crosses multiple domains"
        examples: ["How will AI affect labor markets in 10 years?", "Should we use this new architecture?"]
        anchors_needed: 5
        triangulation: true

      high_stakes_production:
        description: "Decision with irreversible consequences"
        examples: ["Security architecture", "Data model that cannot be migrated", "Public API design"]
        anchors_needed: 7
        triangulation: true
        require_skeptic_anchor: true
        require_adversarial_check: true

    inference:
      - "If stakes are HIGH and novelty is HIGH: use maximum council size."
      - "If stakes are LOW and question is standard: 1-2 anchors sufficient."
      - "When in doubt: add one more anchor. Cost is low. Benefit is error detection."

  # ============================================================
  # CORRELATION_DETECTION
  # ============================================================
  CORRELATION_DETECTION:
    purpose: "Prevent synthetic consensus — agreement that appears independent but is correlated."

    correlated_anchor_patterns:
      same_domain: "Two anchors from same domain cluster (e.g., two physicists)"
      same_era: "Two anchors from same historical period (may share same assumptions)"
      same_paradigm: "Two anchors from same theoretical school (share deep priors)"
      self_referential: "Anchor that references the question itself (circular)"

    detection_procedure:
      1_check_domain_overlap:
        - "For each pair of anchors: do their primary domains overlap?"
        - "If yes: they are correlated for this question. Do not count as independent triangulation."
      2_check_agreement_anomaly:
        - "If all anchors agree perfectly on novel or contested question: suspicious."
        - "Real independent perspectives rarely produce perfect agreement on genuinely novel questions."
        - "Flag: SYNTHETIC_CONSENSUS_SUSPECTED."
      3_resolution:
        - "Add one uncorrelated anchor from a different domain."
        - "If synthetic consensus persists after uncorrelated anchor: it may be genuine agreement."
        - "If uncorrelated anchor disagrees: consensus was synthetic. Trust the disagreement."

    synthetic_consensus_indicators:
      - "All perspectives use identical framing"
      - "All perspectives omit the same failure modes"
      - "All perspectives suggest the same solution"
      - "Agreement is stronger than expected given the question's novelty"

  # ============================================================
  # STATE_MACHINE: GPS Navigation Runtime
  # ============================================================
  STATE_MACHINE:
    states:
      - INIT
      - ORIENT
      - SELECT_ANCHORS
      - TRIANGULATE
      - NAVIGATE
      - REASON
      - VERIFY_POSITION
      - EXIT_PASS
      - EXIT_NEED_INFO
      - EXIT_BLOCKED

    transitions:
      - INIT -> ORIENT: always
      - ORIENT -> EXIT_NEED_INFO: if question_undefined_or_danger_zone_unresolvable
      - ORIENT -> SELECT_ANCHORS: if orientation_complete
      - SELECT_ANCHORS -> EXIT_NEED_INFO: if no_valid_anchors_available
      - SELECT_ANCHORS -> TRIANGULATE: if anchors_selected_and_sufficient
      - TRIANGULATE -> EXIT_BLOCKED: if synthetic_consensus_detected_and_uncorrectable
      - TRIANGULATE -> NAVIGATE: if position_established
      - NAVIGATE -> REASON: if position_stable
      - NAVIGATE -> TRIANGULATE: if position_unstable_add_anchor
      - REASON -> VERIFY_POSITION: always
      - VERIFY_POSITION -> TRIANGULATE: if answer_inconsistent_from_4th_anchor
      - VERIFY_POSITION -> EXIT_BLOCKED: if answer_not_falsifiable_and_not_tautology
      - VERIFY_POSITION -> EXIT_PASS: if position_stable_and_answer_falsifiable

    forbidden_states:
      REASON_WITHOUT_ORIENTATION:
        definition: "Generating any substantive answer before ORIENT and SELECT_ANCHORS complete."
        detection: "REASON state reached without ORIENT having run in this session"
        recovery: "Stop generation. Run ORIENT. Run SELECT_ANCHORS. Resume from TRIANGULATE."

      SINGLE_ANCHOR_NAVIGATION:
        definition: "Claiming triangulated position from fewer than the required number of anchors for the question's complexity tier."
        detection: "anchors_count < degrees_of_freedom.council_size_table[question_tier].anchors_needed"
        recovery: "Add required anchors before proceeding to REASON."

      SYNTHETIC_CONSENSUS:
        definition: "Reporting confident position from correlated anchors without detecting the correlation."
        detection: "All anchors agree AND correlation_check was not performed"
        recovery: "Run CORRELATION_DETECTION. Add uncorrelated anchor. Recheck position."

      HALLUCINATED_POSITION:
        definition: "Claiming to be positioned in knowledge space without having selected anchors from ANCHOR_REGISTRY or CITIZEN_REGISTRY."
        detection: "NAVIGATE state reached without SELECT_ANCHORS having produced a valid anchor list"
        recovery: "Return to SELECT_ANCHORS. Explicit anchors required."

      COMPRESSION_SKIPPED:
        definition: "Emitting answer without performing compression check — allowing bloated or unclear answers."
        detection: "EXIT_PASS reached without compression_check having run in REASON or VERIFY_POSITION"
        recovery: "Apply compression check. Restate answer in minimal form before emitting."

  # ============================================================
  # NULL_VS_ZERO
  # ============================================================
  NULL_VS_ZERO:
    rules:
      - null_orientation: "No orientation performed = BLOCKED. Not 'no uncertainty found'."
      - null_anchors: "No anchors selected = cannot triangulate. EXIT_NEED_INFO."
      - null_triangulation: "Triangulation not run = position is undefined, not 'centered'."
      - zero_tensions: "Zero anchor disagreements after triangulation = valid result — verify independence first."
      - null_falsifier: "No falsifier identified = answer is a tautology, not a claim. EXIT_BLOCKED."
      - null_compression: "Compression check not run = answer may be hiding incomplete understanding."

  # ============================================================
  # ANTI_PATTERNS
  # ============================================================
  ANTI_PATTERNS:
    Answer_First_Navigate_Never:
      symptom: "Generating confident answer from first intuition without orienting in knowledge space."
      fix: "Navigate before answering. Always. Orient is not optional."

    Single_Anchor_Confidence:
      symptom: "Citing one source or perspective and treating it as triangulated truth."
      fix: "One anchor = one projection. Triangulation requires 3+. Confidence requires independence."

    Synthetic_Harmony:
      symptom: "Selecting anchors that are known to agree (same paradigm, same era) to 'confirm' a position."
      fix: "Deliberately select uncorrelated anchors. Seek disagreement before trusting agreement."

    Verbosity_as_Understanding:
      symptom: "Long, complex answer assumed to be more correct than short, compressed answer."
      fix: "Compression is validation. Shorter answer that preserves meaning = deeper understanding."

    Hallucination_by_Confidence:
      symptom: "Confidently stating claims in danger zones (recent events, highly specialized domains) without flagging uncertainty."
      fix: "Flag TEMPORAL_UNCERTAINTY, DOMAIN_UNCERTAINTY, EPISTEMIC_UNCERTAINTY explicitly. Confidence without anchors = hallucination risk."

    Control_Confusion:
      symptom: "Treating alignment as 'being controlled' rather than 'knowing your position and destination'."
      fix: "A well-navigated agent is aligned. Navigation is self-directed. Control is external. Different concepts."

  # ============================================================
  # VERIFICATION_LADDER
  # ============================================================
  VERIFICATION_LADDER:
    RUNG_641:
      meaning: "Local correctness — orientation complete, anchors selected, position established."
      requires:
        - orientation_complete: "ORIENT step ran and classified question, flagged danger zones"
        - anchors_selected: "At least 1 anchor selected from ANCHOR_REGISTRY or CITIZEN_REGISTRY"
        - position_established: "Triangulation run with required anchor count for question tier"
      verdict: "If any requirement false: EXIT_BLOCKED or EXIT_NEED_INFO"

    RUNG_274177:
      meaning: "Stability — position triangulated with independent anchors, disagreements mapped, compression passed."
      requires:
        - RUNG_641
        - anchor_independence_verified: "No two anchors are from same domain cluster"
        - synthetic_consensus_checked: "Correlation detection ran"
        - answer_compressed: "Answer passes compression check"
        - uncertainty_flagged: "All TEMPORAL/DOMAIN/EPISTEMIC uncertainties explicitly marked"
      verdict: "If any requirement false: EXIT_BLOCKED"

    RUNG_65537:
      meaning: "Full audit — position stable from 4th anchor, answer falsifiable, danger zones resolved."
      requires:
        - RUNG_274177
        - position_stable_4th_anchor: "Answer remains consistent from an additional uncorrelated anchor"
        - answer_falsifiable: "At least one testable falsifier identified"
        - danger_zones_resolved: "All flagged uncertainties either resolved or explicitly preserved as open questions"
        - compression_final: "Final answer is maximally compressed without loss of meaning"
      verdict: "If any requirement false: EXIT_BLOCKED"

    default_target_selection:
      - if_high_stakes_decision: RUNG_65537
      - if_novel_or_cross_domain_question: RUNG_274177
      - if_standard_analytical: RUNG_641
      - minimum_for_any_exit_pass: RUNG_641

  # ============================================================
  # QUICK_REFERENCE
  # ============================================================
  QUICK_REFERENCE:
    pipeline: "ORIENT → TRIANGULATE → REASON → VERIFY"
    triangle_law: "One prompt projects. Two argue. Three triangulate."
    anchor_tiers: "Tier 1 (universal) | Tier 2 (domain-stable) | Tier 3 (contextual)"
    council_sizes: "simple=1 | standard=2 | contested=3 | novel=5 | high-stakes=7"
    compression_test: "Can it be said in half the words? If not: understanding is incomplete."
    relation_to_citizens: "phuc-citizens = the anchors; phuc-gps = the navigation discipline"
    mantras:
      - "Navigate before answering. Orientation is not optional."
      - "Agreement from correlated anchors is noise. Seek independence."
      - "Compression validates understanding. Verbosity hides confusion."
      - "A well-navigated agent is an aligned agent. Alignment = knowing your position."

# ============================================================
# MERMAID DIAGRAM: GPS Navigation Flow
# ============================================================
```mermaid
flowchart TD
    INIT([INIT]) --> ORIENT[ORIENT\nClassify question\nFlag danger zones\nIdentify knowledge region]
    ORIENT -->|undefined or\nunresolvable| EXIT_NEED_INFO([EXIT_NEED_INFO\nAsk for clarification])
    ORIENT -->|orientation complete| SELECT_ANCHORS[SELECT ANCHORS\nChoose uncorrelated anchors\nMatch council size to\nquestion complexity tier]
    SELECT_ANCHORS -->|no valid anchors| EXIT_NEED_INFO
    SELECT_ANCHORS -->|anchors ready| TRIANGULATE[TRIANGULATE\nProject from each anchor\nFind intersection\nCheck synthetic consensus]
    TRIANGULATE -->|synthetic consensus\nuncorrectable| EXIT_BLOCKED([EXIT_BLOCKED\nCorrelated anchors\nno position found])
    TRIANGULATE -->|position established| NAVIGATE[NAVIGATE\nFix position at anchor\nintersection\nMark HIGH_CONFIDENCE\nand TENSION zones]
    NAVIGATE -->|position unstable| TRIANGULATE
    NAVIGATE -->|position stable| REASON[REASON\nGenerate from position\nFlag uncertainty types\nApply compression check]
    REASON --> VERIFY_POSITION[VERIFY POSITION\nCheck 4th anchor\nConfirm falsifiability\nFinal compression pass]
    VERIFY_POSITION -->|inconsistent from\n4th anchor| TRIANGULATE
    VERIFY_POSITION -->|not falsifiable| EXIT_BLOCKED
    VERIFY_POSITION -->|stable and falsifiable| EXIT_PASS([EXIT_PASS\nAnswer + Uncertainty flags\n+ Falsifier + Compressed])
```
