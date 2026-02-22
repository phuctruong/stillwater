# Diagram 17: Northstar Reverse Engineering Algorithm

**Description:** The Northstar Reverse Engineering skill (`skills/northstar-reverse.md`) reframes goal pursuit from the naive forward direction (current state → ??? → Northstar) to a backward-chaining approach (Northstar → last 3 steps → chain backward → connect to current → forward plan). The maze insight: starting from the end of a maze and drawing back to the beginning prunes the combinatorial search space because constraints propagate backward. Applied to QA: reverse-engineer what tests must be true for a claim to hold.

---

## Forward vs Reverse Approach

```mermaid
flowchart LR
    subgraph FORWARD["FORWARD (Young Entrepreneur)"]
        direction LR
        CS_F["Current State\nFeb 2026\n50 GitHub stars\n0 projects at rung 65537\n0 community contributors"]
        Q1["???"]
        Q2["???"]
        Q3["???"]
        NS_F["NORTHSTAR\n10,000 stars\n8 projects at 65537\n50 contributors"]
        PROBLEM["PROBLEM:\nCombinatorial explosion\nMany paths, most dead ends\nNo constraints to prune search"]

        CS_F -.->|"step 1"| Q1
        Q1 -.->|"step 2"| Q2
        Q2 -.->|"step 3"| Q3
        Q3 -.->|"step N"| NS_F
        Q1 & Q2 & Q3 --> PROBLEM
    end

    subgraph REVERSE["REVERSE (Wise Entrepreneur)"]
        direction RL
        NS_R["NORTHSTAR\n10,000 stars\n8 projects at 65537\n50 contributors"]
        L3["LAST 3 STEPS\nbefore Northstar"]
        L2["STEP BEFORE THAT"]
        L1["STEP BEFORE THAT"]
        CS_R["Current State\nFeb 2026"]
        ADVANTAGE["ADVANTAGE:\nConstraints propagate backward\nPrunes dead ends automatically\nFirst action becomes obvious"]

        NS_R -->|"what must be\ntrue before this?"| L3
        L3 -->|"what must be\ntrue before this?"| L2
        L2 -->|"what must be\ntrue before this?"| L1
        L1 -->|"chain reaches\ncurrent or reveals gap"| CS_R
        L3 & L2 & L1 --> ADVANTAGE
    end
```

---

## The 5-Step Algorithm

```mermaid
flowchart TD
    STEP1["STEP 1: DEFINE THE SUMMIT\nConcrete, measurable Northstar victory condition\nNot vague ('be successful')\nSpecific + falsifiable\n\nExample: 10,000 GitHub stars + 8 projects at rung 65537\n+ OAuth3 adopted by 1 external platform"]

    STEP1 --> STEP2["STEP 2: LAST 3 STEPS\nWhat MUST be true immediately before the Northstar?\nThink: What conditions make the goal inevitable?\n\nExample:\n- Store has 100+ skills (community flywheel self-sustains)\n- Recipe hit rate >= 80% (economic moat locked)\n- 1 external AI platform ships OAuth3 support"]

    STEP2 --> STEP3["STEP 3: CHAIN BACKWARD\nFor each step, what must be true before it?\nRepeat until you reach present or reveal a gap.\n\nExample (for '100+ skills'):\n  ← Store review process automated (rung 65537)\n  ← 25 skill submissions/mo (from 1,000 paying users)\n  ← Store live with public submission form\n  ← OAuth3 spec published + reference impl working\n  ← solace-browser Phase 1 (LinkedIn recipe) shipped ✅"]

    STEP3 --> STEP4["STEP 4: CONNECT TO CURRENT\nThe backward chain either:\n  (a) Reaches present state → path is clear\n  (b) Reveals a gap → identifies missing prerequisite\n\nExample gap found:\n  'Store review process automated' requires\n  rung 65537 CI/CD → not built yet → THIS is the bottleneck"]

    STEP4 --> STEP5["STEP 5: FORWARD PLAN\nReverse the backward chain → the first action is clear.\nNot 'what should I do?' but 'what is the prerequisite chain?'\n\nExample forward plan:\n  1. Build rung 65537 CI/CD (unblocks Store automation)\n  2. Publish OAuth3 spec (unblocks solace-browser Phase 2)\n  3. Ship Store submission form (unblocks community flywheel)\n  4. Ship 25 skills (unblocks recipe hit rate > 70%)\n  5. Hit 1,000 paying users (flywheel self-sustains)"]

    STEP5 --> SEAL["EXIT: First action is clear.\nNo combinatorial explosion.\nConstraints pruned the search."]

    style STEP1 text-align:left
    style STEP2 text-align:left
    style STEP3 text-align:left
    style STEP4 text-align:left
    style STEP5 text-align:left
```

---

## Applied to Stillwater's NORTHSTAR Metrics

```mermaid
flowchart RL
    subgraph SUMMIT["SUMMIT (End 2026)"]
        direction TB
        N1["10,000 GitHub stars"]
        N2["8 projects at rung 65537"]
        N3["100+ Store skills"]
        N4["80% recipe hit rate"]
        N5["50 community contributors"]
        N6["OAuth3 adopted by 1 external platform"]
    end

    subgraph L3["LAST 3 STEPS before Summit"]
        direction TB
        L3A["Community flywheel\nself-sustaining\n(25+ submissions/mo)"]
        L3B["Economic moat locked\n(recipe hit rate >= 80%)"]
        L3C["External OAuth3 adoption\n(1 platform ships it)"]
    end

    subgraph L2["Before L3"]
        direction TB
        L2A["Stillwater Store live\nwith automated review\n(rung 65537 CI/CD)"]
        L2B["1,000+ paying\nsolaceagi.com users"]
        L2C["OAuth3 v1.0 spec\npublished + reference impl"]
    end

    subgraph L1["Before L2"]
        direction TB
        L1A["Store submission form\nshipped + 25 skills"]
        L1B["solaceagi.com Pro tier\nlive (OAuth3 vault + twin)"]
        L1C["solace-browser OAuth3\ncore module shipped"]
    end

    subgraph NOW["Current State (Feb 2026)"]
        direction TB
        C1["stillwater v1.4.0\nLLM Portal stable ✅"]
        C2["solace-browser Phase 1\nLinkedIn MVP ✅"]
        C3["OAuth3 spec: in progress"]
        C4["Store: not built yet"]
    end

    N1 & N2 & N3 --> L3A
    N4 --> L3B
    N6 --> L3C

    L3A --> L2A
    L3B --> L2B
    L3C --> L2C

    L2A --> L1A
    L2B --> L1B
    L2C --> L1C

    L1A --> C4
    L1B --> C3
    L1C --> C2
    L2A --> C1
```

---

## The Maze Insight: Applied to QA

```mermaid
flowchart TD
    subgraph MAZE["The Maze Insight"]
        START["Entry point\n(current state)"]
        DEAD1["Dead end"]
        DEAD2["Dead end"]
        DEAD3["Dead end"]
        EXIT["Exit\n(Northstar)"]

        START -->|"Forward search\ntries all paths"| DEAD1 & DEAD2 & DEAD3 & PATH_TO_EXIT
        PATH_TO_EXIT --> EXIT

        EXIT -->|"Backward from exit\nonly one path\nleads here"| ONLY_PATH["Only valid path\n(constraints pruned the rest)"]
        ONLY_PATH --> START
    end

    subgraph QA_REVERSE["Applied to QA (Reverse Engineering Evidence)"]
        CLAIM["CLAIM to verify:\n'This skill achieves rung 65537'"]

        CLAIM -->|"Forward: what tests do I write?"| F_EXPLODE["Combinatorial explosion\nof possible tests"]

        CLAIM -->|"Reverse: what MUST be true\nfor this claim to hold?"| R1["MUST: adversarial test passing"]
        R1 --> R2["MUST: security gate passing"]
        R2 --> R3["MUST: behavioral hash stable"]
        R3 --> R4["MUST: seed sweep at rung 274177"]
        R4 --> R5["MUST: red/green test at rung 641"]
        R5 --> R6["First test to write:\nred/green reproduction"]

        R6 --> EVIDENCE["Evidence bundle:\nrepro_red.log + repro_green.log\ntests.json + plan.json\nbehavioral_hash.json"]
    end

    style F_EXPLODE fill:#3a1a1a,stroke:#f85149
    style EVIDENCE fill:#1a3a2a,stroke:#3fb950
```

---

## Northstar Reverse for Each Stillwater Metric

```mermaid
flowchart LR
    subgraph METRIC1["Metric: 10,000 GitHub stars"]
        M1_NOW["50 stars now"] -->|"reverse chain"| M1_PRE3["1,000 paying users\n(social proof)"]
        M1_PRE3 --> M1_PRE2["Viral HN post\n(concrete claims + evidence)"]
        M1_PRE2 --> M1_PRE1["Paper: 'AI without evidence\nis malpractice' published"]
        M1_PRE1 --> M1_FIRST["First action:\nPublish paper on phuc.net"]
    end

    subgraph METRIC2["Metric: 8 projects at rung 65537"]
        M2_NOW["0 projects now"] -->|"reverse chain"| M2_PRE3["Rung 65537 CI/CD\nautomated in 2 repos"]
        M2_PRE3 --> M2_PRE2["Rung 274177 achieved\nin 3 repos"]
        M2_PRE2 --> M2_PRE1["Rung 641 evidence\nbundles in 5 repos"]
        M2_PRE1 --> M2_FIRST["First action:\nBuild rung 641 test harness\nfor stillwater itself"]
    end

    subgraph METRIC3["Metric: 100+ Store skills"]
        M3_NOW["7 combos now"] -->|"reverse chain"| M3_PRE3["25 community submissions/mo"]
        M3_PRE3 --> M3_PRE2["Store live + review automated"]
        M3_PRE2 --> M3_PRE1["OAuth3 enforcer skill\npublished (rung 65537)"]
        M3_PRE1 --> M3_FIRST["First action:\nPublish oauth3-spec skill"]
    end
```

---

## Source Files

- `NORTHSTAR.md` — Northstar metrics, reverse engineering algorithm, content pipeline
- `skills/northstar-reverse.md` — Full northstar-reverse skill specification
- `swarms/northstar-navigator.md` — Sun Tzu persona swarm agent
- `papers/41-northstar-reverse-engineering.md` — Full paper
- `papers/42-reverse-paths.md` — Applied reverse paths for each metric

---

## Coverage

- Forward vs reverse approach comparison (why reverse wins)
- The 5-step algorithm: DEFINE SUMMIT → LAST 3 STEPS → CHAIN BACKWARD → CONNECT TO CURRENT → FORWARD PLAN
- Applied to Stillwater's own NORTHSTAR metrics (stars, rung 65537, Store skills, recipe hit rate, contributors, OAuth3 adoption)
- The maze insight (exit → entry is faster than entry → exit)
- Applied to QA: reverse-engineering what evidence must exist before a claim holds
- Backward constraint propagation as the mechanism that prunes combinatorial explosion
- Per-metric reverse chains showing the first concrete action for each NORTHSTAR goal
