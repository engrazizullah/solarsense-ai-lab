"""Base class that every database table model inherits from."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
