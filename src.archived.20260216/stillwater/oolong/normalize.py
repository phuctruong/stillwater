"""Answer normalization for OOLONG benchmark matching.

Handles:
- Python list string format: "['spam']" -> "spam"
- Lowercase + strip
- Month name normalization
- Numeric format normalization
"""

from __future__ import annotations

import ast
import re


_MONTH_MAP: dict[str, str] = {
    "jan": "january", "january": "january", "1": "january", "01": "january",
    "feb": "february", "february": "february", "2": "february", "02": "february",
    "mar": "march", "march": "march", "3": "march", "03": "march",
    "apr": "april", "april": "april", "4": "april", "04": "april",
    "may": "may", "5": "may", "05": "may",
    "jun": "june", "june": "june", "6": "june", "06": "june",
    "jul": "july", "july": "july", "7": "july", "07": "july",
    "aug": "august", "august": "august", "8": "august", "08": "august",
    "sep": "september", "sept": "september", "september": "september",
    "9": "september", "09": "september",
    "oct": "october", "october": "october", "10": "october",
    "nov": "november", "november": "november", "11": "november",
    "dec": "december", "december": "december", "12": "december",
}

_MONTH_FULL_TO_NUM: dict[str, str] = {
    "january": "1", "february": "2", "march": "3", "april": "4",
    "may": "5", "june": "6", "july": "7", "august": "8",
    "september": "9", "october": "10", "november": "11", "december": "12",
}


def normalize_answer(raw: str) -> str:
    """Normalize an answer string for comparison."""
    s = raw.strip()

    # Parse Python list format: "['spam']" or "[10]" or "['a', 'b']"
    s = _parse_list_format(s)

    # Lowercase
    s = s.lower().strip()

    # Remove surrounding quotes
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        s = s[1:-1]

    # Normalize date format: "mar 03, 2023" -> "march 3, 2023"
    s = _normalize_date(s)

    # Normalize numbers: "5.0" -> "5", strip leading zeros
    s = _normalize_number(s)

    # Strip articles
    for prefix in ("the ", "a ", "an "):
        if s.startswith(prefix):
            s = s[len(prefix):]

    return s.strip()


def normalize_month(raw: str) -> str:
    """Normalize a month string to full lowercase name."""
    key = raw.strip().lower().rstrip(".")
    return _MONTH_MAP.get(key, key)


def month_to_number(month: str) -> str:
    """Convert month name to number string."""
    key = normalize_month(month)
    return _MONTH_FULL_TO_NUM.get(key, month)


def answers_match(predicted: str, expected: str) -> bool:
    """Check if predicted answer matches expected after normalization.

    Handles multi-answer expected values (ties):
    - expected="['a', 'b']" matches predicted="a" OR predicted="b"
    """
    p = normalize_answer(predicted)

    # Try to parse expected as a list (for ties)
    expected_list = _parse_expected_list(expected)

    for e in expected_list:
        e_norm = normalize_answer(e)

        if p == e_norm:
            return True

        # Try month normalization
        p_month = normalize_month(p)
        e_month = normalize_month(e_norm)
        if p_month == e_month and p_month in _MONTH_MAP.values():
            return True

        # Try numeric comparison
        try:
            if float(p) == float(e_norm):
                return True
        except (ValueError, TypeError):
            pass

    return False


def _parse_expected_list(expected: str) -> list[str]:
    """Parse expected answer, handling list format for multi-answer (ties)."""
    import datetime

    expected = str(expected).strip()

    # Handle datetime.date string format: "[datetime.date(2022, 5, 12)]"
    if "datetime.date(" in expected:
        import calendar
        result = []
        for match in re.finditer(r"datetime\.date\((\d+),\s*(\d+),\s*(\d+)\)", expected):
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            # Format as "Month Day, Year" without zero-padding day
            month_name = calendar.month_name[month]
            result.append(f"{month_name} {day}, {year}")
        if result:
            return result

    if expected.startswith("[") and expected.endswith("]"):
        try:
            parsed = ast.literal_eval(expected)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed]
        except (ValueError, SyntaxError):
            pass

    return [expected]


def _parse_list_format(s: str) -> str:
    """Parse Python list string format: \"['spam']\" -> \"spam\"."""
    if not s.startswith("["):
        return s

    try:
        parsed = ast.literal_eval(s)
        if isinstance(parsed, list):
            if len(parsed) == 1:
                return str(parsed[0])
            if len(parsed) == 0:
                return ""
            return ", ".join(str(x) for x in parsed)
    except (ValueError, SyntaxError):
        pass

    # Fallback: strip brackets and quotes manually
    inner = s.strip("[]").strip()
    inner = inner.strip("'\"")
    return inner


def _normalize_number(s: str) -> str:
    """Normalize numeric strings: '5.0' -> '5', '007' -> '7'."""
    try:
        f = float(s)
        if f == int(f):
            return str(int(f))
        return s
    except (ValueError, TypeError):
        return s


def _normalize_date(s: str) -> str:
    """Normalize date strings: 'mar 03, 2023' -> 'march 3, 2023', 'feb 01' -> 'february 1'."""
    # Pattern: word 0X, year OR word 0X
    parts = s.split()
    if len(parts) >= 2:
        month_part = parts[0].rstrip(",.")
        day_part = parts[1].rstrip(",.")

        # Normalize month name - only proceed if it's a valid month
        month_norm = normalize_month(month_part)
        valid_months = {"january", "february", "march", "april", "may", "june",
                       "july", "august", "september", "october", "november", "december"}
        if month_norm not in valid_months:
            return s

        # Remove leading zero from day
        if day_part.isdigit() and len(day_part) == 2 and day_part[0] == '0':
            day_part = day_part[1]

        # Reconstruct
        if len(parts) == 2:
            return f"{month_norm} {day_part}"
        elif len(parts) >= 3:
            year_part = parts[2].rstrip(",.")
            return f"{month_norm} {day_part}, {year_part}"

    return s
