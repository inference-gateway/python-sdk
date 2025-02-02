import pytest
from unittest.mock import Mock, patch
from inference_gateway.client import InferenceGatewayClient, Provider, Role, Message


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


def test_client_initialization():
    """Test client initialization with and without token"""
    client = InferenceGatewayClient("http://test-api")
    assert client.base_url == "http://test-api"
    assert "Authorization" not in client.session.headers

    client_with_token = InferenceGatewayClient(
        "http://test-api", token="test-token")
    assert "Authorization" in client_with_token.session.headers
    assert client_with_token.session.headers["Authorization"] == "Bearer test-token"


@patch("requests.Session.get")
def test_list_models(mock_get, client, mock_response):
    """Test listing available models"""
    mock_get.return_value = mock_response
    response = client.list_models()

    mock_get.assert_called_once_with("http://test-api/llms")
    assert response == {"response": "test"}


@patch("requests.Session.post")
def test_generate_content(mock_post, client, mock_response):
    """Test content generation"""
    messages = [Message(Role.SYSTEM, "You are a helpful assistant"), Message(
        Role.USER, "Hello!")]

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
