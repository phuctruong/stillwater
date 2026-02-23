"""
Execution Twin — Phase 3 of the SW5.0 Small Talk Twin.

Maps wish IDs (from Phase 2 Intent Twin) to concrete execution plans
(swarm agent + skill recipe) using a deterministic CPU lookup engine.

Architecture:
  wish_id → O(1) combo lookup → {swarm, recipe} → ExecutionMatch

Key classes:
  ExecutionCPU   — CPU matcher (< 1ms P99 hot path, O(1) dict lookup)
  ComboDB        — Database loader (combos.jsonl + learned_combos.jsonl)
  Combo          — wish_id → {swarm, recipe} mapping
  ExecutionMatch — Result of a CPU or LLM match

Quick start:
  from admin.orchestration.execute import ExecutionCPU, ComboDB

  db = ComboDB()
  cpu = ExecutionCPU(combo_db=db)
  match = cpu.match("oauth-integration")
  # match.swarm == "coder"
  # match.recipe == ["prime-safety", "prime-coder", "oauth3-enforcer"]

Pipeline (Phase 1 → 2 → 3):
  prompt → SmallTalkCPU (Phase 1) → IntentCPU (Phase 2) → ExecutionCPU (Phase 3)
  Each phase < 1ms. Total < 3ms on hot path.

rung_target: 641 (deterministic, testable, offline-first)
"""

from .cpu import ExecutionCPU
from .database import ComboDB, ComboLookupLog
from .models import Combo, ComboDatabase, ComboLookupEntry, ExecutionMatch, LearnedCombo

__all__ = [
    "ExecutionCPU",
    "ComboDB",
    "ComboLookupLog",
    "Combo",
    "ComboDatabase",
    "ComboLookupEntry",
    "ExecutionMatch",
    "LearnedCombo",
]
