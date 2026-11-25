"""API tests for the Battery Calculator endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_size_returns_200_and_result() -> None:
    response = client.post(
        "/api/battery/size",
        json={"load_watts": 600, "backup_hours": 4, "chemistry": "lead_acid"},
    )

    assert response.status_code == 200
    assert response.json()["units_12v_100ah"] == 6


def test_negative_load_is_rejected() -> None:
    response = client.post(
        "/api/battery/size", json={"load_watts": -50, "backup_hours": 4}
    )

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["loc"] == ["body", "load_watts"]
