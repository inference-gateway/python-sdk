from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest
import requests

from inference_gateway.client import (
    InferenceGatewayAPIError,
    InferenceGatewayClient,
    InferenceGatewayError,
    InferenceGatewayValidationError,
)
from inference_gateway.models import (
    CreateChatCompletionRequest,
    CreateChatCompletionResponse,
    ListModelsResponse,
    Message,
    MessageRole,
    Model,
    Provider,
    SSEvent,
)


@pytest.fixture
def client():
    """Create a test client instance"""
    return InferenceGatewayClient("http://test-api")


@pytest.fixture
def mock_response():
    """Create a mock response"""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        "provider": "openai",
        "object": "list",
        "data": [
            {
                "id": "gpt-4",
                "object": "model",
                "created": 1687882410,
                "owned_by": "openai",
                "served_by": "openai",
            }
        ],
    }
    mock.headers = {"content-type": "application/json"}
    mock.raise_for_status.return_value = None
    return mock


@pytest.fixture
def test_params():
    """Fixture providing test parameters"""
    return {
        "api_url": "http://test-api",
        "provider": "openai",
        "model": "gpt-4",
        "message": Message(role="user", content="Hello"),
    }


def test_client_initialization():
    """Test client initialization with and without token"""
    client = InferenceGatewayClient("http://test-api")
    assert client.base_url == "http://test-api"
    assert "Authorization" not in client.session.headers

    client_with_token = InferenceGatewayClient("http://test-api", token="test-token")
    assert "Authorization" in client_with_token.session.headers
    assert client_with_token.session.headers["Authorization"] == "Bearer test-token"


@patch("requests.Session.request")
def test_list_models(mock_request, client, mock_response):
    """Test listing available models"""
    mock_request.return_value = mock_response
    response = client.list_models()

    mock_request.assert_called_once_with(
        "GET", "http://test-api/v1/models", params={}, timeout=30.0
    )
    assert isinstance(response, ListModelsResponse)
    assert response.provider == "openai"
    assert response.object == "list"
    assert len(response.data) == 1
    assert response.data[0].id == "gpt-4"


@patch("requests.Session.request")
def test_list_models_with_provider(mock_request, client):
    """Test listing models with provider filter"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "provider": "openai",
        "object": "list",
        "data": [
            {
                "id": "gpt-4",
                "object": "model",
                "created": 1687882410,
                "owned_by": "openai",
                "served_by": "openai",
            },
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": 1687882410,
                "owned_by": "openai",
                "served_by": "openai",
            },
        ],
    }
    mock_request.return_value = mock_response

    response = client.list_models("openai")

    mock_request.assert_called_once_with(
        "GET", "http://test-api/v1/models", params={"provider": "openai"}, timeout=30.0
    )
    assert isinstance(response, ListModelsResponse)
    assert response.provider == "openai"
    assert response.object == "list"
    assert len(response.data) == 2
    assert response.data[0].id == "gpt-4"
    assert response.data[1].id == "gpt-3.5-turbo"


@patch("requests.Session.request")
def test_list_models_error(mock_request, client):
    """Test error handling when listing models"""
    mock_request.side_effect = requests.exceptions.HTTPError("Provider not found")

    with pytest.raises(InferenceGatewayError, match="Request failed"):
        client.list_models("ollama")

    mock_request.assert_called_once_with(
        "GET", "http://test-api/v1/models", params={"provider": "ollama"}, timeout=30.0
    )


@patch("requests.Session.request")
def test_create_chat_completion(mock_request, client):
    """Test chat completion"""
    messages = [
        Message(role="system", content="You are a helpful assistant"),
        Message(role="user", content="Hello!"),
    ]

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Hello! How can I help you today?"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
    }
    mock_request.return_value = mock_response

    response = client.create_chat_completion("gpt-4", messages, "openai")

    mock_request.assert_called_once_with(
        "POST",
        "http://test-api/v1/chat/completions",
        params={"provider": "openai"},
        json={
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello!"},
            ],
            "stream": False,
        },
        timeout=30.0,
    )
    assert isinstance(response, CreateChatCompletionResponse)
    assert response.id == "chatcmpl-123"


@patch("requests.Session.request")
def test_health_check(mock_request, client):
    """Test health check endpoint"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_request.return_value = mock_response

    assert client.health_check() is True
    mock_request.assert_called_once_with("GET", "http://test-api/health", timeout=30.0)

    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Server error")
    assert client.health_check() is False


def test_message_model():
    """Test Message model creation and serialization"""
    message = Message(role="user", content="Hello!")
    assert message.role == "user"
    assert message.content == "Hello!"

    message_dict = message.model_dump()
    assert message_dict["role"] == "user"
    assert message_dict["content"] == "Hello!"


def test_provider_values():
    """Test Provider values"""
    provider = Provider("openai")
    assert provider.root == "openai"

    with pytest.raises(ValueError):
        Provider("invalid_provider")


def test_message_role_values():
    """Test MessageRole values"""
    role = MessageRole("system")
    assert role.root == "system"

    role = MessageRole("user")
    assert role.root == "user"

    role = MessageRole("assistant")
    assert role.root == "assistant"

    with pytest.raises(ValueError):
        MessageRole("invalid_role")


@pytest.mark.parametrize("use_sse,expected_format", [(True, "sse"), (False, "json")])
@patch("requests.Session.request")
def test_create_chat_completion_stream(mock_request, client, use_sse, expected_format):
    """Test streaming chat completion with both raw JSON and SSE formats"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None

    if use_sse:
        mock_response.iter_lines.return_value = [
            b"event: message-start",
            b'data: {"role":"assistant"}',
            b"",
            b"event: content-delta",
            b'data: {"content":"Hello"}',
            b"",
            b"event: content-delta",
            b'data: {"content":" world!"}',
            b"",
            b"event: message-end",
            b'data: {"content":""}',
            b"",
        ]
    else:
        mock_response.iter_lines.return_value = [
            b'data: {"choices":[{"delta":{"role":"assistant"}}],"model":"gpt-4"}',
            b'data: {"choices":[{"delta":{"content":"Hello"}}],"model":"gpt-4"}',
            b'data: {"choices":[{"delta":{"content":" world!"}}],"model":"gpt-4"}',
            b"data: [DONE]",
        ]

    mock_request.return_value = mock_response

    messages = [Message(role="user", content="What's up?")]
    chunks = list(
        client.create_chat_completion_stream(
            model="gpt-4", messages=messages, provider="openai", use_sse=use_sse
        )
    )

    mock_request.assert_called_once_with(
        "POST",
        "http://test-api/v1/chat/completions",
        data=None,
        json={
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "What's up?"}],
            "stream": True,
        },
        params={"provider": "openai"},
        stream=True,
    )

    if expected_format == "sse":
        assert len(chunks) == 4
        assert chunks[0].event == "message-start"
        assert chunks[0].data == '{"role":"assistant"}'
        assert chunks[1].event == "content-delta"
        assert chunks[1].data == '{"content":"Hello"}'
        assert chunks[2].event == "content-delta"
        assert chunks[2].data == '{"content":" world!"}'
        assert chunks[3].event == "message-end"
        assert chunks[3].data == '{"content":""}'
    else:
        assert len(chunks) == 3
        assert "choices" in chunks[0]
        assert "delta" in chunks[0]["choices"][0]
        assert chunks[0]["choices"][0]["delta"]["role"] == "assistant"
        assert chunks[1]["choices"][0]["delta"]["content"] == "Hello"
        assert chunks[2]["choices"][0]["delta"]["content"] == " world!"


@pytest.mark.parametrize(
    "error_scenario",
    [
        {"status_code": 500, "error": Exception("API Error"), "expected_match": "Request failed"},
        {
            "status_code": 401,
            "error": requests.exceptions.HTTPError("Unauthorized"),
            "expected_match": "Request failed",
        },
        {
            "status_code": 400,
            "error": requests.exceptions.HTTPError("Invalid model"),
            "expected_match": "Request failed",
        },
    ],
)
@patch("requests.Session.request")
def test_create_chat_completion_stream_error(mock_request, client, test_params, error_scenario):
    """Test error handling during streaming for various scenarios"""
    mock_response = Mock()
    mock_response.status_code = error_scenario["status_code"]

    if "error" in error_scenario:
        mock_response.raise_for_status.side_effect = error_scenario["error"]

    if "iter_lines" in error_scenario:
        mock_response.iter_lines.return_value = error_scenario["iter_lines"]

    mock_request.return_value = mock_response
    use_sse = error_scenario.get("use_sse", False)

    with pytest.raises(InferenceGatewayError, match=error_scenario["expected_match"]):
        list(
            client.create_chat_completion_stream(
                model=test_params["model"],
                messages=[test_params["message"]],
                provider=test_params["provider"],
                use_sse=use_sse,
            )
        )

    mock_request.assert_called_once_with(
        "POST",
        "http://test-api/v1/chat/completions",
        data=None,
        json={
            "model": test_params["model"],
            "messages": [test_params["message"].model_dump(exclude_none=True)],
            "stream": True,
        },
        params={"provider": test_params["provider"]},
        stream=True,
    )


@patch("requests.Session.request")
def test_proxy_request(mock_request, client):
    """Test proxy request to provider"""

    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"response": "test"}
    mock_resp.raise_for_status.return_value = None
    mock_request.return_value = mock_resp

    response = client.proxy_request(
        provider="openai", path="completions", method="POST", json_data={"prompt": "Hello"}
    )

    mock_request.assert_called_once_with(
        "POST", "http://test-api/proxy/openai/completions", json={"prompt": "Hello"}, timeout=30.0
    )

    assert response == {"response": "test"}


def test_exception_hierarchy():
    """Test exception hierarchy and error handling"""

    base_error = InferenceGatewayError("Base error")
    assert str(base_error) == "Base error"
    assert isinstance(base_error, Exception)

    api_error = InferenceGatewayAPIError("API error", status_code=400)
    assert str(api_error) == "API error"
    assert api_error.status_code == 400
    assert isinstance(api_error, InferenceGatewayError)

    validation_error = InferenceGatewayValidationError("Validation error")
    assert str(validation_error) == "Validation error"
    assert isinstance(validation_error, InferenceGatewayError)


def test_context_manager():
    """Test client as context manager"""
    with InferenceGatewayClient("http://test-api") as client:
        assert client.base_url == "http://test-api"
        assert client.session is not None


@patch("requests.Session.request")
def test_client_with_custom_timeout(mock_request):
    """Test client with custom timeout settings"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "provider": "openai",
        "object": "list",
        "data": [
            {
                "id": "gpt-4",
                "object": "model",
                "created": 1687882410,
                "owned_by": "openai",
                "served_by": "openai",
            }
        ],
    }
    mock_request.return_value = mock_response

    client = InferenceGatewayClient("http://test-api", timeout=30)
    client.list_models()

    mock_request.assert_called_once_with("GET", "http://test-api/v1/models", params={}, timeout=30)


def test_sse_event_parsing():
    """Test SSEvent model parsing"""
    event = SSEvent(event="content-delta", data='{"content": "Hello"}', retry=None)
    assert event.event == "content-delta"
    assert event.data == '{"content": "Hello"}'

    event_dict = event.model_dump()
    assert event_dict["event"] == "content-delta"
    assert event_dict["data"] == '{"content": "Hello"}'


def test_list_tools():
    """Test listing MCP tools"""
    mock_response_data = {
        "object": "list",
        "data": [
            {
                "name": "read_file",
                "description": "Read content from a file",
                "server": "http://mcp-filesystem-server:8083/mcp",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file to read"}
                    },
                    "required": ["path"],
                },
            },
            {
                "name": "write_file",
                "description": "Write content to a file",
                "server": "http://mcp-filesystem-server:8083/mcp",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file to write"},
                        "content": {"type": "string", "description": "Content to write"},
                    },
                    "required": ["path", "content"],
                },
            },
        ],
    }

    with patch("requests.Session.request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        client = InferenceGatewayClient("http://test-api/v1", "test-token")
        response = client.list_tools()

        assert response.object == "list"
        assert len(response.data) == 2

        first_tool = response.data[0]
        assert first_tool.name == "read_file"
        assert first_tool.description == "Read content from a file"
        assert first_tool.server == "http://mcp-filesystem-server:8083/mcp"
        assert "path" in first_tool.input_schema["properties"]

        second_tool = response.data[1]
        assert second_tool.name == "write_file"
        assert second_tool.description == "Write content to a file"
        assert second_tool.server == "http://mcp-filesystem-server:8083/mcp"
        assert "path" in second_tool.input_schema["properties"]
        assert "content" in second_tool.input_schema["properties"]

        mock_request.assert_called_once_with(
            "GET",
            "http://test-api/v1/mcp/tools",
            timeout=30.0,
        )


def test_list_tools_error():
    """Test list_tools method with API error"""
    with patch("requests.Session.request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error": "MCP not exposed"}
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "403 Client Error: Forbidden"
        )
        mock_request.return_value = mock_response

        client = InferenceGatewayClient("http://test-api/v1", "test-token")

        with pytest.raises(InferenceGatewayAPIError) as excinfo:
            client.list_tools()

        assert "Request failed" in str(excinfo.value)

        mock_request.assert_called_once_with(
            "GET",
            "http://test-api/v1/mcp/tools",
            timeout=30.0,
        )


def test_list_tools_validation_error():
    """Test list_tools method with validation error"""
    invalid_response_data = {"object": "invalid", "data": "not an array"}

    with patch("requests.Session.request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = invalid_response_data
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        client = InferenceGatewayClient("http://test-api/v1", "test-token")

        with pytest.raises(InferenceGatewayValidationError) as excinfo:
            client.list_tools()

        assert "Response validation failed" in str(excinfo.value)
