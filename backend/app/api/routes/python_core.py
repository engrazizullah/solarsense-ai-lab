"""Python Core endpoints: CSV data-quality report."""

import csv
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.schemas.profile import ProfileResponse
from app.services.profiler import CsvProfiler

router = APIRouter(prefix="/api/python-core", tags=["Python Core"])

MAX_BYTES = 5 * 1024 * 1024  # 5 MB
CHUNK_BYTES = 64 * 1024


@router.post("/profile", response_model=ProfileResponse)
async def profile_csv(file: UploadFile) -> ProfileResponse:
    """Upload a CSV (max 5 MB) and get a data-quality report."""
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")

    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "upload.csv"  # never trust the user's filename
        size = 0
        with path.open("wb") as out:
            while chunk := await file.read(CHUNK_BYTES):
                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(status_code=413, detail="File is over 5 MB.")
                out.write(chunk)

        try:
            report = await run_in_threadpool(CsvProfiler(path).profile)
        except (UnicodeDecodeError, csv.Error):
            raise HTTPException(
                status_code=400, detail="Could not read this file as a UTF-8 CSV."
            ) from None

    return ProfileResponse.from_report(report)
