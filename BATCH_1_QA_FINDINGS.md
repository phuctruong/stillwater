# BATCH 1 HARSH QA FINDINGS

**Date:** 2026-02-17
**Target:** 5/5 (100% success on astropy instances)
**Achieved:** 0/5 (0%)
**Auth:** 65537

---

## Executive Summary

Batch 1 execution was BLOCKED due to **Solver phase diff generation failures**. While phases 1-3 (DREAM/FORECAST/DECIDE) work reliably, Phase 4 (ACT - Solver diff generation) consistently produces malformed diffs that fail patch application.

### Root Cause

The **unified diff format is fundamentally incompatible** with how the LLM generates indented Python code:

```
Unified diff requires:    --- LLM generates:
SPACE+code                 code (forgets prefix)
-code (removed)            -code (may lose indent)
+code (added)              +code (may lose indent)
```

When the LLM processes indented Python code (which is common in all 5 astropy instances), it struggles to maintain the proper prefix + indentation combination.

---

## Detailed Findings

### Phase 1: DREAM (Scout) ✅ **WORKING RELIABLY**

**Status:** 5/5 instances passed Scout analysis

Success indicators:
- All instances generated valid SCOUT_REPORT.json
- Correctly identified failing tests
- Correctly identified suspect files
- JSON schema validation passed

**Confidence:** HIGH - No changes needed

---

### Phase 2: FORECAST (Grace) ✅ **WORKING RELIABLY**

**Status:** 5/5 instances passed Grace analysis

Success indicators:
- All instances generated valid FORECAST_MEMO.json
- Identified 5+ failure modes per instance
- Ranked risks appropriately (HIGH/MED/LOW)
- Anti-rot context isolation confirmed (fresh context input)

**Confidence:** HIGH - No changes needed

---

### Phase 3: DECIDE (Judge) ✅ **WORKING RELIABLY**

**Status:** 4-5/5 instances passed Judge decision locking

Success indicators:
- Valid DECISION_RECORD.json generated
- Approach clearly stated
- Scope locked (exact files identified)
- Stop rules defined

**Occasional failures:** Instances 1 & 4 occasionally failed, likely due to complex problem statements requiring clearer prompting. Can be fixed with minor prompt refinement.

**Confidence:** HIGH - Minor improvements possible

---

### Phase 4: ACT (Solver) ❌ **CRITICALLY FAILING**

**Status:** 0/5 instances produced valid, applicable diffs

#### Failure Mode 1: Diff Format Not Generated (Instances 1, 5, 6)

```
Expected: Response containing "--- a/" and "+++"
Actual: Descriptive text explaining the approach, no diff
```

**Root cause:** LLM response to the prompt was explanatory rather than directive. The prompt was too open-ended.

**Instances affected:** astropy__astropy-12907, astropy__astropy-6938

#### Failure Mode 2: Malformed Diff - Missing Line Prefixes (Instances 2, 3, 4)

```
Generated diff:
@@ -40,6 +40,6 @@
 def function():
-    old_line
+    new_line
     context_line   ❌ BUG: Should be " context_line" (space prefix)
              more_indent   ❌ BUG: Should be " more_indent"
```

**Error from patch command:**
```
patch: **** malformed patch at line 45: [context line]
patch: **** malformed patch at line 32: +        [whitespace]
```

**Root cause:** When source code is indented (Python), the diff format requires:
- FIRST character = prefix (space, minus, plus)
- FOLLOWING characters = actual indentation + code

The LLM generates:
- FIRST characters = indentation from source
- Missing the prefix character entirely

**Instances affected:** astropy__astropy-14182, astropy__astropy-14365, astropy__astropy-14995

#### Failure Mode 3: Placeholder Line Numbers (Instance 5)

```
Generated hunk header: @@ -XX,7 +XX,7 @@  ❌ Placeholder!
Expected: @@ -40,7 +40,7 @@  ✅ Real line number
```

**Root cause:** LLM uses "XX" as a placeholder instead of counting source lines

**Solution:** Provide explicit line numbers in numbered source code view. PARTIALLY attempted but not fully resolved.

---

## Why Phases 1-3 Work but Phase 4 Fails

### Phases 1-3: JSON Output Format

Advantages:
- JSON has clear structure (keys, values)
- LLM can generate structured data easily
- Validation schema enforces correctness

### Phase 4: Unified Diff Format

Disadvantages:
- Diff format is **character-position dependent** (first character matters)
- **Indentation sensitive** (mixing content with structure)
- **Stateful format** (context lines, hunk headers, counts all interdependent)
- **Whitespace significant** (can't trim or reformat without breaking)

The unified diff format is fundamentally hostile to LLM generation because:
1. It embeds structural information (prefixes) in character position 1
2. It mixes indentation (content) with prefixes (structure)
3. It requires careful accounting of line counts

---

## Solutions Tested

### Attempt 1: Verbose System Prompt (~100 lines)
❌ **Failed** - LLM confused, didn't generate diffs at all

### Attempt 2: Enhanced Examples
❌ **Failed** - LLM generated diffs with placeholder line numbers (@@ -XX,...)

### Attempt 3: Minimal System Prompt
⚠️ **Partial** - Some instances generated diffs but still malformed

### Attempt 4: Ultra-Minimal + Example Diff
⚠️ **Partial** - diffs generated but context lines missing prefixes

---

## Recommended Solutions (Priority Order)

### OPTION 1: Post-Process LLM Diff Output ⭐ RECOMMENDED

**Approach:**
1. Extract whatever diff the LLM generates (partial/malformed is OK)
2. Parse it to identify: file, line ranges, removed lines, added lines
3. Re-generate correct unified diff from the parsed components
4. Apply corrected diff

**Pros:**
- Fixes all prefix/indentation issues automatically
- Works with partially correct LLM output
- No need to retrain LLM behavior
- Can handle edge cases

**Cons:**
- Adds complexity
- Requires robust parsing

**Estimated effort:** 2-3 hours implementation + testing

---

### OPTION 2: Ask LLM for JSON Diff Instead

**Approach:**
```json
{
  "changes": [
    {
      "file": "tokenizer.py",
      "line": 42,
      "old_code": "if x > 0:",
      "new_code": "if x >= 0:",
      "type": "modify"
    }
  ]
}
```

**Pros:**
- LLM naturally generates structured data
- Easy to parse and validate
- Can automatically generate unified diff from JSON

**Cons:**
- Major architecture change
- Need to update all phases to use new format

**Estimated effort:** 4-5 hours refactor

---

### OPTION 3: Use Specialized Diff Model

**Approach:**
- Use different model/API specialized for diff generation
- Or use traditional tools (git, diffstat) if available

**Pros:**
- Might work better with proper formatting

**Cons:**
- Dependency on external model
- Breaks homogeneity of system

---

## Immediate Action Items

### BLOCKER: Phase 4 Fails on All Instances

**Fix:** Implement Option 1 (Post-Process LLM Diff Output)

Steps:
1. Keep Solver generating diffs as-is (even if malformed)
2. Add diff parser that extracts: file path, hunk locations, +/- lines
3. Re-render diff using correct format
4. Test on all 5 instances

**Timeline:** Start immediately
**Effort:** ~3 hours
**Expected outcome:** 5/5 passing

### SECONDARY: Improve Phase 3 (Judge) Occasionally Fails

**Fix:** Refine Judge prompt for clarity

Steps:
1. Add explicit examples of DECISION_RECORD format
2. Simplify chosen_approach requirement
3. Test on instances 1 & 4

**Timeline:** After Phase 4 fix
**Effort:** ~1 hour

---

## Evidence Artifacts

### Successful Phases: Evidence Files

```
✅ DREAM Phase:
   - All instances generated valid SCOUT_REPORT.json
   - Evidence: /tmp/batch_1_phuc/astropy__*/scout_report.json

✅ FORECAST Phase:
   - All instances generated valid FORECAST_MEMO.json
   - Evidence: /tmp/batch_1_phuc/astropy__*/grace_memo.json

✅ DECIDE Phase:
   - 4-5/5 instances generated DECISION_RECORD.json
   - Evidence: /tmp/batch_1_phuc/astropy__*/decision.json
```

### Failing Phase: Error Evidence

```
❌ ACT Phase:
   - 0/5 instances produced applicable diffs
   - Errors:
     * 2/5: Diffs generated but malformed (missing prefixes)
     * 2/5: No diffs generated (explanatory text instead)
     * 1/5: Placeholder line numbers (@@-XX,...)
   - Evidence: /tmp/batch_1_phuc_orchestration.log (lines with "malformed patch")
```

---

## Verification Checklist for Fix

When OPTION 1 (Post-Process) is implemented, verify:

- [ ] ALL 5 instances proceed through Phase 5 (VERIFY)
- [ ] RED gate passes (test fails without patch)
- [ ] GREEN gate passes (test passes with patch) ✅
- [ ] No regressions on other tests
- [ ] SKEPTIC_VERDICT.json = APPROVED for all 5

---

## Lessons Learned

1. **JSON generation > Diff generation** - LLMs excel at structured output, struggle with format/position-sensitive formats

2. **Indentation is enemy of format** - Python code's natural indentation conflicts with unified diff's structural prefix requirement

3. **Anti-rot context isolation works** - Phases 1-3 confirm that fresh context per phase eliminates drift

4. **Simple prompts > complex ones** - Verbose essays confuse; minimal rules + examples work better

5. **Validation reveals problems late** - Format validation passed diffs that failed on apply; need semantic validation too

---

## Next Steps

1. **Implement diff post-processor** (OPTION 1)
2. **Test on all 5 instances**
3. **Update HOW-TO-CRUSH guide** with findings
4. **Run full Batch 1 again**
5. **Document final results**

**Target:** 5/5 success (100%)
**Timeline:** ~4-6 hours to complete

---

## Auth: 65537 | Phuc Forecast v1.0.2
