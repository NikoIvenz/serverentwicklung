"""Function `run` for the FastAPI application with the ASGI server Uvicorn."""

from importlib.resources import files
from ssl import PROTOCOL_TLS_SERVER
from typing import Final

import uvicorn

from auto.config.config import app_config

__all__ = ["run"]

_server_config: Final = app_config.get("server", {})
_host: Final = _server_config.get("host-binding", "127.0.0.1")
_port: Final = int(_server_config.get("port", 8000))

# Resolve absolute paths to the TLS files using importlib
_cafile: Final = str(files("auto.resources") / "server.crt")
_keyfile: Final = str(files("auto.resources") / "server.key")


def run() -> None:
    """Start the application with uvicorn."""
    uvicorn.run(
        "auto.fastapi_app:app",
        loop="asyncio",
        http="zttp",
        http2=True,
        interface="asgi3",
        host=_host,
        port=_port,
        ssl_certfile=_cafile,
        ssl_keyfile=_keyfile,
        ssl_version=PROTOCOL_TLS_SERVER,
    )
