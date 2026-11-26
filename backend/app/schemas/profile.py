"""Response shapes for the Python Core CSV profiler."""

from pydantic import BaseModel

from app.services.profiler import ProfileReport


class ColumnSummary(BaseModel):
    name: str
    kind: str
    missing: int
    missing_pct: float
    unique: str
    minimum: float | None
    maximum: float | None
    mean: float | None


class ProfileResponse(BaseModel):
    rows: int
    duplicate_rows: int
    columns: list[ColumnSummary]

    @classmethod
    def from_report(cls, report: ProfileReport) -> "ProfileResponse":
        return cls(
            rows=report.rows,
            duplicate_rows=report.duplicate_rows,
            columns=[
                ColumnSummary(
                    name=c.name,
                    kind=c.kind,
                    missing=c.missing,
                    missing_pct=round(100 * c.missing / c.count, 1) if c.count else 0.0,
                    unique=c.unique_label,
                    minimum=c.minimum,
                    maximum=c.maximum,
                    mean=c.mean,
                )
                for c in report.columns
            ],
        )
