# Diagram 27: Portal Architecture — Prime Compression as BIC Boundary Crossing

**Description:** Companion diagram for Paper #45 (Prime Compression / Magic Words). Shows the source BIC → portal → target BIC compression flow, the 4-tier semantic prime hierarchy, the 97.4% compression ratio mechanism, and the 5 dimensions that make prime words compression-superior to any other vocabulary.

---

## BIC-to-BIC Portal: The Compression Gateway

```mermaid
flowchart LR
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph SOURCE_BIC["Source BIC — High-Entropy Context"]
        direction TB
        SB1["Raw project session\n115.6 KB\nCode, docs, context,\ndecisions, jargon"]:::gate
        SB2["Tier 3 domain words\nhighly composite\nlow portability\nrequires context to decode"]:::gate
        SB3["Tier 2 compound words\n3+ prime factors\ndomain-specific\nredundant overlap"]:::gate
        SB1 --> SB2 --> SB3
    end

    subgraph PORTAL["Portal — Prime Magic Word Extraction"]
        direction TB
        P1["Bayesian Handshake\nP(E|BubbleA) ≈ P(E|BubbleB)\nmust hold before transfer\n(precondition for lossless compression)"]:::store
        P2["Extract prime-word summary\n15 trunk words (Tier 0)\n15 branch words (Tier 1)\n70 leaf words (Tier 2)\n= 100 classified magic words"]:::portal
        P3["Compression ratio:\n115.6 KB → 3 KB\n= 97.4% compression\nnear-zero semantic loss"]:::active
        P4["Send the key\nLet target reconstruct the lock\n(target activates pre-loaded conventions\nnot just receives a file)"]:::portal
        P1 --> P2 --> P3 --> P4
    end

    subgraph TARGET_BIC["Target BIC — Dense Convention Network"]
        direction TB
        T1["Stillwater skill system\nskills/ + recipes/ + swarms/\npre-loaded conventions\nfor every trunk word"]:::active
        T2["Convention activation\n'coherence' → activates\nentire coherence framework:\nrelationships, tests, implications"]:::active
        T3["Reconstruction\nfull context rebuilt from\n3 KB prime summary +\npre-existing skill conventions"]:::active
        T1 --> T2 --> T3
    end

    SOURCE_BIC -->|"high entropy\nhigh cost per bit"| PORTAL
    PORTAL -->|"prime-word summary\n3 KB"| TARGET_BIC
    TARGET_BIC -.->|"GLOW verification:\nsemantic preservation ratio\n= GLOW(compressed)/GLOW(original)\ntarget ≥ 0.95"| PORTAL
```

---

## The 4-Tier Prime Hierarchy

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph TIER0["Tier 0 — Semantic Primes (15 words)"]
        direction LR
        T0A["coherence"]:::active
        T0B["symmetry"]:::active
        T0C["asymmetry"]:::active
        T0D["constraint"]:::active
        T0E["compression"]:::active
        T0F["signal"]:::active
        T0G["alignment"]:::active
        T0H["equilibrium"]:::active
        T0I["causality"]:::active
        T0J["entropy"]:::active
        T0K["emergence"]:::active
        T0L["integrity"]:::active
        T0M["perspective"]:::active
        T0N["boundary"]:::active
        T0O["reversibility"]:::active
    end

    T0_NOTE["Irreducible: cannot be defined\nwithout circular reference\nStable across all cultures and eras\nSemantic bedrock"]:::active

    subgraph TIER1["Tier 1 — Products of 2 Primes (15 words)"]
        direction LR
        T1A["verification\n= signal × integrity"]:::portal
        T1B["governance\n= constraint × alignment"]:::portal
        T1C["trust\n= coherence × reversibility"]:::portal
        T1D["feedback\n= causality × signal"]:::portal
        T1E["resilience\n= equilibrium × boundary"]:::portal
    end

    subgraph TIER2["Tier 2 — Products of 3+ Primes (70 words)"]
        direction LR
        T2A["authentication\n= integrity × boundary × trust × causality"]:::gate
        T2B["orchestration\n= alignment × emergence × constraint × signal"]:::gate
        T2C["recipe replay\n= causality × compression × reversibility × signal"]:::gate
    end

    subgraph TIER3["Tier 3 — Highly Composite Domain Words"]
        direction LR
        T3A["OAuth3-vault\nboundary × integrity × trust\n× constraint × reversibility × causality\nMaximum prime factors\nMinimum portability"]:::store
        T3B["stillwater-rung-65537\nAll pillars combined\nEcosystem-specific meaning\nRequires convention context to decode"]:::store
    end

    TIER0 --> TIER1 --> TIER2 --> TIER3

    COMPRESSION_RULE["Compression Rule:\nTier 3 → Tier 0 = maximum compression\nTier 0 → Tier 3 = maximum redundancy\nCompression ratio = prime-word content / composite-word content"]:::active

    TIER3 --> COMPRESSION_RULE

    T0A & T0B & T0C & T0D & T0E --> T0_NOTE
```

---

## The 5 Compression Advantages of Prime Magic Words

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    ROOT["Why prime words compress better\nthan any other vocabulary\n(Paper #45 — 5 dimensions)"]:::store

    D1["1. Minimum Entropy\nPrime words have precise, stable,\nuniversally-agreed meaning\n= low entropy per symbol\nHigh-entropy jargon requires context to decode\nPrime words decode instantly\nBasis vocabulary = lowest-entropy symbols"]:::active

    D2["2. Semantic Orthogonality\nMathematical primes: mutually coprime\nPrime words: semantically orthogonal\n'coherence' and 'entropy' describe\ndifferent dimensions — no overlap\nCombination = genuine double coverage\nComposite words violate orthogonality\n(technical debt ≈ code quality → redundant)"]:::portal

    D3["3. Stable Reference\nMathematical primes: unchanged since antiquity\nPrime words: civilization load-bearing\n'boundary', 'causality', 'integrity'\nappear in every culture, every era\nCompressed form using prime words\ndoes not expire"]:::gate

    D4["4. Hierarchical Expressiveness\nPrimes compose into all integers\nPrime words compose into all concepts\n15 trunk words → every domain concept reachable\nCompleteness is the design invariant\nDeeper hierarchy = higher domain specificity"]:::portal

    D5["5. Cross-Domain Transfer\n2 × 3 × 5 valid in number theory,\ncryptography, music, chemistry\nPrime words valid across all domains\n'coherence' same meaning in codebase,\nlegal argument, business strategy\nPrime form = domain-independent compressed key"]:::active

    ROOT --> D1 & D2 & D3 & D4 & D5

    THEOREM["Fundamental Theorem of Semantics (proposed):\nEvery concept C = P₁ × P₂ × ... × Pₙ\nwhere each Pᵢ is an irreducible semantic prime\nAnalog: Fundamental Theorem of Arithmetic\nEvery integer = unique product of primes"]:::store

    D1 & D2 & D3 & D4 & D5 --> THEOREM
```

---

## Portal Protocol: Stillwater Implementation

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph IMPL["Three Interlocking Mechanisms"]
        direction TB

        subgraph MW["phuc-magic-words skill\n(Magic Words Database)"]
            MW1["4-tier tree: 100 classified words"]:::active
            MW2["Navigation: trunk-first rule\n(prime-first factorization)"]:::active
            MW3["Loading: branches relevant to query only"]:::active
            MW4["Measurement: track compression ratio\nafter each load operation"]:::active
        end

        subgraph PP["phuc-portals skill\n(Portal Protocol)"]
            PP1["1. Identify source + target BICs"]:::portal
            PP2["2. Assess target convention density\n(how many of 100 magic words known?)"]:::portal
            PP3["3. Extract prime-word summary\nfrom source context"]:::portal
            PP4["4. Transfer through portal"]:::portal
            PP5["5. Verify target can reconstruct\nessential meaning"]:::portal
            PP1 --> PP2 --> PP3 --> PP4 --> PP5
        end

        subgraph TL["phuc-triangle-law skill\n(Triangle Verification)"]
            TL1["REMIND: state the prime-word summary"]:::gate
            TL2["VERIFY: confirm target BIC reconstructs meaning"]:::gate
            TL3["ACKNOWLEDGE: commit compressed form\nas official context representation"]:::gate
            TL1 --> TL2 --> TL3
            SKIP_WARN["Skipping VERIFY =\n'theater of compliance'\nappearance without substance"]:::gate
        end
    end

    subgraph MEASURE["Semantic Preservation Measurement"]
        direction LR
        M1["Semantic preservation ratio\n= GLOW(compressed) / GLOW(original)"]:::store
        M2["Ratio ≥ 0.95\n= near-lossless\nprime compression achieved"]:::active
        M3["Ratio < 0.80\n= semantic loss\ncritical content removed\nredo compression"]:::gate
        M1 --> M2
        M1 --> M3
    end

    MW --> PP
    PP --> TL
    TL --> MEASURE
```

---

## Source Files

- `papers/45-prime-compression-magic-words.md` — Foundational paper this diagram accompanies
- `skills/phuc-magic-words.md` — 4-tier magic word database
- `skills/phuc-portals.md` — BIC portal protocol + Bayesian Handshake
- `skills/phuc-triangle-law.md` — REMIND → VERIFY → ACKNOWLEDGE for compressed contexts
- `skills/prime-llm-portal.md` — LLM-to-LLM portal instantiation
- `papers/36-prime-mermaid-primacy.md` — Related: canonical representation theory

---

## Coverage

- Source BIC → Portal → Target BIC flow with concrete 115.6 KB → 3 KB numbers
- 4-tier semantic prime hierarchy (Tier 0: 15 primes → Tier 1: 15 branches → Tier 2: 70 leaves → Tier 3: domain)
- Tier 0 complete: all 15 prime words listed
- Tier 1 examples with prime factorization notation
- Tier 2 and Tier 3 examples showing increasing composite complexity
- 5 compression advantage dimensions with failure mode per dimension
- Fundamental Theorem of Semantics formal statement
- Bayesian Handshake precondition for lossless compression
- Three interlocking mechanisms: magic-words + portals + triangle-law
- GLOW-based semantic preservation ratio with pass/fail thresholds
