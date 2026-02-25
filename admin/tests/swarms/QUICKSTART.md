# ABCD Testing Quick Start

## What is ABCD Testing?

The ABCD framework tests code generation quality across three models:
- **A**: Baseline (no skills)
- **B**: haiku (skills loaded)
- **C**: sonnet (skills loaded)
- **D**: opus (skills loaded)

This tests the "uplift" effect of skill loading on code quality.

---

## Quick Start

### 1. Run Tests
```bash
cd /home/phuc/projects/stillwater

# Make sure LLM portal is running first
bash admin/start-llm-portal.sh

# Run all ABCD tests
pytest admin/tests/swarms/test_abcd_coding.py -v -s

# Run specific test
pytest admin/tests/swarms/test_abcd_coding.py::TestABCDCoding::test_coding_task -k "task_1" -v

# Run summary report
pytest admin/tests/swarms/test_abcd_coding.py::TestABCDSummary -v -s
```

### 2. Generate Uplift Report
```bash
python3 admin/tests/swarms/generate_uplift_report.py
```

Output files:
- `admin/tests/swarms/UPLIFT_REPORT.md` - Human-readable report
- `admin/tests/swarms/results/BENCHMARK_METRICS.json` - Machine-readable metrics

### 3. Check Results
```bash
# View individual test results
cat admin/tests/swarms/results/sonnet/task_1_simple_sum_sonnet.json | jq .

# View all metrics
cat admin/tests/swarms/results/BENCHMARK_METRICS.json | jq .
```

---

## Understanding Results

### Per-Test Metrics (in JSON files)

```json
{
  "model": "sonnet",
  "task_name": "task_1_simple_sum",
  "syntax_valid": true,
  "functional_pass": true,
  "quality_score": 0.6,
  "system_prompt_detected": true,
  "benchmark_metrics": {
    "evidence_completeness": 7.0,      // 0-10 scale (higher is better)
    "hallucination_rate": 0.1,         // 0-1 scale (lower is better)
    "rung_achieved": 641,              // 0|641|274177|65537
    "token_efficiency": 1.16           // 1.0 = baseline cost
  }
}
```

### Benchmark Metrics Explained

| Metric | Scale | Meaning | Target |
|--------|-------|---------|--------|
| **Evidence Completeness** | 0-10 | Quality of code structure, tests, docs | 7-10 |
| **Hallucination Rate** | 0-1 | Fraction of claims without witness | <0.3 |
| **Rung Achieved** | 0\|641\|274177\|65537 | Verification level | 641+ |
| **Token Efficiency** | 1.0-2.0x | Cost overhead vs baseline | 1.10-1.20x |

### Model Comparison

From this session's uplift report:

```
SONNET (Best)
  Evidence: 4.75/10  ✓ Highest
  Hallucination: 0.30  ✓ Lowest
  Rung: 320 avg (50% at 641)  ✓ Best
  Uplift: 961  ✓ Highest

HAIKU (Good)
  Evidence: 3.38/10
  Hallucination: 0.50
  Rung: 320 avg
  Uplift: 577

OPUS (Lower)
  Evidence: 3.00/10
  Hallucination: 0.50
  Rung: 160 avg
  Uplift: 288
```

---

## What Changed (This Session)

### 1. Context Detection Fixed
**Before**: Looked for "## SKILL:" in the LLM response (wrong location)
**After**: Checks the actual system_prompt sent to the LLM (correct)

### 2. Benchmark Metrics Added
Now calculates Hallucination Rate, Evidence Completeness, Rung, and Token Efficiency per test.

### 3. Donald Knuth Persona Added
`personas/language-creators/donald-knuth.md` - Emphasizes algorithmic rigor, proofs, and documentation.

---

## Files You Should Know About

**Test Code**
- `admin/tests/swarms/test_abcd_coding.py` - Main test framework

**Results**
- `admin/tests/swarms/results/` - Test results (JSON per task per model)
- `admin/tests/swarms/UPLIFT_REPORT.md` - Generated uplift report
- `admin/tests/swarms/results/BENCHMARK_METRICS.json` - Aggregated metrics

**Reference**
- `benchmarks/ai-uplift-benchmark.md` - Benchmark spec and baseline
- `personas/language-creators/donald-knuth.md` - Skills persona

**Utilities**
- `admin/tests/swarms/generate_uplift_report.py` - Report generator
- `admin/tests/swarms/reprocess_results.py` - Recalculate metrics for existing results

---

## Interpreting the Uplift Report

### Key Sections

**DETAILED METRICS BY MODEL**
- Shows per-model averages
- Look for: highest Evidence, lowest Hallucination, highest Rung

**COMPARATIVE ANALYSIS**
- Shows which model is best at each metric
- Usually one model (e.g., Sonnet) wins multiple categories

**COMPARISON TO BENCHMARK**
- Compares against baseline from `ai-uplift-benchmark.md`
- Shows uplift as percentage delta
- +55% Evidence improvement = skills are working!
- -17% Hallucination = skills reduce false claims!

---

## Troubleshooting

### LLM Portal Not Responding
```bash
# Check if running
curl http://localhost:8080/health

# Start it
bash admin/start-llm-portal.sh

# Check logs
tail -f admin/logs/llm_portal.log
```

### Tests Fail to Import
```bash
# Ensure PYTHONPATH includes src/cli/src
export PYTHONPATH=/home/phuc/projects/stillwater/src/cli/src:$PYTHONPATH

# Try again
pytest admin/tests/swarms/test_abcd_coding.py -v
```

### Results Not Saving
```bash
# Check permissions
ls -la admin/tests/swarms/results/

# Ensure directory exists
mkdir -p admin/tests/swarms/results/{haiku,sonnet,opus}
```

---

## Success Criteria

After running tests, you should see:

✅ 12 JSON files created (4 tasks × 3 models)
✅ Each file has `benchmark_metrics` section
✅ UPLIFT_REPORT.md shows comparison
✅ Sonnet outperforms other models in most metrics
✅ Evidence Completeness >3.0 average
✅ Hallucination Rate <0.5 average

If these are met: **Tests are working correctly!**

---

## Next Steps

1. **Run tests** to generate fresh results with corrected detection logic
2. **Review UPLIFT_REPORT.md** for model comparison
3. **Check benchmark_metrics** in individual results for deep dive
4. **Compare** to baseline in `benchmarks/ai-uplift-benchmark.md`

---

## Questions?

See related docs:
- `FIXES_AND_RESULTS.md` - Detailed technical changes
- `benchmarks/ai-uplift-benchmark.md` - Benchmark methodology
- `ABCD_TESTING.md` - Original framework documentation
