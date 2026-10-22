"""Package entry point and declaration."""

from auto.asgi_server import run
from auto.fastapi_app import app

__all__ = ["app", "main"]


def main() -> None:
    """Start the server; target of the console script `auto`."""
    run()
