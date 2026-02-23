"""
Intent Twin — Phase 2 of the SW5.0 Small Talk Twin.

Matches user prompts to "wishes" (intent/task categories) using
a deterministic CPU keyword-lookup engine.

Architecture:
  prompt → extract_tokens() → keyword_index_lookup() → score_best() → IntentMatch

Key classes:
  IntentCPU   — CPU matcher (< 1ms P99 hot path)
  WishDB      — Database loader (wishes.jsonl + learned_wishes.jsonl)
  Wish        — Named intent category with keywords
  IntentMatch — Result of a CPU or LLM match

Quick start:
  from admin.orchestration.intent import IntentCPU, WishDB

  db = WishDB()
  cpu = IntentCPU(wish_db=db)
  match = cpu.match("help me implement oauth token refresh")
  # match.wish_id == "oauth-integration"

rung_target: 641 (deterministic, testable, offline-first)
"""

from .cpu import IntentCPU
from .database import LookupLog, WishDB
from .models import IntentMatch, LearnedWish, LookupEntry, Wish, WishDatabase

__all__ = [
    "IntentCPU",
    "WishDB",
    "LookupLog",
    "IntentMatch",
    "Wish",
    "WishDatabase",
    "LookupEntry",
    "LearnedWish",
]
