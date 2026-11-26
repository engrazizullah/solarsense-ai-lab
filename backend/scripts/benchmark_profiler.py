"""Compare the plain-Python and Pandas profilers on a generated CSV.

Run from backend/:  uv run python -m scripts.benchmark_profiler 200000
"""

import csv
import random
import sys
import tempfile
import time
import tracemalloc
from collections.abc import Callable
from pathlib import Path

from app.services.profiler import CsvProfiler
from app.services.profiler_pandas import profile_with_pandas

CITIES = ["Rahim Yar Khan", "Lahore", "Karachi", "Multan", "Islamabad"]


def make_csv(path: Path, rows: int) -> None:
    rng = random.Random(42)  # fixed seed: same file every run
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["date", "city", "irradiance_kwh_m2", "temp_c"])
        for i in range(rows):
            irradiance = "" if rng.random() < 0.02 else f"{rng.uniform(3, 8):.2f}"
            writer.writerow(
                [
                    f"day-{i}",
                    rng.choice(CITIES),
                    irradiance,
                    f"{rng.uniform(5, 48):.1f}",
                ]
            )


def seconds(func: Callable[[], object]) -> float:
    start = time.perf_counter()
    func()
    return time.perf_counter() - start


def peak_mb(func: Callable[[], object]) -> float:
    tracemalloc.start()
    func()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1_000_000


def main() -> None:
    rows = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "readings.csv"
        make_csv(path, rows)
        print(f"Rows: {rows:,}  |  file size: {path.stat().st_size / 1_000_000:.1f} MB")
        for name, run in [
            ("Plain Python", lambda: CsvProfiler(path).profile()),
            ("Pandas", lambda: profile_with_pandas(path)),
        ]:
            print(
                f"{name:13} {seconds(run):6.2f} s   peak memory {peak_mb(run):7.1f} MB"
            )


if __name__ == "__main__":
    main()
