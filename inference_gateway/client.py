"""Modern Python SDK client for Inference Gateway API.

This module provides a comprehensive client for interacting with the Inference Gateway,
supporting multiple AI providers with a unified interface.
"""

import json
from typing import Any, Dict, Generator, List, Optional, Union

import httpx
import requests
from pydantic import ValidationError

from inference_gateway.models import (
    CreateChatCompletionRequest,
    CreateChatCompletionResponse,
    ListModelsResponse,
    ListToolsResponse,
    Message,
    Provider,
    SSEvent,
)


class InferenceGatewayError(Exception):
    """Base exception for Inference Gateway SDK errors."""

    pass


class InferenceGatewayAPIError(InferenceGatewayError):
    """Exception raised for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class InferenceGatewayValidationError(InferenceGatewayError):
    """Exception raised for validation errors."""

    pass


class InferenceGatewayClient:
    """Modern client for interacting with the Inference Gateway API.

    This client provides a comprehensive interface to the Inference Gateway,
    supporting multiple AI providers with type-safe operations.

    Example:
        ```python
        # Basic usage
        client = InferenceGatewayClient("https://api.example.com")

        # With authentication
        client = InferenceGatewayClient(
            "https://api.example.com",
            token="your-api-token"
        )

        # List available models
        models = client.list_models()

        # Create a chat completion
        messages = [Message(role="user", content="Hello!")]
        response = client.create_chat_completion(
            model="gpt-4o",
            messages=messages
        )
        ```
    """

    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        timeout: float = 30.0,
        use_httpx: bool = False,
    ):
        """Initialize the client with base URL and optional auth token.

        Args:
            base_url: The base URL of the Inference Gateway API
            token: Optional authentication token
            timeout: Request timeout in seconds (default: 30.0)
            use_httpx: Whether to use httpx instead of requests (default: False)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.use_httpx = use_httpx

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        if use_httpx:
            self.client = httpx.Client(
                timeout=timeout,
                headers=headers,
            )
        else:
            self.session = requests.Session()
            self.session.headers.update(headers)
            self._timeout = timeout

    def __enter__(self) -> "InferenceGatewayClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        if self.use_httpx and hasattr(self, "client"):
            self.client.close()

    def _make_request(
        self, method: str, url: str, **kwargs: Any
    ) -> Union[requests.Response, httpx.Response]:
        """Make an HTTP request using the configured client."""
        response: Optional[Union[requests.Response, httpx.Response]] = None
        try:
            if self.use_httpx:
                response = self.client.request(method, url, **kwargs)
            else:
                if "timeout" not in kwargs and hasattr(self, "_timeout"):
                    kwargs["timeout"] = self._timeout
                response = self.session.request(method, url, **kwargs)

            if response is not None:
                response.raise_for_status()
                return response
            else:
                raise InferenceGatewayError("No response received")

        except (requests.HTTPError, httpx.HTTPStatusError) as e:
            try:
                error_data = response.json() if response and response.content else {}
            except (json.JSONDecodeError, ValueError):
                error_data = {}

            status_code = response.status_code if response else 0
            raise InferenceGatewayAPIError(
                f"Request failed: {str(e)}",
                status_code=status_code,
                response_data=error_data,
            )
        except (requests.RequestException, httpx.RequestError) as e:
            raise InferenceGatewayError(f"Request failed: {str(e)}")

    def list_models(self, provider: Optional[Union[Provider, str]] = None) -> ListModelsResponse:
        """List all available language models.

        Args:
            provider: Optional provider to filter models

        Returns:
            ListModelsResponse: List of available models

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If response validation fails
        """
        url = f"{self.base_url}/v1/models"
        params = {}

        if provider:
            provider_value = provider.root if hasattr(provider, "root") else str(provider)
            params["provider"] = provider_value

        try:
            response = self._make_request("GET", url, params=params)
            return ListModelsResponse.model_validate(response.json())
        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Response validation failed: {e}")

    def list_tools(self) -> ListToolsResponse:
        """List all available MCP tools.

        Returns:
            ListToolsResponse: List of available MCP tools

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If response validation fails
        """
        url = f"{self.base_url}/mcp/tools"

        try:
            response = self._make_request("GET", url)
            return ListToolsResponse.model_validate(response.json())
        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Response validation failed: {e}")

    def _parse_sse_chunk(self, chunk: bytes) -> SSEvent:
        """Parse an SSE message chunk into structured event data.

        Args:
            chunk: Raw SSE message chunk in bytes format

        Returns:
            SSEvent: Parsed SSE message with event type and data fields

        Raises:
            InferenceGatewayValidationError: If chunk format or content is invalid
        """
        if not isinstance(chunk, bytes):
            raise TypeError(f"Expected bytes, got {type(chunk)}")

        try:
            decoded = chunk.decode("utf-8")
            event_type = None
            data = None

            for line in (l.strip() for l in decoded.split("\n") if l.strip()):
                if line.startswith("event:"):
                    event_type = line.removeprefix("event:").strip()
                elif line.startswith("data:"):
                    data = line.removeprefix("data:").strip()

            return SSEvent(event=event_type, data=data, retry=None)

        except UnicodeDecodeError as e:
            raise InferenceGatewayValidationError(f"Invalid UTF-8 encoding in SSE chunk: {chunk!r}")

    def _parse_json_line(self, line: bytes) -> Dict[str, Any]:
        """Parse a single JSON line into a dictionary.

        Args:
            line: JSON line as bytes

        Returns:
            Dict[str, Any]: Parsed JSON data

        Raises:
            InferenceGatewayValidationError: If JSON parsing fails
        """
        try:
            decoded_line = line.decode("utf-8")
            result: Dict[str, Any] = json.loads(decoded_line)
            return result
        except UnicodeDecodeError as e:
            raise InferenceGatewayValidationError(f"Invalid UTF-8 encoding: {line!r}")
        except json.JSONDecodeError as e:
            raise InferenceGatewayValidationError(f"Invalid JSON response: {decoded_line}")

    def create_chat_completion(
        self,
        model: str,
        messages: List[Message],
        provider: Optional[Union[Provider, str]] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> CreateChatCompletionResponse:
        """Generate a chat completion.

        Args:
            model: Name of the model to use
            messages: List of messages for the conversation
            provider: Optional provider specification
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            tools: List of tools the model may call
            **kwargs: Additional parameters to pass to the API

        Returns:
            CreateChatCompletionResponse: The completion response

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If request/response validation fails
        """
        url = f"{self.base_url}/v1/chat/completions"
        params = {}

        if provider:
            provider_value = provider.root if hasattr(provider, "root") else str(provider)
            params["provider"] = provider_value

        try:
            request_data = {
                "model": model,
                "messages": [msg.model_dump(exclude_none=True) for msg in messages],
                "stream": stream,
            }

            if max_tokens is not None:
                request_data["max_tokens"] = max_tokens
            if tools:
                request_data["tools"] = tools

            request_data.update(kwargs)

            request = CreateChatCompletionRequest.model_validate(request_data)

            response = self._make_request(
                "POST", url, params=params, json=request.model_dump(exclude_none=True)
            )

            return CreateChatCompletionResponse.model_validate(response.json())

        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Request/response validation failed: {e}")

    def create_chat_completion_stream(
        self,
        model: str,
        messages: List[Message],
        provider: Optional[Union[Provider, str]] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        use_sse: bool = True,
        **kwargs: Any,
    ) -> Generator[Union[Dict[str, Any], SSEvent], None, None]:
        """Stream a chat completion.

        Args:
            model: Name of the model to use
            messages: List of messages for the conversation
            provider: Optional provider specification
            max_tokens: Maximum number of tokens to generate
            tools: List of tools the model may call
            use_sse: Whether to use Server-Sent Events format
            **kwargs: Additional parameters to pass to the API

        Yields:
            Union[Dict[str, Any], SSEvent]: Stream chunks

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If request validation fails
        """
        url = f"{self.base_url}/v1/chat/completions"
        params = {}

        if provider:
            provider_value = provider.root if hasattr(provider, "root") else str(provider)
            params["provider"] = provider_value

        try:
            request_data = {
                "model": model,
                "messages": [msg.model_dump(exclude_none=True) for msg in messages],
                "stream": True,
            }

            if max_tokens is not None:
                request_data["max_tokens"] = max_tokens
            if tools:
                request_data["tools"] = tools

            request_data.update(kwargs)

            request = CreateChatCompletionRequest.model_validate(request_data)

            if self.use_httpx:
                with self.client.stream(
                    "POST", url, params=params, json=request.model_dump(exclude_none=True)
                ) as response:
                    try:
                        response.raise_for_status()
                    except httpx.HTTPStatusError as e:
                        raise InferenceGatewayAPIError(f"Request failed: {str(e)}")
                    yield from self._process_stream_response(response, use_sse)
            else:
                requests_response = self.session.post(
                    url, params=params, json=request.model_dump(exclude_none=True), stream=True
                )
                try:
                    requests_response.raise_for_status()
                except (requests.exceptions.HTTPError, Exception) as e:
                    raise InferenceGatewayAPIError(f"Request failed: {str(e)}")
                yield from self._process_stream_response(requests_response, use_sse)

        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Request validation failed: {e}")

    def _process_stream_response(
        self, response: Union[requests.Response, httpx.Response], use_sse: bool
    ) -> Generator[Union[Dict[str, Any], SSEvent], None, None]:
        """Process streaming response data."""
        if use_sse:
            buffer: List[bytes] = []

            for line in response.iter_lines():
                if not line:
                    if buffer:
                        chunk = b"\n".join(buffer)
                        yield self._parse_sse_chunk(chunk)
                        buffer = []
                    continue

                if isinstance(line, str):
                    line_bytes = line.encode("utf-8")
                else:
                    line_bytes = line
                buffer.append(line_bytes)
        else:
            for line in response.iter_lines():
                if not line:
                    continue

                if isinstance(line, str):
                    line_bytes = line.encode("utf-8")
                else:
                    line_bytes = line

                if line_bytes.strip() == b"data: [DONE]":
                    continue
                if line_bytes.startswith(b"data: "):
                    json_str = line_bytes[6:].decode("utf-8")
                    data = json.loads(json_str)
                    yield data
                else:
                    yield self._parse_json_line(line_bytes)

    def proxy_request(
        self,
        provider: Union[Provider, str],
        path: str,
        method: str = "GET",
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Proxy a request to a provider's API.

        Args:
            provider: The provider to route to
            path: Path segment after the provider
            method: HTTP method to use
            json_data: Optional JSON data for request body
            **kwargs: Additional parameters to pass to the request

        Returns:
            Dict[str, Any]: Provider response

        Raises:
            InferenceGatewayAPIError: If the API request fails
            ValueError: If an unsupported HTTP method is used
        """
        provider_value = provider.root if hasattr(provider, "root") else str(provider)
        url = f"{self.base_url}/proxy/{provider_value}/{path.lstrip('/')}"

        method = method.upper()
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            raise ValueError(f"Unsupported HTTP method: {method}")

        request_kwargs = kwargs.copy()
        if json_data and method in ["POST", "PUT", "PATCH"]:
            request_kwargs["json"] = json_data

        response = self._make_request(method, url, **request_kwargs)
        result: Dict[str, Any] = response.json()
        return result

    def health_check(self) -> bool:
        """Check if the API is healthy.

        Returns:
            bool: True if the API is healthy, False otherwise
        """
        try:
            response = self._make_request("GET", f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
