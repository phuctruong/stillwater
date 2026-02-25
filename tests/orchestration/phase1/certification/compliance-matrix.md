# Compliance Matrix -- Stillwater AI Orchestration Engine

**Document ID:** CM-001
**Version:** 1.0.0
**Effective Date:** 2026-02-24
**Owner:** Security & Compliance Team
**Review Cycle:** Quarterly
**Related Documents:** SOP-001 through SOP-005, audit-entry-schema.json

---

## Overview

This compliance matrix tracks all security and regulatory certifications relevant to the Stillwater AI orchestration engine. Each certification is prioritized by business urgency and mapped to specific technical requirements, audit trail obligations, cost estimates, and timelines.

**Priority Definitions:**

| Priority | Meaning | Target Window |
|----------|---------|---------------|
| P0 | Immediate -- required for launch or legal compliance | Current quarter |
| P1 | Next quarter -- required for key market segments | Next quarter |
| P2 | This year -- competitive advantage or market expansion | Within 12 months |
| P3 | Future -- strategic positioning or emerging requirements | 12+ months |

**Status Definitions:**

| Status | Meaning |
|--------|---------|
| NOT_STARTED | No work has begun |
| IN_PROGRESS | Active work underway; gap analysis or remediation in flight |
| COMPLIANT | All controls implemented; awaiting or scheduling formal audit |
| CERTIFIED | Third-party audit passed; certificate issued |

---

## P0 -- Immediate

### SOC 2 Type II

| Field | Value |
|-------|-------|
| **Full Name** | Service Organization Control 2 Type II |
| **Governing Body** | American Institute of Certified Public Accountants (AICPA) |
| **Priority** | P0 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | Yes -- licensed CPA firm |
| **Estimated Cost** | $30,000 -- $80,000 (initial audit); $20,000 -- $50,000 (annual renewal) |
| **Estimated Timeline** | 6--9 months (readiness + Type I + observation period + Type II) |

**Key Requirements:**
- Implement and document controls across all five Trust Services Criteria (Security, Availability, Processing Integrity, Confidentiality, Privacy)
- Maintain continuous monitoring over a minimum 6-month observation period for Type II
- Produce a System Description document covering infrastructure, software, people, procedures, and data
- Demonstrate formal risk assessment process with documented mitigation plans
- Implement vendor management program for all sub-processors

**Audit Trail Requirements:**
- All system access events logged with timestamps, user identity, and action performed (see SOP-001)
- Change management records for every production deployment (see SOP-002)
- Evidence of periodic access reviews (quarterly minimum) (see SOP-003)
- Incident response records with root cause analysis and remediation proof (see SOP-005)
- Retention: minimum 12 months; recommended 3 years for re-audit continuity

---

### ISO/IEC 42001

| Field | Value |
|-------|-------|
| **Full Name** | ISO/IEC 42001:2023 -- Artificial Intelligence Management System (AIMS) |
| **Governing Body** | International Organization for Standardization (ISO) / International Electrotechnical Commission (IEC) |
| **Priority** | P0 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | Yes -- accredited ISO certification body |
| **Estimated Cost** | $40,000 -- $100,000 (initial certification); $15,000 -- $30,000 (annual surveillance) |
| **Estimated Timeline** | 6--12 months (AIMS establishment + Stage 1 + Stage 2 audit) |

**Key Requirements:**
- Establish an AI Management System (AIMS) with defined scope, policy, and objectives
- Conduct AI-specific risk assessments covering bias, fairness, transparency, and accountability
- Implement AI impact assessments for all deployed models (see SOP-004)
- Document AI lifecycle governance: design, development, deployment, monitoring, decommission
- Maintain records of AI system behavior, decisions, and performance metrics

**Audit Trail Requirements:**
- Full model version history with rationale for every change (see SOP-004)
- AI decision logs: input features, model version, output, confidence score, timestamp
- Impact assessment records for each model deployment or significant parameter change
- Training data provenance and lineage documentation
- Performance monitoring dashboards with drift detection alerts and response records
- Retention: minimum 3 years; recommended lifetime of the AI system

---

### EU AI Act

| Field | Value |
|-------|-------|
| **Full Name** | Regulation (EU) 2024/1689 -- Artificial Intelligence Act |
| **Governing Body** | European Parliament and Council of the European Union |
| **Priority** | P0 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | Yes -- for high-risk AI systems (notified body conformity assessment) |
| **Estimated Cost** | $50,000 -- $150,000 (conformity assessment + legal review); ongoing compliance costs variable |
| **Estimated Timeline** | 6--12 months (risk classification + conformity assessment preparation); legal deadline August 2026 |

**Key Requirements:**
- Classify all AI components by risk tier (unacceptable, high, limited, minimal) per Annex III
- For high-risk systems: implement risk management system, data governance, technical documentation, record-keeping, transparency, human oversight, accuracy/robustness/cybersecurity
- Register high-risk AI systems in the EU database before market placement
- Implement transparency obligations: users must be informed they are interacting with AI
- Designate an authorized representative in the EU if operating from outside the EU

**Audit Trail Requirements:**
- Automatic logging of all AI system operations for the lifetime of the system (Article 12)
- Logs must enable traceability of AI system behavior and identification of risk situations
- Technical documentation must be kept up-to-date and available to competent authorities
- Records of conformity assessments, declarations of conformity, and CE marking
- Incident reports for serious incidents or malfunctions within 15 days to market surveillance authority
- Retention: minimum 10 years from market placement for high-risk systems

---

## P1 -- Next Quarter

### ISO 27001

| Field | Value |
|-------|-------|
| **Full Name** | ISO/IEC 27001:2022 -- Information Security Management System (ISMS) |
| **Governing Body** | ISO / IEC |
| **Priority** | P1 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | Yes -- accredited ISO certification body |
| **Estimated Cost** | $25,000 -- $60,000 (initial certification); $10,000 -- $25,000 (annual surveillance) |
| **Estimated Timeline** | 6--12 months |

**Key Requirements:**
- Establish ISMS with defined scope, information security policy, and risk treatment plan
- Conduct formal risk assessment using a recognized methodology (e.g., ISO 27005)
- Implement controls from Annex A (93 controls across 4 themes: organizational, people, physical, technological)
- Conduct internal audits and management reviews at planned intervals
- Demonstrate continual improvement through corrective action and risk reassessment

**Audit Trail Requirements:**
- Risk assessment and treatment records with version history
- Access control logs covering all information assets in scope (see SOP-003)
- Change management records for all ISMS-scoped systems (see SOP-002)
- Internal audit reports and management review minutes
- Retention: minimum 3 years; aligned with risk assessment cycle

---

### HIPAA

| Field | Value |
|-------|-------|
| **Full Name** | Health Insurance Portability and Accountability Act of 1996 (Privacy Rule, Security Rule, Breach Notification Rule) |
| **Governing Body** | U.S. Department of Health and Human Services (HHS), Office for Civil Rights (OCR) |
| **Priority** | P1 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | No (self-attestation), but third-party assessment strongly recommended |
| **Estimated Cost** | $20,000 -- $50,000 (gap assessment + remediation); ongoing compliance costs variable |
| **Estimated Timeline** | 3--6 months (gap analysis + remediation) |

**Key Requirements:**
- Implement Administrative, Physical, and Technical Safeguards per the Security Rule (45 CFR 164.308-312)
- Execute Business Associate Agreements (BAAs) with all vendors handling PHI
- Conduct annual risk analysis (required, not optional) per 45 CFR 164.308(a)(1)
- Implement minimum necessary standard for PHI access and disclosure
- Establish breach notification procedures (individual notice within 60 days; HHS notification)

**Audit Trail Requirements:**
- All access to Protected Health Information (PHI) logged with user, timestamp, action, and data accessed
- Authentication and session logs for all systems containing PHI (see SOP-003)
- Audit logs must be tamper-evident; hash chain integrity verification required (see SOP-001)
- Breach investigation records with timeline, scope, and notification evidence (see SOP-005)
- Retention: minimum 6 years from date of creation or last effective date

---

### HITRUST r2

| Field | Value |
|-------|-------|
| **Full Name** | HITRUST CSF r2 Validated Assessment |
| **Governing Body** | HITRUST Alliance |
| **Priority** | P1 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | Yes -- HITRUST Authorized External Assessor |
| **Estimated Cost** | $80,000 -- $200,000 (r2 validated assessment); $40,000 -- $80,000 (annual interim assessment) |
| **Estimated Timeline** | 9--18 months (readiness + validated assessment + HITRUST QA review) |

**Key Requirements:**
- Implement controls mapped across 14 control categories covering 19 domains
- Demonstrate maturity across five levels: Policy, Procedure, Implemented, Measured, Managed
- Provide evidence of control operation over a minimum 90-day period (r2 validated)
- Complete MyCSF assessment with all applicable requirement statements scored
- Address all corrective action plans (CAPs) before certification issuance

**Audit Trail Requirements:**
- All control evidence must be dated, attributed, and retained in the MyCSF portal
- Continuous monitoring evidence for key controls (access, change, incident)
- Risk assessment documentation with linkage to HITRUST control requirements
- Third-party risk management records for all in-scope service providers
- Retention: minimum 3 years; HITRUST retains certification records for 2 years post-expiry

---

### FedRAMP Moderate

| Field | Value |
|-------|-------|
| **Full Name** | Federal Risk and Authorization Management Program -- Moderate Impact Level |
| **Governing Body** | U.S. General Services Administration (GSA), Joint Authorization Board (JAB) / Agency ATO |
| **Priority** | P1 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | Yes -- FedRAMP-accredited Third Party Assessment Organization (3PAO) |
| **Estimated Cost** | $250,000 -- $750,000 (initial authorization); $100,000 -- $200,000 (annual continuous monitoring) |
| **Estimated Timeline** | 12--18 months (readiness + 3PAO assessment + JAB/Agency review) |

**Key Requirements:**
- Implement all 325 NIST SP 800-53 Rev. 5 controls at Moderate baseline
- Deploy in a FedRAMP-authorized cloud infrastructure (AWS GovCloud, Azure Government, etc.)
- Prepare System Security Plan (SSP), Security Assessment Report (SAR), and Plan of Action & Milestones (POA&M)
- Implement continuous monitoring per FedRAMP ConMon requirements (monthly vulnerability scans, annual penetration testing)
- Maintain FIPS 140-2/3 validated cryptographic modules for data at rest and in transit

**Audit Trail Requirements:**
- Comprehensive audit logging per AU control family (AU-1 through AU-16)
- Centralized log aggregation with tamper-evident storage (SIEM required)
- Real-time alerting for security-relevant events per AU-5
- Monthly vulnerability scan reports and annual penetration test results
- POA&M tracking with remediation timelines and closure evidence
- Retention: minimum 3 years for audit logs; POA&M records retained for system lifecycle

---

### FDA 21 CFR Part 11

| Field | Value |
|-------|-------|
| **Full Name** | Title 21 Code of Federal Regulations Part 11 -- Electronic Records; Electronic Signatures |
| **Governing Body** | U.S. Food and Drug Administration (FDA) |
| **Priority** | P1 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | No (FDA inspection-based), but third-party pre-audit recommended |
| **Estimated Cost** | $30,000 -- $80,000 (gap assessment + system remediation); ongoing compliance embedded in development |
| **Estimated Timeline** | 3--6 months (gap analysis + remediation + validation) |

**Key Requirements:**
- Implement closed system controls: validated systems, audit trails, operational checks, authority checks, device checks
- Electronic signatures must be unique, linked to electronic records, and include printed name, date/time, and meaning
- Audit trails must be computer-generated, timestamped, and capture who, what, when, and why for record changes
- System validation per GAMP 5 methodology (or equivalent) with Installation/Operational/Performance Qualification
- Implement controls to prevent unauthorized use of electronic signatures (two-factor authentication required for signing)

**Audit Trail Requirements:**
- Computer-generated, time-stamped audit trail for every create, modify, or delete action on electronic records
- Audit trail entries must include: operator identity, timestamp, old value, new value, and reason for change
- Audit trail must be independent of the operator (cannot be modified by the record creator)
- Part11AuditEntry schema (see audit-entry-schema.json) must capture all required fields
- Audit trails must be available for FDA inspection and copying for the retention period
- Retention: minimum 7 years or as defined by the applicable predicate rule (whichever is longer)

---

## P2 -- This Year

### CMMC Level 2

| Field | Value |
|-------|-------|
| **Full Name** | Cybersecurity Maturity Model Certification Level 2 (Advanced) |
| **Governing Body** | U.S. Department of Defense (DoD), Cyber AB (Accreditation Body) |
| **Priority** | P2 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | Yes -- CMMC Third-Party Assessment Organization (C3PAO) |
| **Estimated Cost** | $50,000 -- $150,000 (assessment); $30,000 -- $60,000 (annual reassessment) |
| **Estimated Timeline** | 6--12 months |

**Key Requirements:**
- Implement all 110 practices from NIST SP 800-171 Rev. 2 across 14 domains
- Protect Controlled Unclassified Information (CUI) in non-federal systems
- Prepare System Security Plan (SSP) and Plan of Action & Milestones (POA&M)
- Implement FIPS-validated cryptography for CUI at rest and in transit
- Establish incident reporting to DoD within 72 hours of discovery

**Audit Trail Requirements:**
- Audit logging for all CUI-scoped systems per NIST 800-171 family 3.3
- Log review and analysis at defined intervals (weekly minimum recommended)
- Protection of audit information from unauthorized access, modification, and deletion
- Correlation of audit records across system components
- Retention: minimum 3 years; aligned with contract requirements

---

### PCI DSS

| Field | Value |
|-------|-------|
| **Full Name** | Payment Card Industry Data Security Standard v4.0.1 |
| **Governing Body** | PCI Security Standards Council |
| **Priority** | P2 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | Yes -- Qualified Security Assessor (QSA) for Level 1; SAQ for lower levels |
| **Estimated Cost** | $50,000 -- $200,000 (Level 1 QSA assessment); $15,000 -- $40,000 (annual) |
| **Estimated Timeline** | 6--12 months |

**Key Requirements:**
- Implement all 12 high-level requirements across 6 control objectives
- Segment cardholder data environment (CDE) from general network
- Encrypt cardholder data at rest (AES-256) and in transit (TLS 1.2+)
- Implement strong access control with least privilege and need-to-know
- Conduct quarterly vulnerability scans (ASV) and annual penetration tests

**Audit Trail Requirements:**
- Log all access to cardholder data and all actions by privileged users
- Synchronize all system clocks to a reliable time source (NTP)
- Secure audit trails so they cannot be altered (write-once storage or integrity checking)
- Review logs daily using automated mechanisms (SIEM)
- Retain audit trail history for at least 12 months; 3 months immediately available
- Retention: minimum 12 months

---

### GDPR

| Field | Value |
|-------|-------|
| **Full Name** | General Data Protection Regulation (EU) 2016/679 |
| **Governing Body** | European Data Protection Board (EDPB) and national Data Protection Authorities (DPAs) |
| **Priority** | P2 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | No (self-compliance), but Data Protection Impact Assessments (DPIAs) required for high-risk processing |
| **Estimated Cost** | $30,000 -- $100,000 (DPIA + legal review + implementation); DPO costs variable |
| **Estimated Timeline** | 3--6 months (initial compliance); ongoing obligation |

**Key Requirements:**
- Establish lawful basis for processing personal data (consent, contract, legitimate interest, etc.)
- Implement data subject rights: access, rectification, erasure, portability, restriction, objection
- Appoint Data Protection Officer (DPO) if required by Article 37
- Conduct Data Protection Impact Assessments (DPIAs) for high-risk processing activities
- Implement data protection by design and by default (Article 25)

**Audit Trail Requirements:**
- Record of processing activities (ROPA) per Article 30
- Consent records with timestamp, scope, and withdrawal mechanism
- Data subject request logs with response timelines (30-day deadline tracking)
- Data breach notification records (72-hour notification to supervisory authority) (see SOP-005)
- Data transfer impact assessments for international transfers (Schrems II compliance)
- Retention: retain processing records for the duration of processing; breach records for minimum 5 years

---

### CCPA/CPRA

| Field | Value |
|-------|-------|
| **Full Name** | California Consumer Privacy Act / California Privacy Rights Act |
| **Governing Body** | California Privacy Protection Agency (CPPA) |
| **Priority** | P2 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | No (self-compliance); annual cybersecurity audits may be required by CPPA regulations |
| **Estimated Cost** | $15,000 -- $50,000 (gap assessment + implementation) |
| **Estimated Timeline** | 2--4 months |

**Key Requirements:**
- Implement consumer rights: know, delete, opt-out of sale/sharing, correct, limit use of sensitive PI
- Provide "Do Not Sell or Share My Personal Information" mechanism
- Conduct cybersecurity audits (if processing meets thresholds defined by CPPA)
- Conduct risk assessments for processing that presents significant risk to consumer privacy
- Implement reasonable security procedures and practices

**Audit Trail Requirements:**
- Consumer request logs with timestamps, type, and response within 45 days
- Opt-out signal processing records (Global Privacy Control support)
- Service provider and contractor agreement records
- Risk assessment documentation
- Retention: minimum 24 months for consumer request records

---

### SOX

| Field | Value |
|-------|-------|
| **Full Name** | Sarbanes-Oxley Act of 2002 (Sections 302, 404) |
| **Governing Body** | U.S. Securities and Exchange Commission (SEC), Public Company Accounting Oversight Board (PCAOB) |
| **Priority** | P2 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | Yes -- registered public accounting firm for Section 404(b) |
| **Estimated Cost** | $100,000 -- $500,000 (initial; highly variable by company size) |
| **Estimated Timeline** | 6--12 months |

**Key Requirements:**
- Implement internal controls over financial reporting (ICFR)
- Document and test IT General Controls (ITGCs): access, change management, operations, SDLC
- Management assessment of ICFR effectiveness (Section 404(a))
- Segregation of duties for financially significant systems
- Entity-level controls including tone-at-the-top and fraud risk assessment

**Audit Trail Requirements:**
- All changes to financially significant systems logged and reviewed (see SOP-002)
- Access control logs for financial systems with periodic review (see SOP-003)
- Evidence of management testing and assessment of control effectiveness
- Deficiency tracking and remediation records
- Retention: minimum 7 years for audit workpapers; 5 years for financial records

---

## P3 -- Future

### NIST AI RMF

| Field | Value |
|-------|-------|
| **Full Name** | NIST Artificial Intelligence Risk Management Framework 1.0 |
| **Governing Body** | National Institute of Standards and Technology (NIST) |
| **Priority** | P3 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | No (voluntary framework; no formal certification) |
| **Estimated Cost** | $10,000 -- $30,000 (self-assessment and implementation) |
| **Estimated Timeline** | 3--6 months |

**Key Requirements:**
- Implement the four core functions: Govern, Map, Measure, Manage
- Establish AI risk governance structure and policies
- Map AI system contexts, capabilities, and limitations
- Measure AI risks using quantitative and qualitative methods
- Implement risk management and mitigation controls

**Audit Trail Requirements:**
- AI risk assessment records with versioning
- Governance meeting minutes and decision records
- Measurement methodology documentation and results
- Risk mitigation action tracking
- Retention: recommended 5 years; no formal requirement

---

### ISO 27017 / ISO 27018

| Field | Value |
|-------|-------|
| **Full Name** | ISO/IEC 27017:2015 (Cloud Security) / ISO/IEC 27018:2019 (PII in Cloud) |
| **Governing Body** | ISO / IEC |
| **Priority** | P3 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | Yes -- accredited ISO certification body (typically combined with ISO 27001 audit) |
| **Estimated Cost** | $15,000 -- $30,000 (incremental to ISO 27001) |
| **Estimated Timeline** | 3--6 months (incremental to existing ISO 27001) |

**Key Requirements:**
- ISO 27017: Implement cloud-specific controls for both cloud service providers and customers
- ISO 27017: Define shared responsibility model and document cloud-specific risk treatment
- ISO 27018: Implement consent mechanisms and purpose limitation for PII processing in cloud
- ISO 27018: Provide transparency about sub-processor locations and data handling
- Both require ISO 27001 as prerequisite

**Audit Trail Requirements:**
- Cloud resource provisioning and deprovisioning logs
- PII processing activity records with lawful basis
- Sub-processor audit records and SLA compliance evidence
- Data location and transfer records
- Retention: aligned with ISO 27001 (minimum 3 years)

---

### ISO 9001

| Field | Value |
|-------|-------|
| **Full Name** | ISO 9001:2015 -- Quality Management System (QMS) |
| **Governing Body** | ISO |
| **Priority** | P3 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | Yes -- accredited ISO certification body |
| **Estimated Cost** | $15,000 -- $40,000 (initial certification); $8,000 -- $15,000 (annual surveillance) |
| **Estimated Timeline** | 6--12 months |

**Key Requirements:**
- Establish QMS with quality policy, objectives, and documented processes
- Implement Plan-Do-Check-Act (PDCA) cycle across all processes
- Conduct customer satisfaction measurement and analysis
- Implement nonconformity management and corrective action process
- Conduct management reviews and internal audits at planned intervals

**Audit Trail Requirements:**
- Documented information (records) for all QMS processes
- Nonconformity and corrective action records
- Internal audit reports and management review minutes
- Customer complaint and feedback records
- Retention: defined by organization; minimum 3 years recommended

---

### StateRAMP / GovRAMP

| Field | Value |
|-------|-------|
| **Full Name** | StateRAMP (State Risk and Authorization Management Program) |
| **Governing Body** | StateRAMP Board of Directors |
| **Priority** | P3 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | Yes -- StateRAMP-approved 3PAO |
| **Estimated Cost** | $50,000 -- $150,000 (leverages FedRAMP work if available) |
| **Estimated Timeline** | 3--6 months (if FedRAMP baseline exists); 9--12 months standalone |

**Key Requirements:**
- Implement NIST SP 800-53 controls at the appropriate impact level
- Prepare Security Snapshot or full Security Assessment based on maturity level
- Submit to StateRAMP PMO for review and authorization
- Implement continuous monitoring aligned with StateRAMP requirements
- Annual reassessment by 3PAO

**Audit Trail Requirements:**
- Aligned with FedRAMP AU control family
- Continuous monitoring evidence per StateRAMP ConMon requirements
- Vulnerability scan and remediation records
- Retention: minimum 3 years

---

### ITAR

| Field | Value |
|-------|-------|
| **Full Name** | International Traffic in Arms Regulations |
| **Governing Body** | U.S. Department of State, Directorate of Defense Trade Controls (DDTC) |
| **Priority** | P3 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | No (registration and self-compliance), but violations carry criminal penalties |
| **Estimated Cost** | $50,000 -- $200,000 (compliance program establishment); DDTC registration fee ~$2,500/yr |
| **Estimated Timeline** | 6--12 months |

**Key Requirements:**
- Register with DDTC if manufacturing or exporting defense articles or services
- Implement Technology Control Plan (TCP) restricting access to ITAR-controlled data to U.S. persons only
- Ensure all cloud infrastructure for ITAR data is within U.S. borders with U.S.-person-only access
- Obtain export licenses or use exemptions for any foreign national access
- Implement end-to-end encryption for ITAR-controlled technical data

**Audit Trail Requirements:**
- Access logs restricted to U.S. persons only for ITAR-scoped systems
- Export license tracking and compliance records
- Technology transfer records and approvals
- Training records for all personnel with ITAR access
- Retention: minimum 5 years from date of export or transfer

---

### DoD IL4 / IL5

| Field | Value |
|-------|-------|
| **Full Name** | Department of Defense Cloud Computing Security Requirements Guide -- Impact Levels 4 and 5 |
| **Governing Body** | Defense Information Systems Agency (DISA) |
| **Priority** | P3 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | Yes -- DISA assessment + FedRAMP Moderate (IL4) or FedRAMP High (IL5) as baseline |
| **Estimated Cost** | $500,000 -- $1,500,000 (including infrastructure requirements) |
| **Estimated Timeline** | 18--24 months |

**Key Requirements:**
- IL4: FedRAMP Moderate baseline + DoD-specific controls for Controlled Unclassified Information (CUI)
- IL5: FedRAMP High baseline + physical separation requirements + U.S.-person-only access
- Deploy on DoD-authorized cloud infrastructure (AWS GovCloud, Azure Government, etc.)
- Implement STIG-compliant configurations for all system components
- Maintain Provisional Authorization (PA) through continuous monitoring

**Audit Trail Requirements:**
- All FedRAMP AU controls plus DoD-specific STIG requirements
- Security Information and Event Management (SIEM) with real-time correlation
- Privileged access monitoring with session recording
- Cross-domain solution logging (if applicable)
- Retention: minimum 5 years; aligned with DoD records management

---

### GLBA

| Field | Value |
|-------|-------|
| **Full Name** | Gramm-Leach-Bliley Act (Financial Services Modernization Act of 1999) |
| **Governing Body** | Federal Trade Commission (FTC), Federal banking regulators (OCC, FDIC, Federal Reserve) |
| **Priority** | P3 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | No (examination-based by federal regulators), but independent assessment recommended |
| **Estimated Cost** | $20,000 -- $60,000 (gap assessment + implementation) |
| **Estimated Timeline** | 3--6 months |

**Key Requirements:**
- Implement Safeguards Rule: designate qualified individual, conduct risk assessment, implement safeguards
- Develop written information security program
- Implement access controls, encryption, and multi-factor authentication for customer financial information
- Conduct periodic vulnerability assessments and penetration testing
- Establish service provider oversight program

**Audit Trail Requirements:**
- Access logs for all systems containing nonpublic personal information (NPI)
- Risk assessment and safeguard testing records
- Service provider due diligence and monitoring records
- Incident response records for security events involving NPI (see SOP-005)
- Retention: minimum 5 years

---

### PIPEDA

| Field | Value |
|-------|-------|
| **Full Name** | Personal Information Protection and Electronic Documents Act |
| **Governing Body** | Office of the Privacy Commissioner of Canada (OPC) |
| **Priority** | P3 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | No (complaint-based enforcement by OPC) |
| **Estimated Cost** | $10,000 -- $30,000 (gap assessment + implementation) |
| **Estimated Timeline** | 2--4 months |

**Key Requirements:**
- Implement 10 fair information principles (accountability, identifying purposes, consent, limiting collection, limiting use/disclosure/retention, accuracy, safeguards, openness, individual access, challenging compliance)
- Designate privacy officer accountable for compliance
- Obtain meaningful consent for collection, use, and disclosure of personal information
- Implement breach reporting to OPC and affected individuals for breaches creating real risk of significant harm
- Respond to individual access requests within 30 days

**Audit Trail Requirements:**
- Consent records and privacy policy version history
- Access request logs with response timelines
- Breach records including risk-of-harm assessment
- Cross-border data transfer records and safeguard documentation
- Retention: as long as necessary for identified purposes; then securely destroyed

---

### LGPD

| Field | Value |
|-------|-------|
| **Full Name** | Lei Geral de Protecao de Dados Pessoais (General Data Protection Law) |
| **Governing Body** | Autoridade Nacional de Protecao de Dados (ANPD) |
| **Priority** | P3 |
| **Status** | NOT_STARTED |
| **Third-Party Audit Required** | No (self-compliance with ANPD enforcement) |
| **Estimated Cost** | $10,000 -- $30,000 (gap assessment + implementation) |
| **Estimated Timeline** | 2--4 months |

**Key Requirements:**
- Establish lawful basis for processing personal data (10 legal bases including consent, legitimate interest, etc.)
- Appoint Data Protection Officer (Encarregado) and register with ANPD
- Implement data subject rights: confirmation, access, correction, anonymization, portability, deletion, information about sharing
- Prepare Data Protection Impact Assessment (RIPD) for high-risk processing
- Implement security measures proportional to the risk of processing

**Audit Trail Requirements:**
- Processing activity records per ANPD requirements
- Data subject request logs with response timelines (15-day deadline)
- Consent records with timestamp and scope
- International data transfer records and safeguard documentation
- Retention: as defined by legal basis and purpose; ANPD may request records at any time

---

## Cross-Reference: Audit Trail Requirements by SOP

| SOP | SOC2 | ISO 42001 | EU AI Act | ISO 27001 | HIPAA | HITRUST | FedRAMP | FDA Part 11 | CMMC | PCI DSS | GDPR | SOX |
|-----|------|-----------|-----------|-----------|-------|---------|---------|-------------|------|---------|------|-----|
| SOP-001 (Audit Trail) | X | X | X | X | X | X | X | X | X | X | X | X |
| SOP-002 (Change Control) | X | X | X | X | | X | X | X | X | X | | X |
| SOP-003 (Access Control) | X | X | | X | X | X | X | X | X | X | X | X |
| SOP-004 (Model Version) | | X | X | | | | | X | | | | |
| SOP-005 (Incident Response) | X | X | X | X | X | X | X | | X | X | X | X |

---

## Summary Dashboard

| Certification | Priority | Status | Third-Party Audit | Est. Cost (Initial) | Est. Timeline |
|--------------|----------|--------|-------------------|---------------------|---------------|
| SOC 2 Type II | P0 | NOT_STARTED | Yes | $30K--$80K | 6--9 months |
| ISO/IEC 42001 | P0 | NOT_STARTED | Yes | $40K--$100K | 6--12 months |
| EU AI Act | P0 | NOT_STARTED | Yes (high-risk) | $50K--$150K | 6--12 months |
| ISO 27001 | P1 | NOT_STARTED | Yes | $25K--$60K | 6--12 months |
| HIPAA | P1 | NOT_STARTED | Recommended | $20K--$50K | 3--6 months |
| HITRUST r2 | P1 | NOT_STARTED | Yes | $80K--$200K | 9--18 months |
| FedRAMP Moderate | P1 | NOT_STARTED | Yes | $250K--$750K | 12--18 months |
| FDA 21 CFR Part 11 | P1 | NOT_STARTED | Recommended | $30K--$80K | 3--6 months |
| CMMC Level 2 | P2 | NOT_STARTED | Yes | $50K--$150K | 6--12 months |
| PCI DSS | P2 | NOT_STARTED | Yes (Level 1) | $50K--$200K | 6--12 months |
| GDPR | P2 | NOT_STARTED | No | $30K--$100K | 3--6 months |
| CCPA/CPRA | P2 | NOT_STARTED | No | $15K--$50K | 2--4 months |
| SOX | P2 | NOT_STARTED | Yes | $100K--$500K | 6--12 months |
| NIST AI RMF | P3 | NOT_STARTED | No | $10K--$30K | 3--6 months |
| ISO 27017/27018 | P3 | NOT_STARTED | Yes | $15K--$30K | 3--6 months |
| ISO 9001 | P3 | NOT_STARTED | Yes | $15K--$40K | 6--12 months |
| StateRAMP | P3 | NOT_STARTED | Yes | $50K--$150K | 3--12 months |
| ITAR | P3 | NOT_STARTED | No | $50K--$200K | 6--12 months |
| DoD IL4/IL5 | P3 | NOT_STARTED | Yes | $500K--$1.5M | 18--24 months |
| GLBA | P3 | NOT_STARTED | Recommended | $20K--$60K | 3--6 months |
| PIPEDA | P3 | NOT_STARTED | No | $10K--$30K | 2--4 months |
| LGPD | P3 | NOT_STARTED | No | $10K--$30K | 2--4 months |
