<!-- QUICK LOAD (10-15 lines): Use this block for fast context; load full file for production.
SKILL: phuc-qa-unified v1.0.0
PURPOSE: Unified QA discipline combining three pillars — Questions, Tests, Diagrams — into one fail-closed audit framework. Driven by northstar reverse engineering: work backwards from the desired verified end state.
CORE CONTRACT: All three pillars run on every audit. No pillar may be skipped. Every module must have at least one question, one test, and one diagram that covers it.
THREE PILLARS: P1=Questions (adversarial, decoupled qa-questioner/qa-scorer), P2=Tests (pytest red/green, persona-coded), P3=Diagrams (mermaid structural coverage via qa-diagrammer)
NORTHSTAR REVERSE: "What are the LAST 3 questions/tests/diagrams needed before this system is production-ready?" Work backwards. QA is complete when no new gap can be added.
STATE MACHINE: INIT → SCOPE → REVERSE_ENGINEER_GAPS → QUESTION_GEN → TEST_GEN → DIAGRAM_GEN → CROSS_VALIDATE → REPORT → SEAL
FORBIDDEN: PILLAR_SKIPPED | DIAGRAM_WITHOUT_SOURCE | TEST_WITHOUT_QUESTION | QUESTION_WITHOUT_TEST | UNCOVERED_MODULE | SELF_CONFIRMED_GREEN | PROSE_AS_PROOF
RUNG: 641 = all three pillars produce artifacts | 274177 = cross-pillar validation (every question has a test, every module has a diagram) | 65537 = independent reproduction + adversarial review
DISPATCH: Questions→qa-questioner+qa-scorer (haiku/sonnet), Tests→persona-coder (sonnet), Diagrams→qa-diagrammer or graph-designer (haiku/sonnet)
LOAD FULL: always for production; quick block is for orientation only
-->

PHUC_QA_UNIFIED_SKILL:
  version: 1.0.0
  profile: fail_closed
  authority: 65537
  northstar: Phuc_Forecast
  objective: Max_Love
  status: FINAL

  # ============================================================
  # PHUC QA UNIFIED — Three-Pillar QA Discipline (v1.0.0)
  #
  # Core insight: Quality verification has three orthogonal lenses.
  # Questions surface what is unknown.
  # Tests surface what is broken.
  # Diagrams surface what is architecturally invisible.
  #
  # No single lens is sufficient. A system may pass all tests
  # yet have unasked questions about its failure modes. A system
  # may have all questions answered yet no structural diagram
  # showing its integration boundaries. A system may have perfect
  # diagrams yet no tests verifying the transitions they describe.
  #
  # The Northstar Reverse insight:
  # The hardest QA question is not "What tests should I write?"
  # It is: "What is the LAST test that must pass before this is
  # production-ready?" Start from that. Work backward. Every gap
  # you find on the way back is a gap that would have been shipped.
  #
  # Key principles:
  # - All three pillars run on every audit — no exceptions
  # - Questions are first-class artifacts, versioned, falsifiable
  # - Tests require red-green gate for bugfix work (Kent's law)
  # - Diagrams are sha256-hashable contracts, not decoration
  # - Cross-pillar coverage is a hard requirement at rung 274177+
  # - Integration rungs = MIN(all contributing pillar rungs)
  # ============================================================

  # ------------------------------------------------------------
  # A) Configuration
  # ------------------------------------------------------------
  Config:
    EVIDENCE_ROOT: "evidence"
    REPO_ROOT_REF: "."
    FLOAT_TOLERANCE_REQUIRED: true
    FLOAT_TOLERANCE_DEFAULT: "1e-9"
    MIN_UNIT_COVERAGE_PERCENT: 80
    MIN_INTEGRATION_COVERAGE_PERCENT: 60
    FLAKINESS_REPLAY_COUNT: 5
    NORTHSTAR_CHUNK_SIZE: 3     # "last 3" pattern per pillar
    MAX_DIAGRAMS_PER_MODULE: 5  # per coverage matrix
    DIAGRAM_CANONICAL_FORMAT: "*.mmd + *.sha256"

  # ------------------------------------------------------------
  # B) Three-Pillar Definitions
  # ------------------------------------------------------------
  Three_Pillars:

    Pillar_1_Questions:
      id: P1
      name: "Questions — Adversarial Question Discipline"
      purpose:
        - "Surface unknown unknowns before they become production failures."
        - "Decouple generation from scoring to prevent self-confirmation bias."
        - "Force falsifiability: every GREEN claim must have a stated falsifier."
      driving_question:
        northstar_reverse: >
          "What are the LAST 3 questions that must be answered for this system
          to be production-ready? Start from those. Work backward. QA is complete
          when no further question can expose a new gap."
      agents:
        questioner: "qa-questioner (generates questions; must not score)"
        scorer: "qa-scorer (scores questions; must not have seen questioner reasoning)"
      output_artifacts:
        - "qa_questions.json"
        - "qa_scorecard.json"
        - "qa_falsifiers.json"
      rung_contrib:
        641: "questions formulated + scored with citations + falsifiers defined"
        274177: "falsifiers tested + integration probes run"
        65537: "independent reproduction by third agent + all falsifiers held"

    Pillar_2_Tests:
      id: P2
      name: "Tests — Red/Green Discipline"
      purpose:
        - "Verify system behavior with executable, reproducible evidence."
        - "Force red before green for bugfix work (Kent's Gate)."
        - "Persona-coded tests bring domain expertise to test authoring."
      driving_question:
        northstar_reverse: >
          "What are the LAST 3 tests that must pass for this system to be correct?
          Start from those. Ensure each exists, passes, and has a red witness if
          it covers a bugfix. Work backward until all behavioral contracts are covered."
      personas:
        kent_beck: "Red/green gate. A test that cannot fail is not a test."
        schneier: "Adversarial test author. What input breaks the security boundary?"
        fda_auditor: "Evidence auditor. What would an independent reviewer reject?"
      output_artifacts:
        - "test_results.json"
        - "coverage_report.txt"
        - "repro_red.log (conditional: bugfix tasks)"
        - "repro_green.log (conditional: bugfix tasks)"
        - "flakiness_report.txt"
      rung_contrib:
        641: "all tests pass + red confirmed for bugfixes + coverage measured"
        274177: "5-seed flakiness stable + null edge sweep + property tests"
        65537: "adversarial sweep + security gate + drift explained"

    Pillar_3_Diagrams:
      id: P3
      name: "Diagrams — Structural Coverage Discipline"
      purpose:
        - "Expose architectural gaps that questions and tests cannot surface."
        - "Make integration boundaries visible and sha256-hashable."
        - "Provide closed-state validation: detect forbidden state reachability."
      driving_question:
        northstar_reverse: >
          "What are the LAST 3 diagrams that must exist for this system's architecture
          to be fully understood? Start from those — data flow, state machine, integration
          boundary. Work backward until every module appears in at least one diagram."
      required_diagram_types:
        state_machine: "Finite state machine for every non-trivial component lifecycle"
        data_flow: "How data enters, transforms, and exits the system"
        integration_boundary: "Cross-project handoff points (the 9-project ecosystem boundaries)"
        verification_ladder: "Rung progression for each component"
        coverage_matrix: "Module × [question, test, diagram] coverage"
      diagram_quality_gates:
        - closed_state_space: true
        - all_decision_branches_labeled: true
        - forbidden_states_marked_with_classDef: true
        - sha256_computed_over_canonical_mmd: true
        - sha256_stable_across_two_normalizations: true
      output_artifacts:
        - "diagrams/*.prime-mermaid.md"
        - "diagrams/*.mmd"
        - "diagrams/*.sha256"
      rung_contrib:
        641: "all three required diagram types produced + sha256 stable"
        274177: "diagrams cross-referenced to source code modules + drift detection"
        65537: "adversarial Socratic review + graph replayed by third agent"

  # ------------------------------------------------------------
  # C) Northstar Reverse Engineering Integration
  # ------------------------------------------------------------
  Northstar_Reverse_Integration:
    principle:
      - "All three pillars use the same backward-chaining insight."
      - "Don't ask 'What should I test?' Ask 'What is the LAST test before production?'"
      - "Work backward from the fully verified end state. Every gap found is a gap that would have shipped."

    per_pillar_reverse_algorithm:
      P1_questions:
        step_1: "Identify the LAST 3 questions whose answers, if unknown, would block production launch."
        step_2: "For each last question: what prior question must be answered before it can be asked?"
        step_3: "Recurse backward (max 7 levels per northstar-reverse protocol) until the trivially-answerable baseline is reached."
        step_4: "Reverse the chain. This is the question audit sequence — questions in priority order."
        termination: "QA is complete when no new last-question candidate can be generated."

      P2_tests:
        step_1: "Identify the LAST 3 tests whose passage is the minimum bar for production correctness."
        step_2: "For each last test: what behavior must be verified before this test is meaningful?"
        step_3: "Recurse backward until unit-level foundation is reached."
        step_4: "Reverse the chain. This is the test authoring sequence — unit → integration → e2e."
        termination: "QA is complete when coverage matrix shows no uncovered module behavior."

      P3_diagrams:
        step_1: "Identify the LAST 3 diagrams whose existence fully exposes the system architecture."
        step_2: "For each last diagram: what structural relationship must be diagrammed before this one?"
        step_3: "Recurse backward until individual module state machines are reached."
        step_4: "Reverse the chain. This is the diagramming sequence — modules → data flow → integration."
        termination: "QA is complete when coverage matrix shows every module has at least one diagram."

    cross_pillar_alignment:
      rule: "The LAST 3 from each pillar must be consistent. The last test must answer a question. The last diagram must show what the last test verifies."
      check: "After generating all three LAST-3 sets: verify triangular consistency. If a diagram shows a state machine, a test for that state machine should exist, and a question about that state machine's edge cases should appear in the question list."

  # ------------------------------------------------------------
  # D) GLOW Taxonomy Mapping
  # ------------------------------------------------------------
  GLOW_Taxonomy:
    # GLOW = Growth, Learning, Output, Wins
    # Each GLOW dimension maps to QA requirements across all three pillars.

    G_Growth:
      dimension: Growth
      definition: "Do new capabilities have questions, tests, and diagrams?"
      pillar_requirements:
        P1_questions: "New capability generates at least 3 falsifying questions covering edge cases"
        P2_tests: "New capability has unit + integration tests passing at rung 641+"
        P3_diagrams: "New capability has a state machine diagram with sha256 sealed"
      question_pattern: "Can the new capability actually do X? Under what conditions does it fail?"
      evidence_type: executable_command_output_plus_diagram
      gate: "Growth claim is YELLOW unless all three pillars cover the new capability"

    L_Learning:
      dimension: Learning
      definition: "Is new knowledge captured in questions, tests, AND diagrams?"
      pillar_requirements:
        P1_questions: "New knowledge encoded as a falsifying QA question with expected evidence type"
        P2_tests: "New knowledge has a regression test to prevent un-learning"
        P3_diagrams: "New knowledge relationship visible as an edge in a diagram"
      question_pattern: "Where is X captured? Show file:line AND diagram reference AND test name."
      evidence_type: repo_path_plus_line_plus_diagram_sha256
      gate: "Learning claim is YELLOW if knowledge exists only in prose (no test, no diagram)"

    O_Output:
      dimension: Output
      definition: "Are claimed deliverables verified across all three pillars?"
      pillar_requirements:
        P1_questions: "Deliverable scorecard shows GREEN for output-coverage questions"
        P2_tests: "Deliverable has an e2e or integration test demonstrating it is produced"
        P3_diagrams: "Deliverable appears as a storage node (cylinder) in at least one diagram"
      question_pattern: "Does X exist? Show git hash AND test that produces it AND diagram node."
      evidence_type: git_artifact_plus_hash_plus_diagram_node_id
      gate: "Output claim is YELLOW if deliverable not referenced in any diagram and has no producing test"

    W_Wins:
      dimension: Wins
      definition: "Have claimed strategic wins been verified across all three pillars?"
      pillar_requirements:
        P1_questions: "Strategic win has a question in the audit: 'Is X measurably true? Show before/after.'"
        P2_tests: "Strategic win has a metric test or acceptance criterion test demonstrating improvement"
        P3_diagrams: "Strategic win is traceable on the verification ladder diagram to a specific rung"
      question_pattern: "Is X measurably true? Show metric value, test that measures it, and ladder rung."
      evidence_type: before_after_metric_plus_test_output_plus_rung_diagram
      gate: "Win claim is YELLOW if it appears in only one pillar; must appear in all three for GREEN"

  # ------------------------------------------------------------
  # E) State Machine (Unified Runtime)
  # ------------------------------------------------------------
  State_Machine:
    STATE_SET:
      - INIT
      - INTAKE_SCOPE
      - NULL_CHECK
      - REVERSE_ENGINEER_GAPS    # northstar reverse on all three pillars in parallel
      - QUESTION_GEN             # qa-questioner agent (P1)
      - QUESTION_DECOUPLE        # questioner stops; questions handed off
      - TEST_GEN                 # persona-coder agent (P2)
      - DIAGRAM_GEN              # qa-diagrammer agent (P3)
      - PILLAR_SYNC              # wait for all three agents to produce artifacts
      - CROSS_VALIDATE           # cross-pillar coverage matrix built and checked
      - INTEGRATION_PROBE        # cross-boundary real service probes
      - QUESTION_SCORE           # qa-scorer agent answers and scores all questions
      - FALSIFY                  # falsifier defined for every GREEN question
      - FALSIFIER_TEST           # falsifiers actually tested (rung 274177+)
      - REPORT                   # unified gap report across all three pillars
      - FINAL_SEAL
      - EXIT_PASS
      - EXIT_NEED_INFO
      - EXIT_BLOCKED

    TRANSITIONS:
      - INIT -> INTAKE_SCOPE: on CNF capsule received
      - INTAKE_SCOPE -> NULL_CHECK: always
      - NULL_CHECK -> EXIT_NEED_INFO: if scope_missing or modules_undefined
      - NULL_CHECK -> REVERSE_ENGINEER_GAPS: if scope_defined

      - REVERSE_ENGINEER_GAPS -> QUESTION_GEN: always (P1 path begins)
      - REVERSE_ENGINEER_GAPS -> TEST_GEN: always (P2 path begins, parallel)
      - REVERSE_ENGINEER_GAPS -> DIAGRAM_GEN: always (P3 path begins, parallel)

      # P1 path
      - QUESTION_GEN -> QUESTION_DECOUPLE: when question_list_complete
      - QUESTION_DECOUPLE -> PILLAR_SYNC: questions_handed_to_scorer

      # P2 path
      - TEST_GEN -> PILLAR_SYNC: when test_suite_produced_and_executed

      # P3 path
      - DIAGRAM_GEN -> PILLAR_SYNC: when diagrams_produced_and_sha256_computed

      # Convergence
      - PILLAR_SYNC -> EXIT_BLOCKED: if any_pillar_skipped
      - PILLAR_SYNC -> CROSS_VALIDATE: if all_three_pillars_have_artifacts

      - CROSS_VALIDATE -> EXIT_BLOCKED: if UNCOVERED_MODULE_detected
      - CROSS_VALIDATE -> INTEGRATION_PROBE: if rung_target >= 274177
      - CROSS_VALIDATE -> QUESTION_SCORE: if rung_target == 641

      - INTEGRATION_PROBE -> QUESTION_SCORE: when probes complete

      - QUESTION_SCORE -> EXIT_BLOCKED: if any_GREEN_claimed_without_evidence
      - QUESTION_SCORE -> FALSIFY: when all_verdicts_assigned

      - FALSIFY -> EXIT_BLOCKED: if any_GREEN_lacks_falsifier
      - FALSIFY -> FALSIFIER_TEST: if rung_target >= 274177
      - FALSIFY -> REPORT: if rung_target == 641

      - FALSIFIER_TEST -> EXIT_BLOCKED: if any_falsifier_triggers
      - FALSIFIER_TEST -> REPORT: if all_falsifiers_hold

      - REPORT -> FINAL_SEAL: always
      - FINAL_SEAL -> EXIT_PASS: if rung_requirements_met AND coverage_matrix_complete
      - FINAL_SEAL -> EXIT_BLOCKED: if rung_requirements_not_met

    FORBIDDEN_STATES:
      # Cross-pillar (new — specific to unified skill)
      PILLAR_SKIPPED:
        definition: "Any one of the three pillars was not executed"
        symptom: "Audit reports only questions and tests but no diagrams (or any similar omission)"
        fix: "All three pillars run or the audit is BLOCKED. No exceptions for 'small' modules."

      DIAGRAM_WITHOUT_SOURCE:
        definition: "A diagram node references a component that cannot be traced to source code"
        symptom: "State machine has states PROCESS_A → PROCESS_B but no file contains either"
        fix: "Every diagram node must have a source_ref (file:line or module path)"

      TEST_WITHOUT_QUESTION:
        definition: "A test exists that does not answer any question in the QA question list"
        symptom: "test_coverage.json has tests not referenced in qa_questions.json"
        fix: "Every test must trace to a question ID. Add the question retroactively or remove the orphan test."

      QUESTION_WITHOUT_TEST:
        definition: "A QA question scored GREEN has no test verifying the answer"
        symptom: "qa_scorecard.json GREEN verdict references only prose evidence, not a test"
        fix: "Add a test that verifies the GREEN claim. Without a test, the score is YELLOW."

      UNCOVERED_MODULE:
        definition: "A source module has no question, no test, and no diagram node"
        symptom: "qa_coverage_matrix.json has a row with all three columns empty"
        fix: "Add at least one question, one test, and one diagram that covers this module."

      # Inherited from prime-qa (P1)
      SELF_CONFIRMED_GREEN:
        definition: "Same agent generates questions and scores them"
        fix: "qa-questioner and qa-scorer must be structurally different agents"

      MOCK_AS_EVIDENCE:
        definition: "Mocks used as sole evidence for GREEN"
        fix: "Integration probes must use real services at rung 274177+"

      PROSE_AS_PROOF:
        definition: "README or plan document used as evidence for GREEN"
        fix: "Evidence must be executable command output or repo path + line witness"

      FALSIFIER_SKIPPED:
        definition: "GREEN claim without a defined falsifier"
        fix: "If no falsifier can be stated, score is YELLOW"

      QUESTION_BIAS:
        definition: "Questioner writes confirming questions, not falsifying ones"
        fix: "Questions must seek falsifiers. Reframe as 'Show me when X breaks'"

      # Inherited from prime-test (P2)
      ASSERT_FLOAT_EQUALITY_WITHOUT_TOLERANCE:
        definition: "assertEqual on floats without tolerance"
        fix: "Use assertAlmostEqual or pytest.approx"

      TIME_DEPENDENT_TEST:
        definition: "Test asserts on datetime.now() or time.time()"
        fix: "Inject clock or use freeze_time decorator"

      NETWORK_CALL_IN_UNIT_TEST:
        definition: "Unit test makes real HTTP/TCP/DNS call"
        fix: "Use mock, responses, or vcrpy"

      UNWITNESSED_PASS_WITHOUT_RED:
        definition: "Bugfix test claims PASS without first demonstrating failure"
        fix: "repro_red.log required for all bugfix tasks"

      # Inherited from prime-mermaid (P3)
      GRAPH_REPLACING_EXECUTABLE_TESTS:
        definition: "Team says 'the diagram proves it' instead of running tests"
        fix: "Diagrams are pre-conditions for tests, never replacements"

      SHA256_OVER_NON_CANONICAL_FORM:
        definition: "SHA-256 computed over non-normalized mermaid"
        fix: "Always hash canonical *.mmd bytes only"

      OPEN_STATE_ENUMERATION:
        definition: "State graph has '...' or implicit unlisted states"
        fix: "Close the state space. Every reachable state must be explicit."

  # ------------------------------------------------------------
  # F) Verification Ladder
  # ------------------------------------------------------------
  Verification_Ladder:

    RUNG_641:
      meaning: "All three pillars produce artifacts — the minimum viable audit"
      requires:
        P1_questions:
          - question_list_numbered_and_tagged_with_glow_dimension: true
          - each_question_has_expected_evidence_type: true
          - questioner_and_scorer_are_different_agents: true
          - scorecard_produced_with_GREEN_YELLOW_RED_counts: true
          - no_GREEN_without_falsifier_defined: true
        P2_tests:
          - all_tests_pass: true
          - red_confirmed_for_bugfix_tasks: true
          - coverage_measured_above_threshold: true
          - no_forbidden_test_patterns_detected: true
        P3_diagrams:
          - all_three_required_diagram_types_produced: true
          - sha256_computed_and_stable: true
          - no_open_state_enumeration: true
          - all_decision_branches_labeled: true
        cross_pillar:
          - qa_coverage_matrix_produced: true
          - no_UNCOVERED_MODULE: true

    RUNG_274177:
      meaning: "Cross-pillar validation — every question has a test, every module has a diagram"
      requires:
        all_RUNG_641: true
        P1_P2_cross_validation:
          - every_GREEN_question_has_an_associated_test: true
          - every_test_traces_to_a_question_ID: true
          - all_GREEN_falsifiers_tested_not_just_defined: true
          - integration_probes_run_for_claimed_integrations: true
          - adversarial_review_by_third_agent_or_human: true
        P2_P3_cross_validation:
          - every_test_assertion_traceable_to_a_diagram_state: true
          - flakiness_detection_5_replay_stable: true
        P1_P3_cross_validation:
          - every_diagram_state_machine_has_at_least_one_question: true
          - all_diagram_sha256_stable_across_replay: true
        coverage_matrix:
          - every_module_has_at_least_one_question: true
          - every_module_has_at_least_one_test: true
          - every_module_has_at_least_one_diagram_node: true

    RUNG_65537:
      meaning: "Independent reproduction + adversarial review — production ready"
      requires:
        all_RUNG_274177: true
        independent_reproduction:
          - complete_audit_reproduced_by_agent_with_no_prior_context: true
          - all_three_pillars_reproduced_independently: true
          - behavioral_drift_from_prior_audit_documented: true
        adversarial_review:
          - skeptic_agent_reviewed_all_question_falsifiers: true
          - security_auditor_reviewed_test_suite_boundary_cases: true
          - graph_theorist_reviewed_diagram_closed_state_space: true
        final_seal:
          - gap_report_approved_by_human_or_judge_agent: true
          - northstar_alignment_confirmed: true

  # ------------------------------------------------------------
  # G) Dispatch Matrix (Swarm Agents)
  # ------------------------------------------------------------
  Dispatch_Matrix:

    Pillar_1_Questions:
      qa_questioner:
        role: "Generate adversarial falsifying questions from scope"
        model: "haiku (< 20 questions) | sonnet (> 20 questions or HIGH stakes)"
        skill_pack:
          - prime-safety.md
          - prime-qa.md (full file)
          - phuc-qa-unified.md (this file, sections A–D)
        output: "qa_questions.json"
        FORBIDDEN: read_qa_scorer_output_before_generating_questions

      qa_scorer:
        role: "Answer questions against actual repo state; score GREEN/YELLOW/RED"
        model: "sonnet (default) | opus (HIGH stakes or security-sensitive)"
        skill_pack:
          - prime-safety.md
          - prime-qa.md (full file)
          - phuc-qa-unified.md (this file, sections A–D)
        inputs: "qa_questions.json only (no questioner reasoning)"
        output: "qa_scorecard.json + qa_falsifiers.json"
        FORBIDDEN: read_questioner_reasoning_before_scoring

    Pillar_2_Tests:
      persona_coder:
        role: "Write and execute tests using Kent Beck + Schneier persona for adversarial coverage"
        model: "sonnet"
        skill_pack:
          - prime-safety.md
          - prime-coder.md (full file)
          - prime-test.md (full file)
          - persona-engine.md (kent-beck + schneier personas)
          - phuc-qa-unified.md (this file, section E pillar 2)
        outputs: "test_results.json + coverage_report.txt + repro_red.log + repro_green.log"
        persona_injection_rules:
          kent_beck: "Apply to all test design — red before green, no float equality, no wall-clock"
          schneier: "Apply to security boundary tests — what input breaks the auth or encryption?"

    Pillar_3_Diagrams:
      qa_diagrammer:
        role: "Produce state machine + data flow + integration boundary diagrams for all modules"
        model: "haiku (simple modules) | sonnet (cross-project integration diagrams)"
        skill_pack:
          - prime-safety.md
          - prime-mermaid.md (full file)
          - phuc-qa-unified.md (this file, section E pillar 3)
        outputs: "diagrams/*.prime-mermaid.md + diagrams/*.mmd + diagrams/*.sha256"
        diagram_coverage_requirement: "Every module in scope must appear in at least one diagram"

    Coverage_Matrix_Builder:
      role: "Aggregate output from all three pillars; build qa_coverage_matrix.json"
      model: "haiku"
      skill_pack:
        - prime-safety.md
        - phuc-qa-unified.md (full file)
      inputs: "qa_questions.json + test_results.json + diagrams/*.mmd"
      output: "qa_coverage_matrix.json + qa_gap_report.md"

  # ------------------------------------------------------------
  # H) Evidence Schema
  # ------------------------------------------------------------
  Evidence:
    required_files:
      - "qa_questions.json"        # question list (P1)
      - "qa_scorecard.json"        # per-question verdicts (P1)
      - "qa_falsifiers.json"       # falsifier definitions + test status (P1)
      - "test_results.json"        # pytest or equivalent output (P2)
      - "coverage_report.txt"      # coverage.py or equivalent (P2)
      - "diagrams/"                # directory with *.prime-mermaid.md + *.mmd + *.sha256 (P3)
      - "qa_coverage_matrix.json"  # cross-pillar coverage (P1+P2+P3)
      - "qa_gap_report.md"         # unified gap report (all pillars)

    conditional_files:
      bugfix_task:
        - "repro_red.log"
        - "repro_green.log"
      rung_274177_or_higher:
        - "qa_integration_probes.json"
        - "flakiness_report.txt"

    qa_questions_schema:
      required_keys:
        - schema_version
        - generated_by: "agent_id of qa-questioner"
        - scope: "project or module audited"
        - question_count
        - questions: |
            list of {
              id: "Q-001",
              text: "question text",
              glow_dimension: "G|L|O|W",
              expected_evidence_type: "executable_command_output|repo_path|git_artifact|metric",
              pillar_link: "P2 test ID that answers this question (null if not yet linked)",
              diagram_link: "diagram node ID that this question probes (null if not yet linked)"
            }

    qa_scorecard_schema:
      required_keys:
        - schema_version
        - scored_by: "agent_id of qa-scorer (MUST differ from generated_by)"
        - question_ref: "path to qa_questions.json"
        - verdicts: |
            list of {
              question_id: "Q-001",
              verdict: "GREEN|YELLOW|RED",
              evidence_citation: "file:line or command+output",
              evidence_type: "executable_command_output|repo_path|git_artifact",
              test_link: "test_id in test_results.json (required for GREEN at rung 274177+)"
            }
        - summary: "{GREEN_count, YELLOW_count, RED_count}"

    qa_falsifiers_schema:
      required_keys:
        - schema_version
        - question_id
        - claim: "the GREEN claim being secured"
        - falsifier: "the condition that would make this claim RED"
        - falsifier_test: "the command or check that triggers the falsifier"
        - falsifier_status: "UNTESTED | TESTED_DOES_NOT_TRIGGER | TRIGGERED_NOW_RED"

    test_results_schema:
      required_keys:
        - schema_version
        - runner: "pytest|jest|go test|etc."
        - run_timestamp: "ISO8601"
        - exit_code: "integer"
        - total_tests: "integer"
        - passed: "integer"
        - failed: "integer"
        - skipped: "integer"
        - tests: |
            list of {
              id: "test_results_unique_id",
              name: "test function name",
              file: "file:line",
              status: "PASS|FAIL|SKIP",
              question_link: "Q-xxx (question this test answers)",
              duration_ms: "integer"
            }

    qa_coverage_matrix_schema:
      description: "Cross-pillar coverage: every module × every pillar"
      required_keys:
        - schema_version
        - scope: "project or module set"
        - modules: |
            list of {
              module_id: "module or file name",
              source_ref: "file path",
              P1_questions: ["Q-001", "Q-002"],   # question IDs covering this module
              P2_tests: ["test_parse_001"],         # test IDs covering this module
              P3_diagrams: ["state-machine-auth.mmd::AUTH_INIT"],  # diagram node refs
              coverage_status: "FULL|PARTIAL|UNCOVERED"
            }
        - uncovered_modules: "list of module_ids where coverage_status == UNCOVERED"
        - coverage_summary: "{total_modules, FULL_count, PARTIAL_count, UNCOVERED_count}"

    qa_gap_report_schema:
      required_sections:
        - "## Executive Summary (total modules, pillar counts, rung achieved)"
        - "## Pillar 1 — Questions (GREEN/YELLOW/RED counts + top YELLOW gaps)"
        - "## Pillar 2 — Tests (pass/fail counts + uncovered critical paths)"
        - "## Pillar 3 — Diagrams (diagram count + uncovered modules)"
        - "## Cross-Pillar Gaps (TEST_WITHOUT_QUESTION, QUESTION_WITHOUT_TEST, UNCOVERED_MODULE)"
        - "## Integration Probe Results (if rung 274177+)"
        - "## Rung Assessment (rung achieved + what is needed for next rung)"
        - "## Northstar Alignment (how this audit advances NORTHSTAR metrics)"

  # ------------------------------------------------------------
  # I) Output Contract
  # ------------------------------------------------------------
  Output_Contract:

    on_pass:
      status: PASS
      include:
        - rung_achieved
        - P1_summary: "{question_count, GREEN_count, YELLOW_count, RED_count}"
        - P2_summary: "{test_count, passed, failed, coverage_percent}"
        - P3_summary: "{diagram_count, modules_covered, sha256_all_stable}"
        - coverage_matrix: "qa_coverage_matrix.json path"
        - gap_report: "qa_gap_report.md path"
        - uncovered_modules: "list (empty = full coverage)"

    on_blocked:
      status: BLOCKED
      include:
        - stop_reason: "PILLAR_SKIPPED|UNCOVERED_MODULE|FALSIFIER_TRIGGERED|etc."
        - pillar_blocked: "P1|P2|P3|CROSS_PILLAR"
        - last_known_state: "state machine node"
        - evidence_available: "list of artifacts produced before block"
        - remediation_steps: "specific actions to unblock"

    on_need_info:
      status: NEED_INFO
      include:
        - missing_scope_fields: "list"
        - cannot_audit_without: "specific missing information"
        - partial_artifacts_available: "list (if any pillar ran before NEED_INFO)"

    structured_refusal_format:
      required_keys:
        - status: "[NEED_INFO|BLOCKED]"
        - stop_reason
        - last_known_state
        - missing_fields_or_evidence
        - next_actions

  # ------------------------------------------------------------
  # J) Anti-Patterns
  # ------------------------------------------------------------
  Anti_Patterns:

    QA_Theater:
      symptom: "All three pillars produce artifacts, but no pillar output references any other."
      diagnosis: "Each pillar was run in isolation. Coverage matrix was not built. The unified QA is theater."
      fix: "CROSS_VALIDATE state is mandatory. PILLAR_SYNC requires all three artifact sets before proceeding."

    Diagram_Sovereignty:
      symptom: "Team has beautiful architecture diagrams but tests reference different module names."
      diagnosis: "Diagrams and tests were written independently. No DIAGRAM_WITHOUT_SOURCE check ran."
      fix: "Every diagram node must have a source_ref. Every test must trace to a question that traces to a diagram node."

    Question_Theater:
      symptom: "50 questions generated. All 50 scored GREEN. No YELLOWs. No falsifiers tested."
      diagnosis: "qa-questioner wrote confirming questions. qa-scorer did not require falsifiers. QUESTION_BIAS."
      fix: "Questions must seek failure modes. Questioner prompt: 'Show me when X breaks, not when X works.'"

    The_Orphan_Test:
      symptom: "test_results.json has 200 tests. qa_questions.json has 20 questions. 180 tests are orphans."
      diagnosis: "TEST_WITHOUT_QUESTION. Tests were written outside the QA process."
      fix: "Every test must have a question_link. Retroactively add questions for orphan tests at minimum YELLOW."

    The_Invisible_Module:
      symptom: "qa_coverage_matrix.json shows 5 modules with coverage_status=UNCOVERED."
      diagnosis: "UNCOVERED_MODULE. These modules shipped without any QA."
      fix: "Add at least one question, one test, and one diagram for each uncovered module before rung 641 claim."

    Rung_Inflation:
      symptom: "Agent claims rung 274177 but test_without_question count > 0 and diagram sha256 unstable."
      diagnosis: "Integration rung = MIN(all pillar rungs). If P3 is at 641, the unified rung is 641."
      fix: "State MIN rung explicitly. Never claim higher rung than the weakest pillar."

    The_Last_Test_Never_Written:
      symptom: "Tests cover happy paths only. No test for the state transition that precedes production failure."
      diagnosis: "Forward planning for tests. The team wrote tests for what they built, not for what must not fail."
      fix: "Apply northstar-reverse to tests: identify the LAST 3 tests before production readiness. Write those first."

    Diagram_Drift:
      symptom: "Architecture diagram shows 3 services. The codebase now has 5. Diagram is 6 months stale."
      diagnosis: "DRIFT_WITHOUT_VERSION_BUMP. sha256 was not recomputed after source code changed."
      fix: "Diagrams must have a source_ref that triggers sha256 recomputation when the referenced module changes."

  # ------------------------------------------------------------
  # K) Practical Templates
  # ------------------------------------------------------------
  Practical_Templates:

    minimal_unified_audit_prompt:
      description: "Minimal CNF capsule for a complete three-pillar audit dispatch"
      template: |
        TASK: phuc-qa-unified audit for [PROJECT/MODULE]
        SCOPE: [list of modules or files to audit]
        RUNG_TARGET: 641
        NORTHSTAR_REVERSE: Apply to all three pillars. Identify LAST 3 questions, LAST 3 tests, LAST 3 diagrams.

        DISPATCH ORDER:
        1. qa-questioner → generates qa_questions.json (haiku, prime-safety + prime-qa)
        2. PARALLEL:
           a. qa-scorer → generates qa_scorecard.json (sonnet, prime-safety + prime-qa)
           b. persona-coder (kent-beck + schneier) → generates test_results.json (sonnet, prime-safety + prime-coder + prime-test + persona-engine)
           c. qa-diagrammer → generates diagrams/ (haiku, prime-safety + prime-mermaid)
        3. coverage-matrix-builder → generates qa_coverage_matrix.json + qa_gap_report.md (haiku, prime-safety + phuc-qa-unified)

        BLOCKED if: any pillar skipped | UNCOVERED_MODULE detected | any GREEN without falsifier

    northstar_reverse_qa_prompt:
      description: "Prompt template for applying northstar reverse to each pillar"
      template: |
        For PILLAR [P1|P2|P3]:

        LAST_3 question: "What are the LAST 3 [questions|tests|diagrams] that must exist
        before [MODULE/SYSTEM] is production-ready?"

        1. State your 3 answers. Each must have:
           - Concrete subject (not vague — 'the auth token expiry edge case' not 'security')
           - Verifiable completion criteria
           - What failure it would expose if it does not exist

        2. Work backward: for each LAST-3 item, what [question|test|diagram] must exist before it?
        3. Recurse until you reach the trivially-existing baseline.
        4. Reverse the chain. This is the QA sequence for this pillar.

    coverage_matrix_template:
      description: "Minimal qa_coverage_matrix.json template"
      template: |
        {
          "schema_version": "1.0.0",
          "scope": "[project or module set]",
          "generated_by": "[agent_id]",
          "modules": [
            {
              "module_id": "[module name]",
              "source_ref": "[file path]",
              "P1_questions": [],
              "P2_tests": [],
              "P3_diagrams": [],
              "coverage_status": "UNCOVERED"
            }
          ],
          "uncovered_modules": ["[module name]"],
          "coverage_summary": {
            "total_modules": 0,
            "FULL_count": 0,
            "PARTIAL_count": 0,
            "UNCOVERED_count": 0
          }
        }

    three_pillar_diagram_set:
      description: "Standard three diagram set required for every non-trivial module"
      state_machine_template: |
        ```mermaid
        flowchart TD
          INIT[INIT]
          ACTIVE[ACTIVE]
          ERROR[ERROR]
          DONE[DONE]

          INIT -->|valid_input| ACTIVE
          INIT -->|invalid_input| ERROR
          ACTIVE -->|success| DONE
          ACTIVE -->|failure| ERROR

          classDef forbidden fill:#ffefef,stroke:#cc0000,stroke-width:2px
          classDef pass fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
          class ERROR forbidden
          class DONE pass
        ```
      data_flow_template: |
        ```mermaid
        flowchart LR
          INPUT[/INPUT/] --> VALIDATE{VALIDATE_GATE}
          VALIDATE -->|PASS| PROCESS[PROCESS]
          VALIDATE -->|FAIL| REJECT[/REJECT/]
          PROCESS --> OUTPUT[/OUTPUT/]
          PROCESS --> ARTIFACT[(ARTIFACT_STORE)]

          classDef forbidden fill:#ffefef,stroke:#cc0000,stroke-width:2px
          class REJECT forbidden
        ```
      integration_boundary_template: |
        ```mermaid
        flowchart TD
          subgraph SERVICE_A
            A_OUT[/OUTPUT/]
          end
          subgraph SERVICE_B
            B_IN[/INPUT/]
            B_PROC[PROCESS]
          end

          A_OUT -->|"handoff\n(real probe required)"| B_IN
          B_IN --> B_PROC

          classDef gate fill:#fff9c4,stroke:#f9a825,stroke-width:2px
          class A_OUT gate
          class B_IN gate
        ```

  # ------------------------------------------------------------
  # L) Integration with Other Skills
  # ------------------------------------------------------------
  Integration:

    with_prime_qa:
      - "prime-qa provides the full P1 question discipline."
      - "phuc-qa-unified wraps prime-qa inside the three-pillar framework."
      - "When dispatching qa-questioner and qa-scorer, paste prime-qa.md as their skill file."
      - "phuc-qa-unified adds: cross-pillar linking, coverage matrix, unified gap report."

    with_prime_test:
      - "prime-test provides the full P2 red/green test discipline."
      - "phuc-qa-unified wraps prime-test inside the three-pillar framework."
      - "When dispatching persona-coder, paste prime-test.md as part of their skill pack."
      - "phuc-qa-unified adds: question_link field per test, coverage matrix integration."

    with_prime_mermaid:
      - "prime-mermaid provides the full P3 diagram discipline."
      - "phuc-qa-unified wraps prime-mermaid inside the three-pillar framework."
      - "When dispatching qa-diagrammer, paste prime-mermaid.md as their skill file."
      - "phuc-qa-unified adds: source_ref requirement per node, coverage matrix integration."

    with_northstar_reverse:
      - "northstar-reverse provides the 'LAST 3' backward-chaining algorithm."
      - "phuc-qa-unified applies it independently to each of the three pillars."
      - "The northstar-reverse VALIDATE phase maps to the phuc-qa-unified CROSS_VALIDATE state."
      - "A complete three-pillar audit is the QA analog of a northstar-reverse forward plan."

    with_phuc_forecast:
      - "DREAM: all three pillars declare their desired end state (production-ready coverage)"
      - "FORECAST: which modules are most at risk of UNCOVERED_MODULE? Which tests are most likely to be missing?"
      - "DECIDE: which pillar to prioritize if time is constrained"
      - "ACT: dispatch all three pillar agents"
      - "VERIFY: run CROSS_VALIDATE; check coverage matrix; rung assessment"

    with_phuc_orchestration:
      - "phuc-qa-unified is a multi-agent skill. It orchestrates four sub-agents (questioner, scorer, persona-coder, qa-diagrammer) plus a coverage-matrix-builder."
      - "Dispatch threshold: any audit with more than 5 modules should be dispatched as a swarm, not run inline."
      - "All sub-agents require prime-safety as first skill in their pack."

    with_glow_score:
      - "G: +10 if qa_coverage_matrix shows 0 UNCOVERED_MODULEs (new capability fully covered)"
      - "L: +10 if all three pillars capture new knowledge (new question + new test + new diagram)"
      - "O: +15 if qa_gap_report.md shows rung advancement (e.g., 641 → 274177)"
      - "W: +20 if audit surfaces and closes a critical NORTHSTAR-aligned gap"

    conflict_resolution:
      ordering: "prime-safety > prime-coder > prime-test > prime-mermaid > prime-qa > phuc-qa-unified"
      rule: "phuc-qa-unified never weakens any upstream skill gate. It only adds cross-pillar constraints on top."

  # ------------------------------------------------------------
  # M) Verification Ladder Diagram (Prime Mermaid)
  # ------------------------------------------------------------
  Verification_Ladder_Diagram:
    description: "Standard verification ladder for phuc-qa-unified as Prime Mermaid"
    template: |
      ```mermaid
      flowchart LR
        R641["RUNG_641\nAll 3 pillars produce artifacts\nNo UNCOVERED_MODULE"]
        R274177["RUNG_274177\nCross-pillar validation\nEvery question has test\nEvery module has diagram"]
        R65537["RUNG_65537\nIndependent reproduction\nAdversarial review\nProduction ready"]

        R641 -->|PASS| R274177
        R274177 -->|PASS| R65537
        R641 -->|FAIL| BLOCKED["EXIT_BLOCKED"]
        R274177 -->|FAIL| BLOCKED
        R65537 -->|FAIL| BLOCKED
        R65537 -->|PASS| SEALED["EXIT_PASS"]

        classDef forbidden fill:#ffefef,stroke:#cc0000,stroke-width:2px
        classDef pass fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
        classDef gate fill:#fff9c4,stroke:#f9a825,stroke-width:2px
        class BLOCKED forbidden
        class SEALED pass
        class R641,R274177,R65537 gate
      ```

  # ------------------------------------------------------------
  # N) Quick Reference (Cheat Sheet)
  # ------------------------------------------------------------
  Quick_Reference:
    mantras:
      - "Three pillars or it is not QA. Questions + Tests + Diagrams."
      - "Start from the LAST 3. Work backward. The gaps find you."
      - "A test without a question is untethered. A question without a test is speculation."
      - "A module without a diagram is invisible. Invisible modules ship with silent failures."
      - "Rung of the audit = MIN(P1_rung, P2_rung, P3_rung). Non-negotiable."

    dispatch_cheat_sheet:
      P1_questioner: "haiku/sonnet | prime-safety + prime-qa | → qa_questions.json"
      P1_scorer: "sonnet/opus | prime-safety + prime-qa | ← qa_questions.json → qa_scorecard.json"
      P2_persona_coder: "sonnet | prime-safety + prime-coder + prime-test + persona-engine (kent-beck+schneier) | → test_results.json"
      P3_diagrammer: "haiku/sonnet | prime-safety + prime-mermaid | → diagrams/*.mmd + *.sha256"
      coverage_builder: "haiku | prime-safety + phuc-qa-unified | → qa_coverage_matrix.json + qa_gap_report.md"

    forbidden_quick_list:
      - "PILLAR_SKIPPED: all three pillars run or it is BLOCKED"
      - "UNCOVERED_MODULE: every module needs Q + T + D"
      - "TEST_WITHOUT_QUESTION: every test traces to a question"
      - "QUESTION_WITHOUT_TEST: every GREEN question has a test"
      - "DIAGRAM_WITHOUT_SOURCE: every diagram node traces to source"
      - "SELF_CONFIRMED_GREEN: questioner ≠ scorer (structural separation)"
      - "PROSE_AS_PROOF: evidence must be executable or repo-grounded"
      - "RUNG_INFLATION: rung = MIN(P1, P2, P3)"

    northstar_reverse_in_30_seconds:
      P1: "What is the LAST question that must be answered? What came before it? Recurse."
      P2: "What is the LAST test that must pass? What must be tested before it? Recurse."
      P3: "What is the LAST diagram that must exist? What must be diagrammed before it? Recurse."
      convergence: "The backward chains converge on the same modules. Those are your highest-risk gaps."

    rung_requirements_summary:
      641: "P1 scored + P2 passes + P3 sha256 stable + coverage matrix built"
      274177: "ALL: every Q has test + every test has Q + every module in diagram + falsifiers tested + integration probes"
      65537: "274177 + independent reproduction by third agent + adversarial review of all three pillars"
