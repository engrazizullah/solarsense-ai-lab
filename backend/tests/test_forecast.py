from datetime import date, timedelta

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.db.session import get_session
from app.main import app
from app.ml.forecast import build_features, forecast_next

client = TestClient(app)


def make_history(days: int) -> pd.DataFrame:
    start = date(2026, 1, 1)
    return pd.DataFrame(
        {
            "city": "Lahore",
            "day": [start + timedelta(days=i) for i in range(days)],
            "irradiance_kwh_m2": [float(i + 1) for i in range(days)],  # 1, 2, 3...
            "temp_max_c": 30.0,
            "precipitation_mm": 0.0,
        }
    )


class FakeModel:
    """Stands in for the real model and remembers the row it was given."""

    def __init__(self, output: float) -> None:
        self.output = output
        self.seen = None

    def predict(self, rows):
        self.seen = rows
        return [self.output]


def test_features_use_only_past_days():
    feats = build_features(make_history(10))
    row = feats.iloc[7]  # the 8th day, whose own value is 8.0
    assert row["lag1"] == 7.0  # yesterday, not today
    assert row["roll7"] == pytest.approx(4.0)  # mean of 1..7, today excluded


def test_forecast_next_predicts_the_following_day():
    model = FakeModel(output=4.567)
    day, value = forecast_next(make_history(10), "Lahore", model)
    assert day == date(2026, 1, 11)
    assert value == 4.57  # rounded to 2 decimals
    assert model.seen["lag1"].iloc[0] == 10.0
    assert model.seen["roll7"].iloc[0] == pytest.approx(7.0)  # mean of 4..10


def test_forecast_never_negative():
    _, value = forecast_next(make_history(10), "Lahore", FakeModel(output=-0.3))
    assert value == 0.0


def test_forecast_needs_enough_history():
    with pytest.raises(ValueError):
        forecast_next(make_history(5), "Lahore", FakeModel(output=1.0))


def test_metrics_endpoint():
    response = client.get("/api/forecast/metrics")
    assert response.status_code == 200
    assert response.json()["best_model"] == "Linear regression"


def test_next_unknown_city_is_404():
    # No database in CI: swap the real session for a dummy (dependency injection).
    app.dependency_overrides[get_session] = lambda: None
    try:
        response = client.get("/api/forecast/next", params={"city": "Paris"})
    finally:
        app.dependency_overrides.pop(get_session, None)  # don't leak into other tests
    assert response.status_code == 404
