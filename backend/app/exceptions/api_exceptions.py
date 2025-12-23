from typing import Any, Dict, Optional


class ApiException(Exception):
    """
    Base exception for external API errors.
    """
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors or {}

    def __str__(self) -> str:
        return f"ApiException(status_code={self.status_code}, message={self.message}, errors={self.errors})"
