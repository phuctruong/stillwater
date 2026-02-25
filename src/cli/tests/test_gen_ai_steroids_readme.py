from __future__ import annotations

from stillwater.gen_ai_steroids_readme import parse_gemini_report, parse_gpt_style_report


def test_parse_gpt_style_report_extracts_pairs() -> None:
    text = """
## prime-coder.md
- Score before: 6/10
- Score after: 9/10

## prime-safety.md
- Score before: 5/10
- Score after: 9/10
"""
    out = parse_gpt_style_report(text)
    assert out["prime-coder.md"] == (6, 9)
    assert out["prime-safety.md"] == (5, 9)


def test_parse_gemini_report_extracts_first_two_scores_in_section() -> None:
    text = """
### 1. Prime Safety (`prime-safety.md`)
- **A:** blah. Score: 4/10
- **B:** blah. Score: 10/10

### 2. Prime Coder (`prime-coder.md`)
- **A:** Score: 7/10
- **B:** Score: 9/10
"""
    out = parse_gemini_report(text)
    assert out["prime-safety.md"] == (4, 10)
    assert out["prime-coder.md"] == (7, 9)
