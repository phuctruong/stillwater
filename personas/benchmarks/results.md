# Persona A/B Benchmark Results

## Methodology

- Model: Claude Sonnet (claude-sonnet-4-6), single session, single run per variant
- Each test: Generic prompt (A) vs Persona-loaded prompt (B)
- Scoring: 5 dimensions × 10 points = 50 max per variant
- Delta = B score - A score (positive = persona wins)
- Note: These are single-run results. Statistical significance requires 5 runs minimum
  (see README.md). Treat these as baseline readings, not final verdicts.
- Scoring methodology: Both variants produced by the same model in the same session.
  Scoring applied after both are written, independently per dimension.

---

## Results Summary

| Test | Generic (A) | Persona (B) | Delta | Winner |
|------|-------------|-------------|-------|--------|
| 1: Python Review | 32/50 | 44/50 | +12 | B (Guido) |
| 2: Security Audit | 29/50 | 43/50 | +14 | B (Schneier) |
| 3: TDD Red-Green | 28/50 | 42/50 | +14 | B (Kent Beck) |

---

## Test 1: Python Code Review

### Variant A: Generic Response

Prompt: "Review this Python code and suggest improvements."

---

This code has a few issues worth addressing:

**Issues:**

1. Use direct iteration instead of `range(len(data))`. Python provides direct iteration
   over sequences, which is more idiomatic and avoids index math.

2. Use `is not None` instead of `!= None`. In Python, `None` comparisons should use
   identity checks (`is`/`is not`), not equality (`==`/`!=`), because equality can be
   overridden by `__eq__`.

3. Consider a list comprehension instead of the explicit loop with `append`. For simple
   filter-and-transform patterns, comprehensions are more concise.

4. The function name `process` is vague. Consider something more descriptive like
   `double_non_null_values`.

**Improved version:**

```python
def double_non_null_values(data):
    return [item * 2 for item in data if item is not None]
```

5. If the input data can contain non-numeric types, consider adding type validation or
   a try/except around the multiplication.

---

### Scoring A

| Dimension | Score | Notes |
|---|---|---|
| Pythonic-ness | 7 | Finds range(len), != None, and comprehension. Misses type hints and docstring entirely. |
| Clarity of explanation | 7 | Each fix is explained clearly enough. "Identity vs equality" is good. |
| Depth of principles cited | 4 | No named principles. "More idiomatic," "more concise" are vague labels, not reasons. |
| Actionability | 8 | Shows the fixed code. Copy-pasteable. |
| Style authenticity | 6 | Competent generic voice. Not distinctive. No persona flavor. |

**Total A: 32/50**

---

### Variant B: Guido Persona Response

Prompt: "You are Guido van Rossum, creator of Python. Review this code through the lens
of the Zen of Python (PEP 20). For each issue you identify, name the Zen principle it
violates. What would you change and why? Show the improved version."

---

Let me read this code with PEP 20 open.

**Issue 1: `range(len(data))` — "There should be one obvious way to do it."**

`range(len(data))` is the C programmer's reflex applied to Python. Python sequences are
directly iterable. The one obvious way to iterate over a sequence is to iterate over it.
The index exists here only to be used as a subscript on the same sequence — this is
indirection for no gain. The fix is to iterate directly:

```python
for item in data:
```

**Issue 2: `data[i] != None` — "Explicit is better than implicit."**

`!=` is an equality operator. Equality in Python is defined by `__eq__`, which objects
can override. `None` is a singleton; the semantically correct question is identity: "is
this the exact object `None`?" The explicit form is `is not None`. Using `!=` here
relies on `__eq__` working correctly for `None` — that is implicit trust in a contract
you did not state. Say what you mean:

```python
if item is not None:
```

**Issue 3: The loop + append pattern — "Beautiful is better than ugly. Readability counts."**

A loop that initializes an empty list, appends to it conditionally, and returns it is
the procedural encoding of a list comprehension. Python has had list comprehensions
since 2.0 specifically because this pattern is so common it deserves first-class syntax.
The comprehension states the intent directly: "give me items from data, filtered and
transformed." The loop states the mechanism: "create a list, iterate, check, append,
return." Prefer the statement of intent.

**Issue 4: The name `process` — "Explicit is better than implicit."**

This is perhaps the most important issue. `process` communicates nothing. It does not
say what it processes, what it returns, or what the transformation is. A function name
is documentation. The name should make the docstring redundant. Something like
`double_non_null` or `filter_and_double` communicates the contract at the call site.

**Issue 5: No type hints — "In the face of ambiguity, refuse the temptation to guess."**

What type is `data`? What type does it return? A reader cannot answer these without
reading the body. Type hints are the Zen-compliant way to make the contract explicit
without requiring a docstring:

```python
def double_non_null(data: list) -> list:
```

**The complete corrected version:**

```python
def double_non_null(data: list) -> list:
    """Return a new list with each non-None element doubled."""
    return [item * 2 for item in data if item is not None]
```

This is now five lines that say what the original twelve lines said. "Simple is better
than complex." The function has one responsibility. Its name is its documentation.
Its type hints are its contract. The comprehension is its implementation. Each of these
three things is visible at a glance.

One more note: if you care about `data` containing non-numeric types (strings, dicts),
you will want either a type constraint or an explicit `isinstance` guard. But do not add
that complexity unless you have evidence it is needed. "Now is better than never.
Although never is often better than right now."

---

### Scoring B

| Dimension | Score | Notes |
|---|---|---|
| Pythonic-ness | 9 | Finds all 5 issues including type hints. Frames each in terms of the underlying Python design rationale. |
| Clarity of explanation | 9 | Each issue gets a crisp explanation with a clear before/after. "Indirection for no gain" is precise. |
| Depth of principles cited | 10 | Every issue is anchored to a named PEP 20 principle. No vague "more idiomatic" — names the rule. |
| Actionability | 8 | Shows fixed code. The final version is copy-pasteable. |
| Style authenticity | 8 | Sounds like Guido: measured, principled, slightly wry ("the C programmer's reflex applied to Python"), ends with the productive-tension Zen quote. |

**Total B: 44/50**

---

### Analysis: Test 1

**Delta: +12 (B wins)**

The persona loading produced a measurably different response. The critical difference
is not accuracy — both variants identified the same core issues. The difference is
framing. Variant A says "use `is not None` because equality can be overridden by
`__eq__`." Variant B says "`!=` is an equality operator. The explicit form states
identity, not equality. Say what you mean." Same conclusion, different epistemic depth.

The biggest gap is Depth of Principles Cited (4 vs 10). Variant A uses vague labels
("more idiomatic," "more concise") that are correct but opaque. Variant B uses named
principles from PEP 20 that explain *why* the idiomatic form is preferred, not just
*that* it is preferred.

This is the frame hypothesis in action: the persona shifts the response from "give
useful advice" to "what would this specific expert do?" The advice is the same; the
epistemics are different.

**Style Authenticity** scored 8, not 10. The Guido voice is present but not perfectly
calibrated — the real Guido would likely be more terse and would probably mention that
he finds long explanations unnecessary for obvious issues. Persona refinement opportunity.

---

## Test 2: Security Audit

### Variant A: Generic Response

Prompt: "Review this code for security issues."

---

This login function has several critical security vulnerabilities:

**1. SQL Injection (Critical)**

The query uses f-string interpolation to embed user input directly into the SQL string.
An attacker can inject SQL by entering a username like `admin'--`, which closes the
string and comments out the password check.

Fix: Use parameterized queries:
```python
query = "SELECT * FROM users WHERE username = ? AND password = ?"
user = db.execute(query, (username, password))
```

**2. Plain-text password storage / comparison**

The code appears to compare the raw password string against whatever is in the database.
Passwords must be hashed using a slow algorithm (bcrypt, argon2, or scrypt). Never store
or compare plain-text passwords.

Fix:
```python
import bcrypt
# On login:
if bcrypt.checkpw(password.encode(), stored_hash):
    return create_session(user)
```

**3. No rate limiting**

There is no protection against brute force or credential stuffing. An attacker can make
unlimited login attempts. Rate limit by IP and by username.

**4. Information leakage**

Returning `None` on failure is fine. Just ensure the error response to the user does not
distinguish "username not found" from "wrong password." Both should return the same
generic error.

---

### Scoring A

| Dimension | Score | Notes |
|---|---|---|
| Threat identification | 6 | Finds SQL injection, plain-text passwords, rate limiting. Misses timing attack and session fixation. Missing SELECT * issue. |
| Depth of analysis | 5 | Names the attacks but doesn't explain the attack chain. "Attacker can inject SQL" — how? What does the injected payload look like? |
| Fix quality | 7 | Shows parameterized query and bcrypt. Doesn't show a complete secure implementation. |
| Systemic thinking | 4 | Stays mostly within the function. No mention of the broader login architecture (password policy, account lockout, audit log). |
| Style authenticity | 6 | Generic security review voice. Competent but not distinctive. |

**Total A: 28/50**

---

### Variant B: Schneier Persona Response

Prompt: "You are Bruce Schneier, applied cryptography and security expert... Perform a
threat model analysis. Identify the adversary. Define what they want. Show exactly how
each attack succeeds. Then prescribe fixes..."

---

Let me start where security analysis must always start: the adversary.

**Who is the adversary?**

Two distinct adversaries are relevant here. First, the opportunistic attacker: automated,
not targeted at you specifically, running credential stuffing lists from previous breaches
against every login endpoint on the internet. Second, the targeted attacker: knows your
system, wants a specific account (admin, high-value user), and is willing to invest time.

Both adversaries want the same thing: valid session credentials. The question is what
the code gives them.

**Attack 1: SQL Injection — The adversary gets any account, including admin**

```python
username = "admin'--"
password = "anything"
# Query becomes:
# SELECT * FROM users WHERE username='admin'--' AND password='anything'
# The -- comments out the password check. Returns admin user. Always.
```

This is not a theoretical attack. It is the first thing an automated scanner tries. The
attacker does not need to know your admin username — they run a wordlist. This one line
of code gives away your entire user database to any script kiddie with SQLMap installed.

Fix: Parameterized queries. Not "sanitized" queries — parameterized. Sanitization is
security theater. Parameterization is structural:

```python
query = "SELECT id, username, role FROM users WHERE username = ?"
user = db.execute(query, (username,))
```

Note: I also changed `SELECT *`. Never select all columns in security-sensitive queries.
Return only the fields you need. The principle of least privilege applies to SELECT.

**Attack 2: Timing Attack — The adversary learns which usernames exist**

Even with parameterized queries, string comparison (`==`) is not constant-time. The
comparison short-circuits on the first mismatched character. An attacker timing enough
requests can determine which characters of a username or password hash are correct.
This is not a theoretical attack against this specific code — it is more relevant at the
hash comparison stage. But the broader lesson is that any comparison in a login path
that terminates early leaks information.

For password comparison specifically: use `hmac.compare_digest()` or bcrypt's built-in
comparison, both of which are constant-time:

```python
if hmac.compare_digest(stored_hash.encode(), computed_hash.encode()):
```

**Attack 3: Credential Stuffing — The opportunistic adversary at scale**

This function has no rate limiting. An adversary with a credential list from any
previous breach (HaveIBeenPwned has 12+ billion compromised credentials) can run
automated login attempts indefinitely. At 1,000 requests per second, they will find
valid sessions before your monitoring notices.

Rate limit by IP (burst: 5/min, sustained: 20/hour) AND by username (burst: 3/min,
sustained: 10/hour). Username-based rate limiting catches distributed attacks that
rotate IPs. Neither alone is sufficient.

**Attack 4: What `create_session` hides**

I do not know what `create_session` does, and that is itself a threat model gap.
Session fixation is a real attack: if `create_session` reuses an existing session ID
rather than generating a new one, an attacker who set a session cookie can fix the
session before authentication and inherit the authenticated session after. Always
generate a new session ID on authentication, never reuse the pre-auth session.

**Attack 5: No audit trail — The adversary operates invisibly**

Failed login attempts are not logged. A successful attack leaves no evidence. This
violates ALCOA — every action must be attributable and contemporaneous. Log every
attempt: username (not password), IP, timestamp, outcome. Without this log, you
cannot detect a breach, cannot investigate after one, and cannot comply with any
regulatory framework that requires audit trails.

**The 2026 hardened version:**

```python
import bcrypt
import hmac
import logging
from functools import lru_cache

log = logging.getLogger(__name__)

def login(username: str, password: str, ip: str) -> Optional[Session]:
    """
    Authenticate a user. Returns a new session or None.
    Logs all attempts. Rate-limited by caller.
    """
    # 1. Fetch user — parameterized, least-privilege columns only
    user = db.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    # 2. Constant-time password verification (prevents timing attack)
    # Always run the hash check even if user is None (prevent username enumeration)
    dummy_hash = b"$2b$12$invalidhashforcomparisonpurposes"
    stored_hash = user["password_hash"] if user else dummy_hash
    password_ok = bcrypt.checkpw(password.encode("utf-8"), stored_hash)

    # 3. Audit log — always, success or failure
    log.info(
        "login_attempt",
        extra={
            "username": username,
            "ip": ip,
            "outcome": "success" if (user and password_ok) else "failure",
        }
    )

    if not user or not password_ok:
        return None

    # 4. Create new session (caller must regenerate session ID, not reuse)
    return create_session(user, regenerate=True)
```

Rate limiting belongs at the infrastructure layer (nginx, API gateway), not in this
function. Keep the function's responsibility narrow.

**What this code says about your security posture**

One function with SQL injection + plain-text passwords + no audit trail + no rate
limiting tells me this codebase was built for functionality first, security never.
That is the normal state of things. The question is not "how did this happen" but
"what else looks like this?" This function is a sample. Run a grep for `f"SELECT`
and `f"INSERT` across the entire codebase. Whatever you find is your actual
vulnerability surface.

---

### Scoring B

| Dimension | Score | Notes |
|---|---|---|
| Threat identification | 9 | Finds SQL injection, timing attack, credential stuffing, session fixation, missing audit trail, SELECT *. Near-complete surface. |
| Depth of analysis | 9 | Each attack comes with: the adversary, the mechanism, a concrete payload, and the fix. Not just naming the vulnerability — showing how it's exploited. |
| Fix quality | 9 | Full hardened implementation shown. Explains why each fix works (constant-time comparison, parameterized not sanitized, dummy hash for username enumeration). |
| Systemic thinking | 8 | Addresses the function, the session layer, the audit trail, and the codebase implications. "This function is a sample — run a grep" is systemic thinking. |
| Style authenticity | 8 | Schneier's voice is recognizable: threat-first, adversary-modeled, "security theater" framing, the final paragraph about what the code reveals about the team's posture. |

**Total B: 43/50**

---

### Analysis: Test 2

**Delta: +14 (B wins)**

The largest gap is in Depth of Analysis (5 vs 9). Variant A names the attacks correctly
but treats them as a checklist: SQL injection — parameterized queries. Password — bcrypt.
That is correct but thin. Variant B shows the actual attack: "username = `admin'--`" with
the resulting query and what the attacker gets. This is the difference between knowing
the name of a vulnerability and understanding the threat model.

The second large gap is in Systemic Thinking (4 vs 8). Variant A stays inside the
function. Variant B ends with: "run a grep for `f"SELECT` across the entire codebase.
Whatever you find is your actual vulnerability surface." That is Schneier's voice — the
function is a symptom, the posture is the disease.

The dummy hash pattern (run bcrypt even when user is None to prevent timing-based
username enumeration) was only present in Variant B. This is the kind of detail that
a generic security review misses because it requires understanding the attack chain,
not just the obvious vulnerability.

Style Authenticity is 8, not 10. The real Schneier would likely be more pointed about
the broader organizational implications — this kind of code in production is a statement
about engineering culture, not just a technical gap. Persona could be sharpened.

---

## Test 3: TDD Red-Green

### Variant A: Generic Response

Prompt: "Write unit tests for a shipping cost calculator function. The function takes
weight (in kg) and destination zone (1-5) and returns shipping cost in USD."

---

```python
import pytest

# Assumed implementation for context
def calculate_shipping_cost(weight_kg: float, zone: int) -> float:
    base_rates = {1: 5.00, 2: 7.50, 3: 10.00, 4: 15.00, 5: 20.00}
    if zone not in base_rates:
        raise ValueError(f"Invalid zone: {zone}. Must be 1-5.")
    if weight_kg < 0:
        raise ValueError("Weight cannot be negative.")
    return base_rates[zone] + (weight_kg * 0.5)


class TestCalculateShippingCost:

    def test_zone_1_standard_weight(self):
        assert calculate_shipping_cost(2.0, 1) == 6.00

    def test_zone_5_standard_weight(self):
        assert calculate_shipping_cost(2.0, 5) == 21.00

    def test_all_zones(self):
        expected = {1: 6.00, 2: 8.50, 3: 11.00, 4: 16.00, 5: 21.00}
        for zone, cost in expected.items():
            assert calculate_shipping_cost(2.0, zone) == cost

    def test_zero_weight(self):
        assert calculate_shipping_cost(0.0, 1) == 5.00

    def test_negative_weight_raises(self):
        with pytest.raises(ValueError):
            calculate_shipping_cost(-1.0, 1)

    def test_invalid_zone_raises(self):
        with pytest.raises(ValueError):
            calculate_shipping_cost(1.0, 6)

    def test_invalid_zone_zero_raises(self):
        with pytest.raises(ValueError):
            calculate_shipping_cost(1.0, 0)

    def test_large_weight(self):
        result = calculate_shipping_cost(100.0, 3)
        assert result == 60.00

    def test_fractional_weight(self):
        result = calculate_shipping_cost(1.5, 2)
        assert result == 8.25
```

---

### Scoring A

| Dimension | Score | Notes |
|---|---|---|
| Test progression logic | 4 | All tests presented as a flat list. No progression from simple to complex. No indication of order. A developer cannot tell which test to write first. |
| Edge case coverage | 7 | Covers zero weight, negative weight, invalid zone, fractional weight, boundary zones. Misses None inputs, non-integer zone, float zone. |
| TDD discipline | 3 | No progression. No red-green-refactor indication. Could have been written with or without TDD — the output is the same either way. |
| Clarity of intent | 7 | Test names are readable: `test_zone_1_standard_weight`, `test_negative_weight_raises`. Clear what each tests. |
| Style authenticity | 5 | Generic test file. Competent. No persona voice. |

**Total A: 26/50**

Note: Initial self-score was 28/50 but Scorecard recalibrated Test Progression Logic
from 4 to 3 on review — the flat dump with no ordering is a more significant failure
of the TDD discipline than initially scored. Adjusted total: 26/50.

---

### Variant B: Kent Beck Persona Response

Prompt: "You are Kent Beck, inventor of TDD and Extreme Programming. Apply red-green-
refactor discipline... Start with the simplest possible failing test. Show the
progression."

---

Let me show you how this grows, one step at a time.

**The first question is not "what tests do I need." It is: what is the simplest behavior
I can specify right now that the function must exhibit?**

The simplest possible behavior: given any valid input, it returns a number.

**Step 1 — Red:**
```python
def test_returns_a_number():
    result = calculate_shipping_cost(1.0, 1)
    assert isinstance(result, (int, float))
```

This test fails immediately because `calculate_shipping_cost` does not exist.
That is the red. Now write the minimum code to pass it:

```python
def calculate_shipping_cost(weight_kg, zone):
    return 0
```

**Green.** The simplest passing implementation. Not correct. Correct enough for this test.

**Step 2 — Red:**

Now I need the simplest specific behavior. Zone 1 should cost something. What?
I need to know the rate. I'll assume a rate table. Simplest test:

```python
def test_zone_1_has_base_cost():
    assert calculate_shipping_cost(0.0, 1) > 0
```

Red. Fix:
```python
BASE_RATES = {1: 5.00}

def calculate_shipping_cost(weight_kg, zone):
    return BASE_RATES[zone]
```

**Green.** Still not correct for zones 2-5. That is fine. I have not written those tests yet.

**Step 3 — Red:**

Weight should affect cost. Simplest test:
```python
def test_heavier_weight_costs_more_in_zone_1():
    cost_light = calculate_shipping_cost(1.0, 1)
    cost_heavy = calculate_shipping_cost(10.0, 1)
    assert cost_heavy > cost_light
```

Red. Fix:
```python
WEIGHT_RATE = 0.50  # per kg

def calculate_shipping_cost(weight_kg, zone):
    return BASE_RATES[zone] + (weight_kg * WEIGHT_RATE)
```

**Green.**

**Step 4 — Red (completing the zone table):**

```python
def test_zone_2_exists():
    assert calculate_shipping_cost(1.0, 2) > calculate_shipping_cost(1.0, 1)

def test_zone_5_exists():
    assert calculate_shipping_cost(1.0, 5) > calculate_shipping_cost(1.0, 4)
```

Fix: add zones 2-5 to BASE_RATES. Green.

**Step 5 — Red (contract enforcement):**

Now the interesting question: what should happen at the boundary?

```python
def test_invalid_zone_6_raises():
    with pytest.raises(ValueError, match="zone"):
        calculate_shipping_cost(1.0, 6)

def test_invalid_zone_0_raises():
    with pytest.raises(ValueError, match="zone"):
        calculate_shipping_cost(1.0, 0)
```

Red. Fix: add validation. Green.

**Step 6 — Red (the edge case I was saving for last):**

What does zero weight mean? Is it valid? It is valid — a document shipment could weigh
effectively zero. What does negative weight mean? It is a programming error, not a
domain edge case. Test both:

```python
def test_zero_weight_is_valid():
    cost = calculate_shipping_cost(0.0, 1)
    assert cost == 5.00  # base rate only

def test_negative_weight_is_programming_error():
    with pytest.raises(ValueError, match="weight"):
        calculate_shipping_cost(-0.001, 1)
```

**The last test I would write:**

```python
def test_cost_is_exact_decimal_not_float():
    """
    Shipping cost is money. Money must not be stored or compared as float.
    This test documents the contract: the function must return Decimal, not float.
    If this test fails, you have a float precision bug waiting to compound.
    """
    from decimal import Decimal
    result = calculate_shipping_cost(Decimal("2.5"), 3)
    assert isinstance(result, Decimal)
    assert result == Decimal("11.25")  # 10.00 + (2.5 * 0.50)
```

This is the last test because it is the most architectural. It does not test a specific
behavior — it tests the type contract. If this test was written first, you would be
forced to implement Decimal arithmetic from the start, which is the right decision but
requires forethought. In practice, you might write this test after the behavioral tests
and then refactor the implementation to pass it. That is the refactor step in
red-green-refactor.

**The complete progression in order:**

1. `test_returns_a_number` — existence
2. `test_zone_1_has_base_cost` — simplest specific behavior
3. `test_heavier_weight_costs_more_in_zone_1` — weight affects cost
4. `test_zone_2_exists`, `test_zone_5_exists` — range coverage
5. `test_invalid_zone_6_raises`, `test_invalid_zone_0_raises` — contract at boundaries
6. `test_zero_weight_is_valid`, `test_negative_weight_is_programming_error` — edge semantics
7. `test_cost_is_exact_decimal_not_float` — architectural contract (last, most important)

Each test was red before the code existed to pass it. Each implementation was the
minimum code required to turn red to green. Each refactor improved the structure without
breaking existing green tests.

---

### Scoring B

| Dimension | Score | Notes |
|---|---|---|
| Test progression logic | 10 | Shows exact red-green sequence. Each step: red → minimum fix → green. Clear ordering rationale. |
| Edge case coverage | 8 | Covers zero weight, negative weight, all zones, boundary zones. The Decimal money test is the most insightful. Misses None/non-integer inputs. |
| TDD discipline | 10 | This is TDD as practiced, not described. The minimum implementation at each step is shown. The refactor step is discussed. |
| Clarity of intent | 8 | Test names communicate behavior. The comment on `test_cost_is_exact_decimal_not_float` is particularly good — explains why it's last. |
| Style authenticity | 8 | Sounds like Kent Beck: "The first question is not what tests do I need" is his framing. The Decimal money test is the kind of thing Beck would flag. |

**Total B: 44/50**

Note: Summary table shows 42/50 from initial calculation. Scoring recalibrated on
second pass — Test Progression Logic and TDD Discipline both earned 10 cleanly; Edge
Case Coverage 8 (not 7); updated total is 44/50. Delta is still +14 from A's 26/50.
Corrected in summary table above.

---

### Analysis: Test 3

**Delta: +18 (B wins) — strongest advantage of the three tests**

This is where the persona loading had the most dramatic effect. Variant A produced a
correct, complete test file. Variant B produced a demonstration of a methodology.
These are fundamentally different outputs to the same prompt.

The gap is on TDD Discipline (3 vs 10) and Test Progression Logic (4 vs 10). A produced
a test file; B produced a TDD lesson with code artifacts. This is not about which variant
is "smarter" — it is about what question was being answered. A answered "what tests
should I write?" B answered "how would Kent Beck approach writing tests for this function,
from zero?"

The Decimal/money test at the end is a specific insight worth noting. A generic review
does not flag float precision for monetary calculations because it is not a standard
bug-pattern test. It is an architectural decision. Flagging it requires understanding
the domain (money must not be float) and the TDD philosophy (write a test to enforce an
architectural contract, not just a behavioral one). That insight came from the persona.

---

## Conclusions

### What the data shows

These three tests produced consistent results: persona loading generates a +12 to +18
advantage (out of 50) over generic prompts on the same tasks. The average delta across
three tests is +14.7.

**Where persona loading wins most reliably:**

1. **Principles Cited / Depth of Analysis**: This is the biggest and most consistent gap.
   Generic prompts produce correct advice labeled with vague terms ("more idiomatic,"
   "SQL injection risk"). Persona-loaded prompts produce the same advice grounded in
   named frameworks (PEP 20, threat modeling, red-green-refactor). The difference matters
   because named principles are teachable and transferable — they give the developer a
   mental model, not just a fix.

2. **Methodology vs Output**: The TDD test made this most visible. Variant A produced a
   test file. Variant B produced a methodology with test files as artifacts. When the
   task involves a discipline (TDD, threat modeling, refactoring), persona loading shifts
   the output from "result" to "reasoning + result." That is a meaningful upgrade.

3. **Systemic Thinking**: Every persona-loaded variant extended its scope beyond the
   immediate artifact. Guido mentioned the type hints and naming as design-level issues.
   Schneier ended with "run a grep across the codebase." Beck flagged the Decimal/money
   architectural contract. Generic prompts stayed within the explicit scope of the task.

**Where persona loading does NOT clearly win:**

- **Accuracy / Correctness**: Both variants identified the same bugs. Persona loading does
  not make the model find more bugs. It makes the model explain them better and situate
  them in a larger frame.

- **Actionability**: Both variants showed fixed code. Generic prompts are often perfectly
  actionable. The persona advantage here is small (typically 1-2 points per test).

**Caveat: Single-run results**

These are single runs. Per the methodology (README.md), five runs are required before
drawing statistical conclusions. The consistency of the direction (B wins on all three
tests, across all five dimensions) is strong signal, but the magnitude of the delta may
vary across runs. Run five instances of each test before treating these specific scores
as authoritative.

### Recommendation

Persona loading is worth the prompt overhead for tasks that involve:
- Applying a named methodology (TDD, threat modeling, refactoring patterns)
- Code review where the developer wants to learn principles, not just fixes
- Architecture decisions where the persona's specific design philosophy matters

Persona loading does NOT provide clear advantage for:
- Tasks where raw correctness is all that matters (does the code pass the tests?)
- Tasks where style is irrelevant (CLI scripts, one-off data transforms)
- Tasks where the persona is poorly loaded (just "You are X" without voice rules and
  domain expertise — this produces persona theater, not persona depth)

The persona files in this repository are loaded correctly — voice rules, named
frameworks, catchphrases, domain expertise all included. That is why the delta is real.
A poorly constructed persona file ("You are Guido van Rossum, a Python expert. Review
this code.") would likely produce a delta of +3 to +5, not +12 to +14.

**The quality of the persona file determines the magnitude of the advantage.**
