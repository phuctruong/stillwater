# SOP-004: Model Version Control

**Document ID:** SOP-004
**Version:** 1.0.0
**Effective Date:** 2026-02-24
**Owner:** AI Engineering & Compliance Team
**Approved By:** [Pending Approval]
**Review Cycle:** Annual (or upon significant model architecture change)
**Related Documents:** compliance-matrix.md, SOP-001, SOP-002, SOP-005, audit-entry-schema.json

---

## 1. Purpose

This Standard Operating Procedure establishes the requirements, procedures, and responsibilities for managing AI model versioning within the Stillwater AI orchestration engine. It ensures that all model changes -- including retraining, parameter updates, data changes, and configuration modifications -- are tracked, validated, documented, and auditable.

This SOP addresses model governance requirements for ISO/IEC 42001 (AI Management System), EU AI Act (Article 9 risk management, Article 12 record-keeping), FDA 21 CFR Part 11 (system validation), NIST AI RMF (Govern, Map, Measure, Manage), and SOC 2 processing integrity.

---

## 2. Scope

This procedure applies to:
- All AI/ML models deployed within the Stillwater orchestration engine
- All model components: weights, architectures, hyperparameters, preprocessing pipelines, postprocessing logic
- All model artifacts: training data references, evaluation datasets, model cards, deployment configurations
- All model lifecycle stages: development, validation, deployment, monitoring, deprecation, decommission

This procedure does NOT apply to:
- Experimental models in research/sandbox environments that are not promoted to staging or production
- Third-party foundation models used via API (governed by vendor agreements), except for fine-tuned versions or prompt engineering configurations that are under Stillwater control

---

## 3. Responsibilities

| Role | Responsibility |
|------|---------------|
| **AI Engineer** | Develops, trains, and validates models; creates model cards; submits model change requests |
| **AI Lead** | Reviews model changes; approves Minor model updates; ensures model quality standards |
| **CAB (Change Advisory Board)** | Approves Major and Critical model changes per SOP-002 |
| **QA Engineer** | Validates model performance against acceptance criteria; executes model testing plans |
| **Security Engineer** | Assesses security implications of model changes (adversarial robustness, data poisoning risks) |
| **Compliance Officer** | Ensures model changes comply with certification requirements; reviews model cards for regulated deployments |
| **Data Engineer** | Manages training data versioning and lineage; ensures data quality and provenance |
| **Model Registry Admin** | Maintains the model registry; manages model promotion and rollback procedures |

---

## 4. Procedures

### 4.1 Model Versioning Scheme

All models follow semantic versioning (SemVer) with AI-specific semantics:

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

| Component | Increment When | Example |
|-----------|---------------|---------|
| **MAJOR** | Model architecture changes; training data domain shift; output format/schema changes; breaking API changes | `1.0.0` to `2.0.0` |
| **MINOR** | Retraining with updated data (same distribution); hyperparameter tuning; new feature addition (backward compatible); preprocessing pipeline update | `1.0.0` to `1.1.0` |
| **PATCH** | Bug fix in preprocessing/postprocessing; configuration correction; documentation update; no model weight changes | `1.0.0` to `1.0.1` |
| **PRERELEASE** | Candidate versions under validation | `2.0.0-rc.1` |
| **BUILD** | Build metadata (training run ID, timestamp) | `1.1.0+train-20260224-001` |

### 4.2 Model Change Triggers

The following events trigger a model version change:

| Trigger | Version Impact | Change Classification (SOP-002) |
|---------|---------------|-------------------------------|
| Architecture redesign | MAJOR | Critical |
| Training data domain shift (new data source, significant distribution change) | MAJOR | Critical |
| Output schema change | MAJOR | Critical |
| Retraining with updated data (same distribution) | MINOR | Major |
| Hyperparameter optimization | MINOR | Major |
| New feature/input addition (backward compatible) | MINOR | Major |
| Preprocessing pipeline modification | MINOR | Major |
| Bug fix in pre/postprocessing logic | PATCH | Minor |
| Configuration file correction | PATCH | Minor |
| Prompt template update (for LLM-based models) | MINOR | Major |
| Fine-tuning a foundation model | MAJOR | Critical |
| Threshold/decision boundary adjustment | MINOR | Major |

### 4.3 Validation Requirements Per Change Type

#### 4.3.1 PATCH Changes (Minor Classification)

| Validation Step | Required | Evidence |
|----------------|----------|----------|
| Unit tests for affected component | Yes | Test execution report (pass/fail) |
| Regression test on evaluation dataset | Yes | Metrics unchanged (within tolerance) |
| Code review | Yes | Approved pull request |
| Model card update | If documentation is affected | Updated model card |
| Approval | AI Lead | Signed approval in CR |

#### 4.3.2 MINOR Changes (Major Classification)

| Validation Step | Required | Evidence |
|----------------|----------|----------|
| All PATCH validations | Yes | See above |
| Performance evaluation on standard benchmark | Yes | Metrics report with comparison to baseline |
| Bias and fairness evaluation | Yes | Fairness metrics report |
| A/B test or shadow deployment (minimum 7 days) | Yes | A/B test results with statistical significance |
| Data quality validation | Yes (if data changed) | Data quality report |
| Integration test | Yes | Integration test execution report |
| Security assessment (adversarial inputs) | Recommended | Adversarial test results |
| Model card update | Yes | Updated model card |
| Approval | CAB (majority) | Signed approval in CR |

#### 4.3.3 MAJOR Changes (Critical Classification)

| Validation Step | Required | Evidence |
|----------------|----------|----------|
| All MINOR validations | Yes | See above |
| Full revalidation per GAMP 5 (IQ/OQ/PQ) | Yes (FDA-regulated) | Validation report |
| AI impact assessment | Yes | Impact assessment document |
| Adversarial robustness testing | Yes | Adversarial test results with attack vectors |
| Explainability/interpretability analysis | Yes | SHAP/LIME or equivalent analysis |
| Data provenance audit | Yes | Data lineage documentation |
| External review (if high-risk per EU AI Act) | Conditional | External assessment report |
| Compliance review | Yes | Compliance Officer sign-off |
| Rollback test | Yes | Successful rollback execution evidence |
| Model card update | Yes | Updated model card |
| Approval | CAB (unanimous) + Compliance Officer | Signed approvals in CR |

### 4.4 Frozen Model Policy

Models that are locked for compliance purposes are designated as FROZEN:

#### 4.4.1 Freeze Criteria

A model MUST be frozen when:
- It is part of a certified system under active audit (e.g., during SOC 2 observation period)
- It is referenced in a regulatory submission (e.g., FDA 510(k), EU AI Act registration)
- It is subject to a legal hold or investigation
- It is designated as a reference model for benchmark comparisons

#### 4.4.2 Freeze Implementation

1. Model version is tagged as `FROZEN` in the model registry.
2. All write permissions to the model artifact are revoked.
3. Automated deployment pipelines are configured to reject updates to frozen models.
4. Any attempt to modify a frozen model generates a `SECURITY_EVENT` audit entry.
5. Frozen status can only be lifted by the Compliance Officer with documented justification.

#### 4.4.3 Frozen Model Exceptions

If a critical security vulnerability or safety issue is discovered in a frozen model:
1. Follow the emergency change procedure in SOP-002, Section 4.4.
2. The Compliance Officer must authorize unfreezing with documented justification.
3. After patching, the model is re-frozen at the new version.
4. Full audit trail of the unfreeze-patch-refreeze cycle is maintained.
5. Relevant certification bodies are notified if required by the certification terms.

### 4.5 Model Performance Monitoring

#### 4.5.1 Continuous Monitoring Metrics

The following metrics are monitored continuously for all deployed models:

| Metric Category | Specific Metrics | Alert Threshold |
|----------------|-----------------|----------------|
| **Accuracy** | Precision, recall, F1, AUC-ROC (classification); RMSE, MAE (regression) | > 5% degradation from baseline |
| **Drift** | Feature drift (PSI, KS test); prediction drift (distribution shift) | PSI > 0.2 or KS p-value < 0.01 |
| **Latency** | P50, P95, P99 inference latency | P95 > 2x baseline |
| **Throughput** | Requests per second; batch processing time | < 80% of expected throughput |
| **Error rate** | Inference failures; malformed outputs; timeout rate | > 1% error rate |
| **Bias** | Demographic parity difference; equalized odds difference | > 0.1 disparity |
| **Resource utilization** | GPU/CPU usage; memory consumption | > 90% sustained for 30 minutes |

#### 4.5.2 Monitoring Schedule

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Automated metric collection | Continuous (per-inference) | System (automated) |
| Dashboard review | Daily | AI Engineer |
| Drift analysis | Weekly | Data Engineer |
| Bias evaluation | Monthly | AI Lead |
| Comprehensive performance review | Quarterly | AI Lead + Compliance Officer |

#### 4.5.3 Alert Response

When a monitoring alert fires:

1. AI Engineer investigates within 4 hours (Critical alert) or 24 hours (non-Critical).
2. Determine root cause (data drift, system issue, model degradation, adversarial input).
3. If model degradation confirmed: initiate model change request per Section 4.2.
4. If data drift confirmed: evaluate need for retraining and initiate if warranted.
5. If adversarial input detected: escalate to Security Engineer and initiate SOP-005.
6. Document investigation and resolution in monitoring log.

### 4.6 Rollback Procedures

#### 4.6.1 Automated Rollback Triggers

The following conditions trigger automatic rollback to the previous model version:

| Condition | Trigger | Rollback Action |
|-----------|---------|----------------|
| Error rate spike | > 5% error rate sustained for 5 minutes post-deployment | Automatic rollback; alert AI Engineer |
| Latency spike | P99 > 5x baseline sustained for 10 minutes post-deployment | Automatic rollback; alert AI Engineer |
| Health check failure | Model endpoint returns non-200 for 3 consecutive checks | Automatic rollback; alert AI Engineer |

#### 4.6.2 Manual Rollback Procedure

1. AI Engineer or Release Manager initiates rollback request.
2. Identify the target rollback version (previous stable version from the model registry).
3. Execute rollback via the deployment pipeline: `stillwater model rollback --model <name> --version <target>`.
4. Verify the rolled-back model is serving correctly (health check + smoke test).
5. Document the rollback in the change management system (SOP-002).
6. Generate audit trail entries for the rollback action.
7. Conduct root cause analysis for the failed deployment.

#### 4.6.3 Rollback Constraints

- Rollback to a FROZEN version requires Compliance Officer verification that the version is still valid.
- Rollback across MAJOR versions is not permitted without full revalidation (treat as new deployment).
- Rollback evidence must include: reason, target version, verification results, and approver.

### 4.7 Documentation Requirements (Model Card)

Every model version MUST have a model card containing:

| Section | Contents |
|---------|----------|
| **Model Identity** | Name, version (SemVer), unique ID, creation date, author(s) |
| **Model Description** | Purpose, architecture, input/output specification, intended use cases, known limitations |
| **Training Data** | Dataset name and version, size, source, collection methodology, preprocessing steps, data splits, known biases |
| **Training Process** | Framework, hyperparameters, training duration, hardware used, random seed(s), reproducibility instructions |
| **Evaluation Results** | Metrics on standard benchmarks, performance across subgroups, comparison to previous version |
| **Bias and Fairness** | Fairness metrics, demographic performance analysis, mitigation steps applied |
| **Security** | Adversarial robustness results, known vulnerabilities, attack surface analysis |
| **Deployment** | Deployment configuration, resource requirements, scaling parameters, monitoring thresholds |
| **Compliance** | Applicable regulations, risk classification (EU AI Act), validation status (GAMP 5), frozen status |
| **Change Log** | Summary of changes from previous version with rationale |
| **Approvals** | Names, roles, and dates of all approvers |

Model cards are stored in the model registry alongside model artifacts and are subject to the same retention policy (10 years per SOP-001).

---

## 5. Records

The following records are generated and maintained under this SOP:

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| Model cards (all versions) | AI Engineer | 10 years | Model registry |
| Model artifacts (weights, configs) | Model Registry Admin | 10 years (or lifetime of system + 2 years) | Model artifact store |
| Training data version references | Data Engineer | 10 years | Data catalog |
| Validation reports (IQ/OQ/PQ) | QA Engineer | 10 years | Compliance repository |
| AI impact assessments | AI Lead | 10 years | Compliance repository |
| Performance monitoring logs | System (automated) | 5 years | Monitoring system |
| Drift analysis reports | Data Engineer | 5 years | Analytics repository |
| Rollback records | Release Manager | 10 years | Change management system |
| Model change requests | AI Engineer | 10 years | Change management system (SOP-002) |

---

## 6. References

- ISO/IEC 42001:2023 -- Artificial Intelligence Management System
- EU AI Act -- Article 9 (Risk Management), Article 11 (Technical Documentation), Article 12 (Record-keeping), Article 15 (Accuracy, Robustness, Cybersecurity)
- FDA 21 CFR Part 11 -- System Validation Requirements
- GAMP 5: A Risk-Based Approach to Compliant GxP Computerized Systems (ISPE)
- NIST AI RMF 1.0 -- Govern, Map, Measure, Manage Functions
- NIST SP 800-53 Rev. 5 -- SA-15 (Development Process, Standards, and Tools), SI-7 (Software, Firmware, and Information Integrity)
- AICPA TSC CC7.1 -- Processing Integrity (Monitoring)
- EU AI Act Annex IV -- Technical Documentation Requirements
- Model Cards for Model Reporting (Mitchell et al., 2019)
- SOP-001: Audit Trail Management
- SOP-002: Change Control
- SOP-005: Incident Response
- compliance-matrix.md

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2026-02-24 | AI Engineering & Compliance Team | Initial release |
