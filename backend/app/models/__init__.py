"""Import every model here so Alembic can find all tables."""

from app.models.weather import WeatherDaily

__all__ = ["WeatherDaily"]
