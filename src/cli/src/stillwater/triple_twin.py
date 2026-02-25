"""triple_twin.py — Production Triple-Twin orchestration engine.

Orchestrates user input through a three-phase pipeline:

  Phase 1 (Small Talk Twin):  Classify input as small-talk vs. task.
  Phase 2 (Intent Twin):      Map task to a wish/intent category.
  Phase 3 (Execution Twin):   Select the best combo (skill + recipe + persona).

Each phase has a CPU learner that attempts to handle the input locally.
When the CPU learner is not confident enough, an optional LLM validator
is called, and the result is learned and persisted for future CPU handling.

Discovery:
  - CPU node configs:  data/default/cpu-nodes/*.md  (YAML frontmatter)
  - Seed patterns:     data/default/seeds/*.jsonl
  - Learned patterns:  data/custom/learned_*.jsonl  (DataRegistry overlay)

stdlib only: json, re, dataclasses, typing.
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from stillwater.cpu_learner import CPULearner

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class PhaseResult:
    """Result from a single phase of the pipeline."""
    phase: int
    handled_by: str  # "cpu" or "llm"
    label: str
    confidence: float


@dataclass
class OrchestrationResult:
    """Complete result from the Triple-Twin pipeline."""
    input: str
    phase1: Optional[PhaseResult] = None
    phase2: Optional[PhaseResult] = None
    phase3: Optional[PhaseResult] = None
    matched_wish: Optional[str] = None
    matched_combo: Optional[str] = None
    final_action: Optional[str] = None
    response_text: Optional[str] = None  # small talk response text (from SmallTalkResponder)


# ---------------------------------------------------------------------------
# LLM client protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class LLMValidator(Protocol):
    """Protocol for the LLM validator client.

    Any object with a ``validate`` method matching this signature can be
    used as the ``llm_client`` parameter to ``TripleTwinEngine``.
    """

    def validate(self, phase: str, text: str, context: Optional[dict] = None) -> dict:
        """Validate input for a given phase.

        Parameters
        ----------
        phase:
            One of ``"phase1"``, ``"phase2"``, ``"phase3"``.
        text:
            The user input text.
        context:
            Optional context dict (e.g. previous phase results).

        Returns
        -------
        dict
            Must contain at least ``"label"`` (str) and ``"confidence"`` (float).
            May also contain ``"reasoning"`` (str).
        """
        ...


# ---------------------------------------------------------------------------
# YAML frontmatter parser (stdlib only — no PyYAML)
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    """Parse YAML-like frontmatter from the beginning of a markdown file.

    Supports:
      - ``key: value`` pairs (string, int, float)
      - ``key: [a, b, c]`` inline lists
      - Quoted strings (single or double)
      - Comments (``# ...``)

    Returns an empty dict if no frontmatter is found.
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}

    result: dict = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Split on first colon
        colon_idx = line.find(":")
        if colon_idx < 0:
            continue

        key = line[:colon_idx].strip()
        raw_value = line[colon_idx + 1:].strip()

        if not key:
            continue

        result[key] = _parse_value(raw_value)

    return result


def _parse_value(raw: str) -> Any:
    """Parse a single YAML value: string, int, float, list, bool, or null."""
    if not raw:
        return ""

    # Strip inline comments (but not inside quotes)
    if not (raw.startswith('"') or raw.startswith("'")):
        comment_idx = raw.find(" #")
        if comment_idx >= 0:
            raw = raw[:comment_idx].strip()

    # Inline list: [a, b, c]
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        items = [_parse_value(item.strip()) for item in inner.split(",")]
        return items

    # Quoted string
    if (raw.startswith('"') and raw.endswith('"')) or \
       (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]

    # Boolean
    if raw.lower() in ("true", "yes"):
        return True
    if raw.lower() in ("false", "no"):
        return False

    # Null
    if raw.lower() in ("null", "~", ""):
        return None

    # Integer
    try:
        return int(raw)
    except ValueError:
        pass

    # Float
    try:
        return float(raw)
    except ValueError:
        pass

    # Bare string
    return raw


# ---------------------------------------------------------------------------
# PhaseRunner — wraps a CPULearner with config from a cpu-node .md file
# ---------------------------------------------------------------------------


class PhaseRunner:
    """Wraps a CPULearner with phase config parsed from a cpu-node .md file.

    Parameters
    ----------
    phase:
        Phase identifier (``"phase1"``, ``"phase2"``, ``"phase3"``).
    name:
        Human-readable name for this phase (e.g. ``"small-talk"``).
    learner:
        The CPULearner instance for this phase.
    validator_model:
        The LLM model name to use for validation (informational).
    labels:
        Expected label values for this phase.
    learnings_file:
        Relative path for persisting learned patterns via DataRegistry
        (e.g. ``"learned_phase1.jsonl"``).
    """

    def __init__(
        self,
        phase: str,
        name: str,
        learner: CPULearner,
        validator_model: str,
        labels: list,
        learnings_file: str,
    ) -> None:
        self.phase = phase
        self.name = name
        self.learner = learner
        self.validator_model = validator_model
        self.labels = labels
        self.learnings_file = learnings_file


# ---------------------------------------------------------------------------
# TripleTwinEngine — the main orchestration engine
# ---------------------------------------------------------------------------


class TripleTwinEngine:
    """Triple-Twin orchestration engine.

    Discovers CPU nodes, loads seed and learned patterns, and processes
    user input through a Phase 1 -> 2 -> 3 pipeline.

    Parameters
    ----------
    registry:
        A ``DataRegistry`` instance for all file I/O.
    llm_client:
        Optional LLM validator client.  If ``None``, the engine runs in
        CPU-only mode (no LLM fallback — graceful degradation).
    """

    def __init__(
        self,
        registry: Any,
        llm_client: Any = None,
        audit_logger: Any = None,
        session_id: Optional[str] = None,
        user_id: str = "system",
    ) -> None:
        self.registry = registry
        self.llm_client = llm_client

        # Audit logger (FDA 21 CFR Part 11 compliant, optional)
        self._audit_logger = audit_logger
        self._session_id = session_id or str(uuid.uuid4())
        self._user_id = user_id

        # Phase runners keyed by phase name ("phase1", "phase2", "phase3")
        self._phases: Dict[str, PhaseRunner] = {}

        # Small talk responder — lazy-initialized on first non-task result
        self._smalltalk_responder: Any = None
        self._smalltalk_disabled = False

        # Statistics counters
        self._cpu_hits = 0
        self._llm_calls = 0
        self._total_processed = 0

        # Discover and load on construction
        self._discover_and_load()

    # ------------------------------------------------------------------
    # Discovery + loading
    # ------------------------------------------------------------------

    def _discover_and_load(self) -> None:
        """Discover cpu-nodes, load seeds, and load learned patterns."""
        self._discover_cpu_nodes()
        self._load_seeds()
        self._load_learned()

    def _discover_cpu_nodes(self) -> None:
        """Discover cpu-node .md files from data/default/cpu-nodes/ and data/custom/cpu-nodes/.

        Each .md file has YAML frontmatter describing a phase:
          - phase: phase1 | phase2 | phase3
          - name: human-readable name
          - validator_model: LLM model for validation
          - labels: [label1, label2, ...]
          - learnings_file: relative path for persistence
        """
        all_data = self.registry.load_all_data()
        prefix = "cpu-nodes/"

        # Collect node configs — custom/ overrides default/ (already handled by DataRegistry)
        for rel_path, content in sorted(all_data.items()):
            if not rel_path.startswith(prefix):
                continue
            if not rel_path.endswith(".md"):
                continue

            try:
                config = parse_frontmatter(content)
            except (ValueError, TypeError):
                continue  # skip malformed files

            raw_phase = config.get("phase")
            if not raw_phase:
                continue
            # Accept both integer (1, 2, 3) and string ("phase1", "phase2", "phase3")
            if isinstance(raw_phase, int):
                phase = f"phase{raw_phase}"
            else:
                phase = str(raw_phase)
            if phase not in ("phase1", "phase2", "phase3"):
                continue

            name = config.get("name", rel_path)
            validator_model = config.get("validator_model", "default")
            labels = config.get("labels", [])
            learnings_file = config.get("learnings_file", f"learned_{phase}.jsonl")

            if not isinstance(labels, list):
                labels = [labels] if labels else []

            learner = CPULearner(phase=phase)
            runner = PhaseRunner(
                phase=phase,
                name=name,
                learner=learner,
                validator_model=validator_model,
                labels=labels,
                learnings_file=learnings_file,
            )
            # Later entries override earlier ones (custom/ wins since DataRegistry
            # returns custom on top of default for the same relative path)
            self._phases[phase] = runner

    def _load_seeds(self) -> None:
        """Load seed patterns from data/default/seeds/*.jsonl."""
        all_data = self.registry.load_all_data()
        prefix = "seeds/"

        for rel_path, content in sorted(all_data.items()):
            if not rel_path.startswith(prefix):
                continue
            if not rel_path.endswith(".jsonl"):
                continue

            self._load_jsonl_into_phases(content)

    def _load_learned(self) -> None:
        """Load learned patterns from data/custom/learned_*.jsonl."""
        all_data = self.registry.load_all_data()

        for rel_path, content in sorted(all_data.items()):
            if not rel_path.startswith("learned_"):
                continue
            if not rel_path.endswith(".jsonl"):
                continue

            self._load_jsonl_into_phases(content)

    def _load_jsonl_into_phases(self, content: str) -> None:
        """Parse JSONL content and load records into the appropriate phase learner."""
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            phase = record.get("phase")
            if not phase or phase not in self._phases:
                continue

            runner = self._phases[phase]
            kw = record.get("keyword")
            if not kw:
                continue

            runner.learner._patterns[kw] = {
                "count": record.get("count", 1),
                "label": record.get("label", "unknown"),
                "examples": record.get("examples", []),
            }
            # Clear confidence cache for this keyword
            runner.learner._confidence_cache.pop(kw, None)

    # ------------------------------------------------------------------
    # Processing pipeline
    # ------------------------------------------------------------------

    def process(self, user_input: str) -> OrchestrationResult:
        """Process user input through the Phase 1 -> 2 -> 3 pipeline.

        Returns an ``OrchestrationResult`` with phase results, matched wish,
        matched combo, and final action.
        """
        self._total_processed += 1
        result = OrchestrationResult(input=user_input)

        # Phase 1: Small Talk classification
        phase1_result = self._run_phase("phase1", user_input)
        result.phase1 = phase1_result

        if phase1_result is None:
            # No phase1 runner configured — treat everything as a task
            pass
        elif phase1_result.label != "task":
            # Small talk — generate response and stop here
            result.final_action = f"small_talk:{phase1_result.label}"
            result.response_text = self._get_smalltalk_response(
                phase1_result.label, phase1_result.confidence, user_input,
            )
            return result

        # Phase 2: Intent classification
        phase2_result = self._run_phase("phase2", user_input, context={
            "phase1_label": phase1_result.label if phase1_result else "task",
        })
        result.phase2 = phase2_result

        if phase2_result is not None:
            result.matched_wish = phase2_result.label

        # Phase 3: Execution combo selection
        phase3_context = {
            "phase1_label": phase1_result.label if phase1_result else "task",
            "phase2_label": phase2_result.label if phase2_result else "unknown",
        }
        phase3_result = self._run_phase("phase3", user_input, context=phase3_context)
        result.phase3 = phase3_result

        if phase3_result is not None:
            result.matched_combo = phase3_result.label

        # Build final action string
        wish = result.matched_wish or "unknown"
        combo = result.matched_combo or "default-combo"
        result.final_action = f"execute:{wish}:{combo}"

        return result

    def _get_smalltalk_response(
        self, label: str, confidence: float, user_input: str,
    ) -> Optional[str]:
        """Get a response from SmallTalkResponder (lazy-init on first call).

        Returns the response text, or None if SmallTalkResponder is unavailable
        (e.g. no response data files found).
        """
        if self._smalltalk_disabled:
            return None

        if self._smalltalk_responder is None:
            try:
                from stillwater.smalltalk_responder import SmallTalkResponder
                self._smalltalk_responder = SmallTalkResponder(self.registry)
            except ImportError as exc:
                logger.error("SmallTalkResponder import failed; disabling smalltalk: %s", exc)
                self._smalltalk_disabled = True
                return None

        try:
            response = self._smalltalk_responder.respond(
                label=label, confidence=confidence, user_input=user_input,
            )
            return response.text
        except (ValueError, KeyError) as exc:
            logger.error("smalltalk response failed for label=%s: %s", label, exc)
            return None

    def _log_cpu_prediction(
        self, label: str, confidence: float, keywords: List[str], user_input: str,
    ) -> None:
        """Log a CPU prediction to the audit trail (if audit_logger is set)."""
        if self._audit_logger is None:
            return
        try:
            self._audit_logger.log_cpu_prediction(
                user_id=self._user_id,
                label=label,
                confidence=confidence,
                keywords=keywords,
                user_input=user_input,
                session_id=self._session_id,
            )
        except Exception as exc:
            logger.error("audit logger failed for cpu prediction: %s", exc)

    def _log_llm_call(
        self, model: str, input_text: str, output_text: str,
        label: str, confidence: float,
    ) -> None:
        """Log an LLM call to the audit trail (if audit_logger is set)."""
        if self._audit_logger is None:
            return
        try:
            self._audit_logger.log_llm_call(
                user_id=self._user_id,
                model=model,
                input_text=input_text,
                output_text=output_text,
                label=label,
                confidence=confidence,
                tokens={"input": 0, "output": 0},
                session_id=self._session_id,
            )
        except Exception as exc:
            logger.error("audit logger failed for llm call: %s", exc)

    def _run_phase(
        self,
        phase_name: str,
        text: str,
        context: Optional[dict] = None,
    ) -> Optional[PhaseResult]:
        """Run a single phase: CPU predict first, LLM fallback if not confident.

        Returns None if the phase is not configured.
        """
        if phase_name not in self._phases:
            return None

        runner = self._phases[phase_name]
        phase_num = int(phase_name[-1])  # "phase1" -> 1

        # Try CPU prediction first
        label, conf, matched_kws = runner.learner.predict(text)

        if runner.learner.can_handle(text) and label is not None:
            self._cpu_hits += 1
            self._log_cpu_prediction(label, conf, matched_kws, text)
            return PhaseResult(
                phase=phase_num,
                handled_by="cpu",
                label=label,
                confidence=conf,
            )

        # CPU not confident — call LLM validator
        llm_result = self._call_validator(runner, text, context)
        llm_label = llm_result.get("label", "unknown")
        llm_conf = llm_result.get("confidence", 0.0)
        llm_reasoning = llm_result.get("reasoning", "")

        if llm_label != "unknown":
            # Learn from LLM result
            runner.learner.learn(text, llm_label, reasoning=llm_reasoning)
            # Persist learned patterns
            self._persist_learned(runner)

        if llm_conf > 0.0:
            self._llm_calls += 1
            self._log_llm_call(
                runner.validator_model, text, llm_reasoning,
                llm_label, llm_conf,
            )

        return PhaseResult(
            phase=phase_num,
            handled_by="llm" if llm_conf > 0.0 else "cpu",
            label=llm_label,
            confidence=llm_conf,
        )

    # ------------------------------------------------------------------
    # LLM validation
    # ------------------------------------------------------------------

    def _call_validator(
        self,
        phase: PhaseRunner,
        text: str,
        context: Optional[dict] = None,
    ) -> dict:
        """Call the LLM validator for a phase.

        If no LLM client is configured, returns a default
        ``{"label": "unknown", "confidence": 0.0}`` result.
        If an LLM client exists and fails, the exception is propagated.
        """
        if self.llm_client is None:
            return {"label": "unknown", "confidence": 0.0}

        try:
            return self.llm_client.validate(phase.phase, text, context)
        except (RuntimeError, OSError, TimeoutError, ValueError, KeyError) as exc:
            logger.error("LLM validator failed for %s: %s", phase.phase, exc)
            raise

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _persist_learned(self, phase_runner: PhaseRunner) -> None:
        """Persist learned patterns to data/custom/ via DataRegistry."""
        records = phase_runner.learner.to_jsonl_records()
        lines = [json.dumps(record) for record in records]
        content = "\n".join(lines) + "\n" if lines else ""
        self.registry.save_data_file(phase_runner.learnings_file, content)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def stats(self) -> dict:
        """Return engine-level statistics.

        Returns
        -------
        dict
            Keys: ``total_processed``, ``cpu_hits``, ``llm_calls``,
            ``cpu_hit_rate``, ``phases`` (per-phase learner stats).
        """
        phase_stats = {}
        for phase_name, runner in sorted(self._phases.items()):
            phase_stats[phase_name] = {
                "name": runner.name,
                "validator_model": runner.validator_model,
                "labels": runner.labels,
                "learner": runner.learner.stats(),
            }

        total = self._total_processed
        total_phase_calls = self._cpu_hits + self._llm_calls
        cpu_rate = self._cpu_hits / total_phase_calls if total_phase_calls > 0 else 0.0

        return {
            "total_processed": total,
            "cpu_hits": self._cpu_hits,
            "llm_calls": self._llm_calls,
            "cpu_hit_rate": round(cpu_rate, 4),
            "phases": phase_stats,
        }
