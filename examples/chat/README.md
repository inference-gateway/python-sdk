# Chat Completions Example

This example demonstrates how to use the Inference Gateway Python SDK for chat completions with both standard HTTP requests and streaming responses.

## Features

- **Standard Chat Completion**: Traditional request-response pattern with complete messages
- **Streaming Chat Completion**: Real-time streaming responses for better user experience

## Usage

1. **Set up environment**:

   ```bash
   export LLM_NAME="groq/meta-llama/llama-4-scout-17b-16e-instruct"
   ```

2. **Run the example**:
   ```bash
   python main.py
   ```

## Code Examples

### Standard Chat Completion

```python
from inference_gateway import InferenceGatewayClient, Message

client = InferenceGatewayClient("http://localhost:8080/v1")

response = client.create_chat_completion(
    model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[
        Message(role="system", content="You are a helpful assistant"),
        Message(role="user", content="Hello! Please introduce yourself briefly."),
    ],
    max_tokens=100,
)

print(response.choices[0].message.content)
```

### Streaming Chat Completion

```python
from inference_gateway import InferenceGatewayClient, Message
from inference_gateway.models import SSEvent, CreateChatCompletionStreamResponse
from pydantic import ValidationError
import json

client = InferenceGatewayClient("http://localhost:8080/v1")

stream = client.create_chat_completion_stream(
    model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[
        Message(role="system", content="You are a helpful assistant"),
        Message(role="user", content="Tell me a short story."),
    ],
    max_tokens=200,
)

for chunk in stream:
    if chunk.data:
        try:
            # Parse the raw JSON data
            data = json.loads(chunk.data)

            # Unmarshal to structured model for type safety
            try:
                structured_chunk = CreateChatCompletionStreamResponse.model_validate(data)

                # Use the structured model for better type safety and IDE support
                if structured_chunk.choices and len(structured_chunk.choices) > 0:
                    choice = structured_chunk.choices[0]
                    if hasattr(choice.delta, 'content') and choice.delta.content:
                        print(choice.delta.content, end="", flush=True)

            except ValidationError:
                # Fallback to manual parsing for non-standard chunks
                if "choices" in data and len(data["choices"]) > 0:
                    delta = data["choices"][0].get("delta", {})
                    if "content" in delta and delta["content"]:
                        print(delta["content"], end="", flush=True)

        except json.JSONDecodeError:
            pass
```

## Error Handling

The SDK provides specific exception types:

- `InferenceGatewayAPIError`: API-related errors (4xx, 5xx responses)
- `InferenceGatewayError`: SDK-related errors (network, parsing, etc.)

```python
from inference_gateway.client import InferenceGatewayAPIError, InferenceGatewayError

try:
    response = client.create_chat_completion(...)
except (InferenceGatewayAPIError, InferenceGatewayError) as e:
    print(f"Error: {e}")
```

## Dependencies

- `inference_gateway`: The Python SDK for Inference Gateway
- Standard library: `json`, `os`

## Configuration

The example uses the `LLM_NAME` environment variable to specify the model. Supported models include:

- OpenAI models: `openai/gpt-4`, `openai/gpt-3.5-turbo`
- Groq models: `groq/meta-llama/llama-4-scout-17b-16e-instruct`
- Other providers as configured in your Inference Gateway instance
