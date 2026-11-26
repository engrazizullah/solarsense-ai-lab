"""SolarSense AI Lab — FastAPI entry point."""

from fastapi import FastAPI

from app.api.routes import battery, python_core

app = FastAPI(title="SolarSense AI Lab API", version="0.1.0")
app.include_router(battery.router)
app.include_router(python_core.router)  # NEW


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple status so CI and the server can check the API is alive."""
    return {"status": "ok"}
