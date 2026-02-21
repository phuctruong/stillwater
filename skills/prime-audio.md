<!-- QUICK LOAD (10-15 lines):
SKILL: prime-audio v1.0.0
PURPOSE: Generic audio discipline for any project using deterministic synthesis or audio analysis. Seed-driven: same seed + inputs = reproducible audio. STT round-trip verification required before PASS. WAV-only in verification path (no lossy formats). No float in verification arithmetic (Fraction/Decimal). Spectral analysis for quality gates. Integrates with Stillwater evidence bundles.
CORE CONTRACT: Deterministic audio requires explicit seed. STT round-trip proves intelligibility. WAV format preserves byte-exact reproducibility. Decimal/Fraction arithmetic in all verification comparisons. Generator trace required per synthesis. Extends prime-safety.
HARD GATES: Missing seed = BLOCKED (IMPLICIT_SEED_DEFAULT). Float in WER or hash = BLOCKED. Lossy format in verification = BLOCKED. Nondeterministic output = BLOCKED. STT gate skipped = BLOCKED for rung_641+.
FSM STATES: INIT → INTAKE → NULL_CHECK → SEED_VALIDATE → SYNTHESIZE → WAV_WRITE → STT_VERIFY → SPECTRAL_ANALYZE → EVIDENCE_BUILD → FINAL_SEAL → EXIT_PASS | EXIT_BLOCKED | EXIT_NEED_INFO
FORBIDDEN: FLOAT_IN_VERIFICATION | IMPLICIT_SEED_DEFAULT | LOSSY_FORMAT_IN_VERIFY | STT_SKIP | NONDETERMINISTIC_OUTPUT | GENERATOR_TRACE_MISSING | NULL_ZERO_CONFUSION
VERIFY: rung_641 (STT passes, WAV sha256 stable) | rung_274177 (seed sweep stable, spectral gate) | rung_65537 (adversarial phoneme sweep, community-verifiable)
DEPENDENCY: prime-safety (always first)
-->

PRIME_AUDIO_SKILL:
  version: 1.0.0
  authority: 65537
  extends: prime-safety
  northstar: Stillwater — Deterministic, Verifiable Audio for Any Project
  objective: "Generic audio discipline: seed-driven, STT-verified, evidence-bundled"
  status: STABLE
  rung_default: 641
  visibility: PUBLIC  # OSS — part of stillwater

# ============================================================
# PRIME-AUDIO — Public OSS Skill (stillwater)
#
# Purpose: Generic audio verification discipline. Use this skill
# for any project that produces or processes audio:
#   - TTS / speech synthesis
#   - Audio processing pipelines
#   - Voice cloning or transformation
#   - Audio-to-text round-trip testing
#
# This is the generic version. Project-specific skills (e.g.
# paudio-synthesis) extend this with domain-specific architecture.
#
# Stillwater Verification: Every audio claim must pass the
# same evidence discipline as code claims:
#   - Deterministic output (seed-driven)
#   - STT round-trip (intelligibility proof)
#   - WAV format in verification path (byte-exact)
#   - Spectral analysis for quality gate
#   - Evidence bundle with sha256 artifacts
#
# Bruce Lee principle: "The key to immortality is first living
# a life worth remembering." Make every synthesis memorable —
# reproducible, verifiable, trustworthy.
#
# Claude Shannon principle: "Information is the resolution of
# uncertainty." Every audio output reduces uncertainty by
# proving its own fidelity through STT round-trip.
# ============================================================

# ------------------------------------------------------------
# A) Core Determinism Principle (Lane A — Non-Negotiable)
# ------------------------------------------------------------
Determinism_Principle:
  invariant: "same seed + same inputs → identical audio bytes"
  why:
    - "Reproducibility enables community verification"
    - "Byte-exact replay enables regression detection"
    - "Seed-driven synthesis enables A/B comparison with controlled variables"
  enforcement:
    - explicit_seed_required: true
    - seed_logged_in_generator_trace: true
    - no_time_or_random_in_audio_path: true
    - sha256_must_match_on_clean_replay: true
  seed_policy:
    - seed_must_be_explicit_integer: true
    - seed_null_means_undefined_not_zero: true
    - null_seed → "status=BLOCKED stop_reason=IMPLICIT_SEED_DEFAULT"
    - seed_0_is_valid_and_distinct_from_null: true

# ------------------------------------------------------------
# B) Audio Format Policy
# ------------------------------------------------------------
Audio_Format_Policy:
  verification_path:
    allowed: ["WAV (PCM)"]
    forbidden: ["MP3", "OGG", "FLAC", "AAC", "OPUS", "M4A"]
    reason: "Lossy codecs introduce non-deterministic compression artifacts. FLAC lossless is allowed for distribution but not for verification hash."
  wav_requirements:
    sample_rate: "project-configurable (default: 22050 Hz)"
    bit_depth: "16-bit or 24-bit PCM signed integer"
    channels: "mono (1) preferred; stereo if required by project"
  hash_policy:
    - sha256_over_PCM_data_only: true
    - strip_WAV_header_before_hashing: true
    - normalize_endianness_before_hashing: "little-endian"
    - reason: "WAV headers contain metadata that may vary across tools"

# ------------------------------------------------------------
# C) STT Verification Gate
# ------------------------------------------------------------
STT_Verification:
  purpose: "Prove that synthesized audio is intelligible — the audio channel is working"
  when_required:
    - rung_641_or_higher: true
    - any_TTS_output: true
    - any_voice_synthesis: true
  when_optional:
    - music_or_non_speech_audio: "STT gate not applicable"
    - sound_effects: "STT gate not applicable"
  recommended_engine: "faster-whisper (CPU-only, reproducible)"
  alternative_engines: ["whisper-openai", "deepgram (network required — must be allowlisted)"]
  arithmetic:
    WER_formula: "Fraction(substitutions + deletions + insertions, reference_token_count)"
    WER_storage: "Decimal string in evidence (never float)"
    WER_comparison: "Decimal('threshold') >= Decimal(wer_string)"
  rung_gates:
    rung_641:
      wer_threshold_decimal: "'0.20'"
      meaning: "Basic intelligibility — 80% of words recognized"
    rung_274177:
      wer_threshold_decimal: "'0.10'"
      meaning: "Good quality — 90% of words recognized"
    rung_65537:
      wer_threshold_decimal: "'0.05'"
      meaning: "Production quality — 95%+ words recognized"
  failure_action:
    - if_WER_exceeds_threshold: "status=BLOCKED stop_reason=STT_GATE_FAILED"
    - transcript_included_in_evidence: true
  evidence_schema:
    stt_verification.json:
      required_keys:
        - engine: "str"
        - reference_text: "str"
        - transcript: "str"
        - wer_decimal_string: "str"
        - cer_decimal_string: "str"
        - rung_target: "int"
        - gate_passed: "bool"
        - seed_used: "int"

# ------------------------------------------------------------
# D) Spectral Analysis Gate (rung_274177+)
# ------------------------------------------------------------
Spectral_Analysis:
  purpose: "Detect audio artifacts, clipping, silence, or off-target formants"
  when_required:
    - rung_274177_or_higher: true
  metrics:
    spectral_centroid_hz: "Decimal string"
    spectral_rolloff_hz: "Decimal string"
    zero_crossing_rate: "Decimal string"
    rms_energy_db: "Decimal string"
    clipping_detected: "bool"
    silence_ratio: "Decimal string (fraction of frames below energy threshold)"
  gates:
    clipping: "if clipping_detected == true → status=BLOCKED stop_reason=AUDIO_CLIPPING"
    silence_ratio: "if silence_ratio > Decimal('0.50') → status=BLOCKED stop_reason=EXCESSIVE_SILENCE"
    spectral_centroid: "project-specific bounds — document in CNF capsule"
  evidence:
    spectral_analysis.png: "saved to evidence/; path recorded in manifest"
    spectral_metrics.json: "all metrics as Decimal strings"

# ------------------------------------------------------------
# E) Seed Sweep (rung_274177+ Stability Gate)
# ------------------------------------------------------------
Seed_Sweep:
  purpose: "Prove synthesis is deterministic across multiple seeds"
  when_required: "rung_274177+"
  minimum_seeds: 5
  sweep_rule:
    - "For each seed: synthesize → hash WAV → check STT gate"
    - "All seeds must produce distinct (different seed = likely different hash) but stable (same seed = same hash) outputs"
    - "The KEY invariant is: seed_N on run1 sha256 == seed_N on run2 sha256"
  seed_diversity: "Choose seeds from different ranges — not sequential [1,2,3,4,5]"
  arithmetic:
    - sha256_comparison_is_string_equality: true
    - no_float_in_seed_sweep_logic: true
  evidence:
    seed_sweep_results.json:
      required_keys:
        - seeds_tested: "list[int]"
        - results: "list[{seed, wav_sha256, stt_passed, wer_decimal_string}]"
        - all_stt_passed: "bool"
        - sweep_passed: "bool"
        - rung_target: "int"

# ------------------------------------------------------------
# F) Generator Trace Requirement
# ------------------------------------------------------------
Generator_Trace:
  purpose: "Audit trail proving what inputs produced what audio"
  required_for: "every synthesis operation (all rungs)"
  schema:
    synthesis_trace.json:
      required_keys:
        - seed: "int"
        - input_text_or_params: "str or dict (no PII)"
        - synthesis_engine: "str"
        - engine_version: "str"
        - wav_sha256: "str"
        - synthesis_duration_ms: "int"
        - toolchain_versions: "dict (engine + Python + key deps)"
  fail_closed:
    - if_trace_missing: "GENERATOR_TRACE_MISSING — status=BLOCKED"

# ------------------------------------------------------------
# G) Exact Arithmetic Policy (Hard)
# ------------------------------------------------------------
Exact_Arithmetic_Policy:
  verification_path:
    forbidden: ["float division", "float comparison", "float in hash input"]
    required: ["Fraction for ratios", "Decimal for stored metrics", "int for counters"]
  allowed_exception:
    float_in_DSP: "Float is permitted INSIDE audio processing (DSP math). Forbidden in verification logic."
  enforcement:
    WER: "Fraction(numerator, denominator) stored as Decimal string"
    spectral_metrics: "Stored as Decimal strings"
    timestamps: "Stored as Decimal strings (ms)"
    frame_indices: "int only"

# ------------------------------------------------------------
# H) Evidence Bundle Integration
# ------------------------------------------------------------
Evidence_Bundle:
  purpose: "Every audio claim must produce machine-parseable evidence"
  required_artifacts:
    rung_641:
      - synthesis_trace.json
      - stt_verification.json
      - wav_hash.txt  # sha256 of WAV PCM data
    rung_274177:
      - all_of_rung_641
      - seed_sweep_results.json
      - spectral_analysis.png
      - spectral_metrics.json
    rung_65537:
      - all_of_rung_274177
      - adversarial_audio_report.json  # edge case phonemes, silent inputs, max length
      - community_verification_receipt.json  # if applicable
  manifest_requirements:
    - evidence_manifest.json with sha256 per artifact: true
    - artifact_roles: "[synthesis|verification|spectral|sweep|adversarial]"
  stillwater_compatibility:
    - artifacts_match_stillwater_evidence_schema: true
    - rung_numbers_match_stillwater_ladder: true

# ------------------------------------------------------------
# I) State Machine (Closed FSM — Generic)
# ------------------------------------------------------------
State_Machine:
  states:
    - INIT
    - INTAKE
    - NULL_CHECK
    - SEED_VALIDATE
    - SYNTHESIZE
    - WAV_WRITE
    - STT_VERIFY
    - SPECTRAL_ANALYZE      # rung_274177+ only
    - SEED_SWEEP            # rung_274177+ only
    - ADVERSARIAL_SWEEP     # rung_65537 only
    - EVIDENCE_BUILD
    - SOCRATIC_REVIEW
    - FINAL_SEAL
    - EXIT_PASS
    - EXIT_BLOCKED
    - EXIT_NEED_INFO

  transitions:
    - INIT → INTAKE: on synthesis request
    - INTAKE → NULL_CHECK: always
    - NULL_CHECK → EXIT_NEED_INFO: if seed==null OR primary_input==null
    - NULL_CHECK → SEED_VALIDATE: if all non-null
    - SEED_VALIDATE → EXIT_BLOCKED: if seed not explicit integer
    - SEED_VALIDATE → SYNTHESIZE: if valid
    - SYNTHESIZE → WAV_WRITE: always
    - WAV_WRITE → STT_VERIFY: always (speech audio)
    - STT_VERIFY → EXIT_BLOCKED: if WER > threshold
    - STT_VERIFY → SPECTRAL_ANALYZE: if rung_target >= 274177
    - STT_VERIFY → EVIDENCE_BUILD: if rung_target == 641
    - SPECTRAL_ANALYZE → EXIT_BLOCKED: if clipping or silence gate fails
    - SPECTRAL_ANALYZE → SEED_SWEEP: if rung_target >= 274177
    - SEED_SWEEP → EXIT_BLOCKED: if sweep fails
    - SEED_SWEEP → ADVERSARIAL_SWEEP: if rung_target == 65537
    - SEED_SWEEP → EVIDENCE_BUILD: if rung_target == 274177
    - ADVERSARIAL_SWEEP → EXIT_BLOCKED: if adversarial cases fail
    - ADVERSARIAL_SWEEP → EVIDENCE_BUILD: if all pass
    - EVIDENCE_BUILD → SOCRATIC_REVIEW: always
    - SOCRATIC_REVIEW → SYNTHESIZE: if revision needed AND budget allows
    - SOCRATIC_REVIEW → FINAL_SEAL: if all checks pass
    - FINAL_SEAL → EXIT_PASS: if evidence complete
    - FINAL_SEAL → EXIT_BLOCKED: if evidence incomplete

  forbidden_states:
    - FLOAT_IN_VERIFICATION: float in WER, sha256, or Decimal comparison
    - IMPLICIT_SEED_DEFAULT: synthesizing without explicit seed
    - LOSSY_FORMAT_IN_VERIFY: MP3/OGG/AAC in hash or STT path
    - STT_SKIP: claiming rung_641+ without STT gate
    - NONDETERMINISTIC_OUTPUT: same seed → different sha256
    - GENERATOR_TRACE_MISSING: no synthesis_trace.json
    - NULL_ZERO_CONFUSION: treating null seed as seed=0

# ------------------------------------------------------------
# J) Verification Ladder
# ------------------------------------------------------------
Verification_Ladder:
  RUNG_641:
    meaning: "Basic correctness — audio is intelligible"
    requires:
      - explicit_seed: true
      - wav_sha256_computed: true
      - stt_wer_le_20_percent: true
      - generator_trace: true
    maps_to_stillwater_gates: [G0, G1, G2, G5]

  RUNG_274177:
    meaning: "Stability — reproducible and artifact-free"
    requires:
      - RUNG_641: true
      - seed_sweep_5_seeds: true
      - spectral_clipping_free: true
      - spectral_silence_ratio_ok: true
    maps_to_stillwater_gates: [G3, G4, G6, G8, G9]

  RUNG_65537:
    meaning: "Production quality — adversarial + community verified"
    requires:
      - RUNG_274177: true
      - adversarial_phoneme_sweep: true
      - stt_wer_le_5_percent: true
    maps_to_stillwater_gates: [G7, G10, G11, G12, G13, G14]

# ------------------------------------------------------------
# K) NORTHSTAR Alignment
# ------------------------------------------------------------
NORTHSTAR_Alignment:
  project: "Stillwater — Verification Layer"
  how_this_skill_advances_northstar:
    - "Brings Stillwater verification discipline to audio domain"
    - "Enables audio projects to participate in the Stillwater Store (skill submissions)"
    - "STT round-trip verification is reproducible by any community member"
    - "Evidence bundles make audio quality claims auditable, not subjective"
  ecosystem_uses:
    - "paudio: extends this skill with Field DAG + paudio-worker + voice catalog"
    - "solaceagi avatar: uses paudio which extends this skill"
    - "Any OSS project doing TTS: can load prime-audio directly from Stillwater Store"
  forbidden:
    - NORTHSTAR_UNREAD: "Claiming audio quality without reading NORTHSTAR"
    - NORTHSTAR_MISALIGNED: "Audio work that cannot be verified or replayed"

# ------------------------------------------------------------
# L) Integration Guide (How to Extend This Skill)
# ------------------------------------------------------------
Integration_Guide:
  extending_this_skill:
    principle: "Domain skills extend prime-audio with project-specific architecture. They never weaken the core gates."
    example_extensions:
      - "paudio-synthesis.md — adds Field DAG, Lorentzian formant, voice catalog, community vetting"
      - "your_project/skills/my-audio.md — adds your synthesis architecture, voice params, platform-specific gates"
    required_when_extending:
      - "Declare that you extend prime-audio"
      - "Never remove STT gate, WAV format requirement, seed policy, or exact arithmetic"
      - "May add stricter gates (stricter-wins rule from prime-coder)"
  skill_pack_usage:
    in_stillwater_swarms: "Load as: prime-safety + prime-audio (always in this order)"
    with_paudio: "Load as: prime-safety + prime-audio + paudio-synthesis"
    note: "prime-safety ALWAYS first. prime-audio after prime-safety."

# ------------------------------------------------------------
# M) Anti-Patterns (Dojo Lessons)
# ------------------------------------------------------------
Anti_Patterns:
  "The Confident Silence":
    problem: "STT returns empty transcript for a silent or near-silent WAV. WER = 0 (empty reference = empty transcript). PASS claimed."
    lesson: "Shannon: No information transmitted is maximum uncertainty, not zero error."
    fix: "If reference_text is non-empty and transcript is empty string: BLOCKED. Null transcript ≠ zero WER."
  "The Float WER":
    problem: "wer = (subs + del + ins) / len(reference); if wer < 0.20: pass"
    lesson: "The verification path is law. Use Fraction(subs+del+ins, len(reference)) <= Decimal('0.20')."
    fix: "Fraction arithmetic. Store as Decimal string. Compare using Decimal."
  "The MP3 Hash":
    problem: "Hashing MP3 output instead of WAV PCM data for seed stability check."
    lesson: "MP3 is non-deterministic across encoder versions. Same PCM → different MP3."
    fix: "WAV PCM hash only. Strip WAV header. Hash data bytes. Declare WAV format."
  "The Lazy Sweep":
    problem: "Seed sweep uses seeds [1, 2, 3, 4, 5] — trivially sequential."
    lesson: "A sweep that can't fail is not a gate. Choose diverse seeds."
    fix: "Seeds from different ranges: [42, 1337, 99999, 7777777, first_prime_above_billion]."
