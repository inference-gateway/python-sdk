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
    - [Listing Available MCP Tools](#listing-available-mcp-tools)
    - [Custom HTTP Configuration](#custom-http-configuration)
  - [Examples](#examples)
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
from inference_gateway import InferenceGatewayClient, Message

# Initialize client
client = InferenceGatewayClient("http://localhost:8080/v1")

# Simple chat completion
response = client.create_chat_completion(
    model="openai/gpt-4",
    messages=[
        Message(role="system", content="You are a helpful assistant"),
        Message(role="user", content="Hello!")
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
client = InferenceGatewayClient("http://localhost:8080/v1")

# With authentication
client = InferenceGatewayClient(
    "http://localhost:8080/v1",
    token="your-api-token",
    timeout=60.0  # Custom timeout
)

# Using httpx instead of requests
client = InferenceGatewayClient(
    "http://localhost:8080/v1",
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
from inference_gateway import Message

response = client.create_chat_completion(
    model="openai/gpt-4",
    messages=[
        Message(role="system", content="You are a helpful assistant"),
        Message(role="user", content="Explain quantum computing")
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
        Message(role="user", content="Tell me a story")
    ],
    use_sse=True
):
    print(chunk.data, end="", flush=True)

# Using JSON lines
for chunk in client.create_chat_completion_stream(
    model="anthropic/claude-3",
    messages=[
        Message(role="user", content="Explain AI safety")
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
# Define a weather tool using type-safe Pydantic models
from inference_gateway.models import ChatCompletionTool, FunctionObject, FunctionParameters

weather_tool = ChatCompletionTool(
    type="function",
    function=FunctionObject(
        name="get_current_weather",
        description="Get the current weather in a given location",
        parameters=FunctionParameters(
            type="object",
            properties={
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit to use"
                }
            },
            required=["location"]
        )
    )
)

# Using tools in a chat completion
response = client.create_chat_completion(
    model="openai/gpt-4",
    messages=[
        Message(role="system", content="You are a helpful assistant with access to weather information"),
        Message(role="user", content="What is the weather like in New York?")
    ],
    tools=[weather_tool]  # Pass the tool definition
)

print(response.choices[0].message.content)

# Check if the model made a tool call
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        print(f"Tool called: {tool_call.function.name}")
        print(f"Arguments: {tool_call.function.arguments}")
```

### Listing Available MCP Tools

```python
# List available MCP tools (requires MCP_ENABLE and MCP_EXPOSE to be set on the gateway)
tools = client.list_tools()
print("Available tools:", tools)
```

**Server-Side Tool Management**

The SDK currently supports listing available MCP tools, which is particularly useful for UI applications that need to display connected tools to users. The key advantage is that tools are managed server-side:

- **Automatic Tool Injection**: Tools are automatically inferred and injected into requests by the Inference Gateway server
- **Simplified Client Code**: No need to manually manage or configure tools in your client application
- **Transparent Tool Calls**: During streaming chat completions with configured MCP servers, tool calls appear in the response stream - no special handling required except optionally displaying them to users

This architecture allows you to focus on LLM interactions while the gateway handles all tool management complexities behind the scenes.

### Custom HTTP Configuration

```python
# With custom headers
client = InferenceGatewayClient(
    "http://localhost:8080/v1",
    headers={"X-Custom-Header": "value"}
)

# With proxy settings
client = InferenceGatewayClient(
    "http://localhost:8080/v1",
    proxies={"http": "http://proxy.example.com"}
)
```

## Examples

For comprehensive examples demonstrating various use cases, see the [examples](examples/) directory:

- [List LLMs](examples/list/) - How to list available models
- [Chat](examples/chat/) - Basic and advanced chat completion examples
- [Tools](examples/tools/) - Working with function tools
- [MCP](examples/mcp/) - Model Context Protocol integration examples

Each example includes a detailed README with setup instructions and explanations.

## License

This SDK is distributed under the MIT License, see [LICENSE](LICENSE) for more information.
