---
id: browser-combo
type: combo
wish: browser
agents: [twin-agent]
skills: [prime-safety, prime-browser]
rung_target: 641
model_tier: sonnet
description: "Browser automation — scraping, form filling, testing, and web interaction"
---

# Browser Combo

## Agents
- **twin-agent** (sonnet) -- automate browser interactions, scrape data, fill forms, capture screenshots

## Skill Pack
- prime-safety (god-skill, always first)
- prime-browser (browser automation expertise)

## Execution Flow

```mermaid
flowchart LR
    A[Parse Browser Task] --> B[Launch Browser Session]
    B --> C[Execute Actions]
    C --> D[Capture Results]
    D --> E{Success?}
    E -->|Yes| F[Evidence Bundle]
    E -->|No| C
```

## Evidence Required
- browser_log.json (action sequence and results)
- screenshots/ (captured page states)
- extracted_data.json (scraped content if applicable)
- env_snapshot.json (reproducibility)

## Notes
- Browser sessions are isolated and ephemeral
- All navigation is scope-gated by recipe permissions
- Screenshots provide visual evidence of completion
