"""ETL job: fetch recent weather for every city and upsert it."""

import logging
from datetime import date, timedelta

import httpx2
from sqlalchemy.orm import Session

from app.services.open_meteo import CITIES, WeatherFetchError, fetch_daily
from app.services.weather_store import upsert_weather

logger = logging.getLogger(__name__)


def run_pipeline(
    session: Session,
    days: int = 10,
    end: date | None = None,
    client: httpx2.Client | None = None,
) -> dict[str, int]:
    """Fetch the last `days` days per city. One failing city never stops the rest."""
    end = end or date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    results: dict[str, int] = {}
    for city in CITIES:
        try:
            rows = fetch_daily(city, start, end, client)
            results[city] = upsert_weather(session, rows)
        except WeatherFetchError:
            logger.warning("Skipped %s: weather fetch failed", city)
            results[city] = 0
    return results
