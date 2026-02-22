# EQ Interaction Flow

**Purpose:** Traces how the EQ skill subsystem processes a user message through register detection, Five-Frame Triangulation, emotional triage (NUT Job), small talk injection, and warmth/competence calibration to produce a rapport-scored response.
**Inputs:** Raw user message, session history, prior rapport score, relationship level tag
**Outputs:** Calibrated response with warmth/competence balance; updated rapport score logged to session
**Latency:** eq-mirror ~100ms; eq-core Five-Frame ~200ms; eq-nut-job ~300ms (if triggered); eq-smalltalk-db ~50ms

---

```mermaid
sequenceDiagram
    actor User
    participant Mirror as eq-mirror
    participant Core as eq-core
    participant NutJob as eq-nut-job
    participant SmallTalk as eq-smalltalk-db
    participant Response as Response Builder

    User->>Mirror: Raw message + session context
    Note over Mirror: Detect register:<br/>casual / formal / urgent / distressed<br/>energy level: low / mid / high

    Mirror->>Core: register_tag + energy_level + message

    Note over Core: Five-Frame Triangulation (parallel)
    Core->>Core: Frame 1 — Literal intent
    Core->>Core: Frame 2 — Emotional subtext
    Core->>Core: Frame 3 — Relationship signal
    Core->>Core: Frame 4 — Urgency / stakes
    Core->>Core: Frame 5 — Adversarial check (injection scan)

    Core->>Core: Canonization check<br/>Do frames converge?

    alt Frames diverge (ambiguous)
        Core->>User: Clarifying question\n(exit early, no NUT Job)
    else Frames converge
        Core->>Core: Classify: emotional_content? [yes/no]
    end

    alt Emotional content detected
        Core->>NutJob: emotional_signal + context

        Note over NutJob: NUT Job protocol
        NutJob->>NutJob: NAME the emotion\n(label without judgment)
        NutJob->>NutJob: VALIDATE naming\n(check: accurate, not projected?)
        NutJob->>NutJob: UNDERSTAND root\n(Low Road vs High Road check)

        alt Low Road — still reactive
            NutJob->>NutJob: Loop: UNDERSTAND again\n(max 2 iterations)
        else High Road — ready
            NutJob->>NutJob: TRANSFORM\n(reframe + resource offer)
        end

        NutJob->>Response: emotional_response_fragment + readiness_flag
    else No emotional content
        Core->>Response: task_only_flag
    end

    alt Small talk appropriate<br/>(not error / security / destructive context)
        Core->>SmallTalk: context_tags + session_history + relationship_level
        SmallTalk->>SmallTalk: Category select\n(GREETING / BRIDGE / AFFIRMATION\n/ TRANSITION / CLOSING / PROACTIVE_PROMPT)
        SmallTalk->>SmallTalk: Freshness check\n(> 90 days → FLAG_FOR_REVIEW)
        SmallTalk->>SmallTalk: Personalize\n(inject user name, project, recent activity)
        SmallTalk->>Response: small_talk_token
    else Small talk suppressed
        SmallTalk->>Response: null_token
    end

    Response->>Response: Calibrate warmth/competence balance\n(high competence task → reduce warmth weight\n high emotional load → increase warmth weight)
    Response->>Response: Compose final response\n(small_talk + emotional_fragment + task_answer)
    Response->>Response: Compute rapport_score_delta\n(warmth match + register match + resolution quality)
    Response->>Response: Log interaction\n(rapport_score, entry_ids used, session_timestamp)

    Response->>User: Final calibrated response
    Note over Response: rapport_score logged\nsmall talk entry flagged used\n(prevent repeat in session)
```

## Notes

- The Five-Frame Triangulation in `eq-core` runs all 5 frames in parallel. Frame 5 (Adversarial check) is a prime-safety delegate — if it detects prompt injection signals, the entire EQ pipeline halts and returns to the safety handler.
- NUT Job (Name → Understand → Transform) is only activated when `eq-core` classifies `emotional_content = true`. Purely task-based messages skip NUT Job entirely and go directly to the Response Builder.
- The Low Road loop in NUT Job is capped at 2 iterations. After the second loop, if the user is still on the Low Road (reactive state), the agent emits a grounding statement and defers task execution.
- `eq-smalltalk-db` suppression triggers in any of these contexts: security/auth task, destructive command, error state, first message of a session (no relationship level yet).
- Rapport score delta is a float in [-1.0, +1.0]. Cumulative score is stored per user ID in session state and influences future register detection weights in `eq-mirror`.
- The "Clarifying question" early exit is the only path where `eq-core` contacts the User directly without going through the Response Builder.
