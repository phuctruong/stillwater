# SOP-002: Change Control

**Document ID:** SOP-002
**Version:** 1.0.0
**Effective Date:** 2026-02-24
**Owner:** Engineering & Compliance Team
**Approved By:** [Pending Approval]
**Review Cycle:** Annual (or upon significant process change)
**Related Documents:** compliance-matrix.md, SOP-001, SOP-004, SOP-005

---

## 1. Purpose

This Standard Operating Procedure establishes the change control process for the Stillwater AI orchestration engine. It ensures that all changes to production systems, configurations, code, models, and documentation are assessed, approved, tested, and documented in a manner that satisfies regulatory and certification requirements.

This SOP addresses change control requirements for SOC 2 (CC8.1), ISO 27001 (A.8.32), FedRAMP (CM control family), FDA 21 CFR Part 11, SOX ITGCs, HITRUST, and CMMC.

---

## 2. Scope

This procedure applies to all changes affecting:
- Production application code and infrastructure
- AI models and model configurations (also governed by SOP-004)
- Database schemas and data migration scripts
- System configurations, environment variables, and feature flags
- Security controls, firewall rules, and access policies
- Third-party integrations and API contracts
- Documentation that constitutes part of the quality or compliance system

This procedure does NOT apply to:
- Changes in development environments that have not been promoted to staging or production
- Emergency hotfixes (see Section 4.4 for emergency change procedure)
- Routine operational tasks covered by runbooks (e.g., log rotation, certificate renewal on schedule)

---

## 3. Responsibilities

| Role | Responsibility |
|------|---------------|
| **Change Requestor** | Submits the Change Request (CR) with full description, justification, and risk assessment |
| **Change Advisory Board (CAB)** | Reviews and approves/rejects Major and Critical changes; meets weekly or on-demand for Critical |
| **Technical Lead** | Reviews Minor changes; approves or escalates to CAB; ensures technical adequacy |
| **QA Lead** | Validates that testing requirements are met before promotion; signs off on test evidence |
| **Security Engineer** | Assesses security impact; required reviewer for all changes touching authentication, authorization, encryption, or audit systems |
| **Compliance Officer** | Reviews changes with regulatory impact; required approver for changes affecting certified systems |
| **Release Manager** | Coordinates deployment; ensures all approvals are in place; executes or oversees production deployment |
| **System Administrator** | Executes infrastructure changes; provides post-deployment verification |

---

## 4. Procedures

### 4.1 Change Classification

All changes MUST be classified before processing:

| Classification | Definition | Examples | Approval Authority | Testing Requirement |
|---------------|------------|----------|-------------------|-------------------|
| **Minor** | Low-risk change with no impact on security controls, compliance posture, or system architecture | UI text fix, non-functional dependency update, documentation correction | Technical Lead | Unit tests + regression suite |
| **Major** | Moderate-risk change affecting functionality, performance, or system behavior but not security controls directly | New feature, API endpoint addition, database schema migration, model parameter tuning | CAB (majority approval) | Unit + integration + performance tests + staging validation |
| **Critical** | High-risk change affecting security controls, compliance-scoped systems, authentication, encryption, audit trails, or AI model behavior | Security patch, encryption algorithm change, audit trail schema change, model retraining, access control modification | CAB (unanimous approval) + Compliance Officer | Full test suite + security scan + penetration test (if applicable) + staging validation + rollback verification |

### 4.2 Change Request Process

#### Step 1: Submit Change Request

The Change Requestor creates a CR containing:

| Field | Required | Description |
|-------|----------|-------------|
| CR ID | Auto-generated | Unique identifier (format: `CR-YYYY-NNNN`) |
| Title | Yes | Brief description of the change |
| Classification | Yes | Minor, Major, or Critical |
| Description | Yes | Detailed description of what will change and how |
| Justification | Yes | Business or technical reason for the change |
| Risk Assessment | Yes | Identified risks and mitigation strategies |
| Impact Assessment | Yes | Systems, users, and certifications affected (see Section 4.3) |
| Rollback Plan | Yes | Detailed procedure to reverse the change if needed |
| Testing Plan | Yes | Specific tests to be executed and pass criteria |
| Target Date | Yes | Requested deployment date |
| Requestor | Yes | Name and role of the person requesting the change |
| Rung Level | Yes | Stillwater rung target for verification (641, 274177, or 65537) |

#### Step 2: Impact Assessment

The Change Requestor, with assistance from the Technical Lead and Security Engineer, completes the impact assessment:

1. **System Impact:** Which systems, services, or components are affected?
2. **User Impact:** Will users experience downtime, behavior changes, or require retraining?
3. **Data Impact:** Does the change affect data schemas, data flows, or data retention?
4. **Security Impact:** Does the change affect authentication, authorization, encryption, or audit controls?
5. **Compliance Impact:** Which certifications are affected? (Cross-reference compliance-matrix.md)
6. **Model Impact:** Does the change affect AI model behavior, inputs, or outputs? (If yes, also follow SOP-004)
7. **Dependency Impact:** Are upstream or downstream systems affected?

#### Step 3: Review and Approval

| Classification | Review Process | Approval Timeline |
|---------------|----------------|-------------------|
| Minor | Technical Lead reviews CR, test plan, and code diff. Approves or requests revision. | 1 business day |
| Major | CAB reviews at weekly meeting (or async if urgent). Security Engineer and QA Lead must sign off. | 3 business days |
| Critical | CAB convenes emergency session if needed. Compliance Officer, Security Engineer, and QA Lead must all sign off. Unanimous CAB approval required. | 5 business days (emergency: same day) |

#### Step 4: Implementation

1. Developer implements the change in a feature branch.
2. Code review by at least one reviewer (two reviewers for Critical changes).
3. Automated test suite executes per the testing plan.
4. For Major and Critical changes: deploy to staging environment and validate.
5. QA Lead signs off on test evidence.
6. Release Manager confirms all approvals are recorded in the CR.

#### Step 5: Deployment

1. Release Manager schedules deployment within the approved maintenance window.
2. Pre-deployment checklist completed (backups verified, rollback tested, monitoring alerts configured).
3. Change deployed to production.
4. Post-deployment verification executed (smoke tests, health checks, audit trail verification).
5. Deployment confirmation recorded in the CR.

#### Step 6: Post-Change Verification

1. Verify the change achieves its stated objective.
2. Verify no regressions via monitoring dashboards (minimum 24-hour observation for Major/Critical).
3. Verify audit trail entries are generated for the change (see SOP-001).
4. For compliance-impacting changes: Compliance Officer reviews and signs off.
5. CR status updated to COMPLETED or ROLLED_BACK.

### 4.3 Impact Assessment: Certification Cross-Reference

When a change affects a certified system, the following additional requirements apply:

| Certification | Additional Requirement |
|--------------|----------------------|
| SOC 2 | Document the change in the continuous monitoring evidence package |
| ISO 27001 | Update the Statement of Applicability if new controls are introduced or removed |
| ISO 42001 | Update AI impact assessment if model behavior is affected |
| EU AI Act | Update technical documentation; re-notify if risk classification changes |
| FedRAMP | Submit Significant Change Request (SCR) to authorizing official if security boundary changes |
| FDA Part 11 | Revalidate system per GAMP 5; update IQ/OQ/PQ documentation |
| HIPAA | Update risk analysis if PHI handling is affected |
| HITRUST | Update MyCSF control evidence |
| PCI DSS | Update network diagrams and data flow diagrams if CDE is affected |
| SOX | Update ITGC documentation and management testing schedule |
| CMMC | Update SSP and POA&M if CUI handling is affected |

### 4.4 Emergency Change Procedure

For changes required to address active security incidents, critical system outages, or imminent regulatory deadlines:

1. **Authorization:** Verbal or electronic approval from at least one CAB member and the Security Engineer (or Compliance Officer if compliance-related).
2. **Implementation:** Change implemented with abbreviated (not eliminated) testing.
3. **Minimum Testing:** Smoke test and security scan must pass before production deployment.
4. **Documentation:** Full CR must be submitted retroactively within 24 hours of deployment.
5. **Review:** Emergency change reviewed at next CAB meeting with full post-mortem.
6. **Audit Trail:** All emergency changes are flagged in the audit trail with `event_type: CONFIG_CHANGE` and `reason` field noting "EMERGENCY CHANGE" with the justification.

---

## 5. Approval Authority Matrix by Rung Level

The Stillwater rung system provides an additional verification layer aligned with change classification:

| Rung Level | Change Scope | Verification Requirements |
|------------|-------------|--------------------------|
| **641** | Minor changes | Local safety check; red/green gate; no regressions; evidence bundle (unit tests + code review) |
| **274177** | Major changes | Stability verification; seed sweep; replay tests; null/zero edge cases; integration test evidence |
| **65537** | Critical changes | Adversarial testing; security scanner evidence; exploit reproduction attempt; drift analysis; full promotion sweeps; Compliance Officer sign-off |

A change MUST achieve its declared rung level before promotion to production. The integration rung of a release is the MINIMUM rung across all included changes.

---

## 6. Documentation Requirements

### 6.1 Change Request Record

Every CR record MUST be retained with the following documentation:

- Original CR submission (all fields per Section 4.2, Step 1)
- Impact assessment (all dimensions per Section 4.2, Step 2)
- All review comments and approval/rejection records with timestamps
- Code diff or configuration diff
- Test execution results with pass/fail status
- Deployment log with timestamps
- Post-change verification results
- Rollback execution record (if applicable)

### 6.2 Audit Trail Entries

The following audit events are generated automatically for each change:

| Event | `event_type` | Trigger |
|-------|-------------|---------|
| CR created | `RECORD_CREATE` | CR submission |
| CR approved/rejected | `RECORD_MODIFY` | Approval action |
| Code deployed to staging | `CONFIG_CHANGE` | Staging deployment |
| Code deployed to production | `CONFIG_CHANGE` | Production deployment |
| Post-change verification | `RECORD_MODIFY` | Verification completion |
| Rollback executed | `CONFIG_CHANGE` | Rollback action |

All audit entries follow the Part11AuditEntry schema (see SOP-001 and audit-entry-schema.json).

### 6.3 Retention

| Record | Retention Period |
|--------|-----------------|
| Change Request records | 10 years (aligned with SOP-001 unified retention) |
| Code diffs | 10 years (retained in version control) |
| Test execution results | 5 years |
| Deployment logs | 5 years |
| CAB meeting minutes | 5 years |

---

## 7. Post-Change Verification

### 7.1 Automated Verification

The following automated checks execute after every production deployment:

1. **Health check:** All service endpoints return expected status codes.
2. **Smoke tests:** Core user journeys execute successfully.
3. **Audit trail check:** Verify that the deployment generated expected audit entries.
4. **Security scan:** SAST/DAST scan against the deployed version (Critical changes only).
5. **Performance baseline:** Response times and error rates within acceptable thresholds.

### 7.2 Manual Verification

For Major and Critical changes, the following manual steps are required within 24 hours:

1. QA Lead verifies the change against acceptance criteria.
2. Security Engineer reviews security scan results (Critical changes).
3. Compliance Officer confirms compliance posture is maintained (compliance-impacting changes).
4. Release Manager updates the CR with verification results and closes the CR.

---

## 8. Records

The following records are generated and maintained under this SOP:

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| Change Request records | Release Manager | 10 years | Change management system |
| CAB meeting minutes | CAB Chair | 5 years | Compliance repository |
| Test execution evidence | QA Lead | 5 years | CI/CD artifact store |
| Deployment logs | Release Manager | 5 years | Operations log store |
| Post-change verification reports | Release Manager | 5 years | Change management system |
| Emergency change post-mortems | CAB Chair | 5 years | Compliance repository |

---

## 9. References

- AICPA TSC CC8.1 -- Change Management
- ISO/IEC 27001:2022 Annex A.8.32 -- Change Management
- NIST SP 800-53 Rev. 5 -- CM Control Family (CM-1 through CM-11)
- FDA 21 CFR Part 11 -- System Validation Requirements
- SOX ITGC -- Change Management Controls
- HITRUST CSF -- Change Management Domain
- FedRAMP Configuration Management (CM) Controls
- CMMC Level 2 -- Configuration Management (CM) Domain
- SOP-001: Audit Trail Management
- SOP-004: Model Version Control
- SOP-005: Incident Response
- compliance-matrix.md

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2026-02-24 | Engineering & Compliance Team | Initial release |
