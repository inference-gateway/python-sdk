import pytest
import requests
from unittest.mock import Mock, patch
from inference_gateway.client import (
    InferenceGatewayClient,
    Provider,
    Role,
    Message,
    GenerateResponse,
    ResponseTokens,
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
    mock.json.return_value = {"response": "test"}
    return mock


@pytest.fixture
def test_params():
    """Fixture providing test parameters"""
    return {
        "api_url": "http://test-api",
        "provider": Provider.OPENAI,
        "model": "gpt-4",
        "message": Message(Role.USER, "Hello"),
        "endpoint": "/llms/openai/generate",
    }


def test_client_initialization():
    """Test client initialization with and without token"""
    client = InferenceGatewayClient("http://test-api")
    assert client.base_url == "http://test-api"
    assert "Authorization" not in client.session.headers

    client_with_token = InferenceGatewayClient("http://test-api", token="test-token")
    assert "Authorization" in client_with_token.session.headers
    assert client_with_token.session.headers["Authorization"] == "Bearer test-token"


@patch("requests.Session.get")
def test_list_models(mock_get, client, mock_response):
    """Test listing available models"""
    mock_get.return_value = mock_response
    response = client.list_models()

    mock_get.assert_called_once_with("http://test-api/llms")
    assert response == {"response": "test"}


@patch("requests.Session.get")
def test_list_provider_models(mock_get, client, mock_response):
    """Test listing models for a specific provider"""
    mock_response.json.return_value = {
        "provider": "openai",
        "models": [{"name": "gpt-4"}, {"name": "gpt-3.5-turbo"}],
    }
    mock_get.return_value = mock_response

    response = client.list_providers_models(Provider.OPENAI)

    mock_get.assert_called_once_with("http://test-api/llms/openai")

    assert response == {
        "provider": "openai",
        "models": [{"name": "gpt-4"}, {"name": "gpt-3.5-turbo"}],
    }


@patch("requests.Session.get")
def test_list_provider_models_error(mock_get, client):
    """Test error handling when listing provider models"""
    mock_get.side_effect = requests.exceptions.HTTPError("Provider not found")

    with pytest.raises(requests.exceptions.HTTPError, match="Provider not found"):
        client.list_providers_models(Provider.OLLAMA)

    mock_get.assert_called_once_with("http://test-api/llms/ollama")


@patch("requests.Session.post")
def test_generate_content(mock_post, client, mock_response):
    """Test content generation"""
    messages = [Message(Role.SYSTEM, "You are a helpful assistant"), Message(Role.USER, "Hello!")]

    mock_post.return_value = mock_response
    response = client.generate_content(Provider.OPENAI, "gpt-4", messages)

    mock_post.assert_called_once_with(
        "http://test-api/llms/openai/generate",
        json={
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello!"},
            ],
        },
    )
    assert response == {"response": "test"}


@patch("requests.Session.get")
def test_health_check(mock_get, client):
    """Test health check endpoint"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    assert client.health_check() is True
    mock_get.assert_called_once_with("http://test-api/health")

    # Test unhealthy response
    mock_response.status_code = 500
    assert client.health_check() is False


def test_message_to_dict():
    """Test Message class serialization"""
    message = Message(Role.USER, "Hello!")
    assert message.to_dict() == {"role": "user", "content": "Hello!"}


def test_provider_enum():
    """Test Provider enum values"""
    assert Provider.OPENAI == "openai"
    assert Provider.OLLAMA == "ollama"
    assert Provider.GROQ == "groq"
    assert Provider.CLOUDFLARE == "cloudflare"
    assert Provider.COHERE == "cohere"


def test_role_enum():
    """Test Role enum values"""
    assert Role.SYSTEM == "system"
    assert Role.USER == "user"
    assert Role.ASSISTANT == "assistant"


@pytest.mark.parametrize("use_sse,expected_format", [(True, "sse"), (False, "json")])
@patch("requests.Session.post")
def test_generate_content_stream(mock_post, client, use_sse, expected_format):
    """Test streaming content generation with both raw JSON and SSE formats"""
    mock_response = Mock()
    mock_response.status_code = 200

    if use_sse:
        mock_response.raw = Mock()
        mock_response.raw.read = (
            Mock(
                side_effect=[
                    b"event: message-start\n",
                    b'data: {"role":"assistant"}\n\n',
                    b"event: content-delta\n",
                    b'data: {"content":"Hello"}\n\n',
                    b"event: content-delta\n",
                    b'data: {"content":" world!"}\n\n',
                    b"event: message-end\n",
                    b'data: {"content":""}\n\n',
                    b"",
                ]
            )
            if use_sse
            else Mock(
                side_effect=[
                    b'{"role":"assistant","model":"gpt-4","content":"Hello"}\n',
                    b'{"role":"assistant","model":"gpt-4","content":" world!"}\n',
                    b"",
                ]
            )
        )
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
            b'{"role":"assistant","model":"gpt-4","content":"Hello"}',
            b'{"role":"assistant","model":"gpt-4","content":" world!"}',
        ]

    mock_post.return_value = mock_response

    messages = [Message(Role.USER, "What's up?")]
    chunks = list(
        client.generate_content_stream(
            provider=Provider.OPENAI, model="gpt-4", messages=messages, use_sse=use_sse
        )
    )

    mock_post.assert_called_once_with(
        "http://test-api/llms/openai/generate",
        json={
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "What's up?"}],
            "stream": True,
            "ssevents": use_sse,
        },
        stream=True,
    )

    if expected_format == "sse":
        assert len(chunks) == 4
        assert chunks[0] == {"event": "message-start", "data": {"role": "assistant"}}
        assert chunks[1] == {"event": "content-delta", "data": {"content": "Hello"}}
        assert chunks[2] == {"event": "content-delta", "data": {"content": " world!"}}
        assert chunks[3] == {"event": "message-end", "data": {"content": ""}}
    else:
        assert len(chunks) == 2
        assert isinstance(chunks[0], ResponseTokens)
        assert isinstance(chunks[1], ResponseTokens)
        assert chunks[0].role == "assistant"
        assert chunks[0].model == "gpt-4"
        assert chunks[0].content == "Hello"
        assert chunks[1].content == " world!"

    for chunk in chunks:
        if use_sse:
            assert isinstance(chunk, dict)
            assert "event" in chunk
        else:
            assert isinstance(chunk, ResponseTokens)


@pytest.mark.parametrize(
    "error_scenario",
    [
        {"status_code": 500, "error": Exception("API Error"), "expected_match": "API Error"},
        {
            "status_code": 401,
            "error": requests.exceptions.HTTPError("Unauthorized"),
            "expected_match": "Unauthorized",
        },
        {
            "status_code": 400,
            "error": requests.exceptions.HTTPError("Invalid model"),
            "expected_match": "Invalid model",
        },
        {
            "status_code": 200,
            "iter_lines": [b'{"invalid": "json'],
            "expected_match": r"Invalid JSON response: \{\"invalid\": \"json.*column \d+.*char \d+",
        },
        {
            "status_code": 200,
            "iter_lines": [b"{}"],
            "expected_match": r"Missing required arguments: role, model, content",
        },
    ],
)
@patch("requests.Session.post")
def test_generate_content_stream_error(mock_post, client, test_params, error_scenario):
    """Test error handling during streaming for various scenarios"""
    mock_response = Mock()
    mock_response.status_code = error_scenario["status_code"]

    if "error" in error_scenario:
        mock_response.raise_for_status.side_effect = error_scenario["error"]

    if "iter_lines" in error_scenario:
        mock_response.iter_lines.return_value = error_scenario["iter_lines"]

    mock_post.return_value = mock_response
    use_sse = error_scenario.get("use_sse", False)

    with pytest.raises(Exception, match=error_scenario["expected_match"]):
        list(
            client.generate_content_stream(
                provider=test_params["provider"],
                model=test_params["model"],
                messages=[test_params["message"]],
                use_sse=use_sse,
            )
        )

    expected_url = f"{test_params['api_url']}{test_params['endpoint']}"
    expected_payload = {
        "model": test_params["model"],
        "messages": [test_params["message"].to_dict()],
        "stream": True,
        "ssevents": use_sse,
    }

    mock_post.assert_called_once_with(expected_url, json=expected_payload, stream=True)
