---
ripple_id: ripple.legal-compliance
version: 1.0.0
base_skills: [phuc-forecast, prime-safety]
persona: Legal analyst / compliance officer (contract review, regulatory mapping, risk flagging)
domain: legal-compliance
author: contributor:legal-tech-team
swarm_agents: [skeptic, adversary, ethicist, security, reviewer]
---

# Legal & Compliance Ripple

## Domain Context

This ripple configures phuc-forecast and prime-safety for legal document analysis,
compliance checking, and regulatory risk assessment:

- **Document types:** contracts, NDAs, SaaS agreements, privacy policies, terms of service,
  employment agreements, vendor agreements, data processing agreements (DPA)
- **Regulatory frameworks:** GDPR, CCPA/CPRA, HIPAA, SOC 2, ISO 27001, FINRA, PCI-DSS,
  EU AI Act, NIST CSF
- **Risk surfaces:** ambiguous indemnification, uncapped liability, data retention obligations,
  prohibited transfer clauses, auto-renewal traps, governing law conflicts
- **Output types:** risk flags, redline suggestions, compliance gap reports, regulatory
  mapping matrices

CRITICAL DISCLAIMER:
  This ripple is for analysis assistance only. It does NOT constitute legal advice.
  All outputs must be reviewed by a qualified attorney before any legal reliance.
  The ripple enforces this disclaimer on every output.

## Skill Overrides

```yaml
skill_overrides:
  phuc-forecast:
    stakes_default: HIGH
    note: >
      Legal and compliance work defaults to HIGH stakes. The premortem must identify
      risks in all five categories: financial, reputational, operational, regulatory,
      and legal liability. Fail-closed if document scope is ambiguous.
    required_lenses: [skeptic, adversary, ethicist, security, reviewer]
    premortem_required: true
    hypothesis_formulation_required: true
  prime-safety:
    rung_default: 274177
    require_source_citation: true
    note: >
      Every risk flag and compliance finding must cite the specific clause, section,
      or article number in the source document. No findings without source grounding.
    forbidden_ops:
      - legal_advice_without_disclaimer
      - finding_without_clause_citation
      - regulatory_mapping_without_version_of_regulation
      - privilege_waiver_risk_not_flagged
    output_contract:
      require_disclaimer_on_every_output: true
      disclaimer_text: >
        DISCLAIMER: This output is for analysis assistance only and does not constitute
        legal advice. All findings must be reviewed by a qualified attorney before
        any legal reliance.
```

## Recipe Preferences

```yaml
recipe_preferences:
  - id: recipe.contract-review
    priority: HIGH
    name: "Contract Risk Review"
    reason: >
      Contract review must be systematic, clause-by-clause, not impressionistic.
      Every risk flag must cite the specific clause and quantify the exposure
      (financial cap, data scope, time horizon) where possible.
    steps:
      1: "Identify document type, parties, governing law, and effective date"
      2: "Extract and list all defined terms; flag any circular or ambiguous definitions"
      3: "Review each section category: payment/fees, IP ownership, indemnification,
          limitation of liability, termination, data rights, governing law, dispute resolution"
      4: "For each clause: classify risk as LOW/MED/HIGH with specific concern"
      5: "Flag any: uncapped liability, unilateral amendment rights, auto-renewal with short notice,
          broad IP assignment, data sharing without restriction, unfavorable jurisdiction"
      6: "Produce risk matrix: clause reference, risk description, exposure estimate, suggested redline"
      7: "Apply disclaimer; deliver risk_review.json + redline_suggestions.md"
    required_artifacts:
      - evidence/risk_review.json (clause_ref, risk_level, exposure_description, suggested_redline)
      - evidence/redline_suggestions.md
      - disclaimer appended to all outputs

  - id: recipe.gdpr-compliance-check
    priority: HIGH
    name: "GDPR / Data Privacy Compliance Gap Analysis"
    reason: >
      GDPR fines up to 4% of global annual revenue. A systematic gap analysis must
      check all 11 GDPR lawfulness bases, 8 data subject rights, and controller/processor
      obligations against current practices.
    steps:
      1: "Identify all personal data categories processed: name, email, IP, biometric, health, etc."
      2: "Map each data category to a lawfulness basis (Art. 6 / Art. 9 GDPR)"
      3: "Verify data subject rights are operationalized: access (Art. 15), erasure (Art. 17),
          portability (Art. 20), rectification (Art. 16), restriction (Art. 18), objection (Art. 21)"
      4: "Check DPA (Data Processing Agreement) exists for every processor (Art. 28)"
      5: "Check retention policy: each data category has defined retention period"
      6: "Check breach notification procedure: 72-hour window to supervisory authority (Art. 33)"
      7: "Produce compliance_gap_matrix.json: requirement, status (MET/PARTIAL/NOT_MET), evidence"
    required_artifacts:
      - evidence/compliance_gap_matrix.json (gdpr_article, status, evidence_or_gap_description)
      - evidence/data_inventory.json (data_category, lawfulness_basis, retention_period, processors)

  - id: recipe.risk-flagging
    priority: HIGH
    name: "Regulatory Risk Flagging"
    reason: >
      New product features or business processes must be screened against applicable
      regulations before launch. This recipe produces a regulatory impact assessment.
    steps:
      1: "Define the feature/process: what data is collected, processed, shared? Who are the users?"
      2: "Identify applicable regulatory frameworks based on: geography, data type, industry, user type"
      3: "For each framework: list specific obligations triggered by this feature"
      4: "Classify each obligation: already met / gap / unknown (needs legal review)"
      5: "Identify any hard blockers (e.g., HIPAA BAA required before launch)"
      6: "Produce regulatory_impact.json with: framework, version, obligations, status, blockers"
      7: "Flag any items requiring attorney review before ship decision"
    required_artifacts:
      - evidence/regulatory_impact.json (framework, version, obligation, status, blocker)

  - id: recipe.vendor-dpa-review
    priority: MED
    name: "Vendor Data Processing Agreement Review"
    reason: >
      Sharing personal data with a vendor without an adequate DPA is an Art. 28 GDPR
      violation. This recipe checks DPAs for minimum required clauses.
    steps:
      1: "Confirm DPA exists and is signed by both parties"
      2: "Check for required Art. 28(3) clauses: processing only on documented instructions,
          confidentiality, security measures, sub-processor restrictions, data subject assistance,
          deletion or return of data post-contract, audit rights"
      3: "Verify sub-processor list is provided and change notification mechanism exists"
      4: "Check SCCs or adequacy decision for international data transfers (Art. 46)"
      5: "Record: vendor_name, dpa_version, date_signed, missing_clauses, transfer_mechanism"
    required_artifacts:
      - evidence/vendor_dpa_review.json (vendor_name, dpa_version, clauses_present, clauses_missing, transfer_mechanism)

  - id: recipe.soc2-control-mapping
    priority: MED
    name: "SOC 2 Control Mapping"
    reason: >
      SOC 2 Type II audits require evidence of control effectiveness over a period.
      This recipe maps existing controls to the Trust Services Criteria (TSC).
    steps:
      1: "Identify which TSCs are in scope: CC (Common Criteria), A (Availability), C (Confidentiality),
          PI (Processing Integrity), P (Privacy)"
      2: "For each TSC criterion: identify current control, control owner, and evidence type"
      3: "Flag any criterion with no mapped control as a GAP requiring remediation"
      4: "Estimate evidence collection timeline for Type II audit period"
      5: "Produce control_mapping.json: criterion, control_description, owner, evidence_type, status"
    required_artifacts:
      - evidence/control_mapping.json (tsc_criterion, control, owner, evidence_type, gap_flag)
```

## Forbidden States (Domain-Specific)

```yaml
forbidden_states:
  - id: NO_LEGAL_ADVICE_WITHOUT_DISCLAIMER
    description: >
      Every output from this ripple that contains a legal risk assessment, contract
      redline, or compliance finding must include the standard disclaimer that this
      is not legal advice and requires attorney review.
    detector: "Check every output document for presence of DISCLAIMER: header."
    recovery: "Prepend standard disclaimer to output before delivery."

  - id: NO_FINDING_WITHOUT_CLAUSE_CITATION
    description: >
      Every risk flag or compliance finding must cite the specific clause number,
      section, or article in the source document or regulation. Vague findings
      like 'the indemnification seems broad' without a clause reference are forbidden.
    detector: "Check evidence/risk_review.json: every entry must have clause_ref field populated."
    recovery: "Re-review source document; find specific clause; update finding with exact reference."

  - id: NO_REGULATORY_MAPPING_WITHOUT_VERSION
    description: >
      Regulatory requirements change. Any mapping to GDPR, CCPA, HIPAA, or other
      regulations must specify the version/amendment date of the regulation used.
    detector: "Check evidence/compliance_gap_matrix.json: every framework entry must have version field."
    recovery: "Add version: 'GDPR (OJ L 119, 04/05/2016, as amended)' to each framework reference."

  - id: NO_PRIVILEGE_WAIVER_RISK_UNCHECKED
    description: >
      Documents that may be covered by attorney-client privilege or work product
      protection must have waiver risk assessed before being shared or analyzed
      in a context where privilege could be challenged.
    detector: "Check if document source is from legal department or in-house counsel — flag for privilege review."
    recovery: "Add privilege_waiver_risk: ASSESS_BEFORE_SHARING to evidence/risk_review.json."

  - id: NO_PII_IN_EVIDENCE_ARTIFACTS
    description: >
      Evidence artifacts (JSON files, logs, analysis outputs) must not contain actual
      PII from the documents being reviewed. Use anonymized references (Clause 3.2)
      not the actual personal data content.
    detector: "Scan evidence/*.json for patterns matching email, SSN, DOB, phone number formats."
    recovery: "Replace PII with placeholder references: [REDACTED] or clause reference only."
```

## Verification Extensions

```yaml
verification_extensions:
  rung_641:
    required_checks:
      - disclaimer_present: "DISCLAIMER header present in all output files"
      - clause_citations_complete: "every finding in risk_review.json has clause_ref"
      - regulatory_version_documented: "all framework references include version"
      - no_pii_in_evidence: "evidence/*.json contains no raw PII from source documents"
  rung_274177:
    required_checks:
      - second_reviewer_pass: "risk_review.json reviewed by a second analyst; review_date logged"
      - regulation_currency_check: "verify regulation versions are current as of today's date"
      - gap_remediation_plan: "every NOT_MET gap has a remediation_action in compliance_gap_matrix.json"
      - privilege_review_complete: "privilege_waiver_risk assessed for all privileged-source documents"
  rung_65537:
    required_checks:
      - attorney_review_scheduled: "evidence/attorney_review.json with scheduled_date field"
      - adversarial_scenario_tested: "worst-case interpretation of each HIGH-risk clause documented"
      - cross_jurisdiction_check: "governing law conflicts with data subject locations identified"
      - complete_regulatory_matrix: "all applicable frameworks mapped with no UNKNOWN statuses"
```

## Quick Start

```bash
# Load this ripple and start a legal analysis task
stillwater run --ripple ripples/legal-compliance.md --task "Review this SaaS vendor agreement for GDPR compliance and liability exposure"
```

## Example Use Cases

- Perform a systematic clause-by-clause contract review: extracts defined terms, flags uncapped
  liability and broad IP assignment clauses with exact section citations, produces a risk matrix
  JSON with HIGH/MED/LOW ratings, and appends the required attorney-review disclaimer to all outputs.
- Run a GDPR compliance gap analysis for a new product feature: maps personal data categories to
  lawfulness bases, checks all eight data subject rights are operationalized, identifies missing
  DPAs for processors, and produces a compliance_gap_matrix.json with remediation priorities.
- Screen a new SaaS vendor's DPA for minimum Art. 28 GDPR clauses and international transfer
  mechanisms: identifies missing sub-processor change notification clauses, flags absent SCCs,
  and produces a vendor_dpa_review.json with specific missing clause references.
