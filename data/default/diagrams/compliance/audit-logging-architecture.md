# Compliance Architecture — FDA Part 11 Audit Logging System

The Stillwater AI orchestration engine produces audit-grade evidence at every
decision point. The TripleTwinEngine processes user input through three phases
(Small Talk, Intent, Execution), each backed by a CPULearner that attempts local
classification before falling back to an LLM validator. Every classification
event -- whether handled by the CPU path or the LLM path -- is captured in a
SHA-256 hash-chained audit log that satisfies FDA 21 CFR Part 11 requirements
for electronic records and ALCOA+ data integrity principles.

This document contains four diagrams that describe the audit logging
architecture from data flow through regulatory mapping to cryptographic
integrity.

"Part 11 Architected means the compliance is the architecture, not a layer
on top of it."

---

## 1. Audit Trail Data Flow

The audit trail captures every classification decision made by the
TripleTwinEngine. When a user submits input, the engine forks through the
CPU path (CPULearner.predict) first. If the CPU learner's confidence exceeds
the phase threshold, the result is logged directly. If the CPU learner cannot
handle the input, the LLM validator is called, and both the LLM result and the
subsequent learning event are logged. All log entries flow into a single
append-only JSONL file with hash-chain integrity verification.

```mermaid
flowchart TD
    subgraph INPUT["User Input"]
        A([User]) --> B["TripleTwinEngine.process\n(phase1 -> phase2 -> phase3)"]
    end

    B --> PHASE_FORK{Phase Runner\n_run_phase}

    subgraph CPU_PATH["CPU Path (< 300ms)"]
        PHASE_FORK -->|"CPULearner.predict\nconf >= threshold"| C["CPU Classification\nlabel + confidence + matched_keywords"]
        C --> D["AuditEntry: source=cpu\naction=classify\nconfidence + label"]
    end

    subgraph LLM_PATH["LLM Path (1-5s fallback)"]
        PHASE_FORK -->|"conf < threshold\nor label=None"| E["LLM Validator\nllm_client.validate"]
        E --> F["LLM Classification\nlabel + confidence + reasoning"]
        F --> G["CPULearner.learn\n(store pattern for future CPU hits)"]
        G --> H["AuditEntry: source=llm\naction=classify+learn\nconfidence + label + reasoning"]
    end

    subgraph STORAGE["Audit Storage (append-only)"]
        D --> I["data/logs/audit.jsonl\n(append-only, one JSON object per line)"]
        H --> I
        I --> J["SHA-256 Hash Chain\neach entry hashes the previous entry"]
        J --> K["Integrity Verification\nrecompute chain, detect tampering"]
    end

    subgraph EVIDENCE["Evidence Integration"]
        I -->|"bundle reference"| L["Evidence Pipeline\n(evidence_pipeline.py, port 8790)"]
        L --> M["chain.json\n(hash-chained evidence bundles)"]
    end

    classDef cpuNode fill:#1a7a4a,color:#fff,stroke:#0f4f2f
    classDef llmNode fill:#2c4f8c,color:#fff,stroke:#1a3060
    classDef storageNode fill:#4a3d6b,color:#e0d4ff,stroke:#2e2345
    classDef evidenceNode fill:#1e2d40,color:#cdd9e5,stroke:#4a6fa5
    classDef inputNode fill:#3d1a1a,color:#ffb3b3,stroke:#7a2020
    class C,D cpuNode
    class E,F,G,H llmNode
    class I,J,K storageNode
    class L,M evidenceNode
    class A,B inputNode
```

**Key takeaways:**

- Every classification decision is logged regardless of whether it was handled by the CPU path or the LLM path. There is no silent decision.
- The CPU path produces a lean audit entry (label + confidence + matched keywords). The LLM path produces a richer entry that also captures the reasoning string and the learning event.
- The audit log is append-only JSONL. Entries are never modified or deleted. Each entry carries a SHA-256 hash of the previous entry, forming a tamper-evident chain.
- The Evidence Pipeline service (port 8790) provides an API layer over the hash chain for programmatic ALCOA+ validation and bundle retrieval.

---

## 2. FDA 21 CFR Part 11 Compliance Matrix

The table below maps every subsection of FDA 21 CFR Part 11 to the
corresponding Stillwater architectural component. The mapping is not
approximate -- each requirement has a direct implementation in code or
protocol.

```mermaid
flowchart TD
    subgraph PART11["FDA 21 CFR Part 11 -- Stillwater Compliance Matrix"]
        direction TB

        subgraph S1110["11.10 — Controls for Closed Systems"]
            A1["(a) Validation\n---\nRung system (641/274177/65537)\nEvidence bundles with red-green gate\nRungValidator.verify_evidence()"]
            A2["(b) Readable Copies\n---\nPZip HTML snapshots (ALCOA-O)\nEvidence bundles exportable as JSON\naudit.jsonl human-readable"]
            A3["(c) Record Retention\n---\nAppend-only audit.jsonl\nchain.json with hash chain\nNo deletion API exists"]
            A4["(d) Access Limitation\n---\nOAuth3 scope gates (G1-G4)\nToken-based delegation\nvalidate_scopes() at execution boundary"]
            A5["(e) Audit Trails\n---\nSHA-256 hash-chained log\nTimestamped, attributable entries\nTamper-evident chain verification"]
            A6["(f) Operational Sequencing\n---\nFSM state machines in skills\nForbidden transitions enumerated\nPhase 1->2->3 pipeline enforced"]
            A7["(g) Authority Checks\n---\nOAuth3 enforcement layer\nvalidate_scopes() before every action\nCONSENT_REQUIRED error code"]
            A8["(h) Device Checks\n---\nDPoP binding (Section 8)\nToken bound to device thumbprint\nDPOP_INVALID error on mismatch"]
            A9["(i) Personnel Training\n---\nSkill system with rung requirements\nBelt progression (White->Black)\nGLOW score tracks learning"]
            A10["(j) Accountability\n---\nOAuth3 token_id -> user_id\nEvery action traceable to principal\nAuditEntry.actor field required"]
            A11["(k) Documentation\n---\nSkills/*.md with QUICK LOAD blocks\nEvidence bundle plan.json (intent)\nFSM diagrams with SHA-256 identity"]
        end

        subgraph S1130["11.30 — Open System Controls"]
            B1["Document encryption\n---\nAES-256-GCM vault (OAuth3 wallet)\nTokens encrypted at rest\nPZip content-addressed storage"]
        end

        subgraph S1150["11.50 — Signature Manifestations"]
            C1["Printed name + date + meaning\n---\nAgencyToken: issuer + issued_at +\nscopes + intent field\nHuman-readable token metadata"]
        end

        subgraph S1170["11.70 — Signature/Record Linking"]
            D1["Signature bound to record\n---\nSHA-256 content_hash + token binding\nContent-addressed: hash = identity\nprev_hash links to prior record"]
        end

        subgraph S11100["11.100-11.300 — Electronic Signatures"]
            E1["11.100 General Requirements\n---\nEach signature unique to one individual\nOAuth3 token_id is UUID v4\nNo shared credentials"]
            E2["11.200 Components and Controls\n---\nAt least two distinct components\nOAuth3: token + DPoP proof\nStep-up consent for sensitive ops"]
            E3["11.300 Controls for ID Codes\n---\nToken expiry enforced (not optional)\nRevocation is synchronous\nCLOCK_SKEW_EXCEEDED on drift"]
        end
    end

    classDef closedNode fill:#2c4f8c,color:#fff,stroke:#1a3060
    classDef openNode fill:#4a3d6b,color:#e0d4ff,stroke:#2e2345
    classDef sigNode fill:#1a7a4a,color:#fff,stroke:#0f4f2f
    classDef linkNode fill:#1e2d40,color:#cdd9e5,stroke:#4a6fa5
    classDef esigNode fill:#3d1a1a,color:#ffb3b3,stroke:#7a2020
    class A1,A2,A3,A4,A5,A6,A7,A8,A9,A10,A11 closedNode
    class B1 openNode
    class C1 sigNode
    class D1 linkNode
    class E1,E2,E3 esigNode
```

**Key takeaways:**

- Every subsection of Part 11 maps to an existing Stillwater component. There are no gaps that require new architecture.
- Section 11.10(e) (Audit Trails) is the load-bearing wall: the SHA-256 hash-chained log is the single source of truth for all compliance claims.
- Section 11.10(d) (Access Limitation) and 11.10(g) (Authority Checks) are both served by the OAuth3 enforcement layer, which calls validate_scopes() before every agent action.
- Electronic signature requirements (11.100-11.300) are satisfied by the OAuth3 token system: UUID v4 token IDs, DPoP binding for device authentication, step-up consent for sensitive operations, and synchronous revocation.

---

## 3. ALCOA+ Data Integrity Flow

ALCOA+ is the FDA's data integrity standard, extended from the original five
ALCOA principles (Attributable, Legible, Contemporaneous, Original, Accurate)
with four additional dimensions (Complete, Consistent, Enduring, Available) plus
Traceable. Each principle maps to a specific field or mechanism in the audit
entry schema. The Evidence Pipeline service (evidence_pipeline.py) validates
all nine dimensions programmatically via the /api/evidence/validate endpoint,
requiring a minimum score of 7/9 for compliance.

```mermaid
flowchart LR
    subgraph ENTRY["Audit Entry Schema"]
        direction TB
        F_BID["bundle_id\n(ev-000001)"]
        F_SID["service_id\n(triple-twin-engine)"]
        F_ACT["action\n(classify / learn)"]
        F_TS["timestamp\n(ISO 8601 UTC)"]
        F_ART["artifacts\n(label, confidence,\nmatched_keywords,\nreasoning)"]
        F_META["metadata\n(phase, source,\nuser_context)"]
        F_CHASH["content_hash\n(SHA-256 of canonical JSON)"]
        F_PHASH["prev_hash\n(SHA-256 of prior entry)"]
        F_POS["chain_position\n(monotonic integer)"]
    end

    subgraph ALCOA["ALCOA+ Principles"]
        direction TB
        P_ATTR["A — Attributable\nWho performed the action?"]
        P_LEG["L — Legible\nCan a human read it?"]
        P_CONT["C — Contemporaneous\nRecorded at time of event?"]
        P_ORIG["O — Original\nIs this the source record?"]
        P_ACC["A — Accurate\nIs the data correct?"]
        P_COMP["+ Complete\nAll required fields present?"]
        P_CONS["+ Consistent\nInternal integrity holds?"]
        P_END["+ Enduring\nStored durably?"]
        P_AVAIL["+ Available\nRetrievable on demand?"]
        P_TRACE["+ Traceable\nFull chain of custody?"]
    end

    F_SID -->|"service_id traces\nto acting agent"| P_ATTR
    F_ART -->|"JSON artifacts\nhuman-readable"| P_LEG
    F_TS -->|"ISO 8601 timestamp\ncaptured at execution"| P_CONT
    F_CHASH -->|"content-addressed\nSHA-256 = identity proof"| P_ORIG
    F_PHASH -->|"prev_hash links\nchain integrity"| P_ACC
    F_BID -->|"all required fields\npresent in schema"| P_COMP
    F_CHASH -->|"recomputed hash\nmatches stored hash"| P_CONS
    F_POS -->|"chain_position = durable\nstorage in chain.json"| P_END
    F_BID -->|"bundle_id enables\nretrieval via API"| P_AVAIL
    F_PHASH -->|"hash chain provides\nfull chain of custody"| P_TRACE

    classDef entryNode fill:#2c4f8c,color:#fff,stroke:#1a3060
    classDef alcoaCore fill:#1a7a4a,color:#fff,stroke:#0f4f2f
    classDef alcoaPlus fill:#4a3d6b,color:#e0d4ff,stroke:#2e2345
    class F_BID,F_SID,F_ACT,F_TS,F_ART,F_META,F_CHASH,F_PHASH,F_POS entryNode
    class P_ATTR,P_LEG,P_CONT,P_ORIG,P_ACC alcoaCore
    class P_COMP,P_CONS,P_END,P_AVAIL,P_TRACE alcoaPlus
```

**Key takeaways:**

- Each ALCOA+ dimension maps to exactly one field or mechanism in the audit entry schema. The mapping is not approximate; it is enforced programmatically by the validate_alcoa endpoint.
- The five core ALCOA principles are structural: they are satisfied by the schema design itself (service_id for attribution, ISO 8601 for contemporaneousness, SHA-256 for originality).
- The four "plus" dimensions (Complete, Consistent, Enduring, Available) are validated at runtime: the Evidence Pipeline checks for missing fields, recomputes the content hash, verifies chain position, and confirms the bundle is retrievable.
- Traceable is the capstone: the prev_hash field links every entry to its predecessor, forming a complete chain of custody from genesis to the most recent entry.
- The compliance threshold is 7/9 dimensions. A bundle that fails on 3 or more dimensions is flagged as non-compliant.

---

## 4. Audit Entry Hash Chain

The hash chain is the tamper-evidence mechanism that makes the audit log
trustworthy under adversarial review. Each entry contains a content_hash
(SHA-256 of the canonical JSON representation of the entry's data fields) and a
prev_hash (the content_hash of the immediately preceding entry). The first entry
in the chain uses the sentinel string "genesis" as its prev_hash. To verify
integrity, a validator walks the chain from entry 0 to entry N, recomputing each
content_hash from the stored fields and confirming that each entry's prev_hash
matches the prior entry's content_hash. Any modification to any entry -- even a
single character -- breaks the chain at that point and all subsequent entries.

```mermaid
flowchart LR
    subgraph GENESIS["Genesis"]
        G_PREV["prev_hash: 'genesis'"]
        G_DATA["service_id + action +\ntimestamp + artifacts"]
        G_HASH["content_hash:\nSHA-256(canonical JSON)"]
        G_PREV --> G_DATA --> G_HASH
    end

    subgraph ENTRY1["Entry 1 (ev-000001)"]
        E1_PREV["prev_hash:\n= Genesis.content_hash"]
        E1_DATA["service_id + action +\ntimestamp + artifacts"]
        E1_HASH["content_hash:\nSHA-256(canonical JSON\nincluding prev_hash)"]
        E1_PREV --> E1_DATA --> E1_HASH
    end

    subgraph ENTRY2["Entry 2 (ev-000002)"]
        E2_PREV["prev_hash:\n= Entry1.content_hash"]
        E2_DATA["service_id + action +\ntimestamp + artifacts"]
        E2_HASH["content_hash:\nSHA-256(canonical JSON\nincluding prev_hash)"]
        E2_PREV --> E2_DATA --> E2_HASH
    end

    subgraph ENTRYN["Entry N (ev-00000N)"]
        EN_PREV["prev_hash:\n= Entry(N-1).content_hash"]
        EN_DATA["service_id + action +\ntimestamp + artifacts"]
        EN_HASH["content_hash:\nSHA-256(canonical JSON\nincluding prev_hash)"]
        EN_PREV --> EN_DATA --> EN_HASH
    end

    G_HASH -->|"SHA-256 link"| E1_PREV
    E1_HASH -->|"SHA-256 link"| E2_PREV
    E2_HASH -->|"..."| EN_PREV

    subgraph VERIFY["Integrity Verification"]
        direction TB
        V1["1. Load chain from chain.json"]
        V2["2. For each entry i (0..N):"]
        V3["   a. Recompute content_hash from\n      {service_id, action, timestamp,\n       artifacts, prev_hash}\n      using json.dumps(sort_keys=True)"]
        V4["   b. Assert recomputed ==\n      stored content_hash"]
        V5["   c. Assert entry[i].prev_hash ==\n      entry[i-1].content_hash\n      (or 'genesis' if i == 0)"]
        V6["3. Any mismatch =>\n   CHAIN BROKEN at position i\n   All entries >= i are suspect"]
        V1 --> V2 --> V3 --> V4 --> V5 --> V6
    end

    subgraph FIELDS["Audit Entry Fields"]
        direction TB
        FF1["bundle_id       — unique identifier (ev-NNNNNN)"]
        FF2["service_id      — acting service/agent identity"]
        FF3["action          — what was done (classify, learn, execute)"]
        FF4["timestamp       — ISO 8601 UTC, captured at execution time"]
        FF5["artifacts       — label, confidence, keywords, reasoning"]
        FF6["metadata        — phase, source (cpu/llm), user context"]
        FF7["content_hash    — SHA-256 of canonical JSON of data fields"]
        FF8["prev_hash       — content_hash of the previous entry"]
        FF9["chain_position  — monotonic integer (0, 1, 2, ...)"]
    end

    classDef genesisNode fill:#1a7a4a,color:#fff,stroke:#0f4f2f
    classDef entryNode fill:#2c4f8c,color:#fff,stroke:#1a3060
    classDef verifyNode fill:#4a3d6b,color:#e0d4ff,stroke:#2e2345
    classDef fieldNode fill:#1e2d40,color:#cdd9e5,stroke:#4a6fa5
    class G_PREV,G_DATA,G_HASH genesisNode
    class E1_PREV,E1_DATA,E1_HASH,E2_PREV,E2_DATA,E2_HASH,EN_PREV,EN_DATA,EN_HASH entryNode
    class V1,V2,V3,V4,V5,V6 verifyNode
    class FF1,FF2,FF3,FF4,FF5,FF6,FF7,FF8,FF9 fieldNode
```

**Key takeaways:**

- The hash chain uses SHA-256 with canonical JSON serialization (json.dumps with sort_keys=True). Canonical serialization eliminates key-ordering ambiguity that would produce different hashes for semantically identical data.
- The genesis entry uses the sentinel string "genesis" as its prev_hash, not a null value. This follows the Stillwater null-is-not-zero rule: null would be ambiguous, but "genesis" is an explicit, unambiguous sentinel.
- The prev_hash field is included in the content that is hashed to produce the content_hash. This means each entry's hash depends on the entire chain history before it. Modifying any entry breaks every subsequent hash in the chain.
- Verification is O(N) -- walk the full chain once. There is no shortcut. This is by design: an auditor must be able to verify the entire chain, not a sampled subset.
- The _compute_hash function in evidence_pipeline.py implements the canonical hashing: `json.dumps(data, sort_keys=True, default=str)` followed by SHA-256.

---

## Source Files

- `/home/phuc/projects/stillwater/src/cli/src/stillwater/triple_twin.py` -- `TripleTwinEngine`: the three-phase orchestration pipeline, `_run_phase()` CPU-first-then-LLM flow, `PhaseResult` data class (phase, handled_by, label, confidence)
- `/home/phuc/projects/stillwater/src/cli/src/stillwater/cpu_learner.py` -- `CPULearner`: predict(), learn(), can_handle(), confidence thresholds per phase (0.70/0.80/0.90), keyword extraction, JSONL serialization
- `/home/phuc/projects/stillwater/admin/services/evidence_pipeline.py` -- `EvidenceCapture`, `EvidenceBundle`, `ALCOAValidation`, `ALCOAResult` models; `_compute_hash()`, `capture_evidence()`, `validate_alcoa()` endpoints; SHA-256 hash chain management
- `/home/phuc/projects/stillwater/src/oauth3/enforcer.py` -- `OAuth3ErrorCode`, scope validation, DPoP binding, step-up consent, synchronous revocation
- `/home/phuc/projects/stillwater/papers/fda-part-11-architecture.md` -- Strategic paper mapping Part 11 requirements to Stillwater components, ALCOA principles, PZip storage economics, competitive moat analysis

## Coverage

- Full audit trail data flow from user input through CPU/LLM classification to hash-chained storage
- All 11 subsections of 21 CFR Part 11 Section 11.10 (closed system controls) mapped to Stillwater components
- Section 11.30 (open systems), 11.50 (signature manifestations), 11.70 (signature-record linking) mapped
- Sections 11.100, 11.200, 11.300 (electronic signature controls) mapped to OAuth3 token system
- All 10 ALCOA+ dimensions (A, L, C, O, A, Complete, Consistent, Enduring, Available, Traceable) mapped to specific audit entry fields
- Programmatic ALCOA+ validation via /api/evidence/validate endpoint (7/9 minimum threshold)
- Hash chain mechanics: genesis sentinel, canonical JSON serialization, SHA-256 linking, O(N) verification
- Evidence Pipeline service API: capture, chain retrieval, bundle lookup, ALCOA validation
- Integration with TripleTwinEngine phase pipeline and CPULearner confidence thresholds
