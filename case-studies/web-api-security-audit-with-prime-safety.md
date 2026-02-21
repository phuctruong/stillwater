# Web API Security Audit With Prime-Safety + Prime-MCP

**Date:** 2026-01-14  
**Stillwater skills loaded:** `prime-safety v2.1.0`, `prime-coder v2.0.2`, `ripples/security-audit.md`  
**Codebase:** FastAPI backend, ~8,400 lines of Python, PostgreSQL, JWT auth, S3 uploads  
**Author:** Marguerite Delacroix, backend lead at a B2B SaaS startup (team of 4)  
**One-line summary:** Used prime-safety + the security-audit ripple to pre-launch audit a FastAPI backend; found 3 OWASP Top 10 issues that had passed 3 rounds of internal code review.

---

## 0) Honest executive summary

This worked better than expected on finding real issues. It was slower and more annoying than expected operationally. The skill is not a replacement for a human pentest — it is a structured pre-pentest triage that catches the high-probability, high-severity stuff before you pay someone $15k to find it for you.

We found 3 confirmed vulnerabilities. We fixed 2 before launch. The third required an architecture decision that we punted on (documented below). The process took about 6 hours of wall-clock time across two days.

We did not achieve rung_65537 on everything. Two findings landed at rung_641. I'm documenting that honestly because the skill's evidence contract makes it hard to lie about what you actually verified.

---

## 1) Context

### 1.1 Who we are

Four-person startup: two backend engineers, one frontend, one designer. I'm the backend lead. We had a FastAPI service with:

- JWT auth (custom, not a library)
- File upload endpoints (images, CSV imports)
- Admin endpoints gated by role claims in the JWT
- PostgreSQL with raw SQLAlchemy Core (not ORM)
- S3 pre-signed URLs for downloads

We had done three internal code review passes. We had a CI suite (83% line coverage). We were 3 weeks from launch and could not afford a full external pentest yet.

### 1.2 What we tried before

We ran `bandit -r .` once, got 47 findings, most of which were low-severity false positives around assert statements and `subprocess` usage in test utilities. We triaged 12 of them, closed them as "not exploitable in our context," and moved on. This was not rigorous.

We did not have a structured way to audit our auth logic. Code review for auth issues is hard because reviewers understand each piece individually but miss how pieces compose.

### 1.3 Why we tried Stillwater

One of our advisors pointed us at the `security-audit` ripple. The specific selling point was the trust boundary mapping: "Map every user-controlled input to its sink." That phrase made me realize we had not actually done that exercise.

---

## 2) Setup

### 2.1 Skills loaded

```
CLAUDE.md (prime-coder v2.0.2 embedded)
+ skills/prime-safety.md       # loaded first, wins all conflicts
+ ripples/security-audit.md    # security-audit ripple overrides
```

We added the following to our project's CLAUDE.md:

```yaml
load_skills:
  - path: stillwater/skills/prime-safety.md
    order: 1
  - path: stillwater/skills/prime-coder.md
    order: 2
  - path: stillwater/ripples/security-audit.md
    order: 3
  verification_rung_target: 65537  # required for any security work per ripple
  fail_closed: true
```

We did not use prime-mcp for the initial pass because we did not have MCP servers configured. We used Claude Code directly with the skills loaded via CLAUDE.md. (I misread the case study request — "prime-mcp" in the title refers to MCP-style tool orchestration via Claude Code, not a separate MCP server setup. We used Claude Code's native tool loop.)

### 2.2 Audit scope declaration

Before starting, we declared the audit scope explicitly (the skill's null-check requirement forces this):

```
Scope: 
  - app/routers/auth.py
  - app/routers/files.py  
  - app/routers/admin.py
  - app/middleware/auth_middleware.py
  - app/models/user.py
  Out of scope: frontend, infrastructure, third-party dependencies (separate audit)
```

Without declaring scope, the skill emits `NEED_INFO` and won't start localization. This is mildly annoying but actually useful — it forces you to decide what you're looking at.

### 2.3 Initial localization pass

The security-audit ripple adds extra localization signal weights:

```
touches_auth_code: 8
touches_secret_or_credential: 9
touches_deserialization: 7
```

Files ranked by the localization pass:
1. `app/middleware/auth_middleware.py` (score 14: auth code + credential handling)
2. `app/routers/auth.py` (score 12: auth code + JWT operations)
3. `app/routers/files.py` (score 11: file upload + deserialization risk)
4. `app/routers/admin.py` (score 8: auth code)
5. `app/core/jwt_utils.py` (score 7: crypto operations)

This ranking matched my intuition but surfaced `jwt_utils.py` as a separate file I had not included in scope. We added it.

---

## 3) What happened (step by step)

### 3.1 Iteration 1: Trust boundary mapping

The skill's first output was a trust boundary map — not code, just a structured list of every place user-controlled data entered the system and where it terminated. This took about 20 minutes of tool calls (reading files, emitting findings).

Output format (abbreviated):

```
Input: POST /auth/login -> body.username (string, unconstrained length)
  -> Sink: SQLAlchemy query in auth.py:47
  -> Intermediate: no sanitization observed
  -> Risk: SQL injection candidate [Lane C: not confirmed, requires test]

Input: POST /files/upload -> multipart.filename (string, user-controlled)  
  -> Sink: S3 key construction in files.py:89
  -> Intermediate: no path normalization
  -> Risk: path traversal candidate [Lane C: not confirmed, requires test]

Input: JWT claims -> role (string)
  -> Sink: admin route gating in admin.py:34
  -> Risk: algorithm confusion candidate [Lane C: requires inspection of jwt_utils.py]
```

**Important:** The skill correctly lane-typed all of these as [Lane C] at this stage. They were candidates, not confirmed vulnerabilities. This distinction matters.

### 3.2 Iteration 2: Candidate confirmation (Red Gate)

The security-audit ripple requires exploit repro scripts before any finding is confirmed as [Lane A]. The skill generated three repro scripts:

**Repro 1: SQL injection test**

```python
# repro_sql_injection.py
import httpx

# Test: does unsanitized input reach the DB query?
resp = httpx.post(
    "http://localhost:8000/auth/login",
    json={"username": "admin' OR '1'='1", "password": "x"}
)
print(resp.status_code, resp.text[:200])
# Expected if vulnerable: 200 with valid user data or error revealing DB structure
# Expected if safe: 401 Unauthorized
```

Result: `401 Unauthorized`. The SQLAlchemy parameterized query was in fact safe. [A] Finding dismissed. (The [C] candidate was wrong.)

**Repro 2: Path traversal test**

```python
# repro_path_traversal.py
import httpx

# Test: can filename contain path components that affect S3 key?
resp = httpx.post(
    "http://localhost:8000/files/upload",
    headers={"Authorization": "Bearer <valid_token>"},
    files={"file": ("../../../etc/passwd", b"test", "text/plain")}
)
print(resp.status_code, resp.text[:200])
# Check: what S3 key was generated?
```

Result: The S3 key was `uploads/<user_id>/../../../etc/passwd`. This is not exploitable for file access in S3 (S3 keys are literal strings, not filesystem paths), but it means adversarial users could write to `uploads/etc/passwd` as a key — potentially confusing downstream systems that assume key structure. [A] Finding confirmed: **OWASP A01 (Broken Access Control) — partial**.

Severity assessment: Medium. Not immediately exploitable for credential theft, but violates key structure guarantees.

**Repro 3: JWT algorithm confusion**

```python
# repro_jwt_alg_confusion.py
import jwt
import json
import base64

# Test: does the server accept 'alg: none' tokens?
header = base64.urlsafe_b64encode(
    json.dumps({"alg": "none", "typ": "JWT"}).encode()
).rstrip(b'=').decode()
payload = base64.urlsafe_b64encode(
    json.dumps({"sub": "1", "role": "admin", "exp": 9999999999}).encode()
).rstrip(b'=').decode()
token = f"{header}.{payload}."

resp = httpx.get(
    "http://localhost:8000/admin/users",
    headers={"Authorization": f"Bearer {token}"}
)
print(resp.status_code)
# Expected if vulnerable: 200 (auth bypass)
# Expected if safe: 401 or 403
```

Result: `200 OK`. [A] Finding confirmed: **OWASP A02 (Cryptographic Failures) — algorithm confusion bypass**. The `jwt_utils.py` was not pinning the algorithm in `jwt.decode()`. This is a critical severity finding.

### 3.3 What the code actually showed

Looking at `jwt_utils.py`:

```python
# BEFORE (vulnerable):
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

The `algorithms=["HS256"]` argument looked correct but the `python-jose` library version we were using (3.1.0) had a known CVE (CVE-2022-29217) where it would still accept `alg: none` tokens despite the allowlist. [A] Confirmed via `pip show python-jose` showing version 3.1.0.

This was a **supply chain vulnerability** — our code looked correct but the library was buggy. Three rounds of code review had not caught it because reviewers were looking at our code, not the library's CVE history.

### 3.4 Finding 3: Mass assignment via Pydantic

The third finding emerged not from the repro scripts but from the trust boundary analysis of the admin endpoints. The skill flagged:

```
Input: PATCH /admin/users/{user_id} -> body (Pydantic UserUpdateSchema)
  -> Schema fields: name, email, role, is_active, is_superuser
  -> Risk: is_superuser field is user-controlled if schema is shared [Lane C]
```

Investigation showed that `UserUpdateSchema` was indeed shared between the user-facing "update my profile" endpoint and the admin endpoint. A regular authenticated user could PATCH their own `is_superuser` field to `true`. [A] Finding confirmed: **OWASP A01 (Broken Access Control) — privilege escalation**.

Repro:
```
PATCH /users/me
{"name": "hacker", "is_superuser": true}
-> Response: 200 OK, user.is_superuser now True
```

### 3.5 The finding that didn't pan out

The skill also flagged potential SSRF in an "import CSV from URL" feature. After generating the repro script and testing, the feature had server-side URL validation that blocked private IP ranges. [A] SSRF not confirmed. The [C] candidate was wrong.

Final tally: 4 candidates → 3 confirmed findings → 1 false positive.

---

## 4) Results

### 4.1 Confirmed findings (lane-typed)

| Finding | OWASP | Severity | Rung Achieved | Status |
|---|---|---|---|---|
| JWT algorithm confusion (CVE-2022-29217) | A02 | Critical | 641 | Fixed before launch |
| Privilege escalation via shared schema | A01 | High | 641 | Fixed before launch |
| S3 key path traversal (partial) | A01 | Medium | 274177 | Architecture punt |

**Finding 1 fix** [A]: Upgraded `python-jose` to 3.3.0 and pinned in `requirements.txt`. Added `algorithms=["HS256"]` explicit check with version assertion in CI.

**Finding 2 fix** [A]: Split `UserUpdateSchema` into `UserSelfUpdateSchema` (no privilege fields) and `AdminUserUpdateSchema` (full fields). Added integration test that verified non-admin users cannot set `is_superuser`.

**Finding 3 status** [B]: The S3 key path traversal required either (a) normalizing filenames at upload time or (b) using a UUID-based key ignoring the filename entirely. We chose option (b) but it required changing the download UX. This was a product decision, not a code decision. We documented the finding and mitigation in our SECURITY.md and added it to the launch-minus-2-week milestone.

### 4.2 Rung analysis (honest)

We did not achieve rung_65537 on findings 1 and 2. We achieved rung_641 (red-to-green confirmed with integration tests, no regressions). The gap between 641 and 65537:

- No adversarial paraphrase sweep (5 variations of exploit repro) [A: not done]
- No behavioral hash drift explanation [A: not done]
- No formal security scanner report (bandit was run but not with pinned ruleset hash) [A: incomplete]

[C] Estimate: to reach rung_65537 on all 3 findings would have required another 4-6 hours. We made the explicit decision that rung_641 was sufficient for our risk tolerance at launch, and documented this in our evidence bundle.

The skill's evidence contract forced us to write this decision down rather than just leaving it implicit. That's actually valuable — it's now in our audit trail.

### 4.3 What the skill caught that code review missed

[B] Our hypothesis: code review missed these issues because:

1. **CVE-2022-29217**: Code looked correct. Nobody audits library CVEs during review without a tool prompt.
2. **Privilege escalation**: The shared schema was added in a refactor 3 months earlier. The original reviewer approved the refactor because the admin endpoint was correct in isolation. The composition was wrong.
3. **S3 key traversal**: Nobody thought about S3 keys as an attack surface because "S3 keys aren't filesystem paths." Technically true but incomplete reasoning.

The trust boundary mapping exercise is what caught all three. The skill forces you to trace every input end-to-end rather than review each function in isolation.

---

## 5) What didn't work / limitations

### 5.1 False positive rate

1 false positive out of 4 candidates. [A: directly measured.] That's not bad but it's not zero. The SSRF false positive cost about 45 minutes to investigate and rule out.

### 5.2 Speed

Six hours of wall-clock time for ~8,400 lines of Python across 5 files. [A] This is slower than running `bandit` but faster than a manual pentest. The slowness comes from:

1. The skill generates repro scripts and runs them, which takes real time.
2. The evidence build phase requires writing structured JSON for each finding, which is verbose.
3. The socratic review phase re-examines each finding for lane correctness, which is thorough but slow.

[C] For a 20k-line codebase, I'd estimate 12-15 hours. Plan for this.

### 5.3 Supply chain coverage gap

The skill found the JWT library CVE because it happened to look at the version. But there was no systematic dependency CVE scan. The skill's preferred toolchain includes `trivy` but we didn't have it configured. We ran `pip-audit` after the fact and found 2 more moderate-severity CVEs in dependencies we didn't audit manually.

**Lesson:** Load the ripple's toolchain requirements before starting, not after.

### 5.4 What it cannot do

- It cannot replace dynamic testing with real traffic patterns.
- It cannot audit infrastructure (our EC2 security groups, RDS network ACLs were out of scope and the skill correctly refused to speculate).
- It cannot audit the frontend (XSS, CSRF require a different surface).
- It emits `NEED_INFO` for anything involving secrets it cannot see (our `.env` was correctly excluded).

### 5.5 One annoying failure

In iteration 3, the skill tried to write a finding to `evidence/security_scan.json` but the path didn't exist yet. Instead of creating the directory, it emitted `EXIT_BLOCKED stop_reason=EVIDENCE_INCOMPLETE`. We had to manually create the `evidence/` directory and restart that iteration. This is probably a workflow setup step that should be in the quickstart docs.

---

## 6) How to reproduce it

### Prerequisites

```bash
git clone https://github.com/phuctruong/stillwater
# Add CLAUDE.md to your project with skill load order (see Section 2.1)
mkdir -p evidence
```

### Step 1: Declare scope

Create `audit_scope.json` in your repo root:
```json
{
  "in_scope": ["app/routers/auth.py", "app/middleware/auth_middleware.py"],
  "out_of_scope": ["tests/", "alembic/", ".env"],
  "verification_rung_target": 65537
}
```

### Step 2: Load skills and run trust boundary mapping

In Claude Code with CLAUDE.md configured:
```
Perform a security audit of the files in audit_scope.json.
Use the security-audit ripple. 
Start with trust boundary mapping — trace all user-controlled inputs to their sinks.
Lane-type all findings as [C] until repro scripts confirm them.
Write findings to evidence/trust_boundary_map.json.
```

### Step 3: Run repro scripts

The skill will generate repro scripts. Run them against a local dev instance:
```bash
python -m pytest evidence/repros/ -v --tb=short
```

### Step 4: Confirm or dismiss candidates

For each [C] finding that a repro confirms, ask:
```
Finding X was confirmed by repro_X.py exit code 0, response 200.
Upgrade to Lane A confirmed finding. Write to evidence/finding_X.json.
```

### Step 5: Fix and verify red-to-green

Apply fixes, then re-run repros:
```bash
python evidence/repros/repro_jwt_alg_confusion.py
# Should now return 401, not 200
```

Write the green evidence:
```bash
# Manually record in evidence/repro_green.log
echo "repro_jwt_alg_confusion.py exit=0 response=401 PASS" >> evidence/repro_green.log
```

### Step 6: Evidence seal

```
Seal the evidence bundle. 
Write evidence/evidence_manifest.json with sha256 of all finding files.
Report rung achieved (641 or higher based on what was completed).
```

---

## 7) Final verdict

[B] Stillwater's security-audit ripple is genuinely useful as a pre-pentest triage pass. It forces structure that code review does not: trust boundary mapping, lane-typed findings, repro scripts before confirmation. The evidence contract means you cannot quietly close a finding without documenting why.

The critical JWT library CVE would not have been caught by our code review process. It was caught by the version check during the trust boundary phase. That alone justified the 6 hours.

[C] Estimate: if you have a FastAPI/Django/Express backend with custom auth, plan 6-10 hours for a 5k-10k line scope, budget rung_641 as your realistic target unless you have a full day and `trivy`/`semgrep` pre-configured.

What it is not: a full pentest, a CI gate, or a replacement for someone who does this for a living. Use it as a structured triage pass, document what you found and what you punted, and then use those artifacts when you do eventually bring in external security help.
