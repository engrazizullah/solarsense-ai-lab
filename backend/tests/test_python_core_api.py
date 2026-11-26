"""API tests for the CSV profiler upload."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
SAMPLE = Path(__file__).parent / "data" / "sample_readings.csv"
URL = "/api/python-core/profile"


def test_upload_sample_returns_report() -> None:
    with SAMPLE.open("rb") as f:
        response = client.post(URL, files={"file": ("readings.csv", f, "text/csv")})

    assert response.status_code == 200
    body = response.json()
    assert body["rows"] == 6
    assert body["duplicate_rows"] == 1


def test_non_csv_is_rejected() -> None:
    response = client.post(URL, files={"file": ("notes.txt", b"hello", "text/plain")})
    assert response.status_code == 400


def test_file_over_5mb_is_rejected() -> None:
    big = b"a,b\n" + b"1,2\n" * (1_400_000)  # about 5.6 MB
    response = client.post(URL, files={"file": ("big.csv", big, "text/csv")})
    assert response.status_code == 413


def test_non_utf8_file_is_rejected_with_generic_message() -> None:
    bad = b"name\n\xff\xfe\xfa\n"
    response = client.post(URL, files={"file": ("bad.csv", bad, "text/csv")})
    assert response.status_code == 400
    assert "Traceback" not in response.text
