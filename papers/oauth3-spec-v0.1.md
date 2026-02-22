# OAuth3: Delegated Agency Authorization — Formal Specification

**Document ID:** oauth3-spec-v0.1
**Version:** 0.1.0
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

---

## Table of Contents

1. AgencyToken Schema
2. Scope Format and Registry
3. Consent Flow
4. Revocation
5. Evidence Bundle

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
      "description": "Cryptographic stub for token integrity. In v0.1 (pre-PKI): SHA-256 hex digest of the canonical JSON of all other fields (sorted keys, no whitespace). In v1.0: ECDSA-P256 signature over the same canonical form."
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
| `state` | OPTIONAL | CSRF protection nonce. SHOULD be included. |

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

Revocation is the mechanism by which a principal invalidates a previously issued AgencyToken. Revocation MUST take effect immediately and synchronously: any gate check (G4 in Section 1.4) MUST reflect revocation within 1 second of the DELETE call returning 200.

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
  "metadata": "object | null (implementation-specific fields)"
}
```

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

## Revision History

| Version | Date | Change |
|---------|------|--------|
| 0.1.0 | 2026-02-21 | Initial specification. Rung 641. Five sections complete. |

---

*End of OAuth3 Specification v0.1.0*
