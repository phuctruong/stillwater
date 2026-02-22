# CLI Triple-Twin Architecture

**Purpose:** Shows the full triple-twin CLI architecture where user input is forked into three parallel paths — a CPU Twin (Layer 1) for sub-300ms warm responses, an Intent Twin (Layer 2) for wish-matching and classification within 300ms-1s, and an LLM Twin (Layer 3) for full substantive execution — merged by a rule-based Merge Layer with prime-safety override authority.
**Inputs:** Raw user input text, session context, relationship level, task complexity classification, wish backlog
**Outputs:** Merged CLI response compositing warm acknowledgment (CPU Twin), intent confirmation (Intent Twin), and substantive answer (LLM Twin)
**Latency:** CPU Twin < 300ms; Intent Twin 300ms-1s; LLM Twin 1–5s; Merge Layer < 50ms; User-perceived < 500ms for simple tasks

---

```mermaid
flowchart TD
    USER([User Input]) --> INTAKE[Input Intake\nparse + classify]
    INTAKE --> SAFETY_GATE{prime-safety\ngate}
    SAFETY_GATE -->|BLOCKED| SAFETY_HALT[Safety Halt\nemit redaction notice]
    SAFETY_GATE -->|PASS| FORK[Fork Dispatcher\nlaunch parallel twins]

    FORK --> CPU_TWIN
    FORK --> INTENT_TWIN
    FORK --> LLM_TWIN

    subgraph CPU_TWIN["CPU Twin — Layer 1 (< 300ms)"]
        direction TB
        CT_RECV[Receive task snapshot] --> CT_MIRROR[eq-mirror\nregister detect\ncasual / formal / energy]
        CT_MIRROR --> CT_LOOKUP[eq-smalltalk-db\nlookup by context tags]
        CT_LOOKUP --> CT_PROACTIVE[Proactive prompt check\nmeetings / queue / feedback]
        CT_PROACTIVE --> CT_SAFETY{prime-safety\nsuppress check}
        CT_SAFETY -->|SUPPRESS| CT_NULL[Emit: null token\nno warm response]
        CT_SAFETY -->|OK| CT_FORMAT[Format warm response\ninject user name + project]
        CT_FORMAT --> CT_EMIT[Emit CPU token\n< 300ms]
    end

    subgraph INTENT_TWIN["Intent Twin — Layer 2 (300ms–1s)"]
        direction TB
        IT_RECV[Receive task snapshot] --> IT_PARSE[Parse intent categories\ntask / question / wish / chat]
        IT_PARSE --> IT_WISH[prime-wishes\nwish decomposition match]
        IT_WISH --> IT_SKILL[Identify skill/recipe/combo/swarm\nneeded for this intent]
        IT_SKILL --> IT_CLASSIFY[Haiku-class LLM\nintent classification]
        IT_CLASSIFY --> IT_CONFIRM[eq-mirror confirm\nintent back to user]
        IT_CONFIRM --> IT_EMIT[Emit Intent token\ntask_type + skill_pack + complexity\n300ms–1s]
    end

    subgraph LLM_TWIN["LLM Twin — Layer 3 (1–5s)"]
        direction TB
        LT_RECV[Receive full task +\nIntent Twin output] --> LT_ORCH[phuc-orchestration\ndispatch decision]
        LT_ORCH --> LT_SKILL[Skill pack load\nprime-safety first]
        LT_SKILL --> LT_CLASSIFY{Task type?}
        LT_CLASSIFY -->|Trivial < 50 lines| LT_INLINE[Inline execution]
        LT_CLASSIFY -->|Coder domain| LT_CODER[Dispatch: Coder agent\nsonnet + prime-coder]
        LT_CLASSIFY -->|Math / proof| LT_MATH[Dispatch: Mathematician\nopus + prime-math]
        LT_CLASSIFY -->|Planning / risk| LT_PLAN[Dispatch: Planner agent\nsonnet + phuc-forecast]
        LT_INLINE --> LT_EXEC[Task execution\nmodel inference]
        LT_CODER --> LT_EXEC
        LT_MATH --> LT_EXEC
        LT_PLAN --> LT_EXEC
        LT_EXEC --> LT_EVIDENCE[Evidence format\ntests.json + artifacts]
        LT_EVIDENCE --> LT_EMIT[Emit LLM token\n1–5s]
    end

    subgraph MERGE["Merge Layer (< 50ms)"]
        direction TB
        ML_RECV_CPU[Receive CPU token] --> ML_ARBITER{Task complexity\narbiter}
        ML_RECV_INTENT[Receive Intent token] --> ML_ARBITER
        ML_RECV_LLM[Receive LLM token] --> ML_ARBITER
        ML_ARBITER -->|Simple task| ML_PREFIX[Prefix merge\nCPU warm + Intent confirm + LLM answer]
        ML_ARBITER -->|Complex task| ML_BRIDGE[Bridge fill\nCPU opens + Intent routes + LLM continues]
        ML_ARBITER -->|Layer 1+2 sufficient| ML_LIGHT[Light merge\nCPU + Intent only\nno LLM needed]
        ML_ARBITER -->|CPU suppressed| ML_LLM_ONLY[LLM + Intent only\nno warm prefix]
        ML_PREFIX --> ML_EMIT[Emit merged response]
        ML_BRIDGE --> ML_EMIT
        ML_LIGHT --> ML_EMIT
        ML_LLM_ONLY --> ML_EMIT
    end

    CT_EMIT --> MERGE
    IT_EMIT --> MERGE
    LT_EMIT --> MERGE
    CT_NULL --> MERGE
    ML_EMIT --> OUTPUT([Response to User])

    SAFETY_HALT --> OUTPUT

    classDef cpu fill:#4CAF50,color:#fff,stroke:#388E3C
    classDef intent fill:#00BCD4,color:#fff,stroke:#006064
    classDef llm fill:#2196F3,color:#fff,stroke:#1565C0
    classDef safety fill:#f44336,color:#fff,stroke:#b71c1c
    classDef merge fill:#FF9800,color:#fff,stroke:#E65100
    classDef io fill:#9C27B0,color:#fff,stroke:#6A1B9A

    class CT_RECV,CT_MIRROR,CT_LOOKUP,CT_PROACTIVE,CT_FORMAT,CT_EMIT,CT_NULL cpu
    class IT_RECV,IT_PARSE,IT_WISH,IT_SKILL,IT_CLASSIFY,IT_CONFIRM,IT_EMIT intent
    class LT_RECV,LT_ORCH,LT_SKILL,LT_CLASSIFY,LT_INLINE,LT_CODER,LT_MATH,LT_PLAN,LT_EXEC,LT_EVIDENCE,LT_EMIT llm
    class SAFETY_GATE,CT_SAFETY,SAFETY_HALT safety
    class ML_RECV_CPU,ML_RECV_INTENT,ML_RECV_LLM,ML_ARBITER,ML_PREFIX,ML_BRIDGE,ML_LIGHT,ML_LLM_ONLY,ML_EMIT merge
    class USER,OUTPUT,INTAKE,FORK io
```

## Notes

- The three twins execute in **true parallel** after the fork dispatcher fires. No twin blocks any other.
- `prime-safety` has two interception points: (1) at the global SAFETY_GATE before any fork, and (2) inside the CPU Twin at the suppress check. The global gate halts all three twins; the inner check suppresses only the warm response without stopping the Intent or LLM Twin.
- **Layer 2 (Intent Twin) is the key new layer** that separates the triple-twin from the double-twin. It handles intent classification and wish decomposition before the full LLM execution is needed, using a lightweight haiku-class model call. For simple conversational tasks, the response from Layer 1 + Layer 2 is sufficient — Layer 3 is not invoked.
- The Merge Layer uses a rule-based arbiter — no LLM inference occurs here. Rules are: task complexity score (from INTAKE classifier), whether CPU token is null, whether Intent Twin identified the task as fully handled by Layer 1+2, and whether the CPU warm text is redundant with the LLM answer opening.
- **Bridge fill mode**: the CPU Twin emits a partial opening sentence and the LLM Twin fills in the rest, giving the user a visible start within 300ms even for long tasks. The Intent Twin's confirmation is composited in between.
- **Light merge mode** (new in triple-twin): when the Intent Twin classifies the task as a simple wish match or recipe replay, the Merge Layer composes the CPU warm response plus the Intent confirmation only. The LLM Twin's output is either not awaited or used only as a background artifact.
- Evidence bundles (tests.json, artifacts) are only emitted by the LLM Twin path; CPU Twin and Intent Twin output are never treated as Lane A evidence.
- The Intent Twin's `task_type + skill_pack_needed + complexity_estimate` output is forwarded to the LLM Twin, allowing the LLM Twin to skip the full classification step and load the skill pack directly — reducing LLM Twin latency by approximately 100ms on the hot path.
