"""Data access for Auto entities including their 1:1 and 1:N relations."""

from collections.abc import Mapping
from typing import Final

from loguru import logger
from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from auto.entity import Auto
from auto.repository.slice import Pageable, Slice

__all__ = ["AutoRepository"]


class AutoRepository:
    """Stateless repository; the caller owns the session and the transaction."""

    _EAGER_LOADING: Final = (
        joinedload(Auto.kennzeichen),
        selectinload(Auto.wartungen),
    )

    def find_by_id(self, auto_id: int, session: Session) -> Auto | None:
        """Read an Auto by ID, eagerly loading its relations."""
        logger.debug("auto_id={}", auto_id)
        statement = select(Auto).options(*self._EAGER_LOADING).where(Auto.id == auto_id)
        return session.scalars(statement).first()

    def find(
        self,
        suchparameter: Mapping[str, str],
        pageable: Pageable,
        session: Session,
    ) -> Slice[Auto]:
        """Search by `marke` (case-insensitive substring) and/or `fin` (exact match)."""
        logger.debug("suchparameter={}, pageable={}", suchparameter, pageable)
        criteria = self._build_criteria(suchparameter)

        statement = (
            select(Auto)
            .options(*self._EAGER_LOADING)
            .where(*criteria)
            .order_by(Auto.id)
            .limit(pageable.size)
            .offset(pageable.offset)
        )
        autos = list(session.scalars(statement).all())

        count_statement = select(func.count()).select_from(Auto).where(*criteria)
        total_elements = session.scalar(count_statement) or 0
        return Slice(content=autos, total_elements=total_elements)

    def exists_fin(self, fin: str, session: Session) -> bool:
        """Check whether a vehicle identification number is already in use."""
        logger.debug("fin={}", fin)
        statement = select(func.count()).select_from(Auto).where(Auto.fin == fin)
        return (session.scalar(statement) or 0) > 0

    def exists_fin_other_id(self, fin: str, auto_id: int, session: Session) -> bool:
        """Check whether a vehicle identification number is used by another Auto."""
        logger.debug("fin={}, auto_id={}", fin, auto_id)
        statement = (
            select(func.count())
            .select_from(Auto)
            .where(Auto.fin == fin, Auto.id != auto_id)
        )
        return (session.scalar(statement) or 0) > 0

    def create(self, auto: Auto, session: Session) -> Auto:
        """Persist a new Auto with its license plate and maintenance records."""
        logger.debug("auto={}", auto)
        session.add(auto)
        session.flush()
        return auto

    def update(self, auto: Auto, session: Session) -> None:
        """Flush the changed master data of an attached Auto to the database."""
        logger.debug("auto={}", auto)
        session.flush()

    def delete_by_id(self, auto_id: int, session: Session) -> None:
        """Delete an Auto by ID; related records are removed by cascade."""
        logger.debug("auto_id={}", auto_id)
        auto = self.find_by_id(auto_id, session)
        if auto is not None:
            session.delete(auto)
            session.flush()

    @staticmethod
    def _build_criteria(suchparameter: Mapping[str, str]) -> list[ColumnElement[bool]]:
        criteria: list[ColumnElement[bool]] = []
        if (marke := suchparameter.get("marke")) is not None:
            criteria.append(Auto.marke.ilike(f"%{marke}%"))
        if (fin := suchparameter.get("fin")) is not None:
            criteria.append(Auto.fin == fin)
        return criteria
