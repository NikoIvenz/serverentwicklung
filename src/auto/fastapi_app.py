"""Main FastAPI application module."""

from contextlib import asynccontextmanager
from typing import Final

from fastapi import FastAPI
from loguru import logger

from auto.repository.session_factory import engine

__all__ = ["app"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for handling startup and shutdown events."""
    logger.info("Application startup: initializing resources.")
    yield
    logger.info("Application shutdown: disposing database connection pool.")
    engine.dispose()


app: Final = FastAPI(lifespan=lifespan, title="Auto REST API", version="2026.10.1")


@app.get("/health/liveness")
def liveness() -> dict[str, str]:
    """Liveness probe to check if the server is running."""
    return {"status": "up"}
