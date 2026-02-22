# Diagram 18: Complete User Journey — Discovery to Black Belt

**Description:** The complete user journey from initial discovery of Stillwater through installation, first skill execution, first evidence bundle, skill store submission, and belt progression to Black Belt. Shows three distinct user paths: hobbyist/individual developer, enterprise/team, and community contributor.

---

## Full Journey Overview

```mermaid
flowchart TD
    subgraph DISCOVERY["Discovery"]
        D1["GitHub browse\n(search: AI verification)"]
        D2["Hacker News post\n('AI without evidence is malpractice')"]
        D3["LinkedIn article\n(Phuc Truong / Stillwater Dispatch)"]
        D4["Word of mouth\n(colleague shares)"]
        D5["phuc.net article\n(SEO / organic search)"]
    end

    subgraph INSTALL["Installation"]
        I1["Clone repo:\ngit clone stillwater"]
        I2["Install CLI:\npip install -e cli/"]
        I3["Run doctor:\npython -m stillwater doctor"]
        I4["Configure LLM:\npython -m stillwater llm status"]
        I5["Set API key or\nstart Ollama locally"]
    end

    subgraph FIRST_SKILL["First Skill Run"]
        F1["Browse skills/\n(prime-safety, prime-coder, etc.)"]
        F2["Run with LLM:\nllm_call('ping', provider='ollama')"]
        F3["See call logged to\n~/.stillwater/llm_calls.jsonl"]
        F4["Run a recipe\n(skills/prime-coder.md)"]
        F5["See evidence output:\ntests.json + plan.json"]
    end

    subgraph WHITE["White Belt — Rung 641"]
        W1["Write a failing test (red)"]
        W2["Apply patch"]
        W3["Test passes (green)"]
        W4["Evidence bundle:\nrepro_red.log + repro_green.log\ntests.json + plan.json"]
        W5["WHITE BELT EARNED\nLocal correctness verified"]
    end

    subgraph YELLOW["Yellow Belt — Rung 274177"]
        Y1["Run seed sweep\n(multiple random seeds)"]
        Y2["Run replay test\n(same input → same output)"]
        Y3["Run null edge sweep\n(null inputs handled correctly)"]
        Y4["YELLOW BELT EARNED\nStability verified"]
    end

    subgraph ORANGE["Orange Belt — Store Submission"]
        O1["Develop skill or recipe\nwith evidence at rung 641+"]
        O2["Submit to Stillwater Store\n(PR + evidence bundle)"]
        O3["Community review\n(rung gate validation)"]
        O4["Skill published to Store"]
        O5["ORANGE BELT EARNED\nFirst skill in Stillwater Store"]
    end

    subgraph GREEN["Green Belt — Rung 65537"]
        G1["Add adversarial tests"]
        G2["Pass security gate\n(prime-safety audit)"]
        G3["Behavioral hash stable\n(hash.json committed)"]
        G4["GREEN BELT EARNED\nProduction confidence"]
    end

    subgraph BLUE["Blue Belt — Cloud 24/7"]
        B1["Deploy skill to\nsolaceagi.com cloud"]
        B2["Automated execution\n24/7 (no manual trigger)"]
        B3["BLUE BELT EARNED\nCloud execution running"]
    end

    subgraph BLACK["Black Belt"]
        BK1["Production task running\nat rung 65537 for 30 days"]
        BK2["Models = commodities\nSkills = capital\nOAuth3 = law"]
        BK3["BLACK BELT EARNED"]
    end

    DISCOVERY --> INSTALL
    INSTALL --> FIRST_SKILL
    FIRST_SKILL --> WHITE
    WHITE --> YELLOW
    YELLOW --> ORANGE
    ORANGE --> GREEN
    GREEN --> BLUE
    BLUE --> BLACK
```

---

## Three User Paths

```mermaid
flowchart TD
    START["User discovers Stillwater"]
    START --> FORK{"Who are you?"}

    FORK -->|"Individual\ndeveloper / hobbyist"| HOBBYIST
    FORK -->|"Team / Enterprise"| ENTERPRISE
    FORK -->|"OSS Contributor"| CONTRIBUTOR

    subgraph HOBBYIST["Path A: Individual Developer"]
        direction TB
        H1["Clone + install\n(free, BYOK)"]
        H2["Connect own API key\n(Anthropic / OpenAI / Ollama)"]
        H3["Run prime-coder on\nown project bugfixes"]
        H4["Achieve White Belt\n(rung 641 evidence)"]
        H5["Use Admin UI\n(localhost:8787) to\nbrowse/edit skills"]
        H6["Use LLM Portal\n(localhost:8788) to\ntest providers"]
        H7["Submit first recipe\nto Stillwater Store"]
        H8["Orange Belt — recognized\ncommunity contributor"]

        H1 --> H2 --> H3 --> H4 --> H5 & H6 --> H7 --> H8
    end

    subgraph ENTERPRISE["Path B: Enterprise Team"]
        direction TB
        E1["Evaluate OSS CLI\n(stillwater/cli)"]
        E2["Sign up for solaceagi.com\nPro ($19/mo) or Enterprise ($99/mo)"]
        E3["Upgrade to solace-cli\n(OAuth3 vault + cloud twin)"]
        E4["Configure team tokens\n(Enterprise tier)"]
        E5["Run SOC2 audit trail\n(hash-chained evidence)"]
        E6["Deploy skills at rung 65537\n(FDA 21 CFR Part 11 ready)"]
        E7["24/7 cloud execution\n(Blue Belt)"]

        E1 --> E2 --> E3 --> E4 --> E5 --> E6 --> E7
    end

    subgraph CONTRIBUTOR["Path C: OSS Contributor"]
        direction TB
        C1["Fork + clone stillwater"]
        C2["Read CLAUDE.md + skills/\n(understand dispatch model)"]
        C3["Write new skill or recipe\n(prime-safety first)"]
        C4["Submit PR + evidence bundle\n(rung 641 minimum)"]
        C5["Pass community review\n(rung gate check)"]
        C6["Skill published to Store\n(Orange Belt)"]
        C7["Improve recipe hit rate\nfor ALL users (flywheel)"]
        C8["Earn community belt XP\n(tracked in STORE.md)"]

        C1 --> C2 --> C3 --> C4 --> C5 --> C6 --> C7 --> C8
    end
```

---

## Discovery to Installation Sequence

```mermaid
sequenceDiagram
    participant USER as New User
    participant GH as GitHub
    participant CLI as stillwater CLI
    participant PORTAL as LLM Portal (8788)
    participant ADMIN as Admin Server (8787)
    participant LLM as LLM Provider

    USER->>GH: git clone https://github.com/stillwater/stillwater
    GH-->>USER: Repo cloned

    USER->>CLI: pip install -e cli/
    CLI-->>USER: stillwater installed

    USER->>CLI: python -m stillwater doctor
    CLI-->>USER: {ok: true, providers: [...], rung: 641}

    USER->>PORTAL: bash admin/start-llm-portal.sh
    PORTAL-->>USER: Running on localhost:8788

    USER->>PORTAL: Browser: http://localhost:8788
    PORTAL-->>USER: Dark-theme web UI

    USER->>PORTAL: POST /api/providers/auth {provider:"anthropic", api_key:"sk-..."}
    PORTAL-->>USER: {status:"authenticated"}

    USER->>PORTAL: POST /v1/chat/completions {messages:[{role:"user", content:"Hello!"}]}
    PORTAL->>LLM: Route to Anthropic API
    LLM-->>PORTAL: Response text
    PORTAL-->>USER: {choices:[...], _meta:{latency_ms:450, provider:"anthropic"}}

    USER->>CLI: python -m stillwater llm status
    CLI-->>USER: Active: anthropic | claude-sonnet-4-6 | PASS

    Note over USER,LLM: Call logged to ~/.stillwater/llm_calls.jsonl<br/>White Belt journey begins
```

---

## Belt Progression Milestones

```mermaid
flowchart LR
    subgraph BELTS["Belt System — Stillwater Dojo"]
        W["WHITE BELT\nRung 641\nLocal correctness\nred/green test passes\nevidence bundle complete"]
        Y["YELLOW BELT\nRung 274177\nStability\nseed sweep + replay\nnull edge sweep"]
        O["ORANGE BELT\nFirst Store submission\nSkill reviewed + published\ncommunity validated"]
        G["GREEN BELT\nRung 65537\nProduction confidence\nadversarial + security\nbehavioral hash stable"]
        B["BLUE BELT\nCloud 24/7\nAutomated execution\nno manual trigger needed"]
        BK["BLACK BELT\n30 days at rung 65537\nModels = commodities\nSkills = capital\nOAuth3 = law"]

        W -->|"seed sweep\n+ replay tests"| Y
        Y -->|"build skill\n+ submit PR"| O
        O -->|"adversarial tests\n+ security gate"| G
        G -->|"deploy to cloud\n+ automate"| B
        B -->|"30 days production\nstability"| BK
    end
```

---

## GLOW Score Along the Journey

```mermaid
flowchart TD
    subgraph GLOW_JOURNEY["GLOW Score Integration in User Journey"]
        SESSION["Every session earns GLOW\nG: Growth (0-25)\nL: Learning (0-25)\nO: Output (0-25)\nW: Wins (0-25)"]

        SESSION --> COMMIT_FORMAT["Commit format:\nfeat: {description}\nGLOW {total} [G:{g} L:{l} O:{o} W:{w}]\nNorthstar: {metric advanced}\nRung: {rung}"]

        subgraph PACE["Pace Targets"]
            P1["Warrior: 60+ GLOW/day"]
            P2["Master: 70+ GLOW/week avg"]
            P3["Steady: 40+ GLOW/day"]
        end

        subgraph CHEAT_RESISTANT["Cheat-Resistant Design"]
            CR1["O requires git commit\n(no vibes without artifacts)"]
            CR2["W requires NORTHSTAR\nmetric advancement"]
            CR3["G requires tests\n(not just code)"]
            CR4["Max GLOW without commits = 20\n(learning only)"]
        end

        SESSION --> PACE & CHEAT_RESISTANT
    end
```

---

## Source Files

- `NORTHSTAR.md` — Belt system, GLOW score, user journey milestones
- `ROADMAP.md` — Phased build plan (audit → OAuth3 → Store → 65537)
- `admin/server.py` — Admin UI entry point (localhost:8787)
- `admin/llm_portal.py` — LLM Portal entry point (localhost:8788)
- `cli/src/stillwater/__main__.py` — CLI entry point (doctor, llm status)
- `STORE.md` — Stillwater Store policy and belt XP tracking

---

## Coverage

- Full journey: Discovery → Installation → First Skill → White Belt → Black Belt
- Three distinct user paths: hobbyist (BYOK free), enterprise (Pro/Enterprise tiers), OSS contributor
- Belt criteria for all 6 belts (White through Black) with exact rung requirements
- Discovery channels: GitHub, HN, LinkedIn, phuc.net, word of mouth
- Installation sequence with CLI commands
- GLOW score integration (gamification per session)
- Belt XP cheat-resistant design (artifacts required, not prose confidence)
- Community flywheel: contributor skills improve hit rate for all users
