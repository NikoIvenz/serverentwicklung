"""Entity class for maintenance records (Wartung)."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, override

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from auto.entity.base import Base

if TYPE_CHECKING:
    from auto.entity.auto import Auto


class Wartung(Base):
    """ORM entity representing a maintenance entry in a 1:N relation to Auto."""

    __tablename__ = "wartung"

    beschreibung: Mapped[str]
    """Description of the maintenance work performed."""

    kosten: Mapped[Decimal]
    """Cost of the maintenance work."""

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """The auto-generated primary key ID."""

    auto_id: Mapped[int | None] = mapped_column(
        ForeignKey("auto.id", ondelete="CASCADE"),
    )
    """Foreign key referencing the associated Auto."""

    auto: Mapped[Auto | None] = relationship(back_populates="wartungen")
    """Reference to the parent Auto entity."""

    @override
    def __repr__(self) -> str:
        return f"Wartung(id={self.id}, beschreibung={self.beschreibung}, kosten={self.kosten})"
