---
ripple_id: ripple.data-science
version: 1.0.0
base_skills: [prime-safety, prime-coder]
persona: Data scientist / ML engineer (Python, pandas, numpy, scikit-learn, PyTorch)
domain: data-science
---

# Data Science Ripple

## Domain Context

This ripple configures the prime-coder and prime-safety skills for data science and machine
learning work using the Python scientific stack:

- **Data manipulation:** pandas, numpy, polars
- **Machine learning:** scikit-learn, XGBoost, LightGBM
- **Deep learning:** PyTorch, torchvision, transformers (HuggingFace)
- **Experiment tracking:** MLflow, Weights & Biases
- **Notebooks:** Jupyter, nbconvert
- **Correctness surface:** floating-point arithmetic, null/NaN handling, random seed reproducibility,
  data leakage, distribution shift

## Skill Overrides

```yaml
skill_overrides:
  prime-coder:
    exact_arithmetic:
      enforce_in_verification_path: true
      note: >
        Model metrics (accuracy, AUC, loss) must be stored as Decimal strings in artifacts,
        not bare floats. Comparisons for pass/fail thresholds must use Decimal arithmetic.
      forbidden_in_verification:
        - float_comparison_with_epsilon_hack
        - numpy_allclose_as_sole_assertion
        - rounded_float_in_evidence_hash
    reproducibility:
      require_seed_in_all_random_calls: true
      seed_fields_required:
        - numpy: "np.random.seed(SEED) or np.random.default_rng(SEED)"
        - pytorch: "torch.manual_seed(SEED)"
        - python_random: "random.seed(SEED)"
        - sklearn: "random_state=SEED on all estimators"
      seed_sweep:
        min_seeds: 3
        required_for_rung_274177: true
    localization:
      extra_signals:
        touches_data_loading: 5
        touches_feature_engineering: 4
        touches_model_training: 5
        touches_evaluation_metrics: 6
  prime-safety:
    rung_default: 274177
    null_zero_policy: STRICT
    require_null_check_report_before_modeling: true
```

## Recipe Preferences

```yaml
recipe_preferences:
  - id: recipe.null-zero-audit
    priority: HIGH
    reason: >
      Data pipelines are the primary source of null/NaN/0 confusion bugs. A null-check
      report must be generated and reviewed before any modeling step.
    trigger_on:
      - any DataFrame construction or loading
      - any feature engineering step
      - any join/merge operation
    required_output: "null_check_report.json with column-level null counts and dtype verification"

  - id: recipe.portability-audit
    priority: MED
    reason: "Notebooks must be reproducible across Python versions and OS environments."
    trigger_on:
      - any .ipynb file changed
      - requirements.txt or pyproject.toml changed
```

## Forbidden States (Domain-Specific)

```yaml
forbidden_states:
  - id: NO_FLOAT_IN_THRESHOLD_COMPARISON
    description: >
      Never use bare float comparison (e.g., accuracy > 0.95) in pass/fail gates.
      Use Decimal('0.95') for exact comparison in verification paths.
    detector: "grep -n 'if.*accuracy\\|if.*auc\\|if.*loss\\|if.*score' in evaluation code"
    recovery: "Import Decimal; cast metric to Decimal string before comparison."

  - id: NO_DATA_LEAKAGE
    description: >
      Train/test split must happen before any feature computation that uses aggregate
      statistics (mean, std, min, max). Fitting a scaler on the full dataset is leakage.
    detector: "Review pipeline order: fit_transform must only see train split."
    recovery: "Use sklearn Pipeline to ensure transforms are fit only on train data."

  - id: NO_UNSEEDED_RANDOM
    description: >
      Any call to np.random, random, torch, or sklearn estimators without an explicit
      seed produces non-reproducible results.
    detector: "grep -n 'np.random\\|random.\\|torch.rand\\|RandomForest\\|train_test_split' -- check for seed/random_state"
    recovery: "Add seed/random_state parameter. Document SEED value in experiment config."

  - id: NO_MODELING_WITHOUT_NULL_CHECK_REPORT
    description: >
      A null-check report (column-level null counts, dtypes, zero-vs-null distinction)
      must be generated and stored in evidence before any .fit() call.
    detector: "Verify null_check_report.json exists in EVIDENCE_ROOT before model training step."
    recovery: "Run df.isnull().sum() + dtype audit; write results to null_check_report.json."

  - id: NO_UNLABELED_EXPERIMENT
    description: >
      Every experiment run must have a unique run_id, seed, and hyperparameter snapshot.
      Anonymous runs cannot be reproduced or compared.
    detector: "Check for run_id in artifacts.json."
    recovery: "Use MLflow run or manual run_id = hashlib.sha256(config_json).hexdigest()[:8]."
```

## Verification Extensions

```yaml
verification_extensions:
  pre_modeling_gate:
    description: "Hard gate: null-check report must exist before any model fitting."
    required_artifacts:
      - null_check_report.json:
          required_keys:
            - dataset_shape
            - null_counts_per_column
            - zero_counts_per_column
            - dtype_per_column
            - null_zero_distinctions_flagged
  rung_641:
    required_checks:
      - unit_tests_green: "pytest tests/ exits 0"
      - null_check_report_exists: "EVIDENCE_ROOT/null_check_report.json present"
      - seed_documented: "SEED value in artifacts.json"
  rung_274177:
    required_checks:
      - seed_sweep_3_seeds: "Run experiment with seeds [42, 137, 9999]; metrics within tolerance"
      - replay_stability: "Re-run with same seed produces identical metric Decimal strings"
      - no_data_leakage_audit: "Pipeline order reviewed; documented in evidence"
  rung_65537:
    required_checks:
      - adversarial_input_sweep: "Test with all-null columns, zero-variance features, empty DataFrame"
      - distribution_shift_test: "Evaluate on held-out temporal or geographic split"
      - model_card_present: "docs/model-card.md with intended use, limitations, and bias audit"
```
