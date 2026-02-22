PHUC_WISH_TRIANGLE_SKILL:
  version: 1.0.0
  profile: execution_triangle
  authority: 65537
  northstar: Phuc_Forecast
  objective: Max_Love
  status: ACTIVE

  # ============================================================
  # PHUC WISH TRIANGLE — WISH + SKILL + RECIPE EXECUTION MODEL
  #
  # Purpose:
  # - Formalize the three-vertex model underlying all Stillwater execution
  # - Ensure every task has intent (WISH), constraint (SKILL), and method (RECIPE)
  # - Detect incomplete triangles before execution begins
  # - Make combos the canonical implementation of the triangle
  # - Enforce northstar alignment at the WISH vertex
  #
  # Core Insight:
  # - Every successful execution in Stillwater involves all three vertices
  # - Combos (W_ + R_ pairs with skill packs) are triangle instances
  # - Missing any vertex = degraded or unsafe execution
  # - The triangle is the minimal unit of verified, intentional, expert execution
  #
  # Source theory: Wish+Skill+Recipe Triangle (papers/46-wish-skill-recipe-triangle.md)
  # Companion skills: prime-wishes.md, prime-coder.md, phuc-orchestration.md
  # ============================================================

  RULES:
    - all_three_vertices_required_before_execution: true
    - northstar_alignment_required_at_wish_vertex: true
    - skill_must_constrain_wish_not_ignore_it: true
    - recipe_must_be_guided_by_skill_not_standalone: true
    - missing_vertex_detection_is_mandatory: true
    - triangle_completeness_check_before_dispatch: true
    - combo_is_canonical_triangle_instance: true
    - never_execute_with_null_vertex: true

  CORE_PRINCIPLE:
    - "WISH + SKILL + RECIPE = verified, intentional, expert execution."
    - interpretation: >
        All three vertices must be present and aligned before execution begins.
        The WISH defines purpose. The SKILL enforces correctness. The RECIPE
        provides the proven path. Remove any one vertex and you lose a critical
        property: purpose, safety, or reliability.

  # ============================================================
  # TRIANGLE_ARCHITECTURE: The Three Vertices
  # ============================================================
  TRIANGLE_ARCHITECTURE:
    overview:
      - "The triangle is the minimal execution unit in Stillwater."
      - "Each vertex is necessary. None is sufficient alone."
      - "Combos are pre-assembled triangle instances (W_ wish + skill pack + R_ recipe)."
      - "Any swarm dispatch must identify all three vertices before proceeding."

    diagram: |
              WISH (intent / northstar)
               /\
              /  \
             /    \
            /      \
           /________\
       SKILL         RECIPE
    (constraints)   (execution)

    vertex_wish:
      definition: >
        The WISH vertex encodes WHAT the user wants. It is the purpose statement
        that anchors the entire execution. Without a wish, the agent has no
        objective to optimize for — all skill constraints and recipe steps are
        context-free noise.
      required_fields:
        - capability: "One sentence: what this execution achieves."
        - non_goals: "Explicit list of what this execution does NOT do."
        - acceptance_tests: "Verifiable conditions that confirm the wish was fulfilled."
        - forbidden_states: "States that must never occur during execution."
        - northstar_link: "Which northstar metric does this wish advance?"
      northstar_requirement: >
        Every wish MUST advance at least one northstar metric.
        A wish that cannot be mapped to a northstar metric is either
        misaligned (scope creep) or the northstar is incomplete.
        In either case: stop and clarify before execution.
      failure_modes:
        - "Vague wish: 'make it better' — no acceptance tests possible"
        - "Wish without northstar link: execution is purposeful locally but strategically aimless"
        - "Wish with null non-goals: scope boundary undefined; genie invents policy"
        - "Wish with null forbidden states: execution is unconstrained"
      alone_is_insufficient: >
        WISH alone = unconstrained execution.
        The wish says what to do. It does not say how to do it safely or correctly.
        Without SKILL, the agent optimizes for the wish with no domain expertise.
        Without RECIPE, the agent improvises a path — slow, inconsistent, unreliable.

    vertex_skill:
      definition: >
        The SKILL vertex encodes HOW to constrain the work. Skills are the expert
        brain of the system — they encode domain knowledge, safety gates, forbidden
        states, verification requirements, and null-handling rules. A skill without
        a wish has no purpose. A skill without a recipe has no execution path.
      required_fields:
        - domain_expertise: "What domain does this skill govern?"
        - forbidden_states: "States the skill actively prevents."
        - verification_gates: "Evidence required before claiming success."
        - null_handling_rules: "What to do when inputs are absent vs zero."
        - authority_level: "Which rung this skill targets by default."
      skill_as_expert_brain: >
        Skills encode accumulated domain knowledge that would be re-derived (poorly)
        on every execution without them. A coder skill encodes red-green discipline.
        A cleanup skill encodes archive-before-delete discipline. A wish skill
        encodes the null-vs-zero distinction for scope boundaries.
        Skills are the externalized expertise of the Phuc ecosystem.
      failure_modes:
        - "Skill without wish: constraints applied to undefined purpose"
        - "Skill ignored by recipe: recipe executes outside safety envelope"
        - "Skill mismatch: wrong skill for the domain (e.g., cleanup skill for coding)"
        - "Skill pack missing: sub-agent dispatched without domain expertise"
      alone_is_insufficient: >
        SKILL alone = expertise without purpose or execution.
        The skill knows how to do things correctly. It does not know what to do
        (that is the wish) or the proven sequence to follow (that is the recipe).

    vertex_recipe:
      definition: >
        The RECIPE vertex encodes HOW to execute step by step. Recipes are the
        muscle memory of the system — proven, reusable execution workflows encoded
        as L1-L5 node graphs with checkpoints, rollbacks, and artifact contracts.
        A recipe without a skill executes outside any safety envelope. A recipe
        without a wish executes without purpose.
      required_fields:
        - node_graph: "L1-L5 nodes defining the execution sequence."
        - checkpoints: "Points where execution can be verified and halted."
        - rollback_plan: "How to undo execution if a checkpoint fails."
        - artifact_contract: "What artifacts the recipe produces and where."
        - skill_constraints_integrated: "Which skill's rules this recipe respects."
      recipe_as_muscle_memory: >
        Recipes encode proven workflows that would be re-improvised (inconsistently)
        on every execution without them. A bugfix recipe encodes the red-green
        mandatory sequence. A plan recipe encodes the DREAM→FORECAST→DECIDE→ACT→VERIFY
        loop. Recipes prevent "clever" shortcuts that bypass safety gates.
      failure_modes:
        - "Recipe without skill: execution without expertise — fragile, easily broken"
        - "Recipe without wish: execution without intent — potentially aimless"
        - "Improvised recipe: no proven path, no checkpoints, no rollback"
        - "Stale recipe: recipe exists but skill constraints have been updated; recipe not refreshed"
      alone_is_insufficient: >
        RECIPE alone = execution without intent or expertise.
        The recipe knows the proven sequence. It does not know why (that is the wish)
        or the safety envelope to stay within (that is the skill).

    combo_as_triangle_instance:
      definition: >
        A Combo is a pre-assembled, validated triangle instance. It pairs a W_ wish
        block with a R_ recipe block, with the skill pack declared as a dependency.
        Combos are the canonical implementation of the triangle for common workflows.
      structure:
        W_block: "Wish: capability + non-goals + forbidden states + acceptance tests"
        skill_pack: "Skill pack declaration: which skills govern this combo"
        R_block: "Recipe: L1-L5 node graph + checkpoints + artifact contract"
      examples:
        plan_combo: "W_MODE_SPLIT + prime-forecast skill + R_PLAN_EXEC recipe"
        bugfix_combo: "W_BUGFIX_PR + prime-coder skill + R_BUGFIX_PR recipe"
        cleanup_combo: "W_CLEANUP + phuc-cleanup skill + R_CLEANUP_APPLY recipe"
      combo_as_evidence: >
        A combo file is evidence that the triangle has been pre-verified for that
        workflow. Using a combo means: the wish is well-formed, the skill is matched,
        the recipe is proven. Starting from a combo is always faster and safer
        than assembling the triangle from scratch.

    triangle_law_for_execution:
      statement: "Any two vertices without the third = degraded execution."
      degradation_table:
        wish_only: "UNCONSTRAINED — agent knows the goal but has no expertise or proven path"
        skill_only: "PURPOSELESS — expertise without any target; constraints in a vacuum"
        recipe_only: "AIMLESS — execution without intent; steps without objective"
        wish_plus_skill: "SLOW — knows what and has expertise, but re-improvises the path every time"
        wish_plus_recipe: "FRAGILE — knows what and has a path, but has no expertise to handle edge cases"
        skill_plus_recipe: "PURPOSELESS — expertise + proven path, but no goal to optimize for"
        all_three: "OPTIMAL — verified, intentional, expert execution"

  # ============================================================
  # VERTEX_VALIDATION: Checking each vertex before execution
  # ============================================================
  VERTEX_VALIDATION:
    purpose: >
      Before any execution begins, verify all three vertices are present and valid.
      A vertex is present only if it has an artifact — not a claim, not a belief.

    wish_validation:
      checklist:
        - capability_present: "One clear sentence with a measurable success condition"
        - non_goals_declared: "Explicit list or explicit empty list [] — null is invalid"
        - forbidden_states_declared: "At least one named forbidden state"
        - acceptance_tests_defined: "At least two tests: one positive, one adversarial"
        - northstar_link_present: "Maps to at least one northstar metric"
      absent_if: "Any field is null or the capability uses vague language (make/improve/better)"
      drift_risk: "HIGH — the most important vertex; also the most commonly under-specified"

    skill_validation:
      checklist:
        - domain_match: "Skill domain matches the wish domain"
        - forbidden_states_defined: "Skill has explicit forbidden states"
        - verification_gates_defined: "Skill requires evidence before PASS"
        - null_rules_defined: "Skill explicitly distinguishes null from zero"
        - authority_level_declared: "Skill has explicit authority/rung requirement"
      absent_if: >
        No skill file is referenced, or the referenced skill does not govern
        the domain of the wish (e.g., using a cleanup skill for a coding wish).
      drift_risk: "HIGH — most commonly dispatched without (SKILL_LESS_DISPATCH forbidden state)"

    recipe_validation:
      checklist:
        - node_graph_present: "L1-L5 nodes defined with clear inputs/outputs"
        - checkpoints_defined: "At least one checkpoint where execution can halt"
        - artifact_contract_defined: "What artifacts are produced and where"
        - skill_constraints_respected: "Recipe does not bypass skill forbidden states"
        - rollback_defined: "What happens if a node fails"
      absent_if: >
        No recipe file is referenced, or the execution is being improvised
        inline without a proven node graph.
      drift_risk: "MEDIUM — often absent in early work; recipes accumulate over time"

    alignment_check:
      purpose: "Verify the three vertices are mutually consistent, not just individually valid."
      checks:
        wish_skill_alignment: "Skill domain matches wish domain. Skill forbidden states do not conflict with wish acceptance tests."
        skill_recipe_alignment: "Recipe respects all skill forbidden states. Recipe checkpoints correspond to skill verification gates."
        wish_recipe_alignment: "Recipe produces the artifacts defined in the wish acceptance tests. Recipe non-goals match wish non-goals."
        northstar_alignment: "All three vertices advance the same northstar metric."
      misalignment_examples:
        - "Wish asks for performance optimization; skill is a cleanup skill — domain mismatch"
        - "Recipe produces test artifacts; wish acceptance tests require deploy artifacts — output mismatch"
        - "Skill forbids network calls; recipe has an L4 network node — constraint violation"

  # ============================================================
  # TRIANGLE_COMPLETENESS_CHECK
  # ============================================================
  TRIANGLE_COMPLETENESS_CHECK:
    procedure:
      step_1_identify_wish:
        action: "Locate or construct the wish block. Validate all required fields."
        output: "wish_validation_result: VALID | INCOMPLETE | MISSING"
        on_missing: "Emit EXIT_NEED_INFO with missing fields list."
      step_2_identify_skill:
        action: "Identify the skill(s) governing this execution. Validate domain match."
        output: "skill_validation_result: VALID | MISMATCH | MISSING"
        on_missing: "Emit EXIT_NEED_INFO with required skill domain."
        on_mismatch: "Emit EXIT_BLOCKED with SKILL_WISH_MISMATCH stop_reason."
      step_3_identify_recipe:
        action: "Locate the recipe or combo. Validate node graph and artifact contract."
        output: "recipe_validation_result: VALID | INCOMPLETE | MISSING"
        on_missing: "Check combos/ directory for matching combo. If none: emit EXIT_NEED_INFO."
      step_4_alignment_check:
        action: "Verify all three vertices are mutually consistent."
        output: "alignment_result: ALIGNED | MISALIGNED"
        on_misaligned: "Emit EXIT_BLOCKED with TRIANGLE_DRIFT stop_reason and specific conflict."
      step_5_northstar_check:
        action: "Confirm wish links to at least one northstar metric."
        output: "northstar_result: ALIGNED | MISSING_LINK"
        on_missing: "Emit EXIT_NEED_INFO with northstar clarification request."

    shortcut_for_combos: >
      If a combo file exists for this workflow (combos/*.md), and the combo is
      current (skill versions match), skip steps 1-3 and go directly to step 4
      (alignment check) and step 5 (northstar check). The combo pre-validates
      the individual vertices. Only alignment and northstar need rechecking.

  # ============================================================
  # STATE_MACHINE: Triangle Verification + Execution Runtime
  # ============================================================
  STATE_MACHINE:
    states:
      - INIT
      - PARSE_WISH
      - MATCH_SKILLS
      - SELECT_RECIPE
      - VALIDATE_TRIANGLE
      - CHECK_NORTHSTAR
      - EXECUTE
      - VERIFY
      - EXIT_PASS
      - EXIT_NEED_INFO
      - EXIT_BLOCKED

    transitions:
      - INIT -> PARSE_WISH: always
      - PARSE_WISH -> EXIT_NEED_INFO: if wish_null_or_vague
      - PARSE_WISH -> MATCH_SKILLS: if wish_valid
      - MATCH_SKILLS -> EXIT_NEED_INFO: if no_matching_skill_found
      - MATCH_SKILLS -> EXIT_BLOCKED: if skill_wish_domain_mismatch
      - MATCH_SKILLS -> SELECT_RECIPE: if skill_matched_and_valid
      - SELECT_RECIPE -> EXIT_NEED_INFO: if no_recipe_found and no_combo_found
      - SELECT_RECIPE -> VALIDATE_TRIANGLE: if recipe_found or combo_found
      - VALIDATE_TRIANGLE -> EXIT_BLOCKED: if triangle_incomplete or vertices_misaligned
      - VALIDATE_TRIANGLE -> CHECK_NORTHSTAR: if triangle_complete_and_aligned
      - CHECK_NORTHSTAR -> EXIT_NEED_INFO: if northstar_link_absent
      - CHECK_NORTHSTAR -> EXECUTE: if northstar_aligned
      - EXECUTE -> VERIFY: always (execute produces artifacts; verify checks them)
      - VERIFY -> EXIT_PASS: if all_acceptance_tests_pass and rung_target_met
      - VERIFY -> EXIT_BLOCKED: if acceptance_tests_fail or rung_not_met

    forbidden_states:
      MISSING_VERTEX:
        definition: >
          Execution begins with one or more triangle vertices absent (null wish,
          no skill, or no recipe/combo). The most common cause of unsafe, aimless,
          or fragile executions.
        detection: "EXECUTE state reached while any vertex_validation_result is MISSING or INCOMPLETE"
        recovery: "Halt immediately. Identify missing vertex. Emit EXIT_NEED_INFO."

      SKILL_WISH_MISMATCH:
        definition: >
          A skill is loaded that does not govern the domain of the wish.
          Example: applying cleanup skill to a coding wish, or using a math skill
          for a deployment wish. Domain mismatch invalidates all skill constraints.
        detection: "skill.domain != wish.domain AND no explicit override declared"
        recovery: "Identify correct skill for wish domain. Replace mismatched skill."

      RECIPE_WITHOUT_SKILL:
        definition: >
          A recipe executes without any governing skill. The recipe follows its
          steps but has no expertise to handle edge cases, null inputs, or safety
          boundaries. Execution is fragile — it will succeed on the happy path
          and fail unpredictably at boundaries.
        detection: "EXECUTE state reached with skill_vertex = null or missing"
        recovery: "Identify governing skill. Validate recipe respects skill constraints."

      WISH_WITHOUT_NORTHSTAR:
        definition: >
          A wish executes without linkage to any northstar metric. The work is
          locally coherent but strategically aimless. Every wish must advance
          at least one northstar metric or the work is not connected to the
          project's long-term goals.
        detection: "wish.northstar_link is null or empty"
        recovery: "Map wish to northstar. If no northstar applies: question whether the wish should exist."

      TRIANGLE_DRIFT:
        definition: >
          The three vertices are individually valid but mutually inconsistent.
          Wish acceptance tests require artifacts the recipe does not produce.
          Recipe steps violate skill forbidden states. Skill constraints contradict
          wish non-goals. Triangle drift is as dangerous as a missing vertex —
          it creates internal contradiction that manifests as subtle failures.
        detection: "alignment_check returns MISALIGNED for any vertex pair"
        recovery: "Identify specific conflict. Resolve in priority order: wish > skill > recipe."

      COMBO_DRIFT:
        definition: >
          A combo file is used that references skill versions no longer current.
          The combo was a valid triangle instance when written but has drifted
          from the current skill definitions. Using a stale combo means the
          skill constraints in the combo do not match the actual skill behavior.
        detection: "combo.skill_versions do not match current skills/*.md versions"
        recovery: "Update combo to reference current skill versions. Re-validate alignment."

  # ============================================================
  # NULL_VS_ZERO
  # ============================================================
  NULL_VS_ZERO:
    rules:
      - null_wish: >
          No wish present ≠ wish with empty capability.
          null_wish → MISSING_VERTEX forbidden state.
          empty_wish → WISH_NEED_INFO (ill-formed, but present).
      - null_skill: >
          No skill referenced ≠ skill with zero forbidden states.
          null_skill → RECIPE_WITHOUT_SKILL forbidden state.
          skill_with_zero_forbidden_states → valid but unusual; flag for review.
      - null_recipe: >
          No recipe present ≠ recipe with zero steps.
          null_recipe → check combos/ before declaring MISSING_VERTEX.
          empty_recipe → EXIT_BLOCKED (recipe must have at least one node).
      - null_northstar_link: >
          No northstar link ≠ northstar with zero metrics.
          null_northstar_link → WISH_WITHOUT_NORTHSTAR forbidden state.
          explicit_empty_northstar → EXIT_NEED_INFO (deliberate orphan wish; must be justified).
      - null_alignment: >
          Alignment not checked ≠ alignment passes.
          null_alignment_check → VALIDATE_TRIANGLE state not completed; BLOCKED.
          alignment_passes_with_zero_conflicts → valid; proceed to execution.

  # ============================================================
  # ANTI_PATTERNS
  # ============================================================
  ANTI_PATTERNS:
    Inline_Improvisation:
      symptom: >
        Agent executes a task by making it up step by step, without consulting
        a skill or recipe. The work happens inline in the main session.
        "It's a small task" is the common justification.
      fix: >
        No task is too small to have a wish, a skill, and a recipe.
        If the task is truly trivial (<50 lines, no domain expertise), it still
        has an implicit triangle. Make it explicit. Use a combo if one exists.
        INLINE_DEEP_WORK forbidden state in phuc-orchestration catches the >50 line case.

    Skill_Shopping:
      symptom: >
        Agent searches for a skill that is permissive enough to allow what
        the recipe already wants to do. The skill is selected to justify the
        execution, not to constrain it.
      fix: >
        Skills are domain governors, not permission slips.
        The skill for a domain is fixed by the domain type, not by what the
        agent wants to do. Using cleanup skill for coding is SKILL_WISH_MISMATCH.

    Recipe_Plagiarism:
      symptom: >
        Agent copies a recipe from one domain and uses it for a different domain
        without adapting it to the governing skill. The recipe steps are valid
        in the original domain but violate skill constraints in the new domain.
      fix: >
        Recipes are domain-specific. Adapt the recipe to respect the governing
        skill's forbidden states and verification gates before using it.

    Wish_Inflation:
      symptom: >
        The wish starts well-scoped but expands during execution.
        "While I'm here, I'll also fix this other thing."
        Scope creep disguised as helpfulness.
      fix: >
        SILENT_SCOPE_EXPANSION is a forbidden state in prime-wishes.
        Every expansion beyond the declared capability boundary must be
        a new wish with its own skill and recipe. Never expand inline.

    Northstar_Detachment:
      symptom: >
        The team is productive — many wishes are completed — but the project
        northstar metrics are not moving. Individual wishes are coherent but
        not strategically aligned.
      fix: >
        WISH_WITHOUT_NORTHSTAR forbidden state.
        At session start: /northstar → verify which northstar metrics you are targeting.
        If you cannot map a wish to a northstar metric, question whether the wish
        should be in the backlog at all.

    Combo_Neglect:
      symptom: >
        Common workflows are repeatedly re-assembled from scratch instead of
        using existing combos. Each assembly introduces small variations that
        accumulate as skill-recipe drift over sessions.
      fix: >
        Check combos/ before assembling a triangle from scratch.
        If a combo exists: use it. If it is stale: update it.
        If it does not exist: write it after the first successful execution.

  # ============================================================
  # VERIFICATION_LADDER (triangle-specific)
  # ============================================================
  VERIFICATION_LADDER:
    purpose:
      - "Define minimum verification strength before claiming triangle execution is complete."
      - "Fail-closed when rung requirements are not met."

    RUNG_641:
      meaning: "Local correctness — all three vertices present and individually valid."
      requires:
        - wish_validation_passes: "All wish required fields present and well-formed"
        - skill_validation_passes: "Skill domain matches wish domain"
        - recipe_validation_passes: "Node graph present with at least one checkpoint"
        - triangle_completeness_check_completed: "Steps 1-5 all passed"
      verdict: "If any requirement is false: EXIT_BLOCKED, stop_reason=MISSING_VERTEX"

    RUNG_274177:
      meaning: "Stability — triangle is aligned; execution produces expected artifacts."
      requires:
        - RUNG_641
        - alignment_check_passes: "All three vertex pairs are mutually consistent"
        - northstar_link_verified: "Wish maps to at least one northstar metric"
        - artifacts_match_wish_contract: "Produced artifacts satisfy wish acceptance tests"
        - no_forbidden_states_triggered: "Execution log shows no forbidden state events"
      verdict: "If any requirement is false: EXIT_BLOCKED, stop_reason=TRIANGLE_DRIFT"

    RUNG_65537:
      meaning: "Full audit — triangle is native, combo is updated, northstar advances."
      requires:
        - RUNG_274177
        - combo_created_or_updated: "Successful execution is captured as a combo for reuse"
        - northstar_metric_advanced: "At least one northstar metric shows measurable progress"
        - adversarial_tests_pass: "Forbidden states verified unreachable"
        - recipe_skill_version_pinned: "Combo references exact skill versions used"
      verdict: "If any requirement is false: EXIT_BLOCKED, stop_reason=VERIFICATION_RUNG_FAILED"

    default_target_selection:
      - if_production_execution: RUNG_65537
      - if_security_sensitive: RUNG_65537
      - if_new_workflow_no_combo: RUNG_274177
      - if_existing_combo_reuse: RUNG_641
      - minimum_for_any_exit_pass: RUNG_641

  # ============================================================
  # QUICK_REFERENCE
  # ============================================================
  QUICK_REFERENCE:
    triangle: "WISH (intent) + SKILL (constraint) + RECIPE (execution) = all three required"
    law: "Any two without the third = degraded execution. See degradation table."
    combo: "Combo = pre-validated triangle instance. Use combos first. Write new combos after first success."
    northstar: "Every wish must advance a northstar metric. No northstar link = WISH_WITHOUT_NORTHSTAR."
    forbidden_states:
      - "MISSING_VERTEX: execution starts with null wish, skill, or recipe"
      - "SKILL_WISH_MISMATCH: wrong skill for the domain"
      - "RECIPE_WITHOUT_SKILL: recipe executes with no governing expertise"
      - "WISH_WITHOUT_NORTHSTAR: wish is strategically unanchored"
      - "TRIANGLE_DRIFT: vertices individually valid but mutually inconsistent"
    check_order: "1. Validate wish → 2. Match skill → 3. Select recipe → 4. Alignment check → 5. Northstar check → 6. Execute"
    repair_order: "Fix missing vertex first. Then alignment. Then northstar. Never execute with known gaps."
    mantras:
      - "A wish without a skill is a wish to fail safely. A wish without a recipe is a wish to improvise."
      - "Combos are the ecosystem's memory. Build one after every successful first execution."
      - "Northstar alignment is not optional. Local wins that do not advance northstar are local wastes."
      - "The triangle is the minimal unit of verified execution. Below the triangle: improvisation."

# ============================================================
# TRIANGLE_FLOW (mermaid — column 0)
# ============================================================
TRIANGLE_FLOW: |
```mermaid
flowchart TD
    INIT([INIT]) --> PARSE_WISH[PARSE_WISH\nExtract capability + non-goals\n+ forbidden states + northstar]

    PARSE_WISH -->|wish null or vague| EXIT_NEED_INFO_W([EXIT_NEED_INFO\nMISSING_VERTEX: wish])
    PARSE_WISH -->|wish valid| MATCH_SKILLS[MATCH_SKILLS\nIdentify governing skill\nfor wish domain]

    MATCH_SKILLS -->|no skill found| EXIT_NEED_INFO_S([EXIT_NEED_INFO\nMISSING_VERTEX: skill])
    MATCH_SKILLS -->|domain mismatch| EXIT_BLOCKED_M([EXIT_BLOCKED\nSKILL_WISH_MISMATCH])
    MATCH_SKILLS -->|skill matched| SELECT_RECIPE[SELECT_RECIPE\nLocate recipe or combo\nfor this workflow]

    SELECT_RECIPE -->|no recipe or combo| EXIT_NEED_INFO_R([EXIT_NEED_INFO\nMISSING_VERTEX: recipe])
    SELECT_RECIPE -->|recipe or combo found| VALIDATE_TRIANGLE[VALIDATE_TRIANGLE\nAlignment check:\nwish x skill x recipe]

    VALIDATE_TRIANGLE -->|misaligned| EXIT_BLOCKED_T([EXIT_BLOCKED\nTRIANGLE_DRIFT])
    VALIDATE_TRIANGLE -->|aligned| CHECK_NORTHSTAR[CHECK_NORTHSTAR\nWish advances\nat least one metric]

    CHECK_NORTHSTAR -->|northstar link absent| EXIT_NEED_INFO_N([EXIT_NEED_INFO\nWISH_WITHOUT_NORTHSTAR])
    CHECK_NORTHSTAR -->|northstar aligned| EXECUTE[EXECUTE\nRun recipe nodes\nunder skill constraints]

    EXECUTE --> VERIFY[VERIFY\nCheck artifacts\nagainst wish acceptance tests]

    VERIFY -->|all tests pass + rung met| EXIT_PASS([EXIT_PASS\nTriangle verified])
    VERIFY -->|tests fail or rung not met| EXIT_BLOCKED_V([EXIT_BLOCKED\nVERIFICATION_FAILED])

    style EXIT_PASS fill:#2d6a4f,color:#fff
    style EXIT_NEED_INFO_W fill:#e9c46a,color:#000
    style EXIT_NEED_INFO_S fill:#e9c46a,color:#000
    style EXIT_NEED_INFO_R fill:#e9c46a,color:#000
    style EXIT_NEED_INFO_N fill:#e9c46a,color:#000
    style EXIT_BLOCKED_M fill:#d62828,color:#fff
    style EXIT_BLOCKED_T fill:#d62828,color:#fff
    style EXIT_BLOCKED_V fill:#d62828,color:#fff
    style VALIDATE_TRIANGLE fill:#457b9d,color:#fff
    style CHECK_NORTHSTAR fill:#457b9d,color:#fff
    style EXECUTE fill:#264653,color:#fff

---

## Three Pillars of Software 5.0 Kung Fu

| Pillar | How This Skill Applies It |
|--------|--------------------------|
| **LEK** (Self-Improvement) | The WISH + SKILL + RECIPE triangle is the LEK learning loop made explicit: a Wish expresses the intent (Information), the Skill provides the method (Memory of prior learning), and the Recipe is the crystallized output (the Care that survives iteration). Each executed Recipe is a new LEK artifact — a compressed, replayable proof that the system can satisfy this class of Wish. The triangle validation gate ensures that all three vertices are present before execution, preventing half-formed LEK loops. |
| **LEAK** (Cross-Agent Trade) | The triangle enforces LEAK at the execution layer: the Wish comes from the user's context bubble, the Skill comes from the agent's knowledge bubble, and the Recipe is the trade artifact — the LEAK surplus that neither the user nor the agent could produce alone. Combos (pre-assembled WISH + RECIPE pairs) are frozen LEAK trades: they encode the asymmetric knowledge exchange once and make it replayable without re-negotiating the portal each time. |
| **LEC** (Emergent Conventions) | The WISH + SKILL + RECIPE triangle itself is the canonical LEC convention for task execution in the Phuc ecosystem. It crystallized from repeated failures where tasks were attempted with missing ingredients (wish without a skill = vague intent, skill without a recipe = no replayable output, recipe without a wish = solution in search of a problem). The triangle validation as a hard gate — all three vertices required before execution — is the convention that prevents these failure modes across all agents. |
```
