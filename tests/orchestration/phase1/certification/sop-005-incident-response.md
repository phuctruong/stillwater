# SOP-005: Incident Response

**Document ID:** SOP-005
**Version:** 1.0.0
**Effective Date:** 2026-02-24
**Owner:** Security & Compliance Team
**Approved By:** [Pending Approval]
**Review Cycle:** Annual (or after any Critical incident)
**Related Documents:** compliance-matrix.md, SOP-001, SOP-002, SOP-003, SOP-004

---

## 1. Purpose

This Standard Operating Procedure establishes the requirements, procedures, and responsibilities for detecting, responding to, investigating, and recovering from security incidents affecting the Stillwater AI orchestration engine. It ensures that incidents are handled promptly, documented thoroughly, and reported to the appropriate authorities within the timeframes required by each applicable certification.

This SOP addresses incident response requirements for SOC 2 (CC7.3-CC7.5), ISO 27001 (A.5.24-A.5.28), HIPAA Breach Notification Rule (45 CFR 164.400-414), GDPR (Articles 33-34), EU AI Act (Article 62), FedRAMP (IR control family), PCI DSS (Requirements 10, 12.10), CMMC (IR domain), and FDA 21 CFR Part 11 (system integrity).

---

## 2. Scope

This procedure applies to:
- All security events and incidents affecting systems within the Stillwater compliance boundary
- All data breaches involving personal data, protected health information, cardholder data, or controlled unclassified information
- All AI system malfunctions, safety incidents, or adversarial attacks
- All incidents affecting the integrity of audit trails or electronic records
- All environments: production, staging, and disaster recovery

This procedure does NOT apply to:
- Planned maintenance activities (governed by SOP-002)
- Non-security operational issues (e.g., performance degradation without security implications)
- Development environment incidents with no data exposure

---

## 3. Responsibilities

| Role | Responsibility |
|------|---------------|
| **Incident Commander (IC)** | Leads incident response; coordinates all activities; makes containment decisions; owns the incident until closure |
| **Security Engineer** | Primary responder for detection, triage, and technical investigation; implements containment and remediation actions |
| **Compliance Officer** | Determines notification obligations per certification requirements; coordinates external notifications; ensures regulatory compliance |
| **AI Lead** | Leads investigation for AI-specific incidents (model attacks, poisoning, bias incidents); coordinates with SOP-004 for model response |
| **System Administrator** | Executes infrastructure containment (network isolation, server lockdown); provides system logs and forensic data |
| **Legal Counsel** | Advises on legal obligations, notification requirements, and liability; reviews external communications |
| **Communications Lead** | Drafts external notifications (customer, regulatory, public); coordinates with Legal Counsel |
| **Development Team** | Develops and deploys patches for vulnerabilities; supports forensic analysis of application-layer incidents |
| **Executive Sponsor** | Authorizes significant business decisions during incidents (service shutdown, public disclosure); receives regular status updates |

### 3.1 Incident Response Team (IRT) Composition

The IRT is activated based on incident severity:

| Severity | IRT Members |
|----------|-------------|
| Low | Security Engineer + relevant System Administrator |
| Medium | Security Engineer + System Administrator + AI Lead (if AI-related) |
| High | All of Medium + Incident Commander + Compliance Officer |
| Critical | Full IRT: all roles above + Legal Counsel + Communications Lead + Executive Sponsor |

---

## 4. Procedures

### 4.1 Incident Classification

#### 4.1.1 Severity Levels

| Severity | Definition | Examples | Response Time |
|----------|------------|----------|---------------|
| **Critical** | Active exploitation or data breach with confirmed data exfiltration; service-wide outage; audit trail integrity compromised; high-risk AI safety incident | Active attacker with data access; ransomware execution; hash chain broken in production; AI model producing harmful outputs at scale | Immediate (< 15 minutes to begin response) |
| **High** | Probable security breach without confirmed exfiltration; significant service degradation; attempted exploitation of critical vulnerability; AI model integrity concern | Unauthorized access detected but scope unknown; critical CVE exploitable in production; model drift indicating possible data poisoning; electronic signature system failure | < 1 hour |
| **Medium** | Security event with limited impact; vulnerability discovered but not yet exploited; policy violation; AI performance anomaly | Failed brute-force attack blocked; medium-severity vulnerability in non-critical component; unauthorized configuration change detected; model accuracy degradation | < 4 hours |
| **Low** | Security event with minimal impact; informational alert; policy reminder needed | Single failed login from unusual location; minor policy deviation; outdated dependency with low-severity CVE; false positive from security tool | Next business day |

#### 4.1.2 Incident Categories

| Category | Description | Primary Responder |
|----------|-------------|-------------------|
| **Unauthorized Access** | Unauthorized login, privilege escalation, or access to restricted data | Security Engineer |
| **Data Breach** | Confirmed or suspected exposure of protected data (PII, PHI, CHD, CUI) | Security Engineer + Compliance Officer |
| **Malware/Ransomware** | Malicious software detected on any system in scope | Security Engineer + System Administrator |
| **Denial of Service** | Attack causing service unavailability or significant degradation | System Administrator + Security Engineer |
| **AI Safety Incident** | Model producing harmful, biased, or unsafe outputs; adversarial attack on model | AI Lead + Security Engineer |
| **Audit Trail Integrity** | Hash chain break, unauthorized audit log modification, or logging failure | Security Engineer + Compliance Officer |
| **Electronic Signature Compromise** | Unauthorized use of electronic signatures, signature system failure | Security Engineer + Compliance Officer |
| **Insider Threat** | Malicious or negligent action by authorized user | Security Engineer + HR + Legal Counsel |
| **Supply Chain** | Compromise of a third-party vendor, library, or service | Security Engineer + Development Team |
| **Physical Security** | Unauthorized physical access to systems or facilities | System Administrator + Security Engineer |

### 4.2 Detection and Reporting Procedures

#### 4.2.1 Automated Detection

| Detection Source | Monitored Events | Alert Mechanism |
|-----------------|-----------------|----------------|
| SIEM | Correlation rules for known attack patterns; anomaly detection | Real-time alert to Security Engineer on-call |
| Intrusion Detection System (IDS/IPS) | Network-level attack signatures; anomalous traffic patterns | Real-time alert + automatic blocking for known signatures |
| Audit Trail Integrity Monitor | Hash chain verification failures; unexpected audit entry patterns | Immediate alert to Security Engineer + Compliance Officer |
| Model Monitoring System | Performance drift, adversarial input detection, output anomalies | Alert per SOP-004 monitoring thresholds |
| Vulnerability Scanner | New vulnerabilities in deployed components | Daily scan results to Security Engineer |
| Endpoint Detection and Response (EDR) | Malicious process execution, file integrity changes | Real-time alert to Security Engineer |
| Cloud Security Posture Management (CSPM) | Misconfiguration, policy violations, excessive permissions | Real-time alert to Security Engineer |

#### 4.2.2 Manual Reporting

Any team member who suspects a security incident MUST report it immediately:

1. **Internal reporting channel:** Security incident Slack channel (#security-incidents) or email (security@stillwater.ai)
2. **Required information:**
   - Reporter name and contact
   - Date and time of observation
   - Description of what was observed
   - Systems, data, or users potentially affected
   - Any actions already taken
3. **Do NOT attempt to investigate or remediate independently** unless you are the on-call Security Engineer.

### 4.3 Escalation Matrix

| Elapsed Time | Severity: Low | Severity: Medium | Severity: High | Severity: Critical |
|-------------|---------------|-----------------|----------------|-------------------|
| 0 min | Security Engineer notified | Security Engineer notified | IRT (High) activated | Full IRT activated |
| 15 min | -- | -- | IC assigned; containment begins | IC assigned; containment begins; Executive Sponsor notified |
| 1 hour | -- | IC assigned if unresolved | Status update to Executive Sponsor | First status report to Executive Sponsor; Legal Counsel engaged |
| 4 hours | IC assigned if unresolved | Status update to management | Compliance Officer assesses notification obligations | External notification assessment begins |
| 24 hours | Resolution or escalation to Medium | Resolution or escalation to High | Post-containment review; notification if required | Notifications issued per Section 4.7; ongoing status updates every 4 hours |

### 4.4 Containment Procedures

#### 4.4.1 Immediate Containment (First 15 Minutes)

Prioritized by severity and category:

| Action | When | Authorized By |
|--------|------|---------------|
| Disable compromised user account(s) | Unauthorized access confirmed | Security Engineer |
| Isolate affected system from network | Active exploitation or malware confirmed | Security Engineer or System Administrator |
| Block attacking IP addresses/ranges | Attack source identified | Security Engineer (automated for known-bad) |
| Revoke compromised API keys/tokens | Credential compromise confirmed | Security Engineer |
| Disable affected AI model endpoint | AI safety incident confirmed | AI Lead or Security Engineer |
| Freeze audit trail segment | Audit integrity compromised | Security Engineer + Compliance Officer |
| Enable enhanced logging on affected systems | Any High/Critical incident | Security Engineer |

#### 4.4.2 Short-Term Containment (First 4 Hours)

| Action | When | Authorized By |
|--------|------|---------------|
| Deploy temporary network segmentation | Lateral movement suspected | Incident Commander |
| Rotate all credentials for affected systems | Scope of credential compromise unclear | Incident Commander |
| Deploy temporary WAF rules | Web application attack vector | Security Engineer |
| Switch to backup systems | Primary systems compromised | Incident Commander |
| Rollback model to previous version | Model integrity compromised | AI Lead per SOP-004 |
| Preserve forensic images of affected systems | Any High/Critical incident | Security Engineer |

#### 4.4.3 Long-Term Containment

| Action | When | Authorized By |
|--------|------|---------------|
| Rebuild affected systems from clean images | System integrity cannot be verified | Incident Commander + Executive Sponsor |
| Implement permanent network changes | Attack vector requires architectural change | Incident Commander per SOP-002 |
| Retrain model on verified clean data | Data poisoning confirmed | AI Lead per SOP-004 |
| Engage third-party forensics firm | Complex incident exceeding internal capabilities | Executive Sponsor |

### 4.5 Investigation and Root Cause Analysis

#### 4.5.1 Evidence Collection

All evidence MUST be collected following forensic best practices:

1. **Preserve original evidence:** Create forensic copies; never analyze originals.
2. **Chain of custody:** Document who handled evidence, when, and what actions were taken.
3. **Evidence types to collect:**
   - Audit trail entries (Part11AuditEntry records) for the incident timeframe
   - System logs (application, OS, network, cloud provider)
   - Network traffic captures (if available)
   - Memory dumps (for malware analysis)
   - Model inference logs (for AI incidents)
   - User session records
   - Configuration snapshots (before and after incident)

#### 4.5.2 Root Cause Analysis (RCA)

The Incident Commander ensures an RCA is conducted for all Medium, High, and Critical incidents:

1. **Timeline reconstruction:** Build a minute-by-minute timeline of the incident using evidence.
2. **Attack vector identification:** Determine how the attacker gained access or how the failure occurred.
3. **Impact assessment:** Quantify the impact (data records affected, users impacted, systems compromised, duration).
4. **Contributing factors:** Identify systemic issues (process gaps, missing controls, configuration errors).
5. **Root cause determination:** Use the "5 Whys" or fishbone diagram methodology to identify the root cause.

#### 4.5.3 Documentation

The RCA report MUST include:

| Section | Contents |
|---------|----------|
| Executive summary | One-paragraph summary of the incident, impact, and resolution |
| Incident timeline | Chronological record of events from detection through resolution |
| Root cause | Identified root cause with supporting evidence |
| Impact assessment | Data, systems, users, and certifications affected; business impact |
| Containment actions | Actions taken to contain the incident with timestamps |
| Remediation actions | Steps taken to eliminate the root cause |
| Evidence inventory | List of all evidence collected with chain of custody |
| Lessons learned | What went well, what could be improved |

### 4.6 Corrective and Preventive Actions (CAPA)

#### 4.6.1 CAPA Process

For all Medium, High, and Critical incidents:

1. **Identify corrective actions:** Actions to fix the specific issue that caused this incident.
2. **Identify preventive actions:** Actions to prevent similar incidents in the future.
3. **Assign owners and deadlines:** Each CAPA item has a named owner and target completion date.
4. **Track to completion:** CAPA items tracked in the incident management system until closed.
5. **Verify effectiveness:** After implementation, verify the CAPA is effective (re-test, re-scan, or re-audit).
6. **Update SOPs:** If the incident revealed a process gap, update the relevant SOP(s) per SOP-002.

#### 4.6.2 CAPA Timelines

| Severity | Corrective Action Deadline | Preventive Action Deadline | Verification Deadline |
|----------|---------------------------|---------------------------|----------------------|
| Critical | 72 hours | 30 days | 60 days |
| High | 7 days | 60 days | 90 days |
| Medium | 30 days | 90 days | 120 days |
| Low | 90 days | Best effort | Best effort |

### 4.7 Notification Requirements

#### 4.7.1 Notification Matrix by Certification

| Certification | Notification Recipient | Notification Deadline | Trigger Condition | Content Requirements |
|--------------|----------------------|----------------------|-------------------|---------------------|
| **HIPAA** | HHS (OCR) via breach portal; affected individuals | 60 days from discovery; without unreasonable delay to individuals | Breach of unsecured PHI affecting 500+ individuals (immediate to HHS); < 500 individuals (annual log to HHS) | Nature of breach; types of information involved; steps individuals should take; what covered entity is doing; contact information |
| **GDPR** | Supervisory authority (lead DPA); affected data subjects | 72 hours to supervisory authority from awareness; without undue delay to data subjects if high risk | Personal data breach likely to result in risk to rights and freedoms | Nature of breach; categories and approximate number of data subjects; likely consequences; measures taken/proposed |
| **EU AI Act** | Market surveillance authority | Without undue delay after becoming aware; serious incidents within 15 days | Serious incident or malfunction of high-risk AI system that constitutes a serious incident per Article 62 | Description of incident; AI system identification; corrective measures taken; impact assessment |
| **FedRAMP** | US-CERT; authorizing official | 1 hour for significant incidents (US-CERT); same day (authorizing official) | Any incident affecting the confidentiality, integrity, or availability of the FedRAMP-authorized system | Per US-CERT reporting guidelines; incident category, impact, affected systems |
| **PCI DSS** | Acquiring bank; affected card brands | Immediately upon discovery | Compromise of cardholder data or cardholder data environment | Per card brand incident response procedures |
| **CMMC** | DoD CIO via DIBNet | 72 hours from discovery | Cyber incident affecting covered contractor information systems or CUI | Per DFARS 252.204-7012 reporting requirements |
| **SOC 2** | No external notification required by SOC 2 itself | N/A (report to auditor at next examination) | Document per Trust Services Criteria | Include in management assertion for SOC 2 report |
| **ISO 27001** | No mandatory external notification (unless other regulations apply) | Per ISMS incident management procedure | Per risk assessment | Per ISMS documentation requirements |
| **CCPA/CPRA** | California Attorney General (if 500+ CA residents); affected consumers | Expeditiously; without unreasonable delay | Breach of unencrypted personal information of California residents | Nature of breach; types of information; steps consumers should take; entity contact information |
| **SOX** | Audit committee; external auditor | Promptly | Material weakness in ICFR related to IT systems | Per management assessment and auditor communication requirements |
| **GLBA** | Federal regulator (FTC, OCC, etc.); affected customers | As soon as possible | Unauthorized access to customer financial information | Per Safeguards Rule notification requirements |
| **PIPEDA** | OPC; affected individuals | As soon as feasible after determination that breach occurred | Real risk of significant harm to individuals | Description of breach; information involved; steps taken; risk reduction measures |
| **LGPD** | ANPD; affected data subjects | Reasonable time (ANPD has authority to define specific deadline) | Security incident involving personal data | Nature of data affected; information about data subjects; measures taken |

#### 4.7.2 Internal Notification

| Stakeholder | Notification Trigger | Method | Timeline |
|-------------|---------------------|--------|----------|
| Executive Sponsor | All High and Critical incidents | Phone + email | Within 15 minutes (Critical); within 1 hour (High) |
| Compliance Officer | All incidents with regulatory implications | Email + incident system | Within 30 minutes of classification |
| Legal Counsel | All High and Critical incidents; any potential data breach | Phone + email | Within 1 hour |
| Affected team managers | All incidents affecting their systems or team members | Email + incident system | Within 4 hours |
| All staff (awareness) | Critical incidents with org-wide impact | Internal communication channel | Within 24 hours (after containment) |

#### 4.7.3 Customer Notification

When an incident affects customer data or services:

1. Legal Counsel and Communications Lead draft the notification.
2. Compliance Officer reviews for regulatory compliance.
3. Executive Sponsor approves before distribution.
4. Notification includes: description of incident, data affected, actions taken, customer remediation steps, contact information.
5. Notification sent via appropriate channel (email, in-app notification, postal mail as required).
6. Customer notification records retained as part of the incident record.

### 4.8 Post-Incident Review

#### 4.8.1 Post-Incident Review Meeting

A post-incident review (PIR) meeting is held for all Medium, High, and Critical incidents:

| Timing | Severity |
|--------|----------|
| Within 5 business days of incident closure | Critical |
| Within 10 business days of incident closure | High |
| Within 20 business days of incident closure | Medium |

#### 4.8.2 PIR Agenda

1. Incident timeline walkthrough
2. Root cause analysis review
3. Effectiveness of detection and response
4. Communication effectiveness (internal and external)
5. CAPA review and prioritization
6. SOP and process improvement recommendations
7. Lessons learned documentation
8. Action item assignment with owners and deadlines

#### 4.8.3 PIR Outputs

- Updated RCA report (if additional findings from the review)
- CAPA items (new or refined)
- SOP change requests (if process gaps identified)
- Lessons learned document (distributed to all relevant teams)
- Updated runbooks or playbooks (if response procedures need refinement)

---

## 5. Records

The following records are generated and maintained under this SOP:

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| Incident reports (all severities) | Incident Commander | 10 years | Incident management system |
| Root Cause Analysis reports | Incident Commander | 10 years | Incident management system |
| CAPA records | CAPA owner (tracked by Compliance Officer) | 10 years | Incident management system |
| Forensic evidence and chain of custody | Security Engineer | 10 years (or as required by legal hold) | Secure forensic evidence store |
| External notification records | Compliance Officer | 10 years | Compliance repository |
| Customer notification records | Communications Lead | 10 years | Compliance repository |
| Post-Incident Review minutes | Incident Commander | 5 years | Incident management system |
| Lessons learned documents | Security Engineer | 5 years | Knowledge base |
| Incident metrics and trend reports | Security Engineer | 5 years | Analytics repository |

---

## 6. References

- AICPA TSC CC7.3 (Detection), CC7.4 (Response), CC7.5 (Recovery)
- ISO/IEC 27001:2022 -- A.5.24 (Information Security Incident Management Planning), A.5.25 (Assessment and Decision), A.5.26 (Response), A.5.27 (Learning from Incidents), A.5.28 (Collection of Evidence)
- HIPAA Breach Notification Rule -- 45 CFR 164.400-414
- GDPR Articles 33 (Notification to Supervisory Authority) and 34 (Communication to Data Subject)
- EU AI Act Article 62 (Reporting of Serious Incidents)
- NIST SP 800-53 Rev. 5 -- IR Control Family (IR-1 through IR-10)
- NIST SP 800-61 Rev. 2 -- Computer Security Incident Handling Guide
- FedRAMP Incident Communications Procedures
- PCI DSS v4.0.1 -- Requirement 12.10 (Incident Response Plan)
- CMMC Level 2 -- Incident Response (IR) Domain
- DFARS 252.204-7012 -- Safeguarding Covered Defense Information and Cyber Incident Reporting
- CCPA/CPRA -- California Civil Code Section 1798.82 (Breach Notification)
- SOP-001: Audit Trail Management
- SOP-002: Change Control
- SOP-003: Access Control
- SOP-004: Model Version Control
- compliance-matrix.md

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2026-02-24 | Security & Compliance Team | Initial release |
