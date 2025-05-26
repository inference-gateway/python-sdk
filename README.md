# Inference Gateway Python SDK

- [Inference Gateway Python SDK](#inference-gateway-python-sdk)
  - [Features](#features)
  - [Quick Start](#quick-start)
    - [Installation](#installation)
    - [Basic Usage](#basic-usage)
  - [Requirements](#requirements)
  - [Client Configuration](#client-configuration)
  - [Core Functionality](#core-functionality)
    - [Listing Models](#listing-models)
    - [Chat Completions](#chat-completions)
      - [Standard Completion](#standard-completion)
      - [Streaming Completion](#streaming-completion)
    - [Proxy Requests](#proxy-requests)
    - [Health Checking](#health-checking)
  - [Error Handling](#error-handling)
  - [Advanced Usage](#advanced-usage)
    - [Using Tools](#using-tools)
    - [Custom HTTP Configuration](#custom-http-configuration)
  - [License](#license)

A modern Python SDK for interacting with the [Inference Gateway](https://github.com/edenreich/inference-gateway), providing a unified interface to multiple AI providers.

## Features

- 🔗 Unified interface for multiple AI providers (OpenAI, Anthropic, Ollama, etc.)
- 🛡️ Type-safe operations using Pydantic models
- ⚡ Support for both synchronous and streaming responses
- 🚨 Built-in error handling and validation
- 🔄 Proxy requests directly to provider APIs

## Quick Start

### Installation

```sh
pip install inference-gateway
```

### Basic Usage

```python
from inference_gateway import InferenceGatewayClient, Message, MessageRole

# Initialize client
client = InferenceGatewayClient("http://localhost:8080")

# Simple chat completion
response = client.create_chat_completion(
    model="openai/gpt-4",
    messages=[
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant"),
        Message(role=MessageRole.USER, content="Hello!")
    ]
)

print(response.choices[0].message.content)
```

## Requirements

- Python 3.8+
- `requests` or `httpx` (for HTTP client)
- `pydantic` (for data validation)

## Client Configuration

```python
from inference_gateway import InferenceGatewayClient

# Basic configuration
client = InferenceGatewayClient("http://localhost:8080")

# With authentication
client = InferenceGatewayClient(
    "http://localhost:8080",
    token="your-api-token",
    timeout=60.0  # Custom timeout
)

# Using httpx instead of requests
client = InferenceGatewayClient(
    "http://localhost:8080",
    use_httpx=True
)
```

## Core Functionality

### Listing Models

```python
# List all available models
models = client.list_models()
print("All models:", models)

# Filter by provider
openai_models = client.list_models(provider="openai")
print("OpenAI models:", openai_models)
```

### Chat Completions

#### Standard Completion

```python
from inference_gateway import Message, MessageRole

response = client.create_chat_completion(
    model="openai/gpt-4",
    messages=[
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant"),
        Message(role=MessageRole.USER, content="Explain quantum computing")
    ],
    max_tokens=500
)

print(response.choices[0].message.content)
```

#### Streaming Completion

```python
# Using Server-Sent Events (SSE)
for chunk in client.create_chat_completion_stream(
    model="ollama/llama2",
    messages=[
        Message(role=MessageRole.USER, content="Tell me a story")
    ],
    use_sse=True
):
    print(chunk.data, end="", flush=True)

# Using JSON lines
for chunk in client.create_chat_completion_stream(
    model="anthropic/claude-3",
    messages=[
        Message(role=MessageRole.USER, content="Explain AI safety")
    ],
    use_sse=False
):
    print(chunk["choices"][0]["delta"]["content"], end="", flush=True)
```

### Proxy Requests

```python
# Proxy request to OpenAI's API
response = client.proxy_request(
    provider="openai",
    path="/v1/models",
    method="GET"
)

print("OpenAI models:", response)
```

### Health Checking

```python
if client.health_check():
    print("API is healthy")
else:
    print("API is unavailable")
```

## Error Handling

The SDK provides several exception types:

```python
try:
    response = client.create_chat_completion(...)
except InferenceGatewayAPIError as e:
    print(f"API Error: {e} (Status: {e.status_code})")
    print("Response:", e.response_data)
except InferenceGatewayValidationError as e:
    print(f"Validation Error: {e}")
except InferenceGatewayError as e:
    print(f"General Error: {e}")
```

## Advanced Usage

### Using Tools

```python
# List available MCP tools works when MCP_ENABLE and MCP_EXPOSE are set on the gateway
tools = client.list_tools()
print("Available tools:", tools)

# Use tools in chat completion works when MCP_ENABLE and MCP_EXPOSE are set to false on the gateway
response = client.create_chat_completion(
    model="openai/gpt-4",
    messages=[...],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather",
                "parameters": {...}
            }
        }
    ]
)
```

### Custom HTTP Configuration

```python
# With custom headers
client = InferenceGatewayClient(
    "http://localhost:8080",
    headers={"X-Custom-Header": "value"}
)

# With proxy settings
client = InferenceGatewayClient(
    "http://localhost:8080",
    proxies={"http": "http://proxy.example.com"}
)
```

## License

This SDK is distributed under the MIT License, see [LICENSE](LICENSE) for more information.
