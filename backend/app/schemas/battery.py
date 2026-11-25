"""Input and output shapes for the battery backup calculator."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class Chemistry(StrEnum):
    LEAD_ACID = "lead_acid"
    LIFEPO4 = "lifepo4"
    SODIUM_ION = "sodium_ion"


class BatteryRequest(BaseModel):
    load_watts: float = Field(
        gt=0, le=50_000, description="Total running load in watts"
    )
    backup_hours: float = Field(gt=0, le=48, description="Hours of backup needed")
    system_voltage: Literal[12, 24, 48] = 24
    chemistry: Chemistry = Chemistry.LIFEPO4
    inverter_efficiency: float = Field(default=0.9, gt=0, le=1)


class BatteryResult(BaseModel):
    chemistry: Chemistry
    energy_needed_wh: float
    battery_wh: float
    battery_ah: float
    usable_depth: float
    battery_efficiency: float
    units_12v_100ah: int
