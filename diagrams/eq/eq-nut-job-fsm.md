# EQ NUT Job FSM

**Purpose:** Detailed state machine for the NUT Job (Name → Understand → Transform) emotional processing protocol, showing all legal transitions, loop-back conditions, resolution paths, and forbidden states that must never be entered.
**Inputs:** emotional_signal from eq-core, session context, relationship level, prior rapport score
**Outputs:** emotional_response_fragment + readiness_flag (READY / DEFERRED); updated emotional state log
**Latency:** Full happy path (NAME → UNDERSTAND → TRANSFORM → EXIT_RESOLVED): ~300ms; loop iterations add ~150ms each

---

```mermaid
stateDiagram-v2
    [*] --> INTAKE

    INTAKE : INTAKE\nReceive emotional_signal + context
    EMOTIONAL_STATE_DETECT : EMOTIONAL_STATE_DETECT\nClassify: emotion present?\nIntensity: low / mid / high\nType: fear / anger / grief / shame / joy
    NAME : NAME\nLabel the emotion explicitly\nNo judgment — pure description\n"It sounds like you're feeling ___"
    VALIDATE : VALIDATE\nCheck: is label accurate?\nNot projected onto user?\nUser signal confirms or corrects
    UNDERSTAND : UNDERSTAND\nProbe root cause\nAsk: what's beneath this?\nMap: Low Road vs High Road
    READINESS_CHECK : READINESS_CHECK\nAssess: High Road accessible?\nCheck: reactive state resolved?\nEvaluate: ready to transform?
    TRANSFORM : TRANSFORM\nReframe the situation\nOffer resource / next step\nApply High Road perspective
    VERIFY_RESOLUTION : VERIFY_RESOLUTION\nDid reframe land?\nEmotional signal reduced?\nUser acknowledged?
    SKIP_TO_TASK : SKIP_TO_TASK\nNo emotional content detected\nPass through to task execution\nNo NUT Job needed
    GROUNDING_HOLD : GROUNDING_HOLD\nUser still on Low Road after 2 loops\nEmit grounding statement\nDefer task — safety pause
    EXIT_RESOLVED : EXIT_RESOLVED\nEmotional load cleared\nReadiness flag = READY\nLog: resolution_quality score
    EXIT_DEFERRED : EXIT_DEFERRED\nTask deferred — user needs space\nReadiness flag = DEFERRED\nLog: deferred_timestamp

    INTAKE --> EMOTIONAL_STATE_DETECT
    EMOTIONAL_STATE_DETECT --> NAME : emotion detected\nintensity > threshold
    EMOTIONAL_STATE_DETECT --> SKIP_TO_TASK : no emotional content\nor intensity too low

    NAME --> VALIDATE
    VALIDATE --> UNDERSTAND : label confirmed\nor corrected and resubmitted
    VALIDATE --> NAME : label rejected by user\n(re-attempt with correction)

    UNDERSTAND --> READINESS_CHECK : root cause mapped\nHigh Road / Low Road assessed

    READINESS_CHECK --> TRANSFORM : High Road\nuser is ready
    READINESS_CHECK --> UNDERSTAND : Low Road\nstill reactive\n(loop — max 2x)
    READINESS_CHECK --> GROUNDING_HOLD : Low Road\nmax loops reached\n(iteration_count >= 2)

    TRANSFORM --> VERIFY_RESOLUTION

    VERIFY_RESOLUTION --> EXIT_RESOLVED : reframe landed\nemotion reduced\nuser acknowledged
    VERIFY_RESOLUTION --> NAME : new emotion surfaced\nduring transform\n(restart NUT cycle)

    GROUNDING_HOLD --> EXIT_DEFERRED

    SKIP_TO_TASK --> [*] : pass to task executor
    EXIT_RESOLVED --> [*]
    EXIT_DEFERRED --> [*]

    state FORBIDDEN_STATES {
        PREMATURE_TRANSFORM : PREMATURE_TRANSFORM\nTransform attempted\nbefore UNDERSTAND complete
        SKIP_NAME : SKIP_NAME\nEmotion detected but\nNAME step bypassed
        FAKE_VALIDATE : FAKE_VALIDATE\nVALIDATE step skipped\nor auto-confirmed without user signal
        LOOP_WITHOUT_COUNTER : LOOP_WITHOUT_COUNTER\nUnderstand loop iterates\nwithout tracking iteration_count
        TRANSFORM_ON_LOW_ROAD : TRANSFORM_ON_LOW_ROAD\nTRANSFORM entered while\nREADINESS_CHECK = Low Road
    }

    classDef forbidden fill:#f44336,color:#fff,stroke:#b71c1c,stroke-width:2px
    classDef exit fill:#4CAF50,color:#fff,stroke:#388E3C
    classDef warning fill:#FF9800,color:#fff,stroke:#E65100
    classDef normal fill:#2196F3,color:#fff,stroke:#1565C0

    class PREMATURE_TRANSFORM,SKIP_NAME,FAKE_VALIDATE,LOOP_WITHOUT_COUNTER,TRANSFORM_ON_LOW_ROAD forbidden
    class EXIT_RESOLVED,SKIP_TO_TASK exit
    class EXIT_DEFERRED,GROUNDING_HOLD warning
    class INTAKE,EMOTIONAL_STATE_DETECT,NAME,VALIDATE,UNDERSTAND,READINESS_CHECK,TRANSFORM,VERIFY_RESOLUTION normal
```

## Notes

- **Forbidden states are hard constraints** — any code path that reaches a forbidden state must immediately halt and emit a protocol violation log entry. These are not merely discouraged; they represent integrity failures.
- **PREMATURE_TRANSFORM**: The most common violation. Must never transform until UNDERSTAND has completed at least one full root-cause mapping.
- **SKIP_NAME**: Skipping the naming step leaves the emotion unlabeled, which makes VALIDATE and UNDERSTAND semantically undefined. The NUT Job without NAME is not NUT Job — it is projection.
- **FAKE_VALIDATE**: Auto-confirming the label without a user signal (e.g., "I'll assume I'm right") corrupts the entire downstream chain. VALIDATE requires at least one response token from the user path confirming or correcting the label.
- **LOOP_WITHOUT_COUNTER**: The UNDERSTAND → READINESS_CHECK → UNDERSTAND loop is bounded at 2 iterations. Without a counter, the FSM can spin indefinitely. The iteration_count field is mandatory state.
- **TRANSFORM_ON_LOW_ROAD**: Attempting to transform a user who is still in reactive (Low Road) state typically backfires — the reframe is rejected or causes escalation. The READINESS_CHECK gate exists precisely to prevent this.
- The "new emotion surfaced" transition from VERIFY_RESOLUTION back to NAME resets the NUT cycle with a fresh emotional signal. The iteration counter is also reset, since this is a genuinely new emotion.
- EXIT_DEFERRED does not mean the task is dropped. The task execution is queued and resumes after the user signals readiness (or at next session open).
