"""Domain exceptions raised by the service layer."""

__all__ = ["FinExistsError", "NotFoundError", "VersionOutdatedError"]


class NotFoundError(Exception):
    """No Auto exists for the given ID."""

    def __init__(self, auto_id: int) -> None:
        """Remember the ID that was looked up."""
        super().__init__(f"No auto found with id {auto_id}.")
        self.auto_id = auto_id


class FinExistsError(Exception):
    """The vehicle identification number is already assigned to another Auto."""

    def __init__(self, fin: str) -> None:
        """Remember the conflicting FIN."""
        super().__init__(f"The FIN {fin} already exists.")
        self.fin = fin


class VersionOutdatedError(Exception):
    """The supplied version differs from the stored one (lost-update protection)."""

    def __init__(self, version: int) -> None:
        """Remember the outdated version supplied by the client."""
        super().__init__(f"The version {version} is outdated.")
        self.version = version
