import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import httpx

from app.exceptions.api_exceptions import ApiException

logger = logging.getLogger(__name__)


class BaseHttpClient(ABC):
    """
    Abstract base class for external HTTP clients.
    Wraps httpx.AsyncClient and provides error handling structure.
    """
    def __init__(self, base_url: str = "", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self.client.aclose()

    async def execute(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Execute an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (relative to base_url)
            payload: JSON payload for the request
            headers: Optional headers

        Returns:
            The processed response data

        Raises:
            ApiException: On API errors
        """
        try:
            logger.debug(f"Request: {method} {endpoint} | Payload: {payload}")
            response = await self.client.request(
                method=method,
                url=endpoint,
                json=payload,
                headers=headers
            )
            return self.handle_response(response)
        except Exception as e:
            self.handle_error(e)
            # Ensure an exception is raised if handle_error didn't raise one
            raise ApiException(message=f"Unhandled error: {str(e)}") from e

    @abstractmethod
    def handle_response(self, response: httpx.Response) -> Any:
        """
        Parse and validate the response.
        Should raise ApiException on non-2xx status if strict.
        """
        pass

    @abstractmethod
    def handle_error(self, exception: Exception) -> None:
        """
        Handle exceptions (both HTTP and network errors).
        Should convert to and raise ApiException.
        """
        pass
