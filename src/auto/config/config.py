"""Configuration reader for TOML settings and logging setup."""

from importlib.resources import files
from pathlib import Path
from sys import stderr
from tomllib import load
from typing import Any, Final

from loguru import logger

__all__ = ["app_config", "resources_path"]

resources_path: Final[str] = "auto.resources"
_config_file: Final = files(resources_path) / "app.toml"

with Path(str(_config_file)).open(mode="rb") as reader:
    app_config: Final[dict[str, Any]] = load(reader)

LOG_FILE: Final = Path("log") / "app.log"
logger.remove()
logger.add(stderr, level="INFO")
logger.add(LOG_FILE, rotation="1 MB", level="INFO")

logger.info("Logging configuration loaded.")
