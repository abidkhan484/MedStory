import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx
from app.clients.providers.gemini_api_client import GeminiApiClient
from app.exceptions.api_exceptions import ApiException

@pytest.fixture
def api_client():
    return GeminiApiClient(api_key="test_key")

@pytest.mark.asyncio
async def test_make_request_success(api_client):
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"candidates": [{"content": {"parts": [{"text": "Hello"}]}}]}

    with patch.object(api_client.client, 'request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        response = await api_client.make_request({"contents": [{"parts": [{"text": "Hi"}]}]})

        assert response == {"candidates": [{"content": {"parts": [{"text": "Hello"}]}}]}

        mock_request.assert_called_once()
        _, kwargs = mock_request.call_args
        assert kwargs['method'] == "POST"
        assert kwargs['url'] == "/models/gemini-pro:generateContent"
        assert kwargs['headers']['x-goog-api-key'] == "test_key"
        assert kwargs['json'] == {"contents": [{"parts": [{"text": "Hi"}]}]}

@pytest.mark.asyncio
async def test_make_request_api_error(api_client):
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "Bad Request"}
    mock_response.text = '{"error": "Bad Request"}'

    with patch.object(api_client.client, 'request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        with pytest.raises(ApiException) as exc_info:
            await api_client.make_request({"contents": [{"parts": [{"text": "Hi"}]}]})

        assert exc_info.value.status_code == 400
        assert exc_info.value.errors == {"error": "Bad Request"}

@pytest.mark.asyncio
async def test_make_request_network_error(api_client):
    with patch.object(api_client.client, 'request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = Exception("Network error")

        with pytest.raises(ApiException) as exc_info:
            await api_client.make_request({"contents": [{"parts": [{"text": "Hi"}]}]})

        # Check that it wrapped the exception
        assert "Gemini Client Error" in exc_info.value.message

@pytest.mark.asyncio
async def test_custom_model():
    client = GeminiApiClient(api_key="test_key", model="gemini-ultra")
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch.object(client.client, 'request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        await client.make_request({"contents": [{"parts": [{"text": "Hi"}]}]})

        _, kwargs = mock_request.call_args
        assert kwargs['url'] == "/models/gemini-ultra:generateContent"
