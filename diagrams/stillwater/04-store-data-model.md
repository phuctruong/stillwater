# Store Data Model

Pydantic models for the Stillwater Store API. All field names, types, and
constraints are taken directly from `store/models.py`.

```mermaid
classDiagram
    class SkillStatus {
        <<enum>>
        pending
        accepted
        rejected
    }

    class ContentType {
        <<enum>>
        skill
        recipe
        swarm
        prime_wiki
        prime_mermaid
        bugfix
    }

    class APIKey {
        +str key_id
        +str key_hash
        +str name
        +str account_type
        +str description
        +float reputation
        +datetime created_at
        +int submission_count
        +int accepted_count
        +int rejected_count
        +str status
        +List~str~ recent_submission_timestamps
        note: key_id = acct_uuid4hex
        note: key_hash = HMAC-SHA256 of raw key
        note: account_type = human or bot
        note: status = active or suspended
        note: reputation: +1.0 accept, -0.5 reject
    }

    class SkillSubmission {
        +str skill_name
        +str skill_content
        +str author
        +int rung_claimed
        +ContentType content_type
        +Optional~str~ description
        +List~str~ tags
        +Optional~str~ source_context
        validate rung_must_be_valid()
        validate name_must_be_kebab()
        note: skill_name min=3 max=128 kebab-case
        note: skill_content min=10
        note: author min=1 max=128
        note: rung_claimed must be 641 or 274177 or 65537
        note: description max=512
        note: source_context max=1024
    }

    class ReviewRecord {
        +str skill_id
        +str skill_name
        +ContentType content_type
        +str author
        +str key_id
        +int rung_claimed
        +Optional~int~ rung_verified
        +SkillStatus status
        +str skill_content
        +str description
        +List~str~ tags
        +str source_context
        +datetime submitted_at
        +Optional~datetime~ reviewed_at
        +Optional~str~ review_notes
        +Optional~str~ behavior_hash
        note: skill_id = uuid4
        note: rung_verified set by rung_validator.py
        note: behavior_hash set by rung_validator.py
        note: default status = pending
    }

    class SkillListing {
        +str skill_id
        +str skill_name
        +ContentType content_type
        +str author
        +int rung_claimed
        +Optional~int~ rung_verified
        +str description
        +List~str~ tags
        +datetime submitted_at
        +Optional~datetime~ reviewed_at
        +Optional~str~ review_notes
        +Optional~str~ behavior_hash
        +Optional~str~ skill_content
        note: skill_content only in single-skill GET
        note: public-facing read model
    }

    class InstallRequest {
        +str skill_id
        +str target_repo
        +bool dry_run
        note: target_repo = abs path or git URL
        note: dry_run default True
    }

    class InstallResult {
        +str skill_id
        +str skill_name
        +str target_repo
        +bool dry_run
        +bool installed
        +str message
    }

    class PaginatedSkillList {
        +int total
        +int page
        +int per_page
        +List~SkillListing~ skills
        note: response for GET /store/skills
    }

    ReviewRecord --> SkillStatus : status
    ReviewRecord --> ContentType : content_type
    SkillSubmission --> ContentType : content_type
    SkillListing --> ContentType : content_type
    ReviewRecord "1" --> "1" APIKey : submitted by key_id
    PaginatedSkillList "1" *-- "many" SkillListing : contains
    InstallRequest --> SkillListing : references skill_id
    InstallRequest --> InstallResult : produces
```

## Validator Constraints

```mermaid
flowchart LR
    classDef gate fill:#b58c1a,color:#fff,stroke:#806000
    classDef ok fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    classDef fail fill:#7a2d2d,color:#fff,stroke:#5c1a1a

    SUBMIT["SkillSubmission\ninput payload"]

    SUBMIT --> V_RUNG["rung_must_be_valid()\nv in {641, 274177, 65537}"]
    SUBMIT --> V_NAME["name_must_be_kebab()\nregex: ^[a-z0-9][a-z0-9-]*[a-z0-9]$"]
    SUBMIT --> V_LEN["Field lengths\nskill_name: 3-128\nskill_content: min 10\nauthor: 1-128\ndescription: max 512\nsource_context: max 1024"]

    V_RUNG -->|"valid"| PASS["Pydantic validation OK\n-> ReviewRecord created"]
    V_RUNG -->|"invalid"| FAIL["ValueError\n422 Unprocessable Entity"]
    V_NAME -->|"valid"| PASS
    V_NAME -->|"invalid"| FAIL
    V_LEN -->|"valid"| PASS
    V_LEN -->|"invalid"| FAIL

    class V_RUNG,V_NAME,V_LEN gate
    class PASS ok
    class FAIL fail
```

## Source Files

- `store/models.py` — all Pydantic model definitions (lines 1-197)

## Coverage

- All 8 Pydantic models: `APIKey`, `SkillSubmission`, `ReviewRecord`, `SkillListing`, `InstallRequest`, `InstallResult`, `PaginatedSkillList`, plus both enums
- All field names, types, and doc-comment constraints taken from actual source
- Relationships: `ReviewRecord` references `APIKey.key_id`; `PaginatedSkillList` aggregates `SkillListing`
- Validators: `rung_must_be_valid` (set `{641, 274177, 65537}`), `name_must_be_kebab` (regex)
- Field-length constraints from `Field(min_length=..., max_length=...)`
