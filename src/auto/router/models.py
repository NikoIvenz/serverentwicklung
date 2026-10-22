"""Pydantic models for request validation and response serialization."""

from datetime import date
from decimal import Decimal
from math import ceil
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from auto.entity import Auto, Farbe, Kennzeichen, Wartung
from auto.repository.slice import Slice
from auto.service.dto import AutoDTO

__all__ = [
    "AutoFindModel",
    "AutoModel",
    "AutoResponseModel",
    "AutoSliceModel",
    "AutoUpdateModel",
    "KennzeichenModel",
    "WartungModel",
]

Fin = Annotated[str, StringConstraints(pattern=r"^[A-HJ-NPR-Z0-9]{17}$")]
"""Vehicle identification number: 17 characters, without I, O and Q."""

Text = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)
]

LicensePlate = Annotated[
    str,
    StringConstraints(pattern=r"^[A-ZÄÖÜ]{1,3}-[A-Z]{1,2} [1-9][0-9]{0,3}[EH]?$"),
]
"""German license plate, e.g. `B-AB 1000`."""


class KennzeichenModel(BaseModel):
    """License plate of a new Auto."""

    kombination: LicensePlate
    ausstellungsdatum: date

    def to_entity(self) -> Kennzeichen:
        """Convert to the ORM entity."""
        return Kennzeichen(
            kombination=self.kombination,
            ausstellungsdatum=self.ausstellungsdatum,
            id=None,
            auto_id=None,
            auto=None,
        )


class WartungModel(BaseModel):
    """Maintenance record of a new Auto."""

    beschreibung: Text
    kosten: Annotated[Decimal, Field(ge=0, max_digits=10, decimal_places=2)]

    def to_entity(self) -> Wartung:
        """Convert to the ORM entity."""
        return Wartung(
            beschreibung=self.beschreibung,
            kosten=self.kosten,
            id=None,
            auto_id=None,
            auto=None,
        )


class AutoUpdateModel(BaseModel):
    """Changeable master data of an existing Auto (PUT)."""

    fin: Fin
    marke: Text
    modell: Text
    farbe: Farbe | None = None

    def to_entity(self) -> Auto:
        """Convert to a transient entity without relations."""
        return Auto(
            marke=self.marke,
            modell=self.modell,
            farbe=self.farbe,
            id=None,
            fin=self.fin,
            kennzeichen=None,
            wartungen=[],
            erzeugt=None,
            aktualisiert=None,
        )


class AutoModel(AutoUpdateModel):
    """New Auto with its 1:1 license plate and 1:N maintenance records (POST)."""

    kennzeichen: KennzeichenModel
    wartungen: list[WartungModel] = Field(default_factory=list)

    def to_entity(self) -> Auto:
        """Convert to an entity graph ready to be persisted."""
        auto = super().to_entity()
        auto.kennzeichen = self.kennzeichen.to_entity()
        auto.wartungen = [wartung.to_entity() for wartung in self.wartungen]
        return auto


class AutoFindModel(BaseModel):
    """Query parameters of the search endpoint."""

    marke: Text | None = None
    fin: Fin | None = None
    page: Annotated[int, Field(ge=0)] = 0
    size: Annotated[int, Field(ge=1, le=100)] = 5

    @property
    def suchparameter(self) -> dict[str, str]:
        """The filter criteria that were actually supplied."""
        criteria = {"marke": self.marke, "fin": self.fin}
        return {key: value for key, value in criteria.items() if value is not None}


class KennzeichenResponseModel(BaseModel):
    """License plate in responses."""

    model_config = ConfigDict(from_attributes=True)

    kombination: str
    ausstellungsdatum: date


class WartungResponseModel(BaseModel):
    """Maintenance record in responses."""

    model_config = ConfigDict(from_attributes=True)

    beschreibung: str
    kosten: Decimal


class AutoResponseModel(BaseModel):
    """Serialized AutoDTO."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None
    fin: str
    marke: str
    modell: str
    farbe: Farbe | None
    kennzeichen: KennzeichenResponseModel | None
    wartungen: list[WartungResponseModel]


class AutoSliceModel(BaseModel):
    """One page of search results with pagination metadata."""

    content: list[AutoResponseModel]
    page: int
    size: int
    total_elements: int
    total_pages: int

    @classmethod
    def from_slice(cls, result: Slice[AutoDTO], page: int, size: int) -> Self:
        """Build the response from a service result and the requested page."""
        return cls(
            content=[AutoResponseModel.model_validate(dto) for dto in result.content],
            page=page,
            size=size,
            total_elements=result.total_elements,
            total_pages=ceil(result.total_elements / size),
        )
