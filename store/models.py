"""
store/models.py — Pydantic models for the Stillwater Store API.

Models:
  - APIKey           — registered developer API key record
  - SkillSubmission  — incoming submission payload (POST /store/submit)
  - SkillListing     — accepted skill as returned by GET /store/skills
  - ReviewRecord     — full review record (pending|accepted|rejected)
  - InstallRequest   — payload for POST /store/install

Rung target: 641
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ============================================================
# Enums
# ============================================================

class SkillStatus(str, Enum):
    pending  = "pending"
    accepted = "accepted"
    rejected = "rejected"


class ContentType(str, Enum):
    skill        = "skill"
    recipe       = "recipe"
    swarm        = "swarm"
    prime_wiki   = "prime-wiki"
    prime_mermaid = "prime-mermaid"
    bugfix       = "bugfix"


# ============================================================
# API Key model
# ============================================================

class APIKey(BaseModel):
    """A registered Stillwater Store developer API key."""

    key_id:         str                # acct_<hex>
    key_hash:       str                # HMAC-SHA256 of the raw key (stored; raw never stored)
    name:           str                # account name (3–64 chars)
    account_type:   str = "human"      # "human" | "bot"
    description:    str = ""
    reputation:     float = 0.0        # +1 accept, -0.5 reject
    created_at:     datetime
    submission_count: int = 0
    accepted_count:   int = 0
    rejected_count:   int = 0
    status:         str = "active"     # "active" | "suspended"

    # Rate-limit state: list of ISO timestamps of submissions in last 24h
    recent_submission_timestamps: List[str] = Field(default_factory=list)


# ============================================================
# Submission model
# ============================================================

class SkillSubmission(BaseModel):
    """
    Payload for POST /store/submit.

    Required fields:
      skill_name     — unique kebab-case name
      skill_content  — full text content of the skill
      author         — display name / account name
      rung_claimed   — 641 | 274177 | 65537
      content_type   — one of the 6 accepted content types
    """

    skill_name:    str = Field(..., min_length=3, max_length=128)
    skill_content: str = Field(..., min_length=10)
    author:        str = Field(..., min_length=1, max_length=128)
    rung_claimed:  int = Field(..., description="Must be 641, 274177, or 65537")
    content_type:  ContentType = ContentType.skill
    description:   Optional[str] = Field(default="", max_length=512)
    tags:          List[str] = Field(default_factory=list)
    source_context: Optional[str] = Field(default="", max_length=1024)

    @field_validator("rung_claimed")
    @classmethod
    def rung_must_be_valid(cls, v: int) -> int:
        valid_rungs = {641, 274177, 65537}
        if v not in valid_rungs:
            raise ValueError(f"rung_claimed must be one of {sorted(valid_rungs)}, got {v}")
        return v

    @field_validator("skill_name")
    @classmethod
    def name_must_be_kebab(cls, v: str) -> str:
        import re
        if not re.match(r'^[a-z0-9][a-z0-9\-]*[a-z0-9]$', v) and len(v) >= 2:
            raise ValueError(
                f"skill_name must be kebab-case (lowercase, hyphens only), got '{v}'"
            )
        return v


# ============================================================
# Review record model (internal + API)
# ============================================================

class ReviewRecord(BaseModel):
    """
    Full review record stored in the DB for each submission.
    Returned by review.py CLI tool.
    """

    skill_id:       str                    # uuid4
    skill_name:     str
    content_type:   ContentType
    author:         str
    key_id:         str                    # which API key submitted this
    rung_claimed:   int
    rung_verified:  Optional[int] = None   # set after rung_validator.py runs
    status:         SkillStatus = SkillStatus.pending
    skill_content:  str
    description:    str = ""
    tags:           List[str] = Field(default_factory=list)
    source_context: str = ""
    submitted_at:   datetime
    reviewed_at:    Optional[datetime] = None
    review_notes:   Optional[str] = None
    behavior_hash:  Optional[str] = None   # set by rung_validator


# ============================================================
# Public listing model
# ============================================================

class SkillListing(BaseModel):
    """
    Public-facing skill entry returned by GET /store/skills and
    GET /store/skills/{skill_id}.
    """

    skill_id:      str
    skill_name:    str
    content_type:  ContentType
    author:        str
    rung_claimed:  int
    rung_verified: Optional[int]
    description:   str
    tags:          List[str]
    submitted_at:  datetime
    reviewed_at:   Optional[datetime]
    review_notes:  Optional[str]
    behavior_hash: Optional[str]
    # Full content only when fetching single skill
    skill_content: Optional[str] = None


# ============================================================
# Install request model
# ============================================================

class InstallRequest(BaseModel):
    """Payload for POST /store/install (stub v1)."""

    skill_id:    str = Field(..., min_length=1)
    target_repo: str = Field(..., min_length=1,
                             description="Absolute path or git remote URL of target repo")
    dry_run:     bool = True


class InstallResult(BaseModel):
    """Result of POST /store/install."""

    skill_id:    str
    skill_name:  str
    target_repo: str
    dry_run:     bool
    installed:   bool
    message:     str


# ============================================================
# Paginated list response
# ============================================================

class PaginatedSkillList(BaseModel):
    """Response schema for GET /store/skills."""

    total:    int
    page:     int
    per_page: int
    skills:   List[SkillListing]
