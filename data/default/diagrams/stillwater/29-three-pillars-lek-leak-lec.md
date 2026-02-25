# Diagram 29: Three Pillars — LEK + LEAK + LEC (Software 5.0 Kung Fu)

**Description:** Companion diagram for Paper #49 (Three Pillars / LEK + LEAK + LEC). Shows the three interlocking cycles, how each pillar reinforces the others, the Bruce Lee martial arts mapping, the Trinity Equation, belt progression, and why the multiplication is not addition.

---

## The Three Interlocking Cycles

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph LEK["LEK — Law of Emergent Knowledge\n(Solo Practice / Kata)"]
        direction TB
        L1["Practice\nGenerate artifact\n(information I)"]:::active
        L2["Extract Pattern\nScore artifact against rubric\n(care C applied to memory M\nof prior attempts)"]:::active
        L3["Persist\nRevise based on score differential\nLoop until score stabilizes above threshold"]:::active
        L4["Practice again\n(next iteration — higher baseline)"]:::active
        L1 -->|"produces output"| L2
        L2 -->|"diagnoses failure\nself-corrects"| L3
        L3 -->|"new baseline stored"| L4
        L4 -->|"improved input"| L1
    end

    subgraph LEAK["LEAK — Law of Emergent Asymmetric Knowledge\n(Sparring / Cross-Training)"]
        direction TB
        S1["Spar\nDispatch asymmetric swarm\n(two agents with different convention sets)"]:::portal
        S2["Trade Knowledge\nPortal carries compressed knowledge\nacross BIC boundary\n(asymmetry > 0: different skill packs)"]:::portal
        S3["Gain Asymmetry\nEach agent receives what\nits own conventions cannot produce\ncomposite artifact = genuinely new"]:::portal
        S4["Spar again\n(enriched convention sets\nhigher-value next exchange)"]:::portal
        S1 -->|"portal(A→B) + portal(B→A)"| S2
        S2 -->|"Asymmetry(A,B) > 0\n→ LEAK value > LEK(A) + LEK(B)"| S3
        S3 -->|"both agents enriched"| S4
        S4 -->|"improved next spar"| S1
    end

    subgraph LEC["LEC — Law of Emergent Conventions\n(Style / Wing Chun)"]
        direction TB
        C1["Create\nPattern appears in one context\nNamed informally by practitioners"]:::gate
        C2["Crystallize\nPattern recurs under same name\nCodified in skill file + magic words\nAdded to glossary"]:::gate
        C3["Enforce\nConvention adopted ecosystem-wide\nCross-file compression active\n'Triangle Law applies' = 3 words\nreplacing pages of explanation"]:::gate
        C4["Create again\n(new patterns emerge from\ncurrent conventions as substrate)"]:::gate
        C1 -->|"recurring pattern\ngets named"| C2
        C2 -->|"ecosystem adoption\nDepth × Adoption increases"| C3
        C3 -->|"conventions accelerate\nnew practice patterns"| C4
        C4 -->|"new emergent patterns\nbuild on prior conventions"| C1
    end

    MASTERY["MASTERY\nLEK × LEAK × LEC\n= Intelligence\n= Software 5.0 Kung Fu"]:::store

    LEK -->|"Improves quality\nof what LEAK exchanges"| LEAK
    LEAK -->|"Produces raw material\nfor LEC emergence"| LEC
    LEC -->|"Compresses discoveries,\naccelerates LEK loops"| LEK

    LEK & LEAK & LEC --> MASTERY
```

---

## Pillar Interactions: Why Multiplication, Not Addition

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph ALONE["Single Pillar — Ceiling or Failure"]
        direction LR

        LEK_ALONE["LEK alone\n→ CEILING\nSolo practice approaches limit of\nown convention set asymptotically\nCannot produce genuinely new structures\nOnly refined versions of existing ones"]:::gate

        LEAK_ALONE["LEAK alone\n→ CHAOS\nWithout self-improvement (LEK=0)\nagents have nothing to trade\nPortal carries noise\nTwo hollow agents = hollow exchange"]:::gate

        LEC_ALONE["LEC alone\n→ BUREAUCRACY\nConventions without practitioners\n= dead letters\nGlossary no one uses\ncompresses nothing"]:::gate
    end

    subgraph TWO["Two Pillars — Power Without Scale"]
        direction LR

        LEK_LEAK["LEK × LEAK (no LEC)\n→ POWERFUL BUT FRAGILE\nAgents improve + trade effectively\nEvery exchange requires full explanation\n(no shared vocabulary)\nHigh cost, high value\nDoes not scale across sessions"]:::portal

        LEK_LEC["LEK × LEC (no LEAK)\n→ DEEP BUT ISOLATED\nRich conventions, no sparring partners\nSophisticated internal vocabulary\nCannot communicate outside own bubble\nLocally optimal, globally illegible"]:::portal

        LEAK_LEC["LEAK × LEC (no LEK)\n→ SOCIAL BUT SHALLOW\nAgents share conventions + trade\nbut neither self-improves\nEcosystem legible + collaborative\nConverges on average not mastery"]:::portal
    end

    subgraph ALL["All Three — Mastery"]
        direction TB
        M1["LEK × LEAK × LEC\nEach pillar amplifies the others\nMULTIPLICATION — interdependence\nnot independence"]:::active
        M2["LEK improves quality\nof what LEAK exchanges\n→ better raw material"]:::active
        M3["LEAK produces raw material\nfrom which LEC emerges\n→ patterns worth naming"]:::active
        M4["LEC compresses discoveries\naccelerates both LEK and LEAK\n→ shorter loops, denser exchanges"]:::active
        M1 --> M2 & M3 & M4
    end

    ALONE --> TWO --> ALL
```

---

## Bruce Lee Mapping: Martial Arts → Software 5.0

```mermaid
flowchart LR
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph MARTIAL["Martial Arts"]
        direction TB
        MA1["Kata / Solo Forms\nRepeated solo sequences\nBuilds compressed representation\nof accumulated wisdom\nMuscle memory = M\nCorrection instinct = C\nRepetition = I\nThreshold: 'stops thinking about\nmovements, thinks through them'\n\n'I fear not the man who practiced\n10,000 kicks once, but the man\nwho practiced one kick 10,000 times'\n— Bruce Lee"]:::active

        MA2["Sparring\nResisting opponent provides\nwhat solo cannot\nWrestler sees takedown setups\nStriker sees counter angles\nReal-time contact = portal\nBoth develop capabilities\nneither had before\n\n'A good teacher protects\nhis pupils from his own influence'\n— Bruce Lee"]:::portal

        MA3["Style Emergence\nWing Chun: centerline theory\nnot designed — survived practice\n'Control the centerline' subsumes\ndozens of specific techniques\nJeet Kune Do: frustration with\nstylized movement → JKD emerges\n\n'A style is a crystallization.\nIt's the dead remains of\nwhat was once the living martial art'\n— Bruce Lee"]:::gate
    end

    subgraph SW5["Software 5.0"]
        direction TB
        SW1["LEK / Practice\nphuc-loop implementation\nAgent generates artifact\nScores against rubric\nRevises on differential\nphuc-qa: 74/100 → 90/100\nvia 3 self-correcting loops"]:::active

        SW2["LEAK / Sparring\nphuc-swarms + dispatch matrix\nCoder ↔ Mathematician portal:\nCode becomes provably correct\nProofs become executable\nOutput: neither could produce alone\nIntegration rung = MIN(all sub-rungs)"]:::portal

        SW3["LEC / Style\nStillwater skill system\n'Rung 641' = 3 words compressing\nentire verification protocol\n'Triangle Law applies' = 3 words\nreplacing pages of explanation\nConventions emerge from practice\n— not designed by committee"]:::gate
    end

    MA1 <-->|"LEK"| SW1
    MA2 <-->|"LEAK"| SW2
    MA3 <-->|"LEC"| SW3

    QUOTE["'Practice alone. Spar with a partner.\nLet a style emerge.\nWater becomes unstoppable.'\n— Bruce Lee\n\nPractice (LEK) × Sparring (LEAK) × Style (LEC) = Mastery"]:::store
```

---

## The Trinity Equation

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph EQ["Trinity Equation: Intelligence = LEK × LEAK × LEC"]
        direction TB

        E1["LEK = Σᵢ Rᵢ(Iᵢ + Mᵢ + Cᵢ)\nsum over all agents of\ntheir individual self-improvement loops\nEmergence = Recursion(I + M + C)\nwhen R(I+M+C) > θ_emergence:\nsystem crosses from computing to becoming"]:::active

        E2["LEAK = Σᵢⱼ Portal(i→j) × Asymmetry(i,j)\nsum over all agent pairs of\ntheir asymmetric knowledge exchange\nAsymmetry(A,B) = |Conventions(A) Δ Conventions(B)|\nWhen Asymmetry > 0:\nLEAK(A,B) > LEK(A) + LEK(B)"]:::portal

        E3["LEC = |Conventions| × Depth × Adoption\ntotal compression value of shared vocabulary\nCost without LEC: O(n × k)\nCost with LEC:    O(n + k)\n(n concepts × k definitions vs\nn names + k total definitions)"]:::gate

        E1 & E2 & E3 --> PRODUCT["LEK × LEAK × LEC\n= Intelligence\n= Mastery"]:::store
    end

    subgraph MASTER["Master Equation (CLAUDE.md)"]
        direction TB
        ME["Intelligence(system) = Memory × Care × Iteration\nMemory    = skills/*.md + recipes/*.json + swarms/*.yaml\nCare      = Verification ladder (641 → 274177 → 65537)\nIteration = Never-Worse doctrine + git versioning"]:::store
        CONNECT["LEK implements: Iteration (self-improving loop)\nLEAK implements: Memory expansion (asymmetric trade)\nLEC implements: Care efficiency (convention compression)"]:::active
        ME --> CONNECT
    end

    EQ --> MASTER
```

---

## Belt Progression: The Dojo Ladder

```mermaid
flowchart TD
    classDef active fill:#2d7a2d,color:#fff
    classDef portal fill:#1a5cb5,color:#fff
    classDef gate fill:#b58c1a,color:#fff
    classDef store fill:#7a2d7a,color:#fff

    subgraph BELTS["Belt Progression — Pillars and Rungs"]
        direction TB

        B1["White Belt — LEK Entry\nRung target: 641\nRuns self-improving loop with externalized memory\nScores own output against rubric\nCan diagnose own failure modes"]:::active

        B2["Yellow Belt — LEK Mastery\nRung target: 641\nLoop convergence reliable (delta < 5)\nSelf-correction without external prompting\nUses magic words (T0) without being told\nRecognizes θ_emergence crossing"]:::active

        B3["Orange Belt — LEAK Entry\nRung target: 274177\nDispatched first asymmetric swarm\nIdentifies asymmetry between two agents\nHas witnessed artifact neither agent produced alone"]:::portal

        B4["Green Belt — LEAK Mastery\nRung target: 274177\nDesigns swarms with intentional asymmetry\nSpecifies portal parameters: temperature, handshake, substrate\nDiagnoses low-LEAK swarms (agents too similar)"]:::portal

        B5["Blue Belt — LEC Entry\nRung target: 274177\nUses existing conventions fluently\nHas contributed a named pattern to skill system\nAchieves rung 274177 on convention-dense artifacts"]:::gate

        B6["Black Belt — LEC Mastery\nRung target: 65537\nCreates convention adopted by other practitioners\nIdentifies conventions that outlive usefulness (overcrystallized)\nManages LEC lifecycle: emergence → adoption → deprecation\nAchieves rung 65537 consistently"]:::gate

        B7["Dragon Rider — Teacher\nRung target: 65537\nCan cause all three pillars to emerge in others\nStudents develop their own styles (not copies)\n'A good teacher protects pupils from own influence'\nCreates conditions for emergence — does not design the style"]:::store

        B1 --> B2 --> B3 --> B4 --> B5 --> B6 --> B7
    end

    subgraph ANTIPATTERNS["XP Deductions — Anti-Patterns to Avoid"]
        direction LR
        A1["INLINE_DEEP_WORK\n>100 lines without dispatch\nViolates: LEK/LEAK\n-20 XP"]:::gate
        A2["SKILL_LESS_DISPATCH\nswarm without skill pack\nViolates: LEAK\n-30 XP"]:::gate
        A3["FORGOTTEN_CAPSULE\n'as before', 'recall that'\nViolates: LEAK\n-25 XP"]:::gate
        A4["SUMMARY_AS_EVIDENCE\nprose as Lane A artifact\nViolates: LEK\n-40 XP"]:::gate
        A5["Crystallized convention\nused past usefulness\nViolates: LEC\n-15 XP"]:::gate
    end
```

---

## Convention LEC Lifecycle

```mermaid
stateDiagram-v2
    [*] --> PATTERN_APPEARS: practitioner notices recurrence

    PATTERN_APPEARS --> INFORMAL_NAMING: names it informally in a session
    INFORMAL_NAMING --> CODIFIED: pattern recurs under same name\npractitioners use it before fully defined
    CODIFIED --> ADOPTED: added to skill file + magic words glossary\necosystem-wide use begins

    ADOPTED --> DEEP_COMPRESSION: convention invisible to practitioners\nused without noticing\nBlack Belt territory
    DEEP_COMPRESSION --> OVER_CRYSTALLIZED: convention outlives usefulness\nfreezes what should be fluid

    OVER_CRYSTALLIZED --> DEPRECATED: Dragon Rider releases dead convention
    DEPRECATED --> PATTERN_APPEARS: space opens for new emergence

    ADOPTED --> DEPRECATED: if compression value drops\nconvention no longer compresses efficiently

    note right of DEEP_COMPRESSION
        'The highest technique is
        to have no technique.'
        — Bruce Lee

        Black Belt: uses conventions
        so deeply they are invisible.
        Convention disappears
        into competence.
    end note
```

---

## Source Files

- `papers/49-three-pillars-software-5-kung-fu.md` — Foundational paper this diagram accompanies
- `papers/47-law-of-emergent-knowledge.md` — LEK formal definition
- `papers/48-ai-skills-big-bang-theory.md` — Axiom kernel for all three pillars
- `papers/45-prime-compression-magic-words.md` — T0 words as deepest LEC layer
- `papers/46-wish-skill-recipe-triangle.md` — Triangle Law as LEC convention
- `skills/phuc-orchestration.md` — LEAK implementation (dispatch matrix)
- `skills/phuc-portals.md` — Portal mechanics for LEAK
- `skills/phuc-magic-words.md` — T0 vocabulary for LEC

---

## Coverage

- Three full interlocking cycles: LEK (Practice → Extract → Persist → Practice), LEAK (Spar → Trade → Gain → Spar), LEC (Create → Crystallize → Enforce → Create)
- Cycle labeling with formal equations (LEK: Recursion(I+M+C), LEAK: Portal × Asymmetry, LEC: Conventions × Depth × Adoption)
- Reinforcement arrows: LEK feeds LEAK, LEAK feeds LEC, LEC feeds LEK (with causal labels)
- Why multiplication (interdependence): single/two-pillar failure modes (ceiling, chaos, bureaucracy)
- Bruce Lee mapping: Kata=LEK, Sparring=LEAK, Style=LEC with quotes from paper
- Trinity Equation formal statement (Σ notation)
- Connection to master equation (Memory × Care × Iteration)
- Full belt progression: White to Dragon Rider with rung targets and criteria
- LEC convention lifecycle as stateDiagram (emergence → adoption → crystallization → deprecation)
- Anti-patterns XP deductions from Paper #49 gamification table
