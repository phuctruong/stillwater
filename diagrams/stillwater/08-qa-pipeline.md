# Diagram 08 — QA Pipeline

The unified QA pipeline across all three pillars: Questions, Unit Tests, and Mermaid Diagrams.
Each pillar audits the system from a different angle. All three converge into a unified gap
report that determines rung achievement.

The decoupled verification principle (CoVe) is central: the agent that generates questions
must differ structurally from the agent that scores them. Self-confirmation bias is the primary
root cause of false GREEN verdicts.

---

## Pillar 1: Question-Based QA (CoVe Protocol)

```mermaid
flowchart TD
    SCOPE([Audit Scope Defined\nproject + feature + rung_target]) --> QGEN

    subgraph QGEN["PILLAR 1A: Question Generation (qa-questioner agent)"]
        QG1[Generate adversarial questions\ntag each with GLOW dimension\nG / L / O / W]
        QG2[Specify expected evidence type\nper question]
        QG3[Produce qa_questions.json\nnumbered + versioned]
        QG1 --> QG2 --> QG3
    end

    QG3 -->|"DECOUPLE:\nquestioner stops;\nonly questions passed forward"| QSCORE

    subgraph QSCORE["PILLAR 1B: Scoring (qa-scorer agent — different from questioner)"]
        QS1[Read qa_questions.json only\nnot questioner reasoning]
        QS2[Read actual repo / project state\nnot memory]
        QS3{Assign verdict per question}
        QS4A["GREEN:\nevidence = executable\nfalsifier defined"]
        QS4B["YELLOW:\nevidence = prose or partial\nor integration not tested"]
        QS4C["RED:\ncommand fails\nfile missing\ntest fails"]
        QS5[Define falsifier for every GREEN\nfalsifier_status = UNTESTED initially]
        QS6[Produce qa_scorecard.json\n+ qa_falsifiers.json]
        QS1 --> QS2 --> QS3
        QS3 --> QS4A
        QS3 --> QS4B
        QS3 --> QS4C
        QS4A --> QS5 --> QS6
        QS4B --> QS6
        QS4C --> QS6
    end

    QS6 --> FALSIFIER_TEST

    subgraph FALSIFIER_TEST["PILLAR 1C: Falsifier Testing (rung 274177+)"]
        FT1{rung_target ≥ 274177?}
        FT2[Test each falsifier\nfalsifier_status → TESTED_DOES_NOT_TRIGGER\nor TRIGGERED_NOW_RED]
        FT3{Any falsifier triggered?}
        FT4([BLOCKED: claim was wrong\nGREEN → RED])
        FT5[All falsifiers hold\nproceed to integration probes]
        FT1 -- YES --> FT2 --> FT3
        FT3 -- YES --> FT4
        FT3 -- NO --> FT5
        FT1 -- NO\nrung 641 --> FT5
    end

    classDef passNode fill:#1a7a4a,color:#fff,stroke:#0f4f2f,font-weight:bold
    classDef blockedNode fill:#9b2335,color:#fff,stroke:#6b1520,font-weight:bold
    classDef agentNode fill:#2c4f8c,color:#fff,stroke:#1a3060
    classDef decoupleNode fill:#4a3d6b,color:#e0d4ff,stroke:#2e2345,font-style:italic

    class FT4 blockedNode
    class FT5 passNode
```

---

## Pillar 2: Unit Test QA

```mermaid
flowchart TD
    TGEN[Persona-driven test authoring\ne.g. linus for CLI\nschneier for security\nknuth for algorithms] --> TWRITE

    subgraph TWRITE["Test Writing (Coder + prime-coder skill)"]
        TW1[Write repro_red.log\ntest fails BEFORE patch]
        TW2[Apply patch / implement feature]
        TW3[Write repro_green.log\ntest passes AFTER patch]
        TW1 --> TW2 --> TW3
    end

    TWRITE --> TEXEC

    subgraph TEXEC["Test Execution (pytest)"]
        TE1[Run pytest with deterministic seed]
        TE2[Capture exit_code, pass_count, fail_count]
        TE3[Write tests.json]
        TE4{exit_code == 0\npass_count > 0\nfail_count == 0?}
        TE5([BLOCKED: tests failing])
        TE6[Compute behavior_hash\nsha256 over normalized output\nfor seeds 42, 137, 9001]
        TE1 --> TE2 --> TE3 --> TE4
        TE4 -- NO --> TE5
        TE4 -- YES --> TE6
    end

    TE6 --> TCOV

    subgraph TCOV["Coverage Assessment"]
        TC1[Measure line + branch coverage]
        TC2{Coverage meets rung threshold?}
        TC3([BLOCKED: coverage gap])
        TC4[Integration boundary tests\ncross-project handoffs]
        TC2 -- NO --> TC3
        TC2 -- YES --> TC4
    end

    classDef passNode fill:#1a7a4a,color:#fff,stroke:#0f4f2f,font-weight:bold
    classDef blockedNode fill:#9b2335,color:#fff,stroke:#6b1520,font-weight:bold
    class TE5,TC3 blockedNode
    class TE6,TC4 passNode
```

---

## Pillar 3: Mermaid Diagram QA

```mermaid
flowchart TD
    DGEN[Generate structural diagrams\nstate machines, flows, sequences] --> DVAL

    subgraph DVAL["Diagram Validation"]
        DV1[Parse mermaid syntax\ncheck for parse errors]
        DV2[Cross-validate against\nactual source code / state machine]
        DV3{States in diagram\nmatch states in code?}
        DV4([BLOCKED: diagram drifted from code])
        DV5[Check for forbidden states\nare unreachable states listed?]
        DV6[Compute SHA-256 over .mmd bytes\nwrite .sha256 file]
        DV1 --> DV2 --> DV3
        DV3 -- NO --> DV4
        DV3 -- YES --> DV5 --> DV6
    end

    DV6 --> DCOMP

    subgraph DCOMP["Completeness Check"]
        DC1{All system components covered?}
        DC2[Identify coverage gaps\nnodes present in code but not diagram]
        DC3[Update diagrams to close gaps]
        DC1 -- gaps found --> DC2 --> DC3 --> DV1
        DC1 -- complete --> DPILLAR_PASS([Diagram pillar PASS\nsha256 stable])
    end

    classDef passNode fill:#1a7a4a,color:#fff,stroke:#0f4f2f,font-weight:bold
    classDef blockedNode fill:#9b2335,color:#fff,stroke:#6b1520,font-weight:bold
    class DV4 blockedNode
    class DPILLAR_PASS passNode
```

---

## Unified Gap Report (All 3 Pillars Converge)

```mermaid
flowchart TD
    P1_OUT["Pillar 1 Output\nqa_scorecard.json\nqa_falsifiers.json\nqa_integration_probes.json"]
    P2_OUT["Pillar 2 Output\ntests.json\nbehavior_hash.txt\nrepro_red.log\nrepro_green.log"]
    P3_OUT["Pillar 3 Output\nstate.mmd\nstate.sha256\nstate.prime-mermaid.md"]

    P1_OUT --> GAP_REPORT
    P2_OUT --> GAP_REPORT
    P3_OUT --> GAP_REPORT

    subgraph GAP_REPORT["Unified Gap Report: qa_gap_report.md"]
        GR1["## Summary\nGREEN / YELLOW / RED counts"]
        GR2["## GREEN Claims\nwith falsifiers"]
        GR3["## YELLOW Gaps\nwith remediation path"]
        GR4["## RED Failures\nwith root cause"]
        GR5["## Integration Probe Results\ncross-boundary probes"]
        GR6["## Rung Assessment\nrung_achieved = MIN(all contributing agents)"]
        GR1 --> GR2 --> GR3 --> GR4 --> GR5 --> GR6
    end

    GAP_REPORT --> RUNG_GATE

    subgraph RUNG_GATE["Rung Gate"]
        RG1{rung_target 641?}
        RG2{rung_target 274177?}
        RG3{rung_target 65537?}
        RG641_REQ["questions formulated\nverdicts with evidence\nno GREEN without falsifier\ndecoupled agents"]
        RG274_REQ["+ all falsifiers tested\n+ integration probes run\n+ adversarial review"]
        RG65537_REQ["+ independent reproduction\n+ all real services (no mocks)\n+ human/judge approval"]
        EXIT_PASS([EXIT PASS])
        EXIT_BLOCKED([EXIT BLOCKED])
        RG1 -- YES --> RG641_REQ
        RG2 -- YES --> RG274_REQ
        RG3 -- YES --> RG65537_REQ
        RG641_REQ --> EXIT_PASS
        RG274_REQ --> EXIT_PASS
        RG65537_REQ --> EXIT_PASS
    end

    classDef passNode fill:#1a7a4a,color:#fff,stroke:#0f4f2f,font-weight:bold
    classDef blockedNode fill:#9b2335,color:#fff,stroke:#6b1520,font-weight:bold
    classDef pillarNode fill:#2c4f8c,color:#fff,stroke:#1a3060
    class EXIT_PASS passNode
    class EXIT_BLOCKED blockedNode
    class P1_OUT,P2_OUT,P3_OUT pillarNode
```

---

## Source Files

- `/home/phuc/projects/stillwater/skills/phuc-qa.md` — full QA skill: state machine, decoupled verification (CoVe), falsifier requirement, integration probes, evidence schema, GLOW taxonomy, ecosystem boundaries
- `/home/phuc/projects/stillwater/skills/prime-coder.md` — red-green gate, evidence bundle requirements
- `/home/phuc/projects/stillwater/skills/prime-mermaid.md` — diagram-as-code standard, canonical format, SHA-256 identity
- `/home/phuc/projects/stillwater/store/rung_validator.py` — rung validation logic

## Coverage

- All 3 QA pillars: Questions, Unit Tests, Mermaid Diagrams
- CoVe decoupling principle: qa-questioner and qa-scorer are structurally separate agents
- GLOW dimension tagging on questions (G/L/O/W)
- GREEN/YELLOW/RED verdict system with default-YELLOW rule
- Falsifier requirement: every GREEN claim must have a defined falsifier
- 3-seed behavior hash protocol (seeds 42, 137, 9001)
- Integration boundary probes (cross-project handoffs)
- Unified gap report structure (all sections enumerated)
- Rung requirements per tier
- Forbidden states: SELF_CONFIRMED_GREEN, MOCK_AS_EVIDENCE, PROSE_AS_PROOF, FALSIFIER_SKIPPED
