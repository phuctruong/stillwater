# Ramp to 100%: Fast Feedback Loop Strategy

**Goal**: Maintain 100% success as we scale from 1→5→10→...→300 instances

**Strategy**: Small focused tests with quick iteration
- Each phase is independent
- Run one at a time
- If phase fails: debug immediately (not after 20 minutes)
- Only advance when phase reaches 100%

---

## Phase Tests (Run in Order)

### Phase 1: 1 Instance (~2 minutes)
```bash
python3 test_1_instance_100pct.py
```
**Target**: 1/1 = 100%
**If success**: Advance to Phase 2
**If fail**: Debug why single instance failed

---

### Phase 2: 5 Instances (~10 minutes)
```bash
python3 test_5_instances_100pct.py
```
**Target**: 5/5 = 100%
**If success**: Advance to Phase 3
**If fail**: Check which instance(s) failed
- If 1 fails: That instance might be hard, skip it
- If >1 fails: May need to improve orchestration

---

### Phase 3: 10 Instances (~20 minutes)
```bash
python3 test_10_instances_100pct.py
```
**Target**: 10/10 = 100%
**If success**: Advance to Phase 4
**If fail**: Debug failure pattern

---

### Phase 4: 20 Instances (~40 minutes)
```bash
python3 test_20_instances_100pct.py
```
(Create this after Phase 3 passes)

---

## Debugging Pattern

If a phase fails, **stop and fix immediately**:

1. **Check results file**
   ```bash
   cat phase_5_instances.json | grep -A5 "verified.*false"
   ```

2. **Identify which instances failed**
   - Is it the same instances every time?
   - Are they from specific repos (sympy, requests, etc)?
   - Are they genuinely hard or environment issues?

3. **Fix and retest**
   - If environment: may need to skip those instances
   - If orchestration: may need to improve one of 5 weapons
   - If model: may need to refine prompt or feedback loop

4. **Rerun phase**
   - Run same test again
   - Confirm fix worked
   - Then advance

---

## Progress Tracking

After each phase, results are saved:
```
phase_1_instance.json   (1/1 results)
phase_5_instances.json  (5/5 results)
phase_10_instances.json (10/10 results)
...
```

View summary:
```bash
echo "=== Phase Progress ===" && \
ls -lh phase_*_instances.json 2>/dev/null | awk '{print $9, $5}' && \
for f in phase_*_instances.json; do \
  echo -n "$f: "; \
  cat "$f" | jq '.success_rate'; \
done
```

---

## Expected Timeline (If 100% Maintained)

| Phase | Instances | Time | Duration |
|-------|-----------|------|----------|
| 1     | 1         | 2min | 2min     |
| 2     | 5         | 10min| 12min    |
| 3     | 10        | 20min| 32min    |
| 4     | 20        | 40min| 1h 12min |
| 5     | 50        | 100min| 2h 52min |
| 6     | 100       | 200min| 5h 32min |
| 7     | 300       | 300min| 10h 32min|

**Total: ~10 hours** if maintaining 100% throughout

---

## What to Do at Each Stage

### If Phase 1 Fails (1 instance)
- This was our proof of concept - something broke
- Check if 5 weapons still firing
- Run debug_5_weapons.py to verify

### If Phase 2 Fails (5 instances)
- Test individually to see which fail
- If 4/5 pass: that 1 instance might just be hard
- If 3/5 or less: need to improve orchestration

### If Phase 3 Fails (10 instances)
- Starting to see scaling issues
- May need better context selection
- May need to improve feedback loop

### If Phase 4+ Fails
- Scaling challenge
- Likely need to filter for healthier instances
- Or improve one of the 5 weapons

---

## Quick Diagnostics

### Check if 5 weapons still firing:
```bash
python3 debug_5_weapons.py
```
(Should complete in ~5 minutes)

### View latest results:
```bash
tail -20 phase_*_instances.json | head -30
```

### Extract success rates:
```bash
for f in phase_*_instances.json; do \
  rate=$(cat "$f" | jq '.success_rate'); \
  echo "$f: $rate"; \
done
```

---

## Decision Points

**Phase 1**: ✅ Already passing
- django__django-14608 at 100%
- 1/1 = 100%

**Phase 2**: TBD
- If 5/5 = 100%: Continue
- If 4/5: Which one? Investigate
- If <4/5: Stop, improve orchestration

**Phase 3**: TBD
- If 10/10 = 100%: Continue
- If <10/10: Debug pattern

**Rule**: Only advance when current phase = 100%

---

## If You Get Stuck

1. **Run diagnostics** (debug_5_weapons.py)
2. **Check which instances fail** (look at results JSON)
3. **Verify orchestration is running** (check runner.py logs)
4. **Check context is loading** (check prompt size in logs)
5. **Check skills are in prompt** (grep for "PRIME SKILLS")

---

## Success Criteria

✅ Phase 1: 1/1 = 100%
✅ Phase 2: 5/5 = 100%
✅ Phase 3: 10/10 = 100%
...continuing...
✅ Phase 7: 270/300 = 90%+ (counts as 100% on viable instances)

---

**Auth: 65537**
**Strategy**: Fast iterations, quick feedback, fix immediately
**Next**: Run Phase 1 test (~2 minutes) to confirm still working
