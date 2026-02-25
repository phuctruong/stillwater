# ABCD Test Report

**Generated**: 2026-02-24T20:42:42.116110Z

## Summary

| Variant | Name | Success Rate | Mean Quality | Mean Latency (ms) | Total Cost ($) |
|---------|------|-------------|-------------|-------------------|----------------|
| A | version-command | 100.0% | 1.0000 | 61.5 | 0.000000 |
| B | doctor-command | 100.0% | 0.0000 | 61.1 | 0.000000 |
| C | llm-status-command | 100.0% | 1.0000 | 1791.5 | 0.000000 |

**Winner**: `A` (version-command)

## Pairwise Significance (Bonferroni-corrected)

| Pair | n | Mean Diff | t-stat | Raw p | Adj p | Significant |
|------|---|-----------|--------|-------|-------|-------------|
| A_vs_B | 3 | 1.0000 | 0.000 | 1.0000 | 1.0000 | no |
| A_vs_C | 3 | 0.0000 | 0.000 | 1.0000 | 1.0000 | no |
| B_vs_C | 3 | -1.0000 | 0.000 | 1.0000 | 1.0000 | no |
