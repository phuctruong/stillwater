# OAuth3 and the IETF AI Agent Authorization Landscape: Complementary, Not Competing

**Document ID:** oauth3-ietf-complementarity
**Version:** 1.0
**Status:** POSITION PAPER
**Authors:** Phuc Vinh Truong, Stillwater Project
**Date:** 2026-02-23
**Repository:** https://github.com/phuctruong/stillwater

---

## Abstract

The AI agent authorization landscape is fragmenting across multiple IETF working drafts,
each addressing a distinct phase of the agent lifecycle. Four active drafts —
draft-oauth-ai-agents-on-behalf-of-user-02, draft-song-oauth-ai-agent-authorization-00,
draft-oauth-transaction-tokens-for-agents-00, and draft-rosenberg-oauth-aauth-00 — collectively
address agent identity, delegation, granular targeting, and cross-service context propagation.
Together they are necessary but not sufficient: all four drafts assume that once an agent holds
a token, governance is someone else's problem. This paper maps the full agent authorization
lifecycle, identifies the post-token governance gap that none of the IETF drafts address, and
shows how OAuth3 fills that gap as a complementary — not competing — standard. The IETF drafts
handle the pre-token and at-token phases. OAuth3 handles everything after: evidence, limits,
re-consent, audit trails, and revocation during execution.

---

## 1. The Agent Authorization Lifecycle

AI agents operate across four distinct phases. Existing IETF work covers Phases 1-3.
OAuth3 covers Phase 4.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     AGENT AUTHORIZATION LIFECYCLE                            │
├──────────────┬──────────────────────┬────────────────────────────────────────┤
│ PHASE        │ QUESTION ANSWERED    │ COVERED BY                             │
├──────────────┼──────────────────────┼────────────────────────────────────────┤
│ 1. Identity  │ Who is this agent?   │ draft-rosenberg-oauth-aauth-00         │
│              │                      │ (AAuth — agent identity verification)  │
├──────────────┼──────────────────────┼────────────────────────────────────────┤
│ 2. Delegation│ What is the agent    │ draft-oauth-ai-agents-on-behalf-of-    │
│              │ authorized to do?    │ user-02 (OBO — requested_actor,        │
│              │ On behalf of whom?   │ actor_token, JWT act claim)            │
├──────────────┼──────────────────────┼────────────────────────────────────────┤
│ 3a. Targeting│ Which module within  │ draft-song-oauth-ai-agent-             │
│              │ a client is          │ authorization-00 (target_id field)     │
│              │ authorized?          │                                        │
├──────────────┼──────────────────────┼────────────────────────────────────────┤
│ 3b. Context  │ How does agent       │ draft-oauth-transaction-tokens-for-    │
│ Propagation  │ context flow across  │ agents-00 (actor + principal fields    │
│              │ service calls?       │ in transaction tokens)                 │
├──────────────┼──────────────────────┼────────────────────────────────────────┤
│ 4. Governance│ After the token      │ OAuth3 — post-token governance:        │
│ (GAP)        │ exists: What did     │ evidence bundles, action limits,       │
│              │ the agent DO?        │ step-up re-consent, platform           │
│              │ Can we halt it?      │ allowlists, synchronous revocation,    │
│              │ Did it stay in       │ rung-gated trust, audit integrity      │
│              │ bounds?              │                                        │
└──────────────┴──────────────────────┴────────────────────────────────────────┘

   ◄─────────── IETF drafts (pre-token + at-token) ──────────► ◄── OAuth3 ──►
```

---

## 2. What the IETF Drafts Solve

### 2.1 OBO: On-Behalf-Of Delegation
draft-oauth-ai-agents-on-behalf-of-user-02 extends OAuth 2.0 (RFC 6749) with a clean
delegation mechanism. The `requested_actor` parameter at the authorization endpoint names
the agent being delegated to. The `actor_token` at the token endpoint authenticates the
agent itself. The resulting access token carries a JWT `act` claim (per RFC 8693) that
documents the full delegation chain. PKCE (RFC 7636) prevents code interception.

This is exactly the right model for "a human authorizes an AI agent to act on their behalf."
It integrates with RFC 9068 (JWT access tokens) and the existing OAuth 2.0 ecosystem without
breaking backward compatibility.

### 2.2 Target: Per-Module Authorization
draft-song-oauth-ai-agent-authorization-00 adds a `target_id` parameter that identifies
which functional module within a client application receives authorization. Where OBO answers
"who is the agent," Target answers "which part of the agent." This fine-grained targeting
prevents overly broad grants to monolithic agent systems.

### 2.3 Transaction Tokens: Cross-Service Context
draft-oauth-transaction-tokens-for-agents-00 extends the Transaction Tokens framework
with `actor` and `principal` fields. When an agent makes downstream service-to-service calls,
this draft ensures the original principal's identity and the acting agent's identity both
propagate through the call chain — essential for auditing in microservice architectures.

### 2.4 AAuth: Agent Identity
draft-rosenberg-oauth-aauth-00 addresses agent identity verification as an OAuth 2.1
extension. It establishes how an agent proves its identity to an authorization server —
the foundation that all subsequent delegation must build upon.

Together these four drafts create a coherent pre-token and at-token architecture:
identity → delegation → targeting → propagation. This is valuable, well-specified work.

---

## 3. The Post-Token Gap

After an agent acquires a token — which the IETF drafts handle well — the following
questions remain unanswered by any active draft:

**3.1 Mid-execution re-consent.** If an agent, while executing a task, encounters an action
with disproportionate impact (e.g., "delete all files in the project"), none of the IETF drafts
require a pause for human re-approval. The token grants the scope; execution proceeds.

**3.2 Evidence per action.** The `act` claim documents the delegation chain at token issuance.
It does not record what the agent actually did after receiving the token. There is no standard
for an action-by-action evidence bundle that a principal can inspect post-execution.

**3.3 Action quotas.** No IETF draft defines a `max_actions` field — a hard ceiling on the
number of discrete actions an agent may perform under a single token. Without this, a token
valid for one hour can perform an unbounded number of operations.

**3.4 Platform allowlists.** Nothing in OBO, Target, Transaction Tokens, or AAuth prevents
an agent from acting on any domain it can reach. Domain allowlists are absent from all four
drafts.

**3.5 Synchronous revocation during execution.** OAuth 2.0 token revocation (RFC 7009) is
asynchronous and endpoint-based. None of the IETF drafts define how to halt an agent
mid-task when the principal revokes authorization while the agent is actively executing.

**3.6 Hash-chain audit integrity.** Audit trails that an agent self-reports can be altered.
None of the IETF drafts require evidence bundles to be cryptographically chained to prevent
post-hoc falsification.

**3.7 Rung-gated trust levels.** Graduated authority — where an agent earns higher trust
through verified track record — is absent from all four drafts. Trust is binary: the token
is valid or it is not.

---

## 4. OAuth3's Contribution

OAuth3 (oauth3-spec-v0.1.1, 2026-02-23) defines "Delegated Agency Authorization" as a
category and fills each gap identified above with normative requirements.

**AgencyToken schema** adds five fields that no IETF draft provides:
- `step_up_required`: scopes within the grant that MUST trigger re-consent before execution
- `max_actions`: integer ceiling; agent MUST halt when reached
- `platforms`: domain allowlist; agent MUST NOT act outside it
- `agent_id`: agent-locks the token; rejected if presented by a different agent instance
- `signature_stub`: SHA-256 (v0.1) / ECDSA-P256 (v1.0) token integrity per RFC 8785

**Evidence bundle** (Section 5 of the spec): every action taken under an AgencyToken MUST
produce a structured evidence record containing action type, timestamp, outcome, and a
hash linking to the previous record. This creates an immutable, inspectable audit trail.

**Rung-gated trust** (three levels: 641 / 274177 / 65537): agents must demonstrate verified
behavior at each rung before being granted higher-trust scopes. This is not binary trust.

**Regulatory readiness**: Appendix D maps OAuth3 to FDA 21 CFR Part 11 requirements —
the first AI agent authorization spec to address regulatory compliance directly.

**Companion specs**: oauth3-wallet-spec (spending delegation) and oauth3-key-management
(ECDSA-P256 + DPoP binding) extend the core for financial and high-assurance contexts.

---

## 5. Integration Architecture

OAuth3 is designed to layer on top of the IETF stack, not replace it. The recommended
integration sequence:

```
Agent
  │
  ├─1─► AAuth (draft-rosenberg-oauth-aauth-00)
  │      Proves agent identity to authorization server.
  │      AAuth identity ──maps to──► OAuth3 agent_id / cnf.jkt field
  │
  ├─2─► OBO (draft-oauth-ai-agents-on-behalf-of-user-02)
  │      Delegation: requested_actor + actor_token → access token with act claim.
  │      OBO act claim subject ──maps to──► OAuth3 subject + agent_id relationship
  │
  ├─3a─► Target (draft-song-oauth-ai-agent-authorization-00)
  │       Granular per-module targeting via target_id.
  │       Target target_id ──maps to──► OAuth3 platform.action.resource scope format
  │
  ├─3b─► Transaction Tokens (draft-oauth-transaction-tokens-for-agents-00)
  │       Cross-service context propagation via actor + principal fields.
  │       Transaction token carries OAuth3 AgencyToken jti as correlation ID.
  │
  └─4─► OAuth3 (oauth3-spec-v0.1.1)
         Post-token governance layer.
         Enforces: step-up re-consent | max_actions | platform allowlist |
                   evidence bundle | synchronous revocation | rung trust
```

In this architecture, an OAuth3 AgencyToken is issued after OBO delegation completes.
The OBO access token establishes that the human authorized the agent; the AgencyToken
establishes the governance envelope within which the agent must operate. The two tokens
serve different functions and are designed to coexist.

---

## 6. Timing Note: OBO Draft Expiry

draft-oauth-ai-agents-on-behalf-of-user-02 expires 2026-02-27 — four days from this
paper's publication date. This is not a criticism of the draft; expiry is routine in the
IETF process. It is, however, a signal that the community is actively working through
the design space. OAuth3 is positioned to serve as the post-token complement to whatever
emerges from the OBO revision cycle.

---

## 7. Call to Action

OAuth3 v0.1.1 is published and open for review.

- **Specification:** papers/oauth3-spec-v0.1.md (1,075 lines) in the stillwater repository
- **Repository:** https://github.com/phuctruong/stillwater
- **Reference implementation:** solace-browser (OSS) — issues and validates AgencyTokens
- **CLI client:** stillwater/cli (OSS) — presents tokens, requests consent, AES-256-GCM vault

We invite the IETF OAuth working group and the broader AI agent community to:
1. Adopt OAuth3's post-token governance model as the complement to OBO/Target/Transaction Tokens
2. Contribute to the AgencyToken schema (PRs welcome)
3. Reference OAuth3 in future drafts addressing AI agent governance

The four IETF drafts are doing essential work. OAuth3 picks up where they stop.
The full lifecycle requires both.

---

## References

- RFC 2119 — Key words for use in RFCs (Bradner, 1997)
- RFC 6749 — The OAuth 2.0 Authorization Framework (Hardt, 2012)
- RFC 7009 — OAuth 2.0 Token Revocation (Lodderstedt et al., 2013)
- RFC 7519 — JSON Web Token (Jones et al., 2015)
- RFC 7636 — Proof Key for Code Exchange (Sakimura et al., 2015)
- RFC 8693 — OAuth 2.0 Token Exchange (Jones et al., 2020)
- RFC 8785 — JSON Canonicalization Scheme (Rundgren et al., 2020)
- RFC 9068 — JSON Web Token (JWT) Profile for OAuth 2.0 Access Tokens (Bertocci, 2021)
- draft-oauth-ai-agents-on-behalf-of-user-02 — AI Agents: On-Behalf-Of User (expires 2026-02-27)
- draft-song-oauth-ai-agent-authorization-00 — OAuth 2.0 Authorization on Target
- draft-oauth-transaction-tokens-for-agents-00 — Transaction Tokens for Agent Context
- draft-rosenberg-oauth-aauth-00 — AAuth: Agentic Authorization
- oauth3-spec-v0.1.1 — Delegated Agency Authorization (Truong, 2026-02-23)
- oauth3-wallet-spec-v0.1 — Spending Delegation (Truong, 2026-02-23)

---

*This paper is published under the Stillwater Project. Feedback and citations welcome.*
*OAuth3 is an open specification. We coined the term. We welcome the community to build on it.*
