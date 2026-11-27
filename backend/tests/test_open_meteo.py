"""Tests for the Open-Meteo client, using a fake transport (no internet)."""

from datetime import date

import httpx2
import pytest

from app.services.open_meteo import WeatherFetchError, fetch_daily

REAL_RESPONSE = {
    "daily": {
        "time": ["2026-06-01", "2026-06-02", "2026-06-03"],
        "shortwave_radiation_sum": [22.75, 23.81, None],
        "temperature_2m_max": [39.8, 40.1, 41.8],
        "temperature_2m_min": [30.9, 31.3, 30.2],
        "precipitation_sum": [0.0, 0.0, 0.0],
    }
}


def fake_client(status: int, payload: dict) -> httpx2.Client:
    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(status, json=payload)

    return httpx2.Client(transport=httpx2.MockTransport(handler))


def test_fetch_converts_mj_to_kwh_and_keeps_nulls() -> None:
    rows = fetch_daily(
        "Rahim Yar Khan",
        date(2026, 6, 1),
        date(2026, 6, 3),
        fake_client(200, REAL_RESPONSE),
    )

    assert len(rows) == 3
    assert rows[0].day == date(2026, 6, 1)
    assert rows[0].irradiance_kwh_m2 == pytest.approx(6.319, abs=0.001)
    assert rows[2].irradiance_kwh_m2 is None


def test_server_error_raises_clear_error() -> None:
    with pytest.raises(WeatherFetchError):
        fetch_daily("Lahore", date(2026, 6, 1), date(2026, 6, 3), fake_client(500, {}))


def test_mismatched_lists_raise_clear_error() -> None:
    broken = {"daily": {**REAL_RESPONSE["daily"], "temperature_2m_max": [39.8]}}
    with pytest.raises(WeatherFetchError):
        fetch_daily(
            "Lahore", date(2026, 6, 1), date(2026, 6, 3), fake_client(200, broken)
        )
