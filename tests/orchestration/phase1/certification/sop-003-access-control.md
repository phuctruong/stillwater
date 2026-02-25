# SOP-003: Access Control

**Document ID:** SOP-003
**Version:** 1.0.0
**Effective Date:** 2026-02-24
**Owner:** Security & Compliance Team
**Approved By:** [Pending Approval]
**Review Cycle:** Annual (or upon significant system change)
**Related Documents:** compliance-matrix.md, SOP-001, SOP-002, SOP-005

---

## 1. Purpose

This Standard Operating Procedure establishes the requirements, procedures, and responsibilities for managing access control within the Stillwater AI orchestration engine. It ensures that access to systems, data, and electronic records is granted on a least-privilege basis, authenticated securely, and audited continuously.

This SOP addresses access control requirements for FDA 21 CFR Part 11, HIPAA (45 CFR 164.312), SOC 2 (CC6.1-CC6.8), ISO 27001 (A.5.15-A.5.18, A.8.2-A.8.5), FedRAMP (AC/IA control families), PCI DSS (Requirements 7-8), SOX ITGCs, and GDPR (Article 32).

---

## 2. Scope

This procedure applies to:
- All user accounts (human users, service accounts, API keys)
- All systems, applications, and databases within the Stillwater compliance boundary
- All access methods (web UI, CLI, API, SSH, database console, cloud console)
- All environments (production, staging, disaster recovery)

This procedure does NOT apply to:
- Development environment local accounts (separate policy applies)
- Public-facing read-only endpoints that require no authentication

---

## 3. Responsibilities

| Role | Responsibility |
|------|---------------|
| **Security Engineer** | Implements and maintains access control infrastructure (IAM, MFA, RBAC); responds to access-related security events |
| **Compliance Officer** | Oversees quarterly access reviews; ensures access control meets certification requirements |
| **Team Managers** | Approve access requests for their team members; report role changes and departures promptly |
| **System Administrators** | Execute account provisioning, modification, and deprovisioning; manage service accounts |
| **HR Department** | Notifies IT of new hires, role changes, and terminations within 24 hours |
| **All Users** | Protect credentials; report suspected unauthorized access; comply with password and session policies |
| **Internal Auditors** | Review access control logs and configurations during scheduled audits |

---

## 4. Procedures

### 4.1 User Account Management

#### 4.1.1 Account Creation

1. **Request:** The Team Manager submits an Access Request Form containing:
   - User's full name and unique identifier
   - Role assignment (see Section 4.3)
   - Business justification for each requested role
   - Start date
   - Expected duration (permanent or time-bound)
   - Supervisor approval

2. **Verification:** The System Administrator verifies:
   - The request is approved by an authorized manager
   - The requested roles follow least-privilege principle
   - No conflicting roles (segregation of duties check)

3. **Provisioning:** The System Administrator creates the account:
   - Unique user ID (never reused, even after account deletion)
   - Temporary password (must be changed at first login)
   - MFA enrollment initiated (see Section 4.2)
   - Default session timeout configured
   - Account flagged as ACTIVE

4. **Audit:** Account creation generates a Part11AuditEntry with:
   - `event_type`: `ACCESS_GRANT`
   - `action`: "User account created"
   - `resource_type`: `user_account`
   - `reason`: Business justification from the request form

#### 4.1.2 Account Modification

1. **Trigger:** Role change, department transfer, project reassignment, or access review finding.
2. **Request:** Team Manager (new or existing) submits modification request with justification.
3. **Review:** Security Engineer reviews for privilege escalation or segregation-of-duties conflicts.
4. **Execution:** System Administrator modifies the account; old roles removed before new roles added.
5. **Audit:** Modification generates a Part11AuditEntry with `event_type`: `ACCESS_GRANT` or `ACCESS_REVOKE`, capturing old and new role assignments.

#### 4.1.3 Account Deprovisioning

| Trigger | Timeline | Action |
|---------|----------|--------|
| Voluntary departure | Within 24 hours of last working day | Disable account; revoke all active sessions; archive access logs |
| Involuntary termination | Immediately upon notification | Disable account; revoke all active sessions; change shared credentials; archive access logs |
| Role change (no longer needs access) | Within 48 hours of role change | Remove specific roles/permissions; retain account if other access justified |
| Contractor end of engagement | End of contract date | Disable account; revoke all active sessions |
| Inactivity (90 days no login) | Automatic | Disable account; notify manager; require re-justification to reactivate |

Deprovisioning steps:
1. Disable the account (do not delete; retain for audit trail integrity).
2. Revoke all active sessions and tokens.
3. Remove from all groups and roles.
4. Rotate any shared credentials the user had access to.
5. Generate audit entry with `event_type`: `ACCESS_REVOKE`.
6. Archive the user's access history for retention period (10 years per SOP-001).

### 4.2 Authentication Requirements

#### 4.2.1 Password Policy

| Parameter | Requirement | Certification Driver |
|-----------|-------------|---------------------|
| Minimum length | 14 characters | NIST 800-63B, FedRAMP |
| Complexity | At least 3 of 4 categories (upper, lower, digit, special) | PCI DSS, HIPAA |
| Maximum age | 365 days (or upon compromise indication) | NIST 800-63B (updated guidance) |
| Minimum age | 1 day (prevent rapid cycling) | SOX ITGC |
| History | Cannot reuse last 24 passwords | FedRAMP, PCI DSS |
| Lockout threshold | 5 failed attempts | PCI DSS, FedRAMP |
| Lockout duration | 30 minutes (or manual unlock by administrator) | PCI DSS |
| Storage | bcrypt (cost factor >= 12) or Argon2id | OWASP, NIST |

#### 4.2.2 Multi-Factor Authentication (MFA)

MFA is REQUIRED for:

| Context | MFA Requirement | Method |
|---------|----------------|--------|
| All user logins | Required | TOTP (authenticator app) or FIDO2 hardware key |
| Electronic signatures (FDA Part 11) | Required (two distinct factors) | Password + TOTP or Password + FIDO2 |
| Privileged access (admin, root, DBA) | Required (phishing-resistant) | FIDO2 hardware key preferred; TOTP acceptable |
| API access | Required for token issuance | OAuth2 + client certificate or API key + IP allowlist |
| Remote access (VPN, SSH) | Required | Certificate + TOTP or FIDO2 |
| Cloud console access | Required | SSO with MFA enforced at identity provider |

MFA implementation:
- TOTP: RFC 6238 compliant; 30-second time step; SHA-256 minimum
- FIDO2: WebAuthn Level 2 compliant; platform and roaming authenticator support
- Backup codes: 10 single-use codes generated at MFA enrollment; stored encrypted; regenerated upon use of last code
- Recovery: Identity verification by two administrators required if all MFA methods lost

#### 4.2.3 Session Management

| Parameter | Value | Notes |
|-----------|-------|-------|
| Session timeout (idle) | 15 minutes | Configurable per role (minimum 5 minutes for privileged) |
| Session timeout (absolute) | 8 hours | Requires re-authentication regardless of activity |
| Concurrent sessions | Maximum 3 per user | Alert on 4th attempt |
| Session token | Cryptographically random, minimum 128 bits | Regenerated after authentication and privilege changes |
| Secure attributes | HttpOnly, Secure, SameSite=Strict | Required for all session cookies |
| Session termination | Explicit logout or timeout | Session data purged from server; token invalidated |

### 4.3 Authorization Levels (Role-Based Access Control)

#### 4.3.1 Role Definitions

| Role | Description | Access Level | Segregation Constraints |
|------|-------------|-------------|------------------------|
| **Viewer** | Read-only access to non-sensitive system data | View dashboards, reports, public configurations | None |
| **Operator** | Execute pre-defined operations and workflows | Run models, execute recipes, view results | Cannot modify configurations or access raw data |
| **Analyst** | Access to data for analysis and reporting | Query databases (read-only), export reports, view audit logs | Cannot modify data or system configurations |
| **Developer** | Modify application code and configurations | Code repository access, staging deployment, test environment access | Cannot deploy to production directly |
| **QA Engineer** | Test and validate changes | Staging environment access, test data access, test result approval | Cannot approve own code for production |
| **Release Manager** | Deploy approved changes to production | Production deployment, release management | Cannot approve changes they authored |
| **Security Engineer** | Manage security controls and investigate incidents | Security tool access, audit log access, firewall management, incident response | Cannot approve own access changes |
| **Administrator** | Full system administration | All system access, account management, configuration management | Cannot be sole approver for Critical changes |
| **Compliance Officer** | Compliance oversight and certification management | Audit log access, compliance documentation, certification evidence | Cannot modify technical controls directly |
| **Auditor (External)** | Read-only access for audit purposes | Audit logs, compliance documentation, system configuration (read-only) | Time-bound access; supervised sessions |

#### 4.3.2 Role Assignment Principles

1. **Least Privilege:** Users receive only the minimum permissions required for their job function.
2. **Segregation of Duties:** No single user may both create and approve the same transaction. Specific conflicts:
   - Developer + Release Manager (for the same change)
   - Change Requestor + sole Change Approver
   - Account Creator + Account Approver (for the same account)
3. **Need-to-Know:** Access to data is restricted to users whose job function requires it.
4. **Time-Bound Access:** Elevated privileges granted temporarily with automatic expiration.

#### 4.3.3 Service Account Management

Service accounts (non-human identities) follow additional controls:

| Control | Requirement |
|---------|-------------|
| Naming convention | `svc-<system>-<purpose>` (e.g., `svc-orchestrator-db-read`) |
| Owner | Each service account has a named human owner responsible for its lifecycle |
| Authentication | API key + client certificate (no password-based auth) |
| Credential rotation | Every 90 days (automated) |
| Scope | Minimum required permissions; never admin-level |
| Monitoring | All service account activity logged; anomaly detection enabled |
| Review | Included in quarterly access review |

### 4.4 Access Review Schedule

#### 4.4.1 Quarterly Access Review

The Compliance Officer coordinates a quarterly access review:

1. **Generate report:** Export all active accounts, role assignments, and last login dates.
2. **Manager review:** Each Team Manager reviews their team members' access and confirms:
   - Each user still requires the assigned roles
   - No excessive privileges exist
   - No dormant accounts (last login > 90 days)
3. **Segregation check:** Security Engineer verifies no segregation-of-duties violations.
4. **Service account review:** Service account owners confirm each account is still required and properly scoped.
5. **Remediation:** Any issues identified are remediated within 10 business days.
6. **Sign-off:** Compliance Officer signs off on the completed review.
7. **Audit trail:** Review results recorded as Part11AuditEntry events.

#### 4.4.2 Triggered Reviews

Access reviews are also triggered by:
- Security incident involving unauthorized access (see SOP-005)
- Certification audit finding related to access control
- Significant organizational restructuring
- New certification coming into scope

### 4.5 Incident Response for Unauthorized Access

#### 4.5.1 Detection

Unauthorized access may be detected via:
- Failed login threshold alerts (5+ failures in 10 minutes)
- Anomalous access pattern detection (unusual time, location, or volume)
- Privilege escalation alerts
- Access from unknown IP addresses or devices
- Manual report from a user or administrator

#### 4.5.2 Immediate Response

1. **Contain:** Disable the affected account(s) immediately.
2. **Preserve:** Capture and preserve all relevant audit logs.
3. **Assess:** Determine the scope (which systems, data, and records were accessed).
4. **Escalate:** Notify the Security Engineer and Compliance Officer per SOP-005 escalation matrix.

#### 4.5.3 Investigation

1. Review audit trail entries for the affected account(s) and timeframe.
2. Identify the attack vector (credential compromise, session hijacking, privilege escalation, etc.).
3. Determine if any data was exfiltrated, modified, or deleted.
4. Document findings in an incident report.

#### 4.5.4 Remediation

1. Rotate all potentially compromised credentials.
2. Patch the vulnerability or close the attack vector.
3. Review and tighten access controls as needed.
4. Conduct a targeted access review of similarly situated accounts.
5. Update this SOP if a process gap contributed to the incident.

#### 4.5.5 Notification

Per certification requirements:
| Certification | Notification Requirement |
|--------------|-------------------------|
| HIPAA | 60 days for breaches affecting PHI |
| GDPR | 72 hours to supervisory authority |
| PCI DSS | Immediate to acquiring bank and card brands |
| FedRAMP | Within 1 hour to US-CERT for significant incidents |
| CMMC | 72 hours to DoD |

See SOP-005 for full notification procedures.

---

## 5. Records

The following records are generated and maintained under this SOP:

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| Access Request Forms | System Administrator | 10 years | IAM system |
| Account provisioning/deprovisioning records | System Administrator | 10 years | IAM system + audit trail |
| Quarterly Access Review reports | Compliance Officer | 5 years | Compliance repository |
| MFA enrollment records | Security Engineer | Lifetime of account + 2 years | IAM system |
| Service account inventory | Security Engineer | Current + 3 years historical | IAM system |
| Unauthorized access investigation records | Security Engineer | 7 years | Incident tracking system |
| Role assignment change records | System Administrator | 10 years | IAM system + audit trail |

---

## 6. References

- FDA 21 CFR Part 11 -- Subpart C (Electronic Signatures), Section 11.300 (Controls for Identification Codes/Passwords)
- HIPAA Security Rule -- 45 CFR 164.312 (Technical Safeguards: Access Control, Audit Controls, Integrity, Authentication, Transmission Security)
- AICPA TSC CC6.1-CC6.8 -- Logical and Physical Access Controls
- ISO/IEC 27001:2022 -- A.5.15 (Access Control), A.5.16 (Identity Management), A.5.17 (Authentication), A.5.18 (Access Rights), A.8.2-A.8.5 (Technology Controls)
- NIST SP 800-53 Rev. 5 -- AC (Access Control) and IA (Identification and Authentication) Control Families
- NIST SP 800-63B -- Digital Identity Guidelines: Authentication and Lifecycle Management
- PCI DSS v4.0.1 -- Requirements 7 (Restrict Access) and 8 (Identify Users and Authenticate)
- SOX ITGC -- Access Control and Segregation of Duties
- GDPR Article 32 -- Security of Processing
- FedRAMP Access Control (AC) and Identification and Authentication (IA) Controls
- CMMC Level 2 -- Access Control (AC) and Identification and Authentication (IA) Domains
- SOP-001: Audit Trail Management
- SOP-002: Change Control
- SOP-005: Incident Response

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2026-02-24 | Security & Compliance Team | Initial release |
