"use client";

import { useEffect, useState } from "react";

import {
  fetchForecastMetrics,
  fetchNextForecast,
  type ForecastMetrics,
  type NextForecast,
  type SamplePoint,
} from "@/lib/forecast";

const W = 640;
const H = 240;
const PAD = 32;

type SeriesKey = "actual" | "predicted" | "baseline";

function Chart({ points }: { points: SamplePoint[] }) {
  const max = Math.max(1, ...points.flatMap((p) => [p.actual, p.predicted, p.baseline]));
  const x = (i: number) => PAD + (i * (W - 2 * PAD)) / Math.max(points.length - 1, 1);
  const y = (v: number) => H - PAD - (v / max) * (H - 2 * PAD);
  const line = (key: SeriesKey) => points.map((p, i) => `${x(i)},${y(p[key])}`).join(" ");

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full" role="img" aria-label="Actual vs predicted sunlight">
      <line x1={PAD} y1={H - PAD} x2={W - PAD} y2={H - PAD} stroke="currentColor" strokeOpacity={0.3} />
      <polyline fill="none" stroke="#9ca3af" strokeWidth={1.5} strokeDasharray="4 4" points={line("baseline")} />
      <polyline fill="none" stroke="currentColor" strokeWidth={2} points={line("actual")} />
      <polyline fill="none" stroke="#2563eb" strokeWidth={2} points={line("predicted")} />
      <text x={PAD} y={PAD - 10} fontSize={11} fill="currentColor">
        {max.toFixed(1)} kWh/m²
      </text>
      <text x={PAD} y={H - 8} fontSize={11} fill="currentColor">
        {points[0]?.day}
      </text>
      <text x={W - PAD} y={H - 8} fontSize={11} fill="currentColor" textAnchor="end">
        {points.at(-1)?.day}
      </text>
    </svg>
  );
}

export default function ForecastPage() {
  const [metrics, setMetrics] = useState<ForecastMetrics | null>(null);
  const [next, setNext] = useState<NextForecast[]>([]);
  const [city, setCity] = useState("Lahore");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchForecastMetrics()
      .then(async (m) => {
        const results = await Promise.allSettled(
          Object.keys(m.samples).map((c) => fetchNextForecast(c)),
        );
        if (cancelled) return;
        setMetrics(m);
        setNext(
          results
            .filter((r): r is PromiseFulfilledResult<NextForecast> => r.status === "fulfilled")
            .map((r) => r.value),
        );
      })
      .catch(() => {
        if (!cancelled) setError("Forecast is not available right now.");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) return <main className="mx-auto max-w-4xl p-8 text-red-600">{error}</main>;
  if (!metrics) return <main className="mx-auto max-w-4xl p-8">Loading forecast…</main>;

  const points = metrics.samples[city] ?? [];

  return (
    <main className="mx-auto max-w-4xl space-y-10 p-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">Solar Forecast</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Next-day sunlight (kWh/m²) for 5 Pakistani cities, trained on 3 years of Open-Meteo data.
        </p>
      </header>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Next day</h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
          {next.map((f) => (
            <div key={f.city} className="rounded-lg border p-4">
              <div className="text-sm text-gray-500">{f.city}</div>
              <div className="text-2xl font-bold">{f.irradiance_kwh_m2.toFixed(2)}</div>
              <div className="text-xs text-gray-500">{f.day}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Model comparison (test year)</h2>
        <p className="text-sm text-gray-500">
          Train {metrics.train_period[0]} → {metrics.train_period[1]} ({metrics.n_train} rows) · Test{" "}
          {metrics.test_period[0]} → {metrics.test_period[1]} ({metrics.n_test} rows)
        </p>
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b">
              <th className="py-2">Model</th>
              <th>MAE</th>
              <th>RMSE</th>
              <th>R²</th>
              <th>Skill vs baseline</th>
            </tr>
          </thead>
          <tbody>
            {metrics.results.map((r) => (
              <tr
                key={r.name}
                className={`border-b ${r.name === metrics.best_model ? "font-semibold text-blue-600" : ""}`}
              >
                <td className="py-2">
                  {r.name}
                  {r.name === metrics.best_model ? " ✓" : ""}
                </td>
                <td>{r.mae.toFixed(3)}</td>
                <td>{r.rmse.toFixed(3)}</td>
                <td>{r.r2.toFixed(3)}</td>
                <td>{`${r.skill_pct > 0 ? "+" : ""}${r.skill_pct.toFixed(1)}%`}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Actual vs predicted (last 60 test days)</h2>
        <div className="flex flex-wrap gap-2">
          {Object.keys(metrics.samples).map((c) => (
            <button
              key={c}
              onClick={() => setCity(c)}
              className={`rounded-full border px-3 py-1 text-sm ${c === city ? "bg-blue-600 text-white" : ""}`}
            >
              {c}
            </button>
          ))}
        </div>
        <Chart points={points} />
        <div className="flex gap-6 text-sm">
          <span>━ Actual</span>
          <span className="text-blue-600">━ Predicted</span>
          <span className="text-gray-400">┅ Baseline (tomorrow = today)</span>
        </div>
      </section>
    </main>
  );
}
