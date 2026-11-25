// Typed client for the Battery Calculator API (mirrors backend/app/schemas/battery.py).

export type Chemistry = "lead_acid" | "lifepo4" | "sodium_ion";

export interface BatteryRequest {
  load_watts: number;
  backup_hours: number;
  system_voltage: 12 | 24 | 48;
  chemistry: Chemistry;
}

export interface BatteryResult {
  chemistry: Chemistry;
  energy_needed_wh: number;
  battery_wh: number;
  battery_ah: number;
  usable_depth: number;
  battery_efficiency: number;
  units_12v_100ah: number;
}

export async function sizeBattery(request: BatteryRequest): Promise<BatteryResult> {
  const response = await fetch("/api/battery/size", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`Battery API failed with status ${response.status}`);
  }
  return response.json();
}
