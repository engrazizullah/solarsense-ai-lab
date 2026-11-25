"use client";

import { useEffect, useState } from "react";

import { type BatteryResult, type Chemistry, sizeBattery } from "@/lib/battery";

const APPLIANCES = [
  { name: "Ceiling fan", watts: 80 },
  { name: "LED bulb", watts: 12 },
  { name: "Refrigerator", watts: 150 },
  { name: "LED TV", watts: 100 },
  { name: "Wi-Fi router + laptop", watts: 60 },
  { name: "Water pump (1 HP)", watts: 750 },
  { name: "Inverter AC (1.5 ton)", watts: 1200 },
];

const CHEMISTRIES: { id: Chemistry; label: string }[] = [
  { id: "lead_acid", label: "Lead-acid" },
  { id: "lifepo4", label: "Lithium (LiFePO4)" },
  { id: "sodium_ion", label: "Sodium-ion" },
];

const VOLTAGES = [12, 24, 48] as const;
type Voltage = (typeof VOLTAGES)[number];

export default function BatteryPage() {
  const [counts, setCounts] = useState<number[]>([3, 6, 1, 1, 1, 0, 0]);
  const [hours, setHours] = useState(4);
  const [voltage, setVoltage] = useState<Voltage>(24);
  const [results, setResults] = useState<BatteryResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = APPLIANCES.reduce((sum, item, i) => sum + item.watts * counts[i], 0);

  // Ask the API for all three chemistries whenever load, hours or voltage change.
  useEffect(() => {
    if (load === 0) return;
    let cancelled = false;
    Promise.all(
      CHEMISTRIES.map((c) =>
        sizeBattery({
          load_watts: load,
          backup_hours: hours,
          system_voltage: voltage,
          chemistry: c.id,
        }),
      ),
    )
      .then((data) => {
        if (!cancelled) {
          setResults(data);
          setError(null);
        }
      })
      .catch(() => {
        if (!cancelled) setError("Could not calculate right now. Please try again.");
      });
    return () => {
      cancelled = true;
    };
  }, [load, hours, voltage]);

  function change(index: number, delta: number) {
    setCounts((prev) =>
      prev.map((c, i) => (i === index ? Math.min(20, Math.max(0, c + delta)) : c)),
    );
  }

  const shown = load === 0 ? [] : results;

  return (
    <main className="mx-auto max-w-5xl p-6 md:p-10">
      <h1 className="text-3xl font-bold">How much battery do I need?</h1>
      <p className="mt-2 text-gray-600 dark:text-gray-300">
        Pick what you want to run during load-shedding and for how long.
      </p>

      <div className="mt-8 grid gap-8 md:grid-cols-2">
        <section aria-labelledby="load-heading">
          <h2 id="load-heading" className="text-xl font-semibold">
            1 · Your load
          </h2>
          <ul className="mt-4 divide-y divide-gray-200 dark:divide-gray-700">
            {APPLIANCES.map((item, i) => (
              <li key={item.name} className="flex items-center justify-between py-3">
                <span>
                  {item.name}{" "}
                  <span className="text-sm text-gray-500">({item.watts} W)</span>
                </span>
                <span className="flex items-center gap-2">
                  <button
                    type="button"
                    aria-label={`Fewer ${item.name}`}
                    onClick={() => change(i, -1)}
                    className="h-11 w-11 rounded-lg border text-xl"
                  >
                    −
                  </button>
                  <span className="w-6 text-center font-semibold">{counts[i]}</span>
                  <button
                    type="button"
                    aria-label={`More ${item.name}`}
                    onClick={() => change(i, 1)}
                    className="h-11 w-11 rounded-lg border text-xl"
                  >
                    +
                  </button>
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-4 font-semibold">Total load: {load} W</p>

          <label htmlFor="hours" className="mt-6 block font-semibold">
            2 · Backup time: {hours} h
          </label>
          <input
            id="hours"
            type="range"
            min={1}
            max={12}
            value={hours}
            onChange={(e) => setHours(Number(e.target.value))}
            className="mt-2 w-full"
          />

          <p className="mt-6 font-semibold">3 · System voltage</p>
          <div className="mt-2 flex gap-2">
            {VOLTAGES.map((v) => (
              <button
                key={v}
                type="button"
                aria-pressed={voltage === v}
                onClick={() => setVoltage(v)}
                className={`h-11 rounded-lg border px-4 font-semibold ${
                  voltage === v ? "bg-gray-900 text-white dark:bg-white dark:text-gray-900" : ""
                }`}
              >
                {v} V
              </button>
            ))}
          </div>
        </section>

        <section aria-labelledby="result-heading">
          <h2 id="result-heading" className="text-xl font-semibold">
            Battery bank needed
          </h2>
          {error && (
            <p role="alert" className="mt-4 rounded-lg border border-red-400 p-3">
              {error}
            </p>
          )}
          {load === 0 && <p className="mt-4">Add at least one appliance to start.</p>}
          <div className="mt-4 grid gap-4">
            {shown.map((r, i) => (
              <article key={r.chemistry} className="rounded-xl border p-4">
                <h3 className="font-semibold">{CHEMISTRIES[i].label}</h3>
                <p className="mt-1 text-2xl font-bold">
                  {Math.ceil(r.battery_ah)} Ah @ {voltage} V
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  {(r.battery_wh / 1000).toFixed(1)} kWh bank · usable depth{" "}
                  {Math.round(r.usable_depth * 100)}% · ≈ {r.units_12v_100ah} × 12 V 100 Ah
                </p>
              </article>
            ))}
          </div>
          <p className="mt-6 text-sm text-gray-500">
            Estimates only. Always follow the battery and inverter datasheets.
          </p>
        </section>
      </div>
    </main>
  );
}
