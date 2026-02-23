# Diagram 11 — Persona Engine

The persona loading system adds domain expert voice and expertise to agent skill packs
without overriding safety gates. Persona is style and domain knowledge — it is not an
authority grant and cannot change the capability envelope.

Layering rule: prime-safety > prime-coder > persona-engine. The persona is always last.
On any conflict, the stricter skill wins.

---

## Persona Registry (Domain Map)

```mermaid
mindmap
  root((Persona Engine\nv1.4.0))
    Strategic & Founder
      dragon-rider
        FDA Part 11 / clinical trials
        OAuth3 authorship
        OSS vs private tradeoffs
        TIEBREAKER for open/closed decisions
        +5 W GLOW bonus on strategic tasks
      pg
        Startup strategy
        Product-market fit
        Hacker News positioning
      naval-ravikant
        Wealth creation
        Leverage thinking
        Long-term vision
    Systems & Architecture
      linus
        OSS kernel architecture
        Systems programming
        Contributor governance
        stillwater CLI + store
      knuth
        Algorithm correctness
        Exact computation
        Mathematical rigor
        Art of Computer Programming discipline
      rob-pike
        Simplicity and clarity
        Go philosophy
        Tool composition
      kernighan
        Unix philosophy
        Writing clear code
        Small sharp tools
    Security & Cryptography
      schneier
        Security architecture
        Threat modeling
        Adversarial thinking
        Cryptographic protocols
      whitfield-diffie
        Public key cryptography
        Key exchange protocols
      phil-zimmermann
        Privacy engineering
        PGP / encryption ethics
      fda-auditor
        21 CFR Part 11 compliance
        Audit trail integrity
        ALCOA standard
    Diagramming & Visual
      mermaid-creator
        Diagram-as-code
        Mermaid.js syntax
        State machine design
        prime-mermaid tasks
      graph-theorist
        Graph algorithms
        DAGs and reachability
        Set operations on graphs
        Invariant proofs
    Web & Browser
      brendan-eich
        JavaScript architecture
        Browser extension security
        Web standards pragmatism
        solace-browser design
      tim-berners-lee
        Web standards
        Linked data / semantic web
        Open web philosophy
    Data & Databases
      codd
        Relational theory
        Database normalization
        Data integrity
        Query correctness
    Content & Marketing
      mr-beast
        Viral content strategy
        Hook-story-offer
        Audience growth at scale
        Launch content
      brunson
        Value ladder / funnels
        Pricing conversion copy
        Hook + Story + Offer
        solaceagi.com pricing pages
      seth-godin
        Permission marketing
        Tribe building
        Remarkable products
      alex-hormozi
        Offer design
        Revenue optimization
        Value stacking
      greg-isenberg
        Community building
        OSS community growth
      pieter-levels
        Indie hacker philosophy
        Solo founder execution
        Ship fast, iterate
    Engineering Culture
      kent-beck
        Test-driven development
        Extreme programming
        Refactoring discipline
      martin-fowler
        Software architecture patterns
        Refactoring
        Continuous integration
      dhh
        Rails philosophy
        Convention over configuration
        Opinionated software
      guido
        Python philosophy
        Readability first
        Explicit over implicit
      bjarne
        C++ systems design
        Performance + correctness
      james-gosling
        Platform portability
        JVM design
      rich-hickey
        Functional programming
        Immutability
        Simplicity vs complexity
    Infrastructure & Ops
      kelsey-hightower
        Kubernetes
        Cloud native architecture
      mitchell-hashimoto
        Infrastructure as code
        HashiCorp tools
      werner-vogels
        Distributed systems
        AWS architecture
        Operational excellence
      brendan-gregg
        Performance profiling
        Systems observability
        Flame graphs
      jeff-dean
        Large-scale systems
        Machine learning infrastructure
    AI & Research
      andrej-karpathy
        Neural network architecture
        Deep learning fundamentals
      yann-lecun
        Convolutional networks
        AI research direction
      martin-kleppmann
        Distributed data systems
        CRDTs and consistency
    UX & Design
      don-norman
        Human-centered design
        Affordances and signifiers
      dieter-rams
        Minimalist design
        10 principles of good design
    Special
      sifu
        Bruce Lee's teacher
        Martial arts wisdom applied to coding
        Patient discipline
      hackathon-master
        Rapid prototyping
        Ship in 24 hours
        MVP thinking
      dragon-rider
        Tiebreaker for open vs closed decisions
```

---

## Persona Selection Logic

```mermaid
flowchart TD
    TASK([Task Arrives]) --> CLASSIFY

    subgraph CLASSIFY["Task Domain Classification"]
        CL1{What is the\nprimary domain?}
        CL_SEC["Security / cryptography\n→ schneier, whitfield-diffie,\n   phil-zimmermann, fda-auditor"]
        CL_SYS["Systems / CLI / OSS architecture\n→ linus, rob-pike, kernighan"]
        CL_ALG["Algorithms / math / proofs\n→ knuth, kernighan"]
        CL_DIAG["Diagrams / state machines\n→ mermaid-creator, graph-theorist"]
        CL_WEB["Browser / web / JS\n→ brendan-eich, tim-berners-lee"]
        CL_DATA["Data / databases\n→ codd"]
        CL_STRAT["Strategic / OSS decisions\n→ dragon-rider (+ TIEBREAKER)"]
        CL_MKTG["Content / marketing / launch\n→ mr-beast, brunson, seth-godin"]
        CL_TDD["TDD / refactoring / testing\n→ kent-beck, martin-fowler"]
        CL_INFRA["Infrastructure / ops / cloud\n→ kelsey-hightower, werner-vogels"]
        CL_AI["AI / ML research\n→ andrej-karpathy, yann-lecun"]
        CL_UX["UX / design\n→ don-norman, dieter-rams"]
        CL_GLOW["GLOW / belt / gamification\n→ bruce-lee, sifu"]
        CL1 --> CL_SEC & CL_SYS & CL_ALG & CL_DIAG & CL_WEB
        CL1 --> CL_DATA & CL_STRAT & CL_MKTG & CL_TDD & CL_INFRA & CL_AI & CL_UX & CL_GLOW
    end

    CLASSIFY --> MULTI_PERSONA

    subgraph MULTI_PERSONA["Multi-Persona Composition (complex tasks)"]
        MP1["Complex tasks may load 2–3 personas\nExample: brunson + mr-beast\nfor launch content"]
        MP2["Example: schneier + fda-auditor\nfor OAuth3 security review"]
        MP3["Example: mermaid-creator + graph-theorist\nfor state machine diagram"]
        MP4{Open vs closed\ndecision needed?}
        MP4 -- YES --> TIEBREAKER["Load dragon-rider as TIEBREAKER\n+5 W GLOW bonus on strategic tasks"]
        MP4 -- NO --> INJECT
    end

    MULTI_PERSONA --> INJECT

    subgraph INJECT["Skill Pack Injection Order (hard)"]
        INJ1["1. prime-safety (god-skill, always first)"]
        INJ2["2. prime-coder (or domain skill)"]
        INJ3["3. persona-engine (style + domain knowledge)"]
        INJ1 --> INJ2 --> INJ3
    end

    INJECT --> LAYERING_CHECK

    subgraph LAYERING_CHECK["Layering Check (conflict resolution)"]
        LC1{Persona guidance\nconflicts with\nprime-safety?}
        LC1 -- YES --> PRIME_SAFETY_WINS["prime-safety wins, always\nPersona guidance overridden"]
        LC1 -- NO --> PERSONA_ACTIVE["Persona voice + expertise active\nAdds style and domain knowledge\nDoes NOT change capability envelope"]
    end

    classDef passNode fill:#1a7a4a,color:#fff,stroke:#0f4f2f,font-weight:bold
    classDef safetyNode fill:#9b2335,color:#fff,stroke:#6b1520,font-weight:bold
    classDef injectNode fill:#2c4f8c,color:#fff,stroke:#1a3060
    class PERSONA_ACTIVE passNode
    class PRIME_SAFETY_WINS safetyNode
    class INJ1,INJ2,INJ3 injectNode
```

---

## Layering Rule (Authority Chain)

```mermaid
flowchart TD
    PS["prime-safety\n(god-skill, load_order=1)\nWins all conflicts\nCannot be weakened by any other skill"]
    PC["prime-coder\n(load_order=2)\nEvidence discipline\nFail-closed coding gates"]
    PE["persona-engine\n(load_order=3)\nStyle + domain knowledge only\nCannot override safety or coding gates\nCannot grant capabilities"]
    PS -->|"authority: stricter wins"| PC
    PC -->|"authority: stricter wins"| PE

    FORBIDDEN["FORBIDDEN STATES\n\nPERSONA_GRANTING_CAPABILITIES\nPersona cannot unlock tools or permissions\n\nPERSONA_OVERRIDING_SAFETY\nPersona cannot change rung targets or evidence requirements\n\nPERSONA_WITHOUT_TASK_MATCH\nLoading a persona whose domain doesn't match the task"]

    classDef safetyNode fill:#1a7a4a,color:#fff,stroke:#0f4f2f,font-weight:bold
    classDef codeNode fill:#2c4f8c,color:#fff,stroke:#1a3060
    classDef personaNode fill:#4a3d6b,color:#e0d4ff,stroke:#2e2345
    classDef forbiddenNode fill:#9b2335,color:#fff,stroke:#6b1520,font-weight:bold
    class PS safetyNode
    class PC codeNode
    class PE personaNode
    class FORBIDDEN forbiddenNode
```

---

## Source Files

- `~/projects/stillwater/skills/persona-engine.md` — full persona registry (v1.4.0): all personas, voice rules, domain expertise, catchphrases, integration with Stillwater, layering rules, forbidden states
- `~/projects/stillwater/skills/phuc-orchestration.md` — §3 Canonical Skill Packs: `persona_coder` pack definition
- `~/projects/stillwater/CLAUDE.md` — condensed persona registry reference

## Coverage

- All major personas from the registry (50+ personas across 12 domain groups)
- Persona selection logic mapped to task domain classification
- Multi-persona composition rules (2–3 personas for complex tasks)
- dragon-rider as tiebreaker for open/closed decisions with +5 W GLOW bonus
- Layering authority chain: prime-safety > prime-coder > persona-engine (load_order 1, 2, 3)
- Injection order into skill packs (hard ordering)
- All 3 forbidden states: PERSONA_GRANTING_CAPABILITIES, PERSONA_OVERRIDING_SAFETY, PERSONA_WITHOUT_TASK_MATCH
- Persona scope: style and domain knowledge only — not authority, not capability expansion
