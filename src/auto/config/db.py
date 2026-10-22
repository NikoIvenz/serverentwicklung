"""Database URL and connection configuration for SQLAlchemy with PostgreSQL TLS."""

from importlib.resources import files
from typing import Final

from loguru import logger
from sqlalchemy.engine import URL

from auto.config.config import app_config

__all__ = [
    "db_connect_args",
    "db_dialect",
    "db_log_statements",
    "db_url",
    "db_url_admin",
]

_db_toml: Final = app_config.get("db", {})

db_dialect: Final = _db_toml.get("dialect", "postgresql")
_drivername = "postgresql+psycopg"
_dbname: Final = _db_toml.get("name", "auto")
_host: Final = _db_toml.get("host", "localhost")
_username: Final = _db_toml.get("username", "auto")
_password: Final = _db_toml.get("password", "p")
_password_admin: Final = _db_toml.get("password-admin", "p")

db_log_statements: Final = bool(_db_toml.get("log-statements", False))

db_url: Final[URL] = URL.create(
    drivername=_drivername,
    username=_username,
    password=_password,
    host=_host,
    database=_dbname,
)

db_url_admin: Final[URL] = URL.create(
    drivername=_drivername,
    username="postgres",
    password=_password_admin,
    host=_host,
    database=_dbname,
)


def _create_connect_args() -> dict[str, str]:
    # Looking for server.crt directly in resources (matching your project layout)
    cafile: Final = str(files("auto.resources") / "server.crt")
    return {
        "sslmode": "verify-full",
        "sslrootcert": cafile,
    }


db_connect_args: Final = _create_connect_args()
logger.debug("Database configuration initialized with TLS verify-full.")
