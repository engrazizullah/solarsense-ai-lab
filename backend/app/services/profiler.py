"""CSV data-quality profiler written in plain Python (no Pandas)."""

import csv
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from app.core.timing import timed

UNIQUE_LIMIT = 1_000  # stop collecting distinct values after this many
MISSING_MARKERS = {"", "na", "n/a", "#n/a", "<na>", "null", "none", "nan"}


def read_rows(path: Path) -> Iterator[dict[str, str]]:
    """Yield one CSV row at a time as {column: raw text}, never the whole file."""
    with path.open(newline="", encoding="utf-8") as file:
        yield from csv.DictReader(file)


def to_float(text: str) -> float | None:
    """Return the text as a number, or None if it is not numeric."""
    try:
        return float(text)
    except ValueError:
        return None


def is_iso_date(text: str) -> bool:  # NEW
    """True if the text is an ISO date such as 2026-06-01."""
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


@dataclass
class ColumnStats:
    """Running statistics for one column, updated one value at a time."""

    name: str
    count: int = 0
    missing: int = 0
    numeric_count: int = 0
    date_count: int = 0  # NEW
    total: float = 0.0
    minimum: float | None = None
    maximum: float | None = None
    unique: set[str] = field(default_factory=set)
    unique_capped: bool = False

    def add(self, raw: str | None) -> None:
        value = (raw or "").strip()
        self.count += 1
        if value.lower() in MISSING_MARKERS:
            self.missing += 1
            return
        if len(self.unique) < UNIQUE_LIMIT:
            self.unique.add(value)
        elif value not in self.unique:
            self.unique_capped = True
        number = to_float(value)
        if number is None:
            if is_iso_date(value):  # NEW: only checked when it is not a number
                self.date_count += 1
            return
        self.numeric_count += 1
        self.total += number
        self.minimum = number if self.minimum is None else min(self.minimum, number)
        self.maximum = number if self.maximum is None else max(self.maximum, number)

    @property
    def kind(self) -> str:
        filled = self.count - self.missing
        if filled == 0:
            return "empty"
        if self.numeric_count == filled:
            return "numeric"
        if self.date_count == filled:  # NEW
            return "date"
        return "text"

    @property
    def mean(self) -> float | None:
        if self.kind != "numeric":
            return None
        return round(self.total / self.numeric_count, 3)

    @property
    def unique_label(self) -> str:
        count = f"{len(self.unique):,}"
        return f"{count}+" if self.unique_capped else count


@dataclass
class ProfileReport:
    rows: int
    duplicate_rows: int
    columns: list[ColumnStats]


class CsvProfiler:
    """Profile a CSV file in one pass, reading one row at a time."""

    def __init__(self, path: Path) -> None:
        self.path = path

    @timed
    def profile(self) -> ProfileReport:
        columns: dict[str, ColumnStats] = {}
        seen: set[int] = set()  # row hashes, not whole rows
        rows = 0
        duplicates = 0

        for row in read_rows(self.path):
            rows += 1
            key = hash(tuple(str(value) for value in row.values()))
            if key in seen:
                duplicates += 1
            else:
                seen.add(key)
            for name, raw in row.items():
                if name is None:  # extra values beyond the header
                    continue
                columns.setdefault(name, ColumnStats(name)).add(raw)

        return ProfileReport(
            rows=rows, duplicate_rows=duplicates, columns=list(columns.values())
        )
