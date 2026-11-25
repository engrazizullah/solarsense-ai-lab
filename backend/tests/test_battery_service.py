"""Tests for the battery sizing service."""

import pytest

from app.schemas.battery import BatteryRequest, Chemistry
from app.services.battery import size_battery


def test_lifepo4_600w_4h_24v() -> None:
    result = size_battery(BatteryRequest(load_watts=600, backup_hours=4))

    assert result.energy_needed_wh == 2400.0
    assert result.battery_wh == pytest.approx(3118.9, abs=0.1)
    assert result.battery_ah == pytest.approx(130.0, abs=0.1)
    assert result.units_12v_100ah == 4


def test_lead_acid_600w_4h_24v() -> None:
    result = size_battery(
        BatteryRequest(load_watts=600, backup_hours=4, chemistry=Chemistry.LEAD_ACID)
    )

    assert result.energy_needed_wh == 2400.0
    assert result.battery_wh == pytest.approx(6666.7, abs=0.1)
    assert result.battery_ah == pytest.approx(277.8, abs=0.1)
    assert result.units_12v_100ah == 6
