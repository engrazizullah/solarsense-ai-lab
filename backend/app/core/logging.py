"""Send the app's own log messages to the terminal (uvicorn only sets up its own)."""

import logging


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(levelname)-9s %(name)s - %(message)s",
    )
