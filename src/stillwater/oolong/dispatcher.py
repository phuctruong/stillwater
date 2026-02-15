"""Dispatch OOLONG queries against Counter indexes.

Each handler takes QueryParams + Indexes and returns a string answer.
All computation is Counter-based: exact, deterministic, zero LLM.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

from .normalize import normalize_month
from .parser import Record
from .query import QueryParams, QueryType, TargetField


@dataclass
class Indexes:
    """All Counter indexes built from parsed records."""

    label: Counter = field(default_factory=Counter)
    user: Counter = field(default_factory=Counter)
    date: Counter = field(default_factory=Counter)
    # Per-month label counts: month_str -> Counter[label]
    month_label: dict[str, Counter] = field(default_factory=dict)
    # Per-year-month label counts: "2022-12" -> Counter[label]
    year_month_label: dict[str, Counter] = field(default_factory=dict)
    # Per-user label counts: user_str -> Counter[label]
    user_label: dict[str, Counter] = field(default_factory=dict)
    # Per-label user counts: label_str -> Counter[user]
    label_user: dict[str, Counter] = field(default_factory=dict)
    # Filtered counters: for user-filtered label counts
    user_filtered_label: dict[str, Counter] = field(default_factory=dict)
    # Per-date label counts for date-split queries
    date_label: dict[str, Counter] = field(default_factory=dict)


def build_indexes(records: list[Record]) -> Indexes:
    """Build all Counter indexes from parsed records."""
    idx = Indexes()

    for rec in records:
        label = rec.label.strip()
        user = rec.user.strip()
        date = rec.date.strip()

        if label:
            idx.label[label] += 1
        if user:
            idx.user[user] += 1
        if date:
            idx.date[date] += 1

        # Per-month label matrix
        if date and label:
            month = _extract_month(date)
            if month:
                if month not in idx.month_label:
                    idx.month_label[month] = Counter()
                idx.month_label[month][label] += 1

            # Per-year-month label matrix (e.g., "2022-12")
            year_month = _extract_year_month(date)
            if year_month:
                if year_month not in idx.year_month_label:
                    idx.year_month_label[year_month] = Counter()
                idx.year_month_label[year_month][label] += 1

        # Per-user label matrix
        if user and label:
            if user not in idx.user_label:
                idx.user_label[user] = Counter()
            idx.user_label[user][label] += 1

        # Per-label user matrix
        if label and user:
            if label not in idx.label_user:
                idx.label_user[label] = Counter()
            idx.label_user[label][user] += 1

        # Date-label matrix
        if date and label:
            if date not in idx.date_label:
                idx.date_label[date] = Counter()
            idx.date_label[date][label] += 1

    return idx


def dispatch(params: QueryParams, indexes: Indexes) -> str:
    """Dispatch a classified query against indexes and return an answer."""
    handler = _HANDLER_TABLE.get(params.query_type)
    if handler is None:
        return "unknown"
    return handler(params, indexes)


def _get_counter(target: TargetField, indexes: Indexes) -> Counter:
    """Get the appropriate counter for a target field."""
    if target == TargetField.USER:
        return indexes.user
    if target == TargetField.DATE:
        return indexes.date
    return indexes.label


def _get_filtered_counter(params: QueryParams, indexes: Indexes) -> Counter:
    """Get counter for target field.

    NOTE: Filtering now happens at record level before indexes are built,
    so this just returns the base counter.
    """
    return _get_counter(params.target_field, indexes)


def _alpha_tiebreak(candidates: list[str]) -> str:
    """Pick alphabetically first among tied candidates."""
    return sorted(candidates)[0] if candidates else "unknown"


# --- Handlers ---


def _handle_most_freq(params: QueryParams, indexes: Indexes) -> str:
    counter = _get_filtered_counter(params, indexes)
    if not counter:
        return "unknown"
    max_count = max(counter.values())
    winners = [k for k, v in counter.items() if v == max_count]
    return _alpha_tiebreak(winners)


def _handle_least_freq(params: QueryParams, indexes: Indexes) -> str:
    counter = _get_filtered_counter(params, indexes)
    if not counter:
        return "unknown"
    min_count = min(counter.values())
    winners = [k for k, v in counter.items() if v == min_count]
    return _alpha_tiebreak(winners)


def _handle_second_most_freq(params: QueryParams, indexes: Indexes) -> str:
    counter = _get_filtered_counter(params, indexes)
    if not counter:
        return "unknown"
    counts = sorted(set(counter.values()), reverse=True)
    if len(counts) < 2:
        return "unknown"
    second_count = counts[1]
    winners = [k for k, v in counter.items() if v == second_count]
    return _alpha_tiebreak(winners)


def _handle_numeric_one_class(params: QueryParams, indexes: Indexes) -> str:
    """Handle 'how many data points should be classified as label X?'

    NOTE: Filtering already applied at record level before index building.
    """
    counter = indexes.label

    if params.label_a:
        # Count of specific label
        count = _ci_lookup(counter, params.label_a)
        return str(count)
    # Fallback: number of unique labels
    return str(len(counter))


def _handle_relative_freq(params: QueryParams, indexes: Indexes) -> str:
    """Handle 'is label X more common than label Y?' with optional filters.

    NOTE: User/month filtering already applied at record level.
    Only date range filtering needs special handling (TODO).
    """
    # If date_split is set but no label_b, it's a before/after comparison
    if params.date_split and not params.label_b and not ".." in params.date_split:
        return _handle_relative_freq_date_split(params, indexes)

    counter = indexes.label

    # Apply date range filter if specified (TODO: move to record-level filtering)
    if params.date_split and ".." in params.date_split:
        start_str, end_str = params.date_split.split("..", 1)
        counter = _filter_by_date_range(indexes, start_str.strip(), end_str.strip())

    a = params.label_a
    b = params.label_b

    # Case-insensitive lookup
    a_count = _ci_lookup(counter, a)
    b_count = _ci_lookup(counter, b)

    return _compare_frequencies(a_count, b_count)


def _handle_relative_freq_date_split(params: QueryParams, indexes: Indexes) -> str:
    """Handle 'was label X more common before DATE as compared to after?'

    CRITICAL: Use PROPORTIONS, not absolute counts!
    If before has 10 examples and 5 are spam (50%),
    and after has 100 examples and 30 are spam (30%),
    spam was MORE COMMON before (50% > 30%) even though 5 < 30.
    """
    if not params.date_split or not params.label_a:
        return "unknown"

    split_date = params.date_split
    before_target = 0
    before_total = 0
    after_target = 0
    after_total = 0

    for date_str, label_counter in indexes.date_label.items():
        parsed = _parse_date(date_str)
        split_parsed = _parse_date(split_date)
        if parsed and split_parsed:
            # Count target label
            label_val = _ci_lookup(label_counter, params.label_a)
            # Count all labels for this date
            date_total = sum(label_counter.values())

            if parsed < split_parsed:
                before_target += label_val
                before_total += date_total
            else:
                after_target += label_val
                after_total += date_total

    # Compare PROPORTIONS, not absolute counts
    before_prop = before_target / before_total if before_total > 0 else 0
    after_prop = after_target / after_total if after_total > 0 else 0

    if abs(before_prop - after_prop) < 0.01:  # ~1% tolerance for rounding
        return "same frequency"
    elif before_prop > after_prop:
        return "more common"
    else:
        return "less common"


def _handle_represented_n_times(params: QueryParams, indexes: Indexes) -> str:
    """Handle 'how many X are represented exactly N times?'

    NOTE: Filtering already applied at record level.
    """
    counter = _get_counter(params.target_field, indexes)

    if not counter:
        return "0"

    n = params.n_value
    count = sum(1 for v in counter.values() if v == n)
    return str(count)


def _handle_month_first_exceeds(params: QueryParams, indexes: Indexes) -> str:
    """Handle 'in which month did label A first occur more often than label B?'

    Returns: "Month YYYY" format (e.g., "October 2022")
    """
    label_a = params.month_label_a
    label_b = params.month_label_b

    # Sort year-months chronologically (e.g., "2022-10", "2022-11", ...)
    sorted_year_months = sorted(indexes.year_month_label.keys())

    for year_month in sorted_year_months:
        month_counter = indexes.year_month_label[year_month]
        a_count = _ci_lookup(month_counter, label_a)
        b_count = _ci_lookup(month_counter, label_b)
        if a_count > b_count:
            # Convert "2022-10" to "October 2022"
            return _format_year_month(year_month)

    return "unknown"


def _handle_month_count_exceeds(params: QueryParams, indexes: Indexes) -> str:
    """Handle 'for how many months does label A occur more frequently than label B?'

    NOTE: "Disregard months where there is a tie" is implied.
    Only count months where A > B (strict inequality).
    """
    label_a = params.month_label_a
    label_b = params.month_label_b

    count = 0
    for year_month, month_counter in indexes.year_month_label.items():
        a_count = _ci_lookup(month_counter, label_a)
        b_count = _ci_lookup(month_counter, label_b)
        # Strict inequality: disregards ties
        if a_count > b_count:
            count += 1

    return str(count)


def _handle_user_label_compare(params: QueryParams, indexes: Indexes) -> str:
    """Handle 'which user has more instances with the label X: User A or User B?'"""
    label = params.filter_label
    user_a = params.user_a
    user_b = params.user_b

    a_count = 0
    b_count = 0

    user_a_labels = indexes.user_label.get(user_a, Counter())
    user_b_labels = indexes.user_label.get(user_b, Counter())

    a_count = _ci_lookup(user_a_labels, label)
    b_count = _ci_lookup(user_b_labels, label)

    if a_count > b_count:
        return user_a
    elif b_count > a_count:
        return user_b
    return user_a  # tie-break: first mentioned


def _handle_month_is_most_freq(params: QueryParams, indexes: Indexes) -> str:
    """Handle 'for how many months is label X the single most frequently occurring label?'

    Counts months where:
    1. Label X has the highest count
    2. No ties (single most = must be unique max)
    """
    target_label = params.label_a

    count = 0
    for year_month, label_counter in indexes.year_month_label.items():
        if not label_counter:
            continue

        # Find max count
        max_count = max(label_counter.values())

        # Get all labels with max count
        max_labels = [lbl for lbl, cnt in label_counter.items() if cnt == max_count]

        # Check if target label is THE SINGLE most frequent (no ties)
        if len(max_labels) == 1 and _ci_lookup(label_counter, target_label) == max_count:
            count += 1

    return str(count)


# --- Helper functions ---


def _compare_frequencies(count_a: int, count_b: int, tolerance: float = 0.01) -> str:
    """Compare two frequencies with tolerance threshold."""
    if count_a == count_b:
        return "same frequency as"
    if max(count_a, count_b) == 0:
        return "same frequency as"
    relative_diff = abs(count_a - count_b) / max(count_a, count_b)
    if relative_diff <= tolerance:
        return "same frequency as"
    if count_a > count_b:
        return "more common than"
    return "less common than"


def _ci_lookup(counter: Counter, key: str) -> int:
    """Case-insensitive Counter lookup."""
    val = counter.get(key, 0)
    if val > 0:
        return val
    key_lower = key.lower()
    for k, v in counter.items():
        if k.lower() == key_lower:
            return v
    return 0


def _extract_month(date_str: str) -> str:
    """Extract month name from a date string like 'Dec 28, 2022'."""
    date_str = date_str.strip()

    # Try "Mon DD, YYYY" format
    parts = date_str.split()
    if len(parts) >= 1:
        month_part = parts[0].lower().rstrip(",.")
        normalized = normalize_month(month_part)
        # Check if normalized is a valid month name
        valid_months = {"january", "february", "march", "april", "may", "june",
                       "july", "august", "september", "october", "november", "december"}
        if normalized in valid_months:
            return normalized

    # Try YYYY-MM-DD format
    m = _parse_date_ymd(date_str)
    if m:
        month_num = m[1]
        month_map = {
            1: "january", 2: "february", 3: "march", 4: "april",
            5: "may", 6: "june", 7: "july", 8: "august",
            9: "september", 10: "october", 11: "november", 12: "december",
        }
        return month_map.get(month_num, "")

    return date_str


def _extract_year_month(date_str: str) -> str:
    """Extract year-month in YYYY-MM format from date strings like 'Dec 28, 2022' or '2022-12-28'."""
    date_str = date_str.strip()

    # Try "Mon DD, YYYY" format
    parts = date_str.split()
    if len(parts) >= 3:
        month_part = parts[0].rstrip(",.")
        year_part = parts[-1].rstrip(",.")
        month_normalized = normalize_month(month_part.lower())
        if month_normalized and year_part.isdigit():
            # Map month name to number
            month_num = {
                "january": 1, "february": 2, "march": 3, "april": 4,
                "may": 5, "june": 6, "july": 7, "august": 8,
                "september": 9, "october": 10, "november": 11, "december": 12,
            }.get(month_normalized)
            if month_num:
                return f"{year_part}-{month_num:02d}"

    # Try YYYY-MM-DD format
    m = _parse_date_ymd(date_str)
    if m:
        year, month_num, _ = m
        return f"{year}-{month_num:02d}"

    return ""


def _parse_date_ymd(s: str) -> tuple[int, int, int] | None:
    """Parse YYYY-MM-DD format."""
    import re as _re
    m = _re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", s.strip())
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return None


def _parse_date(date_str: str) -> datetime | None:
    """Parse various date formats to datetime."""
    date_str = date_str.strip()

    # Try "Mon DD, YYYY"
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def _sort_months(months: list[str]) -> list[str]:
    """Sort month names chronologically."""
    order = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
    }
    return sorted(months, key=lambda m: order.get(m.lower(), 99))


def _format_year_month(year_month: str) -> str:
    """Convert '2022-10' to 'October 2022'."""
    if "-" not in year_month:
        return year_month

    parts = year_month.split("-")
    if len(parts) != 2:
        return year_month

    year, month_num = parts[0], int(parts[1])
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December",
    }
    month_name = month_names.get(month_num, "")
    return f"{month_name} {year}" if month_name else year_month


def _filter_by_date_range(
    indexes: Indexes, start_str: str, end_str: str
) -> Counter:
    """Build a label Counter filtered by date range."""
    start = _parse_date(start_str)
    end = _parse_date(end_str)
    if not start or not end:
        return indexes.label

    counter: Counter = Counter()
    for date_str, label_counter in indexes.date_label.items():
        parsed = _parse_date(date_str)
        if parsed and start <= parsed <= end:
            counter += label_counter
    return counter


def _iter_date_user(indexes: Indexes) -> list[tuple[str, str]]:
    """Iterate (date, user) pairs from indexes. Not stored directly, so approximate."""
    # This is a limitation -- we'd need the raw records for cross-field filtering
    # For now, return empty (user-filtered date counting is rare)
    return []


_HANDLER_TABLE = {
    QueryType.MOST_FREQ: _handle_most_freq,
    QueryType.LEAST_FREQ: _handle_least_freq,
    QueryType.SECOND_MOST_FREQ: _handle_second_most_freq,
    QueryType.NUMERIC_ONE_CLASS: _handle_numeric_one_class,
    QueryType.RELATIVE_FREQ: _handle_relative_freq,
    QueryType.REPRESENTED_N_TIMES: _handle_represented_n_times,
    QueryType.MONTH_FIRST_EXCEEDS: _handle_month_first_exceeds,
    QueryType.MONTH_COUNT_EXCEEDS: _handle_month_count_exceeds,
    QueryType.MONTH_IS_MOST_FREQ: _handle_month_is_most_freq,
    QueryType.USER_LABEL_COMPARE: _handle_user_label_compare,
}
