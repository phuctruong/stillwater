---
ripple_id: ripple.ml-research
version: 1.0.0
base_skills: [prime-math, prime-coder, phuc-forecast]
persona: ML researcher (PyTorch/JAX, experiment tracking, paper writing, hypothesis testing)
domain: ml-research
author: contributor:ml-research-lab
swarm_agents: [scientist, skeptic, mathematician, adversary, reviewer, statistician]
---

# ML Research Ripple

## Domain Context

This ripple configures prime-math, prime-coder, and phuc-forecast for machine learning
research workflows:

- **Frameworks:** PyTorch 2.x, JAX + Flax/Optax, HuggingFace Transformers, Diffusers
- **Experiment tracking:** Weights & Biases, MLflow, TensorBoard
- **Distributed training:** PyTorch DDP, FSDP, DeepSpeed, JAX pmap/pjit
- **Evaluation:** lm-eval-harness, EleutherAI benchmarks, custom eval loops
- **Paper tools:** LaTeX, Overleaf, arXiv submission, matplotlib/seaborn for figures
- **Correctness surface:** gradient flow, loss curves, seed reproducibility,
  statistical significance, cherry-picking prevention, benchmark contamination

## Skill Overrides

```yaml
skill_overrides:
  prime-math:
    exact_arithmetic:
      enforce_in_verification_path: true
      note: >
        All reported metrics (accuracy, perplexity, BLEU, F1) must be stored as
        Decimal strings in evidence artifacts. Float comparisons for significance
        testing must use Decimal arithmetic with explicit precision.
      forbidden_in_verification:
        - float_comparison_for_metric_thresholds
        - numpy_allclose_as_final_assertion_for_published_results
        - rounded_float_in_experiment_log
    proof_obligations:
      require_convergence_certificate: true
      require_gradient_flow_check: true
      note: >
        Iterative training loops must emit a halting certificate (CONVERGED, TIMEOUT,
        or DIVERGED) with final loss as Decimal string.
  prime-coder:
    reproducibility:
      require_seed_in_all_random_calls: true
      seed_fields_required:
        - pytorch: "torch.manual_seed(SEED) + torch.cuda.manual_seed_all(SEED)"
        - numpy: "np.random.seed(SEED)"
        - python_random: "random.seed(SEED)"
        - jax: "jax.random.PRNGKey(SEED) — never reuse key"
        - dataloader: "DataLoader(..., generator=torch.Generator().manual_seed(SEED))"
      seed_sweep:
        min_seeds: 3
        required_for_rung_274177: true
    localization:
      extra_signals:
        touches_loss_function: 7
        touches_optimizer: 6
        touches_data_loader: 5
        touches_evaluation_loop: 6
        touches_model_architecture: 5
  phuc-forecast:
    premortem_required_before_experiment: true
    hypothesis_formulation_required: true
    note: >
      Before running any experiment, state the hypothesis (what you expect and why),
      list the top 5 failure modes (e.g., gradient explosion, data contamination,
      metric implementation bug), and define success/failure criteria as Decimal thresholds.
```

## Recipe Preferences

```yaml
recipe_preferences:
  - id: recipe.experiment-tracking
    priority: HIGH
    name: "Reproducible Experiment Run"
    reason: >
      Every experiment must be uniquely identified, seeded, and have all
      hyperparameters recorded before training starts. Results must be
      reproducible by a third party from the logged artifacts alone.
    steps:
      1: "Define hypothesis: what change, what metric, what threshold (Decimal)"
      2: "Create experiment config YAML with all hyperparameters + SEED"
      3: "Compute run_id = sha256(config_yaml)[:12]"
      4: "Initialize W&B or MLflow run with run_id and config"
      5: "Run training with all seeds set; log loss/metric as Decimal strings every N steps"
      6: "Emit halting certificate: CONVERGED/TIMEOUT/DIVERGED with final_loss_decimal"
      7: "Store config, metrics, and checkpoint hash in evidence/artifacts.json"
    required_artifacts:
      - evidence/convergence.json
      - evidence/artifacts.json (with checkpoint sha256)
      - evidence/env_snapshot.json (GPU model, CUDA version, framework version)

  - id: recipe.hypothesis-testing
    priority: HIGH
    name: "Statistical Hypothesis Testing"
    reason: >
      Claims of improvement over a baseline must be supported by statistical tests.
      Single-run comparisons are insufficient for publication-grade claims.
    steps:
      1: "Run baseline model with seeds [42, 137, 9999, 31337, 2718]"
      2: "Run experimental model with same 5 seeds"
      3: "Compute mean ± std for each metric as Decimal strings"
      4: "Run paired t-test or Wilcoxon signed-rank test (use scipy.stats)"
      5: "Record p-value as Decimal string; apply Bonferroni correction if multiple metrics"
      6: "Claim improvement only if p < Decimal('0.05') AND effect size > minimum_meaningful_delta"
      7: "Document in evidence/hypothesis_test.json"
    required_artifacts:
      - evidence/hypothesis_test.json (p_value_decimal, effect_size_decimal, test_name, n_seeds)
    forbidden_in_recipe:
      - single_seed_comparison_as_main_result
      - p_value_as_float_in_evidence
      - cherry_picked_seed_reporting

  - id: recipe.paper-writing
    priority: MED
    name: "Result Reproducibility Package"
    reason: >
      Published results must be reproducible by reviewers. The paper submission
      must include a reproducibility checklist and artifact package.
    steps:
      1: "Freeze model checkpoint; compute sha256 of checkpoint file"
      2: "Write reproduce.sh: install env, download checkpoint, run eval, compare to paper Table N"
      3: "Run reproduce.sh from clean environment; verify output matches within R_p tolerance"
      4: "Write reproducibility checklist (NeurIPS/ICML/ICLR standard)"
      5: "Generate figures from data (not from saved images); version figures in git"
      6: "Package: checkpoint hash, reproduce.sh, requirements.txt pinned, data hash"
    required_artifacts:
      - reproduce.sh (executable, documented)
      - evidence/reproducibility_checklist.json
      - evidence/figure_sources/ (data + plotting scripts, not PNGs alone)

  - id: recipe.ablation-study
    priority: MED
    name: "Systematic Ablation"
    reason: >
      Ablation studies must be designed before results are known to prevent
      post-hoc rationalization. Each ablation must use the same seed sweep.
    steps:
      1: "List all components to ablate BEFORE running any ablation experiments"
      2: "For each ablation: state hypothesis of what removing it will do"
      3: "Run each ablation with seeds [42, 137, 9999]"
      4: "Collect results in structured table (component, metric_mean_decimal, metric_std_decimal)"
      5: "Identify which components are load-bearing (removing degrades by > threshold)"
      6: "Store ablation table in evidence/ablation_results.json"

  - id: recipe.benchmark-eval
    priority: HIGH
    name: "Benchmark Evaluation with Contamination Check"
    reason: >
      Benchmark results are only valid if the benchmark data did not appear in training.
      Contamination check is mandatory before reporting benchmark numbers.
    steps:
      1: "Run n-gram overlap check between training data and benchmark test sets"
      2: "Flag any contaminated examples (overlap > threshold); report contamination_rate"
      3: "Run evaluation with lm-eval-harness or task-specific script (pinned version)"
      4: "Record benchmark name, version, evaluation script hash, and contamination_rate"
      5: "Store results as Decimal strings in evidence/benchmark_results.json"
    required_artifacts:
      - evidence/benchmark_results.json (benchmark, version, contamination_rate_decimal, scores_decimal)
      - evidence/eval_script_hash.txt
```

## Forbidden States (Domain-Specific)

```yaml
forbidden_states:
  - id: NO_SINGLE_SEED_CLAIM
    description: >
      Any performance claim (accuracy, loss, benchmark score) based on a single random
      seed is insufficient for publication or internal promotion. Minimum 3 seeds required
      for internal claims; 5 seeds for paper submission.
    detector: "Check evidence/artifacts.json for seed_sweep field; must list >= 3 seeds."
    recovery: "Re-run with seeds [42, 137, 9999]. Report mean ± std as Decimal strings."

  - id: NO_FLOAT_IN_METRIC_GATE
    description: >
      Comparison 'if accuracy > 0.95' using float is forbidden in any verification
      or promotion gate. Use Decimal('0.95') for exact comparison.
    detector: "grep -n 'if.*accuracy\\|if.*loss\\|if.*score\\|if.*perplexity' -- check for float"
    recovery: "from decimal import Decimal; threshold = Decimal('0.95'); assert metric_decimal >= threshold"

  - id: NO_UNREPORTED_HYPERPARAMETER
    description: >
      All hyperparameters that affect results (lr, batch_size, warmup_steps, architecture
      choices, data filtering thresholds) must be logged in evidence before training.
      Post-hoc hyperparameter disclosure is forbidden.
    detector: "Verify evidence/artifacts.json contains hyperparameter_snapshot before run_id is created."
    recovery: "Add all hyperparameters to config YAML; compute run_id from config hash."

  - id: NO_BENCHMARK_WITHOUT_CONTAMINATION_CHECK
    description: >
      Reporting a benchmark score without a documented contamination check is forbidden.
      This applies to all standard benchmarks (MMLU, HellaSwag, HumanEval, GSM8K, etc.).
    detector: "Check evidence/benchmark_results.json for contamination_rate_decimal field."
    recovery: "Run n-gram overlap script; document contamination_rate. If contaminated, report separately."

  - id: NO_GRADIENT_VANISHING_BLINDNESS
    description: >
      Training runs must log gradient norms periodically. A run where gradients vanished
      silently (norm < 1e-8 for > 100 steps) and was not flagged is a corrupt result.
    detector: "Check training logs for grad_norm entries; verify they are non-zero."
    recovery: "Add torch.nn.utils.clip_grad_norm_ with logging; check for NaN/zero grad norms."
```

## Verification Extensions

```yaml
verification_extensions:
  rung_641:
    required_checks:
      - unit_tests_green: "pytest tests/ exits 0 (model forward pass, loss computation, metric fn)"
      - seed_documented: "SEED in evidence/artifacts.json"
      - halting_certificate: "evidence/convergence.json present with lane and final_loss_decimal"
      - hypothesis_stated: "evidence/plan.json contains hypothesis field"
  rung_274177:
    required_checks:
      - seed_sweep_3: "Results from seeds [42, 137, 9999] in evidence/artifacts.json"
      - replay_stable: "Re-run with seed 42 produces identical loss trajectory (Decimal comparison)"
      - null_edge_sweep: "Test with empty batch, all-pad input, zero-length sequence"
      - gradient_flow_verified: "grad_norms logged; no vanishing or exploding reported"
  rung_65537:
    required_checks:
      - seed_sweep_5: "Results from 5 seeds; mean ± std reported"
      - statistical_test: "evidence/hypothesis_test.json with p_value_decimal < 0.05"
      - contamination_check: "evidence/benchmark_results.json with contamination_rate_decimal"
      - reproducibility_package: "reproduce.sh verified from clean environment"
      - ablation_complete: "evidence/ablation_results.json present"
```

## Quick Start

```bash
# Load this ripple and run an ML experiment task
stillwater run --ripple ripples/ml-research.md --task "Compare AdamW vs Lion optimizer on CIFAR-100"
```

## Example Use Cases

- Design a reproducible experiment comparing two training recipes: auto-generates config YAML,
  seeds all random calls, runs 3-seed sweep, emits convergence certificates, and produces
  a hypothesis_test.json with p-value and effect size as Decimal strings.
- Prepare a paper submission reproducibility package: freeze checkpoints with sha256 hashes,
  generate reproduce.sh, run contamination check against benchmark test sets, and produce
  a NeurIPS-style reproducibility checklist.
- Run a systematic ablation study with pre-registered hypotheses: forces hypothesis statement
  before any experiments run, collects results across seeds, and builds ablation_results.json
  to prevent post-hoc rationalization of which components matter.
