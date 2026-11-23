"""SolarSense AI Lab — FastAPI entry point."""

from fastapi import FastAPI

app = FastAPI(title="SolarSense AI Lab API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple status so we (and CI, and the server) can check the API is alive."""
    return {"status": "ok"}
