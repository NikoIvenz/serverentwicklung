"""Reset the tables and reload the test data from CSV files (development only)."""

from importlib.resources import files
from typing import Final

from loguru import logger
from sqlalchemy import text

from auto.config.config import app_config
from auto.repository.session_factory import engine

__all__ = ["db_populate", "db_populate_enabled"]

db_populate_enabled: Final = bool(app_config.get("dev", {}).get("db-populate", False))

_CSV_DIR: Final = files("auto.resources") / "csv"
_TABLES: Final = ("auto", "kennzeichen", "wartung")
"""Tables in load order; parents come before their dependents."""

_IDENTITY_START: Final = 1000


def db_populate() -> None:
    """Empty all tables, reload the CSV data and restart the ID sequences."""
    logger.warning("Resetting the database tables from CSV files.")
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE {', '.join(reversed(_TABLES))}"))
        cursor = connection.connection.cursor()
        for table in _TABLES:
            csv_data = (_CSV_DIR / f"{table}.csv").read_bytes()
            statement = (
                f"COPY {table} FROM STDIN (FORMAT csv, DELIMITER ';', HEADER true)"
            )
            with cursor.copy(statement) as copy:
                copy.write(csv_data)
            connection.execute(
                text(
                    f"ALTER TABLE {table} "
                    f"ALTER COLUMN id RESTART WITH {_IDENTITY_START}"
                ),
            )
    logger.info("Database populated with test data.")
