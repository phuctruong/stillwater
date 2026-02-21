---
ripple_id: ripple.web-dev
version: 1.0.0
base_skills: [prime-safety, prime-coder]
persona: Full-stack web developer (React + Node.js + TypeScript)
domain: web-development
---

# Web Development Ripple

## Domain Context

This ripple configures the prime-coder and prime-safety skills for full-stack web development
using the modern JavaScript/TypeScript ecosystem:

- **Frontend:** React, TypeScript, CSS Modules / Tailwind
- **Backend:** Node.js, Express / Fastify, REST APIs, GraphQL
- **Tooling:** Vite, ESBuild, ESLint, Prettier, Jest, Playwright
- **Security surface:** XSS, CSRF, injection, cookie/session hygiene, CORS configuration

## Skill Overrides

```yaml
skill_overrides:
  prime-coder:
    localization:
      extra_signals:
        contains_pattern_jsx_tsx: 4
        touches_api_route_handler: 5
        touches_auth_middleware: 6
    security_gate:
      always_trigger_on:
        - auth/
        - middleware/
        - api/
        - routes/
      web_specific_checks:
        - xss_output_encoding: REQUIRED
        - csrf_token_validation: REQUIRED
        - sql_injection_parameterized: REQUIRED
        - input_sanitization: REQUIRED
    code_review_emphasis:
      - "Verify all user input is validated server-side (never trust client)."
      - "Check React JSX for dangerouslySetInnerHTML usage."
      - "Ensure fetch/axios calls include CSRF headers where applicable."
      - "Confirm cookies use HttpOnly + SameSite + Secure flags in production."
      - "Audit CORS origin allowlists; reject wildcard (*) in production."
  prime-safety:
    rung_default: 274177
    security_gate_always_on: true
```

## Recipe Preferences

```yaml
recipe_preferences:
  - id: recipe.portability-audit
    priority: HIGH
    reason: "Frontend code ships to user browsers across many environments; portability is critical."
    trigger_on:
      - any .tsx / .jsx file touched
      - any webpack/vite config touched
  - id: recipe.null-zero-audit
    priority: MED
    reason: "API response parsing often conflates null/undefined/0/false; must be distinguished."
    trigger_on:
      - any API handler touched
      - any data-fetching hook touched
```

## Forbidden States (Domain-Specific)

```yaml
forbidden_states:
  - id: NO_JQUERY
    description: "Do not introduce jQuery or jQuery plugins. Use native DOM APIs or React."
    detector: "grep -r 'jquery' --include='*.js' --include='*.ts' --include='*.tsx'"
    recovery: "Replace with native fetch, querySelector, or React state."

  - id: NO_UNTYPED_ANY
    description: "TypeScript 'any' type defeats the type system. Treat as a lint error."
    detector: "tsc --noEmit or eslint @typescript-eslint/no-explicit-any"
    recovery: "Replace with proper types, generics, or 'unknown' with a type guard."

  - id: NO_CONSOLE_LOG_IN_PRODUCTION
    description: "console.log leaks internal state and clutters production logs."
    detector: "eslint no-console rule; or grep 'console.log' in src/"
    recovery: "Use a structured logger (pino, winston) gated by LOG_LEVEL env var."

  - id: NO_DANGEROUSLY_SET_INNER_HTML_WITHOUT_SANITIZE
    description: "dangerouslySetInnerHTML without sanitization is a direct XSS vector."
    detector: "grep -r 'dangerouslySetInnerHTML' src/"
    recovery: "Use DOMPurify.sanitize() before setting HTML, or restructure to avoid raw HTML."

  - id: NO_HARDCODED_SECRETS
    description: "API keys, tokens, passwords must never be committed to source."
    detector: "git-secrets or trufflehog scan"
    recovery: "Move to .env (gitignored) and reference via process.env."
```

## Verification Extensions

```yaml
verification_extensions:
  rung_641:
    required_checks:
      - typescript_compilation_clean: "npx tsc --noEmit exits 0"
      - eslint_clean: "npx eslint src/ exits 0"
      - unit_tests_green: "jest --coverage exits 0"
  rung_274177:
    required_checks:
      - e2e_tests_green: "playwright test exits 0"
      - bundle_size_regression: "compare dist/ sizes; block if >10% increase without justification"
      - lighthouse_score_not_regressed: "optional but recommended for frontend"
  rung_65537:
    required_checks:
      - owasp_zap_or_equivalent: "DAST scan on staging environment"
      - dependency_audit: "npm audit --audit-level=high exits 0"
      - security_headers_check: "verify CSP, HSTS, X-Frame-Options present in responses"
```
