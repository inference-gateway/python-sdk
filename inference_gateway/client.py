"""Modern Python SDK client for Inference Gateway API.

This module provides a comprehensive client for interacting with the Inference Gateway,
supporting multiple AI providers with a unified interface.
"""

import base64
import json
from typing import Any, Dict, Generator, List, Optional, Type, Union

import httpx
import requests
from pydantic import BaseModel, ValidationError

from inference_gateway.models import (
    ChatCompletionTool,
    CreateChatCompletionRequest,
    CreateChatCompletionResponse,
    CreateImageRequest,
    CreateMessagesRequest,
    CreateMusicRequest,
    CreateResponseRequest,
    CreateSFXRequest,
    CreateSpeechRequest,
    ImagesResponse,
    ListModelsResponse,
    MCPJSONRPCRequest,
    MCPJSONRPCResponse,
    Message,
    MessagesMessage,
    MessagesResponse,
    MessagesStreamEvent,
    MessagesTool,
    OAuthProtectedResourceMetadata,
    Provider,
    Response,
    ResponseInputItem,
    ResponseStreamEvent,
    ResponseTool,
    SSEvent,
)

MCP_PROTOCOL_VERSION = "2026-07-28"
_MCP_META_PREFIX = "io.modelcontextprotocol/"


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
        client = InferenceGatewayClient("https://api.example.com/v1")

        # With authentication
        client = InferenceGatewayClient(
            "https://api.example.com/v1",
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
            base_url: The base URL of the Inference Gateway API (should include /v1)
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
        elif hasattr(self, "session"):
            self.session.close()

    def _api_error(
        self,
        e: Exception,
        response: Optional[Union[requests.Response, httpx.Response]],
    ) -> InferenceGatewayAPIError:
        """Build an InferenceGatewayAPIError carrying the HTTP status and error body.

        Note: ``requests.Response.__bool__`` returns ``self.ok``, so every failed
        response is falsy - always test ``is not None`` before reading from it.
        """
        status_code = response.status_code if response is not None else 0
        error_data: Dict[str, Any] = {}
        if response is not None:
            try:
                error_data = response.json() if response.content else {}
            except (json.JSONDecodeError, ValueError):
                error_data = {}
        return InferenceGatewayAPIError(
            f"Request failed: {str(e)}", status_code=status_code, response_data=error_data
        )

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
            raise self._api_error(e, response) from e
        except (requests.RequestException, httpx.RequestError) as e:
            raise InferenceGatewayError(f"Request failed: {str(e)}") from e

    def list_models(
        self,
        provider: Optional[Union[Provider, str]] = None,
        include: Optional[List[str]] = None,
    ) -> ListModelsResponse:
        """List all available language models.

        Args:
            provider: Optional provider to filter models
            include: Optional list of additional metadata to include.
                Supported values: "context_window", "pricing", "modalities".

        Returns:
            ListModelsResponse: List of available models

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If response validation fails
        """
        url = f"{self.base_url}/models"
        params = {}

        if provider:
            provider_value = provider.root if hasattr(provider, "root") else str(provider)
            params["provider"] = provider_value

        if include:
            params["include"] = ",".join(include)

        try:
            response = self._make_request("GET", url, params=params)
            return ListModelsResponse.model_validate(response.json())
        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Response validation failed: {e}")

    @property
    def _root_url(self) -> str:
        """Base URL without the `/v1` prefix, for routes that live at the root."""
        return self.base_url[: -len("/v1")] if self.base_url.endswith("/v1") else self.base_url

    def mcp_jsonrpc(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        request_id: Union[str, int] = 1,
        client_info: Optional[Dict[str, Any]] = None,
    ) -> MCPJSONRPCResponse:
        """Call the gateway's MCP JSON-RPC endpoint (`POST /mcp`).

        The endpoint lives at the root, not under `/v1`, so a `/v1` suffix on
        `base_url` is stripped. Requires `MCP_ENABLED=true` and
        `MCP_EXPOSE=true` on the gateway; otherwise it answers 403.

        The `params._meta` block and the `MCP-Protocol-Version` / `Mcp-Method` /
        `Mcp-Name` headers the protocol requires are filled in automatically; a
        `_meta` passed in `params` is left untouched.

        Args:
            method: `server/discover`, `tools/list` or `tools/call`
            params: Method parameters, e.g. `{"name": ..., "arguments": {...}}`
                for `tools/call` or `{"cursor": ...}` for `tools/list`
            request_id: JSON-RPC request id echoed back in the response
            client_info: Optional `{"name": ..., "version": ...}` override
                identifying the calling client

        Returns:
            MCPJSONRPCResponse: The JSON-RPC envelope, carrying `result` or `error`

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If request/response validation fails
        """
        from inference_gateway import __version__

        request_params: Dict[str, Any] = dict(params or {})
        request_params.setdefault(
            "_meta",
            {
                f"{_MCP_META_PREFIX}protocolVersion": MCP_PROTOCOL_VERSION,
                f"{_MCP_META_PREFIX}clientInfo": client_info
                or {"name": "inference-gateway-python-sdk", "version": __version__},
                f"{_MCP_META_PREFIX}clientCapabilities": {},
            },
        )

        headers = {
            "MCP-Protocol-Version": MCP_PROTOCOL_VERSION,
            "Mcp-Method": method,
        }

        if method == "tools/call":
            name = request_params.get("name")
            if not name:
                raise InferenceGatewayValidationError("tools/call requires params['name']")
            headers["Mcp-Name"] = (
                name if name.isascii() else f"=?base64?{base64.b64encode(name.encode()).decode()}?="
            )

        try:
            request = MCPJSONRPCRequest.model_validate(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "method": method,
                    "params": request_params,
                }
            )

            response = self._make_request(
                "POST",
                f"{self._root_url}/mcp",
                json=request.model_dump(exclude_none=True),
                headers=headers,
            )

            return MCPJSONRPCResponse.model_validate(response.json())

        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Request/response validation failed: {e}")

    def get_mcp_protected_resource_metadata(self) -> OAuthProtectedResourceMetadata:
        """Fetch the OAuth 2.0 Protected Resource Metadata for `POST /mcp`.

        Sends a request to `GET /.well-known/oauth-protected-resource/mcp` (RFC
        9728), which needs no token. The gateway returns 404 unless auth is
        enabled and the MCP endpoint is exposed.

        Returns:
            OAuthProtectedResourceMetadata: The metadata document

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If response validation fails
        """
        url = f"{self._root_url}/.well-known/oauth-protected-resource/mcp"

        try:
            response = self._make_request("GET", url)
            return OAuthProtectedResourceMetadata.model_validate(response.json())
        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Response validation failed: {e}")

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
        tools: Optional[List[ChatCompletionTool]] = None,
        reasoning_format: Optional[str] = None,
        **kwargs: Any,
    ) -> CreateChatCompletionResponse:
        """Generate a chat completion.

        Args:
            model: Name of the model to use
            messages: List of messages for the conversation
            provider: Optional provider specification
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            tools: List of tools the model may call (using ChatCompletionTool models)
            reasoning_format: Format of the reasoning content. Can be `raw` or `parsed`
            **kwargs: Additional parameters to pass to the API

        Returns:
            CreateChatCompletionResponse: The completion response

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If request/response validation fails
        """
        url = f"{self.base_url}/chat/completions"
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
                request_data["tools"] = [tool.model_dump(exclude_none=True) for tool in tools]
            if reasoning_format is not None:
                request_data["reasoning_format"] = reasoning_format

            request_data.update(kwargs)

            request = CreateChatCompletionRequest.model_validate(request_data)

            response = self._make_request(
                "POST",
                url,
                params=params,
                json=request.model_dump(exclude_none=True, exclude_unset=True),
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
        tools: Optional[List[ChatCompletionTool]] = None,
        reasoning_format: Optional[str] = None,
        **kwargs: Any,
    ) -> Generator[SSEvent, None, None]:
        """Stream a chat completion.

        Args:
            model: Name of the model to use
            messages: List of messages for the conversation
            provider: Optional provider specification
            max_tokens: Maximum number of tokens to generate
            tools: List of tools the model may call (using ChatCompletionTool models)
            reasoning_format: Format of the reasoning content. Can be `raw` or `parsed`
            **kwargs: Additional parameters to pass to the API

        Yields:
            SSEvent: Stream chunks in SSEvent format

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If request validation fails
        """
        url = f"{self.base_url}/chat/completions"
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
                request_data["tools"] = [tool.model_dump(exclude_none=True) for tool in tools]
            if reasoning_format is not None:
                request_data["reasoning_format"] = reasoning_format

            request_data.update(kwargs)

            request = CreateChatCompletionRequest.model_validate(request_data)

            if self.use_httpx:
                try:
                    with self.client.stream(
                        "POST",
                        url,
                        params=params,
                        json=request.model_dump(exclude_none=True, exclude_unset=True),
                    ) as response:
                        try:
                            response.raise_for_status()
                        except httpx.HTTPStatusError as e:
                            response.read()
                            raise self._api_error(e, response) from e
                        yield from self._process_stream_response(response)
                except httpx.RequestError as e:
                    raise InferenceGatewayError(f"Request failed: {str(e)}") from e
            else:
                try:
                    requests_response = self.session.post(
                        url,
                        params=params,
                        json=request.model_dump(exclude_none=True, exclude_unset=True),
                        stream=True,
                        timeout=self._timeout,
                    )
                    requests_response.raise_for_status()
                    yield from self._process_stream_response(requests_response)
                except requests.HTTPError as e:
                    raise self._api_error(e, requests_response) from e
                except requests.RequestException as e:
                    raise InferenceGatewayError(f"Request failed: {str(e)}") from e

        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Request validation failed: {e}")

    def _process_stream_response(
        self, response: Union[requests.Response, httpx.Response]
    ) -> Generator[SSEvent, None, None]:
        """Process streaming response data in SSEvent format."""
        current_event = None

        for line in response.iter_lines():
            if not line:
                continue

            if isinstance(line, str):
                line_bytes = line.encode("utf-8")
            else:
                line_bytes = line

            if line_bytes.strip() == b"data: [DONE]":
                continue

            if line_bytes.startswith(b"event: "):
                current_event = line_bytes[7:].decode("utf-8").strip()
                continue
            elif line_bytes.startswith(b"data: "):
                json_str = line_bytes[6:].decode("utf-8")
                event_type = current_event if current_event else "content-delta"
                yield SSEvent(event=event_type, data=json_str)
                current_event = None
            elif line_bytes.strip() == b"":
                continue
            else:
                try:
                    parsed_data = self._parse_json_line(line_bytes)
                    yield SSEvent(event="content-delta", data=json.dumps(parsed_data))
                except Exception:
                    yield SSEvent(event="content-delta", data=line_bytes.decode("utf-8"))

    def _iter_sse_payloads(
        self, response: Union[requests.Response, httpx.Response]
    ) -> Generator[str, None, None]:
        """Yield the payload of each SSE `data:` frame, skipping [DONE] sentinels."""
        for line in response.iter_lines():
            if not line:
                continue

            line_bytes = line.encode("utf-8") if isinstance(line, str) else line

            if not line_bytes.startswith(b"data: "):
                continue

            payload = line_bytes[6:].decode("utf-8")
            if payload.strip() == "[DONE]":
                continue

            yield payload

    def _process_responses_stream(
        self, response: Union[requests.Response, httpx.Response]
    ) -> Generator[ResponseStreamEvent, None, None]:
        """Process a Responses API SSE stream into ResponseStreamEvent objects."""
        for payload in self._iter_sse_payloads(response):
            yield ResponseStreamEvent.model_validate_json(payload)

    def _process_messages_stream(
        self, response: Union[requests.Response, httpx.Response]
    ) -> Generator[MessagesStreamEvent, None, None]:
        """Process a Messages API SSE stream into MessagesStreamEvent objects."""
        for payload in self._iter_sse_payloads(response):
            yield MessagesStreamEvent.model_validate_json(payload)

    def create_response(
        self,
        model: str,
        input: Union[str, List[ResponseInputItem], List[Dict[str, Any]]],
        provider: Optional[Union[Provider, str]] = None,
        max_output_tokens: Optional[int] = None,
        tools: Optional[List[ResponseTool]] = None,
        **kwargs: Any,
    ) -> Response:
        """Create a model response via the OpenAI-compatible Responses API.

        Sends a request to `POST /responses`. Not every provider implements the
        Responses API; requests routed to a provider without support return a
        400 error - use `create_chat_completion` for those providers.

        Args:
            model: Name of the model to use
            input: A text prompt, or a list of input items (dicts or
                ResponseInputItem models) for a multi-turn/batched conversation
            provider: Optional provider specification
            max_output_tokens: Upper bound on the number of tokens to generate
            tools: List of tools the model may call (using ResponseTool models)
            **kwargs: Additional parameters to pass to the API

        Returns:
            Response: The generated model response

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If request/response validation fails
        """
        url = f"{self.base_url}/responses"
        params = {}

        if provider:
            provider_value = provider.root if hasattr(provider, "root") else str(provider)
            params["provider"] = provider_value

        try:
            request_data: Dict[str, Any] = {
                "model": model,
                "input": input,
                "stream": False,
            }

            if max_output_tokens is not None:
                request_data["max_output_tokens"] = max_output_tokens
            if tools:
                request_data["tools"] = [tool.model_dump(exclude_none=True) for tool in tools]

            request_data.update(kwargs)

            request = CreateResponseRequest.model_validate(request_data)

            response = self._make_request(
                "POST",
                url,
                params=params,
                json=request.model_dump(exclude_none=True, exclude_unset=True),
            )

            return Response.model_validate(response.json())

        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Request/response validation failed: {e}")

    def create_response_stream(
        self,
        model: str,
        input: Union[str, List[ResponseInputItem], List[Dict[str, Any]]],
        provider: Optional[Union[Provider, str]] = None,
        max_output_tokens: Optional[int] = None,
        tools: Optional[List[ResponseTool]] = None,
        **kwargs: Any,
    ) -> Generator[ResponseStreamEvent, None, None]:
        """Stream a model response via the OpenAI-compatible Responses API.

        Sends a streaming request to `POST /responses` and yields validated
        `ResponseStreamEvent` objects. The event kind (for example
        `response.created` or `response.output_text.delta`) is available on
        each event's `type` field.

        Args:
            model: Name of the model to use
            input: A text prompt, or a list of input items (dicts or
                ResponseInputItem models) for a multi-turn/batched conversation
            provider: Optional provider specification
            max_output_tokens: Upper bound on the number of tokens to generate
            tools: List of tools the model may call (using ResponseTool models)
            **kwargs: Additional parameters to pass to the API

        Yields:
            ResponseStreamEvent: Typed stream events

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If request or event validation fails
        """
        url = f"{self.base_url}/responses"
        params = {}

        if provider:
            provider_value = provider.root if hasattr(provider, "root") else str(provider)
            params["provider"] = provider_value

        try:
            request_data: Dict[str, Any] = {
                "model": model,
                "input": input,
                "stream": True,
            }

            if max_output_tokens is not None:
                request_data["max_output_tokens"] = max_output_tokens
            if tools:
                request_data["tools"] = [tool.model_dump(exclude_none=True) for tool in tools]

            request_data.update(kwargs)

            request = CreateResponseRequest.model_validate(request_data)

            if self.use_httpx:
                try:
                    with self.client.stream(
                        "POST",
                        url,
                        params=params,
                        json=request.model_dump(exclude_none=True, exclude_unset=True),
                    ) as response:
                        try:
                            response.raise_for_status()
                        except httpx.HTTPStatusError as e:
                            response.read()
                            raise self._api_error(e, response) from e
                        yield from self._process_responses_stream(response)
                except httpx.RequestError as e:
                    raise InferenceGatewayError(f"Request failed: {str(e)}") from e
            else:
                try:
                    requests_response = self.session.post(
                        url,
                        params=params,
                        json=request.model_dump(exclude_none=True, exclude_unset=True),
                        stream=True,
                        timeout=self._timeout,
                    )
                    requests_response.raise_for_status()
                    yield from self._process_responses_stream(requests_response)
                except requests.HTTPError as e:
                    raise self._api_error(e, requests_response) from e
                except requests.RequestException as e:
                    raise InferenceGatewayError(f"Request failed: {str(e)}") from e

        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Request validation failed: {e}")

    def create_message(
        self,
        model: str,
        messages: Union[List[MessagesMessage], List[Dict[str, Any]]],
        max_tokens: int,
        provider: Optional[Union[Provider, str]] = None,
        system: Optional[Union[str, List[Dict[str, Any]]]] = None,
        tools: Optional[List[MessagesTool]] = None,
        **kwargs: Any,
    ) -> MessagesResponse:
        """Create a message via the Anthropic-compatible Messages API.

        Sends a request to `POST /messages`. Not every provider implements the
        Messages API; requests routed to a provider without support return a
        400 error - use `create_chat_completion` for those providers.

        Args:
            model: Name of the model to use
            messages: List of messages (dicts or MessagesMessage models)
            max_tokens: Maximum number of tokens to generate before stopping
            provider: Optional provider specification
            system: Optional system prompt (string or list of content blocks)
            tools: List of tools the model may call (using MessagesTool models)
            **kwargs: Additional parameters to pass to the API

        Returns:
            MessagesResponse: The generated message response

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If request/response validation fails
        """
        url = f"{self.base_url}/messages"
        params = {}

        if provider:
            provider_value = provider.root if hasattr(provider, "root") else str(provider)
            params["provider"] = provider_value

        try:
            request = CreateMessagesRequest.model_validate(
                self._build_messages_request(model, messages, max_tokens, system, tools, kwargs)
            )

            response = self._make_request(
                "POST",
                url,
                params=params,
                json=request.model_dump(exclude_none=True, exclude_unset=True),
            )

            return MessagesResponse.model_validate(response.json())

        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Request/response validation failed: {e}")

    def create_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        provider: Optional[Union[Provider, str]] = None,
        n: Optional[int] = None,
        size: Optional[str] = None,
        quality: Optional[str] = None,
        response_format: Optional[str] = None,
        **kwargs: Any,
    ) -> ImagesResponse:
        """Generate images via the OpenAI-compatible Images API.

        Sends a request to `POST /images/generations`.

        Args:
            prompt: A text description of the desired image
            model: Optional model ID to use for image generation
            provider: Optional provider specification
            n: Number of images to generate (1-10)
            size: Size of the generated images (e.g. `1024x1024`)
            quality: Quality of the image (e.g. `standard`, `hd`, `high`)
            response_format: Format of the returned images (`url` or `b64_json`)
            **kwargs: Additional parameters to pass to the API

        Returns:
            ImagesResponse: The generated images

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If request/response validation fails
        """
        url = f"{self.base_url}/images/generations"
        params = {}

        if provider:
            provider_value = provider.root if hasattr(provider, "root") else str(provider)
            params["provider"] = provider_value

        try:
            request_data: Dict[str, Any] = {"prompt": prompt}

            if model is not None:
                request_data["model"] = model
            if n is not None:
                request_data["n"] = n
            if size is not None:
                request_data["size"] = size
            if quality is not None:
                request_data["quality"] = quality
            if response_format is not None:
                request_data["response_format"] = response_format

            request_data.update(kwargs)

            request = CreateImageRequest.model_validate(request_data)

            response = self._make_request(
                "POST",
                url,
                params=params,
                json=request.model_dump(exclude_none=True, exclude_unset=True),
            )

            return ImagesResponse.model_validate(response.json())

        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Request/response validation failed: {e}")

    def create_image_edit(
        self,
        image: Any,
        prompt: str,
        mask: Optional[Any] = None,
        model: Optional[str] = None,
        provider: Optional[Union[Provider, str]] = None,
        n: Optional[int] = None,
        size: Optional[str] = None,
        quality: Optional[str] = None,
        response_format: Optional[str] = None,
        **kwargs: Any,
    ) -> ImagesResponse:
        """Edit or extend an image via the OpenAI-compatible Images API.

        Sends a `multipart/form-data` request to `POST /images/edits`.

        Args:
            image: The image to edit (bytes, file-like object, or a
                `(filename, fileobj)` tuple as accepted by requests/httpx)
            prompt: A text description of the desired image
            mask: Optional mask image whose transparent areas indicate where
                the image should be edited
            model: Optional model ID to use for image editing
            provider: Optional provider specification
            n: Number of images to generate (1-10)
            size: Size of the generated images (e.g. `1024x1024`)
            quality: Quality of the edited image (e.g. `auto`, `standard`, `high`)
            response_format: Format of the returned images (`url` or `b64_json`)
            **kwargs: Additional form fields to pass to the API

        Returns:
            ImagesResponse: The edited images

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If response validation fails
        """
        url = f"{self.base_url}/images/edits"
        params = {}

        if provider:
            provider_value = provider.root if hasattr(provider, "root") else str(provider)
            params["provider"] = provider_value

        files: Dict[str, Any] = {"image": image}
        if mask is not None:
            files["mask"] = mask

        data: Dict[str, Any] = {"prompt": prompt}
        if model is not None:
            data["model"] = model
        if n is not None:
            data["n"] = n
        if size is not None:
            data["size"] = size
        if quality is not None:
            data["quality"] = quality
        if response_format is not None:
            data["response_format"] = response_format
        data.update(kwargs)

        try:
            response = self._make_request("POST", url, params=params, files=files, data=data)
            return ImagesResponse.model_validate(response.json())
        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Response validation failed: {e}")

    def create_speech(
        self,
        model: str,
        input: str,
        voice: str,
        provider: Optional[Union[Provider, str]] = None,
        instructions: Optional[str] = None,
        response_format: Optional[str] = None,
        speed: Optional[float] = None,
        reference_audio: Optional[str] = None,
        **kwargs: Any,
    ) -> bytes:
        """Generate speech audio via the OpenAI-compatible Audio API.

        Sends a request to `POST /audio/speech` and returns the synthesized
        audio as raw bytes. The audio format is determined by `response_format`
        (default `mp3`). Not every provider implements the Audio API; requests
        routed to a provider without support return a 400 error.

        Args:
            model: Model ID for speech synthesis (e.g. `gpt-4o-mini-tts` or `tts-1`)
            input: The text to synthesize (4096 characters maximum)
            voice: The voice to use (e.g. `alloy`, `nova`, `shimmer`)
            provider: Optional provider specification
            instructions: Optional voice-control instructions (not supported
                    by `tts-1` or `tts-1-hd`)
            response_format: Audio format (`mp3`, `opus`, `aac`, `flac`, `wav`, `pcm`)
            speed: Playback speed (0.25-4.0)
            reference_audio: Base64-encoded audio sample for zero-shot voice
                    cloning (honored only by providers with voice-cloning support)
            **kwargs: Additional parameters to pass to the API

        Returns:
            bytes: The synthesized audio

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If request validation fails
        """
        url = f"{self.base_url}/audio/speech"
        params = {}

        if provider:
            provider_value = provider.root if hasattr(provider, "root") else str(provider)
            params["provider"] = provider_value

        try:
            request_data: Dict[str, Any] = {"model": model, "input": input, "voice": voice}

            if instructions is not None:
                request_data["instructions"] = instructions
            if response_format is not None:
                request_data["response_format"] = response_format
            if speed is not None:
                request_data["speed"] = speed
            if reference_audio is not None:
                request_data["reference_audio"] = reference_audio

            request_data.update(kwargs)

            request = CreateSpeechRequest.model_validate(request_data)

            response = self._make_request(
                "POST",
                url,
                params=params,
                json=request.model_dump(exclude_none=True, exclude_unset=True),
            )

            return response.content

        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Request validation failed: {e}")

    def create_sfx(
        self,
        model: str,
        prompt: str,
        provider: Optional[Union[Provider, str]] = None,
        duration_seconds: Optional[float] = None,
        prompt_influence: Optional[float] = None,
        loop: Optional[bool] = None,
        response_format: Optional[str] = None,
        **kwargs: Any,
    ) -> bytes:
        """Generate a sound effect via the Audio API.

        Sends a request to `POST /audio/sfx` and returns the generated audio
        as raw bytes. The audio format is determined by `response_format`
        (default `mp3`). Only providers with sound-effect support implement
        this endpoint; others return a 400 error.

        Args:
            model: Model ID for sound-effect generation
                    (e.g. `elevenlabs/eleven_text_to_sound_v2`)
            prompt: Description of the sound to generate
            provider: Optional provider specification
            duration_seconds: Length of the clip in seconds (0.5-30)
            prompt_influence: How closely generation follows the prompt (0.0-1.0)
            loop: Whether to generate a seamlessly looping clip
            response_format: Audio format (`mp3`, `opus`, `aac`, `flac`, `pcm`)
            **kwargs: Additional parameters to pass to the API

        Returns:
            bytes: The generated audio

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If request validation fails
        """
        request_data: Dict[str, Any] = {"model": model, "prompt": prompt}

        if duration_seconds is not None:
            request_data["duration_seconds"] = duration_seconds
        if prompt_influence is not None:
            request_data["prompt_influence"] = prompt_influence
        if loop is not None:
            request_data["loop"] = loop
        if response_format is not None:
            request_data["response_format"] = response_format

        request_data.update(kwargs)

        return self._post_audio("/audio/sfx", CreateSFXRequest, request_data, provider)

    def create_music(
        self,
        model: str,
        prompt: str,
        provider: Optional[Union[Provider, str]] = None,
        duration_seconds: Optional[float] = None,
        instrumental: Optional[bool] = None,
        response_format: Optional[str] = None,
        **kwargs: Any,
    ) -> bytes:
        """Compose a music clip via the Audio API.

        Sends a request to `POST /audio/music` and returns the generated audio
        as raw bytes. The audio format is determined by `response_format`
        (default `mp3`). Only providers with music support implement this
        endpoint; others return a 400 error.

        Args:
            model: Model ID for music generation (e.g. `elevenlabs/music_v2_5`)
            prompt: Description of the music to compose - genre, mood,
                    instruments, tempo
            provider: Optional provider specification
            duration_seconds: Length of the clip in seconds (3-600)
            instrumental: Guarantee the generated clip has no vocals
            response_format: Audio format (`mp3`, `opus`, `aac`, `flac`, `pcm`)
            **kwargs: Additional parameters to pass to the API

        Returns:
            bytes: The generated audio

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If request validation fails
        """
        request_data: Dict[str, Any] = {"model": model, "prompt": prompt}

        if duration_seconds is not None:
            request_data["duration_seconds"] = duration_seconds
        if instrumental is not None:
            request_data["instrumental"] = instrumental
        if response_format is not None:
            request_data["response_format"] = response_format

        request_data.update(kwargs)

        return self._post_audio("/audio/music", CreateMusicRequest, request_data, provider)

    def _post_audio(
        self,
        path: str,
        request_model: Type[BaseModel],
        request_data: Dict[str, Any],
        provider: Optional[Union[Provider, str]],
    ) -> bytes:
        """Validate an audio request body, POST it and return the raw audio bytes."""
        params = {}

        if provider:
            provider_value = provider.root if hasattr(provider, "root") else str(provider)
            params["provider"] = provider_value

        try:
            request = request_model.model_validate(request_data)

            response = self._make_request(
                "POST",
                f"{self.base_url}{path}",
                params=params,
                json=request.model_dump(exclude_none=True, exclude_unset=True),
            )

            return response.content

        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Request validation failed: {e}")

    def create_message_stream(
        self,
        model: str,
        messages: Union[List[MessagesMessage], List[Dict[str, Any]]],
        max_tokens: int,
        provider: Optional[Union[Provider, str]] = None,
        system: Optional[Union[str, List[Dict[str, Any]]]] = None,
        tools: Optional[List[MessagesTool]] = None,
        **kwargs: Any,
    ) -> Generator[MessagesStreamEvent, None, None]:
        """Stream a message via the Anthropic-compatible Messages API.

        Sends a streaming request to `POST /messages` and yields validated
        `MessagesStreamEvent` objects. The event kind (for example
        `message_start` or `content_block_delta`) is available on each
        event's `type` field.

        Args:
            model: Name of the model to use
            messages: List of messages (dicts or MessagesMessage models)
            max_tokens: Maximum number of tokens to generate before stopping
            provider: Optional provider specification
            system: Optional system prompt (string or list of content blocks)
            tools: List of tools the model may call (using MessagesTool models)
            **kwargs: Additional parameters to pass to the API

        Yields:
            MessagesStreamEvent: Typed stream events

        Raises:
            InferenceGatewayAPIError: If the API request fails
            InferenceGatewayValidationError: If request or event validation fails
        """
        url = f"{self.base_url}/messages"
        params = {}

        if provider:
            provider_value = provider.root if hasattr(provider, "root") else str(provider)
            params["provider"] = provider_value

        try:
            request = CreateMessagesRequest.model_validate(
                self._build_messages_request(
                    model, messages, max_tokens, system, tools, kwargs, stream=True
                )
            )

            if self.use_httpx:
                try:
                    with self.client.stream(
                        "POST",
                        url,
                        params=params,
                        json=request.model_dump(exclude_none=True, exclude_unset=True),
                    ) as response:
                        try:
                            response.raise_for_status()
                        except httpx.HTTPStatusError as e:
                            response.read()
                            raise self._api_error(e, response) from e
                        yield from self._process_messages_stream(response)
                except httpx.RequestError as e:
                    raise InferenceGatewayError(f"Request failed: {str(e)}") from e
            else:
                try:
                    requests_response = self.session.post(
                        url,
                        params=params,
                        json=request.model_dump(exclude_none=True, exclude_unset=True),
                        stream=True,
                        timeout=self._timeout,
                    )
                    requests_response.raise_for_status()
                    yield from self._process_messages_stream(requests_response)
                except requests.HTTPError as e:
                    raise self._api_error(e, requests_response) from e
                except requests.RequestException as e:
                    raise InferenceGatewayError(f"Request failed: {str(e)}") from e

        except ValidationError as e:
            raise InferenceGatewayValidationError(f"Request validation failed: {e}")

    @staticmethod
    def _build_messages_request(
        model: str,
        messages: Union[List[MessagesMessage], List[Dict[str, Any]]],
        max_tokens: int,
        system: Optional[Union[str, List[Dict[str, Any]]]],
        tools: Optional[List[MessagesTool]],
        kwargs: Dict[str, Any],
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Assemble the request payload shared by create_message[_stream]."""
        request_data: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        if system is not None:
            request_data["system"] = system
        if tools:
            request_data["tools"] = [tool.model_dump(exclude_none=True) for tool in tools]

        request_data.update(kwargs)
        return request_data

    def proxy_request(
        self,
        provider: Union[Provider, str],
        path: str,
        method: str = "GET",
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Proxy a request to a provider's API.

        The route lives at the gateway root (`/proxy/{provider}/{path}`), not
        under `/v1`, so a `/v1` suffix on `base_url` is stripped.

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
        url = f"{self._root_url}/proxy/{provider_value}/{path.lstrip('/')}"

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

        The route lives at the gateway root (`/health`), not under `/v1`,
        so a `/v1` suffix on `base_url` is stripped.

        Returns:
            bool: True if the API is healthy, False otherwise
        """
        try:
            response = self._make_request("GET", f"{self._root_url}/health")
            return response.status_code == 200
        except Exception:
            return False
