# Responses API Example

This example demonstrates how to use the Inference Gateway Python SDK with the OpenAI-compatible Responses API (`POST /responses`), with standard requests, typed streaming events and function tools.

## Features

- **Standard Response**: Send a text prompt as `input` and read the text from the typed `output` item list
- **Streaming Response**: Typed `ResponseStreamEvent` objects (`response.created`, `response.output_text.delta`, `response.completed`, ...) - no manual SSE parsing needed
- **Multi-Turn Input with a Function Tool**: Build `input` from `ResponseInputItem` objects, define a flattened `ResponseTool` and read the call back from a `ResponseFunctionToolCall` output item

> **Note:** Not every provider implements the Responses API. Requests routed to a provider without support return a 400 error - use `create_chat_completion` for those providers.

## Usage

1. **Set up environment**:

   ```bash
   export LLM_NAME="openai/gpt-4o"
   ```

2. **Run the example**:
   ```bash
   python main.py
   ```

## Code Examples

### Standard Response

```python
from inference_gateway import InferenceGatewayClient, ResponseOutputMessage, ResponseOutputText

client = InferenceGatewayClient("http://localhost:8080/v1")

response = client.create_response(
    model="openai/gpt-4o",
    input="Hello! Please introduce yourself briefly.",
    max_output_tokens=100,
)

for item in response.output:
    if isinstance(item.root, ResponseOutputMessage):
        for part in item.root.content:
            if isinstance(part.root, ResponseOutputText):
                print(part.root.text)
```

### Streaming Response

```python
for event in client.create_response_stream(
    model="openai/gpt-4o",
    input="Tell me a short story about a robot.",
    max_output_tokens=200,
):
    if event.type == "response.output_text.delta" and event.delta:
        print(event.delta, end="", flush=True)
```

### Multi-Turn Input with a Function Tool

The Responses API uses a flattened tool shape - `name`, `description` and `parameters` sit directly on `ResponseTool` instead of under a nested `function` object.

```python
import json

from inference_gateway import ResponseFunctionToolCall, ResponseInputItem, ResponseTool
from inference_gateway.models import FunctionParameters

weather_tool = ResponseTool(
    name="get_current_weather",
    description="Get the current weather in a given location",
    parameters=FunctionParameters(
        type="object",
        properties={
            "location": {"type": "string", "description": "The city, e.g. San Francisco"},
        },
        required=["location"],
    ),
)

response = client.create_response(
    model="openai/gpt-4o",
    input=[
        ResponseInputItem(role="system", content="You are a helpful weather assistant."),
        ResponseInputItem(role="user", content="Hi, I am planning a trip."),
        ResponseInputItem(role="assistant", content="Great! Where are you heading?"),
        ResponseInputItem(role="user", content="New York. What is the weather there?"),
    ],
    max_output_tokens=200,
    tools=[weather_tool],
)

for item in response.output:
    if isinstance(item.root, ResponseFunctionToolCall):
        print(f"Tool called: {item.root.name} (call_id={item.root.call_id})")
        print(f"Arguments: {json.loads(item.root.arguments)}")
```

## Error Handling

The SDK provides specific exception types:

- `InferenceGatewayAPIError`: API-related errors (4xx, 5xx responses) - including the 400 returned by providers without Responses API support
- `InferenceGatewayError`: SDK-related errors (network, parsing, etc.)

```python
from inference_gateway.client import InferenceGatewayAPIError, InferenceGatewayError

try:
    response = client.create_response(...)
except (InferenceGatewayAPIError, InferenceGatewayError) as e:
    print(f"Error: {e}")
```

## Dependencies

- `inference_gateway`: The Python SDK for Inference Gateway
- Standard library: `json`, `os`

## Configuration

The example uses the `LLM_NAME` environment variable to specify the model (default `openai/gpt-4o`). Pick a model from a provider that implements the Responses API.
