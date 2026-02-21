# OAuth3 Wallet: Spending Delegation for AI Agents — Formal Specification

**Document ID:** oauth3-wallet-spec-v0.1
**Version:** 0.1.0
**Status:** DRAFT — Rung 641 (Local Correctness)
**Authors:** Phuc Vinh Truong, Stillwater Project
**Framework:** Stillwater OS v1.4.0
**Date:** 2026-02-21
**Depends on:** oauth3-spec-v0.1 (normative base)
**Repository:** https://github.com/phuctruong/stillwater

---

## Abstract

OAuth3 Wallet extends the OAuth3 agency authorization protocol with structured spending delegation for AI agents. Where the base OAuth3 spec (v0.1) governs _what actions_ an agent may take, OAuth3 Wallet governs _how much an agent may spend_ doing them.

The problem with existing payment rails — Coinbase AgentKit, Stripe ACP, Google AP2, Visa/Mastercard agentic tokens — is that they solve settlement but not delegation. They answer "how does the agent pay?" but not "who authorized the agent to pay, for how much, and with what evidence?" OAuth3 Wallet answers the second question.

This specification defines:
1. Budget token claims extending the base AgencyToken schema
2. The delegation chain protocol with MIN-cap enforcement
3. The budget envelope pattern for per-task spending authorization
4. Settlement rail abstraction (Stripe, x402/USDC, internal credits)
5. Evidence bundles for financial actions (integer-only, chain-linked)
6. Revocation cascade for parent/child token hierarchies
7. Forbidden states enforced at every spending gate

OAuth3 Wallet is not a payment processor. It is an authorization and evidence layer that sits above any payment rail. A principal uses OAuth3 Wallet to delegate bounded financial authority to an agent; the agent uses a settlement rail to execute the payment; the wallet produces a cryptographically chained evidence bundle that proves what was authorized, what was spent, and by whom.

**Lane classification:** This specification is Lane B (framework truth within the OAuth3 axiom system). Implementations that satisfy Section 6 (Evidence Bundle) produce Lane A artifacts.

---

## Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

**Fail-closed rule (hard):** Any system implementing this spec MUST refuse a spending action if any budget gate fails. Failing open (allowing spend on gate error) is a critical violation of this specification.

**Integer rule (hard):** All monetary amounts in this specification MUST be represented as integers in cents (USD) or equivalent minor currency units. Float representation of monetary amounts in any spending gate, evidence record, or delegation chain is a forbidden state (FLOAT_IN_BUDGET). See Section 7.

---

## Table of Contents

1. Motivation
2. OAuth3 Wallet Token Schema (Extended AgencyToken Claims)
3. Delegation Chain Protocol
4. Budget Envelope Pattern
5. Settlement Rails
6. Evidence Bundle for Financial Actions
7. Forbidden States
8. Revocation Cascade
9. Integration with Software 5.0 Verification
10. Competitive Landscape
11. Implementation Roadmap
12. Appendix A: Comparison to Existing Payment Protocols
13. Appendix B: Security Considerations
14. Appendix C: Stillwater Integration

---

## Section 1: Motivation

### 1.1 The Authorization Gap in Agentic Payments

The agentic economy is arriving faster than its authorization infrastructure. In 2025-2026, AI agents are already booking travel, purchasing API credits, and executing microtransactions on behalf of users. Payment networks have responded:

- **Coinbase AgentKit**: Crypto wallet management for AI agents (Base L2, USDC)
- **Stripe ACP (Agent Connect Protocol)**: Stripe-hosted payment accounts for agent workflows
- **Google AP2 (Agent Payment Protocol)**: Budget envelopes within Google Pay ecosystem
- **Visa/Mastercard agentic tokens**: Virtual card numbers with spending controls for AI sessions

Each of these solves a real problem: how does an agent settle payment with a merchant? None of them solve the prior problem: how does a human principal authorize an agent to spend, with what constraints, over what time window, with what evidence, and with the ability to revoke?

This is the authorization gap. It is not a gap in payment rails. It is a gap in agency delegation.

### 1.2 Why Payment Alone is Insufficient

Consider a user who instructs their AI agent: "Book the cheapest flight to New York under $400, economy class only, direct flights only." The agent must:

1. Search for flights (read action, no spend)
2. Select a candidate (no spend)
3. Enter payment information (spend action — up to $400)
4. Confirm booking (irreversible)

Existing payment protocols govern step 3 partially — they can issue a virtual card or USDC payment with a cap. But none of them:

- Enforce that the agent only acts on flight booking platforms (no merchant restriction)
- Require step-up re-consent before the irreversible confirmation (step 4)
- Produce a chained evidence bundle from the original authorization through to the receipt
- Allow the principal to revoke mid-booking if they change their mind
- Enforce that a sub-agent (e.g., a specialized travel booking agent) cannot exceed the parent agent's cap
- Record the specific scope (`travel.book.flight`) that authorized the action

OAuth3 Wallet addresses all of these gaps.

### 1.3 The OAuth3 Foundation

OAuth3 Wallet builds directly on the base OAuth3 specification (oauth3-spec-v0.1). All AgencyToken validation gates (G1: Schema, G2: TTL, G3: Scope, G4: Revocation) apply without modification. OAuth3 Wallet adds five new gates (G5 through G9) covering budget enforcement.

Readers MUST be familiar with oauth3-spec-v0.1 before implementing this extension. The base spec's AgencyToken schema, consent flow, revocation protocol, and evidence bundle format are incorporated by reference.

### 1.4 Design Principles

**Principle 1 — Authorization before settlement.** The OAuth3 Wallet token must be validated before any payment rail is invoked. The payment rail is downstream of authorization, not a replacement for it.

**Principle 2 — Delegation degrades monotonically.** A sub-agent can never have more spending authority than its parent. The MIN-cap rule (Section 3) is non-negotiable.

**Principle 3 — Integer arithmetic for money.** All budget amounts are integers in cents. No floats, no Decimals that might lose precision under division. This mirrors the prime-coder skill's rule: "Null != Zero; float != money."

**Principle 4 — Evidence is not optional.** Every spending action, regardless of size, produces a complete evidence chain from the original authorization to the final settlement proof. A $0.001 micropayment and a $1,000 enterprise purchase produce identically structured evidence bundles.

**Principle 5 — Fail closed.** Budget gate failure means the action is blocked, not deferred or approved-with-warning. The system MUST choose between verifiable safety and functionality; it MUST choose safety.

---

## Section 2: OAuth3 Wallet Token Schema

### 2.1 Extension Approach

OAuth3 Wallet extends the base AgencyToken schema by adding a `wallet` block to the `metadata` field. This approach preserves backward compatibility: base OAuth3 implementations that do not support wallets will treat the `wallet` block as unrecognized metadata and will enforce only the base four gates (G1-G4).

Wallet-aware implementations MUST enforce all nine gates (G1-G9). Any agent operating under a wallet-extended token that ignores the `wallet` block is in violation of this specification.

### 2.2 Wallet Block Schema (JSON)

The `wallet` block is placed inside the AgencyToken's `metadata` field under the key `oauth3_wallet`:

```json
{
  "metadata": {
    "oauth3_wallet": {
      "budget_cap_cents": 40000,
      "per_tx_max_cents": 40000,
      "daily_cap_cents": 40000,
      "budget_spent_cents": 0,
      "payment_rail": "stripe",
      "merchant_allowlist": ["flights.google.com", "kayak.com", "expedia.com"],
      "budget_envelope_id": "env_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "parent_token_id": null,
      "delegation_depth": 0,
      "currency": "USD"
    }
  }
}
```

### 2.3 Wallet Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `budget_cap_cents` | `integer >= 0` | REQUIRED | Total spending cap for this token's lifetime, in cents. Agent MUST halt if `budget_spent_cents >= budget_cap_cents`. |
| `per_tx_max_cents` | `integer >= 1` | REQUIRED | Maximum amount for any single transaction, in cents. Agent MUST reject any transaction attempt exceeding this value. |
| `daily_cap_cents` | `integer >= 1` | REQUIRED | Maximum spend in any rolling 24-hour window, in cents. Computed from the first transaction in the window. |
| `budget_spent_cents` | `integer >= 0` | REQUIRED | Running total of confirmed spend against this token, in cents. Updated by the resource server after each settled transaction. MUST NOT be set by the agent. |
| `payment_rail` | `string` | REQUIRED | Settlement mechanism. MUST be one of: `"stripe"`, `"x402_usdc"`, `"internal_credits"`. |
| `merchant_allowlist` | `array[string]` | OPTIONAL | Domain allowlist for merchant destinations. If present and non-empty, agent MUST NOT transact with any domain not in this list. |
| `budget_envelope_id` | `string (UUID v4)` | REQUIRED | Links spend to a parent budget envelope (Section 4). MUST exist in the envelope registry before token is used. |
| `parent_token_id` | `string (UUID v4) \| null` | REQUIRED | If this is a delegated sub-token, the UUID of the parent token. NULL for root tokens. |
| `delegation_depth` | `integer >= 0` | REQUIRED | Depth in the delegation chain. Root tokens have depth 0. Sub-tokens increment by 1. MUST NOT exceed the system maximum (default: 3). |
| `currency` | `string` | REQUIRED | ISO 4217 currency code. In v0.1, MUST be `"USD"`. Multi-currency support is deferred to v1.0. |

### 2.4 Wallet Gate Definitions (G5 through G9)

All wallet gates run AFTER the base gates (G1-G4). A token that fails any base gate MUST NOT reach the wallet gates.

| Gate | Name | Check | Failure Action |
|------|------|-------|----------------|
| G5: Budget | Budget remaining | `budget_spent_cents + tx_amount_cents <= budget_cap_cents` | BLOCKED: WALLET_BUDGET_EXCEEDED |
| G6: Per-TX | Per-transaction cap | `tx_amount_cents <= per_tx_max_cents` | BLOCKED: WALLET_PER_TX_EXCEEDED |
| G7: Daily | Daily rolling cap | Sum of all `budget_spent_cents` in rolling 24h <= `daily_cap_cents` | BLOCKED: WALLET_DAILY_CAP_EXCEEDED |
| G8: Merchant | Merchant allowlist | `merchant_domain in merchant_allowlist` (only if list is non-empty) | BLOCKED: WALLET_MERCHANT_NOT_ALLOWED |
| G9: Envelope | Envelope validity | `budget_envelope_id` exists, is open, and has remaining capacity | BLOCKED: WALLET_ENVELOPE_INVALID |

All gate failures MUST be appended to `oauth3_wallet_audit.jsonl` with `status: "BLOCKED"` and the specific gate identifier.

### 2.5 Canonical Wallet Token Example

The following is a complete AgencyToken with wallet extension for a travel booking agent:

```json
{
  "$schema": "https://stillwater.dev/schemas/oauth3/agency-token/v0.1.json",
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "version": "0.1.0",
  "issued_at": "2026-02-21T10:00:00Z",
  "expires_at": "2026-02-21T12:00:00Z",
  "scopes": [
    "travel.search.flights",
    "travel.book.flight",
    "travel.read.confirmation"
  ],
  "issuer": "https://solaceagi.com",
  "subject": "user:phuc@example.com",
  "agent_id": "solace-browser:twin:abc123",
  "step_up_required": ["travel.book.flight"],
  "max_actions": 5,
  "platforms": ["flights.google.com", "kayak.com", "expedia.com"],
  "metadata": {
    "solace.session_id": "sess_travel_xyz789",
    "solace.consent_ui_version": "1.0.2",
    "oauth3_wallet": {
      "budget_cap_cents": 40000,
      "per_tx_max_cents": 40000,
      "daily_cap_cents": 40000,
      "budget_spent_cents": 0,
      "payment_rail": "stripe",
      "merchant_allowlist": ["flights.google.com", "kayak.com", "expedia.com"],
      "budget_envelope_id": "env_c3d4e5f6-a7b8-9012-cdef-012345678902",
      "parent_token_id": null,
      "delegation_depth": 0,
      "currency": "USD"
    }
  },
  "signature_stub": "sha256:e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7"
}
```

---

## Section 3: Delegation Chain Protocol

### 3.1 The Problem of Delegation Escalation

When an orchestrating agent (Agent A) spawns a sub-agent (Agent B) to handle a subtask, a fundamental security question arises: what financial authority does Agent B inherit? In naive implementations, Agent B might inherit Agent A's full budget, or worse, receive a separately issued token with an uncorrelated budget — allowing the combined spend of A and B to exceed the principal's actual authorization.

OAuth3 Wallet prevents this through the MIN-cap rule and explicit delegation chain tracking.

### 3.2 The MIN-Cap Rule (Normative)

When Agent A delegates to Sub-Agent B, the following constraints MUST be enforced at delegation time:

```
B.budget_cap_cents    = MIN(A.budget_cap_cents - A.budget_spent_cents, B.requested_budget_cap_cents)
B.per_tx_max_cents    = MIN(A.per_tx_max_cents, B.requested_per_tx_max_cents)
B.daily_cap_cents     = MIN(A.daily_cap_cents - A.daily_spent_cents, B.requested_daily_cap_cents)
B.scopes              = INTERSECTION(A.scopes, B.requested_scopes)
B.merchant_allowlist  = INTERSECTION(A.merchant_allowlist, B.requested_merchant_allowlist)
B.parent_token_id     = A.id
B.delegation_depth    = A.delegation_depth + 1
```

The server issuing the sub-token MUST enforce this computation. An agent MUST NOT self-issue a sub-token that exceeds these constraints.

This mirrors the phuc-orchestration integration rung rule: the quality of integrated output equals the MIN of all contributing sub-agents. Here, the spending authority of a delegation chain equals the MIN of all links in the chain.

### 3.3 Delegation Chain Example

```
Principal authorizes: $400 travel budget

Agent A (orchestrator):
  budget_cap_cents    = 40000  (= $400)
  per_tx_max_cents    = 40000
  delegation_depth    = 0

Agent A delegates to Agent B (flight search specialist):
  budget_cap_cents    = MIN(40000 - 0, 30000) = 30000  (= $300)
  per_tx_max_cents    = MIN(40000, 30000)      = 30000
  delegation_depth    = 1
  parent_token_id     = A.id

Agent B delegates to Agent C (payment executor):
  budget_cap_cents    = MIN(30000 - 0, 30000) = 30000
  per_tx_max_cents    = MIN(30000, 25000)      = 25000  (C requested less)
  delegation_depth    = 2
  parent_token_id     = B.id

Invariant: C.budget_cap_cents <= B.budget_cap_cents <= A.budget_cap_cents <= Principal.authorized_cents
```

### 3.4 Budget Deduction Propagation

When Agent C executes a transaction for 31,500 cents ($315):

1. C's gate G5 checks: `0 + 31500 <= 30000` → BLOCKED: WALLET_BUDGET_EXCEEDED (C's cap is $300)
2. The transaction is rejected before any payment rail is invoked
3. The rejection is logged to the wallet audit trail with the full delegation chain

When Agent C executes a transaction for 28,000 cents ($280):

1. C's gate G5 checks: `0 + 28000 <= 30000` → PASS
2. Transaction settles
3. Resource server updates: `C.budget_spent_cents = 28000`
4. Resource server propagates: `B.budget_spent_cents += 28000` (B's running total)
5. Resource server propagates: `A.budget_spent_cents += 28000` (A's running total)
6. Remaining budget in chain: `A.budget_cap_cents - A.budget_spent_cents = 40000 - 28000 = 12000` ($120)

**Propagation rule:** Spend at any leaf agent MUST be propagated up the delegation chain synchronously before the next gate check in the chain is valid.

### 3.5 Delegation Depth Limit

The default maximum delegation depth is 3. Implementations MAY configure a lower limit. Implementations MUST NOT allow delegation depth to exceed 5.

Rationale: Deep delegation chains make spend attribution complex and increase the attack surface for delegation escalation via many small sub-delegations. Depth 3 covers the realistic orchestrator → specialist → executor pattern.

### 3.6 Delegation Request (POST)

A wallet-aware agent requests a sub-token via:

**Endpoint:** `POST /oauth3/wallet/delegate`

**Request Body (JSON):**

```json
{
  "parent_token_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "requested_budget_cap_cents": 30000,
  "requested_per_tx_max_cents": 30000,
  "requested_daily_cap_cents": 30000,
  "requested_scopes": ["travel.search.flights", "travel.book.flight"],
  "requested_merchant_allowlist": ["kayak.com"],
  "agent_id": "solace-browser:specialist:def456",
  "ttl_seconds": 3600
}
```

**Normative Response (201 Created):**

```json
{
  "status": "delegated",
  "sub_token": { "...full AgencyToken with wallet block..." },
  "delegation_chain": [
    "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "c3d4e5f6-a7b8-9012-cdef-012345678902"
  ],
  "audit_record": "oauth3_delegation_c3d4e5f6.json"
}
```

**Error Responses:**

| HTTP Code | Error Code | Condition |
|-----------|------------|-----------|
| 400 | `WALLET_DELEGATION_EXCEEDS_PARENT` | Requested cap > parent remaining budget |
| 400 | `WALLET_DELEGATION_DEPTH_EXCEEDED` | `parent.delegation_depth >= max_depth` |
| 400 | `WALLET_SCOPE_ESCALATION` | Requested scopes not subset of parent scopes |
| 400 | `WALLET_MERCHANT_ESCALATION` | Requested allowlist not subset of parent allowlist |
| 403 | `WALLET_DELEGATION_FORBIDDEN` | Caller is not the parent token's bound agent |
| 404 | `OAUTH3_TOKEN_NOT_FOUND` | Parent token ID does not exist |

---

## Section 4: Budget Envelope Pattern

### 4.1 Purpose

A budget envelope is a pre-authorized spending container for a specific task. It solves a coordination problem: when an orchestrator spawns multiple agents for a task, each agent needs a slice of the total budget, but the slices must not sum to more than the total. The envelope is the container that enforces this sum.

The pattern is inspired by Google AP2's envelope concept but extends it with OAuth3's evidence requirements and revocation semantics.

### 4.2 Envelope Schema

**Endpoint:** `POST /oauth3/wallet/envelopes`

**Envelope Object:**

```json
{
  "envelope_id": "env_c3d4e5f6-a7b8-9012-cdef-012345678902",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "task_description": "Book cheapest direct flight NYC, economy, under $400",
  "budget_ceiling_cents": 40000,
  "budget_committed_cents": 0,
  "budget_spent_cents": 0,
  "allowed_scopes": ["travel.search.flights", "travel.book.flight"],
  "allowed_merchants": ["flights.google.com", "kayak.com", "expedia.com"],
  "payment_rail": "stripe",
  "time_window_start": "2026-02-21T10:00:00Z",
  "time_window_end": "2026-02-21T12:00:00Z",
  "status": "open",
  "parent_grant_id": "grant_a9b8c7d6-e5f4-3210-fedc-ba9876543210",
  "created_at": "2026-02-21T10:00:00Z",
  "closed_at": null,
  "tokens_issued": []
}
```

### 4.3 Envelope Lifecycle

```
[CREATE] → open → [SPEND] → partially_consumed → [COMPLETE] → closed
                                                  [REVOKE]   → revoked
                                                  [EXPIRE]   → expired
```

**State transitions:**

| Event | From | To | Side Effect |
|-------|------|----|-------------|
| Token issued against envelope | open | open (committed_cents incremented) | Token added to `tokens_issued` |
| Transaction settled | open | open (spent_cents incremented) | Propagated to parent grant |
| All tokens expired/revoked | open | closed | Unspent committed budget returned to grant |
| Parent grant revoked | open | revoked | All tokens in envelope immediately revoked |
| `time_window_end` reached | open | expired | All tokens immediately invalidated |
| Task completed (explicit) | open | closed | Unspent budget NOT refunded (consumed) |

**Critical rule:** Unused budget in a completed envelope does NOT roll over. This is intentional. The principal authorized a budget for a task. If the task completes under budget, the surplus returns to the grant (parent authorization), not to the agent for discretionary use.

### 4.4 Envelope Capacity Gate

Before issuing any token against an envelope, the server MUST check:

```
new_token.budget_cap_cents + envelope.budget_committed_cents <= envelope.budget_ceiling_cents
```

If this check fails, the token issuance MUST be rejected with `WALLET_ENVELOPE_OVER_COMMITTED`.

This prevents the common mistake of issuing multiple tokens against the same envelope that sum to more than the ceiling.

### 4.5 Envelope Creation via Consent Flow Extension

When the principal approves an OAuth3 consent request that includes wallet claims, the server simultaneously:

1. Issues the AgencyToken with the wallet block
2. Creates the budget envelope with the approved ceiling
3. Links the envelope to the token via `budget_envelope_id`

The consent UI MUST display the budget envelope fields (ceiling, time window, merchant allowlist, task description) as prominently as the action scopes.

---

## Section 5: Settlement Rails

### 5.1 Rail Abstraction

OAuth3 Wallet is rail-agnostic at the authorization layer. The `payment_rail` field in the wallet block specifies which settlement mechanism will be used, but all authorization gates run before any rail is invoked.

**Rail selection at consent time:** The principal and agent agree on the rail when the token is issued. The rail cannot be changed after token issuance.

**Rail mismatch:** If the resource server's settlement infrastructure does not support the specified rail, the action MUST be blocked with `WALLET_RAIL_NOT_SUPPORTED`. The agent MUST NOT fall back to a different rail.

### 5.2 Stripe Rail

**Use case:** Traditional card payments for SaaS subscriptions, e-commerce, and any Stripe-integrated merchant.

**Settlement flow:**
1. Agent presents wallet token to resource server
2. Resource server validates all nine gates (G1-G9)
3. Resource server initiates Stripe PaymentIntent against the principal's stored card
4. Stripe returns a `charge_id` (e.g., `ch_3Mxxxx...`)
5. Resource server records `charge_id` as settlement proof in the evidence bundle
6. Resource server updates `budget_spent_cents` and propagates up the chain

**Evidence fields specific to Stripe:**
```json
{
  "settlement_proof": "ch_3MxxxxxxxxxxxxxxxxxxxxXXXX",
  "settlement_type": "stripe_charge_id",
  "merchant_name": "Kayak.com",
  "merchant_domain": "kayak.com"
}
```

### 5.3 x402/USDC Rail

**Use case:** HTTP 402 micropayments for API-to-API transactions. When an agent calls a paid API endpoint, the server returns HTTP 402 with payment details; the agent pays in USDC and the server responds with the requested resource.

**Settlement flow:**
1. Agent calls API endpoint, receives HTTP 402 with `X-Payment-Required` header
2. Agent validates wallet token gates (G1-G9) for the requested amount
3. Agent submits USDC payment to the on-chain address specified in the 402 response
4. Agent waits for on-chain confirmation (minimum 1 block confirmation)
5. On-chain transaction hash is recorded as settlement proof
6. Agent retries the API call with `X-Payment-Proof` header containing the transaction hash
7. Resource server verifies on-chain proof and returns resource

**Evidence fields specific to x402/USDC:**
```json
{
  "settlement_proof": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
  "settlement_type": "onchain_tx_hash",
  "chain": "base",
  "block_number": 14523891,
  "usdc_amount_micro": 28000000
}
```

**Note on unit conversion:** USDC uses 6 decimal places (1 USDC = 1,000,000 micro-USDC). The gateway MUST convert cents to micro-USDC using integer arithmetic. Floating-point conversion is a forbidden state (FLOAT_IN_BUDGET).

```
usdc_micro = cents * 10000  (integer multiplication — exact)
```

### 5.4 Internal Credits Rail

**Use case:** Solaceagi.com managed LLM tier. Users pre-purchase credits; agents spend credits for LLM inference and managed task execution.

**Settlement flow:**
1. Agent presents wallet token to solaceagi.com resource server
2. Server validates all nine gates
3. Server atomically decrements the user's credit balance (using database transaction with optimistic locking)
4. Server records the internal transaction ID as settlement proof
5. Server updates `budget_spent_cents` and propagates

**Evidence fields specific to internal credits:**
```json
{
  "settlement_proof": "itx_solaceagi_20260221T101532Z_a1b2c3",
  "settlement_type": "internal_credit_debit",
  "credit_balance_before_cents": 100000,
  "credit_balance_after_cents": 71500,
  "platform": "solaceagi.com"
}
```

### 5.5 Rail Selection Guide

| Scenario | Recommended Rail |
|----------|-----------------|
| Booking flights, hotels, SaaS subscriptions | `stripe` |
| AI API microtransactions (< $1 per call) | `x402_usdc` |
| solaceagi.com managed LLM task budget | `internal_credits` |
| Inter-agent payments in crypto-native workflows | `x402_usdc` |
| Enterprise procurement with PO integration | `stripe` (Stripe Invoicing) |

---

## Section 6: Evidence Bundle for Financial Actions

### 6.1 Chain-of-Custody Requirement

Every OAuth3 Wallet spending action MUST produce a complete chain-of-custody evidence bundle. The chain must be traversable from the original principal authorization to the final settlement proof, with no gaps.

The chain is structured as:

```
principal_grant_id → token_id → envelope_id → transaction_id → settlement_proof
```

A Lane A claim for a financial action requires this full chain. A transaction without a verifiable chain is an evidence gap (EVIDENCE_GAP) and is a forbidden state.

### 6.2 Wallet Audit Record Schema

Each financial action appends to `oauth3_wallet_audit.jsonl`. The record extends the base OAuth3 audit record (Section 5 of oauth3-spec-v0.1) with wallet-specific fields:

```json
{
  "$schema": "https://stillwater.dev/schemas/oauth3/wallet-audit/v0.1.json",
  "audit_id": "string (UUID v4)",
  "event": "string (see event registry below)",
  "timestamp": "string (ISO 8601 UTC)",
  "token_id": "string (UUID v4)",
  "subject": "string",
  "issuer": "string",
  "scope": "string (the spend-authorizing scope)",
  "platform": "string (merchant domain)",
  "status": "string ('PASS' | 'BLOCKED' | 'SETTLED' | 'REVOKED')",
  "gate_failed": "string | null ('G5' through 'G9' if BLOCKED)",
  "error_code": "string | null",

  "wallet": {
    "envelope_id": "string (UUID v4)",
    "parent_token_id": "string (UUID v4) | null",
    "delegation_depth": "integer",
    "delegation_chain": ["string (UUID v4)", "..."],

    "amount_cents": "integer (NEVER float)",
    "budget_cap_cents": "integer",
    "budget_spent_cents_before": "integer",
    "budget_spent_cents_after": "integer",
    "daily_cap_cents": "integer",
    "daily_spent_cents_before": "integer",
    "per_tx_max_cents": "integer",
    "payment_rail": "string",
    "merchant_domain": "string",

    "intent_hash": "string (SHA-256 hex of the original authorization scope + amount + merchant)",
    "action_hash": "string (SHA-256 hex of the actual transaction details before settlement)",
    "settlement_proof": "string | null (rail-specific; populated after settlement)",
    "settlement_type": "string | null",
    "rung": "integer (641 | 274177 | 65537)"
  }
}
```

### 6.3 Intent Hash and Action Hash

**Intent hash** is computed at authorization time (when the principal approves the wallet token):

```python
intent_hash = sha256(
    canonical_json({
        "subject": token.subject,
        "scope": spend_scope,
        "merchant_domain": merchant_domain,
        "max_amount_cents": per_tx_max_cents,
        "budget_cap_cents": budget_cap_cents,
        "envelope_id": envelope_id,
        "issued_at": token.issued_at
    })
).hexdigest()
```

**Action hash** is computed at execution time (when the agent submits the transaction):

```python
action_hash = sha256(
    canonical_json({
        "token_id": token.id,
        "scope": spend_scope,
        "merchant_domain": merchant_domain,
        "amount_cents": actual_amount_cents,
        "execution_timestamp": iso8601_utc_now(),
        "intent_hash": intent_hash
    })
).hexdigest()
```

The `action_hash` includes the `intent_hash` as a field, creating a cryptographic link between authorization and execution. Any modification to either hash makes the chain traversal fail.

**Rule:** `actual_amount_cents` MUST be an integer at all times. The hash function receives an integer, not a float. Implementations MUST use `int()` coercion with explicit validation that the value is already integral (i.e., `amount_cents % 1 == 0`) rather than silent rounding.

### 6.4 Financial Event Registry

| Event | When | Required Wallet Fields |
|-------|------|----------------------|
| `WALLET_TOKEN_ISSUED` | Wallet token granted via consent | `envelope_id`, `budget_cap_cents`, `payment_rail` |
| `WALLET_GATE_CHECKED` | All 5 wallet gates validated | `gate_failed` or null, `amount_cents`, `budget_spent_cents_before` |
| `WALLET_TRANSACTION_INITIATED` | Payment rail invoked | `amount_cents`, `intent_hash`, `action_hash`, `merchant_domain` |
| `WALLET_TRANSACTION_SETTLED` | Settlement confirmed | `settlement_proof`, `settlement_type`, `budget_spent_cents_after` |
| `WALLET_TRANSACTION_FAILED` | Settlement failed (rail error) | `error_code`, `amount_cents` (budget NOT decremented) |
| `WALLET_BUDGET_PROPAGATED` | Parent budget updated | `delegation_chain`, `amount_cents` |
| `WALLET_ENVELOPE_CLOSED` | Task complete or expired | `envelope_id`, `budget_spent_cents`, `budget_ceiling_cents` |
| `WALLET_TOKEN_REVOKED` | Wallet token revoked | `envelope_id`, `remaining_budget_cents` |
| `WALLET_GATE_BLOCKED` | Any G5-G9 gate failure | `gate_failed`, `error_code` |

### 6.5 Evidence File Naming

| File | Location | Contents |
|------|----------|----------|
| `oauth3_wallet_audit.jsonl` | `artifacts/oauth3/wallet/` | JSONL append-only log of all wallet events |
| `oauth3_wallet_envelope_{envelope_id}.json` | `artifacts/oauth3/wallet/envelopes/` | Full envelope record with lifecycle history |
| `oauth3_wallet_tx_{audit_id}.json` | `artifacts/oauth3/wallet/transactions/` | Single transaction evidence (intent_hash + action_hash + settlement_proof) |
| `oauth3_wallet_chain_{token_id}.json` | `artifacts/oauth3/wallet/chains/` | Full delegation chain from root to leaf |

All files MUST have a SHA-256 sidecar (`.sha256`) per the base OAuth3 evidence integrity rules.

### 6.6 Canonical Transaction Evidence Example

```json
{
  "$schema": "https://stillwater.dev/schemas/oauth3/wallet-audit/v0.1.json",
  "audit_id": "d4e5f6a7-b8c9-0123-def0-123456789012",
  "event": "WALLET_TRANSACTION_SETTLED",
  "timestamp": "2026-02-21T10:47:33Z",
  "token_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "subject": "user:phuc@example.com",
  "issuer": "https://solaceagi.com",
  "scope": "travel.book.flight",
  "platform": "kayak.com",
  "status": "SETTLED",
  "gate_failed": null,
  "error_code": null,
  "wallet": {
    "envelope_id": "env_c3d4e5f6-a7b8-9012-cdef-012345678902",
    "parent_token_id": null,
    "delegation_depth": 0,
    "delegation_chain": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"],
    "amount_cents": 31499,
    "budget_cap_cents": 40000,
    "budget_spent_cents_before": 0,
    "budget_spent_cents_after": 31499,
    "daily_cap_cents": 40000,
    "daily_spent_cents_before": 0,
    "per_tx_max_cents": 40000,
    "payment_rail": "stripe",
    "merchant_domain": "kayak.com",
    "intent_hash": "sha256:a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
    "action_hash": "sha256:b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3",
    "settlement_proof": "ch_3MxxxxxxxxxxxxxxxxxxxxXXXX",
    "settlement_type": "stripe_charge_id",
    "rung": 274177
  }
}
```

---

## Section 7: Forbidden States

OAuth3 Wallet enforces strict fail-closed behavior. The following states are forbidden and MUST cause immediate action blockage plus audit logging.

### 7.1 FLOAT_IN_BUDGET

**Definition:** Any monetary amount in the spending path represented as a floating-point number.

**Where it can occur:**
- `amount_cents` field contains a float (e.g., `31.99` instead of `3199`)
- Budget gate arithmetic uses float division
- USDC micro-unit conversion uses float multiplication
- JSON parsing coerces a large integer to float (JavaScript `Number` precision issue)

**Mitigation:** All implementations MUST use integer types for all budget fields. In Python: use `int`. In JavaScript: use `BigInt` for amounts > 2^53. In Go: use `int64`. In Rust: use `u64`.

**Detection gate:** G5 MUST verify `type(amount_cents) == int` before any comparison. If the type check fails: BLOCKED: FLOAT_IN_BUDGET.

### 7.2 BUDGET_EXCEEDED

**Definition:** A transaction that would cause `budget_spent_cents + amount_cents > budget_cap_cents` at any level of the delegation chain.

**Note:** The gate checks `>=` (not `>`) because a `budget_cap_cents` of 0 means the token has been fully spent. An attempt to spend $0.01 against a $0-remaining budget is still a BUDGET_EXCEEDED state.

**Detection gate:** G5.

### 7.3 ORPHAN_ENVELOPE

**Definition:** An AgencyToken with a `budget_envelope_id` that does not exist in the envelope registry, has been closed, or has expired.

**Detection gate:** G9.

### 7.4 REVOKED_TOKEN_SPEND

**Definition:** An attempt to execute a spending action using a token that has been revoked.

**Detection gate:** G4 (base revocation gate). Listed here because the failure mode in financial contexts is particularly severe — a settlement initiated after revocation could result in an unreversible charge.

**Additional requirement:** The resource server MUST perform a fresh G4 check against the live revocation registry (not a cached result) for any transaction above `per_tx_max_cents / 10`. Cache staleness in financial contexts is a vulnerability.

### 7.5 EVIDENCE_GAP

**Definition:** A settled transaction for which the full chain `principal_grant_id → token_id → envelope_id → transaction_id → settlement_proof` cannot be verified.

**Detection:** The resource server MUST verify chain completeness before marking a transaction as SETTLED. If any link in the chain is missing: the transaction status MUST be set to `EVIDENCE_INCOMPLETE` and escalated for human review.

**Rule:** An `EVIDENCE_INCOMPLETE` transaction is never counted as Lane A evidence for any Stillwater verification run.

### 7.6 DELEGATION_ESCALATION

**Definition:** A sub-token with any budget field exceeding the parent's corresponding field.

**Detection:** The delegation endpoint (Section 3.6) MUST compute the MIN-cap values server-side and reject any request where the computed value differs from the agent's request in a direction that would grant more authority.

**Specific checks:**
- `sub.budget_cap_cents > (parent.budget_cap_cents - parent.budget_spent_cents)` → BLOCKED
- `sub.per_tx_max_cents > parent.per_tx_max_cents` → BLOCKED
- `sub.daily_cap_cents > (parent.daily_cap_cents - parent.daily_spent_cents)` → BLOCKED
- `any sub.scope not in parent.scopes` → BLOCKED
- `any sub.merchant_allowlist entry not in parent.merchant_allowlist` → BLOCKED

### 7.7 Forbidden State Summary Table

| State | Gate | HTTP Error | Audit Code |
|-------|------|------------|------------|
| FLOAT_IN_BUDGET | G5 (pre-check) | 400 | `WALLET_FLOAT_IN_BUDGET` |
| BUDGET_EXCEEDED | G5 | 402 | `WALLET_BUDGET_EXCEEDED` |
| PER_TX_EXCEEDED | G6 | 402 | `WALLET_PER_TX_EXCEEDED` |
| DAILY_CAP_EXCEEDED | G7 | 402 | `WALLET_DAILY_CAP_EXCEEDED` |
| MERCHANT_NOT_ALLOWED | G8 | 403 | `WALLET_MERCHANT_NOT_ALLOWED` |
| ORPHAN_ENVELOPE | G9 | 400 | `WALLET_ENVELOPE_INVALID` |
| REVOKED_TOKEN_SPEND | G4 | 401 | `OAUTH3_TOKEN_REVOKED` |
| EVIDENCE_GAP | Post-settlement | 500 | `WALLET_EVIDENCE_INCOMPLETE` |
| DELEGATION_ESCALATION | Delegation | 400 | `WALLET_DELEGATION_ESCALATION` |

---

## Section 8: Revocation Cascade

### 8.1 Cascade Semantics

When a parent token is revoked in the base OAuth3 protocol, the revocation applies only to that token. In OAuth3 Wallet, revocation cascades through the delegation chain and across all open budget envelopes.

**Cascade rule (normative):** When token T is revoked:
1. All tokens with `parent_token_id = T.id` are immediately revoked (direct children)
2. Step 1 recurses: all tokens with `parent_token_id = T.child.id` are revoked (grandchildren)
3. All budget envelopes in `tokens_issued` for any revoked token are closed
4. All pending transactions against those envelopes MUST be canceled before settlement
5. Unspent committed budget in closed envelopes MUST be returned to the parent grant

### 8.2 Cascade Algorithm

```
function revoke_cascade(token_id):
  token = registry.get(token_id)
  if token.status == "revoked": return  # idempotent

  # Mark this token revoked
  registry.revoke(token_id, timestamp=now(), reason=reason)

  # Find and revoke all direct children
  children = registry.find_by_parent_token_id(token_id)
  for child in children:
    revoke_cascade(child.id)  # recursive

  # Close all envelopes associated with this token
  envelopes = envelope_registry.find_by_token_id(token_id)
  for envelope in envelopes:
    if envelope.status == "open":
      # Return uncommitted budget to parent grant
      refund = envelope.budget_ceiling_cents - envelope.budget_spent_cents
      grant_registry.return_budget(envelope.parent_grant_id, refund)
      envelope_registry.close(envelope.envelope_id, reason="token_revoked")

  # Log the cascade event
  audit.append(WALLET_REVOCATION_CASCADE, {
    "revoked_token": token_id,
    "children_revoked": [c.id for c in children],
    "envelopes_closed": [e.envelope_id for e in envelopes]
  })
```

### 8.3 Cascade Timing Requirement

The full cascade (all descendants revoked, all envelopes closed) MUST complete within 5 seconds of the root DELETE call returning 200. This is stricter than the base OAuth3 revocation requirement (1 second) because of the additional state to update.

Implementations with large delegation trees SHOULD use graph traversal with BFS and batch updates rather than sequential recursive calls.

### 8.4 Pending Transaction Handling

If a transaction is in-flight (payment rail invoked but settlement not yet confirmed) when revocation cascades to its authorizing token:

- **Stripe:** The resource server MUST issue a `PaymentIntent.cancel()` if the intent has not yet been captured. If already captured, the server MUST issue a refund via `Refund.create()`.
- **x402/USDC:** If the on-chain transaction is unconfirmed, the server MUST NOT process the HTTP retry. If already confirmed on-chain, the transaction cannot be reversed — this MUST be logged as `WALLET_REVOKED_AFTER_SETTLEMENT` and escalated to the principal.
- **Internal credits:** The server MUST NOT decrement the balance if the revocation cascade arrives before the atomic debit. Atomic debit operations MUST check revocation status as part of the database transaction.

### 8.5 Revocation Cascade Audit Record

```json
{
  "audit_id": "e5f6a7b8-c9d0-1234-ef01-234567890123",
  "event": "WALLET_REVOCATION_CASCADE",
  "timestamp": "2026-02-21T11:30:00Z",
  "token_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "subject": "user:phuc@example.com",
  "revocation_reason": "User requested session termination",
  "cascade": {
    "tokens_revoked": [
      "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "c3d4e5f6-a7b8-9012-cdef-012345678902"
    ],
    "envelopes_closed": ["env_c3d4e5f6-a7b8-9012-cdef-012345678902"],
    "budget_returned_cents": 8501,
    "pending_transactions_canceled": 0,
    "pending_transactions_already_settled": 0
  }
}
```

---

## Section 9: Integration with Software 5.0 Verification

### 9.1 Rung Requirements for Wallet Operations

OAuth3 Wallet operations carry higher rung requirements than base OAuth3 operations because financial actions are irreversible.

| Operation | Minimum Rung | Rationale |
|-----------|-------------|-----------|
| Local wallet token validation (dev/test) | 641 | Local correctness |
| Wallet gate compliance check | 641 | Spec conformance test |
| Envelope creation | 274177 | Persistent state created |
| Transaction execution (any rail) | 274177 | Irreversible financial action |
| Delegation chain validation | 274177 | Cascade security property |
| Production wallet deployment | 65537 | Production security gate |
| Stripe live key usage | 65537 | Financial production |
| x402/USDC mainnet usage | 65537 | On-chain irreversibility |

### 9.2 Integration Rung for Delegation Chains

Per the phuc-orchestration integration rung rule, the rung of a delegation chain equals the MIN rung of all contributing agents:

```
chain_rung = MIN(rung(root_agent), rung(agent_B), rung(agent_C), ...)
```

A delegation chain where the root agent is at rung 65537 but a sub-agent is at rung 641 produces a chain_rung of 641. This is by design: the chain is only as verified as its least-verified link.

### 9.3 Lane Classification for Financial Evidence

| Evidence | Lane |
|----------|------|
| Wallet audit JSONL with intent + action hash + settlement proof | Lane A (replayable) |
| Budget gate check results (no transaction) | Lane A |
| Delegation chain schema validation | Lane B (within OAuth3 axiom system) |
| Spending forecast ("agent will probably stay under budget") | Lane C (heuristic) |
| Agent prose claiming a transaction succeeded | NOT evidence — requires WALLET_TRANSACTION_SETTLED record |

### 9.4 Recipe Integration Pattern

Any recipe that includes spending actions MUST declare wallet requirements alongside OAuth3 scope requirements:

```json
{
  "oauth3": {
    "required_scopes": ["travel.search.flights", "travel.book.flight"],
    "step_up_scopes": ["travel.book.flight"],
    "min_ttl_seconds": 3600,
    "evidence_output": "artifacts/oauth3/oauth3_audit.jsonl"
  },
  "oauth3_wallet": {
    "budget_cap_cents": 40000,
    "per_tx_max_cents": 40000,
    "payment_rail": "stripe",
    "merchant_allowlist": ["kayak.com", "expedia.com"],
    "evidence_output": "artifacts/oauth3/wallet/oauth3_wallet_audit.jsonl",
    "min_rung": 274177
  }
}
```

The `oauth3-enforcer` skill reads both blocks. If `oauth3_wallet` is present, it enforces all nine gates (G1-G9). It refuses to proceed if `min_rung` is not met.

---

## Section 10: Competitive Landscape

### 10.1 The Fundamental Gap

Every major player in agentic payments has solved a narrow slice of the problem. None has built a general-purpose delegation and evidence layer. The following table maps what each protocol covers and what it leaves to OAuth3 Wallet.

### 10.2 Comparison Matrix

| Capability | Coinbase AgentKit | Stripe ACP | Google AP2 | Visa/MC Agentic | OAuth3 Wallet |
|-----------|-------------------|------------|------------|-----------------|----------------|
| Spending caps | Yes (wallet balance) | Yes (account limits) | Yes (envelopes) | Yes (virtual card limits) | Yes (G5-G7 gates) |
| Per-transaction limits | Partial (wallet config) | Yes | Yes | Yes | Yes (G6 gate) |
| Time-bound authorization | No | No | Yes (session) | No | Yes (TTL from base token) |
| Step-up re-consent | No | No | No | No | Yes (inherited from base OAuth3) |
| Merchant allowlist | No | No | Yes (limited) | Yes (MCC codes) | Yes (G8 gate) |
| Scope-based spending | No | No | No | No | Yes (platform.action.resource) |
| Delegation chain with MIN-cap | No | No | No | No | Yes (Section 3) |
| Revocation cascade | No | Manual | No | Card cancel | Yes (Section 8) |
| Evidence chain (intent→settlement) | No | Stripe logs | No | No | Yes (Section 6) |
| Human consent flow | No | No | No | No | Yes (base OAuth3 consent) |
| Non-financial action auth | No | No | No | No | Yes (base OAuth3 scopes) |
| Open standard | No (Base chain) | No (Stripe-only) | No (Google) | No (card networks) | Yes |
| Audit trail | No | Stripe dashboard | No | No | Yes (JSONL, SHA-256) |
| Multi-rail abstraction | No | Stripe only | Google Pay | Card rails | Yes |

### 10.3 Why Existing Solutions Cannot Fill the Gap

**Coinbase AgentKit** is excellent at crypto wallet management and USDC spending for agents. It is not an authorization protocol — it does not define who authorized the agent, for what purpose, with what scope, and with revocation semantics. It is an execution mechanism without an authorization layer.

**Stripe ACP** provides agents with Stripe-managed payment accounts. The agent has a Stripe account; it can spend from that account; Stripe enforces limits. But the scoping ("this spend is for booking flights only"), the step-up re-consent ("pause and confirm before irreversible booking"), the delegation chain ("sub-agent inherits constrained budget from orchestrator"), and the evidence chain ("prove the authorization matches the spend") are all absent.

**Google AP2** is the closest conceptually — it introduces the budget envelope pattern (which this spec acknowledges and extends). But AP2 is Google-ecosystem-only, lacks the scope-action model, lacks step-up consent, lacks delegation chains, and does not produce verifiable evidence bundles.

**Visa/Mastercard agentic tokens** are virtual cards with merchant category code (MCC) restrictions. They are card-network-specific, do not address non-financial agent actions, cannot express fine-grained action scopes, and have no revocation cascade mechanism.

**The structural reason none can converge on OAuth3 Wallet:** Token-revenue vendors (OpenAI, Anthropic, Google, Mistral) benefit from higher token usage. OAuth3 Wallet enables recipe-based task execution that achieves the same user outcomes with far fewer tokens. These vendors cannot implement OAuth3 Wallet without cannibalizing their primary revenue. Card networks cannot implement it because it requires a consent and revocation infrastructure they do not operate. Only an open, independent standard — issued outside any token-revenue or settlement-revenue interest — can define this layer.

### 10.4 First-Mover Position

OAuth3 Wallet is the first formal specification for the authorization and evidence layer above agentic payment rails. By publishing this spec at v0.1, the Stillwater project establishes the reference point. The goal is to drive adoption via:

1. Open-source reference implementation in `solace-browser`
2. CLI client support in `solace-cli` (AES-256-GCM vault for wallet tokens)
3. Stillwater Store governance (skills must declare wallet requirements)
4. Community scope registry (platform.action.resource for spending actions)

---

## Section 11: Implementation Roadmap

### Phase 0 — Specification (Current)

- [x] Wallet token schema defined (Section 2)
- [x] Delegation chain protocol defined (Section 3)
- [x] Budget envelope pattern defined (Section 4)
- [x] Settlement rail abstraction defined (Section 5)
- [x] Evidence bundle schema defined (Section 6)
- [x] Forbidden states enumerated (Section 7)
- [x] Revocation cascade defined (Section 8)
- [x] Rung requirements defined (Section 9)

**Rung target:** 641 (local correctness — spec is self-consistent)

### Phase 1 — Reference Implementation (solace-browser)

- [ ] Wallet token issuance endpoint (`POST /oauth3/wallet/delegate`)
- [ ] Budget envelope registry (SQLite-backed, schema in Section 4.2)
- [ ] All nine gates (G1-G9) implemented in `oauth3-enforcer.md` skill
- [ ] Internal credits rail (mock, for testing)
- [ ] Wallet audit JSONL writer with SHA-256 sidecars
- [ ] Evidence chain traversal verifier

**Rung target:** 274177 (persistent state, evidence-carrying)

### Phase 2 — Stripe Integration

- [ ] Stripe PaymentIntent creation (test keys, rung 641)
- [ ] Stripe charge ID recorded as settlement proof
- [ ] Refund flow on revocation cascade (test environment)
- [ ] Stripe live keys (rung 65537 gate before enabling)
- [ ] Consent UI updated to display merchant allowlist and budget fields

**Rung target:** 65537 (production/security gate)

### Phase 3 — x402/USDC Integration

- [ ] HTTP 402 payment flow (Base testnet, rung 641)
- [ ] On-chain transaction hash as settlement proof
- [ ] Integer USDC micro-unit conversion (no floats)
- [ ] Block confirmation wait (minimum 1 block)
- [ ] Base mainnet (rung 65537 gate before enabling)

**Rung target:** 65537

### Phase 4 — Delegation Chain Production

- [ ] Multi-level delegation with MIN-cap enforcement
- [ ] Budget propagation on transaction settlement
- [ ] Delegation chain audit records (`oauth3_wallet_chain_{token_id}.json`)
- [ ] Cascade revocation with BFS traversal and batch updates
- [ ] Pending transaction cancellation on revocation

**Rung target:** 65537

### Phase 5 — Community Scope Registry

- [ ] Spending scope format: `platform.spend.category` (e.g., `travel.spend.flight`)
- [ ] Standard spending scopes published in Stillwater Store
- [ ] Skill submission protocol requires wallet block if scope includes `spend.*`
- [ ] Third-party payment integrators can register custom spending scopes

**Rung target:** 274177 (community review gate)

---

## Appendix A: Comparison to Base OAuth3

| Property | OAuth3 (base) | OAuth3 Wallet (extension) |
|----------|---------------|--------------------------|
| Authorizes | Agent actions | Agent actions + spending |
| Token schema | AgencyToken | AgencyToken + wallet block |
| Validation gates | G1-G4 | G1-G9 |
| Scope format | platform.action.resource | + platform.spend.category |
| Delegation | Not defined | MIN-cap chain (Section 3) |
| Budget enforcement | Not defined | G5-G7 gates |
| Settlement | Not defined | Rail abstraction (Section 5) |
| Evidence bundle | oauth3_audit.jsonl | + oauth3_wallet_audit.jsonl |
| Revocation | Single token | Cascade (Section 8) |
| Integer requirement | Not specified | REQUIRED (FLOAT_IN_BUDGET) |
| Rung for production | 65537 | 65537 (financial) |

---

## Appendix B: Security Considerations

### B.1 Budget Depletion Attack

**Threat:** A malicious agent attempts many small transactions just below the `per_tx_max_cents` limit to exhaust `budget_cap_cents` before the principal notices.

**Mitigation:**
- `daily_cap_cents` limits the rate of spend (G7 gate)
- `max_actions` from base AgencyToken limits the number of discrete actions
- The consent UI MUST show real-time spend against budget (requires server-push or principal dashboard)
- Wallet audit JSONL provides full transaction history for post-hoc detection

### B.2 Delegation Chain Forgery

**Threat:** A compromised sub-agent claims a higher budget cap than was delegated, forging a wallet block with inflated values.

**Mitigation:**
- Sub-tokens are issued by the authorization server, not self-issued by agents
- The server enforces MIN-cap at delegation time (Section 3.2)
- The `signature_stub` over the full token JSON detects tampering
- In v1.0: ECDSA-P256 signature makes forgery computationally infeasible

### B.3 Timing Attack on Revocation

**Threat:** An agent races to initiate settlement between revocation and the cascade completing.

**Mitigation:**
- The resource server MUST perform a fresh G4 check (no cache) for any transaction above `per_tx_max_cents / 10`
- Stripe PaymentIntent uses separate authorize-and-capture; capture can be canceled post-revocation
- x402/USDC: the server refuses the HTTP retry if revocation arrived before confirmation
- Cascade MUST complete within 5 seconds (Section 8.3)

### B.4 Integer Overflow

**Threat:** `budget_cap_cents` for a large enterprise grant could exceed `int32` range (2,147,483,647 cents = $21.4M). A system using `int32` would silently overflow.

**Mitigation:** All budget fields MUST use `int64` minimum. Maximum value is `9_223_372_036_854_775_807` cents ($92 trillion) — sufficient for any realistic use. Implementations MUST validate that `budget_cap_cents >= 0` and `budget_cap_cents <= MAX_INT64`.

### B.5 Settlement Proof Verification

**Threat:** A compromised resource server records a fake `settlement_proof` (e.g., a made-up Stripe charge ID) without actually charging the payment method.

**Mitigation:**
- For Stripe: implementations SHOULD verify the charge ID against the Stripe API before recording as SETTLED
- For x402/USDC: the on-chain transaction hash is publicly verifiable
- For internal credits: the debit is an atomic database operation; the transaction ID is system-generated
- The rung 65537 gate for production requires evidence that settlement proof verification is implemented

---

## Appendix C: Stillwater Integration

### C.1 New Skills Required

| Skill | Purpose | Model |
|-------|---------|-------|
| `oauth3-wallet-enforcer.md` | Implements G5-G9 gates; extends `oauth3-enforcer.md` | sonnet |
| `oauth3-wallet-ledger.md` | Budget tracking and propagation across delegation chains | sonnet |
| `oauth3-wallet-audit.md` | Evidence bundle writer for financial actions | haiku |

### C.2 Scope Registry Extensions

New spending scopes registered with the Stillwater Store follow the same `platform.action.resource` format. The `action` segment for spending scopes MUST be `spend`:

| Scope | Description | Step-Up Required? |
|-------|-------------|-------------------|
| `travel.spend.flight` | Book and pay for a flight | Yes — irreversible |
| `travel.spend.hotel` | Book and pay for a hotel | Yes — irreversible |
| `saas.spend.subscription` | Purchase a SaaS subscription | Yes — recurring |
| `api.spend.credits` | Purchase API credits | No (if under per_tx threshold) |
| `ecommerce.spend.purchase` | Make an e-commerce purchase | Yes |
| `cloud.spend.compute` | Allocate cloud compute resources | Yes — potentially recurring |

### C.3 Vault Storage (solace-cli)

Wallet tokens MUST be stored in the AES-256-GCM vault alongside base OAuth3 tokens. The vault entry for a wallet token MUST include:

```json
{
  "token_id": "...",
  "wallet_envelope_id": "...",
  "budget_cap_cents": 40000,
  "payment_rail": "stripe",
  "stored_at": "2026-02-21T10:00:00Z",
  "encrypted_token": "AES-256-GCM ciphertext"
}
```

The cleartext `budget_cap_cents` and `payment_rail` are stored outside the encrypted blob for principal dashboard display without requiring vault unlock.

---

## Revision History

| Version | Date | Change |
|---------|------|--------|
| 0.1.0 | 2026-02-21 | Initial specification. Rung 641. Eleven sections complete. Coins OAuth3 Wallet concept. |

---

*End of OAuth3 Wallet Specification v0.1.0*

*This specification is a Stillwater Project original. OAuth3 and OAuth3 Wallet are concepts originated by Phuc Vinh Truong / Stillwater. The base OAuth3 specification (oauth3-spec-v0.1) is the normative dependency for all implementations of this document.*
