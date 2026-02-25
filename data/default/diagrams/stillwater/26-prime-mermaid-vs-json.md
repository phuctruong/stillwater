# Diagram 26: Prime Mermaid vs JSON — Why .prime-mermaid.md Is the Canonical Source of Truth

**Description:** Companion diagram for Paper #36 (Prime Mermaid Primacy). Contrasts graph-native Mermaid structure against JSON's tree constraint, shows the 5 structural advantages of .prime-mermaid.md, enumerates the ban list of artifact categories that must use .prime-mermaid.md as canonical source, and illustrates the 4-section standard format.

---

## Structure Contrast: Graph vs Tree

```mermaid
flowchart LR
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph MERMAID["Mermaid: Graph Structure (native)"]
        direction TB
        MA["INIT"]:::active
        MB["RUNNING"]:::active
        MC["PASS"]:::active
        MD["BLOCKED"]:::gate
        ME["RETRY"]:::portal

        MA -->|"gate_pass"| MB
        MB -->|"evidence_complete"| MC
        MB -->|"gate_failure"| MD
        MD -->|"user_override"| ME
        ME -->|"re-enter"| MB
    end

    subgraph JSON["JSON: Tree Structure (forced)"]
        direction TB
        JR["root object"]
        JS["states: [ ]"]
        JT["transitions: [ ]"]
        JI["initial: INIT"]
        JX["terminal: [ ]"]

        JR --> JS
        JR --> JT
        JR --> JI
        JR --> JX

        JT --> JT1["from: INIT\nto: RUNNING\non: gate_pass"]
        JT --> JT2["from: RUNNING\nto: PASS\non: evidence_complete"]
        JT --> JT3["from: RUNNING\nto: BLOCKED\non: gate_failure"]
    end

    MERMAID -->|"cycles, cross-edges\nnative — visible"| ADVANTAGE["MERMAID WINS\nGraph is the true structure"]:::active
    JSON -->|"no cycles allowed\ncross-refs need workarounds"| DISADVANTAGE["JSON LOSES\nTree lies about graph reality"]:::gate
```

---

## The 5 Structural Advantages of .prime-mermaid.md

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    SOURCE["Source: Why .prime-mermaid.md wins\n(Paper #36 — 5 arguments)"]:::store

    A1["1. Graph-Native\nNodes + directed edges\nSubgraphs, cycles, multi-path\nStructure matches the system\nJSON imposes a tree on a graph"]:::active

    A2["2. Human-Readable\nLegible in any text editor\nNo parser required\nNode names carry semantics\nJSON requires mental simulation"]:::portal

    A3["3. Hashable Without Ambiguity\nSHA-256 over canonical .md\nDeterministic byte sequence\nJSON key order is undefined\n{a:1,b:2} ≠ {b:2,a:1} by hash"]:::gate

    A4["4. Forbidden States Inspectable\nAuditor traces paths with eyes\nSafety check is visual\nJSON requires reachability algorithm\nAudit = run a program"]:::gate

    A5["5. Composable via Subgraphs\nNamed component groupings\nCross-subgraph edges visible\nJSON tree nesting hides relationships\nBidirectional refs break tree"]:::portal

    INVARIANT["Invariant: Diagram changes without\nInvariants change = WARNING\nInvariants are the spec\nDiagram is the visualization"]:::store

    SOURCE --> A1
    SOURCE --> A2
    SOURCE --> A3
    SOURCE --> A4
    SOURCE --> A5
    A1 & A2 & A3 & A4 & A5 --> INVARIANT
```

---

## The Ban List: Artifact Categories That Must Use .prime-mermaid.md

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph BAN["Ban List — JSON/YAML/XML FORBIDDEN as canonical source"]
        direction TB

        B1["Skill Definitions\nBehavioral contracts: states, transitions,\nforbidden behaviors, evidence requirements\nCanonical: .md + Mermaid stateDiagram-v2\nJSON: derived transport only"]:::gate

        B2["State Machines\nVerification rungs, agent lifecycle,\nOAuth3 gate sequence, recipe execution flow\nCanonical: Mermaid stateDiagram-v2\nJSON: secondary artifact for machine parsing"]:::gate

        B3["Configuration\nComponent dependencies, skill packs,\nscope requirements per platform\nCanonical: .prime-mermaid.md + dependency diagram\nYAML: derived deployment artifact"]:::gate

        B4["Scope Registry\nOAuth3 platform.action.resource triples\nRisk levels, step-up requirements\nCanonical: .prime-mermaid.md mindmap/ER diagram\nJSON/YAML: machine validation only"]:::gate

        B5["Agent Orchestration Plans\nSwarm structure: agents, delegation,\nskill packs per agent\nCanonical: Mermaid flowchart/sequence\nJSON: derived transport"]:::gate

        B6["NORTHSTAR Metrics\nFlywheel, belt progression,\nmetric dependency graph\nCanonical: .prime-mermaid.md flowchart\nJSON: reporting export only"]:::gate
    end

    subgraph EXCEPTION["The One Exception: Recipes as Transport"]
        direction TB
        E1["Recipe JSON files ARE acceptable\nThey are wire format — not specification\nRequired: parseable by execution engine\nDiffable + versioned + SHA-256 sidecar"]:::portal
        E2["Canonical recipe SPEC:\n.prime-mermaid.md (state machine + fields)\nJSON schema: derived from spec\nIndividual recipe.json: conforms to schema"]:::portal
        E1 --> E2
    end

    BAN --> EXCEPTION
```

---

## The .prime-mermaid.md Standard: 4-Section Format

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph FORMAT[".prime-mermaid.md — Required Sections"]
        direction TB

        S1["## Overview\nOne paragraph\nWhat system does this describe?\nWhat are the key entities?\nHuman reads this first"]:::portal

        S2["## Diagram\nOne or more Mermaid blocks\nstateDiagram-v2 → state machines\nflowchart → process flows\nsequenceDiagram → protocols\nerDiagram → data relationships\nmindmap → taxonomy"]:::active

        S3["## Invariants\nBullet list of always-true properties\n'State X only reachable via gate Y'\n'No path from START to FORBIDDEN\nwithout CONFIRMATION'\n'Every non-terminal node has outgoing edge'\nThese ARE the specification"]:::gate

        S4["## Derivations\nWhat is mechanically derivable?\n'JSON schema for recipe.json\nderived from Recipe state machine'\n'OAuth3 scope list derived from\nScope registry mindmap'\nOutputs from this canonical source"]:::store

        HASH["SHA-256 Hash\nComputed over entire .prime-mermaid.md\nChange any section = different hash\nStored in: filename.prime-mermaid.md.sha256\nHash is the drift detector"]:::gate

        S1 --> S2 --> S3 --> S4 --> HASH
    end

    subgraph DIAGRAM_TYPES["Mermaid Diagram Type Selection"]
        direction LR
        DT1["stateDiagram-v2\n→ agent FSMs\n→ verification rungs\n→ OAuth3 gate flow"]:::active
        DT2["flowchart\n→ process flows\n→ orchestration plans\n→ dependency graphs"]:::portal
        DT3["sequenceDiagram\n→ interaction protocols\n→ cross-service comms\n→ portal handshakes"]:::portal
        DT4["erDiagram\n→ data models\n→ scope registry\n→ token schema"]:::store
        DT5["mindmap\n→ taxonomy trees\n→ skill families\n→ magic word tiers"]:::store
    end

    FORMAT --> DIAGRAM_TYPES
```

---

## Workflow: Draw the Graph First

```mermaid
flowchart LR
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    W1["1. Write\n.prime-mermaid.md\n(canonical source)"]:::active
    W2["2. Derive\nJSON schema\nfrom spec"]:::portal
    W3["3. Author\nindividual artifact\nconforming to schema"]:::portal
    W4["4. SHA-256\nhash the artifact\nstore sidecar"]:::gate
    W5["5. Drift Detection\nhash change without\ndocumented reason\n= REGRESSION"]:::gate

    W1 -->|"derive schema"| W2
    W2 -->|"conform"| W3
    W3 -->|"hash"| W4
    W4 -->|"monitor"| W5
    W5 -.->|"revert / re-author"| W1

    QUOTE["'Draw the graph first.\nThe JSON is the shadow it casts.'\n— Paper #36"]:::store
```

---

## Source Files

- `papers/36-prime-mermaid-primacy.md` — Foundational paper this diagram accompanies
- `skills/prime-mermaid.md` — Prime Mermaid standard (full skill)
- `skills/prime-safety.md` — Forbidden states as first-class architectural concept
- `papers/03-verification-ladder.md` — Rung system graph structure

---

## Coverage

- Graph vs tree structural contrast with concrete state machine example
- 5 structural advantages of .prime-mermaid.md with JSON failure modes per advantage
- Full ban list: 6 artifact categories that must use .prime-mermaid.md as canonical source
- The one exception: recipe.json as wire format (not specification)
- 4-section .prime-mermaid.md standard (Overview, Diagram, Invariants, Derivations)
- Mermaid diagram type selection guide (5 types, when to use each)
- End-to-end workflow: write canonical → derive schema → author artifact → hash → monitor drift
