"""The same CSV checks using Pandas, for comparison with the plain-Python profiler."""

from pathlib import Path

import pandas as pd

from app.core.timing import timed


@timed
def profile_with_pandas(path: Path) -> dict[str, object]:
    df = pd.read_csv(path)
    return {
        "rows": len(df),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing": {name: int(n) for name, n in df.isna().sum().items()},
    }
