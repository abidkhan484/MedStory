from typing import Any, Dict

import httpx

from app.clients.base_http_client import BaseHttpClient
from app.exceptions.api_exceptions import ApiException


class GeminiApiClient(BaseHttpClient):
    """
    Client for interacting with Google's Gemini API.
    """
    def __init__(self, api_key: str, model: str = "gemini-pro", base_url: str = "https://generativelanguage.googleapis.com/v1beta", timeout: int = 30):
        super().__init__(base_url, timeout)
        self.api_key = api_key
        self.model = model
        # Default endpoint for text generation
        self.api_endpoint = f"/models/{model}:generateContent"
        self.http_method = "POST"

    def build_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

    def build_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construct the payload for Gemini API.
        The caller is responsible for providing the correct structure.
        """
        return data

    def parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the successful response from Gemini.
        """
        # Return raw data or simplified structure?
        # For infrastructure, returning parsed JSON (dict) is safer than assumptions.
        return data

    async def make_request(self, payload: Dict[str, Any]) -> Any:
        """
        Make a request to the Gemini API.
        """
        headers = self.build_headers()
        final_payload = self.build_payload(payload)

        return await self.execute(
            method=self.http_method,
            endpoint=self.api_endpoint,
            payload=final_payload,
            headers=headers
        )

    def handle_response(self, response: httpx.Response) -> Any:
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except Exception:
                error_data = {"raw": response.text}

            raise ApiException(
                message=f"Gemini API Error: {response.status_code}",
                status_code=response.status_code,
                errors=error_data
            )

        try:
            return self.parse_response(response.json())
        except Exception as e:
            raise ApiException(
                message="Failed to parse response",
                status_code=500,
                errors={"details": str(e)}
            )

    def handle_error(self, exception: Exception) -> None:
        """
        Handle connection/client errors.
        """
        if isinstance(exception, ApiException):
            raise exception

        raise ApiException(
            message=f"Gemini Client Error: {str(exception)}",
            status_code=500,
            errors={"original_error": str(exception)}
        )
