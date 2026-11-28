export type ModelResult = {
  name: string;
  mae: number;
  rmse: number;
  r2: number;
  skill_pct: number;
};

export type SamplePoint = {
  day: string;
  actual: number;
  predicted: number;
  baseline: number;
};

export type ForecastMetrics = {
  trained_at: string;
  train_period: [string, string];
  test_period: [string, string];
  n_train: number;
  n_test: number;
  features: string[];
  results: ModelResult[];
  best_model: string;
  samples: Record<string, SamplePoint[]>;
};

export type NextForecast = {
  city: string;
  day: string;
  irradiance_kwh_m2: number;
};

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return (await res.json()) as T;
}

export function fetchForecastMetrics(): Promise<ForecastMetrics> {
  return getJson<ForecastMetrics>("/api/forecast/metrics");
}

export function fetchNextForecast(city: string): Promise<NextForecast> {
  return getJson<NextForecast>(`/api/forecast/next?city=${encodeURIComponent(city)}`);
}
