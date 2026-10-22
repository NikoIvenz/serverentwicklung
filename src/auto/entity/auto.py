"""Entity class for vehicle data (Auto)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Self, override

from sqlalchemy import Identity, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from auto.entity.base import Base
from auto.entity.farbe import Farbe

if TYPE_CHECKING:
    from auto.entity.kennzeichen import Kennzeichen
    from auto.entity.wartung import Wartung


class Auto(Base):
    """ORM entity representing a vehicle with 1:1 license plate and 1:N maintenance records."""

    __tablename__ = "auto"

    marke: Mapped[str]
    """The brand of the vehicle (e.g., 'VOLKSWAGEN')."""

    modell: Mapped[str]
    """The model name of the vehicle (e.g., 'Golf')."""

    farbe: Mapped[Farbe | None]
    """The optional color of the vehicle."""

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """The auto-generated primary key ID."""

    fin: Mapped[str] = mapped_column(unique=True)
    """The unique vehicle identification number."""

    kennzeichen: Mapped[Kennzeichen | None] = relationship(
        back_populates="auto",
        innerjoin=True,
        cascade="save-update, delete",
    )
    """1:1 relationship to the assigned license plate."""

    wartungen: Mapped[list[Wartung]] = relationship(
        back_populates="auto",
        cascade="save-update, delete",
    )
    """1:N relationship to the vehicle's maintenance records."""

    erzeugt: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
    )
    """Timestamp when the record was initially created."""

    aktualisiert: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now(),
    )
    """Timestamp when the record was last updated."""

    version: Mapped[int] = mapped_column(nullable=False, default=0)
    """Version number used for optimistic concurrency control."""

    __mapper_args__ = {"version_id_col": version}  # ruff: ignore[mutable-class-default]

    def set(self, auto: Self) -> None:
        """Overwrite primitive attributes before a database update."""
        self.fin = auto.fin
        self.marke = auto.marke
        self.modell = auto.modell
        self.farbe = auto.farbe

    @override
    def __eq__(self, other: object) -> bool:
        """Compare two Auto entities by ID without triggering SQL joins."""
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False
        return self.id is not None and self.id == other.id

    @override
    def __hash__(self) -> int:
        """Compute hash based on the primary key ID."""
        return hash(self.id) if self.id is not None else hash(type(self))

    @override
    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return (
            f"Auto(id={self.id}, version={self.version}, "
            f"fin={self.fin}, marke={self.marke}, "
            f"modell={self.modell}, farbe={self.farbe})"
        )
