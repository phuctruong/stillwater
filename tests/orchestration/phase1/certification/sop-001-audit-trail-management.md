# SOP-001: Audit Trail Management

**Document ID:** SOP-001
**Version:** 1.0.0
**Effective Date:** 2026-02-24
**Owner:** Security & Compliance Team
**Approved By:** [Pending Approval]
**Review Cycle:** Annual (or upon significant system change)
**Related Documents:** compliance-matrix.md, audit-entry-schema.json, SOP-002, SOP-003, SOP-005

---

## 1. Purpose

This Standard Operating Procedure establishes the requirements, procedures, and responsibilities for managing audit trails within the Stillwater AI orchestration engine. Audit trails provide a tamper-evident, chronological record of all system activities, enabling regulatory compliance, forensic investigation, and operational accountability.

This SOP is designed to satisfy audit trail requirements across all certifications tracked in the compliance matrix, with particular attention to FDA 21 CFR Part 11 (the most prescriptive), HIPAA, SOC 2 Type II, EU AI Act, and FedRAMP.

---

## 2. Scope

This procedure applies to:
- All electronic records created, modified, or deleted within the Stillwater orchestration engine
- All AI model decisions, predictions, and outputs
- All user authentication and authorization events
- All administrative and configuration changes
- All systems, subsystems, and integrations within the compliance boundary

This procedure does NOT apply to:
- Development and staging environments (separate logging policy applies)
- Third-party systems outside the Stillwater compliance boundary (covered by vendor agreements)

---

## 3. Responsibilities

| Role | Responsibility |
|------|---------------|
| **Compliance Officer** | Owns this SOP; ensures it is current and enforced; conducts quarterly reviews of audit trail completeness |
| **Security Engineer** | Implements and maintains audit trail infrastructure; monitors integrity verification systems; responds to integrity alerts |
| **System Administrators** | Ensure logging agents are operational; manage log storage and retention; execute backup procedures |
| **Development Team** | Instrument all code paths to emit Part11AuditEntry-compliant log entries; include audit logging in code review checklists |
| **QA Team** | Verify audit trail completeness during testing; validate that all required fields are populated |
| **Internal Auditors** | Conduct monthly audit trail reviews; report findings to Compliance Officer |
| **External Auditors** | Access audit trails during certification assessments (read-only, supervised access) |

---

## 4. Audit Trail Format

### 4.1 Schema

All audit trail entries MUST conform to the Part11AuditEntry JSON schema defined in `audit-entry-schema.json`. The schema is the authoritative source; key fields are summarized here for reference.

### 4.2 Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `entry_id` | string (UUID v4) | Globally unique identifier for this audit entry | `"f47ac10b-58cc-4372-a567-0e02b2c3d479"` |
| `timestamp` | string (ISO 8601) | UTC timestamp of the event | `"2026-02-24T14:30:00.000Z"` |
| `event_type` | string (enum) | Category of event | `"RECORD_CREATE"`, `"RECORD_MODIFY"`, `"RECORD_DELETE"`, `"USER_LOGIN"`, `"USER_LOGOUT"`, `"SIGNATURE_APPLY"`, `"SIGNATURE_VERIFY"`, `"ACCESS_GRANT"`, `"ACCESS_REVOKE"`, `"CONFIG_CHANGE"`, `"MODEL_INFERENCE"`, `"MODEL_UPDATE"`, `"SYSTEM_ERROR"`, `"SECURITY_EVENT"` |
| `actor_id` | string | Unique identifier of the user or system performing the action | `"user-1234"` or `"system-orchestrator"` |
| `actor_name` | string | Human-readable name of the actor (printed name per Part 11) | `"Jane Smith"` |
| `action` | string | Description of the action performed | `"Updated patient record field: dosage"` |
| `resource_type` | string | Type of resource affected | `"electronic_record"`, `"model"`, `"configuration"`, `"user_account"` |
| `resource_id` | string | Unique identifier of the affected resource | `"record-5678"` |
| `old_value` | string or null | Previous value (for modifications) | `"50mg"` |
| `new_value` | string or null | New value (for modifications) | `"75mg"` |
| `reason` | string | Reason for the action (required for all modifications per Part 11) | `"Dosage adjustment per physician order #789"` |
| `signature` | object or null | Electronic signature details (when applicable) | See schema |
| `hash` | string | SHA-256 hash of the entry content | `"a1b2c3..."` |
| `previous_hash` | string or null | Hash of the previous entry in the chain (null for first entry) | `"d4e5f6..."` |
| `system_id` | string | Identifier of the system generating the entry | `"stillwater-orchestrator-prod-01"` |
| `session_id` | string | Session identifier linking related actions | `"sess-abcd-1234"` |
| `ip_address` | string | IP address of the actor (when applicable) | `"192.168.1.100"` |
| `integrity_status` | string (enum) | `"VALID"`, `"TAMPERED"`, `"UNVERIFIED"` | `"VALID"` |

### 4.3 Hash Chain

Audit entries form a hash chain to ensure tamper evidence:

1. Each entry's `hash` field contains the SHA-256 hash of the entry's content (all fields except `hash`, `previous_hash`, and `integrity_status`).
2. Each entry's `previous_hash` field contains the `hash` value of the immediately preceding entry.
3. The first entry in a chain has `previous_hash` set to `null`.
4. Breaking the chain (modifying any entry) is detectable by recomputing hashes from the beginning.

### 4.4 Electronic Signature Fields

When `event_type` is `SIGNATURE_APPLY`, the `signature` object MUST contain:

| Field | Type | Description |
|-------|------|-------------|
| `signer_id` | string | Unique identifier of the signer |
| `signer_name` | string | Printed name of the signer |
| `signature_meaning` | string | Meaning of the signature (e.g., "Approved", "Reviewed", "Authored") |
| `signature_timestamp` | string (ISO 8601) | Time the signature was applied |
| `authentication_method` | string | Method used to verify identity (e.g., "password+totp", "biometric+pin") |

---

## 5. Retention Policy

### 5.1 Retention Schedule

| Certification | Minimum Retention | Notes |
|--------------|-------------------|-------|
| FDA 21 CFR Part 11 | 7 years | Or as defined by applicable predicate rule, whichever is longer |
| HIPAA | 6 years | From date of creation or last effective date |
| SOX | 7 years | For audit workpapers |
| EU AI Act | 10 years | From market placement for high-risk AI systems |
| SOC 2 Type II | 3 years | Recommended for re-audit continuity |
| FedRAMP | 3 years | Per AU control family |
| PCI DSS | 12 months | 3 months immediately available |
| GDPR | 5 years | For breach records; processing records for duration of processing |

### 5.2 Unified Retention Policy

To simplify compliance across all certifications, the Stillwater orchestration engine applies a **unified minimum retention period of 10 years** for all audit trail entries. This satisfies the most stringent requirement (EU AI Act) and exceeds all other certification minimums.

### 5.3 Retention Implementation

- Audit entries are stored in append-only, write-once storage.
- Entries older than 90 days are migrated to cold storage (compressed, encrypted, indexed).
- Cold storage entries remain queryable via the audit trail API with higher latency (target: < 30 seconds).
- No audit entry may be deleted before the 10-year retention period expires.
- Deletion after retention period requires Compliance Officer approval and is itself logged as an audit event.

---

## 6. Integrity Verification Procedure

### 6.1 Automated Continuous Verification

The system performs automated hash chain verification on a rolling basis:

1. **Real-time:** Each new entry's `previous_hash` is validated against the most recent entry before insertion.
2. **Hourly:** A background process verifies the hash chain for all entries created in the past 24 hours.
3. **Daily:** A full chain verification runs during the maintenance window (02:00--04:00 UTC).

### 6.2 Manual Verification Procedure

The Security Engineer SHALL perform a manual hash chain verification monthly:

1. Export the audit trail for the verification period using the audit trail API.
2. Execute the hash chain verification tool: `stillwater audit verify --start-date YYYY-MM-DD --end-date YYYY-MM-DD`.
3. The tool recomputes all hashes from the start of the chain and reports:
   - Total entries verified
   - Chain integrity status (INTACT or BROKEN)
   - If BROKEN: the first entry where the chain diverges, with before/after hashes
4. Document the verification result in the Monthly Audit Trail Review Report.
5. If BROKEN: immediately escalate to the Compliance Officer and initiate SOP-005 (Incident Response).

### 6.3 Integrity Alert Response

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| CRITICAL | Hash chain broken in production | Immediate (< 15 minutes) | Isolate affected segment; initiate SOP-005; notify Compliance Officer |
| HIGH | Verification process failure | < 1 hour | Restart verification; investigate root cause; if persistent, escalate |
| MEDIUM | Verification delay (> 2x expected duration) | < 4 hours | Investigate performance; verify no data corruption |
| LOW | Verification warning (non-critical anomaly) | Next business day | Document and investigate during scheduled review |

---

## 7. Backup and Recovery Procedures

### 7.1 Backup Schedule

| Type | Frequency | Retention | Storage |
|------|-----------|-----------|---------|
| Incremental | Every 6 hours | 30 days | Secondary region (encrypted, AES-256-GCM) |
| Full | Weekly (Sunday 00:00 UTC) | 1 year | Secondary region + offline archive |
| Archive | Monthly (1st of month) | 10 years | Offline archive (air-gapped, encrypted) |

### 7.2 Backup Integrity

- All backups are encrypted at rest using AES-256-GCM with keys managed by a Hardware Security Module (HSM).
- Each backup includes a manifest file with SHA-256 checksums of all included audit entries.
- Backup integrity is verified upon creation and again upon any restore operation.

### 7.3 Recovery Procedure

1. Identify the recovery point (timestamp or entry_id).
2. Retrieve the most recent backup that includes or precedes the recovery point.
3. Verify backup integrity using the manifest checksums.
4. Restore the audit trail to a staging environment first.
5. Run full hash chain verification on the restored data.
6. Once verified, promote to production with Compliance Officer approval.
7. Document the recovery event as an audit entry (event_type: `SYSTEM_ERROR`, action: "Audit trail recovery from backup").

### 7.4 Recovery Testing

- Recovery procedures are tested quarterly using a randomly selected backup.
- Recovery test results are documented and retained for 3 years.
- Recovery Time Objective (RTO): 4 hours for hot storage; 24 hours for cold storage.
- Recovery Point Objective (RPO): 6 hours (aligned with incremental backup frequency).

---

## 8. Review Schedule

### 8.1 Monthly Audit Trail Review

The Internal Auditor SHALL conduct a monthly review covering:

1. **Completeness check:** Verify all expected event types are represented in the audit trail.
2. **Integrity verification:** Confirm hash chain is intact (per Section 6.2).
3. **Anomaly detection:** Review for unusual patterns (e.g., bulk deletions, off-hours access, repeated failed logins).
4. **Signature compliance:** Verify all signature events include required fields per Part 11.
5. **Retention compliance:** Confirm no entries have been improperly deleted or modified.

### 8.2 Quarterly Compliance Review

The Compliance Officer SHALL conduct a quarterly review covering:

1. **Cross-certification mapping:** Verify audit trail meets requirements for all in-scope certifications.
2. **Gap analysis:** Identify any new certification requirements not yet addressed.
3. **SOP currency:** Confirm this SOP reflects current system architecture and regulatory landscape.
4. **Finding resolution:** Track and verify resolution of any findings from monthly reviews.

### 8.3 Annual SOP Review

This SOP is reviewed annually (or upon significant system change) by:
- Compliance Officer (owner)
- Security Engineer
- Development Team Lead
- External Auditor (if applicable)

Changes to this SOP follow the change control process defined in SOP-002.

---

## 9. Records

The following records are generated and maintained under this SOP:

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| Audit trail entries | System (automated) | 10 years | Primary + cold storage |
| Monthly Audit Trail Review Reports | Internal Auditor | 5 years | Compliance repository |
| Quarterly Compliance Review Reports | Compliance Officer | 5 years | Compliance repository |
| Hash chain verification logs | System (automated) | 3 years | Operations log store |
| Backup manifests | System Administrator | 10 years (matched to backups) | Backup storage |
| Recovery test results | System Administrator | 3 years | Operations repository |
| Integrity alert investigation records | Security Engineer | 5 years | Incident tracking system |

---

## 10. References

- FDA 21 CFR Part 11 -- Electronic Records; Electronic Signatures
- HIPAA Security Rule (45 CFR 164.312(b) -- Audit Controls)
- AICPA TSC CC7.2 -- System Operations (Monitoring)
- ISO/IEC 42001:2023 -- AI Management System (Clause 9 -- Performance Evaluation)
- EU AI Act Article 12 -- Record-keeping (Logging)
- NIST SP 800-53 Rev. 5 -- AU Control Family
- FedRAMP Continuous Monitoring Strategy Guide
- PCI DSS v4.0.1 -- Requirement 10 (Log and Monitor All Access)
- `audit-entry-schema.json` -- Part11AuditEntry JSON Schema
- SOP-002: Change Control
- SOP-003: Access Control
- SOP-005: Incident Response

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2026-02-24 | Security & Compliance Team | Initial release |
