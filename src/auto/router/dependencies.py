"""FastAPI dependency providers for repository and services."""

from typing import Annotated

from fastapi import Depends

from auto.repository.auto_repository import AutoRepository
from auto.service.auto_service import AutoService
from auto.service.auto_write_service import AutoWriteService

__all__ = [
    "RepositoryDep",
    "ServiceDep",
    "WriteServiceDep",
    "get_repository",
    "get_service",
    "get_write_service",
]


def get_repository() -> AutoRepository:
    """Provide the repository."""
    return AutoRepository()


RepositoryDep = Annotated[AutoRepository, Depends(get_repository)]


def get_service(repository: RepositoryDep) -> AutoService:
    """Provide the read service."""
    return AutoService(repository)


def get_write_service(repository: RepositoryDep) -> AutoWriteService:
    """Provide the write service."""
    return AutoWriteService(repository)


ServiceDep = Annotated[AutoService, Depends(get_service)]
WriteServiceDep = Annotated[AutoWriteService, Depends(get_write_service)]
