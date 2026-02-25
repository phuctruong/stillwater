# Phuc Unit Test Development Flow

**Purpose:** Describes the full pipeline from a mermaid FSM source file to a verified, integrated test suite — enforcing the red-green gate discipline where all generated tests must fail before implementation and pass after, with state coverage above 80% required before integration.
**Inputs:** Mermaid FSM source file (.md with stateDiagram-v2 or flowchart block)
**Outputs:** pytest test module, implementation module, evidence bundle (tests.json + coverage.json + red_gate.log + green_gate.log)
**Latency:** Parse + scaffold: ~5s; Red gate run: ~10s; Implementation: varies; Green gate run: ~10s; Coverage: ~5s

---

```mermaid
flowchart TD
    INPUT([Input:\nMermaid FSM source file\n.md with stateDiagram-v2\nor flowchart block]) --> PARSE

    subgraph TEST_GEN["Test Generation"]
        PARSE[Parse Mermaid Source\nextract: states, transitions,\nside effects, forbidden states]
        PARSE --> EXTRACT[Extract State Graph\nbuild adjacency map\nnode: state, edge: transition + guard]
        EXTRACT --> THRESHOLD{Threshold Filter\nState has 3+ transitions\nOR has side effects?}
        THRESHOLD -->|Yes — include| SCAFFOLD[Scaffold pytest class\nclass Test<StateName>:\n    setup_method\n    teardown_method]
        THRESHOLD -->|No — skip| SKIP_STATE[Skip state\nno test class needed\nlog: skipped_states.json]
        SKIP_STATE --> THRESHOLD
        SCAFFOLD --> GEN_METHODS[Generate test methods\ntest_<state>_<transition>_<target>\none method per edge in threshold states]
        GEN_METHODS --> GEN_FORBIDDEN[Generate forbidden state tests\ntest_forbidden_<state>_not_reachable\nassert raises ProtocolViolation]
        GEN_FORBIDDEN --> WRITE_TEST_FILE[Write test file\ntests/test_<fsm_name>.py\nall methods: assert False — stub]
    end

    WRITE_TEST_FILE --> RED_GATE

    subgraph RED_GREEN["Red-Green Cycle"]
        RED_GATE[Red Gate\npytest tests/test_<fsm_name>.py\n--tb=short -q]
        RED_GATE --> RED_CHECK{All tests\nFAIL?}
        RED_CHECK -->|Not all fail\n(some pass)| RED_FAIL_ALERT[ALERT: Red Gate Violated\nTest passed before implementation\nCheck for stub pollution or\npre-existing code collision]
        RED_FAIL_ALERT --> RED_INSPECT[Inspect: is test logically valid?\nFix test or remove collision]
        RED_INSPECT --> RED_GATE
        RED_CHECK -->|All fail — correct| RED_LOG[Write red_gate.log\ntimestamp + test_count + all_failed=true]

        RED_LOG --> IMPLEMENT[Implement minimal code\nper failing test\nno over-engineering\ntest-name drives scope]
        IMPLEMENT --> GREEN_GATE[Green Gate\npytest tests/test_<fsm_name>.py\n--tb=short -q]
        GREEN_GATE --> GREEN_CHECK{All tests\nPASS?}
        GREEN_CHECK -->|Some fail| FIX_IMPL[Fix implementation\ndo not touch test methods\ntest is the contract]
        FIX_IMPL --> GREEN_GATE
        GREEN_CHECK -->|All pass — correct| GREEN_LOG[Write green_gate.log\ntimestamp + test_count + all_passed=true]
    end

    GREEN_LOG --> COVERAGE

    subgraph INTEGRATION["Integration"]
        COVERAGE[Compute state coverage\npytest --cov + coverage.json\nstate_coverage = tested_states / total_states]
        COVERAGE --> COV_CHECK{State coverage\n> 80%?}
        COV_CHECK -->|Below 80%| COV_ALERT[ALERT: Coverage insufficient\nidentify uncovered states\nadd tests for missed transitions]
        COV_ALERT --> GEN_METHODS
        COV_CHECK -->|>= 80% — pass| BUNDLE[Bundle evidence\ntests.json\ncoverage.json\nred_gate.log\ngreen_gate.log]
        BUNDLE --> CONNECT[Connect to CLI entry point\nregister FSM module in\nsrc/stillwater/<module>.py]
        CONNECT --> INTEGRATION_TEST[Integration test run\npytest tests/integration/\ntest_<fsm_name>_cli.py]
        INTEGRATION_TEST --> INT_CHECK{Integration\ntests pass?}
        INT_CHECK -->|Fail| DEBUG_WIRING[Debug wiring\ncheck CLI registration\ncheck import paths\ncheck state init]
        DEBUG_WIRING --> INTEGRATION_TEST
        INT_CHECK -->|Pass| EVIDENCE_SEAL[Seal evidence bundle\nadd integration_tests.json\ncompute rung = MIN(641, unit_rung, int_rung)]
    end

    EVIDENCE_SEAL --> OUTPUT([Output:\nVerified FSM module + tests\nEvidence bundle sealed\nRung declared])

    classDef gen fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef red fill:#f44336,color:#fff,stroke:#b71c1c
    classDef green fill:#4CAF50,color:#fff,stroke:#388E3C
    classDef int fill:#2196F3,color:#fff,stroke:#1565C0
    classDef alert fill:#FF5722,color:#fff,stroke:#BF360C
    classDef io fill:#607D8B,color:#fff,stroke:#37474F

    class PARSE,EXTRACT,THRESHOLD,SCAFFOLD,GEN_METHODS,GEN_FORBIDDEN,WRITE_TEST_FILE,SKIP_STATE gen
    class RED_GATE,RED_CHECK,RED_LOG red
    class RED_FAIL_ALERT,RED_INSPECT,FIX_IMPL,COV_ALERT,DEBUG_WIRING alert
    class IMPLEMENT,GREEN_GATE,GREEN_CHECK,GREEN_LOG green
    class COVERAGE,COV_CHECK,BUNDLE,CONNECT,INTEGRATION_TEST,INT_CHECK,EVIDENCE_SEAL int
    class INPUT,OUTPUT io
```

## Notes

- **The Red Gate is non-negotiable.** If any generated test passes before the implementation is written, it means either: (a) the test is logically trivial and tests nothing, or (b) pre-existing code in the repo already implements the behavior. Both cases require inspection — do not proceed to implementation until the root cause is identified.
- **Test method naming convention**: `test_<state>_<transition>_<target>` encodes the complete FSM edge being tested. For example: `test_understand_low_road_understand` (loopback) or `test_readiness_check_high_road_transform`. This naming makes coverage analysis trivial — the method name is the coverage map.
- **Forbidden state tests** use `pytest.raises(ProtocolViolation)` to assert that attempting to enter a forbidden state raises a defined exception. These tests are generated automatically from any state annotated as `forbidden` in the mermaid source (via classDef forbidden).
- **Threshold filter (3+ transitions OR side effects)**: States with fewer than 3 transitions and no side effects are typically pass-through nodes. Generating tests for them adds boilerplate without meaningful coverage. The threshold is configurable via `stillwater.toml: [test_gen] min_transitions = 3`.
- **State coverage metric** counts unique *states* covered by at least one passing test, not line coverage. Line coverage is also computed but is secondary. The 80% state coverage gate is the primary gate. 100% is ideal; 80% is the integration admission threshold.
- **Rung assignment**: Unit tests alone achieve rung 641 (trivial). Integration tests + evidence bundle achieve rung 274177 (irreversible changes). The integration rung is MIN(unit_rung, integration_rung) — if any sub-component is rung 641, the whole module is rung 641.
- **The test file is the contract.** During the Green Gate phase, if a test is failing, fix the implementation — never modify the test method body. The only exception is if the test was generated incorrectly (wrong transition target), in which case the fix must be logged in `test_corrections.json` and reviewed.
- Evidence bundle format: `artifacts/<fsm_name>/tests.json` (pytest JSON report), `coverage.json` (coverage.py JSON output), `red_gate.log` (timestamp + all_failed assertion), `green_gate.log` (timestamp + all_passed assertion), `integration_tests.json` (pytest JSON for integration run).
