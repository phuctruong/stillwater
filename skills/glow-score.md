<!-- QUICK LOAD (10-15 lines): Use this block for fast context; load full file for production.
SKILL: glow-score v1.0.0
PURPOSE: GLOW = Growth, Learning, Output, Wins. Gamification scoring system for roadmap-based development.
CORE CONTRACT: Track session progress, award belt XP, align with NORTHSTAR metrics.
COMPONENTS: G (Growth 0-25) + L (Learning 0-25) + O (Output 0-25) + W (Wins 0-25) = GLOW (0-100)
BELT INTEGRATION: White=0-20, Yellow=21-40, Orange=41-60, Green=61-80, Blue=81-90, Black=91-100
SESSION TARGETS: Daily ≥60 (warrior pace), Weekly ≥70 (master pace)
COMMIT FORMAT: feat: ... GLOW {total} [G:{g} L:{l} O:{o} W:{w}]
FORBIDDEN: GLOW_WITHOUT_NORTHSTAR_ALIGNMENT | INFLATED_GLOW | GLOW_FOR_VIBE_WORK
-->
name: glow-score
version: 1.0.0
authority: 65537
northstar: Phuc_Forecast
status: STABLE

# ============================================================
# GLOW SCORE v1.0.0
#
# GLOW = Growth, Learning, Output, Wins
#
# A gamification scoring system for roadmap-based development.
# Every session, every commit, every phase gets a GLOW score.
# GLOW measures real progress against NORTHSTAR metrics.
#
# Design principles:
# - GLOW cannot be inflated: each component has strict criteria
# - GLOW aligns with NORTHSTAR: scores increase only when northstar metrics advance
# - GLOW is transparent: breakdown shown in commit messages
# - GLOW drives belt progression: accumulated GLOW = belt XP
#
# Bruce Lee principle: "You cannot fake the kata. The form knows."
# GLOW cannot be gamed because it is grounded in artifacts, not vibes.
# ============================================================

# ============================================================
# A) GLOW Score Components
# ============================================================

components:
  G_growth:
    name: "Growth"
    range: 0-25
    definition: "New capabilities added to the system"
    criteria:
      25: "Major new module/feature at rung 274177+ with tests + evidence bundle"
      20: "Complete new feature at rung 641 with tests passing"
      15: "Significant enhancement to existing feature with tests"
      10: "New utility function, helper, or configuration option"
      5:  "Minor addition (new test, new constant, small method)"
      0:  "No new capabilities added"
    northstar_link: "Advances 'Stillwater Store skills' or 'Recipe hit rate' metric"
    forbidden: "GROWTH_WITHOUT_TESTS: claiming growth for untested code"

  L_learning:
    name: "Learning"
    range: 0-25
    definition: "New knowledge captured and encoded in the system"
    criteria:
      25: "New skill or paper published to Stillwater Store (rung 65537)"
      20: "New skills/*.md or papers/*.md file created and complete"
      15: "Significant update to existing skill (adds new section, new rules)"
      10: "New persona defined or recipe captured in recipes/"
      5:  "Case study updated with new lesson or postmortem captured"
      0:  "No new knowledge captured"
    northstar_link: "Advances 'Community contributors' or 'Skills in Store' metric"
    forbidden: "LEARNING_AS_NOTES: prose notes that are not executable skills or recipes"

  O_output:
    name: "Output"
    range: 0-25
    definition: "Measurable deliverables produced"
    criteria:
      25: "Multiple files committed, all tests passing, evidence bundle complete (rung 274177+)"
      20: "Files committed with tests.json + plan.json (rung 641)"
      15: "Files committed, some tests passing, evidence partial"
      10: "Single file committed with passing tests"
      5:  "Commit produced (even if small)"
      0:  "No commit produced"
    northstar_link: "Direct commit count and rung achievements"
    evidence_required: "commit hash + evidence bundle path for O >= 20"
    forbidden: "OUTPUT_WITHOUT_COMMIT: claiming output for work not in git"

  W_wins:
    name: "Wins"
    range: 0-25
    definition: "Strategic victories that deepen competitive moats or advance vision"
    criteria:
      25: "First-mover advantage established (new integration, new platform, new capability nobody else has)"
      20: "Competitive moat deepened (OAuth3 enforcement, Part 11 audit trail, evidence bundle)"
      15: "NORTHSTAR metric measurably advanced (recipe hit rate +X%, stars +Y, rung upgraded)"
      10: "Phase completed in ROADMAP (checkbox checked)"
      5:  "Sub-task completed that unblocks another phase"
      0:  "No strategic progress"
    northstar_link: "Direct advancement of any NORTHSTAR metric"
    forbidden: "WINS_BY_NARRATIVE: claiming W points for planned future wins not yet achieved"

total_glow:
  formula: "GLOW = G + L + O + W"
  range: 0-100
  calculation_rule: "Each component scored independently. No rounding up. No partial credit for incomplete criteria."

# ============================================================
# B) Belt Integration
# ============================================================

belt_integration:
  belts:
    White:
      glow_range: 0-20
      meaning: "Learning basics — first recipes, first rung 641"
      xp_per_session: "Accumulate GLOW points per session"
      advancement: "Total GLOW ≥ 21 advances to Yellow"
    Yellow:
      glow_range: 21-40
      meaning: "First tasks delegated — phuc-swarms running, recipes producing"
      xp_per_session: "Sessions averaging 25+ GLOW"
      advancement: "Total GLOW ≥ 41 + first Store submission advances to Orange"
    Orange:
      glow_range: 41-60
      meaning: "Contributing to store — skills published, community impact"
      xp_per_session: "Sessions averaging 50+ GLOW"
      advancement: "Total GLOW ≥ 61 + rung 65537 achieved advances to Green"
    Green:
      glow_range: 61-80
      meaning: "Rung 65537 achieved — production-grade verifiable work"
      xp_per_session: "Sessions averaging 65+ GLOW"
      advancement: "Total GLOW ≥ 81 + 24/7 cloud execution advances to Blue"
    Blue:
      glow_range: 81-90
      meaning: "Cloud execution 24/7 — automation running continuously"
      xp_per_session: "Sessions averaging 80+ GLOW"
      advancement: "Total GLOW ≥ 91 + 30-day production run advances to Black"
    Black:
      glow_range: 91-100
      meaning: "Master level — Models are commodities. Skills are capital. OAuth3 is law."
      xp_per_session: "Sessions consistently at 90+"
      advancement: "No further belt. Black Belt is the dojo."

  dragon_tip_bonus:
    Dragon_Contributor_2pct: "+50 XP/month toward belt progression"
    Super_Dragon_5pct: "+150 XP/month toward belt progression"
    Elder_Dragon_8pct: "+300 XP/month toward belt progression"
    Legendary_Dragon_9pct_plus: "+500 XP/month + custom XP multiplier"

# ============================================================
# C) Session GLOW Tracking
# ============================================================

session_tracking:
  session_start:
    actions:
      - "Display current belt + total GLOW accumulated"
      - "Show current NORTHSTAR metrics (from NORTHSTAR.md)"
      - "State today's GLOW target (60+ for warrior pace)"
      - "Show current phase in ROADMAP"
    format: |
      ```
      GLOW SESSION START
      Belt: {current_belt} | Total GLOW: {total}
      NORTHSTAR: {key_metric}: {current_value} → target: {target_value}
      Current phase: ROADMAP Phase {N}: {phase_name}
      Today's target: GLOW 60+ (warrior pace)
      ```

  per_commit:
    actions:
      - "Score each component: G, L, O, W"
      - "Justify score with artifact reference (not vibes)"
      - "Add GLOW breakdown to commit message"
    format: |
      ```
      feat: {description}

      GLOW {total} [G:{g} L:{l} O:{o} W:{w}]
      Northstar: {which metric advanced} {delta}
      Evidence: {evidence bundle path or N/A}
      Rung: {rung achieved}
      ```
    scoring_rules:
      - "Score after the commit is made, not before"
      - "Only score artifacts that exist in git"
      - "If uncertain between two score levels, take the lower"

  session_end:
    actions:
      - "Calculate session GLOW total (sum of commit GLOWs, or single score for the session)"
      - "Display belt progression if threshold crossed"
      - "Update case study with session GLOW + rung achieved + northstar advancement"
      - "State next ROADMAP phase"
    format: |
      ```
      GLOW SESSION END
      Session GLOW: {total}
      Belt: {before} → {after} (if advanced, otherwise stays same)
      NORTHSTAR delta: {metric}: {before} → {after}
      Phase completed: {yes/no}
      Next phase: ROADMAP Phase {N+1}: {phase_name}
      Case study updated: case-studies/{project}.md
      ```

  pace_targets:
    warrior_pace:
      daily_glow: 60
      description: "Active development day — building, testing, shipping"
    master_pace:
      weekly_average_glow: 70
      description: "Sustained output over a full week"
    steady_pace:
      daily_glow: 40
      description: "Maintenance day — fixes, reviews, docs"
    rest_day:
      daily_glow: 0-20
      description: "Review only, no commits — acceptable, not the goal"

# ============================================================
# D) GLOW Score Calculation Examples
# ============================================================

examples:
  example_1_oauth3_spec:
    task: "Write papers/oauth3-spec-v0.1.md — formal OAuth3 specification"
    G: 20  # complete new feature (spec is new capability for the system)
    L: 25  # new paper published at rung 641 (L max for new paper)
    O: 20  # files committed with tests.json + plan.json
    W: 20  # competitive moat deepened (OAuth3 is our unique advantage)
    total: 85
    belt_impact: "Advances toward Green"
    commit_message: "feat: add oauth3-spec-v0.1.md — formal OAuth3 specification\n\nGLOW 85 [G:20 L:25 O:20 W:20]\nNorthstar: First-mover OAuth3 spec +1\nEvidence: papers/oauth3-spec-v0.1.md\nRung: 641"

  example_2_bug_fix:
    task: "Fix null coercion bug in llm_client.py"
    G: 5   # minor fix, no new capability
    L: 5   # postmortem captured in case study
    O: 10  # single file committed with passing tests
    W: 5   # sub-task completed that unblocks next phase
    total: 25
    belt_impact: "Contributes to Yellow range"
    commit_message: "fix: prevent null coercion in llm_client cost calculation\n\nGLOW 25 [G:5 L:5 O:10 W:5]\nNorthstar: Stability improvement (indirect)\nEvidence: tests/test_llm_client.py::test_null_safety GREEN\nRung: 641"

  example_3_new_skill:
    task: "Write skills/persona-engine.md"
    G: 20  # complete new feature at rung 641
    L: 20  # new skills/*.md file created and complete
    O: 20  # file committed with evidence
    W: 15  # NORTHSTAR metric advanced (skills in store +1)
    total: 75
    belt_impact: "Advances toward Green"

  example_4_store_submission:
    task: "Submit skills/oauth3-enforcer.md to Stillwater Store at rung 65537"
    G: 25  # major module at rung 274177+
    L: 25  # skill published to Stillwater Store at rung 65537
    O: 25  # evidence bundle complete at rung 274177+
    W: 25  # first-mover advantage (first Store submission)
    total: 100
    belt_impact: "Black Belt threshold"

# ============================================================
# E) GLOW Anti-Patterns
# ============================================================

anti_patterns:
  GLOW_WITHOUT_NORTHSTAR_ALIGNMENT:
    symptom: "High GLOW score for work that does not advance any NORTHSTAR metric"
    fix: "W component requires explicit NORTHSTAR metric advancement. If W=0, total GLOW is capped at 75."

  INFLATED_GLOW:
    symptom: "Claiming 25/25 for a component without meeting the top criteria"
    fix: "Score conservatively. When uncertain between levels, take the lower."

  GLOW_FOR_VIBE_WORK:
    symptom: "Claiming GLOW for sessions that produced insights but no committed artifacts"
    fix: "O component requires a commit. Without O, session GLOW is at most 50."

  WINS_BY_NARRATIVE:
    symptom: "Claiming W=25 for 'establishing first-mover advantage' that is a plan, not a fact"
    fix: "W scores require: ROADMAP checkbox checked, metric value changed, or commit exists."

  GLOW_WITHOUT_EVIDENCE:
    symptom: "Claiming O=20 or O=25 without evidence/plan.json in the repository"
    fix: "O >= 20 requires evidence bundle path in commit message."

# ============================================================
# F) Integration with Other Skills
# ============================================================

integration:
  phuc_orchestration:
    rule: "Session GLOW is reported in the hub's update to case-studies/*.md"
    format: "## Session GLOW: {date} | {total} [G:{g} L:{l} O:{o} W:{w}] | Belt: {belt}"

  prime_coder:
    rule: "GLOW O component aligns with prime-coder's evidence requirements"
    rule2: "O=20 requires the same evidence bundle that prime-coder requires for rung 641"
    rule3: "O=25 requires the same evidence bundle that prime-coder requires for rung 274177+"

  persona_engine:
    rule: "Loading a matching persona from persona-engine does not add GLOW by itself"
    rule2: "Persona-enhanced output that leads to better L score is acceptable"
    rule3: "The persona does not score the GLOW — the artifacts do"

  northstar:
    rule: "W component scoring requires explicit citation of which NORTHSTAR metric advanced"
    rule2: "Hub must verify W claim by checking NORTHSTAR.md metric tables"

# ============================================================
# G) Quick Reference Cheat Sheet
# ============================================================
quick_reference:
  formula: "GLOW = G(0-25) + L(0-25) + O(0-25) + W(0-25) = 0-100"
  pace:
    warrior: "60+/day"
    master: "70+/week average"
    steady: "40+/day"
  belt_thresholds: "White<21, Yellow<41, Orange<61, Green<81, Blue<91, Black=91+"
  commit_format: "GLOW {total} [G:{g} L:{l} O:{o} W:{w}]"
  conservative_scoring: "When uncertain, take the lower score. GLOW cannot be retroactively inflated."
  mantras:
    - "You cannot fake the kata. The form knows."
    - "GLOW measures what you shipped, not what you planned."
    - "Black Belt GLOW is earned through evidence, not claimed through confidence."
    - "The dojo keeps score. The score is honest."
