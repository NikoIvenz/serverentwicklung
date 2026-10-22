"""Pagination value objects shared by repository and service layer."""

from dataclasses import dataclass

__all__ = ["Pageable", "Slice"]


@dataclass(frozen=True, slots=True)
class Pageable:
    """Pagination request: zero-based page number and page size."""

    number: int
    size: int

    @property
    def offset(self) -> int:
        """Index of the first element of the requested page."""
        return self.number * self.size


@dataclass(frozen=True, slots=True)
class Slice[T]:
    """One page of query results together with the total number of matches."""

    content: list[T]
    total_elements: int
