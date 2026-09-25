"""Tests for the MCP surface: `POST /mcp` and its protected-resource metadata."""

import base64
from unittest.mock import Mock, patch

import pytest

from inference_gateway import __version__
from inference_gateway.client import (
    MCP_PROTOCOL_VERSION,
    InferenceGatewayClient,
    InferenceGatewayValidationError,
)
from inference_gateway.models import MCPJSONRPCResponse, OAuthProtectedResourceMetadata


@pytest.fixture
def client():
    """Create a test client instance"""
    return InferenceGatewayClient("http://test-api/v1")


def _mock_response(payload):
    """Build a mock JSON response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = payload
    return mock_response


@patch("requests.Session.request")
def test_mcp_jsonrpc_tools_call(mock_request, client):
    """tools/call posts to the root /mcp with the protocol headers and _meta."""
    mock_request.return_value = _mock_response(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"content": [{"type": "text", "text": "42"}], "isError": False},
        }
    )

    response = client.mcp_jsonrpc(
        "tools/call",
        {"name": "mcp_deepwiki_ask_question", "arguments": {"question": "How?"}},
    )

    args, kwargs = mock_request.call_args
    assert args == ("POST", "http://test-api/mcp")
    assert kwargs["headers"] == {
        "MCP-Protocol-Version": MCP_PROTOCOL_VERSION,
        "Mcp-Method": "tools/call",
        "Mcp-Name": "mcp_deepwiki_ask_question",
    }
    assert kwargs["json"] == {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "mcp_deepwiki_ask_question",
            "arguments": {"question": "How?"},
            "_meta": {
                "io.modelcontextprotocol/protocolVersion": MCP_PROTOCOL_VERSION,
                "io.modelcontextprotocol/clientInfo": {
                    "name": "inference-gateway-python-sdk",
                    "version": __version__,
                },
                "io.modelcontextprotocol/clientCapabilities": {},
            },
        },
    }
    assert isinstance(response, MCPJSONRPCResponse)
    assert response.result == {"content": [{"type": "text", "text": "42"}], "isError": False}


@patch("requests.Session.request")
def test_mcp_jsonrpc_tools_list_and_error_envelope(mock_request, client):
    """tools/list sends no Mcp-Name and JSON-RPC errors are parsed, not raised."""
    mock_request.return_value = _mock_response(
        {
            "jsonrpc": "2.0",
            "id": 7,
            "error": {"code": -32602, "message": "unknown tool: nope"},
        }
    )

    response = client.mcp_jsonrpc("tools/list", {"cursor": "abc"}, request_id=7)

    assert "Mcp-Name" not in mock_request.call_args.kwargs["headers"]
    assert mock_request.call_args.kwargs["json"]["params"]["cursor"] == "abc"
    assert response.error is not None
    assert response.error.code == -32602


@patch("requests.Session.request")
def test_mcp_jsonrpc_tools_call_requires_name(mock_request, client):
    """A tools/call without a tool name fails before any request is made."""
    with pytest.raises(InferenceGatewayValidationError):
        client.mcp_jsonrpc("tools/call", {"arguments": {}})

    mock_request.assert_not_called()


@patch("requests.Session.request")
def test_mcp_jsonrpc_encodes_non_ascii_tool_name(mock_request, client):
    """A non-ASCII tool name is sent base64-encoded in the Mcp-Name header."""
    mock_request.return_value = _mock_response({"jsonrpc": "2.0", "id": 1, "result": {}})

    client.mcp_jsonrpc("tools/call", {"name": "mcp_café_ask"})

    header = mock_request.call_args.kwargs["headers"]["Mcp-Name"]
    assert header.startswith("=?base64?")
    assert header.endswith("?=")
    encoded = header[len("=?base64?") : -len("?=")]
    assert base64.b64decode(encoded).decode() == "mcp_café_ask"


@patch("requests.Session.request")
def test_mcp_jsonrpc_keeps_caller_meta(mock_request, client):
    """A caller-supplied _meta is forwarded untouched."""
    mock_request.return_value = _mock_response({"jsonrpc": "2.0", "id": 1, "result": {}})

    client.mcp_jsonrpc("server/discover", {"_meta": {"custom": True}})

    assert mock_request.call_args.kwargs["json"]["params"]["_meta"] == {"custom": True}


@patch("requests.Session.request")
def test_get_mcp_protected_resource_metadata(mock_request, client):
    """The well-known metadata document is fetched from the root URL."""
    mock_request.return_value = _mock_response(
        {
            "resource": "https://gateway.example.com/mcp",
            "authorization_servers": ["https://keycloak.example.com/realms/ig"],
            "bearer_methods_supported": ["header"],
        }
    )

    metadata = client.get_mcp_protected_resource_metadata()

    mock_request.assert_called_once_with(
        "GET",
        "http://test-api/.well-known/oauth-protected-resource/mcp",
        timeout=30.0,
    )
    assert isinstance(metadata, OAuthProtectedResourceMetadata)
    assert metadata.resource == "https://gateway.example.com/mcp"
