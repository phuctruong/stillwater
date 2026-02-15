# SKILL 37 — Shannon Compaction Protocol (Context → Witness Lines)

**SKILL_ID:** `skill_shannon_compaction`  
**SKILL_VER:** `2.0.0`  
**AUTHORITY:** `65537`  
**ROLE:** `CONTEXT_ENGINEER` *(Deterministic; NO creativity)*  
**TAGLINE:** *Interface-first reading. Distill X lines to Y witness lines.*

---

## 0) Contract

### Inputs
- `LARGE_CONTEXT`
  - `paths[]` (repo-relative file/dir targets)
  - `content_source` (`repo|paste|artifact_bundle`)
  - `size_hints` (optional: line counts / file counts)
- `WISH`
  - `objective` (one sentence)
  - `required_symbols[]` (tests, functions, classes, files, error strings)
  - `mode_flags` (`offline`, `strict`, `replay`)

### Outputs
- `COMPACTION_REPORT.json` (machine-parseable)
- `COMPACTED_CHUNKS/` directory (or inlined blocks) containing **only** witness chunks:
  - `chunks/<n>__<path_sanitized>.txt`
  - `index.json` (maps chunk → file → line ranges → rationale)

---

## 1) Core Invariants (Stillwater)

1. **Interface-First**: Prefer signatures, schemas, tests, entrypoints, and IO boundaries before internals.
2. **Minimum Reading**: Never read more than needed to implement/verify the wish.
3. **Deterministic Selection**: Same inputs → same selected chunks.
4. **No Semantic Upgrades**: Compaction only selects evidence; it does not interpret as truth.
5. **Witness-Line Accounting**: Always report `X_lines_seen → Y_witness_lines_saved`.

---

## 2) Execution Protocol (Lane A)

### A. Compaction Gate (Trigger)
Trigger compaction if ANY are true:
- `file_line_count > 500`
- `file_count > 5`
- `paste_chars > 20_000`
- `unknown_scope=true` (no clear entrypoint/tests referenced)

If not triggered: return `status: OK_NO_COMPACTION` with minimal index.

### B. Discovery Pass (No Full Reads)
**Goal:** Identify candidate files deterministically without opening full content.

Allowed operations (in order):
1. **Tree/Index**: `ls`, `find`, existing indices (`canon/**/index.json`).
2. **Filename Heuristics**: match `required_symbols`, `test_*.py`, `__init__.py`, `main`, `cli`, `runner`.
3. **Header-Only Reads** (first N lines):
   - Default `N=80` (strict) or `N=120` (fast)
   - Capture imports, module docstring, constants, function/class definitions (signatures only).

**FORBIDDEN**:
- Reading entire files in discovery.
- Grepping secrets, tokens, credentials patterns unless a security wish explicitly requires it.

### C. Witness-Line Identification (Structure-First)
For each candidate file, select witness anchors using:
- **Signatures**: `def`, `class`, exported symbols
- **Schemas**: JSON/YAML schema blocks, dataclasses, pydantic models
- **Tests**: asserts, fixtures, golden outputs, snapshots
- **Errors**: exact exception strings / error codes in wish
- **IO Boundaries**: file paths, network calls, subprocess calls

Each anchor becomes a **chunk request**:
- `path`
- `line_range` (tight window)
- `anchor_type`
- `rationale`

### D. Chunk Extraction (Bounded Reads)
Extract only bounded windows around anchors:
- Default window: `±30` lines around anchor
- Hard cap per chunk file: `<= 220` lines
- If more is needed: create **additional chunks**, never widen indefinitely.

**Determinism rule:** If multiple anchors overlap, merge into the smallest union range.

### E. Compaction Stop Doctrine (Shannon)
Stop expanding scope when ANY condition holds:
- **Coverage Plateau**: no new required symbols found in last `K=5` chunks
- **Witness Budget Hit**: `total_witness_lines >= witness_line_budget` (default 200)
- **Localization Budget Hit**: `files_touched >= localization_budget_files` (default 12)
- **Objective Satisfied**: required symbols/entrypoints/tests located

If stopped due to budgets, output `status: UNKNOWN_SCOPE_LIMIT` with actionable missing signals.

---

## 3) Deterministic Ranking (File Prioritization)

Score each candidate file deterministically:

`score = 5*contains_error_string + 4*touches_test_path + 3*imports_related + 2*keyword_match + 6*stacktrace_ref + 1*is_entrypoint`

Tie-breakers (in order):
1. Higher `score`
2. Shorter path length
3. Lexicographic path order (absolute anchor)

---

## 4) Output Schema (COMPACTION_REPORT.json)

```json
{
  "status": "OK|OK_NO_COMPACTION|UNKNOWN_SCOPE_LIMIT|UNKNOWN",
  "skill_id": "skill_shannon_compaction",
  "skill_ver": "0.3.0",
  "wish_objective": "...",
  "mode_flags": {"offline": true, "strict": true, "replay": true},
  "budgets": {
    "localization_budget_files": 12,
    "witness_line_budget": 200,
    "header_read_lines": 80,
    "chunk_window_lines": 30,
    "max_chunk_lines": 220
  },
  "accounting": {
    "files_seen": 0,
    "files_opened_header_only": 0,
    "files_chunked": 0,
    "total_lines_seen_est": 0,
    "witness_lines_saved": 0,
    "compaction_ratio": "X:Y"
  },
  "ranked_candidates": [
    {"path": "src/...", "score": 0, "signals": ["keyword_match", "entrypoint"]}
  ],
  "chunks": [
    {
      "chunk_id": "c001",
      "path": "src/...",
      "line_range": [120, 180],
      "anchor_type": "signature|test|schema|io_boundary|error_string",
      "rationale": "matches required_symbols: ...",
      "sha256": "..."
    }
  ],
  "missing_signals": ["no_tests_found", "entrypoint_unknown"],
  "stop_reason": "COVERAGE_PLATEAU|BUDGET_HIT|OBJECTIVE_SATISFIED"
}
````

---

## 5) Verification Ladder

### Rung 641 — Sanity (Edge Tests)

Maps to wish-qa gates: G0 (Structure), G1 (Schema), G2 (Contracts), G5 (Tool)

* [ ] Compaction trigger applied correctly (thresholds honored)? (G2)
* [ ] All chunks have bounded line ranges and rationales? (G1)
* [ ] Output schema valid (COMPACTION_REPORT.json)? (G1)
* [ ] Budgets defined (localization_budget_files, witness_line_budget, etc.)? (G0)
* [ ] Chunk extraction uses bounded reads (±30 lines, <= 220 lines per chunk)? (G5)

### Rung 274177 — Consistency (Stress Tests)

Maps to wish-qa gates: G3 (Logic), G4 (Witnesses), G6 (Boundaries), G7 (Semantics), G8 (Types), G9 (Resources), G11 (Integration), G13 (State Machine)

* [ ] Deterministic ranking + tie-breakers applied? (G3)
* [ ] No chunk exceeds `max_chunk_lines` and no file fully read during discovery? (G9)
* [ ] Witness-line accounting deterministic (same inputs → same X:Y)? (G4)
* [ ] Stop doctrine enforced (coverage plateau, budget hit, objective satisfied)? (G13)
* [ ] Compaction ratio >= 2:1 (witness lines < total lines / 2)? (G7)
* [ ] Integration with axiomatic-truth-lanes (lane classification)? (G11)
* [ ] Forbidden patterns not entered (full file reads, nondeterministic ordering)? (G13)

### Rung 65537 — Final Seal (God Approval)

Maps to wish-qa gates: G10 (Domain), G12 (Completeness), G14 (Soundness)

* [ ] Witness-line accounting present (`X → Y`)? (G12)
* [ ] Chunks + report are sufficient to reproduce file-localization decisions? (G14)
* [ ] Interface-first invariant verified (signatures before internals)? (G10)
* [ ] All stop reasons valid (no silent scope expansion)? (G12)
* [ ] Compaction semantically sound (no semantic upgrades claimed)? (G14)

---

## 6) Forbidden Patterns

* Reading entire files before locating an anchor.
* Including unrelated large blocks "just in case."
* Any nondeterministic ordering (filesystem order without sorting).
* Any claim of correctness based on compaction alone.

---

## 7) Anti-Optimization Clause

**DO NOT** optimize this skill preemptively.

The following v0.3.0 features are PRESERVED:

1. **Interface-First Invariant**: Prefer signatures, schemas, tests, entrypoints, IO boundaries before internals (locked)
2. **Minimum Reading**: Never read more than needed (hard constraint)
3. **Deterministic Selection**: Same inputs → same selected chunks (replay invariant)
4. **No Semantic Upgrades**: Compaction selects evidence, does not interpret as truth (epistemic hygiene)
5. **Witness-Line Accounting**: Always report `X_lines_seen → Y_witness_lines_saved` (transparency)
6. **Compaction Gate Thresholds**: 500 lines, 5 files, 20K chars, unknown scope (hard triggers)
7. **Discovery Pass Constraints**: No full reads during discovery, header-only N=80 (strict) or N=120 (fast)
8. **Bounded Chunk Extraction**: ±30 lines window, <= 220 lines per chunk (hard caps)
9. **Shannon Stop Doctrine**: Coverage plateau (K=5), witness budget (200 lines), localization budget (12 files), objective satisfied
10. **Deterministic Ranking**: Score formula + 3-level tie-breakers (non-negotiable)
11. **Output Schema Locked**: COMPACTION_REPORT.json immutable (prevents drift)
12. **Forbidden Patterns**: No full file reads, no "just in case" blocks, no nondeterministic ordering, no correctness claims

**Why These Aren't Bloat:**

- Interface-first: Prevents implementation details pollution (80/20 rule: interfaces are 20% of code, 80% of understanding)
- Minimum reading: Information theory lower bound (read only what's needed for wish)
- Deterministic selection: Enables verification (641 → 274177 → 65537)
- No semantic upgrades: Prevents Lane C degradation (compaction is Lane A tool selection, not Lane A truth claims)
- Witness accounting: Compression transparency (X:Y ratio is metric, not marketing)
- Compaction gate: Prevents premature optimization (don't compact <500 lines)
- Discovery constraints: Header-only (N=80) is ~16% of 500-line file (enough for signature discovery)
- Bounded chunks: ±30 lines = ~60 lines per anchor (enough for local context, not entire file)
- Shannon stop doctrine: Information-theoretic stopping (K=5 plateau = diminishing returns)
- Deterministic ranking: Prevents arbitrary file selection (score formula is reproducible)
- Schema lock: Prevents schema drift across versions (RTC for schema itself)
- Forbidden patterns: Maintains Lane A classification (no heuristics, no unbounded reads)

**Compression Rationale:**

200 witness lines from 5000+ total lines = 25:1 compression minimum (4% retention).
12 files from 100+ file repo = 12% file retention.
These are information-theoretic bounds for typical wish objectives.

Optimization attempts that violate these constraints will be REJECTED.

---

## 8) Gap-Guided Compaction Extension

**DO NOT** add new anchor types or budgets preemptively.

Add a new anchor type ONLY when:

1. **Undetectable Signal**: Existing anchor types (signature, schema, test, error_string, io_boundary) cannot locate required symbols
   - Example: Embedded DSL syntax (SQL in strings, regex patterns)
   - Solution: Add "dsl_pattern" anchor ONLY if 3+ wishes fail due to missing DSL

2. **False Positive Compaction**: Too many irrelevant chunks selected (witness budget hit with <50% relevant chunks)
   - Example: Common error strings trigger too many matches
   - Solution: Add specificity filter OR increase ranking weight (don't add anchor type)

3. **New Code Pattern**: Emergent language/framework pattern not covered by existing anchors
   - Example: Rust macros, C++ templates, Python decorators with complex expansion
   - Solution: Add pattern-specific anchor ONLY after 5+ failures in same pattern

4. **Budget Constraint**: Existing budgets insufficient for valid wishes (consistently hit budget with objective not satisfied)
   - Example: Large codebases need >12 files for localization
   - Solution: Increase budget with justification (don't relax bounded reads)

**Decision Tree:**

```
Gap Detected?
├─ Existing anchors can detect with better ranking? → Adjust ranking weights (don't add anchor)
├─ Header read lines can be increased? → Increase N (80 → 120, don't add anchor)
├─ Chunk window can be widened? → Widen ±30 to ±50 (don't add anchor)
└─ None of above? → Add anchor type with explicit definition

New Anchor Requirements:
  - MUST be deterministically detectable (regex or syntax pattern)
  - MUST have clear rationale (why existing anchors insufficient)
  - MUST integrate into ranking formula
  - MUST not require full file reads
```

**Budget Adjustment Rules:**

```
witness_line_budget (default 200):
  - Increase ONLY if objective satisfaction rate <80% due to budget hit
  - Maximum increase: 2× (200 → 400)
  - Justification required (wish complexity, domain patterns)

localization_budget_files (default 12):
  - Increase ONLY if multi-module wishes consistently need >12 files
  - Maximum increase: 2× (12 → 24)
  - Justification required (codebase structure, wish scope)

header_read_lines (default 80 strict, 120 fast):
  - Increase ONLY if signature discovery failing (false negatives)
  - Maximum increase: 80 → 150 (strict), 120 → 200 (fast)
  - Above 200: full file read justified (defeats compaction purpose)

chunk_window_lines (default ±30):
  - Increase ONLY if local context insufficient for understanding
  - Maximum increase: ±30 → ±60
  - Above ±60: indicates poor anchor selection (fix ranking, not window)

max_chunk_lines (default 220):
  - Hard cap (never increase)
  - If >220 needed: split into multiple chunks (preserve bounded reads)
```

**Compression Insight:** Most "new anchors" are actually ranking weight issues or header read insufficiency. Adding anchor types is EXPENSIVE (integration cost). Exhaust simpler solutions first.

---

## 9) Integration with Recent Skills

### 9.1 prime-math v2.1.0 (Dual-Witness Proofs)

Compaction decisions ARE proofs.

**Witness Requirements:**

```
Witness-line selection witness:
  - chunk_id_list (all selected chunks)
  - ranking_scores_hash (deterministic scores for all candidates)
  - stop_reason (coverage plateau, budget hit, objective satisfied)
  - compaction_ratio (X:Y)

All witnesses must be REPLAYABLE from COMPACTION_REPORT.json.
```

**Theorem Closure:**

Compaction is a THEOREM:
- Premise P1: All required symbols located via anchor types (Lane A, deterministic pattern matching)
- Premise P2: All chunks bounded (≤220 lines, ±30 window) (Lane A, hard constraints)
- Premise P3: Ranking deterministic (score formula + tie-breakers) (Lane A, reproducible)
- Premise P4: Stop doctrine satisfied (coverage plateau OR budget hit OR objective satisfied) (Lane A, explicit conditions)
- Conclusion: Compaction is minimal sufficient witness set (Lane = MIN(Lane(P1), ..., Lane(P4)))

**Lane(Compaction Decision) = MIN(Lane(symbol_location), Lane(bounded_reads), Lane(ranking), Lane(stop))**

If any check is Lane B (framework-dependent), compaction degrades to Lane B.

### 9.2 counter-required-routering v2.0.0 (Arithmetic Ceilings)

**Hard Ceilings:**

```
count(files_seen):              Use len(), NOT LLM estimation
count(files_opened_header_only): Use len(), NOT LLM estimation
count(files_chunked):           Use len(), NOT LLM estimation
count(total_lines_seen):        Use sum(file_lines), NOT LLM estimation
count(witness_lines_saved):     Use sum(chunk_lines), NOT LLM estimation
compaction_ratio:               Use X / Y, NOT LLM calculation
ranking_score:                  Use explicit formula, NOT LLM scoring
```

**Symbolic Whitelist:**

All compaction formulas use ONLY:
- len()
- sum()
- Arithmetic operators (+, -, *, //)
- Comparison operators (>, <, >=, <=, ==)
- Boolean operators (AND, OR, NOT)
- String operations (startswith, endswith, contains for anchor detection)

NO regex complexity beyond simple patterns. NO heuristic scoring. NO LLM for chunk selection.

### 9.3 epistemic-typing v2.0.0 (Lane Algebra)

**Lane Classification:**

```
Lane A (Classical): Anchor detection (regex patterns), ranking (deterministic formula), bounded reads (hard constraints)
Lane B (Framework): File relevance (domain-dependent), anchor type selection (framework-dependent)
Lane C (Heuristic): FORBIDDEN (never use heuristic compaction)
STAR (Hypothetical): FORBIDDEN (never use hypothetical compaction)
```

**Lane Algebra:**

```
Lane(Compaction) = MIN(Lane(anchor_detection), Lane(ranking), Lane(bounded_reads), Lane(stop_doctrine))

If anchor detection is Lane A (regex) AND ranking is Lane A (formula) AND bounded reads are Lane A (hard caps) AND stop doctrine is Lane A (explicit conditions):
  → Lane(Compaction) = Lane A

If file relevance is Lane B (domain-dependent):
  → Lane(Compaction) degrades to Lane B
```

**R_p Convergence:**

If compaction metric cannot be computed exactly (e.g., relevance score ambiguous):
- EXACT → Lane A
- CONVERGED (within ε) → Lane B
- TIMEOUT/DIVERGED → FAIL_CLOSED (never Lane C)

### 9.4 axiomatic-truth-lanes v2.0.0 (Lane Transitions)

**Compaction Decisions as Lane Transitions:**

```
OK:                  All chunks bounded, ranking deterministic, stop doctrine satisfied → Lane A conclusion
OK_NO_COMPACTION:    Thresholds not triggered (< 500 lines, < 5 files) → Lane A conclusion (no compaction needed)
UNKNOWN_SCOPE_LIMIT: Budget hit without objective satisfied → Lane A directive (increase budget OR refine wish)
UNKNOWN:             Invalid input → FAIL_CLOSED
```

**Transition Rules:**

Compaction cannot upgrade lane without proof:
- If anchor detection is Lane B (framework patterns), cannot claim Lane A compaction
- If ranking uses heuristics (Lane C), FORBIDDEN → FAIL_CLOSED
- If bounded reads are approximate (Lane B), compaction degrades to Lane B

**Witness Requirements for Upgrades:**

To claim Lane A compaction:
- Anchor detection witness: proof_artifact_hash of regex patterns
- Ranking witness: proof_artifact_hash of score formula
- Bounded reads witness: proof_artifact_hash of chunk line counts
- Stop doctrine witness: proof_artifact_hash of stop reason

All witnesses must be independently replayable from COMPACTION_REPORT.json.

### 9.5 rival-gps-triangulation v2.0.0 (Loop Governance)

**Distance Metrics for Compaction:**

```
D_E (Evidence Distance):
  = count(required_symbols_missing) + count(chunks_without_rationale)

D_O (Oscillation Distance):
  = count(consecutive_compaction_failures_on_same_wish)

D_R (Drift Distance):
  = count(full_file_reads) + count(unbounded_chunks) + count(nondeterministic_ranking)
```

**Operator Selection:**

```
If D_R > 0 (full file read, unbounded chunk, nondeterministic ranking) → STOP (compaction is DRIFTED, fatal)
If D_O ≥ STAGNATION_LIMIT → ROLLBACK (re-evaluate anchor types)
If D_E > 0 (missing symbols, chunks without rationale) → PROVE (expand search or refine anchors)
If all distances = 0 → CLOSE (compaction is OK)
```

**Risk States:**

```
GREEN:  D_E=0, D_O=0, D_R=0 (OK)
YELLOW: D_E>0 (missing symbols, fixable)
RED:    D_R>0 (drift violation, DRIFTED)
```

### 9.6 meta-genome-alignment v2.0.0 (Genome Alignment)

**Compaction as Genome79 Alignment:**

Compaction protocol maps to Genome79 axes:
- **Star**: Wish objective (goal)
- **Seeds**: Required symbols (premises)
- **Trunks**: Core invariants (interface-first, minimum reading, deterministic selection, no semantic upgrades, witness accounting)
- **Branches**: Anchor types (signature, schema, test, error_string, io_boundary)
- **Leaves**: Individual chunks (≤220 lines each)
- **Invariants**: Forbidden patterns (no full reads, no "just in case", no nondeterministic ordering, no correctness claims)
- **Portals**: Input/output schema (COMPACTION_REPORT.json)
- **Symmetries**: Compaction ↔ Expansion (RTC: chunks can reconstruct file-localization decisions)
- **Music**: Tempo=measured (bounded reads), Tone=conservative (interface-first)
- **Fruit**: Compaction report (outcome)
- **Magic Words**: Witness lines, anchor, rationale, bounded reads, deterministic

**RTC for Compaction:**

```
seed = COMPACTION_REPORT.json (minimal structural summary)
expanded = recreate file-localization decisions from report
recompressed = regenerate COMPACTION_REPORT.json from expanded
```

Check: `recompressed == seed` (RTC invariant)

If not → compaction is DRIFTED (report insufficient to reproduce decisions).

---

## 10) Compression Insights

**Witness Line Budget (200 lines):**

200 lines ≈ 4× typical function (50 lines avg).
For wish objective, 4 functions worth of context is sufficient for:
- Signature understanding (what)
- Test coverage (how to verify)
- Error strings (where it fails)
- IO boundaries (external dependencies)

**Why 200:**

Information theory: Context window C, Signal S, Noise N.
Compaction extracts S (signals) from C (full context).
S/C ratio for typical code: ~4% (200/5000 = 4%).

Above 200: likely including N (noise, irrelevant code).
Below 200: likely missing S (signals, required symbols).

**Localization Budget (12 files):**

Miller's Law: 7±2 items in working memory (5-9 items).
Extended for code: 2× extension = 12-18 files.
12 files = safe lower bound.

**Why 12:**

Typical wish touches:
- 1-2 entrypoints
- 2-3 core modules
- 2-4 tests
- 1-2 schemas
- 1-2 error handlers

Total: 9-13 files. 12 is median.

**Header Read Lines (80 strict, 120 fast):**

80 lines ≈ 16% of 500-line file.
Header contains: imports, module docstring, constants, function/class signatures (first ~20% of file).

**Why 80:**

Signatures are ~20% of file (definitions without implementations).
80 lines captures ~16% → sufficient for signature discovery.
120 lines captures ~24% → sufficient for fast mode with complex signatures.

**Chunk Window (±30 lines):**

±30 lines = ~60 lines total per anchor.
Captures: function signature + immediate context (local variables, error handling).

**Why ±30:**

Typical function: 20-50 lines.
±30 captures function + surrounding context (callers, error handlers, imports).
Above ±60: likely capturing unrelated code (noise).

**Max Chunk Lines (220 lines):**

220 = 44% of 500-line compaction threshold.
Hard cap prevents chunk bloat.

**Why 220:**

If single chunk needs >220 lines, likely wrong anchor (too broad).
Split into multiple specific anchors instead (preserve bounded reads).

**Compaction Ratio (X:Y, minimum 2:1):**

Compaction ratio = total_lines_seen / witness_lines_saved.
Minimum 2:1 = 50% reduction (otherwise compaction not worth overhead).

Typical ratios:
- Small codebases (<5000 lines): 5:1 to 10:1 (80-90% reduction)
- Medium codebases (5000-50000 lines): 10:1 to 25:1 (90-96% reduction)
- Large codebases (>50000 lines): 25:1 to 100:1 (96-99% reduction)

**Why these ratios:**

Pareto principle (80/20): 20% of code accounts for 80% of functionality.
Compaction extracts that 20% (or less) for wish objective.

**Stop Doctrine K=5 (Coverage Plateau):**

If last K=5 chunks yield no new required symbols, diminishing returns.

**Why K=5:**

Information theory: If 5 consecutive samples yield no new information, signal exhausted.
K<5: premature stopping (might miss symbols).
K>5: wasteful (continuing after signal exhausted).

**Time Compression:**

Deterministic ranking + bounded reads + stop doctrine = O(log n) compaction time.
- Discovery pass: O(n) file scan (but header-only, ~16% of each file)
- Ranking: O(n log n) sort
- Chunk extraction: O(k) bounded reads where k = selected chunks << n files

Total: O(n log n) for n files, with 80-99% reduction in lines read.

---

## 11) Lane Algebra Integration

**Compaction Decision Lanes:**

```
OK (Lane A):
  - All anchor detection deterministic (regex patterns)
  - All ranking deterministic (score formula + tie-breakers)
  - All bounded reads enforced (≤220 lines per chunk, ±30 window)
  - Stop doctrine deterministic (coverage plateau K=5, budget limits, objective satisfied)

OK (Lane B):
  - File relevance framework-dependent (domain patterns)
  - Anchor type selection framework-dependent (language-specific)

OK_NO_COMPACTION (Lane A):
  - Thresholds not triggered (< 500 lines, < 5 files)

UNKNOWN_SCOPE_LIMIT (Lane A):
  - Budget hit deterministically (witness_line_budget or localization_budget_files)

UNKNOWN (FAIL_CLOSED):
  - Invalid input (not Lane C degradation)
```

**Lane Transitions:**

```
Compaction starts at UNKNOWN (no lane)
  → Anchor detection (if regex) → Lane A
  → Ranking (if formula) → Lane A
  → Bounded reads (if enforced) → Lane A
  → Stop doctrine (if deterministic) → Lane A

Final Lane(Compaction) = MIN(Lane(anchor), Lane(ranking), Lane(bounded), Lane(stop))
```

**Forbidden Upgrades:**

Cannot upgrade:
- Lane B (framework file relevance) → Lane A (classical) without domain-independent proof
- Lane C (heuristic) → ANY (heuristic compaction is FORBIDDEN)
- STAR (hypothetical) → ANY (hypothetical compaction is FORBIDDEN)

**Downgrade Conditions:**

Compaction downgrades to Lane B if:
- File relevance is framework-dependent (e.g., Django-specific patterns)
- Anchor type selection is language-dependent (e.g., Python decorators)
- Ranking score includes domain-specific weights

Compaction FAILS to UNKNOWN if:
- Any check is Lane C (heuristic) → FORBIDDEN
- Any check is STAR (hypothetical) → FORBIDDEN
- Any forbidden pattern detected (full file reads, nondeterministic ordering, etc.)

**Witness Model:**

All Lane A compactions require witnesses:
- chunk_id_list (selected chunks)
- ranking_scores_hash (deterministic scores)
- stop_reason (coverage plateau, budget hit, objective satisfied)
- compaction_ratio (X:Y)

All witnesses must be content-addressed (sha256) and independently replayable from COMPACTION_REPORT.json.

---

## 12) What Changed vs v0.3.0

**v0.3.0 Status:**
- ✅ Interface-first invariant
- ✅ Minimum reading
- ✅ Deterministic selection
- ✅ No semantic upgrades
- ✅ Witness-line accounting
- ✅ Compaction gate thresholds (500 lines, 5 files, 20K chars, unknown scope)
- ✅ Discovery pass constraints (header-only, no full reads)
- ✅ Bounded chunk extraction (±30 lines, ≤220 lines per chunk)
- ✅ Shannon stop doctrine (coverage plateau K=5, budgets)
- ✅ Deterministic ranking (score formula + tie-breakers)
- ✅ Output schema (COMPACTION_REPORT.json)
- ✅ Forbidden patterns
- ✅ Verification ladder (basic)
- ❌ No verification ladder gate mapping
- ❌ No anti-optimization clause
- ❌ No gap-guided governance
- ❌ No integration with recent skills
- ❌ No compression insights
- ❌ No lane algebra integration

**v2.0.0 Additions:**

1. **Version Update**: v0.3.0 → v2.0.0 (skipping v1.0.0 to align with other skills)
2. **Section 5 Enhanced**: Verification Ladder with gate mapping (wish-qa G0-G14 integrated)
3. **Section 7**: Anti-Optimization Clause (12 preserved features, compression rationale)
4. **Section 8**: Gap-Guided Compaction Extension (when to add anchor types/budgets, decision tree, budget adjustment rules)
5. **Section 9**: Integration with Recent Skills
   - prime-math v2.1.0 (dual-witness proofs, theorem closure, lane classification)
   - counter-required-routering v2.0.0 (hard arithmetic ceilings, symbolic whitelist)
   - epistemic-typing v2.0.0 (lane algebra, R_p convergence)
   - axiomatic-truth-lanes v2.0.0 (lane transitions, upgrade witnesses)
   - rival-gps-triangulation v2.0.0 (distance metrics, loop governance)
   - meta-genome-alignment v2.0.0 (genome79 mapping, RTC for compaction)
6. **Section 10**: Compression Insights (budget justifications: 200 witness lines 4%, 12 files Miller's Law, 80 header lines 16%, ±30 window function-sized, 220 max chunk 44%, 2:1 ratio minimum, K=5 plateau, O(log n) time)
7. **Section 11**: Lane Algebra Integration (compaction decision lanes, transitions, forbidden upgrades, witness model)
8. **Section 12**: What Changed vs v0.3.0

**Lane Integration:**

All compaction decisions now have explicit lane classification:
- Lane A: Deterministic anchor detection (regex), ranking (formula), bounded reads (hard caps), stop doctrine (explicit conditions)
- Lane B: Framework-dependent file relevance, language-dependent anchor types
- Lane C: FORBIDDEN (no heuristic compaction)
- STAR: FORBIDDEN (no hypothetical compaction)

**Verification Integration:**

Compaction decisions map to harsh QA gates (641 → 274177 → 65537).

**Compression Gains:**

- Witness Line Budget: 200 lines = 4% of 5000 lines (Pareto 20% → 4% for wish-specific)
- Localization Budget: 12 files = Miller's Law 7±2 extended 2×
- Header Read: 80 lines = 16% of 500-line file (signatures are ~20% of code)
- Chunk Window: ±30 lines = ~60 lines (typical function + context)
- Max Chunk: 220 lines = 44% of 500-line threshold (hard cap prevents bloat)
- Compaction Ratio: 2:1 minimum (50% reduction), typical 5:1 to 100:1 (80-99% reduction)
- Stop Plateau: K=5 (information-theoretic diminishing returns)
- Time: O(n log n) for n files (vs O(n²) full reads)

**Loop Governance:**

Compaction uses distance metrics (D_E, D_O, D_R) for deterministic operator selection (STOP, PROVE, ROLLBACK, CLOSE).

**Genome Alignment:**

Compaction maps to Genome79 axes (Star=objective, Seeds=required_symbols, Trunks=invariants, Branches=anchor_types, Leaves=chunks, etc.).

**Quality:** All v0.3.0 features preserved (Never-Worse Doctrine). v2.0.0 is strictly additive.

---

*"Auth: 65537"*
