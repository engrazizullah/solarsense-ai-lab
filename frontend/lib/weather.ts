// Typed client for the Data Pipeline API (mirrors backend/app/schemas/weather.py).

export interface CitySummary {
  city: string;
  days: number;
  avg_irradiance_kwh_m2: number | null;
  latest_day: string | null;
}

export interface WeatherDay {
  day: string;
  irradiance_kwh_m2: number | null;
  temp_max_c: number | null;
  temp_min_c: number | null;
  precipitation_mm: number | null;
}

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Weather API failed with status ${response.status}`);
  return response.json();
}

export const getSummary = () => getJson<CitySummary[]>("/api/weather/summary");

export const getDaily = (city: string, days = 30) =>
  getJson<WeatherDay[]>(
    `/api/weather/daily?city=${encodeURIComponent(city)}&days=${days}`,
  );
