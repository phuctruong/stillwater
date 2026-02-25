# Diagram 28: Wish + Skill + Recipe Triangle — The Fundamental Execution Model

**Description:** Companion diagram for Paper #46 (Wish+Skill+Recipe Triangle). Shows the three-vertex execution model, the characteristic failure mode for each missing vertex, the completeness check (5 questions), evidence flow through the triangle, and how Combos implement the triangle as pre-validated execution units.

---

## The Triangle: Three Vertices

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph TRIANGLE["Wish + Skill + Recipe Triangle\nMinimal unit of verified execution"]

        WISH["WISH\nUser intent / northstar\n\nCapability statement (1 measurable sentence)\nNon-goals (what this does NOT do)\nForbidden states (must never occur)\nAcceptance tests (verifiable conditions)\nNorthstar link (which long-term goal this advances)\n\nSkill: prime-wishes\nFSM: WISH_SCOPED state gate"]:::active

        SKILL["SKILL\nConstraints / expert contract\n\nDomain knowledge encoded\nForbidden states enumerated\nEvidence requirements specified\nNull vs zero handling rules\nVerification rung declared\n\nExamples: prime-coder (Kent Gate)\nprime-safety (forbidden state list)\nprime-math (no floats in verification)"]:::portal

        RECIPE["RECIPE\nExecution / proven workflow\n\nL1–L5 node graph\n(CPU → heuristic → LLM → tool → judge)\nCheckpoints: halt + verify\nRollback plan per node failure\nArtifact contract: what the recipe produces\nHash sidecar: SHA-256 per recipe.json"]:::gate

        WISH -->|"capability matching\nWish domain must match\nSkill domain"| SKILL
        SKILL -->|"execution planning\nSkill constraints must\nshape Recipe steps"| RECIPE
        RECIPE -->|"evidence closes the loop\nArtifacts must satisfy\nWish acceptance tests"| WISH
    end

    VERIFIED["WISH + SKILL + RECIPE\n= Verified, intentional, expert execution\nOnly configuration achieving all 3 properties\n\n'The triangle is the minimal unit\nof verified execution.\nBelow the triangle: improvisation.'\n— Paper #46"]:::store

    TRIANGLE --> VERIFIED
```

---

## Failure Modes: What Happens When a Vertex Is Missing

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph ONE_VERTEX["Single Vertex — Worst Degradation"]
        direction LR

        W_ONLY["WISH only\n(no Skill, no Recipe)\n\nUnconstrained execution\nAgent fulfills wish by any means\nIncluding unsafe ones\nNo acceptance test → over-executes\nChat-prompt paradigm:\ngoal-directed but unsafe + unreliable"]:::gate

        S_ONLY["SKILL only\n(no Wish, no Recipe)\n\nPurposeless expertise\nConstraints applied to undefined purpose\nSafety gates on a task not defined\nMathematically precise\nStrategically irrelevant"]:::gate

        R_ONLY["RECIPE only\n(no Wish, no Skill)\n\nAimless execution\nProven workflow produces artifacts\nthat nobody wanted\nNo domain expertise for edge cases\nFails silently on boundary conditions"]:::gate
    end

    subgraph TWO_VERTEX["Two Vertices — Partial Function"]
        direction LR

        WS["WISH + SKILL\n(no Recipe)\n\nExpert knowledge of goal\nPath improvised each time\nSafe but inconsistent\nDifferent execution per session\nExpertise unapplied to reproducible workflow"]:::portal

        WR["WISH + RECIPE\n(no Skill)\n\nReliable execution of wrong thing\nProven workflow runs predictably\nNo domain expertise for edge cases\nFails outside safety envelope\nIncorrect on boundary conditions"]:::portal

        SR["SKILL + RECIPE\n(no Wish)\n\nExpert, reliable — no purpose\nBoth safe and proven\nProduces artifacts nobody asked for\nConstraints not connected to user goal\nInverse of aimless recipe case"]:::portal
    end

    ONE_VERTEX --> TWO_VERTEX

    ALL_THREE["WISH + SKILL + RECIPE\nAll 3 present + aligned\n\nVerified execution\nIntentional\nExpert\nReproducible\nEvidence-backed"]:::active

    TWO_VERTEX --> ALL_THREE
```

---

## The Completeness Check: 5 Questions

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    START["Before any AI-assisted execution begins"]:::store

    Q1{"Q1. WISH complete?\nCapability = 1 measurable sentence?\nNon-goals declared?\nForbidden states named?\nAcceptance tests defined?"}:::gate

    Q2{"Q2. SKILL matched?\nSkill exists for this domain?\nSkill domain matches wish domain?\nForbidden states defined?\nVerification gates specified?"}:::gate

    Q3{"Q3. RECIPE present?\nRecipe or combo exists for workflow?\nNode graph defined?\nCheckpoints specified?\nArtifact contract written?"}:::gate

    Q4{"Q4. ALIGNMENT holds?\nSkill constraints match recipe steps?\nRecipe produces artifacts\nthe wish acceptance tests require?\nAll three vertices mutually consistent?"}:::gate

    Q5{"Q5. NORTHSTAR linked?\nWish advances ≥ 1 northstar metric?\nCan you name which one?\n(If no: question whether wish\nbelongs in the backlog)"}:::gate

    STOP["STOP\nRetrieve the missing element\nDo not execute\nMissing vertex = predictable failure"]:::gate

    EXECUTE["EXECUTE\nTriangle is complete\nAll 5 checks passed\nEvidence will be produced"]:::active

    START --> Q1
    Q1 -->|"no"| STOP
    Q1 -->|"yes"| Q2
    Q2 -->|"no"| STOP
    Q2 -->|"yes"| Q3
    Q3 -->|"no"| STOP
    Q3 -->|"yes"| Q4
    Q4 -->|"no"| STOP
    Q4 -->|"yes"| Q5
    Q5 -->|"no"| STOP
    Q5 -->|"yes"| EXECUTE

    subgraph COMPLEXITY["Completeness Check Cost"]
        direction LR
        FAST["Pre-validated Combo\n= O(1) — skip vertex checks\ngo straight to alignment + northstar"]:::active
        SLOW["First-time execution\n= O(n) — validate all 3 vertices\nfrom scratch"]:::portal
        FAST ---|"vs"| SLOW
    end

    EXECUTE --> COMPLEXITY
```

---

## Evidence Flow Through the Triangle

```mermaid
flowchart LR
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph DISPATCH["At Dispatch Time (phuc-orchestration)"]
        direction TB
        D1["Skill pack required\n(SKILL_LESS_DISPATCH → BLOCKED)"]:::gate
        D2["CNF capsule required\n(FORGOTTEN_CAPSULE → BLOCKED)\nCNF capsule = full wish context"]:::gate
        D1 & D2 --> D3["Dispatch permitted"]:::active
    end

    subgraph EXECUTION["At Execution Time (prime-wishes)"]
        direction TB
        E1["Wish must reach\nWISH_SCOPED state"]:::portal
        E2["WISH_WITHOUT_NONGOALS → BLOCKED"]:::gate
        E3["AMBIGUOUS_WISH → BLOCKED"]:::gate
        E1 --> E4["Wish validated"]:::active
        E2 & E3 -.->|"forbidden states\nblock progress"| E1
    end

    subgraph VERIFICATION["At Verification Time (prime-coder)"]
        direction TB
        V1["Recipe artifact contract\nspecifies required evidence"]:::gate
        V2["Lane A artifacts required:\ntests.json + PATCH_DIFF"]:::portal
        V3["UNWITNESSED_PASS → BLOCKED\n(no claim of success\nwithout artifact evidence)"]:::gate
        V1 --> V2
        V3 -.->|"blocked"| V2
        V2 --> V4["Rung achieved"]:::active
    end

    DISPATCH -->|"wish + skill delivered\nto sub-agent"| EXECUTION
    EXECUTION -->|"wish validated\nexecution begins"| VERIFICATION
    VERIFICATION -->|"evidence closes loop\nartifacts satisfy\nwish acceptance tests"| DONE["Triangle complete\nVerified execution\nEvidence bundle sealed"]:::store

    DONE -.->|"northstar metric advances\ntriangle crystallizes\nas Combo for reuse"| COMBO["Combo\n(pre-validated triangle)"]:::active
```

---

## Combos: Canonical Triangle Implementation

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph COMBO_STRUCT["Combo File Structure (combos/*.md)"]
        direction TB
        CS1["W_ block\nWish definition:\ncapability, non-goals,\nforbidden states, acceptance tests"]:::active
        CS2["Skill pack declaration\nWhich skills govern this combo's execution\n(prime-safety always first)"]:::portal
        CS3["R_ block\nRecipe: L1–L5 node graph\ncheckpoints, artifact contract"]:::gate
        CS1 --> CS2 --> CS3
    end

    subgraph EXAMPLES["Existing Combo Instances"]
        direction TB

        BF["combos/bugfix.md\n\nWISH: W_BUGFIX_PR\nred repro fails → green repro passes\nPR bundle produced\n\nSKILL: prime-coder + prime-safety\nKent Gate is hard\nno patch without repro\nnever weaken tests\n\nRECIPE: R_BUGFIX_PR\nNode 1: intake\nNode 3: RED run mandatory\nNode 6: apply + GREEN run\nNode 9: final seal"]:::portal

        PL["combos/plan.md\n\nWISH: W_MODE_SPLIT\nstrict separation:\nplanning vs executing\n\nSKILL: prime-forecast\nDREAM→FORECAST→DECIDE\n→ACT→VERIFY required\n\nRECIPE: R_PLAN_EXEC\nintent classifier\n→ plan compiler\n→ mode enforcer\n→ promotion gate"]:::portal
    end

    subgraph ECOSYSTEM_VALUE["Why Combos Are Capital"]
        direction TB
        EV1["Each combo = 1 pre-validated triangle\n= 1 piece of crystallized expertise\n= intent + constraints + execution path\nvalidated together, available for reuse"]:::store
        EV2["Ecosystem value scales with\nnumber + quality of combos\nBuilding combos = building the ecosystem\n100 combos = 100 verified execution units"]:::store
        EV3["Reuse cost:\nO(1) for pre-validated combos\nSkip vertex checks\nGo straight to alignment + northstar"]:::active
        EV1 --> EV2 --> EV3
    end

    COMBO_STRUCT --> EXAMPLES
    EXAMPLES --> ECOSYSTEM_VALUE
```

---

## Source Files

- `papers/46-wish-skill-recipe-triangle.md` — Foundational paper this diagram accompanies
- `combos/bugfix.md` — Bugfix combo (W_BUGFIX_PR + prime-coder + R_BUGFIX_PR)
- `combos/plan.md` — Plan combo (W_MODE_SPLIT + prime-forecast + R_PLAN_EXEC)
- `skills/prime-wishes.md` — Wish completeness enforcement
- `skills/prime-coder.md` — Evidence gate + UNWITNESSED_PASS forbidden state
- `skills/phuc-orchestration.md` — SKILL_LESS_DISPATCH + FORGOTTEN_CAPSULE enforcement
- `papers/49-three-pillars-software-5-kung-fu.md` — Triangle Law as LEC convention

---

## Coverage

- Triangle diagram with 3 vertices (WISH, SKILL, RECIPE) and 3 directed edges
- Each vertex: key properties, required fields, governing skill
- All 7 vertex combinations and their characteristic failure modes
- Completeness check: 5 questions with stop/execute outcomes
- O(1) vs O(n) complexity for pre-validated combos vs first-time executions
- Evidence flow: dispatch → execution → verification → evidence bundle
- 3 forbidden states that block progression (SKILL_LESS_DISPATCH, AMBIGUOUS_WISH, UNWITNESSED_PASS)
- Combo structure (W_ + skill pack + R_)
- Two concrete combo examples (bugfix + plan) with all three vertices shown
- Ecosystem capital argument: combos = crystallized expertise
