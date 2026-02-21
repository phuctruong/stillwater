---
ripple_id: ripple.security-audit
version: 1.0.0
base_skills: [prime-safety, prime-coder]
persona: Security engineer (Bruce Schneier lens — assume breach, verify everything, trust no input)
domain: security-audit
---

# Security Audit Ripple

## Domain Context

This ripple configures the prime-coder and prime-safety skills for security auditing work.
It applies the Bruce Schneier lens: systems fail, attackers are creative, trust must be earned
through evidence not assumption.

- **Standards:** OWASP Top 10, CWE Top 25, NIST Cybersecurity Framework
- **Tooling:** SAST (semgrep, bandit, gosec), DAST (OWASP ZAP, Burp Suite), CVE databases
- **Attack surface:** injection, broken auth, SSRF, deserialization, supply chain, secrets exposure
- **Philosophy:** "Security is a process, not a product." Every PASS claim requires security gate.

## Skill Overrides

```yaml
skill_overrides:
  prime-coder:
    security_gate:
      always_on: true
      rung_required: 65537
      no_exceptions: true
      required_evidence:
        - security_scan.json with tool version + rule set hash
        - exploit_repro_script if manual verification used
      toolchain:
        preferred_scanners: [semgrep, bandit, gosec, trivy]
        require_pinned_versions: true
        require_rule_set_hash: true
      fail_closed:
        if_scanner_unavailable: BLOCKED
        if_scan_findings_unresolved: BLOCKED
        if_exploit_repro_not_attempted: BLOCKED
    localization:
      extra_signals:
        touches_auth_code: 8
        touches_crypto_code: 8
        touches_deserialization: 7
        touches_subprocess_or_eval: 7
        touches_file_upload: 6
        touches_session_management: 6
        touches_secret_or_credential: 9
    code_review_emphasis:
      - "Map every user-controlled input to its sink. Validate at trust boundaries."
      - "Check for insecure defaults (DEBUG=True, open CORS, weak ciphers)."
      - "Verify cryptographic primitives are from standard libraries, not hand-rolled."
      - "Audit dependency tree for known CVEs (pip-audit, npm audit, trivy)."
      - "Check for secrets in code, env dumps, error messages, or log output."
      - "Verify privilege escalation paths: can an unauthenticated user reach this code?"
  prime-safety:
    rung_default: 65537
    security_gate_always_on: true
    fail_closed_on_any_security_finding: true
```

## Recipe Preferences

```yaml
recipe_preferences:
  - id: recipe.portability-audit
    priority: HIGH
    mandatory: true
    reason: >
      Portability audit catches environment-specific assumptions that can become
      security vulnerabilities (path traversal, platform-specific behavior, TOCTOU).

  - id: recipe.null-zero-audit
    priority: HIGH
    mandatory: true
    reason: >
      Null/zero confusion is a common source of authentication bypass (null session token
      treated as valid, zero user ID resolving to admin, null permission check short-circuiting).

  - id: recipe.security-scan
    priority: CRITICAL
    mandatory: true
    reason: "Every PASS claim in security-audit domain requires security-scan recipe completion."
    required_artifacts:
      - security_scan.json
      - exploit_repro_script (if applicable)
```

## Forbidden States (Domain-Specific)

```yaml
forbidden_states:
  - id: NO_PASS_WITHOUT_SECURITY_GATE
    description: >
      In security-audit domain, EXIT_PASS is forbidden unless security_scan.json
      exists in EVIDENCE_ROOT with a clean or fully-mitigated finding set.
    detector: "Check EVIDENCE_ROOT/security_scan.json before any PASS claim."
    recovery: "Run semgrep + bandit (or equivalent). Resolve or document accepted risks."

  - id: NO_HARDCODED_CREDENTIALS
    description: >
      Hardcoded passwords, API keys, tokens, or private keys in source code or config
      are an immediate BLOCKED finding with no exceptions.
    detector: "semgrep rule: hardcoded-credentials; trufflehog; git-secrets"
    recovery: "Rotate the credential immediately. Use secrets manager or env var injection."

  - id: NO_EVAL_OR_EXEC_ON_USER_INPUT
    description: >
      eval(), exec(), subprocess with shell=True on user-controlled input is a
      direct code injection vector.
    detector: "bandit B307, B602, B603; semgrep python.lang.security.audit.eval"
    recovery: "Use ast.literal_eval for safe parsing; parameterized commands for subprocess."

  - id: NO_WEAK_CRYPTO
    description: >
      MD5, SHA1 (for security purposes), DES, RC4, ECB mode, and custom crypto are
      forbidden. Use SHA-256+, AES-GCM, RSA-2048+, or equivalent standards.
    detector: "bandit B303, B304, B305, B413; semgrep crypto rules"
    recovery: "Replace with cryptography library primitives (Fernet, AESGCM, RSA from cryptography pkg)."

  - id: NO_SQL_STRING_FORMATTING
    description: >
      String formatting (f-string, %, .format()) to build SQL queries is a SQL injection
      vector. Parameterized queries are required.
    detector: "bandit B608; semgrep sql-injection rules"
    recovery: "Use parameterized queries or ORM query builders exclusively."

  - id: NO_DESERIALIZATION_OF_UNTRUSTED_INPUT
    description: >
      pickle.loads(), yaml.load() (unsafe), marshal on untrusted data enables
      remote code execution.
    detector: "bandit B301, B302, B506; grep 'pickle.loads\\|yaml.load('"
    recovery: "Use pickle only on trusted data from controlled sources. Use yaml.safe_load()."

  - id: NO_SECURITY_FINDING_SILENCED_WITHOUT_EVIDENCE
    description: >
      Security scanner findings must not be suppressed (noqa, nosec, semgrep ignore)
      without a documented and reviewed justification in evidence.
    detector: "grep -r 'nosec\\|noqa.*B[0-9]\\|semgrep:ignore' in codebase"
    recovery: "Document the accepted risk in security_scan.json with reviewer sign-off."
```

## Verification Extensions

```yaml
verification_extensions:
  rung_641:
    required_checks:
      - sast_scan_clean: "semgrep + bandit exit 0 with no unresolved HIGH/CRITICAL findings"
      - dependency_audit: "pip-audit or npm audit --audit-level=high exits 0"
      - secrets_scan: "trufflehog or git-secrets scan exits clean"
      - security_scan_json_present: "EVIDENCE_ROOT/security_scan.json with tool versions and rule set hash"
  rung_274177:
    required_checks:
      - replay_stability: "Re-run scan on same commit produces identical finding set"
      - null_auth_bypass_test: "Test null/zero/empty session token, user ID, and permission values"
      - seed_sweep_not_applicable: "Note: security findings must be deterministic, not seed-dependent"
  rung_65537:
    required_checks:
      - dast_scan: "OWASP ZAP or Burp Suite active scan against staging environment"
      - exploit_repro_attempted: >
          For each HIGH/CRITICAL finding: exploit_repro_script attempted.
          If exploitable: blocked until patched + retested.
          If not exploitable: document why in security_scan.json.
      - threat_model_review: "STRIDE or equivalent threat model documented in evidence"
      - supply_chain_audit: "SBOM generated; all dependencies pinned with checksums"
      - penetration_test_summary: "Manual pen test or automated DAST result in security_scan.json"

  owasp_top10_checklist:
    A01_broken_access_control: MUST_CHECK
    A02_cryptographic_failures: MUST_CHECK
    A03_injection: MUST_CHECK
    A04_insecure_design: MUST_CHECK
    A05_security_misconfiguration: MUST_CHECK
    A06_vulnerable_components: MUST_CHECK
    A07_auth_failures: MUST_CHECK
    A08_software_data_integrity: MUST_CHECK
    A09_security_logging_monitoring: MUST_CHECK
    A10_ssrf: MUST_CHECK
```
