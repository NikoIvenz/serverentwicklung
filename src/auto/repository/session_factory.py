"""SQLAlchemy engine and session factory configuration."""

from typing import Final

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from auto.config.db import db_connect_args, db_log_statements, db_url

__all__ = ["Session", "engine"]

engine: Final = create_engine(
    db_url,
    connect_args=db_connect_args,
    poolclass=QueuePool,
    pool_size=10,
    echo=db_log_statements,
)

Session = sessionmaker(bind=engine, autoflush=False)
logger.info("SQLAlchemy Session factory created.")
