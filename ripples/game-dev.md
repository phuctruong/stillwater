---
ripple_id: ripple.game-dev
version: 1.0.0
base_skills: [prime-coder, phuc-loop]
persona: Game developer (Unity 6 / Godot 4, C# / GDScript, 2D/3D, indie to mid-size studio)
domain: game-dev
author: contributor:indie-game-studio
swarm_agents: [architect, ux, skeptic, ops, scientist]
---

# Game Development Ripple

## Domain Context

This ripple configures prime-coder and phuc-loop for game development workflows
in Unity (C#, URP/HDRP) and Godot 4 (GDScript/C#):

- **Engines:** Unity 6 LTS, Godot 4.x
- **Languages:** C# (.NET 8), GDScript, HLSL/ShaderLab
- **Platforms:** PC (Steam), mobile (iOS/Android), console (Switch/PS5/Xbox)
- **Physics:** Unity PhysX, Godot Jolt integration
- **Rendering:** URP, HDRP, Godot Forward+, custom shader graph
- **Audio:** FMOD, Unity AudioMixer, Godot AudioStreamPlayer
- **Tools:** Git LFS (assets), Perforce (studio), TextMeshPro, Cinemachine
- **Correctness surface:** frame-rate independence, deterministic physics for rollback netcode,
  memory allocation in hot paths (GC spikes), asset streaming, save data corruption

## Skill Overrides

```yaml
skill_overrides:
  prime-coder:
    frame_rate_independence:
      enforce: true
      note: >
        All movement, physics, timers, and animation that run in Update() / _process()
        must be multiplied by Time.deltaTime (Unity) or delta (Godot). Hard-coded frame
        counts for timing are forbidden.
      detector: "grep -n 'transform.Translate\\|position +=' -- check for * Time.deltaTime"
    memory_allocation:
      hot_path_alloc_forbidden: true
      note: >
        New allocations (new, LINQ on collections, string concatenation with +) in
        Update(), FixedUpdate(), _process(), or _physics_process() are forbidden.
        Use object pools, pre-allocated arrays, and StringBuilder.
      detector: "grep -n 'new \\|\.Select(\\|\.Where(' in Update/FixedUpdate methods"
    reproducibility:
      deterministic_physics_mode: optional
      note: >
        For games with rollback netcode, Physics.simulationMode must be Script,
        and all RNG must use a seeded deterministic RNG (not UnityEngine.Random without seed).
    localization:
      extra_signals:
        touches_game_loop: 7
        touches_physics_layer: 6
        touches_asset_streaming: 5
        touches_save_system: 8
        touches_input_handling: 5
        touches_shader_code: 4
  phuc-loop:
    playtesting_feedback_integration: true
    iteration_budget:
      max_iterations: 8
      checkpoint_every_n: 2
      note: >
        Game feel is iterative. phuc-loop supports up to 8 design iterations per session,
        with a mandatory playtest checkpoint every 2 iterations to gather feedback before
        continuing.
    convergence_criteria:
      fun_proxy_metric: "playtester_retention_at_5min"
      note: >
        Convergence is not just correctness — it includes fun. Define a measurable proxy
        (e.g., 80% of playtesters reach minute 5) and iterate toward it.
```

## Recipe Preferences

```yaml
recipe_preferences:
  - id: recipe.game-loop-design
    priority: HIGH
    name: "Core Game Loop Design"
    reason: >
      The game loop (input → update state → render → repeat) must be designed
      with frame-rate independence, bounded update time, and clear separation of
      physics, game logic, and rendering concerns.
    steps:
      1: "Define loop invariants: what state changes per frame? what is fixed-rate?"
      2: "Separate FixedUpdate (physics, 50Hz) from Update (input/animation) from LateUpdate (camera)"
      3: "Verify all movement uses delta time; write unit test asserting position after N seconds"
      4: "Profile with Unity Profiler or Godot Profiler: confirm < 2ms frame budget in hot path"
      5: "Add frame budget guard: if delta > 0.1s (spiral of death), clamp and log warning"
      6: "Document loop architecture in docs/game-loop.md"
    required_artifacts:
      - evidence/profiler_baseline.json (frame_time_ms_p95, gc_alloc_per_frame_bytes)
      - docs/game-loop.md

  - id: recipe.asset-pipeline
    priority: HIGH
    name: "Asset Import and Streaming Pipeline"
    reason: >
      Incorrectly configured asset import settings cause memory spikes, load time regressions,
      and platform submission failures. Asset pipeline must be defined and automated.
    steps:
      1: "Define asset categories: textures (resolution caps per platform), audio (compression format), meshes (LOD required?)"
      2: "Configure AssetImporter presets or Godot import settings per category"
      3: "Write import validation script: check all textures <= max resolution, audio <= bitrate cap"
      4: "Run validation on asset folder; fail if any asset violates constraints"
      5: "Set up Addressables (Unity) or resource packs (Godot) for runtime streaming"
      6: "Profile load time for critical scenes: must be < 3 seconds on target hardware"
    required_artifacts:
      - evidence/asset_validation_report.json (violations_found, violations_fixed)
      - evidence/load_time_profile.json (scene, load_time_ms, target_hardware)

  - id: recipe.playtesting-feedback
    priority: HIGH
    name: "Structured Playtesting Session"
    reason: >
      Game feel cannot be verified by code alone. Playtesting sessions must be
      structured to produce actionable, quantitative feedback (not just "it feels off").
    steps:
      1: "Define playtest goals: what game feel questions are you testing this session?"
      2: "Prepare observation template: note exact moment player hesitates, fails, gets confused"
      3: "Record session (with consent): screen capture + tester audio commentary"
      4: "During session: do not explain or help — observe and timestamp issues"
      5: "Post-session: collect ratings on 5-point scale for: responsiveness, difficulty curve, clarity"
      6: "Synthesize top 3 actionable changes; prioritize by frequency × severity"
      7: "Create phuc-loop iteration plan for next 2 design changes based on findings"
    required_artifacts:
      - evidence/playtesting_notes.json (tester_id, session_goals, issues_timestamped, ratings)
      - evidence/iteration_plan.json (changes_planned, priority, expected_effect)

  - id: recipe.save-system
    priority: HIGH
    name: "Save Data Safety"
    reason: >
      Save data corruption is the highest-severity player-facing bug in shipped games.
      Save writes must be atomic, versioned, and validated on load.
    steps:
      1: "Define save data schema as a versioned struct/class with schema_version field"
      2: "Implement atomic write: write to temp file, then rename (POSIX rename is atomic)"
      3: "Implement load with schema_version check: handle upgrade paths for old saves"
      4: "Add checksum (CRC32 or SHA256 first 8 bytes) to save file footer"
      5: "Write unit tests: corrupt save → graceful error + new game prompt (not crash)"
      6: "Write unit tests: old schema version → successful migration to current schema"
    required_artifacts:
      - evidence/save_system_tests.json (test_corrupt_save, test_schema_migration, all passing)
    forbidden_in_recipe:
      - overwrite_save_file_in_place_without_temp
      - save_without_schema_version
      - load_without_checksum_validation

  - id: recipe.performance-profiling
    priority: MED
    name: "Frame Budget Profiling"
    reason: >
      Performance regressions in games directly hurt player experience. Every feature
      that touches the hot path must be profiled before and after.
    steps:
      1: "Record baseline frame time with Unity Profiler or Godot profiler (1000 frames)"
      2: "Implement feature change"
      3: "Record post-change frame time (same scene, same hardware)"
      4: "Compare: if p95 frame time increases by > 0.5ms, flag as regression"
      5: "If regression: profile call stack to identify hot spot; optimize or defer"
      6: "Store before/after in evidence/profiler_comparison.json"
```

## Forbidden States (Domain-Specific)

```yaml
forbidden_states:
  - id: NO_FRAME_RATE_DEPENDENT_PHYSICS
    description: >
      Movement, forces, or timers computed without multiplying by deltaTime (Unity)
      or delta (Godot) will behave differently at different frame rates. This is
      a critical bug on platforms with variable refresh rates.
    detector: "grep -n 'transform.position +=' -- verify '* Time.deltaTime' present"
    recovery: "Multiply all per-frame deltas by Time.deltaTime or move to FixedUpdate."

  - id: NO_HOT_PATH_ALLOCATION
    description: >
      GC allocations in Update(), FixedUpdate(), _process(), or _physics_process()
      cause frame stutters due to garbage collection. New, LINQ, and string + are forbidden.
    detector: "Unity Profiler GC.Alloc marker in Update call stack; or Godot memory profiler."
    recovery: "Use ObjectPool<T>, pre-allocated List<T> with Clear(), and StringBuilder."

  - id: NO_HARDCODED_RESOLUTION_ASSUMPTION
    description: >
      UI and gameplay code that assumes a fixed screen resolution (1920x1080) will
      break on mobile, ultrawide, or console displays.
    detector: "grep -n '1920\\|1080\\|Screen.width\\|Screen.height' in UI/layout code without reference resolution"
    recovery: "Use Canvas Scaler (Unity) or Control anchors (Godot) for resolution-independent layout."

  - id: NO_SAVE_OVERWRITE_IN_PLACE
    description: >
      Writing directly to the save file path without atomic temp-file rename risks
      save corruption if the process is interrupted (power loss, OS kill).
    detector: "Review save write code: must write to .tmp file then File.Move / rename()"
    recovery: "Write to savefile.tmp; on success, File.Move(tmpPath, savePath) with overwrite=true."

  - id: NO_UNVERSIONED_SAVE_SCHEMA
    description: >
      Save data without a schema_version field cannot be safely migrated when
      the save format changes in future updates, corrupting player progress.
    detector: "Verify save data struct/class has schema_version: int field."
    recovery: "Add schema_version = CURRENT_VERSION to save data; implement LoadAndMigrate()."
```

## Verification Extensions

```yaml
verification_extensions:
  rung_641:
    required_checks:
      - unit_tests_green: "dotnet test (Unity) or pytest tests/ (Godot Python scripts) exits 0"
      - no_hot_path_alloc: "profiler GC.Alloc == 0 in Update call stack"
      - save_system_tests_green: "corrupt save and schema migration tests pass"
      - delta_time_audit: "grep scan: no frame-rate-dependent movement found"
  rung_274177:
    required_checks:
      - playtesting_session_complete: "evidence/playtesting_notes.json with >= 3 testers"
      - profiler_comparison: "p95 frame time delta <= 0.5ms from baseline"
      - asset_validation_clean: "evidence/asset_validation_report.json shows 0 violations"
      - load_time_within_budget: "evidence/load_time_profile.json p95 <= 3000ms"
  rung_65537:
    required_checks:
      - platform_target_build: "build succeeds on all target platforms"
      - controller_and_keyboard_tested: "both input methods verified in playtesting"
      - save_corruption_recovery_verified: "force-corrupt save; confirm new game prompt, no crash"
      - performance_on_min_spec: "frame time within budget on minimum specified hardware"
```

## Quick Start

```bash
# Load this ripple and start a game dev task
stillwater run --ripple ripples/game-dev.md --task "Implement object pool for projectile bullets in Unity"
```

## Example Use Cases

- Design a game loop with proper separation of physics, input, and rendering concerns:
  generates a frame budget analysis, enforces delta-time usage, profiles GC allocations,
  and produces a documented architecture in docs/game-loop.md.
- Build a safe save system with atomic writes, schema versioning, and checksum validation:
  generates unit tests for save corruption and schema migration scenarios before implementation.
- Run a structured playtesting session analysis: synthesizes tester feedback into a prioritized
  iteration plan, tracks fun proxy metrics across phuc-loop iterations, and converges toward
  a defined playtester-retention target.
