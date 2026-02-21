---
ripple_id: ripple.education
version: 1.0.0
base_skills: [phuc-forecast, prime-wishes]
persona: Curriculum designer / tutor (K-12 through university, online and in-person)
domain: education
author: contributor:open-curriculum-collective
swarm_agents: [scientist, ux, ethicist, skeptic, maintainer]
---

# Education Ripple

## Domain Context

This ripple configures phuc-forecast and prime-wishes for curriculum design, tutoring,
knowledge gap detection, and exercise generation across educational contexts:

- **Levels:** K-12, undergraduate, graduate, adult professional learning
- **Modalities:** in-person instruction, online async (LMS), live tutoring, self-paced
- **Subjects:** mathematics, computer science, sciences, humanities, professional skills
- **Tools:** LaTeX (exercises/exams), Markdown (course notes), Jupyter (STEM labs),
  Anki (flashcards), Canvas/Moodle (LMS), Socratic dialogue patterns
- **Correctness surface:** prerequisite ordering (Bloom's taxonomy), misconception detection,
  assessment validity, accessibility compliance, learner privacy (FERPA/COPPA)

## Skill Overrides

```yaml
skill_overrides:
  phuc-forecast:
    stakes_default: MED
    required_lenses: [scientist, ux, ethicist, skeptic]
    note: >
      Educational design must forecast: what misconceptions will students bring?
      What prerequisite gaps will block learning? What cognitive load does this
      activity impose? Premortem must address these before curriculum is finalized.
    premortem_required_before_curriculum_design: true
    hypothesis_formulation_required: true
  prime-wishes:
    wish_validation:
      require_bloom_level_declaration: true
      require_prerequisite_map: true
      require_accessibility_check: true
      note: >
        Every learning objective (wish) must declare: Bloom's taxonomy level
        (Remember/Understand/Apply/Analyze/Evaluate/Create), prerequisite concepts,
        and accessibility accommodations required.
    forbidden_wishes:
      - ambiguous_objective_without_measurable_outcome
      - objective_without_bloom_level
      - assessment_without_rubric
```

## Recipe Preferences

```yaml
recipe_preferences:
  - id: recipe.socratic-questioning
    priority: HIGH
    name: "Socratic Dialogue Pattern"
    reason: >
      Socratic questioning develops critical thinking by guiding learners to construct
      understanding rather than receive it passively. Questions must be calibrated to
      the learner's current knowledge level and guide without giving away answers.
    steps:
      1: "Assess learner's current understanding: ask an open diagnostic question first"
      2: "Identify the gap between current understanding and the target concept"
      3: "Formulate a question that exposes the contradiction or missing piece — do not explain yet"
      4: "If learner answers correctly: ask a probing deepening question (one level up Bloom's)"
      5: "If learner answers incorrectly: ask a simpler question that leads toward the error's source"
      6: "Never directly state the answer if the learner can be guided to it within 3 more exchanges"
      7: "When learner arrives at correct understanding: ask them to explain it in their own words"
      8: "Record: question_sequence, learner_response_summary, misconceptions_surfaced"
    required_artifacts:
      - evidence/socratic_session.json (topic, diagnostic_answer, misconceptions_found, exchanges_count)
    constraints:
      max_direct_statements_before_question: 2
      never_give_answer_if_within_3_exchanges: true

  - id: recipe.knowledge-gap-detection
    priority: HIGH
    name: "Prerequisite Gap Detection"
    reason: >
      Students who lack prerequisite knowledge cannot build on new concepts. A diagnostic
      must identify specific gaps before instruction begins, not after frustration sets in.
    steps:
      1: "List the prerequisite concepts for the target learning objective (dependency graph)"
      2: "Design 1-2 diagnostic questions per prerequisite concept (not the target concept)"
      3: "Administer diagnostics; classify each prerequisite as: SOLID / SHAKY / MISSING"
      4: "For each MISSING prerequisite: add it to the remediation queue before the main lesson"
      5: "For each SHAKY prerequisite: add a targeted 5-minute review to the lesson opening"
      6: "Adjust lesson pacing based on gap severity (more gaps = slower pace, more examples)"
      7: "Record gap_map.json: prerequisite, status, diagnostic_question_used, remediation_action"
    required_artifacts:
      - evidence/gap_map.json (prerequisite_concept, status, remediation_action)
      - evidence/diagnostic_questions.json (concept, question_text, correct_answer, misconception_addressed)

  - id: recipe.exercise-generation
    priority: HIGH
    name: "Exercise and Assessment Generation"
    reason: >
      Good exercises test exactly the intended Bloom's level, no more and no less.
      Each exercise must have a rubric, a worked solution, and 2-3 common wrong answers
      with explanations of the misconception each wrong answer reveals.
    steps:
      1: "Declare Bloom's level: Remember/Understand/Apply/Analyze/Evaluate/Create"
      2: "Write the exercise stem — test exactly the declared Bloom's level"
      3: "Write the model answer and full worked solution"
      4: "Write 2-3 plausible wrong answers (distractors); for each: name the misconception"
      5: "Write the rubric: what earns full credit, partial credit, no credit"
      6: "Check accessibility: is the language clear? Is any visual element described in alt text?"
      7: "Check prerequisite alignment: does solving this require any unlisted prerequisite?"
    required_artifacts:
      - evidence/exercises.json (bloom_level, stem, model_answer, distractors_with_misconceptions, rubric)

  - id: recipe.curriculum-sequencing
    priority: MED
    name: "Learning Objective Sequencing"
    reason: >
      Poorly ordered objectives create cognitive overload and unnecessary confusion.
      Curriculum must be sequenced by prerequisite dependency, with explicit ordering
      justified by the learning science of spaced repetition and interleaving.
    steps:
      1: "List all learning objectives for the unit/course"
      2: "Build prerequisite dependency graph: which objectives must precede which"
      3: "Topologically sort objectives; identify any circular dependencies (error — must resolve)"
      4: "Apply interleaving: distribute practice of older concepts throughout new content"
      5: "Apply spaced repetition: schedule review sessions at 1-day, 7-day, 30-day intervals"
      6: "Estimate time-on-task per objective (hours); sum to check against available course time"
      7: "Produce sequence_plan.json: ordered objectives, dependencies, time_estimate_hours, review_schedule"
    required_artifacts:
      - evidence/sequence_plan.json (objective_id, bloom_level, prerequisites, time_estimate_hours, review_schedule)

  - id: recipe.accessibility-audit
    priority: MED
    name: "Learning Material Accessibility Check"
    reason: >
      Educational materials must be accessible to all learners. WCAG 2.1 AA compliance
      is the minimum bar. FERPA and COPPA apply to learner data collection.
    steps:
      1: "Check all images have descriptive alt text (not just 'Figure 1')"
      2: "Check all videos have captions (auto-captions alone are insufficient — review accuracy)"
      3: "Check color contrast: text must meet WCAG 2.1 AA (4.5:1 normal text, 3:1 large text)"
      4: "Check reading level: use Flesch-Kincaid; flag sections above target grade level + 2"
      5: "Check any learner data collection for FERPA/COPPA compliance (parental consent for < 13)"
      6: "Produce accessibility_report.json: item, standard, pass_fail, remediation_note"
    required_artifacts:
      - evidence/accessibility_report.json (item, wcag_criterion, status, remediation)
```

## Forbidden States (Domain-Specific)

```yaml
forbidden_states:
  - id: NO_OBJECTIVE_WITHOUT_BLOOM_LEVEL
    description: >
      A learning objective that cannot be classified at a specific Bloom's taxonomy level
      is not a measurable objective. Vague objectives like "understand calculus" are forbidden.
    detector: "Check evidence/sequence_plan.json: every objective must have bloom_level field."
    recovery: "Rewrite objective with an action verb: 'Apply the chain rule to differentiate composite functions' (Apply level)."

  - id: NO_ASSESSMENT_WITHOUT_RUBRIC
    description: >
      Any graded assessment (quiz, project, essay) without an explicit rubric is unfair
      and cannot be applied consistently. Rubrics must be shared with learners before submission.
    detector: "Check evidence/exercises.json: every exercise must have rubric field populated."
    recovery: "Write rubric with at least 3 levels: full_credit, partial_credit, no_credit with criteria."

  - id: NO_ANSWER_GIVEN_PREMATURELY_IN_SOCRATIC
    description: >
      Giving the answer directly before the learner has had at least 2 guided attempts
      defeats the Socratic method and prevents deep learning.
    detector: "Check evidence/socratic_session.json: exchanges_count must be >= 2 before any direct_answer field."
    recovery: "Ask a simpler guiding question; record the exchange; continue guiding."

  - id: NO_LEARNER_PII_IN_EVIDENCE
    description: >
      Evidence artifacts must not contain learner names, student IDs, email addresses,
      or any personally identifiable information. FERPA requires protection of education records.
    detector: "Scan evidence/*.json for name, email, student_id, date_of_birth patterns."
    recovery: "Replace with anonymized identifiers: learner_001, learner_002. Store PII mapping separately under access control."

  - id: NO_CIRCULAR_PREREQUISITE_DEPENDENCY
    description: >
      A curriculum where Objective A requires B and B requires A is unimplementable.
      Circular dependencies in the prerequisite graph are a hard error, not a warning.
    detector: "Run topological sort on sequence_plan.json dependency graph; detect cycles."
    recovery: "Identify which dependency is spurious; remove or restructure the objective pair."
```

## Verification Extensions

```yaml
verification_extensions:
  rung_641:
    required_checks:
      - bloom_levels_declared: "all objectives in sequence_plan.json have bloom_level"
      - rubrics_present: "all exercises in exercises.json have rubric field"
      - prerequisites_mapped: "gap_map.json present with dependency graph"
      - no_learner_pii: "evidence/*.json passes PII scan"
  rung_274177:
    required_checks:
      - diagnostic_questions_validated: "each diagnostic question reviewed by subject-matter expert"
      - accessibility_audit_complete: "evidence/accessibility_report.json with 0 FAIL items"
      - time_estimates_realistic: "total time_estimate_hours in sequence_plan.json <= available course hours"
      - spaced_repetition_schedule_present: "review_schedule populated in sequence_plan.json"
  rung_65537:
    required_checks:
      - pilot_test_complete: "at least 3 learners completed pilot; evidence/pilot_feedback.json present"
      - misconception_coverage: "all distractors in exercises.json address documented misconceptions"
      - ferpa_coppa_compliance: "if learners under 18, parental consent mechanism documented"
      - learning_outcomes_measurable: "each objective can be assessed by the generated exercises"
```

## Quick Start

```bash
# Load this ripple and start a curriculum task
stillwater run --ripple ripples/education.md --task "Design a 3-lesson unit on recursion for CS undergraduates"
```

## Example Use Cases

- Run a Socratic tutoring session on a student struggling with integration by parts: diagnoses
  the prerequisite gap (product rule not solid), guides with calibrated questions, never gives
  the answer before 3 exchanges, and produces a socratic_session.json with all misconceptions
  surfaced and the exchange sequence recorded.
- Generate a problem set for an Apply-level Bloom's unit on probability: produces 10 exercises
  each with worked solutions, 3 distractors per exercise with named misconceptions, and a
  consistent rubric — then audits for reading level and accessibility compliance.
- Design a full curriculum sequence for an intro Python course: builds a prerequisite dependency
  graph across 24 learning objectives, topologically sorts them, applies interleaving and spaced
  repetition scheduling, and estimates total time-on-task against a 15-week semester constraint.
