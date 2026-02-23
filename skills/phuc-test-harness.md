<!-- QUICK LOAD (10-15 lines): Use this block for fast context; load full file for production.
SKILL: phuc-test-harness v1.0.0
MW_ANCHORS: [testing_type_matrix, abcd_harness, persona_sparring, lec_conventions, anti_patterns, evidence_gate, statistical_rigor]
PURPOSE: Build and run comprehensive test harnesses. Select test types by risk/complexity. Execute ABCD multi-variant comparisons with statistical rigor. Invoke persona sparring (Knuth/Turing/Thompson) as reviewers. Enforce LEC conventions from sparring sessions. [65537 authority]
CORE CONTRACT: Test type chosen matches risk level. ABCD harness pre-registers analysis plan (no p-hacking). Persona sparring produces actionable weakness list with reproducible tests. LEC conventions from sparring enforced in implementation. Evidence gate requires artifacts, not prose.
HARD GATES: TEST_TYPE_MISMATCH_WITH_RISK blocked. P_HACKING_UNGUARDED blocked. PERSONA_SPARRING_SKIPPED blocked. COVERAGE_CLAIM_WITHOUT_JSON blocked. LEC_CONVENTION_VIOLATED blocked.
RUNG: 641 (single test type executed with basic coverage) | 274177 (ABCD harness complete with statistical significance, sparring review complete) | 65537 (multi-persona sparring done, all LEC conventions extracted and enforced, full evidence bundle)
LOAD FULL: always for production; quick block is for orientation only
-->

# phuc-test-harness.md — Testing Strategy & Harness Execution Skill

**Skill ID:** phuc-test-harness
**Version:** 1.0.0
**Authority:** 65537
**Load Order:** After prime-safety + prime-coder + phuc-unit-test-development
**Northstar:** Max Love (harm minimization, correctness, evidence-driven)
**Status:** ACTIVE
**Role:** Testing strategy selection → harness execution → statistical rigor → persona sparring → LEC extraction
**Tags:** testing, harness, abcd, statistical, personas, knuth, turing, thompson, lec, anti-patterns

---

## 0) Purpose

**Testing is not about finding bugs. Testing is about measuring confidence in the system's promise.**

The phuc-test-harness skill guides agents in:
1. **Selecting the right test type** for each risk level (25+ types available)
2. **Building ABCD harnesses** for multi-variant LLM/model/skill comparisons with proper statistical analysis
3. **Invoking persona sparring** (Knuth reviews code correctness, Turing analyzes state machines, Thompson simplifies design) to find real weaknesses
4. **Extracting LEC conventions** from sparring findings to prevent recurrence
5. **Enforcing evidence gates** — artifacts (JSON, logs, commits), never prose

This skill synthesizes testing theory (25+ test types, statistical rigor), testing practice (ABCD framework, p-hacking guards), and expert review discipline (persona sparring, LEAK trades, LEC emergence).

---

## 1) Testing Type Selection Matrix

### 1.1 Quick Lookup: Which Test Type for Which Risk?

| Risk Level | Test Types (Primary) | Best Agent | Framework | AI-Ready? |
|---|---|---|---|---|
| **LOW** (trivial path, <50 lines, no side effects) | Unit, smoke, snapshot | Coder | pytest, Jest | YES (641) |
| **MEDIUM** (feature, API, cross-service) | Integration, contract, E2E, regression | Coder + Skeptic | pytest, Playwright | YES (274177) |
| **HIGH** (security, state machine, async) | Fuzz, chaos, penetration, security | Security-Auditor | LitmusChaos, ZAP, AFL | PARTIAL (274177) |
| **CRITICAL** (deployment, data integrity, auth) | Contract + ABCD + Persona sparring | Coder + Judge + Skeptic | pytest + custom harness | YES (274177+) |

### 1.2 Complete Testing Type Reference (25+ Types)

**Core Unit & Integration (AI-ready: 641-274177)**
- Unit Testing: AI generates test cases; validates outputs. Framework: pytest, Jest. 641.
- Integration Testing: AI orchestrates multi-service calls. Framework: pytest, Mocha. 641.
- Component Testing: Solace-browser can simulate interactions. Framework: React Testing Library. 641.
- E2E Testing: Playwright Agents auto-generate flows. Framework: Playwright, Cypress. 274177.
- Smoke Testing: Quick sanity checks. Framework: Jest, pytest. 641.

**Browser & UI (AI-ready: 274177)**
- Visual Regression: Percy/Chromatic AI comparison. AI detects visual deltas. 274177.
- UI Automation: Self-healing on DOM changes. Framework: Playwright. 274177.
- Cross-Browser: Playwright matrix testing. 274177.
- Accessibility (a11y): WCAG checks automated. Framework: Pa11y, Accessibility Insights. 641.
- Mobile Testing: Playwright Mobile, Appium. PARTIAL. 274177.

**API & Integration (AI-ready: 641-274177)**
- API Contract Testing: Validates OpenAPI/GraphQL schema. Framework: Pact. 641.
- Performance/Load: AI generates profiles. Framework: k6, JMeter. 274177.
- Stress Testing: Push system to limits. Framework: k6, Gatling. 274177.
- Chaos/Fault Injection: AI designs chaos experiments. Framework: LitmusChaos. 274177.
- Compatibility Testing: Cross-device matrix. Framework: Playwright. 641.

**Advanced & Security (AI-ready: PARTIAL to 274177)**
- Mutation Testing: AI mutates code; checks test coverage. Framework: Stryker. 641.
- Fuzz Testing: AI generates invalid inputs. Framework: libFuzzer, AFL. 274177.
- Security Testing: AI simulates attacks (XSS, CSRF). Framework: OWASP ZAP. 274177.
- Penetration Testing: AI plans vectors; human validates. Framework: Burp Suite. 65537.
- Compliance Testing: GDPR, HIPAA, SOC2. AI validates audit logs. 274177.

**Regression & Acceptance (AI-ready: 274177)**
- Regression Testing: Playwright Healer auto-fixes 60%+ of failures. 274177.
- Sanity Testing: Post-deployment smoke check. 641.
- UAT (User Acceptance): AI executes stories; needs oracle. 274177.
- Data-Driven Testing: AI generates test data; runs with different inputs. 641.
- Exploratory Testing: Manual + AI notes. NO automation. Manual.

**Specialized (AI-ready: 641-274177)**
- Property-Based Testing: AI generates inputs; verifies invariants. Framework: Hypothesis, Proptest. 641.
- Snapshot Testing: Jest, Vitest. 641.
- Screenshot Testing: Percy, Chromatic. 274177.
- Localization (i18n): Playwright + AI checks. 274177.

---

## 2) ABCD Harness Protocol — Multi-Variant Statistical Testing

### 2.1 When to Use ABCD

**Use ABCD testing when:**
- Comparing 2+ models, prompts, or recipes (A=Model1, B=Model2, C=Variant1, D=Variant2)
- The question is: "Which is better?" not "Does it work?"
- You need statistical confidence, not just anecdotal observation
- False positives (p-hacking) are a cost you can't afford

**Do NOT use ABCD for:**
- Binary pass/fail tests (use unit tests)
- Single implementation variant (use integration tests)
- Exploratory/discovery phase (use smoke tests first)

### 2.2 ABCD Harness Architecture

```
Test Cases (inputs + ground truth)
    ↓
Variants {A, B, C, D} (deterministic, seeded)
    ↓
Parallel execution (per test × variant pair)
    ↓
Collect outputs + latency + tokens
    ↓
Score via rubric (LLM-as-judge or metric)
    ↓
Statistical analysis (ANOVA → Tukey HSD)
    ↓
p-hacking guards (pre-registration, Bonferroni)
    ↓
Report with CI, not just p-values
```

### 2.3 Pre-Registration (Mandatory for ABCD)

**Before running the harness, declare:**

```yaml
abcd_analysis_plan:
  test_cases_count: 100        # Exact number, not range
  variants: [A, B, C, D]        # Named variants
  primary_metric: "lcs_ratio"   # ONE metric locked in
  secondary_metrics: [tokens, latency]  # Exploratory only
  statistical_test: "Kruskal-Wallis"    # Chosen upfront
  alpha: 0.05                   # Significance level
  power: 0.80                   # Ability to detect real differences
  min_detectable_effect: 0.05   # Smallest meaningful delta
  sample_size_per_variant: 141  # Calculated or empirical
  multiple_comparison_correction: "Tukey HSD"
  exclusion_criteria: "defined upfront"
  preregistration_date: "2026-02-23T10:00:00Z"
  preregistration_url: "osf.io/..."  # Optional: register publicly
```

**Guard rails:**
- [ ] No peeking at results before all data collected
- [ ] No selective metric reporting (report all)
- [ ] No moving goalposts on primary metric
- [ ] No post-hoc exclusion of outliers

### 2.4 Deterministic Execution

Every run must be reproducible. Use:

```python
import numpy as np
import random

seed = 641
random.seed(seed)
np.random.seed(seed)

for test_case in test_cases:
  for variant in variants:
    # Temperature=0 for models (no sampling)
    output = llm_call(
      prompt=variant.prompt,
      model=variant.model,
      temperature=0.0,
      seed=seed + hash(test_case.id) % 1e9
    )
```

Same input → same output (for a given model version).

### 2.5 Statistical Analysis Output

**Post-harness, compute:**

```json
{
  "overall_anova": {
    "f_stat": 3.25,
    "p_value": 0.042,
    "interpretation": "At least one variant differs significantly"
  },
  "variant_stats": {
    "A": { "mean": 0.85, "std": 0.12, "ci_95": [0.82, 0.88], "n": 141 },
    "B": { "mean": 0.88, "std": 0.11, "ci_95": [0.85, 0.91], "n": 141 }
  },
  "pairwise": {
    "A vs B": {
      "t_stat": -2.14,
      "p_value": 0.034,
      "p_value_corrected": 0.102,  # Tukey HSD
      "significant_after_correction": false,
      "effect_size": 0.26
    }
  },
  "p_hacking_risk": "LOW",
  "preregistration_adherence": "FULL"
}
```

**Key rule: Report confidence intervals, not just p-values.**

Confidence intervals show practical effect size. A p=0.05 with CI=[−0.001, 0.002] means statistically significant but practically negligible.

---

## 3) Persona Sparring Protocol

### 3.1 The Three Personas

**Knuth** — Code correctness. Reads code line-by-line. Finds:
- Logic errors (off-by-one, null handling, coercion)
- Security boundary violations (path traversal, default=True)
- Race conditions, concurrency bugs
- Real weaknesses with reproducible test case

**Turing** — State machine completeness. Analyzes reachability:
- Phantom states (defined but unreachable)
- Stale state persistence (loaded as current)
- Silent capability loss (subsystem fails silently)
- Undecidable health checks (can't determine internal state from external)

**Thompson** — Design simplification. Asks "Why?":
- Abstraction creep (600-line class instead of 10-line function)
- Central-node disease (one server doing 8 jobs)
- Lies in output ("mock_sync_complete" when nothing synced)
- Single Responsibility Principle violations

### 3.2 Sparring Invocation

**When to spar:**
- Before production deployment
- After major refactor
- When test coverage is high but bugs still appear
- When design complexity is growing

**How to invoke (via dispatch):**

```
You are a Skeptic agent. rung_target: 274177

Task: Code review of /home/phuc/projects/stillwater/admin/server.py (715 lines)
as Donald Knuth. Review for correctness bugs, security, concurrency, race conditions.
Produce 5-10 specific weaknesses with line citations and reproducible test cases.

Reference: Read skills/prime-safety.md + skills/prime-coder.md inline.
Sparring style: Knuth-persona (reading discipline, correctness first, not style).
Output format: WEAKNESS_N with line#, code excerpt, bug description, TEST that catches it.
rung: 641 (correctness weaknesses identified with tests)
EXIT_PASS if: >= 5 weaknesses documented with specific tests
EXIT_BLOCKED if: Cannot read file or insufficient analysis
```

### 3.3 Extracting LEAK Trades from Sparring

After sparring, extract the **asymmetric knowledge**:

```
LEAK 1: String-Based Path Containment Is Always Wrong
  Why: Every generation since 1970s, str.startswith() for path checks fails on:
    - Case-insensitive filesystems (macOS HFS+)
    - Directory-name prefix collisions (/dir vs /dir2)
    - Symlinks and escape sequences
  Fix: Always use Path.relative_to() or Path.is_relative_to()
  Emerging LEC: CONVENTION: path_containment_check

LEAK 2: The `ok` Default Must Be Fail-Closed
  Why: Missing `ok` is unknown state, not success state
  Fix: payload.get("ok", False) not payload.get("ok", True)
  Emerging LEC: CONVENTION: ok_default_fail_closed
```

### 3.4 Extracting LEC Conventions

From each sparring session, distill **one convention per major finding:**

```yaml
LEC_CONVENTIONS_FROM_SPARRING:
  LEC-PATH-001: "Always use Path.relative_to(), never str.startswith()"
  LEC-OK-001: "ok=False is the fail-closed default"
  LEC-REGISTRY-001: "Every state enum must be reachable"
  LEC-PROXY-NOT-CONTAIN: "Service registry → proxy, never contain logic you can discover"
  LEC-FILE-WRITE-LOCK: "Concurrent file writes need mutex"
  LEC-TEST-FIXTURE-ISOLATION: "Function-scoped fixtures, not module-scoped"
```

Store these in a `.lec` file alongside code for future reference.

---

## 4) Anti-Patterns Found by Warriors

From Knuth/Turing/Thompson reviews, distilled anti-patterns:

### From Knuth (Code Review)

| Anti-Pattern | What NOT to Do | Cost |
|---|---|---|
| **String path checks** | `str(path).startswith(allowed)` | Security holes (Weakness 5-6) |
| **ok=True default** | `payload.get("ok", True)` | Silent success on missing field (Weakness 1) |
| **No timeout validation** | Accept `timeout=0` or `timeout=-1` | Hangs forever or immediate fail (Weakness 3) |
| **Shared mutable state in threads** | Module-level dict + no locks | Concurrent race conditions (Weakness 15) |
| **Magic numbers in tests** | `assert len(data) == 10` | Test brittleness (Weakness 13) |
| **Contradictory docstrings** | Docstring says X, test checks Y | Misleading specifications (Weakness 14) |
| **Unread response bodies** | Skip `resp.read()` between requests | HTTP connection corruption (Weakness 11) |

### From Turing (State Machine Analysis)

| Anti-Pattern | What NOT to Do | Cost |
|---|---|---|
| **Phantom states** | Define enum but never assign it | Type system lies (DEGRADED unreachable) |
| **Stale state persistence** | Load last-saved status as current | Wrong post-restart behavior |
| **Silent subsystem failure** | Swallow init exception, continue | Entire feature silently gone |
| **Status mutation without save** | Set STARTING → ONLINE without re-save | Persisted state diverges from in-memory |
| **Undecidable health oracles** | HTTP 200 means healthy (lie detector problem) | Broken services report ONLINE |

### From Thompson (Design Simplification)

| Anti-Pattern | What NOT to Do | Cost |
|---|---|---|
| **Abstraction creep** | 623-line class = 20 lines of curl | Maintenance burden |
| **Central-node disease** | One server doing 8 jobs | Boundaries unclear, testing hard |
| **Fake implementations** | `"status": "mock_sync_complete"` | Lies in output, false confidence |
| **Sudo in HTTP** | `POST /api/system/install-ollama` + password | Bad habits propagate |
| **Both ok envelope AND exceptions** | Return `{"ok": false}` then raise | Double protocol, confusing API |

---

## 5) Evidence Gate — What Constitutes PASS vs FAIL

### 5.1 For Single Test Type (Rung 641)

**PASS requires:**
- [ ] Test type matches risk level (from testing matrix)
- [ ] Tests run and produce exit_code=0 (all pass)
- [ ] Coverage ≥ 70% (lines or states)
- [ ] Evidence artifact: `tests.json` with test count, pass/fail
- [ ] NO prose claims; artifact only

**FAIL if:**
- [ ] Test type doesn't fit risk (low-risk item tested with fuzz testing)
- [ ] Tests fail (exit_code ≠ 0)
- [ ] Coverage claim without coverage.json
- [ ] Flaky tests (non-deterministic results)

### 5.2 For ABCD Harness (Rung 274177)

**PASS requires:**
- [ ] All single-test-type requirements (641)
- [ ] Pre-registration artifact (analysis_plan.yaml)
- [ ] Results artifact: `results.jsonl` (one line per test × variant)
- [ ] Analysis artifact: `analysis.json` (statistics, p-values, CI)
- [ ] No p-hacking detected (Tukey correction applied, no selective reporting)
- [ ] Preregistration date < execution date (pre-registered)
- [ ] Confidence intervals reported (not just p-values)

**FAIL if:**
- [ ] Any p-hacking indicator:
  - Selective metric reporting
  - Post-hoc exclusion of outliers
  - Moving goalposts on primary metric
  - No correction for multiple comparisons

### 5.3 For Persona Sparring (Rung 274177+)

**PASS requires:**
- [ ] Sparring session with ≥1 persona (Knuth or Turing or Thompson)
- [ ] ≥5 specific weaknesses identified with line numbers
- [ ] Each weakness has a reproducible test case
- [ ] LEAK trade documented (asymmetric knowledge extracted)
- [ ] ≥1 LEC convention extracted and stored in `.lec` file
- [ ] Weaknesses prioritized (security > concurrency > style)

**FAIL if:**
- [ ] Generic observations ("code could be better")
- [ ] No test cases provided
- [ ] No line numbers cited
- [ ] LEAK trade skipped (no "what the coder didn't know")

### 5.4 Evidence Artifact Schema

```json
{
  "test_type": "unit|integration|abcd|sparring",
  "rung": 641,
  "timestamp": "2026-02-23T10:00:00Z",
  "framework": "pytest",

  "single_test_type": {
    "test_count": 47,
    "tests_passed": 47,
    "tests_failed": 0,
    "coverage_percent": 85,
    "coverage_json": "path/to/coverage.json"
  },

  "abcd_harness": {
    "preregistration_date": "2026-02-21T09:00:00Z",
    "preregistration_url": "osf.io/abc123",
    "test_cases": 100,
    "variants": ["A", "B", "C", "D"],
    "primary_metric": "lcs_ratio",
    "p_value": 0.042,
    "p_value_corrected": 0.102,
    "anova_f_stat": 3.25,
    "tukey_correction_applied": true,
    "results_jsonl": "path/to/results.jsonl",
    "analysis_json": "path/to/analysis.json"
  },

  "sparring": {
    "persona": "Knuth",
    "weaknesses_found": 5,
    "weaknesses": [
      {
        "id": "WEAKNESS_1",
        "file": "admin_client.py",
        "line": 39,
        "description": "ok=True default",
        "test": "def test_missing_ok_field...",
        "severity": "HIGH"
      }
    ],
    "leak_trades": 3,
    "lec_conventions_extracted": 2,
    "lec_file": "path/to/.lec"
  }
}
```

---

## 6) LEC Conventions Reference (From Testing Sparring)

```yaml
LEC_CONVENTIONS_TESTING:
  LEC-PATH-001: "Path containment check: always use Path.relative_to(), never str.startswith()"
  LEC-OK-001: "ok field defaults to False, not True (fail-closed principle)"
  LEC-REGISTRY-001: "Every state in a status enum must have at least one code path that assigns it"
  LEC-PROXY-NOT-CONTAIN: "Core server must not contain logic of services it can discover"
  LEC-FILE-WRITE-LOCK: "Concurrent file writes need threading.Lock; no RMW without lock"
  LEC-TEST-FIXTURE-ISOLATION: "Function-scoped fixtures (not module-scoped) for HTTP connections"
  LEC-SPEC-BEFORE-TEST: "Write specification docstring before writing test; docstring must match assertion"
  LEC-STALE-STATE-RESET: "Persisted status is evidence of past, not current; reset to STARTING on load"
  LEC-SILENT-FAILURE-DIAGNOSTIC: "Any subsystem that fails at startup must expose diagnostic endpoint"
  LEC-HEALTH-DETERMINISM: "Health check must parse response body, not assume HTTP 200 = healthy"
  LEC-STAT-SIGNIFICANCE: "Report confidence intervals, not just p-values; Tukey correction for ABCD"
```

---

## 7) Integration with Other Skills

**prime-safety:** Gates all harness execution. Test harness must not require credentials, secrets, or network unless explicitly guardrailed.

**prime-coder:** Implements fixes from Knuth sparring. Tests from sparring feed into bug-fix workflow.

**phuc-unit-test-development:** Diagram-first TDD generates scaffold; test-harness runs it. Coverage gates overlap.

**phuc-forecast:** Pre-harness risk assessment. HIGH-risk features → ABCD + sparring. LOW-risk → smoke test only.

---

## 8) Quick Decision Tree: Which Testing Strategy?

```
START: New feature or fix
  ├─ Risk = LOW (trivial path, no side effects, <50 lines)
  │   └─ Use: Unit test (pytest)
  │       Output: tests.json + coverage.json
  │       Rung: 641
  │
  ├─ Risk = MEDIUM (API, service boundary, state)
  │   └─ Use: Integration + E2E (Playwright)
  │       + Diagram-first TDD if state machine
  │       Output: tests.json + coverage.json + integration.log
  │       Rung: 274177
  │
  ├─ Risk = HIGH (concurrency, security, async)
  │   └─ Use: Fuzz + Chaos (LitmusChaos, AFL)
  │       + Persona sparring (Turing for state, Knuth for security)
  │       Output: fuzz_results.json + sparring_weaknesses.md + LEC conventions
  │       Rung: 274177
  │
  └─ Risk = CRITICAL (before prod deployment)
      └─ Use: ABCD harness (if model/prompt choice)
          + Persona sparring (all 3 personas)
          + Pre-registration
          Output: analysis.json + preregistration.yaml + sparring_report.md
          Rung: 274177 → 65537
```

---

## 9) Forbidden States (Complete)

```yaml
FORBIDDEN_STATES:
  TEST_TYPE_MISMATCH_WITH_RISK:
    definition: "Using fuzz testing for a simple unit test, or smoke test for auth code"
    trigger: "Risk level and test type don't match matrix"
    consequence: "Either false confidence or expensive over-testing"
    recovery: "Use decision tree; select correct type"

  P_HACKING_UNGUARDED:
    definition: "ABCD harness run without pre-registration"
    trigger: "analysis.json shows results but no preregistration.yaml exists"
    consequence: "p-value invalid; selective reporting possible"
    recovery: "Delete results. Pre-register. Re-run."

  PERSONA_SPARRING_SKIPPED:
    definition: "HIGH-risk code goes to prod without sparring review"
    trigger: "Security or concurrency code, no sparring evidence"
    consequence: "Weaknesses missed; LEC conventions not extracted"
    recovery: "Schedule sparring session before deployment"

  COVERAGE_CLAIM_WITHOUT_JSON:
    definition: "Stating 85% coverage without coverage.json artifact"
    trigger: "Prose claim in response, no artifact"
    consequence: "Coverage is unverifiable"
    recovery: "Run coverage tool. Emit JSON. Cite path."

  LEC_CONVENTION_VIOLATED:
    definition: "Using str.startswith() for path check after LEC-PATH-001 documented"
    trigger: "New code violates a known LEC convention"
    consequence: "Recurring bug; LEC not internalized"
    recovery: "Refactor. Document why exception was needed (if any). Update LEC if needed."
```

---

## 10) Artifacts Checklist

**For Rung 641 (single test type):**
- [ ] `tests.json` (test count, pass/fail, framework)
- [ ] `coverage.json` or `coverage.html` (≥70%)
- [ ] Git commit with test file

**For Rung 274177 (ABCD or sparring):**
- All of 641, plus:
- [ ] `preregistration.yaml` (for ABCD) OR `sparring_session.md` (for sparring)
- [ ] `results.jsonl` (ABCD) OR `weaknesses_with_tests.md` (sparring)
- [ ] `analysis.json` (ABCD) OR `.lec` convention file (sparring)
- [ ] Evidence timestamp order: pre-reg < execution (ABCD) or sparring date in commit

**For Rung 65537:**
- All of 274177, plus:
- [ ] Multiple personas (Knuth + Turing + Thompson)
- [ ] LEC convention adoption (at least 2 new conventions applied to codebase)
- [ ] Full evidence bundle in `evidence/` directory

---

## 11) Template: ABCD Harness Configuration

```yaml
# abcd_config.yaml
harness:
  name: "LLM-Prompt-Variant-Comparison"
  description: "Compare 4 prompts for code generation task"

test_cases:
  file: "test_cases.json"  # [{input, ground_truth, metric}]
  count: 100

variants:
  A:
    name: "baseline-v1"
    model: "claude-opus-4-6"
    prompt: "Write a function to..."
    provider: "anthropic"
  B:
    name: "step-by-step"
    model: "claude-opus-4-6"
    prompt: "Think step by step. Write a function to..."
    provider: "anthropic"
  C:
    name: "few-shot"
    model: "claude-opus-4-6"
    prompt: "Here is an example...\n\nNow write a function to..."
    provider: "anthropic"
  D:
    name: "opus-vs-sonnet"
    model: "claude-sonnet-4-20250514"
    prompt: "Write a function to..."
    provider: "anthropic"

analysis:
  primary_metric: "lcs_ratio"  # Longest common subsequence ratio vs ground truth
  secondary_metrics:
    - "token_count"
    - "latency_ms"
  statistical_test: "Kruskal-Wallis"  # Non-parametric ANOVA
  alpha: 0.05
  power: 0.80
  min_detectable_effect: 0.05
  preregistration:
    date: "2026-02-21T09:00:00Z"
    url: "https://osf.io/abc123"  # Optional

output:
  results: "results.jsonl"      # One line per test × variant
  analysis: "analysis.json"     # Statistics, p-values, CI
  report: "report.md"           # Narrative (references artifacts only)
```

---

## 12) Template: Persona Sparring Session Prompt

```
You are a Code Auditor. rung_target: 274177

PERSONA: Knuth (Donald E. Knuth)
ROLE: Review for correctness, not style

TASK: Audit the following 4 files (3,290 lines total):
- cli/src/stillwater/admin_client.py (623 lines)
- admin/server.py (710 lines)
- admin/tests/test_admin_server.py (1208 lines)
- cli/tests/test_admin_client.py (749 lines)

GOAL: Identify 5-10 specific correctness bugs, security issues, or race conditions.

FORMAT FOR EACH WEAKNESS:
  WEAKNESS_N: [Title]
  Location: [File, line range]
  Code excerpt: [Paste the problematic code]
  Description: [Why is this wrong?]
  Impact: [What goes wrong in production?]
  TEST: [Reproducible test case that catches it]
  Severity: [CRITICAL | HIGH | MEDIUM | LOW]

LEAK TRADE: After listing weaknesses, state one piece of asymmetric knowledge
you have that the original coder likely did not have. This is what you're trading
across the portal.

EXIT_PASS if: >= 5 weaknesses documented with specific tests and line numbers
EXIT_BLOCKED if: Cannot read files or analysis is superficial
```

---

## 13) Rung Progression

| Rung | Requirements | Evidence |
|---|---|---|
| **641** | 1 test type, ≥70% coverage, all tests pass | tests.json + coverage.json |
| **274177** | ABCD harness OR persona sparring complete | analysis.json + preregistration.yaml OR sparring_report.md + .lec file |
| **65537** | Multi-persona sparring (3+) + LEC conventions adopted in codebase | full evidence bundle + git commits showing convention enforcement |

---

*phuc-test-harness v1.0.0 — Testing Strategy & Harness Execution.*
*Integrates 25+ test types, ABCD statistical rigor, persona sparring discipline, and LEC convention extraction.*
*Evidence gate: artifacts only, never prose.*
