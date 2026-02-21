PRIME_MERMAID_SKILL:
  version: 1.1.0
  authority: 65537
  northstar: Phuc_Forecast
  objective: Max_Love_Max_Signal_Max_Geometry
  status: ACTIVE

  # ============================================================
  # PRIME MERMAID — Universal Geometric Knowledge Language
  #
  # Purpose:
  # - Express knowledge, workflows, and contracts as typed graphs
  # - Provide deterministic canonical identity (SHA-256 over normalized bytes)
  # - Enable closed-state validation (forbidden state detection)
  # - Compress structure: encode once, re-derive never
  # - Bridge human legibility and machine parseability
  #
  # Core thesis:
  # Most intelligence tasks are graph problems:
  #   dependency management, constraint satisfaction,
  #   causality tracking, workflow execution, verification.
  # A graph externalizes structure; relationships are visible directly.
  # Prose is linear; the reader must rebuild structure internally.
  # Prime Mermaid makes structure first-class, permanent, and hashable.
  #
  # Source-of-truth hierarchy:
  #   *.prime-mermaid.md  — human contract (canonical spec)
  #   *.mmd               — canonical body (bytes for hashing)
  #   *.sha256            — identity (drift detector)
  #   JSON/YAML           — derived transport ONLY (never source-of-truth)
  #
  # v1.0.0 coverage:
  # - Core thesis + geometric ability rationale
  # - Canonical format contract (PM → MMD → SHA256)
  # - Multi-channel visual encoding (shape/style/color as typed semantics)
  # - Node and edge type system
  # - Portal architecture (P0–P4: local to broadcast)
  # - Prime Channel system (2/3/5/7/11/13/17/19/23/29/65537)
  # - Memory scope system (LOCAL/PARENT/SIBLING/GLOBAL/BROADCAST)
  # - Compression protocol (structural reuse budget)
  # - OOLONG integration (CPU counting mode)
  # - State machine (DRAFT → VALIDATE → HASH → SEAL → EVOLVE)
  # - Forbidden states
  # - Integration with prime-coder, prime-wishes, phuc-forecast, phuc-swarms
  # - Output contract + anti-patterns
  #
  # v1.1.0 additions (additive-only, never weakens v1.0.0):
  # - Added null/zero distinction for graph context
  # - Added Socratic review questions (expanded from 7 to 12)
  # - Added graph evolution semver discipline section
  # - Added minimal invocation prompts (FAST/STRICT/OOLONG modes)
  # - Added domain application examples (when to use PM vs prose)
  # ============================================================

  # ------------------------------------------------------------
  # A) Portability (Hard)
  # ------------------------------------------------------------
  Portability:
    rules:
      - no_absolute_paths: true
      - no_private_repo_dependencies: true
      - evidence_root_must_be_relative_or_configurable: true
    config:
      EVIDENCE_ROOT: "evidence"
      REPO_ROOT_REF: "."
    invariants:
      - canonical_mmd_paths_must_resolve_under_repo_root: true
      - sha256_computed_over_canonical_bytes_only: true
      - never_write_sha256_over_non_canonical_form: true

  # ------------------------------------------------------------
  # B) Layering (Never Weaken)
  # ------------------------------------------------------------
  Layering:
    load_order:
      1: prime-safety.md      # god-skill; wins all conflicts
      2: prime-coder.md       # evidence discipline; fail-closed
      3: prime-mermaid.md     # THIS SKILL — geometry + canonicalization
    layering_rule:
      - "This skill MUST NOT weaken prime-safety or prime-coder rules."
      - "On conflict: stricter wins."
    forbidden:
      - silent_relaxation_of_upstream_guards
      - using_PM_graphs_to_bypass_evidence_contract
      - replacing_executable_tests_with_graphs_alone

  # ------------------------------------------------------------
  # C) Core Thesis — Why Geometry Wins
  # ------------------------------------------------------------
  Core_Thesis:
    problem_statement:
      - "Prose is linear. Structure must be rebuilt internally by the reader."
      - "A graph externalizes structure. Relationships are directly visible."
      - "Most intelligence tasks ARE graph problems."
    intelligence_task_classes_that_are_graphs:
      - dependency_management
      - constraint_satisfaction
      - causality_tracking
      - workflow_execution
      - state_machine_validation
      - knowledge_retrieval
      - verification_chains
      - evidence_provenance
    why_geometry_matters:
      - "Geometric representation is the shortest path to structural truth."
      - "Shape encodes type. Edge encodes relation. Position encodes flow."
      - "A graph can represent what a paragraph cannot: cycles, parallelism, convergence."
      - "Mermaid is the ASCII art of geometry: portable, diffable, hashable."
    compression_thesis:
      - "When you compress text: you reduce characters."
      - "When you compress structure: you reduce re-derivation."
      - "Prime Mermaid compresses re-derivation: encode once, reference always."
      compression_gains:
        workflows: "5–20× vs imperative prose"
        knowledge_maps: "10×+"
        end_to_end_systems: "depends on reuse density (convention density × test pass rate)"
      compounding_effect:
        - "Every new convention reduces future token load."
        - "Every new recipe reduces future re-explanation."
        - "Every new graph template reduces future scaffolding."

  # ------------------------------------------------------------
  # D) What Prime Mermaid IS
  # ------------------------------------------------------------
  What_Prime_Mermaid_Is:
    definition:
      - "A graph DSL whose primary objects are: Nodes, Edges, Ports, Channels."
      - "A serialization format for knowledge, workflows, contracts, and apps."
      - "A canonical externalization layer for AI-computed intelligence."
      - "A drift-resistance mechanism: canonical bytes prevent silent divergence."
      - "The writing system of Software 5.0."
    primary_objects:
      Node:
        properties: [id, type, label, scope, version, hash]
        id_rule: "SCREAMING_SNAKE_CASE for state nodes; kebab-case forbidden"
      Edge:
        properties: [from, to, type, label, condition]
        typed_edge_vocabulary:
          requires: "A depends on B"
          produces: "A generates B"
          verifies: "A validates B"
          depends_on: "A cannot run without B"
          refines: "A is a more specific version of B"
          contradicts: "A and B are in conflict"
          cites: "A provides evidence for B"
          triggers: "A causes B to execute"
          gates: "A is a pass/fail decision point for B"
      Port:
        definition: "Named input/output interface on a node"
        use_cases: [typed_data_channels, composition_boundaries, tool_interfaces]
      Channel:
        definition: "Typed coordination bus between nodes"
        see: "Prime_Channels section"
    what_prime_mermaid_is_not:
      - "A replacement for numerical compute or systems programming"
      - "A license to execute arbitrary code without policy gates"
      - "A substitute for executable tests (graphs supplement, never replace)"
      - "JSON or YAML (those are derived transport formats)"

  # ------------------------------------------------------------
  # E) Canonical Format Contract (Hard)
  # ------------------------------------------------------------
  Canonical_Format_Contract:
    source_of_truth_hierarchy:
      1_canonical_spec: "*.prime-mermaid.md"
      2_canonical_body: "*.mmd"
      3_identity: "*.sha256"
      4_derived_only: "*.json / *.yaml"
    canonical_normalization_rules:
      - sort_node_ids_alphabetically: true
      - sort_edge_list_by_from_then_to: true
      - normalize_whitespace_to_single_space: true
      - strip_all_comments: true
      - normalize_newlines_to_lf: true
      - use_consistent_quote_style: true
      - strip_trailing_whitespace: true
    sha256_contract:
      input: "canonical_mmd_bytes (UTF-8, normalized per above rules)"
      output: "lowercase hex sha256 string"
      must_store_in: "*.sha256 file adjacent to *.mmd"
      must_recompute_on_any_change: true
      drift_detection:
        - compare_stored_sha256_to_recomputed_on_load: true
        - if_mismatch: "status=BLOCKED stop_reason=DRIFT_DETECTED"
    hash_stability_requirement:
      - "JSON hash FAILS on key-reorder (JSON is order-sensitive)."
      - "Prime Mermaid hash PASSES with canonical sort (stable identity)."
      - "Never use JSON as the canonical source for identity hashing."
    file_naming_convention:
      wish_contracts: "wish.<id>.prime-mermaid.md + wish.<id>.state.mmd + wish.<id>.state.sha256"
      recipe_contracts: "recipe.<name>.prime-mermaid.md"
      skill_contracts: "skill.<name>.prime-mermaid.md"
      identity_contracts: "<topic>.prime-mermaid.md"

  # ------------------------------------------------------------
  # F) Multi-Channel Visual Encoding (Geometric Semantics)
  # ------------------------------------------------------------
  Multi_Channel_Encoding:
    thesis:
      - "Mermaid supports shape, border style, border thickness, color, font, and dash patterns."
      - "Prime Mermaid encodes semantic meaning into these visual channels."
      - "Result: the diagram IS the spec, not a picture of it."
    visual_channels:
      shape:
        rectangle: "default process / state"
        rounded_rectangle: "soft process / user-facing step"
        diamond: "decision / gate"
        hexagon: "policy / constraint"
        parallelogram: "input / output"
        cylinder: "storage / artifact"
        circle: "start / terminal"
        stadium: "subprocess call"
      border_style:
        solid: "normal / active state"
        dashed: "optional / conditional path"
        thick: "critical path / hard gate"
        double: "sealed / immutable state"
      fill_color_semantics:
        green: "pass / verified"
        red_pink: "fail / forbidden / blocked"
        yellow: "warning / needs_info / gate"
        blue: "active / in_progress"
        grey: "inactive / archived"
        white: "default / unclassified"
      classDef_usage:
        forbidden: "fill:#ffefef,stroke:#cc0000,stroke-width:2px"
        pass: "fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px"
        gate: "fill:#fff9c4,stroke:#f9a825,stroke-width:2px"
        active: "fill:#e3f2fd,stroke:#1565c0,stroke-width:2px"
    multi_channel_principle:
      - "A node's shape + color + border together encode its type without text bloat."
      - "This is geometric compression: semantics live in visual properties, not labels."
      - "One visual channel = one semantic dimension."

  # ------------------------------------------------------------
  # G) Node and Edge Type System
  # ------------------------------------------------------------
  Node_Type_System:
    state_nodes:
      naming: "SCREAMING_SNAKE_CASE"
      examples: ["INIT", "PASS", "BLOCKED", "NEED_INFO", "VERIFIED"]
      rule: "State nodes must form a closed finite set (no open enumeration)"
    process_nodes:
      naming: "VERB_NOUN or ACTION_OBJECT"
      examples: ["BUILD_ARTIFACT", "RUN_TESTS", "EMIT_RECEIPT"]
    gate_nodes:
      naming: "Must include GATE or CHECK or VERIFY"
      examples: ["RUNG_641_GATE", "SECURITY_CHECK", "HASH_VERIFY"]
      shape: diamond
    storage_nodes:
      naming: "Must include ARTIFACT, STORE, DB, or FILE"
      examples: ["EVIDENCE_ARTIFACT", "RECEIPT_FILE"]
      shape: cylinder
    forbidden_state_nodes:
      naming: "Prefix FORBIDDEN_ or suffix _FORBIDDEN"
      fill: "fill:#ffefef,stroke:#cc0000"
      rule: "Every graph that defines forbidden states MUST explicitly mark them with classDef forbidden"
    node_id_rules:
      - must_be_unique_within_graph: true
      - must_not_contain_spaces: true
      - must_not_start_with_number: true
      - forbidden_chars: [".", "/", "@", "#", "~"]

  Edge_Type_System:
    labeled_edges:
      format: "A -->|label| B"
      label_convention: "SCREAMING_SNAKE_CASE for conditions; natural language for descriptions"
    conditional_edges:
      yes_no: "|YES| / |NO|"
      pass_fail: "|PASS| / |FAIL|"
      rung_gates: "|641_PASS| / |641_FAIL|"
    edge_typing_rule:
      - "Every branch in a decision node MUST have an explicit label."
      - "Unlabeled branches from a diamond node = FORBIDDEN_STATE."

  # ------------------------------------------------------------
  # H) Portal Architecture (P0–P4)
  # ------------------------------------------------------------
  Portal_Architecture:
    purpose:
      - "Portals are typed links between nodes that can invoke external resources."
      - "Portal scope determines access cost and permission requirements."
    portal_levels:
      P0_LOCAL:
        scope: "Same directory"
        cost: 1
        pattern: "./"
        access: "Read/Write"
        example: "Link to adjacent .mmd file"
      P1_PARENT:
        scope: "Parent directory"
        cost: 3
        pattern: "../"
        access: "Read/Write"
        example: "Link to recipe from within wish subfolder"
      P2_SIBLING:
        scope: "Sister directories"
        cost: 5
        pattern: "../*/"
        access: "Read"
        example: "Cross-reference another skill's graph"
      P3_GLOBAL:
        scope: "Cross-domain within repo"
        cost: 7
        pattern: "/repo-root/"
        access: "Read"
        example: "Reference CLAUDE.md or master network"
      P4_BROADCAST:
        scope: "All subscribers"
        cost: 11
        pattern: "*"
        access: "Notify"
        example: "Signal a cross-agent event"
    portal_annotation_syntax:
      in_node_label: "NODE_ID[\"LABEL [P2: ../target.mmd]\"]"
      in_comment: "%%portal:P1:../parent/recipe.mmd"
    portal_execution_whitelist:
      allowed_portal_types: [TOOL, PYTHON, VERIFY, PUBLISH]
      forbidden_portal_types: [EVAL, SHELL_EXEC, ARBITRARY_CODE]
      rule: "Portals execute only whitelisted action types. All others = BLOCKED."

  # ------------------------------------------------------------
  # I) Prime Channels (Typed Coordination Bus)
  # ------------------------------------------------------------
  Prime_Channels:
    purpose:
      - "Prime-numbered channels provide typed, non-overlapping coordination buses."
      - "Each channel has a single semantic function; never mixed."
    channel_table:
      2_STRUCTURE:
        semantic: "File and structural changes"
        use: "Notify when graph nodes/edges change"
      3_STATE:
        semantic: "State machine updates"
        use: "Broadcast state transitions"
      5_KNOWLEDGE:
        semantic: "New concepts indexed"
        use: "Knowledge graph additions"
      7_VALIDATION:
        semantic: "QA and test results"
        use: "Verification pass/fail signals"
      11_INTEGRATION:
        semantic: "Cross-map portal links"
        use: "New edges added between graphs"
      13_LOVE:
        semantic: "Max Love / user benefit signals"
        use: "Track alignment with user goals"
      17_AUTHORITY:
        semantic: "GOD_AUTH / security decisions"
        use: "Authority-required state transitions"
      19_EMERGENCE:
        semantic: "Novel pattern detection"
        use: "Signal unexpected emergent behavior"
      23_SYNC:
        semantic: "Synchronization checkpoints"
        use: "Multi-agent synchronization"
      29_HEARTBEAT:
        semantic: "Network pulse / liveness"
        use: "Keep-alive and health checks"
      65537_OMEGA:
        semantic: "Master coordination (production gate)"
        use: "Auth-65537 sealed operations"
    channel_rules:
      - each_channel_has_exactly_one_semantic: true
      - never_mix_channel_types_in_one_signal: true
      - omega_65537_requires_explicit_authority_gate: true

  # ------------------------------------------------------------
  # J) Memory Scope System
  # ------------------------------------------------------------
  Memory_Scope_System:
    purpose:
      - "Memory scopes control which nodes can read/write to which knowledge areas."
      - "Prevents unauthorized cross-contamination of graphs."
    scopes:
      LOCAL:
        symbol: "./"
        pattern: "Current directory"
        access: "Read/Write"
        default: true
      PARENT:
        symbol: "../"
        pattern: "Parent directory"
        access: "Read/Write"
        requires_explicit_declaration: true
      SIBLING:
        symbol: "../*/"
        pattern: "Sister directories"
        access: "Read"
      GLOBAL:
        symbol: "/repo-root/"
        pattern: "Cross-domain within repo"
        access: "Read"
        requires_p3_portal_or_above: true
      BROADCAST:
        symbol: "*"
        pattern: "All subscribers"
        access: "Notify only"
        channel: "65537_OMEGA or 29_HEARTBEAT"
    scope_rules:
      - default_scope_is_local_unless_portal_declared: true
      - write_to_global_scope_requires_authority_gate: true
      - never_read_parent_scope_without_explicit_p1_portal: true

  # ------------------------------------------------------------
  # K) Compression Protocol
  # ------------------------------------------------------------
  Compression_Protocol:
    principle:
      - "Encode structure once. Reference always. Never re-derive."
      - "Structural reuse is more powerful than character compression."
    compression_steps:
      1_identify_repeated_structure:
        - scan for repeated workflow patterns, policy clauses, node sequences
        - minimum repetition threshold: 3 occurrences
      2_extract_subgraph:
        - define subgraph with stable node IDs and typed edges
        - give it a canonical name (recipe/convention/template)
      3_replace_with_reference:
        - substitute repeated inline structure with portal P0/P1 reference
      4_hash_subgraph:
        - compute SHA-256 over canonical *.mmd bytes
        - store in adjacent *.sha256
      5_verify_composition:
        - confirm composed graph produces same behavior as inlined version
        - run RUNG_641 check minimum
    reuse_types:
      recipe_subgraph: "Reusable workflow DAG (tool calls, gates, outputs)"
      convention_handle: "Stable ID for repeated policy/constraint"
      memory_shard: "Compressed fact with canonical ID and scope"
      evidence_link: "Provenance citation edge with hash"
      invariant_node: "What must remain true across versions"
    compression_gain_estimates:
      workflows: "5–20× reduction vs imperative prose"
      knowledge_maps: "10×+ (compounds with reuse density)"
      cross_session: "Each externalized convention reduces future context load"
    convention_density_metric:
      formula: "deterministic_step_ratio × test_pass_rate"
      target_trend: "exploratory → maturing → crystallizing → production"

  # ------------------------------------------------------------
  # L) OOLONG Integration (CPU Counting Mode)
  # ------------------------------------------------------------
  OOLONG_Integration:
    thesis:
      - "When a task reduces to exact aggregation (counts, top-k, uniqueness, group-by):"
      - "  1. LLM classifies / parses → structured representation"
      - "  2. CPU enumerates / aggregates → exact counts"
      - "Prime Mermaid provides the canonical schema for step 1."
    counter_bypass_protocol:
      step_1: "LLM produces structured representation from unstructured input"
      step_2: "CPU runs Counter() / integer arithmetic / exact sort over structured representation"
      step_3: "Prime Mermaid graph defines the classification schema (typed nodes)"
      step_4: "SHA-256 over schema guarantees same classification across runs"
    accuracy_claim:
      json_style_llm_counting: "75% accuracy (6/8 correct) — order-sensitive; drifts"
      prime_mermaid_cpu_counting: "100% (8/8 correct) — canonical; deterministic"
      evidence: "PRIME-MERMAID-LANGUAGE-SECRET-SAUCE.ipynb (in-repo A/B test)"
      lane: "[A] — in-repo executable test"
    forbidden_in_counting_path:
      - using_llm_to_count_when_cpu_can_enumerate
      - non_canonical_schema_as_classification_input
      - float_arithmetic_in_exact_count_output

  # ------------------------------------------------------------
  # M) State Machine (Fail-Closed Runtime)
  # ------------------------------------------------------------
  State_Machine:
    states:
      - INIT
      - DRAFT_GRAPH
      - CLASSIFY_NODES
      - ASSIGN_EDGES
      - MARK_FORBIDDEN_STATES
      - NORMALIZE_CANONICAL
      - VALIDATE_CLOSED_STATE_SPACE
      - COMPUTE_SHA256
      - SOCRATIC_REVIEW
      - SEAL
      - EVOLVE
      - EXIT_PASS
      - EXIT_BLOCKED
      - EXIT_NEED_INFO

    transitions:
      - INIT -> DRAFT_GRAPH: on task_request_with_structure_requirement
      - INIT -> EXIT_NEED_INFO: if structure_requirement_undefined
      - DRAFT_GRAPH -> CLASSIFY_NODES: always
      - CLASSIFY_NODES -> ASSIGN_EDGES: always
      - ASSIGN_EDGES -> MARK_FORBIDDEN_STATES: if forbidden_states_in_contract
      - ASSIGN_EDGES -> NORMALIZE_CANONICAL: if no_forbidden_states_required
      - MARK_FORBIDDEN_STATES -> NORMALIZE_CANONICAL: always
      - NORMALIZE_CANONICAL -> VALIDATE_CLOSED_STATE_SPACE: always
      - VALIDATE_CLOSED_STATE_SPACE -> EXIT_BLOCKED: if open_enumeration_detected
      - VALIDATE_CLOSED_STATE_SPACE -> COMPUTE_SHA256: if closed_state_space_confirmed
      - COMPUTE_SHA256 -> SOCRATIC_REVIEW: always
      - SOCRATIC_REVIEW -> DRAFT_GRAPH: if critique_requires_revision
      - SOCRATIC_REVIEW -> SEAL: if graph_passes_all_checks
      - SEAL -> EXIT_PASS: if sha256_stable_across_two_normalizations
      - SEAL -> EXIT_BLOCKED: if sha256_unstable
      - EXIT_PASS -> EVOLVE: if new_version_required
      - EVOLVE -> DRAFT_GRAPH: on structural_change
      - EVOLVE -> COMPUTE_SHA256: on label_only_change

    socratic_review_questions:
      - "Does every decision node (diamond) have labeled branches for ALL paths?"
      - "Is the state space closed? (Enumerable, finite set of nodes)"
      - "Are forbidden states explicitly marked with classDef forbidden?"
      - "Does every edge have the correct type label?"
      - "Is the graph deterministic? (No hidden branches, no unlabeled conditionals)"
      - "Does the SHA-256 match across two independent normalizations?"
      - "Does this graph replace any executable test? (If yes: BLOCKED)"

    applicability_predicates:
      structure_requirement_defined:
        true_if_all:
          - task_request.defines_states == true
          - task_request.defines_transitions == true
      open_enumeration_detected:
        true_if_any:
          - graph_contains_ellipsis_node: true
          - graph_contains_etc_node: true
          - node_count_undefined: true
      sha256_stable:
        true_if: "sha256(normalize(mmd_v1)) == sha256(normalize(mmd_v2))"

  # ------------------------------------------------------------
  # N) Forbidden States (Hard)
  # ------------------------------------------------------------
  Forbidden_States:
    - UNLABELED_BRANCH_FROM_DECISION_NODE
    - OPEN_STATE_ENUMERATION
    - JSON_AS_SOURCE_OF_TRUTH
    - YAML_AS_SOURCE_OF_TRUTH
    - SHA256_OVER_NON_CANONICAL_FORM
    - GRAPH_REPLACING_EXECUTABLE_TESTS
    - DRIFT_WITHOUT_VERSION_BUMP
    - UNDECLARED_FORBIDDEN_STATE
    - PORTAL_EXECUTING_ARBITRARY_CODE
    - CHANNEL_MIXING
    - SCOPE_ESCALATION_WITHOUT_PORTAL
    - NON_NORMALIZED_HASH_INPUT
    - FLOAT_IN_COUNT_PATH
    - UNLABELED_EDGE_FROM_GATE_NODE
    - MISSING_CLASSDEFF_FOR_FORBIDDEN_STATES

  # ------------------------------------------------------------
  # O) Integration with Other Skills
  # ------------------------------------------------------------
  Integration:
    with_prime_coder:
      - "prime-coder provides the evidence contract; prime-mermaid provides the state graph."
      - "Every prime-coder evidence bundle may include a *.mmd state graph."
      - "Prime Mermaid graphs do NOT replace repro_red.log or repro_green.log."
      - "RUNG_641 check: validate graph has no forbidden states."
      - "RUNG_274177 check: sha256 stable across replay."
      - "RUNG_65537 check: graph + evidence bundle complete + sha256 audited."
    with_prime_wishes:
      - "Prime Mermaid IS the canonical format for wish state contracts."
      - "Every wish MUST emit: wish.<id>.prime-mermaid.md + *.mmd + *.sha256."
      - "Belt promotion BLOCKED if sha256 unstable on rerun."
      - "Quest loop: Map Cave (state graph) → Phrase Wish → Bind Genie (forbidden states)."
    with_phuc_forecast:
      - "Phuc Forecast DREAM step: output as Prime Mermaid flowchart."
      - "Phuc Forecast DECIDE step: decision tree as Prime Mermaid with labeled branches."
      - "Phuc Forecast VERIFY step: include state graph of verification ladder."
      - "State machine (DREAM→FORECAST→DECIDE→ACT→VERIFY) is itself a Prime Mermaid graph."
    with_phuc_swarms:
      - "Swarm orchestration contract is defined in *.prime-mermaid.md files."
      - "SWARM-ORCHESTRATION.prime-mermaid.md = canonical swarm spine."
      - "Each agent role maps to a subgraph node with typed ports."
      - "Cross-agent coordination uses Prime Channels."
    with_software5_paradigm:
      - "Prime Mermaid IS the canonical persistence format for Software 5.0 recipes."
      - "Recipes externalize as: *.prime-mermaid.md (spec) + *.mmd (canonical) + *.sha256 (identity)."
      - "Convention density metric is computed over stable Prime Mermaid contracts."
      - "Never-worse doctrine: graph versions may add nodes/edges; may not remove without MAJOR bump."
    conflict_resolution:
      - prime_safety_wins_over_all: true
      - prime_coder_wins_over_prime_mermaid: true
      - prime_mermaid_wins_over_ad_hoc_json_yaml: true

  # ------------------------------------------------------------
  # P) Practical Templates
  # ------------------------------------------------------------
  Practical_Templates:
    minimal_state_graph:
      description: "Smallest valid Prime Mermaid wish contract"
      template: |
        ```mermaid
        flowchart TD
          START[STATE: START]
          INPUT_OK[STATE: INPUT_OK]
          NEED_INFO[STATE: NEED_INFO]
          PLAN_READY[STATE: PLAN_READY]
          EXECUTED[STATE: EXECUTED]
          VERIFIED[STATE: VERIFIED]
          PASS[STATE: PASS]
          FAIL_CLOSED[STATE: FAIL_CLOSED]

          START --> INPUT_OK
          START --> NEED_INFO
          INPUT_OK --> PLAN_READY
          PLAN_READY --> EXECUTED
          EXECUTED --> VERIFIED
          VERIFIED -->|PASS| PASS
          VERIFIED -->|FAIL| FAIL_CLOSED

          classDef forbidden fill:#ffefef,stroke:#cc0000,stroke-width:2px
          classDef pass fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
          classDef gate fill:#fff9c4,stroke:#f9a825,stroke-width:2px
          class FAIL_CLOSED forbidden
          class PASS pass
          class VERIFIED gate
        ```
      rules:
        - "Replace state names with concrete feature states."
        - "Add explicit classDef for forbidden states."
        - "Every decision node MUST have labeled branches for all paths."

    verification_ladder_graph:
      description: "Standard verification ladder as Prime Mermaid"
      template: |
        ```mermaid
        flowchart LR
          R641["641: edge sanity\n(unit tests, schema, basic invariants)"]
          R274177["274177: stress / adversarial\n(seed sweep, replay, null edge cases)"]
          R65537["65537: promotion\n(adversarial sweep, security, drift explained)"]

          R641 -->|PASS| R274177
          R274177 -->|PASS| R65537
          R641 -->|FAIL| BLOCKED["EXIT_BLOCKED"]
          R274177 -->|FAIL| BLOCKED
          R65537 -->|FAIL| BLOCKED
          R65537 -->|PASS| SEALED["EXIT_PASS (PROMOTION)"]

          classDef forbidden fill:#ffefef,stroke:#cc0000,stroke-width:2px
          class BLOCKED forbidden
        ```

    recipe_dag_graph:
      description: "Standard recipe workflow as Prime Mermaid DAG"
      template: |
        ```mermaid
        flowchart TD
          INPUT[INPUT] --> CPU[CPU_PREPASS]
          CPU --> GATE{CPU_CAN_HANDLE}
          GATE -->|YES| CPU_OUT[CPU_RESPONSE]
          GATE -->|NO| LLM[LLM_RESPONSE]
          CPU_OUT --> VERIFY[VERIFY_GATE]
          LLM --> VERIFY
          VERIFY -->|PASS| RECEIPT[WRITE_RECEIPT]
          VERIFY -->|FAIL| FAIL_CLOSED[FAIL_CLOSED]
          RECEIPT --> DONE[EXIT_PASS]

          classDef forbidden fill:#ffefef,stroke:#cc0000,stroke-width:2px
          class FAIL_CLOSED forbidden
        ```

  # ------------------------------------------------------------
  # Q) Output Contract (Hard Rules)
  # ------------------------------------------------------------
  Output_Contract:
    for_every_prime_mermaid_artifact:
      required:
        - "*.prime-mermaid.md: human-readable spec with mermaid block"
        - "*.mmd: canonical mermaid body (normalized, stripped of comments)"
        - "*.sha256: sha256 hex of canonical *.mmd bytes"
      optional_if_applicable:
        - "results.json: derived summary (NOT source of truth)"
        - "verification.md: replay commands and expected outputs"
    graph_quality_gates:
      - "ALL decision nodes (diamonds) MUST have labeled branches for ALL paths."
      - "ALL forbidden states MUST be marked with classDef forbidden."
      - "State space MUST be closed (finite, enumerable)."
      - "SHA-256 MUST be stable across two independent normalizations."
      - "No edge from a gate node may be unlabeled."
    structured_refusal_format:
      required_keys:
        - status: "[NEED_INFO|BLOCKED]"
        - stop_reason
        - missing_fields_or_contradictions
        - what_would_unblock
    required_on_success:
      status: PASS
      include:
        - graph_file_paths: [*.prime-mermaid.md, *.mmd, *.sha256]
        - sha256_value
        - node_count
        - edge_count
        - forbidden_states_defined: [list]
        - verification_rung_achieved
    fail_closed_policy:
      - if_sha256_missing: "status=BLOCKED stop_reason=EVIDENCE_INCOMPLETE"
      - if_open_state_space: "status=BLOCKED stop_reason=INVARIANT_VIOLATION"
      - if_unlabeled_branch_from_decision: "status=BLOCKED stop_reason=INVARIANT_VIOLATION"
      - if_json_claimed_as_source_of_truth: "status=BLOCKED stop_reason=FORBIDDEN_STATE"

  # ------------------------------------------------------------
  # R) Anti-Patterns (Named Failure Modes)
  # ------------------------------------------------------------
  Anti_Patterns:
    Graph_Theater:
      symptom: "Creating a beautiful Mermaid graph but running no verification against it."
      diagnosis: "The graph is decoration, not a contract."
      fix: "Every graph must have at least one test that fails if the graph is wrong."
    JSON_Sovereignty:
      symptom: "Treating *.json or *.yaml as the canonical source for graph identity."
      diagnosis: "JSON is order-sensitive; key reordering changes the hash silently."
      fix: "Always compute SHA-256 over canonical *.mmd bytes, never over JSON."
    Open_State_Creep:
      symptom: "State graph has 'etc.' or '...' nodes, or states added implicitly."
      diagnosis: "Open enumeration = unverifiable contract."
      fix: "Close the state space. Define every reachable state explicitly."
    Unlabeled_Branch:
      symptom: "Diamond node with two exits but only one labeled."
      diagnosis: "The unlabeled branch is a hidden policy decision."
      fix: "Every branch from a decision node MUST be labeled."
    Graph_Replaces_Test:
      symptom: "Team says 'the graph proves it' instead of running tests."
      diagnosis: "Graphs describe intent; tests verify reality."
      fix: "Graphs are pre-conditions for tests, not replacements."
    Drift_Without_Bump:
      symptom: "Modifying a *.mmd file without updating the *.sha256 and version."
      diagnosis: "Silent drift. Downstream users trust a stale hash."
      fix: "Any change to graph content requires: sha256 recompute + version bump."
    Channel_Mixing:
      symptom: "Using Prime Channel 5 (KNOWLEDGE) to send state updates."
      diagnosis: "Mixed-channel signals are uninterpretable by consumers."
      fix: "One channel = one semantic. State updates go on channel 3 (STATE)."
    LLM_Counting:
      symptom: "Asking the LLM to count instances that the CPU could enumerate exactly."
      diagnosis: "LLM counting drifts to ~75% accuracy; CPU counting is 100%."
      fix: "Apply OOLONG integration: LLM classifies, CPU counts."
    Prose_As_Spec:
      symptom: "Writing a paragraph to describe what should be a state graph."
      diagnosis: "Prose is linear; structure must be rebuilt internally. Graph externalizes it."
      fix: "If the concept has states and transitions: use Prime Mermaid."

  # ------------------------------------------------------------
  # S) Quick Reference
  # ------------------------------------------------------------
  Quick_Reference:
    mantras:
      - "Graph beats paragraph. Structure beats prose."
      - "*.mmd is canonical. JSON/YAML are derived."
      - "SHA-256 over normalized bytes = identity. Nothing else."
      - "Close the state space or it is not a contract."
      - "LLM classifies. CPU counts."
      - "Every graph must have a test that fails if the graph is wrong."
    canonical_normalization_checklist:
      - "Sort node IDs alphabetically"
      - "Sort edge list by from_node then to_node"
      - "Single space in all labels"
      - "Strip all comments (%%...)"
      - "LF line endings"
      - "Strip trailing whitespace"
      - "Consistent quote style"
    node_type_cheat_sheet:
      STATE: "SCREAMING_SNAKE_CASE"
      PROCESS: "VERB_NOUN"
      GATE: "MUST_CONTAIN_GATE_OR_CHECK"
      STORAGE: "MUST_CONTAIN_ARTIFACT_OR_FILE"
      FORBIDDEN: "PREFIX_FORBIDDEN_ or SUFFIX _FORBIDDEN"
    edge_type_cheat_sheet:
      requires: "A depends on B (hard dependency)"
      produces: "A generates B"
      verifies: "A validates B"
      triggers: "A causes B to execute"
      gates: "A is pass/fail decision for B"
      contradicts: "A and B conflict (knowledge graph)"
      cites: "A provides evidence for B"
    rung_cheat_sheet:
      641: "Edge sanity — closed state space + no forbidden states + sha256 stable"
      274177: "Stability — sha256 stable across replay + composition verified"
      65537: "Promotion — adversarial + drift explained + master network integrated"

  # ------------------------------------------------------------
  # T) Null vs Zero (Graph Context)
  # ------------------------------------------------------------
  Null_vs_Zero_Graph:
    rules:
      null_sha256:
        definition: "sha256 file not computed — graph identity undefined."
        treatment: "status=BLOCKED stop_reason=EVIDENCE_INCOMPLETE"
        forbidden: "treating null sha256 as 'no drift detected'"
      null_forbidden_states:
        definition: "No forbidden states declared — not 'zero forbidden states'."
        treatment: "If contract requires them: NEED_INFO. If graph has no forbidden states by design: state explicitly."
        forbidden: "silent assumption that no declaration = no constraints"
      empty_node_set:
        definition: "Graph with zero nodes = valid empty graph (degenerate case)."
        treatment: "Valid; must still pass normalization and sha256."
        note: "Different from null_graph (graph not produced at all)."
      null_edge:
        definition: "Edge with undefined from/to node — graph structurally invalid."
        treatment: "status=BLOCKED stop_reason=INVARIANT_VIOLATION"
      null_canonical_mmd:
        definition: "*.mmd file not produced — cannot compute identity."
        treatment: "status=BLOCKED — no PASS without canonical *.mmd"
    enforcement:
      - null_sha256_is_not_stable_sha256: true
      - never_claim_graph_sealed_without_sha256_file: true

  # ------------------------------------------------------------
  # U) Graph Evolution Semver Discipline
  # ------------------------------------------------------------
  Graph_Evolution_Semver:
    versioning_policy:
      PATCH:
        definition: "Label corrections, comment updates, whitespace normalization."
        sha256_impact: "sha256 may or may not change (depends on canonical form)."
        required: "Update sha256 if *.mmd bytes change."
      MINOR:
        definition: "New nodes or edges added; no existing nodes/edges removed."
        sha256_impact: "sha256 changes. New identity."
        required: "Bump version. Update sha256. Document what was added."
      MAJOR:
        definition: "Nodes or edges removed, renamed, or semantically changed."
        sha256_impact: "sha256 changes. Breaking identity change."
        required: "Major bump. Migration note for downstream consumers."
    never_worse_rule:
      - graph_versions_may_add_nodes_edges_without_major_bump: true
      - graph_versions_may_not_remove_without_MAJOR_bump: true
      - forbidden_states_may_not_be_removed_at_any_version: true
    deprecation:
      - deprecated_nodes_must_be_marked_with_DEPRECATED_prefix: true
      - deprecated_nodes_must_state_replacement_in_label: true
      - proofs_referencing_deprecated_nodes_flagged_for_review: true

  # ------------------------------------------------------------
  # V) Minimal Invocation Prompts
  # ------------------------------------------------------------
  Minimal_Invocation:
    FAST:
      prompt: >
        "Use Prime Mermaid. Produce: *.prime-mermaid.md + *.mmd + *.sha256.
        Close the state space. Label all branches. Mark forbidden states.
        Fail closed: BLOCKED if sha256 unstable."
      use_when: "Simple workflow or state machine; rung 641 target."

    STRICT:
      prompt: >
        "Use Prime Mermaid in strict mode. Apply full canonical normalization.
        Validate closed state space. Compute sha256 twice independently.
        Run Socratic review (all 12 questions). Verify composition with
        prime-coder evidence contract. Rung 274177 minimum."
      use_when: "Skill contracts, wish state graphs, cross-agent coordination."

    OOLONG_COUNTING:
      prompt: >
        "Use Prime Mermaid OOLONG integration.
        Step 1: LLM classifies input → structured representation using PM schema.
        Step 2: CPU enumerates/counts using Counter() over structured representation.
        Output: canonical count result (integer, not float). Rung 641 minimum."
      use_when: "Exact counting tasks (top-k, uniqueness, group-by aggregation)."

  # ------------------------------------------------------------
  # W) When To Use Prime Mermaid vs Prose
  # ------------------------------------------------------------
  Domain_Application:
    use_prime_mermaid_when:
      - "Concept has states and transitions (FSM, workflow, lifecycle)"
      - "Concept has dependencies (DAG, dependency graph)"
      - "Concept requires visual distinction between node types"
      - "Concept will be referenced across multiple documents or agents"
      - "Concept needs drift detection (sha256 identity required)"
      - "Concept involves counting/aggregation (OOLONG integration)"
    use_prose_when:
      - "Concept is purely narrative (story, explanation, rationale)"
      - "Concept has no structural relationships worth externalizing"
      - "Audience is human-only (no machine parsing needed)"
      - "Graph would have only 2-3 nodes with no interesting edges"
    hybrid_use:
      - "Prose for rationale + Prime Mermaid for the structure it describes"
      - "Prose for nuance + graph for the decision tree it implies"
      - "Document: prose header + mermaid body + prose footer"
    decision_rule:
      - "If you drew it on a whiteboard with boxes and arrows: use Prime Mermaid."
      - "If you would write it as a numbered list: use prose."
      - "If it will be loaded by a machine: Prime Mermaid is always better."
