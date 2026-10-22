"""REST endpoints for Auto."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Header, Query, Request, Response, status
from loguru import logger

from auto.repository.slice import Pageable
from auto.router.dependencies import ServiceDep, WriteServiceDep
from auto.router.models import (
    AutoFindModel,
    AutoModel,
    AutoResponseModel,
    AutoSliceModel,
    AutoUpdateModel,
)

__all__ = ["router"]

router = APIRouter(tags=["Auto"])


def _etag(version: int) -> str:
    return f'"{version}"'


def _strip_etag(value: str) -> str:
    """Remove the weak-validator prefix and the quotes of an entity tag."""
    return value.strip().removeprefix("W/").strip('"')


def _parse_if_match(if_match: str | None) -> int:
    """Extract the version from the If-Match header.

    Raises:
        HTTPException: 428 if the header is missing, 412 if it is not a version.

    """
    if if_match is None:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="Header If-Match is required.",
        )
    version = _strip_etag(if_match)
    if not version.isascii() or not version.isdecimal():
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=f"Invalid version in If-Match: {if_match}",
        )
    return int(version)


@router.get("/{auto_id}", response_model=AutoResponseModel)
def get_by_id(
    auto_id: int,
    service: ServiceDep,
    response: Response,
    if_none_match: Annotated[str | None, Header()] = None,
) -> AutoResponseModel | Response:
    """Read an Auto; answers 304 if the client's cached version is current."""
    logger.debug("auto_id={}, if_none_match={}", auto_id, if_none_match)
    auto = service.find_by_id(auto_id)
    etag = _etag(auto.version)

    if if_none_match is not None and any(
        _strip_etag(tag) == str(auto.version) for tag in if_none_match.split(",")
    ):
        return Response(
            status_code=status.HTTP_304_NOT_MODIFIED, headers={"ETag": etag}
        )

    response.headers["ETag"] = etag
    return AutoResponseModel.model_validate(auto)


@router.get("")
def get(
    query: Annotated[AutoFindModel, Query()],
    service: ServiceDep,
) -> AutoSliceModel:
    """Search Autos by brand and/or FIN with pagination."""
    logger.debug("query={}", query)
    result = service.find(query.suchparameter, Pageable(query.page, query.size))
    return AutoSliceModel.from_slice(result, query.page, query.size)


@router.post("", status_code=status.HTTP_201_CREATED)
def post(
    auto_model: AutoModel,
    request: Request,
    service: WriteServiceDep,
) -> Response:
    """Create an Auto; the Location header points to the new resource."""
    auto_dto = service.create(auto_model.to_entity())
    location = f"{request.url.path.rstrip('/')}/{auto_dto.id}"
    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": location, "ETag": _etag(auto_dto.version)},
    )


@router.put("/{auto_id}", status_code=status.HTTP_204_NO_CONTENT)
def put(
    auto_id: int,
    auto_model: AutoUpdateModel,
    service: WriteServiceDep,
    if_match: Annotated[str | None, Header()] = None,
) -> Response:
    """Update the master data of an Auto using optimistic locking via If-Match."""
    version = _parse_if_match(if_match)
    auto_dto = service.update(auto_model.to_entity(), auto_id, version)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": _etag(auto_dto.version)},
    )


@router.delete("/{auto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(auto_id: int, service: WriteServiceDep) -> Response:
    """Delete an Auto; deleting a missing resource is not an error."""
    service.delete_by_id(auto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
