// Typed client for the Python Core CSV profiler (mirrors backend/app/schemas/profile.py).

export interface ColumnSummary {
  name: string;
  kind: "numeric" | "date" | "text" | "empty";
  missing: number;
  missing_pct: number;
  unique: string;
  minimum: number | null;
  maximum: number | null;
  mean: number | null;
}

export interface ProfileResponse {
  rows: number;
  duplicate_rows: number;
  columns: ColumnSummary[];
}

export async function profileCsv(file: File): Promise<ProfileResponse> {
  const form = new FormData();
  form.append("file", file);

  const response = await fetch("/api/python-core/profile", { method: "POST", body: form });
  if (!response.ok) {
    // Our API returns short, safe messages for 400/413; anything else stays generic.
    const body = await response.json().catch(() => null);
    const message =
      (response.status === 400 || response.status === 413) && typeof body?.detail === "string"
        ? body.detail
        : "Could not analyse this file right now. Please try again.";
    throw new Error(message);
  }
  return response.json();
}
