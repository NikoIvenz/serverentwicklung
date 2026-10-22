"""CLI entry point allowing the module to be executed as `python -m auto`."""

from auto.asgi_server import run

__all__ = ["run"]

if __name__ == "__main__":
    run()
