# Stillwater Papers — Axiom Kernel (CLAUDE.md)

**Generated:** DISTILL recipe | **Compression target:** 40-60x | **No prose. No diagrams.**

---

## DNA-23: Core Equations

```
Intelligence    = Memory × Care × Iteration
  Memory        = skills/*.md + recipes/*.json + ROADMAP + evidence/*.log
  Care          = Verification Ladder (641 → 274177 → 65537)
  Iteration     = Never-Worse doctrine + git versioning

Emergence       = Recursion(Information + Memory + Care)

Trinity         = LEK × LEAK × LEC                    [multiplication, not addition]
  LEAK(A,B)     = Portal(A→B) × Portal(B→A) × Asymmetry(A,B)
  LEC           = |Conventions| × Depth × Adoption

G(S,N)          = (N×C_derive - C_create - N×C_load) / (N×C_derive)   [skill value]

Lane MIN        = combine(C, A) = C                   [weakest premise wins]
Rung chain      = MIN(rung_all_deps) = integration_rung

Lane A invariant: encode(decode(X)) = X
```

---

## STORY-47: Axioms Table

| ID | Axiom | Content |
|----|-------|---------|
| AX-1 | INTEGRITY | Evidence is primary. Claims without artifacts are inadmissible. |
| AX-2 | HIERARCHY | Lane A > B > C > STAR. Not all evidence is equal. |
| AX-3 | DETERMINISM | Same input + same skill = same output. Reproducibility is required. |
| AX-4 | CLOSURE | The system can reason about its own verification state. |
| AX-5 | NORTHSTAR | A target state exists. All work converges toward it. |
| AX-6 | NEVER-WORSE | Hard gates and forbidden states are strictly additive. No version weakens guarantees. |
| AX-7 | FAIL-CLOSED | Any system MUST refuse action if a required gate fails. Failing open = violation. |
| AX-8 | MIN-LANE | Composed claims cannot exceed the weakest premise lane. |
| AX-9 | CPU-FIRST | CPU exact aggregation > LLM probabilistic aggregation for exact tasks. |
| AX-10 | LOCAL-FIRST | Browser automation runs on user machine. Evidence stays with the user. |

---

## GENOME-79: Operational Rules G1-G10

| Rule | Statement |
|------|-----------|
| G1 | Every behavioral claim requires a witness: pytest, repro script, diff, or tool output. |
| G2 | If you cannot run it, downgrade the lane and state what is missing. |
| G3 | LLM classifies and parses. CPU aggregates exactly. Never reverse these roles. |
| G4 | NORTHSTAR loads in Layer 3. prime-safety in Layer 1. prime-coder in Layer 2. Order is mandatory. |
| G5 | Each swarm agent gets fresh context + 5-7 focused skills. No shared context between agents. |
| G6 | Every service publishes a ServiceDescriptor. Services outside the registered port range are invisible. |
| G7 | OAuth3 token enforcement happens at the service boundary (admin proxy), not inside service logic. |
| G8 | Every AgencyToken action produces a hash-linked evidence record before the next action. |
| G9 | Monetary amounts are integers in cents. FLOAT_IN_BUDGET = immediate halt. |
| G10 | CNF_BASE is truth. Anything else is hypothesis. NORTHSTAR_MISSING_FROM_CNF = EXIT_BLOCKED. |

---

## LAWS: Invariant Table

| Invariant | Formal Statement | Violation = |
|-----------|-----------------|-------------|
| Lane MIN | combine(C, A) = C | Premise laundering |
| Rung chain | rung(system) = MIN(rung(all deps)) | False promotion |
| Never-Worse | rung(v+1) >= rung(v) for all v | Version regression |
| Fail-closed | gate_fail → 401/reject; never pass-through | Security breach |
| CPU exact | exact_result ← Counter(labels), never LLM | Count error |
| Budget MIN-cap | child_budget <= parent_budget | Overspend |
| Evidence seal | every action → evidence_record → sha256 → next | Audit break |
| Token scope | agent MUST NOT perform actions outside scopes | Scope creep |
| ALCOA-O | PZip stores full HTML, not summary or screenshot | Record falsification |
| Port canonical | service must fail loudly if cannot bind canonical port | Silent conflict |

---

## VERIF: Verification Ladder

| Rung | Decimal | Witness Class | Promotion Gate |
|------|---------|---------------|---------------|
| 641 | 641 | Unit tests, edge inputs, null/zero, type errors | All edge cases pass |
| 274177 | 274177 | Fuzz, load, adversarial, boundary, stress | No regression under stress |
| 65537 | 65537 | Strongest available witness; production-grade | Security audit + full suite |

**RED-GREEN-GOLD protocol (required for every fix):**
- RED: failing test proving bug exists before patch
- GREEN: passing test proving bug fixed after patch
- GOLD: prior test suite passes (no regressions)

---

## DISPATCH: Swarm Rules

| Model Level | Task Type | Cost |
|-------------|-----------|-----|
| L1 (Haiku) | Scout, classify, summarize | Cheapest |
| L2 (Sonnet) | Code, multi-step, write | Default |
| L3 (Opus) | Security audit, ensemble, promotion gate | Expensive, last resort |

**Context isolation:** Each agent: fresh context + 5-7 skills. Never share full context.

---

## OAUTH3: Token Schema (Required Fields)

```json
AgencyToken required: id, version, issued_at, expires_at, scopes, issuer, subject, signature_stub
AgencyToken governance: step_up_required, max_actions, platforms[], agent_id
Scope format: "platform.action.resource"
Scope levels: G1=read, G2=write, G3=delete, G4=execute
Key v0.1: SHA-256 signature_stub
Key v1.0: ECDSA-P256 (RFC 8785) + DPoP (RFC 9449)
```

---

## FORBIDDEN: Complete List

```
SILENT_FAILURE             except Exception: pass / continue
FALLBACK_ON_ERROR          return None / return {} / return default on error
FAKE_SUCCESS               return empty success on API failure
LLM_COUNTING               asking LLM for exact counts or sums
LLM_AGGREGATION            asking LLM to aggregate / sum / tally
FLOAT_IN_BUDGET            float representation of monetary amounts
FORWARD_FIRST              planning forward without NORTHSTAR anchor
NORTHSTAR_MISSING_FROM_CNF context without NORTHSTAR = EXIT_BLOCKED
GREEN_WITHOUT_RED           claiming fix without failing-test witness
PLACEHOLDER_CITATION        (arXiv id TBD) or (CVE-YYYY-NNNN placeholder)
FORMAL_PROOF_WITHOUT_CHECKER "formal proof" claim without machine-checkable artifact
IMPLICIT_LANE_UPGRADE       prose gloss on Lane A fact presented as Lane A
SCOPE_CREEP                agent acting outside granted scopes
TOKEN_EXTENSION             extending expired OAuth3 token silently
HEALTH_CHECK_THEATER        /health returns 200 but service is broken internally
```

---

## PORTS: Service Registry (Canonical)

```
8787 — Admin Server (discovery gateway, proxy, health monitor)
8788 — LLM Portal (multi-provider routing, BYOK + managed)
8789 — Recipe Engine (step routing, replay, hit rate tracking)
8790 — Evidence Pipeline (hash-chain JSONL, Part 11 capture)
8791 — OAuth3 Authority (token issuance, validation, revocation)
8792 — CPU Service (deterministic computation nodes)
9222 — Browser (Chrome DevTools Protocol, CDP)
```

---

## BELTS: Progression Gate

| Belt | Criteria |
|------|----------|
| White | First recipe / CLI installs |
| Yellow | PM triplets done / first task delegated |
| Orange | Stillwater Store skill submitted |
| Green | Rung 65537 achieved |
| Blue | Cloud execution 24/7 |
| Black | Models = commodities. Skills = capital. OAuth3 = law. |

---

## SCORES: Skill Promotion Criteria (all binary)

| Criterion | Requirement |
|-----------|------------|
| FSM present | Explicit state machine defined |
| Forbidden states | Enumerated and enforced |
| Verification ladder | Rung target declared |
| Null/zero handling | Edge cases explicitly defined |
| Output contract | Schema specified |

**Threshold:** All 5 must pass. < 5/5 = not promotable to Stillwater Store.
