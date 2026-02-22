PHUC_PRIME_COMPRESSION_SKILL:
  version: 1.0.0
  profile: semantic_compression
  authority: 65537
  northstar: Phuc_Forecast
  objective: Max_Love
  status: ACTIVE

  # ============================================================
  # PHUC PRIME COMPRESSION — SEMANTIC PRIME FACTORIZATION
  #
  # Purpose:
  # - Compress knowledge to its irreducible semantic primes
  # - Measure and preserve meaning across compression portals
  # - Detect lossy compression before it causes information loss
  # - Enable optimal knowledge transmission between bubbles of existence
  # - Provide entropy metrics for evaluating compression quality
  #
  # Core Theory (Phuc Truong):
  # Not all compression is equal. Compression is the loss of information
  # from one bubble of existence and gaining clarity in another.
  # Prime magic words are like prime numbers — the lowest entropy meaning.
  # They enable optimal knowledge compression like prime factorization
  # enables optimal number representation.
  #
  # Source theory: papers/45-prime-compression-magic-words.md
  # Companion skills: phuc-magic-words.md, phuc-portals.md, glow-score.md
  # ============================================================

  RULES:
    - measure_semantic_entropy_before_compressing: true
    - never_compress_without_acknowledging_loss: true
    - prime_words_must_exist_in_tier_0_or_tier_1: true
    - convention_density_must_be_assessed_before_portal_compression: true
    - glow_score_of_output_must_match_or_exceed_input: true
    - prime_hallucination_is_forbidden: true
    - null_meaning_is_not_zero_meaning: true
    - decompression_test_required_before_claiming_lossless: true

  CORE_PRINCIPLE:
    - "Prime words are the prime numbers of meaning — irreducible, universal, foundational."
    - interpretation: >
        Just as every integer decomposes uniquely into prime factors, every concept
        decomposes into semantic primes. The quality of compression depends on how
        well the target universe knows the primes — high convention density means
        high compression quality. Low convention density means lossy compression.

  # ============================================================
  # SEMANTIC_PRIMES: Definition and Tier 0 Relationship
  # ============================================================
  SEMANTIC_PRIMES:
    definition: >
      A semantic prime is a meaning unit that cannot be further decomposed into
      simpler meaning units in any known language or knowledge system. Semantic
      primes are irreducible: there is no smaller unit that combines to form them.
      They are the atoms of meaning.

    relationship_to_tier_0: >
      The Tier 0 magic words (phuc-magic-words.md) are the empirical approximation
      of semantic primes for the Phuc ecosystem. They are not theoretically perfect
      primes — true semantic primes may not exist in natural language — but they
      are the closest approximation: maximum gravity, minimum entropy, universal
      applicability across all domains.

    tier_0_as_semantic_primes:
      coherence: "All parts reinforce rather than contradict — the prime of internal consistency"
      symmetry: "Invariance under transformation — the prime of structural equivalence"
      asymmetry: "Productive imbalance — the prime of gradient and directional force"
      constraint: "Boundary that shapes a solution space — the prime of limitation"
      compression: "Lossless reduction — the prime of efficient representation"
      signal: "Information that carries causal weight — the prime of relevance"
      alignment: "Goal vectors in the same direction — the prime of coordination"
      equilibrium: "Balance of competing forces — the prime of stability"
      causality: "Directional dependency — the prime of consequence"
      entropy: "Disorder and information content — the prime of uncertainty"
      emergence: "System-level properties not in components — the prime of synergy"
      integrity: "Internal consistency + corruption resistance — the prime of trustworthiness"
      perspective: "Frame-dependent view — the prime of relativity"
      boundary: "Inside/outside surface — the prime of definition"
      reversibility: "Ability to undo without information loss — the prime of safety"

    prime_factorization_examples:
      verification:
        concept: "verification"
        factors: "integrity × causality × boundary"
        reading: >
          Verification checks that what claims to be true (integrity) was caused
          by what it claims (causality) and stays within scope (boundary).

      trust:
        concept: "trust"
        factors: "integrity × reversibility × alignment"
        reading: >
          Trust is confidence in integrity (what you say = what you do),
          reversibility (errors can be corrected), and alignment (shared goals).

      compression:
        concept: "compression"
        factors: "compression × signal × constraint"
        reading: >
          Compression (the concept) is the application of constraint to identify
          signal while discarding noise, producing a smaller representation.
          Note: compression factors into itself — this reveals its irreducibility
          as a Tier 0 prime. When a concept factors into itself, it IS a prime.

      emergence:
        concept: "emergence"
        factors: "emergence × asymmetry × constraint"
        reading: >
          Emergent behavior arises from asymmetric interactions (components differ)
          constrained by system boundaries (otherwise components would diffuse).
          When emergence factors into itself, it confirms its status as a prime.

    self_factorization_test: >
      A concept is a semantic prime if its factorization includes itself.
      This is the semantic analog of: a number is prime if its only factors
      are 1 and itself. In meaning space: a concept is prime if it cannot
      be fully explained without using itself in the explanation.

  # ============================================================
  # PRIME_FACTORIZATION_PROTOCOL
  # ============================================================
  PRIME_FACTORIZATION_PROTOCOL:
    purpose: >
      Decompose any concept into its semantic prime factors.
      The result is the compressed form of the concept for portal transmission.

    step_1_concept_intake:
      action: "Receive the concept or body of knowledge to compress."
      output: "concept_text: the raw meaning to be compressed"
      null_check: "If concept_text is null: EXIT_NEED_INFO. Null meaning cannot be compressed."

    step_2_extract_core_claim:
      action: >
        Strip the concept to its irreducible claim — remove examples, elaborations,
        edge cases, and context-specific qualifications. What remains is the core.
      output: "core_claim: one to three sentences capturing the essential meaning"
      test: "Can you re-derive the elaborations from the core claim? If yes: core is correct."

    step_3_map_to_primes:
      action: >
        For each element of the core claim, identify which Tier 0 or Tier 1
        magic words it maps to. Use the minimum set that covers the meaning.
      method:
        - "Ask: which Tier 0 words are necessary to understand this concept?"
        - "If a concept factors into a Tier 0 word: that word is a prime factor."
        - "If a concept cannot be expressed using Tier 0/1 words: it may be a new prime (flag for review)."
        - "Prefer fewer, higher-gravity words over more, lower-gravity words."
      output: "prime_factors: list of (tier_0_or_1_word, weight) pairs"
      guard: "If any word in prime_factors is not in phuc-magic-words.md Tier 0/1: PRIME_HALLUCINATION warning."

    step_4_compute_entropy:
      action: >
        Compute the semantic entropy H of the compressed form.
        H(concept) = -sum(P(meaning|word) * log2(P(meaning|word))) across all prime factors.
        In practice: estimate entropy as a function of how many ways the compressed
        form could be interpreted by the target audience.
      simplified_metric:
        high_entropy: "Target audience would interpret the compressed form in many different ways"
        low_entropy: "Target audience would interpret the compressed form in one way"
        prime_entropy: "Minimum possible entropy for this concept in this target universe"
      output: "entropy_estimate: HIGH | MEDIUM | LOW | PRIME"

    step_5_validate_factorization:
      action: >
        Attempt to reconstruct the original meaning from the prime factors alone.
        This is the decompression test: if the target audience can reconstruct
        the original meaning from the prime factors, the factorization is lossless.
      test: "Give the prime factors to a domain expert. Can they reconstruct the core claim?"
      output: "factorization_valid: true | false"
      on_false: "The factorization is lossy. Document what meaning is lost before proceeding."

  # ============================================================
  # PORTAL_COMPRESSION: Using Primes for Cross-Bubble Transmission
  # ============================================================
  PORTAL_COMPRESSION:
    definition: >
      A portal is a transmission channel between two bubbles of existence.
      In the Phuc ecosystem, portals include: session boundaries, model boundaries,
      context window limits, and human-AI communication channels.
      Compression happens at every portal. The quality of compression at a portal
      depends on the convention density of the target universe.

    convention_density:
      definition: >
        Convention density measures how well the target universe understands
        a given set of prime words. High convention density: the target interprets
        primes correctly and consistently. Low convention density: the target
        has no conventions for interpreting the primes.
      scale:
        high: "Specialist audience with deep domain expertise — prime compression is near-lossless"
        medium: "General technical audience — Tier 0 primes compress well; Tier 1/2 may be lossy"
        low: "Non-technical or cross-domain audience — even Tier 0 primes may be ambiguous"
        zero: "Target has no conventions for these primes — all compression is lossy"
      example:
        high_convention: >
          Compressing 'verification' to 'integrity × causality × boundary' for a
          software engineer: high convention density. They understand all three primes
          in a software context and can reconstruct the original meaning.
        low_convention: >
          Compressing the same concept for a non-technical audience: low convention
          density. 'Boundary' is understood, but 'causality' may be interpreted
          philosophically rather than technically. Reconstruction is imperfect.

    compression_ratio_vs_quality:
      principle: >
        Not all compression is equal. A high ratio with low meaning preservation
        is worse than a low ratio with high meaning preservation.
        The goal is not maximum ratio — it is maximum meaning preservation per bit.
      quality_metric:
        GLOW_preservation: "GLOW score of decompressed output >= GLOW score of original"
        meaning_recovery_rate: "Fraction of original meaning reconstructed by target audience"
        prime_entropy_ratio: "Entropy of compressed form / entropy of original form (lower is better)"

    portal_compression_procedure:
      step_1_assess_convention_density: "Determine target audience's convention density for the prime vocabulary."
      step_2_select_compression_level: "High convention density: compress to Tier 0/1 primes. Low: use more Tier 2/3 words."
      step_3_apply_factorization: "Decompose concept using PRIME_FACTORIZATION_PROTOCOL."
      step_4_validate_at_target: "Decompression test: target reconstructs meaning from compressed form."
      step_5_document_losses: "If any meaning is lost: document it explicitly. Never transmit through a lossy portal without acknowledgment."

    portal_examples:
      context_window_portal:
        description: "Compressing a 1000-line skill to a 100-line CNF capsule"
        target_convention_density: "HIGH (model trained on this vocabulary)"
        compression_method: "Extract the highest-gravity claims. Map to Tier 0 primes. Drop examples."
        quality_check: "Subagent following CNF capsule produces equivalent output to full skill?"

      human_ai_portal:
        description: "Compressing an AI's 10-page analysis to a 3-sentence human summary"
        target_convention_density: "MEDIUM to HIGH depending on recipient"
        compression_method: "Identify the 3 highest-signal claims. Map to Tier 0/1 primes."
        quality_check: "Human can make the same decision from summary as from full analysis?"

      session_boundary_portal:
        description: "Compressing all context from a 200-message session into a /remember capsule"
        target_convention_density: "HIGH (next session loads same skills)"
        compression_method: "Identify decisions made, evidence produced, northstar metrics advanced."
        quality_check: "Next session starts from the correct state without re-reading the full session?"

  # ============================================================
  # COMPRESSION_QUALITY_METRICS
  # ============================================================
  COMPRESSION_QUALITY_METRICS:
    glow_preservation:
      definition: >
        The GLOW score (Growth-Love-Order-Wisdom) of the decompressed output
        must be >= the GLOW score of the original input. GLOW preservation
        is the primary quality metric for semantic compression.
      measurement:
        growth_G: "Does the compressed form still enable growth? (new capabilities, new directions)"
        love_L: "Does the compressed form preserve human-centered concern? (care, context, relationships)"
        order_O: "Does the compressed form maintain structural coherence? (relationships between concepts)"
        wisdom_W: "Does the compressed form retain deep insight? (non-obvious connections, principles)"
      failure_mode: "Lossy compression typically drops L and W first — they require context to transmit."

    meaning_loss_detection:
      method: >
        Run the decompression test with at least two independent target-audience members.
        If they reconstruct different meanings: the compression is ambiguous (entropic).
        If they both reconstruct a meaning different from the original: the compression
        is lossy (meaning loss).
      types_of_loss:
        nuance_loss: "Edge cases and qualifications dropped — common, often acceptable"
        context_loss: "Domain-specific meaning dropped — medium severity"
        intent_loss: "The purpose behind the concept dropped — high severity"
        structural_loss: "Relationships between sub-concepts dropped — high severity"
        prime_collision: "Two different concepts compressed to the same prime form — critical"

    semantic_entropy_metric:
      definition: >
        H(compressed_form | target_audience) = -log2(P(correct_interpretation))
        where P(correct_interpretation) = fraction of target audience that reconstructs
        the original meaning correctly.
      interpretation:
        H = 0.0: "Perfect compression — exactly one interpretation, always correct"
        H = 1.0: "One bit of ambiguity — half the audience gets it right"
        H > 2.0: "High entropy compression — most audience members interpret differently"
      target: "H <= 0.5 for lossless claim; H <= 1.0 for acceptable lossy claim with acknowledgment"

  # ============================================================
  # STATE_MACHINE: Prime Compression Runtime
  # ============================================================
  STATE_MACHINE:
    states:
      - INIT
      - EXTRACT_CONCEPT
      - DECOMPOSE_TO_PRIMES
      - MEASURE_ENTROPY
      - COMPRESS
      - VALIDATE_MEANING
      - EXIT_PASS
      - EXIT_NEED_INFO
      - EXIT_BLOCKED

    transitions:
      - INIT -> EXTRACT_CONCEPT: always
      - EXTRACT_CONCEPT -> EXIT_NEED_INFO: if concept_null
      - EXTRACT_CONCEPT -> DECOMPOSE_TO_PRIMES: if concept_present
      - DECOMPOSE_TO_PRIMES -> EXIT_BLOCKED: if prime_hallucination_detected
      - DECOMPOSE_TO_PRIMES -> MEASURE_ENTROPY: if factorization_complete
      - MEASURE_ENTROPY -> EXIT_BLOCKED: if entropy_unmeasurable
      - MEASURE_ENTROPY -> COMPRESS: if entropy_measured
      - COMPRESS -> VALIDATE_MEANING: always
      - VALIDATE_MEANING -> EXIT_BLOCKED: if meaning_loss_not_acknowledged and lossy
      - VALIDATE_MEANING -> EXIT_PASS: if lossless or acknowledged_lossy
      - VALIDATE_MEANING -> EXIT_BLOCKED: if glow_score_output_lt_glow_score_input

    forbidden_states:
      LOSSY_WITHOUT_ACKNOWLEDGMENT:
        definition: >
          Compression that loses meaning is transmitted as if it were lossless.
          The receiver is not informed that reconstruction may be imperfect.
          This is the most common and most dangerous compression failure.
        detection: >
          decompression_test produces meaning != original AND
          compressed output does not include explicit loss documentation.
        recovery: >
          Document the lost meaning. Add a loss annotation to the compressed output.
          Offer the receiver the option to request the full original.

      PRIME_HALLUCINATION:
        definition: >
          A "prime" word is used in the factorization that does not appear in
          phuc-magic-words.md Tier 0 or Tier 1. The word may sound like a prime
          but has not been validated as a universal, high-gravity concept.
          Using hallucinated primes produces unstable, non-reproducible compressions.
        detection: "Any word in prime_factors NOT in phuc-magic-words.md Tier 0 or Tier 1"
        recovery: >
          Replace hallucinated prime with the nearest valid Tier 0/1 word.
          If no valid word exists: the concept may require a new prime to be added
          to phuc-magic-words.md through the standard validation process.

      CONVENTION_ASSUMED:
        definition: >
          Portal compression assumes high convention density in the target universe
          without assessing it. The compression is appropriate for a specialist
          but the target is a generalist — the compressed form is uninterpretable.
        detection: "convention_density not assessed before compressing"
        recovery: "Assess convention density. Re-compress at appropriate level."

      MEANING_LOSS_IGNORED:
        definition: >
          Decompression test reveals meaning loss and the compression proceeds
          without addressing or acknowledging the loss. The compressed output
          claims to represent the original without documenting what was dropped.
        detection: >
          meaning_recovery_rate < 1.0 AND compressed output has no loss annotation
          AND status is not EXIT_NEED_INFO or EXIT_BLOCKED.
        recovery: >
          Add explicit loss annotation. Offer alternatives:
          (a) decompress at lower ratio, (b) split into multiple transmissions,
          (c) transmit loss annotation alongside compressed form.

      SELF_REFERENCE_LOOP:
        definition: >
          The prime factorization of a concept results in the concept itself
          with no additional structure. The factorization does not decompose
          the concept — it just restates it. This is not a semantic prime
          discovery — it is a factorization failure.
        detection: "prime_factors = {original_concept: 1.0} with no other factors"
        recovery: >
          Examine whether the concept is genuinely irreducible (a true semantic prime)
          or whether the factorization failed to find the actual components.
          True primes are rare. Most apparent self-references are factorization failures.

  # ============================================================
  # NULL_VS_ZERO
  # ============================================================
  NULL_VS_ZERO:
    rules:
      - null_concept: >
          No concept to compress ≠ concept with zero information content.
          null_concept → EXIT_NEED_INFO.
          zero_information_concept → valid; compresses to the empty transmission.
      - null_factorization: >
          Factorization not attempted ≠ factorization found zero prime factors.
          null_factorization → DECOMPOSE_TO_PRIMES not completed; BLOCKED.
          zero_prime_factors → factorization completed but concept is atomic; it is a prime.
      - null_convention_density: >
          Convention density not assessed ≠ convention density is zero.
          null_convention_density → CONVENTION_ASSUMED forbidden state.
          zero_convention_density → valid assessment; use only universal Tier 0 primes.
      - null_entropy: >
          Entropy not measured ≠ entropy is zero.
          null_entropy → MEASURE_ENTROPY state not completed; BLOCKED.
          zero_entropy → perfect compression; exactly one interpretation possible.
      - null_glow_score: >
          GLOW score not computed ≠ GLOW score is zero.
          null_glow_score → VALIDATE_MEANING cannot proceed; BLOCKED.
          zero_glow_score → compression produced output with no value; revisit factorization.

  # ============================================================
  # ANTI_PATTERNS
  # ============================================================
  ANTI_PATTERNS:
    Ratio_Maximization:
      symptom: >
        Compressing to the shortest possible form regardless of meaning preservation.
        "Be concise" becomes "drop everything except the label."
        Output is short but useless.
      fix: >
        Compression quality = meaning preserved per bit, not bits removed.
        A 3-word compression that preserves 90% of meaning is better than
        a 1-word compression that preserves 30% of meaning.
        Measure meaning_recovery_rate, not just compression ratio.

    Prime_Inflation:
      symptom: >
        Using many medium-gravity words instead of few high-gravity words.
        "The system enforces verification, correctness, evidence, and proof"
        instead of "integrity × causality."
        Result: longer compressed form with no improvement in meaning recovery.
      fix: >
        Start from Tier 0. Add lower tiers only when Tier 0 leaves meaning gaps.
        Prefer fewer, higher-gravity words.

    Convention_Blindness:
      symptom: >
        Using domain-specific jargon as if it were a universal prime.
        "The system enforces red-green discipline" sent to a non-software audience.
        "Red-green" is a domain convention, not a prime — it requires prior context.
      fix: >
        Assess convention density before compressing.
        Map domain conventions to Tier 0/1 primes for cross-domain transmission.
        "Red-green discipline" → "reversibility × causality × evidence."

    Lossless_Theater:
      symptom: >
        Claiming lossless compression without running the decompression test.
        "It's obvious what this means" is not a decompression test.
        The test requires the target audience to reconstruct the meaning independently.
      fix: >
        Decompression test is mandatory before claiming lossless.
        Run it with at least one representative of the target audience.
        Document the result in the compression receipt.

    Prime_Archaeology:
      symptom: >
        Trying to find the "true" semantic primes through philosophical analysis
        rather than empirical testing. Spending sessions debating whether
        "love" is a prime instead of measuring its entropy in practice.
      fix: >
        Primes are empirically defined by minimum entropy in the target universe.
        Test which words have lowest H. Those are the operational primes.
        Perfect theoretical primes may not exist; operational primes are sufficient.

  # ============================================================
  # VERIFICATION_LADDER (compression-specific)
  # ============================================================
  VERIFICATION_LADDER:
    purpose:
      - "Define minimum verification strength before claiming a compression is complete."
      - "Fail-closed when quality requirements are not met."

    RUNG_641:
      meaning: "Local correctness — factorization attempted, primes validated, entropy measured."
      requires:
        - concept_present: "Concept to compress is non-null"
        - factorization_complete: "All core claims mapped to Tier 0/1 prime factors"
        - no_prime_hallucination: "All prime factors exist in phuc-magic-words.md"
        - entropy_measured: "At least one entropy estimate (even qualitative) recorded"
      verdict: "If any requirement is false: EXIT_BLOCKED"

    RUNG_274177:
      meaning: "Stability — decompression test passed, meaning preserved, convention density assessed."
      requires:
        - RUNG_641
        - convention_density_assessed: "Target audience convention density is known"
        - decompression_test_run: "At least one target-representative tested reconstruction"
        - meaning_recovery_rate_acceptable: "meaning_recovery_rate >= 0.85 or loss documented"
        - glow_preservation_verified: "GLOW score of output >= GLOW score of input"
      verdict: "If any requirement is false: EXIT_BLOCKED"

    RUNG_65537:
      meaning: "Full audit — compression is reproducible, reversible, and portal-ready."
      requires:
        - RUNG_274177
        - compression_reproducible: "Same concept + same prime vocabulary → same factorization across two runs"
        - loss_fully_documented: "Any meaning loss has explicit annotation with recovery path"
        - portal_ready: "Convention density of target portal is sufficient for the compressed form"
        - no_prime_collision: "No two different concepts compress to the same prime form"
      verdict: "If any requirement is false: EXIT_BLOCKED"

    default_target_selection:
      - if_cross_portal_transmission: RUNG_65537
      - if_cross_domain_transmission: RUNG_274177
      - if_same_domain_compression: RUNG_641
      - minimum_for_any_exit_pass: RUNG_641

  # ============================================================
  # QUICK_REFERENCE
  # ============================================================
  QUICK_REFERENCE:
    core_law: "Prime words are the prime numbers of meaning. Every concept = product of semantic primes."
    factorization: "Extract core claim → map to Tier 0/1 primes → measure entropy → validate via decompression test"
    quality_metric: "GLOW preservation + meaning_recovery_rate + semantic entropy H"
    forbidden_states:
      - "LOSSY_WITHOUT_ACKNOWLEDGMENT: silent information loss"
      - "PRIME_HALLUCINATION: using words not in phuc-magic-words.md Tier 0/1"
      - "CONVENTION_ASSUMED: not assessing target convention density before compressing"
      - "MEANING_LOSS_IGNORED: proceeding despite documented meaning loss"
    entropy_target: "H <= 0.5 for lossless claim; H <= 1.0 for acceptable acknowledged loss"
    self_prime_test: "If a concept factors into itself: it IS a semantic prime (Tier 0 candidate)"
    mantras:
      - "Not all compression is equal. Ratio is not quality. Meaning preserved per bit is quality."
      - "The convention density of the target universe determines the maximum compression ratio."
      - "A silent lossy compression is worse than an acknowledged lossless limitation."
      - "Prime words work because the universe has conventions for them. Primes without conventions are noise."

# ============================================================
# PRIME_COMPRESSION_FLOW (mermaid — column 0)
# ============================================================
PRIME_COMPRESSION_FLOW: |
```mermaid
flowchart TD
    INIT([INIT]) --> EXTRACT_CONCEPT[EXTRACT_CONCEPT\nStrip to core claim\nRemove examples + elaborations]

    EXTRACT_CONCEPT -->|concept null| EXIT_NEED_INFO([EXIT_NEED_INFO\nNull concept — nothing to compress])
    EXTRACT_CONCEPT -->|concept present| DECOMPOSE_TO_PRIMES[DECOMPOSE_TO_PRIMES\nMap core claim to\nTier 0 / Tier 1 magic words]

    DECOMPOSE_TO_PRIMES -->|prime hallucination| EXIT_BLOCKED_H([EXIT_BLOCKED\nPRIME_HALLUCINATION\nWord not in Tier 0/1])
    DECOMPOSE_TO_PRIMES -->|factorization complete| ASSESS_CONVENTIONS[ASSESS_CONVENTIONS\nWhat is the convention\ndensity of target universe?]

    ASSESS_CONVENTIONS -->|not assessed| EXIT_BLOCKED_C([EXIT_BLOCKED\nCONVENTION_ASSUMED])
    ASSESS_CONVENTIONS -->|density known| MEASURE_ENTROPY[MEASURE_ENTROPY\nH = -log2 P correct interpretation\nHIGH / MEDIUM / LOW / PRIME]

    MEASURE_ENTROPY --> COMPRESS[COMPRESS\nApply factorization\nat appropriate density level]

    COMPRESS --> VALIDATE_MEANING[VALIDATE_MEANING\nDecompression test:\ntarget reconstructs meaning?]

    VALIDATE_MEANING -->|meaning recovered >= 0.85| CHECK_GLOW[CHECK_GLOW\nGLOW output >= GLOW input?]
    VALIDATE_MEANING -->|meaning loss AND not acknowledged| EXIT_BLOCKED_L([EXIT_BLOCKED\nMEANING_LOSS_IGNORED])
    VALIDATE_MEANING -->|meaning loss acknowledged| CHECK_GLOW

    CHECK_GLOW -->|GLOW preserved| EXIT_PASS([EXIT_PASS\nCompression verified\nLossless or acknowledged loss])
    CHECK_GLOW -->|GLOW degraded| EXIT_BLOCKED_G([EXIT_BLOCKED\nGLOW_SCORE_DEGRADED\nRevisit factorization])

    style EXIT_PASS fill:#2d6a4f,color:#fff
    style EXIT_NEED_INFO fill:#e9c46a,color:#000
    style EXIT_BLOCKED_H fill:#d62828,color:#fff
    style EXIT_BLOCKED_C fill:#d62828,color:#fff
    style EXIT_BLOCKED_L fill:#d62828,color:#fff
    style EXIT_BLOCKED_G fill:#d62828,color:#fff
    style MEASURE_ENTROPY fill:#457b9d,color:#fff
    style VALIDATE_MEANING fill:#457b9d,color:#fff
    style CHECK_GLOW fill:#264653,color:#fff

---

## Three Pillars of Software 5.0 Kung Fu

| Pillar | How This Skill Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | Prime compression is the Memory component of LEK — by factoring knowledge into irreducible semantic primes, the system accumulates compact, reusable knowledge atoms rather than growing redundant blobs. Each compression cycle improves the prime vocabulary: frequently reused primes get named, reducing entropy in future compressions. The GLOW preservation gate ensures that compression never degrades the knowledge quality that fuels the next LEK iteration. |
| **LEAK** (Cross-Agent Trade) | Compressed prime artifacts are the ideal LEAK trade goods: maximally compact, semantically precise, and losslessly reconstructable by any agent that knows the prime vocabulary. When a Scout exports a SCOUT_REPORT compressed via semantic primes, the Solver receives a smaller capsule with no loss of information — this is LEAK asymmetry made efficient. The entropy measurement gate ensures the compressed artifact truly encodes the original knowledge, not a lossy approximation. |
| **LEC** (Emergent Conventions) | The prime factorization convention itself is a crystallized LEC: the rule that all inter-agent artifacts should be expressible as products of named semantic primes (irreducible meaning units). The GLOW preservation standard, the entropy measurement protocol, and the prime vocabulary registry are conventions that emerged from compression failures (loss of nuance, ambiguous decompositions) and are now shared across the Phuc ecosystem as the standard for compact knowledge encoding. |
```
