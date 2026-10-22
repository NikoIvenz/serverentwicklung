"""Data transfer objects that decouple the upper layers from the ORM entities."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Self

from auto.entity import Auto, Farbe, Kennzeichen, Wartung

__all__ = ["AutoDTO", "KennzeichenDTO", "WartungDTO"]


@dataclass(slots=True)
class KennzeichenDTO:
    """License plate data."""

    kombination: str
    ausstellungsdatum: date

    @classmethod
    def from_entity(cls, kennzeichen: Kennzeichen) -> Self:
        """Copy the values of a Kennzeichen entity."""
        return cls(
            kombination=kennzeichen.kombination,
            ausstellungsdatum=kennzeichen.ausstellungsdatum,
        )


@dataclass(slots=True)
class WartungDTO:
    """Maintenance record data."""

    beschreibung: str
    kosten: Decimal

    @classmethod
    def from_entity(cls, wartung: Wartung) -> Self:
        """Copy the values of a Wartung entity."""
        return cls(beschreibung=wartung.beschreibung, kosten=wartung.kosten)


@dataclass(slots=True)
class AutoDTO:
    """Vehicle data including license plate and maintenance records."""

    id: int | None
    version: int
    fin: str
    marke: str
    modell: str
    farbe: Farbe | None
    kennzeichen: KennzeichenDTO | None
    wartungen: list[WartungDTO]

    @classmethod
    def from_entity(cls, auto: Auto) -> Self:
        """Copy an Auto entity; its relations must be loadable (open session)."""
        kennzeichen = auto.kennzeichen
        return cls(
            id=auto.id,
            version=auto.version,
            fin=auto.fin,
            marke=auto.marke,
            modell=auto.modell,
            farbe=auto.farbe,
            kennzeichen=(
                KennzeichenDTO.from_entity(kennzeichen) if kennzeichen else None
            ),
            wartungen=[WartungDTO.from_entity(w) for w in auto.wartungen],
        )
