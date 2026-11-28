"""Forecast endpoints: model metrics + next-day prediction per city."""

import logging
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.ml.forecast import forecast_next, load_metrics, load_model
from app.models.weather import WeatherDaily
from app.schemas.forecast import NextForecast
from app.services.open_meteo import CITIES

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/forecast", tags=["Forecast"])

HISTORY_DAYS = 14  # needs 8+ days for lag + 7-day rolling mean


@router.get("/metrics")
def get_metrics() -> dict[str, Any]:
    try:
        return load_metrics()
    except FileNotFoundError:
        raise HTTPException(503, "Forecast model is not available.") from None


@router.get("/next", response_model=NextForecast)
def get_next(city: str, session: Session = Depends(get_session)) -> NextForecast:
    if city not in CITIES:
        raise HTTPException(404, "Unknown city.")
    stmt = (
        select(
            WeatherDaily.city,
            WeatherDaily.day,
            WeatherDaily.irradiance_kwh_m2,
            WeatherDaily.temp_max_c,
            WeatherDaily.precipitation_mm,
        )
        .where(WeatherDaily.city == city)
        .order_by(WeatherDaily.day.desc())
        .limit(HISTORY_DAYS)
    )
    history = pd.DataFrame(session.execute(stmt).mappings().all())
    try:
        day, value = forecast_next(history, city, load_model())
    except (FileNotFoundError, ValueError, KeyError):
        logger.exception("Forecast failed for %s", city)  # details only in logs
        raise HTTPException(503, "Forecast is not available right now.") from None
    return NextForecast(city=city, day=day, irradiance_kwh_m2=value)
