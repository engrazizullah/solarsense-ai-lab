"""Tests for the plain-Python CSV profiler."""

from pathlib import Path

from app.services.profiler import CsvProfiler

SAMPLE = Path(__file__).parent / "data" / "sample_readings.csv"


def test_profiler_counts_rows_and_duplicates() -> None:
    report = CsvProfiler(SAMPLE).profile()

    assert report.rows == 6
    assert report.duplicate_rows == 1


def test_profiler_missing_values_per_column() -> None:
    report = CsvProfiler(SAMPLE).profile()
    missing = {c.name: c.missing for c in report.columns}

    assert missing["irradiance_kwh_m2"] == 1
    assert missing["temp_c"] == 1
    assert missing["panel_status"] == 2


def test_profiler_detects_column_types() -> None:
    report = CsvProfiler(SAMPLE).profile()
    kinds = {c.name: c.kind for c in report.columns}

    assert kinds["irradiance_kwh_m2"] == "numeric"
    assert kinds["city"] == "text"


def test_unique_values_are_capped() -> None:
    from app.services.profiler import UNIQUE_LIMIT, ColumnStats

    col = ColumnStats("id")
    for i in range(UNIQUE_LIMIT + 500):
        col.add(str(i))

    assert len(col.unique) == UNIQUE_LIMIT
    assert col.unique_capped is True
    assert col.unique_label == "1,000+"


def test_profiler_detects_date_column() -> None:
    report = CsvProfiler(SAMPLE).profile()
    kinds = {c.name: c.kind for c in report.columns}

    assert kinds["date"] == "date"
    assert kinds["irradiance_kwh_m2"] == "numeric"


def test_mixed_dates_and_text_is_text() -> None:
    from app.services.profiler import ColumnStats

    col = ColumnStats("when")
    col.add("2026-06-01")
    col.add("yesterday")

    assert col.kind == "text"
