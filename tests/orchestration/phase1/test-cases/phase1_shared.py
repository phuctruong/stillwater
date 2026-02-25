"""phase1_shared.py -- Constants shared across Phase 1 orchestration audit tests.

Separated from conftest.py to avoid pytest conftest resolution collisions
when running tests from the repo root with multiple test directories.
"""

# The 9 Phase 1 labels defined in data/default/cpu-nodes/small-talk.md
PHASE1_LABELS = [
    "task",
    "greeting",
    "gratitude",
    "humor",
    "small_talk",
    "question",
    "emotional_positive",
    "emotional_negative",
    "unknown",
]

# Phase 1 confidence threshold
PHASE1_THRESHOLD = 0.70

# All shipped seeds have count=25 -> confidence via logistic: 1 - 1/(1 + 0.3*25)
SEED_CONFIDENCE = 1.0 - 1.0 / (1.0 + 0.3 * 25)  # 0.8824 (approx)

# All 20 simulation prompts: (text, expected_label, verdict_type)
# verdict_type: PASS, PASS-EDGE, FAIL-GAP, FAIL-BUG
PHASE1_DATASET = [
    ("hello", "greeting", "PASS"),
    ("fix the login bug", "task", "PASS"),
    ("Hello! Can you fix the broken tests?", "greeting", "FAIL-BUG"),
    ("yo", "unknown", "PASS-EDGE"),
    ("thanks for fixing that, now deploy it", "gratitude", "FAIL-BUG"),
    ("what is the best way to optimize queries?", "task", "PASS"),
    ("I'm feeling frustrated with this code", "unknown", "FAIL-GAP"),
    ("run", "task", "PASS"),
    ("can you help me understand the architecture?", "task", "PASS"),
    ("", "unknown", "PASS-EDGE"),
    ("hey hey hey fix fix fix", "task", "PASS"),
    ("DEPLOY TO PRODUCTION NOW", "task", "PASS"),
    ("plz halp", "unknown", "FAIL-GAP"),
    ("the the the the", "unknown", "PASS-EDGE"),
    ("12345", "unknown", "PASS-EDGE"),
    ("fix", "task", "PASS"),
    ("I need to write documentation and also run tests", "task", "PASS"),
    ("tell me a joke about security vulnerabilities", "humor", "FAIL-BUG"),
    (
        "good morning! how's the weather? also please review my PR",
        "small_talk",
        "FAIL-BUG",
    ),
    ("............", "unknown", "PASS-EDGE"),
]

# Happy path prompts (indices 0-based)
HAPPY_PATH_INDICES = [0, 1, 5, 7, 8, 10, 11, 15, 16]

# The 8 breaking pattern categories
BREAKING_PATTERNS = {
    "null_edge": "Empty string or None-like input",
    "length_edge": "Ultra-short input (< 3 chars), e.g. 'yo', single char",
    "filter_edge": "All stop words: 'the the the the'",
    "count_edge": "Repeated keyword: 'fix fix fix fix'",
    "case_edge": "All caps: 'DEPLOY TO PRODUCTION NOW'",
    "numeric_edge": "Numeric only: '12345'",
    "punctuation_edge": "Punctuation only: '............'",
    "misspelling_edge": "Misspellings: 'plz halp'",
}
