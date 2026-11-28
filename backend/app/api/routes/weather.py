"""Data Pipeline endpoints: read stored daily weather."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.weather import WeatherDaily
from app.schemas.weather import CitySummary, WeatherDay
from app.services.open_meteo import CITIES

router = APIRouter(prefix="/api/weather", tags=["Data Pipeline"])


@router.get("/summary", response_model=list[CitySummary])
def summary(session: Session = Depends(get_session)) -> list[CitySummary]:
    """Rows stored, average sunlight and latest day, per city."""
    stmt = (
        select(
            WeatherDaily.city,
            func.count(),
            func.avg(WeatherDaily.irradiance_kwh_m2),
            func.max(WeatherDaily.day),
        )
        .group_by(WeatherDaily.city)
        .order_by(WeatherDaily.city)
    )
    return [
        CitySummary(
            city=city,
            days=days,
            avg_irradiance_kwh_m2=None if avg is None else round(avg, 2),
            latest_day=latest,
        )
        for city, days, avg, latest in session.execute(stmt)
    ]


@router.get("/daily", response_model=list[WeatherDay])
def daily(
    city: str,
    days: int = Query(30, ge=1, le=365),
    session: Session = Depends(get_session),
) -> list[WeatherDaily]:
    """The most recent `days` days for one city, oldest first."""
    if city not in CITIES:
        raise HTTPException(status_code=404, detail="Unknown city.")
    stmt = (
        select(WeatherDaily)
        .where(WeatherDaily.city == city)
        .order_by(WeatherDaily.day.desc())
        .limit(days)
    )
    return list(reversed(session.scalars(stmt).all()))
