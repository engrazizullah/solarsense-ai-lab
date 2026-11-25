"""Battery bank sizing — pure calculation, no web code."""

import math
from dataclasses import dataclass

from app.schemas.battery import BatteryRequest, BatteryResult, Chemistry


@dataclass(frozen=True)
class ChemistrySpec:
    usable_depth: float  # share of capacity we can safely use (depth of discharge)
    efficiency: float  # round-trip battery efficiency


# Typical values for estimates only; real designs follow the battery datasheet.
CHEMISTRY_SPECS: dict[Chemistry, ChemistrySpec] = {
    Chemistry.LEAD_ACID: ChemistrySpec(usable_depth=0.5, efficiency=0.80),
    Chemistry.LIFEPO4: ChemistrySpec(usable_depth=0.9, efficiency=0.95),
    Chemistry.SODIUM_ION: ChemistrySpec(usable_depth=0.9, efficiency=0.92),
}

UNIT_WH = 12 * 100  # one 12 V 100 Ah battery = 1,200 Wh


def size_battery(request: BatteryRequest) -> BatteryResult:
    """Return the battery bank needed to run a load for the requested hours."""
    spec = CHEMISTRY_SPECS[request.chemistry]

    energy_needed_wh = request.load_watts * request.backup_hours
    total_efficiency = request.inverter_efficiency * spec.efficiency * spec.usable_depth
    battery_wh = energy_needed_wh / total_efficiency
    battery_ah = battery_wh / request.system_voltage

    # 12 V units go in series strings: 24 V needs 2 per string, 48 V needs 4.
    per_string = request.system_voltage // 12
    units = math.ceil(battery_wh / UNIT_WH / per_string) * per_string

    return BatteryResult(
        chemistry=request.chemistry,
        energy_needed_wh=round(energy_needed_wh, 1),
        battery_wh=round(battery_wh, 1),
        battery_ah=round(battery_ah, 1),
        usable_depth=spec.usable_depth,
        battery_efficiency=spec.efficiency,
        units_12v_100ah=units,
    )
