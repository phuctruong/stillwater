---
id: email-triage-combo
type: combo
wish: email-triage
agents: [email-classifier, skeptic]
skills: [prime-safety, email-triage, oauth3-enforcer]
rung_target: 274177
model_tier: sonnet
recipe: recipe.email-triage-inbox.md
description: "Safe inbox triage with OAuth3 scopes, budget gates, and confirmation."
---

# Email Triage Combo

## Purpose

Run triage in bounded mode:

- read-only first
- no delete automation
- confirmation required for archive/bulk label
- ALCOA+ evidence on every action

## Evidence

- `triage_result.json`
- `budget_log.json`
- `audit_trail.json`

