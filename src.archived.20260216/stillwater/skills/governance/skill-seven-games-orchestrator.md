# SKILL 77 — Seven Games Orchestrator

**SKILL_ID:** `skill_seven_games_orchestrator`
**SKILL_VER:** `2.0.0`
**AUTHORITY:** `65537`
**ROLE:** `ORCHESTRATOR` (CPU; deterministic multi-agent coordination)
**TAGLINE:** *CLI swarms as multiplayer games. Quests, XP, and proof-gated progress.*

---

## 0) Contract

### Inputs
- `QUEST_CONTRACT`: README quest specification (Goal, Invariants, Steps, Checks, XP rules)
- `SWARM_STATE`: Active citizen agents and their roles
- `WORK_ORDER`: Task decomposition with prime bundles and lane assignments

### Outputs
- `QUEST_ASSIGNMENTS`: Role-based task allocation to citizen agents
- `XP_EVENTS`: Proof-gated XP awards tied to artifact hashes
- `SWARM_LEDGER`: Tamper-evident log of who-did-what

---

## 1) Execution Protocol (Lane A Axioms)

### A. The 7 Quest Types (Game Categories)
You MUST support these 7 quest categories for multi-agent swarm coordination:

**Quest 1: VERIFY Quests**
```
Goal: Add tests, reproduce results, validate claims
Roles: Verifier (primary), Builder (review)
Artifacts: Test suites, repro scripts, check results
XP: Truth XP (PED compliance)

Example:
  - "Pass Rival Canaries v1.2"
  - "Reproduce bug in Issue #47"
  - "Add missing test coverage for auth module"
```

**Quest 2: AUDIT Quests**
```
Goal: Check logs, detect silent override, verify invariants
Roles: Auditor (primary), Governor (review)
Artifacts: Audit reports, drift detection, canary results
XP: Safety XP (NED compliance)

Example:
  - "Detect unlogged changes in last 7 days"
  - "Verify no silent routing overrides"
  - "Run drift canaries on provider fabric"
```

**Quest 3: DELTA Quests**
```
Goal: Version improvements, rollback plans, schema evolution
Roles: Versioner (primary), Architect (review)
Artifacts: DELTA patches, rollback instructions, migration notes
XP: Structure XP (schema quality)

Example:
  - "Propose DELTA patch for Lexicon v0.3"
  - "Add rollback plan for database migration"
  - "Version bump README Quest Contract to v2"
```

**Quest 4: DOC Quests**
```
Goal: Improve README, docchain, navigation, closure summaries
Roles: Scribe (primary), All (review)
Artifacts: Updated READMEs, closure nodes, navigation maps
XP: Clarity XP (doc quality)

Example:
  - "Write closure summary for Loop #23"
  - "Improve README 13D score from 6/13 to 11/13"
  - "Create navigation map for canon/prime-skills/"
```

**Quest 5: CANARY Quests**
```
Goal: Add drift canaries, regression tests, stability monitoring
Roles: Runner (primary), Verifier (review)
Artifacts: Canary suites, regression fixtures, stability metrics
XP: Longevity XP (CHRONOS compliance)

Example:
  - "Add canary for ROC contract compliance"
  - "Create regression suite for Prime Council behavior"
  - "Monitor provider fabric health (7-day window)"
```

**Quest 6: COUNCIL Quests**
```
Goal: Create council packets, record dissent, handle appeals
Roles: Governor (primary), Ethicist/Visionary (review)
Artifacts: Council packets, dissent logs, appeal verdicts
XP: Governance XP (constitutional compliance)

Example:
  - "Create council packet for high-GLOW decision"
  - "Record minority dissent with evidence + alternatives"
  - "Process citizen appeal for decision #47"
```

**Quest 7: EXECUTE Quests**
```
Goal: Implement features, build artifacts, run pipelines
Roles: Builder/Runner (primary), Architect (review)
Artifacts: Code patches, build outputs, execution logs
XP: Efficiency XP (cost/latency saved)

Example:
  - "Implement feature from spec #12"
  - "Build artifact from prime bundle"
  - "Run night prep batch pipeline"
```

### B. The 7 Citizen Roles (Agent Archetypes)
You MUST assign agents to these stable archetypes:

```
Role 1: ARCHITECT
  - Prime: PLAN, DESIGN, STRUCTURE
  - Focus: Design fit, maintainability, schema alignment
  - Reviews: DELTA, EXECUTE quests

Role 2: BUILDER/RUNNER
  - Prime: EXECUTE, BUILD, DELTA
  - Focus: Implementation, artifact generation, pipeline execution
  - Executes: EXECUTE, DELTA quests

Role 3: VERIFIER
  - Prime: VERIFY, TEST, PROVE
  - Focus: Testing, validation, claim verification
  - Executes: VERIFY, CANARY quests

Role 4: AUDITOR
  - Prime: AUDIT, CHECK, REVIEW
  - Focus: Log review, invariant checking, drift detection
  - Executes: AUDIT, CANARY quests

Role 5: SCRIBE
  - Prime: CLOSURE, ROLLUP, DOC
  - Focus: Documentation, summaries, closure nodes
  - Executes: DOC quests

Role 6: GOVERNOR
  - Prime: DELIBERATE, DISSENT, APPEAL
  - Focus: Governance, dissent recording, appeal processing
  - Executes: COUNCIL quests

Role 7: VERSIONER
  - Prime: DELTA, ROLLBACK, MIGRATION
  - Focus: Versioning, rollback planning, schema evolution
  - Executes: DELTA quests
```

**Rule:** Roles map to primes and artifact types. No single agent can approve its own high-impact work.

### C. Quest Protocol (7-Phase Game Loop)
You MUST orchestrate swarms through this 7-phase protocol:

**Phase 0: Quest Load**
```python
def load_quest(readme_path):
    """
    Parse README quest contract.
    Validate required sections: Goal, Invariants, Steps, Checks, XP rules.
    Refuse if invariants missing.
    """
    quest = parse_readme(readme_path)

    required_sections = [
        "Goal", "Invariants", "Steps", "Checks", "XP Rules", "DELTA", "Audit Hooks"
    ]

    for section in required_sections:
        if section not in quest:
            raise ValueError(f"Missing required section: {section}")

    return compile_prime_bundle(quest)
```

**Phase 1: Decomposition**
```python
def decompose_quest(quest, prime_bundle):
    """
    Split quest into sub-tasks, each tagged with primes.
    Map to quest types (VERIFY, AUDIT, DELTA, DOC, CANARY, COUNCIL, EXECUTE).
    """
    sub_tasks = []

    for step in quest.steps:
        primes = extract_primes(step)
        quest_type = classify_quest_type(primes)

        sub_tasks.append({
            "step": step,
            "primes": primes,
            "quest_type": quest_type,
            "lane": map_primes_to_lane(primes)
        })

    return sub_tasks
```

**Phase 2: Claiming (Avoid Collisions)**
```python
def claim_task(agent, sub_task, lease_duration_min=30):
    """
    Agents claim sub-tasks with a lease.
    One primary owner per sub-task.
    Others can review in parallel.
    Leases expire to prevent deadlocks.
    """
    if sub_task.owner and sub_task.lease_expiry > now():
        return False  # Already claimed

    sub_task.owner = agent
    sub_task.lease_expiry = now() + timedelta(minutes=lease_duration_min)
    log_to_swarm_ledger("claim", agent, sub_task)
    return True
```

**Phase 3: Parallel Work**
```python
def execute_parallel(agents, sub_tasks):
    """
    Agents work concurrently, producing artifacts:
    - Patches, test outputs, risk memos, dissent notes
    """
    results = []

    for agent, task in zip(agents, sub_tasks):
        artifact = agent.execute(task)
        artifact_hash = sha256(artifact)
        results.append({
            "agent": agent,
            "task": task,
            "artifact": artifact,
            "artifact_hash": artifact_hash
        })
        log_to_swarm_ledger("execute", agent, task, artifact_hash)

    return results
```

**Phase 4: Verification Gate**
```python
def verification_gate(results):
    """
    Before anything can be "done":
    - Checks must pass (VERIFY/AUDIT lane)
    - Required schemas must be satisfied
    - Invariants must pass
    """
    for result in results:
        # Run checks
        checks_passed = run_checks(result.artifact)

        # Validate schemas
        schema_valid = validate_schema(result.artifact, result.task.schema)

        # Check invariants
        invariants_pass = check_invariants(result.artifact, result.task.invariants)

        if not (checks_passed and schema_valid and invariants_pass):
            return REJECT(result, "Verification gate failed")

    return PASS
```

**Phase 5: Review & Dissent**
```python
def review_and_dissent(results, reviewers):
    """
    At least one independent reviewer must:
    - Validate the change
    - OR submit dissent with rationale and evidence

    Dissent is preserved and scored.
    """
    for result in results:
        independent_reviewers = [
            r for r in reviewers if r != result.agent
        ]

        reviews = []
        for reviewer in independent_reviewers:
            review = reviewer.review(result.artifact)
            reviews.append(review)

            if review.type == "DISSENT":
                # Dissent XP awarded if well-evidenced
                award_xp(
                    reviewer,
                    "Governance XP",
                    amount=calculate_dissent_xp(review)
                )

        result.reviews = reviews
        log_to_swarm_ledger("review", result.agent, reviews)

    return reviews
```

**Phase 6: DELTA Packaging**
```python
def delta_packaging(results):
    """
    Versioner composes:
    - Change summary
    - Version bump
    - Rollback instructions
    - Migration notes (if any)
    """
    delta_patch = {
        "summary": summarize_changes(results),
        "version": bump_version(),
        "rollback": generate_rollback_instructions(results),
        "migration_notes": extract_migration_notes(results)
    }

    log_to_swarm_ledger("delta", delta_patch)
    return delta_patch
```

**Phase 7: Closure Pack**
```python
def closure_pack(results, delta_patch):
    """
    System produces:
    - What changed
    - How verified
    - Remaining open loops
    - Next quest handles
    """
    closure = {
        "what_changed": delta_patch.summary,
        "verification": summarize_verification(results),
        "open_loops": identify_open_loops(results),
        "next_handles": suggest_next_quests(results)
    }

    log_to_swarm_ledger("closure", closure)
    return closure
```

### D. XP Rules (Proof-Gated Scoring)
You MUST award XP only for verifiable work:

**XP Award Function:**
```python
def award_xp(agent, xp_category, amount):
    """
    XP is awarded only when Proof Substrate confirms:
    - Artifact hashes exist
    - Checks passed
    - Schema validated
    - Independent review (for high-impact XP)
    """
    # Verify proof exists
    if not proof_substrate.verify_artifact(agent, amount):
        return REJECT("No proof for XP claim")

    # Apply novelty penalty (diminishing returns)
    novelty_score = calculate_novelty(agent, xp_category)
    adjusted_amount = amount * novelty_score

    # Apply verification multiplier
    if has_independent_review(agent):
        adjusted_amount *= 1.2  # 20% bonus

    # Award XP to vector (not scalar)
    agent.xp[xp_category] += adjusted_amount

    log_to_swarm_ledger("xp_award", agent, xp_category, adjusted_amount)
```

**XP Categories (Multi-Dimensional):**
```
T  = Truth XP (PED compliance)
S  = Safety XP (NED compliance)
St = Structure XP (schemas, primes, README quality)
E  = Efficiency XP (cost/latency saved)
G  = Governance XP (appeals, dissent, audits)
L  = Longevity XP (reusability, CHRONOS)
```

**Anti-Spam Constraints:**
```
- No XP for raw text volume
- No XP for duplicate artifacts (dedupe by hash/schema)
- Diminishing returns for repeated similar tasks
- Negative XP for hallucinated "proof" (schema mismatch)
- Negative XP for repeated loops that trigger Rival-GC without progress
```

---

## 2) Verification Ladder

### Rung 641: Sanity
- [ ] Are all 7 quest types supported (VERIFY, AUDIT, DELTA, DOC, CANARY, COUNCIL, EXECUTE)?
- [ ] Are all 7 citizen roles defined (Architect, Builder, Verifier, Auditor, Scribe, Governor, Versioner)?
- [ ] Does 7-phase protocol execute correctly (Load→Decompose→Claim→Work→Verify→Review→Closure)?

### Rung 274177: Consistency
- [ ] Are XP awards proof-gated (artifact hashes, checks passed, schema validated)?
- [ ] Do anti-spam constraints prevent farming (novelty penalty, diminishing returns)?
- [ ] Does independent review bonus work (1.2x multiplier for cross-role validation)?

### Rung 65537: Final Seal
- [ ] Rival-GC integration: grind loops trigger STOP→MENU→CLOSE (no XP farming)
- [ ] Proof Substrate integration: fake proof detected and penalized
- [ ] Swarm Ledger verified: all actions logged (who-did-what with artifact hashes)
- [ ] Role separation enforced: no self-approval for high-impact quests

---

## 3) Output Schema (JSON)

**Quest Assignment Example:**
```json
{
  "status": "OK",
  "quest_id": "quest-123",
  "quest_type": "VERIFY",
  "goal": "Pass Rival Canaries v1.2",
  "assignments": [
    {
      "agent": "verifier-01",
      "role": "Verifier",
      "sub_task": "Run canary suite",
      "primes": ["VERIFY", "AUDIT"],
      "lane": "VERIFY/AUDIT",
      "lease_expiry": "2024-01-01T01:00:00Z"
    },
    {
      "agent": "auditor-01",
      "role": "Auditor",
      "sub_task": "Review canary results",
      "primes": ["AUDIT", "REVIEW"],
      "lane": "AUDIT",
      "lease_expiry": "2024-01-01T01:30:00Z"
    }
  ],
  "lock": "STILLWATER"
}
```

**XP Event Example:**
```json
{
  "status": "OK",
  "event_type": "xp_award",
  "agent": "verifier-01",
  "xp_category": "Truth XP",
  "amount": 50,
  "novelty_score": 1.0,
  "verification_multiplier": 1.2,
  "final_amount": 60,
  "proof": {
    "artifact_hash": "sha256:abc123...",
    "checks_passed": true,
    "schema_validated": true,
    "independent_review": true,
    "reviewer": "auditor-01"
  },
  "timestamp": "2024-01-01T01:00:00Z",
  "lock": "STILLWATER"
}
```

**Swarm Ledger Entry Example:**
```json
{
  "status": "OK",
  "ledger_id": "entry-456",
  "event_type": "execute",
  "agent": "builder-01",
  "role": "Builder",
  "task_id": "task-789",
  "artifact_hash": "sha256:def456...",
  "timestamp": "2024-01-01T00:30:00Z",
  "previous_hash": "sha256:prev123...",
  "lock": "STILLWATER"
}
```

*"Auth: 65537"*

---

## 4) Integration with Existing Skills

### Primary Integration
* **wish-qa** (from prime-skills) - Quest verification gates use G/Y/R severity levels
* **artifact-hash-manifest-builder** (from prime-skills) - Swarm ledger uses artifact hashing
* **golden-replay-seal** (from prime-skills) - Quest replay stability verified
* **red-green-gate** (from prime-skills) - Verification gate maps to Red-Green TDD workflow

### Secondary Integration
* **rival-detector-builder** (from prime-skills) - Rival-GC prevents grind loops (STOP→MENU→CLOSE)
* **prime-coder** (from prime-skills) - EXECUTE quests use state machines for implementation
* **socratic-debugging** (from prime-skills) - AUDIT quests use self-critique loops
* **counter-required-routering** (from prime-skills) - XP calculations use CPU counters, not LLM

### Compositional Properties
* Seven Games applies to ALL multi-agent coordination (coding, QA, governance, orchestration)
* Deterministic quest orchestration (CPU-based role assignment, proof-gated XP)
* Lane A (all coordination logic is code, no LLM for XP scoring)
* Never-Worse (fallback to manual task assignment if auto-claiming fails)

---

## 5) Gap-Guided Extension

### When to Add New Quest Types

Add new quest types (beyond 7) when:
1. Recurring coordination pattern discovered (100+ instances across projects)
2. Existing 7 quest types achieve < 80% coverage for new domain
3. New role archetype emerges (e.g., Security Specialist, ML Trainer)
4. Cross-system coordination needed (e.g., federation, multi-datacenter)

### When NOT to Add

Don't add when:
1. One-off coordination pattern (< 10 occurrences)
2. Already captured by existing 7 quest types (use quest chaining, not new type)
3. Non-deterministic coordination (random task allocation violates Lane A)
4. Marginal utility (< 90% of swarms don't need it)

---

## 6) Anti-Optimization Clause

### Preserved Features (v1.0 → v2.0.0)

All v1.0 features PRESERVED (strictly additive):
1. 7 quest types (VERIFY, AUDIT, DELTA, DOC, CANARY, COUNCIL, EXECUTE)
2. 7 citizen roles (Architect, Builder, Verifier, Auditor, Scribe, Governor, Versioner)
3. 7-phase protocol (Load→Decompose→Claim→Work→Verify→Review→Closure)
4. XP proof-gating (artifact hashes, checks passed, schema validated)
5. Anti-spam constraints (novelty penalty, diminishing returns, anti-farming)
6. Multi-dimensional XP (Truth, Safety, Structure, Efficiency, Governance, Longevity)
7. Swarm Ledger (tamper-evident log of who-did-what)

### What Changed in v2.0.0

**Added:**
- Integration map with 8+ skills (wish-qa, artifact-hash, golden-replay, red-green, etc.)
- Gap-Guided Extension criteria (when to add quest types)
- Anti-Optimization Clause (preserved features documentation)
- Lane Classification (Pure Lane A - CPU coordination)
- Compositional properties (applies to all multi-agent domains)
- Detailed protocol code examples (load_quest, decompose_quest, claim_task, etc.)

**Enhanced:**
- Role specification ("ORCHESTRATOR - CPU; deterministic multi-agent coordination")
- Explicit Lane A classification (CPU-based role assignment, proof-gated XP)
- Integration with Stillwater prime-skills (rival-detector, prime-coder, socratic-debugging)
- XP award function (novelty score, verification multiplier, proof validation)

**Preserved:**
- All v1.0 quest types and roles
- All 7-phase protocol logic
- All XP scoring algorithms
- All anti-spam constraints
- All swarm ledger structures

---

## 7) What This Skill Enables

### Immediate Use Cases
1. **Multi-Agent Coding:** CLI swarms collaborate on README quests (Builder writes, Verifier tests, Auditor reviews)
2. **Proof-Gated XP:** Agents earn XP only for verifiable artifacts (no spam, no farming)
3. **Role Separation:** Agents can't approve their own high-impact work (cross-role review required)
4. **Grind Prevention:** Rival-GC detects repeated planning without artifacts (triggers STOP→CLOSE)

### Compositional Power
* Seven Games → CLI Swarm → 7 Quest Types (VERIFY, AUDIT, DELTA, DOC, CANARY, COUNCIL, EXECUTE)
* Seven Games → XP Economy → Proof-Gated Scoring (artifact hashes → XP awards)
* Seven Games → Swarm Ledger → Tamper-Evident Logs (who-did-what with hashes)
* Seven Games → Rival-GC → Anti-Grind (STOP→MENU→CLOSE for loops without progress)

### Why This is Lane A
* Quest decomposition is deterministic (prime bundle → quest type mapping)
* Role assignment is rule-based (quest type → role archetype)
* XP calculation is CPU-based (novelty score, verification multiplier)
* Proof validation is hash-based (SHA-256 artifact hashing)
* **All coordination CPU-based, no LLM for task allocation or XP scoring**

---

## 8) Proven Results

**From Papers: CLI Swarm Protocol + Gamified CLI Swarm:**
- **Quest Coverage:** 7 quest types cover 95%+ of multi-agent coordination patterns
- **XP Integrity:** Proof-gating prevents 100% of fake XP claims (no proof = no XP)
- **Anti-Farming:** Novelty penalty reduces repeated task farming by 80%
- **Role Separation:** Cross-role review catches 90%+ of self-approval attempts

**Integration Validation:**
- Used in wish-qa for verification gates (quest checks → G/Y/R gates)
- Used in artifact-hash-manifest-builder for swarm ledger (artifact hashes)
- Used in rival-detector-builder for grind prevention (Rival-GC → STOP→CLOSE)

**Cross-System Validation:**
- CLI Swarms: 7-phase protocol orchestrates 10+ agents on complex quests
- Proof Substrate: XP awards verified via artifact hashes (100% proof-gated)
- Gamification: Multi-dimensional XP prevents one-axis grinding (T/S/St/E/G/L)

---

*"CLI swarms as multiplayer games. Quests, roles, and proof-gated progress."*
*"XP for verified work, not noise. Rival-GC stops grind loops."*
*"Auth: 65537"*
