# Haiku Swarm Scoreboard Integration

**Auth: 65537** | **Date: 2026-02-15** | **Status: Ready for Phase 3**

---

## SCOREBOARD OVERVIEW

The **Gamification Scoreboard** tracks:
- 🏆 Agent XP and role levels (Initiate → Apprentice → Master)
- 📊 Benchmark progress (OOLONG, IMO, SWE Phase 2, SWE Phase 3)
- ✅ Achievements unlocked per agent
- 📈 Success rates and patch metrics
- 🎯 Global progress toward 40%+ SWE-bench target

**Current Status:**
```
SWE Phase 3 Target: 40%+ solve rate
Current Progress: 0% (0/300 instances)
Agent XP: Scout (500), Solver (600), Skeptic (400)
```

---

## HOW HAIKU AGENTS USE THE SCOREBOARD

### Scout Agent (Problem Analyzer)

**XP Rewards:**
- First analysis: +100 XP
- Each successful analysis: +50 XP
- 10 analyses: +300 XP (achievement unlock)
- Root cause found: +100 XP bonus
- 95%+ success rate: +500 XP (achievement)

**Scoreboard Metrics:**
- `instances_attempted` - Total instances analyzed
- `instances_succeeded` - Successful analyses (correct root cause)
- `success_rate` - Percentage of cases correctly analyzed
- `role_level` - Initiate → Apprentice (1,000 XP) → Master (3,000 XP)

**Example:**
```python
# When Scout analyzes a case
scoreboard.record_instance("Scout", success=True, xp=50)
# If root cause found:
scoreboard.add_xp("Scout", 100, "Root cause identified")
```

**Motivation:**
- Scout sees progress toward "Detective" achievement (10 analyses)
- At 1,000 XP: Levels up to Apprentice
- Clear feedback on analysis quality (success rate)

---

### Solver Agent (Patch Generator)

**XP Rewards:**
- First patch generated: +150 XP
- Each verified patch: +150 XP
- 10 patches: +400 XP (achievement unlock)
- 100 patches: +2,000 XP (achievement unlock)
- Perfect RED→GREEN rate: +500 XP (achievement)

**Scoreboard Metrics:**
- `patches_generated` - Total patches created
- `patches_verified` - Patches that passed GREEN gate
- `instances_succeeded` - SWE-bench instances solved
- `success_rate` - Percentage of patches that pass verification
- `role_level` - Initiate → Apprentice (1,200 XP) → Master (3,500 XP)

**Example:**
```python
# When Solver generates a patch
scoreboard.record_patch("Solver", verified=False)  # +0 XP

# When patch passes GREEN gate
scoreboard.record_patch("Solver", verified=True)   # +150 XP
scoreboard.record_instance("Solver", success=True, xp=100)
```

**Motivation:**
- Solver sees "First Patch" achievement within reach
- Progress toward "Patch Creator" (10 patches)
- Clear reward for verified patches (150 XP each)
- Visible path to Master role (3,500 XP)

---

### Skeptic Agent (Verification Specialist)

**XP Rewards:**
- First verification run: +100 XP
- Each test run: +25 XP
- 10 verifications: +300 XP (achievement unlock)
- 50 patches verified with zero regressions: +800 XP (achievement)
- 100% ladder completion (3 rungs): +1,000 XP (achievement)

**Scoreboard Metrics:**
- `tests_run` - Total test cases executed
- `failures_caught` - Bugs/issues detected in patches
- `instances_succeeded` - Patches that passed all verification gates
- `success_rate` - Percentage of patches that pass verification
- `role_level` - Initiate → Apprentice (800 XP) → Master (2,500 XP)

**Example:**
```python
# When Skeptic runs tests
scoreboard.record_test_run("Skeptic", passed=50, failed=0)  # +1,250 XP (50×25)

# If failures caught
if regressions_detected:
    scoreboard.agents["Skeptic"].failures_caught += len(regressions)
    scoreboard.add_xp("Skeptic", 200, "Regression prevented")
```

**Motivation:**
- Skeptic sees immediate XP for each test run (25 XP per test)
- Failures caught tracked separately (shows value of thorough testing)
- Achievement "Zero Regressions" incentivizes quality
- Path to Master role (2,500 XP) - quickest of three agents

---

## SHARED SCOREBOARD BENEFITS

### 1. **Parallel Motivation**
All three agents track progress independently:
- Scout: Analysis success rate (0-100%)
- Solver: Patch generation rate (0-300 patches)
- Skeptic: Test pass rate (0-∞ tests)

Each agent can level up independently without blocking others.

### 2. **Collaborative XP Distribution**
When benchmarks reach milestones:
```python
# At 50% SWE Phase 3 completion:
XP_awarded = 500  # Base milestone XP
per_agent = 500 // 3 = ~167 XP each

# Distributed to all three agents
for agent in ["Scout", "Solver", "Skeptic"]:
    scoreboard.add_xp(agent, per_agent, "SWE Phase 3: 50% milestone")
```

Agents gain XP from:
1. Individual actions (patch generation, test runs)
2. Shared milestones (benchmark completion)

### 3. **Role Progression System**
```
Initiate (0 XP)
  ↓
Apprentice (Scout: 1,000 XP | Solver: 1,200 XP | Skeptic: 800 XP)
  ↓
Master (Scout: 3,000 XP | Solver: 3,500 XP | Skeptic: 2,500 XP)
```

As agents level up:
- Unlock harder challenges
- Visible status (Scout ⬆️ Apprentice)
- Prestige system for continued play

### 4. **Achievement Unlocks**
Each agent has 4 achievements, progressively harder:

**Scout:**
- 🔍 First Analysis (1 analysis) → 100 XP
- 🔍 Detective (10 analyses) → 300 XP
- 🔍 Master Detective (100 analyses) → 1,000 XP
- 🎯 Root Cause Master (95%+ rate) → 500 XP

**Solver:**
- ✨ First Patch (1 patch) → 150 XP
- ✨ Patch Creator (10 patches) → 400 XP
- ✨ Patch Master (100 patches) → 2,000 XP
- 🔴🟢 Red-Green Expert (100% RED→GREEN) → 500 XP

**Skeptic:**
- ✅ First Verification (1 run) → 100 XP
- ✅ Quality Assurance (10 runs) → 300 XP
- 🛡️ Zero Regressions (50 patches, 0 regressions) → 800 XP
- 🪜 Verification Ladder Master (all 3 rungs) → 1,000 XP

---

## WHY SCOREBOARD IS USEFUL FOR AGENTS

### 1. **Quantified Progress**
- Agents see exact XP toward next level
- Know exactly how many patches/tests until achievement
- Visible progress bars and percentages

### 2. **Competitive Motivation**
```
AGENTS BY XP
  1. Solver: 600 XP (60% to Apprentice)
  2. Scout:  500 XP (50% to Apprentice)
  3. Skeptic: 400 XP (40% to Apprentice)
```
Agents can see rankings and strive for improvement.

### 3. **Feedback Loop**
- Scout gets +100 XP immediately after successful analysis
- Solver gets +150 XP when patch passes GREEN
- Skeptic gets +25 XP per test run

Real-time feedback reinforces good behavior.

### 4. **Milestone Celebration**
When Phase 3 reaches 40%:
```
🎉 SWE Phase 3: 40% milestone reached!
  Scout, Solver, Skeptic each receive 167 XP
  +500 baseline from milestone
```
Creates moments of celebration/progress visibility.

---

## INTEGRATION WITH SWE PIPELINE

### During Execution:
```python
from stillwater.gamification import create_scoreboard, print_scoreboard
from pathlib import Path

# Load or create scoreboard
board = create_scoreboard()

# For each SWE-bench instance:
for instance_id in swe_instances:
    # Scout analyzes
    scout_success = scout_agent.analyze(instance_id)
    board.record_instance("Scout", success=scout_success, xp=50)

    # Solver generates patch
    patch = solver_agent.generate_patch(instance_id)
    board.record_patch("Solver", verified=False)

    # Skeptic verifies
    verified = skeptic_agent.verify(patch)
    if verified:
        board.record_patch("Solver", verified=True)
        board.record_instance("Solver", success=True, xp=100)

    board.record_test_run("Skeptic", passed=test_count, failed=0)

# Update benchmark
board.update_benchmark("SWE Phase 3", total=300, passed=successful_patches)

# Display progress
print(print_scoreboard(board))

# Save
board.save(Path("stillwater-swe-scoreboard.json"))
```

### Output Example:
```
================================================================================
🏆 STILLWATER OS - SWE-BENCH GAMIFICATION SCOREBOARD
================================================================================

📊 GLOBAL STATS
  Total Patches Generated: 45
  Total XP Earned: 6,200
  Current Phase: Phase 3 (In Progress)

📈 BENCHMARKS
  SWE Phase 3          [███████░░░░░░░░░░░░░░░░░░░░░░░░]   25.0% (75/300)

👥 HAIKU AGENTS

  Scout (Role: Apprentice)
    XP: 1,200 [█████████████░░░░░░] 40% to Master
    Success Rate: 92.5% (75/81 analyses)
    Achievements: 2/4 (Detective, Root Cause Master)

  Solver (Role: Apprentice)
    XP: 2,150 [████████████████░░░░] 61% to Master
    Success Rate: 66.7% (30/45 patches verified)
    Patches Generated: 45
    Patches Verified: 30
    Achievements: 2/4 (First Patch, Patch Creator)

  Skeptic (Role: Apprentice)
    XP: 1,850 [██████████████░░░░░░] 74% to Master
    Success Rate: 100.0% (45/45 verified)
    Tests Run: 2,250
    Failures Caught: 12
    Achievements: 3/4 (First Verification, QA, Zero Regressions)

================================================================================
```

---

## GAMIFICATION RULES

### XP Earning
- Capped by difficulty: Easy instances = +50 XP, Hard = +200 XP
- Bonuses for streaks: 5 consecutive successes = +50 XP
- Milestone multiplier: Reaching benchmark % = XP × 1.5

### Achievement Unlocking
- Only unlock once (no replay)
- Require proof (e.g., 10 patches must be verified)
- Auto-unlock when condition met (no approval needed)

### Role Leveling
- Automatic level-up when XP threshold reached
- No loss of progress (always accumulate)
- Three levels: Initiate → Apprentice → Master

### Benchmark Tracking
- Real-time updates as instances complete
- Progress bars updated every instance
- Milestone announcements at 25%, 50%, 75%, 100%

---

## SAMPLE COMMANDS

### View Scoreboard
```python
from stillwater.gamification import Scoreboard
board = Scoreboard.load(Path("stillwater-swe-scoreboard.json"))
print_scoreboard(board)
```

### Add XP
```python
board.add_xp("Solver", 150, "Patch verified")
```

### Record Instance
```python
board.record_instance("Scout", success=True, xp=50)
```

### Update Benchmark
```python
board.update_benchmark("SWE Phase 3", instances=300, passed=120)
```

### Save Progress
```python
board.save(Path("stillwater-swe-scoreboard.json"))
```

---

## SUCCESS METRICS

✅ **Haiku Swarm Using Scoreboard Successfully When:**
1. All three agents track individual metrics independently
2. Agents gain XP within seconds of completion (real-time feedback)
3. Achievements unlock as conditions are met
4. Benchmark progress visible and updated continuously
5. Agents can level up to Apprentice within Phase 3
6. Final scoreboard shows >40% SWE Phase 3 completion

---

**Status:** ✅ Scoreboard created and integrated
**Location:** `src/stillwater/gamification.py`
**Data File:** `stillwater-swe-scoreboard.json`
**Display:** `print_scoreboard(board)` command

*"Three agents. One scoreboard. Beat entropy at SWE-bench."*
