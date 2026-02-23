# OAuth3 Key Management Specification

**Document ID:** oauth3-key-management-v0.1
**Version:** 0.1.0
**Status:** DRAFT — Rung 641 (Local Correctness)
**Authors:** Phuc Vinh Truong, Stillwater Project
**Framework:** Stillwater OS v1.4.0
**Date:** 2026-02-23
**Depends on:** oauth3-spec-v0.1 (normative base)
**Repository:** https://github.com/phuctruong/stillwater

---

## Abstract

This specification defines the key management requirements for OAuth3 token signing and verification. It is the companion document to oauth3-spec-v0.1, and provides the complete protocol for replacing the v0.1 `signature_stub` (SHA-256 digest) with full ECDSA-P256 cryptographic signatures in v1.0.

Schneier's adversarial review of OAuth3 (33 findings) identified key management as finding C-1 (CRITICAL): "Without key management, tokens are decorative." This specification resolves C-1 by defining normative requirements for issuer key generation, rotation, emergency revocation, DPoP agent key binding (RFC 9449), token signing and verification, and trust anchor bootstrap.

This specification covers:
1. Issuer key generation, publication, rotation, and emergency revocation
2. Agent key generation and DPoP proof-of-possession (RFC 9449)
3. Token signature upgrade from `signature_stub` to ECDSA-P256 (`signature`)
4. Trust anchor bootstrap for enforcement systems
5. Security considerations specific to key management
6. Stillwater integration requirements for key operations

**Lane classification:** This specification is Lane B (framework truth within the OAuth3 axiom system). Implementations that satisfy Section 4 (Token Signature) and produce verifiable ECDSA signatures constitute Lane A evidence.

---

## Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

**Fail-closed rule (hard):** Any system implementing this specification MUST refuse any operation if a required key management gate fails. Failing open (accepting a token with an unverifiable or missing signature) is a critical violation of this specification.

**Algorithm restriction (hard):** In v1.0, the only permitted signing algorithm is ECDSA with P-256 curve (algorithm identifier: `ES256`). Any implementation that accepts or produces tokens signed with any other algorithm is in violation of this specification.

---

## Normative References

The following documents are normative references for this specification:

- **oauth3-spec-v0.1** — OAuth3: Delegated Agency Authorization — Formal Specification (Phuc Vinh Truong, Stillwater Project, 2026)
- **RFC 2119** — Key words for use in RFCs to Indicate Requirement Levels (Bradner, 1997)
- **RFC 7517** — JSON Web Key (JWK) (Jones, 2015)
- **RFC 7518** — JSON Web Algorithms (JWA) (Jones, 2015)
- **RFC 7519** — JSON Web Token (JWT) (Jones et al., 2015)
- **RFC 7638** — JSON Web Key (JWK) Thumbprint (Jones & Sakimura, 2015)
- **RFC 8785** — JSON Canonicalization Scheme (JCS) (Rundgren et al., 2020)
- **RFC 9449** — OAuth 2.0 Demonstrating Proof of Possession (DPoP) (Fett et al., 2023)

---

## Table of Contents

1. Purpose and Scope
2. Issuer Key Management
3. Agent Key Management (DPoP)
4. Token Signature (v1.0 Upgrade)
5. Trust Anchor Bootstrap
6. Security Considerations
7. Appendix A: Stillwater Integration
8. Appendix B: Comparison to Existing Key Management Standards
9. Revision History

---

## Section 1: Purpose and Scope

### 1.1 Purpose

This specification defines the complete key management protocol for OAuth3 token signing and verification. It covers both the issuer keys used to sign AgencyTokens and the agent keys used to prove DPoP (Demonstrating Proof of Possession) in accordance with RFC 9449.

Without this specification, the `signature_stub` field in oauth3-spec-v0.1 is a SHA-256 hash digest, not a cryptographic signature. A hash digest detects accidental corruption but does NOT prevent a malicious party from generating a valid-looking token. This specification resolves that gap by defining the key management infrastructure that enables genuine ECDSA-P256 signatures in v1.0.

### 1.2 Scope

This specification normatively defines:

- **Issuer key management** — how consent servers generate, publish, rotate, and revoke the signing keys used to sign AgencyTokens
- **Agent key management** — how agent instances generate key pairs and bind them to AgencyTokens via DPoP (RFC 9449)
- **Token signature protocol** — how tokens are signed at issuance (Section 4.1) and verified at enforcement gates (Section 4.2)
- **Trust anchor bootstrap** — how a new enforcement gate discovers which issuers to trust

This specification does NOT define:

- The consent flow, scope registry, or revocation protocol (defined in oauth3-spec-v0.1)
- The evidence bundle format for application-level actions (defined in oauth3-spec-v0.1 Section 5)
- Implementation code for any specific language or platform (spec only)

### 1.3 Relationship to oauth3-spec-v0.1

This specification is a companion to oauth3-spec-v0.1. The base spec defines WHAT is authorized. This spec defines HOW that authorization is cryptographically bound and verified. All normative references to AgencyToken fields, validation gates (G1–G4), and audit records use the definitions from oauth3-spec-v0.1.

This specification adds one new validation gate:

| Gate | Check | Failure Action |
|------|-------|----------------|
| G5: DPoP | DPoP proof valid AND thumbprint matches token's `cnf.jkt` | BLOCKED: OAUTH3_DPOP_BINDING_MISMATCH |

Gate G5 MUST be checked after gates G1–G4 pass. All five gates MUST pass before any agent action is authorized.

---

## Section 2: Issuer Key Management

### 2.1 Key Generation Requirements

Issuer keys are the signing keys held by the consent server (the entity that issues AgencyTokens). These requirements are normative for all OAuth3 v1.0 issuers.

**Algorithm.** The signing algorithm MUST be ECDSA with P-256 curve, designated by the JWA identifier `ES256` (RFC 7518 §3.4). No alternative algorithms are permitted in v1.0. P-384 (`ES384`) MAY be supported in future versions but is not a required or permitted alternative in v1.0.

**Randomness.** Key generation MUST use a cryptographically secure random number generator (CSPRNG). Platform-provided entropy sources (e.g., `/dev/urandom` on Linux, `BCryptGenRandom` on Windows, `SecRandomCopyBytes` on macOS/iOS) MUST be used. Application-level pseudorandom number generators MUST NOT be used for key generation.

**Hardware Security Module.** Private keys SHOULD be stored in a Hardware Security Module (HSM) or a cloud-hosted Key Management Service (KMS). Acceptable KMS options include:
- AWS Key Management Service (AWS KMS)
- Google Cloud Key Management Service (Cloud KMS)
- Azure Key Vault
- HashiCorp Vault with auto-unseal

Private keys MUST NEVER appear in:
- Application logs
- System logs
- Token payloads
- API responses
- Audit records (`oauth3_audit.jsonl`)
- Environment variables persisted to disk

**Minimum Key Strength.** P-256 provides 128-bit security. This is the minimum permitted in v1.0. Key sizes below 256 bits MUST NOT be used.

### 2.2 JWK Format

Issuer public keys MUST be published in JSON Web Key (JWK) format as defined in RFC 7517. Each key in the published JWK Set MUST include the following fields:

| Field | Requirement | Value |
|-------|-------------|-------|
| `kty` | REQUIRED | `"EC"` |
| `crv` | REQUIRED | `"P-256"` |
| `x` | REQUIRED | Base64url-encoded x-coordinate of the public key |
| `y` | REQUIRED | Base64url-encoded y-coordinate of the public key |
| `kid` | REQUIRED | Stable, unique key identifier (see §2.2.1) |
| `use` | REQUIRED | `"sig"` |
| `alg` | REQUIRED | `"ES256"` |

Private key fields (`d`) MUST NEVER be included in published JWKs.

**Example issuer public key (JWK):**

```json
{
  "kty": "EC",
  "crv": "P-256",
  "x": "f83OJ3D2xF1Bg8vub9tLe1gHMzV76e8Tus9uPHvRVEU",
  "y": "x_FEzRu9m36HLN_tue659LNpXW6pCyStikYjKIWI5a0",
  "kid": "issuer-key-2026-02-23",
  "use": "sig",
  "alg": "ES256"
}
```

#### 2.2.1 Key ID (`kid`) Requirements

The `kid` field MUST be a stable, unique identifier for the key. Two acceptable formats are:

**Format A: UUID v4.** A randomly generated UUID (e.g., `"550e8400-e29b-41d4-a716-446655440000"`). Simple to generate; does not convey key material.

**Format B: JWK Thumbprint (RECOMMENDED).** The SHA-256 thumbprint of the JWK computed per RFC 7638. This format is preferred because the `kid` can be independently verified from the key material itself.

The JWK thumbprint computation per RFC 7638 for an EC P-256 key is:
1. Construct the required member JSON object: `{"crv":"P-256","kty":"EC","x":"<x-value>","y":"<y-value>"}`
   (members MUST be in lexicographic order; no extra whitespace)
2. Compute the SHA-256 hash of the UTF-8 encoding of that JSON object
3. Base64url-encode the result

Implementations MUST NOT reuse a `kid` value for different key material. Once a `kid` is assigned to a key pair, it MUST NOT be reassigned to any other key pair.

#### 2.2.2 JWK Set Format

The JWK Set (JWKS) MUST be formatted as:

```json
{
  "keys": [
    {
      "kty": "EC",
      "crv": "P-256",
      "x": "f83OJ3D2xF1Bg8vub9tLe1gHMzV76e8Tus9uPHvRVEU",
      "y": "x_FEzRu9m36HLN_tue659LNpXW6pCyStikYjKIWI5a0",
      "kid": "issuer-key-2026-02-23",
      "use": "sig",
      "alg": "ES256"
    }
  ]
}
```

Multiple keys MAY appear in the `keys` array. This is the normal state during key rotation (see §2.4). Enforcement systems MUST accept tokens signed with any key present in the JWKS at the time of verification.

### 2.3 Key Publication Endpoint

**Discovery URI.** Issuers MUST publish their JWK Set at a well-known URI derived from the issuer's base URI:

```
{issuer}/.well-known/oauth3-keys.json
```

For example, if `issuer` is `https://www.solaceagi.com`, the JWKS endpoint is:

```
https://www.solaceagi.com/.well-known/oauth3-keys.json
```

**Transport.** The endpoint MUST be served over HTTPS (TLS 1.2 minimum, TLS 1.3 RECOMMENDED). The endpoint MUST NOT be served over unencrypted HTTP. Any HTTP request to the JWKS endpoint MUST be rejected with a redirect to the HTTPS equivalent or a 400 error.

**Content-Type.** The endpoint MUST return `Content-Type: application/json`.

**Cache-Control.** The endpoint MUST include a `Cache-Control` response header. The RECOMMENDED value is:

```
Cache-Control: public, max-age=3600
```

Issuers SHOULD NOT set `max-age` above 86400 (24 hours), as long cache lifetimes delay rotation propagation. Issuers MUST NOT set `no-cache` or `no-store`, as enforcement systems depend on caching for performance.

**CORS.** Issuers SHOULD include `Access-Control-Allow-Origin: *` to permit browser-based verification.

### 2.4 Key Rotation

Issuers SHOULD rotate their signing keys at least every 90 days. The following zero-downtime rotation procedure MUST be followed.

**Rotation Procedure:**

1. Generate a new key pair. Assign a new `kid` to the new key.
2. Publish the new public key to the JWK Set, alongside the currently active key. Both keys MUST appear in the `keys` array.
3. Wait a grace period before switching the active signing key. The RECOMMENDED grace period is 24 hours. This allows enforcement systems that have cached the old JWKS to refresh and discover the new key before it begins signing.
4. Switch the signing process to use the new key. All tokens issued after this point MUST use the new key. The `kid` of the active signing key MUST be embedded in the token's JWS signature header.
5. Continue publishing both the old and the new public keys until all tokens signed with the old key have expired. Given the maximum AgencyToken TTL of 86400 seconds (24 hours) defined in oauth3-spec-v0.1 §3.2, the old key MUST remain in the JWKS for at least 24 hours after the signing switch (Step 4), plus the grace period from Step 3. The minimum retention period for the old key is therefore: `24h (max TTL) + 24h (grace period) = 48 hours`.
6. After the retention period, remove the old public key from the JWKS.

**Rotation State Example:**

During the grace period (Steps 2–3), the JWKS contains two keys:

```json
{
  "keys": [
    {
      "kty": "EC",
      "crv": "P-256",
      "x": "f83OJ3D2xF1Bg8vub9tLe1gHMzV76e8Tus9uPHvRVEU",
      "y": "x_FEzRu9m36HLN_tue659LNpXW6pCyStikYjKIWI5a0",
      "kid": "issuer-key-2026-02-23",
      "use": "sig",
      "alg": "ES256"
    },
    {
      "kty": "EC",
      "crv": "P-256",
      "x": "0RfR98k8yuC1okAoT0cXBWr1TJzMmDPZ-IYh6oJHVTg",
      "y": "gmFNTBMOetxE3LH5R9eKfm7bGVMQOe-eWCOhvdK3bHA",
      "kid": "issuer-key-2026-05-24",
      "use": "sig",
      "alg": "ES256"
    }
  ]
}
```

After the retention period (Step 6), only the new key remains:

```json
{
  "keys": [
    {
      "kty": "EC",
      "crv": "P-256",
      "x": "0RfR98k8yuC1okAoT0cXBWr1TJzMmDPZ-IYh6oJHVTg",
      "y": "gmFNTBMOetxE3LH5R9eKfm7bGVMQOe-eWCOhvdK3bHA",
      "kid": "issuer-key-2026-05-24",
      "use": "sig",
      "alg": "ES256"
    }
  ]
}
```

**Key rotation events MUST be logged** to `oauth3_audit.jsonl` with event type `KEY_ROTATION_STARTED`, `KEY_ROTATION_SWITCHED`, and `KEY_ROTATION_COMPLETED`. See Appendix A for audit record details.

### 2.5 Emergency Key Revocation

If an issuer signing key is suspected or confirmed to be compromised, the issuer MUST execute the following emergency procedure immediately:

**Step 1: Remove compromised key.** Immediately remove the compromised key from the JWKS by deleting its entry from the `keys` array and redeploying the JWKS endpoint. This MUST take effect within 60 seconds of confirming the compromise. Any token signed with the compromised key that is presented after this point MUST fail signature verification (G5 gate failure: `OAUTH3_SIGNATURE_INVALID`).

**Step 2: Generate replacement key.** Generate a new key pair following the requirements of Section 2.1. The new key MUST be published in the JWKS before Step 3.

**Step 3: Bulk-revoke affected tokens.** The issuer MUST revoke ALL tokens that were signed with the compromised key. This is accomplished via the bulk revocation endpoint defined in oauth3-spec-v0.1 §4.3. The revocation call MUST use a reason field that references the key compromise event.

**Step 4: Publish key revocation record.** The issuer MUST publish a key revocation record to:

```
{issuer}/.well-known/oauth3-key-revocations.json
```

The key revocation record format is:

```json
{
  "revocations": [
    {
      "kid": "issuer-key-2026-02-23",
      "revoked_at": "2026-02-23T14:30:00Z",
      "reason": "PRIVATE_KEY_COMPROMISE",
      "replacement_kid": "issuer-key-2026-02-23-emergency",
      "affected_token_range": {
        "issued_after": "2026-01-01T00:00:00Z",
        "issued_before": "2026-02-23T14:30:00Z"
      }
    }
  ]
}
```

Enforcement systems SHOULD poll `/.well-known/oauth3-key-revocations.json` on JWKS cache miss or at application startup.

**Step 5: Log the incident.** The issuer MUST log the key compromise event to `oauth3_audit.jsonl` with event type `KEY_COMPROMISE_DETECTED`. The audit record MUST include the `kid` of the compromised key, the timestamp, and the number of tokens bulk-revoked.

---

## Section 3: Agent Key Management (DPoP)

### 3.1 Overview

OAuth3 v1.0 replaces bearer tokens with DPoP-bound tokens in accordance with RFC 9449 (OAuth 2.0 Demonstrating Proof of Possession). Under the bearer token model of v0.1, a stolen AgencyToken can be used by any party that holds it. Under DPoP, the token is cryptographically bound to the agent's key pair. A stolen token is useless without the agent's private key.

The DPoP mechanism works as follows:

1. The agent generates a key pair at first startup (see §3.2).
2. When requesting a token, the agent presents its public key to the consent server. The consent server embeds a thumbprint of the agent's public key in the issued token's `cnf.jkt` claim.
3. Each API request the agent makes includes a DPoP proof: a short-lived, single-use JWT signed with the agent's private key (see §3.3).
4. The enforcement gate verifies the DPoP proof, computes the public key thumbprint, and confirms it matches the `cnf.jkt` in the token (see §3.4, Gate G5).

### 3.2 Agent Key Generation

**Algorithm.** Agent keys MUST use ECDSA P-256 (`ES256`), the same algorithm as issuer keys. This ensures a uniform algorithm surface and simplifies enforcement gate logic.

**Generation time.** The agent MUST generate its key pair at first startup. The same key pair SHOULD be reused across sessions for the same agent instance. Key pairs MUST NOT be generated per-request.

**Storage.** The agent private key MUST be stored encrypted at rest. The minimum acceptable encryption is AES-256-GCM. On platforms with OS-level secure storage (e.g., macOS Keychain, Linux Kernel Keyring, Android Keystore, iOS Secure Enclave), agents SHOULD use the platform's secure storage facility.

**Public key format.** The agent's public key, for use in DPoP proof headers and token requests, MUST be formatted as a JWK with the following fields:

```json
{
  "kty": "EC",
  "crv": "P-256",
  "x": "base64url-encoded-x-coordinate",
  "y": "base64url-encoded-y-coordinate"
}
```

The agent public JWK MUST NOT include `kid`, `use`, or `alg` when embedded in a DPoP proof header. These fields are added by enforcement systems as needed.

### 3.3 DPoP Proof Structure

Each agent request to an OAuth3-protected endpoint MUST include a DPoP proof in the `DPoP` HTTP request header. The DPoP proof is a JWT constructed as follows.

**DPoP proof header:**

```json
{
  "typ": "dpop+jwt",
  "alg": "ES256",
  "jwk": {
    "kty": "EC",
    "crv": "P-256",
    "x": "f83OJ3D2xF1Bg8vub9tLe1gHMzV76e8Tus9uPHvRVEU",
    "y": "x_FEzRu9m36HLN_tue659LNpXW6pCyStikYjKIWI5a0"
  }
}
```

The `typ` field MUST be exactly `"dpop+jwt"`. The `alg` field MUST be `"ES256"`. The `jwk` field MUST contain the agent's public key in JWK format (without `kid`, `use`, or `alg` fields).

**DPoP proof payload:**

```json
{
  "jti": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "htm": "POST",
  "htu": "https://api.example.com/oauth3/action",
  "iat": 1709000000,
  "ath": "fUHyO2r2Z3DZ53EsNrWBb0xWXoaNy59IiKCAqksmQEo"
}
```

| Field | Requirement | Description |
|-------|-------------|-------------|
| `jti` | REQUIRED | UUID v4 unique proof identifier. MUST be single-use (see nonce enforcement in §6.2). |
| `htm` | REQUIRED | HTTP method of the request (e.g., `"POST"`, `"DELETE"`). MUST match the actual request method. |
| `htu` | REQUIRED | HTTP target URI of the request. MUST match the actual request URI, without query parameters or fragment. |
| `iat` | REQUIRED | Unix timestamp (seconds since epoch) when the DPoP proof was created. MUST be within the last 60 seconds at the time of verification (see §6.2 for replay window). |
| `ath` | REQUIRED | Base64url-encoded SHA-256 hash of the ASCII encoding of the access token (the AgencyToken's JWS compact serialization). Binds this proof to the specific token presented. |

The DPoP proof MUST be signed with the agent's private key using ES256. The resulting JWT is placed in the HTTP `DPoP` header of the request.

**DPoP proof lifetime.** The maximum lifetime of a DPoP proof is 60 seconds (`iat` + 60 > current UTC time). Proofs older than 60 seconds MUST be rejected. A 30-second clock skew tolerance MAY be applied (consistent with the token TTL clock skew tolerance defined in oauth3-spec-v0.1 §1.4), but in no case may a proof older than 90 seconds from issuance be accepted.

### 3.4 Token Binding

**At token issuance.** When an agent requests a token (via the consent flow in oauth3-spec-v0.1 §3), the agent MUST include its public key in the consent request. The consent server MUST compute the JWK thumbprint of the agent's public key per RFC 7638 and embed it in the issued token's `cnf` claim:

```json
"cnf": {
  "jkt": "0ZcOCORZNYy-DWpqq30jZyJGHTN0d2HglBV3uiguA4I"
}
```

The `cnf.jkt` field is the base64url-encoded SHA-256 JWK thumbprint. This field MUST be included in all v1.0 AgencyTokens that are presented with DPoP proofs. Tokens without `cnf.jkt` MUST NOT be accepted when DPoP is in use.

**At validation (Gate G5).** The enforcement gate MUST perform the following sequence when validating a DPoP-bound token:

1. Extract the `DPoP` header from the request. If the `DPoP` header is absent and the token contains `cnf.jkt`, BLOCKED: `OAUTH3_DPOP_PROOF_MISSING`.
2. Parse the DPoP proof JWT. Verify the header `typ` is `"dpop+jwt"`.
3. Extract the public key from the DPoP proof header's `jwk` field.
4. Verify the DPoP proof JWT signature using the extracted public key (ES256).
5. Verify the DPoP proof `iat` is within the allowed replay window (see §6.2).
6. Verify the DPoP proof `jti` has not been seen before (nonce enforcement). If `jti` was already used, BLOCKED: `OAUTH3_DPOP_REPLAY_DETECTED`.
7. Verify the DPoP proof `htm` matches the request HTTP method.
8. Verify the DPoP proof `htu` matches the request URI.
9. Verify the DPoP proof `ath` matches the SHA-256 hash of the presented token.
10. Compute the JWK thumbprint of the public key from the DPoP proof header's `jwk` field.
11. Compare the computed thumbprint to the `cnf.jkt` field in the token. If they do not match, BLOCKED: `OAUTH3_DPOP_BINDING_MISMATCH`.
12. If all checks pass: Gate G5 PASS.

All G5 gate failures MUST be logged to `oauth3_audit.jsonl` with `gate_failed: "G5"` and the specific error code.

### 3.5 Mapping to OAuth3 Fields

The DPoP integration produces the following field-level changes to the AgencyToken schema defined in oauth3-spec-v0.1 §1.2:

| v0.1 Field | v1.0 Replacement | Change |
|------------|------------------|--------|
| `agent_id` (string) | `cnf.jkt` (JWK thumbprint) | Replaces opaque string agent identifier with cryptographic binding. `agent_id` MAY still be included as a human-readable annotation but MUST NOT be used as the binding identifier. |
| `signature_stub` (SHA-256 hex) | `signature` (JWS compact serialization) | Replaces integrity hash with ECDSA-P256 signature from the issuer's signing key. |

The `cnf` claim is added as a new top-level field in the AgencyToken JSON object:

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "version": "1.0.0",
  "issued_at": "2026-02-23T10:00:00Z",
  "expires_at": "2026-02-23T11:00:00Z",
  "scopes": ["linkedin.post.text", "linkedin.read.feed"],
  "issuer": "https://www.solaceagi.com",
  "subject": "user:phuc@example.com",
  "cnf": {
    "jkt": "0ZcOCORZNYy-DWpqq30jZyJGHTN0d2HglBV3uiguA4I"
  },
  "platforms": ["linkedin.com"],
  "signature": "eyJhbGciOiJFUzI1NiIsImtpZCI6Imlzc3Vlci1rZXktMjAyNi0wMi0yMyJ9.eyJpZCI6ImExYjJjM2Q0Li4uIn0.signature-value"
}
```

---

## Section 4: Token Signature (v1.0 Upgrade)

### 4.1 Signing Process

The following process MUST be used by the consent server to sign every AgencyToken in v1.0:

**Step 1: Canonical JSON serialization.** Compute the canonical JSON of the token body using RFC 8785 (JSON Canonicalization Scheme, JCS). The `signature` field MUST be excluded from the canonical form. All other fields MUST be included. The canonical form MUST be a UTF-8 encoded JSON object with members sorted in lexicographic order by key name and no insignificant whitespace.

**Step 2: Construct the JWS payload.** The canonical JSON bytes are the JWS payload.

**Step 3: Construct the JWS header.** The protected header MUST be:

```json
{
  "alg": "ES256",
  "kid": "issuer-key-2026-02-23"
}
```

The `kid` MUST identify the active signing key used in this operation. The `alg` MUST be `"ES256"`.

**Step 4: Sign.** Sign the JWS (header + payload) using the issuer's private key with the ES256 algorithm. Produce the JWS Compact Serialization:

```
BASE64URL(UTF8(JWS Protected Header)) || '.' ||
BASE64URL(JWS Payload) ||  '.' ||
BASE64URL(JWS Signature)
```

**Step 5: Set the `signature` field.** Place the JWS Compact Serialization in the token's `signature` field. The token body in transit (stored, transmitted) MUST include this field.

**Signed token example (abbreviated):**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "version": "1.0.0",
  "issued_at": "2026-02-23T10:00:00Z",
  "expires_at": "2026-02-23T11:00:00Z",
  "scopes": ["linkedin.read.feed"],
  "issuer": "https://www.solaceagi.com",
  "subject": "user:phuc@example.com",
  "cnf": { "jkt": "0ZcOCORZNYy-DWpqq30jZyJGHTN0d2HglBV3uiguA4I" },
  "platforms": ["linkedin.com"],
  "signature": "eyJhbGciOiJFUzI1NiIsImtpZCI6Imlzc3Vlci1rZXktMjAyNi0wMi0yMyJ9.eyJpZCI6ImExYjJjM2Q0LWU1ZjYtNzg5MC1hYmNkLWVmMTIzNDU2Nzg5MCIsInZlcnNpb24iOiIxLjAuMCJ9.MEUCIQD_example_signature_value"
}
```

### 4.2 Verification Process

The following process MUST be used by enforcement gates to verify the signature of a v1.0 AgencyToken:

**Step 1: Check `version` field.** Extract the `version` field. If the version is `"1.0.x"`, proceed with ECDSA verification (this section). If the version is `"0.1.x"`, the token MUST be rejected (see §4.3 for version compatibility rules).

**Step 2: Extract the signature.** Extract the `signature` field from the token. Parse it as a JWS Compact Serialization. Extract the protected header, payload, and signature components.

**Step 3: Extract `kid` from the JWS header.** Parse the protected header. Extract the `kid` field. This identifies which issuer key was used to sign the token.

**Step 4: Fetch the issuer's JWKS.** Extract the `issuer` field from the token. Fetch the issuer's JWK Set from:

```
{issuer}/.well-known/oauth3-keys.json
```

Enforcement systems MUST cache the JWKS with the `Cache-Control` expiry returned by the issuer (see §2.3). On cache miss, enforcement systems MUST fetch a fresh copy.

**Step 5: Locate the signing key.** In the JWKS, find the key whose `kid` matches the `kid` from the JWS header (Step 3). If no matching `kid` is found, BLOCKED: `OAUTH3_SIGNING_KEY_NOT_FOUND`. The enforcement system MUST NOT attempt signature verification without a matching key.

**Step 6: Reconstruct the canonical JSON.** Reconstruct the canonical JSON of the token per RFC 8785, excluding the `signature` field. This MUST produce byte-for-byte identical output to Step 1 of the signing process.

**Step 7: Verify the ES256 signature.** Verify the JWS signature using the issuer's public key (from Step 5) and the ES256 algorithm. If verification fails, BLOCKED: `OAUTH3_SIGNATURE_INVALID`. If verification passes, continue to DPoP gate (G5).

All signature verification failures MUST be logged to `oauth3_audit.jsonl` with `gate_failed: "G5"` (or a new `gate_failed: "G_SIG"` label — implementation choice, but MUST be consistent and documented).

### 4.3 Version Compatibility

**v1.0 enforcement systems MUST reject v0.1 tokens.** The `signature_stub` field is not a cryptographic signature. A v1.0 enforcement gate configured for ECDSA verification MUST NOT fall back to SHA-256 hash verification for tokens carrying `signature_stub`. The rejection error code is `OAUTH3_VERSION_DOWNGRADE_REJECTED`.

**v1.0 tokens MUST use `version: "1.0.0"` (or `"1.0.x"` for minor revisions).** The consent server MUST set the `version` field to a `1.0.x` semver string when issuing v1.0 tokens.

**No downgrade is permitted.** A system configured to enforce v1.0 MUST NOT accept v0.1 tokens, even if they are otherwise well-formed and not expired. This is a hard rule. Systems that support both v0.1 and v1.0 MUST route them through separate enforcement paths and MUST document which path is active.

**Migration procedure.** During the upgrade window from v0.1 to v1.0:
1. The consent server begins issuing v1.0 tokens with `signature` (ECDSA) in place of `signature_stub` (SHA-256).
2. Enforcement gates are updated to process v1.0 tokens.
3. All active v0.1 tokens MUST be allowed to expire naturally (maximum 24 hours per the TTL limit in oauth3-spec-v0.1 §3.2) or MUST be bulk-revoked.
4. After the migration window, enforcement gates switch to v1.0-only mode.

---

## Section 5: Trust Anchor Bootstrap

### 5.1 The Problem

A new enforcement gate must answer: "Which issuers can I trust?" This is the "first key" problem common to all public-key infrastructure (PKI) systems. Unlike traditional X.509 PKI, OAuth3 does not rely on a hierarchy of Certificate Authorities. Instead, trust is anchored by direct configuration or by discovery through a known registry.

### 5.2 Bootstrap Options

Three bootstrap options are defined. Implementations MUST choose exactly one for their deployment context. The chosen option MUST be documented in the deployment configuration.

**Option A: Pre-configured issuer allowlist (RECOMMENDED for single-org deployments).**

The enforcement gate is initialized with a static list of trusted issuer URIs and their corresponding JWKS endpoints. Any token from an issuer not on this list MUST be rejected: BLOCKED: `OAUTH3_ISSUER_NOT_TRUSTED`.

Configuration example:

```json
{
  "trusted_issuers": [
    {
      "issuer": "https://www.solaceagi.com",
      "jwks_uri": "https://www.solaceagi.com/.well-known/oauth3-keys.json"
    },
    {
      "issuer": "urn:stillwater:self-issued",
      "jwks_uri": "file:///etc/oauth3/self-issued-keys.json"
    }
  ]
}
```

**Option B: DNS-based discovery.**

The issuer domain publishes a DNS TXT record that points to the JWKS URI:

```
_oauth3-keys.solaceagi.com. IN TXT "v=oauth3km1 jwks_uri=https://www.solaceagi.com/.well-known/oauth3-keys.json"
```

The enforcement gate performs a DNS TXT lookup on `_oauth3-keys.{issuer_domain}` to discover the JWKS URI. The TXT record format is:
- `v=oauth3km1` — version identifier (REQUIRED)
- `jwks_uri=<URI>` — the JWKS endpoint URI (REQUIRED)

DNS-based discovery MUST be used only over DNSSEC-validated resolvers. Without DNSSEC, DNS-based discovery is vulnerable to DNS spoofing and MUST NOT be considered a security boundary.

**Option C: Stillwater Store registry.**

Trusted issuers register their JWKS URIs in the Stillwater Store as part of their OAuth3 issuer certification. The enforcement gate queries the Stillwater Store registry API to discover issuer JWKS URIs.

```
GET https://store.stillwater.dev/oauth3/issuers/{issuer_domain}
```

Response:

```json
{
  "issuer": "https://www.solaceagi.com",
  "jwks_uri": "https://www.solaceagi.com/.well-known/oauth3-keys.json",
  "registered_at": "2026-02-23T00:00:00Z",
  "rung": 65537
}
```

Option C SHOULD be used in multi-tenant or open ecosystem deployments where issuers are not known in advance.

### 5.3 Issuer Verification on First Contact

When an enforcement gate encounters an issuer it has not previously seen, it MUST execute the following verification flow before caching the issuer's JWKS:

**Step 1: Resolve the JWKS URI.** Obtain the JWKS URI via the configured bootstrap option (A, B, or C).

**Step 2: Fetch the JWK Set.** Make an HTTPS request to the JWKS URI. Verify the TLS certificate chain for the issuer domain. If the TLS certificate cannot be verified, BLOCKED: `OAUTH3_ISSUER_TLS_UNVERIFIABLE`. Certificate pinning SHOULD be implemented for high-security deployments (see §6.3).

**Step 3: Parse and validate the JWKS.** Parse the response as a JWK Set. Validate that all keys conform to §2.2 requirements. Reject any JWKS that contains keys with `alg` values other than `ES256`.

**Step 4: Cache the JWKS.** Cache the JWKS keyed by issuer URI, with expiry per the `Cache-Control` header. Cache the mapping `kid → public key` for efficient signature verification.

**Step 5: Optionally check the Stillwater Store.** Regardless of the bootstrap option, enforcement gates MAY additionally query the Stillwater Store registry to confirm the issuer's registration status. This is OPTIONAL for Option A deployments but RECOMMENDED for Option C deployments.

---

## Section 6: Security Considerations

### 6.1 Private Key Compromise

The consequences of a signing key compromise differ by key type:

**Issuer key compromise.** If an issuer signing key is compromised, an attacker can mint arbitrary AgencyTokens that appear valid to enforcement gates. The blast radius is all tokens signed with that key across all subjects. The emergency procedure in §2.5 MUST be executed immediately. The time between compromise detection and removal of the compromised key from the JWKS is the critical window; during this window, forged tokens can pass signature verification. Implementations SHOULD monitor for anomalous token usage patterns (unusual issuance rates, unusual subject identifiers) as a secondary detection mechanism.

**Agent key compromise.** If an agent's private key is compromised, an attacker can forge DPoP proofs for that agent's bound tokens. The blast radius is limited to that agent's active tokens. The agent MUST generate a new key pair and re-request all tokens. The old tokens (bound to the compromised key's `cnf.jkt`) MUST be revoked.

### 6.2 DPoP Replay Window and Nonce Enforcement

DPoP proofs are single-use and short-lived. Enforcement of both properties is required:

**Replay window.** The maximum age of a DPoP proof at verification time is 60 seconds (from the `iat` claim). A 30-second clock skew tolerance MAY be applied, yielding an effective maximum age of 90 seconds. Proofs older than 90 seconds MUST be rejected: BLOCKED: `OAUTH3_DPOP_PROOF_EXPIRED`.

**Nonce enforcement.** The `jti` claim of each DPoP proof MUST be stored by the enforcement gate for the duration of the replay window (minimum 90 seconds). Any DPoP proof whose `jti` was seen before MUST be rejected: BLOCKED: `OAUTH3_DPOP_REPLAY_DETECTED`. Storage requirements: a fixed-size cache or ring buffer with TTL eviction is sufficient. The cache MUST survive within a request processing cycle; it MAY be in-memory (process-local) for single-node deployments. For multi-node deployments, a shared cache (e.g., Redis) MUST be used.

### 6.3 JWK Set Cache Poisoning

An attacker who can influence the JWKS fetched by an enforcement gate can substitute a malicious public key, enabling the attacker to sign tokens that pass verification. Mitigations:

**HTTPS.** All JWKS fetches MUST use HTTPS. TLS provides transport integrity.

**TLS certificate verification.** The enforcement gate MUST verify the full TLS certificate chain for the issuer domain. Certificate verification MUST NOT be disabled, even in development environments.

**Certificate pinning (RECOMMENDED for high-security deployments).** For issuers that have stable, long-lived TLS certificates (e.g., a production consent server), enforcement gates SHOULD pin the issuer's TLS certificate or its public key. Certificate rotation must then be coordinated between the issuer and enforcement systems.

**JWKS integrity.** Enforcement gates SHOULD record the SHA-256 digest of the JWKS at the time of caching. On cache refresh, if the new JWKS digest differs from the cached digest and the `Cache-Control` expiry has not yet passed, the enforcement gate SHOULD log a `JWKS_UNEXPECTED_CHANGE` audit event and may choose to reject the new JWKS pending manual review.

### 6.4 Algorithm Confusion Attacks

An algorithm confusion attack occurs when an attacker causes a verifier to use a different algorithm than was intended, enabling signature forgery. In OAuth3 v1.0, this attack surface is eliminated by the algorithm restriction (Section 1, normative language): only `ES256` is permitted.

Enforcement gates MUST:
- Reject any JWS with an `alg` value other than `ES256`: BLOCKED: `OAUTH3_ALGORITHM_REJECTED`.
- Reject any JWK with an `alg` value other than `ES256`.
- Never infer the algorithm from the token or key material without a normative check.
- Never accept `alg: "none"` (unsigned tokens).

The `alg` field in both the JWS header and the JWK MUST be present and MUST equal `"ES256"`. Absence of the `alg` field is treated as a rejection condition.

### 6.5 Clock Skew for DPoP `iat`

DPoP proof verification depends on the `iat` claim being within the replay window. If the agent clock is significantly skewed from the enforcement gate clock, valid proofs may be rejected (false negatives) or expired proofs may be accepted (false positives).

**Maximum permitted clock skew:** 30 seconds, consistent with the token TTL clock skew tolerance in oauth3-spec-v0.1 §1.4.

**Clock synchronization.** Both the issuing consent server and all enforcement gates MUST synchronize their system clocks via NTP. A stratum-2 or better NTP source is RECOMMENDED for production deployments.

**Effective replay window with clock skew:** `60 seconds + 30 seconds = 90 seconds maximum age at verification time.`

---

## Appendix A: Stillwater Integration

### A.1 Rung Requirements for Key Management Operations

Key management operations are security-critical and MUST meet the following rung requirements:

| Operation | Minimum Rung | Rationale |
|-----------|-------------|-----------|
| Key pair generation (agent) | 641 | Local operation; correctness sufficient |
| Token signature implementation (issuer) | 65537 | Security-critical; production gate required |
| JWKS endpoint deployment | 65537 | Production/security gate |
| Key rotation procedure | 65537 | Production/security gate |
| Emergency key revocation | 65537 | Security-critical; production gate required |
| Trust anchor configuration | 274177 | Irreversible configuration; persistence required |
| Multi-node nonce enforcement | 274177 | Distributed state; persistence required |

No key management operation at rung 65537 or above MAY be performed without a passing evidence bundle.

### A.2 Key Operation Audit Events

Key management operations MUST be logged to `oauth3_audit.jsonl` with the following event types. These events extend the event registry defined in oauth3-spec-v0.1 §5.3:

| Event | When | Required Fields |
|-------|------|-----------------|
| `KEY_GENERATED` | After issuer key pair generation | `kid`, `alg`, `crv` |
| `KEY_PUBLISHED` | After JWKS endpoint updated | `kid`, `jwks_uri` |
| `KEY_ROTATION_STARTED` | When new key added to JWKS alongside old key | `new_kid`, `retiring_kid`, `grace_period_ends_at` |
| `KEY_ROTATION_SWITCHED` | When active signing switches to new key | `new_kid`, `retiring_kid` |
| `KEY_ROTATION_COMPLETED` | When old key removed from JWKS | `retired_kid`, `active_kid` |
| `KEY_COMPROMISE_DETECTED` | When issuer key is suspected compromised | `kid`, `tokens_bulk_revoked` |
| `JWKS_UNEXPECTED_CHANGE` | When JWKS digest changes before cache expiry | `kid`, `old_digest`, `new_digest` |
| `DPOP_PROOF_VERIFIED` | After Gate G5 PASS | `jti`, `cnf_jkt` |
| `DPOP_REPLAY_DETECTED` | When `jti` is seen twice | `jti`, `original_iat` |

All key operation audit records MUST include the `previous_hash` chain field as defined in oauth3-spec-v0.1 §5.2.

### A.3 Evidence Bundle for Key Rotation

A key rotation event at rung 65537 MUST produce the following evidence bundle:

```
artifacts/oauth3/key-rotation/
  rotation_plan.json          — planned timing, key IDs, grace period
  rotation_started.json       — audit record: KEY_ROTATION_STARTED
  rotation_switched.json      — audit record: KEY_ROTATION_SWITCHED
  rotation_completed.json     — audit record: KEY_ROTATION_COMPLETED
  verification_report.json    — evidence that new key passes signature verification
  rotation_plan.json.sha256   — integrity hash
```

This evidence bundle constitutes Lane A evidence for the key rotation rung gate. The absence of any required artifact is a gate failure.

---

## Appendix B: Comparison to Existing Key Management Standards

### B.1 Comparison to OIDC Discovery (RFC 8414)

OpenID Connect (OIDC) defines a discovery mechanism (RFC 8414) that publishes provider metadata at `{issuer}/.well-known/openid-configuration`, including a `jwks_uri` pointing to the provider's JWK Set. This is structurally similar to OAuth3's JWKS endpoint at `{issuer}/.well-known/oauth3-keys.json`.

| Property | OIDC / RFC 8414 | OAuth3 Key Management |
|----------|-----------------|----------------------|
| Discovery URI | `/.well-known/openid-configuration` (metadata) | `/.well-known/oauth3-keys.json` (keys directly) |
| Key format | JWK Set (RFC 7517) | JWK Set (RFC 7517) — same |
| Algorithm | RS256 common, ES256 RECOMMENDED | ES256 REQUIRED (no alternatives) |
| Rotation procedure | Not normatively specified | Normatively specified (§2.4) |
| Emergency revocation | Not specified | Normatively specified (§2.5) |
| Key revocation record | Not defined | `/.well-known/oauth3-key-revocations.json` |
| DPoP binding | Supported per RFC 9449 | Required in v1.0 |

**Key difference:** OIDC discovery publishes a metadata document that includes the JWKS URI as one field among many (token endpoint, authorization endpoint, etc.). OAuth3 publishes the JWK Set directly at the well-known URI, simplifying enforcement gate implementation by eliminating the metadata indirection step.

### B.2 Comparison to X.509 PKI

Traditional X.509 PKI uses Certificate Authorities (CAs) to sign certificates that bind public keys to identities. OAuth3 uses direct JWK publication instead of CA-signed certificates. The tradeoffs are:

| Property | X.509 PKI | OAuth3 JWK Direct |
|----------|-----------|-------------------|
| Trust anchor | CA certificate hierarchy | Configured issuer allowlist, DNS, or Store registry |
| Key binding | CA-signed certificate binds key to domain | Token's `issuer` field binds key to issuer URI |
| Revocation | OCSP, CRL (complex, often unreliable) | `/.well-known/oauth3-key-revocations.json` (simple, app-specific) |
| Key rotation | New certificate from CA (ceremony required) | New JWK published directly (no CA ceremony) |
| Algorithm | RSA and EC both common | ES256 only (P-256) |
| Infrastructure | Requires CA, certificate chain management | No CA required |

**Why OAuth3 avoids X.509 CAs.** The CA hierarchy is a trusted third party. Its compromise (e.g., DigiNotar, Comodo breach) is an ecosystem-wide failure. OAuth3's trust model is direct: the issuer publishes its keys, enforcement gates trust issuers they have explicitly configured. The trust relationship is bilateral and auditable, not delegated to a third party.

### B.3 Why ES256 over RS256

Both RS256 (RSASSA-PKCS1-v1_5 with SHA-256) and ES256 (ECDSA with P-256 and SHA-256) provide approximately 128-bit security. However, ES256 has several practical advantages for the OAuth3 use case:

| Property | RS256 (2048-bit RSA) | ES256 (P-256) |
|----------|----------------------|---------------|
| Signature size | 256 bytes | 64 bytes (4x smaller) |
| Public key size | ~294 bytes (PKCS#1) | ~65 bytes (uncompressed) |
| Key generation time | Slower (primality testing) | Faster (CSPRNG + curve point) |
| Signing time | ~1ms | ~0.1ms |
| Verification time | ~0.1ms | ~0.5ms |
| Security level | 112-bit (2048-bit RSA) | 128-bit (P-256) |

ES256 produces smaller signatures and smaller keys, which matters for:
- Token size: smaller `signature` field reduces token payload by ~200 bytes versus RS256
- JWK Set size: smaller public keys in the JWKS reduce bandwidth for enforcement gate polling
- DPoP proofs: smaller proofs reduce per-request header overhead

ES256 also provides a higher security level than 2048-bit RSA (128 bits vs. 112 bits), making it the strictly dominant choice at the target security level for OAuth3 v1.0.

**Note on RS256 legacy deployments.** Existing systems that use RS256 for OIDC or OAuth 2.x tokens are not required to change their existing token infrastructure. The ES256 requirement applies only to OAuth3 AgencyTokens as defined in this specification.

---

## Revision History

| Version | Date | Change |
|---------|------|--------|
| 0.1.0 | 2026-02-23 | Initial specification. Rung 641. All six sections and two appendices complete. Addresses Schneier adversarial review finding C-1 (CRITICAL: key management). Covers issuer key lifecycle, DPoP agent binding, v1.0 signature upgrade, trust anchor bootstrap, and Stillwater integration. |

---

*End of OAuth3 Key Management Specification v0.1.0*
