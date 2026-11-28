from datetime import date

from pydantic import BaseModel


class NextForecast(BaseModel):
    city: str
    day: date
    irradiance_kwh_m2: float
