"""Parse OOLONG context records.

OOLONG contexts contain pipe-delimited records like:
  Date: Dec 28, 2022 || User: 76063 || Instance: ... || Label: spam
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    date: str
    user: str
    label: str


def parse_records(context: str) -> list[Record]:
    """Parse OOLONG context text into structured records."""
    records: list[Record] = []
    for line in context.split("\n"):
        line = line.strip()
        if "||" not in line:
            continue
        fields: dict[str, str] = {}
        for segment in line.split("||"):
            segment = segment.strip()
            if ":" not in segment:
                continue
            key, _, value = segment.partition(":")
            fields[key.strip().lower()] = value.strip()

        if "label" in fields:
            records.append(Record(
                date=fields.get("date", ""),
                user=fields.get("user", ""),
                label=fields.get("label", ""),
            ))
    return records
