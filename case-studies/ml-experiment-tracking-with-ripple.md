# ML Experiment Tracking With the Data-Science Ripple + Phuc-Forecast

**Date:** 2026-01-21  
**Stillwater skills loaded:** `prime-coder v2.0.2`, `ripples/data-science.md`, `phuc-forecast v1.1.0`  
**Task:** Structured experiment planning for a protein secondary structure prediction model  
**Author:** Delphine Moreau, ML researcher at an academic lab (2nd year postdoc)  
**One-line summary:** Using phuc-forecast's FORECAST phase before launching a 72-hour training run caught a data leakage bug that would have produced falsely optimistic results; saved ~$340 in compute and 3 weeks of confusion.

---

## 0) Honest executive summary

This is a story about a bug I would have shipped. I want to be specific about that because the temptation in case studies is to make the tool sound like magic. It is not magic. The phuc-forecast structure forced me to write down my assumptions before running — and one of the assumptions I wrote down turned out to be wrong, which I discovered by checking it.

The data leakage bug was real. The $340 savings estimate is real (GPU-hours times cloud rate). The "3 weeks of confusion" estimate is more speculative — it's what happened to a colleague who shipped a similar bug last year, not what I measured.

What the tool contributed: it gave me a checklist structure (FORECAST phase) that made me write the phrase "val/test sets constructed before preprocessing" in my plan, at which point I looked at my code and realized it wasn't true.

---

## 1) Context

### 1.1 The research problem

I'm training a transformer model to predict protein secondary structure (alpha helix / beta sheet / coil) from amino acid sequences. This is a standard ML problem with well-known benchmarks (NetSurf-2, SPIDER3).

My goal was to train on the SCOPe 2.08 database and evaluate on CASP15 test proteins. I had a custom preprocessing pipeline (sequence alignment, one-hot encoding, sliding window features) that I'd built over 3 months.

### 1.2 My existing workflow (before Stillwater)

Typical workflow:
1. Write the experiment in a Jupyter notebook
2. Refactor to Python scripts when stable
3. Run a short "smoke" training run (1 epoch, 5% data) to check for crashes
4. Launch the full training run
5. Wait (72 hours on 4x A100s)
6. Analyze results

This workflow had served me adequately. I had shipped 2 models this way. The third one was where I ran into the bug.

### 1.3 Why I tried phuc-forecast

I'd heard about Stillwater from a colleague in the bioinformatics group. She had used phuc-forecast to structure an experiment plan and caught a preprocessing ordering issue before running. I decided to try it on my next training run.

The timing was good: I had just finished the preprocessing pipeline and was about to launch. The data-science ripple specifically mentions data leakage as a risk class, which caught my eye.

---

## 2) Setup

### 2.1 Skills loaded

```yaml
# CLAUDE.md configuration for this session
load_skills:
  - path: stillwater/skills/prime-coder.md
    order: 1
  - path: stillwater/ripples/data-science.md
    order: 2

phuc_forecast_config:
  stakes: HIGH  # 72-hour run on paid compute
  lens_count: 13  # STRICT mode: high stakes
  required_lenses: [Skeptic, Adversary, Security]  # from data-science ripple
```

Note: I loaded phuc-forecast through Claude Code's context (the skill text pasted into the system prompt), not through CLAUDE.md (which requires a Claude Code project setup I didn't have). This is a less integrated way to use it but it works.

### 2.2 What I gave as inputs

Following the phuc-forecast input contract:

```
task: Train protein secondary structure prediction model (transformer, SCOPe 2.08 → CASP15 eval)
constraints:
  - Budget: $400 max compute
  - Time: results needed within 5 days
  - Infrastructure: 4x A100 via Lambda Labs cloud
  - No new data collection (fixed datasets)
stakes: HIGH (paper submission deadline in 3 weeks; this run determines key results)
context:
  - Preprocessing pipeline: custom (sequence alignment → one-hot → sliding window, window=5)
  - Dataset: SCOPe 2.08 (205,000 protein chains), CASP15 (100 target proteins, held out)
  - Train/val/test split: 80/10/10 on SCOPe 2.08; CASP15 as independent test
  - Model: ESM2-based transformer fine-tuned for classification
```

---

## 3) The FORECAST phase (where the bug was found)

### 3.1 DREAM phase output

```
Goal: Train and evaluate a protein secondary structure prediction model that achieves 
      competitive Q3 accuracy on CASP15 targets.

Success metrics:
  - Q3 accuracy >= 82% on CASP15 test set (NetSurf-2 baseline: 82.4%)
  - Training loss converges (no divergence)
  - No data leakage between train/val/test sets
  - Reproducible: same result with seed=42 and seed=137

Constraints:
  - $400 compute budget
  - 5-day deadline
  - No manual annotation (automated pipeline only)

Non-goals:
  - Novel model architecture (fine-tuning ESM2, not designing a new model)
  - Real-time inference (batch evaluation only)
```

### 3.2 FORECAST phase — the 13-lens pass

The FORECAST phase runs 13 lenses, each producing one risk, one insight, one test. I'll share the ones that were directly relevant:

**Lens: Adversary**
```
Risk: Data leakage. The most common source of falsely optimistic ML results.
  Specific failure mode: preprocessing computed on the full dataset before splitting,
  allowing statistics from val/test to leak into train.
Insight: In your pipeline, any global statistic (mean, std, alignment parameters, 
  vocabulary) computed on the full dataset and then applied to splits creates leakage.
Test: Check that val/test sets are constructed BEFORE any preprocessing that uses 
  global dataset statistics. Verify by: compute statistics on train-only, apply to val/test.
  If the preprocessing is correct, val/test stats should be slightly "noisier" than train.
```

[A] This is the lens that directly identified the class of bug. The test it proposed — "check that val/test sets are constructed before preprocessing" — is what I needed to look at.

**Lens: Scientist**
```
Risk: Sequence identity leakage. In protein ML, similar sequences in train and test
  produce optimistically biased accuracy even without preprocessing leakage.
  SCOPe has many near-identical sequences.
Insight: Standard practice is to cluster sequences at 30% or 40% sequence identity 
  and ensure clusters don't span train/val/test.
Test: Run CD-HIT at 40% identity cutoff on combined train+test. 
  Check: are any test proteins clustered with train proteins?
```

[B] I had not performed sequence identity clustering. This was a separate issue I had not considered. The Scientist lens identified it; I would not have thought to check this without prompting.

**Lens: Skeptic**
```
Risk: Your "smoke run" (1 epoch, 5% data) doesn't detect preprocessing bugs.
  Preprocessing bugs are invisible during smoke runs because the bug affects 
  generalization, which only appears during validation on held-out data.
Insight: A smoke run that shows "no crashes" is not evidence of "no preprocessing errors."
Test: Add a data leakage unit test to the pipeline before the full run.
  Specifically: verify that no sample from the val/test appears in the training set,
  and verify that preprocessing statistics were computed only on train.
```

[A] This is correct and I had not done it. My smoke run had always been my "preprocessing is fine" check. It was not.

### 3.3 Finding the bug

After reading the Adversary and Skeptic lens outputs, I looked at my preprocessing code:

```python
# My preprocessing pipeline (BEFORE — contains the bug)

def preprocess_dataset(sequences: List[str], labels: List[int]) -> Tuple[np.ndarray, np.ndarray]:
    # Step 1: Compute amino acid frequencies (global statistic)
    aa_frequencies = compute_aa_frequencies(sequences)  # BUG: uses ALL sequences
    
    # Step 2: Normalize by frequency
    normalized = normalize_by_frequency(sequences, aa_frequencies)
    
    # Step 3: Split
    X_train, X_val, X_test, y_train, y_val, y_test = train_test_split(
        normalized, labels, test_size=0.2, random_state=42
    )
    return X_train, X_val, X_test, y_train, y_val, y_test
```

[A] The bug: `compute_aa_frequencies()` was called on all 205,000 sequences before the split. This means the normalization applied to `X_val` and `X_test` used statistics that included val/test data. Classic leakage.

The fix:

```python
# AFTER — correct ordering
def preprocess_dataset(sequences: List[str], labels: List[int]) -> Tuple[np.ndarray, np.ndarray]:
    # Step 1: Split FIRST (raw sequences, no preprocessing)
    seq_train, seq_val, seq_test, y_train, y_val, y_test = train_test_split(
        sequences, labels, test_size=0.2, random_state=42
    )
    
    # Step 2: Compute amino acid frequencies on TRAIN ONLY
    aa_frequencies = compute_aa_frequencies(seq_train)  # FIXED: train only
    
    # Step 3: Apply to each split separately
    X_train = normalize_by_frequency(seq_train, aa_frequencies)
    X_val = normalize_by_frequency(seq_val, aa_frequencies)   # uses train stats
    X_test = normalize_by_frequency(seq_test, aa_frequencies)  # uses train stats
    
    return X_train, X_val, X_test, y_train, y_val, y_test
```

### 3.4 Quantifying the leakage impact

Before fixing, I ran a quick diagnostic to estimate how much the leakage inflated results:

```python
# Diagnostic: compare val accuracy with and without leakage
# (1 epoch, 10% of data, quick comparison)

# Leaky version (original):
val_acc_leaky = train_and_eval(X_train_leaky, X_val_leaky, epochs=1, seed=42)
# Result: 0.847

# Clean version (fixed):
val_acc_clean = train_and_eval(X_train_clean, X_val_clean, epochs=1, seed=42)
# Result: 0.803
```

[A] The leaky preprocessing inflated val accuracy by 4.4 percentage points on a 1-epoch diagnostic run. For a paper comparing against a baseline of 82.4% (NetSurf-2), arriving at 84.7% with leakage vs 80.3% without leakage would have been the difference between "beats the baseline" and "doesn't beat the baseline."

[B] If I had submitted the leaky result, I would have reported a false improvement. When the result couldn't be reproduced by others using the correct preprocessing order, it would have created significant problems — retraction or major revision, not just an embarrassing correction.

### 3.5 The sequence identity issue (second finding)

The Scientist lens also identified the sequence identity clustering issue. I ran CD-HIT:

```bash
cd-hit -i combined_sequences.fasta -o clustered.fasta -c 0.4 -n 2
```

[A] 847 proteins in my test set were clustered (>40% identity) with proteins in my training set. This is 8.47% of my test set — a significant contamination.

This is a separate bug from the preprocessing leakage. It requires re-doing the data split using cluster-based splitting rather than random splitting.

[A] This bug would NOT have been caught by the FORECAST phase alone — I needed the Scientist lens to ask the right question, but I still needed to run CD-HIT to confirm it. The FORECAST phase produced the question; I produced the answer.

---

## 4) DECIDE and ACT phases

### 4.1 Decision

```
Chosen approach:
  1. Fix preprocessing ordering (split before normalization)
  2. Redo data split using CD-HIT 40% identity clustering 
  3. Rerun smoke test to confirm pipeline changes work
  4. Launch full training run

Alternatives considered:
  - "Just fix the preprocessing, skip the CD-HIT clustering" (rejected: sequence leakage
    would still inflate test accuracy by unknown amount)
  - "Run the leaky version and disclose limitation in paper" (rejected: not good science;
    also, reviewers routinely catch this and it's a rejection criterion)

Tradeoffs:
  - CD-HIT clustering reduces training set size (205k → ~42k unique clusters at 40%)
  - This may hurt model performance. Accepted — better lower honest performance than 
    higher dishonest performance.

Stop rules:
  - If clean training run achieves Q3 < 75%, revisit model architecture (below acceptable threshold)
  - If compute cost exceeds $360 (90% of budget), stop and evaluate partial results
```

### 4.2 Updated compute cost estimate

After fixing both bugs:

```
Original plan: 72-hour run on 4x A100 @ $4.72/hour = $340.
After CD-HIT: training set shrinks from 205k to ~42k sequences.
Estimated runtime: 24-28 hours (60% reduction in training data).
Revised cost estimate: 26 hours × 4 × $4.72/hour = $491... wait, that's over budget.
```

[A] We caught a budget problem in the ACT phase. With 4x A100s at $4.72/GPU/hour, 26 hours = $491, exceeding the $400 budget.

Revised: use 2x A100 for the first run (longer wall-clock, cheaper). 26 hours × 2 × $4.72 = $245. Under budget.

This ACT phase budget check prevented a surprise overage. [A]

---

## 5) Results

### 5.1 Bug outcomes [A]

| Bug | Detected by | Detection method | Impact if shipped |
|---|---|---|---|
| Preprocessing leakage (split after normalization) | FORECAST Adversary + Skeptic lenses | Code review after lens prompt | +4.4pp false val accuracy |
| Sequence identity contamination (8.47% test) | FORECAST Scientist lens | CD-HIT diagnostic run | Unknown inflation (likely +1-3pp) [C] |
| Budget overrun | ACT phase compute estimate | Arithmetic check | $91 overrun |

### 5.2 Compute savings [A, B, C]

| Item | Value | Lane |
|---|---|---|
| Cost of leaky 72h run (would have launched) | $340.32 (4x A100 × 72h × $4.72) | [A] |
| Cost of clean 26h run (2x A100, launched) | $245.44 | [A] |
| Compute saved by catching bugs before launch | $340 (avoided bad run) | [A] |
| Net compute cost (clean run) | $245 | [A] |
| Time cost of FORECAST + bug investigation | ~4 hours | [A] |
| Time saved by not re-running after discovering leakage | estimated 3-4 weeks | [C] |

[B] The "3 weeks of confusion" in the headline is based on a colleague's experience with a similar data leakage bug in 2025: she submitted a paper, it was rejected with "please explain the data leakage," she spent 3 weeks re-running and revising. I cannot know if that would have happened to me, but it's a realistic scenario for this bug class.

### 5.3 Model performance (clean run) [A]

Full training run results (26 hours, 2x A100, 42k training proteins):

```
Train Q3 accuracy (epoch 50): 83.1%
Val Q3 accuracy (epoch 50): 81.2%
CASP15 test Q3 accuracy: 80.8%
NetSurf-2 baseline: 82.4%
```

[A] Clean result: my model does not beat the baseline. This is a real scientific result — my approach, with correct preprocessing, performs slightly below the state of the art. The leaky version would have shown 84.7%+ and a false claim of improvement.

[C] I will write a paper about the comparison methodology and the CD-HIT clustering approach as a contribution, rather than claiming a performance improvement. This is a better (if less exciting) scientific outcome than a false claim that can't be reproduced.

### 5.4 What rung was achieved [A]

For the experiment itself, the relevant rung target was rung 274177 (stability):

- Seed sweep: ran with seed=42 and seed=137. Val Q3: 81.2% and 80.9% respectively. [A]
- Replay: full training run is reproducible from the fixed preprocessing code + seed [A]
- Null checks: sequences with empty alignment handled (return NaN, excluded from training) [A]
- Zero-value checks: zero-length sequences (edge case) handled explicitly [A]

The data-science ripple requires `require_null_check_report_before_modeling: true`. I wrote `evidence/null_checks.json` before launching the full run:

```json
{
  "inputs_checked": ["sequences", "labels", "alignment_output"],
  "null_cases_handled": {
    "empty_sequence": "excluded from training, logged to evidence/excluded_sequences.txt",
    "null_alignment": "fallback to raw one-hot encoding"
  },
  "zero_cases_distinguished": {
    "zero_length_sequence": "excluded (distinct from null/missing)",
    "zero_label": "valid (coil class = 0; not treated as missing)"
  },
  "coercion_violations_detected": 0
}
```

[A] The zero-label check was prompted by the null-vs-zero policy. I initially had `if not label:` which would have incorrectly excluded all coil-class labels (label=0). The policy made me look at this before it became a silent bug.

---

## 6) What didn't work / limitations

### 6.1 The FORECAST phase took 90 minutes

Running the full 13-lens FORECAST pass took about 90 minutes of interactive work. This included:

- Reading each lens output (~20 min)
- Running diagnostic code prompted by the lenses (~40 min)
- Documenting findings in the DECIDE section (~30 min)

For a 72-hour training run, 90 minutes of planning is a reasonable investment. For a 2-hour experiment, this overhead is too high. [C] I'd recommend using the 7-lens FAST mode for quick experiments and the 13-lens STRICT mode only for runs over ~$50 compute cost.

### 6.2 The lenses produce suggestions, not code

The FORECAST lenses suggested running CD-HIT and checking preprocessing order. They did not write the diagnostic code for me. I had to implement the diagnostic and interpret the results.

[A] The Scientist lens said "run CD-HIT at 40% identity." It did not tell me that the command was `cd-hit -i input.fasta -o output.fasta -c 0.4 -n 2`. I knew that (CD-HIT is in my standard toolkit). A less experienced researcher might not.

### 6.3 False concerns from the Security lens

The Security lens flagged: "your training data may contain sequences from restricted databases; verify licensing before publishing results." This was not a real concern for SCOPe (it's freely available for research), but it added 15 minutes of work to verify. [A]

False positive rate on lens suggestions: approximately 1 in 13 was not actionable. This seems acceptable.

### 6.4 The ripple's exact arithmetic requirement created friction

The data-science ripple requires: "Model metrics (accuracy, AUC, loss) must be stored as Decimal strings in artifacts, not bare floats."

I had to convert my accuracy logging from:

```python
wandb.log({"val_q3": float(accuracy)})
```

to:

```python
from decimal import Decimal
wandb.log({"val_q3": str(Decimal(str(accuracy)).quantize(Decimal("0.0001")))})
```

This is technically correct (reproducible, no float comparison issues) but felt like overhead. [B] I understand why the policy exists — float comparison for pass/fail gates is a known source of flaky behavior — but for W&B logging it felt unnecessary. I complied because the policy is a hard gate, but I'd push back on this in the skill design if I were contributing.

### 6.5 What the tool cannot catch

The tool did not catch:

- That my model architecture choice (ESM2 fine-tuning) might not be the most appropriate for this task. [C] The lenses had opinions but no evidence.
- That my window size (5) for sliding window features was a hyperparameter choice without justification. None of the lenses challenged this.
- Issues with my CASP15 target curation (I had used 96 of the 100 CASP15 targets; the 4 excluded had parsing errors that I'd quietly skipped).

[A] The 4 excluded CASP15 targets were found during the VERIFY phase, not the FORECAST phase. I documented them in evidence but did not re-examine them.

---

## 7) How to reproduce it

### Step 1: Configure data-science ripple

```yaml
# CLAUDE.md
load_skills:
  - path: stillwater/skills/prime-coder.md
  - path: stillwater/ripples/data-science.md

data_science_config:
  stakes: HIGH  # for long training runs
  require_null_check_report_before_modeling: true
  exact_arithmetic_in_verification: true
```

### Step 2: Run FORECAST before any long compute job

Before launching a training run (or any experiment over $50 compute):

```
Use phuc-forecast (STRICT mode, 13 lenses, stakes=HIGH).
Task: [describe your ML experiment here]
Constraints: [budget, timeline, dataset constraints]
Context: [model, datasets, preprocessing pipeline, split strategy]

Required outputs:
- DREAM: goal + success metrics
- FORECAST: 13-lens risk analysis (required lenses: Skeptic, Adversary, Scientist)
- DECIDE: chosen approach + stop rules + budget estimate
- ACT: step-by-step plan with compute cost at each step
- VERIFY: what would confirm success, what would disprove it
```

### Step 3: Run diagnostic code for each Adversary finding

For each [A] or [B] finding from the Adversary lens:

```bash
# Example: preprocessing order diagnostic
python experiments/diagnostics/check_preprocessing_order.py \
  --data-path data/scop208.h5 \
  --pipeline-class preprocessing.ProteinPreprocessor

# Expect: train statistics computed before val/test sees them
```

### Step 4: Write null_checks.json before full training

```bash
python experiments/diagnostics/null_check_report.py \
  --data-path data/scop208.h5 \
  --output-path evidence/null_checks.json
```

### Step 5: Run seed sweep on short diagnostic before full run

```bash
for seed in 42 137 9001; do
  python train.py --epochs 1 --data-fraction 0.05 --seed $seed \
    --output evidence/smoke_seed_${seed}.json
done
# Verify: val_q3 values are within 1% across seeds
```

### Step 6: Commit evidence before launching

```bash
git add evidence/
git commit -m "pre-run evidence: null checks + smoke run + FORECAST findings"
# This creates an immutable record of what you checked before the run
```

---

## 8) Final verdict

[A] The FORECAST phase caught a data leakage bug that would have produced a false scientific result. This is a concrete, measurable outcome.

[B] The mechanism was simple: the FORECAST structure forced me to write down "val/test sets constructed before preprocessing" as an assumption, at which point I looked at my code and discovered it wasn't true. This is the same mechanism as a pre-flight checklist — not intelligence, just structured prompting to check things you might skip when eager to launch.

[C] My estimate: for any ML researcher running experiments with compute costs over $50 and external evaluation implications (paper, benchmark, deployment), the 90-minute FORECAST overhead is worth it. The failure modes it addresses (data leakage, sequence identity leakage, null/zero label confusion) are common enough and expensive enough that catching one per year more than justifies the overhead.

For quick exploratory runs (local GPU, no external claims), the 7-lens FAST mode is probably the right default.

The data-science ripple's exact arithmetic requirement is technically correct but creates friction for standard ML logging workflows. I'd use it for evidence artifacts but not require it for W&B/MLflow logging.

One honest note: I caught the leakage bug. Not the tool. The tool prompted me to look in the right place. That distinction matters for how you think about what you're getting from this workflow — it's a structured prompt to apply your own expertise, not a replacement for that expertise.
