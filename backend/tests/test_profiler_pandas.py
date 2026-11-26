"""The Pandas profiler must agree with the plain-Python profiler."""

from pathlib import Path

from app.services.profiler import CsvProfiler
from app.services.profiler_pandas import profile_with_pandas

SAMPLE = Path(__file__).parent / "data" / "sample_readings.csv"


def test_pandas_and_plain_python_agree() -> None:
    plain = CsvProfiler(SAMPLE).profile()
    pandas_result = profile_with_pandas(SAMPLE)

    assert pandas_result["rows"] == plain.rows
    assert pandas_result["duplicate_rows"] == plain.duplicate_rows
    assert pandas_result["missing"] == {c.name: c.missing for c in plain.columns}
