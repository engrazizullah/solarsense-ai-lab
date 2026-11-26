"""Database engine and sessions."""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Create the connection pool once, on first use."""
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """Give one request its own session, and always close it afterwards."""
    with Session(get_engine()) as session:
        yield session
