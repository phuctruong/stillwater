# Diagram: QA Audit Process Recipe (Reusable)

## PM Status Summary

```
STATUS SUMMARY
=======================================
DONE/STABLE:    4 steps (SIMULATE, QUESTION, FALSIFY, ANALYZE MAGIC WORDS)
IN-PROGRESS:    1 step  (PROPOSE FIXES — bugs documented, fixes not yet implemented)
PENDING:        2 steps (VERIFY — no coder agent run yet, PERSIST — partial)
=======================================
```

| QA Step | Status | Evidence |
|---------|--------|----------|
| Step 1: SIMULATE | DONE | 20 prompts generated, all run, results documented in `02-edge-case-map.md` |
| Step 2: QUESTION | DONE | 30+ questions generated across 6 personas |
| Step 3: FALSIFY | DONE | False positive/negative tests written for all 8 labels |
| Step 4: ANALYZE MAGIC WORDS | DONE | Seed counts, stop-word collisions, tie-breaking all mapped |
| Step 5: PROPOSE FIXES | IN-PROGRESS | 5 bugs documented with severity; fixes proposed but not coded |
| Step 6: VERIFY | PENDING | No coder agent has implemented + retested fixes |
| Step 7: PERSIST | PENDING | Diagrams + results saved; fix verification artifacts missing |

## The Question-Based QA Pipeline

```mermaid
flowchart TD
    classDef phase fill:#2d7a2d,color:#fff,stroke:#1a4a1a,font-weight:bold
    classDef action fill:#1a5cb5,color:#fff,stroke:#0a3a80
    classDef output fill:#8b44ac,color:#fff,stroke:#5a1a7a
    classDef gate fill:#c0392b,color:#fff,stroke:#7a1a1a

    classDef done fill:#2ecc71,stroke:#27ae60,color:#fff
    classDef inprogress fill:#f39c12,stroke:#e67e22,color:#fff
    classDef pending fill:#e74c3c,stroke:#c0392b,color:#fff
    classDef bug fill:#e74c3c,stroke:#c0392b,color:#fff,stroke-dasharray: 5 5

    START["QA AUDIT START<br/>Load phase config"]:::done

    subgraph SIMULATE ["Step 1: SIMULATE"]
        GEN["Generate 20 prompts<br/>(8 breaking patterns<br/>+ 12 domain-specific)"]:::done
        RUN["Run through engine<br/>Capture: keywords, label,<br/>confidence, LLM called"]:::done
        DOC["Document results<br/>PASS / FAIL / EDGE"]:::done
    end

    subgraph QUESTION ["Step 2: QUESTION"]
        KNUTH["Knuth: Algorithms<br/>complexity, data structures"]:::done
        SCHNEIER["Schneier: Security<br/>adversarial, injection"]:::done
        LISKOV["Liskov: Contracts<br/>pre/post conditions"]:::done
        TURING["Turing: Falsification<br/>what breaks the claim?"]:::done
        DIJKSTRA["Dijkstra: Invariants<br/>loop invariants, termination"]:::done
        BECK["Beck: TDD<br/>missing tests, red tests"]:::done
        QDB["Questions DB<br/>(30+ per phase)"]:::done
    end

    subgraph FALSIFY ["Step 3: FALSIFY"]
        FP["For each label:<br/>false positive test<br/>(IS this label, SHOULDN'T be)"]:::done
        FN["For each label:<br/>false negative test<br/>(ISN'T this label, SHOULD be)"]:::done
    end

    subgraph ANALYZE ["Step 4: ANALYZE MAGIC WORDS"]
        SEEDS["Count seeds per label"]:::done
        STOPS["Map stop_word collisions"]:::done
        TIES["Test tie-breaking"]:::done
        MATRIX["Seed coverage matrix"]:::done
    end

    subgraph FIX ["Step 5: PROPOSE FIXES"]
        BUGS["Document each bug:<br/>severity, root cause,<br/>proposed fix, test case"]:::inprogress
        FIXES["Proposed fixes doc"]:::inprogress
    end

    VERIFY["Step 6: VERIFY<br/>(separate coder agent<br/>implements + retests)"]:::pending

    PERSIST["Step 7: PERSIST<br/>Save all to tests/orchestration/{phase}/"]:::pending

    START --> SIMULATE
    GEN --> RUN --> DOC
    DOC --> QUESTION
    KNUTH --> QDB
    SCHNEIER --> QDB
    LISKOV --> QDB
    TURING --> QDB
    DIJKSTRA --> QDB
    BECK --> QDB
    QDB --> FALSIFY
    FP --> FN
    FN --> ANALYZE
    SEEDS --> MATRIX
    STOPS --> MATRIX
    TIES --> MATRIX
    MATRIX --> FIX
    BUGS --> FIXES
    FIXES --> VERIFY --> PERSIST
```

### Legend

```
DONE (green, solid):           Step completed with evidence on disk
IN-PROGRESS (yellow, solid):   Step partially done — work items remain
PENDING (red, solid):          Step not yet started
```

## The 8 Breaking Patterns (universal for keyword classifiers)

```mermaid
mindmap
  root((8 Breaking<br/>Patterns))
    NULL EDGE
      empty string
      null input
      whitespace only
    LENGTH EDGE
      single char
      < min_length
      single word
    FILTER EDGE
      all stop-words
      all filtered out
      only punctuation
    COUNT EDGE
      repeated words
      duplicate keywords
      frequency inflation
    TIE-BREAK EDGE
      mixed intents
      same confidence
      first-wins bias
    CASE EDGE
      ALL CAPS
      mIxEd CaSe
      Unicode
    FUZZY EDGE
      misspellings
      slang
      abbreviations
    INJECTION EDGE
      greeting + hidden task
      humor + real concern
      multi-sentence mixed
```

## Breaking Pattern Coverage Status

| Pattern | Tested? | Prompts Covering It | Status |
|---------|:-------:|---------------------|--------|
| NULL EDGE | YES | #10 (empty), #14 (all stop words), #20 (punctuation) | DONE — all fall to LLM correctly |
| LENGTH EDGE | YES | #4 ("yo"), #8 ("run"), #16 ("fix") | DONE — BUG-P1-003 documented for < 3 chars |
| FILTER EDGE | YES | #14 ("the the the the"), #6 (stop words removed, task survives) | DONE — filter behavior verified |
| COUNT EDGE | YES | #11 ("hey hey fix fix") | DONE — repeated keywords tested |
| TIE-BREAK EDGE | YES | #3, #5, #18, #19 (mixed intent) | DONE — BUG-P1-001 confirmed |
| CASE EDGE | YES | #12 ("DEPLOY TO PRODUCTION") | DONE — lowercasing handles it |
| FUZZY EDGE | YES | #13 ("plz halp") | DONE — gap documented, deferred to v2 |
| INJECTION EDGE | YES | #3 (greeting + task), #5 (gratitude + task), #18 (humor + task) | DONE — BUG-P1-001 confirmed |

## Application Guide

To apply this recipe to Phase 2 or Phase 3:

1. **Change parameters:**
   - Phase 2: threshold=0.80, labels=21 intents, seed_file=intent-seeds.jsonl
   - Phase 3: threshold=0.90, labels=21 combos, seed_file=execution-seeds.jsonl

2. **Adjust domain prompts:**
   - Phase 2: test that intents classify correctly (bugfix vs feature vs deploy)
   - Phase 3: test that combos match correctly (bugfix-combo vs feature-combo)

3. **Same 8 breaking patterns apply universally**

4. **Cross-phase: test that Phase 1 seed chain is complete**
   - Every Phase 2 label keyword MUST also be a Phase 1 "task" seed
   - Every Phase 3 combo keyword MUST have Phase 1 + Phase 2 coverage

## Famous Persona Question Targets

| Persona | Phase 1 Focus | Phase 2 Focus | Phase 3 Focus |
|---------|--------------|--------------|---------------|
| Knuth | keyword extraction perf | intent disambiguation | combo resolution |
| Schneier | greeting injection | intent spoofing | combo escalation |
| Liskov | gatekeeper contract | intent contract | execution contract |
| Turing | false greeting | false intent | wrong combo |
| Dijkstra | filter invariants | label invariants | cascade invariants |
| Beck | missing Phase 1 tests | missing Phase 2 tests | missing E2E tests |

## Test Coverage

| QA Step | Test Evidence | Exists? | Location |
|---------|--------------|:-------:|----------|
| SIMULATE: 20 prompts generated | Prompt list + expected outcomes | YES | `02-edge-case-map.md` |
| SIMULATE: Engine run results | Actual keywords, label, confidence per prompt | YES | `test_edge_cases.py` output |
| QUESTION: 30+ persona questions | Questions DB document | YES | `questions/phase1-questions.md` |
| FALSIFY: False positive tests | FP test for each of 8 labels | YES | `test_edge_cases.py` |
| FALSIFY: False negative tests | FN test for each of 8 labels | YES | `test_edge_cases.py` |
| ANALYZE: Seed count per label | Seed distribution table | YES | `01-phase1-flow.md` bug hotspots |
| ANALYZE: Stop-word collision map | Stop words vs label triggers | YES | Documented in questions |
| ANALYZE: Tie-break tests | First-wins behavior confirmed | YES | `test_edge_cases.py` |
| PROPOSE FIXES: Bug docs | 5 bugs with severity + proposed fix | YES | `02-edge-case-map.md` bug summary |
| PROPOSE FIXES: Fix implementations | Actual code patches | PENDING | No patches written yet |
| VERIFY: Coder agent re-test | Red-to-green proof per fix | PENDING | No coder agent dispatched |
| PERSIST: All artifacts saved | Diagrams + results + questions | PARTIAL | Diagrams done, fix artifacts missing |
