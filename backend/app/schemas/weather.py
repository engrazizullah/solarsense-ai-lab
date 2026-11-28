"""Response shapes for stored weather data."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class WeatherDay(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    day: date
    irradiance_kwh_m2: float | None
    temp_max_c: float | None
    temp_min_c: float | None
    precipitation_mm: float | None


class CitySummary(BaseModel):
    city: str
    days: int
    avg_irradiance_kwh_m2: float | None
    latest_day: date | None
