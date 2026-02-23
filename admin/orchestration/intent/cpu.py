"""
IntentCPU — CPU-side intent matcher for the Intent Twin (Phase 2).

Architecture (from SMALLTALK_TWIN_BRAINSTORM.md Phase 2):

  User prompt
    |
    v
  1. Token extraction (deterministic, no ML, < 0.1ms)
     Lowercase + split + strip punctuation + deduplicate
    |
    v
  2. Keyword-to-wish lookup (in-memory index, < 0.5ms)
     For each extracted token:
       → query WishDatabase._keyword_index[token]
       → collect candidate wish ids + matched keyword lists
    |
    v
  3. Score + rank (< 0.1ms)
     score(wish) = (matched_keywords / total_wish_keywords) * wish.confidence
     Return highest-scoring wish as IntentMatch
     Falls back to None if no keywords found
    |
    v
  IntentMatch(wish_id, matched_keywords, confidence, source="cpu")

No network. No ML. No randomness. All deterministic.
Compiled regex patterns loaded at module import time — zero latency on hot path.

rung_target: 641 (deterministic, testable, offline-first)
"""

from __future__ import annotations

import re
import time
from typing import Dict, List, Optional, Tuple

from .database import LookupLog, WishDB
from .models import IntentMatch, LookupEntry


# ---------------------------------------------------------------------------
# Pre-compiled token extraction patterns (module-level — zero hot-path cost)
# ---------------------------------------------------------------------------

# Strip leading/trailing punctuation from tokens
_PUNCT_STRIP = re.compile(r"^[^\w]+|[^\w]+$")

# Split on whitespace and common delimiters
_SPLIT_PATTERN = re.compile(r"[\s/\-_,.;:!?()[\]{}\"'`<>|@#$%^&*+=~]+")

# Tokens to skip (stop words + very short tokens)
_STOP_WORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "to", "of", "in", "on", "at", "by", "for", "with", "about", "against",
    "between", "into", "through", "during", "before", "after", "above",
    "below", "from", "up", "down", "out", "off", "over", "under",
    "again", "then", "once", "and", "but", "or", "nor", "so", "yet",
    "both", "either", "neither", "not", "only", "own", "same", "than",
    "too", "very", "just", "i", "me", "my", "we", "our", "you", "your",
    "he", "his", "she", "her", "it", "its", "they", "their", "them",
    "what", "which", "who", "this", "that", "these", "those",
    "am", "im", "also", "how", "when", "where", "why", "all",
    "each", "few", "more", "most", "other", "some", "such", "no",
    "like", "well", "want", "need", "help", "make", "get", "set",
    "use", "using", "used", "can", "please", "hi", "hey", "ok", "okay",
})

# Minimum token length to consider
_MIN_TOKEN_LEN = 3


# ---------------------------------------------------------------------------
# IntentCPU
# ---------------------------------------------------------------------------

class IntentCPU:
    """
    CPU-side intent matcher.

    Instantiate once with a loaded WishDB.
    Call match() on every user prompt.

    Hot path budget: < 1ms total (token extraction + keyword lookup + scoring).

    Thread-safe (read-only access to WishDB after init).
    """

    def __init__(
        self,
        wish_db: WishDB,
        lookup_log: Optional[LookupLog] = None,
    ) -> None:
        """
        Args:
            wish_db:    Loaded WishDB (must be pre-loaded before calling match()).
            lookup_log: Optional log for CPU match events (for LLM feedback).
        """
        self._db = wish_db
        self._log = lookup_log

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def match(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        session_id: str = "",
    ) -> Optional[IntentMatch]:
        """
        Match a prompt to the best wish.

        Args:
            prompt:     User's input text.
            context:    Optional dict with extra hints, e.g. {"project": "oauth"}.
            session_id: Session identifier (for lookup log).

        Returns:
            IntentMatch if a wish was found, None otherwise.
        """
        context = context or {}
        t_start = time.perf_counter()

        # Step 1: Extract tokens
        tokens = self.extract_tokens(prompt)

        # Augment with context hints (project name, explicit tags)
        context_tokens = self._extract_context_tokens(context)
        all_tokens = list(dict.fromkeys(tokens + context_tokens))  # dedupe, preserve order

        # Step 2: Lookup candidates
        candidates = self._lookup_candidates(all_tokens)

        # Step 3: Score and pick best
        best = self._score_best(candidates, all_tokens)

        latency_ms = (time.perf_counter() - t_start) * 1000

        # Log event (for LLM feedback loop)
        if self._log is not None:
            log_entry = LookupEntry(
                prompt=prompt,
                prompt_tokens=all_tokens,
                cpu_match=best[0] if best else None,
                cpu_confidence=best[1] if best else 0.0,
                session_id=session_id,
            )
            self._log.record(log_entry)

        if best is None:
            return None

        wish_id, confidence, matched_keywords = best
        return IntentMatch(
            wish_id=wish_id,
            matched_keywords=matched_keywords,
            confidence=confidence,
            source="cpu",
            latency_ms=latency_ms,
            prompt_tokens=all_tokens,
        )

    def extract_tokens(self, text: str) -> List[str]:
        """
        Extract meaningful tokens from prompt text.

        Deterministic:
          1. Lowercase
          2. Split on whitespace + delimiters
          3. Strip leading/trailing punctuation per token
          4. Filter stop words and short tokens
          5. Deduplicate (preserve first occurrence order)

        No randomness. No ML.
        """
        text_lower = text.lower()
        raw_tokens = _SPLIT_PATTERN.split(text_lower)

        seen: Dict[str, bool] = {}
        result: List[str] = []
        for tok in raw_tokens:
            tok = _PUNCT_STRIP.sub("", tok)
            if len(tok) < _MIN_TOKEN_LEN:
                continue
            if tok in _STOP_WORDS:
                continue
            if tok not in seen:
                seen[tok] = True
                result.append(tok)

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_context_tokens(self, context: Dict) -> List[str]:
        """
        Extract additional tokens from context dict.

        Recognizes:
          context["project"]  → split + tokenize project name
          context["tags"]     → use as-is (already tokenized)
          context["keywords"] → use as-is
        """
        extra: List[str] = []

        project = context.get("project", "")
        if project:
            extra.extend(self.extract_tokens(project))

        tags = context.get("tags", [])
        if isinstance(tags, list):
            for tag in tags:
                extra.extend(self.extract_tokens(str(tag)))

        keywords = context.get("keywords", [])
        if isinstance(keywords, list):
            for kw in keywords:
                tok = str(kw).lower().strip()
                if tok and len(tok) >= _MIN_TOKEN_LEN:
                    extra.append(tok)

        return extra

    def _lookup_candidates(
        self,
        tokens: List[str],
    ) -> Dict[str, Tuple[float, List[str]]]:
        """
        For each token, look up matching wishes and accumulate matched keywords.

        Returns:
            dict of wish_id → (wish.confidence, [matched_keywords])

        Deterministic: iterates tokens in extraction order.
        """
        candidates: Dict[str, Tuple[float, List[str]]] = {}

        for token in tokens:
            wishes = self._db.lookup_by_keyword(token)
            for wish in wishes:
                if wish.id not in candidates:
                    candidates[wish.id] = (wish.confidence, [])
                _, matched = candidates[wish.id]
                if token not in matched:
                    matched.append(token)

        return candidates

    def _score_best(
        self,
        candidates: Dict[str, Tuple[float, List[str]]],
        all_tokens: List[str],
    ) -> Optional[Tuple[str, float, List[str]]]:
        """
        Score candidates and return the best match.

        Scoring formula:
            overlap_ratio = len(matched_keywords) / len(wish.keywords)
            score = overlap_ratio * wish.confidence

        Tie-breaking:
            1. Higher score first
            2. Among equal scores: wish with more total keywords first (broader match)
            3. Among still-equal: alphabetical wish id (deterministic)

        Returns None if candidates is empty.
        """
        if not candidates:
            return None

        scored: List[Tuple[float, str, List[str]]] = []
        for wish_id, (base_confidence, matched) in candidates.items():
            wish = self._db.get(wish_id)
            if wish is None:
                continue
            total_keywords = len(wish.keywords)
            if total_keywords == 0:
                continue
            overlap_ratio = len(matched) / total_keywords
            score = overlap_ratio * base_confidence
            scored.append((score, wish_id, matched))

        if not scored:
            return None

        # Sort: score DESC, total_keywords DESC (proxy: wish_id for stable tie-break)
        scored.sort(
            key=lambda t: (
                -t[0],                    # score descending
                -len(t[2]),               # matched count descending
                t[1],                     # wish_id ascending (stable)
            )
        )

        best_score, best_id, best_matched = scored[0]
        return (best_id, best_score, best_matched)
