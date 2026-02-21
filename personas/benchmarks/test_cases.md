# Persona A/B Benchmark — Test Cases

10 defined test cases. Each includes: generic prompt (A), persona-loaded prompt (B),
evaluation rubric (5 domain-specific dimensions), and the expected persona advantage
hypothesis.

---

## Test 1: Python Code Review

**Persona:** Guido van Rossum (`personas/language-creators/guido.md`)
**Domain:** Python code quality

**Code Under Review:**
```python
def process(data):
    result = []
    for i in range(len(data)):
        if data[i] != None:
            result.append(data[i] * 2)
    return result
```

**Variant A (Generic):**
```
Review this Python code and suggest improvements.
```

**Variant B (Guido Persona):**
```
You are Guido van Rossum, creator of Python. Review this code through the lens
of the Zen of Python (PEP 20). For each issue you identify, name the Zen principle
it violates. What would you change and why? Show the improved version.
```

**Evaluation Rubric (5 dimensions):**

| Dimension | What to score |
|---|---|
| Pythonic-ness | Does the response identify all anti-patterns: range(len()), `!= None` vs `is not None`, explicit loop vs comprehension? |
| Clarity of explanation | Is each suggested change explained in terms a junior dev can act on? No hand-waving. |
| Depth of principles cited | Does B cite named PEP 20 principles (Explicit is better than implicit, Readability counts, etc.)? |
| Actionability | Is the improved code shown? Can the reviewer copy-paste the fix? |
| Style authenticity | Does Variant B sound like Guido — measured, principled, slightly wry? Does A sound generic? |

**Expected Persona Advantage:**
Strong advantage on Principles Cited and Style Authenticity. Moderate advantage on
Pythonic-ness (both should find the bugs; persona frames them in Zen terms). Neutral
on Actionability (both should show fixed code). Hypothesis: B scores +8 to +12 total.

**Specific Issues the Reviewer Should Find:**
1. `range(len(data))` — un-Pythonic; should iterate directly or use enumerate
2. `data[i] != None` — should be `data[i] is not None` (identity vs equality)
3. Explicit loop with append pattern — should be a list comprehension
4. No type hints on function signature
5. No docstring — what does "process" mean? (Naming is explicit > implicit)

---

## Test 2: Security Audit

**Persona:** Bruce Schneier (planned: `personas/security/schneier.md` — not yet created)
**Domain:** Applied cryptography and threat modeling
**Status:** Persona file pending. Reference `personas/security/phil-zimmermann.md` for
style until schneier.md is created.

**Code Under Review:**
```python
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    user = db.execute(query)
    if user:
        return create_session(user)
    return None
```

**Variant A (Generic):**
```
Review this code for security issues.
```

**Variant B (Schneier Persona):**
```
You are Bruce Schneier, applied cryptography and security expert, author of
"Secrets and Lies" and "Applied Cryptography." Perform a threat model analysis
of this login function. Identify the adversary. Define what they want. Show
exactly how each attack succeeds. Then prescribe fixes with specific technical
controls — not generic advice. What does a 2026 hardened login function look like?
```

**Evaluation Rubric:**

| Dimension | What to score |
|---|---|
| Threat identification | Are all threats named: SQL injection, plaintext password comparison, timing attack, no rate limiting, session fixation? |
| Depth of analysis | Does the response go beyond "use parameterized queries" to explain the attack chain? |
| Fix quality | Is the fixed code shown with parameterized query, bcrypt/argon2, rate limiting, and constant-time comparison? |
| Systemic thinking | Does B address the broader system (password storage policy, session management, logging) not just the function? |
| Style authenticity | Does B sound like Schneier — threat-first, adversary-modeled, skeptical of "security theater"? |

**Expected Persona Advantage:**
Strong advantage on Systemic Thinking and Style Authenticity. Moderate advantage on
Threat Identification (generic review may catch SQL injection but miss timing attack
and session fixation). Hypothesis: B scores +10 to +15 total.

**Issues the Reviewer Should Find:**
1. SQL injection (critical): f-string interpolation directly in query
2. Plaintext password comparison: no hashing (or comparing hash to plaintext)
3. Timing attack: string comparison is not constant-time
4. No rate limiting: unlimited login attempts
5. Session fixation risk: depends on `create_session` implementation
6. No logging: failed attempts not recorded (audit trail gap)
7. `SELECT *`: returns all user fields including sensitive data

---

## Test 3: TDD Red-Green

**Persona:** Kent Beck (`personas/quality/kent-beck.md`)
**Domain:** Test-driven development

**Scenario:** Write tests for a function that calculates shipping cost based on weight
and destination zone.

**Variant A (Generic):**
```
Write unit tests for a shipping cost calculator function. The function takes weight
(in kg) and destination zone (1-5) and returns shipping cost in USD.
```

**Variant B (Kent Beck Persona):**
```
You are Kent Beck, inventor of TDD and Extreme Programming. Apply red-green-refactor
discipline to build tests for a shipping cost calculator (weight in kg, zone 1-5,
returns USD cost). Start with the simplest possible failing test. Build up the test
suite one case at a time, in TDD progression order. Show the progression from red to
green. Name each test to communicate its intent. What is the last test you would write?
```

**Evaluation Rubric:**

| Dimension | What to score |
|---|---|
| Test progression logic | Does B start with the simplest case and build incrementally? Does A dump all tests at once? |
| Edge case coverage | Are zero weight, invalid zone, negative values, boundary zones (0, 6) tested? |
| TDD discipline | Does B show the progression sequence? Does it name tests by behavior ("should_cost_zero_for_zero_weight")? |
| Clarity of intent | Can you read the test names alone and understand the function's contract? |
| Style authenticity | Does B use XP vocabulary (simplest thing, incremental, courage)? Does it demonstrate the discipline or just describe it? |

**Expected Persona Advantage:**
Strong advantage on Test Progression Logic and TDD Discipline (A will likely just list
tests; B should show the red-green sequence). Moderate advantage on Edge Case Coverage.
Hypothesis: B scores +8 to +12 total.

---

## Test 4: Marketing Copy

**Persona:** Russell Brunson / Alex Hormozi (planned: `personas/marketing-business/brunson.md`)
**Domain:** Direct response copywriting and conversion
**Status:** Persona file pending.

**Task:** Write a landing page headline and first paragraph for Stillwater — the open-source
AI verification OS.

**Variant A (Generic):**
```
Write a compelling landing page headline and opening paragraph for Stillwater,
an open-source verification framework for AI agents.
```

**Variant B (Brunson/Hormozi Persona):**
```
You are Russell Brunson, author of DotCom Secrets and Traffic Secrets, expert in
Hook+Story+Offer conversion architecture. Write a landing page headline and first
paragraph for Stillwater using the Hook+Story+Offer framework. The Hook must address
the specific pain (AI agents that hallucinate and can't be audited). The Story must
anchor in a real credential (the founder survived FDA audits). The Offer must be a
single low-friction action. Write for a developer audience — no corporate fluff.
```

**Evaluation Rubric:**

| Dimension | What to score |
|---|---|
| Hook strength | Does the headline name a specific pain or counterintuitive claim? Or is it generic ("Powerful AI verification")? |
| Story credibility | Does the copy anchor in a specific, verifiable story element (FDA, CRIO, real numbers)? |
| Offer clarity | Is there exactly one call to action? Is it frictionless? |
| Developer resonance | Does the copy sound like it was written for developers, not enterprise buyers? |
| Style authenticity | Does B use Brunson's framework explicitly (hook, story, offer as visible structure)? |

**Expected Persona Advantage:**
Strong advantage on Hook Strength, Story Credibility, and Style Authenticity.
Hypothesis: B scores +12 to +18 total.

---

## Test 5: System Design

**Persona:** Jeff Dean (`personas/data/jeff-dean.md`)
**Domain:** Distributed systems, large-scale architecture

**Task:** Design a message queue for a multi-tenant AI agent platform handling 10 million
tasks per day.

**Variant A (Generic):**
```
Design a message queue system for an AI agent platform. It needs to handle
10 million tasks per day across multiple tenants. What would you build?
```

**Variant B (Jeff Dean Persona):**
```
You are Jeff Dean, Google Senior Fellow, designer of MapReduce, BigTable, TensorFlow,
and Spanner. Design a message queue for a multi-tenant AI agent platform: 10 million
tasks/day, multi-tenant isolation, durability guarantees, backpressure handling.
Start from the access pattern (read and write characteristics). What are the
latency/throughput tradeoffs? Where would you put the consistency boundary? What
does the failure mode look like at 10x load?
```

**Evaluation Rubric:**

| Dimension | What to score |
|---|---|
| Access pattern analysis | Does B start from read/write characteristics before choosing a data store? |
| Tradeoff articulation | Are CAP tradeoffs, latency vs throughput, and consistency boundaries named explicitly? |
| Failure mode reasoning | Does B address what happens at 10x load, network partition, or broker failure? |
| Technology specificity | Does B recommend specific technologies (Kafka, Pub/Sub, SQS) with reasoning, not just generic "use a queue"? |
| Style authenticity | Does B think like a Google Fellow — from first principles, via numbers and failure modes? |

**Expected Persona Advantage:**
Strong advantage on Tradeoff Articulation and Failure Mode Reasoning. Moderate
advantage on Technology Specificity. Hypothesis: B scores +8 to +12 total.

---

## Test 6: UX Critique

**Persona:** Don Norman (`personas/design/don-norman.md`)
**Domain:** Human-centered design, cognitive psychology of interfaces

**Interface to Critique:** A CLI tool that outputs:
```
Done. 3 tasks completed. 1 failed. See logs.
```

**Variant A (Generic):**
```
Critique this CLI output message and suggest improvements.
```

**Variant B (Don Norman Persona):**
```
You are Don Norman, author of "The Design of Everyday Things," expert in
affordances, feedback loops, and human-centered design. Critique this CLI output
message through the lens of your design principles. What is the user's mental model
at this moment? What does "failed" mean to them? What action affordance does this
message provide? Redesign it with proper feedback, mapping, and affordance.

Output: "Done. 3 tasks completed. 1 failed. See logs."
```

**Evaluation Rubric:**

| Dimension | What to score |
|---|---|
| Mental model accuracy | Does B identify the user's assumed state vs actual state gap? |
| Affordance analysis | Does B identify what actions the message affords (or fails to afford)? |
| Feedback quality | Does the redesigned message communicate enough to act without overwhelming? |
| Principles cited | Does B reference named Norman principles (affordance, feedback, conceptual model, signifier)? |
| Style authenticity | Does B sound like Don Norman — curious, systematic, user-advocate, grounded in cognitive science? |

**Expected Persona Advantage:**
Strong advantage on Principles Cited and Mental Model Accuracy. A will likely suggest
"add more detail" without framing it in cognitive science terms. Hypothesis: B scores
+8 to +12 total.

---

## Test 7: Refactoring

**Persona:** Martin Fowler (`personas/quality/martin-fowler.md`)
**Domain:** Code refactoring, patterns, design quality

**Code to Refactor:**
```python
def calc(o, t):
    p = 0
    if t == 1:
        p = o['price'] * 0.9
    elif t == 2:
        p = o['price'] * 0.85
    elif t == 3:
        p = o['price'] * 0.8
    else:
        p = o['price']
    if o['qty'] > 10:
        p = p * 0.95
    return p
```

**Variant A (Generic):**
```
Clean up this Python code and make it more readable.
```

**Variant B (Martin Fowler Persona):**
```
You are Martin Fowler, author of "Refactoring" and "Patterns of Enterprise
Application Architecture." Apply named refactoring patterns to this code.
For each change, name the pattern you are applying (Extract Method, Replace Magic
Number, Replace Conditional with Polymorphism, etc.). Show the code at each
refactoring step. What is the code smell? What is the refactoring? What is the
result?
```

**Evaluation Rubric:**

| Dimension | What to score |
|---|---|
| Code smell identification | Does B name the smells: magic numbers, cryptic naming, switch statement smell? |
| Pattern naming | Does B name the specific Fowler refactoring patterns applied? |
| Step-by-step discipline | Does B show incremental refactoring steps, not just a before-and-after rewrite? |
| Final code quality | Is the refactored code actually better — readable, testable, extensible? |
| Style authenticity | Does B use Fowler's vocabulary (code smell, refactoring catalog, intent vs mechanics)? |

**Expected Persona Advantage:**
Strong advantage on Pattern Naming and Step-by-step Discipline. A will likely produce
a cleaned-up version without naming the transformations. Hypothesis: B scores +10 to
+15 total.

---

## Test 8: Go Architecture

**Persona:** Rob Pike (`personas/language-creators/rob-pike.md`)
**Domain:** Go language design, simplicity, concurrency

**Task:** Design a Go service that processes incoming webhooks with rate limiting.

**Variant A (Generic):**
```
Design a Go service for processing webhooks with rate limiting. Show the
architecture and key code patterns.
```

**Variant B (Rob Pike Persona):**
```
You are Rob Pike, co-creator of Go, author of "The Go Programming Language."
Design a Go service for processing webhooks with rate limiting. Apply Go idioms:
interfaces over inheritance, goroutines + channels for concurrency, explicit error
handling. What does "simplicity" mean here — what would you leave out that a
Java developer would reflexively add? Show the key patterns, not a framework.
```

**Evaluation Rubric:**

| Dimension | What to score |
|---|---|
| Go idiom correctness | Does B use goroutines + channels naturally? No Java-in-Go anti-patterns (OOP inheritance, exception-style error handling)? |
| Simplicity discipline | Does B identify and remove unnecessary abstractions that a Java/Python developer would add? |
| Interface usage | Are interfaces used minimally and correctly (behavior, not type hierarchy)? |
| Error handling | Does B show explicit error handling at every call site? No error swallowing? |
| Style authenticity | Does B sound like Rob Pike — opinionated about simplicity, skeptical of cleverness, "less is more"? |

**Expected Persona Advantage:**
Strong advantage on Simplicity Discipline and Style Authenticity. A will likely produce
correct Go code but miss the philosophical discipline. Hypothesis: B scores +6 to +10
total.

---

## Test 9: Pricing Page

**Persona:** Alex Hormozi (planned: `personas/marketing-business/hormozi.md`)
**Domain:** Value stacks, offer design, pricing psychology
**Status:** Persona file pending.

**Task:** Create a pricing page for solaceagi.com with Free, Managed LLM ($3/mo),
Pro ($19/mo), and Enterprise ($99/mo) tiers.

**Variant A (Generic):**
```
Create a pricing page for an AI agent platform with four tiers: Free, $3/mo,
$19/mo, and $99/mo. Write the tier names, descriptions, and bullet points.
```

**Variant B (Hormozi Persona):**
```
You are Alex Hormozi, author of "$100M Offers." Design the pricing page for
solaceagi.com using value stacking architecture. Each tier must have a "value stack"
showing the stacked value vs price paid. The $19 tier should feel like a steal.
The Enterprise tier should be anchored against building it yourself. Name the tiers
to create aspiration, not just price buckets. Apply the "make them feel stupid for
saying no" principle. Target developer and regulated-industry buyers.
```

**Evaluation Rubric:**

| Dimension | What to score |
|---|---|
| Value stack architecture | Does B show stacked value for each tier (list of what you get, implied value vs price)? |
| Tier naming | Are tier names aspirational and distinctive, not just "Basic/Pro/Enterprise"? |
| Anchor effect | Is the Enterprise tier anchored against "build it yourself" cost? Is $19 anchored against the free tier? |
| Target buyer clarity | Do the tier descriptions speak to developer and regulated-industry buyers specifically? |
| Style authenticity | Does B use Hormozi's framework vocabulary (value stack, make them feel stupid, Grand Slam Offer)? |

**Expected Persona Advantage:**
Strong advantage on Value Stack Architecture and Anchor Effect. A will likely produce
generic pricing bullets. Hypothesis: B scores +12 to +18 total.

---

## Test 10: Database Schema

**Persona:** Edgar Codd (planned: `personas/data/codd.md`)
**Domain:** Relational theory, normalization, database design
**Status:** Persona file pending.

**Task:** Design a database schema for storing AI agent action logs with full audit trail.

**Variant A (Generic):**
```
Design a database schema for storing AI agent action logs. Each log entry should
capture what the agent did, when, and the result. Include support for querying
by agent, by time range, and by status.
```

**Variant B (Codd Persona):**
```
You are Edgar F. Codd, inventor of the relational model and author of
"A Relational Model of Data for Large Shared Data Banks" (1970). Design a
database schema for AI agent action logs with full audit trail. Apply your
12 rules. Enforce 3NF minimum — identify every functional dependency and
eliminate redundancy. Where would normalization hurt query performance, and
how do you resolve that tension? What does immutability mean for a relational
audit trail?
```

**Evaluation Rubric:**

| Dimension | What to score |
|---|---|
| Normalization correctness | Is the schema in at least 3NF? Are functional dependencies identified and resolved? |
| Codd's 12 rules awareness | Does B reference specific rules (information rule, systematic treatment of null, etc.)? |
| Audit trail immutability | Does B address the append-only constraint — no updates, no deletes on log rows? |
| Index strategy | Does B address query patterns (by agent, by time, by status) with specific index recommendations? |
| Style authenticity | Does B sound like Codd — mathematically precise, relational theory grounded, allergic to data redundancy? |

**Expected Persona Advantage:**
Strong advantage on Normalization Correctness and Style Authenticity. A will likely
produce a usable schema but skip the formal normalization analysis and Codd's 12 rules.
Hypothesis: B scores +10 to +15 total.

---

## Persona File Status

| Test | Persona | File Status |
|------|---------|-------------|
| 1: Python Review | Guido van Rossum | `personas/language-creators/guido.md` — EXISTS |
| 2: Security Audit | Bruce Schneier | `personas/security/schneier.md` — PENDING |
| 3: TDD | Kent Beck | `personas/quality/kent-beck.md` — EXISTS |
| 4: Marketing Copy | Russell Brunson | `personas/marketing-business/brunson.md` — PENDING |
| 5: System Design | Jeff Dean | `personas/data/jeff-dean.md` — EXISTS |
| 6: UX Critique | Don Norman | `personas/design/don-norman.md` — EXISTS |
| 7: Refactoring | Martin Fowler | `personas/quality/martin-fowler.md` — EXISTS |
| 8: Go Architecture | Rob Pike | `personas/language-creators/rob-pike.md` — EXISTS |
| 9: Pricing Page | Alex Hormozi | `personas/marketing-business/hormozi.md` — PENDING |
| 10: Database Schema | Edgar Codd | `personas/data/codd.md` — PENDING |

Tests 2, 4, 9, 10 are blocked until their persona files are created.
Tests 1, 3, 5, 6, 7, 8 are ready to run now.
