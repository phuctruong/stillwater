"""Tests for the OOLONG solver module."""

from __future__ import annotations

import pytest

from stillwater.oolong.parser import Record, parse_records
from stillwater.oolong.query import (
    QueryParams,
    QueryType,
    TargetField,
    classify_query,
)
from stillwater.oolong.normalize import (
    normalize_answer,
    normalize_month,
    answers_match,
)
from stillwater.oolong.dispatcher import (
    Indexes,
    build_indexes,
    dispatch,
)
from stillwater.oolong.solver import solve, solve_and_check


# --- Test context fixture ---

SAMPLE_CONTEXT = """Date: Dec 28, 2022 || User: 76063 || Instance: hello world || Label: spam
Date: Dec 28, 2022 || User: 24151 || Instance: buy now || Label: spam
Date: Jan 15, 2023 || User: 76063 || Instance: good morning || Label: ham
Date: Jan 15, 2023 || User: 24151 || Instance: free offer || Label: spam
Date: Feb 10, 2023 || User: 76063 || Instance: meeting at 3 || Label: ham
Date: Feb 10, 2023 || User: 24151 || Instance: click here || Label: spam
Date: Feb 10, 2023 || User: 99999 || Instance: hi there || Label: ham
"""


# ============ Parser Tests ============


class TestParser:
    def test_parse_records_basic(self):
        records = parse_records(SAMPLE_CONTEXT)
        assert len(records) == 7

    def test_parse_record_fields(self):
        records = parse_records(SAMPLE_CONTEXT)
        r = records[0]
        assert r.date == "Dec 28, 2022"
        assert r.user == "76063"
        assert r.label == "spam"

    def test_parse_empty(self):
        records = parse_records("")
        assert records == []

    def test_parse_no_pipes(self):
        records = parse_records("just some text\nno pipes here")
        assert records == []

    def test_parse_missing_label(self):
        records = parse_records("Date: Dec 28 || User: 123 || Instance: text")
        assert records == []


# ============ Query Classification Tests ============


class TestQueryClassification:
    def test_most_freq_label(self):
        params = classify_query(
            "Which label appears most frequently?",
            "TASK_TYPE.MOST_FREQ",
            "counting",
        )
        assert params.query_type == QueryType.MOST_FREQ
        assert params.target_field == TargetField.LABEL

    def test_most_freq_user(self):
        params = classify_query(
            "Which user appears most frequently?",
            "TASK_TYPE.MOST_FREQ",
            "user",
        )
        assert params.query_type == QueryType.MOST_FREQ
        assert params.target_field == TargetField.USER

    def test_least_freq(self):
        params = classify_query(
            "Which label appears least frequently?",
            "TASK_TYPE.LEAST_FREQ",
            "counting",
        )
        assert params.query_type == QueryType.LEAST_FREQ

    def test_second_most_freq(self):
        params = classify_query(
            "What is the second most frequent label?",
            "TASK_TYPE.SECOND_MOST_FREQ",
            "counting",
        )
        assert params.query_type == QueryType.SECOND_MOST_FREQ

    def test_numeric_one_class(self):
        params = classify_query(
            "How many data points should be classified as label 'spam'?",
            "TASK_TYPE.NUMERIC_ONE_CLASS",
            "counting",
        )
        assert params.query_type == QueryType.NUMERIC_ONE_CLASS
        assert params.label_a == "spam"

    def test_represented_n_times(self):
        params = classify_query(
            "How many dates are represented exactly 3 times?",
            "TASK_TYPE.REPRESENTED_N_TIMES",
            "counting",
        )
        assert params.query_type == QueryType.REPRESENTED_N_TIMES
        assert params.n_value == 3

    def test_user_label_compare(self):
        params = classify_query(
            "Which user has more instances with the label ham: User 76063 or User 24151?",
            "TASK_TYPE.MOST_FREQ",
            "user",
        )
        assert params.query_type == QueryType.USER_LABEL_COMPARE
        assert params.user_a == "76063"
        assert params.user_b == "24151"
        assert params.filter_label == "ham"

    def test_unknown_task(self):
        params = classify_query("random question", "UNKNOWN_TASK", "")
        assert params.query_type == QueryType.UNKNOWN


# ============ Normalize Tests ============


class TestNormalize:
    def test_list_format_single(self):
        assert normalize_answer("['spam']") == "spam"

    def test_list_format_number(self):
        assert normalize_answer("[10]") == "10"

    def test_list_format_float(self):
        assert normalize_answer("[5.0]") == "5"

    def test_plain_string(self):
        assert normalize_answer("  Spam  ") == "spam"

    def test_quoted(self):
        assert normalize_answer("'ham'") == "ham"

    def test_month_normalize(self):
        assert normalize_month("jan") == "january"
        assert normalize_month("Dec") == "december"
        assert normalize_month("february") == "february"

    def test_answers_match_basic(self):
        assert answers_match("spam", "spam")
        assert answers_match("Spam", "spam")
        assert answers_match("['spam']", "spam")

    def test_answers_match_month(self):
        assert answers_match("jan", "january")
        assert answers_match("January", "january")

    def test_answers_match_number(self):
        assert answers_match("10", "10.0")
        assert answers_match("[10]", "10")

    def test_answers_no_match(self):
        assert not answers_match("spam", "ham")
        assert not answers_match("10", "11")


# ============ Dispatcher Tests ============


class TestDispatcher:
    def setup_method(self):
        self.records = parse_records(SAMPLE_CONTEXT)
        self.indexes = build_indexes(self.records)

    def test_build_indexes(self):
        assert self.indexes.label["spam"] == 4
        assert self.indexes.label["ham"] == 3
        assert self.indexes.user["76063"] == 3
        assert self.indexes.user["24151"] == 3
        assert self.indexes.user["99999"] == 1

    def test_most_freq_label(self):
        params = QueryParams(
            query_type=QueryType.MOST_FREQ,
            target_field=TargetField.LABEL,
        )
        result = dispatch(params, self.indexes)
        assert result == "spam"

    def test_least_freq_user(self):
        params = QueryParams(
            query_type=QueryType.LEAST_FREQ,
            target_field=TargetField.USER,
        )
        result = dispatch(params, self.indexes)
        assert result == "99999"

    def test_numeric_one_class(self):
        params = QueryParams(
            query_type=QueryType.NUMERIC_ONE_CLASS,
            target_field=TargetField.LABEL,
            label_a="spam",
        )
        result = dispatch(params, self.indexes)
        assert result == "4"

    def test_represented_n_times(self):
        # How many users appear exactly 3 times?
        params = QueryParams(
            query_type=QueryType.REPRESENTED_N_TIMES,
            target_field=TargetField.USER,
            n_value=3,
        )
        result = dispatch(params, self.indexes)
        assert result == "2"  # 76063 and 24151

    def test_user_label_compare(self):
        params = QueryParams(
            query_type=QueryType.USER_LABEL_COMPARE,
            target_field=TargetField.USER,
            user_a="76063",
            user_b="24151",
            filter_label="ham",
        )
        result = dispatch(params, self.indexes)
        assert "76063" in result  # 76063 has 2 ham, 24151 has 0 ham

    def test_month_label_index(self):
        assert "december" in self.indexes.month_label
        assert "january" in self.indexes.month_label
        assert "february" in self.indexes.month_label
        assert self.indexes.month_label["december"]["spam"] == 2

    def test_unknown_query_type(self):
        params = QueryParams(query_type=QueryType.UNKNOWN)
        result = dispatch(params, self.indexes)
        assert result == "unknown"


# ============ Solver Integration Tests ============


class TestSolver:
    def test_solve_most_freq(self):
        answer = solve(
            SAMPLE_CONTEXT,
            "Which label appears most frequently?",
            "TASK_TYPE.MOST_FREQ",
            "counting",
        )
        assert answer == "spam"

    def test_solve_least_freq(self):
        answer = solve(
            SAMPLE_CONTEXT,
            "Which label appears least frequently?",
            "TASK_TYPE.LEAST_FREQ",
            "counting",
        )
        assert answer == "ham"

    def test_solve_numeric(self):
        answer = solve(
            SAMPLE_CONTEXT,
            "How many data points should be classified as label 'spam'?",
            "TASK_TYPE.NUMERIC_ONE_CLASS",
            "counting",
        )
        assert answer == "4"

    def test_solve_and_check_correct(self):
        predicted, correct = solve_and_check(
            SAMPLE_CONTEXT,
            "Which label appears most frequently?",
            "['spam']",
            "TASK_TYPE.MOST_FREQ",
            "counting",
        )
        assert predicted == "spam"
        assert correct is True

    def test_solve_and_check_wrong_answer(self):
        predicted, correct = solve_and_check(
            SAMPLE_CONTEXT,
            "Which label appears most frequently?",
            "['ham']",
            "TASK_TYPE.MOST_FREQ",
            "counting",
        )
        assert predicted == "spam"
        assert correct is False

    def test_solve_empty_context(self):
        answer = solve("", "question?", "TASK_TYPE.MOST_FREQ", "counting")
        assert answer == "unknown"
