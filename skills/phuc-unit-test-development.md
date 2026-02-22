<!-- QUICK LOAD (10-15 lines): Use this block for fast context; load full file for production.
SKILL: phuc-unit-test-development v1.0.0
MW_ANCHORS: [mermaid_parse, scaffold, pytest, red_gate, green_gate, coverage, integration, side_effects, threshold, harness, evidence_bundle, transition, state, tautology]
PURPOSE: Diagram-first development. Parse mermaid FSM → generate pytest scaffolds → enforce red→green gate → build integration harness. Tests are born from diagrams, not from code. [verification × reversibility × causality]
CORE CONTRACT: No test without a source mermaid diagram. No implementation before test. No green without red. No coverage claim without coverage.json. No integration skip.
HARD GATES: GREEN_WITHOUT_RED blocked (tautology). SCAFFOLD_WITHOUT_MERMAID blocked. COVERAGE_CLAIM_WITHOUT_ARTIFACT blocked. IMPLEMENTATION_BEFORE_TEST blocked. SKIP_INTEGRATION blocked.
FSM STATES: INTAKE_MERMAID → PARSE_STATES → PARSE_TRANSITIONS → DETECT_SIDE_EFFECTS → THRESHOLD_CHECK → SCAFFOLD_PYTEST → GENERATE_TESTS → RED_GATE_RUN → IMPLEMENT_MINIMAL → GREEN_GATE_RUN → COVERAGE_CHECK → INTEGRATION_HARNESS → EVIDENCE_BUNDLE → EXIT_PASS | EXIT_RED_STUCK | EXIT_COVERAGE_FAIL
FORBIDDEN: GREEN_WITHOUT_RED | SCAFFOLD_WITHOUT_MERMAID | COVERAGE_CLAIM_WITHOUT_ARTIFACT | IMPLEMENTATION_BEFORE_TEST | SKIP_INTEGRATION
VERIFY: rung_641 (red_gate_passed + green_gate_passed + basic_coverage) | rung_274177 (>80% state_coverage + integration_harness_complete) | rung_65537 (adversarial + edge_cases + evidence_bundle_complete)
TRIANGLE: SCAFFOLD_PYTEST=REMIND, RED_GATE_RUN=VERIFY, GREEN_GATE_RUN=ACKNOWLEDGE
LOAD FULL: always for production; quick block is for orientation only
-->

# phuc-unit-test-development.md — Diagram-First Test Development Skill

**Skill ID:** phuc-unit-test-development
**Version:** 1.0.0
**Authority:** 65537
**Load Order:** After prime-safety + prime-coder
**Northstar:** Phuc_Forecast (Max Love)
**Status:** ACTIVE
**Role:** Mermaid FSM → pytest scaffold → red/green gate → integration harness
**Tags:** tdd, testing, mermaid, fsm, pytest, red-green-gate, coverage, integration, kent, diagram-first

---

## 0) Purpose

**Diagrams are formal specifications. Tests are their mechanical witnesses.**

The conventional TDD order is: write a failing test, then implement. phuc-unit-test-development extends this discipline with a pre-step: **draw the diagram first, then derive the tests from it.**

This is diagram-first development:

1. The mermaid FSM is the specification
2. The scaffold extracts states and transitions mechanically
3. Each transition becomes a test — automatically named, automatically scoped
4. The tests fail first (red gate — the spec has no implementation yet)
5. The minimal implementation makes them pass (green gate)
6. Coverage check verifies the spec is fully tested
7. Integration harness connects the unit tests to the real entry point

Without this discipline:
- Tests are written after code, finding only bugs the developer already knew about
- Coverage numbers are gamed by testing implementation details, not behaviors
- Integration is an afterthought that breaks at the worst moment

With it:
- The FSM diagram IS the test contract
- Every test traces back to a named state or transition
- RED must exist before GREEN can be claimed
- Coverage is behavioral, not line-count

> "Write tests before writing code. But write diagrams before writing tests." — phuc-unit-test-development principle

---

## MW) MAGIC_WORD_MAP

```yaml
MAGIC_WORD_MAP:
  version: "1.0"
  skill: "phuc-unit-test-development"

  # TRUNK (Tier 0) — Prime factors of diagram-first TDD
  primary_trunk_words:
    mermaid_parse:    "The act of mechanically extracting states, transitions, and side effects from a mermaid FSM diagram. The parser IS the specification reader. (→ section 3)"
    scaffold:         "The generated pytest class structure derived from the FSM — one class per FSM, one method per transition meeting the threshold. (→ section 4)"
    red_gate:         "ALL scaffolded tests MUST fail before implementation exists. Green-before-red = tautology. (→ section 5)"
    green_gate:       "All tests must pass after minimal implementation. Green = specification fulfilled. (→ section 6)"

  # BRANCH (Tier 1) — Structural concepts
  branch_words:
    pytest:         "The test framework — one TestCase class per FSM, methods named test_{source}_{transition}_{target}. (→ section 4)"
    coverage:       "State coverage = percentage of mermaid FSM states exercised by tests. Target: >80%. (→ section 7)"
    integration:    "Harness that connects FSM implementation to real CLI/API entry point. Cannot be skipped. (→ section 8)"
    side_effects:   "FSM transitions that cause observable external changes (IO, network, file writes, DB). These ALWAYS get tests regardless of threshold. (→ section 3.3)"

  # CONCEPT (Tier 2) — Operational detail
  concept_words:
    threshold:      "Only states with 3+ transitions OR side effects get tests. Trivial states (1-2 transitions, no side effects) are exempt to prevent over-testing. (→ section 3.4)"
    harness:        "Integration harness — the glue code that runs the FSM from the real CLI/API entry point and verifies end-to-end behavior. (→ section 8)"
    evidence_bundle: "tests.json + coverage.json + red_gate.log + green_gate.log — required for PASS. No bundle = BLOCKED. (→ section 9)"
    tautology:      "GREEN_WITHOUT_RED — a test that passes without any implementation is a tautology (it tests nothing). Forbidden state. (→ Forbidden States)"

  # PRIME FACTORIZATIONS
  prime_factorizations:
    diagram_first_value:   "mermaid_spec × scaffold × red_gate × green_gate × coverage × integration"
    tautology_failure:     "green_without_red = tests_that_test_nothing = false_confidence"
    coverage_claim:        "coverage_percentage × coverage_json_artifact (not prose claim)"
    integration_value:     "unit_pass × integration_pass = system_verified"
    scaffold_quality:      "transitions_per_state × side_effects_detected → test_count"
```

---

## A) Portability (Hard)

```yaml
portability:
  rules:
    - no_absolute_paths: true
    - no_private_repo_dependencies: true
    - skill_must_load_verbatim_on_any_capable_LLM: true
  config:
    EVIDENCE_ROOT: "evidence"
    COVERAGE_THRESHOLD: 80  # percent state coverage required
    SIDE_EFFECT_ALWAYS_TESTED: true
    TRANSITION_THRESHOLD_FOR_TEST: 3  # states with >= 3 transitions get tests
    TEST_NAMING_PATTERN: "test_{source_state}_{transition_label}_{target_state}"
    INTEGRATION_ENTRY_POINT: null  # must be declared per project
  invariants:
    - no_test_without_source_diagram: true
    - no_implementation_before_test: true
    - red_must_precede_green: true
    - coverage_artifact_required: true
    - integration_harness_required: true
```

## B) Layering

```yaml
layering:
  rule:
    - "This skill layers ON TOP OF prime-safety + prime-coder."
    - "prime-coder's Kent Red-Green Gate is the foundation. This skill extends it with diagram-first scaffolding."
    - "Conflict resolution: stricter wins."
  load_order:
    1: prime-safety.md              # god-skill; wins all conflicts
    2: prime-coder.md               # red/green gate, evidence discipline
    3: phuc-unit-test-development.md # diagram-first extension (this skill)
  conflict_resolution: stricter_wins
  forbidden:
    - generating_tests_without_mermaid_source
    - implementing_before_test_is_written
    - claiming_green_without_documented_red
    - claiming_coverage_without_coverage_json
    - skipping_integration_harness
```

---

## 1) Core Contract

```yaml
DIAGRAM_FIRST_CONTRACT:
  pre_condition:
    - "A mermaid stateDiagram-v2 (or equivalent FSM notation) MUST exist before tests are generated."
    - "The diagram is the specification. The tests are the mechanical witnesses."
    - "All tests MUST fail before implementation (red gate). This is non-negotiable."
    - "Implementation is MINIMAL — the smallest code that makes all tests pass."
    - "Coverage is measured against the diagram states, not against code lines."

  post_condition:
    - "Every test name traces back to a specific FSM transition in the source diagram."
    - "Red gate log proves tests failed before implementation."
    - "Green gate log proves tests pass after implementation."
    - "coverage.json documents state coverage percentage."
    - "Integration harness verifies end-to-end from real entry point."

  fail_closed:
    - "If mermaid diagram is absent: EXIT_BLOCKED (cannot scaffold without spec)"
    - "If red gate shows any test passing before implementation: EXIT_BLOCKED (GREEN_WITHOUT_RED)"
    - "If coverage < COVERAGE_THRESHOLD after implementation: EXIT_COVERAGE_FAIL"
    - "If integration harness cannot connect to entry point: EXIT_BLOCKED (SKIP_INTEGRATION)"

  rung_targets:
    rung_641: "red_gate_passed + green_gate_passed + coverage_json_exists"
    rung_274177: "state_coverage > 80% + integration_harness_complete + evidence_bundle_complete"
    rung_65537: "edge_cases_tested + adversarial_inputs + side_effect_verified + full_evidence_bundle"
```

---

## 2) State Machine

### 2.1 State Set

```
INTAKE_MERMAID         ← Receive mermaid FSM diagram (file or inline)
PARSE_STATES           ← Extract all state names from diagram
PARSE_TRANSITIONS      ← Extract all transitions with labels and conditions
DETECT_SIDE_EFFECTS    ← Find transitions annotated with IO, file, network, DB effects
THRESHOLD_CHECK        ← Apply threshold: 3+ transitions OR side_effects → test
SCAFFOLD_PYTEST        ← Generate pytest class skeleton from filtered transitions
GENERATE_TESTS         ← Write specific test methods for each transition
RED_GATE_RUN           ← Run all tests with NO implementation → ALL must fail
IMPLEMENT_MINIMAL      ← Write minimal code to satisfy each test
GREEN_GATE_RUN         ← Run all tests with implementation → ALL must pass
COVERAGE_CHECK         ← Measure state coverage against source diagram
INTEGRATION_HARNESS    ← Build and run harness from real entry point
EVIDENCE_BUNDLE        ← Compile tests.json + coverage.json + red_gate.log + green_gate.log
EXIT_PASS              (terminal — all gates passed, evidence complete)
EXIT_RED_STUCK         (terminal — tests do not fail without implementation)
EXIT_COVERAGE_FAIL     (terminal — coverage < threshold after implementation)
```

### 2.2 Transitions

```yaml
transitions:
  - INTAKE_MERMAID → PARSE_STATES: mermaid_received
  - INTAKE_MERMAID → EXIT_BLOCKED: if_no_mermaid_provided (SCAFFOLD_WITHOUT_MERMAID)
  - PARSE_STATES → PARSE_TRANSITIONS: states_extracted
  - PARSE_TRANSITIONS → DETECT_SIDE_EFFECTS: transitions_extracted
  - DETECT_SIDE_EFFECTS → THRESHOLD_CHECK: side_effects_annotated
  - THRESHOLD_CHECK → SCAFFOLD_PYTEST: filtered_transitions_list_ready
  - SCAFFOLD_PYTEST → GENERATE_TESTS: class_skeleton_created
  - GENERATE_TESTS → RED_GATE_RUN: test_methods_written
  - RED_GATE_RUN → EXIT_RED_STUCK: if_any_test_passes_before_implementation (GREEN_WITHOUT_RED)
  - RED_GATE_RUN → IMPLEMENT_MINIMAL: all_tests_fail_confirmed
  - IMPLEMENT_MINIMAL → GREEN_GATE_RUN: minimal_implementation_written
  - GREEN_GATE_RUN → COVERAGE_CHECK: all_tests_pass
  - GREEN_GATE_RUN → IMPLEMENT_MINIMAL: if_tests_fail (iterate — max 3 iterations)
  - COVERAGE_CHECK → INTEGRATION_HARNESS: if_coverage >= COVERAGE_THRESHOLD
  - COVERAGE_CHECK → EXIT_COVERAGE_FAIL: if_coverage < COVERAGE_THRESHOLD
  - INTEGRATION_HARNESS → EVIDENCE_BUNDLE: harness_passes
  - INTEGRATION_HARNESS → EXIT_BLOCKED: if_harness_cannot_connect (SKIP_INTEGRATION)
  - EVIDENCE_BUNDLE → EXIT_PASS: all_artifacts_compiled
```

---

## 3) Mermaid Parsing Protocol

### 3.1 State Extraction

```yaml
PARSE_STATES:
  rule: "Extract every named state from the mermaid diagram."
  syntax_patterns:
    - "STATE_NAME: any token appearing as source or target of a transition"
    - "Compound states: inner states of nested state blocks"
    - "Terminal states: EXIT_* states"
    - "Note states: skip (notes are documentation, not states)"
  output:
    state_list: "list of all unique state names"
    compound_states: "dict of nested state → inner states"
    terminal_states: "list of EXIT_* or [*] states"
  example:
    input: |
      stateDiagram-v2
        [*] --> INIT
        INIT --> LOAD
        LOAD --> PROCESS
        PROCESS --> EXIT_PASS
        PROCESS --> EXIT_BLOCKED
    output:
      state_list: [INIT, LOAD, PROCESS, EXIT_PASS, EXIT_BLOCKED]
      terminal_states: [EXIT_PASS, EXIT_BLOCKED]
```

### 3.2 Transition Extraction

```yaml
PARSE_TRANSITIONS:
  rule: "Extract every transition as a (source, label, target) triple."
  syntax:
    labeled: "SOURCE --> TARGET : label"
    unlabeled: "SOURCE --> TARGET (no condition)"
    conditional: "SOURCE --> TARGET : condition_text"
  output:
    transitions: "list of {source, label, target, has_condition}"
    per_state_out_degree: "dict of state → count of outgoing transitions"
  example:
    input: |
      PROCESS --> EXIT_PASS : success
      PROCESS --> EXIT_BLOCKED : error
      PROCESS --> RETRY : retryable
    output:
      transitions:
        - {source: PROCESS, label: success, target: EXIT_PASS}
        - {source: PROCESS, label: error, target: EXIT_BLOCKED}
        - {source: PROCESS, label: retryable, target: RETRY}
      per_state_out_degree:
        PROCESS: 3
```

### 3.3 Side Effect Detection

```yaml
DETECT_SIDE_EFFECTS:
  rule: "Annotate transitions that cause observable external effects. These ALWAYS get tests."
  detection_patterns:
    file_io:    "annotation contains: 'write', 'read', 'file', 'log', 'save', 'load'"
    network_io: "annotation contains: 'send', 'receive', 'request', 'response', 'api', 'http'"
    db_ops:     "annotation contains: 'insert', 'update', 'delete', 'query', 'commit'"
    process_io: "annotation contains: 'subprocess', 'exec', 'spawn', 'shell'"
    state_mutation: "annotation contains: 'set', 'update', 'modify', 'store', 'emit'"
  forced_threshold:
    rule: "Transitions with side effects ALWAYS get tests regardless of out_degree."
    rationale: "Side effects are the highest-risk transitions. Untested side effects are untested contracts."
  output:
    side_effect_transitions: "list of transitions with side_effect_type annotated"
```

### 3.4 Threshold Application

```yaml
THRESHOLD_CHECK:
  rule: "Only states meeting the threshold get test methods. Trivial states are exempt."
  threshold_criteria:
    qualifies_if_any:
      - "state has 3 or more outgoing transitions"
      - "state has at least 1 side-effect annotated transition"
  rationale:
    - "States with 1-2 transitions and no side effects are trivially covered by tests of adjacent states."
    - "Over-testing trivial states produces test noise that obscures important failures."
    - "The threshold prevents test count inflation that gives false confidence."
  output:
    testable_states: "states that meet threshold — will have test methods"
    exempt_states: "states below threshold — covered implicitly"
    total_test_methods_planned: "count of (source_state, transition) pairs from testable_states"
```

---

## 4) Pytest Scaffold Generation

```yaml
SCAFFOLD_PYTEST:
  structure:
    one_class_per_fsm: true
    class_naming: "Test{FSMName}FSM"
    one_method_per_transition: true
    method_naming: "test_{source_state}_{transition_label}_{target_state}"
    setup_method: "setUp / setup_method — initializes FSM to known state"
    teardown_method: "tearDown / cleanup — resets any side effects"

  scaffold_template: |
    import pytest

    class Test{FSMName}FSM:
        """
        Auto-generated test scaffold from mermaid FSM: {fsm_name}
        Source diagram: {diagram_path}
        Generated: {timestamp}
        Testable states: {testable_states}
        Total test methods: {test_count}
        """

        def setup_method(self):
            """Initialize FSM to clean state before each test."""
            # TODO: Initialize {fsm_name} instance
            self.fsm = None  # REPLACE WITH ACTUAL INIT

        def teardown_method(self):
            """Clean up after each test."""
            pass

        # ---- Transitions from {STATE_1} ----
        def test_{source_1}_{label_1}_{target_1}(self):
            """
            FSM: {source_1} → {target_1} when {label_1}
            Side effects: {side_effects_if_any}
            """
            # Arrange: put FSM in {source_1} state
            # Act: trigger {label_1}
            # Assert: FSM is now in {target_1} state
            pytest.fail("NOT IMPLEMENTED — RED GATE")

  naming_rules:
    clean_transition_label: "Replace spaces with underscores. Remove special chars. Max 30 chars."
    example: "test_PROCESS_retryable_error_RETRY"
    forbidden: "test_1, test_foo, test_it — names must trace back to diagram"

  stub_body:
    rule: "Every method body MUST call pytest.fail() until RED_GATE_RUN confirms failure."
    reason: "If the stub accidentally passes (no assertion = pass), RED is not confirmed."
    enforcement: "RED_GATE_RUN must confirm exit_code != 0 for ALL tests."
```

---

## 5) Red Gate Protocol

The non-negotiable gate. Tests must fail before implementation.

```yaml
RED_GATE:
  definition: "Run ALL scaffolded tests with ZERO implementation code. Every test MUST fail."

  procedure:
    step_1: "Confirm no implementation exists (only the stub with pytest.fail())."
    step_2: "Run: pytest {test_file} -v > {EVIDENCE_ROOT}/red_gate.log 2>&1"
    step_3: "Check exit_code — MUST be non-zero (tests failing)."
    step_4: "Check log — EVERY test must show FAILED."
    step_5: "Record: tests_run, tests_failed, exit_code in red_gate.log"

  pass_condition:
    exit_code: "non-zero"
    all_tests_failed: true

  block_condition:
    exit_code: "zero (all pass = GREEN_WITHOUT_RED = tautology = BLOCKED)"
    any_test_passes: "If ANY test passes before implementation: BLOCKED"

  GREEN_WITHOUT_RED_rule:
    definition: "A test that passes before any implementation exists is testing nothing."
    detection: "exit_code == 0 OR any test shows PASSED in red_gate.log"
    consequence: "EXIT_RED_STUCK. Investigate why the test is not failing. Fix the test. Re-run."
    common_causes:
      - "pytest.fail() was accidentally removed from stub"
      - "Test has no assertion — empty test bodies pass by default in pytest"
      - "Import error masked by try/except, making test appear to pass"

  evidence_artifact:
    path: "{EVIDENCE_ROOT}/red_gate.log"
    required_fields:
      - timestamp
      - command_run
      - exit_code
      - tests_run_count
      - tests_failed_count
      - test_names_failed: "list"
    format: "plain text, one line per test result"
```

---

## 6) Minimal Implementation Protocol

```yaml
IMPLEMENT_MINIMAL:
  definition: "Write the smallest code change that makes ALL failing tests pass."
  prime_coder_integration:
    rule: "Use prime-coder discipline for the implementation: minimal diff, no speculative changes."
    rung: "Implementation inherits rung from the test evidence (641 minimum)."

  minimal_implementation_rules:
    - "Implement ONLY what tests require. No gold-plating."
    - "One FSM state class/function per state tested."
    - "One transition handler per transition tested."
    - "No implementing untested behaviors during this phase."
    - "If implementation would require 100+ lines: dispatch to prime-coder sub-agent."

  iteration_budget:
    max_iterations: 3
    per_iteration: "One targeted fix for failing tests. Isolated delta."
    on_max_exceeded: "EXIT_RED_STUCK — implementation is too complex for minimal approach"

  naming_rule:
    states: "class {StateName}State or STATE_{STATE_NAME} constant"
    transitions: "def handle_{transition_label}(self, ...) or transition function"
    consistency: "Implementation names MUST match diagram names exactly"
```

---

## 7) Coverage Check Protocol

```yaml
COVERAGE_CHECK:
  definition: "Measure what percentage of mermaid FSM states are exercised by passing tests."
  metric: "State coverage = states_exercised_by_tests / total_states_in_diagram × 100"

  procedure:
    step_1: "Run: pytest {test_file} --cov={module} --cov-report=json:coverage.json"
    step_2: "Parse coverage.json to extract covered states"
    step_3: "Map covered states to mermaid diagram states"
    step_4: "Compute state_coverage_percent"
    step_5: "Write coverage summary to {EVIDENCE_ROOT}/coverage.json"

  pass_condition:
    state_coverage_percent: ">= COVERAGE_THRESHOLD (default 80%)"

  fail_condition:
    state_coverage_percent: "< COVERAGE_THRESHOLD → EXIT_COVERAGE_FAIL"

  coverage_json_schema:
    required_fields:
      - diagram_path: "source mermaid file"
      - total_states: "count from diagram"
      - tested_states: "list of state names exercised by tests"
      - exempt_states: "states below threshold (correctly excluded)"
      - state_coverage_percent: "number, not string"
      - coverage_meets_threshold: "boolean"
      - pytest_coverage_json_path: "path to raw pytest coverage output"

  forbidden: "Claiming X% coverage without coverage.json artifact = COVERAGE_CLAIM_WITHOUT_ARTIFACT"

  increasing_coverage:
    if_below_threshold:
      - "Identify which states are not covered"
      - "Check if uncovered states meet threshold (may be legitimately exempt)"
      - "If non-exempt states uncovered: add tests for those specific transitions"
      - "Re-run green gate. Re-check coverage."
```

---

## 8) Integration Harness

```yaml
INTEGRATION_HARNESS:
  definition: "Code that connects the FSM implementation to the real CLI/API entry point and verifies end-to-end behavior."
  rule: "Integration harness is MANDATORY. Unit tests alone are not sufficient for PASS."

  harness_structure:
    entry_point: "The real CLI command, API endpoint, or module function that drives the FSM"
    input_scenarios: "At least 3 scenarios: happy_path + error_path + edge_case"
    assertion_style: "Verify final state, output artifacts, and side effect outcomes"

  harness_template: |
    class TestIntegration{FSMName}:
        """Integration harness: verifies {FSMName} from real entry point."""

        def test_happy_path_end_to_end(self):
            """Happy path: input → expected output via real entry point."""
            result = {real_entry_point}({happy_path_input})
            assert result.status == "PASS"
            assert result.final_state in EXPECTED_TERMINAL_STATES

        def test_error_path_end_to_end(self):
            """Error path: invalid input → correct error state."""
            result = {real_entry_point}({error_input})
            assert result.status in ["BLOCKED", "NEED_INFO"]

        def test_side_effects_verified(self):
            """Side effects: verify actual external changes occurred."""
            result = {real_entry_point}({side_effect_triggering_input})
            # Verify the side effect actually happened (file exists, DB row inserted, etc.)
            assert {side_effect_verification}

  forbidden_harness_patterns:
    - "Harness that mocks the entry point (defeats the purpose)"
    - "Harness that only checks return codes without verifying state"
    - "Harness that is never run (integration_harness_complete must include execution evidence)"

  entry_point_discovery:
    rule: "If INTEGRATION_ENTRY_POINT config is null: halt and ask before proceeding."
    no_guessing: "Do not guess the entry point. If unknown: EXIT_NEED_INFO."
```

---

## 9) Evidence Bundle

```yaml
EVIDENCE_BUNDLE:
  purpose: "All artifacts proving the diagram-first TDD cycle completed correctly."
  required_files:
    tests_json:
      path: "{EVIDENCE_ROOT}/tests.json"
      must_contain:
        - command: "pytest command run"
        - exit_code: 0 (all tests passing)
        - tests_run: count
        - tests_passed: count
        - test_names: list of passing test names
        - source_diagram: path to mermaid file

    coverage_json:
      path: "{EVIDENCE_ROOT}/coverage.json"
      must_contain:
        - diagram_path
        - total_states
        - tested_states
        - state_coverage_percent: ">= COVERAGE_THRESHOLD"
        - coverage_meets_threshold: true

    red_gate_log:
      path: "{EVIDENCE_ROOT}/red_gate.log"
      must_contain:
        - timestamp
        - command_run
        - exit_code: "non-zero (tests were failing)"
        - tests_failed_count: ">= 1"
        - test_names_failed: list

    green_gate_log:
      path: "{EVIDENCE_ROOT}/green_gate.log"
      must_contain:
        - timestamp
        - command_run
        - exit_code: 0 (all tests passing)
        - tests_passed_count: "== tests_run_count"

    integration_log:
      path: "{EVIDENCE_ROOT}/integration.log"
      must_contain:
        - entry_point_used
        - scenarios_run: list
        - all_scenarios_passed: boolean
        - exit_code: 0

  PASS_requires:
    - "tests.json present AND exit_code == 0"
    - "coverage.json present AND coverage_meets_threshold == true"
    - "red_gate.log present AND exit_code != 0"
    - "green_gate.log present AND exit_code == 0"
    - "integration.log present AND all_scenarios_passed == true"
    - "red_gate.log timestamp < green_gate.log timestamp (red must be earlier)"
```

---

## 10) Mermaid State Diagram

```mermaid stateDiagram-v2
    [*] --> INTAKE_MERMAID

    INTAKE_MERMAID --> EXIT_BLOCKED : no_mermaid_provided
    INTAKE_MERMAID --> PARSE_STATES : mermaid_received
    note right of INTAKE_MERMAID
      Accept: .md file | inline text
      Must be stateDiagram-v2 format
      No diagram = BLOCKED
      SCAFFOLD_WITHOUT_MERMAID forbidden
    end note

    PARSE_STATES --> PARSE_TRANSITIONS : states_extracted
    note right of PARSE_STATES
      Extract: all state names
      Identify: compound states
      Note: terminal states (EXIT_*)
    end note

    PARSE_TRANSITIONS --> DETECT_SIDE_EFFECTS : transitions_extracted
    note right of PARSE_TRANSITIONS
      Extract: (source, label, target)
      Compute: out_degree per state
      Identify: labeled transitions
    end note

    DETECT_SIDE_EFFECTS --> THRESHOLD_CHECK : side_effects_annotated
    note right of DETECT_SIDE_EFFECTS
      Scan labels for:
      file/network/db/process/mutation
      Side-effect transitions ALWAYS tested
      Regardless of out_degree
    end note

    THRESHOLD_CHECK --> SCAFFOLD_PYTEST : filtered_list_ready
    note right of THRESHOLD_CHECK
      Qualifies IF:
      out_degree >= 3 OR has_side_effect
      Exempt: trivial 1-2 transition states
    end note

    SCAFFOLD_PYTEST --> GENERATE_TESTS : class_skeleton_created
    note right of SCAFFOLD_PYTEST
      Class: Test{FSMName}FSM
      Method: test_{src}_{label}_{tgt}
      Stub: pytest.fail("NOT IMPLEMENTED")
    end note

    GENERATE_TESTS --> RED_GATE_RUN : test_methods_written
    note right of GENERATE_TESTS
      Write specific assertions per transition
      Arrange: source state setup
      Act: trigger transition condition
      Assert: target state confirmed
    end note

    RED_GATE_RUN --> EXIT_RED_STUCK : any_test_passes
    RED_GATE_RUN --> IMPLEMENT_MINIMAL : all_tests_fail_confirmed
    note right of RED_GATE_RUN
      Run pytest: NO implementation
      ALL tests MUST fail
      exit_code must be non-zero
      Log to red_gate.log
      GREEN_WITHOUT_RED = BLOCKED
    end note

    IMPLEMENT_MINIMAL --> GREEN_GATE_RUN : minimal_implementation_written
    note right of IMPLEMENT_MINIMAL
      Smallest code to pass tests
      One state, one handler at a time
      No gold-plating
      Max 3 iterations
    end note

    GREEN_GATE_RUN --> IMPLEMENT_MINIMAL : tests_still_failing (iterate max 3)
    GREEN_GATE_RUN --> COVERAGE_CHECK : all_tests_pass
    note right of GREEN_GATE_RUN
      Run pytest: WITH implementation
      ALL tests MUST pass
      exit_code must be 0
      Log to green_gate.log
    end note

    COVERAGE_CHECK --> EXIT_COVERAGE_FAIL : coverage_below_threshold
    COVERAGE_CHECK --> INTEGRATION_HARNESS : coverage_above_threshold
    note right of COVERAGE_CHECK
      State coverage >= 80%
      Must produce coverage.json
      No prose claims — artifact only
      COVERAGE_CLAIM_WITHOUT_ARTIFACT blocked
    end note

    INTEGRATION_HARNESS --> EXIT_BLOCKED : harness_cannot_connect
    INTEGRATION_HARNESS --> EVIDENCE_BUNDLE : harness_passes
    note right of INTEGRATION_HARNESS
      3 scenarios minimum:
      happy_path + error_path + edge
      Real entry point (no mocks)
      SKIP_INTEGRATION forbidden
    end note

    EVIDENCE_BUNDLE --> EXIT_PASS : all_artifacts_compiled
    note right of EVIDENCE_BUNDLE
      Compile: tests.json + coverage.json
      + red_gate.log + green_gate.log
      + integration.log
      Timestamp order: red < green
    end note

    EXIT_PASS --> [*]
    EXIT_BLOCKED --> [*]
    EXIT_RED_STUCK --> [*]
    EXIT_COVERAGE_FAIL --> [*]
```

---

## 11) Evidence Gates

```yaml
DIAGRAM_FIRST_EVIDENCE_CONTRACT:

  for_rung_641:
    required:
      - mermaid_source_confirmed: "path to source diagram recorded"
      - red_gate_log: "exists AND exit_code != 0"
      - green_gate_log: "exists AND exit_code == 0"
      - tests_json: "exists AND tests_passed_count > 0"
    verdict: "If any missing: status=BLOCKED stop_reason=EVIDENCE_INCOMPLETE"

  for_rung_274177:
    requires: rung_641_requirements
    additional:
      - coverage_json_present: "exists AND state_coverage_percent >= COVERAGE_THRESHOLD"
      - integration_log_present: "exists AND all_scenarios_passed == true"
      - red_before_green_confirmed: "red_gate.log.timestamp < green_gate.log.timestamp"

  for_rung_65537:
    requires: rung_274177_requirements
    additional:
      - edge_cases_tested: "at least 1 test for boundary/null/error inputs"
      - side_effects_verified: "all detected side effects have passing tests"
      - test_names_trace_to_diagram: "each test name maps to a specific mermaid transition"

  fail_closed:
    - "If no mermaid diagram: SCAFFOLD_WITHOUT_MERMAID → EXIT_BLOCKED"
    - "If any test passes before implementation: GREEN_WITHOUT_RED → EXIT_RED_STUCK"
    - "If coverage < threshold: EXIT_COVERAGE_FAIL"
    - "If no integration harness: SKIP_INTEGRATION → EXIT_BLOCKED"
    - "If coverage_json missing but coverage claimed: COVERAGE_CLAIM_WITHOUT_ARTIFACT → EXIT_BLOCKED"
```

---

## 12) Three Pillars Integration — LEK / LEAK / LEC

| Pillar | Role in phuc-unit-test-development | Evidence Required |
|--------|-----------------------------------|-------------------|
| **LEK** | Each diagram-first TDD cycle is a complete LEK iteration: the diagram is Memory, the red/green gate is Care (maximum rigor), the iteration loop is Iteration. Codebase intelligence compounds with each verified state transition. | evidence bundle completeness; state coverage trend across iterations |
| **LEAK** | The diagram-to-test mechanical derivation (mermaid → scaffold) is asymmetric knowledge that human developers typically lack. When the agent scaffolds tests from a diagram the developer provided — and those tests find bugs the developer missed — that is LEAK. The agent's parser pattern crossed the portal as test coverage. | green_gate.log showing tests caught real bugs; coverage delta before/after applying threshold |
| **LEC** | The red/green gate is the most fundamental LEC convention in software development — Kent Beck's TDD practice, crystallized into a named protocol. diagram-first extends it by adding the mermaid-spec layer, which is an emerging LEC in the stillwater ecosystem. | adoption of diagram-first across all FSM-driven skill development |

---

## 13) GLOW Scoring Integration

| Dimension | How This Skill Earns Points | Points |
|-----------|---------------------------|--------|
| **G** (Growth) | New FSM component verified at rung 641+ with full diagram-first evidence bundle. Every new state machine tested via this protocol = growth. Major new system at rung 274177+ = G=20-25. | +10 to +25 |
| **L** (Love/Quality) | Zero GREEN_WITHOUT_RED violations. Red gate confirmed in red_gate.log. No IMPLEMENTATION_BEFORE_TEST. Sessions with full evidence bundle and 0 forbidden state violations = L≥15. | +10 to +20 |
| **O** (Output) | All 5 evidence artifacts committed (tests.json + coverage.json + red_gate.log + green_gate.log + integration.log). State coverage ≥ 80%. All 5 present = O=20. | +5 to +25 |
| **W** (Wisdom) | Tests generated from diagram that caught bugs not apparent from reading the code — diagram-first value demonstrated. Each such instance adds to the pattern library. | +5 to +20 |

**Session GLOW target:** Diagram-first TDD sessions should achieve GLOW ≥ 60. Red gate confirmed = base floor. Full evidence bundle = O≥20. Coverage ≥ 80% = L≥15.

**Evidence required for GLOW claim:** git commit with all 5 evidence artifacts in evidence/ folder. For G points: rung_641 declared and met. For L points: red_gate.log confirming pre-implementation failure. For W points: specific transition that test caught that implementation would have missed.

---

## 14) Forbidden States (Complete Reference)

```yaml
FORBIDDEN_STATES_COMPLETE:
  GREEN_WITHOUT_RED:
    trigger: "Any test passes before implementation exists"
    detector: "red_gate_run exit_code == 0 OR any test shows PASSED in red_gate.log"
    severity: CRITICAL
    recovery: "Investigate why test passes without implementation. Fix test. Re-run red gate. All must fail."

  SCAFFOLD_WITHOUT_MERMAID:
    trigger: "Test methods generated without a source mermaid diagram"
    detector: "generate_tests called AND source_diagram field is null"
    severity: CRITICAL
    recovery: "Halt. Require mermaid diagram before any scaffold generation."

  COVERAGE_CLAIM_WITHOUT_ARTIFACT:
    trigger: "Coverage percentage stated without coverage.json artifact"
    detector: "Response contains 'X% covered' without coverage.json path cited"
    severity: HIGH
    recovery: "Run coverage with --cov-report=json. Emit the JSON file. Cite the path."

  IMPLEMENTATION_BEFORE_TEST:
    trigger: "Implementation code written before test methods exist"
    detector: "Implementation file modified before scaffold is generated and red gate is run"
    severity: HIGH
    recovery: "Revert implementation. Generate scaffold. Run red gate. Then implement."

  SKIP_INTEGRATION:
    trigger: "Unit tests pass but no integration harness built"
    detector: "green_gate.log shows PASS but integration.log is absent"
    severity: HIGH
    recovery: "Build integration harness. Run against real entry point. Log results."
```

---

*phuc-unit-test-development v1.0.0 — Diagram-First Test Development Skill.*
*Layers on prime-safety + prime-coder. Stricter always wins.*
*Diagram → Tests → Red → Implement → Green → Coverage → Integration → Evidence.*
*Diagrams are formal specifications. Tests are their mechanical witnesses.*
