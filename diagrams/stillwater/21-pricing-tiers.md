# Diagram 21: Platform Pricing and Billing Flow

**Description:** solaceagi.com operates a 4-tier pricing model (Free → Student → Warrior → Master → Grandmaster) plus an additive Managed LLM option ($3/mo). Billing is handled via Stripe with webhook event processing. The pricing architecture is designed for zero day-one infrastructure cost: Free tier = OSS + BYOK, paid tiers = proxy passthrough to Together.ai/OpenRouter with 20% markup. Each tier unlocks specific features.

---

## Tier Comparison

```mermaid
flowchart TD
    subgraph FREE["Free — $0/mo"]
        F_DESC["Registration: social media post\n(no credit card, no tip required)\nTarget: early adopters, students, hobbyists"]
        F_FEATURES["Features:\n- stillwater/cli OSS client\n- BYOK (Anthropic/OpenAI/Llama)\n- Community skills from Stillwater Store\n- LLM Portal (localhost:8788)\n- Admin Server (localhost:8787)\n- Rung 641 evidence bundles"]
        F_LLM["LLM: Bring Your Own Key\nUser's own API costs\nStillwater = $0 COGS on LLM"]
    end

    subgraph MANAGED["Managed LLM Add-on — +$3/mo"]
        ML_DESC["Add-on for any tier\n(not standalone)"]
        ML_FEATURES["Features:\n- Hosted LLM (no API key needed)\n- Together.ai/OpenRouter passthrough\n- Primary: Llama 3.3 70B ($0.59/M tokens)\n- Fallback: OpenRouter (Claude, GPT-4, Mixtral)\n- ~6,000 tasks/mo at 70% recipe hit rate"]
        ML_ECONOMICS["Economics:\n20% markup on actual LLM token cost\nPrimary: $0.59/M → ~$0.71/M charged\n~$3/mo flat at average usage\nStillwater gross margin: 20% on LLM proxy"]
    end

    subgraph PRO["Pro — $19/mo (Warrior equivalent)"]
        P_DESC["Target: serious individual developers\nteams, freelancers with client work"]
        P_FEATURES["Includes Managed LLM (+$3/mo value)\n- Cloud twin (solace-browser + solace-cli)\n- OAuth3 vault (AES-256-GCM, cloud-backed)\n- 90-day evidence trail (tamper-evident)\n- All community skills\n- Rung 65537 evidence bundles"]
        P_ECONOMICS["Economics at Pro:\nRecipe hit rate 70% → COGS $5.75/user/mo\n(Haiku at $0.001/task, 6,000 tasks)\n70% gross margin at $19/mo"]
    end

    subgraph ENTERPRISE["Enterprise — $99/mo (Master equivalent)"]
        E_DESC["Target: teams, regulated industries,\nstartups with compliance requirements"]
        E_FEATURES["All Pro features, plus:\n- SOC2 audit trail export\n- Team tokens (multiple agents per org)\n- Private Stillwater Store (internal skills)\n- Dedicated nodes (no shared queue)\n- FDA 21 CFR Part 11 alignment docs\n- Priority support"]
    end

    FREE --> MANAGED
    FREE --> PRO
    PRO --> ENTERPRISE

    style FREE fill:#1a3a1a,stroke:#3fb950
    style MANAGED fill:#1a2a3a,stroke:#58a6ff
    style PRO fill:#2a1a3a,stroke:#a371f7
    style ENTERPRISE fill:#3a1a1a,stroke:#f85149
```

---

## Billing Products (Stripe)

```mermaid
flowchart LR
    subgraph STRIPE_PRODUCTS["Stripe Product Catalog"]
        direction TB
        S1["Student — $8/mo\nEntry-level paid tier\nManaged LLM included\n+ basic cloud features"]
        S2["Warrior — $48/mo\nPro equivalent\nFull cloud twin + OAuth3\n+ 90-day evidence"]
        S3["Master — $88/mo\nEnterprise lite\nTeam tokens + private store\n+ SOC2 audit"]
        S4["Grandmaster — $188/mo\nFull enterprise\nDedicated nodes + FDA docs\n+ priority support"]
    end

    subgraph PRICE_MAP["Tier Mapping"]
        direction TB
        PM1["Free ($0) → OSS only, no Stripe"]
        PM2["Student ($8) → 1,000 tasks/mo\nManaged LLM passthrough"]
        PM3["Warrior ($48) → 6,000 tasks/mo\nCloud twin + OAuth3 vault"]
        PM4["Master ($88) → Team (5 seats)\nPrivate store + SOC2"]
        PM5["Grandmaster ($188) → Team (20 seats)\nDedicated + FDA + SLA"]
    end

    STRIPE_PRODUCTS --> PRICE_MAP
```

---

## Stripe Checkout Flow

```mermaid
sequenceDiagram
    participant USER as User (browser)
    participant SOLACE as solaceagi.com
    participant STRIPE as Stripe
    participant BACKEND as solace-cli backend (PRIVATE)
    participant DB as User DB

    USER->>SOLACE: Click "Upgrade to Warrior ($48/mo)"
    SOLACE->>BACKEND: POST /api/billing/checkout {tier:"warrior", email}
    BACKEND->>STRIPE: Create checkout session\n(price_id: warrior_monthly)
    STRIPE-->>BACKEND: {checkout_url: "https://checkout.stripe.com/..."}
    BACKEND-->>SOLACE: {checkout_url}
    SOLACE-->>USER: Redirect to Stripe Checkout

    USER->>STRIPE: Enter card details
    STRIPE-->>USER: Payment success

    STRIPE->>BACKEND: POST /webhook {type:"checkout.session.completed",\ncustomer_id, subscription_id}
    BACKEND->>BACKEND: Verify Stripe webhook signature\n(STRIPE_WEBHOOK_SECRET)
    BACKEND->>DB: Upgrade user to warrior tier\nset: subscription_id, status: active
    BACKEND->>USER: Email: "Warrior tier activated"

    USER->>SOLACE: Access cloud twin features
    SOLACE->>BACKEND: GET /api/user/tier
    BACKEND->>DB: Check tier
    DB-->>BACKEND: {tier: "warrior", status: "active"}
    BACKEND-->>SOLACE: Authorized

    Note over STRIPE,BACKEND: Webhook events handled:<br/>checkout.session.completed<br/>customer.subscription.updated<br/>customer.subscription.deleted<br/>invoice.payment_failed
```

---

## Webhook Event Handling

```mermaid
flowchart TD
    WEBHOOK["POST /webhook\n(Stripe signature verified)"]

    WEBHOOK --> EVENT_TYPE{"event.type"}

    EVENT_TYPE -->|"checkout.session.completed"| E1["Provision tier:\nActivate subscription\nSend welcome email\nEnable cloud features"]

    EVENT_TYPE -->|"customer.subscription.updated"| E2["Tier change:\nUpgrade or downgrade\nAdjust feature flags\nLog in audit trail"]

    EVENT_TYPE -->|"customer.subscription.deleted"| E3["Cancellation:\nDowngrade to Free\nDisable cloud features\nKeep local CLI (OSS)"]

    EVENT_TYPE -->|"invoice.payment_failed"| E4["Payment failure:\nGrace period (3 days)\nSend reminder email\nRestrict cloud features\n(keep local CLI)"]

    EVENT_TYPE -->|"invoice.payment_succeeded"| E5["Payment success:\nReset grace period\nLog successful billing"]

    E1 & E2 & E3 & E4 & E5 --> AUDIT_LOG["Append to billing audit JSONL\n(hash-chained)"]
```

---

## Economics Model

```mermaid
flowchart TD
    subgraph BYOK_ECON["BYOK Path Economics (Free tier)"]
        BK1["User brings own API key"]
        BK2["Recipe hit rate 70%"]
        BK3["70% of tasks: Haiku at $0.001/task\n(recipe replay — near zero)"]
        BK4["30% of tasks: full LLM call\n(user's API key, not Stillwater's cost)"]
        BK5["Stillwater COGS: $0 on LLM\nRevenue: $0 (free tier)"]
        BK1 --> BK2 --> BK3 & BK4 --> BK5
    end

    subgraph MANAGED_ECON["Managed LLM Economics (+$3/mo)"]
        ML1["User pays +$3/mo managed LLM"]
        ML2["Stillwater proxies Together.ai\n(Llama 3.3 70B at $0.59/M tokens)"]
        ML3["~6,000 tasks/mo at 70% hit rate\n= 1,800 full LLM calls"]
        ML4["Avg 1,800 tokens/call = 3.24M tokens\nat $0.59/M = $1.91 actual cost"]
        ML5["Charged: $3/mo (20% markup)\nGross margin: $1.09/user/mo on LLM"]
        ML1 --> ML2 --> ML3 --> ML4 --> ML5
    end

    subgraph PRO_ECON["Pro Tier Economics ($19/mo)"]
        PR1["$19/mo flat rate"]
        PR2["Includes Managed LLM ($3 value)\n+ Cloud twin + OAuth3 vault\n+ 90-day evidence"]
        PR3["COGS at 70% hit rate:\n$5.75/user/mo (Haiku + Together.ai)"]
        PR4["Gross margin: $13.25/user/mo\n= 70% gross margin"]
        PR1 --> PR2 --> PR3 --> PR4
    end

    subgraph DAY_ONE["Day-One Infrastructure"]
        D1["Day 1: proxy Together.ai/OpenRouter\nZero GPU infra\nZero ML ops"]
        D2["Primary: Llama 3.3 70B\n($0.59/M tokens, Together.ai)"]
        D3["Fallback: OpenRouter\n(broader model selection)"]
        D4["Self-host option:\ndeploy solace-cli + twin\n$0/mo infra for power users"]
        D1 --> D2 & D3 & D4
    end
```

---

## Feature Unlock Matrix

```mermaid
flowchart TD
    subgraph FEATURES["Feature Unlock by Tier"]
        direction TB

        subgraph COL_LABEL["Feature"]
            F01["stillwater/cli OSS"]
            F02["BYOK (own API key)"]
            F03["Community skills"]
            F04["LLM Portal (local)"]
            F05["Admin Server (local)"]
            F06["Rung 641 evidence"]
            F07["Managed LLM (hosted)"]
            F08["Cloud twin"]
            F09["OAuth3 vault"]
            F10["90-day evidence trail"]
            F11["Rung 65537 evidence"]
            F12["Team tokens"]
            F13["Private Store"]
            F14["SOC2 audit export"]
            F15["Dedicated nodes"]
            F16["FDA 21 CFR Part 11 docs"]
        end

        FREE_COL["Free $0\n✓ ✓ ✓ ✓ ✓ ✓\n- - - - - - - - - -"]
        STUDENT_COL["Student $8\n✓ ✓ ✓ ✓ ✓ ✓\n✓ - - - - - - - - -"]
        WARRIOR_COL["Warrior $48\n✓ ✓ ✓ ✓ ✓ ✓\n✓ ✓ ✓ ✓ ✓ - - - - -"]
        MASTER_COL["Master $88\n✓ ✓ ✓ ✓ ✓ ✓\n✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ - -"]
        GRAND_COL["Grandmaster $188\n✓ ✓ ✓ ✓ ✓ ✓\n✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓"]
    end
```

---

## Source Files

- `NORTHSTAR.md` — Pricing tiers (Free, Managed LLM, Pro, Enterprise), economic model
- `/home/phuc/.claude/CLAUDE.md` — Pricing tiers: Student/Warrior/Master/Grandmaster Stripe products
- `case-studies/solaceagi.md` — Refactor + rebuild plan for solaceagi.com
- `ROADMAP.md` — Phase 3: billing integration (Stripe)

---

## Coverage

- All 5 pricing tiers: Free ($0), Student ($8), Warrior ($48), Master ($88), Grandmaster ($188)
- Managed LLM add-on (+$3/mo) as separate additive product
- Feature unlock matrix per tier (16 features)
- Stripe checkout flow: session creation → payment → webhook → provisioning
- All 5 Stripe webhook events and their handling
- Economics model: BYOK COGS $0, Managed LLM 20% markup, Pro 70% gross margin
- Day-one infrastructure: zero GPU, proxy Together.ai/OpenRouter
- Self-host option for power users
