"""cpu_learner.py — Production CPU learning engine for the Triple-Twin pipeline.

Extracts keywords and patterns from LLM reasoning, stores them locally,
and builds a CPU-side knowledge base that grows more confident with
repeated observations.  Over time, the CPU learner handles more requests
without needing to call the LLM validator, reducing latency and cost.

Design:
  - Confidence follows a logistic curve: more observations = higher confidence.
  - Phase-specific thresholds (phase1=0.70, phase2=0.80, phase3=0.90)
    ensure progressively stricter gates for more impactful decisions.
  - Serialization uses JSONL (one JSON object per line) for append-friendly
    persistence compatible with DataRegistry.

stdlib only: json, os, random, re, collections, typing.
"""

from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from typing import Optional


# Minimum frequency before a pattern is considered "learned"
MIN_FREQUENCY_FOR_CONFIDENCE = 2

# Confidence threshold per phase — stricter for later phases
CONFIDENCE_THRESHOLD = {
    "phase1": 0.70,
    "phase2": 0.80,
    "phase3": 0.90,
}


class CPULearner:
    """Extracts patterns from LLM responses and builds a CPU-side knowledge base.

    Confidence grows as a pattern is seen more frequently, following a logistic
    curve.  When confidence exceeds the phase threshold, the CPU learner can
    handle the input without calling the LLM.

    Parameters
    ----------
    phase:
        One of ``"phase1"``, ``"phase2"``, ``"phase3"``.
    """

    def __init__(self, phase: str) -> None:
        if phase not in CONFIDENCE_THRESHOLD:
            raise ValueError(f"Unknown phase: {phase!r} — expected one of {sorted(CONFIDENCE_THRESHOLD)}")
        self.phase = phase
        self.threshold = CONFIDENCE_THRESHOLD[phase]

        # pattern_key -> {"count": int, "label": str, "examples": list}
        self._patterns: dict = defaultdict(lambda: {"count": 0, "label": None, "examples": []})

        # Cache: pattern_key -> confidence float (recomputed on update)
        self._confidence_cache: dict = {}

        # Total learning events
        self.total_learned = 0

    # ------------------------------------------------------------------
    # Keyword extraction
    # ------------------------------------------------------------------

    @staticmethod
    def extract_keywords(text: str) -> list:
        """Extract meaningful keywords from a text string.

        Strips stop words, lowercases, splits on non-alpha characters,
        deduplicates while preserving order.
        """
        stop_words = {
            "a", "an", "the", "is", "it", "in", "on", "at", "to", "for",
            "of", "and", "or", "but", "not", "with", "by", "from", "as",
            "i", "you", "we", "they", "he", "she", "this", "that", "be",
            "are", "was", "were", "has", "have", "had", "do", "does", "did",
            "will", "would", "can", "could", "should", "may", "might",
            "me", "my", "your", "our", "their", "its", "if", "so",
            "all", "any", "some", "no", "yes", "just", "like", "about",
            "what", "how", "when", "where", "why", "who", "which",
            "there", "here", "up", "out", "into", "then", "than",
            "now", "also", "very", "more", "most", "really", "please",
            "im", "ive", "dont", "cant", "wont", "isnt", "wasnt",
        }

        # Lowercase + split on non-alpha characters
        words = re.findall(r"[a-z]+", text.lower())

        # Filter stop words and very short words
        keywords = [w for w in words if w not in stop_words and len(w) >= 3]

        # Deduplicate while preserving order
        seen: set = set()
        unique: list = []
        for w in keywords:
            if w not in seen:
                seen.add(w)
                unique.append(w)

        return unique

    # ------------------------------------------------------------------
    # Pattern learning
    # ------------------------------------------------------------------

    def learn(self, input_text: str, label: str, reasoning: str = "") -> list:
        """Learn from an LLM validation result.

        Parameters
        ----------
        input_text:
            The original user input.
        label:
            The LLM's classification/decision.
        reasoning:
            Optional LLM reasoning string (extra signal for keyword extraction).

        Returns
        -------
        list
            Keywords that were learned or reinforced.
        """
        # Extract keywords from input + reasoning
        keywords = self.extract_keywords(input_text)
        if reasoning:
            keywords += self.extract_keywords(reasoning)

        # Deduplicate
        keywords = list(dict.fromkeys(keywords))

        learned = []
        for kw in keywords:
            entry = self._patterns[kw]
            entry["count"] += 1
            entry["label"] = label  # last label wins (LLM decision)
            if len(entry["examples"]) < 5:
                entry["examples"].append(input_text[:80])

            # Invalidate cache
            self._confidence_cache.pop(kw, None)
            learned.append(kw)

        self.total_learned += 1
        return learned

    # ------------------------------------------------------------------
    # Confidence scoring
    # ------------------------------------------------------------------

    def _label_priority(self, label: Optional[str]) -> int:
        """Return tie-break priority for labels.

        For phase1 (small-talk triage), task intent wins ties so mixed
        messages like "hello fix bug" route to execution instead of chatter.
        """
        if not label:
            return 0
        if self.phase == "phase1":
            if label == "task":
                return 100
            if label == "question":
                return 50
        return 10

    def confidence(self, keyword: str) -> float:
        """Return confidence score for a keyword in [0.0, 1.0].

        Based on frequency using a logistic-inspired curve::

            confidence = 1 - 1 / (1 + 0.3 * count)

        Approximate values: count=0 -> 0.0, count=1 -> 0.23,
        count=2 -> 0.375, count=5 -> 0.60, count=10 -> 0.75,
        count=20 -> 0.857.
        """
        if keyword not in self._patterns:
            return 0.0

        if keyword in self._confidence_cache:
            return self._confidence_cache[keyword]

        count = self._patterns[keyword]["count"]
        # Logistic-inspired: confidence = 1 - 1/(1 + 0.3 * count)
        conf = 1.0 - 1.0 / (1.0 + 0.3 * count)
        self._confidence_cache[keyword] = conf
        return conf

    def predict(self, text: str) -> tuple:
        """Try to predict the label from learned patterns.

        Returns
        -------
        tuple[str | None, float, list[str]]
            ``(label, confidence, matched_keywords)`` where label is ``None``
            if no pattern was found, confidence is the max confidence among
            matched keywords, and matched_keywords lists the keywords that
            contributed.
        """
        keywords = self.extract_keywords(text)

        best_label = None
        best_conf = 0.0
        best_priority = -1
        matched = []

        for kw in keywords:
            if kw not in self._patterns:
                continue
            conf = self.confidence(kw)
            label = self._patterns[kw]["label"]
            priority = self._label_priority(label)
            if conf > best_conf:
                best_conf = conf
                best_label = label
                best_priority = priority
                matched = [kw]
            elif abs(conf - best_conf) < 1e-12 and best_label is not None:
                if priority > best_priority:
                    best_label = label
                    best_priority = priority
                    matched = [kw]
                else:
                    matched.append(kw)

        return best_label, best_conf, matched

    def can_handle(self, text: str) -> bool:
        """Return True if the CPU learner is confident enough to handle this input."""
        _, conf, _ = self.predict(text)
        return conf >= self.threshold

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_jsonl_records(self) -> list:
        """Convert learned patterns to a list of JSONL-compatible records."""
        records = []
        for kw, entry in self._patterns.items():
            records.append({
                "keyword": kw,
                "label": entry["label"],
                "count": entry["count"],
                "confidence": round(self.confidence(kw), 4),
                "examples": entry["examples"],
                "phase": self.phase,
            })
        # Sort by confidence descending
        records.sort(key=lambda r: r["confidence"], reverse=True)
        return records

    def save(self, filepath: str) -> None:
        """Save learned patterns to a JSONL file."""
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        records = self.to_jsonl_records()
        with open(filepath, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")

    def load(self, filepath: str) -> None:
        """Load learned patterns from a JSONL file.

        If the file does not exist, this is a no-op (cold start).
        """
        if not os.path.exists(filepath):
            return
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                kw = record["keyword"]
                self._patterns[kw] = {
                    "count": record["count"],
                    "label": record["label"],
                    "examples": record.get("examples", []),
                }
        # Clear confidence cache after loading
        self._confidence_cache.clear()

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def stats(self) -> dict:
        """Return statistics about the learned patterns."""
        if not self._patterns:
            return {
                "total_patterns": 0,
                "total_learning_events": self.total_learned,
                "high_confidence_patterns": 0,
                "avg_confidence": 0.0,
                "top_patterns": [],
            }

        confidences = [self.confidence(kw) for kw in self._patterns]
        high_conf = sum(1 for c in confidences if c >= self.threshold)
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        # Top 5 patterns by confidence
        top = sorted(
            [(kw, self.confidence(kw), self._patterns[kw]["label"])
             for kw in self._patterns],
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        return {
            "total_patterns": len(self._patterns),
            "total_learning_events": self.total_learned,
            "high_confidence_patterns": high_conf,
            "avg_confidence": round(avg_conf, 4),
            "top_patterns": [
                {"keyword": t[0], "confidence": round(t[1], 4), "label": t[2]}
                for t in top
            ],
        }
