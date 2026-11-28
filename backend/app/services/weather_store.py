"""Save daily weather to PostgreSQL with an idempotent upsert."""

from dataclasses import asdict

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.weather import WeatherDaily
from app.services.open_meteo import DailyWeather

VALUE_COLUMNS = ("irradiance_kwh_m2", "temp_max_c", "temp_min_c", "precipitation_mm")


def upsert_weather(session: Session, rows: list[DailyWeather]) -> int:
    """Insert new (city, day) rows; update existing ones. Returns rows processed."""
    if not rows:
        return 0
    table = WeatherDaily.__table__
    stmt = insert(table).values([asdict(row) for row in rows])
    updates = {
        name: func.coalesce(
            stmt.excluded[name], table.c[name]
        )  # never overwrite with null
        for name in VALUE_COLUMNS
    }
    updates["fetched_at"] = func.now()
    stmt = stmt.on_conflict_do_update(constraint="uq_weather_city_day", set_=updates)
    session.execute(stmt)
    session.commit()
    return len(rows)
