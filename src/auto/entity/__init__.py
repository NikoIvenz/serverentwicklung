"""Package exposing persistent ORM entity classes for the auto domain."""

from auto.entity.auto import Auto
from auto.entity.base import Base
from auto.entity.farbe import Farbe
from auto.entity.kennzeichen import Kennzeichen
from auto.entity.wartung import Wartung

__all__ = [
    "Auto",
    "Base",
    "Farbe",
    "Kennzeichen",
    "Wartung",
]
