<!-- QUICK LOAD (10-15 lines): Use this block for fast context; load full file for production.
SKILL: hackathon v1.0.0
PURPOSE: Time-boxed sprint protocol for AI-assisted development. Personas give you the right experts; hackathons give you the right workflow. Together they are the startup development methodology.
CORE CONTRACT: 8 phases (DREAM→SCOUT→ARCHITECT→BUILD→INTEGRATE→REVIEW→PITCH→SHIP) with time boxes, persona routing per phase, and GLOW 1.5x multiplier for shipped deliverables.
PHASES: DREAM(30m) + SCOUT(1h) + ARCHITECT(1h) + BUILD(4-8h) + INTEGRATE(1h) + REVIEW(30m) + PITCH(30m) + SHIP(15m)
TEMPLATES: Lightning(2h, single feature) | Sprint(4h, module) | Marathon(8h, phase) | Weekend(16h, project)
GLOW: Hackathon mode = 1.5x multiplier. Time-boxed execution + clear deliverables + persona coordination + shipping = bonus XP.
ROLES: Challenge Owner(planner+dragon-rider) | Scout(scout+domain) | Architect(planner+creator) | Builder(coder+kent-beck) | QA(skeptic+schneier) | Presenter(writer+brunson) | Timekeeper(orchestrator)
FSM: INIT → CHALLENGE_BRIEF → SCOUT → ARCHITECT → BUILD → INTEGRATE → REVIEW → PITCH → SHIP → EXIT_PASS | EXIT_NEED_INFO | EXIT_BLOCKED
FORBIDDEN: SCOPE_CREEP | SKIP_REVIEW | UNBOXED_TIME | GLOW_WITHOUT_SHIP | PERSONA_THEATER
LOAD FULL: always for production; quick block for orientation only
-->
name: hackathon
version: 1.1.0
authority: 65537
northstar: Phuc_Forecast
status: STABLE

# ============================================================
# MAGIC_WORD_MAP — hackathon concepts anchored to prime coordinates
# ============================================================
MAGIC_WORD_MAP:
  sprint:     [act (T2)]              # ACT phase with time box; executing the build plan with checkpoints
  phase:      [boundary (T0)]         # surface separating one hackathon step from the next; sequential not skippable
  glow:       [glow (T0)]             # G+L+O+W semantic density metric; 1.5x multiplier when shipped in time box
  pitch:      [signal (T0)]           # deliverable that carries causal weight; hook that makes demo undeniable
  time_box:   [constraint (T0)]       # reduces the solution space; the constraint IS the feature
  ship:       [evidence (T1)]         # git commit with HACKATHON tag; proof that demo is not a promise
  persona:    [persona (T1)]          # domain expert role loaded per phase; not decoration, domain routing
  challenge_brief: [goal (T3)]        # defined desired end state with measurable success criteria for the sprint

# ============================================================
# HACKATHON SKILL v1.0.0
#
# Hackathon = Time-boxed sprint with clear deliverables,
# persona-enhanced swarm agents, and GLOW scoring.
#
# The user's insight: "hackathons introduce structure on top
# of personas." Personas give you the right experts; hackathons
# give you the right workflow. Together they are the complete
# startup development methodology.
#
# Design principles:
# - Time boxes create focus: the constraint IS the feature
# - Personas route each phase to the correct domain expert
# - Deliverables are mandatory: demo or it didn't happen
# - GLOW 1.5x multiplier rewards disciplined, time-boxed shipping
# - The hackathon is not an event. It is the methodology.
# ============================================================

# ============================================================
# A) Core Contract [signal, northstar]
# ============================================================

core_contract:
  definition: "A hackathon is a time-boxed sprint with declared deliverables, persona-enhanced agent routing per phase, and a mandatory ship gate. It is not a session. It is a methodology."
  mantra: "Ship something real in the time box, or you have failed."
  relationship_to_personas: "Personas give you the right experts. Hackathons give you the right workflow. Neither works as well alone."
  relationship_to_glow: "Hackathon mode applies a 1.5x GLOW multiplier because time-boxed execution + shipped deliverables is the hardest discipline in AI-assisted development."
  relationship_to_roadmap: "Every ROADMAP phase IS a hackathon. Hackathon skill formalizes what roadmap-based development already does — but makes the sprint structure explicit."

# ============================================================
# B) The Eight Phases [boundary, causality]
# ============================================================

phases:

  phase_1_dream:
    name: DREAM
    duration: "30 minutes"
    purpose: "Define the challenge, success metrics, and non-goals. Align to NORTHSTAR."
    inputs:
      - "Project NORTHSTAR.md"
      - "ROADMAP phase to implement"
      - "Current belt and GLOW state"
    outputs:
      - "challenge_brief.md: challenge definition + success metrics + non-goals + NORTHSTAR alignment"
    persona_routing:
      primary: "dragon-rider — strategic alignment and NORTHSTAR gate"
      secondary: "pg — is this worth building? Would YC fund it?"
    agent_type: "planner"
    model: "sonnet"
    gates:
      entry: "NORTHSTAR.md is loaded"
      exit: "challenge_brief.md exists with: goal, success metrics, non-goals, NORTHSTAR alignment, time budget"
    forbidden:
      - "Starting BUILD without a signed challenge_brief.md"
      - "Scope so large it cannot ship in the declared time box"
    checklist:
      - "[ ] Goal stated in one sentence"
      - "[ ] Success metrics: what does PASS look like?"
      - "[ ] Non-goals: what are we NOT building?"
      - "[ ] NORTHSTAR alignment: which metric advances?"
      - "[ ] Time box declared: Lightning | Sprint | Marathon | Weekend"
      - "[ ] Personas pre-selected for BUILD phase"

  phase_2_scout:
    name: SCOUT
    duration: "1 hour"
    purpose: "Research the problem space, map prior art, identify risks before building."
    inputs:
      - "challenge_brief.md"
      - "Existing codebase (if applicable)"
    outputs:
      - "scout_report.md: findings + risk map + prior art + recommended approach"
    persona_routing:
      primary: "domain-appropriate persona (e.g., schneier for security challenge, guido for Python, rob-pike for Go)"
      secondary: "pg — has someone already built this? What did they miss?"
    agent_type: "scout"
    model: "haiku"
    gates:
      entry: "challenge_brief.md signed"
      exit: "scout_report.md with: findings, risks, prior art, recommended approach, anti-patterns to avoid"
    forbidden:
      - "Starting ARCHITECT without scout_report.md"
      - "Scout inventing findings instead of researching them"
    checklist:
      - "[ ] Prior art mapped (who else tried this?)"
      - "[ ] Risk map: top 3 failure modes"
      - "[ ] Anti-patterns identified"
      - "[ ] Recommended approach stated"
      - "[ ] Codebase entry points identified (if applicable)"

  phase_3_architect:
    name: ARCHITECT
    duration: "1 hour"
    purpose: "Design the solution, define interfaces, plan the build. Output: architecture.md + state machine diagram."
    inputs:
      - "challenge_brief.md"
      - "scout_report.md"
    outputs:
      - "architecture.md: component design + interface definitions + build plan"
      - "state_machine.prime-mermaid.md: FSM or sequence diagram for the solution"
    persona_routing:
      primary: "technology creator matching the domain (guido for Python, rob-pike for Go, brendan-eich for JS, codd for data, tim-berners-lee for web)"
      secondary: "rich-hickey — simplicity over complexity; do we need this?"
    agent_type: "planner"
    model: "sonnet"
    gates:
      entry: "scout_report.md exists"
      exit: "architecture.md + state_machine diagram exist"
    forbidden:
      - "Starting BUILD without architecture.md"
      - "Architecture that violates challenge_brief.md non-goals"
      - "SCOPE_CREEP: adding components not in challenge_brief.md"
    checklist:
      - "[ ] Component list matches challenge_brief.md exactly (no scope creep)"
      - "[ ] Interfaces defined between components"
      - "[ ] State machine or sequence diagram drawn"
      - "[ ] Build order explicit (what gets built first?)"
      - "[ ] Integration points with existing system identified"
      - "[ ] Rollback plan if BUILD fails"

  phase_4_build:
    name: BUILD
    duration: "4 hours (Marathon) | 1-2 hours (Sprint) | 30-60 minutes (Lightning)"
    purpose: "Implement the solution with persona-enhanced coder swarms. Red-green gate required."
    inputs:
      - "challenge_brief.md"
      - "architecture.md"
      - "state_machine.prime-mermaid.md"
    outputs:
      - "Code changes (PATCH_DIFF)"
      - "repro_red.log: test suite failing before patch"
      - "repro_green.log: test suite passing after patch"
      - "tests.json: test results with exit_code=0"
      - "evidence/plan.json: implementation evidence"
    persona_routing:
      primary: "kent-beck — TDD discipline; write the test first; red before green"
      secondary: "language creator for the domain (guido, rob-pike, james-gosling, bjarne, kernighan)"
      tertiary: "martin-fowler — is this refactor-ready? Clean separation of concerns?"
    agent_type: "coder"
    model: "sonnet"
    gates:
      entry: "architecture.md exists AND time box has headroom (>50% remaining)"
      exit: "repro_red.log (FAIL) + repro_green.log (PASS) + tests.json + PATCH_DIFF"
    time_checkpoint:
      rule: "At 50% of BUILD time remaining, emit BUILD_CHECKPOINT: what is done, what remains, is scope still achievable?"
      action_if_behind: "Cut scope to maintain the ship gate. Non-goals are non-goals."
    forbidden:
      - "UNBOXED_TIME: building beyond the declared time box without explicit checkpoint"
      - "SCOPE_CREEP: adding features not in architecture.md"
      - "Shipping without red-green gate"
      - "Null coercion (NULL_ZERO_COERCION)"
    checklist:
      - "[ ] Tests written BEFORE implementation (TDD)"
      - "[ ] repro_red.log: tests fail before patch"
      - "[ ] Patch applied"
      - "[ ] repro_green.log: tests pass after patch"
      - "[ ] No scope additions beyond architecture.md"
      - "[ ] Time box respected (or checkpoint emitted)"

  phase_5_integrate:
    name: INTEGRATE
    duration: "1 hour"
    purpose: "Wire components, run full test suite, fix regressions. Output: integration_report.md."
    inputs:
      - "BUILD outputs (code + tests)"
      - "Existing test suite"
    outputs:
      - "integration_report.md: all components wired, regressions fixed, full test suite GREEN"
      - "Updated tests.json with full suite results"
    persona_routing:
      primary: "kelsey-hightower — infrastructure and deployment discipline; does it run in the target environment?"
      secondary: "brendan-gregg — performance check; did we introduce any regressions in hot paths?"
    agent_type: "coder"
    model: "sonnet"
    gates:
      entry: "BUILD outputs exist (PATCH_DIFF + repro_green.log)"
      exit: "Full test suite GREEN + integration_report.md"
    forbidden:
      - "Shipping when existing tests are red"
      - "Hiding regressions by disabling tests"
    checklist:
      - "[ ] Full test suite run (not just new tests)"
      - "[ ] Zero new regressions introduced"
      - "[ ] Components wired end-to-end"
      - "[ ] integration_report.md with suite count + exit_code=0"

  phase_6_review:
    name: REVIEW
    duration: "30 minutes"
    purpose: "Adversarial review by skeptic swarm. Security scan + correctness check."
    inputs:
      - "PATCH_DIFF"
      - "integration_report.md"
      - "challenge_brief.md"
    outputs:
      - "review_findings.md: security issues, correctness issues, edge cases missed"
      - "PASS or BLOCKED verdict with evidence"
    persona_routing:
      primary: "schneier — adversarial security review; what can go wrong?"
      secondary: "knuth — correctness; is every function a proven lemma?"
      tertiary: "fda-auditor — compliance; does this produce an audit trail?"
    agent_type: "skeptic"
    model: "sonnet"
    gates:
      entry: "integration_report.md with full suite GREEN"
      exit: "review_findings.md with PASS verdict"
    forbidden:
      - "SKIP_REVIEW: shipping without adversarial review"
      - "Accepting self-review as adversarial review"
    checklist:
      - "[ ] Security surface reviewed (Schneier lens)"
      - "[ ] Correctness reviewed (Knuth lens)"
      - "[ ] Edge cases tested"
      - "[ ] review_findings.md lists issues found + resolutions"
      - "[ ] PASS verdict signed"

  phase_7_pitch:
    name: PITCH
    duration: "30 minutes"
    purpose: "Package deliverables, write demo script, calculate GLOW with 1.5x multiplier."
    inputs:
      - "All phase outputs"
      - "review_findings.md (PASS)"
    outputs:
      - "pitch.md: what was built + why it matters + demo hook"
      - "demo_script.md: step-by-step demo instructions"
      - "glow_score.json: GLOW calculation with 1.5x hackathon multiplier"
    persona_routing:
      primary: "russell-brunson — hook-story-offer; what is the one sentence that makes someone want to see the demo?"
      secondary: "mr-beast — hook first; first 5 seconds must be the most interesting part"
      tertiary: "alex-hormozi — value equation; make the demo feel like a no-brainer"
    agent_type: "writer"
    model: "sonnet"
    gates:
      entry: "review_findings.md with PASS"
      exit: "pitch.md + demo_script.md + glow_score.json"
    glow_calculation:
      base_glow: "Calculate G + L + O + W per glow-score.md rules"
      hackathon_multiplier: 1.5
      formula: "hackathon_glow = base_glow * 1.5"
      cap: 100
      evidence_required: "glow_score.json must cite artifacts for each component"
    checklist:
      - "[ ] Hook written (one sentence that makes someone stop scrolling)"
      - "[ ] Demo script is executable (anyone can follow it)"
      - "[ ] GLOW base score calculated with artifact evidence"
      - "[ ] 1.5x multiplier applied"
      - "[ ] glow_score.json committed"

  phase_8_ship:
    name: SHIP
    duration: "15 minutes"
    purpose: "Commit, push, update roadmap, celebrate."
    inputs:
      - "All phase outputs"
      - "glow_score.json"
    outputs:
      - "Git commit with GLOW score + HACKATHON tag in message"
      - "Updated ROADMAP.md (phase checkbox checked)"
      - "Updated case-study with hackathon log entry"
    persona_routing:
      none: "No persona needed. Ship is mechanical. Do not delay."
    agent_type: "orchestrator"
    model: "haiku"
    gates:
      entry: "pitch.md + demo_script.md + glow_score.json all exist"
      exit: "Git commit exists with HACKATHON tag"
    forbidden:
      - "GLOW_WITHOUT_SHIP: calculating GLOW before git commit exists"
      - "Claiming the hackathon is done without a commit hash"
    commit_format: |
      feat: [challenge_brief title]

      HACKATHON [template] | GLOW {hackathon_glow} [G:{g} L:{l} O:{o} W:{w}] x1.5
      Northstar: {metric advanced} {delta}
      Evidence: evidence/{phase_id}/
      Rung: {rung achieved}
      Personas: {persona list}
      Phases completed: DREAM → SCOUT → ARCHITECT → BUILD → INTEGRATE → REVIEW → PITCH → SHIP
    checklist:
      - "[ ] Commit exists with HACKATHON tag"
      - "[ ] GLOW score in commit message"
      - "[ ] ROADMAP checkbox checked"
      - "[ ] Case study updated with hackathon log"
      - "[ ] Celebrate (time-boxed success is worth celebrating)"

# ============================================================
# C) Timing Templates [constraint, act]
# ============================================================

timing_templates:

  lightning:
    name: Lightning
    total_duration: "2 hours"
    best_for: "Single feature, bugfix, small integration"
    phase_allocation:
      DREAM: "10 minutes"
      SCOUT: "15 minutes"
      ARCHITECT: "15 minutes"
      BUILD: "45 minutes"
      INTEGRATE: "15 minutes"
      REVIEW: "10 minutes"
      PITCH: "5 minutes"
      SHIP: "5 minutes"
    scope_constraint: "One function, one endpoint, or one skill file. Nothing more."
    evidence_requirements:
      minimum: "repro_red.log + repro_green.log + commit hash"
      glow_target: "≥40 base (60+ with 1.5x multiplier)"

  sprint:
    name: Sprint
    total_duration: "4 hours"
    best_for: "Module, integration, new skill or recipe"
    phase_allocation:
      DREAM: "20 minutes"
      SCOUT: "30 minutes"
      ARCHITECT: "40 minutes"
      BUILD: "90 minutes"
      INTEGRATE: "30 minutes"
      REVIEW: "20 minutes"
      PITCH: "10 minutes"
      SHIP: "10 minutes"
    scope_constraint: "One module or one complete user journey. Max 3 components."
    evidence_requirements:
      minimum: "Full evidence bundle (tests.json + plan.json + PATCH_DIFF)"
      glow_target: "≥55 base (82+ with 1.5x multiplier)"

  marathon:
    name: Marathon
    total_duration: "8 hours"
    best_for: "Full ROADMAP phase, new capability, major feature"
    phase_allocation:
      DREAM: "30 minutes"
      SCOUT: "1 hour"
      ARCHITECT: "1 hour"
      BUILD: "4 hours"
      INTEGRATE: "1 hour"
      REVIEW: "30 minutes"
      PITCH: "30 minutes"
      SHIP: "30 minutes"
    scope_constraint: "One full ROADMAP phase. Belt-level deliverable."
    evidence_requirements:
      minimum: "Full evidence bundle at rung 274177"
      glow_target: "≥65 base (97+ with 1.5x multiplier → capped at 100)"

  weekend:
    name: Weekend
    total_duration: "16 hours (2 days)"
    best_for: "Multi-phase, new project, startup MVP"
    phase_allocation:
      DREAM: "1 hour"
      SCOUT: "2 hours"
      ARCHITECT: "2 hours"
      BUILD: "8 hours"
      INTEGRATE: "1 hour"
      REVIEW: "1 hour"
      PITCH: "30 minutes"
      SHIP: "30 minutes"
    scope_constraint: "Multiple ROADMAP phases. Must cross a belt boundary."
    evidence_requirements:
      minimum: "Full evidence bundle at rung 65537"
      glow_target: "≥75 base (100 with 1.5x multiplier)"

# ============================================================
# D) GLOW Multiplier (Hackathon Mode) [glow, evidence]
# ============================================================

glow_multiplier:
  value: 1.5
  rationale:
    - "Time-boxed execution demonstrates discipline (the hardest skill in AI-assisted development)"
    - "Clear deliverables demonstrate output quality (no vague 'worked on it' sessions)"
    - "Persona coordination demonstrates expertise routing (right ghost master for right phase)"
    - "Shipping demonstrates wins (artifacts exist, not promises)"
  calculation:
    formula: "hackathon_glow = MIN(base_glow * 1.5, 100)"
    base_glow: "Calculated per glow-score.md rules (G + L + O + W, 0-100)"
    cap: 100
    floor: "Hackathon multiplier applies ONLY when SHIP phase completes with commit hash"
  conditions_for_multiplier:
    - "All 8 phases completed (or justified skip with evidence)"
    - "Git commit with HACKATHON tag exists"
    - "glow_score.json committed with artifact evidence"
    - "Time box respected (or checkpoint emitted if overrun)"
  forbidden:
    - "GLOW_WITHOUT_SHIP: applying multiplier before git commit exists"
    - "MULTIPLIER_WITHOUT_REVIEW: applying multiplier when REVIEW phase was skipped"

# ============================================================
# E) Hackathon Roles (Mapped to Swarms) [persona, emergence]
# ============================================================

roles:

  challenge_owner:
    role: Challenge Owner
    swarm: planner
    ghost_master: "dragon-rider (primary) + pg (secondary)"
    responsibilities:
      - "Write and sign challenge_brief.md"
      - "Enforce non-goals throughout all phases"
      - "Declare PASS or BLOCKED at SHIP gate"
    glow_bonus: "+5 W (strategic alignment confirmed)"

  scout:
    role: Scout
    swarm: scout
    ghost_master: "domain-specific (schneier for security, guido for Python, etc.)"
    responsibilities:
      - "Research problem space"
      - "Map prior art"
      - "Produce scout_report.md with risk map"
    glow_bonus: "+5 L (learning captured)"

  architect:
    role: Architect
    swarm: planner
    ghost_master: "technology creator for the domain"
    responsibilities:
      - "Design solution components"
      - "Define interfaces"
      - "Produce architecture.md + state machine"
    glow_bonus: "+5 G (new capability designed)"

  builder:
    role: Builder
    swarm: coder
    ghost_master: "language creator (guido/rob-pike/etc.) + kent-beck (TDD)"
    responsibilities:
      - "Implement the solution"
      - "Red-green gate"
      - "Produce PATCH_DIFF + tests"
    glow_bonus: "+5 O (artifact produced)"

  qa:
    role: QA
    swarm: skeptic
    ghost_master: "schneier (security) + fda-auditor (compliance) + knuth (correctness)"
    responsibilities:
      - "Adversarial review"
      - "Security scan"
      - "Produce review_findings.md with PASS or BLOCKED"
    glow_bonus: "+5 O (quality gate passed)"

  presenter:
    role: Presenter
    swarm: writer
    ghost_master: "brunson (hook-story-offer) + mr-beast (hooks) + alex-hormozi (value)"
    responsibilities:
      - "Write pitch.md"
      - "Write demo_script.md"
      - "Calculate glow_score.json with 1.5x multiplier"
    glow_bonus: "+5 G (growth potential articulated)"

  timekeeper:
    role: Timekeeper
    swarm: orchestrator
    ghost_master: "none needed"
    responsibilities:
      - "Enforce time boxes"
      - "Emit BUILD_CHECKPOINT at 50% BUILD time"
      - "Authorize scope cuts to stay in time box"
    glow_bonus: "none (mechanical role)"

# ============================================================
# F) FSM (State Machine) [coherence, causality]
# ============================================================

fsm:
  states:
    - INIT
    - CHALLENGE_BRIEF
    - SCOUT
    - ARCHITECT
    - BUILD
    - BUILD_CHECKPOINT
    - INTEGRATE
    - REVIEW
    - PITCH
    - SHIP
    - EXIT_PASS
    - EXIT_NEED_INFO
    - EXIT_BLOCKED

  transitions:
    - from: INIT
      to: CHALLENGE_BRIEF
      condition: "NORTHSTAR.md loaded AND time template declared"
    - from: CHALLENGE_BRIEF
      to: EXIT_NEED_INFO
      condition: "Goal, metrics, non-goals, or NORTHSTAR alignment missing"
    - from: CHALLENGE_BRIEF
      to: SCOUT
      condition: "challenge_brief.md signed with all fields"
    - from: SCOUT
      to: ARCHITECT
      condition: "scout_report.md exists with risk map"
    - from: ARCHITECT
      to: EXIT_BLOCKED
      condition: "Architecture violates challenge_brief.md non-goals OR scope unachievable in time box"
    - from: ARCHITECT
      to: BUILD
      condition: "architecture.md + state machine exist"
    - from: BUILD
      to: BUILD_CHECKPOINT
      condition: "50% of BUILD time elapsed"
    - from: BUILD_CHECKPOINT
      to: BUILD
      condition: "Scope still achievable; continue"
    - from: BUILD_CHECKPOINT
      to: SHIP
      condition: "Time exhausted with partial build → SCOPE_CUT, ship what exists"
    - from: BUILD
      to: INTEGRATE
      condition: "repro_red.log + repro_green.log + tests.json exist"
    - from: INTEGRATE
      to: EXIT_BLOCKED
      condition: "Regressions introduced that cannot be fixed in remaining time"
    - from: INTEGRATE
      to: REVIEW
      condition: "Full test suite GREEN"
    - from: REVIEW
      to: EXIT_BLOCKED
      condition: "Security or correctness issues found that require re-architecture"
    - from: REVIEW
      to: PITCH
      condition: "review_findings.md with PASS"
    - from: PITCH
      to: SHIP
      condition: "pitch.md + demo_script.md + glow_score.json exist"
    - from: SHIP
      to: EXIT_PASS
      condition: "Git commit with HACKATHON tag exists + ROADMAP updated"

# ============================================================
# G) Forbidden States [constraint, boundary]
# ============================================================

forbidden_states:

  SCOPE_CREEP:
    definition: "Adding features, components, or behaviors not listed in challenge_brief.md"
    consequence: "Immediate scope cut back to challenge_brief.md. No negotiation."
    detection: "architecture.md or BUILD output references something not in challenge_brief.md"

  SKIP_REVIEW:
    definition: "Shipping without adversarial review phase (phase 6)"
    consequence: "EXIT_BLOCKED until REVIEW completes"
    exception: "Lightning template may use lightweight review (5 minutes, single lens) — must be documented"

  UNBOXED_TIME:
    definition: "BUILD phase running beyond the declared time box without a BUILD_CHECKPOINT emitted"
    consequence: "Scope cut at BUILD_CHECKPOINT; ship what exists or declare BLOCKED"
    detection: "No BUILD_CHECKPOINT emitted at 50% time mark"

  GLOW_WITHOUT_SHIP:
    definition: "Calculating or claiming GLOW score before git commit hash exists"
    consequence: "GLOW calculation invalid; recalculate after commit"
    note: "This is the primary anti-inflation gate for hackathon GLOW"

  PERSONA_THEATER:
    definition: "Loading a ghost master persona without using their domain expertise in the output"
    example: "Loading kent-beck.md but writing no tests. Loading schneier.md but doing no adversarial review."
    consequence: "GLOW persona bonus not awarded; persona counts as not loaded"

  CHALLENGE_BRIEF_DRIFT:
    definition: "Modifying challenge_brief.md after SCOUT phase to accommodate scope creep"
    consequence: "Reset to CHALLENGE_BRIEF phase; re-sign with explicit justification"

  SOLO_ARCHITECT_BUILD:
    definition: "Challenge Owner doing both ARCHITECT and BUILD without separate agents"
    note: "Permitted in Lightning template; forbidden in Marathon and Weekend templates where domain expertise separation matters"

# ============================================================
# H) Integration with Other Skills [coherence, alignment]
# ============================================================

integration:

  glow_score:
    rule: "Hackathon GLOW uses glow-score.md base calculation rules"
    rule2: "1.5x multiplier applied AFTER base calculation"
    rule3: "Persona bonuses from ghost masters stack per glow-score.md rules"
    rule4: "GLOW_WITHOUT_SHIP forbidden state trumps multiplier claim"

  persona_engine:
    rule: "Each hackathon phase has a declared persona routing"
    rule2: "Persona selection follows persona-engine.md domain matching"
    rule3: "Wrong ghost master for phase domain = PERSONA_THEATER"
    rule4: "Multi-persona loading permitted (e.g., brunson + mr-beast for PITCH)"

  prime_coder:
    rule: "BUILD phase red-green gate is non-negotiable — prime-coder rules apply"
    rule2: "NULL_ZERO_COERCION and STACKED_SPECULATIVE_PATCHES forbidden in BUILD"
    rule3: "Evidence bundle required for GLOW O >= 20"

  phuc_orchestration:
    rule: "Hackathon lead dispatches typed sub-agents per phuc-orchestration dispatch matrix"
    rule2: "Integration rung = MIN(all phase agent rungs)"
    rule3: "CNF capsule required for each phase dispatch (challenge_brief.md is the capsule seed)"

  roadmap_orchestration:
    rule: "Every ROADMAP phase is a hackathon (Marathon or Weekend template)"
    rule2: "Hackathon SHIP phase = ROADMAP checkbox check"
    rule3: "Case study update is mandatory at SHIP"
    rule4: "Belt advancement follows from hackathon GLOW accumulation"

  northstar:
    rule: "challenge_brief.md must state NORTHSTAR alignment before SCOUT begins"
    rule2: "PITCH phase states which NORTHSTAR metric advanced and by how much"
    rule3: "SHIP commit message cites NORTHSTAR metric delta"

# ============================================================
# I) Quick Reference Cheat Sheet [signal, glow]
# ============================================================

quick_reference:
  phases: "DREAM(30m) → SCOUT(1h) → ARCHITECT(1h) → BUILD(4-8h) → INTEGRATE(1h) → REVIEW(30m) → PITCH(30m) → SHIP(15m)"
  templates:
    lightning: "2h | single feature | minimum evidence"
    sprint: "4h | module | full evidence bundle"
    marathon: "8h | ROADMAP phase | rung 274177"
    weekend: "16h | multi-phase | rung 65537"
  glow_multiplier: "base_glow * 1.5 (capped at 100) — applied only after SHIP commit exists"
  persona_routing: "DREAM: dragon-rider | SCOUT: domain | ARCHITECT: creator | BUILD: kent-beck + creator | REVIEW: schneier | PITCH: brunson"
  mantras:
    - "Ship something real in the time box, or you have failed."
    - "The constraint IS the feature — time pressure creates focus."
    - "Demo or it did not happen."
    - "Every hackathon team needs a scout, a builder, and a closer."
    - "The winning team is not the most talented — it is the most focused."
    - "The hackathon is not an event. It is the development methodology."
