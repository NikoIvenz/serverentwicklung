"""Read-only business logic for Auto."""

from collections.abc import Mapping

from loguru import logger

from auto.repository.auto_repository import AutoRepository
from auto.repository.session_factory import Session
from auto.repository.slice import Pageable, Slice
from auto.service.dto import AutoDTO
from auto.service.exceptions import NotFoundError

__all__ = ["AutoService"]


class AutoService:
    """Reads Auto data; each call runs in its own session."""

    def __init__(self, repository: AutoRepository) -> None:
        """Store the repository used for data access."""
        self._repository = repository

    def find_by_id(self, auto_id: int) -> AutoDTO:
        """Return the Auto with the given ID.

        Raises:
            NotFoundError: if no such Auto exists.

        """
        logger.debug("auto_id={}", auto_id)
        with Session() as session:
            auto = self._repository.find_by_id(auto_id, session)
            if auto is None:
                raise NotFoundError(auto_id)
            return AutoDTO.from_entity(auto)

    def find(
        self,
        suchparameter: Mapping[str, str],
        pageable: Pageable,
    ) -> Slice[AutoDTO]:
        """Return one page of Autos matching the search parameters."""
        logger.debug("suchparameter={}, pageable={}", suchparameter, pageable)
        with Session() as session:
            result = self._repository.find(suchparameter, pageable, session)
            return Slice(
                content=[AutoDTO.from_entity(auto) for auto in result.content],
                total_elements=result.total_elements,
            )
