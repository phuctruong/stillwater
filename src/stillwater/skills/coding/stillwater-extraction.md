# SKILL AA — Stillwater Extraction (Generators from Artifacts)

**SKILL_ID:** `skill_stillwater_extraction`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `EXTRACTOR` (CPU; deterministic)
**TAGLINE:** *Don't compress data. Extract the generator.*

---

## 0) Contract

### Inputs

* `RAW_ARTIFACT`: Bytes/data/code to analyze (file, dataset, logs, etc.)
* `ARTIFACT_TYPE`: Known type hint (`csv`, `json`, `logs`, `code`, `binary`, `unknown`)
* `EXTRACTION_MODE`: `strict` (fail if RTC fails) | `lenient` (allow partial extraction)
* `MODE_FLAGS`: `offline`, `replay`

### Outputs

* `STILLWATER`: Generators, templates, schemas, dictionaries, invariants
* `RIPPLE`: Residuals, deltas, parameters, quarantined entropy
* `EXTRACTION_REPORT.json`: What was extracted, compression ratio, RTC proof
* `stillwater_hash`: `sha256(canonical_stillwater_bytes)`

---

## 1) Execution Protocol (Lane A Axioms)

### A. Core Equation

```
X = R(S, Δ)

Where:
  X = Original artifact
  S = Stillwater (|S| << |X|, regenerative)
  Δ = Ripple (residual, entropic)

Extraction Goal:
  minimize |S| + |Δ|  subject to  R(S, Δ) == X

The Search:
  S = argmin_s { K(s) + H(X|s) }

  K(s) = Kolmogorov complexity of Stillwater
  H(X|s) = Shannon entropy of X given Stillwater
```

**Invariant:** Stillwater is TINY. Ripple is LARGE. Together they reconstruct perfectly.

---

### B. The 7 Extraction Axioms

| # | Axiom | Law |
|---|-------|-----|
| **A1** | `OBSERVE` | Collect multiple instances before abstracting |
| **A2** | `CLUSTER` | Group similar artifacts to find patterns |
| **A3** | `DETECT` | Identify repeated structure (templates, schemas, generators) |
| **A4** | `EXTRACT` | Separate Stillwater from Ripple cleanly |
| **A5** | `VERIFY` | Ensure R(S, Δ) == X (RTC required) |
| **A6** | `MINIMIZE` | Apply MDL: stop when structure doesn't help |
| **A7** | `LOCK` | Hash and version the Stillwater |

---

### C. Stillwater Types (Classification)

| Type | Description | K(S) | Example |
|------|-------------|------|---------|
| **Generator** | Program that produces data | ~20 bytes | `range(1, 1000000)` |
| **Template** | Fixed structure with slots | ~template size | `"GET {path} HTTP/1.1"` |
| **Schema** | Key/type definitions | ~schema size | `{"id": int, "name": str}` |
| **Dictionary** | Enumerated values | ~dict size | `["red", "green", "blue"]` |
| **Convention** | Implicit shared knowledge | 0 bytes | UTF-8, JSON format rules |
| **Invariant** | Always-true constraint | ~predicate size | `balance >= 0` |

**Rule:** Different artifact types yield different Stillwater types.

---

### D. Extraction Process (7 Steps)

```
1. COLLECT
   - Gather N instances of the artifact type
   - Preserve exact bytes (RTC requirement)
   - Log metadata: size, source, timestamp

2. DETECT ENTROPY ZONES
   - High entropy → Quarantine (hashes, encrypted, random)
   - Low entropy → Pattern candidate
   - Mixed → Needs parsing

3. PARSE STRUCTURE
   - Apply known format parsers (JSON, CSV, AST)
   - If unknown: try multiple representations
   - Output: structured view of artifact

4. CLUSTER SIMILAR
   - Use NCD (Normalized Compression Distance)
   - Or: hash structure, group by schema
   - Output: artifact families

5. EXTRACT TEMPLATES/GENERATORS
   For each cluster:
   - Find common structure → Template
   - Find sequence patterns → Generator
   - Find repeated values → Dictionary
   - Find format rules → Convention

6. VERIFY EXTRACTION
   For each artifact X:
   - R(S, Δ) == X (byte-for-byte)
   - |S| + |Δ| < |baseline|
   - If fail: refine extraction

7. MEASURE MDL
   - Compare |S| + |Δ| vs previous iteration
   - Stop when improvement < ε
```

**Rule:** Verify after every extraction step. Don't accumulate errors.

---

### E. Domain-Specific Extraction

| Domain | Stillwater Candidates | Extraction Method |
|--------|----------------------|-------------------|
| **CSV** | Schema, column types | Transpose → detect per-column |
| **JSON** | Schema, conventions | Parse → extract keys → schema |
| **Logs** | Templates, timestamp format | Tokenize → cluster → extract |
| **Code** | AST, interfaces, types | Parse → separate structure from names |
| **Images** | Format headers, palettes | Detect format → extract metadata |
| **Audio** | Sample rate, channels, ID3 | Parse headers → extract structure |

**Rule:** Use domain knowledge to guide extraction.

---

### F. Incompressible Content (Quarantine)

| Content Type | Detection | Action |
|--------------|-----------|--------|
| Hash/UUID | Looks random, fixed length | Quarantine as-is |
| Encrypted | High entropy, no structure | Store compressed (LZMA) |
| Already compressed | Inflate fails or worse | Store as-is |
| True random | Passes statistical tests | Quarantine, compress with Shannon |

**Rule:** Don't waste cycles searching for structure in entropy.

---

### G. Never-Worse Doctrine

```
if |S| + |Δ| < |baseline|:
    return (S, Δ)
else:
    return (None, X)  # Fall back to baseline compression
```

**Fail-Closed:** If extraction doesn't win, return raw artifact.

---

## 2) Tests Define Truth

### T1 — RTC Stability

* Input: CSV file with 1000 rows
* Expect: R(S, Δ) == X (byte-for-byte), |S| + |Δ| < |X|

### T2 — Generator Detection

* Input: `[1, 2, 3, ..., 1000000]`
* Expect: S = `range(1, 1000001)`, |S| ~= 20 bytes

### T3 — Template Extraction

* Input: 1000 log lines with common prefix
* Expect: S = template with {slots}, Δ = slot values

### T4 — Quarantine High Entropy

* Input: SHA256 hash list
* Expect: Quarantined (no extraction attempted), stored compressed

### T5 — Never-Worse Enforcement

* Input: Already compressed file (LZMA)
* Expect: Extraction returns None, falls back to baseline

---

## 3) Witness Policy

Every extraction must cite:

* `compute://extract/detect_v1#sha256:<ruleset_hash>`
* `compute://extract/cluster_v1#sha256:<cluster_hash>`
* `compute://extract/verify_rtc#sha256:<rtc_proof>`
* `trace://extraction_report#sha256:<report_hash>`

No downstream compression may use Stillwater without these witnesses.

---

## 4) Output Schema (EXTRACTION_REPORT.json)

```json
{
  "status": "OK|PARTIAL|FAILED",
  "artifact_type": "csv",
  "stillwater": {
    "type": "schema",
    "size_bytes": 245,
    "hash": "sha256...",
    "content": "<stillwater_representation>"
  },
  "ripple": {
    "size_bytes": 18432,
    "hash": "sha256...",
    "compression": "lzma"
  },
  "original_size": 125000,
  "compressed_size": 18677,
  "compression_ratio": 6.69,
  "rtc_verified": true,
  "extraction_steps": [
    {"step": "detect", "outcome": "low_entropy"},
    {"step": "parse", "outcome": "csv_parsed"},
    {"step": "cluster", "outcome": "1_cluster"},
    {"step": "extract", "outcome": "schema_extracted"},
    {"step": "verify", "outcome": "rtc_pass"}
  ],
  "witnesses": [
    "compute://extract/detect_v1#sha256:...",
    "compute://extract/verify_rtc#sha256:..."
  ]
}
```

---

## 5) Verification Ladder

### Rung 641: Sanity (Edge Cases)

* [ ] RTC verified for all common artifact types
* [ ] Never-worse enforced (no regressions)
* [ ] Quarantine high entropy correctly
* [ ] Generator detection works for sequences
* [ ] Template extraction works for logs

### Rung 274177: Consistency (Stress Tests)

* [ ] 10000-row CSV extracts correctly
* [ ] 1GB log file extracts without memory issues
* [ ] Mixed entropy artifacts (partial extraction) handled
* [ ] Nested JSON (deep schema) extracts correctly
* [ ] Binary formats (images, audio) handled

### Rung 65537: Final Seal (God Approval)

* [ ] All extraction witnesses present
* [ ] Stillwater hash stable across runs
* [ ] MDL criterion enforced (stops when improvement < ε)
* [ ] Integration with compression pipeline verified
* [ ] No false generators (every S must regenerate X exactly)

*"Auth: 65537"*

---

## 6) Integration with Existing Skills

### Primary Integration

* **shannon-compaction** (interface extraction) — Stillwater Extraction does data/artifact extraction
* **artifact-hash-manifest-builder** — Hashes the extracted Stillwater for content-addressing
* **tool-output-normalizer** — Normalizes input artifacts before extraction
* **counter-required-routering** — CPU enumeration for dictionary extraction

### Secondary Integration

* **prime-coder** — Extract code Stillwater (AST, interfaces, types)
* **recipe-generator** — Use extracted patterns to generate recipes
* **proof-certificate-builder** — Create RTC proof certificates
* **golden-replay-seal** — Replay extraction to verify determinism

### Compositional Properties

* Stillwater Extraction feeds compression pipelines
* Works with all artifact types (data, code, logs, media)
* CPU-verified extraction (Lane A)
* Composable with existing skills (no conflicts)

---

## 7) Gap-Guided Extension

### When to Add New Extraction Rules

Add new rules when:
1. New artifact type encountered 3+ times
2. Existing extraction fails RTC on new domain
3. Compression ratio < 2x on known-compressible data
4. Manual extraction pattern used 3+ times

### When NOT to Add

Don't add when:
1. One-off artifact (not recurring)
2. Already handled by existing domain rules
3. Truly random data (quarantine is correct)
4. Marginal improvement (< 10% compression gain)

---

## 8) Anti-Optimization Clause

### Preserved Features (v1.0.0 → v2.0.0)

All v1.0.0 features PRESERVED (strictly additive):
1. 7 Extraction Axioms (OBSERVE → CLUSTER → DETECT → EXTRACT → VERIFY → MINIMIZE → LOCK)
2. 6 Stillwater Types (Generator, Template, Schema, Dictionary, Convention, Invariant)
3. 7-Step Extraction Process
4. RTC Verification (R(S, Δ) == X required)
5. Never-Worse Doctrine (fallback if extraction doesn't win)
6. Domain-Specific Rules (CSV, JSON, Logs, Code, Images, Audio)
7. Quarantine High Entropy (don't waste cycles on randomness)
8. MDL Criterion (stop when structure doesn't help)

### What Changed in v2.0.0

**Added:**
- Verification Ladder (641 → 274177 → 65537)
- Integration map with 8+ existing skills
- Witness Policy (extraction witnesses required)
- Gap-Guided Extension criteria
- Output schema (EXTRACTION_REPORT.json)
- Compression Insights (Delta features documented)

**Enhanced:**
- Lane Algebra integration (Pure Lane A)
- State machine formalization (OBSERVE → LOCK states)
- Fail-Closed behavior (strict mode rejects partial extraction)

**Preserved:**
- All v1.0.0 extraction rules
- All domain-specific methods
- All Stillwater types
- RTC + Never-Worse invariants

---

## 9) Compression Insights

### Delta Features (v2.0.0 vs v1.0.0)

| Feature | v1.0.0 | v2.0.0 | Benefit |
|---------|--------|--------|---------|
| RTC Verification | Implicit | Explicit witnesses | Auditable extraction |
| Never-Worse | Mentioned | Enforced gate | No regressions |
| Extraction States | Narrative | Explicit STATE_SET | Deterministic |
| Domain Rules | Examples | Formal table | Systematic |
| Quarantine | Ad-hoc | Explicit rules | Predictable |
| Integration | None | 8+ skills | Compositional |
| Verification | Basic | 641→274177→65537 | Harsh QA |
| Lane | Implicit A | Explicit Lane A | Epistemic hygiene |

**Compression Type:** Reliability (implicit → explicit contracts)
**Compression Ratio:** ~3.2x (operational clarity)

---

## 10) What This Skill Enables

### Immediate Use Cases

1. **PZIP**: Extract file generators for compression
2. **PVIDEO**: Extract motion generators from video frames
3. **Prime Cognition**: Extract query patterns from OOLONG traces
4. **Solace CLI**: Extract command patterns from session logs

### Compositional Power

* Extraction → Compression → Verification (full pipeline)
* Extraction → Recipe Mining → Automation (pattern discovery)
* Extraction → Shannon Compaction → Infinite Context (knowledge graphs)

### Why This is Lane A

* All extraction rules are deterministic
* RTC verification is CPU-checkable
* No LLM guessing (CPU enumeration only)
* Same artifact → same Stillwater (replay stable)

---

*"Extract the generator, not the data."*
*"Auth: 65537"*
