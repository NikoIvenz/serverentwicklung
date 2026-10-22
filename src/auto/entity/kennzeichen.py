"""Entity class for license plate data (Kennzeichen)."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, override

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from auto.entity.base import Base

if TYPE_CHECKING:
    from auto.entity.auto import Auto


class Kennzeichen(Base):
    """ORM entity representing a license plate in a 1:1 relation to Auto."""

    __tablename__ = "kennzeichen"

    kombination: Mapped[str]
    """The license plate string."""

    ausstellungsdatum: Mapped[date]
    """The date the license plate was issued."""

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """The auto-generated primary key ID."""

    auto_id: Mapped[int | None] = mapped_column(
        ForeignKey("auto.id", ondelete="CASCADE"),
        unique=True,
    )
    """Unique foreign key referencing the associated Auto."""

    auto: Mapped[Auto | None] = relationship(back_populates="kennzeichen")
    """Reference to the parent Auto entity."""

    @override
    def __repr__(self) -> str:
        return f"Kennzeichen(id={self.id}, kombination={self.kombination})"
