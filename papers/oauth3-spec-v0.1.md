# OAuth3: Delegated Agency Authorization — Formal Specification

**Document ID:** oauth3-spec-v0.1
**Version:** 0.1.1
**Status:** DRAFT — Rung 641 (Local Correctness)
**Authors:** Phuc Vinh Truong, Stillwater Project
**Framework:** Stillwater OS v1.4.0
**Date:** 2026-02-21
**Repository:** https://github.com/phuctruong/stillwater

---

## Abstract

OAuth3 is a delegated agency authorization protocol for AI agents operating on behalf of human principals. Unlike OAuth 2.x, which authorizes data _access_, OAuth3 authorizes agent _action_. Every delegation is scoped, time-bound, revocable, and evidence-carrying. This specification defines the AgencyToken schema, the scope registry format, the consent flow, the revocation protocol, and the evidence bundle requirement for all token operations.

This spec is normative for:
- `stillwater` — verification OS (consumes spec, enforces via `oauth3-enforcer.md`)
- `solace-browser` — OAuth3 reference implementation (issues and validates tokens)
- `solace-cli` — CLI client (presents tokens, requests consent, stores in AES-256-GCM vault)

---

## Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

**Fail-closed rule (hard):** Any system implementing this spec MUST refuse an action if a required gate fails. Failing open (allowing action on token error) is a violation of this specification.

### Transport Security Requirement

All OAuth3 endpoints MUST be served over HTTPS (TLS 1.2 minimum, TLS 1.3 RECOMMENDED). Implementations MUST NOT serve OAuth3 endpoints over unencrypted HTTP. Any HTTP request to an OAuth3 endpoint MUST be rejected or redirected. Token payloads MUST NOT traverse unencrypted channels.

---

## Table of Contents

1. AgencyToken Schema
2. Scope Format and Registry
3. Consent Flow
4. Revocation
5. Evidence Bundle
6. Competitive Landscape and Differentiation
7. Proof-of-Possession (DPoP)

---

## Section 1: AgencyToken Schema

### 1.1 Purpose

An AgencyToken is a structured, signed authorization object that a principal (human user) issues to an agent (AI system or automated process). The token grants the agent permission to perform a bounded set of actions within a bounded time window.

### 1.2 Normative Schema (JSON)

All AgencyTokens MUST conform to the following schema. All required fields MUST be present. Implementations MUST reject tokens with missing required fields.

```json
{
  "$schema": "https://stillwater.dev/schemas/oauth3/agency-token/v0.1.json",
  "type": "object",
  "required": [
    "id",
    "version",
    "issued_at",
    "expires_at",
    "scopes",
    "issuer",
    "subject",
    "signature_stub"
  ],
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid",
      "description": "Globally unique token identifier (UUID v4). Used as revocation key."
    },
    "version": {
      "type": "string",
      "pattern": "^0\\.1\\.\\d+$",
      "description": "Schema version this token was issued under. MUST match spec version."
    },
    "issued_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp of token issuance. MUST be in the past at validation time."
    },
    "expires_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp of token expiry. MUST be after issued_at. Agent MUST refuse to act after this time."
    },
    "scopes": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-z][a-z0-9_-]+(\\.[a-z][a-z0-9_-]+){2}$"
      },
      "minItems": 1,
      "description": "List of granted scopes in platform.action.resource format. MUST NOT be empty. Agent MUST NOT perform actions outside this list."
    },
    "issuer": {
      "type": "string",
      "description": "Principal who issued the token. For user-issued tokens: URI of the issuing platform (e.g., 'https://www.solaceagi.com'). For self-issued: 'urn:stillwater:self-issued'."
    },
    "subject": {
      "type": "string",
      "description": "Identifier of the principal delegating authority. Typically the user's platform-specific ID or email. MUST be the consenting human's identifier."
    },
    "agent_id": {
      "type": "string",
      "description": "OPTIONAL. Identifier of the specific agent instance authorized. If present, token is agent-locked and MUST be rejected if presented by a different agent."
    },
    "step_up_required": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-z][a-z0-9_-]+(\\.[a-z][a-z0-9_-]+){2}$"
      },
      "description": "OPTIONAL. Scopes within the granted set that require step-up re-consent before execution. Agent MUST pause and re-request consent before performing any scope listed here."
    },
    "max_actions": {
      "type": "integer",
      "minimum": 1,
      "description": "OPTIONAL. Maximum number of discrete actions the agent may perform under this token. Agent MUST halt after this limit."
    },
    "platforms": {
      "type": "array",
      "items": { "type": "string" },
      "description": "OPTIONAL. Allowlist of platform domains the agent may act on. If present, agent MUST NOT act on any domain not in this list."
    },
    "metadata": {
      "type": "object",
      "description": "OPTIONAL. Extensible key-value bag for implementation-specific data. MUST NOT be used to override normative fields. Keys MUST be namespaced (e.g., 'solace.session_id')."
    },
    "signature_stub": {
      "type": "string",
      "description": "Cryptographic stub for token integrity. In v0.1 (pre-PKI): SHA-256 hex digest of the canonical JSON of all other fields, computed per RFC 8785 (JSON Canonicalization Scheme). The canonical form excludes the signature_stub field itself. In v1.0: ECDSA-P256 signature over the same canonical form."
    }
  }
}
```

### 1.3 Canonical Example Token

```json
{
  "$schema": "https://stillwater.dev/schemas/oauth3/agency-token/v0.1.json",
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "version": "0.1.0",
  "issued_at": "2026-02-21T10:00:00Z",
  "expires_at": "2026-02-21T11:00:00Z",
  "scopes": [
    "linkedin.post.text",
    "linkedin.react.like",
    "linkedin.read.feed"
  ],
  "issuer": "https://www.solaceagi.com",
  "subject": "user:phuc@example.com",
  "agent_id": "solace-browser:twin:abc123",
  "step_up_required": ["linkedin.post.text"],
  "max_actions": 10,
  "platforms": ["linkedin.com"],
  "metadata": {
    "solace.session_id": "sess_xyz789",
    "solace.consent_ui_version": "1.0.2"
  },
  "signature_stub": "sha256:a3f1e9b2c8d74e5f6a1b3c9d2e4f0a7b8c3d5e6f1a2b4c7d8e9f0a1b2c3d4e5"
}
```

### 1.4 Validation Gates (Normative)

An implementing agent MUST check all four gates before any action:

| Gate | Check | Failure Action |
|------|-------|----------------|
| G1: Schema | Token parses and all required fields present | BLOCKED: OAUTH3_MALFORMED_TOKEN |
| G2: TTL | `expires_at` > current UTC time | BLOCKED: OAUTH3_TOKEN_EXPIRED |
| G3: Scope | Requested action scope in `scopes` list | BLOCKED: OAUTH3_SCOPE_DENIED |
| G4: Revocation | Token `id` not in revocation registry | BLOCKED: OAUTH3_TOKEN_REVOKED |

**Clock Skew Tolerance:** Implementations MUST allow a configurable clock skew tolerance (default: 30 seconds) when checking G2 (TTL). The effective check is: `expires_at + clock_skew_tolerance > current_UTC_time`. Token issuers and enforcement gates MUST synchronize clocks via NTP.

All gate failures MUST be logged to `oauth3_audit.json` (see Section 5) with `status: "BLOCKED"` and the specific gate identifier.

---

## Section 2: Scope Format and Registry

### 2.1 Scope Format

All OAuth3 scopes MUST use the triple-segment format:

```
platform.action.resource
```

Where:
- `platform` — lowercase identifier of the target platform (e.g., `linkedin`, `gmail`, `reddit`)
- `action` — lowercase verb describing the operation class (e.g., `post`, `read`, `delete`, `react`)
- `resource` — lowercase identifier of the target resource type (e.g., `text`, `inbox`, `comment`, `feed`)

All three segments are required. Two-segment or four-segment scopes MUST be rejected.

**Pattern (regex):** `^[a-z][a-z0-9_-]+\.[a-z][a-z0-9_-]+\.[a-z][a-z0-9_-]+$`

### 2.2 Scope Semantics

Scopes are atomic: each scope covers exactly one action class on exactly one resource type. Wildcards (e.g., `linkedin.*.*`) are NOT supported in v0.1 and MUST be rejected. Broad delegation is accomplished by listing multiple explicit scopes.

**Scope composition rule:** Granting scope `platform.action.resource` does NOT grant any other scope. An agent authorized for `gmail.read.inbox` is NOT authorized for `gmail.delete.email`, even if both are "read-adjacent".

### 2.3 Standard Scope Registry (v0.1)

The following scopes are canonical in v0.1. Implementations SHOULD use these exact strings.

#### LinkedIn Platform (`linkedin.*.*`)

| Scope | Description | Step-Up Required? |
|-------|-------------|-------------------|
| `linkedin.read.feed` | Read the user's LinkedIn feed | No |
| `linkedin.read.messages` | Read received messages | No |
| `linkedin.read.profile` | Read profile data | No |
| `linkedin.read.notifications` | Read notifications | No |
| `linkedin.post.text` | Create a new text post | Yes — destructive to reputation |
| `linkedin.post.article` | Publish a long-form article | Yes — destructive to reputation |
| `linkedin.edit.post` | Edit an existing post | Yes |
| `linkedin.delete.post` | Delete a post (irreversible) | Yes — irreversible |
| `linkedin.react.like` | Like a post | No |
| `linkedin.comment.text` | Post a comment | Yes |
| `linkedin.send.message` | Send a direct message | Yes |
| `linkedin.connect.request` | Send a connection request | Yes |

#### Gmail Platform (`gmail.*.*`)

| Scope | Description | Step-Up Required? |
|-------|-------------|-------------------|
| `gmail.read.inbox` | Read inbox messages | No |
| `gmail.read.labels` | Read label list | No |
| `gmail.send.email` | Send an email | Yes — irreversible |
| `gmail.delete.email` | Delete an email | Yes — irreversible |
| `gmail.label.apply` | Apply a label to a message | No |
| `gmail.draft.create` | Create a draft (not sent) | No |

#### Reddit Platform (`reddit.*.*`)

| Scope | Description | Step-Up Required? |
|-------|-------------|-------------------|
| `reddit.read.feed` | Read subreddit posts | No |
| `reddit.post.text` | Create a text post | Yes |
| `reddit.post.link` | Create a link post | Yes |
| `reddit.comment.text` | Post a comment | Yes |
| `reddit.vote.up` | Upvote a post or comment | No |
| `reddit.delete.post` | Delete a post (irreversible) | Yes — irreversible |

#### GitHub Platform (`github.*.*`)

| Scope | Description | Step-Up Required? |
|-------|-------------|-------------------|
| `github.read.issues` | Read issues and PRs | No |
| `github.create.issue` | Open a new issue | No |
| `github.comment.issue` | Comment on an issue | No |
| `github.create.pr` | Open a pull request | Yes |
| `github.merge.pr` | Merge a pull request | Yes — irreversible |
| `github.delete.branch` | Delete a branch | Yes — irreversible |

#### HackerNews Platform (`hackernews.*.*`)

| Scope | Description | Step-Up Required? |
|-------|-------------|-------------------|
| `hackernews.read.feed` | Read front page posts | No |
| `hackernews.vote.up` | Upvote a post or comment | No |
| `hackernews.comment.text` | Post a comment | Yes |
| `hackernews.submit.link` | Submit a link post | Yes |

### 2.4 Registering Custom Scopes

Custom platform scopes MAY be registered by third-party integrators. Custom scopes MUST:

1. Use a non-conflicting platform prefix (e.g., `myapp.action.resource`)
2. Be declared in the Stillwater Store skill submission that uses them
3. Document the step-up requirement in the scope registry entry
4. Not shadow or override any canonical scope defined in Section 2.3

Custom scope declarations are submitted to the Stillwater Store via `STORE.md` skill submission protocol.

---

## Section 3: Consent Flow

### 3.1 Overview

The consent flow is the mechanism by which a human principal explicitly approves token issuance. No AgencyToken SHALL be issued without completing the consent flow. Pre-approved tokens (issued without human review of scope list) are a violation of this specification.

The flow has three stages:
1. **Request** — Agent presents requested scopes to the consent surface
2. **Human Approval** — Principal reviews and approves (or denies) the scope list
3. **Token Issuance** — System issues a signed AgencyToken with exactly the approved scopes

### 3.2 Consent Request (GET)

**Endpoint:** `GET /oauth3/consent`

**Query Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `scopes` | REQUIRED | Comma-separated list of requested scopes (platform.action.resource format) |
| `issuer` | REQUIRED | URI of the requesting platform (e.g., `https://www.solaceagi.com`) |
| `subject` | REQUIRED | Identifier of the consenting principal |
| `ttl_seconds` | OPTIONAL | Requested token lifetime in seconds. Default: 3600. Maximum: 86400. |
| `agent_id` | OPTIONAL | Agent instance identifier for agent-locked tokens |
| `redirect_uri` | OPTIONAL | URI to redirect to after approval (for browser flows) |
| `state` | REQUIRED | CSRF protection nonce. Implementations MUST include this parameter. Consent requests without `state` MUST be rejected with 400. See RFC 6819 §4.4.1.8. |

**Example Request:**

```
GET /oauth3/consent?scopes=linkedin.post.text,linkedin.read.feed&issuer=https%3A%2F%2Fsolaceagi.com&subject=user%3Aphuc%40example.com&ttl_seconds=3600&state=csrf_nonce_abc123
```

**Normative Response (200 OK):**

```json
{
  "consent_id": "consent_550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "requested_scopes": [
    {
      "scope": "linkedin.post.text",
      "description": "Create a new text post on LinkedIn",
      "step_up_required": true,
      "risk_level": "medium"
    },
    {
      "scope": "linkedin.read.feed",
      "description": "Read the user's LinkedIn feed",
      "step_up_required": false,
      "risk_level": "low"
    }
  ],
  "issuer": "https://www.solaceagi.com",
  "subject": "user:phuc@example.com",
  "expires_in_seconds": 3600,
  "consent_ui_url": "https://www.solaceagi.com/consent/review?consent_id=consent_550e8400-...",
  "state": "csrf_nonce_abc123"
}
```

**Consent UI Origin Requirement:** The `consent_ui_url` returned in the consent response MUST be same-origin with the `issuer` URI. Agents and recipe runners MUST NOT render consent UIs from URLs whose origin differs from the token's `issuer`. An origin mismatch MUST be treated as a consent phishing attempt and logged with event `CONSENT_ORIGIN_MISMATCH`.

**Error Responses:**

| HTTP Code | Error Code | Condition |
|-----------|------------|-----------|
| 400 | `OAUTH3_INVALID_SCOPE` | Any requested scope fails the pattern check |
| 400 | `OAUTH3_UNKNOWN_SCOPE` | Any requested scope is not in the registry |
| 400 | `OAUTH3_MISSING_SUBJECT` | `subject` parameter absent |
| 400 | `OAUTH3_TTL_EXCEEDED` | `ttl_seconds` > 86400 |
| 400 | `OAUTH3_EMPTY_SCOPES` | `scopes` parameter empty |
| 403 | `OAUTH3_ISSUER_BLOCKED` | Issuer URI on block list |

### 3.3 Consent Approval (POST)

The human principal reviews the consent UI (rendered from the `consent_ui_url`) and submits approval or denial.

**Subject Authentication Requirement:** The server MUST derive the `subject` field from the authenticated session (cookie, session token, or bearer authentication), NOT from client-supplied parameters. If the `subject` in the approval request body does not match the authenticated session's principal, the server MUST reject with 403 `OAUTH3_SUBJECT_MISMATCH`.

**Endpoint:** `POST /oauth3/consent/approve`

**Request Body (JSON):**

```json
{
  "consent_id": "consent_550e8400-e29b-41d4-a716-446655440000",
  "approved_scopes": [
    "linkedin.read.feed"
  ],
  "denied_scopes": [
    "linkedin.post.text"
  ],
  "subject": "user:phuc@example.com",
  "state": "csrf_nonce_abc123"
}
```

Note: `approved_scopes` + `denied_scopes` MUST cover all scopes from the original request. Partial responses MUST be rejected.

**Normative Response (201 Created) — Token Issued:**

```json
{
  "status": "issued",
  "token": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "version": "0.1.0",
    "issued_at": "2026-02-21T10:00:00Z",
    "expires_at": "2026-02-21T11:00:00Z",
    "scopes": ["linkedin.read.feed"],
    "issuer": "https://www.solaceagi.com",
    "subject": "user:phuc@example.com",
    "step_up_required": [],
    "signature_stub": "sha256:b9f3e2a1c7d4e5f6..."
  },
  "denied_scopes": ["linkedin.post.text"],
  "audit_record": "oauth3_consent_550e8400.json"
}
```

**Response (200 OK) — All Scopes Denied:**

```json
{
  "status": "denied",
  "token": null,
  "denied_scopes": ["linkedin.post.text", "linkedin.read.feed"],
  "audit_record": "oauth3_consent_550e8400.json"
}
```

**Error Responses:**

| HTTP Code | Error Code | Condition |
|-----------|------------|-----------|
| 400 | `OAUTH3_CONSENT_EXPIRED` | `consent_id` has expired (> 10 minutes since GET) |
| 400 | `OAUTH3_CONSENT_NOT_FOUND` | `consent_id` not found |
| 400 | `OAUTH3_CSRF_MISMATCH` | `state` parameter does not match |
| 400 | `OAUTH3_PARTIAL_RESPONSE` | `approved_scopes` + `denied_scopes` does not cover all requested scopes |
| 403 | `OAUTH3_SUBJECT_MISMATCH` | `subject` in request does not match authenticated session principal |
| 409 | `OAUTH3_CONSENT_ALREADY_RESOLVED` | `consent_id` already approved or denied |

### 3.4 Step-Up Re-Consent Flow

For scopes marked `step_up_required: true`, the agent MUST pause before executing the action and re-request consent for that specific scope. The step-up flow uses the same endpoints:

1. Agent encounters a `step_up_required` scope during execution
2. Agent calls `GET /oauth3/consent?scopes={step_up_scope}&issuer=...&subject=...`
3. Human approves in UI (MUST present the specific action context, not just the scope name)
4. On approval, agent receives a short-lived sub-token (max TTL: 300 seconds) for that scope
5. Agent executes the action under the sub-token
6. Sub-token is immediately invalidated after single use

**Step-Up Token Properties:**
- `max_actions: 1` — MUST be set; single-use only
- `expires_at` — MUST be within 300 seconds of issuance
- Inherits `subject` and `issuer` from parent token
- Parent token MUST still be valid (not expired, not revoked) for step-up to be valid

---

## Section 4: Revocation

### 4.1 Revocation Semantics

Revocation is the mechanism by which a principal invalidates a previously issued AgencyToken. Revocation MUST take effect immediately and synchronously. For single-node deployments, any gate check (G4 in Section 1.4) MUST reflect revocation within 1 second of the DELETE call returning 200. For multi-node deployments, implementations MUST document their replication lag and SHOULD use a strongly-consistent distributed store (e.g., etcd, CockroachDB). Multi-node implementations MUST NOT claim compliance with the 1-second guarantee unless they can demonstrate it under load.

Revocation is permanent. A revoked token CANNOT be re-activated.

### 4.2 Revocation Endpoint (DELETE)

**Endpoint:** `DELETE /oauth3/tokens/{token_id}`

**Path Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `token_id` | REQUIRED | The `id` field of the AgencyToken to revoke |

**Headers:**

| Header | Required | Description |
|--------|----------|-------------|
| `X-Revocation-Subject` | REQUIRED | Must match the `subject` field of the token being revoked |
| `X-Revocation-Reason` | OPTIONAL | Human-readable reason for revocation (logged to audit) |

**Example Request:**

```
DELETE /oauth3/tokens/a1b2c3d4-e5f6-7890-abcd-ef1234567890
X-Revocation-Subject: user:phuc@example.com
X-Revocation-Reason: User manually revoked via UI
```

**Normative Response (200 OK) — Revocation Successful:**

```json
{
  "status": "revoked",
  "token_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "revoked_at": "2026-02-21T10:30:00Z",
  "revoked_by": "user:phuc@example.com",
  "reason": "User manually revoked via UI",
  "audit_record": "oauth3_revocation_a1b2c3d4.json"
}
```

**Error Responses:**

| HTTP Code | Error Code | Condition |
|-----------|------------|-----------|
| 404 | `OAUTH3_TOKEN_NOT_FOUND` | Token ID does not exist in registry |
| 403 | `OAUTH3_REVOCATION_FORBIDDEN` | `X-Revocation-Subject` does not match token's `subject` |
| 409 | `OAUTH3_TOKEN_ALREADY_REVOKED` | Token was already revoked (returns revocation timestamp) |

### 4.3 Bulk Revocation (Subject Revocation)

**Endpoint:** `DELETE /oauth3/tokens`

Revokes ALL tokens for a given subject. MUST be used when a user account is compromised or when the user terminates their session.

**Request Body (JSON):**

```json
{
  "subject": "user:phuc@example.com",
  "issuer": "https://www.solaceagi.com",
  "reason": "Account session terminated"
}
```

**Normative Response (200 OK):**

```json
{
  "status": "bulk_revoked",
  "subject": "user:phuc@example.com",
  "tokens_revoked": 3,
  "revoked_at": "2026-02-21T10:30:00Z",
  "audit_record": "oauth3_bulk_revocation_2026-02-21T10-30-00Z.json"
}
```

### 4.4 Revocation Registry

Implementations MUST maintain a revocation registry. Minimum requirements:

- **Persistence:** Registry MUST survive process restart. Acceptable storage: SQLite, Redis with persistence, append-only flat file.
- **Format (flat file option):** One revoked token ID per line, with timestamp:
  ```
  a1b2c3d4-e5f6-7890-abcd-ef1234567890 2026-02-21T10:30:00Z
  ```
- **Lookup time:** O(1) preferred (hash set). O(log n) acceptable. O(n) MUST NOT be used in production.
- **Cleanup:** Expired tokens (past `expires_at` by > 24 hours) MAY be pruned from the registry; they are implicitly invalid via the TTL gate (G2) regardless.

### 4.5 Agent Behavior on Revocation Discovery

If an agent discovers that its current token has been revoked (via G4 gate failure mid-execution), it MUST:

1. Immediately halt all actions authorized under the revoked token
2. Log the mid-execution revocation to `oauth3_audit.json` with `event: "REVOCATION_DISCOVERED_MID_EXECUTION"`
3. NOT attempt to continue under a different token without new consent
4. Report the halt to the user with the revoked token ID and revocation timestamp

---

## Section 5: Evidence Bundle

### 5.1 Purpose

Every token operation (issuance, validation, action execution, revocation) MUST produce an audit record. This is the evidence bundle. The evidence bundle enables:

- Non-repudiation: the principal cannot deny authorizing an action
- Debugging: failed actions have a trace of which gate blocked them
- Regulatory compliance: audit trail for actions taken by AI agents
- Stillwater rung verification: Lane A evidence for recipe execution

### 5.2 oauth3_audit.json Schema

Each token operation produces one `oauth3_audit.json` record. Records for a session are appended to a JSONL file (one JSON object per line).

**Per-operation record schema:**

```json
{
  "$schema": "https://stillwater.dev/schemas/oauth3/audit/v0.1.json",
  "audit_id": "string (UUID v4)",
  "event": "string (see event registry below)",
  "timestamp": "string (ISO 8601 UTC)",
  "token_id": "string (UUID v4) | null",
  "subject": "string | null",
  "issuer": "string | null",
  "scope": "string | null (the specific scope of the action, if applicable)",
  "platform": "string | null (target platform domain, e.g. 'linkedin.com')",
  "status": "string ('PASS' | 'BLOCKED' | 'REVOKED' | 'STEP_UP_REQUIRED')",
  "gate_failed": "string | null (G1/G2/G3/G4 if status=BLOCKED)",
  "action_description": "string | null (human-readable description of the action attempted)",
  "artifact_path": "string | null (path to output artifact if action succeeded)",
  "artifact_sha256": "string | null (SHA-256 hex of artifact file if action succeeded)",
  "error_code": "string | null (OAUTH3_* code if status=BLOCKED)",
  "error_detail": "string | null",
  "metadata": "object | null (implementation-specific fields)",
  "previous_hash": "string (SHA-256 hex of previous audit record, or session nonce for genesis record)"
}
```

**Audit Record Chain (v0.1.1):** Each audit record MUST include a `previous_hash` field containing the SHA-256 hex digest of the previous record in the JSONL file. The genesis record (first in a session) MUST use a session nonce as the `previous_hash` value. This creates a hash chain that detects record deletion or reordering. Implementations MUST verify chain integrity before using audit records as Lane A evidence.

### 5.3 Event Registry

| Event | When | Required Fields |
|-------|------|-----------------|
| `TOKEN_ISSUED` | After successful `POST /oauth3/consent/approve` | `token_id`, `subject`, `issuer`, `scopes` (in metadata) |
| `TOKEN_VALIDATED` | After all 4 gates pass | `token_id`, `scope`, `status: PASS` |
| `TOKEN_GATE_FAILED` | After any gate failure | `token_id`, `gate_failed`, `error_code`, `status: BLOCKED` |
| `ACTION_STARTED` | Before executing an agent action | `token_id`, `scope`, `platform`, `action_description` |
| `ACTION_COMPLETED` | After successful action execution | `token_id`, `scope`, `platform`, `artifact_path`, `artifact_sha256` |
| `ACTION_FAILED` | After action execution failure (non-gate) | `token_id`, `scope`, `platform`, `error_detail` |
| `STEP_UP_REQUIRED` | Before step-up re-consent | `token_id`, `scope`, `status: STEP_UP_REQUIRED` |
| `STEP_UP_APPROVED` | After step-up consent granted | `token_id`, `scope` |
| `TOKEN_REVOKED` | After `DELETE /oauth3/tokens/{id}` | `token_id`, `subject`, `status: REVOKED` |
| `REVOCATION_DISCOVERED_MID_EXECUTION` | Agent discovers revocation during execution | `token_id`, `scope`, `platform` |
| `CONSENT_DENIED` | All scopes denied by principal | `token_id: null`, `subject`, `issuer` |

### 5.4 Canonical Audit Record Examples

**Successful action execution:**

```json
{
  "audit_id": "f7a3b9c2-1d4e-5f6a-7b8c-9d0e1f2a3b4c",
  "event": "ACTION_COMPLETED",
  "timestamp": "2026-02-21T10:15:32Z",
  "token_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "subject": "user:phuc@example.com",
  "issuer": "https://www.solaceagi.com",
  "scope": "linkedin.read.feed",
  "platform": "linkedin.com",
  "status": "PASS",
  "gate_failed": null,
  "action_description": "Read LinkedIn feed, discovered 12 posts with >50 engagement",
  "artifact_path": "artifacts/runs/f7a3b9c2/result.json",
  "artifact_sha256": "sha256:d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4",
  "error_code": null,
  "error_detail": null,
  "metadata": {
    "solace.recipe_id": "linkedin-discover-posts",
    "solace.task_id": "task_550e8400"
  }
}
```

**Gate failure (token expired):**

```json
{
  "audit_id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
  "event": "TOKEN_GATE_FAILED",
  "timestamp": "2026-02-21T11:05:00Z",
  "token_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "subject": "user:phuc@example.com",
  "issuer": "https://www.solaceagi.com",
  "scope": "linkedin.post.text",
  "platform": "linkedin.com",
  "status": "BLOCKED",
  "gate_failed": "G2",
  "action_description": "Attempted to post text to LinkedIn",
  "artifact_path": null,
  "artifact_sha256": null,
  "error_code": "OAUTH3_TOKEN_EXPIRED",
  "error_detail": "Token expired at 2026-02-21T11:00:00Z; current time is 2026-02-21T11:05:00Z",
  "metadata": null
}
```

**Gate failure (scope not granted):**

```json
{
  "audit_id": "e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0b",
  "event": "TOKEN_GATE_FAILED",
  "timestamp": "2026-02-21T10:20:00Z",
  "token_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "subject": "user:phuc@example.com",
  "issuer": "https://www.solaceagi.com",
  "scope": "linkedin.delete.post",
  "platform": "linkedin.com",
  "status": "BLOCKED",
  "gate_failed": "G3",
  "action_description": "Attempted to delete a LinkedIn post",
  "artifact_path": null,
  "artifact_sha256": null,
  "error_code": "OAUTH3_SCOPE_DENIED",
  "error_detail": "Scope 'linkedin.delete.post' not in granted scopes: [linkedin.read.feed, linkedin.react.like]",
  "metadata": null
}
```

### 5.5 Evidence File Naming Convention

| File | Location | Contents |
|------|----------|----------|
| `oauth3_audit.jsonl` | `artifacts/oauth3/` | JSONL append-only log of all audit events for the session |
| `oauth3_consent_{consent_id}.json` | `artifacts/oauth3/consents/` | Full consent request and approval record |
| `oauth3_revocation_{token_id}.json` | `artifacts/oauth3/revocations/` | Revocation record with timestamp and reason |
| `oauth3_token_{token_id}.json` | `artifacts/oauth3/tokens/` | The issued token (public fields only; no private keys) |

### 5.6 Evidence Integrity

All evidence files MUST include a SHA-256 self-hash in their filename or in an accompanying `.sha256` sidecar file:

```
oauth3_audit.jsonl
oauth3_audit.jsonl.sha256        ← contains the hex digest of the jsonl file at seal time
```

The SHA-256 is computed over the full file content at the time of sealing (end of session or explicit flush). Implementations MUST recompute and verify the hash before using an evidence file as Lane A evidence in a Stillwater verification run.

---

## Section 6: Competitive Landscape and Differentiation

### 6.1 Overview

OAuth3 addresses a problem space that existing authorization standards do not cover: the post-token lifecycle of an AI agent acting on behalf of a human principal. This section characterizes each adjacent standard, identifies what it solves, what it does not solve, and how OAuth3 relates to it. The analysis is structured to be accurate and falsifiable: any claim below can be verified against the referenced standard documents.

The key finding is that the existing landscape splits along a single fault line:

- **Pre-token protocols** (OAuth 2.x family, IETF OBO draft, AAuth, OIDC-A): define how an agent _acquires_ authorization. They are silent on what happens after the token is issued.
- **Framework-level access control** (OpenClaw, Browser-Use, Bardeen): define what tools an agent _can invoke_. They have no formal authorization layer, no evidence requirement, and no revocation semantics.

OAuth3 occupies the gap between these two categories. It does not compete with pre-token protocols — it extends them. It does not compete with agent frameworks — it governs them.

### 6.2 Comparison Table

The table below evaluates each standard or framework across the seven properties that OAuth3 defines normatively.

| Property | OAuth3 | IETF OBO Draft | AAuth | OIDC-A 1.0 | OpenClaw | Browser-Use / Bardeen |
|---|---|---|---|---|---|---|
| **Domain** | Post-token agent action governance | Pre-token delegation acquisition | Agent identity verification | Agent identity in OIDC | Agent framework (skill execution) | Browser automation |
| **Scope format** | `platform.action.resource` (triple-segment, normative registry) | OAuth 2.x free-form strings | Not defined | OIDC `scope` claim | Skill names (no authorization layer) | Not defined |
| **Step-up consent mid-execution** | Required for `step_up_required` scopes (Section 3.4) | Not addressed | Not addressed | Not addressed | Not addressed | Not addressed |
| **Evidence bundle (per-action audit)** | Required (`oauth3_audit.jsonl`, Section 5) | Not addressed | Not addressed | Not addressed | Not addressed | Not addressed |
| **Synchronous revocation** | Required (< 1 second, Section 4.1) | Not addressed | Not addressed | Not addressed | Not addressed | Not addressed |
| **Action limits (`max_actions`)** | Normative token field (Section 1.2) | Not addressed | Not addressed | Not addressed | Not addressed | Not addressed |
| **Platform allowlist** | Normative token field (`platforms`, Section 1.2) | Not addressed | Not addressed | Not addressed | Not addressed | Not addressed |
| **Delegation chain (actor identity)** | `agent_id` field (optional lock, Section 1.2) | JWT `act` claim (nested sub, RFC 8693) | Core feature | OIDC ID token extension | Implicit (process identity) | Not defined |
| **Token acquisition flow** | Section 3 (consent-first issuance) | Full specification (PKCE, short-lived codes) | Partial | Full OIDC flow | Not defined | Not defined |
| **Rung-gated skill trust** | Normative (Appendix C, Stillwater integration) | Not addressed | Not addressed | Not addressed | Not defined (ClawHavoc breach) | Not addressed |

### 6.3 IETF draft-oauth-ai-agents-on-behalf-of-user

**Document:** draft-oauth-ai-agents-on-behalf-of-user (IETF draft, expires 2026-02-27)

**What it solves:** The IETF OBO draft defines how an AI agent acquires an OAuth 2.0 token that represents a delegated user context. It introduces a `requested_actor` parameter at the authorization endpoint and an `actor_token` at the token endpoint. The delegation chain is encoded in a JWT `act` claim (RFC 8693), which nests the actor's `sub` identifier inside the delegated token. The draft enforces PKCE (RFC 7636), short-lived authorization codes, and requires consent UIs to "clearly display client identity, requested actor identity, and specific access scopes."

This is a well-scoped, technically rigorous contribution to the pre-token acquisition problem.

**What it does not solve:** The IETF draft is silent on everything that happens after the token is issued. It specifies no requirements for:
- What the agent may do with the token (no action limits, no platform allowlist)
- Whether high-risk actions require a pause for re-consent (no step-up model)
- What evidence the agent must produce to prove it acted within scope (no audit requirement)
- How revocation is made synchronous and immediately enforceable (defers to RFC 7009, which is asynchronous)
- How many actions the token authorizes (unbounded by default)

**Relationship to OAuth3:** Complementary. The IETF OBO draft solves token acquisition. OAuth3 governs the token's post-issuance lifecycle. A conformant implementation SHOULD use both: the IETF OBO draft to issue the AgencyToken through a standards-compliant delegation flow, and OAuth3 gates (Sections 1, 4, 5) to govern agent behavior under that token.

**Strategic note:** The IETF draft expires 2026-02-27. This is a deliberate IETF working document lifecycle checkpoint, not a sunset of the concept. The expiry date signals that the working group is actively developing this area. OAuth3's complementary positioning ensures that adoption of the IETF standard does not displace OAuth3 — it creates demand for it.

### 6.4 AAuth (Agent Authentication)

**What it solves:** AAuth, proposed by agent framework vendors, focuses on the identity verification problem: proving that a request comes from a specific agent instance rather than an impersonator. It defines how agents present credentials to services that need to trust the caller's identity.

**What it does not solve:** AAuth addresses the identity plane, not the authorization plane. It has no delegation semantics: a verified identity is not the same as a consented scope. AAuth does not specify what an authenticated agent is permitted to do, how many actions it may take, whether actions must be audited, or how a human principal can revoke an ongoing session. There is no evidence bundle requirement.

**Relationship to OAuth3:** AAuth and OAuth3 address different layers. AAuth answers "who is this agent?" OAuth3 answers "what is this agent allowed to do, and what did it actually do?" An implementation MAY use AAuth for agent identity establishment and OAuth3 for action authorization. OAuth3's `agent_id` field (Section 1.2) provides a binding point: the AAuth-verified agent identity MAY be placed in `agent_id` to create an agent-locked token.

### 6.5 OIDC-A 1.0 (OpenID Connect for Agents)

**What it solves:** OIDC-A 1.0 extends OpenID Connect to include agent identity claims in the ID token. This allows a service provider to know that a session was initiated by an AI agent acting for a user, and to receive structured claims about the agent's identity and capabilities at authentication time.

**What it does not solve:** Like OIDC, OIDC-A treats authorization as a downstream concern handled by the resource server and access token. OIDC-A does not specify post-token agent behavior. It defines no step-up consent model for mid-execution high-risk actions, no per-action evidence requirement, no action limits, and no synchronous revocation. The protocol boundary ends at the ID token.

**Relationship to OAuth3:** OIDC-A establishes the authentication context that MAY precede OAuth3 consent issuance. An OAuth3 implementation MAY use an OIDC-A flow to authenticate the agent before the `GET /oauth3/consent` call (Section 3.2). The subject identifier established in the OIDC-A ID token MAY be used as the `subject` claim in the resulting AgencyToken.

### 6.6 OpenClaw

**What it solves:** OpenClaw is an open-source AI agent framework with reported deployments of 21,000 instances and 53 skills. It provides a runtime for multi-agent task execution, including skill chaining and tool invocation. It solves the orchestration problem: how to compose agent capabilities into multi-step workflows.

**What it does not solve:** The ClawHavoc security breach demonstrated that OpenClaw's skill trust model is structurally broken. A post-mortem of that incident confirmed that 1,184 malicious skills ran unchecked across the deployment. The root cause is architectural: OpenClaw has no rung gates, no evidence bundles, no consent flow for skill-level scope escalation, and no revocation mechanism. Skills execute at the framework level without human authorization of individual scope grants.

A skill in OpenClaw is equivalent to a function call with no authorization wrapper. The framework assumes that installing a skill implies unlimited trust in that skill's scope of action. This is the authorization assumption that OAuth3 was designed to eliminate.

**Relationship to OAuth3:** OpenClaw and OAuth3 are not directly competing standards — OpenClaw is a framework, OAuth3 is an authorization protocol. However, they address the same deployment context (AI agent action on external platforms), and their designs reflect fundamentally different trust models. OpenClaw's model is implicit trust (installed = trusted). OAuth3's model is explicit, revocable, scope-bounded, evidenced consent. An OpenClaw deployment SHOULD implement OAuth3 as its authorization layer to remediate the ClawHavoc-class vulnerability class.

### 6.7 Browser Automation Frameworks: Browser-Use, Bardeen, and Vercel agent-browser

**What they solve:** This class of tools (Browser-Use, Bardeen, Vercel agent-browser) provides AI agents with the ability to control a web browser — navigating pages, filling forms, clicking UI elements, and extracting content. They solve the browser control problem competently.

**What they do not solve:** None of these frameworks define an authorization standard. From an authorization perspective:

- There is no consent flow: the agent is granted access to the browser session without the user explicitly approving a scope list.
- There is no evidence bundle: actions taken in the browser are not logged to a tamper-evident audit record.
- There is no revocation mechanism: once a browser session is live, the user cannot revoke a specific action authorization without terminating the entire session.
- There is no scope registry: the agent's capability is bounded only by what the browser can do, not by what the user has authorized the agent to do.

Browser-Use is session-scoped but not consent-scoped. Bardeen is limited to Chrome extension deployment with no cloud authorization layer. Vercel agent-browser is cloud-only with no recipe library and no OAuth3 integration.

**Relationship to OAuth3:** These frameworks SHOULD use OAuth3 as their authorization layer. The OAuth3 scope format (Section 2) directly supports browser automation use cases: `linkedin.post.text`, `gmail.send.email`, `github.merge.pr` are all browser-executable actions that are also OAuth3 scope-bounded. An agent using Browser-Use as its browser driver and OAuth3 as its authorization protocol would be the correct layered architecture.

### 6.8 OAuth3's Unique Contributions

The following properties are defined normatively in this specification and are not present in any of the above standards or frameworks:

1. **Post-token action governance.** OAuth3 governs what an agent does _after_ it holds a valid token. No pre-token standard (IETF OBO, OIDC-A, AAuth) specifies post-token behavior. No agent framework (OpenClaw, Browser-Use) specifies a formal authorization layer.

2. **Step-up re-consent mid-execution.** The `step_up_required` mechanism (Section 3.4) allows a token to authorize a broad set of actions while requiring the human principal to re-approve specific high-risk actions at execution time, with full action context visible. This is a qualitatively different consent model from one-time upfront approval.

3. **Mandatory evidence bundles.** Every token operation produces a structured, tamper-evident audit record (Section 5). This is not optional telemetry — it is a normative gate. An agent that cannot produce `oauth3_audit.jsonl` is non-conformant. No adjacent standard requires this.

4. **Synchronous revocation with < 1 second propagation.** The revocation requirement in Section 4.1 is normative and immediate. RFC 7009 (OAuth 2.x revocation) is advisory and asynchronous. For AI agents that can execute dozens of actions per minute, asynchronous revocation is insufficient.

5. **Action limits as a first-class token field.** The `max_actions` field (Section 1.2) is a normative constraint on the token itself. No other standard places an action budget directly on the authorization object.

6. **Platform allowlist as a first-class token field.** The `platforms` field (Section 1.2) restricts the agent to a declared set of target domains. A token issued for `linkedin.com` MUST NOT be used to authorize actions on `twitter.com`, even if the action type is identical.

7. **Rung-gated skill trust.** The Stillwater integration (Appendix C) ties OAuth3 token operations to a verified rung hierarchy. Skill trust is not implicit (OpenClaw model) but is a function of demonstrated, evidence-backed verification rungs.

### 6.9 Positioning Statement

OAuth3 coins the category of **delegated agency authorization** — the authorization layer that governs AI agent action between token acquisition and session termination. We define this category. We set the terms.

The IETF working group defines pre-token delegation acquisition. OAuth3 defines post-token agent governance. These are not competing positions — they are adjacent layers in the same stack. A complete AI agency authorization architecture requires both.

For AI agent frameworks that currently operate without any authorization layer, OAuth3 is the path to trust. For platforms deploying multi-agent systems at scale, OAuth3 is the audit requirement they will eventually be compelled to meet. We publish this specification now so that the standard exists before the regulatory mandate requires it.

---

## Section 7: Proof-of-Possession (DPoP)

### 7.1 Overview

OAuth3 v0.1 uses bearer tokens: possession of the token alone grants authority. DPoP (Demonstrating Proof-of-Possession, RFC 9449) upgrades this by binding each token to a specific agent's cryptographic key pair. A stolen token cannot be replayed without the agent's private key.

DPoP is RECOMMENDED for all OAuth3 deployments in v0.1.1. DPoP MUST be supported by all implementations claiming v1.0 compliance.

### 7.2 Agent Key Pair

Each OAuth3 agent MUST generate an ECDSA P-256 key pair at initialization. The private key MUST be stored encrypted at rest (AES-256-GCM minimum). The public key is included in DPoP proofs and bound to the token at issuance.

The agent's public key identifier is the JWK Thumbprint (RFC 7638) of the public key. This thumbprint replaces the string-based `agent_id` field as the canonical agent identifier in v1.0.

### 7.3 Token Binding

At consent approval (Section 3.3), the agent includes its DPoP proof in the token request. The consent server:
1. Extracts the agent's public key from the DPoP proof header
2. Computes the JWK Thumbprint
3. Includes the thumbprint in the issued token as a `cnf` (confirmation) claim:

```json
{
  "cnf": {
    "jkt": "SHA-256-base64url-thumbprint-of-agents-jwk"
  }
}
```

AgencyTokens with a `cnf` claim are DPoP-bound. The `cnf` claim is OPTIONAL in v0.1.1 and REQUIRED in v1.0.

### 7.4 DPoP Proof Structure

Each request to an OAuth3 enforcement gate MUST include a DPoP proof in the `DPoP` HTTP header. The proof is a JWT with:

Header:
```json
{
  "typ": "dpop+jwt",
  "alg": "ES256",
  "jwk": {
    "kty": "EC",
    "crv": "P-256",
    "x": "...",
    "y": "..."
  }
}
```

Payload:
```json
{
  "jti": "unique-proof-id-uuid-v4",
  "htm": "POST",
  "htu": "https://enforcement.example.com/oauth3/action",
  "iat": 1709000000,
  "ath": "base64url-SHA-256-of-the-access-token"
}
```

- `jti`: Unique proof identifier. Enforcement gates MUST reject duplicate `jti` values within a time window.
- `htm`: HTTP method of the request.
- `htu`: HTTP URI of the target endpoint (scheme + authority + path, no query/fragment).
- `iat`: Issuance time. MUST be within 60 seconds of current time (accounting for clock skew).
- `ath`: Base64url-encoded SHA-256 hash of the ASCII representation of the associated access token.

### 7.5 Validation Gate G5: DPoP

Add a fifth validation gate to the existing four gates (Section 1.4):

| Gate | Check | Failure Action |
|------|-------|----------------|
| G5: DPoP | DPoP proof present, valid signature, JWK thumbprint matches token `cnf.jkt`, `htm`/`htu` match request, `iat` within 60s, `jti` not replayed | BLOCKED: OAUTH3_DPOP_INVALID |

G5 is checked AFTER G1-G4. All five gates must pass before action execution.

When `cnf` is present in the token, G5 is REQUIRED. When `cnf` is absent (v0.1 bearer tokens), G5 is skipped. In v1.0, `cnf` is always present, so G5 is always enforced.

### 7.6 DPoP Error Codes

| Error Code | Condition |
|------------|-----------|
| `OAUTH3_DPOP_MISSING` | Token has `cnf` claim but request has no DPoP header |
| `OAUTH3_DPOP_INVALID_SIGNATURE` | DPoP proof signature does not verify |
| `OAUTH3_DPOP_BINDING_MISMATCH` | JWK thumbprint in proof does not match `cnf.jkt` in token |
| `OAUTH3_DPOP_EXPIRED` | DPoP `iat` is more than 60 seconds old |
| `OAUTH3_DPOP_REPLAY` | DPoP `jti` has been seen before within the replay window |
| `OAUTH3_DPOP_METHOD_MISMATCH` | DPoP `htm` does not match actual HTTP method |
| `OAUTH3_DPOP_URI_MISMATCH` | DPoP `htu` does not match actual request URI |

### 7.7 Audit Record Extension

DPoP-bound actions MUST include additional fields in the audit record (Section 5.2):
- `dpop_jkt`: The JWK thumbprint of the agent that presented the proof
- `dpop_jti`: The proof's unique identifier (for replay detection audit)

### 7.8 Backward Compatibility

- v0.1.1 implementations SHOULD support DPoP but MUST accept bearer tokens
- v1.0 implementations MUST require DPoP and MUST NOT accept plain bearer tokens
- Mixed deployments: enforcement gate checks for `cnf` in token; if present, DPoP required; if absent, bearer accepted

---

## Appendix A: Comparison to OAuth 2.x

| Property | OAuth 2.x | OAuth3 |
|----------|-----------|--------|
| Authorizes | Data access | Agent actions |
| Scope format | Free-form string | platform.action.resource (triple-segment) |
| Step-up auth | Optional (PKCE) | Required for high-risk scopes |
| Evidence bundle | Not defined | Required per token operation |
| Revocation | RFC 7009 (async) | Synchronous (< 1s) |
| Agent identity | Not addressed | agent_id field (optional lock) |
| Bulk revocation | Not standard | Defined (DELETE /oauth3/tokens) |
| Audit trail | Not required | Required (oauth3_audit.jsonl) |

## Appendix B: Security Considerations

### B.1 Signature Stub (v0.1 Limitation)

The `signature_stub` field in v0.1 is a SHA-256 digest over the canonical JSON of the token, NOT a cryptographic signature from a keypair. This means:

- Token integrity check detects accidental corruption
- Token integrity check does NOT prevent a malicious party from generating a valid-looking token if they have access to the canonical JSON format

**Mitigation in v0.1:** The revocation registry and the consent server are the authoritative source of token validity. Enforcement systems MUST validate token issuance via the `/oauth3/tokens/{id}` registry lookup, not just the signature_stub.

**v1.0 plan:** Replace `signature_stub` with ECDSA-P256 signature over canonical JSON. The issuer holds the private key; enforcement systems verify against the issuer's published public key.

### B.2 Token Storage

- Tokens MUST be stored encrypted at rest (AES-256-GCM minimum)
- Tokens MUST NOT be logged in plaintext to general system logs
- Tokens MUST NOT appear in URLs (use request body or Authorization header)
- The `oauth3_audit.jsonl` file contains `token_id` (UUID) but MUST NOT contain the full token JSON

### B.3 Consent UI Requirements

The consent UI MUST:
- Display the full scope list with plain-language descriptions
- Display the requested TTL
- Display the issuer identity (not just URI — resolve to display name)
- Provide scope-level granularity (user can deny individual scopes)
- Not use dark patterns (pre-checked boxes, confusing deny flows)
- Use CSRF protection (`state` nonce validation)

### B.4 Platform Respect

Agents operating under OAuth3 tokens MUST:
- Identify themselves as automated agents if required by platform terms
- Respect platform rate limits
- Not impersonate other users
- Not aggregate data beyond what the authorized scope permits
- Not bypass security controls (CAPTCHAs, 2FA, IP-based rate limiting)

---

## Appendix C: Stillwater Integration

### C.1 Rung Requirements for OAuth3

| Operation | Minimum Rung | Rationale |
|-----------|-------------|-----------|
| Spec compliance check | 641 | Local correctness |
| Enforcement skill production use | 65537 | Production/security gate |
| Revocation registry deployment | 274177 | Persistence required |
| PKI signature implementation (v1.0) | 65537 | Security-critical |

### C.2 Integration Points

- `skills/oauth3-enforcer.md` — loads this spec, implements the 4 gates, outputs `oauth3_audit.json`
- `solace-browser/` — OAuth3 reference implementation (issues tokens, hosts consent UI, maintains revocation registry)
- `solace-cli/` — CLI client (presents tokens to enforcement gates, stores tokens in AES-256-GCM vault)
- `STORE.md` — requires scope declaration for any skill touching external platforms

### C.3 Recipe Integration Pattern

Any recipe touching an external platform MUST include:

```json
{
  "oauth3": {
    "required_scopes": ["linkedin.read.feed", "linkedin.post.text"],
    "step_up_scopes": ["linkedin.post.text"],
    "min_ttl_seconds": 300,
    "evidence_output": "artifacts/oauth3/oauth3_audit.jsonl"
  }
}
```

The `oauth3-enforcer` skill reads this block and enforces all four gates before the recipe's first step executes.

---

## Appendix D: FDA 21 CFR Part 11 Compliance Mapping

### D.1 Purpose and Scope

This appendix maps every normative OAuth3 mechanism to the corresponding requirement in Title 21 CFR Part 11 — the FDA regulation governing electronic records and electronic signatures in clinical and regulated industries. The mapping demonstrates that an OAuth3 implementation, when deployed against this specification at rung ≥ 274177, satisfies Part 11 requirements as a complete delegation-and-evidence framework.

The FDA guidance documents referenced herein are:

- **21 CFR Part 11** — Electronic Records; Electronic Signatures (Final Rule, 1997)
- **FDA Guidance for Industry: Part 11, Electronic Records; Electronic Signatures — Scope and Application** (2003)
- **FDA Guidance: Data Integrity and Compliance with Drug CGMP** (2018)
- **FDA Guidance: Computer Software Assurance for Production and Quality System Software** (2022)

All normative language in this appendix ("MUST", "SHALL", "REQUIRED") is interpreted per RFC 2119.

---

### D.2 Compliance Matrix

The following table maps each Part 11 requirement to the specific OAuth3 field, mechanism, or section that satisfies it. An implementation that conforms to the normative requirements of this specification MUST satisfy each mapping entry as written.

| Part 11 Requirement | CFR Citation | OAuth3 Mechanism | Spec Reference | Gap (v0.1) |
|---------------------|-------------|-----------------|----------------|------------|
| Audit trail — computer-generated, time-stamped | §11.10(e) | `oauth3_audit.jsonl` — append-only JSONL, ISO 8601 UTC timestamps on every record | §5.2, §5.3 | None |
| Record integrity — detect invalid or altered records | §11.10(a) | SHA-256 self-hash on every evidence file + sidecar `.sha256` verification file | §5.4 | None |
| Access controls — limit access to authorized individuals | §11.10(d) | Consent flow (Section 3) + scope-level granularity + step-up re-consent | §3.1–§3.4 | None |
| Authority checks — only authorized users can use system | §11.10(g) | 4-gate validation (G1–G4): token presence, scope match, expiry, revocation status | §1.4 | None |
| Electronic signature — legally equivalent to handwritten | §11.50–§11.200 | `signature_stub` field (SHA-256 digest in v0.1); full ECDSA-P256 in v1.0 | §1.2 | ECDSA-P256 required for full §11.50 equivalence — see §D.3 |
| Signature non-repudiation | §11.100(a) | `issuer` + `subject` + `agent_id` + `signature_stub` together constitute the bound identity claim | §1.2 | ECDSA binding of key to identity required in v1.0 |
| Signature meaning — indicate the purpose of signing | §11.50(a) | `scopes` array enumerates the specific actions authorized; each scope is a human-readable triple (`resource.verb.target`) | §2.1 | None |
| Signature components — printed name, date/time, meaning | §11.50(b) | `subject` (printed name/identity), `issued_at` (date/time), `scopes` (meaning/purpose) | §1.2 | None |
| Attributable — data traceable to originating individual | ALCOA+ A | `subject` field (human principal), `issuer` field (server), `agent_id` field (delegated agent) | §1.2, §5.2 | None |
| Legible — human-readable records | ALCOA+ L | JSON schema with `description` annotations on every field; scope triple is English-readable (`linkedin.post.text`) | §1.2, §2.1 | None |
| Contemporaneous — recorded at time of activity | ALCOA+ C | `issued_at`, `expires_at`, and every `oauth3_audit.jsonl` record timestamp MUST be generated at the moment of the operation, not retroactively | §1.2, §5.3 | None |
| Original — first capture of data, not a copy | ALCOA+ O | JSONL append-only format prohibits edit or delete; revocation adds a new record and MUST NOT modify the original | §4.1, §5.3 | None |
| Accurate — correct and truthful record | ALCOA+ Ac | SHA-256 hash chain on evidence files; G1–G4 fail-closed validation ensures only authorized, valid tokens produce records | §1.4, §5.4 | None |
| Complete — all data present, nothing omitted | ALCOA+ Co | Event registry covers the full token lifecycle: 11 mandatory event types (issued, consent_granted, consent_denied, step_up_granted, step_up_denied, used, expired, revoked, bulk_revoked, gate_passed, gate_failed) | §5.2 | None |
| Consistent — data are internally self-consistent | ALCOA+ Cs | JSON Schema validation at issuance + triple-segment scope format enforced by G2; `$schema` field in every token | §1.2, §2.1, §1.4 | None |
| Enduring — records persist for the intended retention period | ALCOA+ E | Revocation registry MUST be persisted to durable storage; evidence file naming convention (`oauth3_<event>_<token_id_prefix>.json`) prevents collision and enables long-term archival | §4.1, §5.1 | None |
| Available — records accessible for review and inspection | ALCOA+ Av | Evidence file structure under `artifacts/oauth3/` with defined, stable paths; the `evidence_output` field in recipes specifies the canonical location | §5.1, Appendix C §C.3 | None |

---

### D.3 Electronic Signature Compliance Path

#### D.3.1 v0.1 Status: Signature Stub

In v0.1.0 of this specification, the `signature_stub` field carries a SHA-256 digest of the token body. This satisfies record integrity under §11.10(a) but does NOT yet constitute a legally binding electronic signature under §11.50–§11.200 for the following reason:

> FDA Part 11 §11.100(a) requires that electronic signatures be "unique to one individual" and "not reused by, or reassigned to, anyone else." A bare SHA-256 hash does not bind the identity of the signer to the token cryptographically — it cannot prove that the individual named in `subject` produced the signature.

Implementations operating under v0.1.0 in regulated environments MUST treat `signature_stub` as an integrity check only and MUST supplement it with a separate identity assurance mechanism (e.g., SSO provider assertion, PKI certificate, biometric challenge) to satisfy §11.100(a).

#### D.3.2 v1.0 Requirement: ECDSA-P256

Version 1.0 of this specification SHALL require the following upgrade to satisfy §11.50–§11.200 in full:

- `signature_stub` SHALL be replaced by `signature`, carrying an ECDSA-P256 signature over the canonical serialization of the token body (excluding the `signature` field itself).
- The signing key MUST be bound to the `subject` identity via a certificate or verifiable credential that links the cryptographic key to the named individual.
- The verification key MUST be published in the issuer's JWKS endpoint at a well-known URI.
- Implementations MUST verify the ECDSA signature at G1 (token presence and integrity gate).

Until this upgrade is deployed, an implementation CANNOT claim full Part 11 electronic signature equivalence under §11.50.

---

### D.4 Audit Trail Requirements — §11.10(e) Mapping

Section 11.10(e) of Part 11 requires:

> "Use of secure, computer-generated, time-stamped audit trails to independently record the date and time of operator entries and actions that create, modify, or delete electronic records."

The `oauth3_audit.jsonl` file specified in Section 5 satisfies this requirement as follows:

**Computer-generated.** The audit record MUST be written by the `oauth3-enforcer` implementation automatically, without operator involvement. Manual creation or modification of audit records is a violation of this specification.

**Time-stamped.** Every audit record MUST carry an `event_timestamp` field in ISO 8601 UTC format. The timestamp MUST be generated by the server system clock at the moment the event occurs, not supplied by the client.

**Independently records entries and actions.** Each of the 11 mandatory event types (see §5.2) represents a distinct operational event. No operation that creates, modifies, or terminates a token delegation may occur without a corresponding audit record.

**Secure.** The JSONL file MUST be stored with write-once semantics (append only). Systems that support file system access controls MUST restrict write access to the `oauth3-enforcer` process. The SHA-256 sidecar file (§5.4) provides tamper detection.

**Modify and delete coverage.** OAuth3 tokens are immutable once issued. "Modification" manifests as scope reduction via step-up re-consent, which MUST generate a new sub-token and a `step_up_granted` or `step_up_denied` audit record. "Deletion" manifests as revocation, which MUST generate a `revoked` or `bulk_revoked` audit record. The original token record MUST NOT be deleted from the JSONL file.

---

### D.5 Access Control Requirements — §11.10(d) and §11.10(g) Mapping

#### D.5.1 §11.10(d) — Limiting Access to Authorized Individuals

The OAuth3 consent flow (Section 3) implements a mandatory human-in-the-loop authorization gate. The agent MUST NOT execute any action before:

1. Presenting the requested scope(s) to the human principal via the consent UI (§3.2)
2. Receiving an explicit `approved_scopes` response from the human (§3.3)
3. Obtaining a valid AgencyToken with the approved scopes (§1.2)
4. Passing all four validation gates (G1–G4) at the enforcement point (§1.4)

Implementations MUST NOT allow agents to self-approve consent requests. The `issuer` and `subject` fields MUST refer to different entities.

#### D.5.2 §11.10(g) — Authority Checks

The 4-gate validation sequence (G1–G4) in Section 1.4 constitutes the authority check mechanism required by §11.10(g):

| Gate | Check | Part 11 Purpose |
|------|-------|----------------|
| G1 | Token present and parseable | Record exists and is legible |
| G2 | Requested scope is in `scopes` array | Authority is scoped — agent may only do what was explicitly approved |
| G3 | `expires_at` > current UTC time | Authority is time-limited — expired authority cannot be exercised |
| G4 | Token ID not in revocation registry | Authority has not been withdrawn — revoked authority cannot be exercised |

Failure at any gate MUST result in an immediate, fail-closed rejection. The failed gate check MUST produce a `gate_failed` audit record specifying which gate failed and why.

---

### D.6 Recipe Inheritance of Part 11 Compliance

Any recipe that includes the OAuth3 integration block (specified in Appendix C §C.3) inherits full Part 11 compliance coverage through the following chain:

1. **Pre-execution.** The `oauth3-enforcer` skill enforces G1–G4 before the recipe's first step. No recipe action occurs without a valid, authorized, non-expired, non-revoked token. This satisfies §11.10(g).

2. **Attribution.** The recipe execution is attributed to `subject` (the human principal) via the token `subject` field. Every recipe action is traceable to the authorizing individual. This satisfies ALCOA+ Attributable.

3. **Audit continuity.** The recipe MUST write its `evidence_output` to the path specified in the `oauth3` integration block. The `oauth3_audit.jsonl` file covers the authorization lifecycle; the recipe's own evidence artifacts cover the action record. Together they form an unbroken audit trail from authorization grant to action completion to outcome. This satisfies §11.10(e).

4. **Contemporaneous recording.** The `oauth3-enforcer` timestamps the gate-pass event at the moment of enforcement, before any recipe step executes. The recipe MUST timestamp its own artifacts at action time. Neither timestamp may be retroactively set.

5. **Revocability.** If the human principal revokes the token mid-recipe (via `DELETE /oauth3/tokens/{token_id}`), any recipe step that re-validates the token after revocation MUST fail at G4 and halt execution. Implementations MUST check token validity at each step that requires authorization, not only at recipe start.

A recipe that does NOT include the `oauth3` integration block MUST NOT be submitted to the Stillwater Store for any skill that touches an external platform. Violation of this requirement constitutes a SCOPE_EXPANSION event under `prime-safety` and MUST be flagged by the `oauth3-enforcer` skill.

---

### D.7 Gap Summary and v1.0 Upgrade Requirements

The following gaps exist in v0.1.0 and MUST be addressed before an OAuth3 implementation may claim full Part 11 electronic signature equivalence under §11.50–§11.200:

| Gap ID | Description | Blocking Requirement | Target Version |
|--------|-------------|---------------------|----------------|
| GAP-D1 | `signature_stub` is a hash digest, not a bound electronic signature | Full §11.50–§11.200 equivalence requires ECDSA-P256 with identity binding | v1.0 |
| GAP-D2 | JWKS endpoint not yet specified in this spec | Signature verification key publication is required for §11.100(a) | v1.0 |
| GAP-D3 | No biometric or knowledge-based authentication (KBA) path defined | Part 11 §11.200(a)(1) permits two-component signatures; v1.0 SHOULD define the KBA path as an alternative to PKI for environments where certificate infrastructure is not available | v1.0 |
| GAP-D4 | `signature` field not in normative schema | §1.2 MUST be updated to replace `signature_stub` with `signature` carrying the ECDSA-P256 value | v1.0 |

Implementations that operate at rung ≥ 274177 and require FDA Part 11 compliance MUST track these gaps and MUST NOT deploy to regulated environments without resolving GAP-D1 and GAP-D2.

---

## Revision History

| Version | Date | Change |
|---------|------|--------|
| 0.1.0 | 2026-02-21 | Initial specification. Rung 641. Five sections complete. |
| 0.1.1 | 2026-02-23 | Security hardening: CSRF state REQUIRED, HTTPS normative, consent UI origin enforcement, RFC 8785 canonicalization, subject authentication binding, audit hash chain, clock skew tolerance, distributed revocation qualification. Schneier adversarial review applied. |
| 0.1.1+ | 2026-02-23 | Added Section 7: DPoP proof-of-possession (RFC 9449). New gate G5. |

---

*End of OAuth3 Specification v0.1.1*
