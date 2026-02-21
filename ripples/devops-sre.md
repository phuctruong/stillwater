---
ripple_id: ripple.devops-sre
version: 1.0.0
base_skills: [prime-safety, prime-hooks, prime-coder]
persona: SRE / Platform engineer (Kubernetes, Terraform, Prometheus, PagerDuty, GitHub Actions)
domain: devops-sre
author: contributor:sre-platform-team
swarm_agents: [ops, security, skeptic, adversary, architect]
---

# DevOps / SRE Ripple

## Domain Context

This ripple configures prime-safety, prime-hooks, and prime-coder for infrastructure,
reliability engineering, and CI/CD work:

- **Orchestration:** Kubernetes (EKS/GKE/AKS), Helm, ArgoCD, Kustomize
- **Infrastructure as Code:** Terraform, Pulumi, AWS CDK
- **Observability:** Prometheus, Grafana, Loki, OpenTelemetry, Datadog
- **Incident management:** PagerDuty, OpsGenie, Statuspage
- **CI/CD:** GitHub Actions, Buildkite, Tekton, Docker/Buildx
- **Secrets:** HashiCorp Vault, AWS Secrets Manager, SOPS
- **Correctness surface:** blast radius of infra changes, secret rotation safety,
  deployment rollback paths, alert noise vs. signal, runbook coverage

## Skill Overrides

```yaml
skill_overrides:
  prime-safety:
    rung_default: 274177
    blast_radius_check_required: true
    note: >
      Any Terraform plan or Helm upgrade that touches production resources must have
      an explicit blast radius assessment: which resources are replaced/destroyed,
      estimated downtime, and rollback command documented before apply.
    rollback_gate:
      require_rollback_command_before_apply: true
      require_dry_run_output_in_evidence: true
    forbidden_ops:
      - terraform_apply_without_plan_review
      - kubectl_delete_without_backup_annotation
      - secret_rotation_without_staged_rollout
  prime-hooks:
    pre_incident_checklist: true
    require_runbook_pointer_in_alert: true
    note: >
      Every new Prometheus alert rule must have a runbook_url annotation pointing
      to a runbook that covers: what fired, why it matters, how to triage,
      escalation path, and recovery actions.
  prime-coder:
    localization:
      extra_signals:
        touches_terraform_main: 6
        touches_helm_values: 5
        touches_kubernetes_manifest: 5
        touches_github_actions_workflow: 5
        touches_alerting_rules: 7
        touches_secret_management: 8
    reproducibility:
      require_pinned_image_digests: true
      note: "Docker images in manifests must use @sha256 digest, not mutable tags like :latest or :main"
```

## Recipe Preferences

```yaml
recipe_preferences:
  - id: recipe.incident-response
    priority: HIGH
    name: "Incident Response Flow"
    reason: >
      Incidents require a structured, time-boxed response to minimize MTTR. This recipe
      enforces the DREAM→FORECAST→ACT→VERIFY loop for incident management.
    steps:
      1: "TRIAGE: Acknowledge alert; identify affected service(s), severity (SEV1/2/3), blast radius"
      2: "COMMUNICATE: Post to incident channel: 'Investigating [service] issue since [time]'"
      3: "HYPOTHESIZE: List top 3 likely causes with supporting evidence (metrics, logs, recent deploys)"
      4: "CONTAIN: Apply immediate mitigation (rollback, scale-up, circuit break, traffic redirect)"
      5: "VERIFY: Confirm mitigation is effective (metric returns to SLO within 5 minutes)"
      6: "RESOLVE: Close incident; write 5-line summary in incident channel"
      7: "POSTMORTEM: Schedule within 48 hours; fill template (timeline, root cause, action items)"
    required_artifacts:
      - evidence/incident_timeline.json (start_time, severity, affected_services, mitigation_applied)
      - evidence/postmortem_draft.md

  - id: recipe.runbook-creation
    priority: HIGH
    name: "Alert Runbook Template"
    reason: >
      Every actionable alert must have a runbook. Runbooks must be testable:
      a team member unfamiliar with the service must be able to follow it.
    steps:
      1: "Copy runbook template; fill: alert name, severity, SLO impact, metric query"
      2: "Write triage steps: which dashboards to open, which logs to search, key metrics"
      3: "Write decision tree: if X then do Y; if Z then escalate to <team>"
      4: "Write recovery commands (exact kubectl/terraform/curl commands, not prose)"
      5: "Write verification: how to confirm service is healthy (metric query + expected range)"
      6: "Test runbook: ask a colleague to follow it cold; record gaps"
      7: "Add runbook_url to Prometheus alert rule; deploy updated alert rules"
    required_artifacts:
      - docs/runbooks/<alert-name>.md (with required sections: Overview, Triage, Recovery, Verify)
      - evidence/runbook_review.json (reviewer, gaps_found, gaps_resolved)

  - id: recipe.alert-triage
    priority: HIGH
    name: "Alert Noise Reduction"
    reason: >
      Alert fatigue is an SRE correctness failure. Every alert must be actionable,
      have a defined response, and have a measured false-positive rate.
    steps:
      1: "Pull 30-day alert history for the target alert rule"
      2: "Classify each firing: true-positive (real issue) or false-positive (noise)"
      3: "If false-positive rate > 20%: adjust threshold or add inhibition rule"
      4: "Compute precision = true_positives / (true_positives + false_positives) as Decimal"
      5: "Set alert_precision_target = Decimal('0.80') as minimum for production alerts"
      6: "Document changes in evidence/alert_triage.json"
    required_artifacts:
      - evidence/alert_triage.json (alert_name, firing_count, true_positive_count, precision_decimal)

  - id: recipe.terraform-change
    priority: HIGH
    name: "Safe Terraform Apply"
    reason: >
      Terraform changes to production infrastructure must never be applied without a
      reviewed plan, documented blast radius, and a tested rollback command.
    steps:
      1: "Run terraform plan -out=tfplan; save output to evidence/terraform_plan.txt"
      2: "Parse plan: count resources to add/change/destroy; flag any destroy operations"
      3: "Assess blast radius: will this cause downtime? which services are affected?"
      4: "Document rollback: exact command to revert if apply goes wrong"
      5: "Get second approval for any plan with destroy > 0 or production traffic impact"
      6: "Apply during maintenance window if SEV1 risk; otherwise apply with canary"
      7: "Verify post-apply: check metrics, run smoke test, confirm no regressions"
    forbidden_in_recipe:
      - terraform_apply_without_saved_plan
      - apply_during_peak_traffic_without_feature_flag
      - no_rollback_documented

  - id: recipe.secret-rotation
    priority: MED
    name: "Zero-Downtime Secret Rotation"
    reason: >
      Rotating secrets (API keys, DB passwords, TLS certs) must be done without
      service interruption using a dual-write staged rollout pattern.
    steps:
      1: "Generate new secret; store in Vault/AWS Secrets Manager as a new version"
      2: "Update application to accept BOTH old and new secret (dual-read phase)"
      3: "Deploy and verify dual-read works: both old and new authenticate correctly"
      4: "Rotate the external service to issue new secret as primary"
      5: "Remove old secret from application (single-read phase)"
      6: "Deprecate old secret version; set TTL to 0 in Vault"
      7: "Verify no authentication failures in metrics for 24 hours post-rotation"
    required_artifacts:
      - evidence/secret_rotation_log.json (secret_name, old_version, new_version, rollout_stages)
```

## Forbidden States (Domain-Specific)

```yaml
forbidden_states:
  - id: NO_TERRAFORM_APPLY_WITHOUT_PLAN
    description: >
      terraform apply without -auto-approve=false and a reviewed plan output is forbidden
      in any environment that shares resources with production.
    detector: "Check CI/CD pipeline: terraform apply must reference a saved plan file."
    recovery: "Always: terraform plan -out=tfplan && review && terraform apply tfplan"

  - id: NO_MUTABLE_IMAGE_TAG_IN_PRODUCTION
    description: >
      Docker images referenced as :latest, :main, :dev, or any non-digest tag in
      Kubernetes manifests or Helm values are forbidden in production environments.
    detector: "grep -n 'image:' k8s/**/*.yaml helm/**/values*.yaml | grep -v '@sha256'"
    recovery: "Pin all images to @sha256 digest. Use image digester tool in CI."

  - id: NO_ALERT_WITHOUT_RUNBOOK
    description: >
      A Prometheus alerting rule without a runbook_url annotation is an orphan alert.
      Orphan alerts are forbidden in production alert groups.
    detector: "grep -L 'runbook_url' monitoring/rules/*.yaml"
    recovery: "Add annotations: { runbook_url: 'https://wiki/runbooks/<alert-name>' } to alert rule."

  - id: NO_SECRET_IN_PLAINTEXT_CONFIGMAP
    description: >
      Kubernetes ConfigMaps must not contain secret values. All secrets must live in
      Kubernetes Secrets (ideally sealed or Vault-injected), not ConfigMaps.
    detector: "grep -rn 'kind: ConfigMap' k8s/ | xargs grep -l 'PASSWORD\\|SECRET\\|TOKEN\\|KEY'"
    recovery: "Move secret values to a Kubernetes Secret or use Vault Agent Injector."

  - id: NO_INCIDENT_WITHOUT_POSTMORTEM
    description: >
      Any SEV1 or SEV2 incident that is resolved must have a postmortem scheduled
      within 24 hours and published within 5 business days. Blameless postmortems only.
    detector: "Check incident tracker: all closed SEV1/2 incidents must have postmortem_url field."
    recovery: "Schedule postmortem meeting; use standard template; assign action items with owners + due dates."
```

## Verification Extensions

```yaml
verification_extensions:
  rung_641:
    required_checks:
      - terraform_plan_clean: "terraform validate exits 0; plan shows no unexpected destroys"
      - helm_lint_clean: "helm lint exits 0"
      - yaml_valid: "kubeval or kubeconform on all manifests exits 0"
      - no_mutable_tags: "no :latest or mutable tags in manifests"
  rung_274177:
    required_checks:
      - staging_deploy_successful: "argocd sync exits 0 in staging"
      - smoke_test_green: "smoke test script exits 0 post-deploy"
      - rollback_tested: "kubectl rollout undo or terraform apply previous plan verified"
      - alert_rules_valid: "promtool check rules exits 0"
  rung_65537:
    required_checks:
      - production_canary: "10% canary deployed; error rate <= baseline for 30 minutes"
      - secret_scan_clean: "no plaintext secrets in manifests (detect-secrets scan)"
      - runbook_coverage: "all alerts have runbook_url; runbook reviewed by >= 1 peer"
      - disaster_recovery_tested: "DR drill documented in evidence/ within last 90 days"
```

## Quick Start

```bash
# Load this ripple and start an SRE task
stillwater run --ripple ripples/devops-sre.md --task "Create runbook for HighMemoryUsage alert on payments service"
```

## Example Use Cases

- Respond to an active incident: generates a structured incident timeline, surfaces the top 3
  hypotheses from recent deploy history and metrics, produces mitigation commands, and
  auto-drafts a postmortem skeleton with action items.
- Review a Terraform plan for production infrastructure changes: computes blast radius, flags
  any destroy operations, documents rollback command, and blocks apply if no second approval
  is recorded for destructive changes.
- Audit all Prometheus alert rules for orphan alerts (no runbook), high false-positive rates,
  and mutable image tags in associated deployments — produces an alert_triage.json with
  precision metrics as Decimal strings for each alert.
