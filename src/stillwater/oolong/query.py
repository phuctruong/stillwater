"""Query classification and parameter extraction for OOLONG questions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class QueryType(str, Enum):
    MOST_FREQ = "MOST_FREQ"
    LEAST_FREQ = "LEAST_FREQ"
    SECOND_MOST_FREQ = "SECOND_MOST_FREQ"
    NUMERIC_ONE_CLASS = "NUMERIC_ONE_CLASS"
    RELATIVE_FREQ = "RELATIVE_FREQ"
    REPRESENTED_N_TIMES = "REPRESENTED_N_TIMES"
    MONTH_FIRST_EXCEEDS = "MONTH_FIRST_EXCEEDS"
    MONTH_COUNT_EXCEEDS = "MONTH_COUNT_EXCEEDS"
    MONTH_IS_MOST_FREQ = "MONTH_IS_MOST_FREQ"
    USER_LABEL_COMPARE = "USER_LABEL_COMPARE"
    UNKNOWN = "UNKNOWN"


class TargetField(str, Enum):
    LABEL = "label"
    USER = "user"
    DATE = "date"


@dataclass(frozen=True)
class QueryParams:
    query_type: QueryType
    target_field: TargetField = TargetField.LABEL
    label_a: str = ""
    label_b: str = ""
    user_a: str = ""
    user_b: str = ""
    filter_users: list[str] = field(default_factory=list)
    filter_label: str = ""
    filter_month: str = ""
    date_split: str = ""
    n_value: int = 0
    month_label_a: str = ""
    month_label_b: str = ""


def classify_query(question: str, task: str, task_group: str) -> QueryParams:
    """Classify an OOLONG question into a structured query."""
    q = question.lower()

    # Detect filter patterns
    user_filter_ids = _extract_filter_users(question)
    has_user_filter = len(user_filter_ids) > 0
    month_filter = _extract_month_filter(q)
    date_range = _extract_date_range(question)

    # PRIORITY CHECKS: Meta-queries that must be handled BEFORE standard task types
    # "For how many months is label X the single most frequently occurring label?"
    if "for how many months" in q and ("most frequent" in q or "single most" in q):
        m = re.search(r"label ['\"]?([^'\"]+)['\"]?", question, re.IGNORECASE)
        label = m.group(1).strip() if m else ""
        return QueryParams(
            query_type=QueryType.MONTH_IS_MOST_FREQ,
            target_field=TargetField.LABEL,
            label_a=label,
        )

    # Use task metadata for primary classification
    if task == "TASK_TYPE.MOST_FREQ":
        if task_group == "user":
            if _has_user_compare(q):
                return _parse_user_label_compare(question)
            # Check if asking about labels with user filter vs asking about users
            if has_user_filter or month_filter or date_range or "which of the labels" in q:
                return QueryParams(
                    query_type=QueryType.MOST_FREQ,
                    target_field=TargetField.LABEL,
                    filter_users=user_filter_ids,
                    filter_month=month_filter,
                    date_split=date_range,
                )
            # Extract label filter for "which user has most instances with label X?"
            filter_label = _extract_label_filter(question)
            return QueryParams(
                query_type=QueryType.MOST_FREQ,
                target_field=TargetField.USER,
                filter_label=filter_label,
            )
        if task_group == "timeline":
            # Detect if asking for date vs label
            if "which date" in q or "what date" in q:
                return QueryParams(
                    query_type=QueryType.MOST_FREQ,
                    target_field=TargetField.DATE,
                    filter_month=month_filter,
                    date_split=date_range,
                )
            if month_filter or date_range:
                return QueryParams(
                    query_type=QueryType.MOST_FREQ,
                    target_field=TargetField.LABEL,
                    filter_month=month_filter,
                    date_split=date_range,
                )
        return QueryParams(query_type=QueryType.MOST_FREQ, target_field=TargetField.LABEL)

    if task == "TASK_TYPE.LEAST_FREQ":
        if task_group == "user":
            if has_user_filter or month_filter or date_range or "which of the labels" in q:
                return QueryParams(
                    query_type=QueryType.LEAST_FREQ,
                    target_field=TargetField.LABEL,
                    filter_users=user_filter_ids,
                    filter_month=month_filter,
                    date_split=date_range,
                )
            # Extract label filter for "which user has least instances with label X?"
            filter_label = _extract_label_filter(question)
            return QueryParams(
                query_type=QueryType.LEAST_FREQ,
                target_field=TargetField.USER,
                filter_label=filter_label,
            )
        if task_group == "timeline":
            # Detect if asking for date vs label
            if "which date" in q or "what date" in q:
                return QueryParams(
                    query_type=QueryType.LEAST_FREQ,
                    target_field=TargetField.DATE,
                    filter_month=month_filter,
                    date_split=date_range,
                )
            if month_filter or date_range:
                return QueryParams(
                    query_type=QueryType.LEAST_FREQ,
                    target_field=TargetField.LABEL,
                    filter_month=month_filter,
                    date_split=date_range,
                )
        return QueryParams(query_type=QueryType.LEAST_FREQ, target_field=TargetField.LABEL)

    if task == "TASK_TYPE.SECOND_MOST_FREQ":
        if task_group == "user":
            if has_user_filter or month_filter or "which of the labels" in q:
                return QueryParams(
                    query_type=QueryType.SECOND_MOST_FREQ,
                    target_field=TargetField.LABEL,
                    filter_users=user_filter_ids,
                    filter_month=month_filter,
                )
            # Extract label filter for "which user has second most instances with label X?"
            filter_label = _extract_label_filter(question)
            return QueryParams(
                query_type=QueryType.SECOND_MOST_FREQ,
                target_field=TargetField.USER,
                filter_label=filter_label,
            )
        if task_group == "timeline":
            # Detect if asking for date vs label
            if "which date" in q or "what date" in q:
                return QueryParams(
                    query_type=QueryType.SECOND_MOST_FREQ,
                    target_field=TargetField.DATE,
                    filter_month=month_filter,
                )
            if month_filter:
                return QueryParams(
                    query_type=QueryType.SECOND_MOST_FREQ,
                    target_field=TargetField.LABEL,
                    filter_month=month_filter,
                )
        return QueryParams(query_type=QueryType.SECOND_MOST_FREQ, target_field=TargetField.LABEL)

    if task == "TASK_TYPE.NUMERIC_ONE_CLASS":
        return _parse_numeric_one_class(question, task_group)

    if task == "TASK_TYPE.REPRESENTED_N_TIMES":
        return _parse_represented_n_times(question, task_group)

    if task == "TASK_TYPE.RELATIVE_FREQ":
        return _parse_relative_freq(question, task_group)

    return QueryParams(query_type=QueryType.UNKNOWN)


def _has_user_compare(q: str) -> bool:
    return "which user has more instances" in q


def _parse_user_label_compare(question: str) -> QueryParams:
    """Parse: 'which user has more instances with the label ham: User 76063 or User 24151?'"""
    q = question
    # Extract label
    m = re.search(r"with the label (\w[\w\s]*?):", q, re.IGNORECASE)
    filter_label = m.group(1).strip() if m else ""

    # Extract two user IDs
    users = re.findall(r"User (\d+)", q)
    user_a = users[0] if len(users) > 0 else ""
    user_b = users[1] if len(users) > 1 else ""

    return QueryParams(
        query_type=QueryType.USER_LABEL_COMPARE,
        target_field=TargetField.USER,
        user_a=user_a,
        user_b=user_b,
        filter_label=filter_label,
    )


def _parse_numeric_one_class(question: str, task_group: str) -> QueryParams:
    """Parse: 'how many data points should be classified as label X?'"""
    q = question.lower()

    # Extract filters
    filter_users = _extract_filter_users(question)
    filter_month = _extract_month_filter(q)
    date_range = _extract_date_range(question)

    # "how many data points should be classified as label 'ham'?"
    m = re.search(r"classified as label ['\"]?([^'\"?]+)['\"]?\??", q)
    if m:
        label = m.group(1).strip()
        return QueryParams(
            query_type=QueryType.NUMERIC_ONE_CLASS,
            target_field=TargetField.LABEL,
            label_a=label,
            filter_users=filter_users,
            filter_month=filter_month,
            date_split=date_range,
        )

    return QueryParams(
        query_type=QueryType.NUMERIC_ONE_CLASS,
        target_field=TargetField.LABEL,
        filter_users=filter_users,
        filter_month=filter_month,
        date_split=date_range,
    )


def _parse_represented_n_times(question: str, task_group: str) -> QueryParams:
    """Parse: 'how many dates are represented exactly N times?'"""
    q = question.lower()

    # Extract N
    m = re.search(r"exactly (\d+) times", q)
    n_value = int(m.group(1)) if m else 1

    # Determine field
    if "date" in q:
        target = TargetField.DATE
    elif "user" in q:
        target = TargetField.USER
    else:
        target = TargetField.LABEL

    # Extract filters
    filter_users = _extract_filter_users(question)
    filter_month = _extract_month_filter(q)

    return QueryParams(
        query_type=QueryType.REPRESENTED_N_TIMES,
        target_field=target,
        n_value=n_value,
        filter_users=filter_users,
        filter_month=filter_month,
    )


def _parse_relative_freq(question: str, task_group: str) -> QueryParams:
    """Parse relative frequency questions -- several sub-types."""
    q = question.lower()

    # "In which month did label X first occur more often than label Y?"
    m = re.search(r"in which month did the label ['\"]?([^'\"]+)['\"]?\s*first occur more often than the label ['\"]?([^'\"]+)['\"]?", q)
    if m:
        return QueryParams(
            query_type=QueryType.MONTH_FIRST_EXCEEDS,
            target_field=TargetField.DATE,
            month_label_a=m.group(1).strip(),
            month_label_b=m.group(2).strip(),
        )

    # "For how many months does label X occur more frequently than label Y?"
    m = re.search(r"for how many months does the label ['\"]?([^'\"]+)['\"]?\s*occur more frequent(?:ly)? than the label ['\"]?([^'\"]+)['\"]?", q)
    if m:
        return QueryParams(
            query_type=QueryType.MONTH_COUNT_EXCEEDS,
            target_field=TargetField.DATE,
            month_label_a=m.group(1).strip(),
            month_label_b=m.group(2).strip(),
        )

    # "which user has more instances with the label X: User A or User B?"
    if _has_user_compare(q):
        return _parse_user_label_compare(question)

    # "was label X more common before DATE as compared to after?"
    m = re.search(r"was label ['\"]?([^'\"]+)['\"]?\s*more common.*?before ([0-9]{4}-[0-9]{2}-[0-9]{2})", q)
    if m:
        label = m.group(1).strip()
        date_split = m.group(2).strip()
        return QueryParams(
            query_type=QueryType.RELATIVE_FREQ,
            target_field=TargetField.LABEL,
            label_a=label,
            date_split=date_split,
        )

    # "is label X more common, less common, or same frequency as label Y?"
    m = re.search(r"is label ['\"]?([^'\"]+)['\"]?\s*more common.*?as label ['\"]?([^'\"]+)['\"]?", q)
    if m:
        label_a = m.group(1).strip()
        label_b = m.group(2).strip()

        # Check for user filter
        filter_users = _extract_filter_users(question)

        # Check for month filter
        filter_month = _extract_month_filter(q)

        # Check for date range filter
        date_range = _extract_date_range(question)

        return QueryParams(
            query_type=QueryType.RELATIVE_FREQ,
            target_field=TargetField.LABEL,
            label_a=label_a,
            label_b=label_b,
            filter_users=filter_users,
            filter_month=filter_month,
            date_split=date_range,
        )

    return QueryParams(query_type=QueryType.UNKNOWN)


def _extract_filter_users(question: str) -> list[str]:
    """Extract user ID filter from question text."""
    m = re.search(r"associated with user IDs?\s+([\d,\s]+)", question, re.IGNORECASE)
    if m:
        return [u.strip() for u in m.group(1).split(",") if u.strip()]
    m = re.search(r"only consider.*?user.*?(\d+)", question, re.IGNORECASE)
    if m:
        return [m.group(1)]
    return []


def _extract_month_filter(q: str) -> str:
    """Extract month filter from 'occur in [Month]' patterns."""
    m = re.search(r"occur(?:ring)? in (\w+)", q)
    if m:
        month_raw = m.group(1).strip()
        # Normalize month name
        from .normalize import normalize_month
        return normalize_month(month_raw)
    return ""


def _extract_date_range(question: str) -> str:
    """Extract date range filter."""
    m = re.search(
        r"between\s+(.+?)\s+and\s+(.+?),?\s+incl",
        question,
        re.IGNORECASE,
    )
    if m:
        return f"{m.group(1).strip()}..{m.group(2).strip()}"
    return ""


def _extract_label_filter(question: str) -> str:
    """Extract label filter from 'with the label X' or 'with label X' patterns."""
    m = re.search(r"with (?:the )?label ['\"]?([^'\"?\n]+?)['\"]?(?:\?|$|\.|\s+give)", question, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return ""
