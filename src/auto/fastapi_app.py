"""Main FastAPI application module."""

from contextlib import asynccontextmanager
from typing import Final

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from auto.repository.db_populate import db_populate, db_populate_enabled
from auto.repository.session_factory import engine
from auto.router.auto_router import router as auto_router
from auto.router.problem_details import problem_response
from auto.service.exceptions import FinExistsError, NotFoundError, VersionOutdatedError

__all__ = ["app"]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan context manager for handling startup and shutdown events."""
    logger.info("Application startup: initializing resources.")
    if db_populate_enabled:
        db_populate()
    try:
        yield
    finally:
        logger.info("Application shutdown: disposing database connection pool.")
        engine.dispose()


app: Final = FastAPI(lifespan=lifespan, title="Auto REST API", version="2026.10.1")


@app.get("/health/liveness")
def liveness() -> dict[str, str]:
    """Liveness probe to check if the server is running."""
    return {"status": "up"}


app.include_router(auto_router, prefix="/rest")


@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, error: NotFoundError) -> JSONResponse:
    """Map NotFoundError to 404."""
    return problem_response(status.HTTP_404_NOT_FOUND, str(error), request.url.path)


@app.exception_handler(VersionOutdatedError)
def version_outdated_handler(
    request: Request, error: VersionOutdatedError
) -> JSONResponse:
    """Map VersionOutdatedError to 412."""
    return problem_response(
        status.HTTP_412_PRECONDITION_FAILED, str(error), request.url.path
    )


@app.exception_handler(FinExistsError)
def fin_exists_handler(request: Request, error: FinExistsError) -> JSONResponse:
    """Map FinExistsError to 422."""
    return problem_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT, str(error), request.url.path
    )


@app.exception_handler(StarletteHTTPException)
def http_exception_handler(
    request: Request, error: StarletteHTTPException
) -> JSONResponse:
    """Render all HTTP errors (e.g. 428, unknown routes) as problem details."""
    return problem_response(error.status_code, str(error.detail), request.url.path)
