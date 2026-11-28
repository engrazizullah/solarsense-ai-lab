"use client";

import { useEffect, useState } from "react";

import { type CitySummary, type WeatherDay, getDaily, getSummary } from "@/lib/weather";

export default function DataPipelinePage() {
  const [cities, setCities] = useState<CitySummary[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [days, setDays] = useState<WeatherDay[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSummary()
      .then((data) => {
        setCities(data);
        if (data.length > 0) setSelected(data[0].city);
      })
      .catch(() => setError("Could not load weather data right now."));
  }, []);

  useEffect(() => {
    if (!selected) return;
    let cancelled = false;
    getDaily(selected)
      .then((data) => {
        if (!cancelled) setDays(data);
      })
      .catch(() => {
        if (!cancelled) setError("Could not load this city right now.");
      });
    return () => {
      cancelled = true;
    };
  }, [selected]);

  const max = Math.max(1, ...days.map((d) => d.irradiance_kwh_m2 ?? 0));

  return (
    <main className="mx-auto max-w-5xl p-6 md:p-10">
      <h1 className="text-3xl font-bold">Data pipeline: daily sunlight</h1>
      <p className="mt-2 text-gray-600 dark:text-gray-300">
        Fetched every morning from the Open-Meteo archive API, converted from MJ/m² to
        kWh/m², and upserted into PostgreSQL (one row per city per day — never duplicated).
      </p>

      {error && (
        <p role="alert" className="mt-6 rounded-lg border border-red-400 p-3">
          {error}
        </p>
      )}

      <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {cities.map((c) => (
          <button
            key={c.city}
            type="button"
            aria-pressed={selected === c.city}
            onClick={() => setSelected(c.city)}
            className={`rounded-xl border p-4 text-left ${
              selected === c.city ? "border-2 border-gray-900 dark:border-white" : ""
            }`}
          >
            <span className="block font-semibold">{c.city}</span>
            <span className="mt-1 block text-2xl font-bold">
              {c.avg_irradiance_kwh_m2 ?? "—"}
            </span>
            <span className="block text-xs text-gray-500">
              avg kWh/m²/day · {c.days} days · to {c.latest_day ?? "—"}
            </span>
          </button>
        ))}
      </div>

      {selected && days.length > 0 && (
        <section aria-labelledby="chart-heading" className="mt-8">
          <h2 id="chart-heading" className="text-xl font-semibold">
            {selected}: last {days.length} days
          </h2>
          <div className="mt-4 flex h-48 items-end gap-1" role="img" aria-label={`Daily sunlight for ${selected}`}>
            {days.map((d) => (
              <div
                key={d.day}
                title={`${d.day}: ${d.irradiance_kwh_m2 ?? "no data"} kWh/m²`}
                className="flex-1 rounded-t bg-amber-500"
                style={{ height: `${((d.irradiance_kwh_m2 ?? 0) / max) * 100}%` }}
              />
            ))}
          </div>
          <p className="mt-2 text-xs text-gray-500">
            {days[0].day} → {days[days.length - 1].day} · hover a bar for the value
          </p>
        </section>
      )}
    </main>
  );
}
