"""Domain exceptions with safe, user-facing messages."""


class AppError(Exception):
    """Base exception for expected application failures."""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code

