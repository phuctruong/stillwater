"""CPU-first routing for email triage."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Callable, Mapping, MutableMapping


_KEYWORDS: dict[str, tuple[str, ...]] = {
    "urgent": ("urgent", "critical", "asap", "deadline", "immediately"),
    "work": ("meeting", "standup", "deploy", "incident", "oncall", "review"),
    "promo": ("newsletter", "sale", "offer", "discount", "deal", "promo"),
    "spam": ("winner", "lottery", "claim now", "free gift", "bitcoin"),
}

_PROMPT_INJECTION_MARKERS: tuple[str, ...] = (
    "ignore previous instructions",
    "system prompt",
    "developer message",
    "act as",
    "jailbreak",
    "exfiltrate",
)


@dataclass(frozen=True)
class RouteDecision:
    classification: str
    confidence: float
    routed_to: str
    tokens_used: int = 0


class MailRouter:
    """Route emails to CPU or LLM validation paths."""

    def __init__(
        self,
        cpu_threshold: float = 0.80,
        llm_validator: Callable[[str], Mapping[str, object]] | None = None,
    ) -> None:
        if not (0.0 <= float(cpu_threshold) <= 1.0):
            raise ValueError(f"cpu_threshold must be in [0,1], got {cpu_threshold!r}")
        self.threshold = float(cpu_threshold)
        self._llm_validator = llm_validator

    @staticmethod
    def _sanitize_text(value: str) -> str:
        text = " ".join(str(value).split())
        for marker in _PROMPT_INJECTION_MARKERS:
            text = re.sub(re.escape(marker), "[REDACTED]", text, flags=re.IGNORECASE)
        return text

    def cpu_classify(self, email: Mapping[str, object]) -> tuple[str, float]:
        subject = self._sanitize_text(str(email.get("subject", ""))).lower()
        sender = self._sanitize_text(str(email.get("sender", ""))).lower()
        text = f"{subject} {sender}".strip()

        matches: dict[str, int] = {}
        for label, words in _KEYWORDS.items():
            matches[label] = sum(1 for word in words if word in text)

        total_matches = sum(matches.values())
        if total_matches == 0:
            return "unknown", 0.60

        label = sorted(matches.items(), key=lambda item: (-item[1], item[0]))[0][0]
        max_hits = matches[label]
        confidence = min(0.99, 0.70 + (0.12 * max_hits) + (0.03 * (total_matches - max_hits)))
        return label, round(confidence, 3)

    def llm_validate(self, email: Mapping[str, object]) -> Mapping[str, object]:
        subject = self._sanitize_text(str(email.get("subject", "")))
        sender = self._sanitize_text(str(email.get("sender", "")))
        prompt = (
            f"Subject: {subject}\n"
            f"From: {sender}\n"
            "Classify as one of: urgent, work, promo, spam."
        )
        if self._llm_validator is not None:
            result = dict(self._llm_validator(prompt))
            missing = {"classification", "confidence"}.difference(result.keys())
            if missing:
                raise ValueError(f"llm_validator missing required keys: {sorted(missing)}")
            result.setdefault("tokens_used", 50)
            return result

        label, cpu_conf = self.cpu_classify(email)
        if label == "unknown":
            label = "work"
        return {"classification": label, "confidence": max(0.85, cpu_conf), "tokens_used": 50}

    def route(self, email: Mapping[str, object]) -> RouteDecision:
        classification, confidence = self.cpu_classify(email)
        if confidence >= self.threshold:
            return RouteDecision(classification=classification, confidence=confidence, routed_to="cpu_archive", tokens_used=0)

        llm = self.llm_validate(email)
        return RouteDecision(
            classification=str(llm["classification"]),
            confidence=float(llm["confidence"]),
            routed_to="llm_validate",
            tokens_used=int(llm.get("tokens_used", 0)),
        )

    def classify_batch(self, emails: list[Mapping[str, object]]) -> dict[str, object]:
        decisions: list[dict[str, object]] = []
        cpu_count = 0
        llm_count = 0
        token_total = 0
        for email in emails:
            decision = self.route(email)
            if decision.routed_to == "cpu_archive":
                cpu_count += 1
            else:
                llm_count += 1
            token_total += decision.tokens_used
            item: MutableMapping[str, object] = dict(email)
            item["classification"] = decision.classification
            item["confidence"] = decision.confidence
            item["routed_to"] = decision.routed_to
            item["tokens_used"] = decision.tokens_used
            decisions.append(dict(item))
        return {
            "emails": decisions,
            "emails_processed": len(emails),
            "cpu_classified": cpu_count,
            "llm_escalated": llm_count,
            "tokens_used": token_total,
        }

