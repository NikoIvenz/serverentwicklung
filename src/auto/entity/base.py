"""Base class for all SQLAlchemy ORM entities."""

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase):
    """Declarative base class combined with dataclass mapping."""
