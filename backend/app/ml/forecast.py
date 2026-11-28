"""Next-day solar irradiance forecast: shared features + prediction.

The SAME build_features() is used for training and for live predictions,
so the model always sees inputs prepared exactly the same way.
"""

import json
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from app.services.open_meteo import CITIES

ARTIFACT_DIR = Path(__file__).parent / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "forecast.joblib"
METRICS_PATH = ARTIFACT_DIR / "forecast_metrics.json"

TARGET = "irradiance_kwh_m2"
CITY_COLUMNS = {city: "city_" + city.lower().replace(" ", "_") for city in CITIES}
FEATURES = [
    "lag1",
    "lag2",
    "roll7",
    "tmax_lag1",
    "rain_lag1",
    "doy_sin",
    "doy_cos",
    *CITY_COLUMNS.values(),
]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add model inputs using only information from EARLIER days (no leakage)."""
    out = df.copy()
    out["day"] = pd.to_datetime(out["day"])
    out = out.sort_values(["city", "day"]).reset_index(drop=True)
    by_city = out.groupby("city")

    out["lag1"] = by_city[TARGET].shift(1)
    out["lag2"] = by_city[TARGET].shift(2)
    out["roll7"] = by_city[TARGET].transform(lambda s: s.shift(1).rolling(7).mean())
    out["tmax_lag1"] = by_city["temp_max_c"].shift(1)
    out["rain_lag1"] = by_city["precipitation_mm"].shift(1)

    day_of_year = out["day"].dt.day_of_year
    out["doy_sin"] = np.sin(2 * np.pi * day_of_year / 365.25)
    out["doy_cos"] = np.cos(2 * np.pi * day_of_year / 365.25)

    for city, column in CITY_COLUMNS.items():
        out[column] = (out["city"] == city).astype(int)
    return out


def forecast_next(history: pd.DataFrame, city: str, model: Any) -> tuple[date, float]:
    """Predict the day after the last day in `history` for one city."""
    target_day = pd.to_datetime(history["day"]).max() + timedelta(days=1)
    blank = {
        "city": city,
        "day": target_day,
        TARGET: np.nan,
        "temp_max_c": np.nan,
        "precipitation_mm": np.nan,
    }
    frame = build_features(
        pd.concat([history, pd.DataFrame([blank])], ignore_index=True)
    )
    row = frame.loc[frame["day"] == target_day, FEATURES]
    if row.isna().to_numpy().any():
        raise ValueError("Not enough recent history to forecast.")
    prediction = max(0.0, float(model.predict(row)[0]))  # sunlight is never negative
    return target_day.date(), round(prediction, 2)


@lru_cache
def load_model() -> Any:
    return joblib.load(MODEL_PATH)["model"]


@lru_cache
def load_metrics() -> dict[str, Any]:
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
