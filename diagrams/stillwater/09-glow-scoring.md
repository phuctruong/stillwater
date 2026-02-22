# Diagram 09 — GLOW Scoring System

GLOW is the gamification scoring system for roadmap-based development in Stillwater.
It measures four dimensions of a session or commit: Growth, Learning, Output, Wins.
Each dimension is scored 0–25, for a total of 0–100.

GLOW cannot be inflated: each component has strict criteria grounded in executable
artifacts, not prose or plans. "You cannot fake the kata. The form knows."

---

## GLOW Component Breakdown

```mermaid
flowchart TD
    SESSION([Session / Commit]) --> G_DIM & L_DIM & O_DIM & W_DIM

    subgraph G_DIM["G — Growth (0–25)\nNew capabilities added"]
        G25["25: Major new module/feature\nat rung 274177+ with tests + evidence bundle"]
        G20["20: Complete new feature\nat rung 641 with tests passing"]
        G15["15: Significant enhancement\nto existing feature with tests"]
        G10["10: New utility / helper /\nconfiguration option"]
        G5["5: Minor addition\nnew test, new constant, small method"]
        G0["0: No new capabilities added"]
        G25 --- G20 --- G15 --- G10 --- G5 --- G0
    end

    subgraph L_DIM["L — Learning (0–25)\nNew knowledge captured"]
        L25["25: New skill or paper published\nto Stillwater Store (rung 65537)"]
        L20["20: New skills/*.md or papers/*.md\ncreated and complete"]
        L15["15: Significant update to existing skill\nadds new section, new rules"]
        L10["10: New persona defined or\nrecipe captured in recipes/"]
        L5["5: Case study updated\nwith new lesson or postmortem"]
        L0["0: No new knowledge captured"]
        L25 --- L20 --- L15 --- L10 --- L5 --- L0
    end

    subgraph O_DIM["O — Output (0–25)\nMeasurable deliverables"]
        O25["25: Multiple files committed\nall tests passing\nevidence bundle complete (rung 274177+)"]
        O20["20: Files committed with\ntests.json + plan.json (rung 641)"]
        O15["15: Files committed\nsome tests passing, evidence partial"]
        O10["10: Single file committed\nwith passing tests"]
        O5["5: Commit produced\neven if small"]
        O0["0: No commit produced"]
        O25 --- O20 --- O15 --- O10 --- O5 --- O0
    end

    subgraph W_DIM["W — Wins (0–25)\nStrategic victories"]
        W25["25: First-mover advantage established\nnew integration nobody else has"]
        W20["20: Competitive moat deepened\nOAuth3 enforcement, evidence bundle, audit trail"]
        W15["15: NORTHSTAR metric measurably advanced\nrecipe hit rate +X%, stars +Y, rung upgraded"]
        W10["10: Phase completed in ROADMAP\ncheckbox checked"]
        W5["5: Sub-task completed\nthat unblocks another phase"]
        W0["0: No strategic progress"]
        W25 --- W20 --- W15 --- W10 --- W5 --- W0
    end

    G_DIM --> TOTAL
    L_DIM --> TOTAL
    O_DIM --> TOTAL
    W_DIM --> TOTAL

    TOTAL["GLOW Total = G + L + O + W\nRange: 0 – 100\nNo rounding up. No partial credit."]

    classDef dimNode fill:#2c4f8c,color:#fff,stroke:#1a3060,font-weight:bold
    classDef totalNode fill:#4a3d6b,color:#e0d4ff,stroke:#2e2345,font-weight:bold
    class G_DIM,L_DIM,O_DIM,W_DIM dimNode
    class TOTAL totalNode
```

---

## Belt Progression Map

```mermaid
stateDiagram-v2
    direction LR

    [*] --> White

    White : White Belt\nGLOW 0–20\nFirst recipes, first rung 641\nSessions averaging any GLOW
    Yellow : Yellow Belt\nGLOW 21–40\nFirst tasks delegated via phuc-swarms\nRecipes producing\nSessions averaging 25+ GLOW
    Orange : Orange Belt\nGLOW 41–60\nSkills published to Stillwater Store\nCommunity impact\nSessions averaging 50+ GLOW
    Green : Green Belt\nGLOW 61–80\nRung 65537 achieved\nProduction-grade verifiable work\nSessions averaging 65+ GLOW
    Blue : Blue Belt\nGLOW 81–90\nCloud execution 24/7\nAutomation running continuously\nSessions averaging 80+ GLOW
    Black : Black Belt\nGLOW 91–100\nModels = commodities\nSkills = capital. OAuth3 = law.\nSessions consistently at 90+

    White --> Yellow : total GLOW ≥ 21
    Yellow --> Orange : total GLOW ≥ 41\n+ first Store submission
    Orange --> Green : total GLOW ≥ 61\n+ rung 65537 achieved
    Green --> Blue : total GLOW ≥ 81\n+ 24/7 cloud execution
    Blue --> Black : total GLOW ≥ 91\n+ 30-day production run
```

---

## Evidence Requirements per Belt Level

```mermaid
flowchart TD
    EV_WHITE["White Belt Evidence\n- At least one commit produced (O ≥ 5)\n- At least one recipe file exists\n- skills/ directory present"]
    EV_YELLOW["Yellow Belt Evidence\n- phuc-swarms running\n- Recipes producing output\n- GLOW sessions averaging 25+\n- O ≥ 10 per commit (tests passing)"]
    EV_ORANGE["Orange Belt Evidence\n- Skill submitted to Stillwater Store\n(sw_sk_ API key used)\n- tests.json + plan.json per commit\n- GLOW sessions averaging 50+\n- L ≥ 15 (new skill file created)"]
    EV_GREEN["Green Belt Evidence\n- security_scan.json with status=PASS\n- behavior_hash.txt with 3-seed consensus\n- Rung 65537 achieved\n- GLOW sessions averaging 65+"]
    EV_BLUE["Blue Belt Evidence\n- Cloud deployment live\n- Automation scripts running 24/7\n- GLOW sessions averaging 80+\n- W ≥ 20 (competitive moat)"]
    EV_BLACK["Black Belt Evidence\n- 30-day production run documented\n- All NORTHSTAR metrics advancing\n- GLOW sessions consistently 90+\n- All rungs achieved (641/274177/65537)"]

    EV_WHITE --> EV_YELLOW --> EV_ORANGE --> EV_GREEN --> EV_BLUE --> EV_BLACK

    classDef belt fill:#2c4f8c,color:#fff,stroke:#1a3060
    class EV_WHITE,EV_YELLOW,EV_ORANGE,EV_GREEN,EV_BLUE,EV_BLACK belt
```

---

## Commit Format Integration

```mermaid
flowchart TD
    COMMIT_MSG["Commit Message Format\n\nfeat: {description}\n\nGLOW {total} [G:{g} L:{l} O:{o} W:{w}]\nNorthstar: {which metric advanced} {delta}\nEvidence: {evidence bundle path or N/A}\nRung: {rung achieved}"]

    COMMIT_MSG --> SCORING_RULES

    subgraph SCORING_RULES["Scoring Rules (enforced)"]
        SR1["Score AFTER the commit\nnot before — artifacts must exist in git"]
        SR2["Score from artifacts\nnot memory, not plans, not vibes"]
        SR3["When uncertain between two levels\ntake the LOWER score"]
        SR4["W > 0 requires:\nexplicit NORTHSTAR metric citation"]
        SR5["O ≥ 20 requires:\nevidence bundle path in commit message"]
    end

    COMMIT_MSG --> PACE_TARGETS

    subgraph PACE_TARGETS["Pace Targets"]
        PT1["Warrior Pace: 60+ GLOW/day\nActive dev day — building, testing, shipping"]
        PT2["Master Pace: 70+ GLOW/week average\nSustained output over full week"]
        PT3["Steady Pace: 40+ GLOW/day\nMaintenance day — fixes, reviews, docs"]
        PT4["Rest Day: 0–20 GLOW\nReview only, no commits"]
    end

    classDef ruleNode fill:#1e2d40,color:#cdd9e5,stroke:#4a6fa5
    classDef paceNode fill:#2c4f8c,color:#fff,stroke:#1a3060
    class SR1,SR2,SR3,SR4,SR5 ruleNode
    class PT1,PT2,PT3,PT4 paceNode
```

---

## GLOW Anti-Patterns (Auto-Fail)

```mermaid
flowchart TD
    AP1["GLOW_WITHOUT_NORTHSTAR_ALIGNMENT\nHigh GLOW for work that advances\nno NORTHSTAR metric\n\nFix: W requires explicit NORTHSTAR citation.\nIf W=0, total GLOW capped at 75."]
    AP2["INFLATED_GLOW\nClaiming 25/25 without\nmeeting the top criteria\n\nFix: Score conservatively.\nWhen uncertain, take the lower."]
    AP3["GLOW_FOR_VIBE_WORK\nClaiming GLOW for sessions\nthat produced insights but no commits\n\nFix: O requires a commit.\nWithout O, session GLOW ≤ 50."]
    AP4["WINS_BY_NARRATIVE\nClaiming W=25 for 'establishing\nfirst-mover advantage' that is only a plan\n\nFix: W requires: ROADMAP checkbox checked,\nmetric value changed, or commit exists."]
    AP5["GLOW_WITHOUT_EVIDENCE\nClaiming O=20/25 without\nevidence/plan.json in repo\n\nFix: O ≥ 20 requires evidence bundle\npath in commit message."]

    AP_ROOT(["GLOW Anti-Pattern\nAuto-Rejection Risk"]) --> AP1
    AP_ROOT --> AP2
    AP_ROOT --> AP3
    AP_ROOT --> AP4
    AP_ROOT --> AP5

    classDef apNode fill:#3d1a1a,color:#ffb3b3,stroke:#7a2020
    classDef rootNode fill:#9b2335,color:#fff,stroke:#6b1520,font-weight:bold
    class AP1,AP2,AP3,AP4,AP5 apNode
    class AP_ROOT rootNode
```

---

## Source Files

- `/home/phuc/projects/stillwater/skills/glow-score.md` — full GLOW specification: all component criteria, belt integration, session tracking, commit format, anti-patterns
- `/home/phuc/projects/stillwater/STORE.md` — GLOW score metadata for Store submissions, glow_score.json schema
- `/home/phuc/projects/stillwater/skills/prime-qa.md` — GLOW taxonomy applied to QA questions (G/L/O/W question types)

## Coverage

- All 4 GLOW dimensions (G, L, O, W) with all scoring tiers (0, 5, 10, 15, 20, 25)
- Belt progression: White through Black with threshold conditions and advancement criteria
- Evidence requirements per belt level
- Commit message format with GLOW breakdown
- Pace targets: warrior (60+), master (70+/week), steady (40+), rest (0–20)
- All 5 GLOW anti-patterns with fixes
- NORTHSTAR alignment rule (W > 0 requires metric citation)
- Conservative scoring rule ("when uncertain, take the lower")
- Artifact-grounded scoring (score after commit, not before)
