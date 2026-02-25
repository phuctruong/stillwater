---
id: content-combo
type: combo
wish: content
agents: [writer, social-media]
skills: [prime-safety, prime-docs]
rung_target: 641
model_tier: sonnet
description: "Content creation — articles, social media, marketing copy, and newsletters"
---

# Content Combo

## Agents
- **writer** (sonnet) -- draft long-form content, articles, documentation
- **social-media** (sonnet) -- adapt content for social platforms, create campaigns

## Skill Pack
- prime-safety (god-skill, always first)
- prime-docs (writing and documentation expertise)

## Execution Flow

```mermaid
flowchart LR
    A[Define Content Brief] --> B[Research Topic]
    B --> C[Draft Content]
    C --> D[Review & Edit]
    D --> E{Quality Check}
    E -->|Pass| F[Format for Platform]
    E -->|Fail| C
    F --> G[Evidence Bundle]
```

## Evidence Required
- content_draft.md (written content)
- platform_versions/ (adapted versions per platform)
- style_check.json (tone, readability, SEO metrics)
- env_snapshot.json (reproducibility)

## Notes
- Content must match brand voice guidelines if provided
- Social media posts are limited to platform character limits
- All content is reviewed before publishing
