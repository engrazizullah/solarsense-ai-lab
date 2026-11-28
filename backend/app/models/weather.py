"""Daily weather and sunlight per city, filled by the data pipeline."""

from datetime import date, datetime

from sqlalchemy import DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WeatherDaily(Base):
    __tablename__ = "weather_daily"
    __table_args__ = (UniqueConstraint("city", "day", name="uq_weather_city_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(80))
    day: Mapped[date]
    irradiance_kwh_m2: Mapped[float | None]
    temp_max_c: Mapped[float | None]
    temp_min_c: Mapped[float | None]
    precipitation_mm: Mapped[float | None]
    source: Mapped[str] = mapped_column(String(40), default="open-meteo")
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
