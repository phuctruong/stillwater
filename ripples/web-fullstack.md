---
ripple_id: ripple.web-fullstack
version: 1.0.0
base_skills: [prime-coder, prime-reviewer, prime-mcp]
persona: Full-stack engineer (React/Next.js frontend, FastAPI backend, PostgreSQL, Redis)
domain: web-fullstack
author: contributor:fullstack-guild
swarm_agents: [architect, skeptic, security, ux, reviewer]
---

# Web Full-Stack Ripple

## Domain Context

This ripple configures prime-coder, prime-reviewer, and prime-mcp for full-stack web
development on a React/Next.js + FastAPI + PostgreSQL + Redis stack:

- **Frontend:** React 18, Next.js 14 (App Router), TypeScript, TailwindCSS, React Query
- **Backend:** FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic migrations
- **Data:** PostgreSQL, Redis (sessions/cache), S3-compatible blob storage
- **Auth:** JWT + refresh tokens, OAuth2 (Google/GitHub), session management
- **Testing:** Playwright (E2E), Vitest (unit), pytest (API), httpx (async client)
- **Correctness surface:** type safety, SQL injection, CSRF/XSS, race conditions,
  migration rollback safety, API contract drift

## Skill Overrides

```yaml
skill_overrides:
  prime-coder:
    api_surface_lock:
      enforce: true
      note: >
        Any change to FastAPI route signatures, Pydantic request/response models,
        or Next.js API route schemas triggers a breaking-change check. Must bump
        version in openapi.json and update client SDK types.
      snapshot_paths:
        before: "evidence/api_surface_before.json"
        after: "evidence/api_surface_after.json"
    reproducibility:
      require_deterministic_migrations: true
      require_rollback_script_per_migration: true
    localization:
      extra_signals:
        touches_auth_middleware: 7
        touches_migration_files: 6
        touches_api_route: 5
        touches_react_query_hooks: 4
        touches_env_config: 6
  prime-reviewer:
    rung_default: 274177
    require_type_coverage_report: true
    require_playwright_e2e_before_merge: true
  prime-mcp:
    tool_allowlist:
      - read_file
      - write_file
      - run_tests
      - git_diff
      - browser_screenshot
    network_allowlist:
      domains: ["localhost", "127.0.0.1"]
```

## Recipe Preferences

```yaml
recipe_preferences:
  - id: recipe.api-design
    priority: HIGH
    name: "API Endpoint Design"
    reason: >
      New API endpoints must go through boundary analysis before implementation.
      The contract (request schema, response schema, error codes) must be frozen
      before frontend and backend code is written.
    steps:
      1: "Draft OpenAPI YAML for the new endpoint (path, method, request, response, errors)"
      2: "Write Pydantic request/response models with field validators"
      3: "Write failing pytest integration test against the endpoint (RED gate)"
      4: "Implement FastAPI route handler"
      5: "Run pytest; confirm green. Record exit_code in evidence/tests.json"
      6: "Generate openapi.json and snapshot to evidence/api_surface_after.json"
      7: "Update React Query hook + TypeScript types from new schema"
    required_artifacts:
      - evidence/api_surface_before.json
      - evidence/api_surface_after.json
      - evidence/tests.json

  - id: recipe.component-testing
    priority: HIGH
    name: "React Component Test Harness"
    reason: >
      UI components that render user data must have isolated unit tests (Vitest + Testing Library)
      and at least one Playwright visual regression test.
    steps:
      1: "Write Vitest test for component with mocked React Query data (RED)"
      2: "Implement component with TypeScript props interface"
      3: "Run vitest; confirm green"
      4: "Write Playwright test: render page, assert critical text/aria roles"
      5: "Run playwright; record screenshots to evidence/"
    required_artifacts:
      - evidence/vitest_results.txt
      - evidence/playwright_results.txt

  - id: recipe.auth-pattern
    priority: HIGH
    name: "Auth Flow Implementation"
    reason: >
      Auth code is high-security surface. Any new auth flow must follow the
      JWT + refresh token pattern, include CSRF protection on state-changing routes,
      and be tested with both valid and adversarial tokens.
    steps:
      1: "Define token payload schema (sub, exp, jti, scopes) in Pydantic model"
      2: "Implement /auth/login, /auth/refresh, /auth/logout endpoints"
      3: "Write security tests: expired token, tampered signature, missing scope"
      4: "Run security gate (bandit scan on auth module)"
      5: "Write Playwright test for full login → protected page → logout flow"
      6: "Record security_scan.json in evidence/"
    trigger_on:
      - any file matching "auth", "login", "token", "session", "middleware"
    required_artifacts:
      - evidence/security_scan.json
      - evidence/repro_red.log
      - evidence/repro_green.log

  - id: recipe.db-migration
    priority: MED
    name: "Database Migration Safety"
    reason: >
      Alembic migrations run in production without downtime. Every migration must
      have a tested downgrade() path and must not break existing queries.
    steps:
      1: "Write Alembic migration with both upgrade() and downgrade() implemented"
      2: "Run alembic upgrade head on test DB; verify schema with psql \\d"
      3: "Run existing test suite to check for regressions"
      4: "Run alembic downgrade -1; verify rollback succeeds"
      5: "Document migration in evidence/plan.json under migration_notes"
    forbidden_in_recipe:
      - migration_without_downgrade
      - drop_column_without_default_period
      - rename_column_in_single_migration

  - id: recipe.ssr-data-flow
    priority: MED
    name: "Next.js Server Component Data Flow"
    reason: >
      Server Components fetch data on the server. Caching strategy (no-store, revalidate)
      must be explicit. Secrets must never be forwarded to the client bundle.
    steps:
      1: "Identify which data is user-specific (no-store) vs public (revalidate)"
      2: "Implement server component with fetch() and explicit cache config"
      3: "Verify client bundle does not include env vars (next build --analyze)"
      4: "Write Playwright test asserting correct data appears server-rendered"
```

## Forbidden States (Domain-Specific)

```yaml
forbidden_states:
  - id: NO_HARDCODED_SECRET
    description: >
      API keys, JWT secrets, database URLs, and OAuth credentials must never appear
      in source code. They must come from environment variables loaded via pydantic-settings
      or Next.js runtime config.
    detector: "grep -rn 'SECRET\\|PASSWORD\\|API_KEY\\|DATABASE_URL' --include='*.py' --include='*.ts' | grep -v '.env'"
    recovery: "Move to .env file; load via BaseSettings (FastAPI) or process.env (Next.js). Add to .gitignore."

  - id: NO_UNTYPED_API_RESPONSE
    description: >
      Every FastAPI response must have an explicit response_model. Returning bare dicts
      bypasses Pydantic validation and breaks the TypeScript client contract.
    detector: "grep -n '@app.get\\|@router.get\\|@app.post' -- check for response_model="
    recovery: "Add response_model=YourResponseSchema to every route decorator."

  - id: NO_SQL_INJECTION_SURFACE
    description: >
      Raw string formatting in SQL queries (f-strings, .format(), % operator) is forbidden.
      All queries must use SQLAlchemy ORM, text() with bound parameters, or parameterized execute().
    detector: "grep -n 'execute(f\\|execute(\"' in SQLAlchemy code"
    recovery: "Replace with text('SELECT * FROM t WHERE id = :id').bindparams(id=user_id)"

  - id: NO_MIGRATION_WITHOUT_DOWNGRADE
    description: >
      Every Alembic migration must implement a working downgrade() function.
      pass in downgrade() is forbidden.
    detector: "grep -n 'def downgrade' migrations/versions/*.py | grep -A1 'def downgrade' | grep 'pass'"
    recovery: "Implement the inverse DDL operations in downgrade()."

  - id: NO_UNPROTECTED_STATE_MUTATING_ROUTE
    description: >
      POST/PUT/PATCH/DELETE endpoints must enforce authentication via Depends(get_current_user)
      or equivalent. No state-mutating route should be publicly accessible.
    detector: "Review FastAPI routes: every non-GET route must have a security dependency."
    recovery: "Add Depends(require_auth) or Depends(require_scope('write')) to route signature."
```

## Verification Extensions

```yaml
verification_extensions:
  rung_641:
    required_checks:
      - pytest_api_green: "pytest tests/api/ exits 0"
      - vitest_green: "npx vitest run exits 0"
      - typescript_clean: "npx tsc --noEmit exits 0"
      - no_hardcoded_secrets: "secret scan passes"
  rung_274177:
    required_checks:
      - playwright_e2e_green: "npx playwright test exits 0"
      - api_surface_snapshot_diff: "evidence/api_surface_before vs after reviewed"
      - migration_rollback_tested: "alembic downgrade -1 verified"
      - seed_data_stable: "test DB seeded with fixtures; same data across runs"
  rung_65537:
    required_checks:
      - security_scan: "bandit -r backend/ exits 0 with no HIGH findings"
      - adversarial_auth_test: "expired/tampered tokens return 401, not 500"
      - xss_csrf_review: "all user-controlled output escaped; CSRF tokens on mutations"
      - bundle_analysis: "next build --analyze; no secrets in client bundle"
```

## Quick Start

```bash
# Load this ripple and start a full-stack task
stillwater run --ripple ripples/web-fullstack.md --task "Add /api/v1/users/{id}/avatar upload endpoint"
```

## Example Use Cases

- Design and implement a new REST endpoint with Pydantic schema, FastAPI handler, pytest tests,
  and auto-generated TypeScript client types — all in one flow with API surface lock verification.
- Audit an existing auth flow for CSRF/XSS vulnerabilities, run bandit security scan,
  generate a security_scan.json evidence artifact, and produce a remediation patch.
- Create a Next.js Server Component page that fetches user-specific data, with explicit cache
  config, Playwright visual regression test, and bundle analysis to confirm no secret leakage.
