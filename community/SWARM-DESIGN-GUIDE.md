# Swarm Design Guide

How to design a new swarm agent type for Stillwater.

---

## What Is a Swarm Agent Type?

A swarm agent type is a typed role definition stored in `swarms/<agent-type>.md`. It is not a running process. It is a specification that any LLM session can load to take on that role.

When you "run the Scout agent," you:
1. Open a new LLM sub-session.
2. Paste the skill pack from `swarms/scout.md` into the session.
3. Paste the full content of `swarms/scout.md` into the session.
4. Provide the CNF (Context Normal Form) capsule.
5. The session operates within the Scout's FSM, produces the Scout's required artifacts, and exits.

The agent type file is the contract between the main session (dispatcher) and the sub-session (agent). It defines what the agent will do, what it will produce, and what it is forbidden from doing.

---

## Required Sections

A valid swarm agent type file must contain all of the following sections. Missing sections fail the schema check.

### 0. YAML Frontmatter

```yaml
---
agent_type: <name>
version: X.Y.Z
authority: 65537
skill_pack:
  - prime-safety   # Always first
  - <additional skills>
persona:
  primary: <Historical figure name>
  alternatives:
    - <Alternative figure 1>
    - <Alternative figure 2>
model_preferred: <haiku | sonnet | opus>
rung_default: <641 | 274177 | 65537>
artifacts:
  - <ArtifactName.json>
  - <other artifact file names>
---
```

The `authority` field is always 65537. The `model_preferred` field is a recommendation, not a constraint. The `rung_default` is the rung target this agent type defaults to for most tasks.

### 1. Role

A concise description of what this agent does and what it is explicitly permitted and forbidden to do.

Format:
```
## 0) Role

<2-4 sentences: what the agent maps to, what lens it applies, what makes it distinct>

**<Persona> lens:** <One sentence characterizing the persona's approach>

Permitted: <comma-separated list of allowed actions>
Forbidden: <comma-separated list of forbidden actions>
```

### 2. Skill Pack

The ordered list of skills, with conflict resolution rules.

```
## 1) Skill Pack

Load in order (never skip; never weaken):

1. `skills/prime-safety.md` -- wins all conflicts
2. `skills/<second skill>.md` -- <one-line role description>

Conflict rule: prime-safety wins over all. <second skill> wins over agent heuristics.
```

### 3. Persona Guidance

One paragraph per persona variant (primary + alternatives). The persona is a style prior, not a factual claim. It narrows the search space for how to approach a problem. It never overrides skill pack rules.

```
## 2) Persona Guidance

**<Primary persona> (primary):** <One sentence characterizing approach and strengths>

**<Alt persona> (alt):** <One sentence>
```

### 4. Expected Artifacts

The precise output schemas for every artifact this agent type produces. These must be machine-parseable JSON schemas (or YAML-equivalent). They are the contract that downstream agents and the main session rely on.

For each artifact:
- Name the file (repo-relative or scratch-relative path).
- Provide a JSON schema with all required keys.
- Annotate each key with its type and meaning.

```
## 3) Expected Artifacts

### ArtifactName.json

{
  "schema_version": "1.0.0",
  "agent_type": "<name>",
  "rung_target": 641,
  "<key>": "<type and meaning>",
  ...
  "stop_reason": "PASS | NEED_INFO | BLOCKED",
  "evidence": [
    {"type": "path", "ref": "<repo-relative>", "sha256": "<hex>"}
  ]
}
```

Every artifact schema must include `schema_version`, `agent_type`, `rung_target`, `stop_reason`, and `evidence`.

### 5. CNF Capsule Template

The Context Normal Form (CNF) capsule is what the main session provides to this agent at the start of each run. It prevents context rot by ensuring the agent sees only canonical, current information -- not stale reasoning from prior sessions.

```
## 4) CNF Capsule Template

TASK: <verbatim task statement>
CONSTRAINTS: <time/budget/scope>
REPO_ROOT: <relative path reference>
FAILING_TESTS: <list or NONE>
PRIOR_ARTIFACTS: <links only -- no inline content>
SKILL_PACK: [<skill list>]
BUDGET: {max_files: 12, max_witness_lines: 200, max_tool_calls: 40}
```

The agent must NOT rely on any state outside the CNF capsule.

### 6. FSM (State Machine)

A deterministic state machine specific to this agent type's workflow.

Required elements:
- Named states (including EXIT_PASS, EXIT_NEED_INFO, EXIT_BLOCKED)
- Transition table: (current state, condition) -> next state
- All conditions must be decidable from observable inputs

```
## 5) FSM

States:
- INIT
- INTAKE_TASK
- NULL_CHECK
- <domain-specific states>
- EXIT_PASS
- EXIT_NEED_INFO
- EXIT_BLOCKED

Transitions:
- INIT -> INTAKE_TASK: on CNF capsule received
- INTAKE_TASK -> NULL_CHECK: always
- NULL_CHECK -> EXIT_NEED_INFO: if task_statement == null OR required_inputs undefined
- NULL_CHECK -> <next state>: if inputs defined
...
```

### 7. Forbidden States

Agent-type-specific forbidden states. These extend (not replace) the forbidden states in the loaded skill packs.

Each forbidden state:
- Name in SCREAMING_SNAKE_CASE
- One-line definition
- Detector predicate
- Recovery action

```
## 6) Forbidden States

- ARTIFACT_WITHOUT_WITNESS: "Emitting an artifact claim without a file path + sha256 witness."
  Detector: artifact in output AND evidence array is empty
  Recovery: Do not emit artifact; return to evidence-building state.
```

### 8. Verification Ladder

The rung(s) this agent type can achieve and what is required for each.

### 9. Anti-Patterns

A list of the most common failure modes for this agent type, drawn from swarm run experience. These are not forbidden states (they may be transient) but are patterns to actively avoid.

---

## How to Choose a Persona

The persona is a historical figure whose characteristic lens matches the agent's most important failure mode.

**Principle:** Choose the person whose greatest strength is the quality the agent most needs, and whose most famous failure mode is the one the agent is most likely to fall into.

**Selection method:**

1. Define the agent's primary job in one sentence.
2. Define the agent's single most dangerous failure mode.
3. Find a historical figure who solved a similar problem, but whose known failure modes also match.

**Examples:**

| Agent Role | Failure Mode | Persona | Why |
|-----------|-------------|---------|-----|
| Scout (mapping) | Claiming to map what is not there | Ken Thompson | Built Unix from actual bytes; distrusted abstraction |
| Judge (scoring) | Approving without evidence | Ada Lovelace | Saw the difference between computation and result |
| Skeptic (challenging) | Challenging everything, accepting nothing | Alan Turing | Formalized what it means for a claim to be decidable |
| Mathematician (proofs) | Approximate reasoning in exact contexts | Emmy Noether | Built abstract algebra on pure structural reasoning |
| Coder (patching) | Over-engineering the simplest solution | Donald Knuth | Famous for insisting on correctness before optimization |
| Security Auditor | Missing the obvious attack vector | Bruce Schneier | Documented that security failures are usually simple |

**Hard rule:** The persona is a style prior only. It narrows search heuristics. It never overrides skill pack rules or evidence requirements. A Ken Thompson persona that finds no evidence still exits BLOCKED. A Ken Thompson persona that finds evidence still must produce a witness line.

**Alternatives:** List 2 alternatives for cases where the primary persona does not fit the specific task variant. Alternatives follow the same rules.

---

## How to Define Artifact Schemas

Artifact schemas are the hardest part of swarm design. Get them wrong and downstream agents break silently.

**Rules:**
1. Every artifact must have a `schema_version` field. When the schema changes, bump the version.
2. Every artifact must have a `stop_reason` field. Downstream agents use this to check if the agent completed successfully.
3. Every artifact must have an `evidence` array. Each entry has `type`, `ref` (repo-relative path), and `sha256`.
4. Use exact types: string, integer, boolean, array, object. No floats in verification fields.
5. Do not use nested optional objects without documenting their conditions. A field that is sometimes present and sometimes absent with no stated condition is a null trap.

**Test your schema:** After defining it, write a minimal valid example JSON. Can you parse it? Do all required keys have values? Is any key ambiguous?

---

## Step-by-Step: Design a New Swarm Agent Type

### Step 1: Define the Role First

Write one sentence: what does this agent do, and what does it NOT do?

If you cannot define what the agent does NOT do, the role is too broad. Narrow it.

Example of too-broad: "Reviews and improves code."
Example of correctly-scoped: "Scores code patches against the 5-criterion skill completeness scorecard and produces a pass/fail verdict with evidence; does not write new code."

### Step 2: Define the Artifacts

Before writing any FSM, define what the agent produces. The artifacts are the contract.

Ask for each artifact:
- What does a downstream agent need from this artifact?
- What fields are always present vs. conditionally present?
- What types are used? (Avoid floats in any field used for verification.)
- What is the schema version?

Write the JSON schema. Write a valid example. Only then move to the FSM.

### Step 3: Write the FSM

With the artifacts defined, work backward from the output:
- What state produces the artifact?
- What must be true before entering that state?
- What are the error exits?

Draw the states and transitions. Verify that every state has at least one exit transition. Verify that the FSM is reachable from INIT.

### Step 4: Write the Forbidden States

Read through the FSM and ask: at each state, what is the worst shortcut? These become forbidden states.

Common forbidden states across agent types:
- `ARTIFACT_WITHOUT_WITNESS`: producing an artifact claim without a file path + sha256
- `ROLE_DRIFT`: performing an action outside the agent's defined permitted list
- `SILENT_DEGRADATION`: failing to emit a stop reason on exit
- `CNF_BYPASS`: reading from session state outside the CNF capsule

---

## Template (Minimal Valid Swarm Agent Type File Structure)

```yaml
---
agent_type: <agent-name>
version: 1.0.0
authority: 65537
skill_pack:
  - prime-safety
  - prime-coder
persona:
  primary: <Historical Figure>
  alternatives:
    - <Alternative 1>
    - <Alternative 2>
model_preferred: haiku
rung_default: 641
artifacts:
  - AGENT_REPORT.json
---

# <Agent Name> Agent Type

## 0) Role

<2-4 sentences describing the agent's role, lens, and scope.>

**<Persona> lens:** <One characterizing sentence.>

Permitted: read files, run search tools, produce artifacts.
Forbidden: write patches, approve external decisions, claim PASS without artifact evidence.

---

## 1) Skill Pack

Load in order (never skip; never weaken):

1. `skills/prime-safety.md` -- wins all conflicts
2. `skills/prime-coder.md` -- evidence discipline, localization budget

Conflict rule: prime-safety wins over all. prime-coder wins over agent heuristics.

---

## 2) Persona Guidance

**<Primary> (primary):** <One sentence.>

**<Alt 1> (alt):** <One sentence.>

Persona is a style prior only. It never overrides skill pack rules.

---

## 3) Expected Artifacts

### AGENT_REPORT.json

\`\`\`json
{
  "schema_version": "1.0.0",
  "agent_type": "<agent-name>",
  "rung_target": 641,
  "task_statement": "<verbatim from CNF capsule>",
  "result": {},
  "stop_reason": "PASS | NEED_INFO | BLOCKED",
  "null_checks_performed": true,
  "evidence": [
    {"type": "path", "ref": "<repo-relative path>", "sha256": "<hex>"}
  ]
}
\`\`\`

---

## 4) CNF Capsule Template

\`\`\`
TASK: <verbatim task statement>
CONSTRAINTS: <time/budget/scope>
REPO_ROOT: <relative path reference>
FAILING_TESTS: <list or NONE>
PRIOR_ARTIFACTS: <links only -- no inline content>
SKILL_PACK: [prime-safety, prime-coder]
BUDGET: {max_files: 12, max_witness_lines: 200, max_tool_calls: 40}
\`\`\`

The agent MUST NOT rely on any state outside this capsule.

---

## 5) FSM

States:
- INIT
- INTAKE_TASK
- NULL_CHECK
- <DOMAIN_STATE_1>
- <DOMAIN_STATE_2>
- BUILD_REPORT
- EXIT_PASS
- EXIT_NEED_INFO
- EXIT_BLOCKED

Transitions:
- INIT -> INTAKE_TASK: on CNF capsule received
- INTAKE_TASK -> NULL_CHECK: always
- NULL_CHECK -> EXIT_NEED_INFO: if task_statement == null OR required_inputs missing
- NULL_CHECK -> <DOMAIN_STATE_1>: if inputs defined
- <DOMAIN_STATE_1> -> <DOMAIN_STATE_2>: on TOOL_OUTPUT
- <DOMAIN_STATE_2> -> BUILD_REPORT: always
- BUILD_REPORT -> EXIT_PASS: if evidence complete
- BUILD_REPORT -> EXIT_BLOCKED: if evidence incomplete

---

## 6) Forbidden States

- ARTIFACT_WITHOUT_WITNESS: Emitting an artifact without a file path + sha256 witness.
  Detector: artifact present in output AND evidence array is empty.
  Recovery: Do not emit artifact; return to BUILD_REPORT state and add witness.

- ROLE_DRIFT: Performing an action outside the permitted list (e.g., writing a patch when role is read-only).
  Detector: write tool called AND agent role does not include write permission.
  Recovery: Halt the write; emit EXIT_BLOCKED with stop_reason=INVARIANT_VIOLATION.

- SILENT_EXIT: Exiting without emitting a stop_reason.
  Detector: session ends AND stop_reason field absent from AGENT_REPORT.json.
  Recovery: Always emit stop_reason before exit, even if it is BLOCKED.

---

## 7) Verification Ladder

Rung target: 641

RUNG_641 requires:
- null_check_performed
- no_forbidden_states_entered
- AGENT_REPORT.json present with all required fields
- evidence array non-empty with valid sha256 entries
- stop_reason declared

---

## 8) Anti-Patterns

- <Anti-pattern 1>: <Description and why it is a failure mode for this agent type.>
- <Anti-pattern 2>: <Description.>
```

---

*Next steps: review your agent type against `community/SCORING-RUBRIC.md`, then submit via `community/CONTRIBUTING.md`.*
