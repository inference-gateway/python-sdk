# Messages API Example

This example demonstrates how to use the Inference Gateway Python SDK with the Anthropic-compatible Messages API (`POST /messages`), with both standard requests and typed streaming events.

## Features

- **Standard Message**: Traditional request-response pattern returning a validated `MessagesResponse`
- **Streaming Message**: Typed `MessagesStreamEvent` objects (`message_start`, `content_block_delta`, `message_stop`, ...) - no manual SSE parsing needed

> **Note:** Not every provider implements the Messages API. Requests routed to a provider without support return a 400 error - use `create_chat_completion` for those providers.

## Usage

1. **Set up environment**:

   ```bash
   export LLM_NAME="anthropic/claude-sonnet-5"
   ```

2. **Run the example**:
   ```bash
   python main.py
   ```

## Code Examples

### Standard Message

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
```

### Streaming Message

```python
from inference_gateway import InferenceGatewayClient, MessagesMessage

client = InferenceGatewayClient("http://localhost:8080/v1")

stream = client.create_message_stream(
    model="anthropic/claude-sonnet-5",
    messages=[
        MessagesMessage(role="user", content="Tell me a short story."),
    ],
    max_tokens=200,
)

for event in stream:
    if event.type == "content_block_delta" and event.delta and event.delta.text:
        print(event.delta.text, end="", flush=True)
```

### Tool-Use

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

## Error Handling

The SDK provides specific exception types:

- `InferenceGatewayAPIError`: API-related errors (4xx, 5xx responses)
- `InferenceGatewayError`: SDK-related errors (network, parsing, etc.)

```python
from inference_gateway.client import InferenceGatewayAPIError, InferenceGatewayError

try:
    response = client.create_message(...)
except (InferenceGatewayAPIError, InferenceGatewayError) as e:
    print(f"Error: {e}")
```

## Dependencies

- `inference_gateway`: The Python SDK for Inference Gateway
- Standard library: `os`

## Configuration

The example uses the `LLM_NAME` environment variable to specify the model. The Messages API is supported by providers that implement Anthropic's message format, e.g. `anthropic/claude-sonnet-5`.
