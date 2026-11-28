"""Weather API checks that need no database."""

from fastapi.testclient import TestClient

from app.db.session import get_session
from app.main import app


def test_unknown_city_returns_404() -> None:
    app.dependency_overrides[get_session] = lambda: None
    try:
        response = TestClient(app).get(
            "/api/weather/daily", params={"city": "Atlantis"}
        )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
