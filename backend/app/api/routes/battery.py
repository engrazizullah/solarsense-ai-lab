"""Battery Calculator endpoints."""

from fastapi import APIRouter

from app.schemas.battery import BatteryRequest, BatteryResult
from app.services.battery import size_battery

router = APIRouter(prefix="/api/battery", tags=["Battery Calculator"])


@router.post("/size", response_model=BatteryResult)
def size(request: BatteryRequest) -> BatteryResult:
    """Size a battery bank for a given load and backup time."""
    return size_battery(request)
