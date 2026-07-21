<div align="center">

# 🚀 Inference Gateway Python SDK

### A modern and easy-to-use Python SDK for the Inference Gateway

[![PyPI version](https://img.shields.io/pypi/v/inference-gateway.svg)](https://pypi.org/project/inference-gateway/)
[![Python Version](https://img.shields.io/pypi/pyversions/inference-gateway.svg)](https://pypi.org/project/inference-gateway/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Release](https://img.shields.io/github/release/inference-gateway/python-sdk.svg)](https://github.com/inference-gateway/python-sdk/releases)

Connect to multiple LLM providers through a unified interface • Stream responses • Function calling • Vision support • MCP tools support • Pydantic validation

[Installation](#installation) • [Quick Start](#usage) • [Examples](#examples) • [License](#license)

</div>

---

- [🚀 Inference Gateway Python SDK](#-inference-gateway-python-sdk)
  - [A modern and easy-to-use Python SDK for the Inference Gateway](#a-modern-and-easy-to-use-python-sdk-for-the-inference-gateway)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Creating a Client](#creating-a-client)
    - [Listing Models](#listing-models)
    - [Listing MCP Tools](#listing-mcp-tools)
    - [Generating Content](#generating-content)
    - [Vision Support](#vision-support)
    - [Using ReasoningFormat](#using-reasoningformat)
    - [Streaming Content](#streaming-content)
    - [Tool-Use](#tool-use)
    - [Provider-Specific Tool-Call Metadata](#provider-specific-tool-call-metadata)
    - [Proxy Requests](#proxy-requests)
    - [Health Check](#health-check)
    - [Error Handling](#error-handling)
  - [Examples](#examples)
  - [Supported Providers](#supported-providers)
  - [License](#license)

## Installation

To install the SDK, use `pip`:

```sh
pip install inference-gateway
```

Requires Python 3.12+.

## Usage

### Creating a Client

To create a client, instantiate `InferenceGatewayClient`:

```python
from inference_gateway import InferenceGatewayClient, Message

client = InferenceGatewayClient("http://localhost:8080/v1")
```

The client also supports authentication, custom timeouts, and an optional `httpx` backend:

```python
# With authentication
client = InferenceGatewayClient(
    "http://localhost:8080/v1",
    token="your-api-token",
    timeout=60.0,
)

# Using httpx instead of the default requests backend
client = InferenceGatewayClient(
    "http://localhost:8080/v1",
    use_httpx=True,
)

# Use as a context manager to ensure the underlying HTTP client is closed
with InferenceGatewayClient("http://localhost:8080/v1") as client:
    models = client.list_models()
```

### Listing Models

To list available models, use the `list_models` method:

```python
# List all models from all providers
models = client.list_models()
print("All available models:", models)

# List models for a specific provider
openai_models = client.list_models(provider="openai")
print("OpenAI models:", openai_models)
```

### Listing MCP Tools

To list available MCP (Model Context Protocol) tools, use the `list_tools` method. This functionality is only available when `MCP_ENABLE` and `MCP_EXPOSE` are set on the Inference Gateway server:

```python
tools = client.list_tools()

print(f"Found {len(tools.data)} MCP tools:")
for tool in tools.data:
    print(f"- {tool.name}: {tool.description} (Server: {tool.server})")
```

> **Note:** The MCP tools endpoint requires authentication and is only accessible when the server has `MCP_EXPOSE=true` configured.

**Server-Side Tool Management**

The SDK currently supports listing available MCP tools, which is particularly useful for UI applications that need to display connected tools to users. The key advantage is that tools are managed server-side:

- **Automatic Tool Injection**: Tools are automatically inferred and injected into requests by the Inference Gateway server
- **Simplified Client Code**: No need to manually manage or configure tools in your client application
- **Transparent Tool Calls**: During streaming chat completions with configured MCP servers, tool calls appear in the response stream - no special handling required except optionally displaying them to users

### Generating Content

To generate content using a model, use the `create_chat_completion` method:

> **Note:** Some models support reasoning capabilities. You can use the `reasoning_format` parameter to control how reasoning is provided in the response. The model's reasoning will be available in the `reasoning` or `reasoning_content` fields of the response message.

```python
from inference_gateway import InferenceGatewayClient, Message

client = InferenceGatewayClient("http://localhost:8080/v1")

response = client.create_chat_completion(
    model="ollama/llama2",
    messages=[
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="What is Python?"),
    ],
)

print(response.choices[0].message.content.root)

# If reasoning was requested and the model supports it
if response.choices[0].message.reasoning:
    print("Reasoning:", response.choices[0].message.reasoning)
```

### Vision Support

The SDK supports multimodal messages with images for vision-capable models like GPT-4o. You can include images via URLs or base64-encoded data URLs.

#### Simple Text Message

```python
from inference_gateway import InferenceGatewayClient, Message

client = InferenceGatewayClient("http://localhost:8080/v1")

response = client.create_chat_completion(
    model="openai/gpt-4o",
    messages=[Message(role="user", content="What is the Python programming language?")],
)
```

#### Vision Message with Image URL

```python
from inference_gateway import (
    InferenceGatewayClient,
    Message,
    TextContentPart,
    ImageContentPart,
    ImageURL,
)

client = InferenceGatewayClient("http://localhost:8080/v1")

response = client.create_chat_completion(
    model="openai/gpt-4o",
    messages=[
        Message(
            role="user",
            content=[
                TextContentPart(type="text", text="What is in this image?"),
                ImageContentPart(
                    type="image_url",
                    image_url=ImageURL(
                        url="https://example.com/image.jpg",
                        detail="auto",
                    ),
                ),
            ],
        )
    ],
)
```

#### Vision Message with Base64 Encoded Image

```python
from inference_gateway import ImageContentPart, ImageURL

ImageContentPart(
    type="image_url",
    image_url=ImageURL(
        url="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...",
        detail="high",  # better quality, more expensive
    ),
)
```

#### Multiple Images in One Message

```python
Message(
    role="user",
    content=[
        TextContentPart(type="text", text="Compare these images:"),
        ImageContentPart(type="image_url", image_url=ImageURL(url="https://example.com/image1.jpg")),
        ImageContentPart(type="image_url", image_url=ImageURL(url="https://example.com/image2.jpg")),
    ],
)
```

**Image Detail Levels:**

- `"auto"`: Automatic detail level (default)
- `"low"`: Lower resolution, faster and cheaper
- `"high"`: Higher resolution, better quality but more expensive

For a complete example, see the [chat example](examples/chat/).

### Using ReasoningFormat

You can enable reasoning capabilities by setting the `reasoning_format` parameter in your request:

```python
from inference_gateway import InferenceGatewayClient, Message

client = InferenceGatewayClient("http://localhost:8080/v1")

response = client.create_chat_completion(
    model="anthropic/claude-3-opus-20240229",
    messages=[
        Message(role="system", content="You are a helpful assistant. Please include your reasoning for complex questions."),
        Message(role="user", content="What is the square root of 144 and why?"),
    ],
    reasoning_format="parsed",  # "raw" or "parsed" - defaults to "parsed"
)

print("Content:", response.choices[0].message.content.root)
if response.choices[0].message.reasoning:
    print("Reasoning:", response.choices[0].message.reasoning)
```

### Sampling and Output Controls

`create_chat_completion` and `create_chat_completion_stream` accept the full set of
OpenAI-compatible request parameters as keyword arguments. The SDK only sends the
parameters you set explicitly - spec defaults you do not specify are left off the
request so each provider applies its own.

```python
from inference_gateway import InferenceGatewayClient, Message

client = InferenceGatewayClient("http://localhost:8080/v1")

response = client.create_chat_completion(
    model="openai/gpt-4o",
    messages=[Message(role="user", content="Describe Python as a JSON object.")],
    temperature=0.2,            # 0-2, sampling temperature
    top_p=0.9,                  # 0-1, nucleus sampling
    n=1,                        # 1-128, number of choices to generate
    stop=["\n\n"],              # a string, or up to 4 strings
    frequency_penalty=0.0,      # -2..2
    presence_penalty=0.0,       # -2..2
    seed=42,                    # best-effort determinism
    max_completion_tokens=512,  # preferred over the deprecated max_tokens
    response_format={"type": "json_object"},
    reasoning_effort="medium",  # minimal | low | medium | high
)
```

`response_format` and `tool_choice` are `oneOf` unions. You can pass plain dicts (they
are validated for you) or use the exported typed models:

```python
from inference_gateway import (
    ChatCompletionNamedToolChoice,
    ResponseFormatJsonObject,
)

response = client.create_chat_completion(
    model="openai/gpt-4o",
    messages=[Message(role="user", content="What's the weather in Paris?")],
    response_format=ResponseFormatJsonObject(type="json_object"),
    tool_choice=ChatCompletionNamedToolChoice(
        type="function",
        function={"name": "get_weather"},
    ),
)
```

> **Note:** `max_tokens` is deprecated in favor of `max_completion_tokens`.

### Streaming Content

To generate content using streaming mode, use the `create_chat_completion_stream` method. It yields `SSEvent` objects:

```python
import json
from pydantic import ValidationError
from inference_gateway import InferenceGatewayClient, Message
from inference_gateway.models import CreateChatCompletionStreamResponse

client = InferenceGatewayClient("http://localhost:8080/v1")

for chunk in client.create_chat_completion_stream(
    model="ollama/llama2",
    messages=[
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Tell me a story."),
    ],
):
    if not chunk.data:
        continue

    try:
        data = json.loads(chunk.data)
        stream_response = CreateChatCompletionStreamResponse.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        continue

    for choice in stream_response.choices:
        # Reasoning content (both reasoning and reasoning_content fields)
        if choice.delta.reasoning:
            print(f"💭 Reasoning: {choice.delta.reasoning}")
        if choice.delta.reasoning_content:
            print(f"💭 Reasoning: {choice.delta.reasoning_content}")

        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
```

### Tool-Use

To use tools with the SDK, define a tool with the type-safe Pydantic models and pass it to the request:

```python
from inference_gateway import InferenceGatewayClient, Message
from inference_gateway.models import ChatCompletionTool, FunctionObject, FunctionParameters

client = InferenceGatewayClient("http://localhost:8080/v1")

tools = [
    ChatCompletionTool(
        type="function",
        function=FunctionObject(
            name="get_current_weather",
            description="Get the current weather in a given location",
            parameters=FunctionParameters(
                type="object",
                properties={
                    "location": {
                        "type": "string",
                        "enum": ["san francisco", "new york", "london", "tokyo", "sydney"],
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use",
                    },
                },
                required=["location"],
            ),
        ),
    ),
    ChatCompletionTool(
        type="function",
        function=FunctionObject(
            name="get_current_time",
            description="Get the current time in a given location",
            parameters=FunctionParameters(
                type="object",
                properties={
                    "location": {
                        "type": "string",
                        "enum": ["san francisco", "new york", "london", "tokyo", "sydney"],
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                },
                required=["location"],
            ),
        ),
    ),
]

response = client.create_chat_completion(
    model="openai/gpt-4o",
    messages=[
        Message(role="system", content="You are a helpful assistant with access to weather and time information."),
        Message(role="user", content="What is the weather like in New York?"),
    ],
    tools=tools,
)

# Inspect any tool calls made by the model
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        print(f"Tool called: {tool_call.function.name}")
        print(f"Arguments: {tool_call.function.arguments}")
```

### Provider-Specific Tool-Call Metadata

Some providers attach opaque, per-call metadata that must be echoed back on follow-up requests. The most notable case is Google Gemini's reasoning models, which return a `thought_signature` on each tool call - the next request must round-trip it verbatim or the provider will reject it.

The SDK preserves this automatically as long as you append the assistant message back to the conversation as a model object (rather than reconstructing it from a dict):

```python
response = client.create_chat_completion(
    model="google/gemini-3-pro",
    messages=messages,
    tools=tools,
)

assistant_message = response.choices[0].message
messages.append(assistant_message)  # preserves extra_content.google.thought_signature

# ... append your tool results, then send the follow-up request ...
```

If you need to construct one explicitly:

```python
from inference_gateway import Google, ToolCallExtraContent

extra = ToolCallExtraContent(google=Google(thought_signature="..."))
```

The field is fully optional - providers that don't use it ignore it entirely, and `model_dump(exclude_none=True)` strips it from the wire when unset.

### Messages API (Anthropic-compatible)

The gateway also exposes an Anthropic-compatible Messages API (`POST /messages`). Use `create_message` for standard requests - it returns a validated `MessagesResponse`:

```python
from inference_gateway import InferenceGatewayClient, MessagesMessage, MessagesTextBlock

client = InferenceGatewayClient("http://localhost:8080/v1")

response = client.create_message(
    model="anthropic/claude-sonnet-5",
    messages=[
        MessagesMessage(role="user", content="Hello! Please introduce yourself briefly."),
    ],
    max_tokens=100,
    system="You are a helpful assistant",
)

for block in response.content:
    if isinstance(block.root, MessagesTextBlock):
        print(block.root.text)

print(f"Stop reason: {response.stop_reason}")
print(f"Usage: {response.usage.input_tokens} in / {response.usage.output_tokens} out")
```

`create_message_stream` yields typed `MessagesStreamEvent` objects (`message_start`, `content_block_delta`, `message_stop`, ...) - no manual SSE parsing needed:

```python
for event in client.create_message_stream(
    model="anthropic/claude-sonnet-5",
    messages=[
        MessagesMessage(role="user", content="Tell me a short story."),
    ],
    max_tokens=200,
):
    if event.type == "content_block_delta" and event.delta and event.delta.text:
        print(event.delta.text, end="", flush=True)
```

Tools use the `MessagesTool` shape, and tool calls come back as `MessagesToolUseBlock` content blocks:

```python
from inference_gateway import MessagesTool, MessagesToolUseBlock
from inference_gateway.models import FunctionParameters

tools = [
    MessagesTool(
        name="get_current_weather",
        description="Get the current weather in a given location",
        input_schema=FunctionParameters(
            type="object",
            properties={
                "location": {"type": "string", "description": "The city, e.g. San Francisco"},
            },
            required=["location"],
        ),
    ),
]

response = client.create_message(
    model="anthropic/claude-sonnet-5",
    messages=[MessagesMessage(role="user", content="What is the weather in New York?")],
    max_tokens=200,
    tools=tools,
)

for block in response.content:
    if isinstance(block.root, MessagesToolUseBlock):
        print(f"Tool called: {block.root.name}")
        print(f"Input: {block.root.input}")
```

> **Note:** Not every provider implements the Messages API. Requests routed to a provider without support return a 400 error - use `create_chat_completion` for those providers.

### Proxy Requests

To proxy a raw request directly to a provider's API through the gateway, use `proxy_request`:

```python
response = client.proxy_request(
    provider="openai",
    path="/v1/models",
    method="GET",
)

print("OpenAI models:", response)
```

### Health Check

To check if the API is healthy:

```python
if client.health_check():
    print("API is healthy")
else:
    print("API is unavailable")
```

### Error Handling

The SDK provides several exception types:

```python
from inference_gateway import (
    InferenceGatewayError,
    InferenceGatewayAPIError,
    InferenceGatewayValidationError,
)

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

## Examples

For more detailed examples and use cases, check out the [examples directory](./examples/). The examples include:

- **[List Example](./examples/list/)** - How to list available models
- **[Chat Example](./examples/chat/)** - Basic and advanced chat completion examples
- **[Tools Example](./examples/tools/)** - Function calling and tool usage
- **[Messages Example](./examples/messages/)** - Anthropic-compatible Messages API usage
- **[MCP Example](./examples/mcp/)** - Model Context Protocol integration examples

Each example includes its own README with specific instructions and explanations.

## Supported Providers

The SDK supports the following LLM providers:

- Ollama (`"ollama"`)
- Ollama Cloud (`"ollama_cloud"`)
- Groq (`"groq"`)
- OpenAI (`"openai"`)
- DeepSeek (`"deepseek"`)
- Cloudflare (`"cloudflare"`)
- Cohere (`"cohere"`)
- Anthropic (`"anthropic"`)
- Google (`"google"`)
- Mistral AI (`"mistral"`)
- MiniMax (`"minimax"`)
- Moonshot (`"moonshot"`)
- NVIDIA (`"nvidia"`)

## License

This SDK is distributed under the Apache 2.0 License, see [LICENSE](LICENSE) for more information.
