"""Fetch daily weather and sunlight from the Open-Meteo archive API."""

from dataclasses import dataclass
from datetime import date

import httpx2

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
DAILY_VARIABLES = (
    "shortwave_radiation_sum,temperature_2m_max,temperature_2m_min,precipitation_sum"
)
MJ_PER_KWH = 3.6  # 1 kWh = 3.6 MJ

# Approximate city-centre coordinates (latitude, longitude).
CITIES: dict[str, tuple[float, float]] = {
    "Rahim Yar Khan": (28.42, 70.30),
    "Lahore": (31.55, 74.34),
    "Karachi": (24.86, 67.01),
    "Multan": (30.20, 71.47),
    "Islamabad": (33.69, 73.06),
}


class WeatherFetchError(Exception):
    """Open-Meteo could not be reached or returned unusable data."""


@dataclass(frozen=True)
class DailyWeather:
    city: str
    day: date
    irradiance_kwh_m2: float | None
    temp_max_c: float | None
    temp_min_c: float | None
    precipitation_mm: float | None


def parse_daily(city: str, daily: dict[str, list]) -> list[DailyWeather]:
    """Turn Open-Meteo's parallel lists into one record per day."""
    rows = []
    for day, radiation, t_max, t_min, rain in zip(
        daily["time"],
        daily["shortwave_radiation_sum"],
        daily["temperature_2m_max"],
        daily["temperature_2m_min"],
        daily["precipitation_sum"],
        strict=True,
    ):
        irradiance = None if radiation is None else round(radiation / MJ_PER_KWH, 3)
        rows.append(
            DailyWeather(city, date.fromisoformat(day), irradiance, t_max, t_min, rain)
        )
    return rows


def fetch_daily(
    city: str, start: date, end: date, client: httpx2.Client | None = None
) -> list[DailyWeather]:
    """Fetch one city's daily weather between two dates (inclusive)."""
    latitude, longitude = CITIES[city]
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": DAILY_VARIABLES,
        "timezone": "Asia/Karachi",
    }
    own_client = client is None
    http = client or httpx2.Client(timeout=10.0)
    try:
        response = http.get(ARCHIVE_URL, params=params)
        response.raise_for_status()
        return parse_daily(city, response.json()["daily"])
    except (httpx2.HTTPError, KeyError, ValueError) as exc:
        raise WeatherFetchError(f"Open-Meteo request failed for {city}") from exc
    finally:
        if own_client:
            http.close()
