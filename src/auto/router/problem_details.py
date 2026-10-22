"""Problem Details for HTTP APIs (RFC 7807)."""

from http import HTTPStatus

from fastapi.responses import JSONResponse
from pydantic import BaseModel

__all__ = ["PROBLEM_JSON", "ProblemDetails", "problem_response"]

PROBLEM_JSON = "application/problem+json"


class ProblemDetails(BaseModel):
    """Standardized error body."""

    type: str = "about:blank"
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None


def problem_response(
    status_code: int,
    detail: str | None = None,
    instance: str | None = None,
) -> JSONResponse:
    """Build an `application/problem+json` response for the given status."""
    problem = ProblemDetails(
        title=HTTPStatus(status_code).phrase,
        status=status_code,
        detail=detail,
        instance=instance,
    )
    return JSONResponse(
        content=problem.model_dump(exclude_none=True),
        status_code=status_code,
        media_type=PROBLEM_JSON,
    )
