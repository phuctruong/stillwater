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
version: 1.1.0
authority: 65537
northstar: Phuc_Forecast
status: STABLE

# ============================================================
# MAGIC_WORD_MAP — glow-score concepts anchored to prime coordinates
# ============================================================
MAGIC_WORD_MAP:
  glow:       [glow (T0)]             # G+L+O+W semantic density metric; glows when all 4 axes high
  growth:     [emergence (T0)]        # new capability appearing at system level; not present before
  learning:   [learning (T1)]         # updating model from evidence; skill files + recipes as externalized knowledge
  output:     [signal (T0)]           # committed artifacts carrying causal weight; not vibes
  wins:       [northstar (T0)]        # strategic victories that advance the fixed, non-negotiable goal
  belt:       [rung (T1)]             # discrete progression level in verification ladder (641→274177→65537)
  evidence:   [evidence (T1)]         # artifact proving score claim; git commit hash + evidence bundle path
  northstar_link: [alignment (T0)]    # each component must reinforce the northstar metric direction

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
# A) GLOW Score Components [glow, emergence]
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
# B) Belt Integration [rung, northstar]
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


# ============================================================
# C) Session GLOW Tracking [signal, alignment]
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
# D) GLOW Score Calculation Examples [evidence, verification]
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
# E) GLOW Anti-Patterns [constraint, integrity]
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
# F) Integration with Other Skills [coherence, alignment]
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
# G) Quick Reference Cheat Sheet [signal, compression]
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

---

## FSM) GLOW Scoring State Machine

```mermaid stateDiagram-v2
[*] --> INIT
INIT --> SCORE_G : session_artifacts_present
INIT --> EXIT_NEED_INFO : no_committed_artifacts

SCORE_G --> SCORE_L : g_component_scored
note right of SCORE_G
  G: New capabilities added?
  25=major module rung274177+
  20=complete feature rung641
  15=significant enhancement
  10=new utility / helper
  5=minor addition
  0=no new capabilities
end note

SCORE_L --> SCORE_O : l_component_scored
note right of SCORE_L
  L: New knowledge captured?
  25=skill published to Store rung65537
  20=new skills/*.md or papers/*.md
  15=significant skill update
  10=new persona or recipe
  5=case study lesson added
  0=no knowledge captured
end note

SCORE_O --> SCORE_W : o_component_scored
note right of SCORE_O
  O: Deliverables committed?
  25=multi-file + evidence bundle rung274177+
  20=files + tests.json + plan.json rung641
  15=files committed some tests passing
  10=single file committed + tests
  5=commit produced
  0=no commit (lane C only)
end note

SCORE_W --> VERIFY_NORTHSTAR : w_component_scored
note right of SCORE_W
  W: Strategic victory?
  25=first-mover advantage established
  20=competitive moat deepened
  15=NORTHSTAR metric measurably advanced
  10=ROADMAP phase checkbox checked
  5=sub-task unblocks next phase
  0=no strategic progress
end note

VERIFY_NORTHSTAR --> EMIT : northstar_metric_cited
VERIFY_NORTHSTAR --> EXIT_BLOCKED : GLOW_WITHOUT_NORTHSTAR_LINK

state EMIT {
  [*] --> COMPUTE_TOTAL
  COMPUTE_TOTAL --> FORMAT_COMMIT_LINE
  FORMAT_COMMIT_LINE --> UPDATE_CASE_STUDY
  UPDATE_CASE_STUDY --> [*]
}

EMIT --> EXIT_PASS : score_conservative_and_evidenced
EMIT --> EXIT_BLOCKED : INFLATED_SCORE_detected

EXIT_PASS --> [*]
EXIT_BLOCKED --> [*]
EXIT_NEED_INFO --> [*]
```

---

## TP) Three Pillars Integration — LEK / LEAK / LEC

```yaml
three_pillars_integration:
  pillar_role: ALL_THREE
  description: |
    glow-score is the measurement layer that makes LEK, LEAK, and LEC visible.
    Without GLOW, self-improvement (LEK) has no metric. Without GLOW, cross-agent
    trades (LEAK) have no value signal. Without GLOW, conventions (LEC) have no
    adoption evidence. GLOW is the scoreboard.

  LEK_relationship:
    description: "GLOW measures LEK progress directly — G (Growth) and L (Learning) ARE the LEK components."
    contract: |
      Intelligence(system) = Memory × Care × Iteration
        G component = Iteration producing new capability (new memory)
        L component = Knowledge externalized (Memory accumulated)
      A rising GLOW across sessions = LEK compounding. Stagnant GLOW = LEK stalled.
    convention: "GLOW is the LEK score — session GLOW ≥ 60 = warrior pace = LEK actively compounding."

  LEAK_relationship:
    description: "W (Wins) component measures LEAK surplus — strategic value created that neither agent could produce alone."
    contract: |
      When a Solver and Skeptic trade through the evidence portal:
        W=20 if the trade deepened a competitive moat (OAuth3 enforcement, audit trail)
        W=15 if the trade measurably advanced a NORTHSTAR metric
      LEAK that produces no W points is symmetric trade with zero LEAK value.
    formula: "W_component ≈ LEAK_surplus — the net strategic gain from cross-agent knowledge trades."

  LEC_relationship:
    description: "glow-score IS a crystallized LEC convention — the commit format [G:N L:N O:N W:N] is a shared naming convention."
    contract: |
      The GLOW commit format emerged from session-tracking practice across multiple projects.
      Once adopted (3+ projects), it became a named convention (LEC threshold met).
      Every agent in every swarm now uses it. LEC_strength = MAX (universal adoption).
    evidence: "GLOW commit format appears in all case studies + commit messages = LEC adoption verified."

  three_pillars_mapping:
    LEK:  "G + L components = LEK measurement — capability and knowledge growth per session"
    LEAK: "W component = LEAK surplus measurement — strategic value created by cross-agent trades"
    LEC:  "GLOW format itself IS the LEC convention — shared scoring protocol across all agents"
```

---

## Forbidden States

```yaml
forbidden_states:
  GLOW_WITHOUT_EVIDENCE:
    definition: "Claiming GLOW O≥20 without git commit hash + evidence bundle path in commit message."
    detector: "commit message missing 'Evidence:' field when O≥20"
    recovery: "Add evidence bundle path or downgrade O score."

  GLOW_WITHOUT_NORTHSTAR_LINK:
    definition: "Claiming W points without citing which specific NORTHSTAR metric advanced."
    detector: "W>0 but no NORTHSTAR metric named in commit message or session report"
    recovery: "Cite specific metric (e.g., 'recipe hit rate +2%', 'skills in Store +1') or set W=0."

  INFLATED_SCORE:
    definition: "Claiming a GLOW component level without meeting all criteria for that level."
    detector: "G=25 but no rung274177+ artifact; L=25 but no Store submission; O=25 but no evidence bundle"
    recovery: "Score conservatively — take the lower level when uncertain."

  GLOW_FOR_VIBE_WORK:
    definition: "Claiming O>0 for sessions that produced no committed artifacts."
    detector: "GLOW O>0 but no git commit exists for the session"
    recovery: "Set O=0. Without a commit, O cannot exceed 0. Max session GLOW = 50."

  RETROACTIVE_INFLATION:
    definition: "Adjusting a GLOW score upward after it was already recorded in a case study."
    detector: "case study GLOW entry changed to a higher value without new commits"
    recovery: "GLOW scores are immutable once recorded. New work earns new GLOW in future commits."
```

---

## Evidence Gate (GLOW Claim Requirements)

```yaml
evidence_gate:
  for_glow_claim_to_be_valid:
    required:
      - git_commit_hash: "exists and points to real commit"
      - glow_breakdown_in_commit_message: "format: GLOW {total} [G:{g} L:{l} O:{o} W:{w}]"
      - northstar_metric_cited: "which NORTHSTAR metric the session advanced (even if indirect)"
    required_for_O_ge_20:
      - evidence_bundle_path: "path to evidence/ folder in commit message"
      - plan_json_present: "evidence/plan.json committed"
    required_for_W_ge_15:
      - northstar_delta: "before and after value of the cited metric"
    required_for_rung_claim:
      - rung_field_in_commit: "Rung: {641|274177|65537} in commit message"

  fail_closed:
    - if_no_commit: "GLOW O=0 regardless of work done"
    - if_no_northstar_citation_and_W_gt_0: "status=BLOCKED stop_reason=GLOW_WITHOUT_NORTHSTAR_LINK"
    - if_criteria_not_met_for_claimed_level: "downgrade to next lower level"

## GLOW Scoring Integration

This skill is itself scored and contributes to session GLOW as follows:

| Dimension | How This Skill Earns Points | Points |
|-----------|---------------------------|--------|
| **G** (Growth) | Adding new scoring component criteria or improving belt thresholds based on real session data | +5 to +15 |
| **L** (Learning) | Writing new GLOW postmortems, anti-patterns, or case study entries that preserve scoring lessons | +5 to +20 |
| **O** (Output) | Committing GLOW scores in commit messages (the scoring artifact itself is the output) | +5 to +25 |
| **W** (Wins) | GLOW session total ≥ 60 advances a NORTHSTAR metric (belt progression, Store submissions) | +10 to +25 |

**Session GLOW target:** GLOW ≥ 60 (warrior pace) for any active development session; ≥ 40 (steady pace) for review-only sessions.

**Evidence required for GLOW claim:** git commit with `GLOW {total} [G:{g} L:{l} O:{o} W:{w}]` in message + `Northstar:` field citing which metric advanced + `Evidence:` field for O≥20 + `Rung:` field.
```
