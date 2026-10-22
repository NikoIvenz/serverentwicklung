"""Transactional business logic that modifies Auto data."""

from loguru import logger
from sqlalchemy.orm.exc import StaleDataError

from auto.entity import Auto
from auto.repository.auto_repository import AutoRepository
from auto.repository.session_factory import Session
from auto.service.dto import AutoDTO
from auto.service.exceptions import FinExistsError, NotFoundError, VersionOutdatedError

__all__ = ["AutoWriteService"]


class AutoWriteService:
    """Creates, updates and deletes Autos; each call is one transaction."""

    def __init__(self, repository: AutoRepository) -> None:
        """Store the repository used for data access."""
        self._repository = repository

    def create(self, auto: Auto) -> AutoDTO:
        """Persist a new Auto and return it with its generated ID.

        Raises:
            FinExistsError: if the FIN is already in use.

        """
        logger.debug("auto={}", auto)
        with Session() as session:
            if self._repository.exists_fin(auto.fin, session):
                raise FinExistsError(auto.fin)
            created = self._repository.create(auto, session)
            auto_dto = AutoDTO.from_entity(created)
            session.commit()
        logger.debug("auto_dto={}", auto_dto)
        return auto_dto

    def update(self, auto: Auto, auto_id: int, version: int) -> AutoDTO:
        """Overwrite the master data of an Auto and return it with its new version.

        Raises:
            NotFoundError: if no Auto with `auto_id` exists.
            VersionOutdatedError: if `version` is not the stored version.
            FinExistsError: if the new FIN belongs to another Auto.

        """
        logger.debug("auto={}, auto_id={}, version={}", auto, auto_id, version)
        with Session() as session:
            auto_db = self._repository.find_by_id(auto_id, session)
            if auto_db is None:
                raise NotFoundError(auto_id)
            if auto_db.version != version:
                raise VersionOutdatedError(version)
            if self._repository.exists_fin_other_id(auto.fin, auto_id, session):
                raise FinExistsError(auto.fin)

            auto_db.set(auto)
            try:
                self._repository.update(auto_db, session)
            except StaleDataError as e:  # concurrent update between read and flush
                raise VersionOutdatedError(version) from e
            auto_dto = AutoDTO.from_entity(auto_db)  # version already incremented
            session.commit()
        logger.debug("auto_dto={}", auto_dto)
        return auto_dto

    def delete_by_id(self, auto_id: int) -> None:
        """Delete the Auto with the given ID, if it exists."""
        logger.debug("auto_id={}", auto_id)
        with Session() as session:
            self._repository.delete_by_id(auto_id, session)
            session.commit()
