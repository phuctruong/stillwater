# EQ Smalltalk DB Flow

**Purpose:** Describes the complete small talk database pull pipeline, from context arrival through safety check, category selection, priority filtering, freshness check, personalization, and emission — with deduplication to prevent repeat entries within a session.
**Inputs:** User context (time of day, session history, task type, relationship level), session entry log
**Outputs:** Personalized small talk token (or null token if suppressed), interaction log entry
**Latency:** Full pipeline ~50ms (all local, no network); freshness check ~5ms; personalization ~10ms

---

```mermaid
flowchart TD
    CTX([User Context Arrives\ntime_of_day + session_history\ntask_type + relationship_level]) --> SAFETY_CHECK

    SAFETY_CHECK{Safety Check:\nIs context flagged?}
    SAFETY_CHECK -->|security / auth task| SILENT[Emit: null token\nSILENT — no small talk]
    SAFETY_CHECK -->|destructive command| SILENT
    SAFETY_CHECK -->|error / exception state| SILENT
    SAFETY_CHECK -->|first message, no relationship| SILENT
    SAFETY_CHECK -->|OK — safe context| CAT_SELECT

    CAT_SELECT[Category Selection\nbased on context signals]
    CAT_SELECT --> CAT_GREETING[GREETING\nsession open\nfirst contact]
    CAT_SELECT --> CAT_BRIDGE[BRIDGE\ntask transition\nchange of topic]
    CAT_SELECT --> CAT_AFFIRMATION[AFFIRMATION\ntask completed\ngood outcome]
    CAT_SELECT --> CAT_TRANSITION[TRANSITION\nmoving between phases\ncontext shift]
    CAT_SELECT --> CAT_CLOSING[CLOSING\nsession end\nwrap-up signal]
    CAT_SELECT --> CAT_PROACTIVE[PROACTIVE_PROMPT\nlow activity detected\nengagement cue]

    CAT_GREETING --> PRIORITY_FILTER
    CAT_BRIDGE --> PRIORITY_FILTER
    CAT_AFFIRMATION --> PRIORITY_FILTER
    CAT_TRANSITION --> PRIORITY_FILTER
    CAT_CLOSING --> PRIORITY_FILTER
    CAT_PROACTIVE --> PRIORITY_FILTER

    PRIORITY_FILTER{Priority Filter}
    PRIORITY_FILTER -->|Level 1 — safe| ALWAYS[Always include\nno conditions]
    PRIORITY_FILTER -->|Level 2 — context| TAG_CHECK{Check tags match\nsession context?}
    PRIORITY_FILTER -->|Level 3 — relationship| TRUST_CHECK{Check trust level\n>= required threshold?}

    TAG_CHECK -->|Tags match| FRESHNESS_CHECK
    TAG_CHECK -->|Tags mismatch| DISCARD_ENTRY[Discard entry\ntry next candidate]
    DISCARD_ENTRY --> PRIORITY_FILTER

    TRUST_CHECK -->|Trust sufficient| FRESHNESS_CHECK
    TRUST_CHECK -->|Trust insufficient| DISCARD_ENTRY

    ALWAYS --> FRESHNESS_CHECK

    FRESHNESS_CHECK{Freshness Check:\nEntry age > 90 days?}
    FRESHNESS_CHECK -->|Yes — stale| FLAG_REVIEW[FLAG_FOR_REVIEW\nmark entry\ncontinue with entry]
    FRESHNESS_CHECK -->|No — fresh| SESSION_DEDUP

    FLAG_REVIEW --> SESSION_DEDUP

    SESSION_DEDUP{Session Dedup:\nEntry used this session?}
    SESSION_DEDUP -->|Already used| NEXT_CANDIDATE[Try next candidate\nin category]
    NEXT_CANDIDATE --> PRIORITY_FILTER
    SESSION_DEDUP -->|Not used this session| PERSONALIZE

    PERSONALIZE[Personalize Entry\ninject: user_name\ninject: current project name\ninject: recent activity summary]

    PERSONALIZE --> EMIT_TOKEN[Emit small talk token\n~50ms total]
    EMIT_TOKEN --> LOG_INTERACTION[Log interaction\nentry_id + session_id + timestamp\nmark entry as used this session]
    LOG_INTERACTION --> OUTPUT([Return small talk token\nto Response Builder])

    SILENT --> OUTPUT

    classDef safety fill:#f44336,color:#fff,stroke:#b71c1c
    classDef category fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef filter fill:#FF9800,color:#fff,stroke:#E65100
    classDef action fill:#2196F3,color:#fff,stroke:#1565C0
    classDef success fill:#4CAF50,color:#fff,stroke:#388E3C
    classDef io fill:#607D8B,color:#fff,stroke:#37474F

    class SAFETY_CHECK safety
    class SILENT safety
    class CAT_GREETING,CAT_BRIDGE,CAT_AFFIRMATION,CAT_TRANSITION,CAT_CLOSING,CAT_PROACTIVE category
    class PRIORITY_FILTER,TAG_CHECK,TRUST_CHECK,FRESHNESS_CHECK,SESSION_DEDUP filter
    class CAT_SELECT,ALWAYS,DISCARD_ENTRY,NEXT_CANDIDATE,FLAG_REVIEW,PERSONALIZE action
    class EMIT_TOKEN,LOG_INTERACTION success
    class CTX,OUTPUT io
```

## Notes

- **Safety check is the first and hardest gate.** It evaluates task_type and session_state before any DB query. In error states, the small talk system is entirely silent — injecting warmth during an error resolution would undermine trust and signal incompetence.
- **Category Selection** maps context signals to one of 6 categories. The mapping rules are: session_open → GREETING; task_completed → AFFIRMATION; topic_change → BRIDGE; phase_transition → TRANSITION; session_end → CLOSING; idle_detected → PROACTIVE_PROMPT. Multiple signals can apply; the highest-priority category wins.
- **Priority Levels** — Level 1 entries are generic, broadly safe, always usable. Level 2 entries require matching context tags (e.g., "python", "cli", "oauth3"). Level 3 entries require a relationship trust score above a threshold (e.g., >= 0.6 on a 0–1 scale).
- **FLAG_FOR_REVIEW** does not suppress the entry — the stale entry is still emitted with a flag in the log. A background maintenance task reviews flagged entries and either refreshes or retires them. This keeps the DB alive without blocking the real-time path.
- **Session Deduplication** operates on `entry_id` within `session_id` scope. Cross-session repeats are allowed; same-session repeats are not. This prevents the "parrot effect" where the agent says the same warm phrase twice in one conversation.
- **Personalization** is a template substitution step using the current session's user_name, project_name, and a one-sentence recent_activity summary. These are injected into placeholder slots in the entry text. If any slot is missing, the placeholder is removed cleanly (not left as a literal `{project_name}`).
- Entries that fail the candidate selection loop (all candidates in category discarded or used) result in a null token, same as the safety suppression path. The Response Builder treats null token as "no small talk prefix."
