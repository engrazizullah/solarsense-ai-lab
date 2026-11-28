"""Train and evaluate the next-day irradiance forecast.

Run from backend/:  uv run python -m scripts.train_forecast
"""

import json
import math
from datetime import UTC, datetime

import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sqlalchemy import select

from app.db.session import get_engine
from app.ml.forecast import (
    ARTIFACT_DIR,
    FEATURES,
    METRICS_PATH,
    MODEL_PATH,
    TARGET,
    build_features,
)
from app.models.weather import WeatherDaily

TEST_DAYS = 365  # newest year is the test set: unseen future, all 4 seasons


def load_data() -> pd.DataFrame:
    stmt = select(
        WeatherDaily.city,
        WeatherDaily.day,
        WeatherDaily.irradiance_kwh_m2,
        WeatherDaily.temp_max_c,
        WeatherDaily.precipitation_mm,
    )
    with get_engine().connect() as connection:
        return pd.read_sql(stmt, connection)


def score(name: str, y_true, y_pred, baseline_mae: float | None = None) -> dict:
    mae = mean_absolute_error(y_true, y_pred)
    skill = 0.0 if baseline_mae is None else 100 * (1 - mae / baseline_mae)
    return {
        "name": name,
        "mae": round(mae, 3),
        "rmse": round(math.sqrt(mean_squared_error(y_true, y_pred)), 3),
        "r2": round(r2_score(y_true, y_pred), 3),
        "skill_pct": round(skill, 1),
    }


def main() -> None:
    data = build_features(load_data()).dropna(subset=[*FEATURES, TARGET])
    cutoff = data["day"].max() - pd.Timedelta(days=TEST_DAYS)
    train, test = data[data["day"] <= cutoff], data[data["day"] > cutoff]

    baseline = score("Baseline: tomorrow = today", test[TARGET], test["lag1"])
    results = [baseline]
    candidates = {
        "Linear regression": LinearRegression(),
        "Gradient boosting": HistGradientBoostingRegressor(
            max_iter=300, learning_rate=0.05, random_state=42
        ),
    }
    for name, model in candidates.items():
        model.fit(train[FEATURES], train[TARGET])
        results.append(
            score(name, test[TARGET], model.predict(test[FEATURES]), baseline["mae"])
        )

    best = min(results[1:], key=lambda r: r["mae"])
    best_model = candidates[best["name"]]
    test = test.assign(predicted=best_model.predict(test[FEATURES]))
    samples = {
        city: [
            {
                "day": row.day.date().isoformat(),
                "actual": round(row.irradiance_kwh_m2, 2),
                "predicted": round(row.predicted, 2),
                "baseline": round(row.lag1, 2),
            }
            for row in group.tail(60).itertuples()
        ]
        for city, group in test.groupby("city")
    }

    ARTIFACT_DIR.mkdir(exist_ok=True)
    joblib.dump({"model": best_model, "features": FEATURES}, MODEL_PATH)
    metrics = {
        "trained_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "train_period": [
            str(train["day"].min().date()),
            str(train["day"].max().date()),
        ],
        "test_period": [str(test["day"].min().date()), str(test["day"].max().date())],
        "n_train": len(train),
        "n_test": len(test),
        "features": FEATURES,
        "results": results,
        "best_model": best["name"],
        "samples": samples,
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Train {metrics['train_period']} ({len(train)} rows)")
    print(f"Test  {metrics['test_period']} ({len(test)} rows)")
    for r in results:
        print(
            f"{r['name']:28} MAE {r['mae']:.3f}  RMSE {r['rmse']:.3f}"
            f"  R2 {r['r2']:.3f}  skill {r['skill_pct']:+.1f}%"
        )
    print(f"Saved best model: {best['name']}")


if __name__ == "__main__":
    main()
