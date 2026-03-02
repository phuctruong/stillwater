# Paper 19: E-Sign Architecture — OAuth3-Backed Electronic Signatures

| Field | Value |
|-------|-------|
| **Channel** | [3] Architecture |
| **Rung** | 65537 |
| **GLOW** | G=growth (revenue from day one), L=learn (CRIO heritage), O=optimize (Part 11), W=wow (self-service compliance) |
| **Diagram** | cli:20 (E-Sign Flow + Token Lifecycle) |
| **Depends** | cli:02 (OAuth3), cli:18 (Competitive Moat), browser:03 (Evidence) |
| **Unlocks** | cli:20 (Pricing Architecture), SOP-006 (E-Sign Validation) |
| **Pipeline** | [1] PAPER → [2] DIAGRAM → [3] STYLEGUIDE → [4] WEBSERVICE → [5] TESTS → [6] CODE → [7] SEAL |
| **DNA** | `esign(token, attest, sign, chain, verify) → evidence(hash, link, seal) → revenue($8→$188)` |

---

## [2] Identity — Heritage

CRIO electronic signature system (Java/Struts2, 2015-2026) ported to Python/FastAPI with OAuth3 improvements. CRIO handles 10,000+ signatures/day in FDA-regulated clinical trials. Solace inherits the battle-tested flow and improves every weakness.

### CRIO → Solace Improvements

| Aspect | Solace Enhancement |
|--------|--------------------|
| **Password authentication** | bcrypt/Argon2 hashing |
| **Token binding** | OAuth3 scoped, user-locked, TTL-bounded |
| **Evidence chain** | SHA-256 hash-chained, tamper-evident |
| **Storage encryption** | AES-256-GCM vault + PZip compression |
| **Audit trail** | ALCOA+ compliant evidence bundles |
| **Revocation** | Instant, cross-vertex, OAuth3-scoped |
| **Bulk signing** | Single token for batch, individual evidence per document |
| **Verification** | Public endpoint, anyone with hash can verify |
| **Drawing capture** | Fabric.js (retained — proven UX) |

---

## [3] Architecture — Signing Flow

### 3.1 Token Lifecycle (from CRIO, improved)

```
[1] REQUEST TOKEN → [2] DISPLAY MODAL → [3] SIGN → [4] CHAIN → [5] VERIFY
     UUID+TTL        Password|Drawing    Attest+Hash   Link→prev    Public check
```

### 3.2 State Machine

```
IDLE → TOKEN_ISSUED → MODAL_DISPLAYED → SIGNING → SIGNED → VERIFIED
                                      ↘ REJECTED
                    ↘ EXPIRED
```

### 3.3 Signature Modes (retained from CRIO)

| Mode | Description | Part 11 |
|------|------------|---------|
| **Password** | Username + password re-authentication | Required (21 CFR 11.200) |
| **Drawing** | Fabric.js canvas freehand signature | Required (21 CFR 11.200) |

### 3.4 Attestation Statements (expanded from CRIO)

| Statement | CRIO | Solace |
|-----------|------|--------|
| "I have reviewed this document" | Yes | Yes |
| "I have reviewed and approve this document" | Yes | Yes |
| "I certify that this document is accurate" | Yes | Yes |
| "I certify that this file is a true and correct copy" | Yes | Yes |
| "I attest to the veracity of this record" | No | Yes (new) |
| Custom (user-defined) | Yes | Yes |

### 3.5 Evidence Hash Chain

Each signature creates a hash-chained evidence record:

```python
evidence = {
    "signature_id": uuid4(),
    "document_id": doc_id,
    "user_id": user.id,
    "user_email": user.email,
    "mode": "password|drawing",
    "attestation": "I have reviewed...",
    "signed_at": ISO-8601,
    "previous_hash": chain_head,  # Links to previous signature
    "esign_token": token_uuid,
    "has_drawing": bool,
}
evidence_hash = SHA-256(canonical_json(evidence))
chain_head = evidence_hash  # Advance chain
```

---

## [5] Laws — Part 11 Compliance

### 5.1 21 CFR Part 11 Mapping

| Part 11 Requirement | Section | Solace Implementation |
|---------------------|---------|----------------------|
| **Electronic signatures** | 11.100 | Unique to individual, not reusable |
| **Signature components** | 11.200 | Two components: identity (email) + attestation (statement) |
| **Controls for open systems** | 11.30 | AES-256-GCM encryption + hash chains |
| **Signature linking** | 11.70 | SHA-256 hash chain links signature to document |
| **Authority checks** | 11.10(g) | OAuth3 token validates user authority |
| **Audit trail** | 11.10(e) | Evidence bundle with previous_hash chain |
| **System validation** | 11.10(a) | Automated tests (IQ/OQ/PQ pattern) |

### 5.2 ALCOA+ Compliance

| Principle | Implementation |
|-----------|---------------|
| **Attributable** | user_id + user_email in every signature |
| **Legible** | JSON evidence + PDF export |
| **Contemporaneous** | signed_at = server UTC timestamp |
| **Original** | Hash-chained, tamper-evident |
| **Accurate** | SHA-256 recomputation verification |
| **Complete** | All fields required, no partial signatures |
| **Consistent** | Canonical JSON serialization |
| **Enduring** | PZip compressed, cloud-replicated |
| **Available** | Public /verify endpoint |

---

## [7] Context — API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/esign/token` | Required | Generate e-sign token |
| POST | `/api/v1/esign/sign` | Required | Submit signature |
| POST | `/api/v1/esign/bulk-sign` | Required | Bulk sign documents |
| POST | `/api/v1/esign/verify` | None | Verify signature hash |
| GET | `/api/v1/esign/signatures/{doc_id}` | Required | List document signatures |
| GET | `/api/v1/esign/chain/status` | Required | Chain head + counts |
| GET | `/api/v1/esign/attestations` | None | List attestation options |

---

## [11] Issues — Pricing Integration

### 5-Tier Value Ladder (Rory Sutherland + Russell Brunson)

| Tier | Belt | Price | E-Signatures | Evidence Retention | Part 11 |
|------|------|-------|-------------|-------------------|---------|
| Free | White | $0 | 3/mo | Local only | No |
| Starter | Yellow | $8/mo | 25/mo | 30 days | No |
| Pro | Orange | $28/mo | 100/mo | 90 days + PZip | Architected |
| Team | Green | $88/mo | 500/mo | 1 year + search | Architected |
| Enterprise | Black | $188/mo | Unlimited | Unlimited + regulatory export | Architected |

### Psychology Applied

| Mechanism | Implementation |
|-----------|---------------|
| **Anchoring** | $188 shown first → $28 feels affordable |
| **Goldilocks** | $28 Pro is the target tier (70% of conversions) |
| **Decoy** | $8 Starter makes $28 look like 7x value for 3.5x price |
| **Loss aversion** | "Don't lose audit evidence" not "get storage" |
| **Left-digit** | $28 (not $30), $88 (not $90), $188 (not $200) |
| **Value stack** | Each tier shows 7-21x replacement value vs price |

---

## [13] Evolution — Revenue from Day One

E-sign is the first paid feature that generates revenue from day one. Combined with Part 11 Architected evidence storage (self-service), this fills a $15K-$250K/year market gap where no competitor exists below $1K/year.

**Market gap**: SimplerQMS (cheapest Part 11 storage) starts at $15K/year. Solace Enterprise at $188/mo = $2,256/year. That's 85% cheaper than the cheapest competitor.

**PZip advantage**: Evidence storage costs $0.00032/user/month with PZip compression. Competitors charge $50-200/user/month for the same storage without compression.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-01 | Phuc Truong | Initial release — CRIO port + OAuth3 + 5-tier pricing |
