from __future__ import annotations

from stillwater.cli import _extract_imo_problems_from_text


def _ids(problems: list[dict[str, str]]) -> list[str]:
    return [str(p.get("id")) for p in problems]


def test_extract_problem_headers_variant() -> None:
    text = """
Problem 1. First statement one.
Problem 2. Second statement two.
Problem 3. Third statement three.
Problem 4. Fourth statement four.
Problem 5. Fifth statement five.
Problem 6. Sixth statement six.
"""
    problems, meta = _extract_imo_problems_from_text(text)
    assert _ids(problems) == ["P1", "P2", "P3", "P4", "P5", "P6"]
    assert meta.get("quality", 0.0) > 0.7


def test_extract_numbered_day_style_variant() -> None:
    text = """
Day I
1. A first-day problem.
2. Another first-day problem.
3. Third first-day problem.

Second Day
1. A second-day problem.
2. Another second-day problem.
3. Third second-day problem.
"""
    problems, meta = _extract_imo_problems_from_text(text)
    assert _ids(problems) == ["P1", "P2", "P3", "P4", "P5", "P6"]
    assert meta.get("quality", 0.0) > 0.7


def test_extract_glyph_problem_marker_variant() -> None:
    text = """
Pr♦❜❧❡♠ ✶✳ Statement one.
Pr♦❜❧❡♠ ✷✳ Statement two.
Pr♦❜❧❡♠ ✸✳ Statement three.
Pr♦❜❧❡♠ ✹✳ Statement four.
Pr♦❜❧❡♠ ✺✳ Statement five.
Pr♦❜❧❡♠ ✻✳ Statement six.
"""
    problems, meta = _extract_imo_problems_from_text(text)
    assert _ids(problems) == ["P1", "P2", "P3", "P4", "P5", "P6"]
    assert meta.get("quality", 0.0) > 0.7
