"use client";

import { useState } from "react";

import { type ProfileResponse, profileCsv } from "@/lib/pythonCore";

function fmt(value: number | null): string {
  return value === null ? "—" : value.toLocaleString(undefined, { maximumFractionDigits: 3 });
}

export default function PythonCorePage() {
  const [file, setFile] = useState<File | null>(null);
  const [report, setReport] = useState<ProfileResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function analyse(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      setReport(await profileCsv(file));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-5xl p-6 md:p-10">
      <h1 className="text-3xl font-bold">CSV data-quality report</h1>
      <p className="mt-2 text-gray-600 dark:text-gray-300">
        Upload a CSV (max 5 MB). Built in plain Python with generators, a dataclass and a
        decorator — then checked against Pandas.
      </p>
      <p className="mt-1 text-sm">
        No file handy?{" "}
        <a href="/samples/sample_readings.csv" download className="underline">
          Download a sample CSV
        </a>
      </p>

      <form onSubmit={analyse} className="mt-6 flex flex-wrap items-center gap-3">
        <label htmlFor="csv" className="sr-only">
          CSV file
        </label>
        <input
          id="csv"
          type="file"
          accept=".csv,text/csv"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="rounded-lg border p-2"
        />
        <button
          type="submit"
          disabled={!file || loading}
          className="h-11 rounded-lg bg-gray-900 px-5 font-semibold text-white disabled:opacity-50 dark:bg-white dark:text-gray-900"
        >
          {loading ? "Analysing…" : "Analyse"}
        </button>
      </form>

      {error && (
        <p role="alert" className="mt-6 rounded-lg border border-red-400 p-3">
          {error}
        </p>
      )}

      {report && (
        <section aria-labelledby="report-heading" className="mt-8">
          <h2 id="report-heading" className="text-xl font-semibold">
            Report
          </h2>
          <p className="mt-2">
            <strong>{report.rows.toLocaleString()}</strong> rows ·{" "}
            <strong>{report.duplicate_rows.toLocaleString()}</strong> duplicate rows ·{" "}
            <strong>{report.columns.length}</strong> columns
          </p>
          <div className="mt-4 overflow-x-auto rounded-xl border">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-100 dark:bg-gray-800">
                <tr>
                  <th className="p-3">Column</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Missing</th>
                  <th className="p-3">Unique</th>
                  <th className="p-3">Min</th>
                  <th className="p-3">Max</th>
                  <th className="p-3">Mean</th>
                </tr>
              </thead>
              <tbody>
                {report.columns.map((c) => (
                  <tr key={c.name} className="border-t">
                    <td className="p-3 font-medium">{c.name}</td>
                    <td className="p-3">{c.kind}</td>
                    <td className="p-3">
                      {c.missing} ({c.missing_pct}%)
                    </td>
                    <td className="p-3">{c.unique}</td>
                    <td className="p-3">{fmt(c.minimum)}</td>
                    <td className="p-3">{fmt(c.maximum)}</td>
                    <td className="p-3">{fmt(c.mean)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </main>
  );
}
