"""SolarSense AI Lab — FastAPI entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import battery, forecast, python_core, weather
from app.core.config import get_settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Start background jobs on startup; stop them cleanly on shutdown."""
    setup_logging()
    scheduler = None
    if get_settings().enable_scheduler:
        from app.core.scheduler import start_scheduler

        scheduler = start_scheduler()
    yield
    if scheduler is not None:
        scheduler.shutdown(wait=False)


app = FastAPI(title="SolarSense AI Lab API", version="0.1.0", lifespan=lifespan)
app.include_router(battery.router)
app.include_router(python_core.router)
app.include_router(weather.router)
app.include_router(forecast.router)


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple status so CI and the server can check the API is alive."""
    return {"status": "ok"}
