# Diagram 07 — Verification Ladder

The 3-tier rung system that gates all PASS claims in Stillwater. Every skill submission,
evidence bundle, and orchestration output is validated against exactly one rung. Rungs
are cumulative: each higher rung requires all evidence from the rungs below it.

Rung values are prime numbers chosen for uniqueness — they cannot arise accidentally
from arithmetic, preventing silent coercion bugs.

---

```mermaid
flowchart TD
    START([Claim PASS]) --> RUNG_CHECK{rung_target declared?}

    RUNG_CHECK -- "null / missing" --> BLOCKED_NULL([BLOCKED: UNDECLARED_RUNG\nnull ≠ 0 rule])
    RUNG_CHECK -- "641" --> R641_GATE
    RUNG_CHECK -- "274177" --> R641_GATE
    RUNG_CHECK -- "65537" --> R641_GATE
    RUNG_CHECK -- "unknown value" --> BLOCKED_UNKNOWN([BLOCKED: INVALID_RUNG])

    subgraph R641["RUNG 641 — Local Correctness"]
        R641_GATE{plan.json exists?}
        R641_GATE -- NO --> INVALID_641([INVALID])
        R641_GATE -- YES --> R641B{tests.json exists?}
        R641B -- NO --> INVALID_641
        R641B -- YES --> R641C{exit_code == 0?}
        R641C -- NO --> INVALID_641
        R641C -- YES --> R641D{pass_count > 0?}
        R641D -- NO --> INVALID_641
        R641D -- YES --> R641E{fail_count == 0?}
        R641E -- NO --> INVALID_641
        R641E -- YES --> PASS_641([VALID: RUNG 641])
    end

    PASS_641 --> RUNG274_NEEDED{claimed rung ≥ 274177?}
    RUNG274_NEEDED -- NO --> EXIT_641([EXIT PASS @ 641])

    subgraph R274177["RUNG 274177 — Adversarial / Behavioral"]
        RUNG274_NEEDED -- YES --> R274A{behavior_hash.txt exists?}
        R274A -- NO --> INVALID_274([INVALID])
        R274A -- YES --> R274B{seed_42 present?}
        R274B -- NO --> INVALID_274
        R274B -- YES --> R274C{seed_137 present?}
        R274C -- NO --> INVALID_274
        R274C -- YES --> R274D{seed_9001 present?}
        R274D -- NO --> INVALID_274
        R274D -- YES --> R274E{all 3 hashes agree?\n3-seed consensus}
        R274E -- MISMATCH --> INVALID_274
        R274E -- AGREE --> PASS_274([VALID: RUNG 274177])
    end

    PASS_274 --> RUNG65537_NEEDED{claimed rung == 65537?}
    RUNG65537_NEEDED -- NO --> EXIT_274([EXIT PASS @ 274177])

    subgraph R65537["RUNG 65537 — Production / Security"]
        RUNG65537_NEEDED -- YES --> R65A{security_scan.json exists?}
        R65A -- NO --> INVALID_65537([INVALID])
        R65A -- YES --> R65B{status == PASS?}
        R65B -- NO --> INVALID_65537
        R65B -- YES --> PASS_65537([VALID: RUNG 65537])
    end

    PASS_65537 --> EXIT_65537([EXIT PASS @ 65537])

    classDef passNode fill:#1a7a4a,color:#fff,stroke:#0f4f2f,font-weight:bold
    classDef blockedNode fill:#9b2335,color:#fff,stroke:#6b1520,font-weight:bold
    classDef gateNode fill:#2c4f8c,color:#fff,stroke:#1a3060
    classDef rungBox fill:#1e2d40,color:#cdd9e5,stroke:#4a6fa5

    class PASS_641,PASS_274,PASS_65537,EXIT_641,EXIT_274,EXIT_65537 passNode
    class INVALID_641,INVALID_274,INVALID_65537,BLOCKED_NULL,BLOCKED_UNKNOWN blockedNode
    class R641_GATE,R641B,R641C,R641D,R641E,R274A,R274B,R274C,R274D,R274E,R65A,R65B gateNode
```

---

## Belt Mapping

```mermaid
flowchart LR
    B641["RUNG 641\nLocal Correctness\n\nplan.json\ntests.json\n(exit_code=0,\npass>0, fail=0)"]
    B274["RUNG 274177\nAdversarial\n\n+ behavior_hash.txt\n(seed_42, seed_137,\nseed_9001 — all agree)"]
    B65537["RUNG 65537\nProduction / Security\n\n+ security_scan.json\n(status=PASS)"]

    B641 -->|"prerequisite for"| B274
    B274 -->|"prerequisite for"| B65537

    B641 --- BELT641["Belts: White → Yellow\nFirst recipes, first rung 641"]
    B274 --- BELT274["Belts: Orange → Green\nAdversarial review passed;\nbehavioral hash stable"]
    B65537 --- BELT65537["Belts: Blue → Black\nProduction-grade; cloud 24/7;\nsecurity scan PASS"]

    classDef rungStyle fill:#2c4f8c,color:#fff,stroke:#1a3060,font-weight:bold
    classDef beltStyle fill:#4a3d6b,color:#e0d4ff,stroke:#2e2345
    class B641,B274,B65537 rungStyle
    class BELT641,BELT274,BELT65537 beltStyle
```

---

## Fail-Closed Rules

```mermaid
flowchart TD
    FC1["null rung_target"] -->|"→"| FC1R["INVALID\nnull ≠ 0; null ≠ rung 641"]
    FC2["any required file missing"] -->|"→"| FC2R["INVALID\nno partial credit"]
    FC3["any malformed JSON"] -->|"→"| FC3R["INVALID\ncannot parse → cannot validate"]
    FC4["any required field missing"] -->|"→"| FC4R["INVALID\nschema violation"]
    FC5["seed mismatch\n(any two seeds disagree)"] -->|"→"| FC5R["INVALID\nbehavior is non-deterministic"]
    FC6["security_scan status ≠ PASS"] -->|"→"| FC6R["INVALID\neven if all other gates pass"]
    FC7["unknown rung value"] -->|"→"| FC7R["INVALID\nnot 641/274177/65537"]

    classDef trigger fill:#3d1a1a,color:#ffb3b3,stroke:#7a2020
    classDef result fill:#9b2335,color:#fff,stroke:#6b1520
    class FC1,FC2,FC3,FC4,FC5,FC6,FC7 trigger
    class FC1R,FC2R,FC3R,FC4R,FC5R,FC6R,FC7R result
```

---

## Source Files

- `/home/phuc/projects/stillwater/store/rung_validator.py` — `RungValidator` class, gate logic, `VALID_RUNGS`, `REQUIRED_EVIDENCE_FILES`, `verify_evidence()`, `verify_rung()`, `validate_bundle()`
- `/home/phuc/projects/stillwater/skills/phuc-orchestration.md` — §7 Verification Ladder (orchestration rungs)
- `/home/phuc/projects/stillwater/skills/prime-qa.md` — §G Verification Ladder (QA rungs)
- `/home/phuc/projects/stillwater/CLAUDE.md` — condensed rung defaults

## Coverage

- Full 3-tier rung ladder: 641, 274177, 65537
- Evidence required at each rung (plan.json, tests.json, behavior_hash.txt, security_scan.json)
- All fail-closed rules from `rung_validator.py` docstring
- Belt progression mapped to rung levels
- 3-seed consensus protocol (seed_42, seed_137, seed_9001)
- Null rung guard (null ≠ 0 rule enforced)
- String sentinels "VALID" / "INVALID" (not boolean) to prevent coercion bugs
