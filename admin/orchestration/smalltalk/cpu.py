"""
SmallTalkCPU — Queue-First Small Talk Twin (CPU half).

Architecture (from SMALLTALK_TWIN_BRAINSTORM.md):

  User input
    |
    v
  1. Check BanterQueueDB (< 5ms SLA)
     Hit? → Return instantly + mark_used()
     Miss? → fall through
    |
    v
  2. CPU Deterministic Fallback (< 50ms SLA)
     detect_glow() → float
     high GLOW (> 0.6): keyword+template generation
     low  GLOW (<= 0.6): pull from repos (jokes → weather → facts)
    |
    v
  3. WarmToken returned to caller

GLOW = emotional/communicative intensity signal (0.0 = quiet, 1.0 = intense).

No network on any hot path. No ML. No randomness. All deterministic.

rung_target: 641 (deterministic, testable, offline-first)
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Dict, List, Optional

from .database import BanterQueueDB, JokeRepo, PatternRepo, TechFactRepo
from .models import (
    BanterQueueEntry,
    RegisterProfile,
    SmallTalkPattern,
    WarmToken,
    WeatherContext,
)
from .weather_banter import generate_weather_banter

# ---------------------------------------------------------------------------
# Pre-compiled signal patterns for register / GLOW detection
# (compiled at module import time — zero latency on hot path)
# ---------------------------------------------------------------------------

# Formal signals
_FORMAL_PATTERNS = re.compile(
    r"\b(would you|please|kindly|could you|may i|i request|i would like|"
    r"hereby|regarding|pertaining|pursuant|therefore|furthermore|nevertheless)\b",
    re.IGNORECASE,
)

# Casual signals
_CASUAL_PATTERNS = re.compile(
    r"\b(hey|hi|lol|bruh|yo|gonna|wanna|lemme|btw|asap|thx|ty|np|imo|"
    r"omg|wtf|lmao|haha|hehe|nah|yeah|yep|nope|cool|awesome|nice|"
    r"dude|man|bro|sis)\b",
    re.IGNORECASE,
)

# Urgency signals
_URGENT_PATTERNS = re.compile(
    r"\b(immediately|urgent|asap|right now|now!|critical|emergency|"
    r"broken|down|outage|incident|production issue|help me|stuck|blocked)\b",
    re.IGNORECASE,
)

# Reflective signals
_REFLECTIVE_PATTERNS = re.compile(
    r"\b(thinking|consider|curious|wondering|ponder|maybe|perhaps|"
    r"explore|future|long.term|strategy|vision|plan)\b",
    re.IGNORECASE,
)

# High-energy structural signals: 2+ exclamation marks or 2+ emojis (NOT IGNORECASE — avoids matching regular words)
_HIGH_ENERGY_STRUCT = re.compile(
    r"(!{2,}|[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]{2,})",
    re.UNICODE,
)
# High-energy keyword signals (explicit word list, case-insensitive but word-boundary protected)
_HIGH_ENERGY_KEYWORDS = re.compile(
    r"\b(wow|amazing|incredible|fantastic|excited|hyped|pumped|awesome|"
    r"brilliant|superb|outstanding|legendary|epic|unbelievable)\b",
    re.IGNORECASE,
)
# ALL_CAPS signal (4+ consecutive uppercase letters — no IGNORECASE so it actually checks case)
_ALLCAPS_PATTERN = re.compile(r"\b[A-Z]{4,}\b")

# Low-energy signals
_LOW_ENERGY_PATTERNS = re.compile(
    r"\b(tired|exhausted|drained|meh|whatever|boring|slow|sleepy|"
    r"barely|struggling|tough|rough|burned out|long day|rough day)\b",
    re.IGNORECASE,
)

# GLOW high-intensity signals (emotional intensity markers)
_GLOW_HIGH_PATTERNS = re.compile(
    r"\b(excited|amazing|incredible|love|hate|furious|devastated|"
    r"thrilled|celebrating|won|breakthrough|finally|achieved|"
    r"heartbroken|anxious|stressed|crisis|urgent|victory|success|"
    r"fired|promoted|engaged|married|baby|died|death|lost)\b",
    re.IGNORECASE,
)

# GLOW keywords that suggest high emotional intensity for specific events
_GLOW_CELEBRATION_PATTERNS = re.compile(
    r"\b(congrats|congratulations|won|winning|shipped|launched|"
    r"completed|finished|done|achieved|milestone|celebrate|party|"
    r"engaged|promoted|married|hired|accepted|graduated|retired)\b",
    re.IGNORECASE,
)

# Template fragments for high-GLOW CPU generation
_HIGH_GLOW_TEMPLATES: Dict[str, str] = {
    "celebration": "That is a real milestone. Well done.",
    "achievement": "You shipped it. That took effort.",
    "struggle":    "Tough stretch. But you are still in it.",
    "frustration": "That is genuinely frustrating. Keep at it.",
    "learning":    "New territory. Every expert started here.",
    "general":     "Noted. Keep going.",
}

# Keyword → topic tag extraction (for repo lookups)
_TAG_KEYWORD_MAP: Dict[str, List[str]] = {
    "oauth":       ["oauth", "security", "auth"],
    "auth":        ["oauth", "security", "auth"],
    "token":       ["oauth", "security", "auth"],
    "python":      ["python", "programming"],
    "javascript":  ["javascript", "frontend"],
    "js":          ["javascript", "frontend"],
    "react":       ["react", "javascript", "frontend"],
    "sql":         ["database", "sql"],
    "database":    ["database", "sql"],
    "db":          ["database", "sql"],
    "docker":      ["docker", "devops", "containers"],
    "kubernetes":  ["devops", "containers", "infrastructure"],
    "k8s":         ["devops", "containers", "infrastructure"],
    "git":         ["git", "devops", "version-control"],
    "deploy":      ["devops", "deployment"],
    "ci":          ["devops", "testing"],
    "test":        ["testing", "general"],
    "debug":       ["debugging", "general"],
    "bug":         ["debugging", "general"],
    "security":    ["security", "auth"],
    "ml":          ["machine-learning", "ml"],
    "model":       ["machine-learning", "ml"],
    "api":         ["api", "general"],
    "rest":        ["api", "general"],
    "http":        ["networking", "api"],
    "tcp":         ["networking", "tcp"],
    "unix":        ["unix", "linux", "cli"],
    "linux":       ["unix", "linux"],
}

# Last-resort fallback responses (index by int to stay deterministic)
_FALLBACK_RESPONSES: List[str] = [
    "Keep coding. You are doing great.",
    "You are making progress. Keep at it.",
    "One step at a time. You have got this.",
    "The work continues. Stay focused.",
    "Good effort. Keep building.",
]


# ---------------------------------------------------------------------------
# SmallTalkCPU
# ---------------------------------------------------------------------------

class SmallTalkCPU:
    """
    Queue-First Small Talk Twin — CPU half.

    Instantiate once. Call generate() on every user interaction.
    The queue DB is checked first (<5ms SLA); CPU fallback is
    used when the queue is empty (<50ms SLA).

    Constructor accepts optional pre-loaded repos for testing without
    touching the filesystem.
    """

    def __init__(
        self,
        db: Optional[BanterQueueDB] = None,
        joke_repo: Optional[JokeRepo] = None,
        fact_repo: Optional[TechFactRepo] = None,
        pattern_repo: Optional[PatternRepo] = None,
        data_dir: Optional[str] = None,
    ) -> None:
        """
        Args:
            db:           BanterQueueDB instance (default: in-memory).
            joke_repo:    Pre-loaded JokeRepo (default: load from data_dir/jokes.jsonl).
            fact_repo:    Pre-loaded TechFactRepo (default: load from data_dir/tech_facts.jsonl).
            pattern_repo: Pre-loaded PatternRepo (default: empty).
            data_dir:     Directory containing jokes.jsonl, tech_facts.jsonl.
                          If None, uses the directory this file lives in.
        """
        self._db = db if db is not None else BanterQueueDB(":memory:")

        # Resolve data directory
        if data_dir is None:
            data_dir = str(Path(__file__).parent)

        # Load repos (no-op if already provided)
        self._jokes = joke_repo or self._load_jokes(data_dir)
        self._facts = fact_repo or self._load_facts(data_dir)
        self._patterns = pattern_repo or PatternRepo()

        # Fallback cycle index (deterministic rotation — no randomness)
        self._fallback_index: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        user_id: str,
        session_id: str,
        prompt: str,
        context: Optional[Dict] = None,
        weather: Optional[WeatherContext] = None,
        local_hour: Optional[int] = None,
        trust_level: float = 0.5,
    ) -> WarmToken:
        """
        Main entry point. Returns a WarmToken.

        Steps:
          1. Check banter queue (< 5ms SLA)
          2. If miss: CPU fallback (< 50ms SLA)
             a. detect_glow()
             b. high GLOW → keyword+template generation
             c. low GLOW  → repo lookup (joke → weather → fact → fallback)

        Args:
            user_id:     User identifier for queue lookup.
            session_id:  Current session identifier.
            prompt:      User's latest message text.
            context:     Optional dict with extra context (e.g. {"project": "oauth"}).
            weather:     Optional weather context (caller supplies, not fetched).
            local_hour:  Caller's local hour (0-23) for time-based banter.
            trust_level: Float 0-1 controlling access to priority-3 patterns.

        Returns:
            WarmToken with .response ready for display.
        """
        context = context or {}
        t_start = time.perf_counter()

        # Step 1: Queue hit?
        tags = self._extract_tags(prompt, context)
        entry = self._db.get_next(user_id=user_id, tags=tags if tags else None)

        if entry is not None:
            self._db.mark_used(entry.id)
            latency_ms = (time.perf_counter() - t_start) * 1000
            return WarmToken(
                response=entry.banter,
                source="queue_hit",
                queue_entry_id=entry.id,
                confidence=entry.confidence,
                latency_ms=latency_ms,
                glow_score=0.5,
                tags=entry.tags,
            )

        # Step 2: CPU fallback
        glow = self.detect_glow(prompt)
        register = self.detect_register(prompt)

        if glow > 0.6:
            # High GLOW: generate from keyword+template
            response = self._generate_high_glow(prompt, glow, context)
            source = "cpu_glow"
        else:
            # Low GLOW: pull from repos
            response = (
                self._pull_joke(tags, glow)
                or self._pull_weather(weather, local_hour)
                or self._pull_fact(tags)
                or self._pull_fallback()
            )
            source = "cpu_repo"

        latency_ms = (time.perf_counter() - t_start) * 1000
        return WarmToken(
            response=response,
            source=source,
            confidence=0.6,
            latency_ms=latency_ms,
            glow_score=glow,
            detected_register=register,
            tags=tags,
        )

    def queue_lookup(
        self,
        user_id: str,
        tags: Optional[List[str]] = None,
    ) -> Optional[BanterQueueEntry]:
        """
        Check the banter queue for this user.

        Does NOT mark as used. Caller must call mark_used() separately.
        Returns None if queue is empty or all entries are expired/used.
        """
        return self._db.get_next(user_id=user_id, tags=tags)

    def detect_glow(self, text: str) -> float:
        """
        Detect GLOW (emotional/communicative intensity) of text.

        Returns a float 0.0–1.0.
        Fully deterministic: no ML, no randomness.

        Signal weighting:
          - 1 high-intensity emotional keyword  → +0.30
          - 2+ high-intensity keywords          → +0.45 (capped, not cumulative)
          - Celebration/achievement keywords    → +0.25
          - 2+ exclamation marks               → +0.20
          - 1 exclamation mark                 → +0.05
          - ALL_CAPS words (4+ chars, strict)  → +0.15
          - 2+ emojis                          → +0.15
          - 1 emoji                            → +0.05

        Score clamped to [0.0, 1.0].
        """
        score: float = 0.0

        # Count high-intensity keyword matches (findall to catch multiple)
        high_matches = _GLOW_HIGH_PATTERNS.findall(text)
        if len(high_matches) >= 2:
            score += 0.65  # Multiple high-intensity words = very high GLOW
        elif len(high_matches) == 1:
            score += 0.30

        if _GLOW_CELEBRATION_PATTERNS.search(text):
            score += 0.25

        # Multiple exclamation marks
        excl_count = text.count("!")
        if excl_count >= 2:
            score += 0.20
        elif excl_count == 1:
            score += 0.05

        # ALL_CAPS words (strict — no re.IGNORECASE, detects actual caps)
        caps_words = _ALLCAPS_PATTERN.findall(text)
        if caps_words:
            score += 0.15

        # Multiple emoji (Unicode ranges)
        emojis = re.findall(
            r"[\U0001F300-\U0001FFFF\U00002702-\U000027B0]", text
        )
        if len(emojis) >= 2:
            score += 0.15
        elif len(emojis) == 1:
            score += 0.05

        return min(score, 1.0)

    def detect_register(self, prompt: str) -> RegisterProfile:
        """
        Detect user's communication register from the prompt text.

        Returns a RegisterProfile. Deterministic (regex-based, no ML).
        """
        formal_hits = len(_FORMAL_PATTERNS.findall(prompt))
        casual_hits = len(_CASUAL_PATTERNS.findall(prompt))
        urgent_hits = len(_URGENT_PATTERNS.findall(prompt))
        reflective_hits = len(_REFLECTIVE_PATTERNS.findall(prompt))

        # High-energy: structural signals (2+ !, caps) + keyword signals
        high_struct = len(_HIGH_ENERGY_STRUCT.findall(prompt))
        high_keywords = len(_HIGH_ENERGY_KEYWORDS.findall(prompt))
        caps_words = len(_ALLCAPS_PATTERN.findall(prompt))
        high_e_score = high_struct + high_keywords + caps_words

        # Low-energy: explicit keyword matching (tied to tiredness/exhaustion vocabulary)
        low_e_hits = len(_LOW_ENERGY_PATTERNS.findall(prompt))

        formality: str = "formal" if formal_hits > casual_hits else "casual"

        words = prompt.split()
        length: str = "verbose" if len(words) >= 15 else "terse"

        urgency: str = "urgent" if urgent_hits > reflective_hits else "reflective"

        if high_e_score > 0 and high_e_score > low_e_hits:
            energy = "high"
        elif low_e_hits > 0 and low_e_hits >= high_e_score:
            energy = "low"
        else:
            energy = "medium"

        return RegisterProfile(
            formality=formality,
            length=length,
            urgency=urgency,
            energy=energy,
        )

    def generate_fallback(
        self,
        glow: float,
        tags: Optional[List[str]] = None,
        weather: Optional[WeatherContext] = None,
        local_hour: Optional[int] = None,
    ) -> str:
        """
        CPU-only fallback path (no queue check).

        Used directly in tests and in the generate() internal path.
        Returns a plain string.
        """
        if glow > 0.6:
            return _HIGH_GLOW_TEMPLATES.get("general", "Keep going.")

        response = (
            self._pull_joke(tags or [], glow)
            or self._pull_weather(weather, local_hour)
            or self._pull_fact(tags or [])
            or self._pull_fallback()
        )
        return response

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_tags(self, prompt: str, context: Dict) -> List[str]:
        """
        Extract topic tags from prompt text and context dict.

        Deterministic: keyword scan, no ML.
        """
        tags: set = set()
        prompt_lower = prompt.lower()

        for keyword, tag_list in _TAG_KEYWORD_MAP.items():
            if keyword in prompt_lower:
                tags.update(tag_list)

        # Context may carry explicit tags or project name
        if "tags" in context and isinstance(context["tags"], list):
            tags.update(context["tags"])

        project = context.get("project", "").lower()
        if project and project in _TAG_KEYWORD_MAP:
            tags.update(_TAG_KEYWORD_MAP[project])

        return sorted(tags)

    def _generate_high_glow(
        self, prompt: str, glow: float, context: Dict
    ) -> str:
        """
        Generate a response for high-GLOW (emotional) prompts.

        Uses keyword matching against template fragments. Deterministic.
        """
        prompt_lower = prompt.lower()

        if any(w in prompt_lower for w in [
            "congratulations", "won", "shipped", "launched", "milestone",
            "done", "finished", "celebrate", "achievement", "promoted", "married", "engaged"
        ]):
            return _HIGH_GLOW_TEMPLATES["celebration"]

        if any(w in prompt_lower for w in [
            "stuck", "blocked", "broken", "failed", "crisis", "outage", "bug"
        ]):
            return _HIGH_GLOW_TEMPLATES["struggle"]

        if any(w in prompt_lower for w in [
            "frustrated", "angry", "furious", "annoyed", "hate this"
        ]):
            return _HIGH_GLOW_TEMPLATES["frustration"]

        if any(w in prompt_lower for w in [
            "learning", "new", "first time", "trying", "exploring", "beginner"
        ]):
            return _HIGH_GLOW_TEMPLATES["learning"]

        return _HIGH_GLOW_TEMPLATES["general"]

    def _pull_joke(self, tags: List[str], glow: float) -> Optional[str]:
        """Pull first matching joke from JokeRepo. Returns None if empty."""
        entry = self._jokes.find(tags=tags, glow=glow)
        if entry:
            return entry.joke
        return None

    def _pull_weather(
        self,
        weather: Optional[WeatherContext],
        local_hour: Optional[int],
    ) -> Optional[str]:
        """Generate weather banter. Returns None only if both args are None."""
        if weather is None and local_hour is None:
            return None
        return generate_weather_banter(weather=weather, local_hour=local_hour)

    def _pull_fact(self, tags: List[str]) -> Optional[str]:
        """Pull first matching tech fact. Returns None if repo empty."""
        entry = self._facts.find(tags=tags)
        if entry:
            return f"Fun fact: {entry.fact}"
        return None

    def _pull_fallback(self) -> str:
        """
        Deterministic rotation through fallback strings.

        No randomness: cycles through _FALLBACK_RESPONSES in order.
        """
        response = _FALLBACK_RESPONSES[self._fallback_index % len(_FALLBACK_RESPONSES)]
        self._fallback_index += 1
        return response

    # ------------------------------------------------------------------
    # Repo loaders (called at init time only)
    # ------------------------------------------------------------------

    @staticmethod
    def _load_jokes(data_dir: str) -> JokeRepo:
        repo = JokeRepo()
        path = str(Path(data_dir) / "jokes.jsonl")
        repo.load_jsonl(path)
        return repo

    @staticmethod
    def _load_facts(data_dir: str) -> TechFactRepo:
        repo = TechFactRepo()
        path = str(Path(data_dir) / "tech_facts.jsonl")
        repo.load_jsonl(path)
        return repo
